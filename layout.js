// 共通ヘッダーを作る関数
function loadHeader() {
    const headerHTML = `
    <nav class="site-navbar">
        <a href="index.html" class="site-logo">polimiru</a>
        
        <button class="hamburger-menu" id="hamburger-btn">
            <i class="fa-solid fa-bars"></i>
        </button>

        <div class="nav-links" id="nav-links-container">
            <button class="close-menu" id="close-btn">
                <i class="fa-solid fa-xmark"></i>
            </button>

            <a href="#">About</a>
            <a href="#">News</a>
            <a href="#">Elections</a>
            <a href="#" class="contact-btn">Contact</a>
        </div>
    </nav>
    <div class="menu-overlay" id="menu-overlay"></div>
    `;
    // bodyの一番最初に挿入
    document.body.insertAdjacentHTML('afterbegin', headerHTML);

    // --- ハンバーガーメニューの動きをここに書く ---
    const hamburgerBtn = document.getElementById('hamburger-btn');
    const closeBtn = document.getElementById('close-btn');
    const navLinksContainer = document.getElementById('nav-links-container');
    const overlay = document.getElementById('menu-overlay');

    // メニューを開く・閉じる関数
    const toggleMenu = () => {
        navLinksContainer.classList.toggle('active'); // メニューに active クラスを付け外し
        overlay.classList.toggle('active'); // 背景に active クラスを付け外し
        document.body.classList.toggle('no-scroll'); // メニューが開いている間はスクロール禁止
    };

    // ボタンクリックで実行
    if (hamburgerBtn) hamburgerBtn.addEventListener('click', toggleMenu);
    if (closeBtn) closeBtn.addEventListener('click', toggleMenu);
    if (overlay) overlay.addEventListener('click', toggleMenu); // 背景をクリックしても閉じる
}

// 共通フッターを作る関数（変更なし）
function loadFooter() {
    const footerHTML = `
    <footer class="site-footer">
        <div class="footer-social">
            <span class="follow-text">Follow polimiru</span>
            <a href="#" class="social-icon"><i class="fa-brands fa-facebook-f"></i></a>
            <a href="#" class="social-icon"><i class="fa-brands fa-x-twitter"></i></a>
            <a href="#" class="social-icon"><i class="fa-brands fa-youtube"></i></a>
            <a href="#" class="social-icon"><i class="fa-brands fa-instagram"></i></a>
        </div>
        <a href="#" class="back-to-top">
            <i class="fa-solid fa-arrow-up"></i> Back to top
        </a>
    </footer>
    `;
    document.body.insertAdjacentHTML('beforeend', footerHTML);
}

// 読み込みと同時に実行
document.addEventListener("DOMContentLoaded", () => {
    loadHeader();
    loadFooter();
});