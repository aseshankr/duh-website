module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { topic, news, reddit, hn } = req.body || {};
  if (!topic) return res.status(400).json({ error: 'Missing topic' });
  if (!process.env.ANTHROPIC_API_KEY) return res.status(500).json({ error: 'API key not configured' });

  // Build context from all sources
  const newsText    = news?.slice(0, 5).map(n => `- ${n.title} (${n.srcName})${n.desc ? ': ' + n.desc.slice(0, 120) : ''}`).join('\n') || 'No news found.';
  const redditText  = reddit?.slice(0, 8).map(p => `- [${p.score} upvotes] ${p.title}`).join('\n') || 'No Reddit posts found.';
  const hnText      = hn?.slice(0, 5).map(h => `- [${h.points || 0} points] ${h.title}`).join('\n') || 'No Hacker News stories found.';

  const prompt = `You are a sharp, concise news analyst. Based on the sources below about "${topic}", write a smart brief for a general audience.

NEWS ARTICLES:
${newsText}

REDDIT DISCUSSIONS:
${redditText}

HACKER NEWS:
${hnText}

Write exactly 4 bullet points. Each bullet must:
- Start with a relevant emoji
- Be one clear, specific sentence
- Cover: (1) what's happening, (2) public sentiment, (3) a key debate or opinion, (4) an interesting angle or takeaway

No headers, no intro text. Just the 4 bullet points.`;

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': process.env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json'
      },
      body: JSON.stringify({
        model: 'claude-3-5-haiku-20241022',
        max_tokens: 350,
        messages: [{ role: 'user', content: prompt }]
      })
    });

    const data = await response.json();

    if (!response.ok) {
      console.error('Claude API error:', data);
      return res.status(500).json({ error: data.error?.message || 'Claude API error' });
    }

    res.setHeader('Access-Control-Allow-Origin', '*');
    res.status(200).json({ summary: data.content[0].text });

  } catch (e) {
    console.error('Summarize error:', e);
    res.status(500).json({ error: e.message });
  }
};
