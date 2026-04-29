#!/usr/bin/env python3
"""各政治家の公約スコアカード OGP 画像を生成するスクリプト
出力先: images/ogp/{id}.png  (1200x630)
"""

import json
import os
import glob
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "politicians")
OUT_DIR  = os.path.join(BASE_DIR, "images", "ogp")

FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_IDX  = {"regular": 1, "medium": 1, "semibold": 1, "bold": 1, "light": 1}
STROKE    = {"regular": 0, "medium": 0, "semibold": 1, "bold": 2, "light": 0}

W, H = 1200, 630

# Palette
BG        = "#f5f2ec"
NAVY      = "#0f1f3d"
NAVY_DARK = "#07112b"
WHITE     = "#ffffff"
MUTED     = "#8fa0b5"
BORDER    = "#dde3ee"
SCORE_RED = "#c0392b"
BAR_FILL  = "#f59e0b"
BAR_EMPTY = "#dde3ee"
GREEN_BG  = "#e8faf2"
GREEN_FG  = "#1a7a4a"
ORANGE_BG = "#fff5e6"
ORANGE_FG = "#c87520"

def font(weight, size):
    return ImageFont.truetype(FONT_PATH, size, index=FONT_IDX[weight])

def text(draw, xy, s, weight, size, fill, anchor=None, **kw):
    sw = STROKE[weight]
    f  = font(weight, size)
    opts = dict(font=f, fill=fill)
    if anchor: opts["anchor"] = anchor
    if sw:     opts["stroke_width"] = sw; opts["stroke_fill"] = fill
    draw.text(xy, s, **opts, **kw)

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def blend(c1, c2, t):
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    return (int(r1 + (r2-r1)*t), int(g1 + (g2-g1)*t), int(b1 + (b2-b1)*t))

def draw_rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)

def score_color(score):
    if score >= 70: return "#16a34a"
    if score >= 40: return "#d97706"
    return SCORE_RED

