/* Exact rational oracles and DOM-level interaction checks for the entire Week 5 unit. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),{execFileSync}=require('node:child_process');
const M=require('../assets/week5/week5.js');const close=(a,b,t=1e-10)=>assert.ok(Math.abs(a-b)<=1e-8+t*Math.max(1,Math.abs(a),Math.abs(b)),`${a} != ${b}`);
const snapshots=JSON.parse(execFileSync('python3',['scripts/verify_week5.py','--dom-json'],{encoding:'utf8',maxBuffer:4*1024*1024}));
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
 get value(){if(this._value!==null)return this._value;if(this.tagName==='SELECT'){let o=this.children.find(x=>'selected' in x.attrs)||this.children[0];return o?.attrs.value||'';}return this.attrs.value||'';}set value(v){this._value=String(v);if(this.tagName==='SELECT'&&!this.children.some(x=>x.attrs.value===this._value))this._value='';}
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
function open(file,initial={}){
 const root=fromJSON(snapshots[file]),data={...initial},events={},window={prints:0,addEventListener(k,fn){(events[k]??=[]).push(fn);},print(){this.prints++;for(const f of events.beforeprint||[])f();}},document={readyState:'complete',querySelectorAll:q=>root.querySelectorAll(q),querySelector:q=>root.querySelector(q),getElementById:id=>root.querySelectorAll('[id]').find(x=>x.id===id)||null,createElement:tag=>new Element(tag)};
 const sandbox={document,window,localStorage:{getItem:k=>{if(initial.__failStorage)throw Error('Storage disabled');return data[k]??null;},setItem:(k,v)=>{if(initial.__failStorage)throw Error('Storage disabled');data[k]=String(v);}},Math,console};sandbox.globalThis=sandbox;vm.runInNewContext(fs.readFileSync('assets/week5/week5.js','utf8'),sandbox,{filename:'week5.js'});if(file==='information_cybernetics_timeline.html'){window.Math5=sandbox.Math5;window.Week5Visuals=sandbox.Week5Visuals;sandbox.matchMedia=()=>({matches:false});vm.runInNewContext(fs.readFileSync('assets/week5/history.js','utf8'),sandbox,{filename:'history.js'});}return{root,document,window,data,$:id=>document.getElementById(id),events};
}
for(const x of ['', 'Infinity','NaN','2+2','1/0','2abc'])assert.ok(Number.isNaN(M.number(x)));close(M.number('3/4'),.75);close(M.number('-3/2'),-1.5);close(M.number('1e-3'),.001);
const oracle=JSON.parse(execFileSync('python3',['-c',String.raw`
from fractions import Fraction as F
from decimal import Decimal,getcontext
import random,json
rng=random.Random(10705);cases=[]
for d in range(4):
 for k in [0,.2,.5,1,1.5,2,2.3,2.8]:cases.append(dict(r=70,start=64,k=k,delay=d,steps=20,mode='negative'))
for _ in range(128):cases.append(dict(r=rng.randrange(-100,201),start=rng.randrange(-100,201),k=rng.randrange(0,57)/20,delay=rng.randrange(4),steps=rng.randrange(1,41),mode=rng.choice(['negative','positive'])))
out=[]
for a in cases:
 r,x,k=map(lambda v:F(str(v)),[a['r'],a['start'],a['k']]);d=a['delay'];xs=[x];rows=[]
 for n in range(a['steps']):
  report=xs[n-d] if n>=d else x;error=(r-report) if a['mode']=='negative' else (report-r);correction=k*error;new=xs[-1]+correction;rows.append([n,float(xs[-1]),n-d,float(report),float(error),float(correction),float(new)]);xs.append(new)
 out.append(dict(args=a,states=list(map(float,xs)),rows=rows))
getcontext().prec=60;noise=[]
for sigma in [.5,1,2,4]:
 for m in range(1,26):noise.append([sigma,m,float(Decimal(str(sigma))/Decimal(m).sqrt())])
print(json.dumps(dict(feedback=out,noise=noise)))
`],{encoding:'utf8',maxBuffer:4*1024*1024}));
for(const f of oracle.feedback){const g=M.feedback(f.args);assert.equal(g.states.length,f.states.length);g.states.forEach((x,i)=>close(x,f.states[i]));g.rows.forEach((x,i)=>['n','current','reportIndex','report','error','correction','next'].forEach((k,j)=>close(x[k],f.rows[i][j])));}
for(const [sigma,m,sd] of oracle.noise){const g=M.noise(sigma,m,2);close(g.sd,sd);assert.equal(g.span,(m-1)*2);}
const d=M.feedback({delay:1});assert.deepEqual(d.states.slice(0,9),[64,67,70,71.5,71.5,70.75,70,69.625,69.625]);assert.equal(d.crossings,3);assert.equal(d.rows[2].reportIndex,1);assert.equal(d.rows[3].correction,0);assert.equal(d.maxDeparture,6);
for(const delay of [0,1,2,3])for(const k of [0,.5,1,2.8]){assert.ok(M.feedback({start:70,r:70,k,delay}).states.every(x=>x===70));assert.ok(M.feedback({k:0,delay}).states.every(x=>x===64));}
assert.deepEqual(M.feedback({start:0,r:10,k:2,steps:4}).states,[0,20,0,20,0]);assert.equal(M.feedback({mode:'positive',r:10,start:8,k:.5,steps:1}).states[1],7);
for(const args of [{k:-1},{k:3},{delay:.5},{delay:4},{steps:0},{steps:41},{r:Infinity},{start:201},{mode:'other'}])assert.throws(()=>M.feedback(args));
for(const alpha of [0,.25,.75,1,1.2])for(const start of [-5,1,3,10]){
 const f=M.learning({alpha,start,steps:20});for(let n=0;n<=20;n++)close(f.weights[n],3+(start-3)*(1-2*alpha)**n);
}
assert.deepEqual(M.learning({delay:1,steps:3}).weights,[1,2,3,3.5]);assert.deepEqual(M.learning({alpha:.75,steps:2}).predictions,[2,8,5]);assert.throws(()=>M.learning({alpha:1.3}));assert.throws(()=>M.learning({delay:2}));assert.throws(()=>M.noise(2,0,1));assert.throws(()=>M.noise(2,2.5,1));assert.throws(()=>M.noise(0,1,1));
for(let k=0;k<20;k++)close(M.surprise(2**-k),k);assert.throws(()=>M.surprise(0));assert.throws(()=>M.surprise(1.1));assert.equal(M.entropy(0),0);assert.equal(M.entropy(1),0);assert.equal(M.entropy(.5),1);close(M.entropy(.25),.8112781244591328);for(let p=0;p<=100;p++)close(M.entropy(p/100),M.entropy(1-p/100));
let checked=0;
for(const file of Object.keys(snapshots)){
 const page=open(file),form=page.document.querySelector('[data-answer-store]');if(!form){page.document.querySelector('[data-print-page]').click();assert.equal(page.window.prints,1);continue;}
 const fields=form.querySelectorAll('[data-answer]'),groups=form.querySelectorAll('[data-check-group]');
 for(const g of groups){g.querySelector('[data-check]').click();assert.ok(g.querySelector('.section-feedback').textContent.includes('0 of'));}
 for(const e of fields){e.value=e.dataset.answer;e.dispatch('input');checked++;}
 for(const g of groups){g.querySelector('[data-check]').click();assert.ok(g.querySelector('.section-feedback').textContent.includes(g.querySelector('textarea')?'All numerical and choice responses are correct.':'Every response is correct.'));}
 for(const e of fields)assert.equal(e.getAttribute('aria-invalid'),'false');
 if(fields.length){const first=fields[0];first.value='';first.dispatch('input');const g=first.closest('[data-check-group]');g.querySelector('[data-check]').click();assert.ok(first.closest('.question').querySelector('.field-feedback').textContent.startsWith('Enter a response.'));first.value=first.dataset.answer;first.dispatch('input');g.querySelector('[data-check]').click();}
 const written=form.querySelector('textarea[data-save]');if(written){written.value='The current state and the report describe different times.';written.dispatch('input');}
 const key=form.dataset.answerStore,legacy=form.dataset.legacyStore,saved=JSON.parse(page.data[key]);assert.ok(saved.fields);const restored=open(file,{[key]:page.data[key]});if(written)assert.equal(restored.$(written.id).value,written.value);
 if(legacy){const values=Object.fromEntries(fields.map(e=>[e.id,e.dataset.answer])),old=file==='labs/week5_lab.html'?{values,completed:[true,true,true,true,true,true]}:values,r=open(file,{[legacy]:JSON.stringify(old)});for(const e of fields)assert.equal(r.$(e.id).value,e.dataset.answer);const partialValues={[fields[0].id]:fields[0].dataset.answer},partial=open(file,{[legacy]:JSON.stringify(file==='labs/week5_lab.html'?{values:partialValues,completed:[true,true,true,true,true,true]}:partialValues)});if(partial.$('progressText'))assert.ok(partial.$('progressText').textContent.startsWith('0 /'));else assert.ok(fields.slice(1).some(e=>partial.$(e.id).value===''));}
 const print=page.document.querySelector('[data-print-work]');print.click();assert.equal(page.window.prints,0);page.$('studentName').value='Student Example';print.click();assert.equal(page.window.prints,1);assert.equal(page.$('printName').textContent,'Student: Student Example');assert.equal(page.document.querySelectorAll('.print-answer').length,form.querySelectorAll('.question input,.question select,.question textarea').length);for(const fn of page.events.afterprint||[])fn();assert.equal(page.document.querySelectorAll('.print-answer').length,0);
 const disabled=open(file,{__failStorage:true});assert.ok(disabled.$('saveStatus').textContent.includes('unavailable'));if(fields.length){disabled.$(fields[0].id).value=fields[0].dataset.answer;disabled.$(fields[0].id).dispatch('input');}
}
assert.equal(checked,42);
const originalSchemas=JSON.parse(fs.readFileSync('scripts/week5_response_contracts.json','utf8'));
for(const [file,schema] of Object.entries(originalSchemas)){
 const fresh=open(file),form=fresh.document.querySelector('[data-answer-store]');if(!form||!form.dataset.legacyStore)continue;
 const values={};for(const field of schema){const id=field.attrs.id;if(id==='printStudentName')continue;const el=fresh.$(id);values[id]=field.tag==='textarea'?'Preserved earlier explanation for '+id:el.dataset.answer;}
 const legacy=file==='labs/week5_lab.html'?{values,completed:[true,true,true,true,true,true]}:values,restored=open(file,{[form.dataset.legacyStore]:JSON.stringify(legacy)});
 for(const [id,value] of Object.entries(values))assert.equal(restored.$(id).value,String(value));
}

const e=open('demos/cybernetics.html');assert.ok(e.$('delayedEq').textContent.includes('71.5'));assert.equal(e.$('sequenceTable').querySelectorAll('tbody tr').length,4);e.$('previousStep').click();assert.ok(e.$('sequenceInsight').textContent.includes('reaches 70'));e.$('nextStep').click();assert.ok(e.$('sequenceInsight').textContent.includes('old 67'));e.$('sequenceStep').value=0;e.$('sequenceStep').dispatch('input');assert.ok(e.$('previousStep').disabled);assert.equal(e.$('sequenceTable').querySelectorAll('tbody tr').length,1);e.$('sequenceStep').value=12;e.$('sequenceStep').dispatch('input');assert.ok(e.$('nextStep').disabled);
for(const name of ['delay','strong','cycle','amplify','reading']){e.$('feedbackPreset').value=name;e.$('feedbackPreset').dispatch('change');assert.equal(e.$('feedbackError').textContent,'');assert.ok(e.$('feedbackPlot').innerHTML.includes('<svg'));assert.equal(e.$('feedbackTable').querySelectorAll('tbody tr').length,12);}
e.$('x0').value=70;e.$('x0').dispatch('input');assert.ok(e.$('behavior').textContent.includes('exactly at its reference'));e.$('x0').value=64;e.$('k').value=0;e.$('k').dispatch('input');assert.ok(e.$('behavior').textContent.includes('Zero response'));e.$('feedbackPreset').value='cycle';e.$('feedbackPreset').dispatch('change');assert.ok(e.$('behavior').textContent.includes('indefinitely'));
for(const id of ['r','x0','k','delay','feedbackHorizon']){const old=e.$(id).value;e.$(id).value='';e.$(id).dispatch('input');assert.equal(e.$('feedbackResults').hidden,true);e.$(id).value=old;e.$(id).dispatch('input');assert.equal(e.$('feedbackResults').hidden,false);}
e.$('delay').value=.5;e.$('delay').dispatch('input');assert.equal(e.$('feedbackResults').hidden,true);e.$('noiseN').value=16;e.$('noiseN').dispatch('input');assert.ok(e.$('noiseExplanation').textContent.includes('0.5°F'));assert.ok(e.$('noiseExplanation').textContent.includes('15 minutes'));e.$('noiseN').value='';e.$('noiseN').dispatch('input');assert.equal(e.$('noiseTable').children.length,0);
const ai=open('applications/week5_ai.html');assert.ok(ai.$('learningPlot').innerHTML.includes('<svg'));ai.$('learningTrace').value='late';ai.$('learningTrace').dispatch('change');const row=ai.$('learningTable').querySelectorAll('tbody tr')[2];assert.equal(row.children[1].textContent,'3');assert.equal(row.children[4].textContent,'4');assert.equal(row.children[7].textContent,'3.5');ai.$('learningAlpha').value=.75;ai.$('learningAlpha').dispatch('input');assert.ok(ai.$('learningSummary').textContent.includes('0.75'));ai.$('learningSteps').value='';ai.$('learningSteps').dispatch('input');assert.equal(ai.$('learningPlot').innerHTML,'');assert.equal(ai.$('learningTable').children.length,0);
const ext=open('applications/ai_week5.html');assert.ok(ext.$('surpriseSummary').textContent.includes('3 bits'));ext.$('tokenProbability').value=1;ext.$('tokenProbability').dispatch('input');assert.ok(ext.$('surpriseSummary').textContent.includes('0 bits'));ext.$('tokenProbability').value=0;ext.$('tokenProbability').dispatch('input');assert.ok(ext.$('surpriseSummary').textContent.includes('no finite'));
const h=open('information_cybernetics_timeline.html');assert.ok(h.$('resultCount').textContent.includes('63 of 63'));h.$('searchEvents').value='Margaret Mead';h.$('searchEvents').dispatch('input');assert.equal(h.root.querySelectorAll('.milestone').filter(x=>!x.hidden).length,2);h.$('searchEvents').value='unfindable-word';h.$('searchEvents').dispatch('input');assert.ok(h.$('emptyMessage').className.includes('show'));h.$('clearFilters').click();assert.ok(h.$('resultCount').textContent.includes('63 of 63'));
for(const btn of h.root.querySelectorAll('.cat')){btn.click();assert.equal(btn.getAttribute('aria-pressed'),'true');assert.ok(h.root.querySelectorAll('.milestone').some(x=>!x.hidden));}h.$('clearFilters').click();for(const btn of h.root.querySelectorAll('.era')){btn.click();assert.equal(btn.getAttribute('aria-pressed'),'true');assert.ok(h.root.querySelectorAll('.milestone').some(x=>!x.hidden));}h.$('clearFilters').click();for(const btn of h.root.querySelectorAll('[data-jump]'))btn.click();
h.$('lagBtn').click();assert.equal(h.$('lagBtn').getAttribute('aria-pressed'),'true');assert.ok(h.$('feedbackExplain').textContent.includes('71.5'));assert.equal(h.$('historyFeedbackTable').querySelectorAll('tbody tr')[3].children[1].textContent,'71.5');h.$('nowBtn').click();assert.equal(h.$('nowBtn').getAttribute('aria-pressed'),'true');for(const p of [0,25,50,75,100]){h.$('chanceRange').value=p;h.$('chanceRange').dispatch('input');assert.ok(h.$('entropyVal').textContent.includes(p===50?'1.000':p===0||p===100?'0.000':'0.811'));}
for(const [file,snapshot] of Object.entries(snapshots)){if(file==='information_cybernetics_timeline.html')continue;const root=fromJSON(snapshot),config=root.querySelectorAll('script').find(e=>e.textContent.includes('window.MathJax=')),c={window:{}};vm.runInNewContext(config.textContent,c);assert.equal(c.window.MathJax.tex.inlineMath[0][0],'\\(');assert.equal(c.window.MathJax.tex.displayMath[0][0],'\\[');}
console.log('PASS: 160 exact Fraction feedback oracles and 100 Decimal averaging oracles; closed-form learning comparisons; boundary and zero cases; eight page initializations; 42 remaining answers and option contracts; legacy/new restores; per-answer feedback; saved writing, named printing and storage failure; explorer controls, invalid states, all history filters and both experiments; mathematical rendering configuration.');
