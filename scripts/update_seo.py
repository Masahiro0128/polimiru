#!/usr/bin/env python3
"""全政治家ページのSEOメタタグと静的コンテンツを一括更新するスクリプト

変更点:
- data/politicians/{id}.json を参照して詳細なメタ description を生成
- <main> タグ内に静的コンテンツ（名前・経歴・公約リスト）を埋め込む
  → JSロード後に root.innerHTML で上書きされるため見た目に影響なし
  → Googlebotが「読み込み中...」でなく実際のコンテンツを読める
"""

import os
import re
import json
from html import escape

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POLITICIANS_JS = os.path.join(BASE_DIR, "js", "politicians.js")
POLITICIANS_DIR = os.path.join(BASE_DIR, "politicians")
DATA_DIR = os.path.join(BASE_DIR, "data", "politicians")


def parse_politicians_js():
    """js/politicians.js からカードデータを {id: card} で返す"""
    with open(POLITICIANS_JS, encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'const politicians = (\[.*?\]);', content, re.DOTALL)
    if not match:
        raise ValueError("politicians配列が見つかりません")
    js_array = match.group(1)
    js_array = re.sub(r'(\s)([a-zA-Z_][a-zA-Z0-9_]*):', r'\1"\2":', js_array)
    js_array = re.sub(r',(\s*[}\]])', r'\1', js_array)
    return {p['id']: p for p in json.loads(js_array)}


def load_politician_json(id_):
    """data/politicians/{id}.json を読み込む。なければ None。"""
    path = os.path.join(DATA_DIR, f"{id_}.json")
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    return None


def name_no_space(name):
    return (name or '').replace(' ', '').replace('　', '')


