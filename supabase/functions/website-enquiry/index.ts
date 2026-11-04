const origins = new Set(['https://imsfrane.com', 'https://www.imsfrane.com', 'https://imsfraneinfo.github.io']);
const recipient = 'imsfraneinfo@gmail.com';
function headers(origin: string) { return {'Content-Type':'application/json', 'Access-Control-Allow-Origin': origins.has(origin) ? origin : 'https://imsfrane.com', 'Access-Control-Allow-Headers':'authorization,apikey,content-type', 'Access-Control-Allow-Methods':'GET,POST,OPTIONS', 'Vary':'Origin', 'Cache-Control':'no-store'}; }
function serviceKey() { return Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || JSON.parse(Deno.env.get('SUPABASE_SECRET_KEYS') || '{}').default || ''; }
export async function handler(req: Request): Promise<Response> {
  const origin = req.headers.get('origin') || '';
  const reply = (body: unknown, status = 200) => new Response(JSON.stringify(body), {status, headers: headers(origin)});
  if (req.method === 'OPTIONS') return new Response(null, {status:204, headers:headers(origin)});
  if (!origins.has(origin)) return reply({error:'ORIGIN_NOT_ALLOWED'},403);
  const apiKey = Deno.env.get('RESEND_API_KEY') || '';
  const from = Deno.env.get('WEBSITE_EMAIL_FROM') || Deno.env.get('MEMBER_EMAIL_FROM') || '';
  const configured = !!apiKey && !!from;
  if (req.method === 'GET') return reply({configured});
  if (req.method !== 'POST') return reply({error:'METHOD_NOT_ALLOWED'},405);
  if (!configured) return reply({error:'EMAIL_NOT_CONFIGURED'},503);
  if (Number(req.headers.get('content-length') || 0) > 24000) return reply({error:'INVALID_REQUEST'},413);
  let data: Record<string, unknown>;
  try { const raw = await req.text(); if(raw.length > 24000) return reply({error:'INVALID_REQUEST'},413); data = JSON.parse(raw); } catch { return reply({error:'INVALID_REQUEST'},400); }
  const name = String(data.name || '').trim(), email = String(data.email || '').trim();
  const message = String(data.message || '').trim(), subject = String(data.subject || '').trim();
  const id = String(data.id || ''), kind = data.kind === 'booking' ? 'Réservation' : 'Contact';
  if (data.website) return reply({error:'INVALID_REQUEST'},400);
  if(name.length < 2 || name.length > 100 || email.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || /[\r\n]/.test(name + email + subject) || subject.length > 160 || message.length < 5 || message.length > 12000 || !/^[0-9a-f-]{36}$/i.test(id)) return reply({error:'INVALID_REQUEST'},400);
  const key = serviceKey(); if (!key) return reply({error:'EMAIL_NOT_CONFIGURED'},503);
  const hash = async (value: string) => Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(key + value)))).map(n=>n.toString(16).padStart(2,'0')).join('');
  const ip = req.headers.get('x-forwarded-for')?.split(',')[0]?.trim() || 'unknown';
  try {
    const quota = await fetch((Deno.env.get('SUPABASE_URL') || '') + '/rest/v1/rpc/claim_website_enquiry', {method:'POST', headers:{'apikey':key,'Authorization':'Bearer '+key,'Content-Type':'application/json'}, body:JSON.stringify({email_hash:await hash(email.toLowerCase()),ip_hash:await hash(ip)})});
    if (!quota.ok) return reply({error:'SERVICE_UNAVAILABLE'},503);
    if (await quota.json() !== true) return reply({error:'RATE_LIMITED'},429);
    const result = await fetch('https://api.resend.com/emails', {method:'POST', signal:AbortSignal.timeout(20000), headers:{'Authorization':'Bearer '+apiKey, 'Content-Type':'application/json', 'Idempotency-Key':'website-enquiry-'+id}, body:JSON.stringify({from,to:[recipient],reply_to:email,subject:'IMSFRANE · '+kind+' · '+(subject || name),text:'Demande depuis le site Imsfrane\nNom : '+name+'\nE-mail : '+email+'\nLangue : '+String(data.language || 'en').slice(0,2)+'\n\n'+message})});
    const sent = await result.json();
    if(!result.ok || !sent.id) return reply({error:'SEND_FAILED'},502);
    return reply({sent:true});
  } catch { return reply({error:'SEND_FAILED'},502); }
}
Deno.serve(handler);
