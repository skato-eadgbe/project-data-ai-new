from unittest.mock import MagicMock, patch

from src.collector.hn_collector import HnCollector


class TestHnCollector:
    def test_キーワードでAI関連記事をフィルタできる(self):
        collector = HnCollector(keywords=["AI", "LLM"])
        assert collector.is_relevant("New AI model released") is True
        assert collector.is_relevant("Cooking recipes") is False
        assert collector.is_relevant("LLM benchmark results") is True

    def test_キーワードマッチは大文字小文字を無視する(self):
        collector = HnCollector(keywords=["machine learning"])
        assert collector.is_relevant("Machine Learning trends") is True

    @patch("src.collector.hn_collector.httpx.get")
    def test_トップストーリーのIDを取得できる(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [1, 2, 3, 4, 5]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        collector = HnCollector(max_stories=3)
        ids = collector.fetch_top_story_ids()

        assert ids == [1, 2, 3]

    @patch("src.collector.hn_collector.httpx.get")
    def test_ストーリー詳細を取得できる(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "title": "AI breakthrough",
            "url": "https://example.com/ai",
            "type": "story",
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        collector = HnCollector(keywords=["AI"])
        article = collector.fetch_story(123)

        assert article is not None
        assert article.title == "AI breakthrough"
        assert article.source == "Hacker News"

    @patch("src.collector.hn_collector.httpx.get")
    def test_キーワード非該当のストーリーはNoneを返す(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "title": "Cooking tips",
            "url": "https://example.com/cook",
            "type": "story",
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        collector = HnCollector(keywords=["AI"])
        article = collector.fetch_story(123)

        assert article is None
