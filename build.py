"""Build the public site and durable Markdown posts without a server-side editor."""
from pathlib import Path
from html import escape
from datetime import date, datetime, timedelta, timezone
import json
import hashlib
import re
from urllib.parse import urlsplit
from i18n import story_photo_url, story_thumbnail

ROOT = Path(__file__).resolve().parent
ORIGIN = 'https://hongdaepizza.com'
CATEGORIES = ('매장 소식', '화덕 이야기', '메뉴', '방문·예약')
SLUG = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')


def parse_post(path):
    text = path.read_text(encoding='utf-8')
    if not text.startswith('---\n') or '\n---\n' not in text[4:]:
        raise ValueError(f'{path.name}: front matter is required')
    front, body = text[4:].split('\n---\n', 1)
    meta = {}
    for line in front.splitlines():
        key, value = line.split(':', 1)
        meta[key.strip()] = json.loads(value.strip())
    slug = path.stem
    validate_post(slug, meta, body)
    return {**meta, 'slug': slug, 'body': body.strip(), 'url': f'/stories/{slug}/'}


def validate_post(slug, meta, body):
    if not SLUG.fullmatch(slug):
        raise ValueError('Use a lowercase slug containing words and hyphens')
    for key in ('title', 'category', 'summary', 'date', 'updated', 'status'):
        if not isinstance(meta.get(key), str) or not meta[key].strip():
            raise ValueError(f'{key} is required')
    if meta['category'] not in CATEGORIES or meta['status'] not in ('published', 'draft'):
        raise ValueError('Unknown category or publication status')
    date.fromisoformat(meta['date'])
    date.fromisoformat(meta['updated'])
    if not isinstance(body, str) or not body.strip():
        raise ValueError('Post body is required')


def save_post(folder, slug, payload, updated):
    if not SLUG.fullmatch(slug):
        raise ValueError('Unsafe or invalid slug')
    date.fromisoformat(updated)
    folder = Path(folder).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / (slug + '.md')
    existing = parse_post(target) if target.exists() else {}
    body = payload.get('body', '')
    meta = {key: payload.get(key, existing.get(key, ''))
            for key in ('title', 'category', 'summary')}
    meta.update(date=existing.get('date', updated), updated=updated,
                status=payload.get('status', existing.get('status', 'draft')),
                order=payload.get('order', existing.get('order', 100)))
    validate_post(slug, meta, body)
    document = '---\n' + '\n'.join(
        f'{key}: {json.dumps(value, ensure_ascii=False)}' for key, value in meta.items()
    ) + '\n---\n\n' + body.strip() + '\n'
    pending = target.with_suffix('.md.tmp')
    pending.write_text(document, encoding='utf-8')
    pending.replace(target)
    return target


def read_posts(folder):
    posts = [parse_post(path) for path in sorted(Path(folder).glob('*.md'))]
    return sorted((p for p in posts if p['status'] == 'published'),
                  key=lambda p: (-date.fromisoformat(p['date']).toordinal(), p.get('order', 100), p['slug']))


def render_markdown(text):
    """Render saved text, safe links and local photos; escape arbitrary HTML."""
    def inline(value):
        parts, cursor = [], 0
        for match in re.finditer(r'\[([^\]\n]+)\]\(([^\s)]+)\)', value):
            parts.append(escape(value[cursor:match.start()]))
            label, url = match.groups()
            if (url.startswith('/') and not url.startswith('//')) or re.match(r'^https://[A-Za-z0-9.-]+(?:[/:?#]|$)', url):
                parts.append(f'<a href="{escape(url, quote=True)}">{escape(label)}</a>')
            else:
                parts.append(escape(match.group()))
            cursor = match.end()
        parts.append(escape(value[cursor:]))
        return ''.join(parts)

    output, paragraph, listing = [], [], []
    def flush():
        if paragraph:
            output.append('<p>' + '<br>'.join(inline(line) for line in paragraph) + '</p>')
            paragraph.clear()
        if listing:
            output.append('<ul>' + ''.join('<li>' + inline(line) + '</li>' for line in listing) + '</ul>')
            listing.clear()
    for line in text.splitlines() + ['']:
        photo = re.fullmatch(r'!\[([^\]\n]+)\]\((/assets/[A-Za-z0-9_-]+\.(?:webp|jpg|png))\)', line)
        if photo:
            flush()
            caption, url = photo.groups()
            output.append(f'<figure class="article-photo"><img src="{url}" alt="{escape(caption, quote=True)}" loading="lazy"><figcaption>{escape(caption)}</figcaption></figure>')
        elif line.startswith('## '):
            flush()
            output.append('<h2>' + escape(line[3:]) + '</h2>')
        elif line.startswith('- '):
            if paragraph:
                flush()
            listing.append(line[2:])
        elif not line.strip():
            flush()
        else:
            if listing:
                flush()
            paragraph.append(line)
    return ''.join(output)


