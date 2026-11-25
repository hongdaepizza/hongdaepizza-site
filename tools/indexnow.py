"""Notify Naver (and the IndexNow network) about pages changed by a deploy.

Run by .github/workflows/pages.yml after the site is deployed.
Only URLs affected by the pushed commits are sent; unchanged pages are not resubmitted.
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://hongdaepizza.com'
HOST = 'hongdaepizza.com'
LANG_PREFIXES = ['', '/en', '/ja', '/zh']
ENDPOINTS = ['https://searchadvisor.naver.com/indexnow', 'https://api.indexnow.org/indexnow']
# Files whose change alters the text of every page.
SITEWIDE = {'template.html', 'i18n.py', 'build.py', 'content.json',
            'content/locales.json', 'content/guide_sections.json', 'content/translation_sources.json'}


def find_key():
    keys = [p.stem for p in (ROOT / 'dist').glob('*.txt')
            if re.fullmatch(r'[0-9a-f]{32}', p.stem) and p.read_text(encoding='utf-8').strip() == p.stem]
    if len(keys) != 1:
        sys.exit(f'IndexNow key file not found or ambiguous: {keys}')
    return keys[0]


def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.status, response.read().decode('utf-8', 'replace')


def changed_files():
    before, after = os.environ.get('BEFORE', ''), os.environ.get('AFTER', 'HEAD')
    if os.environ.get('EVENT') != 'push' or not before or set(before) == {'0'}:
        return None  # manual run or first push: treat as full change
    try:
        out = subprocess.run(['git', 'diff', '--name-only', before, after], cwd=ROOT,
                             check=True, capture_output=True, text=True).stdout
    except subprocess.CalledProcessError:
        return None
    return [line.strip() for line in out.splitlines() if line.strip()]


def all_lists():
    urls = []
    for prefix in LANG_PREFIXES:
        urls += [ORIGIN + prefix + '/', ORIGIN + prefix + '/stories/']
    return urls


def urls_for(files, sitemap_urls):
    if files is None or any(f in SITEWIDE for f in files):
        return sorted(sitemap_urls)
    urls = set()
    for f in files:
        match = re.fullmatch(r'content/posts/([a-z0-9-]+)\.md', f)
        if match:
            slug = match.group(1)
            urls.update(ORIGIN + prefix + f'/stories/{slug}/' for prefix in LANG_PREFIXES)
            urls.update(all_lists())  # home pages and story lists show post cards
    return sorted(urls)


def submit(key, urls):
    payload = json.dumps({'host': HOST, 'key': key, 'keyLocation': f'{ORIGIN}/{key}.txt',
                          'urlList': urls}).encode('utf-8')
    for endpoint in ENDPOINTS:
        request = urllib.request.Request(endpoint, data=payload, method='POST',
                                         headers={'Content-Type': 'application/json; charset=utf-8'})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                print(f'{endpoint}: HTTP {response.status}')
                if response.status in (200, 202):
                    return True
        except urllib.error.HTTPError as error:
            print(f'{endpoint}: HTTP {error.code} {error.read().decode("utf-8", "replace")[:300]}')
        except urllib.error.URLError as error:
            print(f'{endpoint}: {error.reason}')
    return False


def main():
    key = find_key()
    for attempt in range(10):  # wait until the deployed key file is publicly served
        try:
            status, body = fetch(f'{ORIGIN}/{key}.txt')
            if status == 200 and body.strip() == key:
                break
        except (urllib.error.URLError, TimeoutError):
            pass
        time.sleep(30)
    else:
        sys.exit('Key file is not live yet; nothing submitted.')
    _, sitemap = fetch(f'{ORIGIN}/sitemap.xml')
    sitemap_urls = set(re.findall(r'<loc>([^<]+)</loc>', sitemap))
    files = changed_files()
    urls = urls_for(files, sitemap_urls)
    print('changed files:', 'ALL (first or manual run)' if files is None else files)
    if not urls:
        print('No page content changed; nothing submitted.')
        return
    print(f'Submitting {len(urls)} URL(s):', *urls, sep='\n  ')
    if not submit(key, urls):
        sys.exit('IndexNow submission failed on all endpoints.')


if __name__ == '__main__':
    main()
