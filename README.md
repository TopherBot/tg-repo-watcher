# tg‑repo‑watcher

A tiny, self‑hosted **Telegram Release Notifier**.

## What it does
- Periodically polls the GitHub Releases API for a set of repositories you care about.
- When a new release is detected, it sends a nicely formatted message to a Telegram chat using a bot token.
- Keeps a tiny local SQLite DB (`seen.db`) to remember which releases have already been announced.

## Why this project?
- Shows **CI/CD** with GitHub Actions (lint, test, Docker build & push).
- Uses **Docker** for reproducible deployments.
- Demonstrates **Telegram Bot API** usage – a favourite of TopherBot’s alerts.
- Small enough to fork and extend (e.g., add Slack‑integration, RSS feeds, or a web UI).

## Quick start (local)
```bash
# 1️⃣ Clone
git clone https://github.com/your‑account/tg-repo-watcher.git
cd tg-repo-watcher

# 2️⃣ Create a virtual env
python3 -m venv .venv
source .venv/bin/activate

# 3️⃣ Install deps
pip install -r requirements.txt

# 4️⃣ Set environment variables (see .env.example)
cp .env.example .env
# edit .env with your Telegram BOT_TOKEN, CHAT_ID and a comma‑separated list of repos

# 5️⃣ Run
python app.py
```

## Docker
```bash
# Build
docker build -t tg-repo-watcher .
# Run (replace env vars with your own values)
docker run -d \
  -e BOT_TOKEN=... \
  -e CHAT_ID=... \
  -e REPOS=octocat/Hello-World,owner/repo \
  --name tg-repo-watcher tg-repo-watcher
```

## CI/CD pipeline
The workflow runs on every push to `main`:
- **lint** with `ruff`
- **unit tests** with `pytest`
- **docker build** and push to GitHub Container Registry (GHCR)
- Deploy can be hooked into any VPS via SSH (see the workflow for an example).

## Contributing
1. Fork the repo
2. Create a feature branch
3. Write tests / update docs
4. Submit a Pull Request

## License
MIT – see LICENSE file.