def card(post):
    return (f'<a class="story-card" href="{post["url"]}">'
            f'{story_thumbnail(post["slug"])}'
            f'<span class="category">{escape(post["category"])}</span>'
            f'<h3>{escape(post["title"])}</h3><p>{escape(post["summary"])}</p></a>')


def post_json(posts):
    keys = ('slug', 'title', 'category', 'summary', 'url', 'date', 'updated')
    return json.dumps([{**{k: post[k] for k in keys}, "thumbnail": story_photo_url(post["slug"]), "preview": "/assets/rain-story-loop.mp4" if post["slug"] == "pizza-pasta-for-two" else None} for post in posts], ensure_ascii=False).replace('<', '\\u003c')


def metadata(title, description, path, schema):
    preview = 'drinks.webp' if path == '/stories/pizza-pasta-for-two/' else 'table.webp'
    return (f'<meta name="description" content="{escape(description, quote=True)}">'
            f'<link rel="canonical" href="{ORIGIN}{path}">'
            f'<meta property="og:title" content="{escape(title, quote=True)}">'
            f'<meta property="og:description" content="{escape(description, quote=True)}">'
            f'<meta property="og:url" content="{ORIGIN}{path}">'
            '<meta property="og:type" content="website">'
            f'<meta property="og:image" content="{ORIGIN}/assets/{preview}">'
            '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c') + '</script>')


def normalize_naver_links(html, destination):
    def replace(match):
        host = (urlsplit(match.group(1)).hostname or '').lower()
        if host == 'naver.me' or host == 'naver.com' or host.endswith('.naver.com'):
            return 'href="' + escape(destination, quote=True) + '"'
        return match.group(0)
    return re.sub(r'href="(https?://[^\"]+)"', replace, html)


def page_shell(title, description, path, inner, nav, footer, schema, script='', naver_url=None):
    html = ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{escape(title)}</title><link rel="stylesheet" href="/style.css">'
            + metadata(title, description, path, schema) + '</head><body id="top">'
            '<a class="skip" href="#main">본문 바로가기</a>' + nav + '<main id="main">'
            + inner + '</main>' + footer + script + '</body></html>')
    return normalize_naver_links(html, naver_url) if naver_url else html


