/* Independent rational-arithmetic oracles and actual-page runtime checks. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),{execFileSync}=require('node:child_process');
const M=require('../assets/week1/week1.js');
const close=(a,b,t=1e-10)=>assert.ok(Math.abs(a-b)<=1e-9+t*Math.max(1,Math.abs(a),Math.abs(b)),String(a)+' != '+String(b));
const snapshots=JSON.parse(execFileSync('python3',['scripts/verify_week1.py','--dom-json'],{encoding:'utf8',maxBuffer:4*1024*1024}));
function matches(el,selector){
 let parts=selector.trim().split(/\s+/),last=parts.pop();if(!simple(el,last))return false;let p=el.parentElement;
 while(parts.length){let s=parts.pop();while(p&&!simple(p,s))p=p.parentElement;if(!p)return false;p=p.parentElement;}return true;
}
function simple(el,s){if(!el)return false;let tag=s.match(/^[a-zA-Z][\w-]*/)?.[0];if(tag&&el.tagName!==tag.toUpperCase())return false;for(let m of s.matchAll(/\.([\w-]+)/g))if(!el.className.split(/\s+/).includes(m[1]))return false;for(let m of s.matchAll(/\[([\w-]+)(?:=["']?([^\]"']+)["']?)?\]/g)){if(!(m[1] in el.attrs))return false;if(m[2]!==undefined&&el.attrs[m[1]]!==m[2])return false;}return true;}
class Element{
 constructor(tag,attrs={},text=''){this.tagName=tag.toUpperCase();this.attrs={...attrs};this.children=[];this.parentElement=null;this.ownText=text;this._value=null;this.style={};this.events={};this.disabled='disabled' in attrs;this.checked='checked' in attrs;this.hidden='hidden' in attrs;this.max=attrs.max||'';this.classList={add:(...ss)=>this.className=[...new Set(this.className.split(/\s+/).filter(Boolean).concat(ss))].join(' '),remove:(...ss)=>this.className=this.className.split(/\s+/).filter(s=>!ss.includes(s)).join(' '),toggle:(s,on)=>{let has=this.className.split(/\s+/).includes(s),yes=on===undefined?!has:on;yes?this.classList.add(s):this.classList.remove(s);return yes;}};}
 get previousElementSibling(){return this.parentElement?.children[this.parentElement.children.indexOf(this)-1]||null;}
 get id(){return this.attrs.id||'';}get className(){return this.attrs.class||'';}set className(x){this.attrs.class=x;}
 get dataset(){let d={};Object.entries(this.attrs).filter(([k])=>k.startsWith('data-')).forEach(([k,v])=>d[k.slice(5).replace(/-([a-z])/g,(_,x)=>x.toUpperCase())]=v);return d;}
 get value(){if(this._value!==null)return this._value;if(this.tagName==='TEXTAREA')return this.ownText;if(this.tagName==='SELECT'){let o=this.children.find(x=>'selected' in x.attrs)||this.children[0];return o?.attrs.value||'';}return this.attrs.value||'';}set value(v){this._value=String(v);if(this.tagName==='SELECT'&&!this.children.some(x=>x.attrs.value===this._value))this._value='';}
 get selectedOptions(){return this.children.filter(x=>x.attrs.value===this.value);}
 get textContent(){return this.ownText+this.children.map(x=>x.textContent+(x.tail||'')).join('');}set textContent(x){this.ownText=String(x);this.children=[];}
 set innerHTML(x){this._html=x;this.children=[];this.ownText='';}get innerHTML(){return this._html||'';}
 hasAttribute(k){return Object.hasOwn(this.attrs,k);}
 getAttribute(k){return Object.hasOwn(this.attrs,k)?this.attrs[k]:null;}setAttribute(k,v){this.attrs[k]=String(v);}removeAttribute(k){delete this.attrs[k];}
 querySelectorAll(q){let selectors=q.split(','),out=[];for(let c of this.children){if(selectors.some(s=>matches(c,s)))out.push(c);out.push(...c.querySelectorAll(q));}return out;}querySelector(q){return this.querySelectorAll(q)[0]||null;}
 closest(q){for(let x=this;x;x=x.parentElement)if(matches(x,q))return x;return null;}
 append(...nodes){for(let n of nodes){n.parentElement=this;this.children.push(n);}}replaceChildren(...nodes){this.children=[];this.ownText='';this._html='';this.append(...nodes);}after(n){let p=this.parentElement;if(p){n.parentElement=p;p.children.splice(p.children.indexOf(this)+1,0,n);}}remove(){let p=this.parentElement;if(p)p.children=p.children.filter(n=>n!==this);}
 addEventListener(type,fn){(this.events[type]??=[]).push(fn);}dispatch(type,event={}){for(let fn of this.events[type]||[])fn({preventDefault(){},...event});}click(){if(!this.disabled)this.dispatch('click');}focus(){this.focused=true;}scrollIntoView(o){this.scrolled=o;}
}
function fromJSON(o){let e=new Element(o.tag,o.attrs,o.text);e.tail=o.tail;for(let c of o.children)e.append(fromJSON(c));return e;}
function open(file,initial={},rng=()=>.123456789){
 const root=fromJSON(snapshots[file]),data={...initial},events={},window={prints:0,confirm:()=>true,addEventListener(k,fn){(events[k]??=[]).push(fn);},print(){this.prints++;for(const f of events.beforeprint||[])f();}},document={readyState:'complete',querySelectorAll:q=>root.querySelectorAll(q),querySelector:q=>root.querySelector(q),getElementById:id=>root.querySelectorAll('[id]').find(x=>x.id===id)||null,createElement:tag=>new Element(tag)};
 const sandbox={document,window,localStorage:{getItem:k=>{if(initial.__failStorage)throw Error('Storage disabled');return data[k]??null;},setItem:(k,v)=>{if(initial.__failStorage)throw Error('Storage disabled');data[k]=String(v);},removeItem:k=>{if(initial.__failStorage)throw Error('Storage disabled');delete data[k];}},Math:Object.assign(Object.create(Math),{random:rng}),console};sandbox.globalThis=sandbox;const script=root.querySelectorAll('script').find(e=>e.getAttribute('src')?.startsWith('../assets/')).getAttribute('src').slice(3);vm.runInNewContext(fs.readFileSync(script,'utf8'),sandbox,{filename:script});return{root,document,window,data,$:id=>document.getElementById(id),events};
}

