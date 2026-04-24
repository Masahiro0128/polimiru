"""
大阪2023 知事選・市長選 選挙公報から公約を抽出するスクリプト

処理フロー:
  1. 大阪府/市 選管から2023年選挙公報PDFを取得
  2. pdfplumber でテキスト抽出 (ネイティブ PDF)
  3. 公約らしい文をルールベースで抽出・構造化
  4. candidates/{id}.json の promises_2023 フィールドに保存
  5. レビュー用 CSV を出力 (Google Sheets にインポート可能)

使い方:
  python scripts/collect_osaka_2023_promises.py --election governor
  python scripts/collect_osaka_2023_promises.py --election mayor
  python scripts/collect_osaka_2023_promises.py --election all
"""

import argparse
import csv
import json
import re
import unicodedata
from pathlib import Path

import requests

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    print("[WARN] pdfplumber が見つかりません。pip install pdfplumber で導入してください。")

ROOT     = Path(__file__).resolve().parents[1]
PDF_DIR  = ROOT / "tmp" / "osaka_2023_bulletins"
CSV_DIR  = ROOT / "tmp" / "review_sheets"

# ------------------------------------------------------------------
#  選挙設定
# ------------------------------------------------------------------
ELECTION_CONFIG = {
    "governor": {
        "candidate_id":  "yoshimura",
        "candidate_name": "吉村 洋文",
        "detail_json":   ROOT / "js/data/osaka_2027_governor/candidates/yoshimura.json",
        "csv_out":       CSV_DIR / "promises_yoshimura_2023.csv",
        # 大阪府選管 令和5年知事選 選挙公報
        # 公示後に https://www.pref.osaka.lg.jp/senkan/chijisen/r5chiji/ 等で公開される
        "pdf_urls": [
            "https://www.pref.osaka.lg.jp/attach/38350/00000000/yoshimura.pdf",  # 仮URL
        ],
        "senkan_url": "https://www.pref.osaka.lg.jp/senkan/chijisen/r5chiji/",
    },
    "mayor": {
        "candidate_id":  "yokoyama",
        "candidate_name": "横山 英幸",
        "detail_json":   ROOT / "js/data/osaka_2027_mayor/candidates/yokoyama.json",
        "csv_out":       CSV_DIR / "promises_yokoyama_2023.csv",
        # 大阪市選管 令和5年市長選 選挙公報
        "pdf_urls": [
            "https://www.city.osaka.lg.jp/senkyokanri/cmsfiles/contents/0000001/yokoyama.pdf",  # 仮URL
        ],
        "senkan_url": "https://www.city.osaka.lg.jp/senkyokanri/",
    },
}

# ------------------------------------------------------------------
#  公約らしい文を判定するルール
# ------------------------------------------------------------------
NUM_RE     = re.compile(r"\d")
DATE_RE    = re.compile(r"(20\d{2}年|令和\d+年|\d+年以内|\d+月|\d+日|任期中|就任後)")
MONEY_RE   = re.compile(r"(億円|万円|予算|財源|税|補助|支援金|交付金)")
PROCESS_RE = re.compile(r"(条例|制度|法律|改正|導入|実施|実行|創設|廃止|設置|整備|推進|拡充|強化|見直し)")
PROMISE_RE = re.compile(r"(する|します|してまいります|目指す|実現|取り組む|進める|図る|行う|進めます)。?$")

# 除外パターン（ヘッダー・氏名行など）
SKIP_RE    = re.compile(r"^[ぁ-ん]{2,8}$|^[A-Za-z0-9\s]{1,20}$|^[。、・…]+$")

