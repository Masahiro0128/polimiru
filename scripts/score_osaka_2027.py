"""
大阪2027 知事選・市長選 スコアリングスクリプト

現職（incumbent）と新人（challenger）で計算ロジックを分ける:
  現職: 公約達成率(60%) + 発言一貫性(40%)
  新人: 公約具体性のみ

使い方:
  python scripts/score_osaka_2027.py --election governor
  python scripts/score_osaka_2027.py --election mayor
  python scripts/score_osaka_2027.py --election all
"""

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ELECTION_CONFIG = {
    "governor": {
        "index_json": ROOT / "js/data/osaka_2027_governor/index.json",
        "cand_dir":   ROOT / "js/data/osaka_2027_governor/candidates",
    },
    "mayor": {
        "index_json": ROOT / "js/data/osaka_2027_mayor/index.json",
        "cand_dir":   ROOT / "js/data/osaka_2027_mayor/candidates",
    },
}

NUM_RE     = re.compile(r"\d")
DATE_RE    = re.compile(r"(20\d{2}年|\d{1,2}月|\d{1,2}日)")
MONEY_RE   = re.compile(r"(億円|万円|予算|財源|税)")
PROCESS_RE = re.compile(r"(条例|制度|改正|導入|実施|実行|創設|廃止|検証)")


# ------------------------------------------------------------------
#  スコア計算
# ------------------------------------------------------------------
def calc_specificity(text: str | None) -> int | None:
    if not text or len(text.strip()) < 10:
        return None
    score = 0
    if NUM_RE.search(text):     score += 30
    if DATE_RE.search(text):    score += 20
    if MONEY_RE.search(text):   score += 25
    if PROCESS_RE.search(text): score += 25
    return min(score, 100)


def calc_progress(d: dict | None) -> int | None:
    if not d:
        return None
    total   = d.get("total")
    done    = d.get("done", 0)
    started = d.get("started", 0)
    if not isinstance(total, int) or total <= 0:
        return None
    return min(max(int(round((done + started * 0.5) / total * 100)), 0), 100)


def calc_incumbent_overall(progress: int | None, consistency: int | None) -> int | None:
    parts = []
    if progress    is not None: parts.append((progress,    0.6))
    if consistency is not None: parts.append((consistency, 0.4))
    if not parts:
        return None
    # 片方だけの場合は比率を正規化
    total_w = sum(w for _, w in parts)
    return int(round(sum(v * w / total_w for v, w in parts)))


# ------------------------------------------------------------------
#  1候補者の詳細JSONをスコアリング
# ------------------------------------------------------------------
def score_candidate(path: Path) -> None:
    try:
        data = json.loads(path.read_text("utf-8"))
    except (json.JSONDecodeError, FileNotFoundError):
        return

    role = data.get("role", "unknown")
    bd   = data.setdefault("score_breakdown", {})

    if role == "incumbent":
        inc        = bd.setdefault("incumbent", {})
        progress    = calc_progress(data.get("progress"))
        consistency = calc_progress(data.get("consistency"))
        inc["progress"]    = progress
        inc["consistency"] = consistency
        inc["total"]       = calc_incumbent_overall(progress, consistency) \
                             or data.get("score_incumbent")

        data["score_incumbent"] = inc["total"]
        data["score_status"]    = "算出" if inc["total"] is not None else "暫定"

    elif role == "challenger":
        ch           = bd.setdefault("challenger", {})
        specificity  = calc_specificity(data.get("manifesto_text"))
        ch["specificity"] = specificity
        ch["total"]       = specificity

        data["score_challenger"] = specificity
        data["score_status"]     = "算出" if specificity is not None else "暫定"

    else:
        data["score_status"] = "暫定"

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf-8")


# ------------------------------------------------------------------
#  index.json のスコアをcandidate詳細JSONと同期
# ------------------------------------------------------------------
def sync_index(index_path: Path, cand_dir: Path) -> None:
    if not index_path.exists():
        return
    try:
        payload = json.loads(index_path.read_text("utf-8"))
    except json.JSONDecodeError:
        return

    changed = False
    for cand in payload.get("candidates", []):
        cid  = cand.get("id")
        path = cand_dir / f"{cid}.json"
        if not path.exists():
            continue
        try:
            detail = json.loads(path.read_text("utf-8"))
        except json.JSONDecodeError:
            continue

        for key in ("score_incumbent", "score_challenger", "score_status"):
            if detail.get(key) != cand.get(key):
                cand[key] = detail.get(key)
                changed = True

    if changed:
        index_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", "utf-8")
        print(f"  index.json 同期完了: {index_path}")


# ------------------------------------------------------------------
#  メイン処理
# ------------------------------------------------------------------
def score_election(cfg: dict) -> None:
    cand_dir = cfg["cand_dir"]
    if not cand_dir.exists():
        print(f"  candidates/ が存在しません: {cand_dir}")
        return

    files = list(cand_dir.glob("*.json"))
    print(f"  {len(files)} 候補者をスコアリング")
    for f in files:
        score_candidate(f)

    sync_index(cfg["index_json"], cand_dir)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--election", choices=["governor", "mayor", "all"], default="all")
    args = parser.parse_args()

    targets = list(ELECTION_CONFIG.items()) if args.election == "all" \
        else [(args.election, ELECTION_CONFIG[args.election])]

    for name, cfg in targets:
        print(f"\n=== {name} スコアリング ===")
        score_election(cfg)


if __name__ == "__main__":
    main()
