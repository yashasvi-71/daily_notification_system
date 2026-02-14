from __future__ import annotations

import argparse
import os
from collections import defaultdict
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from news_fetcher import NewsFetcher
from notifier import Notifier


def build_digest_message(items) -> str:
    grouped = defaultdict(list)
    for item in items:
        grouped[item.topic].append(item)

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"🗞️ Daily News Digest ({now})", ""]
    topic_titles = {
        "tech": "💻 Tech",
        "ai": "🤖 AI",
        "jobs": "🧑‍💼 Jobs",
        "software": "🧩 New Software",
    }

    for topic in ("tech", "ai", "jobs", "software"):
        lines.append(topic_titles[topic])
        entries = grouped.get(topic, [])
        if not entries:
            lines.append("- No relevant stories found today.")
            lines.append("")
            continue

        for story in entries:
            lines.append(f"- {story.title} ({story.source})")
            lines.append(f"  {story.link}")
        lines.append("")

    return "\n".join(lines)


def run_job(per_topic_limit: int) -> None:
    items = NewsFetcher().fetch(per_topic_limit=per_topic_limit)
    message = build_digest_message(items)

    notifier = Notifier(
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID"),
        smtp_host=os.getenv("SMTP_HOST"),
        smtp_port=int(os.getenv("SMTP_PORT", "0")) or None,
        smtp_user=os.getenv("SMTP_USER"),
        smtp_password=os.getenv("SMTP_PASSWORD"),
        email_from=os.getenv("EMAIL_FROM"),
        email_to=os.getenv("EMAIL_TO"),
    )
    notifier.send(message)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Daily news notification system")
    parser.add_argument("--run-once", action="store_true", help="Fetch and send now, then exit")
    parser.add_argument("--time", default="09:00", help="Daily time in 24h format, e.g., 09:30")
    parser.add_argument("--timezone", default="UTC", help="Timezone name, e.g., Asia/Kolkata")
    parser.add_argument("--per-topic", type=int, default=5, help="Top stories per topic")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.run_once:
        run_job(per_topic_limit=args.per_topic)
        return

    hour_str, minute_str = args.time.split(":")
    trigger = CronTrigger(hour=int(hour_str), minute=int(minute_str), timezone=args.timezone)

    scheduler = BlockingScheduler(timezone=args.timezone)
    scheduler.add_job(run_job, trigger=trigger, kwargs={"per_topic_limit": args.per_topic})

    print(
        f"Scheduler started. Daily digest at {args.time} ({args.timezone}). "
        "Press Ctrl+C to stop."
    )
    scheduler.start()


if __name__ == "__main__":
    main()
