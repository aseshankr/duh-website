module.exports = async function handler(req, res) {
  const q = req.query.q || '';
  // Convert search query to a Medium tag (lowercase, hyphenated)
  const tag = q.toLowerCase().replace(/[^a-z0-9\s]/g, '').replace(/\s+/g, '-').slice(0, 60);

  try {
    const response = await fetch(`https://medium.com/feed/tag/${encodeURIComponent(tag)}`, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; duh.co.in/1.0)',
        'Accept': 'application/rss+xml, application/xml, text/xml'
      }
    });
    const text = await response.text();
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Content-Type', 'application/xml; charset=utf-8');
    res.status(200).send(text);
  } catch (e) {
    console.error('Medium error:', e);
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.status(200).send('<rss><channel></channel></rss>');
  }
};
