# Daily Notification System

Automatically delivers a **daily digest of important news** focused on:
- Tech
- AI
- Jobs
- New software / releases

It aggregates from curated RSS feeds, ranks stories by relevance/recency, and pushes to you at a specific time daily.

## Features

- Daily scheduler (timezone-aware)
- Topic-focused feed aggregation
- Relevance ranking + deduplication
- Notification channels:
  - Telegram bot
  - SMTP email

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy and configure environment variables:

```bash
cp .env.example .env
```

Then export variables from `.env` (or use your process manager):

```bash
set -a
source .env
set +a
```

## Configuration

### Telegram (recommended)

- `TELEGRAM_BOT_TOKEN`: token from BotFather
- `TELEGRAM_CHAT_ID`: your chat ID

### Email (optional)

- `SMTP_HOST`
- `SMTP_PORT` (usually `587`)
- `SMTP_USER`
- `SMTP_PASSWORD`
- `EMAIL_FROM`
- `EMAIL_TO`

You can configure both Telegram and email together; the digest is sent to all configured channels.

## Usage

### Test once immediately

```bash
python src/main.py --run-once --per-topic 5
```

### Run daily at specific time

```bash
python src/main.py --time 08:30 --timezone Asia/Kolkata --per-topic 5
```

## Run in background (systemd example)

Create `/etc/systemd/system/daily-news.service`:

```ini
[Unit]
Description=Daily News Notification System
After=network.target

[Service]
Type=simple
WorkingDirectory=/path/to/daily_notification_system
EnvironmentFile=/path/to/daily_notification_system/.env
ExecStart=/path/to/daily_notification_system/.venv/bin/python src/main.py --time 08:30 --timezone Asia/Kolkata --per-topic 5
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now daily-news.service
sudo systemctl status daily-news.service
```

## Notes

- News quality depends on RSS feed quality and availability.
- You can customize feeds in `src/news_fetcher.py`.
