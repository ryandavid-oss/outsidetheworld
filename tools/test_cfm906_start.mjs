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
vm.runInContext(fs.readFileSync(root+config.script,'utf8'),context);
const get=id=>doc.getElementById(id);
const flush=()=>{while(closeEvents.length)closeEvents.shift()();};
const click=element=>{if(typeof element==='string')element=get(element);element.focus();element.fire('click');flush();};
const active=()=>doc.querySelectorAll(config.scene).filter(e=>!e.hidden).map(e=>e.id);
const jump=id=>{get(config.select).value=id;get(config.select).fire('change');flush();};
const elapse=ms=>{now+=ms;for(const fn of ticks.values())fn();};
const headerHome=get('lesson-start');
assert.ok(headerHome && !headerHome.closest('dialog'),'header has a visible start control');
for(const dialog of doc.querySelectorAll('dialog'))assert.ok(dialog.querySelector('[data-lesson-start]'),'every modal has a start control');
function assertHome(){
 assert.deepEqual(active(),[config.first]);
 assert.equal(location.hash,'#'+config.first);
 assert.equal(get(config.select).value,config.first);
 assert.equal(doc.activeElement.id,config.heading,'focus remains at the opening after queued close events');
 assert.equal(doc.querySelectorAll('dialog').some(d=>d.open),false);
 assert.equal(doc.querySelectorAll('video').some(v=>!v.paused),false);
 assert.equal(get(config.previous).disabled,true);
 assert.equal(get(config.app).scrollTop,0,'fullscreen container is scrolled to the top');
}
// Every main and optional section, including a scrolled fullscreen presentation.
for(const section of doc.querySelectorAll(config.scene)){
 jump(section.id);
 doc.querySelectorAll('video').forEach(v=>{v.paused=false;v.currentTime=120;});
 get(config.app).scrollTop=850;w.scrollTop=900;
 click(headerHome);assertHome();assert.equal(w.scrollTop,0);
 assert.ok(doc.querySelectorAll('video').every(v=>v.currentTime===120),'return does not rewind media');
}
doc.fullscreenElement=get(config.app);jump(config.last);get(config.app).scrollTop=600;click(headerHome);assertHome();assert.equal(doc.fullscreenElement,get(config.app),'page fullscreen is preserved');
// Final section and the Home shortcut use the same action.
jump(config.last);assert.equal(get(config.next).disabled,false);assert.equal(get(config.next).textContent,'Back to start');click(config.next);assertHome();
jump(config.optional);const keyboard=config.adult?w:doc;keyboard.fire('keydown',{key:'Home',target:doc.body});flush();assertHome();
// Return directly from teacher notes and a scripture popover.
jump(config.videoSection);click(config.teacherOpen);assert.equal(get(config.teacher).open,true);click(get(config.teacher).querySelector('[data-lesson-start]'));assertHome();
jump(config.optional);click(doc.querySelector('[data-scripture]'));assert.equal(get(config.scripture).open,true);click(get(config.scripture).querySelector('[data-lesson-start]'));assertHome();
// A running class timer and student responses survive navigation.
click(config.timer);elapse(10000);const before=get(config.clock).textContent;assert.equal(before,'24:50');
if(config.adult){
 jump('praise');get('praise-word').value='mercy';get('praise-form').fire('submit');click(headerHome);assertHome();jump('praise');assert.equal(get('praise-wall').children[0].children[0].textContent,'mercy');
 get('moments-menu').open=true;
}else{
 const choice=doc.querySelector('[data-warmup]');click(choice);jump('learning');click(headerHome);assertHome();assert.equal(choice.attrs['aria-pressed'],'true');
 jump('worship');const v=get('y-worship-video');v.currentTime=188.1;v.paused=false;v.fire('timeupdate');flush();assert.equal(get('y-cue').open,true);
 click('cue-timer');const plays=v.playCount||0;click(get('y-cue').querySelector('[data-lesson-start]'));assertHome();assert.equal(v.playCount||0,plays,'leaving a cue never resumes playback');
 click('y-teacher-open');click(doc.querySelector('[data-preview-cue]'));assert.equal(get('y-cue').open,true);click(get('y-cue').querySelector('[data-lesson-start]'));assertHome();
}
click(headerHome);assertHome();if(config.adult)assert.equal(get('moments-menu').open,false);
assert.equal(get(config.clock).textContent,before,'timer is not reset');elapse(5000);assert.equal(get(config.clock).textContent,'24:45','running timer stays running');
// Navigation still works if the browser cannot update the URL.
jump(config.last);blockHistory=true;click(headerHome);assert.deepEqual(active(),[config.first]);assert.equal(doc.activeElement.id,config.heading);
console.log('PASS: '+config.entry+' — start from all sections, all modals, final button, Home key, fullscreen scroll, paused media, preserved timer/responses, blocked history.');
}
