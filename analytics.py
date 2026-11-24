from pathlib import Path
import re, shutil

def integrate_analytics(dist):
    shutil.copyfile(Path(__file__).with_name('analytics.js'), dist/'analytics.js')
    roles = {
        'reservation': ('예약','Reserve','Book','予約','预订'),
        'menu': ('메뉴','가격','Menu','menu','メニュー','菜单'),
        'directions': ('길','지도','Directions','道順','路线'),
    }
    def annotate(m):
        attrs,text=m.groups(); label=re.sub('<[^>]+>','',text)
        role=next((r for r,words in roles.items() if any(w in label for w in words)), 'place')
        return '<a'+attrs+' data-cta-role="'+role+'">'+text+'</a>'
    for f in dist.rglob('*.html'):
        if 'es' == f.relative_to(dist).parts[0]: continue
        s=f.read_text(encoding='utf-8')
        s=re.sub(r'<a([^>]*href="https://naver\.me/xtgp91Fv"[^>]*)>(.*?)</a>',annotate,s,flags=re.S)
        s=s.replace('</body>','<script defer src="/analytics.js"></script></body>')
        f.write_text(s,encoding='utf-8')