def generate(data):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    accent = data.get("accent", {})
    party_from = accent.get("from", "#1e3a6e")
    party_to   = accent.get("to",   "#0f1f3d")

    # ── ヘッダー帯（グラデーション代わりに単色）──
    HEADER_H = 160
    for y in range(HEADER_H):
        t = y / HEADER_H
        c = blend(party_from, party_to, t)
        draw.line([(0, y), (W, y)], fill=c)

    # Polimiru ロゴ（右上）
    text(draw, (W - 40, 22), "polimiru", "bold", 26, (200, 220, 255), anchor="ra")
    text(draw, (W - 40, 52), "公約と実績を見える化する", "regular", 16, (180, 200, 240), anchor="ra")

    # 政治家名
    name_clean = data["name"].replace(" ", "").replace("　", "")
    text(draw, (52, 30), name_clean, "bold", 66, WHITE)

    # 党名 + 役職
    party_role = f'{data.get("party", "")}　{data.get("party_role") or data.get("current_status", "")}'
    if len(party_role) > 28:
        party_role = party_role[:28] + "…"
    text(draw, (54, 110), party_role, "regular", 22, (230, 238, 255))

    # ── コンテンツ部（白カード）──
    CARD_M  = 36
    CARD_T  = HEADER_H + 28
    CARD_B  = H - 28
    draw_rounded_rect(draw, (CARD_M, CARD_T, W - CARD_M, CARD_B),
                      radius=18, fill=WHITE, outline=BORDER, width=1)

    cx = CARD_M + 36
    cy = CARD_T + 32

    # サイクルデータを取得
    cycles = data.get("promise_cycles") or []
    if cycles:
        cycle   = cycles[0]
        title   = cycle.get("title", "")
        score   = cycle.get("score", 0) or 0
        total   = cycle.get("total", 0) or 0
        done    = cycle.get("done", 0) or 0
        started = cycle.get("started", 0) or 0
        pending = cycle.get("pending", 0) or 0
        reviewed = (cycle.get("reviewed_at") or "")[:10].replace("-", ".")

        # サイクルタイトル
        if len(title) > 34:
            title = title[:34] + "…"
        text(draw, (cx, cy), title, "regular", 20, MUTED)
        cy += 34

        # スコア行
        sc = score_color(score)
        text(draw, (cx, cy), "進捗スコア", "regular", 22, NAVY)
        score_txt = str(score)
        text(draw, (W - CARD_M - 40, cy - 4), "/100", "regular", 28, MUTED, anchor="ra")
        text(draw, (W - CARD_M - 44, cy - 8), score_txt, "bold", 82, sc, anchor="ra")
        cy += 90

        # プログレスバー
        BAR_H  = 20
        BAR_W  = W - CARD_M * 2 - 72
        draw_rounded_rect(draw, (cx, cy, cx + BAR_W, cy + BAR_H),
                          radius=10, fill=BAR_EMPTY)
        fill_w = int(BAR_W * score / 100)
        if fill_w > 0:
            draw_rounded_rect(draw, (cx, cy, cx + fill_w, cy + BAR_H),
                              radius=10, fill=BAR_FILL)
        cy += BAR_H + 28

        # 件数ボックス
        items = [
            ("実現",    done,    GREEN_BG,  GREEN_FG),
            ("進行中",  started, ORANGE_BG, ORANGE_FG),
            ("公約",    pending, "#f0f4ff",  "#2a4a8a"),
            ("合計",    total,   "#f4f6fb",  NAVY),
        ]
        BOX_W = (BAR_W - 24) // 4
        BOX_H = 86
        for i, (label, count, bg, fg) in enumerate(items):
            bx = cx + i * (BOX_W + 8)
            draw_rounded_rect(draw, (bx, cy, bx + BOX_W, cy + BOX_H),
                              radius=10, fill=bg, outline=BORDER, width=1)
            text(draw, (bx + BOX_W // 2, cy + 16), label, "regular", 18, fg, anchor="ma")
            text(draw, (bx + BOX_W // 2, cy + 50), str(count), "bold", 32, fg, anchor="ma")
        cy += BOX_H + 20

        # 確認日
        if reviewed:
            text(draw, (cx, cy), f"確認日  {reviewed}", "regular", 17, MUTED)

    else:
        # スコアデータなし
        text(draw, (cx, cy + 40), "公約トラッキング準備中", "regular", 28, MUTED)

    # ── フッター ──
    FOOTER_H = 44
    for y in range(H - FOOTER_H, H):
        t = (y - (H - FOOTER_H)) / FOOTER_H
        c = blend(party_from, party_to, min(t * 2, 1.0))
        draw.line([(CARD_M + 1, y), (W - CARD_M - 1, y)], fill=c)
    text(draw, (cx, H - FOOTER_H + 12), "polimiru.jp", "semibold", 18, (220, 232, 255))

    return img

def needs_update(json_path, png_path):
    if not os.path.exists(png_path):
        return True
    return os.path.getmtime(json_path) > os.path.getmtime(png_path)

def run(force=False, targets=None):
    """
    force=True  : 全員再生成
    targets     : ["takaichi-sanae", ...] のように ID リストを渡すと対象を絞れる
    """
    os.makedirs(OUT_DIR, exist_ok=True)
    files = sorted(glob.glob(os.path.join(DATA_DIR, "*.json")))
    ok = skipped = 0
    for path in files:
        pid = os.path.splitext(os.path.basename(path))[0]
        if targets and pid not in targets:
            continue
        out = os.path.join(OUT_DIR, f"{pid}.png")
        if not force and not needs_update(path, out):
            skipped += 1
            continue
        try:
            data  = json.load(open(path, encoding="utf-8"))
            img   = generate(data)
            img.save(out, "PNG", optimize=True)
            score = (data.get("promise_cycles") or [{}])[0].get("score", "-")
            print(f"  OK  {pid} (score={score})")
            ok += 1
        except Exception as e:
            print(f"  ERR {pid}: {e}")
    print(f"\n完了: 更新 {ok} 枚 / スキップ {skipped} 枚 → images/ogp/")

def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--force", action="store_true", help="変更有無に関わらず全員再生成")
    p.add_argument("--id", nargs="*", help="対象の政治家ID（省略すると全員）")
    args = p.parse_args()
    run(force=args.force, targets=args.id)

if __name__ == "__main__":
    main()
