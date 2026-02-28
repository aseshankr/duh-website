import feedparser
import os
from datetime import datetime
import pytz
import re

IST = pytz.timezone('Asia/Kolkata')

# Free RSS feeds - no API key needed, works from any server
RSS_FEEDS = {
    'general': [
        'https://feeds.feedburner.com/ndtvnews-top-stories',
        'https://timesofindia.indiatimes.com/rssfeedstopstories.cms',
        'https://www.thehindu.com/news/national/feeder/default.rss',
    ],
    'business': [
        'https://feeds.feedburner.com/ndtvnews-business',
        'https://timesofindia.indiatimes.com/rssfeeds/1898055.cms',
        'https://www.thehindu.com/business/feeder/default.rss',
    ],
    'sports': [
        'https://feeds.feedburner.com/ndtvnews-sports',
        'https://timesofindia.indiatimes.com/rssfeeds/4719161.cms',
        'https://www.thehindu.com/sport/feeder/default.rss',
    ],
    'technology': [
        'https://feeds.feedburner.com/ndtvnews-tech',
        'https://timesofindia.indiatimes.com/rssfeeds/-2128672765.cms',
    ],
    'entertainment': [
        'https://feeds.feedburner.com/ndtvnews-entertainment',
        'https://timesofindia.indiatimes.com/rssfeeds/1081479906.cms',
    ],
}

CATEGORY_CONFIG = {
    'general':       {'label': 'üáÆüá≥ India',       'badge': 'b-india'},
    'business':      {'label': 'üíº Business',      'badge': 'b-biz'},
    'sports':        {'label': 'üèè Sports',         'badge': 'b-sports'},
    'technology':    {'label': 'üì± Tech',           'badge': 'b-tech'},
    'entertainment': {'label': 'üé¨ Entertainment', 'badge': 'b-life'},
}

EMOJI_MAP = {
    'general':       ['üáÆüá≥', 'üì∞', 'üèõÔ∏è', '‚ö°', 'üîî'],
    'business':      ['üíº', 'üìà', 'üí∞', 'üè¶', 'üíπ'],
    'sports':        ['üèè', '‚öΩ', 'üèÜ', 'ü•á', 'üéØ'],
    'technology':    ['üì±', 'üíª', 'ü§ñ', 'üöÄ', 'üî¨'],
    'entertainment': ['üé¨', 'üéµ', '‚≠ê', 'üé≠', 'üé™'],
}


def fetch(category, size=5):
    articles = []
    for url in RSS_FEEDS.get(category, []):
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:size]:
                title = entry.get('title', '').strip()
                summary = entry.get('summary', '') or entry.get('description', '')
                summary = re.sub('<[^<]+?>', '', summary).strip()  # Strip HTML tags
                link = entry.get('link', '#')
                source = feed.feed.get('title', 'News')
                if title:
                    articles.append({
                        'title': title,
                        'description': summary,
                        'url': link,
                        'source': source,
                    })
            if articles:
                break  # Got enough from first working feed
        except Exception as e:
            print(f"  Warning: Could not fetch {url}: {e}")
            continue
    return articles[:size]


def clean(text, max_words=40):
    if not text:
        return ''
    words = str(text).split()
    if len(words) > max_words:
        return ' '.join(words[:max_words]) + '...'
    return ' '.join(words)


def why_matters(category):
    tips = {
        'general':       ('üáÆüá≥ Why it matters', 'This story affects India and its people directly.'),
        'business':      ('üí∞ For your wallet', 'Keep an eye on how this affects markets and your money.'),
        'sports':        ('üèÜ For fans', 'Here\'s what this means for Indian sports.'),
        'technology':    ('üì± For you', 'This could change how you use technology soon.'),
        'entertainment': ('üçø In short', 'Here\'s the scoop from the world of entertainment.'),
    }
    return tips.get(category, ('ü§î Why it matters', 'Stay informed on this one.'))


