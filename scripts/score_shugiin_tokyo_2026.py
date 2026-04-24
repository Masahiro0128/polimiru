import json
import re
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[1] / "js" / "data" / "shugiin_tokyo_2026.json"

NUM_RE = re.compile(r"\d")
DATE_RE = re.compile(r"(20\d{2}年|\d{1,2}月|\d{1,2}日)")
MONEY_RE = re.compile(r"(億円|万円|予算|財源|税)")
PROCESS_RE = re.compile(r"(条例|制度|改正|導入|実施|実行|創設|廃止|検証)")


def load_data():
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def save_data(payload):
    DATA_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def calc_specificity(text):
    if not text:
        return None
    text = str(text)
    if len(text.strip()) < 10:
        return None

    score = 0
    if NUM_RE.search(text):
        score += 30
    if DATE_RE.search(text):
        score += 20
    if MONEY_RE.search(text):
        score += 25
    if PROCESS_RE.search(text):
        score += 25

    return min(score, 100)


def calc_progress(progress):
    if not progress:
        return None
    total = progress.get("total")
    done = progress.get("done")
    started = progress.get("started")
    if not isinstance(total, int) or total <= 0:
        return None

    done = done if isinstance(done, int) else 0
    started = started if isinstance(started, int) else 0

    score = (done + started * 0.5) / total * 100
    return min(max(int(round(score)), 0), 100)


def calc_transparency(candidate):
    score = 0
    if candidate.get("bulletin_pdf"):
        score += 35
    if candidate.get("url"):
        score += 30
    if candidate.get("source_url"):
        score += 20
    if candidate.get("kana"):
        score += 10
    if candidate.get("party") and candidate.get("party") != "記載なし":
        score += 5
    return min(score, 100)


def calc_overall(candidate):
    role = candidate.get("role")
    specificity = candidate.get("score_specificity")
    progress = candidate.get("score_progress")
    transparency = candidate.get("score_transparency")
    consistency = candidate.get("score_consistency")

    if role == "incumbent":
        parts = []
        if progress is not None:
            parts.append((progress, 0.6))
        if consistency is not None:
            parts.append((consistency, 0.4))
        if len(parts) == 2:
            return int(round(sum(val * weight for val, weight in parts)))

    if role == "challenger":
        if specificity is not None:
            return specificity

    if specificity is not None:
        return specificity

    return None


def main():
    payload = load_data()
    candidates = payload.get("candidates", [])

    for candidate in candidates:
        candidate.setdefault("role", "unknown")
        candidate.setdefault("manifesto_text", "")
        candidate.setdefault("progress", {})
        candidate.setdefault("consistency", {})

        candidate["score_specificity"] = calc_specificity(candidate.get("manifesto_text"))
        candidate["score_progress"] = calc_progress(candidate.get("progress"))
        candidate["score_consistency"] = calc_progress(candidate.get("consistency"))
        candidate["score_transparency"] = calc_transparency(candidate)

        overall = calc_overall(candidate)
        candidate["overall_score"] = overall

        if candidate.get("role") == "unknown":
            candidate["score_status"] = "暫定"
        elif candidate.get("role") == "incumbent" and (candidate["score_progress"] is None or candidate["score_consistency"] is None):
            candidate["score_status"] = "暫定"
        elif candidate.get("role") == "challenger" and candidate["score_specificity"] is None:
            candidate["score_status"] = "暫定"
        else:
            candidate["score_status"] = "算出"

    save_data(payload)


if __name__ == "__main__":
    main()
