# 人物カード データ契約

## 基本方針

人物カードは「政治家個人」を単位に蓄積する。選挙ページは候補者カードを表示し、人物カードがある場合は `profile_url` で遷移させる。

## 推奨JSON構造

```json
{
  "id": "person-id",
  "name": "氏名",
  "kana": "かな",
  "party": "政党",
  "party_role": "党役職",
  "area": "選挙区・選出",
  "current_status": "衆議院議員など",
  "photo_url": "https://...",
  "accent": {
    "from": "#123456",
    "to": "#123456",
    "color": "#123456"
  },
  "summary": "短い要約",
  "stats": [
    { "label": "党役職", "value": "代表" }
  ],
  "career": [
    { "period": "2024", "text": "..." }
  ],
  "focus_cards": [
    {
      "context": "政策領域",
      "title": "見るべき論点",
      "desc": "検証観点"
    }
  ],
  "source_urls": [
    { "label": "公式プロフィール", "url": "https://..." }
  ]
}
```

## 選挙候補者JSONとの接続

```json
{
  "id": "candidate-id",
  "person_id": "person-id",
  "profile_url": "../../../politicians/person-id/index.html",
  "name": "氏名"
}
```

## 次に追加する候補

- `pledges`: 個人の公約・政策主張を蓄積
- `activities`: 議会発言、提出議案、要望、会見などの活動履歴
- `election_history`: 出馬した選挙と選挙ページへのリンク
- `verifications`: 公約達成度・言行一致の判定結果