def build_head(id_, jdata, card):
    """<head> HTML を生成。jdata (詳細JSON) があれば優先使用。"""
    name = name_no_space((jdata or card or {}).get('name', id_))
    party = (jdata or card or {}).get('party', '')
    area  = (jdata or card or {}).get('area', '')

    if jdata:
        role    = jdata.get('party_role') or jdata.get('current_status') or ''
        summary = jdata.get('summary', '')
        if summary:
            meta_desc = f"{name}（{party}・{area}）の公約・発言・実績を検証。{summary[:80]}..."
        else:
            meta_desc = f"{name}（{party}・{area}）の公約・発言・実績を一次情報で検証。"
    else:
        role  = (card or {}).get('role', '政治家')
        desc  = (card or {}).get('desc', '')
        if desc:
            meta_desc = f"{name}（{party}・{area}）の公約・発言・実績を検証。{desc[:60]}..."
        else:
            meta_desc = f"{name}（{party}）の公約・発言・実績を一次情報で検証。{role}としての約束が守られたかを確認できます。"

    canonical = f"https://polimiru.jp/politicians/{id_}/"
    title     = f"{name}の公約・実績まとめ｜約束は守られたか - Polimiru"
    e = lambda s: escape(str(s or ''), quote=True)

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{e(meta_desc)}">
    <link rel="canonical" href="{canonical}">
    <meta property="og:type" content="profile">
    <meta property="og:title" content="{name}の公約・実績まとめ - Polimiru">
    <meta property="og:description" content="{e(meta_desc)}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:image" content="https://polimiru.jp/images/ogp/{id_}.png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:site_name" content="Polimiru">
    <meta property="og:locale" content="ja_JP">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{name}の公約・実績まとめ - Polimiru">
    <meta name="twitter:description" content="{e(meta_desc)}">
    <meta name="twitter:image" content="https://polimiru.jp/images/ogp/{id_}.png">
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "Person",
      "name": "{name}",
      "jobTitle": "{e(role)}",
      "memberOf": {{ "@type": "Organization", "name": "{e(party)}" }},
      "url": "{canonical}"
    }}
    </script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
    <link rel="stylesheet" href="../../css/base.css">
    <link rel="stylesheet" href="../../css/header-footer.css">
    <link rel="stylesheet" href="../../css/politician-record.css">
    <link rel="stylesheet" href="../../css/modal.css">
    <link rel="stylesheet" href="../../css/comments.css">"""


def build_static_main(jdata):
    """
    Googlebot 向けの静的コンテンツを生成する。
    JS ロード後に root.innerHTML で完全上書きされるため見た目への影響なし。
    """
    if not jdata:
        return '読み込み中...'

    e = lambda s: escape(str(s or ''))
    parts = ['<div class="seo-prerender">']

    name    = jdata.get('name', '')
    kana    = jdata.get('kana', '')
    party   = jdata.get('party', '')
    role    = jdata.get('party_role') or jdata.get('current_status') or ''
    area    = jdata.get('area', '')
    summary = jdata.get('summary', '')
    stats   = jdata.get('stats', [])
    career  = jdata.get('career', [])
    cycles  = jdata.get('promise_cycles', [])

    parts.append(f'<h1>{e(name)}（{e(kana)}）</h1>')
    parts.append(f'<p>{e(party)} / {e(role)} / {e(area)}</p>')

    if summary:
        parts.append(f'<p>{e(summary)}</p>')

    if stats:
        parts.append('<h2>基本情報</h2><ul>')
        for s in stats:
            parts.append(f'<li>{e(s.get("label",""))}: {e(s.get("value",""))}</li>')
        parts.append('</ul>')

    if career:
        parts.append('<h2>経歴</h2><ul>')
        for c in career:
            period = c.get('period', '')
            text   = c.get('text') or c.get('role') or c.get('title') or ''
            parts.append(f'<li>{e(period)}: {e(text)}</li>')
        parts.append('</ul>')

    for cycle in cycles:
        parts.append(f'<h2>{e(cycle.get("title", "公約"))}</h2>')
        ctx = cycle.get('context', '')
        if ctx:
            parts.append(f'<p>{e(ctx)}</p>')
        score = cycle.get('score')
        if score is not None:
            parts.append(f'<p>公約進捗スコア: {e(score)}/100</p>')
        highlights = cycle.get('highlights', [])
        if highlights:
            parts.append('<ul>')
            for h in highlights:
                parts.append(
                    f'<li>[{e(h.get("status",""))}] {e(h.get("title",""))}（{e(h.get("category",""))}）</li>'
                )
            parts.append('</ul>')

    parts.append('</div>')
    return '\n'.join(parts)


def update_politician_page(id_, jdata, card):
    html_path = os.path.join(POLITICIANS_DIR, id_, "index.html")
    if not os.path.exists(html_path):
        return False

    with open(html_path, encoding="utf-8") as f:
        content = f.read()

    # 旧URLなどのリダイレクトページは、人物ページ用HTMLへ展開し直さない
    if 'http-equiv="refresh"' in content.lower() and not jdata and not card:
        return False

    head_end = re.search(r'</head>', content)
    if not head_end:
        return False

    body_part = content[head_end.start():]

    # <main id="politician-record-root"> ... </main> の中身を静的コンテンツで置換
    static_html = build_static_main(jdata)
    body_part = re.sub(
        r'(<main id="politician-record-root"[^>]*>).*?(</main>)',
        lambda m: m.group(1) + static_html + m.group(2),
        body_part,
        flags=re.DOTALL,
        count=1,
    )

    new_content = build_head(id_, jdata, card or {}) + "\n" + body_part
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True


def main():
    cards_by_id = parse_politicians_js()

    # politicians/ ディレクトリ配下の全 index.html を対象にする
    all_ids = sorted(
        entry for entry in os.listdir(POLITICIANS_DIR)
        if os.path.isfile(os.path.join(POLITICIANS_DIR, entry, "index.html"))
    )

    print(f"{len(all_ids)} 人の政治家ページを処理\n")
    updated = 0
    for id_ in all_ids:
        jdata  = load_politician_json(id_)
        card   = cards_by_id.get(id_)
        result = update_politician_page(id_, jdata, card)
        if result:
            name = (jdata or card or {}).get('name', id_)
            print(f"  OK: {id_} ({name})")
            updated += 1
        else:
            print(f"  SKIP: {id_}")

    print(f"\n完了: {updated}/{len(all_ids)} ページを更新しました")


if __name__ == "__main__":
    main()
