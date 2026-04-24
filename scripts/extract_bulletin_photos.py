import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

import cv2
import numpy as np
import pdfplumber
import requests

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "js" / "data" / "shugiin_tokyo_2026.json"
PDF_DIR = ROOT / "tmp" / "shugiin_bulletins"
IMAGE_DIR = ROOT / "images" / "elections" / "shugiin_tokyo_2026"
TEMPLATE_PATH = ROOT / "scripts" / "bulletin_crop_config.json"
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
EYE_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_eye.xml"


def load_data():
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def save_data(payload):
    DATA_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def district_order(candidate):
    district_no = candidate.get("district_no")
    if district_no is None:
        return 999
    cid = str(candidate.get("id", ""))
    if len(cid) >= 2 and cid[-2:].isdigit():
        return int(cid[-2:])
    return 999


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


def extract_photos(pdf_path, expected_count):
    images = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page_index, page in enumerate(pdf.pages):
            page_area = page.width * page.height
            for image in page.images:
                width = image.get("width", image.get("x1") - image.get("x0"))
                height = image.get("height", image.get("bottom") - image.get("top"))
                if not width or not height:
                    continue
                aspect = width / height if height else 0
                area = (width * height) / page_area if page_area else 0
                if area < 0.01 or area > 0.12:
                    continue
                if aspect < 0.7 or aspect > 1.4:
                    continue
                images.append(
                    {
                        "page": page_index,
                        "top": image.get("top", 0),
                        "x0": image.get("x0", 0),
                        "bbox": (image.get("x0"), image.get("top"), image.get("x1"), image.get("bottom")),
                    }
                )

        images.sort(key=lambda item: (item["page"], item["top"], item["x0"]))

        if expected_count and len(images) < expected_count:
            return []

        return [(item["page"], item["bbox"]) for item in images]


def extract_candidate_regions(image, candidate_count, config):
    width, height = image.size
    x0 = int(width * config["x0_ratio"])
    x1 = int(width * config["x1_ratio"])
    top = int(height * config["top_margin_ratio"])
    bottom = int(height * config["bottom_margin_ratio"])

    available = max(1, height - top - bottom)
    segment = available / candidate_count
    regions = []

    for idx in range(candidate_count):
        seg_top = top + segment * idx
        y0 = int(seg_top + segment * config["row_top_inset"])
        y1 = int(seg_top + segment * config["row_height_ratio"])
        regions.append((x0, y0, x1, y1))

    return regions


def find_photo_boxes(image_bgr, config):
    height, width = image_bgr.shape[:2]
    x0 = int(width * config["roi_x0_ratio"])
    x1 = int(width * config["roi_x1_ratio"])
    roi = image_bgr[:, x0:x1]

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 31, 10
    )

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []
    min_area = width * height * config.get("min_box_area_ratio", 0.002)
    max_area = width * height * config.get("max_box_area_ratio", 0.03)
    min_aspect = config.get("min_box_aspect", 0.6)
    max_aspect = config.get("max_box_aspect", 1.6)

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        if area < min_area or area > max_area:
            continue
        aspect = w / h if h else 0
        if aspect < min_aspect or aspect > max_aspect:
            continue
        boxes.append((x, y, w, h))

    boxes = sorted(boxes, key=lambda b: b[1])
    return boxes, (x0, x1)


