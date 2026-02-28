import feedparser
import os
from datetime import datetime
import pytz
import re

IST = pytz.timezone('Asia/Kolkata')

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

CATEGORY_LABELS = {
    'general':       'India',
    'business':      'Business',
    'sports':        'Sports',
    'technology':    'Technology',
    'entertainment': 'Entertainment',
}


def fetch(category, size=6):
    articles = []
    for url in RSS_FEEDS.get(category, []):
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:size]:
                title = entry.get('title', '').strip()
                summary = entry.get('summary', '') or entry.get('description', '')
                summary = re.sub('<[^<]+?>', '', summary).strip()
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
                break
        except Exception as e:
            print(f"  Warning: Could not fetch {url}: {e}")
            continue
    return articles[:size]


def clean(text, max_words=35):
    if not text:
        return ''
    words = str(text).split()
    if len(words) > max_words:
        return ' '.join(words[:max_words]) + '...'
    return ' '.join(words)


def make_article_card(article, category):
    title = (article.get('title', '') or '').split(' - ')[0].strip()
    desc = clean(article.get('description', '') or '', 30)
    url = article.get('url', '#') or '#'
    label = CATEGORY_LABELS.get(category, category.title())
    return f'''
        <article class="article-card">
          <p class="article-category">{label}</p>
          <h3 class="article-title"><a href="{url}" target="_blank">{title}</a></h3>
          <p class="article-excerpt">{desc}</p>
          <a href="{url}" target="_blank" class="read-more">Read full article ¬ª</a>
        </article>'''


def make_featured(article, category):
    title = (article.get('title', '') or '').split(' - ')[0].strip()
    desc = clean(article.get('description', '') or '', 50)
    url = article.get('url', '#') or '#'
    source = article.get('source', '')
    label = CATEGORY_LABELS.get(category, category.title())
    return f'''
        <article class="featured-article">
          <p class="article-category">{label}</p>
          <h2 class="featured-title"><a href="{url}" target="_blank">{title}</a></h2>
          <p class="featured-excerpt">{desc}</p>
          <p class="featured-source">{source}</p>
          <a href="{url}" target="_blank" class="read-more">Read full article ¬ª</a>
        </article>'''


