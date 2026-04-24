import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

OUTPUT_PATH = Path(__file__).resolve().parents[1] / "js" / "data" / "shugiin_tokyo_2026.json"
INDEX_URL = "https://r8shugiinsen.metro.tokyo.lg.jp/constituency/index.html"


def load_existing_candidates():
    if not OUTPUT_PATH.exists():
        return {}
    try:
        data = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    candidates = data.get("candidates", [])
    return {cand.get("id"): cand for cand in candidates if cand.get("id")}


def fetch_html(url):
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    return response.text


def parse_index():
    html = fetch_html(INDEX_URL)
    soup = BeautifulSoup(html, "html.parser")

    district_links = []
    for anchor in soup.find_all("a"):
        href = anchor.get("href", "")
        text = anchor.get_text(strip=True)
        if "candidate" in href and text.startswith("候補者の氏名"):
            district_links.append(urljoin(INDEX_URL, href))

    bulletin_links = {}
    for anchor in soup.find_all("a"):
        href = anchor.get("href", "")
        text = anchor.get_text(strip=True)
        if "選挙公報" in text and href.lower().endswith(".pdf"):
            full = urljoin(INDEX_URL, href)
            label = text.replace("選挙公報", "").strip()
            bulletin_links[label] = full

    return district_links, bulletin_links


def parse_candidates(page_url):
    html = fetch_html(page_url)
    soup = BeautifulSoup(html, "html.parser")

    heading = soup.find("h1")
    district_label = heading.get_text(strip=True) if heading else ""

    bulletin_pdf = None
    for anchor in soup.find_all("a"):
        text = anchor.get_text(strip=True)
        href = anchor.get("href", "")
        if "選挙公報" in text and href.lower().endswith(".pdf"):
            bulletin_pdf = urljoin(page_url, href)
            break

    table = soup.find("table")
    if not table:
        return district_label, bulletin_pdf, []

    rows = table.find_all("tr")
    candidates = []
    for row in rows[1:]:
        cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
        if len(cells) < 4:
            continue

        number = cells[0]
        name_raw = cells[1]
        party = cells[2]
        website = cells[3] if cells[3] != "なし" else ""

        kana = ""
        if "(" in name_raw and ")" in name_raw:
            name, kana_part = name_raw.split("(", 1)
            kana = kana_part.replace(")", "").strip()
            name_raw = name.strip()

        candidates.append(
            {
                "number": number.strip(),
                "name": name_raw,
                "kana": kana,
                "party": party,
                "website": website,
            }
        )

    return district_label, bulletin_pdf, candidates


def build_payload():
    district_links, _ = parse_index()
    all_candidates = []
    existing_candidates = load_existing_candidates()
    for link in district_links:
        district_label, bulletin_pdf, candidates = parse_candidates(link)
        for candidate in candidates:
            district_number = "".join([c for c in district_label if c.isdigit()])
            order = int(candidate["number"]) if candidate["number"].isdigit() else 0
            candidate_id = int(f"{district_number or '0'}{order:02d}")
            existing = existing_candidates.get(candidate_id, {})
            image = existing.get("image", "")

            score_transparency = 0
            if bulletin_pdf:
                score_transparency += 35
            if candidate["website"]:
                score_transparency += 30
            if link:
                score_transparency += 20
            if candidate["kana"]:
                score_transparency += 10
            if candidate["party"]:
                score_transparency += 5
            score_transparency = min(score_transparency, 100)

            merged = {
                "id": candidate_id,
                "name": candidate["name"],
                "kana": candidate["kana"],
                "party": candidate["party"] or "記載なし",
                "district": district_label,
                "district_no": int(district_number) if district_number.isdigit() else None,
                "desc": f"小選挙区 {district_label}",
                "url": candidate["website"],
                "source_url": link,
                "bulletin_pdf": bulletin_pdf,
                "image": image,
                "score_transparency": score_transparency,
            }

            # Preserve existing enriched fields.
            for key in [
                "role",
                "manifesto_text",
                "manifesto_text_raw",
                "manifesto_source",
                "progress",
                "score_specificity",
                "score_progress",
                "overall_score",
                "score_status",
            ]:
                if key in existing:
                    merged[key] = existing[key]

            all_candidates.append(merged)

    all_candidates.sort(
        key=lambda item: (
            item["district_no"] if item["district_no"] is not None else 999,
            item["id"],
        )
    )

    return {
        "meta": {
            "election": "衆議院議員総選挙（東京）",
            "announced": "2026-01-27",
            "election_day": "2026-02-08",
            "source_note": "東京都選挙管理委員会の候補者一覧を基に更新",
            "source_index_url": INDEX_URL,
            "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "candidates": all_candidates,
    }


def main():
    payload = build_payload()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
