(() => {
  'use strict';
  const ID = 'G-J4QK7VPJE4', KEY = 'hdpizza.analytics.v1';
  const lang = document.documentElement.lang || 'ko';
  const texts = {
    ko: ['방문 분석 안내','Google Analytics로 방문 경로와 페이지 이용, 네이버·전화 버튼 클릭을 분석합니다. 동의한 경우에만 분석 쿠키와 기기·브라우저 정보를 사용하며 이름·전화번호 입력값은 수집하지 않습니다. 거부해도 사이트를 이용할 수 있고 아래에서 언제든 변경할 수 있습니다. 운영: 홍대화덕피자 · 문의: 0507-1349-2285.','분석 허용','거부','개인정보·분석 설정','닫기','Google의 데이터 이용 안내','동의하면 Google Analytics로 방문 경로와 버튼 클릭을 분석합니다. 거부해도 사이트를 이용할 수 있습니다.','자세히'],
    en: ['Website analytics','With your consent, Google Analytics uses cookies and device/browser information to measure referrals, page use and Naver/phone link clicks. We do not collect entered names or phone numbers. You can refuse and still use this site, or change your choice below. Operator: Hongdae Hwaduk Pizza. Contact: 0507-1349-2285.','Allow analytics','Decline','Privacy & analytics','Close','How Google uses data','With your consent, Google Analytics measures visits and button clicks. You can decline and still use this site.','Details'],
    ja: ['アクセス解析について','同意いただいた場合のみ、Google AnalyticsのCookieと端末・ブラウザ情報を使い、流入元・ページ利用・Naverや電話リンクのクリックを測定します。入力された氏名や電話番号は収集しません。拒否してもサイトを利用でき、設定はいつでも変更できます。運営：홍대화덕피자。連絡先：0507-1349-2285。','解析を許可','拒否','プライバシー・解析設定','閉じる','Googleのデータ利用について','同意いただいた場合のみ、Google Analyticsで訪問とボタンのクリックを測定します。拒否してもサイトを利用できます。','詳細'],
    'zh-Hans': ['访问分析说明','仅在您同意后，Google Analytics使用Cookie和设备、浏览器信息统计访问来源、页面使用情况及Naver和电话链接点击。我们不收集输入的姓名或电话号码。拒绝后仍可使用网站，也可随时更改选择。运营方：홍대화덕피자。联系：0507-1349-2285。','允许分析','拒绝','隐私与分析设置','关闭','Google如何使用数据','经您同意后，Google Analytics将统计访问和按钮点击。拒绝后仍可使用网站。','详细说明']
  };
  const t = texts[lang] || texts.ko;
  let choice = ''; try { choice = localStorage.getItem(KEY) || ''; } catch (_) {}
  let started = false;
  const qa = location.hash === '#analytics-test';
  window.dataLayer = window.dataLayer || [];
  function gtag(){ window.dataLayer.push(arguments); }
  function referrer() { try { return new URL(document.referrer).origin + '/'; } catch (_) { return ''; } }
  function start() {
    if (started || choice !== 'granted' || !['hongdaepizza.com', 'www.hongdaepizza.com', 'hongdae-hwaduk-pizza.ag000000.chatgpt.site'].includes(location.hostname)) return;
    started = true;
    window['ga-disable-' + ID] = false;
    gtag('consent','default',{analytics_storage:'granted',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'});
    gtag('js',new Date());
    // Let this config send the one page_view; do not also send a manual event.
    gtag('set',{page_language:lang});
    gtag('config',ID,{send_page_view:true,page_title:document.title,allow_google_signals:false,allow_ad_personalization_signals:false,page_location:location.origin+location.pathname,page_referrer:referrer(),page_language:lang,debug_mode:qa,qa_test:qa ? 'setup_validation' : 'no'});
    const script = document.createElement('script'); script.async = true; script.src='https://www.googletagmanager.com/gtag/js?id='+ID; document.head.append(script);
  }
  const style=document.createElement('style');
  style.textContent='.analytics-panel{position:fixed;bottom:12px;left:12px;right:12px;max-width:660px;margin:auto;z-index:1000;background:#f6f0e5;color:#173e30;border:1px solid #173e30;border-radius:8px;padding:16px;box-shadow:0 4px 22px #0003;font:14px/1.55 sans-serif;max-height:80vh;overflow:auto}.analytics-panel details{margin:4px 0 2px}.analytics-panel summary{cursor:pointer;text-decoration:underline;font-size:13px}@media(max-width:700px){.analytics-panel{bottom:8px;left:8px;right:8px;padding:10px 12px;font-size:12px;line-height:1.5;max-height:45vh}.analytics-panel h2{font-size:14px;margin:0 0 4px}.analytics-panel p{margin:4px 0}.analytics-panel button{padding:6px 10px;margin:6px 6px 0 0;font-size:12px}.analytics-panel summary{font-size:12px}}.analytics-panel h2{font-size:17px;margin:0 0 8px}.analytics-panel p{margin:8px 0}.analytics-panel button{background:#173e30;color:white;border:1px solid #173e30;padding:8px 12px;margin:8px 8px 0 0;cursor:pointer;border-radius:3px}.analytics-panel button[data-choice="denied"]{background:transparent;color:#173e30}.analytics-settings{background:transparent;border:0;color:inherit;text-decoration:underline;cursor:pointer;padding:8px;font:inherit}.analytics-panel a{color:#173e30;text-decoration:underline}.analytics-panel[hidden]{display:none}';
  document.head.append(style);
  const panel=document.createElement('section'); panel.className='analytics-panel'; panel.setAttribute('aria-label',t[0]);
  const title=document.createElement('h2'); title.textContent=t[0]; panel.append(title);
  const short=document.createElement('p'); short.textContent=t[7]; panel.append(short);
  const more=document.createElement('details'); const moreLabel=document.createElement('summary'); moreLabel.textContent=t[8];
  const text=document.createElement('p'); text.textContent=t[1];
  const info=document.createElement('a'); info.href='https://policies.google.com/technologies/partner-sites'; info.target='_blank'; info.rel='noopener noreferrer'; info.textContent=t[6];
  more.append(moreLabel,text,info); panel.append(more);
  for(const [value,label] of [['granted',t[2]],['denied',t[3]]]){
    const button=document.createElement('button');button.type='button';button.textContent=label;button.dataset.choice=value;
    button.addEventListener('click',()=>{
      choice=value;try{localStorage.setItem(KEY,value);}catch(_){}
      panel.hidden=true;
      if(value==='granted') start();
      else if(started){window['ga-disable-'+ID]=true;gtag('consent','update',{analytics_storage:'denied'});for(const item of document.cookie.split(';')){const name=item.split('=')[0].trim();if(name.startsWith('_ga'))for(const domain of ['', ';domain='+location.hostname,';domain=.'+location.hostname])document.cookie=name+'=;Max-Age=0;path=/'+domain;}location.reload();}
    });panel.append(button);
  }
  const close=document.createElement('button');close.type='button';close.textContent=t[5];close.addEventListener('click',()=>{panel.hidden=true;settings.focus({preventScroll:true});});panel.append(close);
  const settings=document.createElement('button');settings.type='button';settings.className='analytics-settings';settings.textContent=t[4];settings.addEventListener('click',()=>{panel.hidden=false;panel.querySelector('button').focus();});
  (document.querySelector('footer .wrap')||document.querySelector('footer')||document.body).append(settings);document.body.append(panel);panel.hidden=!!choice;
  document.addEventListener('click',event=>{
    if(choice!=='granted'||!started)return;
    const a=event.target.closest('a');if(!a)return;
    const section=a.closest('section');
    const params={page_language:lang,page_path:location.pathname,cta_position:section?.id|| (section?.classList.contains('hero')?'hero':a.closest('header')?'header':a.closest('footer')?'footer':'article'),qa_test:qa?'setup_validation':'no'};
    if(a.href==='https://naver.me/xtgp91Fv')gtag('event','naver_outbound_click',{...params,cta_role:a.dataset.ctaRole||'place'});
    else if(a.getAttribute('href')?.startsWith('tel:'))gtag('event','phone_click',params);
    else if(a.hasAttribute('hreflang'))gtag('event','language_select',{...params,target_language:a.hreflang});
  });
  start();
})();
