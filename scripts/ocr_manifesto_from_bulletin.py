import argparse
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse

import cv2
import numpy as np
import pdfplumber
import requests

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "js" / "data" / "shugiin_tokyo_2026.json"
PDF_DIR = ROOT / "tmp" / "shugiin_bulletins"
OCR_DIR = ROOT / "tmp" / "ocr_manifestos"

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


def load_data():
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def save_data(payload):
    DATA_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def download_pdf(url):
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    filename = Path(urlparse(url).path).name
    target = PDF_DIR / filename
    if target.exists():
        return target
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    target.write_bytes(response.content)
    return target


def find_photo_boxes(image_bgr, roi_x0_ratio=0.70, roi_x1_ratio=0.98):
    height, width = image_bgr.shape[:2]
    x0 = int(width * roi_x0_ratio)
    x1 = int(width * roi_x1_ratio)
    roi = image_bgr[:, x0:x1]

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 31, 10
    )

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        if area < (width * height * 0.002):
            continue
        if area > (width * height * 0.03):
            continue
        aspect = w / h if h else 0
        if aspect < 0.6 or aspect > 1.6:
            continue
        boxes.append((x, y, w, h))

    boxes = sorted(boxes, key=lambda b: b[1])
    return boxes


def split_into_bands(boxes, image_height):
    if not boxes:
        return []
    centers = [y + h / 2 for _, y, _, h in boxes]
    bands = []
    for idx, (x, y, w, h) in enumerate(boxes):
        top = 0
        bottom = image_height
        if idx > 0:
            top = int((centers[idx - 1] + centers[idx]) / 2)
        if idx < len(boxes) - 1:
            bottom = int((centers[idx] + centers[idx + 1]) / 2)
        bands.append((top, bottom))
    return bands


def run_tesseract(image_path, output_base):
    output_base = Path(output_base)
    output_base.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "conda",
        "run",
        "-n",
        "polimiru-ocr",
        "tesseract",
        str(image_path),
        str(output_base),
        "-l",
        "jpn",
        "--psm",
        "6",
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    txt_path = output_base.with_suffix(".txt")
    return txt_path.read_text(encoding="utf-8") if txt_path.exists() else ""


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
    parser = argparse.ArgumentParser(description="OCR manifesto text from bulletin PDFs.")
    parser.add_argument("--district", action="append", default=[], help="District label")
    args = parser.parse_args()

    payload = load_data()
    candidates = payload.get("candidates", [])

    by_district = {}
    for cand in candidates:
        by_district.setdefault(cand.get("district"), []).append(cand)

    districts = list(by_district.keys())
    if args.district:
        districts = [d for d in districts if d in args.district]

    for district in districts:
        district_candidates = by_district.get(district, [])
        if not district_candidates:
            continue
        bulletin = district_candidates[0].get("bulletin_pdf")
        if not bulletin:
            continue

        pdf_path = download_pdf(bulletin)

        with pdfplumber.open(str(pdf_path)) as pdf:
            page = pdf.pages[0]
            image = page.to_image(resolution=300).original

        image_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        boxes = find_photo_boxes(image_bgr)
        if not boxes:
            continue

        bands = split_into_bands(boxes, image_bgr.shape[0])

        district_candidates.sort(key=lambda c: int(str(c.get("id", "0"))[-2:]) if str(c.get("id", "0")).isdigit() else 0)

        for cand, (top, bottom) in zip(district_candidates, bands):
            # Crop full width band
            band = image.crop((0, top, image.width, bottom))
            out_dir = OCR_DIR / district
            out_dir.mkdir(parents=True, exist_ok=True)
            img_path = out_dir / f"band_{cand.get('id','unknown')}.png"
            band.save(img_path)

            txt = run_tesseract(img_path, img_path.with_suffix(""))
            cleaned = clean_text(txt)
            summary = summarize(cleaned)

            cand["manifesto_text_raw"] = cleaned
            cand["manifesto_text"] = summary
            cand["manifesto_source"] = bulletin

        print(f"[OK] OCR extracted for {district}")

    save_data(payload)


if __name__ == "__main__":
    main()
