module.exports = async function handler(req, res) {
  const q = req.query.q || '';
  if (!q) return res.status(400).json({ error: 'Missing query' });

  const url = `https://www.reddit.com/search.json?q=${encodeURIComponent(q)}&sort=relevance&limit=60&t=year&raw_json=1`;

  try {
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; duh.co.in/1.0)',
        'Accept': 'application/json'
      }
    });
    const data = await response.json();
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.status(200).json(data);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
};
