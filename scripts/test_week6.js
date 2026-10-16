/* Independent decimal arithmetic and DOM-level interaction checks for Week 6. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),{execFileSync}=require('node:child_process');
const M=require('../assets/week6/week6.js');const close=(a,b,t=1e-9)=>assert.ok(Math.abs(a-b)<=1e-7+t*Math.max(1,Math.abs(a),Math.abs(b)),`${a} != ${b}`);
const snapshots=JSON.parse(execFileSync('python3',['scripts/verify_week6.py','--dom-json'],{encoding:'utf8'}));
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
 addEventListener(type,fn){(this.events[type]??=[]).push(fn);}dispatch(type,event={}){for(let fn of this.events[type]||[])fn({preventDefault(){},...event});}click(){if(!this.disabled)this.dispatch('click');}focus(){this.focused=true;}
}
function fromJSON(o){let e=new Element(o.tag,o.attrs,o.text);e.tail=o.tail;for(let c of o.children)e.append(fromJSON(c));return e;}
function open(file,initial={}){
 const root=fromJSON(snapshots[file]),data={...initial},events={},window={prints:0,addEventListener(k,fn){(events[k]??=[]).push(fn);},print(){this.prints++;for(const f of events.beforeprint||[])f();}},document={readyState:'complete',querySelectorAll:q=>root.querySelectorAll(q),querySelector:q=>root.querySelector(q),getElementById:id=>root.querySelectorAll('[id]').find(x=>x.id===id)||null,createElement:tag=>new Element(tag)};
 const sandbox={document,window,localStorage:{getItem:k=>{if(initial.__failStorage)throw Error('Storage disabled');return data[k]??null;},setItem:(k,v)=>{if(initial.__failStorage)throw Error('Storage disabled');data[k]=String(v);}},Math,console};sandbox.globalThis=sandbox;vm.runInNewContext(fs.readFileSync('assets/week6/week6.js','utf8'),sandbox,{filename:'week6.js'});return{root,document,window,data,$:id=>document.getElementById(id),events};
}
for(const x of ['', 'Infinity','NaN','2+2','1/0'])assert.ok(Number.isNaN(M.number(x)));close(M.number('3/4'),.75);
assert.throws(()=>M.loan(-1,.06,100));assert.throws(()=>M.loan(1000,-.01,100));assert.throws(()=>M.loan(1000,.06,100,{limit:0}));assert.throws(()=>M.loan(1000,.06,.001));assert.throws(()=>M.savings(1000,.03,1.5,12));
// Decimal arithmetic provides a reference independent of JavaScript's float loop.
const fixtures=JSON.parse(execFileSync('python3',['-c',String.raw`
from decimal import Decimal,ROUND_HALF_UP,getcontext
import random,json
getcontext().prec=65
r=random.Random(10706);cases=[(4000,.06,200,1200),(8000,.18,160,1200),(8000,.18,300,1200),(200000,.045,1013.37,360),(200000,.045,1013.37,1200),(1000,.12,10,1200),(1000,.12,5,1200),(1000,0,100,1200),(1000,0,0,12),(0,.06,0,1200),(.01,.4,.01,12),(.3,0,.1,20)]
for _ in range(228):cases.append((r.randrange(1,1000001)/100,r.randrange(0,4001)/10000,r.randrange(0,50001)/100,r.choice([1,6,24,120,1200])))
out=[]
for principal,annual,payment,limit in cases:
 for mode in ['cents','full']:
  P=Decimal(str(principal));rate=Decimal(str(annual))/12;M=Decimal(str(payment));b=P;total=Decimal(0);interest_sum=Decimal(0);rows=[]
  first=P*rate
  if mode=='cents':first=first.quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
  status='paid' if P==0 else 'constant' if M==first else 'growing' if M<first else 'decreasing'
  steps=min(limit,24) if status in ['constant','growing'] else limit
  if P:
   for month in range(1,steps+1):
    interest=b*rate
    if mode=='cents':interest=interest.quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
    actual=min(M,b+interest);end=b+interest-actual;total+=actual;interest_sum+=interest;rows.append([month,float(b),float(interest),float(actual),float(end)]);b=end
    if b<Decimal('1e-40'):b=Decimal(0);status='paid';break
  if status=='decreasing':status='horizon'
  out.append({'P':principal,'r':annual,'M':payment,'limit':limit,'mode':mode,'status':status,'months':len(rows) if status=='paid' else None,'simulated':len(rows),'balance':float(b),'totalPaid':float(total),'totalInterest':float(interest_sum),'firstInterest':float(first),'rows':rows[:4]+(rows[-1:] if len(rows)>4 else [])})
print(json.dumps(out))
`],{encoding:'utf8',maxBuffer:2*1024*1024}));
for(const f of fixtures){const g=M.loan(f.P,f.r,f.M,{rounding:f.mode,limit:f.limit});assert.equal(g.status,f.status,JSON.stringify(f));assert.equal(g.months,f.months);assert.equal(g.simulated,f.simulated);for(const k of ['balance','totalPaid','totalInterest','firstInterest'])close(g[k],f[k]);for(const row of f.rows){const a=g.rows[row[0]-1];for(const [key,i] of [['start',1],['interest',2],['payment',3],['end',4]])close(a[key],row[i]);}close(g.balance,f.P+g.totalInterest-g.totalPaid);assert.ok(g.rows.every(x=>x.end>=0));if(g.status==='paid')close(g.totalPaid-f.P,g.totalInterest);}
const savings=JSON.parse(execFileSync('python3',['-c',String.raw`
from decimal import Decimal,getcontext
import json,random
getcontext().prec=60;r=random.Random(6006);out=[]
for _ in range(100):
 P=Decimal(r.randrange(0,10000001))/100;rate=Decimal(r.randrange(0,3001))/10000;t=r.randrange(0,41);n=r.choice([1,2,4,12,365]);out.append({'P':float(P),'r':float(rate),'t':t,'n':n,'simple':float(P*(1+rate*t)),'compound':float(P*(1+rate/n)**(n*t)),'yield':float((1+rate/n)**n-1)})
print(json.dumps(out))
`],{encoding:'utf8'}));
for(const f of savings){const g=M.savings(f.P,f.r,f.t,f.n);for(const k of ['simple','compound','yield'])close(g[k],f[k]);assert.equal(g.periods,f.n*f.t);assert.equal(g.rows.length,f.t+1);}
const A=M.loan(8000,.18,160,{rounding:'full'}),B=M.loan(8000,.18,300,{rounding:'full'});assert.equal(A.months,94);assert.equal(B.months,35);close(A.totalInterest-B.totalInterest,4604.4618314581);const reading=M.loan(4000,.06,200);assert.equal(reading.months,22);close(reading.finalPayment,24.99);close(reading.totalInterest,224.99);assert.equal(M.loan(4000,.06,200,{limit:6}).status,'horizon');assert.equal(M.loan(1000,.12,10).status,'constant');assert.equal(M.loan(1000,.12,5).status,'growing');assert.equal(M.loan(0,0,0).months,0);assert.equal(M.loan(.3,0,.1,{rounding:'full'}).months,3);
assert.equal(M.growth(12,400).capYear,7);assert.equal(M.growth(12,400).divergeYear,7);close(M.growth(12,400).rows[12].limited,400);assert.equal(M.growth(2,125).capYear,1);assert.equal(M.growth(2,125).divergeYear,2);assert.throws(()=>M.growth(2,99));
let checked=0;
for(const file of Object.keys(snapshots)){
 const page=open(file),form=page.document.querySelector('[data-answer-store]');if(!form)continue;const fields=form.querySelectorAll('[data-answer]'),groups=form.querySelectorAll('[data-check-group]');
 for(const g of groups){g.querySelector('[data-check]').click();assert.ok(g.querySelector('.section-feedback').textContent.includes('0 of'));}
 for(const e of fields){e.value=e.dataset.answer;e.dispatch('input');checked++;}
 for(const g of groups){g.querySelector('[data-check]').click();assert.ok(g.querySelector('.section-feedback').textContent.includes('Every response is correct.'));}
 for(const e of fields)assert.equal(e.getAttribute('aria-invalid'),'false');
 if(fields.length){const first=fields[0];first.value='';first.dispatch('input');const g=first.closest('[data-check-group]');g.querySelector('[data-check]').click();assert.ok(first.closest('.question').querySelector('.field-feedback').textContent.startsWith('Enter a response.'));first.value=first.dataset.answer;first.dispatch('input');g.querySelector('[data-check]').click();}
 const written=form.querySelector('textarea[data-save]');if(written){written.value='My reasoning uses a rate, period, and current balance.';written.dispatch('input');}
 const key=form.dataset.answerStore,legacy=form.dataset.legacyStore,saved=JSON.parse(page.data[key]);assert.ok(saved.fields);const restored=open(file,{[key]:page.data[key]});if(written)assert.equal(restored.$(written.id).value,written.value);
 if(legacy){const values=Object.fromEntries(fields.map(e=>[e.id,e.dataset.answer])),old=file==='labs/week6_lab.html'?{values,checked:[true,true,true,true,true]}:values,r=open(file,{[legacy]:JSON.stringify(old)});for(const e of fields)assert.equal(r.$(e.id).value,e.dataset.answer);const partialValues={[fields[0].id]:fields[0].dataset.answer},partial=open(file,{[legacy]:JSON.stringify(file==='labs/week6_lab.html'?{values:partialValues,checked:[true,true,true,true,true]}:partialValues)});assert.ok(partial.$('progressText').textContent.startsWith('0 /'));}
 const print=page.document.querySelector('[data-print-work]');print.click();assert.equal(page.window.prints,0);page.$('studentName').value='Student Example';print.click();assert.equal(page.window.prints,1);assert.equal(page.$('printName').textContent,'Student: Student Example');assert.equal(page.document.querySelectorAll('.print-answer').length,form.querySelectorAll('.question input,.question select,.question textarea').length);for(const fn of page.events.afterprint||[])fn();assert.equal(page.document.querySelectorAll('.print-answer').length,0);
 const disabled=open(file,{__failStorage:true});assert.ok(disabled.$('saveStatus').textContent.includes('unavailable'));if(fields.length){disabled.$(fields[0].id).value=fields[0].dataset.answer;disabled.$(fields[0].id).dispatch('input');}
}
assert.equal(checked,50);
const e=open('demos/interest_loans.html');assert.ok(e.$('compoundOut').textContent.includes('2,318.55'));assert.ok(e.$('loanSummary').textContent.includes('month 22'));for(const preset of ['lab','cardA','cardB','discussion','flat','growing','zero','reading']){e.$('loanPreset').value=preset;e.$('loanPreset').dispatch('change');assert.equal(e.$('loanError').textContent,'');assert.ok(e.$('loanPlot').innerHTML.includes('<svg'));}
e.$('loanHorizon').value=6;e.$('loanHorizon').dispatch('input');assert.ok(e.$('loanSummary').textContent.includes('Not paid'));assert.ok(e.$('loanTotals').textContent.includes('totals so far'));e.$('loanHorizon').value=1200;e.$('loanHorizon').dispatch('input');e.$('showAllMonths').checked=true;e.$('showAllMonths').dispatch('change');assert.equal(e.$('loanTable').querySelectorAll('tbody tr').length,22);
e.$('loanRounding').value='full';e.$('loanRounding').dispatch('change');assert.ok(e.$('loanSummary').textContent.includes('$25.00'));e.$('loanPreset').value='flat';e.$('loanPreset').dispatch('change');assert.ok(e.$('loanSummary').textContent.includes('stays unchanged'));e.$('lpay').value=5;e.$('lpay').dispatch('input');assert.ok(e.$('loanSummary').textContent.includes('balance grows'));e.$('lP').value=0;e.$('lP').dispatch('input');assert.ok(e.$('loanSummary').textContent.includes('0 payments'));
for(const id of ['sP','sr','st','lP','lr','lpay','loanHorizon']){const old=e.$(id).value;e.$(id).value='';e.$(id).dispatch('input');assert.ok(e.$(id.startsWith('s')?'savingsResults':'loanResults').hidden);e.$(id).value=old;e.$(id).dispatch('input');}
e.$('sr').value=0;e.$('sr').dispatch('input');assert.ok(e.$('savingsDoubling').textContent.includes('does not double'));e.$('sP').value=0;e.$('sP').dispatch('input');assert.ok(e.$('savingsDoubling').textContent.includes('zero starting'));e.$('st').value=0;e.$('st').dispatch('input');assert.ok(e.$('savingsPlot').innerHTML.includes('<svg'));e.$('sn').value='12';e.$('sn').dispatch('change');assert.equal(e.$('savingsError').textContent,'');
const app=open('applications/week6_application.html');assert.equal(app.$('appResults').hidden,true);app.$('run').click();assert.equal(app.$('appResults').hidden,false);assert.ok(app.$('aMonths').textContent.includes('94'));assert.ok(app.$('bMonths').textContent.includes('35'));app.$('repayPlan').value='B';app.$('repayPlan').dispatch('change');assert.equal(app.$('repayTrace').querySelectorAll('tbody tr').at(-1).children[0].textContent,'35');
const ai=open('applications/week6_ai.html');assert.ok(ai.$('growthSummary').textContent.includes('year 7'));ai.$('growthCap').value=125;ai.$('growthCap').dispatch('input');assert.ok(ai.$('growthSummary').textContent.includes('year 1'));ai.$('growthYears').value=0;ai.$('growthYears').dispatch('input');assert.ok(ai.$('growthPlot').innerHTML.includes('<svg'));ai.$('growthCap').value=99;ai.$('growthCap').dispatch('input');assert.equal(ai.$('growthPlot').innerHTML,'');assert.equal(ai.$('growthTable').children.length,0);
for(const snapshot of Object.values(snapshots)){const root=fromJSON(snapshot),config=root.querySelectorAll('script').find(e=>e.textContent.includes('window.MathJax=')),c={window:{}};vm.runInNewContext(config.textContent,c);assert.equal(c.window.MathJax.tex.inlineMath[0][0],'\\(');assert.equal(c.window.MathJax.tex.displayMath[0][0],'\\[');}
console.log('PASS: 480 independent Decimal repayment comparisons; 100 Decimal savings comparisons; fixed examples; rounding, zero, growing, constant, horizon, and final-payment cases; six page initializations; 50 original answer contracts; legacy restores including nested lab values; per-answer feedback; saved writing and named printing; storage failure; every explorer preset and application control; math-rendering configuration.');
