type ContactCategory = 'factcheck' | 'candidate_info' | 'bug' | 'research' | 'other';

type ContactPayload = {
  category?: ContactCategory;
  name?: string | null;
  email?: string | null;
  page_url?: string | null;
  subject?: string;
  message?: string;
  source_url?: string | null;
  user_agent?: string | null;
};

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
};

const categoryLabels: Record<ContactCategory, string> = {
  factcheck: 'ファクト修正',
  candidate_info: '候補者情報提供',
  bug: '不具合報告',
  research: '取材・共同研究',
  other: 'その他',
};

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...corsHeaders, 'Content-Type': 'application/json; charset=utf-8' },
  });
}

function cleanText(value: unknown, maxLength: number): string {
  return String(value || '').trim().slice(0, maxLength);
}

function cleanNullableText(value: unknown, maxLength: number): string | null {
  const text = cleanText(value, maxLength);
  return text || null;
}

function isHttpUrl(value: string | null): boolean {
  if (!value) return true;
  try {
    const url = new URL(value);
    return url.protocol === 'http:' || url.protocol === 'https:';
  } catch {
    return false;
  }
}

function escapeHtml(value: string | null | undefined): string {
  return String(value || '').replace(/[&<>"']/g, (char) => {
    const table: Record<string, string> = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;',
    };
    return table[char];
  });
}

function buildEmailHtml(payload: Required<ContactPayload>) {
  const category = categoryLabels[payload.category] || payload.category;
  const rows = [
    ['種別', category],
    ['名前', payload.name || '未入力'],
    ['メール', payload.email || '未入力'],
    ['対象ページ', payload.page_url || '未入力'],
    ['参考URL', payload.source_url || '未入力'],
  ];

  return `
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #0f1f3d; line-height: 1.7;">
      <h1 style="font-size: 20px; margin: 0 0 16px;">Polimiru contact</h1>
      <p style="margin: 0 0 18px; font-weight: 700;">${escapeHtml(payload.subject)}</p>
      <table style="border-collapse: collapse; width: 100%; max-width: 720px; margin-bottom: 20px;">
        ${rows.map(([label, value]) => `
          <tr>
            <th style="text-align: left; width: 120px; padding: 8px 10px; background: #f4f6fb; border: 1px solid #e5e7eb;">${escapeHtml(label)}</th>
            <td style="padding: 8px 10px; border: 1px solid #e5e7eb;">${escapeHtml(value)}</td>
          </tr>
        `).join('')}
      </table>
      <div style="white-space: pre-wrap; padding: 14px 16px; background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 8px;">${escapeHtml(payload.message)}</div>
    </div>
  `;
}

async function supabaseRequest(path: string, init: RequestInit) {
  const supabaseUrl = Deno.env.get('SUPABASE_URL');
  const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
  if (!supabaseUrl || !serviceRoleKey) throw new Error('Missing Supabase service configuration');

  return fetch(`${supabaseUrl}/rest/v1/${path}`, {
    ...init,
    headers: {
      apikey: serviceRoleKey,
      Authorization: `Bearer ${serviceRoleKey}`,
      'Content-Type': 'application/json',
      ...(init.headers || {}),
    },
  });
}

async function saveMessage(payload: Required<ContactPayload>) {
  const res = await supabaseRequest('contact_messages', {
    method: 'POST',
    headers: { Prefer: 'return=representation' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Supabase insert failed: ${res.status}`);
  const rows = await res.json();
  return rows[0] as { id: string };
}

async function updateNotification(id: string, status: 'sent' | 'failed', error?: string) {
  await supabaseRequest(`contact_messages?id=eq.${encodeURIComponent(id)}`, {
    method: 'PATCH',
    body: JSON.stringify({
      notification_status: status,
      notified_at: status === 'sent' ? new Date().toISOString() : null,
      notify_error: error ? error.slice(0, 1000) : null,
    }),
  });
}

async function sendNotification(payload: Required<ContactPayload>) {
  const resendApiKey = Deno.env.get('RESEND_API_KEY');
  const notifyTo = Deno.env.get('CONTACT_NOTIFY_TO');
  const from = Deno.env.get('CONTACT_FROM') || 'Polimiru <onboarding@resend.dev>';

  if (!resendApiKey || !notifyTo) throw new Error('Missing Resend notification configuration');

  const res = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${resendApiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      from,
      to: [notifyTo],
      reply_to: payload.email || undefined,
      subject: `[Polimiru] ${categoryLabels[payload.category]}: ${payload.subject}`,
      html: buildEmailHtml(payload),
    }),
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Resend failed: ${res.status} ${body}`);
  }
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }
  if (req.method !== 'POST') {
    return jsonResponse({ error: 'Method not allowed' }, 405);
  }

  let body: ContactPayload;
  try {
    body = await req.json();
  } catch {
    return jsonResponse({ error: 'Invalid JSON' }, 400);
  }

  const category = cleanText(body.category, 40) as ContactCategory;
  const payload: Required<ContactPayload> = {
    category,
    name: cleanNullableText(body.name, 80),
    email: cleanNullableText(body.email, 160),
    page_url: cleanNullableText(body.page_url, 500),
    subject: cleanText(body.subject, 120),
    message: cleanText(body.message, 2000),
    source_url: cleanNullableText(body.source_url, 500),
    user_agent: cleanNullableText(body.user_agent || req.headers.get('user-agent'), 500),
  };

  if (!Object.hasOwn(categoryLabels, payload.category)) {
    return jsonResponse({ error: 'Invalid category' }, 400);
  }
  if (!payload.subject) {
    return jsonResponse({ error: 'Subject is required' }, 400);
  }
  if (payload.message.length < 10) {
    return jsonResponse({ error: 'Message is too short' }, 400);
  }
  if (!isHttpUrl(payload.page_url) || !isHttpUrl(payload.source_url)) {
    return jsonResponse({ error: 'Invalid URL' }, 400);
  }

  try {
    const saved = await saveMessage(payload);
    try {
      await sendNotification(payload);
      await updateNotification(saved.id, 'sent');
      return jsonResponse({ ok: true, notified: true }, 201);
    } catch (error) {
      await updateNotification(saved.id, 'failed', error instanceof Error ? error.message : String(error));
      return jsonResponse({ ok: true, notified: false }, 201);
    }
  } catch (error) {
    console.error(error);
    return jsonResponse({ error: 'Submission failed' }, 500);
  }
});
