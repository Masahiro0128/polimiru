(function () {
    const POL_KEY  = 'polimiru_bookmarks_v1';
    const ELEC_KEY = 'polimiru_election_bookmarks_v1';

    let _polCache  = null;
    let _elecCache = null;

    function getMap(type) {
        if (type === 'election') {
            if (_elecCache) return _elecCache;
            try { _elecCache = JSON.parse(localStorage.getItem(ELEC_KEY)) || {}; }
            catch { _elecCache = {}; }
            return _elecCache;
        }
        if (_polCache) return _polCache;
        try { _polCache = JSON.parse(localStorage.getItem(POL_KEY)) || {}; }
        catch { _polCache = {}; }
        return _polCache;
    }

    function saveMap(type, map) {
        localStorage.setItem(type === 'election' ? ELEC_KEY : POL_KEY, JSON.stringify(map));
    }

    function isBookmarked(id, type) {
        return !!getMap(type || 'politician')[id];
    }

    function toggle(id, type) {
        type = type || 'politician';
        const map  = getMap(type);
        const next = !map[id];
        if (next) map[id] = true; else delete map[id];
        saveMap(type, map);
        logEvent(id, type, next ? 'add' : 'remove');
        return next;
    }

    function logEvent(entityId, entityType, action) {
        var url = window.SUPABASE_URL;
        var key = window.SUPABASE_ANON_KEY;
        if (!url || !key) return;
        fetch(url + '/rest/v1/bookmark_events', {
            method: 'POST',
            headers: {
                'apikey': key,
                'Authorization': 'Bearer ' + key,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ entity_id: entityId, entity_type: entityType, action: action }),
        }).catch(function () {});
    }

    function getBookmarkedIds(type) {
        return Object.keys(getMap(type || 'politician'));
    }

    function insertButton(id, afterEl) {
        if (!afterEl || document.getElementById('pol-bookmark-btn-' + id)) return;
        var saved = isBookmarked(id, 'politician');

        var btn = document.createElement('button');
        btn.id        = 'pol-bookmark-btn-' + id;
        btn.className = 'pol-bookmark-btn' + (saved ? ' bookmarked' : '');
        btn.type      = 'button';
        btn.setAttribute('aria-label', saved ? '保存済み' : '保存する');
        btn.innerHTML =
            '<i class="fa-' + (saved ? 'solid' : 'regular') + ' fa-bookmark"></i>' +
            '<span class="pol-bookmark-label">' + (saved ? '保存済み' : '保存する') + '</span>';

        btn.addEventListener('click', function () {
            var nowSaved = toggle(id, 'politician');
            btn.classList.toggle('bookmarked', nowSaved);
            btn.querySelector('i').className = 'fa-' + (nowSaved ? 'solid' : 'regular') + ' fa-bookmark';
            btn.querySelector('.pol-bookmark-label').textContent = nowSaved ? '保存済み' : '保存する';
            btn.setAttribute('aria-label', nowSaved ? '保存済み' : '保存する');
        });

        afterEl.insertAdjacentElement('afterend', btn);
    }

    function insertElectionButton(id, afterEl) {
        var btnId = 'elec-bookmark-btn-' + id;
        if (!afterEl || document.getElementById(btnId)) return;
        var saved = isBookmarked(String(id), 'election');

        var btn = document.createElement('button');
        btn.id        = btnId;
        btn.className = 'pol-bookmark-btn' + (saved ? ' bookmarked' : '');
        btn.type      = 'button';
        btn.setAttribute('aria-label', saved ? '保存済み' : 'この選挙を保存');
        btn.innerHTML =
            '<i class="fa-' + (saved ? 'solid' : 'regular') + ' fa-bookmark"></i>' +
            '<span class="pol-bookmark-label">' + (saved ? '保存済み' : 'この選挙を保存') + '</span>';

        btn.addEventListener('click', function () {
            var nowSaved = toggle(String(id), 'election');
            btn.classList.toggle('bookmarked', nowSaved);
            btn.querySelector('i').className = 'fa-' + (nowSaved ? 'solid' : 'regular') + ' fa-bookmark';
            btn.querySelector('.pol-bookmark-label').textContent = nowSaved ? '保存済み' : 'この選挙を保存';
            btn.setAttribute('aria-label', nowSaved ? '保存済み' : 'この選挙を保存');
        });

        afterEl.insertAdjacentElement('afterend', btn);
    }

    // 後方互換：旧テンプレートページ（politician-record-rootなし）への自動挿入
    document.addEventListener('DOMContentLoaded', function () {
        var id = document.body.dataset.politicianId;
        if (!id || document.getElementById('politician-record-root')) return;
        var el = document.querySelector('.primary-sources');
        if (el) insertButton(id, el);
    });

    // 選挙ページへの自動挿入
    document.addEventListener('DOMContentLoaded', function () {
        var elecId = document.body.dataset.electionId;
        if (!elecId) return;
        var meta = document.querySelector('.election-hero-meta');
        if (meta) insertElectionButton(elecId, meta);
    });

    window.pBookmarks = { isBookmarked, toggle, getBookmarkedIds, insertButton, insertElectionButton };
    // pLikes は削除済み — 旧コードが参照している場合はpBookmarksを使ってください
    document.dispatchEvent(new CustomEvent('plikesready'));
}());
