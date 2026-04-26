#!/usr/bin/env python3
"""
Automated fact-check for politician promise tracking.

Uses Gemini 2.0 Flash (free tier) with Google Search grounding to assess
whether promise statuses have changed, then updates JSON files in place.

Free tier: 1,500 requests/day — ample for weekly runs.

Setup:
  1. Get free API key: https://aistudio.google.com/apikey
  2. export GEMINI_API_KEY=your_key
  3. pip install google-genai

Usage:
  python tools/fact_check.py              # check all politicians
  python tools/fact_check.py koike        # match by filename substring
  python tools/fact_check.py --dry-run    # print findings without saving
"""

import json
import os
import re
import sys
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


def recompute_cycle(cycle: dict) -> None:
    highlights = cycle.get("highlights", [])
    if not highlights:
        return
    total = len(highlights)
    weights = [SCORE_WEIGHT.get(h["status"], 0) for h in highlights]
    cycle.update({
        "total": total,
        "done":    sum(1 for h in highlights if h["status"] == "実現"),
        "started": sum(1 for h in highlights if h["status"] == "進行中"),
        "pending": sum(1 for h in highlights if h["status"] == "公約"),
        "score":   round(sum(weights) / total),
        "reviewed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    })


def check_politician(client: "genai.Client", data: dict, dry_run: bool) -> bool:
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

        prompt = f"""あなたは日本の政治ファクトチェッカーです。現在の日付は2026年4月です。

政治家: {name}
公約セット: {cycle.get('title', '')}

以下の公約について、Google検索で最新情報を調べ、2026年4月時点の達成状況を判定してください。
確信が持てない場合は "変化なし" を選んでください。

公約リスト:
{json.dumps(checkable, ensure_ascii=False, indent=2)}

回答はJSONのみ（コードブロック不要）:
[
  {{
    "idx": <元のidx>,
    "new_status": "実現" | "進行中" | "公約" | "撤回" | "変化なし",
    "confidence": "high" | "medium" | "low",
    "evidence_url": "<根拠となるニュースURL、なければ空文字>",
    "note": "<判断理由を1文>"
  }}
]"""

        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0.1,
                ),
            )
            text = response.text.strip()
        except Exception as e:
            print(f"  ⚠ API error for {name}: {e}", file=sys.stderr)
            continue

        # Strip markdown fences if present
        text = re.sub(r"```[a-z]*\n?", "", text).strip().rstrip("`")
        try:
            results = json.loads(text)
        except json.JSONDecodeError:
            m = re.search(r"\[[\s\S]+\]", text)
            if not m:
                print(f"  ⚠ Could not parse response for {name}", file=sys.stderr)
                continue
            try:
                results = json.loads(m.group())
            except json.JSONDecodeError:
                print(f"  ⚠ JSON parse failed for {name}", file=sys.stderr)
                continue

        for r in results:
            idx = r.get("idx")
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


def main() -> int:
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    filter_arg = next((a for a in args if not a.startswith("--")), None)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY is not set.\nGet a free key at https://aistudio.google.com/apikey", file=sys.stderr)
        return 1

    client = genai.Client(api_key=api_key)

    data_dir = Path(__file__).parent.parent / "data" / "politicians"
    json_files = sorted(data_dir.glob("*.json"))
    if filter_arg:
        json_files = [f for f in json_files if filter_arg.lower() in f.stem.lower()]

    if not json_files:
        print("No files to process.")
        return 0

    print(f"{'[DRY RUN] ' if dry_run else ''}Checking {len(json_files)} politician file(s)...\n")

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
                    print(f"  ✓ {path.name} saved")
                updated += 1
        except Exception as e:
            print(f"  ⚠ {path.name}: {e}", file=sys.stderr)

    print(f"\nDone. {updated}/{len(json_files)} file(s) {'would be ' if dry_run else ''}updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