def generate_html(articles_by_cat):
    now = datetime.now(IST)
    date_str = now.strftime('%A, %B %d, %Y')
    time_str = now.strftime('%I:%M %p IST')

    general = articles_by_cat.get('general', [])
    business = articles_by_cat.get('business', [])
    sports = articles_by_cat.get('sports', [])
    technology = articles_by_cat.get('technology', [])
    entertainment = articles_by_cat.get('entertainment', [])

    # Featured story
    featured_html = make_featured(general[0], 'general') if general else ''

    # Top 3 grid
    top_grid = []
    if len(general) > 1: top_grid.append((general[1], 'general'))
    if business: top_grid.append((business[0], 'business'))
    if sports: top_grid.append((sports[0], 'sports'))
    top_grid_html = ''.join(make_article_card(a, c) for a, c in top_grid[:3])

    # Business section
    biz_html = ''.join(make_article_card(a, 'business') for a in business[1:4])

    # India section
    india_html = ''.join(make_article_card(a, 'general') for a in general[2:5])

    # Sports & Tech & Entertainment
    other_html = ''
    for a in sports[1:2]: other_html += make_article_card(a, 'sports')
    for a in technology[:2]: other_html += make_article_card(a, 'technology')
    for a in entertainment[:1]: other_html += make_article_card(a, 'entertainment')

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <meta name="description" content="DUH ‚Äî India's news in plain English. Simple, clear, no jargon."/>
  <title>DUH ‚Äî India's Simplest News</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700&family=Source+Serif+4:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Inter:wght@300;400;500;600&display=swap');

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --navy: #1a2744;
      --navy-light: #2d4070;
      --accent: #8b1a1a;
      --text: #1a1a1a;
      --muted: #666;
      --light: #f5f3ef;
      --border: #d4cfc7;
      --white: #ffffff;
    }}

    body {{
      background: var(--white);
      color: var(--text);
      font-family: 'Source Serif 4', Georgia, serif;
      font-size: 16px;
      line-height: 1.6;
    }}

    a {{ color: inherit; text-decoration: none; }}
    a:hover {{ color: var(--accent); }}

    /* ‚îÄ‚îÄ TOP BAR ‚îÄ‚îÄ */
    .topbar {{
      background: var(--navy);
      color: rgba(255,255,255,0.7);
      font-family: 'Inter', sans-serif;
      font-size: 11px;
      letter-spacing: 0.5px;
      padding: 7px 40px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .topbar a {{ color: rgba(255,255,255,0.7); }}
    .topbar a:hover {{ color: white; }}
    .topbar-links {{ display: flex; gap: 20px; }}

    /* ‚îÄ‚îÄ MASTHEAD ‚îÄ‚îÄ */
    .masthead {{
      text-align: center;
      padding: 40px 40px 24px;
      border-bottom: 3px double var(--navy);
    }}
    .masthead-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      font-family: 'Inter', sans-serif;
      font-size: 12px;
      color: var(--muted);
    }}
    .logo {{
      font-family: 'Playfair Display', Georgia, serif;
      font-size: 80px;
      font-weight: 900;
      color: var(--navy);
      letter-spacing: 8px;
      text-transform: uppercase;
      line-height: 1;
    }}
    .tagline {{
      font-family: 'Source Serif 4', Georgia, serif;
      font-style: italic;
      font-size: 15px;
      color: var(--muted);
      margin-top: 8px;
      letter-spacing: 1px;
    }}
    .masthead-rule {{
      border: none;
      border-top: 1px solid var(--border);
      margin: 16px 0 0;
    }}

    /* ‚îÄ‚îÄ NAV ‚îÄ‚îÄ */
    nav {{
      border-bottom: 1px solid var(--border);
      background: var(--white);
      position: sticky;
      top: 0;
      z-index: 100;
    }}
    .nav-inner {{
      max-width: 1200px;
      margin: 0 auto;
      display: flex;
      justify-content: center;
      overflow-x: auto;
      scrollbar-width: none;
      padding: 0 40px;
    }}
    .nav-inner::-webkit-scrollbar {{ display: none; }}
    .nav-item {{
      padding: 12px 18px;
      font-family: 'Inter', sans-serif;
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      color: var(--navy);
      white-space: nowrap;
      border-bottom: 2px solid transparent;
      transition: all 0.2s;
    }}
    .nav-item:hover, .nav-item.active {{
      color: var(--accent);
      border-bottom-color: var(--accent);
    }}

    /* ‚îÄ‚îÄ MAIN LAYOUT ‚îÄ‚îÄ */
    .container {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 40px;
    }}

    /* ‚îÄ‚îÄ EDITION BAR ‚îÄ‚îÄ */
    .edition-bar {{
      text-align: center;
      padding: 12px;
      font-family: 'Inter', sans-serif;
      font-size: 11px;
      letter-spacing: 1px;
      color: var(--muted);
      border-bottom: 1px solid var(--border);
      text-transform: uppercase;
    }}

    /* ‚îÄ‚îÄ SECTION HEADING ‚îÄ‚îÄ */
    .section-heading {{
      font-family: 'Inter', sans-serif;
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 2.5px;
      text-transform: uppercase;
      color: var(--accent);
      padding: 28px 0 12px;
      border-bottom: 2px solid var(--navy);
      margin-bottom: 28px;
      display: flex;
      justify-content: space-between;
      align-items: baseline;
    }}

    /* ‚îÄ‚îÄ FEATURED STORY ‚îÄ‚îÄ */
    .featured-wrap {{
      padding: 40px 0;
      border-bottom: 1px solid var(--border);
      text-align: center;
      max-width: 780px;
      margin: 0 auto;
    }}
    .featured-article .article-category {{
      font-family: 'Inter', sans-serif;
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: var(--accent);
      margin-bottom: 16px;
    }}
    .featured-title {{
      font-family: 'Playfair Display', Georgia, serif;
      font-size: 42px;
      font-weight: 700;
      font-style: italic;
      line-height: 1.2;
      color: var(--navy);
      margin-bottom: 18px;
    }}
    .featured-title a:hover {{ color: var(--accent); }}
    .featured-excerpt {{
      font-size: 17px;
      line-height: 1.8;
      color: #444;
      margin-bottom: 16px;
      font-style: italic;
    }}
    .featured-source {{
      font-family: 'Inter', sans-serif;
      font-size: 11px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 16px;
    }}

    /* ‚îÄ‚îÄ READ MORE ‚îÄ‚îÄ */
    .read-more {{
      font-family: 'Inter', sans-serif;
      font-size: 12px;
      font-weight: 500;
      color: var(--navy);
      letter-spacing: 0.5px;
      display: inline-block;
      margin-top: 8px;
    }}
    .read-more:hover {{ color: var(--accent); }}

    /* ‚îÄ‚îÄ 3 COLUMN GRID ‚îÄ‚îÄ */
    .grid-3 {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 0;
      border-bottom: 1px solid var(--border);
      margin-bottom: 40px;
    }}
    @media(max-width: 900px) {{ .grid-3 {{ grid-template-columns: 1fr 1fr; }} }}
    @media(max-width: 600px) {{ .grid-3 {{ grid-template-columns: 1fr; }} }}

    .article-card {{
      padding: 24px 28px;
      border-right: 1px solid var(--border);
    }}
    .article-card:last-child {{ border-right: none; }}

    .article-category {{
      font-family: 'Inter', sans-serif;
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: var(--accent);
      margin-bottom: 10px;
    }}

    .article-title {{
      font-family: 'Playfair Display', Georgia, serif;
      font-size: 19px;
      font-weight: 700;
      font-style: italic;
      line-height: 1.35;
      color: var(--navy);
      margin-bottom: 10px;
    }}
    .article-title a:hover {{ color: var(--accent); }}

    .article-excerpt {{
      font-size: 13.5px;
      color: #555;
      line-height: 1.7;
      margin-bottom: 12px;
    }}

    /* ‚îÄ‚îÄ 2 COLUMN LAYOUT ‚îÄ‚îÄ */
    .two-col {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 40px;
      padding: 0 0 40px;
      border-bottom: 1px solid var(--border);
      margin-bottom: 40px;
    }}
    @media(max-width: 700px) {{ .two-col {{ grid-template-columns: 1fr; }} }}

    .col-section {{ }}

    .col-article {{
      padding: 16px 0;
      border-bottom: 1px solid var(--border);
    }}
    .col-article:last-child {{ border-bottom: none; }}

    /* ‚îÄ‚îÄ SUBSCRIBE ‚îÄ‚îÄ */
    .subscribe-wrap {{
      background: var(--light);
      border-top: 2px solid var(--navy);
      border-bottom: 2px solid var(--navy);
      padding: 48px 40px;
      text-align: center;
      margin-bottom: 40px;
    }}
    .subscribe-wrap h2 {{
      font-family: 'Playfair Display', Georgia, serif;
      font-size: 30px;
      font-weight: 700;
      font-style: italic;
      color: var(--navy);
      margin-bottom: 10px;
    }}
    .subscribe-wrap p {{
      font-size: 15px;
      color: var(--muted);
      margin-bottom: 24px;
      font-style: italic;
    }}
    .sub-form {{
      display: flex;
      gap: 0;
      max-width: 420px;
      margin: 0 auto;
      border: 1px solid var(--navy);
    }}
    .sub-form input {{
      flex: 1;
      padding: 12px 16px;
      border: none;
      font-size: 14px;
      outline: none;
      font-family: 'Inter', sans-serif;
      background: white;
    }}
    .sub-form button {{
      background: var(--navy);
      color: white;
      border: none;
      padding: 12px 24px;
      font-size: 12px;
      font-weight: 600;
      letter-spacing: 1px;
      text-transform: uppercase;
      cursor: pointer;
      font-family: 'Inter', sans-serif;
      white-space: nowrap;
    }}
    .sub-form button:hover {{ background: var(--accent); }}

    /* ‚îÄ‚îÄ FOOTER ‚îÄ‚îÄ */
    footer {{
      background: var(--navy);
      color: rgba(255,255,255,0.6);
      padding: 40px;
      text-align: center;
    }}
    .footer-logo {{
      font-family: 'Playfair Display', Georgia, serif;
      font-size: 32px;
      font-weight: 900;
      letter-spacing: 6px;
      color: white;
      margin-bottom: 12px;
    }}
    .footer-links {{
      display: flex;
      justify-content: center;
      gap: 24px;
      margin: 16px 0;
      flex-wrap: wrap;
    }}
    .footer-links a {{
      color: rgba(255,255,255,0.6);
      font-family: 'Inter', sans-serif;
      font-size: 11px;
      letter-spacing: 1px;
      text-transform: uppercase;
    }}
    .footer-links a:hover {{ color: white; }}
    .footer-text {{
      font-size: 12px;
      font-family: 'Inter', sans-serif;
      line-height: 1.8;
    }}
  </style>
