import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../', import.meta.url));
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
`,root+'/cfm906-youth.html'],{encoding:'utf8'});
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
doc.getElementById=id=>ids.get(id)||null;doc.body=doc.querySelector('body');doc.activeElement=doc.body;
doc.exitFullscreen=()=>{doc.fullscreenElement=null;doc.fire('fullscreenchange');return Promise.resolve();};
doc.createElement=tag=>new E({tag,attrs:{},children:[]});
const w=new E({tag:'window',attrs:{},children:[]});w.scrollTo=()=>{};
const location={hash:''};let now=1000000;let tick;const revoked=[];
const context=vm.createContext({document:doc,window:w,location,history:{replaceState:(_,__,hash)=>{location.hash=hash;}},Date:{now:()=>now},URL:Object.assign(class extends URL {},{createObjectURL:()=> 'blob:local-video',revokeObjectURL:x=>revoked.push(x)}),setInterval:fn=>{tick=fn;return 1;},setTimeout:()=>1,clearTimeout:()=>{},console});
for(const script of doc.querySelectorAll('script')){
 const src=script.getAttribute('src');
 if(src)vm.runInContext(fs.readFileSync(root+'/'+src.split('?')[0],'utf8'),context,{filename:src});
}
const get=id=>doc.getElementById(id),flush=()=>{while(closeEvents.length)closeEvents.shift()();};
const click=id=>{get(id).focus();get(id).fire('click');flush();};
const select=selector=>doc.querySelector(selector);
const jump=id=>{get('y-section').value=id;get('y-section').fire('change');flush();};
const active=()=>doc.querySelectorAll('.scene').filter(e=>!e.hidden).map(e=>e.id);
const key=(key,target=doc.body)=>doc.fire('keydown',{key,target});
const video=get('y-worship-video'),learning=get('y-learning-video');
assert.deepEqual(active(),['start']);assert.equal(get('y-previous').disabled,true);assert.equal(video.loaded,undefined);
click('y-next');assert.deepEqual(active(),['worship']);assert.equal(video.loaded,1);assert.match(video.querySelector('source').src,/720p-en\.mp4$/);
jump('start');jump('worship');assert.equal(video.loaded,1,'lazy media only loads once');
video.paused=false;click('y-next');assert.equal(video.paused,true);assert.deepEqual(active(),['discuss']);
click('y-psalm-open');assert.deepEqual(active(),['psalm']);assert.equal(get('y-progress').style.width,'50%');click('y-next');assert.deepEqual(active(),['discuss']);
jump('finish');assert.equal(get('y-next').disabled,false);assert.equal(get('y-next').textContent,'Back to start');click('y-next');assert.deepEqual(active(),['start']);
key('Home');assert.deepEqual(active(),['start']);key('ArrowRight');assert.deepEqual(active(),['worship']);key('ArrowRight',video);assert.deepEqual(active(),['worship']);
location.hash='#invalid';w.fire('hashchange');assert.deepEqual(active(),['worship']);
location.hash='#home-study';w.fire('hashchange');assert.deepEqual(active(),['home-study']);click('home-ideas');assert.equal(get('home-examples').hidden,false);click('home-ideas');assert.equal(get('home-examples').hidden,true);
for(const attribute of ['warmup','action']){
 const choices=doc.querySelectorAll(`[data-${attribute}]`);for(const choice of choices){choice.fire('click');assert.equal(choices.filter(c=>c.attrs['aria-pressed']==='true').length,1);assert.equal(choice.attrs['aria-pressed'],'true');}
}
jump('psalm');select('[data-word="path"]').fire('click');assert.match(get('psalm-feedback').textContent,/Not quite/);assert.equal(get('blank-0').textContent,'_____');
for(const [index,word]of ['word','lamp','path'].entries()){select(`[data-word="${word}"]`).fire('click');assert.equal(get('blank-'+index).textContent,word);assert.equal(select(`[data-word="${word}"]`).disabled,true);}
assert.match(get('psalm-feedback').textContent,/read the whole verse/);click('psalm-reset');assert.equal(get('blank-0').textContent,'_____');assert.equal(select('[data-word="word"]').disabled,false);
const scripture=select('[data-scripture]');scripture.fire('click',{metaKey:true});assert.equal(get('y-scripture').open,false);scripture.fire('click');assert.equal(get('y-scripture').open,true);assert.equal(doc.activeElement.id,'y-scripture-title');key('ArrowRight');assert.deepEqual(active(),['psalm']);click('y-scripture-close');assert.equal(doc.activeElement,scripture);

jump('worship');video.paused=false;click('y-teacher-open');assert.equal(get('y-teacher').open,true);assert.equal(video.paused,true);assert.match(get('teacher-section').textContent,/First video/);
select('[data-preview-cue="forgiveness"]').fire('click');flush();assert.equal(get('y-cue').open,true);assert.equal(get('y-teacher').open,false);assert.equal(doc.activeElement.id,'cue-title');assert.equal(get('cue-continue').textContent,'Close preview');click('cue-continue');assert.equal(video.playCount,undefined);assert.equal(doc.activeElement.id,'y-teacher-open');
function playback(v,time){v.paused=false;v.currentTime=time;v.fire('timeupdate');}
playback(video,187.8);assert.equal(get('y-cue').open,false);playback(video,188.05);assert.equal(get('y-cue').open,true);assert.equal(video.paused,true);assert.match(get('cue-title').textContent,/forgiving us/);assert.equal(get('cue-time').textContent,'0:30');
click('cue-timer');now+=10000;tick();assert.equal(get('cue-time').textContent,'0:20');click('cue-timer');now+=10000;tick();assert.equal(get('cue-time').textContent,'0:20');click('cue-timer');now+=25000;tick();assert.equal(get('cue-time').textContent,'0:00');assert.equal(video.paused,true);assert.equal(get('y-cue').open,true,'timer never closes cue or resumes video');
click('cue-continue');assert.equal(video.paused,false);assert.equal(video.playCount,1);assert.equal(doc.activeElement,video);
playback(video,187);playback(video,189);assert.equal(get('y-cue').open,false,'each checkpoint fires once');
playback(video,440.4);assert.equal(get('y-cue').open,false);playback(video,440.7);assert.equal(get('y-cue').open,true);assert.match(get('cue-title').textContent,/think about Jesus/);click('cue-close');assert.equal(video.paused,true);assert.equal(video.playCount,1,'closing does not resume');

jump('learning');get('guided-pauses').checked=false;playback(learning,154);assert.equal(get('y-cue').open,false);get('guided-pauses').checked=true;playback(learning,155);assert.equal(get('y-cue').open,false,'enabling does not fire a missed cue');
const local=select('[data-local-video="y-learning-video"]');local.files=[{name:'sunday.mp4',type:'video/mp4'}];local.fire('change');assert.equal(learning.src,'blob:local-video');assert.match(get('y-learning-file').textContent,/stays on your device/);
learning.seeking=true;playback(learning,160);learning.seeking=false;learning.fire('seeked');playback(learning,161);assert.equal(get('y-cue').open,false,'seeking past does not interrupt');
select('[data-online-video="y-learning-video"]').fire('click');assert.equal(learning.src,'');assert.deepEqual(revoked,['blob:local-video']);
playback(learning,153.1);assert.equal(get('y-cue').open,false);playback(learning,153.3);assert.equal(get('y-cue').open,true);assert.match(get('cue-title').textContent,/at home/);assert.equal(get('cue-time').textContent,'0:45');
get('y-cue').close();flush();assert.equal(learning.paused,true,'Escape or native close keeps video paused');
learning.fire('error');assert.equal(get('y-learning-error').hidden,false);learning.fire('loadeddata');assert.equal(get('y-learning-error').hidden,true);
local.files=[{name:'notes.pdf',type:'application/pdf'}];local.fire('change');assert.equal(learning.src,'');assert.equal(get('y-toast').textContent,'Choose a video file.');

click('y-class-timer');now+=65000;tick();assert.equal(get('y-class-time').textContent,'23:55');
click('y-teacher-open');select('[data-preview-cue="partner"]').fire('click');flush();click('cue-timer');now+=45000;tick();assert.equal(get('cue-time').textContent,'0:00');assert.equal(get('y-class-time').textContent,'23:10');assert.equal(learning.paused,true);
click('cue-close');click('y-class-timer');now+=300000;tick();assert.equal(get('y-class-time').textContent,'23:10');click('y-class-timer');now+=240000;tick();assert.equal(get('y-class-time').textContent,'19:10');now+=2000000;tick();assert.equal(get('y-class-time').textContent,'0:00');assert.equal(get('y-toast').textContent,'Time to close with prayer.');click('y-reset-timer');assert.equal(get('y-class-time').textContent,'25:00');
jump('discuss');const discussion=select('[data-short-timer]');discussion.fire('click');now+=12000;tick();assert.equal(get('discuss-countdown').textContent,'0:48');jump('finish');now+=60000;tick();assert.equal(get('discuss-countdown').textContent,'1:00');
click('y-fullscreen');assert.equal(doc.fullscreenElement.id,'y-app');assert.equal(get('y-fullscreen').attrs['aria-pressed'],'true');click('y-fullscreen');assert.equal(get('y-fullscreen').attrs['aria-pressed'],'false');
console.log('PASS: source markup, navigation, lazy media, keyboard guards, warmup choices, discussion prompts, scripture puzzle/modal, preview focus, all three checkpoints, one-shot pauses, seeking, guided toggle, local files/errors, independent timers, fullscreen controls.');
