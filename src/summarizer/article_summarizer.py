import anthropic

SYSTEM_PROMPT = (
    "あなたはData・AI分野の専門ニュースライターです。"
    "与えられた記事を日本語で簡潔に要約してください。"
    "要約は3〜5文程度で、技術的なポイントと影響を中心にまとめてください。"
    "読者はデータエンジニアやAIエンジニアを想定しています。"
)

DEFAULT_MODEL = "claude-sonnet-4-5-20250929"


class ArticleSummarizer:
    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def summarize(self, title: str, content: str) -> str:
        user_message = f"タイトル: {title}\n\n本文: {content}" if content else f"タイトル: {title}"
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text

    def summarize_articles(self, articles: list[dict]) -> list[dict]:
        results = []
        for article in articles:
            try:
                summary = self.summarize(
                    title=article["title"],
                    content=article.get("summary", ""),
                )
                results.append({"url": article["url"], "summary": summary})
            except Exception as e:
                results.append({"url": article["url"], "summary": None, "error": str(e)})
        return results
