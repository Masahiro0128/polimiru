#!/usr/bin/env python3
"""
Automated fact-check for politician promise tracking.

Reads data/politicians/*.json, uses Claude API (with web search) to assess
whether promise statuses have changed, then updates files in place.

Usage:
  export ANTHROPIC_API_KEY=sk-ant-...
  python tools/fact_check.py              # check all
  python tools/fact_check.py koike        # match by filename substring
  python tools/fact_check.py --dry-run    # print findings without saving
"""

import anthropic
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

MODEL = "claude-opus-4-7"

SCORE_WEIGHT = {"実現": 100, "進行中": 50, "公約": 0, "撤回": 0}

TERMINAL_STATUSES = {"実現", "撤回"}


def recompute_cycle(cycle: dict) -> None:
    highlights = cycle.get("highlights", [])
    if not highlights:
        return
    total = len(highlights)
    done = sum(1 for h in highlights if h["status"] == "実現")
    started = sum(1 for h in highlights if h["status"] == "進行中")
    pending = sum(1 for h in highlights if h["status"] == "公約")
    weights = [SCORE_WEIGHT.get(h["status"], 0) for h in highlights]
    score = round(sum(weights) / total) if total else 0

    cycle.update({"total": total, "done": done, "started": started, "pending": pending, "score": score})
    cycle["reviewed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def check_politician(client: anthropic.Anthropic, data: dict, dry_run: bool) -> bool:
    """Check all non-final promises for one politician. Returns True if any change was made."""
    name = data.get("name", "?")
    changed = False

    for cycle in data.get("promise_cycles", []):
        highlights = cycle.get("highlights", [])
        checkable = [
            {"idx": i, "title": h["title"], "current_status": h["status"]}
            for i, h in enumerate(highlights)
            if h["status"] not in TERMINAL_STATUSES
        ]
        if not checkable:
            continue

        prompt = f"""あなたは日本の政治ファクトチェッカーです。現在の日付は2026年4月です。

政治家: {name}
公約セット: {cycle.get('title', '')}

以下の公約について、最新ニュースを必要に応じて検索し、2026年4月時点の達成状況を判定してください。
確信が持てない場合は "変化なし" にしてください。

公約リスト (JSON):
{json.dumps(checkable, ensure_ascii=False, indent=2)}

各公約について以下の形式でJSONを返してください（コードブロック不要）:
[
  {{
    "idx": <元のidx>,
    "new_status": "実現" | "進行中" | "公約" | "撤回" | "変化なし",
    "confidence": "high" | "medium" | "low",
    "evidence_url": "<根拠URL、なければ空文字>",
    "note": "<判断理由を1文で>"
  }}
]"""

        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=2048,
                tools=[{"type": "web_search_20250305", "name": "web_search"}],
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as e:
            print(f"  ⚠ API error for {name}: {e}", file=sys.stderr)
            continue

        # Extract text from final response
        text = ""
        for block in response.content:
            if hasattr(block, "text"):
                text += block.text

        # Parse JSON — strip any stray markdown
        text = re.sub(r"```[a-z]*\n?", "", text).strip()
        try:
            results = json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON array
            m = re.search(r"\[[\s\S]+\]", text)
            if not m:
                print(f"  ⚠ Could not parse response for {name}", file=sys.stderr)
                continue
            results = json.loads(m.group())

        for r in results:
            idx = r.get("idx")
            new_status = r.get("new_status", "変化なし")
            confidence = r.get("confidence", "low")

            if new_status == "変化なし" or confidence == "low":
                continue
            if idx is None or idx >= len(highlights):
                continue

            old_status = highlights[idx]["status"]
            if new_status == old_status:
                continue

            print(
                f"  [{name}] {highlights[idx]['title'][:40]}...\n"
                f"    {old_status} → {new_status}  (conf:{confidence})\n"
                f"    {r.get('note', '')}"
            )

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

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY is not set.", file=sys.stderr)
        return 1

    client = anthropic.Anthropic(api_key=api_key)

    # Resolve data directory relative to this script
    data_dir = Path(__file__).parent.parent / "data" / "politicians"
    if not data_dir.exists():
        print(f"Error: {data_dir} not found.", file=sys.stderr)
        return 1

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
                    print(f"  ✓ Saved {path.name}")
                updated += 1
        except Exception as e:
            print(f"  ⚠ Error: {e}", file=sys.stderr)

    print(f"\nDone. {updated} file(s) {'would be ' if dry_run else ''}updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
