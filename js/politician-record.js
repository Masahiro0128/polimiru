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
            achieved: '完了',
            started: '着手',
            partial: '一部実現',
            pending: '未着手',
            unknown: '不明',
            initial_review: '初期レビュー'
        };
        return labels[status] || status || '確認中';
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
                    ${cycles.map(cycle => `
                        <article class="cycle-card">
                            <div class="cycle-head">
                                <div>
                                    <div class="focus-context">${escapeHtml(cycle.context || cycle.source || '')}</div>
                                    <h3 class="focus-title">${escapeHtml(cycle.title)}</h3>
                                </div>
                                <span class="cycle-score">${escapeHtml(cycle.score ?? '-')}<small>/100</small></span>
                            </div>
                            <div class="cycle-meter">
                                <span class="done" style="width:${Number(cycle.done || 0) / Number(cycle.total || 1) * 100}%"></span>
                                <span class="started" style="width:${Number(cycle.started || 0) / Number(cycle.total || 1) * 100}%"></span>
                                <span class="pending" style="width:${Number(cycle.pending || 0) / Number(cycle.total || 1) * 100}%"></span>
                            </div>
                            <div class="cycle-legend">
                                <span>完了 ${escapeHtml(cycle.done || 0)}</span>
                                <span>着手 ${escapeHtml(cycle.started || 0)}</span>
                                <span>未着手 ${escapeHtml(cycle.pending || 0)}</span>
                                <span>計 ${escapeHtml(cycle.total || 0)}</span>
                            </div>
                            ${(cycle.highlights || []).slice(0, 4).map(item => `
                                <a class="cycle-highlight" href="${escapeHtml(item.evidence_url || cycle.source_url || '#')}" target="_blank" rel="noopener">
                                    <span class="cycle-status">${escapeHtml(statusLabel(item.status))}</span>
                                    <span>${escapeHtml(item.title)}</span>
                                </a>
                            `).join('')}
                        </article>
                    `).join('')}
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

        const photo = data.photo_url
            ? `<img class="record-photo" src="${escapeHtml(data.photo_url)}" alt="${escapeHtml(data.name)}">`
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
