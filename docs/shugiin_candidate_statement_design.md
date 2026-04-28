# 候補者発言ページの情報設計

## 目的

候補者の発言を「プラットフォーム別一覧」ではなく、「争点別に比較できる形」で整理する。
同時に、要約だけが独り歩きしないよう、元発言と出典へ戻れる構造を維持する。

## ページ構成

1. ヒーロー
- 対象選挙
- 収録候補者数
- 争点数
- 発言件数
- 最終更新日

2. このページの読み方
- 争点別比較を主軸にする
- 要約と原文を分ける
- 出典優先順位を明示する

3. 争点別比較
- 争点ごとに候補者を横並び表示
- 各候補者ごとに「現時点の整理」を 1 文で表示
- 根拠となる発言件数と最終確認日を表示

4. 発言ログ
- 日付順に発言を表示
- 候補者、争点、プラットフォームで絞り込み
- 元リンクへ遷移可能にする

## データの最小単位

候補者発言ページは、以下 2 種類のデータに分けて持つ。

### 1. candidate_positions

候補者ごとの「争点に対する現時点の整理」。

- `candidate_id`: 候補者 ID
- `topic_id`: 争点 ID
- `stance_label`: 一言ラベル
- `summary`: 要約
- `status`: `supported` / `mixed` / `unclear` / `watch`
- `evidence_ids`: 根拠になる statement の配列
- `updated_at`: 最終整理日時

### 2. statements

出典付きの発言レコード本体。

- `id`: 一意な ID
- `candidate_id`: 候補者 ID
- `topic_id`: 争点 ID
- `platform`: プラットフォーム種別
- `platform_label`: 表示名
- `date`: 発言日または掲載日
- `summary`: 発言の短い要約
- `quote_excerpt`: 原文の短い抜粋
- `source_url`: 元リンク
- `source_title`: 出典名
- `source_type`: `primary` / `secondary`
- `verification_status`: `verified` / `needs_review`
- `notes`: 文脈メモ

## 表示ルール

- 発言は必ず `summary` と `quote_excerpt` を分ける
- `quote_excerpt` は短く保つ
- 1 件だけで断定しない
- 古い発言より新しい発言を優先するが、変化がある場合は両方残す
- 切り抜きや転載ではなく一次ソースを優先する

## 優先する出典

1. 選挙公報
2. 候補者公式サイト
3. 公式 SNS
4. 公式 YouTube / 街頭演説動画
5. 報道記事

## 今回の実装方針

- ページは静的 HTML で追加する
- 候補者基本情報は既存の `js/data/shugiin_tokyo_2026.json` を参照する
- 発言比較専用データは `js/data/shugiin_tokyo_2026_statements.json` に分離する
- まずはサンプル件数で UI と運用ルールを先に固める
