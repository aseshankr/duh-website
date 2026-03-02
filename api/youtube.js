module.exports = async function handler(req, res) {
  const q = req.query.q || '';
  const apiKey = process.env.YOUTUBE_API_KEY;

  res.setHeader('Access-Control-Allow-Origin', '*');

  if (!apiKey) {
    return res.status(200).json({ items: [] });
  }

  try {
    const url = `https://www.googleapis.com/youtube/v3/search?part=snippet&q=${encodeURIComponent(q)}&type=video&maxResults=4&order=relevance&key=${apiKey}`;
    const response = await fetch(url);
    const data = await response.json();

    if (!response.ok) {
      console.error('YouTube API error:', data);
      return res.status(200).json({ items: [] });
    }

    res.status(200).json(data);
  } catch (e) {
    console.error('YouTube error:', e);
    res.status(200).json({ items: [] });
  }
};