</head>
<body>

<!-- TOP BAR -->
<div class="topbar">
  <span>‚òÄÔ∏è {date_str}</span>
  <div class="topbar-links">
    <a href="#">About</a>
    <a href="#">Subscribe</a>
    <a href="#">Archive</a>
  </div>
</div>

<!-- MASTHEAD -->
<div class="masthead">
  <div class="masthead-top">
    <span style="font-style:italic">News so simple, you'll go duh</span>
    <span>Updated daily at 7am IST</span>
  </div>
  <div class="logo">DUH</div>
  <div class="tagline">India's news in plain English ‚Äî no jargon, no drama</div>
  <hr class="masthead-rule"/>
</div>

<!-- NAV -->
<nav>
  <div class="nav-inner">
    <a class="nav-item active" href="#">Today</a>
    <a class="nav-item" href="#">India</a>
    <a class="nav-item" href="#">World</a>
    <a class="nav-item" href="#">Business</a>
    <a class="nav-item" href="#">Sports</a>
    <a class="nav-item" href="#">Technology</a>
    <a class="nav-item" href="#">Entertainment</a>
  </div>
</nav>

<!-- EDITION BAR -->
<div class="edition-bar">
  Edition of {date_str} &nbsp;¬∑&nbsp; Updated at {time_str}