for(const raw of ['', ' ','banana','1/0','Infinity','2abc','2+2'])assert.ok(Number.isNaN(M.number(raw)));
assert.equal(M.number('0'),0);assert.equal(M.number('−12'),-12);close(M.number('7/3'),7/3);close(M.number('1e-4'),.0001);
const oracle=JSON.parse(execFileSync('python3',['-c',String.raw`
from fractions import Fraction as F
import random,json,math
r=random.Random(10701);out={'sequences':[],'fractions':[]}
for _ in range(250):
 start=F(r.randrange(-80,81),4);d=F(r.randrange(-20,41),4);factor=F(r.randrange(-10,11),4);n=r.randrange(21);a=[start];b=[start]
 for i in range(n):a.append(a[-1]+d);b.append(b[-1]*factor)
 out['sequences'].append({'start':float(start),'d':float(d),'r':float(factor),'steps':n,'a':list(map(float,a)),'b':list(map(float,b))})
for _ in range(250):
 a=r.randrange(-1001,1002);b=r.choice([x for x in range(-100,101) if x]);c=r.randrange(-1001,1002);d=r.choice([x for x in range(-100,101) if x]);x=F(a,b);y=F(c,d)
 out['fractions'].append({'args':[a,b,c,d],'first':[x.numerator,x.denominator,float(x)],'second':[y.numerator,y.denominator,float(y)],'equal':x==y,'left':a*d,'right':b*c})
print(json.dumps(out))
`],{encoding:'utf8',maxBuffer:3*1024*1024}));
for(const f of oracle.sequences){const s=M.sequences(f.start,f.d,f.r,f.steps);assert.equal(s.additive.length,f.steps+1);s.additive.forEach((x,i)=>close(x,f.a[i]));s.multiplicative.forEach((x,i)=>close(x,f.b[i]));}
for(const f of oracle.fractions){const s=M.compare(...f.args);assert.equal(s.equal,f.equal);assert.equal(s.left,f.left);assert.equal(s.right,f.right);for(const key of ['first','second']){assert.equal(s[key].n,f[key][0]);assert.equal(s[key].d,f[key][1]);close(s[key].value,f[key][2]);}}
for(const args of [[0,1,2,-1],[0,1,2,1.5],[NaN,1,2,5],[0,1,Infinity,2],[0,1,2,61],[1e6,0,10,60]])assert.throws(()=>M.sequences(...args));
for(const args of [[1,0],[1.5,2],[1,Infinity],[1000001,2]])assert.throws(()=>M.fraction(...args));
for(const expression of ['0+(-15)+8+(-5)','-15+8-5','0 − 15 + 8 − 5','0 + (−15) + (+8) + (−5)'])assert.ok(M.answer(expression,'0-15+8-5','diver'));
for(const expression of ['-12','0-15-8+5','0-15+8',''])assert.ok(!M.answer(expression,'0-15+8-5','diver'));
assert.ok(M.answer(' 4, 9,12,7,3,15,1 ','4,9,12,7,3,15,1','csv'));assert.ok(!M.answer('4,9,12,7,3,15,2','4,9,12,7,3,15,1','csv'));assert.ok(M.answer(' SAT  on the mat ','sat on the mat','words'));assert.ok(!M.answer('sat on mat','sat on the mat','words'));
let stops=[0];for(const p of [-15,-7,-12])stops=M.record(stops,p);assert.deepEqual(stops,[0,-15,-7,-12]);assert.throws(()=>M.record(stops,-12));assert.throws(()=>M.record([0],-14));for(const bad of [[],[null],[0,-15,-8],[0,-15,-7,-12,0]])assert.throws(()=>M.path(bad));
assert.deepEqual(M.decode('42,17,8,55,91').words,['cat','sat','on','the','mat']);for(const bad of ['', '42,banana','42,999','42,NaN','42,1/2'])assert.throws(()=>M.decode(bad));

