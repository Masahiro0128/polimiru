"""
大阪維新の会 2023年マニフェストから公約リストを抽出するスクリプト

対象PDF: https://osaka-ishin.jp/pdf/manifesto/ishinfugidan_manifesto2023.pdf
構造:  「◆ 見出し」→ main promise
        「◇ 詳細」 → sub promise (親に紐付ける)
        「≪ カテゴリ ≫」「「カテゴリ」を実現します」で分類

使い方:
  python scripts/parse_ishin_manifesto_2023.py

出力:
  js/data/osaka_2027_governor/candidates/yoshimura.json (promises_2023 フィールド更新)
  tmp/review_sheets/promises_yoshimura_2023.csv         (Googleスプレッドシート用)
"""

import csv
import json
import re
import unicodedata
from pathlib import Path

import pdfplumber

ROOT     = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "tmp/osaka_2023_bulletins/yoshimura/ishin_manifesto2023.pdf"
JSON_OUT = ROOT / "js/data/osaka_2027_governor/candidates/yoshimura.json"
CSV_OUT  = ROOT / "tmp/review_sheets/promises_yoshimura_2023.csv"

# セクション見出しのパターン（ページタイトルから抽出）
SECTION_PATTERNS = [
    (re.compile(r"「(.+?都市.+?)」を実現"),  lambda m: m.group(1)),
    (re.compile(r"「(.+?)」を実現"),          lambda m: m.group(1)),
    (re.compile(r"≪\s*(.+?)\s*≫"),           lambda m: m.group(1)),
    (re.compile(r"^【(.+?)】"),               lambda m: m.group(1)),
]

NUM_RE     = re.compile(r"\d")
DATE_RE    = re.compile(r"(20\d{2}年|令和\d+年|\d+年以内|\d+月|任期中|就任後)")
MONEY_RE   = re.compile(r"(億円|万円|予算|財源|税|補助|支援金|交付金)")
PROCESS_RE = re.compile(r"(条例|制度|法律|改正|導入|実施|創設|廃止|設置|整備|推進|拡充|強化|見直し|民営化|無償化)")

CATEGORY_MAP = {
    "教育":   ["教育", "学校", "子ども", "子育て", "保育", "授業料", "無償", "給食"],
    "経済":   ["経済", "雇用", "企業", "観光", "万博", "IR", "投資", "成長", "産業", "労働"],
    "医療福祉": ["医療", "福祉", "介護", "高齢", "障がい", "健康", "病院", "がん", "長寿"],
    "インフラ": ["交通", "道路", "鉄道", "公共交通", "整備", "建設", "防災", "消防", "津波"],
    "行財政": ["行政", "財政", "改革", "効率", "無駄", "税金", "予算", "議員", "DX", "デジタル"],
    "環境":   ["環境", "脱炭素", "再生可能", "エネルギー", "緑", "林業", "森林"],
    "安全":   ["防犯", "安全", "治安", "感染症"],
    "都市開発": ["まちづくり", "都市", "副首都", "万博", "IR", "夢洲"],
}


def guess_category(text: str) -> str:
    for cat, keywords in CATEGORY_MAP.items():
        if any(k in text for k in keywords):
            return cat
    return "その他"


def calc_specificity(text: str) -> int:
    score = 0
    if NUM_RE.search(text):     score += 25
    if DATE_RE.search(text):    score += 25
    if MONEY_RE.search(text):   score += 25
    if PROCESS_RE.search(text): score += 25
    return min(score, 100)


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    return re.sub(r"[\s　]+", " ", text).strip()


def extract_text_by_page(pdf_path: Path) -> list[str]:
    pages = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages.append(text)
    return pages


def detect_section(line: str) -> str | None:
    for pat, extractor in SECTION_PATTERNS:
        m = pat.search(line)
        if m:
            return extractor(m)
    return None


BULLET_RE    = re.compile(r"^[◆◇]")
TERMINAL_RE  = re.compile(r"[。．」）\)]\s*$|\d\s*$")
SKIP_LINE_RE = re.compile(r"^\d+$|^[（\(提供].+[）\)]$")


def join_pages_to_lines(pages: list[str]) -> list[str]:
    """ページをまたいだ行を結合し、◆/◇ 単位の論理行リストを返す"""
    raw_lines = []
    for page_text in pages:
        raw_lines.extend(page_text.split("\n"))

    logical_lines = []
    buf = ""
    for raw in raw_lines:
        line = normalize(raw)
        if not line or SKIP_LINE_RE.match(line):
            if buf:
                logical_lines.append(buf)
                buf = ""
            continue

        if BULLET_RE.match(line) or detect_section(line):
            if buf:
                logical_lines.append(buf)
            buf = line
        elif buf and not TERMINAL_RE.search(buf):
            # 前行が文末で終わっていない → 継続行として結合
            buf = buf + line
        else:
            if buf:
                logical_lines.append(buf)
            buf = line

    if buf:
        logical_lines.append(buf)

    return logical_lines