def make_card(article, category, idx, size='large'):
    cfg = CATEGORY_CONFIG[category]
    emoji = EMOJI_MAP[category][idx % len(EMOJI_MAP[category])]
    title = (article.get('title', '') or '').split(' - ')[0].strip()
    desc = clean(article.get('description', '') or '', 40)
    url = article.get('url', '#') or '#'
    source = article.get('source', 'News')
    why_label, why_text = why_matters(category)

    if size == 'large':
        return f'''
    <div class="card" onclick="window.open('{url}','_blank')">
      <div class="card-emoji">{emoji}</div>
      <div class="card-body">
        <span class="badge {cfg["badge"]}">{cfg["label"]}</span>
        <div class="card-headline">{title}</div>
        <div class="card-text">{desc if desc else "Click to read the full story."}</div>
        <div class="why-box"><strong>{why_label}:</strong> {why_text}</div>
        <div class="card-footer">
          <span class="read-time">üì∞ {source}</span>
          <a href="{url}" target="_blank" class="read-more">Read full story ‚Üí</a>
        </div>
      </div>
    </div>'''

    elif size == 'side':
        return f'''
      <div class="side-card" onclick="window.open('{url}','_blank')">
        <div class="side-emoji">{emoji}</div>
        <div class="side-content">
          <span class="badge {cfg["badge"]}">{cfg["label"]}</span>
          <div class="side-headline">{title}</div>
          <div class="side-text">{clean(desc, 20) if desc else "Click to read more."}</div>
        </div>
      </div>'''

    else:
        return f'''
    <div class="card card-sm" onclick="window.open('{url}','_blank')">
      <div class="card-emoji">{emoji}</div>
      <div class="card-body card-body-sm">
        <span class="badge {cfg["badge"]}">{cfg["label"]}</span>
        <div class="card-headline">{title}</div>
        <div class="card-text">{clean(desc, 25) if desc else "Click to read the full story."}</div>
        <div class="why-box"><strong>{why_label}:</strong> {why_text}</div>
      </div>
    </div>'''


def generate_ticker(all_articles):
    icons = ['üì∞', '‚ö°', 'üîî', 'üåü', 'üí°', 'üóûÔ∏è', 'üì£', 'üî¥']
    items = []
    for i, a in enumerate(all_articles[:10]):
        title = (a.get('title', '') or '').split(' - ')[0].strip()
        if title:
            items.append(f'<span>{icons[i % len(icons)]} {title}</span><span class="sep">|</span>')
    content = ''.join(items)
    return content * 2  # Duplicate for seamless loop


