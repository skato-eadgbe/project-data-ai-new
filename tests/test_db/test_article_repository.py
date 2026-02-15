import sqlite3

import pytest

from src.collector.rss_collector import Article
from src.db.article_repository import ArticleRepository


@pytest.fixture
def repo(tmp_path):
    db_path = str(tmp_path / "test.db")
    return ArticleRepository(db_path)


class TestArticleRepository:
    def test_テーブルが自動作成される(self, repo):
        conn = sqlite3.connect(repo.db_path)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='articles'"
        )
        assert cursor.fetchone() is not None
        conn.close()

    def test_記事を保存できる(self, repo):
        article = Article(
            title="Test Article",
            url="https://example.com/1",
            summary="Summary",
            source="TestSource",
            published="2026-01-01",
        )
        repo.save(article)
        articles = repo.get_all()
        assert len(articles) == 1
        assert articles[0]["title"] == "Test Article"

    def test_同一URLの記事は重複保存されない(self, repo):
        article = Article(
            title="Test",
            url="https://example.com/dup",
            summary="Summary",
            source="Source",
            published="2026-01-01",
        )
        repo.save(article)
        repo.save(article)
        articles = repo.get_all()
        assert len(articles) == 1

    def test_複数記事を一括保存できる(self, repo):
        articles = [
            Article("A1", "https://a.com/1", "S1", "Src1", "2026-01-01"),
            Article("A2", "https://a.com/2", "S2", "Src2", "2026-01-02"),
            Article("A3", "https://a.com/3", "S3", "Src3", "2026-01-03"),
        ]
        saved_count = repo.save_many(articles)
        assert saved_count == 3
        assert len(repo.get_all()) == 3

    def test_一括保存で重複はスキップされる(self, repo):
        article = Article("A1", "https://a.com/1", "S1", "Src1", "2026-01-01")
        repo.save(article)
        articles = [
            Article("A1", "https://a.com/1", "S1", "Src1", "2026-01-01"),
            Article("A2", "https://a.com/2", "S2", "Src2", "2026-01-02"),
        ]
        saved_count = repo.save_many(articles)
        assert saved_count == 1
        assert len(repo.get_all()) == 2

    def test_URLで記事の存在確認ができる(self, repo):
        article = Article("T", "https://a.com/exists", "S", "Src", "2026-01-01")
        assert repo.exists("https://a.com/exists") is False
        repo.save(article)
        assert repo.exists("https://a.com/exists") is True

    def test_未要約の記事一覧を取得できる(self, repo):
        articles = [
            Article("A1", "https://a.com/1", "S1", "Src1", "2026-01-01"),
            Article("A2", "https://a.com/2", "S2", "Src2", "2026-01-02"),
        ]
        repo.save_many(articles)
        repo.mark_as_summarized("https://a.com/1")
        unsummarized = repo.get_unsummarized()
        assert len(unsummarized) == 1
        assert unsummarized[0]["url"] == "https://a.com/2"
