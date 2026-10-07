// Lead proxy: receives website form posts and creates events in Follow Up Boss.
// The Follow Up Boss API key lives only here (as a Worker secret), never in the website's HTML.

const json = (body, status, cors) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json', ...cors } });

const clean = (v, max = 500) => (typeof v === 'string' ? v.trim().slice(0, max) : '');

export default {
  async fetch(req, env) {
    const origin = req.headers.get('Origin') || '';
    const allowed = (env.ALLOWED_ORIGINS || '').split(',').map((s) => s.trim()).filter(Boolean);
    const originOk = allowed.length === 0 || allowed.includes(origin);
    const cors = {
      'Access-Control-Allow-Origin': originOk && origin ? origin : allowed[0] || '',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Accept',
      Vary: 'Origin',
    };

    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });
    if (req.method !== 'POST') return json({ ok: false, error: 'method_not_allowed' }, 405, cors);
    if (!originOk) return json({ ok: false, error: 'forbidden' }, 403, cors);
    if (!env.FUB_API_KEY) return json({ ok: false, error: 'not_configured' }, 500, cors);

    let d;
    try { d = await req.json(); } catch { return json({ ok: false, error: 'bad_json' }, 400, cors); }

    // Honeypot: bots fill the hidden "website" field. Pretend success and drop it.
    if (clean(d.website)) return json({ ok: true }, 200, cors);

    const name = clean(d.name, 120);
    const email = clean(d.email, 200);
    const phone = clean(d.phone, 40);
    if (!name || !(/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email) || phone)) return json({ ok: false, error: 'invalid' }, 400, cors);

    const [firstName, ...rest] = name.split(/\s+/);
    const lastName = rest.join(' ');
    const isChat = d.formType === 'chat-lead' || d.formType === 'chat-details';
    const isQualification = d.formType === 'property-qualification';
    const county = clean(d.county, 60);
    const services = [].concat(d.services || []).map((s) => clean(s, 60)).filter(Boolean);

    const lines = isQualification
      ? [
          'PROPERTY QUALIFICATION (GB Home Rentals website)',
          `Address: ${clean(d.address)}`,
          `County: ${county || 'Not provided'}`,
          `Property type: ${clean(d.propertyType, 80)}`,
          `Year built: ${clean(String(d.yearBuilt || ''), 10)}`,
          `Bedrooms: ${clean(String(d.bedrooms || ''), 20)}`,
          `Current status: ${clean(d.status, 80)}`,
          `Needs manager: ${clean(d.timeframe, 80)}`,
          `In-house services of interest: ${services.join(', ') || 'None selected'}`,
          `Notes: ${clean(d.notes, 800) || 'None'}`,
        ]
      : isChat
      ? [`WEBSITE CHAT (${d.formType === 'chat-details' ? 'follow-up details' : 'new lead'})`, `Topic: ${clean(d.topic, 80)}`, `Message: ${clean(d.message, 800) || 'None yet'}`]
      : ['GENERAL INFORMATION REQUEST (GB Home Rentals website)', `Message: ${clean(d.message, 800)}`];

    const tags = ['GB Home Rentals', 'Website Lead', isQualification ? 'Owner Qualification' : isChat ? 'Chat Lead' : 'Owner Inquiry'];
    if (county) tags.push(`${county} County`);
    services.forEach((s) => tags.push(`Interest: ${s}`));

    const event = {
      source: 'GB Home Rentals Website',
      system: env.FUB_SYSTEM || 'GBHomeRentals',
      type: isQualification ? 'Registration' : 'General Inquiry',
      message: lines.join('\n'),
      person: {
        firstName,
        lastName,
        emails: email ? [{ value: email }] : [],
        phones: phone ? [{ value: phone }] : [],
        tags,
      },
    };
    if (isQualification && clean(d.street)) {
      event.property = { street: clean(d.street), city: clean(d.city, 80), state: clean(d.state, 10), code: clean(d.zip, 12) };
    }

    const headers = {
      'Content-Type': 'application/json',
      Authorization: 'Basic ' + btoa(env.FUB_API_KEY + ':'),
      'X-System': env.FUB_SYSTEM || 'GBHomeRentals',
    };
    if (env.FUB_SYSTEM_KEY) headers['X-System-Key'] = env.FUB_SYSTEM_KEY;

    const res = await fetch('https://api.followupboss.com/v1/events', { method: 'POST', headers, body: JSON.stringify(event) });
    if (!res.ok && res.status !== 204) {
      console.error('Follow Up Boss error', res.status, (await res.text()).slice(0, 300));
      return json({ ok: false, error: 'crm_error' }, 502, cors);
    }
    return json({ ok: true }, 200, cors);
  },
};
