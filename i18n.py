"""Generate editable, static language versions and reciprocal language links."""
from pathlib import Path
from html import escape as e
import json,re,hashlib
ORIGIN='https://hongdaepizza.com'
NAVER='https://naver.me/xtgp91Fv'
PRIVACY={'en':'Privacy notice','ja':'プライバシーについて','zh-Hans':'隐私说明'}
LABELS={'ko':'한국어','en':'English','ja':'日本語','zh-Hans':'简体中文'}
PREFIX={'ko':'','en':'/en','ja':'/ja','zh-Hans':'/zh'}
PHOTOS={'christmas-date':'table.webp','cheese-pizza':'pizza.webp','gamberi-crema':'cream.webp','directions':'night.webp','reservation':'interior.webp','pizza-pasta-for-two':'drinks.webp','family-visit':'table.webp','vesuvio-oven':'oven-pizza.webp','blue-ribbon-2027':'night.webp'}

def url(lang,path='/'):
 return PREFIX[lang]+path

def switch(lang,path):
 links=''.join(f'<a href="{url(code,path)}" lang="{code}" hreflang="{code}" aria-label="{label}"'+(' aria-current="page"' if code==lang else '')+f'>{label}</a>' for code,label in LABELS.items())
 return f'<details class="language-menu"><summary aria-label="Language / 언어">🌐 {LABELS[lang]}</summary><div class="language-options">{links}</div></details>'

def alternates(path):
 return ''.join(f'<link rel="alternate" hreflang="{code}" href="{ORIGIN+url(code,path)}">' for code in LABELS)+f'<link rel="alternate" hreflang="x-default" href="{ORIGIN+path}">'

def picture(name,alt,cls=''):
 return f'<img src="/assets/{name}" alt="{e(alt)}" loading="lazy" width="1448" height="1086"'+(f' class="{cls}"' if cls else '')+'>'

def link(text,href=NAVER,cls='pill red'):
 return f'<a class="{cls}" href="{href}"'+(' target="_blank" rel="noopener noreferrer"' if href.startswith('https://') else '')+f'>{e(text)} ↗</a>'

def nav(lang,t,path):
 home=url(lang)
 items=''.join(f'<a href="{home}#{anchor}">{e(label)}</a>' for anchor,label in zip(['menu','oven','space','visit'],t['nav']))
 return f'<header class="header"><a class="brand" href="{home}" aria-label="홍대화덕피자"><img class="brand-logo" src="/assets/hongdae-hwaduk-original-logo.png" alt="홍대화덕피자 Pizzeria" width="1000" height="924"></a><nav>{items}</nav>'+switch(lang,path)+link(t['book'])+'</header>'

def shell(lang,t,path,title,description,body,restaurant):
 canonical=ORIGIN+url(lang,path)
 preview=PHOTOS['pizza-pasta-for-two'] if path == '/stories/pizza-pasta-for-two/' else 'table.webp'
 schema={'@context':'https://schema.org','@graph':[{**restaurant,'@id':ORIGIN+'/#restaurant','url':ORIGIN+url(lang)},{'@type':'WebPage','@id':canonical,'url':canonical,'inLanguage':lang,'name':title,'about':{'@id':ORIGIN+'/#restaurant'}}]}
 return '<!doctype html><html lang="'+lang+'"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'+f'<title>{e(title)}</title><meta name="description" content="{e(description,quote=True)}"><link rel="canonical" href="{canonical}">'+alternates(path)+f'<meta property="og:title" content="{e(title,quote=True)}"><meta property="og:description" content="{e(description,quote=True)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{ORIGIN}/assets/{preview}"><meta property="og:type" content="website"><link rel="stylesheet" href="/style.css"><script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False)+'</script></head><body id="top" class="localized"><a class="skip" href="#main">'+e(t['skip'])+'</a>'+nav(lang,t,path)+'<main id="main">'+body+'</main><footer class="footer"><div class="wrap"><a href="'+url(lang)+'">홍대화덕피자</a><p>'+e(t['address'])+'<br>서울 마포구 독막로7길 5, 1층<br><a href="'+url(lang,'/privacy/')+'">'+e(PRIVACY[lang])+'</a></p><small>© 홍대화덕피자</small></div></footer><script src="/app.js"></script></body></html>'

def story_photo_url(slug):
 thumbnail_overrides={
  'christmas-date':'quattro.webp',
  'blue-ribbon-2027':'poster.webp',
  'gamberi-crema':'pastatable.webp',
 }
 return '/assets/'+thumbnail_overrides.get(slug,PHOTOS.get(slug,'table.webp'))

def story_thumbnail(slug):
 photo=story_photo_url(slug)
 image=f'<img class="story-thumbnail" src="{photo}" alt="" loading="lazy" decoding="async">'
 if slug=='pizza-pasta-for-two':
  return ('<span class="story-media">'+image+
          f'<video class="story-preview" muted loop playsinline preload="none" poster="{photo}" '
          'data-src="/assets/rain-story-loop.mp4" aria-hidden="true" tabindex="-1"></video></span>')
 return image