def parse_promises(pages: list[str]) -> list[dict]:
    current_section = "総合"
    promises = []
    pid = 1
    parent_id = None

    for line in join_pages_to_lines(pages):
        # セクション検出
        section = detect_section(line)
        if section:
            current_section = section
            parent_id = None
            continue

        # ◆ メイン公約
        if line.startswith("◆"):
            text = re.sub(r"^◆\s*", "", line).strip()
            if len(text) < 10:
                continue
            cat  = guess_category(text)
            if cat == "その他":
                cat = guess_category(current_section)
            spec = calc_specificity(text)
            cid  = f"p{pid:03d}"
            promises.append({
                "id":                cid,
                "text":              text,
                "category":          cat,
                "section":           current_section,
                "level":             "main",
                "parent_id":         None,
                "has_number":        bool(NUM_RE.search(text)),
                "has_deadline":      bool(DATE_RE.search(text)),
                "has_process":       bool(PROCESS_RE.search(text)),
                "specificity_score": spec,
                "status":            None,
                "evidence_url":      "",
                "note":              "",
            })
            parent_id = cid
            pid += 1

        # ◇ サブ公約
        elif line.startswith("◇"):
            text = re.sub(r"^◇\s*", "", line).strip()
            if len(text) < 10:
                continue
            cat  = guess_category(text)
            if cat == "その他":
                cat = guess_category(current_section)
            spec = calc_specificity(text)
            promises.append({
                "id":                f"p{pid:03d}",
                "text":              text,
                "category":          cat,
                "section":           current_section,
                "level":             "sub",
                "parent_id":         parent_id,
                "has_number":        bool(NUM_RE.search(text)),
                "has_deadline":      bool(DATE_RE.search(text)),
                "has_process":       bool(PROCESS_RE.search(text)),
                "specificity_score": spec,
                "status":            None,
                "evidence_url":      "",
                "note":              "",
            })
            pid += 1

    return promises


def update_json(json_path: Path, promises: list[dict]) -> None:
    try:
        data = json.loads(json_path.read_text("utf-8"))
    except (json.JSONDecodeError, FileNotFoundError):
        data = {}

    data["promises_2023"]         = promises
    data["manifesto_source_2023"] = "https://osaka-ishin.jp/pdf/manifesto/ishinfugidan_manifesto2023.pdf"
    data["manifesto_note_2023"]   = "大阪維新の会 大阪府議会議員団 マニフェスト2023（知事選同時期）"
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(f"  JSON更新: {json_path.name}  ({len(promises)} 件)")


def export_csv(promises: list[dict]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(CSV_OUT, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "候補者", "公約番号", "セクション", "レベル", "親公約番号",
            "公約テキスト", "カテゴリ",
            "KPIあり", "期限あり", "手段あり", "具体性スコア",
            "達成状況", "証拠URL", "メモ",
        ])
        writer.writeheader()
        for p in promises:
            writer.writerow({
                "候補者":    "吉村洋文（維新府議団マニフェスト2023）",
                "公約番号":  p["id"],
                "セクション": p["section"],
                "レベル":    "主要" if p["level"] == "main" else "詳細",
                "親公約番号": p["parent_id"] or "",
                "公約テキスト": p["text"],
                "カテゴリ":  p["category"],
                "KPIあり":   "○" if p["has_number"]   else "×",
                "期限あり":  "○" if p["has_deadline"] else "×",
                "手段あり":  "○" if p["has_process"]  else "×",
                "具体性スコア": p["specificity_score"],
                "達成状況":  "",
                "証拠URL":   "",
                "メモ":      "",
            })
    print(f"  CSV出力:  {CSV_OUT}")


def main() -> None:
    if not PDF_PATH.exists():
        print(f"[ERROR] PDFが見つかりません: {PDF_PATH}")
        print("以下を実行してダウンロードしてください:")
        print("  curl -sL https://osaka-ishin.jp/pdf/manifesto/ishinfugidan_manifesto2023.pdf \\")
        print(f"    -o {PDF_PATH}")
        return

    print(f"PDF読み込み: {PDF_PATH}")
    pages = extract_text_by_page(PDF_PATH)
    print(f"  {len(pages)} ページ")

    promises = parse_promises(pages)
    print(f"  公約抽出: {len(promises)} 件 "
          f"(主要: {sum(1 for p in promises if p['level']=='main')}, "
          f"詳細: {sum(1 for p in promises if p['level']=='sub')})")

    # カテゴリ別サマリー
    from collections import Counter
    cats = Counter(p["category"] for p in promises)
    for cat, cnt in cats.most_common():
        print(f"    {cat}: {cnt}件")

    update_json(JSON_OUT, promises)
    export_csv(promises)

    print(f"\n完了。")
    print(f"CSVを Google スプレッドシートにインポートして、")
    print(f"「達成状況」列（完了/着手/未着手/不明）と「証拠URL」を記入してください。")
    print(f"記入後は: python scripts/import_review_sheet.py \\")
    print(f"              --csv {CSV_OUT} \\")
    print(f"              --json {JSON_OUT}")


if __name__ == "__main__":
    main()
