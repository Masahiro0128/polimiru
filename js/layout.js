// =========================================
//  ベースURLを求めるヘルパー（最強版）
// =========================================
function getBaseUrl() {
    const origin = window.location.origin;
    const path   = window.location.pathname;

    // GitHub Pages対応
    if (path.includes('/polimiru/')) {
        return origin + '/polimiru/';
    }
    
    // ローカル環境 (Live Server) の場合はルートを返す
    return origin + '/'; 
}

// =========================================
//  共通ヘッダー & モーダル制御
// =========================================
function loadHeader() {
    // ★現在の階層からルートまでの相対パスを自動計算
    const pathParts = window.location.pathname.split('/').filter(p => p !== '');
    const isGitHub = window.location.pathname.includes('/polimiru/');

    // 末尾スラッシュ（ディレクトリURL）の場合はファイル名がないため +1 する
    const fileDepth = window.location.pathname.endsWith('/')
        ? pathParts.length
        : pathParts.length - 1;
    const depth = isGitHub ? fileDepth - 1 : fileDepth;

    // 深さの分だけ "../" を繋げる。ルートなら "./"
    let pathPrefix = '';
    if (depth > 0) {
        pathPrefix = '../'.repeat(depth);
    } else {
        pathPrefix = './';
    }

    if (!document.querySelector('link[href$="css/modal.css"]')) {
        const modalStyle = document.createElement('link');
        modalStyle.rel = 'stylesheet';
        modalStyle.href = pathPrefix + 'css/modal.css';
        document.head.appendChild(modalStyle);
    }

    // リンク先を生成
    const homePath      = pathPrefix + 'index.html';
    const aboutPath     = pathPrefix + 'about.html';
    const electionsPath = pathPrefix + 'elections/index.html';
    const newsPath      = pathPrefix + 'news.html';
    const contactPath   = pathPrefix + 'contact.html';
    const methodPath    = pathPrefix + 'method.html';

    // HTML生成
    const headerHTML = `
    <nav class="site-navbar">
        <div class="nav-logo-group">
            <a href="${homePath}" class="site-logo">
                <img src="${pathPrefix}images/logo-icon.png" alt="polimiru" class="site-logo-img">
                <span class="site-logo-text">polimiru</span>
            </a>
            <span class="site-tagline">公約と実績を見える化する、<br>日本最大級の政治家ファクトチェック・データベース</span>
        </div>
        <button class="hamburger-menu" id="hamburger-btn">
            <i class="fa-solid fa-bars"></i>
        </button>
        <div class="nav-links" id="nav-links-container">
            <button class="close-menu" id="close-btn">
                <i class="fa-solid fa-xmark"></i>
            </button>
            <a href="${aboutPath}">
                <span class="nav-en">About</span>
                <span class="nav-ja">私たちについて</span>
            </a>
            <a href="${newsPath}">
                <span class="nav-en">News</span>
                <span class="nav-ja">ニュース</span>
            </a>
            <a href="${electionsPath}">
                <span class="nav-en">Elections</span>
                <span class="nav-ja">選挙・データ</span>
            </a>
<a href="${contactPath}" class="contact-btn">
                <span class="nav-en">Contact</span>
                <span class="nav-ja">お問い合わせ</span>
            </a>
        </div>
        <button class="area-btn-nav" id="area-btn">
            <i class="fa-solid fa-location-dot"></i>
            <span>エリアを設定</span>
        </button>
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

    // --- ハンバーガーメニュー処理 ---
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

    if (hamburgerBtn) hamburgerBtn.addEventListener('click', (e) => { 
        e.stopPropagation(); 
        toggleMenu(true); 
    });
    if (closeBtn) closeBtn.addEventListener('click', () => toggleMenu(false));
    if (overlay) overlay.addEventListener('click', () => toggleMenu(false));

    // --- エリア選択ボタンの動作 ---
    const areaBtn      = document.getElementById('area-btn');
    const areaModal    = document.getElementById('area-modal');
    const closeModalBtn = document.getElementById('close-modal-btn');

    if (areaBtn && areaModal) {
        areaBtn.addEventListener('click', () => { areaModal.classList.add('active'); });
    }
    if (closeModalBtn && areaModal) {
        closeModalBtn.addEventListener('click', () => { areaModal.classList.remove('active'); });
    }
    
    checkSavedArea();
    
    // --- スコア説明リンク ---
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
//  エリア保存 / 反映
// =========================================
window.setArea = function(areaId, areaName) {
    if (areaId) {
        localStorage.setItem('my_area_id', areaId);
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

    const areaLinkTitle = document.querySelector('.area-link-title');
    if (areaLinkTitle) {
        areaLinkTitle.textContent = savedName || 'エリアを設定';
    }
    const areaLinkSub = document.querySelector('.area-link-sub');
    if (areaLinkSub) {
        areaLinkSub.textContent = savedName ? '設定済み — タップして変更' : '地域を選択して情報を最適化';
    }
}

// =========================================
//  共通フッター
// =========================================
function loadFooter() {
    const footerHTML = `
    <footer class="site-footer">
        <div class="footer-support-band">
            <div class="footer-support-inner">
                <div class="footer-support-copy">
                    <p class="footer-support-heading">polimiru を応援する</p>
                    <p class="footer-support-sub">公約データベースの維持・拡充は、読者のみなさまの応援で成り立っています。noteでのサポートをお願いします。</p>
                </div>
                <a href="https://note.com/limber_gibbon907" class="footer-note-btn" target="_blank" rel="noopener">
                    <svg class="footer-note-logo" viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M17.5 0h-11C2.91 0 0 2.91 0 6.5v11C0 21.09 2.91 24 6.5 24h11c3.59 0 6.5-2.91 6.5-6.5v-11C24 2.91 21.09 0 17.5 0zm1.836 10.638l-1.628 6.001c-.133.484-.531.769-1.025.769-.133 0-.266-.019-.399-.057l-2.651-.72-1.529 1.12c-.19.133-.399.19-.608.19-.209 0-.418-.076-.589-.209-.342-.266-.513-.684-.437-1.102l.323-2.233-4.941-1.343c-.494-.133-.779-.57-.703-1.063.076-.494.456-.836.95-.836h.038l2.271.114 1.077-3.98c.209-.76.95-1.196 1.71-.988l5.777 1.571c.76.209 1.196.95.988 1.71l-.114.38 1.71.456c.494.133.779.57.703 1.063-.019.095-.057.19-.114.267z"/></svg>
                    noteでサポートする
                </a>
            </div>
        </div>
        <div class="footer-bottom-bar">
            <div class="footer-bottom-inner">
                <div class="footer-social-row">
                    <span class="footer-follow-label">Follow us</span>
                    <a href="https://x.com/polimiru?s=21" target="_blank" rel="noopener" class="footer-sns-btn">
                        <i class="fa-brands fa-x-twitter"></i><span>X</span>
                    </a>
                    <a href="https://www.instagram.com/polimiru?igsh=MXRjdXE2dG9vcHk0MA%3D%3D&utm_source=qr" target="_blank" rel="noopener" class="footer-sns-btn">
                        <i class="fa-brands fa-instagram"></i><span>Instagram</span>
                    </a>
                    <a href="https://note.com/limber_gibbon907" target="_blank" rel="noopener" class="footer-sns-btn">
                        <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14"><path d="M17.5 0h-11C2.91 0 0 2.91 0 6.5v11C0 21.09 2.91 24 6.5 24h11c3.59 0 6.5-2.91 6.5-6.5v-11C24 2.91 21.09 0 17.5 0zm1.836 10.638l-1.628 6.001c-.133.484-.531.769-1.025.769-.133 0-.266-.019-.399-.057l-2.651-.72-1.529 1.12c-.19.133-.399.19-.608.19-.209 0-.418-.076-.589-.209-.342-.266-.513-.684-.437-1.102l.323-2.233-4.941-1.343c-.494-.133-.779-.57-.703-1.063.076-.494.456-.836.95-.836h.038l2.271.114 1.077-3.98c.209-.76.95-1.196 1.71-.988l5.777 1.571c.76.209 1.196.95.988 1.71l-.114.38 1.71.456c.494.133.779.57.703 1.063-.019.095-.057.19-.114.267z"/></svg>
                        <span>note</span>
                    </a>
                </div>
                <div class="footer-right">
                    <span class="footer-copyright">© 2026 polimiru</span>
                    <a href="#" class="back-to-top"><i class="fa-solid fa-arrow-up"></i> Top</a>
                </div>
            </div>
        </div>
    </footer>
    `;
    
    const existingFooter = document.querySelector('footer');
    if (existingFooter) existingFooter.remove();

    document.body.insertAdjacentHTML('beforeend', footerHTML);
}

document.addEventListener('DOMContentLoaded', () => {
    loadHeader();
    loadFooter();
});
