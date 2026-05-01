(function () {
    const MIN_LEN = 5;
    const MAX_LEN = 500;
    const COMMENT_STATUS_APPROVED = 'approved';

    function esc(str) {
        return String(str || '').replace(/[&<>"']/g, c =>
            ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' })[c]);
    }

    function relTime(iso) {
        const m = Math.floor((Date.now() - new Date(iso)) / 60000);
        if (m <  1)  return 'たった今';
        if (m < 60)  return `${m}分前`;
        const h = Math.floor(m / 60);
        if (h < 24)  return `${h}時間前`;
        const d = Math.floor(h / 24);
        if (d < 30)  return `${d}日前`;
        const mo = Math.floor(d / 30);
        if (mo < 12) return `${mo}ヶ月前`;
        return `${Math.floor(mo / 12)}年前`;
    }

    function apiHeaders(accessToken) {
        return {
            apikey: window.SUPABASE_ANON_KEY,
            Authorization: `Bearer ${accessToken || window.SUPABASE_ANON_KEY}`,
        };
    }

    function validHttpUrl(value) {
        try {
            const url = new URL(String(value || '').trim());
            return url.protocol === 'https:' || url.protocol === 'http:';
        } catch {
            return false;
        }
    }

    async function fetchComments(politicianId) {
        const res = await fetch(
            `${window.SUPABASE_URL}/rest/v1/comments` +
            `?politician_id=eq.${encodeURIComponent(politicianId)}` +
            `&status=eq.${COMMENT_STATUS_APPROVED}&order=created_at.desc&limit=100`,
            { headers: apiHeaders() }
        );
        if (!res.ok) throw new Error(res.status);
        return res.json();
    }

    async function postComment(politicianId, user, session, body, sourceUrl) {
        const nickname = window.pAuth?.displayName(user) || user?.email || 'ログインユーザー';
        const res = await fetch(`${window.SUPABASE_URL}/rest/v1/comments`, {
            method: 'POST',
            headers: { ...apiHeaders(session.access_token), 'Content-Type': 'application/json', Prefer: 'return=representation' },
            body: JSON.stringify({
                politician_id: politicianId,
                user_id: user.id,
                nickname: nickname.trim() || '匿名',
                body: body.trim(),
                source_url: sourceUrl.trim(),
                status: 'pending',
            }),
        });
        if (!res.ok) throw new Error(res.status);
        return res.json();
    }

    function renderList(comments, listEl, countEl) {
        countEl.textContent = `${comments.length}件`;
        if (comments.length === 0) {
            listEl.innerHTML = '<p class="cb-empty">承認済みの発言ログはまだありません。</p>';
            return;
        }
        listEl.innerHTML = comments.map(c => {
            const sourceUrl = validHttpUrl(c.source_url) ? String(c.source_url).trim() : '';
            return `
                <div class="cb-item">
                    <div class="cb-meta">
                        <span class="cb-nick">${esc(c.nickname)}</span>
                        <span class="cb-time">${relTime(c.created_at)}</span>
                    </div>
                    <div class="cb-body">${esc(c.body)}</div>
                    ${sourceUrl ? `
                        <a class="cb-source" href="${esc(sourceUrl)}" target="_blank" rel="noopener">
                            <i class="fa-solid fa-link"></i>
                            根拠リンク
                        </a>
                    ` : '<span class="cb-source cb-source-missing">根拠リンク未登録</span>'}
                </div>`;
        }).join('');
    }

    async function init(politicianId, parentEl, insertBeforeEl) {
        if (!window.SUPABASE_URL || window.SUPABASE_URL.includes('xxxx')) return;
        if (document.getElementById('cb-' + politicianId)) return;

        const section = document.createElement('section');
        section.id        = 'cb-' + politicianId;
        section.className = 'cb-section';
        section.innerHTML = `
            <div class="cb-header">
                <h2 class="cb-title">発言ログ</h2>
                <span class="cb-count" id="cb-count-${politicianId}">読み込み中…</span>
            </div>
            <div class="cb-auth-panel" id="cb-auth-${politicianId}">
                <p class="cb-guidance">投稿にはアカウント登録が必要です。承認後に公開されます。</p>
                <div class="cb-auth-actions">
                    <button class="cb-auth-btn" type="button" data-auth-provider="google">
                        <i class="fa-brands fa-google"></i>
                        Googleで続ける
                    </button>
                    <button class="cb-auth-btn" type="button" data-auth-provider="apple">
                        <i class="fa-brands fa-apple"></i>
                        Appleで続ける
                    </button>
                </div>
                <form class="cb-email-form" id="cb-email-form-${politicianId}" novalidate>
                    <input class="cb-email-input" type="email" placeholder="メールアドレスでログインリンクを受け取る" autocomplete="email">
                    <button class="cb-email-submit" type="submit">送信</button>
                </form>
                <div class="cb-auth-status" id="cb-auth-status-${politicianId}"></div>
            </div>
            <div class="cb-user-panel" id="cb-user-${politicianId}" hidden>
                <span class="cb-user-label"></span>
                <button class="cb-signout" type="button">ログアウト</button>
            </div>
            <form class="cb-form" id="cb-form-${politicianId}" novalidate hidden>
                <p class="cb-guidance">
                    発言・公約・実績の根拠リンクを添えて記録してください。確認できない噂や個人攻撃は載せないでください。投稿は承認後に公開されます。
                </p>
                <input class="cb-source-input" type="url" placeholder="根拠リンク（必須）https://..." autocomplete="off" required>
                <textarea class="cb-body-input" placeholder="いつ・どこで・何を言っていたか（${MIN_LEN}〜${MAX_LEN}文字）"
                          maxlength="${MAX_LEN}" rows="3"></textarea>
                <div class="cb-form-footer">
                    <span class="cb-char">0 / ${MAX_LEN}</span>
                    <span class="cb-error" id="cb-err-${politicianId}"></span>
                </div>
                <button class="cb-submit" type="submit">承認待ちで投稿する</button>
            </form>
            <div class="cb-list" id="cb-list-${politicianId}">
                <p class="cb-empty">読み込み中…</p>
            </div>`;

        if (insertBeforeEl) parentEl.insertBefore(section, insertBeforeEl);
        else parentEl.appendChild(section);

        const listEl  = section.querySelector('.cb-list');
        const countEl = section.querySelector('.cb-count');
        const errEl   = section.querySelector('.cb-error');
        const authPanel = section.querySelector('.cb-auth-panel');
        const userPanel = section.querySelector('.cb-user-panel');
        const userLabel = section.querySelector('.cb-user-label');
        const signoutBtn = section.querySelector('.cb-signout');
        const emailForm = section.querySelector('.cb-email-form');
        const emailIn = section.querySelector('.cb-email-input');
        const authStatus = section.querySelector('.cb-auth-status');
        const form    = section.querySelector('.cb-form');
        const sourceIn = section.querySelector('.cb-source-input');
        const bodyIn  = section.querySelector('.cb-body-input');
        const charEl  = section.querySelector('.cb-char');
        const submitBtn = section.querySelector('.cb-submit');

        bodyIn.addEventListener('input', () => {
            charEl.textContent = `${bodyIn.value.length} / ${MAX_LEN}`;
        });

        async function load() {
            try {
                renderList(await fetchComments(politicianId), listEl, countEl);
            } catch {
                listEl.innerHTML = '<p class="cb-empty">読み込みに失敗しました。</p>';
                countEl.textContent = '';
            }
        }
        load();

        async function updateAuthUi() {
            const user = await (window.pAuth?.getUser ? window.pAuth.getUser() : Promise.resolve(null));
            const signedIn = !!user;
            authPanel.hidden = signedIn;
            userPanel.hidden = !signedIn;
            form.hidden = !signedIn;
            if (signedIn) {
                userLabel.textContent = `${window.pAuth.displayName(user)} でログイン中`;
            }
        }

        section.querySelectorAll('[data-auth-provider]').forEach(btn => {
            btn.addEventListener('click', () => {
                if (!window.pAuth) {
                    authStatus.textContent = 'ログイン設定を読み込めませんでした。';
                    return;
                }
                window.pAuth.signInWithOAuth(btn.dataset.authProvider);
            });
        });

        emailForm.addEventListener('submit', async e => {
            e.preventDefault();
            const email = emailIn.value.trim();
            if (!email || !email.includes('@')) {
                authStatus.textContent = 'メールアドレスを入力してください。';
                return;
            }
            authStatus.textContent = '送信中…';
            try {
                await window.pAuth.sendMagicLink(email);
                authStatus.textContent = 'ログインリンクを送信しました。メールを確認してください。';
                emailIn.value = '';
            } catch {
                authStatus.textContent = '送信できませんでした。時間をおいて再試行してください。';
            }
        });

        signoutBtn.addEventListener('click', async () => {
            await window.pAuth.signOut();
            await updateAuthUi();
        });

        document.addEventListener('pauthchange', updateAuthUi);
        if (window.pAuth?.ready) {
            window.pAuth.ready().then(updateAuthUi);
        } else {
            updateAuthUi();
        }

        form.addEventListener('submit', async e => {
            e.preventDefault();
            const [session, user] = await Promise.all([
                window.pAuth?.getSession ? window.pAuth.getSession() : null,
                window.pAuth?.getUser ? window.pAuth.getUser() : null,
            ]);
            if (!session || !user) {
                errEl.textContent = '投稿にはログインが必要です。';
                await updateAuthUi();
                return;
            }
            const body = bodyIn.value.trim();
            if (body.length < MIN_LEN) {
                errEl.textContent = `${MIN_LEN}文字以上入力してください`;
                return;
            }
            const sourceUrl = sourceIn.value.trim();
            if (!validHttpUrl(sourceUrl)) {
                errEl.textContent = '根拠リンクを https:// または http:// から入力してください';
                sourceIn.focus();
                return;
            }
            errEl.textContent = '';
            submitBtn.disabled = true;
            submitBtn.textContent = '投稿中…';
            try {
                await postComment(politicianId, user, session, body, sourceUrl);
                bodyIn.value = '';
                sourceIn.value = '';
                charEl.textContent = `0 / ${MAX_LEN}`;
                errEl.textContent = '投稿しました。確認後に公開されます。';
                await load();
            } catch {
                errEl.textContent = '投稿できませんでした。しばらくして再試行してください。';
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = '承認待ちで投稿する';
            }
        });
    }

    // 旧テンプレートページの自動初期化（body[data-politician-id] + 静的HTML）
    document.addEventListener('DOMContentLoaded', function () {
        const id = document.body.dataset.politicianId;
        if (!id || document.getElementById('politician-record-root')) return;
        const backHome = document.querySelector('.back-home');
        const parentEl = (backHome && backHome.parentElement) || document.querySelector('main') || document.body;
        init(id, parentEl, backHome || null);
    });

    window.pComments = { init };
    document.dispatchEvent(new CustomEvent('pcommentsready'));
}());