CATEGORIES = {
    "教育":   ["教育", "学校", "子ども", "子育て", "保育", "授業料", "給食"],
    "経済":   ["経済", "雇用", "企業", "観光", "万博", "IR", "投資", "成長"],
    "医療福祉": ["医療", "福祉", "介護", "高齢", "障がい", "健康", "病院"],
    "インフラ": ["交通", "道路", "鉄道", "公共交通", "整備", "建設", "防災"],
    "行財政": ["行政", "財政", "改革", "効率", "無駄", "税金", "予算"],
    "環境":   ["環境", "脱炭素", "再生可能", "エネルギー", "緑"],
    "安全":   ["防犯", "安全", "治安", "消防"],
}


def guess_category(text: str) -> str:
    for cat, keywords in CATEGORIES.items():
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


def is_promise_sentence(text: str) -> bool:
    if len(text) < 15 or len(text) > 200:
        return False
    if SKIP_RE.match(text):
        return False
    return bool(PROCESS_RE.search(text) or PROMISE_RE.search(text))


# ------------------------------------------------------------------
#  PDFテキスト抽出
# ------------------------------------------------------------------
def download_pdf(url: str, dest: Path) -> bool:
    if dest.exists():
        print(f"  [CACHE] {dest.name}")
        return True
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "polimiru-bot/1.0"})
        r.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(r.content)
        print(f"  [DL] {dest.name} ({len(r.content)//1024}KB)")
        return True
    except Exception as e:
        print(f"  [FAIL] {url} → {e}")
        return False


def extract_text_from_pdf(pdf_path: Path) -> str:
    if not HAS_PDFPLUMBER:
        return ""
    try:
        full_text = []
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text.append(text)
        return "\n".join(full_text)
    except Exception as e:
        print(f"  [PDF ERROR] {e}")
        return ""


def find_pdf_from_senkan(senkan_url: str, candidate_name: str) -> str | None:
    """選管ページから候補者の選挙公報PDFリンクを探す"""
    try:
        r = requests.get(senkan_url, timeout=20, headers={"User-Agent": "polimiru-bot/1.0"})
        r.raise_for_status()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "html.parser")
        last_name = candidate_name.replace(" ", "").replace("　", "")[0]  # 姓の最初の文字
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text()
            if last_name in text and href.lower().endswith(".pdf"):
                from urllib.parse import urljoin
                return urljoin(senkan_url, href)
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if ("bulletin" in href or "senkyo" in href or "kouhou" in href) and href.lower().endswith(".pdf"):
                from urllib.parse import urljoin
                return urljoin(senkan_url, href)
    except Exception as e:
        print(f"  [SENKAN SEARCH] {e}")
    return None


# ------------------------------------------------------------------
#  テキスト → 公約リスト
# ------------------------------------------------------------------
def extract_promises(text: str) -> list[dict]:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[　\t]+", " ", text)

    # 箇条書き・句点で分割
    sentences = re.split(r"(?<=[。．\n])|(?<=する）)|(?<=ます）)", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    # さらに改行ベースで分割して候補を絞る
    lines = []
    for s in sentences:
        lines.extend(s.split("\n"))

    promises = []
    seen = set()
    pid = 1
    for line in lines:
        line = line.strip()
        if not line or line in seen:
            continue
        if is_promise_sentence(line):
            seen.add(line)
            spec = calc_specificity(line)
            promises.append({
                "id":             f"p{pid:02d}",
                "text":           line,
                "category":       guess_category(line),
                "has_number":     bool(NUM_RE.search(line)),
                "has_deadline":   bool(DATE_RE.search(line)),
                "has_process":    bool(PROCESS_RE.search(line)),
                "specificity_score": spec,
                "status":         None,
                "evidence_url":   "",
                "note":           "",
            })
            pid += 1

    return promises


# ------------------------------------------------------------------
#  JSON 保存
# ------------------------------------------------------------------
def update_candidate_json(json_path: Path, promises: list[dict], source_url: str) -> None:
    try:
        data = json.loads(json_path.read_text("utf-8"))
    except (json.JSONDecodeError, FileNotFoundError):
        data = {}

    data["promises_2023"]        = promises
    data["manifesto_source_2023"] = source_url
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(f"  JSON更新: {json_path.name} ({len(promises)}件)")


# ------------------------------------------------------------------
#  CSV 出力（Google Sheets インポート用）
# ------------------------------------------------------------------
def export_csv(promises: list[dict], candidate_name: str, csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "候補者", "公約番号", "公約テキスト", "カテゴリ",
            "KPIあり", "期限あり", "手段あり", "具体性スコア",
            "達成状況", "証拠URL", "メモ",
        ])
        writer.writeheader()
        for p in promises:
            writer.writerow({
                "候補者":      candidate_name,
                "公約番号":    p["id"],
                "公約テキスト": p["text"],
                "カテゴリ":    p["category"],
                "KPIあり":    "○" if p["has_number"]   else "×",
                "期限あり":   "○" if p["has_deadline"] else "×",
                "手段あり":   "○" if p["has_process"]  else "×",
                "具体性スコア": p["specificity_score"],
                "達成状況":   "",   # チームが記入: 完了/着手/未着手/不明
                "証拠URL":    "",   # チームが記入
                "メモ":       "",
            })
    print(f"  CSV出力: {csv_path}")


