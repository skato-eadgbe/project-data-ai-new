import json
import logging
from dataclasses import dataclass

import feedparser

logger = logging.getLogger(__name__)


@dataclass
class Article:
    title: str
    url: str
    summary: str
    source: str
    published: str


def load_feed_config(config_path: str) -> dict:
    with open(config_path) as f:
        return json.load(f)


class RssCollector:
    def fetch_feed(self, feed_url: str, source_name: str) -> list[Article]:
        parsed = feedparser.parse(feed_url)

        if parsed.bozo and not parsed.entries:
            logger.warning("フィード取得失敗: %s (%s)", source_name, feed_url)
            return []

        articles = []
        for entry in parsed.entries:
            articles.append(
                Article(
                    title=entry.get("title", ""),
                    url=entry.get("link", ""),
                    summary=entry.get("summary", ""),
                    source=source_name,
                    published=entry.get("published", ""),
                )
            )
        return articles

    def fetch_all_feeds(self, feeds: list[dict]) -> list[Article]:
        all_articles = []
        for feed in feeds:
            articles = self.fetch_feed(feed["url"], feed["name"])
            all_articles.extend(articles)
        return all_articles

    def validate_feed_urls(self, feeds: list[dict]) -> list[dict]:
        results = []
        for feed in feeds:
            parsed = feedparser.parse(feed["url"])
            valid = bool(parsed.entries) and not parsed.bozo
            results.append(
                {
                    "name": feed["name"],
                    "url": feed["url"],
                    "valid": valid,
                    "entry_count": len(parsed.entries),
                }
            )
        return results
