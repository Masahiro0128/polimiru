import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "data" / "raw" / "osaka_2023" / "osaka_results.json"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # 基本の待ち時間を設定
        page.set_default_timeout(60000)

        print("🚀 大阪府議会検索システムにアクセス...")
        page.goto("https://ssp.kaigiroku.net/tenant/prefosaka/SpTop.html")

        # 1. メニューを開く
        print("🖱️ 検索メニューを開きます")
        page.locator("#search_icon").click()

        # 2. キーワード入力
        print("✍️ '吉村洋文' と入力...")
        page.get_by_role("textbox", name="キーワード").fill("吉村洋文")

        # -------------------------------------------
        # 【追加！】期間を「令和7年～令和3年」に絞る
        # -------------------------------------------
        print("📅 期間を '令和7年～令和3年' に設定します...")
        # 「対象年度」の行にあるドロップダウン(selectタグ)を探して選択
        page.locator("tr", has_text="対象年度").locator("select").select_option(label="令和7年～令和3年")

        # 3. 検索ボタンクリック
        print("🖱️ 検索ボタンをクリック！")
        page.locator("#v-search").click()

        # 4. 結果待ち
        print("⏳ 検索結果を待っています...")
        try:
            # ヒットした合図を待つ
            page.wait_for_selector("text=ヒットしました")
            print("✅ 結果が表示されました！")
            page.wait_for_timeout(2000) # ちょっと待つ

        except Exception:
            print("❌ タイムアウト。画面を保存します。")
            page.screenshot(path="error_debug.png")
            browser.close()
            return

        # 5. データ取得
        print("📥 データを読み取っています...")
        items = page.get_by_role("listitem").all()
        
        results_data = []
        for item in items:
            text = item.inner_text().replace("\n", " ").strip()
            if text:
                print(f"  - {text[:20]}...")
                results_data.append(text)

        # 6. 保存
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(results_data, f, ensure_ascii=False, indent=4)

        print(f"🎉 {len(results_data)} 件のデータを保存しました！({OUTPUT_PATH})")
        page.screenshot(path="success_result.png")
        browser.close()

if __name__ == "__main__":
    run()