let checked=0;
for(const file of Object.keys(snapshots)){
 const page=open(file),form=page.document.querySelector('[data-answer-store]');if(!form){page.document.querySelector('[data-print-page]').click();assert.equal(page.window.prints,1);continue;}
 const fields=form.querySelectorAll('[data-answer]'),groups=form.querySelectorAll('[data-check-group]');
 for(const g of groups){g.querySelector('[data-check]').click();assert.ok(g.querySelector('.section-feedback').textContent.includes(g.hasAttribute('data-requires-path')?'Record all three':'0 of'));}
 for(const e of fields){e.value=e.dataset.answer;e.dispatch('input');checked++;}
 if(file==='labs/week1_lab.html')for(const stop of [-15,-7,-12]){page.$('diverMarker').value=stop;page.$('diverMarker').dispatch('input');page.$('recordMove').click();}
 for(const g of groups){g.querySelector('[data-check]').click();assert.ok(g.querySelector('.section-feedback').textContent.includes(g.querySelector('textarea')?'All numerical and choice responses are correct.':'Every response is correct.'));}
 for(const e of fields)assert.equal(e.getAttribute('aria-invalid'),'false');
 if(fields.length){const first=fields[0];first.value='';first.dispatch('input');const g=first.closest('[data-check-group]');g.querySelector('[data-check]').click();assert.ok(first.closest('.question').querySelector('.field-feedback').textContent.startsWith('Enter a response.'));first.value=first.dataset.answer;first.dispatch('input');g.querySelector('[data-check]').click();}
 const written=form.querySelector('textarea[data-save]');if(written){written.value='The percentage increase grows because it is based on a larger current value.';written.dispatch('input');}
 const key=form.dataset.answerStore,legacy=form.dataset.legacyStore,saved=JSON.parse(page.data[key]);assert.ok(saved.fields);const restored=open(file,{[key]:page.data[key]});if(written)assert.equal(restored.$(written.id).value,written.value);
 if(legacy){const values=Object.fromEntries(fields.map(e=>[e.id,e.dataset.answer])),old=values,r=open(file,{[legacy]:JSON.stringify(old)});for(const e of fields)assert.equal(r.$(e.id).value,e.dataset.answer);const partialValues={[fields[0].id]:fields[0].dataset.answer},partial=open(file,{[legacy]:JSON.stringify(partialValues)});if(partial.$('progressText')){const expected=groups.filter(g=>{const es=g.querySelectorAll('[data-answer]');return es.length===1&&es[0].id===fields[0].id;}).length;assert.ok(partial.$('progressText').textContent.startsWith(expected+' /'));}else assert.ok(fields.slice(1).some(e=>partial.$(e.id).value===''));}
 const print=page.document.querySelector('[data-print-work]');print.click();assert.equal(page.window.prints,0);page.$('studentName').value='Student Example';print.click();assert.equal(page.window.prints,1);assert.equal(page.$('printName').textContent,'Student: Student Example');assert.equal(page.document.querySelectorAll('.print-answer').length,form.querySelectorAll('.question input,.question select,.question textarea').length);for(const fn of page.events.afterprint||[])fn();assert.equal(page.document.querySelectorAll('.print-answer').length,0);
 const disabled=open(file,{__failStorage:true});assert.ok(disabled.$('saveStatus').textContent.includes('unavailable'));if(fields.length){disabled.$(fields[0].id).value=fields[0].dataset.answer;disabled.$(fields[0].id).dispatch('input');}
}
assert.equal(checked,53);
const originalSchemas=JSON.parse(fs.readFileSync('scripts/week1_response_contracts.json','utf8'));
for(const [file,schema] of Object.entries(originalSchemas)){
 const fresh=open(file),form=fresh.document.querySelector('[data-answer-store]');if(!form||!form.dataset.legacyStore)continue;
 const values={};for(const field of schema){const id=field.attrs.id;if(id==='printStudentName')continue;const el=fresh.$(id);values[id]=field.tag==='textarea'?'Preserved earlier explanation for '+id:el.dataset.answer??(field.options.find(x=>x[0])?.[0]||'');}
 const legacy=values,restored=open(file,{[form.dataset.legacyStore]:JSON.stringify(legacy)});
 for(const [id,value] of Object.entries(values))assert.equal(restored.$(id).value,String(value));
}

