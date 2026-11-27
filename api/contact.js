// Receives the Contact page form.
// 1) Emails the enquiry to hello@presidentswork.com through Resend (RESEND_API_KEY).
// 2) Also files it in Airtable (base "President's Work — Enquiries", table "Website Contact") when AIRTABLE_TOKEN works.
// The visitor gets a success message if either one succeeds, so an Airtable limit never loses an enquiry.

const BASE = 'appNKEw90Aaca9XbC';
const TABLE = 'tbljuwGucpa90Ed3n';
const STAGES = ['Thinking', 'Launching', 'Building', 'Growing', 'Leading'];
const TO = process.env.CONTACT_TO || 'hello@presidentswork.com';
const FROM = process.env.CONTACT_FROM || 'Presidents Work <onboarding@resend.dev>';

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Use POST' });
    return;
  }

  const resendKey = process.env.RESEND_API_KEY;
  const airtableToken = process.env.AIRTABLE_TOKEN;
  if (!resendKey && !airtableToken) {
    res.status(500).json({ error: 'The form is not connected yet.' });
    return;
  }

  let body = req.body || {};
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch (e) { body = {}; }
  }
  const clean = (v, max = 300) => String(v || '').trim().slice(0, max);

  // Bots fill the hidden website field; people never see it.
  if (clean(body.website)) {
    res.status(200).json({ ok: true });
    return;
  }

  const first = clean(body.first, 100);
  const last = clean(body.last, 100);
  const email = clean(body.email, 200);
  const company = clean(body.company, 200);
  const message = clean(body.message, 5000);
  const stage = (Array.isArray(body.stage) ? body.stage : [body.stage]).map((s) => clean(s, 40)).filter((s) => STAGES.includes(s));
  const source = clean(body.source, 500);

  if (!first || !last || !company || !message) {
    res.status(400).json({ error: 'Please fill in every field marked *.' });
    return;
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) {
    res.status(400).json({ error: 'Please enter a valid email address.' });
    return;
  }
  if (!stage.length) {
    res.status(400).json({ error: 'Please choose at least one stage.' });
    return;
  }

  const name = first + ' ' + last;
  let emailed = false, saved = false;

  if (resendKey) {
    try {
      const rows = [['Name', name], ['Email', email], ['Company', company], ['Stage', stage.join(', ')], ['Came from', source || '—']];
      const html = `<div style="font-family:-apple-system,Helvetica,Arial,sans-serif;color:#121212;max-width:560px">
<p style="font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:#777;margin:0 0 6px">New enquiry · presidentswork.com</p>
<h2 style="font-weight:500;margin:0 0 18px">${esc(name)} — ${esc(company)}</h2>
<table style="border-collapse:collapse;width:100%;font-size:14px">${rows.map(([k, v]) => `<tr><td style="padding:6px 12px 6px 0;color:#777;white-space:nowrap;vertical-align:top">${k}</td><td style="padding:6px 0">${esc(v)}</td></tr>`).join('')}</table>
<p style="white-space:pre-wrap;font-size:15px;line-height:1.55;border-top:1px solid #e5e5e5;margin-top:16px;padding-top:16px">${esc(message)}</p>
<p style="font-size:12px;color:#999">Reply to this email to answer ${esc(first)} directly.</p></div>`;
      const text = rows.map(([k, v]) => k + ': ' + v).join('\n') + '\n\n' + message;
      const r = await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: { Authorization: 'Bearer ' + resendKey, 'Content-Type': 'application/json' },
        body: JSON.stringify({ from: FROM, to: [TO], reply_to: email, subject: `New enquiry: ${name}, ${company}`, html, text })
      });
      if (r.ok) emailed = true;
      else console.error('Resend rejected the email:', r.status, await r.text());
    } catch (err) {
      console.error('Resend request failed:', err);
    }
  }

  if (airtableToken) {
    try {
      const fields = { Name: name, 'First Name': first, 'Last Name': last, Email: email, Company: company, Stage: stage, Message: message, Source: source, Submitted: new Date().toISOString(), Status: 'New' };
      const a = await fetch('https://api.airtable.com/v0/' + BASE + '/' + TABLE, {
        method: 'POST',
        headers: { Authorization: 'Bearer ' + airtableToken, 'Content-Type': 'application/json' },
        body: JSON.stringify({ records: [{ fields }], typecast: true })
      });
      if (a.ok) saved = true;
      else console.error('Airtable rejected the record:', a.status, await a.text());
    } catch (err) {
      console.error('Airtable request failed:', err);
    }
  }

  if (emailed || saved) {
    res.status(200).json({ ok: true, emailed, saved });
    return;
  }
  res.status(502).json({ error: 'We could not save that.' });
}
