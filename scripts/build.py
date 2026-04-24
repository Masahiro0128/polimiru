"""
build.py — elections.yaml から選挙ページと js/elections.js を生成する

使い方:
  python scripts/build.py          # 全選挙を再生成
  python scripts/build.py --dry    # 変更内容を表示するだけ（書き込まない）
  python scripts/build.py --id osaka_2027_governor  # 1件だけ再生成
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML が必要です: pip install pyyaml")
    sys.exit(1)

ROOT       = Path(__file__).resolve().parents[1]
YAML_PATH  = ROOT / "data" / "elections.yaml"
JS_OUT     = ROOT / "js" / "elections.js"

# ── HTML テンプレート ──────────────────────────────────────────────────────
# プレースホルダーは __KEY__ 形式（JS/CSS の {} と衝突しない）
TEMPLATE = """\
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>polimiru | __TITLE__</title>
    <meta property="og:title" content="polimiru | __TITLE__">
    <meta property="og:description" content="__HERO_DESC_PLAIN__">

    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
    <link rel="stylesheet" href="__ROOT__css/base.css">
    <link rel="stylesheet" href="__ROOT__css/header-footer.css">
    <link rel="stylesheet" href="__ROOT__css/elections.css">
    <link rel="stylesheet" href="__ROOT__css/modal.css">
    <link rel="stylesheet" href="__ROOT__css/candidate-modal.css">

    <style>
        body { background: #f5f2ec; }

        .election-hero {
            background: linear-gradient(135deg, __HERO_FROM__, __HERO_TO__);
            color: #fff;
            padding: 40px 20px 32px;
        }
        .election-hero-inner {
            max-width: 1000px;
            margin: 0 auto;
        }
        .election-hero h1 {
            margin: 0 0 8px;
            font-size: 1.7em;
            font-weight: 800;
            letter-spacing: 0.02em;
        }
        .election-hero p {
            margin: 0 0 16px;
            opacity: 0.88;
            line-height: 1.7;
            font-size: 0.95em;
        }
        .election-hero-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            font-size: 0.82em;
            opacity: 0.85;
        }
        .election-hero-meta span {
            background: rgba(255,255,255,0.15);
            padding: 3px 10px;
            border-radius: 999px;
        }

        .page-body {
            max-width: 1000px;
            margin: 0 auto;
            padding: 28px 16px 60px;
        }
        .back-link {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            color: #666;
            text-decoration: none;
            font-size: 0.85em;
            margin-bottom: 20px;
        }
        .back-link:hover { color: #333; }

        .section-head {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            margin-bottom: 16px;
            border-left: 4px solid __ACCENT__;
            padding-left: 12px;
        }
        .section-head h2 {
            margin: 0;
            font-size: 1.1em;
            color: #1a2e45;
        }
        .section-head .count {
            font-size: 0.82em;
            color: #999;
        }

        #loading-msg {
            padding: 40px;
            text-align: center;
            color: #aaa;
            font-size: 0.9em;
        }
    </style>
