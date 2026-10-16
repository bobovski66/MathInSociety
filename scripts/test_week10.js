/* Mathematical fixtures and DOM-level interaction checks; no browser required. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),{execFileSync}=require('node:child_process');
const M=require('../assets/week10/week10.js');
const close=(a,b,t=1e-12)=>assert.ok(Math.abs(a-b)<t,`${a} != ${b}`);
assert.ok(Number.isNaN(M.number('')));assert.ok(Number.isNaN(M.number('1/0')));assert.ok(Number.isNaN(M.number('2+2')));close(M.number('81/256'),.31640625);close(M.number('1e-4'),.0001);close(M.number(' 16 / 9 '),16/9);
for(const [n,steps,peak] of [[1,0,1],[3,7,16],[6,8,16],[7,16,52],[11,14,52],[26,10,40],[27,111,9232],[32,5,32]]){let c=M.collatz(n);assert.equal(c.steps,steps);assert.equal(c.peak,peak);assert.equal(c.values.at(-1),1);assert.equal(c.reachedOne,true);}
assert.equal(M.collatz(27,5).reachedOne,false);for(const x of [0,-1,1.5,NaN,Infinity,1000001])assert.throws(()=>M.collatz(x));
close(M.logistic(2,.2,3)[3],.49160192);close(M.logistic(2.8,.2,10)[10],.6511363927869906);assert.deepEqual(M.logistic(4,.5,4),[.5,1,0,0,0]);
let a=M.logistic(3.9,.4,25),b=M.logistic(3.9,.4001,25);assert.equal(M.crossing(a,b,.01),8);assert.equal(M.crossing(a,b,.1),14);assert.equal(Math.round(Math.abs(a[14]-b[14])*100000),19074);assert.ok(Math.abs(a[1]-b[1])<.0001);assert.ok(Math.abs(a[9]-b[9])<.01);
assert.equal(M.crossing(M.logistic(3.8,.4,20),M.logistic(3.8,.41,20),.05),4);
assert.equal(M.crossing(M.logistic(2.8,.4,100),M.logistic(2.8,.4001,100),.05),-1);
for(const p of [[2.8,.4,100],[3.2,.4,300],[3.83,.4,500]]){let s=M.logistic(...p),period=p[0]===2.8?1:p[0]===3.2?2:3;close(s.at(-1),s.at(-1-period),1e-9);}
for(let n=0;n<=6;n++){let pts=M.koch(n),length=0;assert.equal(pts.length,4**n+1);for(let i=1;i<pts.length;i++)length+=Math.hypot(pts[i][0]-pts[i-1][0],pts[i][1]-pts[i-1][1]);close(length,(4/3)**n,1e-9);assert.equal(M.triangles(n).length,3**n);let area=M.triangles(n).reduce((s,[a,b,c])=>s+Math.abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))/2,0);close(area/(Math.sqrt(3)/4),(.75)**n,1e-10);}
const snapshots=JSON.parse(execFileSync('python3',['scripts/verify_week10.py','--dom-json'],{encoding:'utf8'}));
function matches(el,selector){
 let parts=selector.trim().split(/\s+/),last=parts.pop();if(!simple(el,last))return false;let p=el.parentElement;
 while(parts.length){let s=parts.pop();while(p&&!simple(p,s))p=p.parentElement;if(!p)return false;p=p.parentElement;}return true;
}
function simple(el,s){if(!el)return false;let tag=s.match(/^[a-zA-Z][\w-]*/)?.[0];if(tag&&el.tagName!==tag.toUpperCase())return false;for(let m of s.matchAll(/\.([\w-]+)/g))if(!el.className.split(/\s+/).includes(m[1]))return false;for(let m of s.matchAll(/\[([\w-]+)(?:=["']?([^\]"']+)["']?)?\]/g)){if(!(m[1] in el.attrs))return false;if(m[2]!==undefined&&el.attrs[m[1]]!==m[2])return false;}return true;}
class Element{
 constructor(tag,attrs={},text=''){this.tagName=tag.toUpperCase();this.attrs={...attrs};this.children=[];this.parentElement=null;this.ownText=text;this._value=null;this.style={};this.events={};this.disabled='disabled' in attrs;this.checked='checked' in attrs;this.hidden='hidden' in attrs;this.max=attrs.max||'';this.classList={add:(...ss)=>this.className=[...new Set(this.className.split(/\s+/).filter(Boolean).concat(ss))].join(' '),remove:(...ss)=>this.className=this.className.split(/\s+/).filter(s=>!ss.includes(s)).join(' '),toggle:(s,on)=>{let has=this.className.split(/\s+/).includes(s),yes=on===undefined?!has:on;yes?this.classList.add(s):this.classList.remove(s);return yes;}};}
 get id(){return this.attrs.id||'';}get className(){return this.attrs.class||'';}set className(x){this.attrs.class=x;}
 get dataset(){let d={};Object.entries(this.attrs).filter(([k])=>k.startsWith('data-')).forEach(([k,v])=>d[k.slice(5).replace(/-([a-z])/g,(_,x)=>x.toUpperCase())]=v);return d;}
 get value(){if(this._value!==null)return this._value;if(this.tagName==='SELECT'){let o=this.children.find(x=>'selected' in x.attrs)||this.children[0];return o?.attrs.value||'';}return this.attrs.value||'';}set value(v){this._value=String(v);if(this.tagName==='SELECT'&&!this.children.some(x=>x.attrs.value===this._value))this._value='';}
 get selectedOptions(){return this.children.filter(x=>x.attrs.value===this.value);}
 get textContent(){return this.ownText+this.children.map(x=>x.textContent+(x.tail||'')).join('');}set textContent(x){this.ownText=String(x);this.children=[];}
 set innerHTML(x){this._html=x;this.children=[];this.ownText='';}get innerHTML(){return this._html||'';}
 getAttribute(k){return Object.hasOwn(this.attrs,k)?this.attrs[k]:null;}setAttribute(k,v){this.attrs[k]=String(v);}removeAttribute(k){delete this.attrs[k];}
 querySelectorAll(q){let selectors=q.split(','),out=[];for(let c of this.children){if(selectors.some(s=>matches(c,s)))out.push(c);out.push(...c.querySelectorAll(q));}return out;}querySelector(q){return this.querySelectorAll(q)[0]||null;}
 closest(q){for(let x=this;x;x=x.parentElement)if(matches(x,q))return x;return null;}
 append(...nodes){for(let n of nodes){n.parentElement=this;this.children.push(n);}}replaceChildren(...nodes){this.children=[];this.ownText='';this.append(...nodes);}after(n){let p=this.parentElement;if(p){n.parentElement=p;p.children.splice(p.children.indexOf(this)+1,0,n);}}remove(){let p=this.parentElement;if(p)p.children=p.children.filter(n=>n!==this);}
 addEventListener(type,fn){(this.events[type]??=[]).push(fn);}dispatch(type,event={}){for(let fn of this.events[type]||[])fn({preventDefault(){},...event});}click(){if(!this.disabled)this.dispatch('click');}focus(){this.focused=true;}
}
function fromJSON(o){let e=new Element(o.tag,o.attrs,o.text);e.tail=o.tail;for(let c of o.children)e.append(fromJSON(c));return e;}
function open(file,initial={}){
 const root=fromJSON(snapshots[file]),data={...initial},events={},window={prints:0,addEventListener(k,fn){(events[k]??=[]).push(fn);},print(){this.prints++;for(const f of events.beforeprint||[])f();}},document={readyState:'complete',querySelectorAll:q=>root.querySelectorAll(q),querySelector:q=>root.querySelector(q),getElementById:id=>root.querySelectorAll('[id]').find(x=>x.id===id)||null,createElement:tag=>new Element(tag)};
 const sandbox={document,window,localStorage:{getItem:k=>data[k]??null,setItem:(k,v)=>data[k]=String(v)},Math,console};sandbox.globalThis=sandbox;vm.runInNewContext(fs.readFileSync('assets/week10/week10.js','utf8'),sandbox,{filename:'week10.js'});return{root,document,window,data,$:id=>document.getElementById(id),events};
}
for(const file of Object.keys(snapshots)){
 const t=open(file);
 assert.ok(t.document.querySelector('h1'));
 if(t.document.querySelector('[data-answer-store]')){
  const fields=t.document.querySelectorAll('[data-answer]'),groups=t.document.querySelectorAll('[data-check-group]');
  groups[0].querySelector('[data-check]').click();assert.ok(fields[0].closest('.question').className.includes('incorrect'),'blank numerical answer is rejected');
  for(let f of fields){f.value=f.dataset.answer;f.dispatch('input');}
  for(let g of groups)g.querySelector('[data-check]').click();assert.equal(t.$('progressText').textContent,`${groups.length} / ${groups.length} sections checked`);
  // Changing a mastered response invalidates only its section.
  fields[0].value='';fields[0].dispatch('input');assert.equal(t.$('progressText').textContent,`${groups.length-1} / ${groups.length} sections checked`);
  let again=open(file,t.data);assert.equal(again.$(fields[1].id).value,fields[1].value,'saved response survives reload');
  t.document.querySelector('[data-print-work]').click();assert.equal(t.window.prints,0,'printing completed work requires a name');t.$('studentName').value='Test Student';t.document.querySelector('[data-print-work]').click();assert.equal(t.window.prints,1);assert.equal(t.document.querySelectorAll('.print-answer').length,fields.length);assert.equal(t.$('printName').textContent,'Student: Test Student');
 }
}
// Legacy data is loaded without assuming unchecked responses are complete.
let old=open('labs/week10_lab.html',{math107_week10_lab_v2:JSON.stringify({p1a:'35',p1b:'35.1',p1c:'.1',p1d:'7.29',p1e:'right',done:[true,true,true,true,true]})});assert.equal(old.$('p1a').value,'35');assert.equal(old.$('progressText').textContent,'1 / 5 sections checked');
let app=open('applications/week10_application.html');assert.equal(app.$('fishGap').textContent,'10');app.$('fishN').value='14';app.$('fishN').dispatch('input');assert.equal(app.$('fishGap').textContent,'19,074');
let explorer=open('demos/fractal_recursion.html');assert.equal(explorer.$('colSteps').textContent,'10');assert.equal(explorer.$('colPeak').textContent,'40');assert.equal(explorer.$('logCross').textContent,'n = 13'); // threshold .05 for this pair
explorer.$('tab-frac').click();assert.equal(explorer.$('panel-frac').hidden,false);assert.equal(explorer.$('panel-log').hidden,true);
explorer.$('fracStage').value='4';explorer.$('fracStage').dispatch('input');assert.equal(explorer.$('kochCount').textContent,'256');assert.equal(explorer.$('sierCount').textContent,'81');
explorer.$('colStart').value='27';explorer.$('colStart').dispatch('input');assert.equal(explorer.$('colSteps').textContent,'111');assert.equal(explorer.$('colPeak').textContent,'9,232');explorer.$('colStep').value='111';explorer.$('colStep').dispatch('input');assert.ok(explorer.$('colStepRead').textContent.includes('reached 1'));
explorer.$('logStart').value='.99';explorer.$('logDelta').value='.1';explorer.$('logDelta').dispatch('input');assert.ok(explorer.$('logError').textContent.includes('between 0 and 1'));assert.equal(explorer.$('logCross').textContent,'—');
let ai=open('applications/week10_ai.html');ai.$('aiChoose').children[1].click();assert.ok(ai.$('aiContext').textContent.endsWith('flickering'));ai.$('aiNext').children[0].click();assert.ok(ai.$('aiJoint').textContent.includes('0.28'));
console.log('PASS: exact mathematical fixtures, geometric lengths/areas, all six page initializations, partial answer feedback, edits, autosave/reload, legacy responses, print answers/name, tabs, invalid inputs, Collatz tracing, fish slider, and AI branching.');
