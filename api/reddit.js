module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  const q = req.query.q || '';
  if (!q) return res.status(400).json({ error: 'Missing query' });

  try {
    // Pullpush.io is a public Reddit data API that doesn't block server requests
    const url = `https://api.pullpush.io/reddit/search/submission/?q=${encodeURIComponent(q)}&size=40&sort=desc&sort_type=score`;
    const response = await fetch(url, {
      headers: { 'Accept': 'application/json', 'User-Agent': 'duh.co.in/1.0' }
    });

    if (response.ok) {
      const data = await response.json();
      // Pullpush returns { data: [...] } — normalise to Reddit's { data: { children: [...] } }
      const posts = (data.data || []).map(post => ({
        data: {
          title: post.title || '',
          selftext: post.selftext || '',
          score: post.score || 0,
          url: `https://www.reddit.com${post.permalink || ''}`,
          subreddit: post.subreddit || '',
          num_comments: post.num_comments || 0,
        }
      }));
      return res.status(200).json({ data: { children: posts } });
    }
  } catch (e) {
    console.warn('Pullpush failed:', e.message);
  }

  // Fallback — return empty so frontend handles gracefully
  return res.status(200).json({ data: { children: [] } });
};