</head>
<body>

    <div class="election-hero">
        <div class="election-hero-inner">
            <h1>__TITLE__</h1>
            <p>__HERO_DESC__</p>
            <div class="election-hero-meta">
                <span><i class="fa-regular fa-calendar"></i> __DATE__</span>
                <span><i class="fa-solid fa-location-dot"></i> __PREFECTURE__</span>
                <span id="last-updated-chip"><i class="fa-regular fa-clock"></i> 取得中...</span>
            </div>
        </div>
    </div>

    <div class="page-body">
        <a href="__ROOT__index.html" class="back-link">
            <i class="fa-solid fa-arrow-left"></i> トップへ戻る
        </a>

        <div id="upcoming-banner" class="upcoming-banner" style="display:none">
            <span class="upcoming-banner-icon">📋</span>
            <div>
                <strong>候補者情報は選挙公示後に更新されます。</strong><br>
                現時点では現職情報のみ掲載しています。立候補が確定した候補者から順次追加されます。
            </div>
        </div>

        <div class="section-head">
            <h2>候補者一覧</h2>
            <span class="count" id="candidate-count"></span>
        </div>

        <div id="loading-msg">候補者データを読み込み中...</div>
        <div class="candidate-grid" id="candidate-grid"></div>
    </div>

    <script src="__ROOT__js/layout.js?v=999"></script>
    <script src="__ROOT__js/candidate-modal.js"></script>
    <script>
        const ELECTION_KEY = '__ELECTION_KEY__';

        function partyHeaderClass(party) {
            if (!party) return '';
            if (party.includes('維新')) return 'party-ishin';
            if (party.includes('自由民主') || party.includes('自民')) return 'party-jimin';
            if (party.includes('公明')) return 'party-komei';
            return 'party-other';
        }

        function renderScoreSummary(c) {
            if (c.role === 'incumbent') {
                const v = c.score_incumbent;
                return `
                    <div class="cand-card-score-area">
                        <span class="cand-card-score-label">現職評価（総合）</span>
                        ${v !== null && v !== undefined
                            ? `<span class="cand-card-score-value">${v}<small style="font-size:0.55em;color:#999"> /100</small></span>`
                            : '<span class="cand-card-score-pending">集計中</span>'}
                    </div>`;
            }
            if (c.role === 'challenger') {
                const v = c.score_challenger;
                return `
                    <div class="cand-card-score-area">
                        <span class="cand-card-score-label">新人評価（公約具体性）</span>
                        ${v !== null && v !== undefined
                            ? `<span class="cand-card-score-value type-challenger">${v}<small style="font-size:0.55em;color:#999"> /100</small></span>`
                            : '<span class="cand-card-score-pending">公約情報収集中</span>'}
                    </div>`;
            }
            return `<div class="cand-card-score-area"><span class="cand-card-score-pending">情報準備中</span></div>`;
        }

        function renderCard(c) {
            const photo = c.image
                ? `<img src="${c.image}" class="cand-card-photo" alt="${c.name}" onerror="this.style.display='none'">`
                : `<div class="cand-card-photo-placeholder">👤</div>`;

            const roleBadge = c.role === 'incumbent'
                ? '<span class="cand-badge cand-badge-incumbent">現職</span>'
                : c.role === 'challenger'
                    ? '<span class="cand-badge cand-badge-challenger">新人</span>'
                    : '';

            const unconfirmed = !c.confirmed
                ? '<span class="cand-badge cand-badge-unconfirmed">出馬未確定</span>'
                : '';

            return `
                <div class="cand-card" data-election="${ELECTION_KEY}" data-candidate-id="${c.id}" role="button" tabindex="0">
                    <div class="cand-card-header ${partyHeaderClass(c.party)}">
                        ${photo}
                    </div>
                    <div class="cand-card-body">
                        <div class="cand-card-name">${c.name}</div>
                        <div class="cand-card-party">${c.party || ''}</div>
                        <div class="cand-card-badges">${roleBadge}${unconfirmed}</div>
                        ${renderScoreSummary(c)}
                        <div class="cand-card-detail-hint">詳細を見る <i class="fa-solid fa-arrow-right" style="font-size:0.8em"></i></div>
                    </div>
                </div>`;
        }

        function getDataBase() {
            const path = window.location.pathname;
            if (path.includes('/polimiru/')) {
                const parts = path.replace('/polimiru/', '').split('/').filter(Boolean);
                return '/polimiru/' + '../'.repeat(parts.length);
            }
            const parts = path.split('/').filter(Boolean);
            return parts.length <= 1 ? './' : '../'.repeat(parts.length - 1);
        }

        document.addEventListener('DOMContentLoaded', () => {
            const base = getDataBase();
            fetch(`${base}js/data/${ELECTION_KEY}/index.json`)
                .then(r => r.json())
                .then(data => {
                    const grid   = document.getElementById('candidate-grid');
                    const msg    = document.getElementById('loading-msg');
                    const count  = document.getElementById('candidate-count');
                    const chip   = document.getElementById('last-updated-chip');
                    const banner = document.getElementById('upcoming-banner');

                    msg.style.display = 'none';

                    const candidates = data.candidates || [];
                    count.textContent = `${candidates.length}名`;

                    if (data.meta?.status === 'upcoming') {
                        banner.style.display = 'flex';
                    }

                    if (data.meta?.last_updated) {
                        const d = new Date(data.meta.last_updated);
                        chip.innerHTML = `<i class="fa-regular fa-clock"></i> 更新: ${d.getFullYear()}/${d.getMonth()+1}/${d.getDate()}`;
                    }

                    grid.innerHTML = candidates.map(renderCard).join('');

                    grid.querySelectorAll('.cand-card').forEach(el => {
                        el.addEventListener('keydown', e => {
                            if (e.key === 'Enter' || e.key === ' ') el.click();
                        });
                    });
                })
                .catch(() => {
                    document.getElementById('loading-msg').textContent = 'データを取得できませんでした。';
                });
        });
    </script>

