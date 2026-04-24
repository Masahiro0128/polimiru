(function () {
    const STORAGE_KEY = 'polimiru_likes_v1';

    // Cached in memory; mutated in place by toggleLike — no need to invalidate.
    let _cache = null;

    function getLikedMap() {
        if (_cache) return _cache;
        try { _cache = JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}; }
        catch { _cache = {}; }
        return _cache;
    }

    function isLiked(id) { return !!getLikedMap()[id]; }

    function toggleLike(id) {
        const map = getLikedMap();
        const next = !map[id];
        if (next) map[id] = true; else delete map[id];
        localStorage.setItem(STORAGE_KEY, JSON.stringify(map));
        return next;
    }

    function getTotalLikes(politician) {
        return (politician.baseLikes || 0) + (isLiked(politician.id) ? 1 : 0);
    }

    function formatLikes(n) {
        n = Number(n) || 0;
        if (n >= 10000) return (n / 10000).toFixed(1).replace('.0', '') + '万';
        if (n >= 1000)  return (n / 1000).toFixed(1).replace('.0', '') + 'k';
        return String(n);
    }

    function insertButton(id, afterEl) {
        if (!afterEl || document.getElementById('pol-like-btn-' + id)) return;
        const map   = getLikedMap();
        const liked = !!map[id];
        const pol   = (window.politicians || []).find(p => p.id === id);
        const total = pol ? getTotalLikes(pol) : (liked ? 1 : 0);

        const btn = document.createElement('button');
        btn.id        = 'pol-like-btn-' + id;
        btn.className = 'pol-like-btn' + (liked ? ' liked' : '');
        btn.type      = 'button';
        btn.setAttribute('aria-label', 'いいね');
        btn.innerHTML = `
            <i class="fa-${liked ? 'solid' : 'regular'} fa-heart"></i>
            <span class="pol-like-count">${formatLikes(total)}</span>
            <span class="pol-like-label">注目</span>`;

        btn.addEventListener('click', function () {
            const nowLiked = toggleLike(id);
            const p = (window.politicians || []).find(p => p.id === id);
            const newTotal = p ? getTotalLikes(p) : (nowLiked ? 1 : 0);
            btn.classList.toggle('liked', nowLiked);
            btn.querySelector('i').className = `fa-${nowLiked ? 'solid' : 'regular'} fa-heart`;
            btn.querySelector('.pol-like-count').textContent = formatLikes(newTotal);
        });

        afterEl.insertAdjacentElement('afterend', btn);
    }

    // Auto-init on old-template pages that set body[data-politician-id] manually
    // and render their hero HTML statically (no #politician-record-root).
    document.addEventListener('DOMContentLoaded', function () {
        const id = document.body.dataset.politicianId;
        if (!id || document.getElementById('politician-record-root')) return;
        const el = document.querySelector('.primary-sources');
        if (el) insertButton(id, el);
    });

    window.pLikes = { isLiked, toggleLike, getTotalLikes, formatLikes, insertButton };
    document.dispatchEvent(new CustomEvent('plikesready'));
}());
