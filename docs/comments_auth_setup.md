# Comments Auth Setup

Polimiru comments are intended to be readable by anyone, but writable only by signed-in users. New comments are stored as `pending` and become public only after an admin changes them to `approved`.

## 1. Run SQL

Run the contents of:

```text
scripts/setup_comments_auth.sql
```

Expected behavior:

- Anonymous users can only read `approved` comments.
- Authenticated users can insert their own `pending` comments.
- Browser users cannot update or delete comments directly.
- Existing pre-moderation comments are marked `approved`.

## 2. Enable Supabase Auth Providers

In Supabase Dashboard:

```text
Authentication > Providers
```

Enable:

- Email
- Google
- Apple

For Google and Apple, configure each provider's client ID/secret from the provider console.

## 3. Configure Redirect URLs

In Supabase Dashboard:

```text
Authentication > URL Configuration
```

Set the Site URL:

```text
https://polimiru.jp
```

Add redirect URLs:

```text
https://polimiru.jp/**
http://localhost:*/**
```

Use the localhost redirect only for local testing.

## 4. Email Delivery

Supabase built-in email has strict rate limits. For production, configure custom SMTP:

```text
Authentication > SMTP Settings
```

Recommended provider: Resend or another transactional email service.

## 5. Moderation

Approve a comment by updating:

```sql
update public.comments
set status = 'approved', updated_at = now()
where id = '<comment-id>';
```

Reject a comment:

```sql
update public.comments
set status = 'rejected', moderation_note = 'reason', updated_at = now()
where id = '<comment-id>';
```

## 6. Next Security Step

For stronger abuse protection, move comment submission behind a Supabase Edge Function and add Cloudflare Turnstile plus per-user/IP rate limiting.
