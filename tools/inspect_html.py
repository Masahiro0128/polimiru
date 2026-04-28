import time
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.set_default_timeout(60000)

        print("🚀 大阪府議会検索システムにアクセス...")
        page.goto("https://ssp.kaigiroku.net/tenant/prefosaka/SpTop.html")

        # --- いつもの検索手順 ---
        page.locator("#search_icon").click()
        page.get_by_role("textbox", name="キーワード").fill("吉村洋文")
        # 期間指定（データ量を減らすため）
        page.locator("tr", has_text="対象年度").locator("select").select_option(label="令和7年～令和3年")
        page.locator("#v-search").click()
        
        print("⏳ 検索結果を待っています...")
        page.wait_for_selector("text=ヒットしました")
        page.wait_for_timeout(2000)

        # --- ここから解析 ---
        print("🔍 1件目のリストの中身を解析します...")

        # 1件目のリストアイテムを取得
        first_item = page.get_by_role("listitem").first
        
        # 【重要】そのHTMLコードを抜き出す
        html_content = first_item.inner_html()

        print("\n" + "="*30)
        print("▼ ここから下がHTMLの正体です ▼")
        print("="*30)
        print(html_content)
        print("="*30 + "\n")

        # 念のため、そのリストアイテム自体を強力にクリックしてみる（force=True）
        print("👆 無理やりクリックしてみます...")
        first_item.click(force=True)
        
        page.wait_for_timeout(5000)
        
        # 画面が切り替わったかタイトルで確認
        print(f"現在のページタイトル: {page.title()}")
        if "SpTop" not in page.url:
            print("🎉 画面遷移に成功しました！(URLが変わりました)")
        else:
            print("💦 まだトップページのままです。HTML解析が必要です。")

        browser.close()

if __name__ == "__main__":
    run()