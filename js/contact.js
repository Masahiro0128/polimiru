(function () {
    const MIN_MESSAGE_LEN = 10;
    const MAX_MESSAGE_LEN = 2000;

    function setStatus(el, message, type) {
        el.textContent = message;
        el.classList.toggle('is-error', type === 'error');
        el.classList.toggle('is-success', type === 'success');
    }

    function getValue(form, name) {
        const field = form.elements[name];
        return field ? field.value.trim() : '';
    }

    function validUrl(value) {
        if (!value) return true;
        try {
            const url = new URL(value);
            return url.protocol === 'http:' || url.protocol === 'https:';
        } catch {
            return false;
        }
    }

    async function submitContact(payload) {
        const res = await fetch(`${window.SUPABASE_URL}/functions/v1/contact-submit`, {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${window.SUPABASE_ANON_KEY}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });
        if (!res.ok) throw new Error(String(res.status));
    }

    document.addEventListener('DOMContentLoaded', function () {
        const form = document.getElementById('contact-form');
        if (!form) return;

        const status = document.getElementById('contact-status');
        const submit = document.getElementById('contact-submit');
        const message = document.getElementById('contact-message');
        const counter = document.getElementById('contact-char-count');

        message.addEventListener('input', function () {
            counter.textContent = `${message.value.length} / ${MAX_MESSAGE_LEN}`;
        });

        form.addEventListener('submit', async function (event) {
            event.preventDefault();

            if (getValue(form, 'company')) return;

            const payload = {
                category: getValue(form, 'category'),
                name: getValue(form, 'name') || null,
                email: getValue(form, 'email') || null,
                page_url: getValue(form, 'page_url') || null,
                subject: getValue(form, 'subject'),
                message: getValue(form, 'message'),
                source_url: getValue(form, 'source_url') || null,
                user_agent: navigator.userAgent,
            };

            if (!payload.category) {
                setStatus(status, '種別を選択してください。', 'error');
                return;
            }
            if (!payload.subject) {
                setStatus(status, '件名を入力してください。', 'error');
                return;
            }
            if (payload.message.length < MIN_MESSAGE_LEN) {
                setStatus(status, `${MIN_MESSAGE_LEN}文字以上で内容を入力してください。`, 'error');
                return;
            }
            if (!form.elements.confirm.checked) {
                setStatus(status, '送信前の確認にチェックしてください。', 'error');
                return;
            }
            if (!validUrl(payload.page_url) || !validUrl(payload.source_url)) {
                setStatus(status, 'URLは http または https で始まる形式にしてください。', 'error');
                return;
            }
            if (!window.SUPABASE_URL || !window.SUPABASE_ANON_KEY) {
                setStatus(status, '送信設定が未完了です。', 'error');
                return;
            }

            submit.disabled = true;
            submit.querySelector('span').textContent = '送信中';
            setStatus(status, '', '');

            try {
                await submitContact(payload);
                form.reset();
                counter.textContent = `0 / ${MAX_MESSAGE_LEN}`;
                setStatus(status, '送信しました。内容を確認します。', 'success');
            } catch {
                setStatus(status, '送信できませんでした。時間をおいて再度お試しください。', 'error');
            } finally {
                submit.disabled = false;
                submit.querySelector('span').textContent = '送信する';
            }
        });
    });
}());
