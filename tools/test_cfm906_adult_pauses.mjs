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
for(const config of lessons.filter(lesson=>lesson.adult)){
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
doc.getElementById=id=>ids.get(id)||null;doc.documentElement=doc.querySelector('html');doc.body=doc.querySelector('body');doc.activeElement=doc.body;doc.createElement=tag=>new E({tag,attrs:{},children:[]});
doc.exitFullscreen=()=>{doc.fullscreenElement=null;doc.fire('fullscreenchange');return Promise.resolve();};
const w=new E({tag:'window',attrs:{},children:[]});
const location={hash:''};let now=1000000;const ticks=new Map();let timerID=0;let blockHistory=false;
const context=vm.createContext({document:doc,window:w,location,history:{replaceState:(_,__,hash)=>{if(blockHistory)throw new Error('History unavailable');location.hash=hash;}},navigator:{},Element:E,Date:{now:()=>now},URL:Object.assign(class extends URL {},{createObjectURL:()=> 'blob:adult-video',revokeObjectURL:()=>{}}),setInterval:fn=>{ticks.set(++timerID,fn);return timerID;},clearInterval:id=>ticks.delete(id),setTimeout:()=>1,clearTimeout:()=>{},console});
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
const cue=get('lesson-cue'),video=get('sabbath-video'),school=get('school-video');
const pick=selector=>doc.querySelector(selector);
const key=key=>{w.fire('keydown',{key,target:doc.body});flush();};
const playback=(v,time)=>{v.paused=false;v.currentTime=time;v.fire('timeupdate');};
const resetSource=v=>{pick(`[data-restore-video="${v.id}"]`).fire('click');flush();};
const pauseAt=(v,section,time)=>{resetSource(v);jump(section);v.currentTime=time-.1;v.fire('seeked');playback(v,time-.1);assert.equal(cue.open,false);playback(v,time+.05);assert.equal(cue.open,true);assert.equal(v.paused,true);};
const source=fs.readFileSync(root+config.entry,'utf8');
assert.equal(get('guided-pauses').checked,true);
assert.equal(source.includes('sunday-notes.pdf'),false,'adult pauses have no handout dependency');
assert.ok(source.includes('<dd>12:23</dd>')&&source.includes('<dd>5:07</dd>'));
const rundown=source.match(/<dl class="rundown">([\s\S]*?)<\/dl>/)[1];
const plannedSeconds=[...rundown.matchAll(/<dd>(\d+):(\d+)<\/dd>/g)].map(([,minutes,seconds])=>Number(minutes)*60+Number(seconds));
assert.equal(plannedSeconds.reduce((total,seconds)=>total+seconds,0),1500,'the displayed plan, including pauses and buffer, fits 25 minutes');
assert.equal(doc.querySelectorAll('video').length,2,'both full videos remain');
// Previewing all prompts leaves video positions and real checkpoints unchanged.
jump('worship');video.currentTime=100;
for(const button of doc.querySelectorAll('[data-preview-cue]')){
 click('guide-toggle');click(button);assert.equal(cue.open,true);assert.equal(get('lesson-guide').open,false);assert.equal(doc.activeElement.id,'cue-title');
 assert.equal(get('cue-continue').textContent,'Close preview');click('cue-continue');assert.equal(doc.activeElement.id,'guide-toggle');
 assert.equal(video.playCount||0,0);assert.equal(school.playCount||0,0);assert.equal(video.currentTime,100);
}
// First prompt, independent timers, keyboard guard, and explicit resume.
pauseAt(video,'worship',188);assert.match(get('cue-title').textContent,/willingness to forgive/);assert.equal(get('cue-time').textContent,'0:30');
key('ArrowRight');assert.deepEqual(active(),['worship']);key('Home');assert.deepEqual(active(),['worship']);
click('timer-toggle');click('cue-timer');elapse(10000);assert.equal(get('cue-time').textContent,'0:20');assert.equal(get('timer-display').textContent,'24:50');
click('cue-timer');elapse(5000);assert.equal(get('cue-time').textContent,'0:20');click('cue-timer');elapse(25000);
assert.equal(get('cue-time').textContent,'0:00');assert.equal(get('timer-display').textContent,'24:20');assert.equal(cue.open,true);assert.equal(video.paused,true);assert.equal(video.playCount||0,0);
click('cue-continue');assert.equal(video.paused,false);assert.equal(video.playCount,1);assert.equal(doc.activeElement,video);
playback(video,187);playback(video,189);assert.equal(cue.open,false,'replaying an already used checkpoint does not interrupt');
// Second prompt, close, native Escape, and media play while a prompt is open.
playback(video,440.4);assert.equal(cue.open,false);playback(video,440.7);assert.equal(cue.open,true);assert.match(get('cue-title').textContent,/worship more fully/);
video.paused=false;video.fire('play');assert.equal(video.paused,true,'media keys cannot resume behind the prompt');
click('cue-close');assert.equal(cue.open,false);assert.equal(video.paused,true);assert.equal(video.playCount,1);
pauseAt(school,'learning',153.2);assert.equal(get('cue-time').textContent,'0:45');assert.match(get('cue-title').textContent,/study at home/);
cue.fire('cancel');flush();assert.equal(cue.open,false);assert.equal(school.paused,true);
// Starting over from a pause restores focus and preserves class time and position.
pauseAt(video,'worship',188);click('cue-timer');elapse(3000);const classTime=get('timer-display').textContent,position=video.currentTime;
click(cue.querySelector('[data-lesson-start]'));assert.deepEqual(active(),['welcome']);assert.equal(doc.activeElement.id,'welcome-title');assert.equal(cue.open,false);assert.equal(video.paused,true);assert.equal(video.currentTime,position);assert.equal(get('timer-display').textContent,classTime);
const cueTime=get('cue-time').textContent;elapse(1000);assert.equal(get('cue-time').textContent,cueTime,'navigation cancels the prompt timer');
// Backdrop close keeps media paused.
pauseAt(video,'worship',440.5);cue.fire('click',{clientX:0,clientY:0});flush();assert.equal(cue.open,false);assert.equal(video.paused,true);
// Disabling guided pauses consumes crossed checkpoints without delayed interruptions.
resetSource(school);jump('learning');get('guided-pauses').checked=false;playback(school,154);assert.equal(cue.open,false);
get('guided-pauses').checked=true;playback(school,155);assert.equal(cue.open,false);
// A local copy uses the same pauses; seeking past a checkpoint skips it.
const local=pick('[data-for-video="school-video"]');local.files=[{name:'sunday.mp4',type:'video/mp4'}];local.fire('change');assert.equal(school.src,'blob:adult-video');
school.seeking=true;playback(school,160);school.seeking=false;school.fire('seeked');playback(school,161);assert.equal(cue.open,false);
playback(school,150);playback(school,154);assert.equal(cue.open,false,'seeking past consumes the checkpoint');
resetSource(school);playback(school,153.3);assert.equal(cue.open,true);click('cue-continue');assert.equal(school.paused,false);
// Fullscreen page keeps the dialog; native video fullscreen exits for it.
click('fullscreen-toggle');assert.equal(doc.fullscreenElement,doc.documentElement);pauseAt(video,'worship',188);assert.equal(doc.fullscreenElement,doc.documentElement);click('cue-close');
resetSource(video);jump('worship');doc.fullscreenElement=video;playback(video,188.1);await new Promise(resolve=>setImmediate(resolve));flush();
assert.equal(doc.fullscreenElement,null);assert.equal(cue.open,true);click('cue-close');
// A navigation while waiting for fullscreen exit cancels the pending prompt.
resetSource(video);jump('worship');let finishExit;doc.exitFullscreen=()=>new Promise(resolve=>{finishExit=()=>{doc.fullscreenElement=null;resolve();};});
doc.fullscreenElement=video;playback(video,188.1);click('lesson-start');finishExit();await new Promise(resolve=>setImmediate(resolve));flush();
assert.equal(cue.open,false);assert.deepEqual(active(),['welcome']);assert.equal(doc.activeElement.id,'welcome-title');
console.log('PASS: adult pause previews, all three checkpoints, manual resume, independent clocks, no handouts, keyboard/modal focus, back to start, seek/toggle/local playback, fullscreen and pending-prompt cancellation.');
}