const renderArg=process.argv.find(x=>x.startsWith('--render-dir='));
const renderDir=renderArg?.slice('--render-dir='.length);
if(renderDir)fs.mkdirSync(renderDir,{recursive:true});
function capture(page,id,name){if(renderDir)fs.writeFileSync(require('node:path').join(renderDir,name+'.svg'),page.$(id).innerHTML);}
function enter(page,id,value){page.$(id).value=value;page.$(id).dispatch('input');}

// Exercise the actual controls, including invalid input clearing and all four presets.
const explorer=open('demos/number_systems.html');
assert.ok(explorer.$('addText').textContent.includes('Final value: 12.'));
assert.ok(explorer.$('multText').textContent.includes('Final value: 15.1875.'));
assert.equal(explorer.$('sequenceTable').querySelectorAll('tbody tr').length,6);
for(const id of ['c','sequencePlot'])assert.ok(explorer.$(id).innerHTML.includes('>0</text>'),'The shared value scale must label zero.');
capture(explorer,'c','sequence-original-numberline');capture(explorer,'sequencePlot','sequence-original-history');capture(explorer,'fractionPlot','fractions-equivalent');
for(const [preset,a,b] of [['shrink',3,.25],['alternate',3,-.25],['zero',10,0],['original',12,15.1875]]){
 explorer.document.querySelectorAll('[data-recursion-preset]').find(x=>x.dataset.recursionPreset===preset).click();
 assert.ok(explorer.$('addText').textContent.includes('Final value: '+a+'.'));
 assert.ok(explorer.$('multText').textContent.includes('Final value: '+b+'.'));
 assert.equal(explorer.$('explorerResults').hidden,false);
 if(preset==='alternate'){capture(explorer,'c','sequence-alternate-numberline');capture(explorer,'sequencePlot','sequence-alternate-history');}
}
for(const value of ['', ' ', '2abc', 'Infinity', '1e309', '21', '-21']){
 enter(explorer,'startNumber',value);assert.equal(explorer.$('explorerResults').hidden,true);assert.ok(explorer.$('explorerError').textContent);for(const id of ['c','sequencePlot','sequenceTable'])assert.equal(explorer.$(id).innerHTML,'');
}
enter(explorer,'startNumber',0);assert.equal(explorer.$('explorerResults').hidden,false);
enter(explorer,'steps',1.5);assert.equal(explorer.$('explorerResults').hidden,true);
enter(explorer,'steps',15);assert.equal(explorer.$('sequenceTable').querySelectorAll('tbody tr').length,16);
enter(explorer,'factor',0);assert.ok(explorer.$('multText').textContent.includes('Final value: 0.'));
enter(explorer,'factor',3);assert.equal(explorer.$('explorerResults').hidden,true);
for(const [values,equal] of [[[1,2,2,4],true],[[-1,2,1,-2],true],[[1,3,1,4],false],[[6,3,2,1],true],[[-100,1,1,2],false]]){
 ['numA','denA','numB','denB'].forEach((id,i)=>enter(explorer,id,values[i]));assert.equal(explorer.$('fractionPlot').innerHTML,'');
 explorer.$('compareFractions').click();assert.ok(explorer.$('fractionSummary').textContent.endsWith(equal?'equivalent.':'different.'));
 if(values[0]===-100)capture(explorer,'fractionPlot','fractions-negative');
}
for(const values of [[1,0,2,4],[1.5,2,2,4],['',2,2,4],[1,2,2,'Infinity']]){
 ['numA','denA','numB','denB'].forEach((id,i)=>enter(explorer,id,values[i]));explorer.$('compareFractions').click();assert.equal(explorer.$('fractionPlot').innerHTML,'');assert.ok(explorer.$('fractionSummary').textContent.includes('integer'));
}

