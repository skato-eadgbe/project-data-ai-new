import logging

import httpx

from src.collector.rss_collector import Article

logger = logging.getLogger(__name__)

BASE_URL = "https://hacker-news.firebaseio.com/v0/"


class HnCollector:
    def __init__(
        self,
        keywords: list[str] | None = None,
        max_stories: int = 30,
        base_url: str = BASE_URL,
    ):
        self.keywords = [kw.lower() for kw in (keywords or [])]
        self.max_stories = max_stories
        self.base_url = base_url

    def is_relevant(self, title: str) -> bool:
        title_lower = title.lower()
        return any(kw in title_lower for kw in self.keywords)

    def fetch_top_story_ids(self) -> list[int]:
        response = httpx.get(f"{self.base_url}topstories.json")
        response.raise_for_status()
        ids = response.json()
        return ids[: self.max_stories]

    def fetch_story(self, story_id: int) -> Article | None:
        response = httpx.get(f"{self.base_url}item/{story_id}.json")
        response.raise_for_status()
        data = response.json()

        if not data or data.get("type") != "story":
            return None

        title = data.get("title", "")
        if not self.is_relevant(title):
            return None

        return Article(
            title=title,
            url=data.get("url", ""),
            summary="",
            source="Hacker News",
            published="",
        )

    def fetch_relevant_stories(self) -> list[Article]:
        ids = self.fetch_top_story_ids()
        articles = []
        for story_id in ids:
            article = self.fetch_story(story_id)
            if article:
                articles.append(article)
        return articles
