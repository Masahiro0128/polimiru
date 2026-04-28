# リポジトリ構成メモ

## 公開ページ

- `index.html`
- `about.html`
- `contact.html`
- `method.html`
- `detail.html`
- `elections/`

公開エントリは当面ルートに置く。既存の静的リンクと `js/layout.js` がこの前提で動いているため。

## フロントエンド資産

- `css/`
- `js/`
- `images/`

## 選挙データ

- `js/data/`
- `docs/`

`js/data/` は公開用 JSON、`docs/` は収集ルールや情報設計を置く。

## 調査・収集ツール

- `scripts/`
- `tools/`

`scripts/` は本番データ更新に使う寄りのスクリプト、`tools/` は単発調査や試験用の補助スクリプト。

## 生データ・作業出力

- `data/raw/`
- `tmp/`

`data/raw/` は保存した議事録やスクレイプ結果、`tmp/` は一時画像やデバッグ出力。