// A typed final answer cannot bypass the three recorded signed moves.
const labFile='labs/week1_lab.html',lab=open(labFile),labForm=lab.document.querySelector('[data-answer-store]'),labKey=labForm.dataset.answerStore,labLegacy=labForm.dataset.legacyStore;
const diverGroup=lab.document.querySelectorAll('[data-check-group]').find(x=>x.dataset.checkGroup==='diver');
enter(lab,'diverExpr','0 + (−15) + (+8) + (−5)');enter(lab,'diverFinal','-12');diverGroup.querySelector('[data-check]').click();assert.ok(diverGroup.querySelector('.section-feedback').textContent.includes('Record all three'));
enter(lab,'diverMarker',-14);lab.$('recordMove').click();assert.ok(lab.$('diverDragFeedback').textContent.includes('has not been recorded'));assert.deepEqual(JSON.parse(lab.data[labKey]).activity.diver.stops,[0]);
enter(lab,'diverMarker',-15);lab.$('diverMarker').dispatch('change');assert.deepEqual(JSON.parse(lab.data[labKey]).activity.diver.stops,[0,-15]);
let partialDiver=open(labFile,{[labKey]:lab.data[labKey]});assert.equal(partialDiver.$('diverPosition').textContent,'-15');assert.ok(partialDiver.$('diverMovePrompt').textContent.includes('rise 8'));
for(const position of [-7,-12]){enter(lab,'diverMarker',position);lab.$('recordMove').click();}
assert.equal(lab.$('recordMove').disabled,true);assert.equal(lab.$('diverMarker').disabled,true);diverGroup.querySelector('[data-check]').click();assert.ok(diverGroup.querySelector('.section-feedback').textContent.includes('Every response is correct.'));capture(lab,'numberline','diver-complete');
const restoredLab=open(labFile,{[labKey]:lab.data[labKey]});assert.equal(restoredLab.$('diverMarker').disabled,true);assert.ok(restoredLab.$('progressText').textContent.startsWith('1 /'));
for(const stops of [[0,-15],[0,-15,-7,-12]]){const p=open(labFile,{[labLegacy]:JSON.stringify({diverStops:stops,diverStep:stops.length-1,diverExpr:'0-15+8-5',diverFinal:'-12'})});assert.equal(p.$('diverPosition').textContent,String(stops.at(-1)));assert.equal(p.$('diverMarker').disabled,stops.length===4);}
const corruptLab=open(labFile,{[labLegacy]:JSON.stringify({diverStops:[0,-15,-8],diverStep:3})});assert.equal(corruptLab.$('diverPosition').textContent,'0');assert.equal(corruptLab.$('diverMarker').disabled,false);
lab.$('resetDiverPath').click();assert.deepEqual(JSON.parse(lab.data[labKey]).activity.diver.stops,[0]);assert.ok(lab.$('progressText').textContent.startsWith('0 /'));
lab.$('revealLongRange').click();assert.equal(lab.$('longRange').hidden,false);assert.equal(lab.$('longRangeTable').querySelectorAll('tbody tr').length,15);assert.ok(lab.$('crossoverText').textContent.includes('year 5'));assert.ok(lab.$('crossoverText').textContent.includes('16,367'));
const scaling=lab.document.querySelectorAll('[data-check-group]').find(x=>x.dataset.checkGroup==='scaling');scaling.querySelector('[data-check]').click();assert.equal(lab.$('scaleVal0').textContent,'10.5');assert.equal(lab.$('scaleVal1').textContent,'3.5');assert.equal(lab.$('scaleVal2').textContent,'14');assert.equal(lab.$('scaleVal3').textContent,'2.333333');
enter(lab,'scaleRule1','smaller');assert.equal(JSON.parse(lab.data[labKey]).fields.scaleRule1,'smaller');lab.document.querySelector('[data-clear-work]').click();assert.equal(lab.$('longRange').hidden,true);assert.equal(lab.$('scaleVal0').textContent,'Hidden until you check.');assert.equal(lab.$('diverExpr').value,'');assert.equal(lab.$('scaleRule1').value,'');assert.deepEqual(JSON.parse(lab.data[labKey]).activity.diver.stops,[0]);

