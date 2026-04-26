# Contact notification setup

Contact form submissions go through `supabase/functions/contact-submit`.

The function does three things:

1. validates the submitted payload
2. stores it in `public.contact_messages`
3. sends a notification email via Resend

## 1. Create or update the table

Run this SQL in the Supabase SQL Editor:

```sql
-- scripts/setup_contact_messages.sql
```

Use the contents of `scripts/setup_contact_messages.sql`.

## 2. Create a Resend API key

Create an API key in Resend and keep it secret.

For production, set `CONTACT_FROM` to an address on a verified domain, for example:

```text
Polimiru <contact@your-domain.com>
```

For early testing, Resend's onboarding sender can be used if the recipient is allowed by your Resend account:

```text
Polimiru <onboarding@resend.dev>
```

## 3. Set Supabase Edge Function secrets

Set these secrets in Supabase:

```text
RESEND_API_KEY=your_resend_api_key
CONTACT_NOTIFY_TO=your_destination_email@example.com
CONTACT_FROM=Polimiru <contact@your-domain.com>
```

If you use the Supabase CLI:

```bash
supabase secrets set RESEND_API_KEY=your_resend_api_key
supabase secrets set CONTACT_NOTIFY_TO=your_destination_email@example.com
supabase secrets set "CONTACT_FROM=Polimiru <contact@your-domain.com>"
```

## 4. Deploy the function

```bash
supabase functions deploy contact-submit
```

The frontend posts to:

```text
https://dmwccumxflysgxauzxix.supabase.co/functions/v1/contact-submit
```

## 5. Check submissions

Open Supabase Table Editor and inspect:

```text
public.contact_messages
```

Useful columns:

- `notification_status`: `sent`, `failed`, or `pending`
- `notified_at`: when the email was sent
- `notify_error`: Resend or configuration error when notification failed
