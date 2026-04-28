import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data" / "raw" / "osaka_2023" / "yoshimura_speeches"

def run():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        # ブラウザを立ち上げる
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        # 読み込み待ち時間を長め（60秒）に設定
        page.set_default_timeout(60000)

        # 1. 検索画面に行く
        print("🚀 検索画面へ移動...")
        page.goto("https://ssp.kaigiroku.net/tenant/prefosaka/SpTop.html")

        # 2. 「吉村洋文」で検索する
        page.locator("#search_icon").click()
        page.get_by_role("textbox", name="キーワード").fill("吉村洋文")
        # 期間を絞る（直近4年）
        page.locator("tr", has_text="対象年度").locator("select").select_option(label="令和7年～令和3年")
        page.locator("#v-search").click()

        print("⏳ 検索結果を表示中...")
        page.wait_for_selector("text=ヒットしました")
        time.sleep(2)

        # 3. リストアップされた「会議名」をすべて見つける
        # シンプルに「号」という文字が入っているリンク(aタグ)だけを探します。
        # これでメニューボタン（TOPなど）は除外されます。
        links = page.locator("a").filter(has_text="号").all()
        
        print(f"📋 {len(links)} 件の会議が見つかりました。上から3件取得します。")

        # 4. 順番にクリックして中身を取る（3件だけ）
        limit = 3

        for i in range(limit):
            print(f"\n🔄 {i+1}件目を取得中...")

            # ページを戻るとリンク情報が古くなるので、毎回探し直して、i番目をクリックする
            target_link = page.locator("a").filter(has_text="号").nth(i)
            
            # クリックして中に入る
            target_link.click()

            # 中身が出るまで待つ
            page.wait_for_selector("body", timeout=10000)
            time.sleep(2)

            # テキストを全部コピーする
            full_text = page.locator("body").inner_text()

            # ファイルに保存する
            filename = OUTPUT_DIR / f"speech_{i}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(full_text)
            
            print(f"   ✅ 保存しました: {filename}")

            # 戻るボタンで一覧に戻る
            page.go_back()
            # 一覧が再表示されるのを待つ
            page.wait_for_selector("text=ヒットしました")

        print("\n🎉 完了しました。")
        browser.close()

if __name__ == "__main__":
    run()