def card(lang,t,slug):
 title,body=t['guides'][slug]
 return f'<a class="story-card" href="{url(lang,"/stories/"+slug+"/")}">{story_thumbnail(slug)}<h3>{e(title)}</h3><p>{e(body.split(chr(10))[0][:155])}</p></a>'

def guide_body(lang,t,slug,text,sections):
 """Keep the direct answer first, then render reviewed, localized sections."""
 config=sections['languages'][lang][slug]
 paragraphs=text.split('\n\n')
 headings=config['headings']
 if len(headings)!=len(paragraphs)-1 or any(not h.strip() for h in headings):
  raise ValueError(f'Guide headings need review: {lang}/{slug}')
 body='<p>'+e(paragraphs[0])+'</p>'
 for heading,paragraph in zip(headings,paragraphs[1:]):
  body+='<h2>'+e(heading)+'</h2><p>'+e(paragraph)+'</p>'
 related=config['related']
 if len(set(related))!=len(related) or slug in related or any(s not in t['guides'] for s in related):
  raise ValueError(f'Invalid related guides: {lang}/{slug}')
 body+='<section class="related-guides"><h2>'+e(sections['related_title'][lang])+'</h2><ul>'
 body+=''.join('<li><a href="'+url(lang,'/stories/'+s+'/')+'">'+e(t['guides'][s][0])+'</a></li>' for s in related)
 return body+'</ul></section>'

def home(lang,t,menu):
 names=t['menu_names']; desc=t['menu_desc']
 cards=''.join('<article class="menu-card">'+picture(m['image'],names[i])+f'<span class="menu-type">{e(m["name"])}</span><h3>{e(names[i])}</h3><p class="menu-body">{e(desc[i])}</p></article>' for i,m in enumerate(menu))
 purposes=''.join('<div><dt>'+e(t['purposes'][i])+'</dt><dd>'+e(t['purpose_body'][i])+' '+(link(t['all_guides'],url(lang,'/stories/'+slug+'/'),'plain-link') if slug else '')+'</dd></div>' for i,slug in enumerate(['pizza-pasta-for-two',None,'family-visit']))
 guides=''.join(card(lang,t,slug) for slug in ['cheese-pizza','gamberi-crema','directions','pizza-pasta-for-two','family-visit','reservation'])
 return f'''<section class="hero wrap"><div class="hero-copy"><p class="eyebrow">2012 · HONGDAE · HAPJEONG · SANGSU</p><h1>{e(t['hero'][0])}<br><em>{e(t['hero'][1])}</em></h1><p class="hero-intro">{e(t['intro'])}</p><p class="hero-description">{e(t['hero_body'])}</p><div class="actions">{link(t['book'])}</div></div><figure class="hero-photo"><video id="hero-video" muted loop playsinline preload="metadata" poster="/assets/poster.webp" aria-label="{e(t['photo_alt'])}"><source src="/assets/hero-final.mp4?v=final2" type="video/mp4"></video><button id="video-toggle" type="button" class="video-toggle" data-play-label="{e(t['play'])}" data-pause-label="{e(t['pause'])}" aria-label="{e(t['play'])}">▶ {e(t['play'])}</button><figcaption>{e(t['caption'])}</figcaption></figure></section>
<section id="menu" class="signature wrap section"><div class="section-head"><p class="eyebrow">01 / MENU</p><div><h2>{e(t['menu_title'])}</h2><p>{e(t['menu_intro'])}</p></div></div><div class="menu-grid">{cards}</div><div class="half-banner"><p>{e(t['half'])}</p>{link(t['menu_link'],cls='')}</div><figure class="feast">{picture('table.webp',t['photo_alt'])}<figcaption>{e(t['table_caption'])}</figcaption></figure><div class="actions">{link(t['guides']['cheese-pizza'][0],url(lang,'/stories/cheese-pizza/'),'plain-link')}{link(t['guides']['gamberi-crema'][0],url(lang,'/stories/gamberi-crema/'),'plain-link')}</div></section>
<section class="regulars section"><div class="wrap"><div class="section-head"><p class="eyebrow">02 / SINCE 2012</p><div><h2>{e(t['regulars'][0])}</h2><p>{e(t['regulars'][1])}</p></div></div></div></section>
<section id="oven" class="oven-section wrap section"><figure>{picture('oven-pizza.webp',t['photo_alt'])}</figure><div class="oven-copy"><p class="eyebrow">03 / OUR OVEN</p><h2>{e(t['oven'][0])}</h2><p>{e(t['oven'][1])}</p></div></section>
<section id="space" class="space-section wrap section"><figure>{picture('interior.webp',t['photo_alt'])}</figure><div class="space-copy"><p class="eyebrow">04 / OUR TABLE</p><h2>{e(t['space'][0])}</h2><p>{e(t['space'][1])}</p><dl>{purposes}</dl></div></section>
<div class="photo-strip">{''.join(picture(im,t['photo_alt']) for im in ['pizza.webp','night.webp','cream.webp','table.webp','drinks.webp'])}</div>
<section class="booking-section section" id="reservation"><div class="wrap"><h2>{e(t['reserve_title'])}</h2><p>{e(t['reserve_body'])}</p>{link(t['book'])}</div></section>
<section id="visit" class="visit-section wrap section"><div class="section-head"><p class="eyebrow">05 / VISIT</p><div><h2>{e(t['visit_title'])}</h2><p>{e(t['visit_body'])}</p></div></div><div class="visit-layout"><figure>{picture('night.webp',t['photo_alt'])}</figure><div class="visit-info"><h3>홍대화덕피자</h3><p>{e(t['address'])}<br>서울 마포구 독막로7길 5, 1층</p><dl><div><dt>{e(t['hours_label'])}</dt><dd>{e(t['hours'])}</dd></div><div><dt>{e(t['phone_label'])}</dt><dd>0507-1349-2285</dd></div></dl>{link(t['directions'],cls='pill outline')}</div></div></section>
<section class="stories section"><div class="wrap"><div class="section-head"><p class="eyebrow">06 / GUIDES</p><h2>{e(t['stories_title'])}</h2></div><div class="story-grid">{guides}</div><div class="more-row">{link(t['all_guides'],url(lang,'/stories/'),'pill outline')}</div></div></section>'''

