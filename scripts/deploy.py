#!/usr/bin/env python3
"""
deploy.py — Polimiru のビルドを一括実行する

使い方:
  python scripts/deploy.py          # 差分のみ更新（通常運用）
  python scripts/deploy.py --force  # 全ファイルを強制再生成
  python scripts/deploy.py --dry    # 実行内容を表示するだけ

実行順序:
  1. OGP 画像生成  (generate_ogp.py)  — politician JSON が更新されたものだけ
  2. SEO メタタグ更新 (update_seo.py)  — 全政治家ページの <head>
  3. 選挙ページ生成  (build.py)        — elections.yaml から HTML / JS
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

SCRIPTS = Path(__file__).parent


def step(label):
    print(f"\n{'─' * 52}")
    print(f"  {label}")
    print(f"{'─' * 52}")


def run(cmd, dry):
    print(f"  $ {' '.join(cmd)}", flush=True)
    if dry:
        return True
    result = subprocess.run(cmd, cwd=SCRIPTS.parent)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Polimiru ビルドを一括実行")
    parser.add_argument("--force", action="store_true", help="全ファイルを強制再生成")
    parser.add_argument("--dry",   action="store_true", help="実行内容の表示のみ（書き込まない）")
    args = parser.parse_args()

    start = time.time()
    errors = []

    # 1. OGP 画像生成
    step("1/3  OGP 画像生成")
    ogp_cmd = [sys.executable, str(SCRIPTS / "generate_ogp.py")]
    if args.force:
        ogp_cmd.append("--force")
    if not run(ogp_cmd, args.dry):
        errors.append("generate_ogp.py")

    # 2. SEO メタタグ更新
    step("2/3  SEO メタタグ更新")
    if not run([sys.executable, str(SCRIPTS / "update_seo.py")], args.dry):
        errors.append("update_seo.py")

    # 3. 選挙ページ生成
    step("3/3  選挙ページ生成")
    build_cmd = [sys.executable, str(SCRIPTS / "build.py")]
    if not run(build_cmd, args.dry):
        errors.append("build.py")

    # サマリー
    elapsed = time.time() - start
    print(f"\n{'═' * 52}")
    if errors:
        print(f"  完了（エラーあり）: {', '.join(errors)}  [{elapsed:.1f}s]")
        sys.exit(1)
    else:
        mode = "（dry run）" if args.dry else ""
        print(f"  ✓ 全ステップ完了 {mode}  [{elapsed:.1f}s]")
        if not args.dry:
            print("  次のステップ: git add -A && git commit && git push")
    print(f"{'═' * 52}\n")


if __name__ == "__main__":
    main()
