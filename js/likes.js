(function () {
    const STORAGE_KEY = 'polimiru_bookmarks_v1';

    let _cache = null;

    function getMap() {
        if (_cache) return _cache;
        try { _cache = JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}; }
        catch { _cache = {}; }
        return _cache;
    }

    function isBookmarked(id) { return !!getMap()[id]; }

    function toggle(id) {
        const map = getMap();
        const next = !map[id];
        if (next) map[id] = true; else delete map[id];
        localStorage.setItem(STORAGE_KEY, JSON.stringify(map));
        return next;
    }

    function getBookmarkedIds() {
        return Object.keys(getMap());
    }

    function insertButton(id, afterEl) {
        if (!afterEl || document.getElementById('pol-bookmark-btn-' + id)) return;
        const saved = isBookmarked(id);

        const btn = document.createElement('button');
        btn.id        = 'pol-bookmark-btn-' + id;
        btn.className = 'pol-bookmark-btn' + (saved ? ' bookmarked' : '');
        btn.type      = 'button';
        btn.setAttribute('aria-label', saved ? '保存済み' : '保存する');
        btn.innerHTML = `
            <i class="fa-${saved ? 'solid' : 'regular'} fa-bookmark"></i>
            <span class="pol-bookmark-label">${saved ? '保存済み' : '保存する'}</span>`;

        btn.addEventListener('click', function () {
            const nowSaved = toggle(id);
            btn.classList.toggle('bookmarked', nowSaved);
            btn.querySelector('i').className = `fa-${nowSaved ? 'solid' : 'regular'} fa-bookmark`;
            btn.querySelector('.pol-bookmark-label').textContent = nowSaved ? '保存済み' : '保存する';
            btn.setAttribute('aria-label', nowSaved ? '保存済み' : '保存する');
        });

        afterEl.insertAdjacentElement('afterend', btn);
    }

    // 後方互換：旧テンプレートページ（politician-record-rootなし）への自動挿入
    document.addEventListener('DOMContentLoaded', function () {
        const id = document.body.dataset.politicianId;
        if (!id || document.getElementById('politician-record-root')) return;
        const el = document.querySelector('.primary-sources');
        if (el) insertButton(id, el);
    });

    window.pBookmarks = { isBookmarked, toggle, getBookmarkedIds, insertButton };
    // pLikes は削除済み — 旧コードが参照している場合はpBookmarksを使ってください
    document.dispatchEvent(new CustomEvent('plikesready'));
}());