def build_locales(root,posts,restaurant):
 root=Path(root);dist=root/'dist';data=json.loads((root/'content/locales.json').read_text(encoding='utf-8'));menu=json.loads((root/'content.json').read_text(encoding='utf-8'))['menu'];by_slug={p['slug']:p for p in posts};extra=[]
 revisions=json.loads((root/'content/translation_sources.json').read_text(encoding='utf-8'))['source_sha256']
 sections=json.loads((root/'content/guide_sections.json').read_text(encoding='utf-8'))
 for post in posts:
  digest=hashlib.sha256((root/'content/posts'/f"{post['slug']}.md").read_bytes()).hexdigest()
  if revisions.get(post['slug'])!=digest:
   raise ValueError(f"Translations need review after Korean content changed: {post['slug']}")
 # The Korean versions keep their existing URLs, layout and full article content.
 for f in [dist/'index.html',dist/'stories/index.html']+list((dist/'stories').glob('*/index.html')):
  path='/'+f.relative_to(dist).as_posix().removesuffix('index.html')
  if path=='/index.html':path='/'
  s=f.read_text(encoding='utf-8');s=s.replace('</head>',alternates(path)+'</head>');s=s.replace('</nav>','</nav>'+switch('ko',path),1);f.write_text(s,encoding='utf-8')
 for lang,t in data.items():
  assert set(t['guides'])==set(by_slug),'Language guides must cover the published article set'
  body=home(lang,t,menu);dest=dist/PREFIX[lang].strip('/');dest.mkdir(exist_ok=True)
  (dest/'index.html').write_text(shell(lang,t,'/',t['title'],t['intro'],body,restaurant),encoding='utf-8');extra.append((url(lang),'2026-11-04'))
  archive=dest/'stories';archive.mkdir(exist_ok=True)
  inner='<section class="wrap section archive"><h1>'+e(t['all_guides'])+'</h1><div class="story-grid">'+''.join(card(lang,t,p['slug']) for p in posts)+'</div></section>'
  (archive/'index.html').write_text(shell(lang,t,'/stories/',t['all_guides']+' | 홍대화덕피자',t['intro'],inner,restaurant),encoding='utf-8');extra.append((url(lang,'/stories/'),'2026-11-04'))
  for slug,(title,text) in t['guides'].items():
   path='/stories/'+slug+'/';folder=archive/slug;folder.mkdir(exist_ok=True)
   photo=PHOTOS[slug];body=guide_body(lang,t,slug,text,sections)
   inner='<article class="article wrap"><a class="plain-link" href="'+url(lang,'/stories/')+'">← '+e(t['back'])+'</a><h1>'+e(title)+'</h1><div class="article-body">'+body+'<figure class="article-photo">'+picture(photo,t['photo_alt'])+'</figure><p>'+e(t['source_note'])+'</p></div><div class="article-actions">'+link(t['menu_link'])+link(t['book'],cls='pill outline')+'</div></article>'
   (folder/'index.html').write_text(shell(lang,t,path,title+' | 홍대화덕피자',text.split('\n')[0][:170],inner,restaurant),encoding='utf-8');extra.append((url(lang,path),max(by_slug[slug]['updated'],sections['reviewed_on'])))
 # Retired Spanish URLs lead to the matching English page; they are not indexed.
 for path in ['/','/stories/']+['/stories/'+p['slug']+'/' for p in posts]:
  target=ORIGIN+'/en'+path; folder=dist/('es'+path);folder.mkdir(parents=True,exist_ok=True)
  (folder/'index.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex,follow"><meta http-equiv="refresh" content="0;url='+target+'"><link rel="canonical" href="'+target+'"><title>Continue in English | 홍대화덕피자</title></head><body><h1>Continue in English</h1><a href="'+target+'">Open this page in English</a></body></html>',encoding='utf-8')
 return extra
