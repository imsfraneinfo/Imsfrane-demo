create table if not exists public.website_enquiry_limits (
 bucket text primary key,
 window_start timestamptz not null,
 attempts integer not null check (attempts > 0)
);
alter table public.website_enquiry_limits enable row level security;
revoke all on public.website_enquiry_limits from public, anon, authenticated;
grant select, insert, update, delete on public.website_enquiry_limits to service_role;
create or replace function public.claim_website_enquiry(email_hash text, ip_hash text)
returns boolean language plpgsql security invoker set search_path = pg_catalog, public as $$
declare current_window timestamptz := date_trunc('hour', now());
declare global_count integer;
declare email_count integer;
declare ip_count integer;
begin
 if email_hash !~ '^[a-f0-9]{64}$' or ip_hash !~ '^[a-f0-9]{64}$' then return false; end if;
 perform pg_advisory_xact_lock(756398133);
 delete from public.website_enquiry_limits where window_start < current_window;
 select attempts into global_count from public.website_enquiry_limits where bucket='global';
 select attempts into email_count from public.website_enquiry_limits where bucket='email:'||email_hash;
 select attempts into ip_count from public.website_enquiry_limits where bucket='ip:'||ip_hash;
 if coalesce(global_count,0)>=100 or coalesce(email_count,0)>=3 or coalesce(ip_count,0)>=10 then return false; end if;
 insert into public.website_enquiry_limits(bucket,window_start,attempts)
 values('global',current_window,1),('email:'||email_hash,current_window,1),('ip:'||ip_hash,current_window,1)
 on conflict(bucket) do update set attempts=public.website_enquiry_limits.attempts+1;
 return true;
end;
$$;
revoke all on function public.claim_website_enquiry(text,text) from public,anon,authenticated;
grant execute on function public.claim_website_enquiry(text,text) to service_role;
