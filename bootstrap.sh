#!/usr/bin/env bash
set -euo pipefail

# Runs as root via the Custom Script Extension, on every redeploy (forced via
# forceUpdateTag in vm.bicep). Installs Docker, pulls this repo (public, no
# auth needed), and builds+runs the agent + Caddy (reverse proxy/TLS) via
# docker compose. $1 = the bot's User-Assigned Managed Identity client ID,
# passed through into a .env file that docker compose loads automatically.

UAMI_CLIENT_ID="${1:?Usage: bootstrap.sh <uami-client-id>}"

# unattended-upgrades runs automatically right after boot on a fresh Ubuntu VM
# and holds the dpkg lock - retry instead of assuming it's free.
apt_retry() {
  local n=0
  until "$@"; do
    n=$((n + 1))
    if [ "$n" -ge 20 ]; then
      echo "apt command failed after $n attempts: $*" >&2
      return 1
    fi
    echo "apt busy (lock held), retrying in 5s... (attempt $n)"
    sleep 5
  done
}

apt_retry apt-get update
apt_retry apt-get install -y ca-certificates curl gnupg git
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --batch --yes --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
apt_retry apt-get update
apt_retry apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# leftover from before this repo used docker compose - held port 8000
docker rm -f teams-agent 2>/dev/null || true

rm -rf /opt/teams-agent-app
git clone https://github.com/ChristianKatka/teams-agent-app.git /opt/teams-agent-app
cd /opt/teams-agent-app
echo "UAMI_CLIENT_ID=${UAMI_CLIENT_ID}" > .env
docker compose down 2>/dev/null || true
docker compose up -d --build
