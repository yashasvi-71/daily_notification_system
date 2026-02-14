from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

import feedparser
from dateutil import parser as date_parser


@dataclass(slots=True)
class NewsItem:
    title: str
    link: str
    summary: str
    source: str
    published: datetime
    topic: str


class NewsFetcher:
    """Collects and scores news items from curated RSS feeds."""

    FEEDS: dict[str, list[tuple[str, str]]] = {
        "tech": [
            ("TechCrunch", "https://techcrunch.com/feed/"),
            ("The Verge", "https://www.theverge.com/rss/index.xml"),
            (
                "Google News - Technology",
                "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY",
            ),
        ],
        "ai": [
            (
                "Google News - Artificial Intelligence",
                "https://news.google.com/rss/search?q=artificial+intelligence+OR+machine+learning+OR+LLM+when:1d&hl=en-US&gl=US&ceid=US:en",
            ),
            ("MIT Tech Review - AI", "https://www.technologyreview.com/topic/artificial-intelligence/feed"),
        ],
        "jobs": [
            (
                "Google News - Tech Jobs",
                "https://news.google.com/rss/search?q=tech+jobs+OR+hiring+OR+layoffs+when:1d&hl=en-US&gl=US&ceid=US:en",
            ),
            ("We Work Remotely", "https://weworkremotely.com/categories/remote-programming-jobs.rss"),
        ],
        "software": [
            (
                "Google News - Software Releases",
                "https://news.google.com/rss/search?q=new+software+release+OR+app+launch+OR+open+source+release+when:1d&hl=en-US&gl=US&ceid=US:en",
            ),
            ("GitHub Blog", "https://github.blog/feed/"),
        ],
    }

    KEYWORDS: dict[str, tuple[str, ...]] = {
        "tech": ("technology", "startup", "cloud", "cybersecurity", "chip"),
        "ai": ("ai", "artificial intelligence", "llm", "agent", "model"),
        "jobs": ("hiring", "job", "layoff", "career", "remote"),
        "software": ("release", "launch", "version", "open source", "app"),
    }

    def fetch(self, per_topic_limit: int = 5) -> list[NewsItem]:
        all_items: list[NewsItem] = []

        for topic, sources in self.FEEDS.items():
            topic_items: list[NewsItem] = []
            for source_name, url in sources:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    published = self._parse_published(entry)
                    topic_items.append(
                        NewsItem(
                            title=entry.get("title", "Untitled").strip(),
                            link=entry.get("link", "").strip(),
                            summary=entry.get("summary", "").strip(),
                            source=source_name,
                            published=published,
                            topic=topic,
                        )
                    )

            unique_sorted = self._dedupe_sort_and_score(topic_items, topic)
            all_items.extend(unique_sorted[:per_topic_limit])

        return sorted(all_items, key=lambda n: n.published, reverse=True)

    def _dedupe_sort_and_score(self, items: Iterable[NewsItem], topic: str) -> list[NewsItem]:
        seen_links: set[str] = set()
        deduped: list[NewsItem] = []

        for item in items:
            if not item.link or item.link in seen_links:
                continue
            seen_links.add(item.link)
            deduped.append(item)

        keywords = self.KEYWORDS[topic]

        def score(n: NewsItem) -> tuple[int, datetime]:
            hay = f"{n.title} {n.summary}".lower()
            relevance = sum(1 for word in keywords if word in hay)
            return relevance, n.published

        deduped.sort(key=score, reverse=True)
        return deduped

    @staticmethod
    def _parse_published(entry: dict) -> datetime:
        if "published" in entry:
            try:
                dt = date_parser.parse(entry["published"])
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except (ValueError, TypeError):
                pass
        return datetime.now(timezone.utc)
