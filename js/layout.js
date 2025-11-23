// =========================================
//  ベースURLを求めるヘルパー（修正版）
// =========================================
function getBaseUrl() {
    const origin = window.location.origin;   // 例: http://127.0.0.1:5500
    const path   = window.location.pathname; // 例: /elections/machida.html

    // 1. GitHub Pages 対応 (/polimiru/ 配下の場合)
    if (path.includes('/polimiru/')) {
        return origin + '/polimiru/';
    }

    // 2. ローカル開発環境の修正ポイント
    // URLに /elections/ が含まれている場合、それはサブフォルダなので
    // ルート（トップ）に戻るために origin + '/' を返します。
    if (path.includes('/elections/')) {
        return origin + '/';
    }

    // 3. それ以外（ルート直下など）
    // 基本的にローカルのLive Serverならルートは '/' です
    return origin + '/';
}

// =========================================
//  共通ヘッダー
// =========================================
function loadHeader() {
    const baseUrl     = getBaseUrl();
    const homePath    = baseUrl + 'index.html';
    const contactPath = baseUrl + 'contact.html';

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
            <a href="${contactPath}" class="contact-btn">Contact</a>
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
                <div class="region-group">
                    <h4>北海道・東北</h4>
                    <div class="pref-buttons">
                        <button onclick="setArea('hokkaido', '北海道')">北海道</button>
                        <button onclick="setArea('aomori', '青森県')">青森県</button>
                        <button onclick="setArea('iwate', '岩手県')">岩手県</button>
                        <button onclick="setArea('miyagi', '宮城県')">宮城県</button>
                        <button onclick="setArea('akita', '秋田県')">秋田県</button>
                        <button onclick="setArea('yamagata', '山形県')">山形県</button>
                        <button onclick="setArea('fukushima', '福島県')">福島県</button>
                    </div>
                </div>
                <div class="region-group">
                    <h4>関東</h4>
                    <div class="pref-buttons">
                        <button onclick="setArea('ibaraki', '茨城県')">茨城県</button>
                        <button onclick="setArea('tochigi', '栃木県')">栃木県</button>
                        <button onclick="setArea('gunma', '群馬県')">群馬県</button>
                        <button onclick="setArea('saitama', '埼玉県')">埼玉県</button>
                        <button onclick="setArea('chiba', '千葉県')">千葉県</button>
                        <button onclick="setArea('tokyo', '東京都')">東京都</button>
                        <button onclick="setArea('kanagawa', '神奈川県')">神奈川県</button>
                    </div>
                </div>
                <div class="region-group">
                    <h4>中部</h4>
                    <div class="pref-buttons">
                        <button onclick="setArea('niigata', '新潟県')">新潟県</button>
                        <button onclick="setArea('toyama', '富山県')">富山県</button>
                        <button onclick="setArea('ishikawa', '石川県')">石川県</button>
                        <button onclick="setArea('fukui', '福井県')">福井県</button>
                        <button onclick="setArea('yamanashi', '山梨県')">山梨県</button>
                        <button onclick="setArea('nagano', '長野県')">長野県</button>
                        <button onclick="setArea('gifu', '岐阜県')">岐阜県</button>
                        <button onclick="setArea('shizuoka', '静岡県')">静岡県</button>
                        <button onclick="setArea('aichi', '愛知県')">愛知県</button>
                    </div>
                </div>
                <div class="region-group">
                    <h4>近畿</h4>
                    <div class="pref-buttons">
                        <button onclick="setArea('mie', '三重県')">三重県</button>
                        <button onclick="setArea('shiga', '滋賀県')">滋賀県</button>
                        <button onclick="setArea('kyoto', '京都府')">京都府</button>
                        <button onclick="setArea('osaka', '大阪府')">大阪府</button>
                        <button onclick="setArea('hyogo', '兵庫県')">兵庫県</button>
                        <button onclick="setArea('nara', '奈良県')">奈良県</button>
                        <button onclick="setArea('wakayama', '和歌山県')">和歌山県</button>
                    </div>
                </div>
                <div class="region-group">
                    <h4>中国・四国</h4>
                    <div class="pref-buttons">
                        <button onclick="setArea('tottori', '鳥取県')">鳥取県</button>
                        <button onclick="setArea('shimane', '島根県')">島根県</button>
                        <button onclick="setArea('okayama', '岡山県')">岡山県</button>
                        <button onclick="setArea('hiroshima', '広島県')">広島県</button>
                        <button onclick="setArea('yamaguchi', '山口県')">山口県</button>
                        <button onclick="setArea('tokushima', '徳島県')">徳島県</button>
                        <button onclick="setArea('kagawa', '香川県')">香川県</button>
                        <button onclick="setArea('ehime', '愛媛県')">愛媛県</button>
                        <button onclick="setArea('kochi', '高知県')">高知県</button>
                    </div>
                </div>
                <div class="region-group">
                    <h4>九州・沖縄</h4>
                    <div class="pref-buttons">
                        <button onclick="setArea('fukuoka', '福岡県')">福岡県</button>
                        <button onclick="setArea('saga', '佐賀県')">佐賀県</button>
                        <button onclick="setArea('nagasaki', '長崎県')">長崎県</button>
                        <button onclick="setArea('kumamoto', '熊本県')">熊本県</button>
                        <button onclick="setArea('oita', '大分県')">大分県</button>
                        <button onclick="setArea('miyazaki', '宮崎県')">宮崎県</button>
                        <button onclick="setArea('kagoshima', '鹿児島県')">鹿児島県</button>
                        <button onclick="setArea('okinawa', '沖縄県')">沖縄県</button>
                    </div>
                </div>

                <div class="clear-area">
                    <button onclick="setArea(null, 'エリア未設定')" class="clear-btn">
                        <i class="fa-regular fa-trash-can"></i> 設定を解除する
                    </button>
                </div>
            </div>
        </div>
    </div>
    `;

    document.body.insertAdjacentHTML('afterbegin', headerHTML);

    // --- ハンバーガーメニューの処理 ---
    const hamburgerBtn      = document.getElementById('hamburger-btn');
    const closeBtn          = document.getElementById('close-btn');
    const navLinksContainer = document.getElementById('nav-links-container');
    const overlay           = document.getElementById('menu-overlay');

    const openMenu = () => {
        if (!navLinksContainer) return;
        navLinksContainer.classList.add('active');
        if (overlay) overlay.classList.add('active');
        document.body.classList.add('no-scroll');
    };

    const closeMenu = () => {
        if (!navLinksContainer) return;
        navLinksContainer.classList.remove('active');
        if (overlay) overlay.classList.remove('active');
        document.body.classList.remove('no-scroll');
    };

    if (hamburgerBtn) {
        hamburgerBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            openMenu();
        });
    }
    if (closeBtn)  closeBtn.addEventListener('click', closeMenu);
    if (overlay)   overlay.addEventListener('click', closeMenu);

    // ★ Contact だけは「絶対 contact に飛ぶ」保険をかける
    const contactLink = document.querySelector('#nav-links-container .contact-btn');
    if (contactLink) {
        contactLink.addEventListener('click', (e) => {
            // 念の為デフォルト動作を一度止めて、確実に遷移させる
            e.preventDefault();
            closeMenu();
            window.location.href = contactPath;
        });
    }

    // --- エリア設定モーダル ---
    const areaBtn      = document.getElementById('area-btn');
    const areaModal    = document.getElementById('area-modal');
    const closeModalBtn = document.getElementById('close-modal-btn');

    if (areaBtn) {
        areaBtn.addEventListener('click', () => {
            areaModal.classList.add('active');
        });
    }

    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', () => {
            areaModal.classList.remove('active');
        });
    }

    checkSavedArea();
}

// =========================================
//  エリア保存 / 反映
// =========================================
window.setArea = function(areaId, areaName) {
    if (areaId) {
        localStorage.setItem('my_area_id',   areaId);
        localStorage.setItem('my_area_name', areaName);
    } else {
        localStorage.removeItem('my_area_id');
        localStorage.removeItem('my_area_name');
    }
    location.reload();
};

function checkSavedArea() {
    const savedName = localStorage.getItem('my_area_name');
    const btn = document.getElementById('area-btn');
    
    if (btn) {
        const btnSpan = btn.querySelector('span');
        if (savedName) {
            btnSpan.textContent = savedName;
            btn.classList.add('is-set');
        } else {
            btnSpan.textContent = 'エリア未設定';
            btn.classList.remove('is-set');
        }
    }
}

// =========================================
//  共通フッター
// =========================================
function loadFooter() {
    const footerHTML = `
    <footer class="site-footer">
        <div class="footer-social">
            <span class="follow-text">Follow polimiru</span>
            <a href="#" class="social-icon"><i class="fa-brands fa-facebook-f"></i></a>
            <a href="#" class="social-icon"><i class="fa-brands fa-x-twitter"></i></a>
            <a href="#" class="social-icon"><i class="fa-brands fa-youtube"></i></a>
            <a href="https://www.instagram.com/polimiru?igsh=MXRjdXE2dG9vcHk0MA%3D%3D&utm_source=qr" class="social-icon"><i class="fa-brands fa-instagram"></i></a>
        </div>
        <a href="#" class="back-to-top">
            <i class="fa-solid fa-arrow-up"></i> Back to top
        </a>
    </footer>
    `;
    document.body.insertAdjacentHTML('beforeend', footerHTML);
}

// =========================================
//  DOMContentLoaded
// =========================================
document.addEventListener('DOMContentLoaded', () => {
    loadHeader();
    loadFooter();

    // スコア説明リンク（method.html）のパスも baseUrl から作る
    const baseUrl    = getBaseUrl();
    const methodPath = baseUrl + 'method.html';

    const headers = document.querySelectorAll('.js-score-method-header');

    headers.forEach(header => {
        if (header.querySelector('.score-method-link')) return;

        const link = document.createElement('a');
        link.href      = methodPath;
        link.className = 'score-method-link';
        link.textContent = 'スコアの計算方法を見る';

        header.appendChild(link);
    });
});