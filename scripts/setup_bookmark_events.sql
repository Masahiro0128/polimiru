-- ブックマークイベントログテーブル
-- ユーザー識別なし・IPなし。entity_id と action のみ記録。
create table if not exists public.bookmark_events (
    id          uuid        primary key default gen_random_uuid(),
    entity_id   text        not null,
    entity_type text        not null check (entity_type in ('politician', 'election')),
    action      text        not null check (action in ('add', 'remove')),
    created_at  timestamptz not null default now()
);

-- RLS: 誰でも insert 可、read は不可
alter table public.bookmark_events enable row level security;

drop policy if exists "Anyone can insert bookmark events" on public.bookmark_events;
create policy "Anyone can insert bookmark events"
    on public.bookmark_events for insert
    with check (true);

drop policy if exists "No public read access for bookmark events" on public.bookmark_events;
create policy "No public read access for bookmark events"
    on public.bookmark_events for select
    using (false);

-- 集計用ビュー（管理画面から参照用）
create or replace view public.bookmark_counts as
select
    entity_id,
    entity_type,
    count(*) filter (where action = 'add')    as total_adds,
    count(*) filter (where action = 'remove') as total_removes,
    count(*) filter (where action = 'add') - count(*) filter (where action = 'remove') as net_count
from public.bookmark_events
group by entity_id, entity_type
order by net_count desc;

create index if not exists bookmark_events_entity_idx
    on public.bookmark_events (entity_id, entity_type);
create index if not exists bookmark_events_created_at_idx
    on public.bookmark_events (created_at desc);
