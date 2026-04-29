# 政治家ファクトチェック・データ更新

引数: `$ARGUMENTS` （政治家のID。例: `akazawa-ryosei`）

## あなたのタスク

`data/politicians/$ARGUMENTS.json` の `promise_cycles` を、Webリサーチに基づいてファクトチェックし、粒度を上げて更新してください。

### ステップ1: 現状把握

`data/politicians/$ARGUMENTS.json` を読み込み、現在の promise_cycles の内容・項目数・スコアを確認する。

### ステップ2: Webリサーチ（並列で実施）

以下を WebSearch で調べる：

1. `{名前} {役職} 2025 2026 公約 政策 発言 実績`
2. `{名前} {担当省庁} 記者会見 2026 具体的施策`
3. `{名前} {主要政策テーマ} 進捗 達成 予算 法案`

### ステップ3: 粒度の高いデータに更新

以下の基準で `promise_cycles[0].highlights` を書き直す：

**各 highlight の必須フィールド：**
- `title`: 具体的な政策名（「〇〇を推進」でなく「〇〇法に基づき△△億円を□□に補助」のレベル）
- `category`: エネルギー／半導体／経済安保／中小企業 など
- `status`: 以下のいずれか
  - `実現` — 法律成立・予算確定・事業完了など具体的な成果が確認できる
  - `進行中` — 担当大臣として着手・予算執行・会議開催など動きがある
  - `公約` — 就任時の方針表明のみで具体的な動きが未確認
  - `不明` — 情報不足
- `evidence_source.title`: 出典記事・会見名
- `evidence_source.note`: 具体的な数値・日付・発言を含む1〜2文の説明
- `evidence_source.accessed`: `2026-04-29`（今日）
- `evidence_url`: 一次情報に近いURL（METI公式・NHK・日経など）

**スコア計算：**
```
score = round((done×100 + started×50) / (total×100) * 100)
```

**最低10項目**を目指す。現状の項目は保持しつつ細分化・追加する。

### ステップ4: JSONを更新して deploy

1. `data/politicians/$ARGUMENTS.json` の `promise_cycles` を更新
2. `python3 scripts/deploy.py` を実行（OGP画像再生成 + SEO更新）

### 出力

- 更新前後の項目数・スコアの比較
- 新たに判明したファクト（特に「実現」判定になったもの）のサマリー
