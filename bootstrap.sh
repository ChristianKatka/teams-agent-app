#!/usr/bin/env bash
set -euo pipefail

# Runs as root via the Custom Script Extension, on every redeploy (forced via
# forceUpdateTag in vm.bicep). Installs Docker, pulls this repo (public, no
# auth needed), and builds+runs the agent + Caddy (reverse proxy/TLS) via
# docker compose.

apt-get update
apt-get install -y ca-certificates curl gnupg git
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

rm -rf /opt/teams-agent-app
git clone https://github.com/ChristianKatka/teams-agent-app.git /opt/teams-agent-app
cd /opt/teams-agent-app
docker compose down 2>/dev/null || true
docker compose up -d --build
