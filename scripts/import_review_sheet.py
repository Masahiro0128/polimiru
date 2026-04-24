"""
Googleスプレッドシートのレビュー結果をJSONに反映するスクリプト

使い方:
  1. Googleスプレッドシートを CSV でエクスポート
  2. python scripts/import_review_sheet.py --csv tmp/review_sheets/promises_yoshimura_2023.csv
                                           --json js/data/osaka_2027_governor/candidates/yoshimura.json

スプレッドシートの「達成状況」列に入力する値:
  完了    → 公約が実行・達成された
  着手    → 取り組みが始まっている
  未着手  → 具体的な動きが確認できない
  不明    → 情報が不足していて判定できない
  （空欄）→ 未レビュー
"""

import argparse
import csv
import json
from pathlib import Path

VALID_STATUSES = {"完了", "着手", "未着手", "不明"}

STATUS_SCORE = {
    "完了":   1.0,
    "着手":   0.5,
    "未着手": 0.0,
    "不明":   None,
}


def calc_progress_from_promises(promises: list[dict]) -> dict | None:
    reviewed = [p for p in promises if p.get("status") in VALID_STATUSES]
    if not reviewed:
        return None

    scorable = [p for p in reviewed if p["status"] in ("完了", "着手", "未着手")]
    if not scorable:
        return None

    done    = sum(1 for p in scorable if p["status"] == "完了")
    started = sum(1 for p in scorable if p["status"] == "着手")
    total   = len(scorable)
    score   = int(round((done + started * 0.5) / total * 100))

    return {
        "total":   total,
        "done":    done,
        "started": started,
        "score":   score,
        "reviewed_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
                        .strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv",  required=True, help="レビュー済みCSVのパス")
    parser.add_argument("--json", required=True, help="更新対象の candidates/{id}.json パス")
    args = parser.parse_args()

    csv_path  = Path(args.csv)
    json_path = Path(args.json)

    if not csv_path.exists():
        print(f"[ERROR] CSVが見つかりません: {csv_path}")
        return
    if not json_path.exists():
        print(f"[ERROR] JSONが見つかりません: {json_path}")
        return

    # CSV読み込み
    rows = []
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    if not rows:
        print("[ERROR] CSVが空です")
        return

    print(f"  {len(rows)} 行を読み込みました")

    # JSON読み込み
    data = json.loads(json_path.read_text("utf-8"))
    promises = {p["id"]: p for p in data.get("promises_2023", [])}

    updated = 0
    for row in rows:
        pid    = row.get("公約番号", "").strip()
        status = row.get("達成状況", "").strip()
        ev_url = row.get("証拠URL", "").strip()
        note   = row.get("メモ", "").strip()

        if not pid or pid not in promises:
            continue

        p = promises[pid]

        if status in VALID_STATUSES:
            p["status"] = status
            updated += 1
        elif status == "":
            pass  # 未レビューはそのまま
        else:
            print(f"  [WARN] 不明なステータス '{status}' (行: {pid}) → スキップ")

        if ev_url:
            p["evidence_url"] = ev_url
        if note:
            p["note"] = note

    print(f"  {updated} 件のステータスを更新")

    # 進捗スコアを再計算
    updated_promises = list(promises.values())
    progress = calc_progress_from_promises(updated_promises)
    if progress:
        data["progress"] = progress
        print(f"  公約達成率: {progress['score']} / 100 "
              f"(完了:{progress['done']} 着手:{progress['started']} 計:{progress['total']})")

    data["promises_2023"] = updated_promises
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(f"  保存: {json_path}")


if __name__ == "__main__":
    main()
