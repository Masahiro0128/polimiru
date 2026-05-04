-- Authenticated, moderated comments for politician pages.
-- Run this in Supabase SQL editor before deploying the updated comments UI.

create table if not exists public.comments (
    id uuid primary key default gen_random_uuid(),
    politician_id text not null,
    user_id uuid references auth.users(id) on delete set null,
    nickname text not null default 'ログインユーザー',
    body text not null,
    source_url text,
    status text not null default 'pending' check (status in ('pending', 'approved', 'rejected')),
    moderation_note text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

alter table public.comments
    add column if not exists user_id uuid references auth.users(id) on delete set null,
    add column if not exists status text not null default 'pending',
    add column if not exists moderation_note text,
    add column if not exists updated_at timestamptz not null default now();

-- Treat rows created before moderation existed as already published.
update public.comments
set status = 'approved'
where user_id is null
  and status = 'pending';

do $$
begin
    if not exists (
        select 1
        from pg_constraint
        where conname = 'comments_status_valid'
          and conrelid = 'public.comments'::regclass
    ) then
        alter table public.comments
            add constraint comments_status_valid
            check (status in ('pending', 'approved', 'rejected'));
    end if;

    if not exists (
        select 1
        from pg_constraint
        where conname = 'comments_body_length'
          and conrelid = 'public.comments'::regclass
    ) then
        alter table public.comments
            add constraint comments_body_length
            check (char_length(body) between 5 and 500)
            not valid;
    end if;

    if not exists (
        select 1
        from pg_constraint
        where conname = 'comments_source_url_http'
          and conrelid = 'public.comments'::regclass
    ) then
        alter table public.comments
            add constraint comments_source_url_http
            check (source_url is null or source_url ~* '^https?://')
            not valid;
    end if;
end $$;

create index if not exists comments_politician_status_created_idx
    on public.comments (politician_id, status, created_at desc);

create index if not exists comments_user_created_idx
    on public.comments (user_id, created_at desc);

alter table public.comments enable row level security;

drop policy if exists "Anyone can read approved comments" on public.comments;
create policy "Anyone can read approved comments"
    on public.comments for select
    using (status = 'approved');

drop policy if exists "Authenticated users can submit pending comments" on public.comments;
create policy "Authenticated users can submit pending comments"
    on public.comments for insert
    to authenticated
    with check (
        auth.uid() = user_id
        and status = 'pending'
        and char_length(body) between 5 and 500
        and source_url ~* '^https?://'
    );

drop policy if exists "Users cannot update comments directly" on public.comments;
create policy "Users cannot update comments directly"
    on public.comments for update
    using (false)
    with check (false);

drop policy if exists "Users cannot delete comments directly" on public.comments;
create policy "Users cannot delete comments directly"
    on public.comments for delete
    using (false);
