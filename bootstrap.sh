#!/usr/bin/env bash
set -euo pipefail

# Runs as root via the Custom Script Extension. Installs Docker, pulls this
# repo (public, no auth needed), and builds+runs the agent container.

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
docker build -t teams-agent .
docker rm -f teams-agent 2>/dev/null || true
docker run -d --name teams-agent --restart unless-stopped -p 8000:8000 teams-agent