</div>

<!-- MAIN -->
<div class="container">

  <!-- FEATURED -->
  <div class="featured-wrap">
    {featured_html}
  </div>

  <!-- TOP 3 GRID -->
  <div class="section-heading">
    <span>Top Stories</span>
    <span style="font-style:italic;font-family:'Source Serif 4',serif;font-size:11px;font-weight:300;letter-spacing:0;">Today's most important news</span>
  </div>
  <div class="grid-3">
    {top_grid_html}
  </div>

  <!-- TWO COLUMN: INDIA + BUSINESS -->
  <div class="two-col">
    <div class="col-section">
      <div class="section-heading">India</div>
      {india_html}
    </div>
    <div class="col-section">
      <div class="section-heading">Business</div>
      {biz_html}
    </div>
  </div>

  <!-- BOTTOM GRID: SPORTS / TECH / ENTERTAINMENT -->
  <div class="section-heading">More Stories</div>
  <div class="grid-3" style="margin-bottom:40px;">
    {other_html}
  </div>

</div>

<!-- SUBSCRIBE -->
<div class="subscribe-wrap">
  <h2>Start your morning with DUH</h2>
  <p>India's news, explained simply ‚Äî in your inbox every day at 7am. Free, always.</p>
  <div class="sub-form">
    <input type="email" placeholder="your@email.com"/>
    <button>Subscribe</button>
  </div>
</div>

<!-- FOOTER -->
<footer>
  <div class="footer-logo">DUH</div>
  <div class="footer-links">
    <a href="#">Home</a>
    <a href="#">About</a>
    <a href="#">Archive</a>
    <a href="#">Subscribe</a>
    <a href="#">Contact</a>
  </div>
  <div class="footer-text">
    News so simple, you'll go duh &nbsp;¬∑&nbsp; duh.co.in<br/>
    Not financial or legal advice. Just news, made human.
  </div>
</footer>

</body>
</html>'''


def main():
    print("Fetching news from RSS feeds...")
    articles = {}
    for cat in ['general', 'business', 'sports', 'technology', 'entertainment']:
        articles[cat] = fetch(cat, size=6)
        print(f"  {cat}: {len(articles[cat])} articles fetched")

    total = sum(len(v) for v in articles.values())
    if total == 0:
        print("ERROR: No articles fetched. Check internet connectivity.")
        exit(1)

    print("Generating HTML...")
    html = generate_html(articles)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Done! index.html updated with {total} stories at {datetime.now(IST).strftime('%H:%M IST')}")


if __name__ == '__main__':
    main()

