/* Independent rational-probability oracles and actual-page runtime checks. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),{execFileSync}=require('node:child_process');
const M=require('../assets/week2/week2.js');
const close=(a,b,t=1e-10)=>assert.ok(Math.abs(a-b)<=1e-9+t*Math.max(1,Math.abs(a),Math.abs(b)),String(a)+' != '+String(b));
const snapshots=JSON.parse(execFileSync('python3',['scripts/verify_week2.py','--dom-json'],{encoding:'utf8',maxBuffer:4*1024*1024}));
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
 getAttribute(k){return Object.hasOwn(this.attrs,k)?this.attrs[k]:null;}setAttribute(k,v){this.attrs[k]=String(v);}removeAttribute(k){delete this.attrs[k];}
 querySelectorAll(q){let selectors=q.split(','),out=[];for(let c of this.children){if(selectors.some(s=>matches(c,s)))out.push(c);out.push(...c.querySelectorAll(q));}return out;}querySelector(q){return this.querySelectorAll(q)[0]||null;}
 closest(q){for(let x=this;x;x=x.parentElement)if(matches(x,q))return x;return null;}
 append(...nodes){for(let n of nodes){n.parentElement=this;this.children.push(n);}}replaceChildren(...nodes){this.children=[];this.ownText='';this._html='';this.append(...nodes);}after(n){let p=this.parentElement;if(p){n.parentElement=p;p.children.splice(p.children.indexOf(this)+1,0,n);}}remove(){let p=this.parentElement;if(p)p.children=p.children.filter(n=>n!==this);}
 addEventListener(type,fn){(this.events[type]??=[]).push(fn);}dispatch(type,event={}){for(let fn of this.events[type]||[])fn({preventDefault(){},...event});}click(){if(!this.disabled)this.dispatch('click');}focus(){this.focused=true;}scrollIntoView(o){this.scrolled=o;}
}
function fromJSON(o){let e=new Element(o.tag,o.attrs,o.text);e.tail=o.tail;for(let c of o.children)e.append(fromJSON(c));return e;}
function open(file,initial={},rng=()=>.123456789){
 const root=fromJSON(snapshots[file]),data={...initial},events={},window={prints:0,addEventListener(k,fn){(events[k]??=[]).push(fn);},print(){this.prints++;for(const f of events.beforeprint||[])f();}},document={readyState:'complete',querySelectorAll:q=>root.querySelectorAll(q),querySelector:q=>root.querySelector(q),getElementById:id=>root.querySelectorAll('[id]').find(x=>x.id===id)||null,createElement:tag=>new Element(tag)};
 const sandbox={document,window,localStorage:{getItem:k=>{if(initial.__failStorage)throw Error('Storage disabled');return data[k]??null;},setItem:(k,v)=>{if(initial.__failStorage)throw Error('Storage disabled');data[k]=String(v);},removeItem:k=>{if(initial.__failStorage)throw Error('Storage disabled');delete data[k];}},Math:Object.assign(Object.create(Math),{random:rng}),console};sandbox.globalThis=sandbox;const script=root.querySelectorAll('script').find(e=>e.getAttribute('src')?.startsWith('../assets/')).getAttribute('src').slice(3);vm.runInNewContext(fs.readFileSync(script,'utf8'),sandbox,{filename:script});return{root,document,window,data,$:id=>document.getElementById(id),events};
}

for(const s of ['', ' ', 'Infinity','NaN','2abc','1/0','2+2'])assert.ok(Number.isNaN(M.number(s)));
assert.equal(M.number('0'),0);close(M.number('7/18'),7/18);close(M.number('.375'),.375);close(M.number('1e-3'),.001);
const oracle=JSON.parse(execFileSync('python3',['-c',String.raw`
from fractions import Fraction as F
import random,json
r=random.Random(10702);out={'frequencies':[],'models':[]}
datasets=[[0,0,0,0],[12,8,5,15],[24,16,10,30],[30,0,0,0]]
for _ in range(200):datasets.append([r.randrange(501) for i in range(r.randrange(1,9))])
for xs in datasets:
 n=sum(xs);out['frequencies'].append({'counts':xs,'total':n,'shares':[float(F(x,n)) for x in xs] if n else None})
for _ in range(200):
 cuts=[0]+sorted(r.randrange(1001) for i in range(r.randrange(1,8)))+[1000]
 counts=[b-a for a,b in zip(cuts,cuts[1:])]
 out['models'].append({'counts':counts,'ps':[float(F(c,1000)) for c in counts],'boundaries':[float(F(c,1000)) for c in cuts]})
print(json.dumps(out))
`],{encoding:'utf8',maxBuffer:3*1024*1024}));
for(const f of oracle.frequencies){const x=M.frequencies(f.counts);assert.equal(x.total,f.total);if(f.shares===null){assert.equal(x.shares,null);assert.equal(x.sum,null);}else{x.shares.forEach((p,i)=>close(p,f.shares[i]));close(x.sum,1);const scaled=M.frequencies(f.counts.map(x=>x*3));scaled.shares.forEach((p,i)=>close(p,f.shares[i]));}}
for(const f of oracle.models){
 const intervals=M.intervals(f.ps);intervals.forEach((p,i)=>{assert.equal(p.lo,f.boundaries[i]);assert.equal(p.hi,f.boundaries[i+1]);});
 for(const u of f.boundaries.filter(x=>x<1)){const expected=f.boundaries.findIndex((x,i)=>i>0&&x>u)-1;assert.equal(M.sample(f.ps,u),expected);}
 let j=0,state=M.advance(M.start(f.ps),1000,()=>((j++)+.5)/1000);assert.deepEqual(state.counts,f.counts);assert.equal(state.n,1000);assert.deepEqual(state.history.at(-1).counts,f.counts);
}
for(const xs of [[],[-1,2],[1.5,2],[NaN,1],[Infinity,0],[1000001,1]])assert.throws(()=>M.frequencies(xs));
for(const ps of [[],[-.1,1.1],[.4,.4],[.4,.4,.4],[NaN,1],[Infinity,0]])assert.throws(()=>M.distribution(ps));
for(const u of [-.01,1,Infinity,NaN])assert.throws(()=>M.sample([.5,.5],u));
assert.equal(M.sample([.1,.2,.7],.3),2);assert.equal(M.sample([0,.5,0,.5],0),1);assert.equal(M.sample([0,.5,0,.5],.5),3);assert.equal(M.sample([Number.MIN_VALUE,1],0),0);assert.equal(M.sample([1-Number.EPSILON/2,Number.EPSILON/2],1-Number.EPSILON/2),1);
const untouched=M.start([.5,.5]);let bad=0;assert.throws(()=>M.advance(untouched,3,()=>++bad===2?1:.1));assert.equal(untouched.n,0);assert.deepEqual(untouched.counts,[0,0]);assert.equal(untouched.history.length,0);
for(const n of [0,1.5,10001,NaN])assert.throws(()=>M.advance(untouched,n));assert.throws(()=>M.advance({...untouched,n:9999},2));

let checked=0;
for(const file of Object.keys(snapshots)){
 const page=open(file),form=page.document.querySelector('[data-answer-store]');if(!form){page.document.querySelector('[data-print-page]').click();assert.equal(page.window.prints,1);continue;}
 const fields=form.querySelectorAll('[data-answer]'),groups=form.querySelectorAll('[data-check-group]');
 for(const g of groups){g.querySelector('[data-check]').click();assert.ok(g.querySelector('.section-feedback').textContent.includes('0 of'));}
 for(const e of fields){e.value=e.dataset.answer;e.dispatch('input');checked++;}
 for(const g of groups){g.querySelector('[data-check]').click();assert.ok(g.querySelector('.section-feedback').textContent.includes(g.querySelector('textarea')?'All numerical and choice responses are correct.':'Every response is correct.'));}
 for(const e of fields)assert.equal(e.getAttribute('aria-invalid'),'false');
 if(fields.length){const first=fields[0];first.value='';first.dispatch('input');const g=first.closest('[data-check-group]');g.querySelector('[data-check]').click();assert.ok(first.closest('.question').querySelector('.field-feedback').textContent.startsWith('Enter a response.'));first.value=first.dataset.answer;first.dispatch('input');g.querySelector('[data-check]').click();}
 const written=form.querySelector('textarea[data-save]');if(written){written.value='The survey describes its respondents; reaching other groups could change the estimate.';written.dispatch('input');}
 const key=form.dataset.answerStore,legacy=form.dataset.legacyStore,saved=JSON.parse(page.data[key]);assert.ok(saved.fields);const restored=open(file,{[key]:page.data[key]});if(written)assert.equal(restored.$(written.id).value,written.value);
 if(legacy){const values=Object.fromEntries(fields.map(e=>[e.id,e.dataset.answer])),old=values,r=open(file,{[legacy]:JSON.stringify(old)});for(const e of fields)assert.equal(r.$(e.id).value,e.dataset.answer);const partialValues={[fields[0].id]:fields[0].dataset.answer},partial=open(file,{[legacy]:JSON.stringify(partialValues)});if(partial.$('progressText')){const expected=groups.filter(g=>{const es=g.querySelectorAll('[data-answer]');return es.length===1&&es[0].id===fields[0].id;}).length;assert.ok(partial.$('progressText').textContent.startsWith(expected+' /'));}else assert.ok(fields.slice(1).some(e=>partial.$(e.id).value===''));}
 const print=page.document.querySelector('[data-print-work]');print.click();assert.equal(page.window.prints,0);page.$('studentName').value='Student Example';print.click();assert.equal(page.window.prints,1);assert.equal(page.$('printName').textContent,'Student: Student Example');assert.equal(page.document.querySelectorAll('.print-answer').length,form.querySelectorAll('.question input,.question select,.question textarea').length);for(const fn of page.events.afterprint||[])fn();assert.equal(page.document.querySelectorAll('.print-answer').length,0);
 const disabled=open(file,{__failStorage:true});assert.ok(disabled.$('saveStatus').textContent.includes('unavailable'));if(fields.length){disabled.$(fields[0].id).value=fields[0].dataset.answer;disabled.$(fields[0].id).dispatch('input');}
}
assert.equal(checked,53);
const originalSchemas=JSON.parse(fs.readFileSync('scripts/week2_response_contracts.json','utf8'));
for(const [file,schema] of Object.entries(originalSchemas)){
 const fresh=open(file),form=fresh.document.querySelector('[data-answer-store]');if(!form||!form.dataset.legacyStore)continue;
 const values={};for(const field of schema){const id=field.attrs.id;if(id==='printStudentName')continue;const el=fresh.$(id);values[id]=field.tag==='textarea'?'Preserved earlier explanation for '+id:el.dataset.answer;}
 const legacy=values,restored=open(file,{[form.dataset.legacyStore]:JSON.stringify(legacy)});
 for(const [id,value] of Object.entries(values))assert.equal(restored.$(id).value,String(value));
}

const e=open('demos/probability_distribution.html');
assert.equal(e.$('tot').textContent,'40');assert.equal(e.$('maxp').textContent,'0.375');assert.equal(e.$('sumP').textContent,'1');assert.equal(e.$('tbl').children.length,4);assert.ok(e.$('sharePlot').innerHTML.includes('role="img"'));assert.ok(e.$('trialStatus').textContent.startsWith('0 independent'));
const preset=key=>e.document.querySelectorAll('[data-count-preset]').find(b=>b.dataset.countPreset===key).click();
preset('double');assert.equal(e.$('tot').textContent,'80');assert.equal(e.$('maxp').textContent,'0.375');preset('onlyA');assert.equal(e.$('maxp').textContent,'1');assert.ok(!e.$('sharePlot').innerHTML.includes('NaN'));
const draw=e.document.querySelectorAll('[data-draw]').find(b=>b.dataset.draw==='100');draw.click();assert.ok(e.$('trialStatus').textContent.startsWith('100 independent'));preset('empty');assert.equal(e.$('tot').textContent,'0');assert.equal(e.$('maxp').textContent,'Undefined');assert.equal(e.$('sumP').textContent,'Undefined');assert.ok(e.$('countsStatus').textContent.includes('denominator is zero'));e.$('freezeModel').click();assert.ok(e.$('modelStatus').textContent.includes('unchanged'));assert.ok(e.$('trialStatus').textContent.startsWith('100 independent'));
preset('onlyA');e.$('freezeModel').click();assert.ok(e.$('trialStatus').textContent.startsWith('0 independent'));draw.click();let row=e.$('trialTable').querySelectorAll('tbody tr')[0];assert.equal(row.children[1].textContent,'1');assert.equal(row.children[2].textContent,'100');assert.equal(row.children[3].textContent,'100');assert.equal(row.children[4].textContent,'1');
e.$('focusCategory').value='3';e.$('focusCategory').dispatch('change');assert.ok(e.$('trialHistory').innerHTML.includes('Observed share of D'));e.$('resetTrials').click();assert.ok(e.$('trialStatus').textContent.startsWith('0 independent'));e.$('equalModel').click();assert.ok(e.$('modelStatus').textContent.includes('A = 0.25'));
for(let i=0;i<100;i++)draw.click();assert.ok(e.$('trialStatus').textContent.startsWith('10000 independent'));assert.ok(e.document.querySelectorAll('[data-draw]').every(b=>b.disabled));e.$('resetTrials').click();assert.ok(e.document.querySelectorAll('[data-draw]').every(b=>!b.disabled));
const ai=open('applications/week2_ai.html');for(const b of ai.document.querySelectorAll('[data-token-draw]'))b.click();assert.ok(ai.$('tokenStatus').textContent.startsWith('221 independent'));row=ai.$('tokenTable').querySelectorAll('tbody tr')[0];assert.equal(row.children[2].textContent,'110.5');assert.equal(row.children[3].textContent,'221');assert.equal(row.children[4].textContent,'1');ai.$('resetTokens').click();assert.ok(ai.$('tokenStatus').textContent.startsWith('0 independent'));assert.ok(ai.$('tokenTable').querySelectorAll('tbody tr').every(r=>r.children[4].textContent.includes('Undefined')));
const interval=open('applications/ai_week2.html');
for(const [u,label] of [['0','mat'],['.5','rug'],['.7','chair'],['7/10','chair'],['.9','moon'],['.999999','moon']]){interval.$('uInput').value=u;interval.$('uInput').dispatch('input');assert.equal(interval.$('intervalPlot').innerHTML,'');interval.$('locateU').click();assert.ok(interval.$('intervalStatus').textContent.endsWith('select '+label+'.'));assert.ok(interval.$('intervalPlot').innerHTML.includes('<svg'));}
for(const u of ['','1','-.01','banana','Infinity','1/0']){interval.$('uInput').value=u;interval.$('locateU').click();assert.equal(interval.$('intervalPlot').innerHTML,'');assert.equal(interval.$('uInput').getAttribute('aria-invalid'),'true');}interval.$('randomU').click();assert.ok(interval.$('intervalStatus').textContent.endsWith('select mat.'));
const lab=open('labs/week2_lab.html'),form=lab.document.querySelector('[data-answer-store]'),legacy=form.dataset.legacyStore;
lab.$('sf0').value='4';lab.$('sf0').dispatch('input');lab.window.confirm=()=>false;lab.document.querySelector('[data-clear-work]').click();assert.equal(lab.$('sf0').value,'4');lab.window.confirm=()=>true;lab.data[legacy]=JSON.stringify({sf0:'4'});lab.data[legacy+'_part1']='1';lab.document.querySelector('[data-clear-work]').click();assert.ok(form.querySelectorAll('[data-answer],textarea[data-save]').every(x=>x.value===''));assert.equal(lab.$('progressText').textContent,'0 / 5 sections checked');assert.equal(lab.data[legacy],undefined);assert.equal(lab.data[legacy+'_part1'],undefined);const empty=open('labs/week2_lab.html',{[form.dataset.answerStore]:lab.data[form.dataset.answerStore]});assert.equal(empty.$('sf0').value,'');assert.equal(empty.$('progressText').textContent,'0 / 5 sections checked');
for(const [file,snapshot] of Object.entries(snapshots)){const root=fromJSON(snapshot),config=root.querySelectorAll('script').find(x=>x.textContent.includes('window.MathJax=')),c={window:{}};vm.runInNewContext(config.textContent,c);assert.equal(c.window.MathJax.tex.inlineMath[0][0],'\\(');assert.equal(c.window.MathJax.tex.displayMath[0][0],'\\[');}
console.log('PASS: 204 exact-frequency oracles, 200 exact interval/distribution oracles, 200,000 controlled draws, boundary and invalid-state checks; seven actual page scripts, all 53 original graded responses and options, legacy/current saves, feedback, saved reasoning, named printing, unavailable storage, clearing, fixed graph scales, empty samples, model freezing, trial limits, token counts, and sampling intervals.');
