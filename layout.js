// 共通ヘッダーを作る関数
function loadHeader() {
    const headerHTML = `
    <nav class="site-navbar">
        <a href="index.html" class="site-logo">polimiru</a>
        <div class="nav-links">
            <a href="#">About</a>
            <a href="#">News</a>
            <a href="#">Elections</a>
            <a href="#" class="contact-btn">Contact</a>
        </div>
    </nav>
    `;
    // bodyの一番最初に挿入
    document.body.insertAdjacentHTML('afterbegin', headerHTML);
}

// 共通フッターを作る関数
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
    // bodyの一番最後に挿入
    document.body.insertAdjacentHTML('beforeend', footerHTML);
}

// 読み込みと同時に実行
document.addEventListener("DOMContentLoaded", () => {
    loadHeader();
    loadFooter();
});