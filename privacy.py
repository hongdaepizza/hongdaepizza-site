"""Short privacy notice pages in four languages, kept out of the sitemap and search results."""
import json
from html import escape as e
from pathlib import Path
from i18n import ORIGIN, PREFIX, alternates, shell, switch, url

PATH = '/privacy/'
NOINDEX = '<meta name="robots" content="noindex,follow">'
UPDATED = '2026-11-25'
TEXT = {
    'ko': {
        'title': '개인정보 안내',
        'intro': '홍대화덕피자 홈페이지가 방문자 정보를 어떻게 다루는지 짧게 안내합니다.',
        'sections': [
            ('받지 않는 정보', '이 홈페이지에는 이름이나 전화번호를 입력하는 칸이 없습니다. 예약은 네이버 예약에서 진행되며, 예약할 때 입력한 정보는 네이버의 개인정보 처리방침에 따라 처리됩니다.'),
            ('방문 분석', '방문 분석 안내에서 \'분석 허용\'을 누른 방문자에 한해 Google Analytics로 방문 경로, 본 페이지, 네이버·전화 버튼 클릭을 분석합니다. 이때 분석 쿠키와 기기·브라우저 정보가 사용됩니다. 광고 맞춤 기능은 사용하지 않습니다.'),
            ('거부와 철회', '처음 방문할 때 \'거부\'를 누르면 분석하지 않습니다. 이미 허용했다면 화면 아래의 \'개인정보·분석 설정\'을 눌러 \'거부\'를 선택해 주세요. 분석이 멈추고 저장된 분석 쿠키가 삭제됩니다. 거부해도 홈페이지는 그대로 이용할 수 있습니다.'),
            ('문의', '홍대화덕피자 · 0507-1349-2285'),
        ],
        'updated': '안내 기준일',
    },
    'en': {
        'title': 'Privacy notice',
        'intro': 'A short note on how the 홍대화덕피자 website handles visitor information.',
        'sections': [
            ('What we do not collect', 'This website has no fields for entering your name or phone number. Reservations are made on Naver, and the details you enter there are handled under Naver\'s privacy policy.'),
            ('Website analytics', 'Only if you choose \'Allow analytics\' in the analytics notice, we use Google Analytics to measure referrals, pages viewed and clicks on Naver and phone links. This uses analytics cookies and device/browser information. Ad personalization is not used.'),
            ('Declining or withdrawing consent', 'If you choose \'Decline\' on your first visit, nothing is measured. If you allowed it earlier, tap \'Privacy & analytics\' at the bottom of the page and choose \'Decline\'. Measurement stops and the stored analytics cookies are deleted. You can keep using the website either way.'),
            ('Contact', '홍대화덕피자 · 0507-1349-2285'),
        ],
        'updated': 'Last updated',
    },
    'ja': {
        'title': 'プライバシーについて',
        'intro': '홍대화덕피자のウェブサイトにおける訪問者情報の取り扱いを簡単にご案内します。',
        'sections': [
            ('収集しない情報', 'このサイトには氏名や電話番号を入力する欄はありません。予約はNaver予約で行われ、入力された情報はNaverのプライバシーポリシーに従って取り扱われます。'),
            ('アクセス解析', 'アクセス解析の案内で「解析を許可」を選んだ方に限り、Google Analyticsで流入元、閲覧ページ、Naver・電話リンクのクリックを測定します。その際、解析用Cookieと端末・ブラウザ情報を使用します。広告のパーソナライズは使用しません。'),
            ('拒否と撤回', '初回訪問時に「拒否」を選ぶと測定しません。すでに許可した場合は、画面下の「プライバシー・解析設定」から「拒否」を選んでください。測定が止まり、保存された解析用Cookieが削除されます。拒否してもサイトはそのままご利用いただけます。'),
            ('お問い合わせ', '홍대화덕피자 · 0507-1349-2285'),
        ],
        'updated': '基準日',
    },
    'zh-Hans': {
        'title': '隐私说明',
        'intro': '简要说明홍대화덕피자网站如何处理访客信息。',
        'sections': [
            ('不收集的信息', '本网站没有填写姓名或电话号码的栏位。预订在Naver预订上进行，您在那里填写的信息按照Naver的隐私政策处理。'),
            ('访问分析', '仅当您在访问分析说明中选择“允许分析”时，我们才会通过Google Analytics统计访问来源、浏览页面以及Naver和电话链接的点击。此时会使用分析Cookie及设备、浏览器信息。不使用广告个性化功能。'),
            ('拒绝与撤回', '首次访问时选择“拒绝”，则不会进行统计。如果之前已允许，请点击页面下方的“隐私与分析设置”并选择“拒绝”。统计将停止，已保存的分析Cookie会被删除。拒绝后仍可正常使用本网站。'),
            ('联系方式', '홍대화덕피자 · 0507-1349-2285'),
        ],
        'updated': '更新日期',
    },
}


def body(lang):
    t = TEXT[lang]
    parts = ''.join(f'<h2>{e(head)}</h2><p>{e(text)}</p>' for head, text in t['sections'])
    return ('<article class="article wrap privacy"><h1>' + e(t['title']) + '</h1>'
            '<p class="article-summary">' + e(t['intro']) + '</p><div class="article-body">' + parts
            + f'<p class="article-meta">{e(t["updated"])}: <time datetime="{UPDATED}">{UPDATED}</time></p></div></article>')


def build_privacy(root, dist, page_shell, nav, footer, restaurant):
    root, dist = Path(root), Path(dist)
    t = TEXT['ko']
    schema = {'@context': 'https://schema.org', '@type': 'WebPage', 'name': t['title'], 'url': ORIGIN + PATH}
    html = page_shell(t['title'] + ' | 홍대화덕피자', t['intro'], PATH, body('ko'),
                      nav.replace('</nav>', '</nav>' + switch('ko', PATH), 1), footer, schema)
    html = html.replace('</head>', alternates(PATH) + NOINDEX + '</head>')
    target = dist / 'privacy'
    target.mkdir(exist_ok=True)
    (target / 'index.html').write_text(html, encoding='utf-8')
    locales = json.loads((root / 'content/locales.json').read_text(encoding='utf-8'))
    for lang, strings in locales.items():
        t = TEXT[lang]
        html = shell(lang, strings, PATH, t['title'] + ' | 홍대화덕피자', t['intro'], body(lang), restaurant)
        html = html.replace('</head>', NOINDEX + '</head>')
        target = dist / PREFIX[lang].strip('/') / 'privacy'
        target.mkdir(exist_ok=True)
        (target / 'index.html').write_text(html, encoding='utf-8')
