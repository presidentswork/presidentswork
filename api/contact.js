// Receives the Contact page form and files it in Airtable
// (base "President's Work — Enquiries", table "Website Contact").
// Set AIRTABLE_TOKEN in the Vercel project's environment variables.

const BASE = 'appNKEw90Aaca9XbC';
const TABLE = 'tbljuwGucpa90Ed3n';
const STAGES = ['Thinking', 'Launching', 'Building', 'Growing', 'Leading'];

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Use POST' });
    return;
  }

  const token = process.env.AIRTABLE_TOKEN;
  if (!token) {
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

  const fields = {
    Name: first + ' ' + last,
    'First Name': first,
    'Last Name': last,
    Email: email,
    Company: company,
    Stage: stage,
    Message: message,
    Source: clean(body.source, 500),
    Submitted: new Date().toISOString(),
    Status: 'New'
  };

  try {
    const airtable = await fetch('https://api.airtable.com/v0/' + BASE + '/' + TABLE, {
      method: 'POST',
      headers: { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json' },
      body: JSON.stringify({ records: [{ fields }], typecast: true })
    });
    if (!airtable.ok) {
      console.error('Airtable rejected the record:', airtable.status, await airtable.text());
      res.status(502).json({ error: 'We could not save that.' });
      return;
    }
    res.status(200).json({ ok: true });
  } catch (err) {
    console.error('Airtable request failed:', err);
    res.status(502).json({ error: 'We could not save that.' });
  }
}
