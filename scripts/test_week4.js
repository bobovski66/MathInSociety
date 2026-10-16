/* Independent mathematical oracles and DOM interaction checks for Week 4. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),{execFileSync}=require('node:child_process');
const M=require('../assets/week4/week4.js');
const close=(a,b,t=1e-10)=>assert.ok(Math.abs(a-b)<=1e-9+t*Math.max(1,Math.abs(a),Math.abs(b)),String(a)+' != '+String(b));
const snapshots=JSON.parse(execFileSync('python3',['scripts/verify_week4.py','--dom-json'],{encoding:'utf8',maxBuffer:4*1024*1024}));
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
 const sandbox={document,window,localStorage:{getItem:k=>{if(initial.__failStorage)throw Error('Storage disabled');return data[k]??null;},setItem:(k,v)=>{if(initial.__failStorage)throw Error('Storage disabled');data[k]=String(v);}},Math,console,location:{hash:initial.__hash||''}};sandbox.globalThis=sandbox;vm.runInNewContext(fs.readFileSync('assets/week4/week4.js','utf8'),sandbox,{filename:'week4.js'});return{root,document,window,data,$:id=>document.getElementById(id),events};
}
for(const raw of ['', ' ', 'Infinity','NaN','2+2','1/0','2abc','--2','1.2.3'])assert.ok(Number.isNaN(M.number(raw)));
close(M.number('3/4'),.75);close(M.number('-3/2'),-1.5);close(M.number('1e-3'),.001);assert.equal(M.number('0'),0);assert.ok(!Number.isFinite(M.number('1e999')));
const oracle=JSON.parse(execFileSync('python3',['-c',String.raw`
from decimal import Decimal as D,getcontext
from scipy.stats import norm
import random,json,math
getcontext().prec=60
r=random.Random(10704);out={'normal':[],'interval':[],'precision':[],'sampling':[]}
for _ in range(200):
 mu=r.randrange(201);sd=r.randrange(1,41);x=r.randrange(251)
 out['normal'].append([mu,sd,x,float(norm.pdf(x,loc=mu,scale=sd)),float((D(x)-D(mu))/D(sd))])
for _ in range(120):
 estimate=D(r.randrange(-10000,10001))/100;margin=D(r.randrange(2001))/100
 for comparison in [estimate-margin,estimate+margin,estimate+margin+D('.01')]:
  lo=estimate-margin;hi=estimate+margin
  out['interval'].append([float(estimate),float(margin),float(comparison),float(lo),float(hi),float(2*margin),lo<=comparison<=hi])
for _ in range(120):
 n0=r.randrange(1,1000001);n=r.randrange(1,1000001);e=D(r.randrange(1,100001))/100
 out['precision'].append([n0,float(e),n,float(e*(D(n0)/D(n)).sqrt())])
for n in [4,25,100,400]:
 for seed in [0,1,10704,4294967295]:
  state=seed
  def uniform():
   global state
   state=(1664525*state+1013904223)&0xffffffff
   return (state+.5)/4294967296
  rows=[];margin=1.96*10/math.sqrt(n)
  for study in range(1,11):
   total=0
   for j in range(n):total+=70+10*math.sqrt(-2*math.log(uniform()))*math.cos(2*math.pi*uniform())
   mean=total/n;lo=mean-margin;hi=mean+margin
   rows.append([study,mean,lo,hi,lo<=70<=hi])
  out['sampling'].append({'n':n,'count':10,'seed':seed,'margin':margin,'se':10/math.sqrt(n),'rows':rows})
print(json.dumps(out))
`],{encoding:'utf8',maxBuffer:4*1024*1024}));
for(const [mu,sd,x,p,z] of oracle.normal){close(M.density(x,mu,sd),p);close(M.normal(mu,sd,x).z,z);}
for(const [estimate,margin,comparison,lo,hi,width,inside] of oracle.interval){const f=M.interval(estimate,margin,comparison);close(f.lo,lo);close(f.hi,hi);close(f.width,width);assert.equal(f.inside,inside);}
for(const [n0,E0,n,margin] of oracle.precision)close(M.precision(n0,E0,n).margin,margin);
for(const f of oracle.sampling){const s=M.simulate(f);close(s.se,f.se);close(s.margin,f.margin);assert.equal(s.rows.length,10);s.rows.forEach((row,i)=>{for(const [j,k] of ['study','mean','lo','hi','contains'].entries())typeof row[k]==='boolean'?assert.equal(row[k],f.rows[i][j]):close(row[k],f.rows[i][j]);});assert.equal(s.covered,f.rows.filter(row=>row[4]).length);}
for(const [mu,sd] of [[0,1],[50,5],[50,10],[200,40]]){
 let integral=0;const steps=10000,h=16*sd/steps;for(let i=0;i<=steps;i++)integral+=M.density(mu-8*sd+i*h,mu,sd)*(i===0||i===steps?.5:1)*h;close(integral,1,1e-8);
 for(const z of [0,.5,1,2,3])close(M.density(mu-z*sd,mu,sd),M.density(mu+z*sd,mu,sd));
}
assert.equal(M.normal(180,15,210).z,2);assert.equal(M.normal(35,8,59).z,3);assert.equal(M.normal(75,10,95).z,2);assert.equal(M.normal(50,10,65).z,1.5);
assert.deepEqual(M.normal(50,10,65).bands.map(b=>[b.lo,b.hi,b.central,b.tail]),[[40,60,68,16],[30,70,95,2.5],[20,80,99.7,.15]]);
assert.equal(M.interval(54,5,50).inside,true);assert.equal(M.interval(243,8,230).inside,false);assert.equal(M.interval(.3,.6,.9).inside,true);assert.equal(M.interval(4.2,.3,4).inside,true);assert.equal(M.interval(4.2,.1,4).inside,false);assert.equal(M.interval(0,0,0).inside,true);close(M.precision(200,10,800).margin,5);
for(const args of [[-1,5,5],[201,5,5],[50,0,60],[50,41,60],[50,10,-1],[50,10,251],[50,10,60,4],[NaN,5,5]])assert.throws(()=>M.normal(...args));
for(const args of [[0,0,0],[1,0,0],[1,1,Infinity]])assert.throws(()=>M.density(...args));
for(const args of [[0,-1,0],[NaN,1,0],[0,1000001,0],[1e10,1,0]])assert.throws(()=>M.interval(...args));
for(const args of [[0,1,4],[1,1,0],[1.5,1,4],[1,0,4],[1,1001,4],[1,1,1000001]])assert.throws(()=>M.precision(...args));
for(const args of [{n:3},{n:25.5},{count:9},{count:101},{count:50.5},{seed:-1},{seed:4294967296},{seed:1.5}])assert.throws(()=>M.simulate(args));
const means=[],contains=[];for(let seed=10;seed<20;seed++){const f=M.simulate({n:25,count:100,seed});means.push(...f.rows.map(x=>x.mean));contains.push(...f.rows.map(x=>x.contains));}
const avg=means.reduce((a,b)=>a+b,0)/means.length,sd=Math.sqrt(means.reduce((a,b)=>a+(b-avg)**2,0)/(means.length-1));assert.ok(Math.abs(avg-70)<.2);assert.ok(Math.abs(sd-2)<.15);assert.ok(Math.abs(contains.filter(Boolean).length/contains.length-.95)<.03);

let checked=0;
for(const file of Object.keys(snapshots)){
 const page=open(file),form=page.document.querySelector('[data-answer-store]');if(!form){page.document.querySelector('[data-print-page]').click();assert.equal(page.window.prints,1);continue;}
 const fields=form.querySelectorAll('[data-answer]'),groups=form.querySelectorAll('[data-check-group]');
 for(const group of groups){group.querySelector('[data-check]').click();assert.ok(group.querySelector('.section-feedback').textContent.includes('0 of'));}
 for(const el of fields){el.value=el.dataset.answer;el.dispatch('input');checked++;}
 for(const group of groups){group.querySelector('[data-check]').click();assert.ok(group.querySelector('.section-feedback').textContent.includes(group.querySelector('textarea')?'All numerical and choice responses are correct.':'Every response is correct.'));}
 for(const el of fields)assert.equal(el.getAttribute('aria-invalid'),'false');
 if(fields.length){const first=fields[0],group=first.closest('[data-check-group]');first.value='';first.dispatch('input');assert.equal(group.querySelector('.section-feedback').textContent,'');group.querySelector('[data-check]').click();assert.ok(first.closest('.question').querySelector('.field-feedback').textContent.startsWith('Enter a response.'));first.value=first.dataset.answer;first.dispatch('input');group.querySelector('[data-check]').click();}
 const written=form.querySelector('textarea[data-save]');if(written){written.value='The interval estimates a population mean; individual measurements have a different spread.';written.dispatch('input');}
 const key=form.dataset.answerStore,legacy=form.dataset.legacyStore,saved=JSON.parse(page.data[key]);assert.ok(saved.fields);const restored=open(file,{[key]:page.data[key]});for(const el of fields)assert.equal(restored.$(el.id).value,el.dataset.answer);if(written)assert.equal(restored.$(written.id).value,written.value);
 if(legacy){const values=Object.fromEntries(fields.map(el=>[el.id,el.dataset.answer])),old=file==='labs/week4_lab.html'?{values,completed:[true,true,true,true,true]}:values,r=open(file,{[legacy]:JSON.stringify(old)});for(const el of fields)assert.equal(r.$(el.id).value,el.dataset.answer);const partialValues={[fields[0].id]:fields[0].dataset.answer},partial=open(file,{[legacy]:JSON.stringify(file==='labs/week4_lab.html'?{values:partialValues,completed:[true,true,true,true,true]}:partialValues)});if(partial.$('progressText'))assert.ok(partial.$('progressText').textContent.startsWith('0 /'));else assert.ok(fields.slice(1).every(el=>partial.$(el.id).value===''));}
 const print=page.document.querySelector('[data-print-work]');print.click();assert.equal(page.window.prints,0);page.$('studentName').value='Student Example';print.click();assert.equal(page.window.prints,1);assert.equal(page.$('printName').textContent,'Student: Student Example');assert.equal(page.document.querySelectorAll('.print-answer').length,form.querySelectorAll('.question input,.question select,.question textarea').length);for(const fn of page.events.afterprint||[])fn();assert.equal(page.document.querySelectorAll('.print-answer').length,0);
 const disabled=open(file,{__failStorage:true});assert.ok(disabled.$('saveStatus').textContent.includes('unavailable'));if(fields.length){disabled.$(fields[0].id).value=fields[0].dataset.answer;disabled.$(fields[0].id).dispatch('input');}
}
assert.equal(checked,59);
const zero=open('labs/week4_lab.html');zero.$('z100').value='';zero.$('z100').closest('[data-check-group]').querySelector('[data-check]').click();assert.equal(zero.$('z100').getAttribute('aria-invalid'),'true');zero.$('z100').value='0';zero.$('z100').dispatch('input');zero.$('z100').closest('[data-check-group]').querySelector('[data-check]').click();assert.equal(zero.$('z100').getAttribute('aria-invalid'),'false');
const originalSchemas=JSON.parse(fs.readFileSync('scripts/week4_response_contracts.json','utf8'));
for(const [file,schema] of Object.entries(originalSchemas)){
 const fresh=open(file),form=fresh.document.querySelector('[data-answer-store]');if(!form||!form.dataset.legacyStore)continue;
 const values={};for(const field of schema){const id=field.attrs.id;if(id==='printStudentName')continue;const el=fresh.$(id);values[id]=field.tag==='textarea'?'Preserved earlier explanation for '+id:el.dataset.answer;}
 const legacy=file==='labs/week4_lab.html'?{values,completed:[true,true,true,true,true]}:values,restored=open(file,{[form.dataset.legacyStore]:JSON.stringify(legacy)});for(const [id,value] of Object.entries(values))assert.equal(restored.$(id).value,String(value));
}
const demo=open('demos/normal_z.html'),change=(id,value,event='input')=>{demo.$(id).value=value;demo.$(id).dispatch(event);};
assert.ok(demo.$('interp').textContent.includes('1.5'));assert.ok(demo.$('normalPlot').innerHTML.includes('<svg'));assert.equal(demo.$('empiricalTable').querySelectorAll('tbody tr').length,3);assert.equal(demo.$('normalWindow').value,'fixed');
for(const [preset,expected] of [['apples',2],['commute',3],['scores',2]]){change('preset',preset,'change');assert.ok(demo.$('interp').textContent.includes('= '+expected+'.'));assert.equal(demo.$('normalError').textContent,'');}
for(const k of [1,2,3]){change('normalBand',k,'change');assert.ok(demo.$('normalPlot').innerHTML.includes('central '+k+'-standard-deviation region'));}
change('normalWindow','follow','change');assert.ok(demo.$('normalPlotNote').textContent.includes('follows the model'));change('mu',50);assert.equal(demo.$('preset').value,'custom');
for(const id of ['mu','sig','xx']){const old=demo.$(id).value;change(id,'');assert.ok(demo.$('normalError').textContent.includes('valid number'));assert.equal(demo.$('normalPlot').innerHTML,'');assert.equal(demo.$('empiricalTable').children.length,0);change(id,old);}
const tabs=['zTab','ciTab','coverageTab'],panels=['zMode','ciMode','coverageMode'];for(let i=0;i<3;i++){demo.$(tabs[i]).click();tabs.forEach((id,j)=>{assert.equal(demo.$(id).getAttribute('aria-selected'),String(i===j));assert.equal(demo.$(panels[j]).hidden,i!==j);});}
demo.$('coverageTab').dispatch('keydown',{key:'ArrowRight'});assert.equal(demo.$('zTab').getAttribute('aria-selected'),'true');demo.$('zTab').dispatch('keydown',{key:'ArrowLeft'});assert.equal(demo.$('coverageTab').getAttribute('aria-selected'),'true');demo.$('coverageTab').dispatch('keydown',{key:'Home'});assert.equal(demo.$('zTab').getAttribute('aria-selected'),'true');demo.$('zTab').dispatch('keydown',{key:'End'});assert.equal(demo.$('coverageTab').getAttribute('aria-selected'),'true');
for(const [hash,id] of [['#ciMode','ciTab'],['#coverageMode','coverageTab'],['#unknown','zTab']])assert.equal(open('demos/normal_z.html',{__hash:hash}).$(id).getAttribute('aria-selected'),'true');
assert.ok(demo.$('ciText').textContent.includes('[49, 59]'));assert.ok(demo.$('ciInterp').textContent.includes('inside'));change('est',63);change('err',3);change('claimVal',60);assert.ok(demo.$('ciInterp').textContent.includes('inside'));change('claimVal',59);assert.ok(demo.$('ciInterp').textContent.includes('outside'));
for(const id of ['est','err','claimVal']){const old=demo.$(id).value;change(id,'');assert.equal(demo.$('ciPlot').innerHTML,'');assert.equal(demo.$('ciTable').children.length,0);change(id,old);}
assert.ok(demo.$('scaledE').textContent.includes('margin: 5.'));for(const invalid of ['',0,-1,1.5]){change('newN',invalid);assert.equal(demo.$('precisionTable').children.length,0);}change('newN',900);assert.ok(demo.$('scaledE').textContent.includes('3.333333'));
assert.equal(demo.$('coverageTable').querySelectorAll('tbody tr').length,50);const run0=demo.$('coveragePlot').innerHTML;demo.$('newCoverage').click();assert.notEqual(demo.$('coveragePlot').innerHTML,run0);change('coverageSeed',10704);assert.equal(demo.$('coveragePlot').innerHTML,run0);
for(const n of [4,25,100,400]){change('coverageN',n,'change');assert.ok(demo.$('coverageSummary').textContent.includes('n = '+n+','));assert.equal(demo.$('coverageTable').querySelectorAll('tbody tr').length,50);}
change('coverageSeed',0);assert.ok(demo.$('coverageSummary').textContent.includes('Seed: 0.'));change('coverageSeed',4294967295);demo.$('newCoverage').click();assert.equal(demo.$('coverageSeed').value,'0');
for(const [id,invalid] of [['coverageSeed',-1],['coverageCount',9],['coverageCount',50.5],['coverageCount','']]){const old=demo.$(id).value;change(id,invalid);assert.equal(demo.$('coveragePlot').innerHTML,'');assert.equal(demo.$('coverageTable').children.length,0);change(id,old);}
for(const [file,snapshot] of Object.entries(snapshots)){const root=fromJSON(snapshot),config=root.querySelectorAll('script').find(el=>el.textContent.includes('window.MathJax=')),c={window:{}};vm.runInNewContext(config.textContent,c);assert.equal(c.window.MathJax.tex.inlineMath[0][0],'\\(');assert.equal(c.window.MathJax.tex.displayMath[0][0],'\\[');}
console.log('PASS: 200 independent normal-density/z-score comparisons, 360 Decimal interval and 120 precision comparisons, 16 seeded sampling oracles, density integrals and sampling moments; seven page initializations, 59 original answers, legacy restores, blank/zero handling, saved writing, named printing, storage failure; explorer tabs, controls, seeded coverage, invalid states, and mathematical rendering configuration.');
