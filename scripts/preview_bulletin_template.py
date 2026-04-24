import argparse
from pathlib import Path

import pdfplumber
from PIL import Image, ImageDraw

from extract_bulletin_photos import download_pdf

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "tmp" / "bulletin_previews"


def parse_args():
    parser = argparse.ArgumentParser(description="Preview bulletin crop template.")
    parser.add_argument("--pdf", required=True, help="Bulletin PDF URL")
    parser.add_argument("--out", required=True, help="Output directory name")
    parser.add_argument("--resolution", type=int, default=240)
    parser.add_argument("--x0", type=float, required=True)
    parser.add_argument("--x1", type=float, required=True)
    parser.add_argument("--top", type=float, required=True)
    parser.add_argument("--bottom", type=float, required=True)
    parser.add_argument("--row-top", type=float, required=True)
    parser.add_argument("--row-height", type=float, required=True)
    parser.add_argument("--count", type=int, required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    pdf_path = download_pdf(args.pdf)

    out_dir = DATA_DIR / args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    with pdfplumber.open(str(pdf_path)) as pdf:
        page = pdf.pages[0]
        image = page.to_image(resolution=args.resolution).original

    width, height = image.size
    x0 = int(width * args.x0)
    x1 = int(width * args.x1)
    top = int(height * args.top)
    bottom = int(height * args.bottom)

    available = max(1, height - top - bottom)
    segment = available / args.count

    preview = image.copy()
    draw = ImageDraw.Draw(preview)

    for idx in range(args.count):
        seg_top = top + segment * idx
        y0 = int(seg_top + segment * args.row_top)
        y1 = int(seg_top + segment * args.row_height)
        draw.rectangle((x0, y0, x1, y1), outline="red", width=3)

        crop = image.crop((x0, y0, x1, y1))
        out_path = out_dir / f"crop_{idx+1}.jpg"
        crop.save(out_path, format="JPEG")

    preview.save(out_dir / "preview.jpg", format="JPEG")
    print(out_dir)


if __name__ == "__main__":
    main()
