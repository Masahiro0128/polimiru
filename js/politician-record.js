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
                        <div class="record-kicker">${escapeHtml(data.party)} / ${escapeHtml(data.party_role)}</div>
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
                        ${(data.career || []).map(item => `
                            <li class="career-row">
                                <span class="career-period">${escapeHtml(item.period)}</span>
                                <span class="career-text">${escapeHtml(item.text)}</span>
                            </li>
                        `).join('')}
                    </ol>
                </div>
            </section>

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
