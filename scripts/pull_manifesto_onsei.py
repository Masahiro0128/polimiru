import json
import re
from pathlib import Path
from urllib.parse import urljoin

import pdfplumber
import requests
from bs4 import BeautifulSoup

DATA_PATH = Path(__file__).resolve().parents[1] / "js" / "data" / "shugiin_tokyo_2026.json"

KEYWORDS = [
    "予算",
    "財源",
    "条例",
    "実施",
    "拡充",
    "削減",
    "改革",
    "支援",
    "福祉",
    "医療",
    "教育",
    "子育て",
    "交通",
    "防災",
    "環境",
    "経済",
    "雇用",
    "住宅",
    "税",
    "給付",
]
SKIP_TERMS = [
    "プロフィール",
    "生まれ",
    "出身",
    "学部",
    "経歴",
    "当選",
    "委員会",
    "所属",
    "顧問",
]


def load_data():
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def save_data(payload):
    DATA_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def normalize_name(text):
    text = text.replace("　", " ")
    text = re.sub(r"\s+", "", text)
    return text


def fetch_html(url):
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding
    return resp.text


def extract_onsei_links(source_url):
    html = fetch_html(source_url)
    soup = BeautifulSoup(html, "html.parser")

    rows = []
    pending_name = None

    for tr in soup.find_all("tr"):
        text = tr.get_text(" ", strip=True)
        links = [a.get("href", "") for a in tr.find_all("a")]

        # Candidate row: name in first/second column and a PDF link without onsei.
        if any(href.endswith(".pdf") and "onsei" not in href for href in links):
            tds = tr.find_all("td")
            name = ""
            if len(tds) > 1:
                name = tds[1].get_text(strip=True)
            elif tds:
                name = tds[0].get_text(strip=True)
            if name:
                pending_name = name.split("(")[0]
            continue

        # Onsei row follows
        if "読み上げ対応" in text or any("onsei" in href for href in links):
            onsei = next((href for href in links if "onsei" in href), "")
            if pending_name and onsei:
                rows.append({"name": pending_name, "link": urljoin(source_url, onsei)})
                pending_name = None

    return rows


def extract_text_from_pdf(url):
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    tmp_path = Path("/tmp/manifesto_onsei.pdf")
    tmp_path.write_bytes(resp.content)

    text = []
    with pdfplumber.open(str(tmp_path)) as pdf:
        for page in pdf.pages:
            text.append(page.extract_text() or "")
    return "\n".join(text)


def clean_text(text):
    text = text.replace("\u3000", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def summarize(text, limit=160):
    if not text:
        return ""
    sentences = re.split(r"[。．\.\n]", text)
    scored = []
    for sentence in sentences:
        s = sentence.strip()
        if len(s) < 6:
            continue
        if any(term in s for term in SKIP_TERMS):
            continue
        score = sum(1 for k in KEYWORDS if k in s)
        if re.search(r"\d", s):
            score += 2
        scored.append((score, s))

    if not scored:
        return text[:limit]

    scored.sort(key=lambda x: (-x[0], -len(x[1])))
    picked = [s for _, s in scored[:2]]
    summary = " / ".join(picked)
    return summary[:limit]


def main():
    payload = load_data()
    candidates = payload.get("candidates", [])

    by_district = {}
    for cand in candidates:
        by_district.setdefault(cand.get("district"), []).append(cand)

    for district, district_candidates in by_district.items():
        if not district_candidates:
            continue
        district_no = district_candidates[0].get("district_no")
        if district_no not in {1, 2, 3, 4, 5}:
            continue

        source_url = district_candidates[0].get("source_url")
        if not source_url:
            continue

        rows = extract_onsei_links(source_url)
        if not rows:
            continue

        mapping = {normalize_name(r["name"]): r for r in rows}

        for cand in district_candidates:
            name_key = normalize_name(cand.get("name", ""))
            row = mapping.get(name_key)
            if not row:
                continue

            raw = extract_text_from_pdf(row["link"])
            cleaned = clean_text(raw)
            summary = summarize(cleaned)

            cand["manifesto_text_raw"] = cleaned
            cand["manifesto_text"] = summary
            cand["manifesto_source"] = row["link"]

        print(f"[OK] {district} manifesto text updated")

    save_data(payload)


if __name__ == "__main__":
    main()
