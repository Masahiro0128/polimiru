"""
大阪2027 知事選・市長選 候補者データ自動更新スクリプト

使い方:
  python scripts/update_osaka_2027.py --election governor
  python scripts/update_osaka_2027.py --election mayor
  python scripts/update_osaka_2027.py --election all   (両方)

動作:
  1. 選管サイトを確認し、2027年選挙の候補者ページが公開されていれば取得
  2. 未公開の場合は既存データを保持したまま last_updated のみ更新
  3. 新候補者が増えた場合はindex.jsonに追加（既存データは上書きしない）
  4. candidates/{id}.json が存在しなければ空テンプレートで作成
"""

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]

ELECTION_CONFIG = {
    "governor": {
        "key":        "osaka_2027_governor",
        "label":      "大阪府知事選挙 2027",
        "index_json": ROOT / "js/data/osaka_2027_governor/index.json",
        "cand_dir":   ROOT / "js/data/osaka_2027_governor/candidates",
        "senkan_url": "https://www.pref.osaka.lg.jp/senkan/",
        "search_keywords": ["知事", "2027", "chijisen"],
        "source_note": "大阪府選挙管理委員会",
        "election_day": "2027年4月（予定）",
    },
    "mayor": {
        "key":        "osaka_2027_mayor",
        "label":      "大阪市長選挙 2027",
        "index_json": ROOT / "js/data/osaka_2027_mayor/index.json",
        "cand_dir":   ROOT / "js/data/osaka_2027_mayor/candidates",
        "senkan_url": "https://www.city.osaka.lg.jp/senkyokanri/",
        "search_keywords": ["市長", "2027", "shichosen"],
        "source_note": "大阪市選挙管理委員会",
        "election_day": "2027年4月（予定）",
    },
}


# ------------------------------------------------------------------
#  HTTP
# ------------------------------------------------------------------
def fetch_html(url: str) -> str | None:
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent": "polimiru-bot/1.0"})
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except Exception as e:
        print(f"[WARN] fetch failed: {url} → {e}")
        return None


# ------------------------------------------------------------------
#  選管トップから2027年選挙ページのURLを探す
# ------------------------------------------------------------------
def find_election_page(senkan_url: str, keywords: list[str]) -> str | None:
    html = fetch_html(senkan_url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        href = a["href"]
        if any(kw in text or kw in href for kw in keywords):
            return urljoin(senkan_url, href)
    return None


# ------------------------------------------------------------------
#  候補者テーブルをパース（選管の標準的なHTML構造を想定）
# ------------------------------------------------------------------
def parse_candidates_from_page(url: str) -> list[dict]:
    html = fetch_html(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    candidates = []
    table = soup.find("table")
    if not table:
        return []

    rows = table.find_all("tr")
    for i, row in enumerate(rows[1:], start=1):
        cells = [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"])]
        if len(cells) < 2:
            continue

        name_raw = cells[0] if cells[0] else cells[1]
        party    = cells[1] if len(cells) > 1 else ""
        website  = next((c for c in cells[2:] if c.startswith("http")), "")

        kana = ""
        if "（" in name_raw and "）" in name_raw:
            m = re.search(r"（(.+?)）", name_raw)
            if m:
                kana     = m.group(1)
                name_raw = name_raw[:name_raw.index("（")].strip()

        candidates.append({
            "name":  name_raw,
            "kana":  kana,
            "party": party,
            "url":   website,
        })

    return candidates


# ------------------------------------------------------------------
#  index.json の読み込み / 保存
# ------------------------------------------------------------------
def load_index(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text("utf-8"))
        except json.JSONDecodeError:
            pass
    return {"meta": {}, "candidates": []}


def save_index(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf-8")


# ------------------------------------------------------------------
#  candidates/{id}.json のテンプレート作成
# ------------------------------------------------------------------
def ensure_candidate_detail(cand_dir: Path, cand: dict) -> None:
    cid  = cand["id"]
    path = cand_dir / f"{cid}.json"
    if path.exists():
        return

    detail = {
        "id":    cid,
        "name":  cand["name"],
        "kana":  cand.get("kana", ""),
        "party": cand.get("party", ""),
        "role":  cand.get("role", "challenger"),
        "age":   cand.get("age"),
        "image": cand.get("image", ""),
        "confirmed": cand.get("confirmed", False),
        "note":  "",
        "past_roles":  [],
        "source_urls": [],
        "manifesto_text":   "",
        "manifesto_source": "",
        "progress":    {},
        "consistency": {},
        "score_breakdown": {
            "incumbent":  {"progress": None, "consistency": None, "total": None},
            "challenger": {"specificity": None, "total": None},
        },
        "score_status": "暫定",
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(detail, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(f"  [NEW] {path.name}")


# ------------------------------------------------------------------
#  名前ベースのID生成
# ------------------------------------------------------------------
def make_id(name: str) -> str:
    import unicodedata
    name = name.replace("　", "").replace(" ", "")
    return unicodedata.normalize("NFKC", name).lower()


# ------------------------------------------------------------------
#  メイン処理（1選挙分）
# ------------------------------------------------------------------
def update_election(cfg: dict) -> None:
    label = cfg["label"]
    print(f"\n=== {label} ===")

    existing = load_index(cfg["index_json"])
    existing_by_name = {c["name"]: c for c in existing.get("candidates", [])}

    # 選管ページ探索
    election_page = find_election_page(cfg["senkan_url"], cfg["search_keywords"])

    new_candidates: list[dict] = []
    if election_page:
        print(f"  選挙ページ発見: {election_page}")
        raw = parse_candidates_from_page(election_page)
        print(f"  候補者 {len(raw)} 名取得")
        for r in raw:
            if r["name"] in existing_by_name:
                merged = existing_by_name[r["name"]]
                merged.setdefault("url", r["url"])
                merged.setdefault("party", r["party"])
                new_candidates.append(merged)
            else:
                cid = make_id(r["name"])
                new_candidates.append({
                    "id":           cid,
                    "name":         r["name"],
                    "kana":         r.get("kana", ""),
                    "party":        r.get("party", ""),
                    "role":         "challenger",
                    "age":          None,
                    "image":        "",
                    "score_incumbent":  None,
                    "score_challenger": None,
                    "score_status": "暫定",
                    "confirmed":    True,
                    "note":         "",
                })
                print(f"  [ADD] {r['name']}")
    else:
        print("  候補者ページ未公開。既存データを保持。")
        new_candidates = existing.get("candidates", [])

    # candidates/{id}.json を作成（未存在のものだけ）
    cfg["cand_dir"].mkdir(parents=True, exist_ok=True)
    for c in new_candidates:
        ensure_candidate_detail(cfg["cand_dir"], c)

    payload = {
        "meta": {
            "election":       cfg["label"],
            "election_day":   cfg["election_day"],
            "source_note":    cfg["source_note"],
            "source_index_url": cfg["senkan_url"],
            "last_updated":   datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "status":         "confirmed" if election_page else "upcoming",
        },
        "candidates": new_candidates,
    }
    save_index(cfg["index_json"], payload)
    print(f"  保存完了: {cfg['index_json']}")


# ------------------------------------------------------------------
#  エントリポイント
# ------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--election", choices=["governor", "mayor", "all"], default="all")
    args = parser.parse_args()

    targets = list(ELECTION_CONFIG.values()) if args.election == "all" \
        else [ELECTION_CONFIG[args.election]]

    for cfg in targets:
        update_election(cfg)


if __name__ == "__main__":
    main()