# ------------------------------------------------------------------
#  メイン処理（1候補者分）
# ------------------------------------------------------------------
def collect_promises(cfg: dict) -> None:
    name    = cfg["candidate_name"]
    pdf_dir = PDF_DIR / cfg["candidate_id"]
    pdf_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== {name} (2023) ===")

    # PDFを取得（選管ページを探すか直接URLを試す）
    pdf_path = None
    used_url = ""

    # まず選管ページから動的に探す
    found_url = find_pdf_from_senkan(cfg["senkan_url"], name)
    if found_url:
        dest = pdf_dir / f"{cfg['candidate_id']}_2023.pdf"
        if download_pdf(found_url, dest):
            pdf_path = dest
            used_url = found_url

    # 見つからなければ既定URLを試す
    if not pdf_path:
        for url in cfg["pdf_urls"]:
            dest = pdf_dir / f"{cfg['candidate_id']}_2023.pdf"
            if download_pdf(url, dest):
                pdf_path = dest
                used_url = url
                break

    if not pdf_path:
        print(f"  [SKIP] PDFが見つかりませんでした。")
        print(f"         選管URL: {cfg['senkan_url']}")
        print(f"         候補者のPDFを手動でダウンロードし、")
        print(f"         {pdf_dir}/{cfg['candidate_id']}_2023.pdf に置いてください。")
        # 既存JSONを確認してスキップ
        detail = json.loads(cfg["detail_json"].read_text("utf-8")) if cfg["detail_json"].exists() else {}
        if detail.get("promises_2023"):
            print(f"         既存の公約データ {len(detail['promises_2023'])} 件を保持します。")
        return

    # テキスト抽出
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print("  [WARN] テキスト抽出できませんでした。スキャンPDFの可能性があります。")
        print("         OCRスクリプト (ocr_manifesto_from_bulletin.py) を使用してください。")
        return

    print(f"  テキスト抽出: {len(text)}文字")

    # 公約抽出
    promises = extract_promises(text)
    print(f"  公約候補: {len(promises)}件")

    if not promises:
        print("  [WARN] 公約文が抽出できませんでした。テキストを確認してください。")
        raw_path = pdf_dir / f"{cfg['candidate_id']}_raw.txt"
        raw_path.write_text(text, "utf-8")
        print(f"         生テキストを保存: {raw_path}")
        return

    # 保存
    update_candidate_json(cfg["detail_json"], promises, used_url)
    export_csv(promises, name, cfg["csv_out"])


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
        collect_promises(cfg)

    print("\n完了。")
    print(f"CSVファイルは {CSV_DIR} に出力されました。")
    print("Googleスプレッドシートにインポートして、チームでレビューしてください。")
    print("レビュー後は import_review_sheet.py でJSONに反映できます。")


if __name__ == "__main__":
    main()
