import sqlite3

from src.collector.rss_collector import Article

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    summary TEXT,
    source TEXT NOT NULL,
    published TEXT,
    is_summarized INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""


class ArticleRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(CREATE_TABLE_SQL)

    def save(self, article: Article) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                params = (
                    article.title,
                    article.url,
                    article.summary,
                    article.source,
                    article.published,
                )
                conn.execute(
                    "INSERT INTO articles (title, url, summary, source, published) "
                    "VALUES (?, ?, ?, ?, ?)",
                    params,
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def save_many(self, articles: list[Article]) -> int:
        count = 0
        for article in articles:
            if self.save(article):
                count += 1
        return count

    def exists(self, url: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT 1 FROM articles WHERE url = ?", (url,))
            return cursor.fetchone() is not None

    def get_all(self) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM articles ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def get_unsummarized(self) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM articles WHERE is_summarized = 0 ORDER BY created_at DESC"
            )
            return [dict(row) for row in cursor.fetchall()]

    def update_summary(self, url: str, summary: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE articles SET summary = ? WHERE url = ?", (summary, url))

    def mark_as_summarized(self, url: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE articles SET is_summarized = 1 WHERE url = ?", (url,))
