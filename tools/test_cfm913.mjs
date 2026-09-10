// Interaction/HTML contract checks; this does not claim physical-device visual QA.
// No installed package dependencies: use Node and Python's standard HTML parser.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const root = fileURLToPath(new URL('../', import.meta.url));
const parse = source => JSON.parse(execFileSync('python3', ['-c', `
from html.parser import HTMLParser
import sys,json
class Parser(HTMLParser):
 def __init__(self):
  super().__init__();self.root={'tag':'root','attrs':{},'children':[]};self.stack=[self.root]
 def handle_starttag(self,tag,attrs):
  item={'tag':tag,'attrs':dict(attrs),'children':[]};self.stack[-1]['children'].append(item)
  if tag not in ['area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr']:self.stack.append(item)
 def handle_endtag(self,tag):
  assert self.stack[-1]['tag']==tag,(tag,self.stack[-1]['tag'])
  self.stack.pop()
 def handle_data(self,text):self.stack[-1]['children'].append({'tag':'text','attrs':{},'text':text,'children':[]})
p=Parser();p.feed(sys.stdin.read());assert len(p.stack)==1;print(json.dumps(p.root))
`], {input:source, encoding:'utf8'}));
let doc;
class Element {
  constructor(raw,parent=null) {
    this.tagName=raw.tag;this.attrs=raw.attrs;this.parent=parent;this.children=raw.children.map(r=>new Element(r,this));
    this.rawText=raw.text||'';this.handlers={};this.checked=Object.hasOwn(this.attrs,'checked');this.value=this.attrs.value||'';
    this.hidden=Object.hasOwn(this.attrs,'hidden');this.disabled=Object.hasOwn(this.attrs,'disabled');this.open=false;
    this.dataset=Object.fromEntries(Object.entries(this.attrs).filter(([k])=>k.startsWith('data-')).map(([k,v])=>[k.slice(5),v]));
    const classes=new Set((this.attrs.class||'').split(' '));this.classList={toggle:(c,on)=>on?classes.add(c):classes.delete(c),contains:c=>classes.has(c)};
    if(this.tagName==='select')this.value=this.children.find(c=>Object.hasOwn(c.attrs,'selected'))?.value||this.children[0]?.value||'';
  }
  get id(){return this.attrs.id||'';}
  get isConnected(){return this===doc||!!this.parent?.children.includes(this)&&this.parent.isConnected;}
  get textContent(){return this.rawText+this.children.map(c=>c.textContent).join('');}
  set textContent(text){this.rawText=String(text);this.children=[];}
  set innerHTML(html){this.rawText='';this.children=parse(html).children.map(r=>new Element(r,this));}
  matches(selector){
    selector=selector.trim();if(selector.includes(','))return selector.split(',').some(s=>this.matches(s));
    let checked=false;if(selector.endsWith(':checked')){checked=true;selector=selector.slice(0,-8);}
    if(checked&&!this.checked)return false;
    const id=selector.match(/#([\w-]+)/);if(id&&id[1]!==this.id)return false;
    const cls=selector.match(/\.([\w-]+)/);if(cls&&!(this.attrs.class||'').split(' ').includes(cls[1]))return false;
    const tag=selector.match(/^[a-z][\w-]*/);if(tag&&this.tagName!==tag[0])return false;
    for(const [,attr,value]of selector.matchAll(/\[([^=\]]+)(?:="([^"]*)")?\]/g)){
      if(attr==='open'){if(!this.open)return false;}else if(!Object.hasOwn(this.attrs,attr)||(value!==undefined&&this.attrs[attr]!==value))return false;
    }
    return true;
  }
  querySelectorAll(selector){return this.children.flatMap(c=>[...(c.tagName!=='text'&&c.matches(selector)?[c]:[]),...c.querySelectorAll(selector)]);}
  querySelector(selector){return this.querySelectorAll(selector)[0]||null;}
  closest(selector){for(let e=this;e;e=e.parent)if(e.matches(selector))return e;return null;}
  addEventListener(name,fn){(this.handlers[name]??=[]).push(fn);}
  fire(name,extra={}){const event={target:this,preventDefault(){},...extra};for(let e=this;e;e=e.parent)for(const fn of e.handlers[name]||[])fn(event);}
  focus(){doc.activeElement=this;}
  showModal(){this.open=true;this.querySelector('button')?.focus();}
  close(){if(!this.open)return;this.open=false;this.fire('close');}
}
doc=new Element(parse(fs.readFileSync(root+'cfm913-otw.html','utf8')));
doc.getElementById=id=>doc.querySelector('#'+id);doc.body=doc.querySelector('body');doc.documentElement=doc.querySelector('html');doc.activeElement=doc.body;
doc.documentElement.requestFullscreen=()=>{doc.fullscreenElement=doc.documentElement;return Promise.resolve();};doc.exitFullscreen=()=>{doc.fullscreenElement=null;return Promise.resolve();};
const location={hash:'',href:'https://outsidetheworld.com/cfm913-otw.html'};
const window=new Element({tag:'window',attrs:{},children:[]});window.scrollTo=()=>{};
let now=Date.parse('2026-09-10T12:00:00-07:00'),serial=0;const timers=new Map(),timeouts=new Map(),history=[];
assert.equal(doc.getElementById('mode-toggle').hidden,true,'discussion button is hidden before JavaScript loads');
const sandbox={document:doc,window,location,history:{pushState:(_,__,hash)=>{location.hash=hash;history.push(hash);},replaceState:(_,__,hash)=>{location.hash=hash;}},navigator:{},URL,URLSearchParams,Date:{now:()=>now,parse:Date.parse},setTimeout:(fn,delay)=>{timeouts.set(++serial,{fn,at:now+delay});return serial;},setInterval:fn=>{timers.set(++serial,fn);return serial;},clearInterval:id=>timers.delete(id),console};
vm.runInNewContext(fs.readFileSync(root+'media/cfm913/lesson.js','utf8'),sandbox);
const get=id=>doc.getElementById(id);
const click=selector=>{const e=selector.startsWith('#')?get(selector.slice(1)):doc.querySelector(selector);assert.ok(e,selector+' exists');e.focus();e.fire('click');};
const route=hash=>{location.hash=hash;window.fire('hashchange');};
const key=(name,target=doc.body)=>doc.fire('keydown',{target,key:name});
const elapse=ms=>{now+=ms;for(const [id,timer]of [...timeouts])if(timer.at<=now){timeouts.delete(id);timer.fn();}for(const fn of [...timers.values()])fn();};
function structure(){
  const ids=doc.querySelectorAll('[id]').map(e=>e.id);assert.equal(new Set(ids).size,ids.length,'unique IDs');
  for(const a of doc.querySelectorAll('a')){
    if(a.attrs.href?.startsWith('https://'))assert.ok(a.attrs.rel?.includes('noopener'));
    assert.ok(a.textContent.trim()||a.attrs['aria-label'],'link has an accessible name');
  }
  for(const b of doc.querySelectorAll('button'))assert.ok(b.textContent.trim()||b.attrs['aria-label'],'button has an accessible name');
}
assert.equal(get('welcome').hidden,false);assert.equal(get('presentation').hidden,true);structure();
assert.equal(doc.activeElement,doc.body,'opening the page does not move focus to the title');
assert.equal(get('mode-toggle').hidden,true,'discussion button stays hidden before Sunday');
// Plain-language summaries cover the assigned chapters and return readers to the opener.
const welcomeHash=location.hash;
click('[data-action="reading-summary"]');
assert.equal(get('scripture-reader').open,true);assert.equal(get('welcome').hidden,false);
assert.equal(get('scripture-reader').querySelectorAll('.chapter-summary').length,6);
const chapterLinks=get('scripture-reader').querySelectorAll('.chapter-links').flatMap(section=>section.querySelectorAll('a'));
assert.deepEqual(chapterLinks.map(a=>a.attrs.href),[
  ...[1,2,3,4,15,16,22,31].map(chapter=>`https://www.churchofjesuschrist.org/study/scriptures/ot/prov/${chapter}?lang=eng`),
  ...[1,2,3,11,12].map(chapter=>`https://www.churchofjesuschrist.org/study/scriptures/ot/eccl/${chapter}?lang=eng`)
]);
structure();click('[data-close="scripture-reader"]');
assert.equal(get('scripture-reader').open,false);assert.equal(location.hash,welcomeHash);
assert.equal(doc.activeElement.dataset.action,'reading-summary');
for(const id of ['weary','anger','trust','stumble']){
  route('#welcome');click(`[data-scenario="${id}"]`);
  assert.equal(location.hash,`#study/${id}/0`);assert.equal(doc.activeElement.id,'study-title');
  for(let step=0;step<4;step++){
    assert.equal(get('study').querySelector('[aria-current="step"]').dataset.step,String(step));structure();
    if(step===1){assert.match(get('study').textContent,/King James Version/);assert.ok(get('study').querySelector('blockquote'));}
    if(step===2){
      const first=get('study-question').textContent;click('[data-action="another-study"]');assert.notEqual(get('study-question').textContent,first);
      click('[data-read]');assert.equal(get('scripture-reader').open,true);click('[data-close="scripture-reader"]');assert.equal(get('scripture-reader').open,false);assert.ok(doc.activeElement.dataset.read);
    }
    if(step===3)assert.match(get('study').textContent,/official study/);
    click('[data-action="study-next"]');
  }
  assert.equal(get('welcome').hidden,false);
  assert.equal(get('mode-toggle').hidden,true,'finishing a study path does not reveal the discussion button early');
}
// A teacher can still preview a direct discussion link and return to the study page.
route('#discuss/opening');assert.equal(get('mode-toggle').hidden,false);click('#mode-toggle');assert.equal(get('mode-toggle').hidden,true);
// The button appears at midnight in Arizona, without changing the page or focus.
now=Date.parse('2026-09-13T06:59:59.999Z');elapse(0);assert.equal(get('mode-toggle').hidden,true);
const beforeReveal=doc.activeElement,revealHash=location.hash;
elapse(1);assert.equal(get('mode-toggle').hidden,false);assert.equal(doc.activeElement,beforeReveal);assert.equal(location.hash,revealHash);
assert.equal(timeouts.size,0,'release timer finishes once Sunday arrives');
// Deep links and malformed/prototype routes fail closed without rendering untrusted HTML.
route('#study/trust/1');assert.match(get('study').textContent,/Ecclesiastes 1:17/);
route('#study/anger/999');assert.equal(get('study').querySelector('[aria-current="step"]').dataset.step,'0');
for(const bad of ['#study/toString/1','#study/__proto__/1','#study/<script>/2']){route(bad);assert.equal(get('welcome').hidden,false);}
route('#welcome');click('#mode-toggle');assert.equal(get('presentation').hidden,false);assert.ok(get('presentation').querySelector('[data-action="class-back"]').disabled);
const defaultSlides=get('slide-jump').children.map(e=>e.value);assert.equal(defaultSlides.length,8);
for(const target of defaultSlides){
  get('slide-jump').value=target;get('slide-jump').fire('change');structure();assert.equal(doc.activeElement.id,'slide-title');
  if(target.endsWith('reflect')){const before=get('slide-title').textContent;click('[data-action="another-class"]');assert.notEqual(get('slide-title').textContent,before);click('[data-action="christ"]');assert.equal(get('scripture-reader').open,true);click('[data-close="scripture-reader"]');}
}
click('[data-action="class-next"]');assert.match(location.hash,/#discuss\/opening/);
// Quiet time is manually controlled and cannot navigate or auto-advance.
click('[data-action="pause"]');assert.equal(get('quiet-clock-display').textContent,'0:30');
elapse(10000);click('[data-action="pause"]');const stopped=get('quiet-clock-display').textContent;elapse(45000);assert.equal(get('quiet-clock-display').textContent,stopped);
click('[data-action="pause"]');const beforeTimer=location.hash;elapse(21000);assert.equal(location.hash,beforeTimer);assert.equal(timers.size,0);assert.match(get('quiet-clock-display').textContent,/time you need/);
click('[data-action="pause"]');click('[data-action="class-next"]');assert.equal(timers.size,0);
// Plan changes, empty plan rejection, and URL restoration.
click('[data-action="guide"]');const checkboxes=()=>get('guide-form').querySelectorAll('input[name="paths"]');
for(const input of checkboxes())input.checked=false;get('guide-form').fire('submit');assert.match(get('guide-error').textContent,/at least one/);assert.equal(get('leader-guide').open,true);
for(const input of checkboxes())input.checked=true;get('plan-minutes').value='40';get('plan-minutes').fire('change');assert.match(get('plan-rundown').textContent,/8–9 min/);get('guide-form').fire('submit');
assert.equal(get('leader-guide').open,false);assert.equal(get('slide-jump').children.length,14);assert.match(location.hash,/minutes=40/);
route('#discuss/stumble-reflect?paths=stumble&minutes=15');assert.equal(get('slide-jump').children.length,5);assert.match(get('presentation').textContent,/15-minute/);
click('[data-action="guide"]');const lockedHash=location.hash;key('ArrowRight');assert.equal(location.hash,lockedHash);click('[data-close="leader-guide"]');
key('Home');assert.match(location.hash,/#discuss\/opening/);key('End');assert.match(location.hash,/#discuss\/closing/);
const endHash=location.hash;key('ArrowLeft',get('slide-jump'));assert.equal(location.hash,endHash,'select keys do not navigate presentation');
route('#discuss/opening?paths=__proto__,anger,anger,invalid&minutes=999');assert.equal(get('slide-jump').children.length,5);
click('[data-action="pause"]');click('#mode-toggle');assert.equal(get('welcome').hidden,false);assert.equal(timers.size,0);
// Share fallback always sends readers to the start of the selected personal path.
route('#study/anger/3');click('[data-action="share"]');assert.match(get('share-status').textContent,/#study\/anger\/0/);
structure();
console.log('PASS: Sunday button timing, initial focus, summaries for all 13 assigned chapters, modal focus return, 16 study steps, all discussion slides, deep links, alternate questions, scripture dialogs, empty/custom plans, timer controls, keyboard guards, share fallback, and HTML contracts.');