def build(root=ROOT):
    root = Path(root)
    dist = root / 'dist'
    content = json.loads((root / 'content.json').read_text(encoding='utf-8'))
    naver_url = content.get('naver_place', content['booking'])
    posts = read_posts(root / 'content/posts')
    page = (root / 'template.html').read_text(encoding='utf-8')
    items = []
    for item in content['menu']:
        items.append('<article class="menu-card">'
            f'<img src="assets/{escape(item["image"])}" alt="{escape(item["name"])} 실제 메뉴 사진" width="900" height="900">'
            f'<span class="menu-type">{escape(item["type"])}</span><h3>{escape(item["name"])}</h3>'
            f'<p class="menu-lead">{escape(item["lead"])}</p><p class="menu-body">{escape(item["body"])}</p>'
            '</article>')
    page = page.replace('<!-- MENU_ITEMS -->', ''.join(items))
    # Korean year count since opening in 2012 (2026 = 15th year), using Korea time.
    page = page.replace('<!-- YEARS -->', str(datetime.now(timezone(timedelta(hours=9))).year - 2012 + 1))
    page = page.replace('data-booking target=', f'data-booking href="{escape(content["booking"], quote=True)}" target=')
    page = page.replace('<!-- STORY_ITEMS -->', ''.join(card(p) for p in posts[:3]))
    page = page.replace('<!-- POSTS_JSON -->', post_json(posts))
    restaurant = {'@context': 'https://schema.org', '@type': 'Restaurant',
        '@id': ORIGIN + '/#restaurant', 'name': '홍대화덕피자', 'url': ORIGIN + '/', 'telephone': '0507-1349-2285',
        'servesCuisine': ['화덕피자', '파스타'],
        'address': {'@type': 'PostalAddress', 'streetAddress': '독막로7길 5, 1층',
                    'addressLocality': '마포구', 'addressRegion': '서울', 'addressCountry': 'KR'},
        'sameAs': [naver_url],
        'hasMenu': naver_url}
    page = re.sub(r'<meta name="description"[^>]*>', '', page)
    page = page.replace('</head>', metadata('홍대화덕피자 | 홍대·합정·상수 화덕피자와 파스타', '홍대·합정·상수의 화덕피자와 파스타. 합정역·상수역 도보 약 5분. 메뉴와 공간을 살펴보고 네이버 플레이스에서 예약하세요.', '/', restaurant) + '</head>')
    page = normalize_naver_links(page, naver_url)
    (dist / 'index.html').write_text(page, encoding='utf-8')
    nav = re.search(r'<header\b.*?</header>', page, re.S).group()
    footer = re.search(r'<footer\b.*?</footer>', page, re.S).group()
    for element in ('#top', '#menu', '#oven', '#space', '#visit'):
        nav = nav.replace(f'href="{element}"', f'href="/{element}"')
    footer = footer.replace('href="#top"', 'href="/#top"')
    stories = dist / 'stories'
    stories.mkdir(exist_ok=True)
    # Remove only generator-owned HTML files, so a saved draft cannot leave a stale public article.
    for generated in stories.glob('*/index.html'):
        generated.unlink()
        if not any(generated.parent.iterdir()):
            generated.parent.rmdir()
    filters = '<div class="filters" aria-label="글 분류">' + ''.join(
        f'<button type="button" data-filter="{category}" aria-pressed="{str(category == "전체").lower()}"'
        + (' class="active"' if category == '전체' else '') + f'>{category}</button>'
        for category in ('전체',) + CATEGORIES) + '</div>'
    archive = ('<section class="wrap section archive"><p class="eyebrow">STORIES</p>'
               '<h1>홍대화덕피자 이야기</h1><p class="archive-intro">메뉴와 방문, 예약이 궁금할 때.</p>'
               + filters + '<div class="story-grid" id="story-grid" data-all="true">'
               + ''.join(card(p) for p in posts) + '</div><p class="sr-only" id="story-status" aria-live="polite"></p></section>')
    archive_script = f'<script type="application/json" id="posts-data">{post_json(posts)}</script><script src="/app.js"></script>'
    (stories / 'index.html').write_text(page_shell('홍대화덕피자 이야기 | 메뉴와 방문 가이드',
        '홍대화덕피자의 메뉴, 화덕, 방문과 예약 질문을 읽어보세요.', '/stories/', archive, nav, footer,
        {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': '홍대화덕피자 이야기', 'url': ORIGIN + '/stories/'}, archive_script, naver_url=naver_url), encoding='utf-8')
    for post in posts:
        target = stories / post['slug']
        target.mkdir(exist_ok=True)
        inner = ('<article class="article wrap"><a class="plain-link" href="/stories/">← 이야기 전체 보기</a>'
                 f'<p class="eyebrow article-category">{escape(post["category"])}</p><h1>{escape(post["title"])}</h1>'
                 f'<p class="article-meta">홍대화덕피자 · 작성 <time datetime="{post["date"]}">{post["date"]}</time>'
                 f' · 수정 <time datetime="{post["updated"]}">{post["updated"]}</time></p>'
                 f'<p class="article-summary">{escape(post["summary"])}</p>'
                 '<div class="article-body">' + render_markdown(post['body']) + '</div>'
                 '<div class="article-actions"><a class="pill red" href="' + escape(content['booking'], quote=True)
                 + '" target="_blank" rel="noopener noreferrer">네이버 예약하기 ↗</a>'
                 '<a class="pill outline" href="' + escape(naver_url, quote=True)
                 + '" target="_blank" rel="noopener noreferrer">네이버 메뉴 보기</a></div></article>')
        schema = {'@context': 'https://schema.org', '@type': 'BlogPosting',
                  'headline': post['title'], 'description': post['summary'],
                  'datePublished': post['date'], 'dateModified': post['updated'],
                  'author': {'@type': 'Organization', 'name': '홍대화덕피자'},
                  'mainEntityOfPage': ORIGIN + post['url']}
        (target / 'index.html').write_text(page_shell(post['title'] + ' | 홍대화덕피자', post['summary'],
            post['url'], inner, nav, footer, schema, naver_url=naver_url), encoding='utf-8')
    from i18n import build_locales
    localized_urls = build_locales(root, posts, restaurant)
    from privacy import build_privacy
    build_privacy(root, dist, page_shell, nav, footer, restaurant)
    from analytics import integrate_analytics
    integrate_analytics(dist)
    # A changed stylesheet/script gets a new URL so returning visitors do not
    # combine new markup with an old cached layout or preview controller.
    revisions = {name: hashlib.sha256((dist / name).read_bytes()).hexdigest()[:12]
                 for name in ('style.css', 'app.js', 'analytics.js') if (dist / name).exists()}
    for html_file in dist.rglob('*.html'):
        html = html_file.read_text(encoding='utf-8')
        for name, revision in revisions.items():
            html = re.sub(r'((?:href|src)=")(/?' + re.escape(name) + r')(?:\?[^"<>]*)?"',
                          lambda m: m.group(1) + m.group(2) + '?v=' + revision + '"', html)
        html_file.write_text(html, encoding='utf-8')
    urls = [('/', ''), ('/stories/', '')] + [(post['url'], post['updated']) for post in posts] + localized_urls
    sitemap = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    sitemap += ''.join('<url><loc>' + escape(ORIGIN + url) + '</loc>' +
                       (f'<lastmod>{modified}</lastmod>' if modified else '') + '</url>' for url, modified in urls)
    (dist / 'sitemap.xml').write_text(sitemap + '</urlset>', encoding='utf-8')
    (dist / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: ' + ORIGIN + '/sitemap.xml\n', encoding='utf-8')
    print(f'Built homepage, post archive and {len(posts)} published articles from saved Markdown.')
    return posts


if __name__ == '__main__':
    build()