def generate_html(articles_by_cat):
    now = datetime.now(IST)
    date_str = now.strftime('%A, %d %B %Y')
    time_str = now.strftime('%I:%M %p')

    general = articles_by_cat.get('general', [])
    business = articles_by_cat.get('business', [])
    sports = articles_by_cat.get('sports', [])
    technology = articles_by_cat.get('technology', [])
    entertainment = articles_by_cat.get('entertainment', [])

    all_flat = general + business + sports + technology + entertainment
    total = len(all_flat)

    # Hero card - first general article
    hero_html = make_card(general[0], 'general', 0, 'large') if general else '<p style="color:#888;padding:20px;">No stories today.</p>'

    # Sidebar - one from each category safely
    side_html_parts = []
    sidebar_pairs = [
        (business, 'business'),
        (sports, 'sports'),
        (technology, 'technology'),
    ]
    for idx, (cat_articles, cat_name) in enumerate(sidebar_pairs):
        if cat_articles:
            side_html_parts.append(make_card(cat_articles[0], cat_name, idx, 'side'))
    side_html = ''.join(side_html_parts)

    # Grid cards - mix of remaining articles
    grid_pairs = []
    if len(general) > 1:      grid_pairs.append((general[1], 'general'))
    if len(business) > 1:     grid_pairs.append((business[1], 'business'))
    if entertainment:          grid_pairs.append((entertainment[0], 'entertainment'))
    if len(technology) > 1:   grid_pairs.append((technology[1], 'technology'))
    if len(sports) > 1:       grid_pairs.append((sports[1], 'sports'))
    if len(entertainment) > 1: grid_pairs.append((entertainment[1], 'entertainment'))

    grid_html = ''.join(make_card(a, cat, i, 'small') for i, (a, cat) in enumerate(grid_pairs[:6]))
    ticker_html = generate_ticker(all_flat)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <meta name="description" content="DUH - India's news, so simple you'll go duh. No jargon, no drama."/>
  <title>DUH - India's Simplest News</title>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0;}}
    :root{{--orange:#FF5722;--dark:#0D0D0D;--card:#1A1A1A;--text:#F0F0F0;--muted:#888;--border:#2A2A2A;--green:#00C853;--red:#FF1744;}}
    body{{background:var(--dark);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;min-height:100vh;}}
    .topbar{{background:#111;border-bottom:1px solid var(--border);padding:8px 24px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;}}
    .topbar-date{{color:var(--muted);font-size:12px;}}
    .topbar-links{{display:flex;gap:20px;}}
    .topbar-links a{{color:var(--muted);font-size:12px;text-decoration:none;}}
    .topbar-links a:hover{{color:var(--orange);}}
    header{{background:#111;border-bottom:2px solid var(--border);padding:28px 24px 20px;text-align:center;}}
    .logo{{font-size:72px;font-weight:900;letter-spacing:-4px;color:#fff;line-height:1;}}
    .logo span{{color:var(--orange);}}
    .tagline{{color:var(--muted);font-size:13px;letter-spacing:3px;text-transform:uppercase;margin-top:6px;}}
    .header-sub{{color:#555;font-size:12px;margin-top:8px;}}
    .ticker{{background:var(--orange);padding:8px 0;overflow:hidden;white-space:nowrap;}}
    .ticker-inner{{display:inline-block;animation:ticker 50s linear infinite;}}
    .ticker-inner span{{font-size:13px;font-weight:700;color:#fff;padding:0 32px;}}
    .ticker-inner .sep{{color:rgba(255,255,255,0.4);padding:0 8px;}}
    @keyframes ticker{{0%{{transform:translateX(0);}}100%{{transform:translateX(-50%);}}}}
    nav{{background:#111;border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100;}}
    .nav-inner{{max-width:1140px;margin:0 auto;display:flex;overflow-x:auto;scrollbar-width:none;}}
    .nav-inner::-webkit-scrollbar{{display:none;}}
    .nav-item{{padding:14px 20px;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:var(--muted);white-space:nowrap;border-bottom:3px solid transparent;text-decoration:none;transition:all 0.2s;}}
    .nav-item:hover,.nav-item.active{{color:var(--orange);border-bottom-color:var(--orange);}}
    .container{{max-width:1140px;margin:0 auto;padding:32px 20px;}}
    .markets{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:36px;}}
    @media(max-width:700px){{.markets{{grid-template-columns:repeat(2,1fr);}}}}
    .market-card{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px;text-align:center;}}
    .market-val{{font-size:22px;font-weight:900;}}
    .market-val.up{{color:var(--green);}} .market-val.down{{color:var(--red);}} .market-val.flat{{color:#fff;}}
    .market-label{{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:0.5px;margin-top:4px;}}
    .market-change{{font-size:12px;margin-top:3px;}}
    .market-change.up{{color:var(--green);}} .market-change.down{{color:var(--red);}} .market-change.flat{{color:var(--muted);}}
    .section-label{{font-size:11px;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:16px;display:flex;align-items:center;gap:12px;}}
    .section-label::after{{content:'';flex:1;height:1px;background:var(--border);}}
    .hero-grid{{display:grid;grid-template-columns:1.6fr 1fr;gap:20px;margin-bottom:36px;}}
    @media(max-width:768px){{.hero-grid{{grid-template-columns:1fr;}}}}
    .card{{background:var(--card);border:1px solid var(--border);border-radius:16px;overflow:hidden;cursor:pointer;transition:border-color 0.2s,transform 0.2s;}}
    .card:hover{{border-color:var(--orange);transform:translateY(-2px);}}
    .card-emoji{{height:150px;display:flex;align-items:center;justify-content:center;font-size:72px;background:linear-gradient(135deg,#111,#1a1a1a);}}
    .card-body{{padding:20px;}}
    .badge{{display:inline-block;padding:4px 10px;border-radius:20px;font-size:10px;font-weight:800;letter-spacing:0.5px;text-transform:uppercase;margin-bottom:10px;margin-right:4px;}}
    .b-india{{background:#3D1A0A;color:#FF8C42;}} .b-biz{{background:#0A1A2A;color:#4DB6E0;}}
    .b-sports{{background:#0A2A15;color:#4CAF50;}} .b-tech{{background:#1A0A2A;color:#CE93D8;}}
    .b-life{{background:#2A1A0A;color:#FFB74D;}} .b-breaking{{background:var(--red);color:#fff;}}
    .card-headline{{font-size:20px;font-weight:800;line-height:1.3;margin-bottom:10px;color:#fff;}}
    .card-body-sm .card-headline{{font-size:16px;}}
    .card-text{{font-size:14px;color:#aaa;line-height:1.7;margin-bottom:14px;}}
    .card-body-sm .card-text{{font-size:13px;}}
    .why-box{{background:#111;border-left:3px solid var(--orange);border-radius:0 8px 8px 0;padding:10px 14px;font-size:13px;color:#ccc;line-height:1.5;}}
    .why-box strong{{color:var(--orange);}}
    .card-footer{{display:flex;justify-content:space-between;align-items:center;margin-top:14px;padding-top:12px;border-top:1px solid var(--border);flex-wrap:wrap;gap:8px;}}
    .read-time{{font-size:11px;color:var(--muted);}}
    .read-more{{font-size:12px;font-weight:700;color:var(--orange);text-decoration:none;}}
    .sidebar-stack{{display:flex;flex-direction:column;gap:16px;}}
    .side-card{{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:16px;cursor:pointer;transition:border-color 0.2s;display:flex;gap:14px;align-items:flex-start;}}
    .side-card:hover{{border-color:var(--orange);}}
    .side-emoji{{font-size:32px;flex-shrink:0;width:50px;height:50px;display:flex;align-items:center;justify-content:center;border-radius:10px;background:#111;}}
    .side-headline{{font-size:14px;font-weight:700;line-height:1.35;margin-bottom:6px;color:#fff;}}
    .side-text{{font-size:12px;color:var(--muted);line-height:1.5;}}
    .grid-3{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-bottom:36px;}}
    @media(max-width:900px){{.grid-3{{grid-template-columns:1fr 1fr;}}}}
    @media(max-width:600px){{.grid-3{{grid-template-columns:1fr;}}}}
    .card-sm .card-emoji{{height:100px;font-size:48px;}}
    .subscribe{{background:linear-gradient(135deg,#FF5722,#FF8C42);border-radius:20px;padding:40px 32px;text-align:center;margin-bottom:36px;}}
    .subscribe h2{{font-size:28px;font-weight:900;color:#fff;margin-bottom:8px;}}
    .subscribe p{{color:rgba(255,255,255,0.85);font-size:15px;margin-bottom:24px;}}
    .sub-form{{display:flex;gap:10px;max-width:440px;margin:0 auto;flex-wrap:wrap;justify-content:center;}}
    .sub-form input{{flex:1;min-width:200px;padding:14px 20px;border-radius:30px;border:none;font-size:14px;outline:none;}}
    .sub-form button{{background:#0D0D0D;color:#fff;border:none;padding:14px 24px;border-radius:30px;font-size:14px;font-weight:800;cursor:pointer;}}
    footer{{background:#111;border-top:1px solid var(--border);padding:40px 24px;text-align:center;}}
    .footer-logo{{font-size:36px;font-weight:900;color:#fff;letter-spacing:-2px;margin-bottom:8px;}}
    .footer-logo span{{color:var(--orange);}}
    .footer-links{{display:flex;justify-content:center;gap:24px;margin:16px 0;flex-wrap:wrap;}}
    .footer-links a{{color:var(--muted);font-size:13px;text-decoration:none;}}
    .footer-links a:hover{{color:var(--orange);}}
    .footer-text{{color:var(--muted);font-size:13px;line-height:1.8;}}
    .updated-pill{{display:inline-flex;align-items:center;gap:6px;background:#111;border:1px solid var(--border);border-radius:20px;padding:6px 14px;font-size:12px;color:var(--muted);margin-bottom:24px;}}
    .pulse{{width:8px;height:8px;background:var(--green);border-radius:50%;animation:pulse 1.5s infinite;flex-shrink:0;}}
    @keyframes pulse{{0%,100%{{opacity:1;}}50%{{opacity:0.3;}}}}
  </style>
</head>
<body>

<div class="topbar">
  <span class="topbar-date">‚òÄÔ∏è {date_str}</span>
  <div class="topbar-links">
    <a href="#">About</a>
    <a href="#">Subscribe</a>
    <a href="#">Archive</a>
  </div>
</div>

<header>
  <div class="logo">d<span>u</span>h</div>
  <div class="tagline">News so simple, you'll go duh</div>
  <div class="header-sub">India's most honest, jargon-free daily news</div>
</header>

<div class="ticker">
  <div class="ticker-inner">
    {ticker_html}
  </div>
</div>

<nav>
  <div class="nav-inner">
    <a class="nav-item active" href="#">üè† Today</a>
    <a class="nav-item" href="#">üáÆüá≥ India</a>
    <a class="nav-item" href="#">üåç World</a>
    <a class="nav-item" href="#">üíº Business</a>
    <a class="nav-item" href="#">üèè Sports</a>
    <a class="nav-item" href="#">üì± Tech</a>
    <a class="nav-item" href="#">üé¨ Entertainment</a>
  </div>
</nav>

<div class="container">

  <div class="updated-pill">
    <div class="pulse"></div>
    <span>Updated today at {time_str} IST &nbsp;¬∑&nbsp; {total} stories</span>
  </div>

  <div class="section-label">üî• Today's biggest story</div>
  <div class="hero-grid">
    {hero_html}
    <div class="sidebar-stack">
      {side_html}
    </div>
  </div>

  <div class="section-label">üì∞ More stories today</div>
  <div class="grid-3">
    {grid_html}
  </div>

  <div class="subscribe">
    <h2>‚òÄÔ∏è Get DUH in your inbox every morning</h2>
    <p>Join thousands of Indians who start their day with news that actually makes sense. Free, always.</p>
    <div class="sub-form">
      <input type="email" placeholder="your@email.com"/>
      <button>Subscribe Free ‚Üí</button>
    </div>
  </div>

</div>

<footer>
  <div class="footer-logo">d<span>u</span>h</div>
  <div class="footer-links">
    <a href="#">Home</a>
    <a href="#">About</a>
    <a href="#">Subscribe</a>
    <a href="#">Contact</a>
  </div>
  <div class="footer-text">
    News so simple, you'll go duh ¬∑ Updated daily at 7am IST ¬∑ duh.co.in<br/><br/>
    <span style="font-size:11px;color:#444;">Not financial advice. Not legal advice. Just news, made human.</span>
  </div>
</footer>

</body>
</html>'''


def main():
    print("Fetching news from RSS feeds...")
    articles = {}
    for cat in ['general', 'business', 'sports', 'technology', 'entertainment']:
        articles[cat] = fetch(cat, size=5)
        print(f"  {cat}: {len(articles[cat])} articles fetched")

    total = sum(len(v) for v in articles.values())
    if total == 0:
        print("ERROR: No articles fetched from any feed. Check internet connectivity.")
        exit(1)

    print("Generating HTML...")
    html = generate_html(articles)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Done! index.html updated with {total} stories at {datetime.now(IST).strftime('%H:%M IST')}")


if __name__ == '__main__':
    main()

