/**
 * 候補者詳細モーダル
 * 使い方: data-election="osaka_2027_governor" data-candidate-id="yoshimura" を持つ要素をクリック
 */

(function () {
    // =========================================
    //  DOM 構築（初回のみ）
    // =========================================
    function createModal() {
        if (document.getElementById('cand-modal-overlay')) return;

        const overlay = document.createElement('div');
        overlay.id = 'cand-modal-overlay';
        overlay.className = 'cand-modal-overlay';
        overlay.innerHTML = `
            <div class="cand-modal-panel" id="cand-modal-panel" role="dialog" aria-modal="true">
                <div class="cand-modal-header">
                    <h2 id="cand-modal-title">候補者詳細</h2>
                    <button class="cand-modal-close" id="cand-modal-close" aria-label="閉じる">
                        <i class="fa-solid fa-xmark"></i>
                    </button>
                </div>
                <div class="cand-modal-body" id="cand-modal-body">
                    <div class="cand-modal-loading">読み込み中...</div>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) closeModal();
        });
        document.getElementById('cand-modal-close').addEventListener('click', closeModal);
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeModal();
        });
    }

    // =========================================
    //  開く / 閉じる
    // =========================================
    function openModal(election, candidateId) {
        createModal();
        const overlay = document.getElementById('cand-modal-overlay');
        const body    = document.getElementById('cand-modal-body');

        body.innerHTML = '<div class="cand-modal-loading">読み込み中...</div>';
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';

        const base = getDataBase();
        fetch(`${base}js/data/${election}/candidates/${candidateId}.json`)
            .then(r => {
                if (!r.ok) throw new Error(`HTTP ${r.status}`);
                return r.json();
            })
            .then(data => renderCandidate(body, data))
            .catch(() => {
                body.innerHTML = '<div class="cand-modal-error">データを取得できませんでした。</div>';
            });
    }

    function closeModal() {
        const overlay = document.getElementById('cand-modal-overlay');
        if (overlay) overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    // =========================================
    //  ベースパス取得
    // =========================================
    function getDataBase() {
        const path = window.location.pathname;
        const dir  = path.replace(/\/[^\/]*$/, '/'); // ファイル名を除いてディレクトリだけ取得
        if (dir.includes('/polimiru/')) {
            const subdir = dir.replace(/^.*\/polimiru\//, '');
            const depth  = subdir.split('/').filter(Boolean).length;
            return '../'.repeat(depth) || './';
        }
        const parts = dir.split('/').filter(Boolean);
        return parts.length === 0 ? './' : '../'.repeat(parts.length);
    }

    // =========================================
    //  党名 → カードヘッダークラス
    // =========================================
    function partyClass(party) {
        if (!party) return '';
        if (party.includes('維新')) return 'party-ishin';
        if (party.includes('自由民主') || party.includes('自民')) return 'party-jimin';
        if (party.includes('公明')) return 'party-komei';
        return 'party-other';
    }

    // =========================================
    //  スコアバー1行
    // =========================================
    function scoreRow(label, value, isOrange) {
        if (value === null || value === undefined) return '';
        const colorClass = isOrange ? 'score-bar-fill-orange' : '';
        return `
            <div class="score-row">
                <span class="score-label">${label}</span>
                <div class="score-bar-wrap">
                    <div class="score-bar-bg">
                        <div class="score-bar-fill ${colorClass}" style="width:${value}%"></div>
                    </div>
                    <span class="score-value-num">${value}</span>
                </div>
            </div>`;
    }

    // =========================================
    //  公約達成度 視覚化
    // =========================================
    function renderProgressChart(progress, promises) {
        if (!progress || !promises || !promises.length) return '';
        const { total, done, started, pending, unknown } = progress;
        if (!total) return '';

        const donePct    = (done    / total * 100).toFixed(1);
        const startedPct = (started / total * 100).toFixed(1);
        const pendingPct = (pending / total * 100).toFixed(1);
        const unknownPct = unknown ? (unknown / total * 100).toFixed(1) : 0;

        // カテゴリ別集計
        const catMap = {};
        for (const p of promises) {
            if (!p.status) continue;
            const cat = p.category || 'その他';
            if (!catMap[cat]) catMap[cat] = { done: 0, started: 0, pending: 0, unknown: 0, total: 0 };
            catMap[cat].total++;
            if      (p.status === '完了')   catMap[cat].done++;
            else if (p.status === '着手')   catMap[cat].started++;
            else if (p.status === '未着手') catMap[cat].pending++;
            else                            catMap[cat].unknown++;
        }

        const catRows = Object.entries(catMap)
            .sort(([,a],[,b]) => b.total - a.total)
            .map(([cat, c]) => {
                const dP = (c.done    / c.total * 100).toFixed(0);
                const sP = (c.started / c.total * 100).toFixed(0);
                const pP = (c.pending / c.total * 100).toFixed(0);
                return `
                    <div class="cat-row">
                        <span class="cat-name">${cat}</span>
                        <div class="cat-bar-wrap">
                            <div class="cat-bar">
                                ${c.done    ? `<div class="bar-done"    style="width:${dP}%"></div>` : ''}
                                ${c.started ? `<div class="bar-started" style="width:${sP}%"></div>` : ''}
                                ${c.pending ? `<div class="bar-pending" style="width:${pP}%"></div>` : ''}
                            </div>
                        </div>
                        <span class="cat-count">${c.total}件</span>
                    </div>`;
            }).join('');

        return `
            <div class="promise-chart">
                <div class="promise-stacked-bar">
                    ${done    ? `<div class="bar-done"    style="width:${donePct}%"    title="完了: ${done}件"></div>` : ''}
                    ${started ? `<div class="bar-started" style="width:${startedPct}%" title="着手: ${started}件"></div>` : ''}
                    ${pending ? `<div class="bar-pending" style="width:${pendingPct}%" title="未着手: ${pending}件"></div>` : ''}
                    ${unknown ? `<div class="bar-unknown" style="width:${unknownPct}%" title="不明: ${unknown}件"></div>` : ''}
                </div>
                <div class="promise-legend">
                    ${done    ? `<span class="legend-item legend-done">完了 ${done}</span>` : ''}
                    ${started ? `<span class="legend-item legend-started">着手 ${started}</span>` : ''}
                    ${pending ? `<span class="legend-item legend-pending">未着手 ${pending}</span>` : ''}
                    ${unknown ? `<span class="legend-item legend-unknown">不明 ${unknown}</span>` : ''}
                    <span class="legend-total">計 ${total}件</span>
                </div>
                ${catRows ? `<div class="cat-breakdown">${catRows}</div>` : ''}
            </div>`;
    }

    // =========================================
    //  公約リスト（折りたたみ）
    // =========================================
    function renderPromiseList(promises) {
        if (!promises || !promises.length) return '';
        const reviewed = promises.filter(p => p.status);
        if (!reviewed.length) return '';

        const groups = {
            '完了':   { color: 'done',    items: [] },
            '着手':   { color: 'started', items: [] },
            '未着手': { color: 'pending', items: [] },
            '不明':   { color: 'unknown', items: [] },
        };
        for (const p of promises) {
            if (p.status && groups[p.status]) groups[p.status].items.push(p);
        }

        const groupHtml = Object.entries(groups)
            .filter(([, g]) => g.items.length)
            .map(([status, g]) => {
                const items = g.items.map(p => `
                    <li class="promise-item promise-item-${g.color}">
                        <span class="promise-level-badge">${p.level === 'main' ? '主' : '詳'}</span>
                        <span class="promise-text">${p.text}</span>
                        ${p.evidence_url ? `<a href="${p.evidence_url}" target="_blank" rel="noopener" class="promise-evidence-link"><i class="fa-solid fa-arrow-up-right-from-square"></i></a>` : ''}
                    </li>`).join('');
                return `
                    <div class="promise-group">
                        <div class="promise-group-header promise-group-${g.color}">
                            <span>${status}</span>
                            <span class="promise-group-count">${g.items.length}件</span>
                        </div>
                        <ul class="promise-list">${items}</ul>
                    </div>`;
            }).join('');

        return `
            <details class="promise-details">
                <summary class="promise-details-summary">
                    <span>公約一覧（${reviewed.length}件）</span>
                    <i class="fa-solid fa-chevron-down promise-chevron"></i>
                </summary>
                <div class="promise-details-body">${groupHtml}</div>
            </details>`;
    }

    // =========================================
    //  スコアカード描画
    // =========================================
    function renderScoreCard(data) {
        const role = data.role;
        const bd   = data.score_breakdown || {};

        if (role === 'incumbent') {
            const inc         = bd.incumbent || {};
            const progressVal = inc.progress    ?? data.progress?.score ?? null;
            const consistency = inc.consistency ?? null;
            const total       = inc.total       ?? data.score_incumbent ?? data.progress?.score ?? null;

            const rows = [
                scoreRow('公約達成率', progressVal),
                scoreRow('発言一貫性', consistency),
            ].filter(Boolean).join('');

            return `
                <div class="score-card">
                    <span class="score-type-label score-type-incumbent">現職評価</span>
                    ${rows || '<p class="score-pending">詳細スコアは現在集計中です</p>'}
                    ${rows ? '<hr class="score-divider">' : ''}
                    <div class="score-total-row">
                        <span class="score-total-label">総合評価</span>
                        <span class="score-total-value">
                            ${total !== null ? `${total}<span>/ 100</span>` : '<span style="font-size:1rem;color:#aaa">集計中</span>'}
                        </span>
                    </div>
                </div>`;
        }

        if (role === 'challenger') {
            const ch          = bd.challenger || {};
            const specificity = ch.specificity ?? null;
            const total       = ch.total       ?? data.score_challenger ?? null;

            return `
                <div class="score-card">
                    <span class="score-type-label score-type-challenger">新人評価</span>
                    ${scoreRow('公約具体性', specificity, true) || '<p class="score-pending">公約情報を収集中です</p>'}
                    <hr class="score-divider">
                    <div class="score-total-row">
                        <span class="score-total-label">総合評価</span>
                        <span class="score-total-value type-challenger">
                            ${total !== null ? `${total}<span>/ 100</span>` : '<span style="font-size:1rem;color:#aaa">集計中</span>'}
                        </span>
                    </div>
                </div>`;
        }

        return `<p class="score-pending">候補者情報確定後にスコアを算出します。</p>`;
    }

    // =========================================
    //  モーダル本文描画
    // =========================================
    function renderCandidate(body, data) {
        const photo = data.image
            ? `<img src="${data.image}" class="cand-profile-photo" alt="${data.name}" onerror="this.style.display='none'">`
            : `<div class="cand-profile-photo-placeholder">👤</div>`;

        const roleBadge = data.role === 'incumbent'
            ? '<span class="cand-tag cand-tag-incumbent">現職</span>'
            : data.role === 'challenger'
                ? '<span class="cand-tag cand-tag-challenger">新人</span>'
                : '';

        const unconfirmed = !data.confirmed
            ? '<span class="cand-tag cand-tag-unconfirmed">出馬未確定</span>'
            : '';

        const pastRoles = (data.past_roles || []).map(r => `
            <li class="past-role-item">
                <span class="past-role-period">${r.period || ''}</span>
                <span class="past-role-title">${r.title}</span>
            </li>`).join('');

        const sourceLinks = (data.source_urls || []).map(s => `
            <a href="${s.url}" class="source-link" target="_blank" rel="noopener">
                <i class="fa-solid fa-arrow-up-right-from-square" style="font-size:0.75em"></i>
                ${s.label}
            </a>`).join('');

        const profileLink = data.profile_url
            ? `<a href="${data.profile_url}" class="source-link" style="color:#fff;border:1px solid rgba(255,255,255,0.3);border-radius:999px;padding:3px 9px;text-decoration:none;background:rgba(255,255,255,0.12)">
                   <i class="fa-solid fa-id-card" style="font-size:0.75em"></i>
                   人物カードを見る
               </a>`
            : '';

        const manifesto = data.manifesto_text
            ? `<div class="manifesto-text">${data.manifesto_text}</div>`
            : `<p class="manifesto-pending">候補者発表後に公約テキストを更新します。</p>`;

        const noteHtml = data.note
            ? `<div class="cand-section">
                   <p style="font-size:0.82rem;color:#888;margin:0">${data.note}</p>
               </div>`
            : '';

        document.getElementById('cand-modal-title').textContent = data.name;

        body.innerHTML = `
            <div class="cand-profile">
                ${photo}
                <div class="cand-profile-info">
                    <p class="cand-profile-name">${data.name}</p>
                    <p class="cand-profile-kana">${data.kana || ''}</p>
                    <div class="cand-profile-meta">
                        ${data.party ? `<span class="cand-tag">${data.party}</span>` : ''}
                        ${data.age   ? `<span class="cand-tag">${data.age}歳</span>` : ''}
                        ${roleBadge}
                        ${unconfirmed}
                    </div>
                    ${profileLink ? `<div class="cand-profile-meta" style="margin-top:10px">${profileLink}</div>` : ''}
                </div>
            </div>

            ${noteHtml}

            <div class="cand-section">
                <p class="cand-section-title">スコア</p>
                ${renderScoreCard(data)}
            </div>

            ${data.promises_2023 && data.promises_2023.some(p => p.status) ? `
            <div class="cand-section">
                <p class="cand-section-title">公約達成度の内訳</p>
                ${renderProgressChart(data.progress, data.promises_2023)}
                <div style="margin-top:12px">
                    ${renderPromiseList(data.promises_2023)}
                </div>
                ${data.progress?.review_note ? `<p style="font-size:0.72rem;color:#bbb;margin:8px 0 0">${data.progress.review_note}</p>` : ''}
            </div>` : ''}

            <div class="cand-section">
                <p class="cand-section-title">公約・マニフェスト</p>
                ${manifesto}
            </div>

            ${pastRoles ? `
            <div class="cand-section">
                <p class="cand-section-title">主な経歴</p>
                <ul class="past-roles-list">${pastRoles}</ul>
            </div>` : ''}

            ${sourceLinks ? `
            <div class="cand-section">
                <p class="cand-section-title">情報源</p>
                <div class="source-links">${sourceLinks}</div>
            </div>` : ''}
        `;
    }

    // =========================================
    //  クリックイベント委譲（選挙ページで使う）
    // =========================================
    window.openCandidateModal = openModal;

    document.addEventListener('click', (e) => {
        const card = e.target.closest('[data-candidate-id]');
        if (!card) return;
        const election = card.dataset.election;
        const id       = card.dataset.candidateId;
        if (election && id) openModal(election, id);
    });
})();
