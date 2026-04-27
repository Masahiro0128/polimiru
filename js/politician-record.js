(function () {
    const root = document.getElementById('politician-record-root');
    const id = document.body.dataset.politicianId;

    const escapeHtml = value => String(value || '').replace(/[&<>"']/g, char => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    })[char]);

    const linkIcon = '<i class="fa-solid fa-arrow-up-right-from-square"></i>';

    function initials(name) {
        return String(name || '?').replace(/\s+/g, '').slice(0, 1) || '?';
    }

    function assetUrl(value) {
        const url = String(value || '');
        if (!url) return '';
        if (/^(https?:|data:|\/)/.test(url)) return url;
        return `../../${url.replace(/^\.?\//, '')}`;
    }

    function renderSourceButtons(sources) {
        return (sources || []).slice(0, 3).map(source => `
            <a class="source-btn" href="${escapeHtml(source.url)}" target="_blank" rel="noopener">
                ${linkIcon}${escapeHtml(source.label)}
            </a>
        `).join('');
    }

    function renderCareerItem(item) {
        return `
            <li class="career-row">
                <span class="career-period">${escapeHtml(item.period)}</span>
                <span class="career-text">${escapeHtml(item.text || item.role || item.title)}</span>
            </li>
        `;
    }

    function renderElectionLinks(links) {
        if (!links || !links.length) return '';
        return `
            <section>
                <div class="section-label">
                    <h2>選挙との紐づき</h2>
                    <span>election history</span>
                </div>
                <div class="focus-grid">
                    ${links.map(link => `
                        <article class="focus-card">
                            <div class="focus-context">${escapeHtml(link.role || '選挙')}</div>
                            <h3 class="focus-title">${escapeHtml(link.title)}</h3>
                            <p class="focus-desc">${escapeHtml(link.result || '')}</p>
                        </article>
                    `).join('')}
                </div>
            </section>
        `;
    }

    function statusLabel(status) {
        const labels = {
            achieved: '実現', done: '実現', '実施': '実現', '完了': '実現', '実現': '実現',
            started: '進行中', partial: '進行中', tracking: '進行中',
            '追跡中': '進行中', '進行': '進行中', '進行中': '進行中',
            '法案提出': '進行中', '法案準備': '進行中', '担当': '進行中',
            '論点化': '進行中', '公約化': '進行中', '着手': '進行中',
            '継続': '進行中', '見直し': '進行中', '要検証': '進行中', '実施中': '進行中',
            pending: '公約', '公約': '公約',
            reversed: '撤回', '後退': '撤回', '撤回': '撤回',
            historical_review: '確認済', initial_review: '初期確認', unknown: '確認中',
        };
        return labels[status] || status || '確認中';
    }

    function statusClass(status) {
        const achieved = ['achieved', 'done', '実施', '完了', '実現', 'historical_review', '確認済'];
        const inprogress = ['started', 'partial', 'tracking', '追跡中', '進行', '進行中',
            '法案提出', '法案準備', '担当', '論点化', '公約化', '着手', '継続', '見直し', '要検証', '実施中'];
        const reversed = ['reversed', '後退', '撤回'];
        if (achieved.some(k => status === k || statusLabel(status) === '実現')) return 'status-achieved';
        if (reversed.some(k => status === k)) return 'status-reversed';
        if (inprogress.some(k => status === k || statusLabel(status) === '進行中')) return 'status-started';
        return 'status-pending';
    }

    function renderPromiseCycles(cycles) {
        if (!cycles || !cycles.length) return '';
        return `
            <section>
                <div class="section-label">
                    <h2>公約・実績の追跡</h2>
                    <span>promise tracking</span>
                </div>
                <div class="cycle-grid">
                    ${cycles.map(cycle => {
                        const highlights = cycle.highlights || [];
                        const total = Number(cycle.total || 0);
                        const safeTotal = total || 1;
                        const done = Number(cycle.done || 0);
                        const started = Number(cycle.started || 0);
                        const pending = Number(cycle.pending || 0);
                        const score = cycle.score ?? '-';
                        const reviewedAt = cycle.reviewed_at
                            ? String(cycle.reviewed_at).slice(0, 10).replaceAll('-', '.')
                            : '';
                        return `
                        <article class="cycle-card">
                            <div class="cycle-head">
                                <div>
                                    <div class="focus-context">${escapeHtml(cycle.context || cycle.source || '')}</div>
                                    <h3 class="focus-title">${escapeHtml(cycle.title)}</h3>
                                </div>
                                <span class="cycle-progress-chip">公約進捗</span>
                            </div>
                            <div class="cycle-progress-summary">
                                <div>
                                    <span class="cycle-progress-label">進捗スコア</span>
                                    <span class="cycle-progress-note">${reviewedAt ? `確認 ${escapeHtml(reviewedAt)}` : '出典確認中'}</span>
                                </div>
                                <span class="cycle-score">${escapeHtml(score)}<small>/100</small></span>
                            </div>
                            <div class="cycle-meter">
                                <span class="done" style="width:${done / safeTotal * 100}%"></span>
                                <span class="started" style="width:${started / safeTotal * 100}%"></span>
                                <span class="pending" style="width:${pending / safeTotal * 100}%"></span>
                            </div>
                            <div class="cycle-counts">
                                <span class="cycle-count done"><b>${escapeHtml(done)}</b>実現</span>
                                <span class="cycle-count started"><b>${escapeHtml(started)}</b>進行中</span>
                                <span class="cycle-count pending"><b>${escapeHtml(pending)}</b>公約</span>
                                <span class="cycle-count total"><b>${escapeHtml(total)}</b>合計</span>
                            </div>
                            <div class="cycle-score-foot">
                                <a class="score-method-link" href="/#score-guide" target="_blank" rel="noopener">採点基準 <i class="fa-solid fa-arrow-up-right-from-square" style="font-size:0.6em"></i></a>
                            </div>
                            ${highlights.length > 0 ? `
                                <details class="cycle-details">
                                    <summary class="cycle-details-summary">
                                        <i class="fa-solid fa-chevron-right cycle-details-icon"></i>
                                        公約の内訳を見る
                                        <span class="cycle-details-count">${highlights.length}件</span>
                                    </summary>
                                    <div class="cycle-details-body">
                                        ${highlights.map(item => `
                                            <a class="cycle-highlight" href="${escapeHtml(item.evidence_url || cycle.source_url || '#')}" target="_blank" rel="noopener">
                                                <span class="cycle-status ${statusClass(item.status)}">${escapeHtml(statusLabel(item.status))}</span>
                                                <span class="cycle-highlight-title">${escapeHtml(item.title)}</span>
                                                <i class="fa-solid fa-arrow-up-right-from-square cycle-highlight-icon"></i>
                                            </a>
                                        `).join('')}
                                    </div>
                                </details>
                            ` : ''}
                        </article>
                        `;
                    }).join('')}
                </div>
            </section>
        `;
    }

    function render(data) {
        const accent = data.accent || {};
        root.style.setProperty('--party-from', accent.from || '#1e3a6e');
        root.style.setProperty('--party-to', accent.to || '#0f1f3d');
        root.style.setProperty('--party-accent', accent.color || '#1e3a6e');
        document.title = `${data.name} - polimiru`;

        const photoSrc = assetUrl(data.photo_url);
        const photo = photoSrc
            ? `<img class="record-photo" src="${escapeHtml(photoSrc)}" alt="${escapeHtml(data.name)}">`
            : `<div class="record-photo-placeholder">${escapeHtml(initials(data.name))}</div>`;

        root.innerHTML = `
            <section class="record-hero">
                <div class="record-hero-inner">
                    ${photo}
                    <div>
                        <div class="record-kicker">${escapeHtml(data.party)} / ${escapeHtml(data.party_role || data.current_status)}</div>
                        <h1 class="record-name">${escapeHtml(data.name)}</h1>
                        <p class="record-lead">${escapeHtml(data.summary)}</p>
                        <div class="record-meta">
                            <span class="record-tag primary">${escapeHtml(data.current_status)}</span>
                            <span class="record-tag">${escapeHtml(data.area)}</span>
                            <span class="record-tag">${escapeHtml(data.kana)}</span>
                        </div>
                        <div class="source-buttons">${renderSourceButtons(data.source_urls)}</div>
                    </div>
                </div>
            </section>

            <section class="dashboard-grid">
                <div class="panel">
                    <h2 class="panel-title">基本情報 <small>official profile</small></h2>
                    <div class="stat-grid">
                        ${(data.stats || []).map(stat => `
                            <div class="stat-tile">
                                <span class="stat-label">${escapeHtml(stat.label)}</span>
                                <span class="stat-value">${escapeHtml(stat.value)}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
                <div class="panel">
                    <h2 class="panel-title">履歴 <small>career</small></h2>
                    <ol class="career-list">
                        ${(data.career || []).map(renderCareerItem).join('')}
                    </ol>
                </div>
            </section>

            ${renderElectionLinks(data.election_links)}

            ${renderPromiseCycles(data.promise_cycles)}

            <section>
                <div class="section-label">
                    <h2>現在見るべき論点</h2>
                    <span>party role and policy lens</span>
                </div>
                <div class="focus-grid">
                    ${(data.focus_cards || []).map(card => `
                        <article class="focus-card">
                            <div class="focus-context">${escapeHtml(card.context)}</div>
                            <h3 class="focus-title">${escapeHtml(card.title)}</h3>
                            <p class="focus-desc">${escapeHtml(card.desc)}</p>
                        </article>
                    `).join('')}
                </div>
            </section>

            <section>
                <div class="section-label">
                    <h2>参照元</h2>
                    <span>primary sources</span>
                </div>
                <div class="source-list">
                    ${(data.source_urls || []).map(source => `
                        <a class="source-link" href="${escapeHtml(source.url)}" target="_blank" rel="noopener">
                            ${linkIcon}${escapeHtml(source.label)}
                        </a>
                    `).join('')}
                </div>
            </section>

            <div class="back-home"><a href="../../index.html">トップへ戻る</a></div>
        `;

        const sourceButtons = root.querySelector('.source-buttons');
        if (sourceButtons) {
            if (window.pBookmarks) {
                window.pBookmarks.insertButton(id, sourceButtons);
            } else {
                document.addEventListener('plikesready', function () {
                    window.pBookmarks.insertButton(id, root.querySelector('.source-buttons'));
                }, { once: true });
            }
        }

        const backHome = root.querySelector('.back-home');
        if (window.pComments) {
            window.pComments.init(id, root, backHome);
        } else {
            document.addEventListener('pcommentsready', function () {
                window.pComments.init(id, root, root.querySelector('.back-home'));
            }, { once: true });
        }
    }

    if (!root || !id) return;

    fetch(`../../data/politicians/${id}.json`)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.json();
        })
        .then(render)
        .catch(error => {
            root.innerHTML = `<div class="panel">人物データを読み込めませんでした。${escapeHtml(error.message)}</div>`;
        });
}());