</body>
</html>
"""


# ── ヘルパー ───────────────────────────────────────────────────────────────

def render(template: str, ctx: dict) -> str:
    for key, value in ctx.items():
        template = template.replace(f"__{key}__", str(value))
    return template


def rel_root(output_path: str) -> str:
    """output_path からサイトルートへの相対パスを返す。例: 'elections/osaka/2027_governor/index.html' → '../../../'"""
    depth = len(Path(output_path).parent.parts)
    return "../" * depth if depth > 0 else "./"


def plain_text(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html).replace("  ", " ").strip()


# ── HTML 生成 ──────────────────────────────────────────────────────────────

def build_election_page(e: dict, dry: bool) -> bool:
    out_path = ROOT / e["output_path"]
    root     = rel_root(e["output_path"])

    ctx = {
        "TITLE":           e["title"],
        "ELECTION_KEY":    e["id"],
        "DATE":            e["date"],
        "PREFECTURE":      e["prefecture"],
        "HERO_FROM":       e.get("hero_from", "#1a2a3a"),
        "HERO_TO":         e.get("hero_to",   "#2d4a6a"),
        "ACCENT":          e.get("accent",    "#2d4a6a"),
        "HERO_DESC":       e.get("hero_desc", e.get("list_desc", "")),
        "HERO_DESC_PLAIN": plain_text(e.get("hero_desc", e.get("list_desc", ""))),
        "ROOT":            root,
    }

    html = render(TEMPLATE, ctx)

    existing = out_path.read_text("utf-8") if out_path.exists() else ""
    if existing == html:
        print(f"  [SKIP] {out_path.relative_to(ROOT)}  (変更なし)")
        return False

    if dry:
        print(f"  [DRY]  {out_path.relative_to(ROOT)}  (変更あり)")
        return True

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, "utf-8")
    print(f"  [WRITE] {out_path.relative_to(ROOT)}")
    return True


# ── js/elections.js 生成 ──────────────────────────────────────────────────

def build_elections_js(elections: list[dict], dry: bool) -> bool:
    entries = []
    for e in elections:
        entry = {
            "id":          e["list_id"],
            "title":       e["title"],
            "category":    e["category"],
            "date":        e["date"],
            "prefecture":  e["prefecture"],
            "desc":        e.get("list_desc", ""),
            "image":       e.get("list_image", ""),
            "url":         e["output_path"],
            "badgeType":   e.get("badge_type", "local"),
            "status":      e.get("list_status", ""),
        }
        entries.append(entry)

    js = "// 選挙データを管理するリスト\n"
    js += "// このファイルは scripts/build.py が自動生成します。直接編集しないでください。\n"
    js += "// 選挙を追加・変更するには data/elections.yaml を編集してください。\n"
    js += "const elections = "
    js += json.dumps(entries, ensure_ascii=False, indent=4)
    js += ";\n"

    existing = JS_OUT.read_text("utf-8") if JS_OUT.exists() else ""
    if existing == js:
        print(f"  [SKIP] js/elections.js  (変更なし)")
        return False

    if dry:
        print(f"  [DRY]  js/elections.js  ({len(entries)} 件、変更あり)")
        return True

    JS_OUT.write_text(js, "utf-8")
    print(f"  [WRITE] js/elections.js  ({len(entries)} 件)")
    return True


# ── エントリポイント ──────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="elections.yaml から選挙ページを生成")
    parser.add_argument("--dry", action="store_true", help="書き込まず変更内容だけ表示")
    parser.add_argument("--id",  help="特定の選挙IDだけ再生成")
    args = parser.parse_args()

    data      = yaml.safe_load(YAML_PATH.read_text("utf-8"))
    elections = data["elections"]

    if args.id:
        elections = [e for e in elections if e["id"] == args.id]
        if not elections:
            print(f"[ERROR] ID '{args.id}' が見つかりません")
            return

    print(f"{'[DRY RUN] ' if args.dry else ''}ビルド開始: {len(elections)} 件")
    changed = 0

    for e in elections:
        if e.get("template") == "standard":
            if build_election_page(e, args.dry):
                changed += 1
        else:
            print(f"  [SKIP] {e['id']}  (template: custom)")

    if not args.id:
        if build_elections_js(elections, args.dry):
            changed += 1

    print(f"\n完了。{'変更予定' if args.dry else '変更'}: {changed} ファイル")
    if not args.dry and changed:
        print("git add -A && git commit -m 'build: 選挙ページ再生成' で反映できます")


if __name__ == "__main__":
    main()
