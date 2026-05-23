import os
import time
import sqlite3
import logging
from typing import List
import requests
from telegram import Bot
from telegram.error import TelegramError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOGGER = logging.getLogger(__name__)

# ---------- Configuration ----------
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
REPOS = os.getenv("REPOS", "")  # e.g. "owner/repo,owner2/repo2"
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "300"))  # seconds

if not BOT_TOKEN or not CHAT_ID or not REPOS:
    LOGGER.error("Missing required environment variables: BOT_TOKEN, CHAT_ID, REPOS")
    raise SystemExit(1)

REPO_LIST: List[str] = [repo.strip() for repo in REPOS.split(",") if repo.strip()]

# ---------- Database ----------
DB_PATH = "seen.db"
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute(
    "CREATE TABLE IF NOT EXISTS seen (repo TEXT, release_id TEXT, PRIMARY KEY (repo, release_id))"
)
conn.commit()

# ---------- Helper functions ----------
def has_been_seen(repo: str, release_id: str) -> bool:
    cur.execute("SELECT 1 FROM seen WHERE repo=? AND release_id=?", (repo, release_id))
    return cur.fetchone() is not None

def mark_as_seen(repo: str, release_id: str):
    cur.execute("INSERT OR IGNORE INTO seen (repo, release_id) VALUES (?,?)", (repo, release_id))
    conn.commit()

def fetch_latest_release(repo: str):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    resp = requests.get(url, timeout=10)
    if resp.status_code == 404:
        LOGGER.warning("Repo %s has no releases", repo)
        return None
    resp.raise_for_status()
    return resp.json()

def format_message(repo: str, release: dict) -> str:
    name = release.get("name") or release.get("tag_name")
    url = release.get("html_url")
    body = (release.get("body") or "").split("\n")[0]
    return f"📦 *{repo}* released *{name}*\n{url}\n_{body}_"

# ---------- Main loop ----------
bot = Bot(token=BOT_TOKEN)

LOGGER.info("Starting watcher for %d repos", len(REPO_LIST))
while True:
    for repo in REPO_LIST:
        try:
            release = fetch_latest_release(repo)
            if not release:
                continue
            release_id = release["id"]
            if has_been_seen(repo, str(release_id)):
                continue
            message = format_message(repo, release)
            bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
            LOGGER.info("Notified %s about release %s", repo, release_id)
            mark_as_seen(repo, str(release_id))
        except (requests.RequestException, TelegramError) as e:
            LOGGER.error("Error processing repo %s: %s", repo, e)
        except Exception as e:
            LOGGER.exception("Unexpected error for repo %s", repo)
    LOGGER.debug("Sleeping for %s seconds", POLL_INTERVAL)
    time.sleep(POLL_INTERVAL)
