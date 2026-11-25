"""Validate the generated public language routes, metadata and owner price policy."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote,urljoin
import re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];DIST=ROOT/'dist';ORIGIN='https://hongdaepizza.com'
class Page(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.canonical=[];self.alternates={};self.h1=0;self.ids=set();self.lang=None;self.money=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag in ('a','area') and 'href' in a:
   href=a['href']
   target=urlsplit(urljoin(ORIGIN+'/',href))
   is_internal=target.scheme=='https' and target.netloc==urlsplit(ORIGIN).netloc
   assert is_internal or href=='https://naver.me/xtgp91Fv',('invalid customer link',href)
  if 'id' in a:assert a['id'] not in self.ids,('duplicate id',a['id']);self.ids.add(a['id'])
  if tag=='h1':self.h1+=1
  if tag=='html':self.lang=a.get('lang')
  if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a['href'])
  if tag=='link' and a.get('rel')=='alternate':self.alternates[a['hreflang']]=a['href']
  for key in ['href','src','poster','data-src']:
   if key in a:self.links.append(a[key])
  if tag=='img':assert 'alt' in a,a
 def handle_data(self,data):
  if re.search(r'\d[\d,.]*\s*(?:원|만원|KRW|USD|EUR|JPY|CNY)|[$€¥₩]\s*\d',data,re.I):self.money.append(data)
pages={}
for f in DIST.rglob('*.html'):
 path='/'+f.relative_to(DIST).as_posix().removesuffix('index.html');
 if path.startswith('/es/'):
  legacy=f.read_text(encoding='utf-8');Page().feed(legacy);assert 'noindex,follow' in legacy and 'http-equiv="refresh"' in legacy and ORIGIN+'/en/'+path.removeprefix('/es/') in legacy;continue
 p=Page();p.feed(f.read_text(encoding='utf-8'));assert p.h1==1,(path,'h1',p.h1);assert not p.money,(path,p.money);assert p.canonical==[ORIGIN+path],(path,p.canonical);assert set(p.alternates)=={'ko','en','ja','zh-Hans','x-default'},path;pages[path]=p
for path,p in pages.items():
 for href in p.links:
  full=urlsplit(urljoin(ORIGIN+path,href))
  if full.scheme not in ('http','https') or full.netloc!=urlsplit(ORIGIN).netloc:continue
  dest=unquote(full.path)
  if dest.endswith('/'):
   assert dest in pages,(path,'missing route',dest)
   if full.fragment:assert full.fragment in pages[dest].ids,(path,'missing anchor',href)
  else:assert (DIST/dest.lstrip('/')).is_file(),(path,'missing asset',dest)
 for lang,href in p.alternates.items():
  dest=urlsplit(href).path;assert dest in pages,(path,'missing translation',dest)
  assert ORIGIN+path in pages[dest].alternates.values(),(path,'nonreciprocal locale',dest)
 for href in p.links:
  if 'naver.' in href:assert href=='https://naver.me/xtgp91Fv',(path,href)
locs=[n.text for n in ET.parse(DIST/'sitemap.xml').iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
import sys
sys.path.insert(0, str(ROOT))
from build import read_posts
PRIVACY={'/privacy/','/en/privacy/','/ja/privacy/','/zh/privacy/'}
assert PRIVACY<=set(pages),'privacy notice pages are missing'
for path in PRIVACY:assert 'noindex,follow' in (DIST/path.strip('/')/'index.html').read_text(encoding='utf-8'),path
indexed={p for p in pages if p not in PRIVACY}
expected_pages = 4 * (2 + len(read_posts(ROOT/'content/posts')))
assert len(locs)==len(set(locs))==len(indexed)==expected_pages
assert set(locs)=={ORIGIN+p for p in indexed}
print(f'PASS: {len(pages)} pages, 4 languages, no menu amounts, reciprocal hreflang/canonical, sitemap, anchors, assets and Naver links.')
