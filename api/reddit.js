module.exports = async function handler(req, res) {
  const q = req.query.q || '';
  if (!q) return res.status(400).json({ error: 'Missing query' });

  // Try multiple Reddit endpoints — Reddit sometimes blocks based on User-Agent or path
  const urls = [
    `https://www.reddit.com/search.json?q=${encodeURIComponent(q)}&sort=relevance&limit=60&t=year&raw_json=1`,
    `https://old.reddit.com/search.json?q=${encodeURIComponent(q)}&sort=relevance&limit=60&t=year&raw_json=1`,
  ];

  const headers = [
    { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36', 'Accept': 'application/json' },
    { 'User-Agent': 'web:duh.co.in:v1.0 (by /u/duhwebsite)', 'Accept': 'application/json' },
  ];

  for (let i = 0; i < urls.length; i++) {
    try {
      const response = await fetch(urls[i], { headers: headers[i] });
      if (response.ok) {
        const data = await response.json();
        res.setHeader('Access-Control-Allow-Origin', '*');
        return res.status(200).json(data);
      }
    } catch (e) {
      console.warn(`Reddit attempt ${i + 1} failed:`, e.message);
    }
  }

  // All attempts failed — return empty structure so the frontend handles it gracefully
  res.setHeader('Access-Control-Allow-Origin', '*');
  return res.status(200).json({ data: { children: [] } });
};
