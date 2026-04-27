(function () {
    const MIN_LEN = 5;
    const MAX_LEN = 500;

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

    function apiHeaders() {
        return {
            apikey: window.SUPABASE_ANON_KEY,
            Authorization: `Bearer ${window.SUPABASE_ANON_KEY}`,
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
            `?politician_id=eq.${encodeURIComponent(politicianId)}&order=created_at.desc&limit=100`,
            { headers: apiHeaders() }
        );
        if (!res.ok) throw new Error(res.status);
        return res.json();
    }

    async function postComment(politicianId, nickname, body, sourceUrl) {
        const res = await fetch(`${window.SUPABASE_URL}/rest/v1/comments`, {
            method: 'POST',
            headers: { ...apiHeaders(), 'Content-Type': 'application/json', Prefer: 'return=representation' },
            body: JSON.stringify({
                politician_id: politicianId,
                nickname: nickname.trim() || '匿名',
                body: body.trim(),
                source_url: sourceUrl.trim(),
            }),
        });
        if (!res.ok) throw new Error(res.status);
        return res.json();
    }

    function renderList(comments, listEl, countEl) {
        countEl.textContent = `${comments.length}件`;
        if (comments.length === 0) {
            listEl.innerHTML = '<p class="cb-empty">まだ発言がありません。最初に発言してみましょう。</p>';
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
                <h2 class="cb-title">あの時ああ言ってたぞ欄</h2>
                <span class="cb-count" id="cb-count-${politicianId}">読み込み中…</span>
            </div>
            <form class="cb-form" id="cb-form-${politicianId}" novalidate>
                <p class="cb-guidance">
                    発言・公約・実績の根拠リンクを添えて記録してください。確認できない噂や個人攻撃は載せないでください。
                </p>
                <div class="cb-form-row">
                    <input class="cb-nick-input" type="text" placeholder="名前（省略可）" maxlength="30" autocomplete="off">
                    <button class="cb-submit" type="submit">投稿する</button>
                </div>
                <input class="cb-source-input" type="url" placeholder="根拠リンク（必須）https://..." autocomplete="off" required>
                <textarea class="cb-body-input" placeholder="いつ・どこで・何を言っていたか（${MIN_LEN}〜${MAX_LEN}文字）"
                          maxlength="${MAX_LEN}" rows="3"></textarea>
                <div class="cb-form-footer">
                    <span class="cb-char">0 / ${MAX_LEN}</span>
                    <span class="cb-error" id="cb-err-${politicianId}"></span>
                </div>
            </form>
            <div class="cb-list" id="cb-list-${politicianId}">
                <p class="cb-empty">読み込み中…</p>
            </div>`;

        if (insertBeforeEl) parentEl.insertBefore(section, insertBeforeEl);
        else parentEl.appendChild(section);

        const listEl  = section.querySelector('.cb-list');
        const countEl = section.querySelector('.cb-count');
        const errEl   = section.querySelector('.cb-error');
        const form    = section.querySelector('.cb-form');
        const nickIn  = section.querySelector('.cb-nick-input');
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

        form.addEventListener('submit', async e => {
            e.preventDefault();
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
                await postComment(politicianId, nickIn.value, body, sourceUrl);
                bodyIn.value = '';
                sourceIn.value = '';
                charEl.textContent = `0 / ${MAX_LEN}`;
                await load();
            } catch {
                errEl.textContent = '投稿できませんでした。しばらくして再試行してください。';
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = '投稿する';
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
