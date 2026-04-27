(function () {
    const allowedTags = new Set(['A', 'STRONG']);
    const allowedAttrs = new Set(['href', 'target', 'rel']);

    function sanitizeHtml(html) {
        const template = document.createElement('template');
        template.innerHTML = String(html || '');
        template.content.querySelectorAll('*').forEach(el => {
            if (!allowedTags.has(el.tagName)) {
                el.replaceWith(...el.childNodes);
                return;
            }
            [...el.attributes].forEach(attr => {
                if (!allowedAttrs.has(attr.name)) el.removeAttribute(attr.name);
            });
            if (el.tagName === 'A') {
                const href = el.getAttribute('href') || '';
                if (!/^https?:\/\//.test(href)) el.removeAttribute('href');
                el.setAttribute('target', '_blank');
                el.setAttribute('rel', 'noopener');
            }
        });
        return template.innerHTML;
    }

    function renderItem(item) {
        const badge = item.badge || 'update';
        return `
            <div class="news-item">
                <span class="news-date">${item.date || ''}</span>
                <span class="news-badge news-badge--${badge}">${item.category || '更新'}</span>
                <span class="news-text">${sanitizeHtml(item.text)}</span>
            </div>`;
    }

    async function loadNews() {
        const base = window.POLIMIRU_BASE_PATH || './';
        const res = await fetch(`${base}js/data/news.json`, { cache: 'no-store' });
        if (!res.ok) throw new Error(String(res.status));
        return res.json();
    }

    document.addEventListener('DOMContentLoaded', async function () {
        const root = document.querySelector('[data-news-list]');
        if (!root) return;
        const limit = Number(root.dataset.newsLimit || 0);
        try {
            const news = await loadNews();
            const items = limit > 0 ? news.slice(0, limit) : news;
            root.innerHTML = items.map(renderItem).join('');
        } catch {
            root.innerHTML = '<div class="news-item"><span class="news-text">お知らせを読み込めませんでした。</span></div>';
        }
    });
}());