const decoder=open('applications/week1_ai.html');assert.equal(decoder.$('decodedTokens').textContent,'cat sat on the mat');decoder.$('reverseTokens').click();assert.equal(decoder.$('decodedTokens').textContent,'mat the on sat cat');assert.equal(decoder.$('decodeIds').value,'91,55,8,17,42');
enter(decoder,'decodeIds','103,8,55,91');assert.equal(decoder.$('decodedTokens').textContent,'');decoder.$('decodeTokens').click();assert.equal(decoder.$('decodedTokens').textContent,'slept on the mat');
enter(decoder,'decodeIds','42,999');decoder.$('decodeTokens').click();assert.equal(decoder.$('decodedTokens').textContent,'');assert.ok(decoder.$('decodeStatus').textContent.includes('not in this vocabulary'));
const toy=open('applications/ai_week1.html');assert.equal(toy.$('toyState').textContent,'The cat');for(let i=0;i<4;i++)toy.$('appendToy').click();assert.equal(toy.$('toyState').textContent,'The cat sat on the mat');assert.equal(toy.$('appendToy').disabled,true);assert.ok(toy.$('toyStatus').textContent.includes('total length 6'));toy.$('resetToy').click();assert.equal(toy.$('toyState').textContent,'The cat');assert.equal(toy.$('appendToy').disabled,false);
console.log('PASS: 500 independent arithmetic oracles; all 53 original graded responses; saved-work migration; named printing; and explorer, diver, decoder, and continuation controls.');