def detect_faces(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(CASCADE_PATH)
    faces = cascade.detectMultiScale(
        gray, scaleFactor=1.05, minNeighbors=3, minSize=(30, 30)
    )
    if len(faces) == 0:
        return faces

    eye_cascade = cv2.CascadeClassifier(EYE_CASCADE_PATH)
    valid = []
    for (x, y, w, h) in faces:
        roi = gray[y : y + h, x : x + w]
        eyes = eye_cascade.detectMultiScale(roi, scaleFactor=1.1, minNeighbors=3, minSize=(12, 12))
        if len(eyes) > 0:
            valid.append((x, y, w, h))
    return valid


def crop_face(region_image, face_box):
    x, y, w, h = face_box
    # Expand around the face a bit to include hair/shoulders
    pad_x = int(w * 0.2)
    pad_y = int(h * 0.3)

    x0 = max(0, x - pad_x)
    y0 = max(0, y - pad_y)
    x1 = min(region_image.shape[1], x + w + pad_x)
    y1 = min(region_image.shape[0], y + h + pad_y)

    crop = region_image[y0:y1, x0:x1]
    return crop


def extract_photos_face(pdf_path, candidate_count, config):
    if candidate_count <= 0:
        return []

    with pdfplumber.open(str(pdf_path)) as pdf:
        page = pdf.pages[0]
        image = page.to_image(resolution=config["resolution"]).original

    image_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    boxes, (roi_x0, roi_x1) = find_photo_boxes(image_bgr, config)
    if not boxes:
        return []

    min_face_ratio = config.get("min_face_ratio", 0.08)
    candidates = []
    for (x, y, w, h) in boxes:
        pad = int(min(w, h) * config.get("box_padding_ratio", 0.1))
        x0 = max(0, x - pad)
        y0 = max(0, y - pad)
        x1 = min(image_bgr.shape[1], roi_x0 + x + w + pad)
        y1 = min(image_bgr.shape[0], y + h + pad)
        crop = image_bgr[y0:y1, x0 + roi_x0 : x1]

        faces = detect_faces(crop)
        face_image = None
        if len(faces) > 0:
            faces_sorted = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
            face = faces_sorted[0]
            face_area = face[2] * face[3]
            crop_area = max(1, crop.shape[0] * crop.shape[1])
            if (face_area / crop_area) < min_face_ratio:
                candidates.append({"y": y, "image": None})
                continue
            face_crop = crop_face(crop, face)
            face_image = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)

        candidates.append({"y": y, "image": face_image})

    candidates.sort(key=lambda item: item["y"])

    results = [item["image"] for item in candidates if item["image"] is not None]
    if len(results) < candidate_count:
        # Fill missing slots with None to keep alignment.
        results.extend([None] * (candidate_count - len(results)))

    return results[:candidate_count]


def parse_args():
    parser = argparse.ArgumentParser(description="Extract candidate photos from election bulletins.")
    parser.add_argument("--confirm", action="store_true", help="Confirm you checked usage terms")
    parser.add_argument("--max-districts", type=int, default=None, help="Limit number of districts")
    parser.add_argument("--district", action="append", default=[], help="Process only specific district name")
    return parser.parse_args()

def load_templates():
    if not TEMPLATE_PATH.exists():
        return {}
    try:
        return json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def main():
    args = parse_args()
    if not args.confirm:
        print("This script downloads and extracts photos from election bulletins.")
        print("Run with --confirm if you have checked usage terms and want to proceed.")
        sys.exit(1)

    payload = load_data()
    candidates = payload.get("candidates", [])

    by_district = defaultdict(list)
    for cand in candidates:
        by_district[cand.get("district")].append(cand)

    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    districts = list(by_district.items())
    if args.district:
        districts = [item for item in districts if item[0] in args.district]
    if args.max_districts is not None:
        districts = districts[: args.max_districts]

    templates = load_templates()

    for district, district_candidates in districts:
        district_candidates.sort(key=district_order)
        bulletin = district_candidates[0].get("bulletin_pdf")
        if not bulletin:
            continue

        config = templates.get(district)
        if not config:
            print(f"[WARN] No template config for {district}. Skipping.")
            continue

        try:
            pdf_path = download_pdf(bulletin)
        except Exception as exc:
            print(f"[WARN] Failed to download {bulletin}: {exc}")
            continue

        images = extract_photos_face(pdf_path, len(district_candidates), config)
        if not images:
            print(f"[WARN] Photo extraction failed for {district}. Skipping.")
            continue

        success = 0
        for cand, image in zip(district_candidates, images):
            if image is None:
                cand["image"] = ""
                continue

            filename = f"tokyo_{cand.get('id', 'unknown')}.jpg"
            output_path = IMAGE_DIR / filename
            cv2.imwrite(str(output_path), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            cand["image"] = f"images/elections/shugiin_tokyo_2026/{filename}"
            success += 1

        print(f"[OK] {district} -> {success}/{len(district_candidates)} images")

    save_data(payload)


if __name__ == "__main__":
    main()
