#!/usr/bin/env python3
"""
Automated fact-check for politician promise tracking.

Flow:
  1. For each non-final promise, fetch recent articles via Google News RSS (free, no key needed)
  2. Pass headlines + snippets to Gemini 2.0 Flash (free tier, no grounding)
  3. Update status if confidence is high/medium

Setup:
  export GEMINI_API_KEY=your_key   # https://aistudio.google.com/apikey  (free)
  pip install google-genai

Usage:
  python tools/fact_check.py              # all politicians
  python tools/fact_check.py koike        # filename substring match
  python tools/fact_check.py --dry-run    # print only, no save
"""

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: run `pip install google-genai`", file=sys.stderr)
    sys.exit(1)

MODEL = "gemini-2.0-flash"
SCORE_WEIGHT = {"実現": 100, "進行中": 50, "公約": 0, "撤回": 0}
TERMINAL = {"実現", "撤回"}

# 一次情報源として認める公式ドメイン
OFFICIAL_DOMAINS = [
    "site:go.jp",        # 中央省庁全般（kantei, cao, mof, mlit, mhlw...）
    "site:lg.jp",        # 地方自治体全般
    "site:shugiin.go.jp",
    "site:sangiin.go.jp",
    "site:ndl.go.jp",    # 国立国会図書館（会議録）
    "site:jimin.jp",     # 自民党
    "site:cdp-japan.jp", # 立憲民主党
    "site:nippon-ishin.jp", # 日本維新の会
    "site:dpfp.or.jp",   # 国民民主党
    "site:komei.or.jp",  # 公明党
    "site:jcp.or.jp",    # 共産党
]

OFFICIAL_SITE_QUERY = " OR ".join(OFFICIAL_DOMAINS[:6])  # Google RSS は長すぎるとエラー


# ── ニュース取得 ──────────────────────────────────────────

