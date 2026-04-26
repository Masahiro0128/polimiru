create table if not exists public.contact_messages (
    id uuid primary key default gen_random_uuid(),
    category text not null check (category in ('factcheck', 'candidate_info', 'bug', 'research', 'other')),
    name text,
    email text,
    page_url text,
    subject text not null,
    message text not null,
    source_url text,
    user_agent text,
    status text not null default 'new',
    notification_status text not null default 'pending',
    notified_at timestamptz,
    notify_error text,
    created_at timestamptz not null default now()
);

alter table public.contact_messages enable row level security;

drop policy if exists "Anyone can submit contact messages" on public.contact_messages;
drop policy if exists "No public read access for contact messages" on public.contact_messages;

alter table public.contact_messages
    add column if not exists notification_status text not null default 'pending',
    add column if not exists notified_at timestamptz,
    add column if not exists notify_error text;

create index if not exists contact_messages_created_at_idx
on public.contact_messages (created_at desc);
