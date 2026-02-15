from unittest.mock import MagicMock, patch

import pytest

from src.summarizer.article_summarizer import ArticleSummarizer


@pytest.fixture
def mock_client():
    client = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="これはAIによる要約です。")]
    client.messages.create.return_value = mock_response
    return client


@pytest.fixture
def summarizer(mock_client):
    with patch("src.summarizer.article_summarizer.anthropic.Anthropic", return_value=mock_client):
        return ArticleSummarizer(api_key="test-api-key")


class TestArticleSummarizer:
    def test_初期化時にモデル名がデフォルト設定される(self):
        with patch("src.summarizer.article_summarizer.anthropic.Anthropic"):
            s = ArticleSummarizer(api_key="test-key")
            assert s.model == "claude-sonnet-4-5-20250929"

    def test_初期化時にモデル名を指定できる(self):
        with patch("src.summarizer.article_summarizer.anthropic.Anthropic"):
            s = ArticleSummarizer(api_key="test-key", model="claude-haiku-4-5-20251001")
            assert s.model == "claude-haiku-4-5-20251001"

    def test_単一記事を要約できる(self, summarizer, mock_client):
        result = summarizer.summarize(
            title="新しいLLMが登場",
            content="OpenAIが新しい大規模言語モデルを発表しました。",
        )
        assert result == "これはAIによる要約です。"
        mock_client.messages.create.assert_called_once()
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs["model"] == "claude-sonnet-4-5-20250929"
        assert call_kwargs["max_tokens"] == 1024

    def test_要約プロンプトにタイトルと本文が含まれる(self, summarizer, mock_client):
        summarizer.summarize(title="テストタイトル", content="テスト本文")
        call_kwargs = mock_client.messages.create.call_args[1]
        user_message = call_kwargs["messages"][0]["content"]
        assert "テストタイトル" in user_message
        assert "テスト本文" in user_message

    def test_本文が空の場合タイトルのみで要約できる(self, summarizer, mock_client):
        result = summarizer.summarize(title="タイトルだけの記事", content="")
        assert result == "これはAIによる要約です。"
        mock_client.messages.create.assert_called_once()

    def test_複数記事を一括要約できる(self, summarizer, mock_client):
        articles = [
            {"url": "https://a.com/1", "title": "記事1", "summary": "概要1"},
            {"url": "https://a.com/2", "title": "記事2", "summary": "概要2"},
        ]
        results = summarizer.summarize_articles(articles)
        assert len(results) == 2
        assert results[0]["url"] == "https://a.com/1"
        assert results[0]["summary"] == "これはAIによる要約です。"
        assert results[1]["url"] == "https://a.com/2"
        assert mock_client.messages.create.call_count == 2

    def test_API呼び出し失敗時はエラーを返す(self, summarizer, mock_client):
        mock_client.messages.create.side_effect = Exception("API Error")
        results = summarizer.summarize_articles(
            [{"url": "https://a.com/1", "title": "記事1", "summary": "概要1"}]
        )
        assert len(results) == 1
        assert results[0]["url"] == "https://a.com/1"
        assert results[0]["summary"] is None
        assert "API Error" in results[0]["error"]

    def test_システムプロンプトが日本語要約を指示している(self, summarizer, mock_client):
        summarizer.summarize(title="テスト", content="テスト内容")
        call_kwargs = mock_client.messages.create.call_args[1]
        assert "system" in call_kwargs
        assert "日本語" in call_kwargs["system"]
