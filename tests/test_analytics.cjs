// Tests our DOM/gtag command boundary. These are not a live Google transport test.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const source=fs.readFileSync(path.join(__dirname,'../analytics.js'),'utf8');
function mount({host='www.hongdaepizza.com',lang='ko',choice='',hash=''}={}) {
  class Element {
    constructor(tag){this.tagName=tag;this.children=[];this.attrs={};this.dataset={};this.handlers={};this.className='';this.id='';}
    append(...children){for(const el of children){el.parent=this;this.children.push(el);}}
    setAttribute(key,value){this.attrs[key]=value;}
    getAttribute(key){return this.attrs[key]??null;}
    hasAttribute(key){return key in this.attrs;}
    addEventListener(name,fn){this.handlers[name]=fn;}
    focus(options){this.focusOptions=options;}
    get classList(){return {contains:value=>this.className.split(/\s+/).includes(value)};}
    querySelector(selector){return this.children.find(x=>x.tagName===selector)||null;}
    closest(selector){for(let el=this;el;el=el.parent)if(el.tagName===selector)return el;return null;}
  }
  const head=new Element('head'),body=new Element('body'),footer=new Element('footer');body.append(footer);
  const handlers={};const storage=new Map(choice?[['hdpizza.analytics.v1',choice]]:[]);
  const document={head,body,title:'Test page',referrer:'https://search.naver.com/search.naver?private=query',documentElement:{lang},cookie:'',createElement:tag=>new Element(tag),querySelector:()=>footer,addEventListener:(name,fn)=>handlers[name]=fn};
  const location={hostname:host,origin:'https://'+host,pathname:'/',hash,reload(){this.reloaded=true;}};
  const window={};
  vm.runInNewContext(source,{document,window,location,URL,localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v)}});
  const panel=body.children.find(x=>x.className==='analytics-panel');
  const button=value=>panel.children.find(x=>x.dataset.choice===value);
  const commands=()=>window.dataLayer.map(x=>Array.from(x));
  const configs=()=>commands().filter(x=>x[0]==='config');
  const scripts=()=>head.children.filter(x=>x.tagName==='script');
  function clickLink(containerTag,{id='',className=''}={}) {
    const container=new Element(containerTag);container.id=id;container.className=className;
    const a=new Element('a');a.href='https://naver.me/xtgp91Fv';a.dataset.ctaRole='reservation';
    const span=new Element('span');container.append(a);a.append(span);handlers.click({target:span});
    return commands().filter(x=>x[0]==='event'&&x[1]==='naver_outbound_click').at(-1);
  }
  return {window,panel,button,commands,configs,scripts,clickLink,location};
}
for(const host of ['hongdaepizza.com','www.hongdaepizza.com'])for(const lang of ['ko','en','ja','zh-Hans']) {
  test(`${host}/${lang}: allow creates one configured pageview and preserves language`,()=>{
    const m=mount({host,lang});assert.equal(m.scripts().length,0);assert.equal(m.configs().length,0);
    m.button('granted').handlers.click();
    assert.equal(m.scripts().length,1);assert.equal(m.configs().length,1);
    const config=m.configs()[0];assert.equal(config[1],'G-J4QK7VPJE4');assert.equal(config[2].send_page_view,true);
    assert.equal(config[2].page_language,lang);assert.equal(config[2].page_title,'Test page');
    assert.equal(config[2].page_location,'https://'+host+'/');assert.equal(config[2].page_referrer,'https://search.naver.com/');
    assert.equal(m.commands().filter(x=>x[0]==='event'&&x[1]==='page_view').length,0);
    assert.ok(m.commands().some(x=>x[0]==='set'&&x[1].page_language===lang));
    m.button('granted').handlers.click();assert.equal(m.configs().length,1);assert.equal(m.scripts().length,1);
  });
}
test('undecided, close, and first refusal do not load Google or configure measurement',()=>{
  for(const action of ['none','close','denied']){
    const m=mount();
    if(action==='close')m.panel.children.at(-1).handlers.click();
    if(action==='denied')m.button('denied').handlers.click();
    assert.equal(m.scripts().length,0);assert.equal(m.configs().length,0);assert.equal(m.commands().length,0);
  }
});
test('stored consent sends one config; stored refusal and unknown hosts send none',()=>{
  const m=mount({choice:'granted'});assert.equal(m.configs().length,1);assert.equal(m.scripts().length,1);
  assert.equal(mount({choice:'denied'}).configs().length,0);
  assert.equal(mount({choice:'granted',host:'localhost'}).scripts().length,0);
});
test('test visits retain explicit QA flags',()=>{
  const m=mount({choice:'granted',hash:'#analytics-test'});
  assert.equal(m.configs()[0][2].debug_mode,true);assert.equal(m.configs()[0][2].qa_test,'setup_validation');
});
test('hero, booking section, header, footer, and article map to their actual positions',()=>{
  const m=mount({choice:'granted'});
  for(const [tag,attrs,expected] of [['section',{className:'hero wrap'},'hero'],['section',{id:'reservation'},'reservation'],['header',{},'header'],['footer',{},'footer'],['article',{},'article']]) {
    const e=m.clickLink(tag,attrs);assert.equal(e[2].cta_position,expected);assert.equal(e[2].cta_role,'reservation');assert.equal(e[2].page_language,'ko');
  }
});
test('refusing after consent disables measurement and reloads; clicks then stop',()=>{
  const m=mount({choice:'granted'});m.button('denied').handlers.click();
  assert.equal(m.window['ga-disable-G-J4QK7VPJE4'],true);assert.equal(m.location.reloaded,true);
  assert.equal(m.clickLink('section',{className:'hero'}),undefined);
});
