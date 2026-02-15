# CLAUDE.md - 開発ルール・ガイドライン

## プロジェクト概要

Data・AI関連のニュースを自動収集し、Claude APIで要約してNoteに自動投稿するアプリケーション。

## 技術スタック

| カテゴリ | 技術 |
|---------|------|
| 言語 | Python 3.12+ |
| ニュース収集 | RSS / API (feedparser) |
| AI要約 | Claude API (anthropic) |
| Note投稿 | Playwright（ブラウザ自動操作） |
| データベース | SQLite |
| スケジューリング | GitHub Actions (cron) |
| テスト | pytest |
| リンター / フォーマッター | ruff |

## 開発ワークフロー

すべてのタスクは以下のサイクルで進める：

1. **探索（Explore）** — 関連コードを読み、現状を把握する。この段階ではコードを書かない
2. **計画（Plan）** — 実装方針を整理する。複雑なタスクでは `think hard` や `ultrathink` を活用して拡張思考を行う
3. **実装（Implement）** — 計画に沿ってコードを書く（TDDに従う）
4. **コミット（Commit）** — 変更をコミットする

## テスト駆動開発（TDD）

コードの実装は必ず以下の手順で行う：

1. 期待する入出力を具体的に定義する
2. テストコードを先に作成する
3. テストが失敗することを確認する（Red）
4. テストが通る最小限の実装を行う（Green）
5. コードをリファクタリングする（Refactor）
6. すべてのテストが通ることを確認してからコミットする

### テストに関するルール

- 新機能の追加時は必ずテストを先に書く
- バグ修正時は、まずバグを再現するテストを書いてから修正する
- テストに過度に最適化された実装を避け、汎用性の高いコードを書く
- カバレッジを意識し、正常系・異常系・境界値をテストする

## コーディング規約

- 関数・変数名: `snake_case`
- クラス名: `PascalCase`
- 定数: `UPPER_SNAKE_CASE`
- ファイル名: `snake_case`
- 意味のある命名を心がけ、略語を避ける
- 1つの関数は1つの責務に集中させる

## コミットルール

- コミットメッセージは日本語で記述する
- プレフィックスを付ける: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`
- 1コミット = 1つの論理的変更
- コミット前に必ずすべてのテストを実行し、パスすることを確認する

## コードレビュー・品質チェック

- 実装完了後、型チェック・リンターを実行する
- 変更が既存のテストを壊していないか確認する
- セキュリティ上のリスク（ハードコードされた秘密情報、インジェクションなど）がないか確認する

## ディレクトリ構成

```
project-data-ai-new/
├── CLAUDE.md
├── README.md
├── pyproject.toml
├── src/
│   ├── collector/     # ニュース収集
│   ├── summarizer/    # AI要約
│   ├── publisher/     # Note投稿
│   ├── db/            # データベース操作
│   └── main.py
├── tests/
│   ├── test_collector/
│   ├── test_summarizer/
│   ├── test_publisher/
│   └── test_db/
├── .github/
│   └── workflows/     # GitHub Actions
└── config/            # 設定ファイル
```

## 共通コマンド

```bash
# テスト実行
pytest

# テスト実行（カバレッジ付き）
pytest --cov=src

# リンター実行
ruff check src/ tests/

# フォーマッター実行
ruff format src/ tests/
```
