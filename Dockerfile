FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# git: the coding-agent tool clones/branches/commits/pushes the frontend repo.
# Node.js + Claude Code CLI: does the actual code writing, invoked headlessly
# from src/tools/coding_agent.py. Debian's bundled nodejs is too old for
# Claude Code, so pull a current LTS from NodeSource instead.
RUN apt-get update && apt-get install -y --no-install-recommends git curl gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && npm install -g @anthropic-ai/claude-code \
    && apt-get purge -y curl gnupg \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

EXPOSE 8000

CMD ["python", "main.py"]
