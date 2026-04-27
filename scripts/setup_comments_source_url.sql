-- Comments evidence URL migration.
-- Existing rows are kept as-is; the website requires source_url for new posts.

alter table public.comments
    add column if not exists source_url text;

do $$
begin
    if not exists (
        select 1
        from pg_constraint
        where conname = 'comments_source_url_http'
          and conrelid = 'public.comments'::regclass
    ) then
        alter table public.comments
            add constraint comments_source_url_http
            check (
                source_url is null
                or source_url ~* '^https?://'
            );
    end if;
end $$;

create index if not exists comments_politician_created_at_idx
    on public.comments (politician_id, created_at desc);
