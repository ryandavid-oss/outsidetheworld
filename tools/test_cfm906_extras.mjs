import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../', import.meta.url));
const lessons=[
 {entry:'/cfm906-otw.html',script:'/media/cfm906/lesson.js',adult:true,scene:'.slide',first:'welcome',last:'take-home',optional:'psalms',select:'moment-select',heading:'welcome-title',app:'presentation',previous:'previous',next:'next',videoSection:'worship',teacherOpen:'guide-toggle',teacher:'lesson-guide',scripture:'scripture-reader',timer:'timer-toggle',clock:'timer-display'},
 ...['youth','teens'].map(edition=>({entry:`/cfm906-${edition}.html`,script:edition==='youth'?'/media/cfm906-youth/youth.js':'/media/cfm906-teens/lesson.js',adult:false,scene:'.scene',first:'start',last:'finish',optional:'psalm',select:'y-section',heading:'start-title',app:'y-app',previous:'y-previous',next:'y-next',videoSection:'worship',teacherOpen:'y-teacher-open',teacher:'y-teacher',scripture:'y-scripture',timer:'y-class-timer',clock:'y-class-time'}))
];
for(const config of lessons){
const parsed=execFileSync('python3',['-c',`
from html.parser import HTMLParser
import json,sys
class Parse(HTMLParser):
 def __init__(self):
  super().__init__();self.root={'tag':'document','attrs':{},'children':[]};self.stack=[self.root]
 def handle_starttag(self,tag,attrs):
  node={'tag':tag,'attrs':dict(attrs),'children':[]};self.stack[-1]['children'].append(node)
  if tag not in ['area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr']:self.stack.append(node)
 def handle_endtag(self,tag):
  assert self.stack[-1]['tag']==tag,(tag,self.stack[-1]['tag'])
  self.stack.pop()
p=Parse();p.feed(open(sys.argv[1]).read());assert len(p.stack)==1;print(json.dumps(p.root))
`,root+config.entry],{encoding:'utf8'});
const closeEvents=[];
let doc;
class E {
 constructor(raw,parent=null){
  this.tagName=raw.tag;this.attrs=raw.attrs;this.parent=parent;this.children=raw.children.map(c=>new E(c,this));this.dataset={};
  for(const [k,v]of Object.entries(this.attrs))if(k.startsWith('data-'))this.dataset[k.slice(5).replace(/-([a-z])/g,(_,c)=>c.toUpperCase())]=v;
  this.id=this.attrs.id;this.hidden=Object.hasOwn(this.attrs,'hidden');this.disabled=Object.hasOwn(this.attrs,'disabled');this.checked=Object.hasOwn(this.attrs,'checked');this.handlers={};this.style={setProperty(k,v){this[k]=v;}};
  this.classes=new Set((this.attrs.class||'').split(' '));this.classList={add:name=>this.classes.add(name),remove:name=>this.classes.delete(name),toggle:(name,on)=>{if(on)this.classes.add(name);else this.classes.delete(name);}};
  this.paused=true;this.seeking=false;this.currentTime=0;this.value='';this.open=false;
 }
 append(...children){for(const child of children){child.parent=this;this.children.push(child);}}
 replaceChildren(){this.children=[];}
 get href(){return this.attrs.href||'';}set href(v){this.attrs.href=v;}
 scrollTo({top=0,left=0}){this.scrollTop=top;this.scrollLeft=left;}
 get src(){return this.attrs.src||'';}set src(v){this.attrs.src=v;}
 matches(selector){selector=selector.trim();if(selector.includes(' ')){const split=selector.lastIndexOf(' ');return this.matches(selector.slice(split+1))&&this.parent?.closest(selector.slice(0,split));}if(selector.startsWith('.'))return this.classes.has(selector.slice(1));if(selector==='[hidden]')return this.hidden;if(selector.startsWith('[')){const m=selector.match(/^\[([^=\]]+)(?:="([^"]*)")?\]$/);return m&&Object.hasOwn(this.attrs,m[1])&&(m[2]===undefined||this.attrs[m[1]]===m[2]);}return this.tagName===selector;}
 querySelectorAll(selector){return this.children.flatMap(c=>[...(selector.split(',').some(s=>c.matches(s))?[c]:[]),...c.querySelectorAll(selector)]);}
 querySelector(selector){return this.querySelectorAll(selector)[0]||null;}
 closest(selector){for(let e=this;e;e=e.parent)if(selector.split(',').some(s=>e.matches(s)))return e;return null;}
 contains(other){return this===other||this.children.some(c=>c.contains(other));}
 addEventListener(name,fn){(this.handlers[name]??=[]).push(fn);}
 fire(name,extra={}){for(const fn of this.handlers[name]||[])fn({target:this,button:0,preventDefault(){},...extra});}
 setAttribute(k,v){this.attrs[k]=v;}getAttribute(k){return this.attrs[k]??null;}removeAttribute(k){delete this.attrs[k];}
 focus(){const modal=doc.querySelectorAll('dialog').find(d=>d.open);if(!modal||modal.contains(this))doc.activeElement=this;}
 pause(){this.paused=true;this.pauseCount=(this.pauseCount||0)+1;}
 play(){this.paused=false;this.playCount=(this.playCount||0)+1;return Promise.resolve();}
 load(){this.loaded=(this.loaded||0)+1;this.currentTime=0;}
 showModal(){this.open=true;}
 close(){if(!this.open)return;this.open=false;closeEvents.push(()=>this.fire('close'));}
 getBoundingClientRect(){return {left:20,right:800,top:20,bottom:700};}
 requestFullscreen(){doc.fullscreenElement=this;doc.fire('fullscreenchange');return Promise.resolve();}
}
doc=new E(JSON.parse(parsed));
const all=doc.querySelectorAll('[id]'),ids=new Map(all.map(e=>[e.id,e]));assert.equal(ids.size,all.length,'unique IDs');
doc.getElementById=id=>ids.get(id)||null;doc.body=doc.querySelector('body');doc.activeElement=doc.body;doc.createElement=tag=>new E({tag,attrs:{},children:[]});
doc.exitFullscreen=()=>{doc.fullscreenElement=null;doc.fire('fullscreenchange');return Promise.resolve();};
const w=new E({tag:'window',attrs:{},children:[]});
const location={hash:''};let now=1000000;const ticks=new Map();let timerID=0;let blockHistory=false;
const context=vm.createContext({document:doc,window:w,location,history:{replaceState:(_,__,hash)=>{if(blockHistory)throw new Error('History unavailable');location.hash=hash;}},navigator:{},Element:E,Date:{now:()=>now},URL,setInterval:fn=>{ticks.set(++timerID,fn);return timerID;},clearInterval:id=>ticks.delete(id),setTimeout:()=>1,clearTimeout:()=>{},console});
for(const script of doc.querySelectorAll('script')){
 const src=script.getAttribute('src');
 if(src)vm.runInContext(fs.readFileSync(root+'/'+src.split('?')[0],'utf8'),context,{filename:src});
}
const get=id=>doc.getElementById(id);
const flush=()=>{while(closeEvents.length)closeEvents.shift()();};
const click=element=>{if(typeof element==='string')element=get(element);element.focus();element.fire('click');flush();};
const active=()=>doc.querySelectorAll(config.scene).filter(e=>!e.hidden).map(e=>e.id);
const jump=id=>{get(config.select).value=id;get(config.select).fire('change');flush();};
const elapse=ms=>{now+=ms;for(const fn of ticks.values())fn();};
const pick=selector=>doc.querySelector(selector);
const puzzle=pick('[data-word]').closest(config.scene).id;
const reflection=pick('[data-reflection]').closest(config.scene).id;
const extras=['psalms','praise','lamp','connections',puzzle,reflection];
assert.equal(new Set(extras).size,6);
const menu=get('moments-menu');
const menuButtons=menu.querySelectorAll('[data-moment]');
assert.deepEqual(menuButtons.map(b=>b.dataset.moment).sort(),[...extras].sort(),'all six activities in the header menu');
assert.equal(doc.querySelectorAll('.extra-activity').length,6);
// Every extra is reachable and hopping among extras retains the last core section.
const core=config.adult?'renewal':'discuss';
for(const destination of extras){
 jump(core);
 for(const button of menuButtons){
  menu.open=true;click(button);assert.equal(menu.open,false);assert.deepEqual(active(),[button.dataset.moment]);
  assert.equal(doc.activeElement.id,config.adult?'stage':'y-stage','menu selection moves focus into the lesson');
 }
 jump(destination);click(config.next);assert.deepEqual(active(),[core]);
 jump(destination);click(config.previous);assert.deepEqual(active(),[core]);
}
menu.open=true;doc.fire('keydown',{key:'Escape',target:menu.querySelector('summary')});assert.equal(menu.open,false);assert.equal(doc.activeElement,menu.querySelector('summary'));
// Scriptures resolve to their actual local passage; modified clicks keep the source link.
const reader=get(config.scripture),title=get(config.adult?'scripture-reader-title':'y-scripture-title');
const body=get(config.adult?'scripture-reader-body':'y-scripture-body');
const source=get(config.adult?'scripture-reader-source':'y-scripture-source');
const close=config.adult?'scripture-reader-close':'y-scripture-close';
function read(link,expected,count,phrase){
 link.fire('click',{ctrlKey:true});assert.equal(reader.open,false);
 let prevented=false;link.fire('click',{preventDefault(){prevented=true;}});
 assert.equal(prevented,true);assert.equal(reader.open,true);assert.equal(title.textContent,expected);assert.equal(body.children.length,count);
 assert.equal(source.href,link.href);assert.ok(body.children.some(p=>p.children[1].textContent.includes(phrase)));
 assert.equal(doc.querySelectorAll('video').some(v=>!v.paused),false);
 click(close);assert.equal(doc.activeElement,link);
}
jump('psalms');
for(const [scenario,expected,count,phrase] of [
 ['weary','Psalm 103:13–14',2,'we are dust'],['forgiveness','Psalm 103:8–12',5,'east is from the west'],['direction','Psalm 119:105',1,'lamp unto my feet']
]){
 click(pick(`[data-scenario="${scenario}"]`));assert.equal(get('activity-verse').hidden,true);read(get('activity-reference'),expected,count,phrase);
 click('reveal-scripture');assert.equal(get('activity-verse').hidden,false);assert.ok(get('activity-verse').textContent.includes(phrase));
 click('reveal-scripture');assert.equal(get('activity-verse').hidden,true);
}
// Praise responses stay local, use plain text, scale down, and persist through navigation.
jump('praise');click('praise-reset');
const add=word=>{get('praise-word').value=word;get('praise-form').fire('submit');};
const wall=get('praise-wall');add('  Mercy  ');assert.equal(wall.children.length,1);assert.equal(wall.children[0].children[0].textContent,'Mercy');
const firstScale=Number(wall.style['--praise-scale']);assert.equal(firstScale,26);
add('mercy');assert.equal(wall.children.length,1);add('Hope');assert.ok(Number(wall.style['--praise-scale'])<firstScale);
add('<img src=x onerror=alert(1)>');assert.equal(wall.children[2].children[0].textContent,'<img src=x onerror=alert(1)>');assert.equal(wall.querySelector('img'),null);
jump(core);jump('praise');assert.equal(wall.children.length,3);
click(wall.children[1].children[0]);assert.equal(wall.children.length,2);
for(let i=0;i<12;i++)add('blessing '+i);assert.equal(wall.children.length,12);assert.equal(get('praise-add').disabled,true);
click('praise-reset');assert.equal(wall.children.length,0);assert.equal(get('praise-empty').hidden,false);assert.equal(get('praise-add').disabled,false);
read(get('praise').querySelector('[data-scripture]'),'Psalm 103:1–5',5,'lovingkindness');
// Phrase reveal is bounded, resettable, and remembered after leaving.
jump('lamp');click('lamp-reset');
for(let i=1;i<=3;i++){click('lamp-reveal');assert.equal(get('lamp-phrase-'+i).hidden,false);assert.equal(get('lamp-count').textContent,i+' of 3 phrases');}
click('lamp-reveal');assert.equal(get('lamp-count').textContent,'3 of 3 phrases');assert.equal(get('lamp-reveal').disabled,true);
jump(core);jump('lamp');assert.equal(get('lamp-phrase-3').hidden,false);click('lamp-reset');assert.equal(get('lamp-phrase-1').hidden,true);
// All three matching rounds: wrong choice, correct choice, reveal, return, reset.
jump(core);jump('connections');click('connection-reset');
const rounds=[['Psalm 118:22',1,'stone','Matthew 21:42',1,'stone'],['Psalm 118:25–26',2,'Blessed','Matthew 21:9',1,'Hosanna'],['Psalm 110:4',1,'Melchizedek','Hebrews 5:4–10',7,'eternal salvation']];
for(let i=0;i<3;i++){
 const [ps,n,phrase,nt,m,ntPhrase]=rounds[i];
 assert.equal(get('connection-answer').hidden,true);read(get('connection-reference'),ps,n,phrase);
 click(pick(`[data-connection="${(i+1)%3}"]`));assert.equal(get('connection-answer').hidden,true);assert.match(get('connection-feedback').textContent,/Try another/);
 click(i===1?'connection-reveal':pick(`[data-connection="${i}"]`));assert.equal(get('connection-answer').hidden,false);
 assert.equal(pick(`[data-connection="${i}"]`).attrs['aria-pressed'],'true');read(get('connection-answer-reference'),nt,m,ntPhrase);
 click('connection-next');
}
assert.deepEqual(active(),[core]);jump('connections');click('connection-reset');assert.equal(get('connection-count').textContent,'Passage 1 of 3');
// Puzzle and reflection are both present on every edition and reset independently.
jump(puzzle);click(pick('[data-puzzle-reset]'));click(pick('[data-word="path"]'));assert.match(pick('[data-puzzle-feedback]').textContent,/Not quite/);
for(const word of ['word','lamp','path'])click(pick(`[data-word="${word}"]`));
assert.deepEqual([0,1,2].map(i=>get('blank-'+i).textContent),['word','lamp','path']);
jump(reflection);for(const word of ['word','lamp','path']){click(pick(`[data-reflection="${word}"]`));assert.equal(doc.querySelectorAll('[data-reflection]').filter(b=>b.attrs['aria-pressed']==='true').length,1);assert.ok(pick('[data-reflection-feedback]').textContent.length>20);}
click(pick('[data-reflection-reset]'));assert.equal(doc.querySelectorAll('[data-reflection]').some(b=>b.attrs['aria-pressed']==='true'),false);assert.equal(get('blank-2').textContent,'path');
jump(puzzle);click(pick('[data-puzzle-reset]'));assert.equal(get('blank-0').textContent,'_____');
// Every declared scripture link has a complete local passage, including dynamic answers.
for(const link of doc.querySelectorAll('[data-scripture]'))assert.ok(w.CFMExtras.scriptureFor(link.href),'locally readable passage: '+link.href);
const lookup=w.CFMExtras.scriptureFor;
for(const href of ['https://example.com/study/scriptures/ot/ps/119?id=p105','https://www.churchofjesuschrist.org/study/scriptures/ot/ps/103?id=p1-p99','https://www.churchofjesuschrist.org/study/scriptures/ot/ps/103?id=p14-p8'])assert.equal(lookup(href),null);
console.log('PASS: '+config.entry+' — six extras, menu/focus, return to core, all scripture texts, safe/scaling praise wall, three matching rounds, phrase reveal, puzzle, reflection, independent resets.');
}
