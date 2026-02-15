import json
from unittest.mock import MagicMock, patch

from src.collector.rss_collector import Article, RssCollector, load_feed_config


class TestLoadFeedConfig:
    def test_設定ファイルからRSSフィード一覧を読み込める(self, tmp_path):
        config_file = tmp_path / "feeds.json"
        config_data = {
            "rss_feeds": [{"name": "Test", "url": "https://example.com/feed", "category": "test"}],
            "hacker_news": {"base_url": "https://hn.api/", "max_stories": 10, "keywords": ["AI"]},
        }
        config_file.write_text(json.dumps(config_data))
        config = load_feed_config(str(config_file))
        assert len(config["rss_feeds"]) == 1
        assert config["rss_feeds"][0]["name"] == "Test"

    def test_存在しないファイルでFileNotFoundError(self):
        import pytest

        with pytest.raises(FileNotFoundError):
            load_feed_config("/nonexistent/feeds.json")


class TestRssCollector:
    def _make_feed_entry(self, title, link, summary, published):
        entry = MagicMock()
        entry.get = lambda k, default="": {
            "title": title,
            "link": link,
            "summary": summary,
            "published": published,
        }.get(k, default)
        entry.title = title
        entry.link = link
        return entry

    def _make_parsed_feed(self, entries, status=200, bozo=False):
        feed = MagicMock()
        feed.entries = entries
        feed.status = status
        feed.bozo = bozo
        feed.feed = MagicMock()
        feed.feed.get = lambda k, default="": default
        return feed

    @patch("src.collector.rss_collector.feedparser.parse")
    def test_RSSフィードから記事を取得できる(self, mock_parse):
        entries = [
            self._make_feed_entry("AI News 1", "https://example.com/1", "Summary 1", "2026-01-01"),
            self._make_feed_entry("AI News 2", "https://example.com/2", "Summary 2", "2026-01-02"),
        ]
        mock_parse.return_value = self._make_parsed_feed(entries)

        collector = RssCollector()
        articles = collector.fetch_feed("https://example.com/feed", "TestSource")

        assert len(articles) == 2
        assert articles[0].title == "AI News 1"
        assert articles[0].url == "https://example.com/1"
        assert articles[0].source == "TestSource"

    @patch("src.collector.rss_collector.feedparser.parse")
    def test_不正なフィードは空リストを返す(self, mock_parse):
        mock_parse.return_value = self._make_parsed_feed([], status=404, bozo=True)

        collector = RssCollector()
        articles = collector.fetch_feed("https://invalid.com/feed", "Bad")

        assert articles == []

    @patch("src.collector.rss_collector.feedparser.parse")
    def test_複数フィードからまとめて取得できる(self, mock_parse):
        entries = [self._make_feed_entry("Article", "https://a.com/1", "Sum", "2026-01-01")]
        mock_parse.return_value = self._make_parsed_feed(entries)

        feeds = [
            {"name": "Feed1", "url": "https://a.com/feed", "category": "test"},
            {"name": "Feed2", "url": "https://b.com/feed", "category": "test"},
        ]
        collector = RssCollector()
        articles = collector.fetch_all_feeds(feeds)

        assert len(articles) == 2  # 1 article per feed x 2 feeds

    def test_フィードURL検証で有効なURLリストを返す(self):
        collector = RssCollector()
        results = collector.validate_feed_urls(
            [
                {"name": "Good", "url": "https://example.com/feed", "category": "test"},
            ]
        )
        assert len(results) == 1
        assert "name" in results[0]


class TestArticle:
    def test_Articleデータクラスのフィールド(self):
        article = Article(
            title="Test",
            url="https://example.com",
            summary="Summary",
            source="TestSource",
            published="2026-01-01",
        )
        assert article.title == "Test"
        assert article.source == "TestSource"
