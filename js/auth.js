(function () {
    const SESSION_KEY = 'polimiru_auth_session_v1';
    const EXPIRY_MARGIN_MS = 60 * 1000;

    let cachedSession = null;
    let cachedUser = null;
    let readyPromise = null;

    function authUrl(path) {
        return `${window.SUPABASE_URL}/auth/v1/${path}`;
    }

    function authHeaders(accessToken) {
        const headers = {
            apikey: window.SUPABASE_ANON_KEY,
            'Content-Type': 'application/json',
        };
        if (accessToken) headers.Authorization = `Bearer ${accessToken}`;
        return headers;
    }

    function loadStoredSession() {
        if (cachedSession) return cachedSession;
        try {
            cachedSession = JSON.parse(localStorage.getItem(SESSION_KEY)) || null;
        } catch {
            cachedSession = null;
        }
        return cachedSession;
    }

    function saveSession(session) {
        cachedSession = session || null;
        cachedUser = null;
        if (cachedSession) localStorage.setItem(SESSION_KEY, JSON.stringify(cachedSession));
        else localStorage.removeItem(SESSION_KEY);
        document.dispatchEvent(new CustomEvent('pauthchange', { detail: { session: cachedSession } }));
    }

    function parseHashSession() {
        if (!location.hash || !location.hash.includes('access_token=')) return false;
        const params = new URLSearchParams(location.hash.slice(1));
        const accessToken = params.get('access_token');
        const refreshToken = params.get('refresh_token');
        const expiresIn = Number(params.get('expires_in') || 3600);
        if (!accessToken || !refreshToken) return false;

        saveSession({
            access_token: accessToken,
            refresh_token: refreshToken,
            expires_at: Date.now() + expiresIn * 1000,
            token_type: params.get('token_type') || 'bearer',
        });
        history.replaceState(null, document.title, location.pathname + location.search);
        return true;
    }

    async function refreshSession(session) {
        if (!session?.refresh_token) return null;
        const res = await fetch(authUrl('token?grant_type=refresh_token'), {
            method: 'POST',
            headers: authHeaders(),
            body: JSON.stringify({ refresh_token: session.refresh_token }),
        });
        if (!res.ok) {
            saveSession(null);
            return null;
        }
        const data = await res.json();
        const next = {
            access_token: data.access_token,
            refresh_token: data.refresh_token || session.refresh_token,
            expires_at: Date.now() + Number(data.expires_in || 3600) * 1000,
            token_type: data.token_type || 'bearer',
        };
        saveSession(next);
        return next;
    }

    async function getSession() {
        parseHashSession();
        const session = loadStoredSession();
        if (!session?.access_token) return null;
        if (session.expires_at && session.expires_at - Date.now() < EXPIRY_MARGIN_MS) {
            return refreshSession(session);
        }
        return session;
    }

    async function getUser() {
        const session = await getSession();
        if (!session) return null;
        if (cachedUser) return cachedUser;
        const res = await fetch(authUrl('user'), {
            headers: authHeaders(session.access_token),
        });
        if (!res.ok) {
            saveSession(null);
            return null;
        }
        cachedUser = await res.json();
        return cachedUser;
    }

    function displayName(user) {
        const meta = user?.user_metadata || {};
        return meta.full_name || meta.name || user?.email || 'ログイン中';
    }

    function signInWithOAuth(provider) {
        const redirectTo = location.origin + location.pathname + location.search;
        const params = new URLSearchParams({
            provider,
            redirect_to: redirectTo,
        });
        location.href = authUrl(`authorize?${params.toString()}`);
    }

    async function sendMagicLink(email) {
        const redirectTo = location.origin + location.pathname + location.search;
        const res = await fetch(authUrl('otp'), {
            method: 'POST',
            headers: authHeaders(),
            body: JSON.stringify({
                email,
                type: 'magiclink',
                options: { email_redirect_to: redirectTo },
            }),
        });
        if (!res.ok) throw new Error(String(res.status));
    }

    async function signOut() {
        const session = await getSession();
        if (session?.access_token) {
            await fetch(authUrl('logout'), {
                method: 'POST',
                headers: authHeaders(session.access_token),
            }).catch(() => {});
        }
        saveSession(null);
    }

    function ready() {
        if (!readyPromise) readyPromise = getUser().catch(() => null);
        return readyPromise;
    }

    window.pAuth = {
        ready,
        getSession,
        getUser,
        displayName,
        signInWithOAuth,
        sendMagicLink,
        signOut,
    };

    document.dispatchEvent(new CustomEvent('pauthready'));
}());
