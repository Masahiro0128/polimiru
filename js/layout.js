// =========================================
//  共通ヘッダー (超シンプル版)
// =========================================
function loadHeader() {
    // 現在のURLに '/elections/' が含まれているかチェック
    const isDeepPath = window.location.pathname.includes('/elections/');

    // electionsの中にいるなら '../' (一階層あがる)
    // そうでないなら './' (同じ階層)
    const pathPrefix = isDeepPath ? '../' : './';

    const homePath    = pathPrefix + 'index.html';
    const contactPath = pathPrefix + 'contact.html';
    const methodPath  = pathPrefix + 'method.html';

    const headerHTML = `
    <nav class="site-navbar">
        <a href="${homePath}" class="site-logo">polimiru</a>
        
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
            
            <a href="${contactPath}" class="contact-btn" onclick="window.location.href='${contactPath}'; return false;">Contact</a>
        </div>
    </nav>
    <div class="menu-overlay" id="menu-overlay"></div>
    
    <div id="area-modal" class="area-modal">
        <div class="modal-content modal-wide">
            <div class="modal-header">
                <h3>居住地を選択</h3>
                <button id="close-modal-btn" class="close-icon"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="area-scroll-box">
                 <div class="clear-area" style="margin-top:20px; text-align:center;">
                    <p>※エリア選択機能は省略しています</p>
                </div>
            </div>
        </div>
    </div>
    `;

    document.body.insertAdjacentHTML('afterbegin', headerHTML);

    // --- ハンバーガーメニュー開閉 ---
    const hamburgerBtn      = document.getElementById('hamburger-btn');
    const closeBtn          = document.getElementById('close-btn');
    const navLinksContainer = document.getElementById('nav-links-container');
    const overlay           = document.getElementById('menu-overlay');

    const toggleMenu = (isOpen) => {
        if (!navLinksContainer) return;
        if (isOpen) {
            navLinksContainer.classList.add('active');
            if (overlay) overlay.classList.add('active');
            document.body.classList.add('no-scroll');
        } else {
            navLinksContainer.classList.remove('active');
            if (overlay) overlay.classList.remove('active');
            document.body.classList.remove('no-scroll');
        }
    };

    if (hamburgerBtn) {
        hamburgerBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleMenu(true);
        });
    }
    if (closeBtn) closeBtn.addEventListener('click', () => toggleMenu(false));
    if (overlay)  overlay.addEventListener('click', () => toggleMenu(false));

    // --- スコア計算方法へのリンク生成 ---
    const headers = document.querySelectorAll('.js-score-method-header');
    headers.forEach(header => {
        if (header.querySelector('.score-method-link')) return;
        const link = document.createElement('a');
        link.href = methodPath;
        link.className = 'score-method-link';
        link.textContent = 'スコアの計算方法を見る';
        header.appendChild(link);
    });
}

// =========================================
//  共通フッター
// =========================================
function loadFooter() {
    const footerHTML = `
    <footer class="site-footer">
        <div class="footer-social">
            <span class="follow-text">Follow polimiru</span>
            <a href="#"><i class="fa-brands fa-x-twitter"></i></a>
        </div>
    </footer>
    `;
    document.body.insertAdjacentHTML('beforeend', footerHTML);
}

// =========================================
//  実行
// =========================================
document.addEventListener('DOMContentLoaded', () => {
    loadHeader();
    loadFooter();
});

// エリア機能のダミー関数（エラー防止用）
window.setArea = function() { location.reload(); };