// Tells the Oval Office clock which city the visitor is in.
// Vercel adds the visitor's approximate city to every request (from their network address),
// so no location permission is needed. Nothing is stored or logged.
export default function handler(req, res) {
  let city = '';
  try { city = decodeURIComponent(req.headers['x-vercel-ip-city'] || ''); } catch (e) { city = ''; }
  res.setHeader('Cache-Control', 'private, no-store');
  res.status(200).json({ city });
}
