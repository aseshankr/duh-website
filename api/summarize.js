module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { topic, news, reddit, hn } = req.body || {};
  if (!topic) return res.status(400).json({ error: 'Missing topic' });
  if (!process.env.ANTHROPIC_API_KEY) return res.status(500).json({ error: 'API key not configured' });

  const newsText   = news?.slice(0,5).map(n => `- ${n.title} (${n.srcName})${n.desc ? ': ' + n.desc.slice(0,120) : ''}`).join('\n') || 'No news found.';
  const redditText = reddit?.slice(0,8).map(p => `- [${p.score} upvotes] ${p.title}`).join('\n') || 'No Reddit posts found.';
  const hnText     = hn?.slice(0,5).map(h => `- [${h.points||0} points] ${h.title}`).join('\n') || 'No Hacker News stories found.';

  const prompt = `You are a sharp news analyst. Based on sources about "${topic}", write two things.

NEWS:
${newsText}

REDDIT:
${redditText}

HACKER NEWS:
${hnText}

Return ONLY valid JSON with no markdown or extra text, in this exact format:
{
  "oneliner": "A single punchy sentence under 25 words that explains what's happening — the kind of thing you'd say to start a great conversation at a dinner party. Be specific and interesting, avoid jargon.",
  "bullets": [
    "emoji + one sentence about what is actually happening",
    "emoji + one sentence about public reaction or sentiment",
    "emoji + one sentence about a key debate, controversy or opinion",
    "emoji + one sentence about an interesting angle or takeaway"
  ]
}`;

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': process.env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json'
      },
      body: JSON.stringify({
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 500,
        messages: [{ role: 'user', content: prompt }]
      })
    });

    const data = await response.json();

    if (!response.ok) {
      console.error('Claude API error:', data);
      return res.status(500).json({ error: data.error?.message || 'Claude API error' });
    }

    // Strip markdown code fences if Claude wraps the JSON in ```json ... ```
    const raw = data.content[0].text.trim();
    const text = raw.replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/, '').trim();

    try {
      const parsed = JSON.parse(text);
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.status(200).json({
        summary: Array.isArray(parsed.bullets) ? parsed.bullets.join('\n') : null,
        oneliner: parsed.oneliner || null
      });
    } catch (parseErr) {
      // Fallback: return raw text as summary if JSON parsing fails
      console.warn('JSON parse failed, returning raw text');
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.status(200).json({ summary: text, oneliner: null });
    }

  } catch (e) {
    console.error('Summarize error:', e);
    res.status(500).json({ error: e.message });
  }
};
