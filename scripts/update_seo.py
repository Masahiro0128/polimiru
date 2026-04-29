#!/usr/bin/env python3
"""全政治家ページのSEOメタタグを一括更新するスクリプト"""

import os
import re
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POLITICIANS_JS = os.path.join(BASE_DIR, "js", "politicians.js")
POLITICIANS_DIR = os.path.join(BASE_DIR, "politicians")

def parse_politicians():
    with open(POLITICIANS_JS, encoding="utf-8") as f:
        content = f.read()
    # JSのconst宣言を取り除いてJSONとして読み込めるよう変換
    match = re.search(r'const politicians = (\[.*?\]);', content, re.DOTALL)
    if not match:
        raise ValueError("politicians配列が見つかりません")
    js_array = match.group(1)
    # JSのキー（クォートなし）をJSONのキー（クォートあり）に変換
    js_array = re.sub(r'(\s)([a-zA-Z_][a-zA-Z0-9_]*):', r'\1"\2":', js_array)
    # 末尾カンマを除去
    js_array = re.sub(r',(\s*[}\]])', r'\1', js_array)
    return json.loads(js_array)

def name_no_space(name):
    return name.replace(" ", "").replace("　", "")

def build_head(p):
    id_ = p["id"]
    name = name_no_space(p["name"])
    party = p.get("party", "")
    role = p.get("role", "政治家")
    desc = p.get("desc", "")
    area = p.get("area", "")

    title = f"{name}の公約・実績まとめ｜約束は守られたか - Polimiru"
    meta_desc = f"{name}（{party}）の公約・発言・実績を一次情報で検証。{role}としての約束が守られたかを時系列で確認できます。"
    if desc:
        meta_desc = f"{name}（{party}・{area}）の公約・発言・実績を検証。{desc[:40]}..."
    canonical = f"https://polimiru.jp/politicians/{id_}/"

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_desc}">
    <link rel="canonical" href="{canonical}">
    <meta property="og:type" content="profile">
    <meta property="og:title" content="{name}の公約・実績まとめ - Polimiru">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:image" content="https://polimiru.jp/images/ogp/{id_}.png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:site_name" content="Polimiru">
    <meta property="og:locale" content="ja_JP">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{name}の公約・実績まとめ - Polimiru">
    <meta name="twitter:description" content="{meta_desc}">
    <meta name="twitter:image" content="https://polimiru.jp/images/ogp/{id_}.png">
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "Person",
      "name": "{name}",
      "jobTitle": "{role}",
      "memberOf": {{ "@type": "Organization", "name": "{party}" }},
      "url": "{canonical}"
    }}
    </script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
    <link rel="stylesheet" href="../../css/base.css">
    <link rel="stylesheet" href="../../css/header-footer.css">
    <link rel="stylesheet" href="../../css/politician-record.css">
    <link rel="stylesheet" href="../../css/modal.css">
    <link rel="stylesheet" href="../../css/comments.css">"""

def update_politician_page(p):
    id_ = p["id"]
    html_path = os.path.join(POLITICIANS_DIR, id_, "index.html")
    if not os.path.exists(html_path):
        print(f"  SKIP (not found): {id_}")
        return False

    with open(html_path, encoding="utf-8") as f:
        content = f.read()

    # <head>...</head> の間を置き換え（</head>より前の部分）
    # bodyタグ以降は保持する
    body_match = re.search(r'</head>', content)
    if not body_match:
        print(f"  SKIP (no </head>): {id_}")
        return False

    body_part = content[body_match.start():]  # </head>から末尾まで

    new_content = build_head(p) + "\n" + body_part
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True

def main():
    politicians = parse_politicians()
    print(f"{len(politicians)}人の政治家データを読み込みました\n")

    updated = 0
    for p in politicians:
        result = update_politician_page(p)
        if result:
            print(f"  OK: {p['id']} ({name_no_space(p['name'])})")
            updated += 1

    print(f"\n完了: {updated}/{len(politicians)} ページを更新しました")

if __name__ == "__main__":
    main()