def fetch_news(query: str, max_items: int = 5) -> list[dict]:
    """
    Google News RSS から公式ドメイン限定で記事を取得（APIキー不要）。
    go.jp / lg.jp / 主要政党サイトのみ対象。
    """
    # 一次情報源に絞った検索クエリ
    full_query = f"{query} ({OFFICIAL_SITE_QUERY})"
    encoded = urllib.parse.quote(full_query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=ja&gl=JP&ceid=JP:ja"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            root = ET.fromstring(resp.read())
    except Exception as e:
        return [{"error": str(e)}]

    items = []
    for item in root.findall(".//item")[:max_items]:
        title = (item.findtext("title") or "").strip()
        link  = (item.findtext("link")  or "").strip()
        desc  = re.sub(r"<[^>]+>", "", item.findtext("description") or "").strip()
        pub   = (item.findtext("pubDate") or "").strip()
        items.append({"title": title, "link": link, "snippet": desc[:200], "date": pub})
    return items


def build_news_context(politician_name: str, promises: list[dict]) -> str:
    """各公約についてニュースを取得してコンテキスト文字列を作る。"""
    lines = []
    for p in promises:
        # 政治家名 + 公約キーワードで検索
        keywords = re.sub(r"[（）「」【】・、。]", " ", p["title"])
        keywords = " ".join(keywords.split()[:4])
        query = f"{politician_name} {keywords}"
        articles = fetch_news(query, max_items=3)
        if articles and "error" not in articles[0]:
            lines.append(f"\n[公約] {p['title']}")
            for a in articles:
                lines.append(f"  - {a['date'][:16]}  {a['title']}")
                if a["snippet"]:
                    lines.append(f"    {a['snippet']}")
                lines.append(f"    URL: {a['link']}")
        time.sleep(0.5)  # レート制限を避ける
    return "\n".join(lines) if lines else "（ニュースなし）"


# ── スコア再計算 ──────────────────────────────────────────

def recompute_cycle(cycle: dict) -> None:
    highlights = cycle.get("highlights", [])
    if not highlights:
        return
    total = len(highlights)
    weights = [SCORE_WEIGHT.get(h["status"], 0) for h in highlights]
    cycle.update({
        "total":    total,
        "done":     sum(1 for h in highlights if h["status"] == "実現"),
        "started":  sum(1 for h in highlights if h["status"] == "進行中"),
        "pending":  sum(1 for h in highlights if h["status"] == "公約"),
        "score":    round(sum(weights) / total),
        "reviewed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    })


# ── Gemini 判定 ──────────────────────────────────────────

def check_politician(client, data: dict, dry_run: bool) -> bool:
    name = data.get("name", "?")
    changed = False

    for cycle in data.get("promise_cycles", []):
        highlights = cycle.get("highlights", [])
        checkable = [
            {"idx": i, "title": h["title"], "current_status": h["status"]}
            for i, h in enumerate(highlights)
            if h["status"] not in TERMINAL
        ]
        if not checkable:
            continue

        print(f"  ニュース取得中... ({len(checkable)}件)")
        news_context = build_news_context(name, checkable)

        prompt = f"""あなたは日本の政治ファクトチェッカーです。現在の日付は2026年4月です。

政治家: {name}
公約セット: {cycle.get('title', '')}

【取得した一次情報（go.jp / lg.jp / 公式党サイト 限定）】
{news_context}

【判定対象の公約】
{json.dumps(checkable, ensure_ascii=False, indent=2)}

## 重要なルール
- 根拠として使えるのは **政府・自治体・議会・公式政党サイト（go.jp / lg.jp / 公式党ドメイン）のみ**
- ニュース記事・まとめサイト・SNS・Wikipedia は根拠として不可
- 上記の一次情報源で明確な根拠が見つからない場合は必ず "変化なし" にしてください
- 確信が低い場合も "変化なし" を選んでください（誤更新よりも未更新の方が安全）

JSONのみ返答（コードブロック不要）:
[
  {{
    "idx": <元のidx>,
    "new_status": "実現" | "進行中" | "公約" | "撤回" | "変化なし",
    "confidence": "high" | "medium" | "low",
    "evidence_url": "<go.jp か lg.jp か公式党サイトのURL、なければ空文字>",
    "note": "<判断理由を1文。必ず一次情報源を明記>"
  }}
]"""

        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.1),
            )
            text = response.text.strip()
        except Exception as e:
            print(f"  ⚠ Gemini APIエラー ({name}): {e}", file=sys.stderr)
            continue

        text = re.sub(r"```[a-z]*\n?", "", text).strip().rstrip("`")
        try:
            results = json.loads(text)
        except json.JSONDecodeError:
            m = re.search(r"\[[\s\S]+\]", text)
            if not m:
                print(f"  ⚠ レスポンスのパース失敗 ({name})", file=sys.stderr)
                print(f"  Raw: {text[:300]}", file=sys.stderr)
                continue
            results = json.loads(m.group())

        for r in results:
            idx        = r.get("idx")
            new_status = r.get("new_status", "変化なし")
            confidence = r.get("confidence", "low")

            if new_status == "変化なし" or confidence == "low":
                continue
            if idx is None or not (0 <= idx < len(highlights)):
                continue

            old_status = highlights[idx]["status"]
            if new_status == old_status:
                continue

            print(
                f"  [{name}] {highlights[idx]['title'][:45]}\n"
                f"    {old_status} → {new_status}  ({confidence})\n"
                f"    {r.get('note', '')}"
            )
            if r.get("evidence_url"):
                print(f"    {r['evidence_url']}")

            if not dry_run:
                highlights[idx]["status"] = new_status
                if r.get("evidence_url"):
                    highlights[idx]["evidence_url"] = r["evidence_url"]
                changed = True

        if changed and not dry_run:
            recompute_cycle(cycle)

    return changed


# ── エントリポイント ──────────────────────────────────────

def main() -> int:
    args = sys.argv[1:]
    dry_run    = "--dry-run" in args
    filter_arg = next((a for a in args if not a.startswith("--")), None)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY が未設定です。\nhttps://aistudio.google.com/apikey で無料取得できます。", file=sys.stderr)
        return 1

    client = genai.Client(api_key=api_key)

    data_dir = Path(__file__).parent.parent / "data" / "politicians"
    json_files = sorted(data_dir.glob("*.json"))
    if filter_arg:
        json_files = [f for f in json_files if filter_arg.lower() in f.stem.lower()]

    if not json_files:
        print("対象ファイルなし。")
        return 0

    print(f"{'[DRY RUN] ' if dry_run else ''}対象: {len(json_files)} 人\n")

    updated = 0
    for path in json_files:
        print(f"→ {path.stem}")
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            if check_politician(client, data, dry_run):
                if not dry_run:
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                        f.write("\n")
                    print(f"  ✓ {path.name} 保存完了")
                updated += 1
        except Exception as e:
            print(f"  ⚠ {path.name}: {e}", file=sys.stderr)

    print(f"\n完了。{updated}/{len(json_files)} 件{'（ドライラン）' if dry_run else '更新'}。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
