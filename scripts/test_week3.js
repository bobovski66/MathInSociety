/* Independent exact-statistics oracles and DOM-level checks for Week 3. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),{execFileSync}=require('node:child_process');
const M=require('../assets/week3/week3.js');
const close=(a,b,t=1e-10)=>assert.ok(Math.abs(a-b)<=1e-9+t*Math.max(1,Math.abs(a),Math.abs(b)),String(a)+' != '+String(b));
const snapshots=JSON.parse(execFileSync('python3',['scripts/verify_week3.py','--dom-json'],{encoding:'utf8',maxBuffer:4*1024*1024}));
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
function open(file,initial={}){
 const root=fromJSON(snapshots[file]),data={...initial},events={},window={prints:0,addEventListener(k,fn){(events[k]??=[]).push(fn);},print(){this.prints++;for(const f of events.beforeprint||[])f();}},document={readyState:'complete',querySelectorAll:q=>root.querySelectorAll(q),querySelector:q=>root.querySelector(q),getElementById:id=>root.querySelectorAll('[id]').find(x=>x.id===id)||null,createElement:tag=>new Element(tag)};
 const sandbox={document,window,localStorage:{getItem:k=>{if(initial.__failStorage)throw Error('Storage disabled');return data[k]??null;},setItem:(k,v)=>{if(initial.__failStorage)throw Error('Storage disabled');data[k]=String(v);}},Math,console};sandbox.globalThis=sandbox;const script=root.querySelectorAll('script').find(e=>e.getAttribute('src')?.startsWith('../assets/')).getAttribute('src').slice(3);vm.runInNewContext(fs.readFileSync(script,'utf8'),sandbox,{filename:script});return{root,document,window,data,$:id=>document.getElementById(id),events};
}

for(const s of ['', ' ', 'Infinity','NaN','2abc','1/0','2+2'])assert.ok(Number.isNaN(M.number(s)));
close(M.number('3/4'),.75);close(M.number('-3/2'),-1.5);close(M.number('1e-3'),.001);assert.equal(M.number('0'),0);
for(const s of ['', ' , , ', '1,2,banana','1,Infinity','1,2+2','1,1000001'])assert.throws(()=>M.parse(s));
assert.deepEqual(M.parse('0, -2, 1/2\n1e-3'),[0,-2,.5,.001]);assert.throws(()=>M.parse(Array(201).fill('1').join(',')));
const oracle=JSON.parse(execFileSync('python3',['-c',String.raw`
from fractions import Fraction as F
from decimal import Decimal as D,getcontext
import statistics as st,random,json
getcontext().prec=60;r=random.Random(10703)
datasets=[[50,51,50,49,50],[30,40,50,60,70],[5,6,7,8,9,10,85],[3,0,5,2,1,4,2,8,2,3],[0],[7,7,7],[2,4,4,6,6,8],[-5,-1,0,2],[999999.9,1000000]]
for _ in range(200):datasets.append([float(F(r.randrange(-5000,5001),r.choice([1,2,4,5,10,100]))) for i in range(r.randrange(1,51))])
out={'stats':[],'weights':[],'hist':[]}
for xs in datasets:
 q=[F(str(x)) for x in xs];mu=st.mean(q);dev=[v-mu for v in q];squares=[x*x for x in dev];ss=sum(squares);counts={x:q.count(x) for x in sorted(set(q))};high=max(counts.values());modes=[x for x,c in counts.items() if c==high] if high>1 else []
 var=st.variance(q) if len(q)>1 else None
 sd=float((D(var.numerator)/D(var.denominator)).sqrt()) if var is not None else None
 out['stats'].append({'values':xs,'mean':float(mu),'median':float(st.median(q)),'total':float(sum(q)),'range':float(max(q)-min(q)),'ss':float(ss),'variance':float(var) if var is not None else None,'sd':sd,'modes':list(map(float,modes)),'deviations':list(map(float,dev)),'squares':list(map(float,squares))})
for _ in range(120):
 xs=[F(r.randrange(-100,101),10) for i in range(r.randrange(2,13))];counts=[r.randrange(21) for x in xs]
 if not sum(counts):counts[0]=1
 ws=[F(c,sum(counts)) for c in counts];result=sum(x*w for x,w in zip(xs,ws))
 out['weights'].append({'values':list(map(float,xs)),'weights':list(map(float,ws)),'result':float(result)})
for count in [2,4,5,10,20]:
 for _ in range(20):
  lo=F(-10);hi=F(10);xs=[F(r.randrange(-100,101),10) for i in range(30)];bins=[0]*count;width=(hi-lo)/count
  for x in xs:bins[min(count-1,int((x-lo)//width))]+=1
  out['hist'].append({'values':list(map(float,xs)),'count':count,'lo':float(lo),'hi':float(hi),'bins':bins})
out['hist'].append({'values':[0,.1,.2,.3,1],'count':10,'lo':0,'hi':1,'bins':[1,1,1,1,0,0,0,0,0,1]})
print(json.dumps(out))
`],{encoding:'utf8',maxBuffer:4*1024*1024}));
for(const f of oracle.stats){const s=M.summary(f.values);close(s.mean,f.mean);close(s.median,f.median);close(s.total,f.total);close(s.range,f.range);close(s.ss,f.ss);assert.deepEqual(s.modes,f.modes);if(f.sd===null){assert.equal(s.sampleSD,null);assert.equal(s.sampleVariance,null);}else{close(s.sampleSD,f.sd);close(s.sampleVariance,f.variance);}s.deviations.forEach((x,i)=>close(x,f.deviations[i]));s.squares.forEach((x,i)=>close(x,f.squares[i]));assert.equal(s.frequency.reduce((n,x)=>n+x.count,0),s.n);close(s.populationVariance,s.ss/s.n);if(s.n>1)close(s.sampleVariance*(s.n-1),s.ss);}
for(const f of oracle.weights){const w=M.weighted(f.values,f.weights);close(w.result,f.result);close(w.weights.reduce((a,b)=>a+b,0),1);assert.ok(w.result>=Math.min(...f.values)-1e-10&&w.result<=Math.max(...f.values)+1e-10);}
for(const f of oracle.hist){const h=M.histogram(f.values,f.count,f.lo,f.hi);assert.deepEqual(h.bins.map(x=>x.count),f.bins);assert.equal(h.bins.reduce((a,b)=>a+b.count,0),f.values.length);assert.equal(h.bins.at(-1).hi,f.hi);}
for(const a of [[2,4,4,6],[-3,0,2,7],[5,5,5]]){const s=M.summary(a),shift=M.summary(a.map(x=>x+17)),scale=M.summary(a.map(x=>-3*x));close(shift.mean,s.mean+17);close(shift.sampleSD,s.sampleSD);close(scale.mean,-3*s.mean);close(scale.median,-3*s.median);close(scale.range,3*s.range);close(scale.sampleSD,3*s.sampleSD);}
for(const xs of [[],[NaN],[Infinity],[1000001]])assert.throws(()=>M.summary(xs));
for(const n of [0,1,2.5,21,NaN])assert.throws(()=>M.histogram([1,2,3],n));assert.throws(()=>M.histogram([1,2,3],3,0,2));assert.throws(()=>M.histogram([0],3,-1e308,1e308));
for(const w of [[0,0],[-1,2],[.5,.4],[NaN,1]])assert.throws(()=>M.weighted([1,2],w));assert.throws(()=>M.weighted([1],[.5,.5]));
assert.equal(M.summary([0,0,0]).sampleSD,0);assert.deepEqual(M.summary([1,2,3]).modes,[]);assert.deepEqual(M.summary([2,4,4,6,6,8]).modes,[4,6]);assert.equal(M.outlier(11).median,8);assert.equal(M.outlier(150).median,8);assert.throws(()=>M.outlier(10));

let checked=0;
for(const file of Object.keys(snapshots)){
 const page=open(file),form=page.document.querySelector('[data-answer-store]');if(!form){page.document.querySelector('[data-print-page]').click();assert.equal(page.window.prints,1);continue;}
 const fields=form.querySelectorAll('[data-answer]'),groups=form.querySelectorAll('[data-check-group]');
 for(const g of groups){g.querySelector('[data-check]').click();assert.ok(g.querySelector('.section-feedback').textContent.includes('0 of'));}
 for(const e of fields){e.value=e.dataset.answer;e.dispatch('input');checked++;}
 for(const g of groups){g.querySelector('[data-check]').click();assert.ok(g.querySelector('.section-feedback').textContent.includes(g.querySelector('textarea')?'All numerical and choice responses are correct.':'Every response is correct.'));}
 for(const e of fields)assert.equal(e.getAttribute('aria-invalid'),'false');
 if(fields.length){const first=fields[0];first.value='';first.dispatch('input');const g=first.closest('[data-check-group]');g.querySelector('[data-check]').click();assert.ok(first.closest('.question').querySelector('.field-feedback').textContent.startsWith('Enter a response.'));first.value=first.dataset.answer;first.dispatch('input');g.querySelector('[data-check]').click();}
 const written=form.querySelector('textarea[data-save]');if(written){written.value='The mean shares the total; the median identifies the ordered middle.';written.dispatch('input');}
 const key=form.dataset.answerStore,legacy=form.dataset.legacyStore,saved=JSON.parse(page.data[key]);assert.ok(saved.fields);const restored=open(file,{[key]:page.data[key]});if(written)assert.equal(restored.$(written.id).value,written.value);
 if(legacy){const values=Object.fromEntries(fields.map(e=>[e.id,e.dataset.answer])),old=file==='labs/week3_lab.html'?{values,completed:[true,true,true,true,true]}:values,r=open(file,{[legacy]:JSON.stringify(old)});for(const e of fields)assert.equal(r.$(e.id).value,e.dataset.answer);const partialValues={[fields[0].id]:fields[0].dataset.answer},partial=open(file,{[legacy]:JSON.stringify(file==='labs/week3_lab.html'?{values:partialValues,completed:[true,true,true,true,true]}:partialValues)});if(partial.$('progressText')){const expected=groups.filter(g=>{const es=g.querySelectorAll('[data-answer]');return es.length===1&&es[0].id===fields[0].id;}).length;assert.ok(partial.$('progressText').textContent.startsWith(expected+' /'));}else assert.ok(fields.slice(1).some(e=>partial.$(e.id).value===''));}
 const print=page.document.querySelector('[data-print-work]');print.click();assert.equal(page.window.prints,0);page.$('studentName').value='Student Example';print.click();assert.equal(page.window.prints,1);assert.equal(page.$('printName').textContent,'Student: Student Example');assert.equal(page.document.querySelectorAll('.print-answer').length,form.querySelectorAll('.question input,.question select,.question textarea').length);for(const fn of page.events.afterprint||[])fn();assert.equal(page.document.querySelectorAll('.print-answer').length,0);
 const disabled=open(file,{__failStorage:true});assert.ok(disabled.$('saveStatus').textContent.includes('unavailable'));if(fields.length){disabled.$(fields[0].id).value=fields[0].dataset.answer;disabled.$(fields[0].id).dispatch('input');}
}
assert.equal(checked,61);
const originalSchemas=JSON.parse(fs.readFileSync('scripts/week3_response_contracts.json','utf8'));
for(const [file,schema] of Object.entries(originalSchemas)){
 const fresh=open(file),form=fresh.document.querySelector('[data-answer-store]');if(!form||!form.dataset.legacyStore)continue;
 const values={};for(const field of schema){const id=field.attrs.id;if(id==='printStudentName')continue;const el=fresh.$(id);values[id]=field.tag==='textarea'?'Preserved earlier explanation for '+id:el.dataset.answer;}
 const legacy=file==='labs/week3_lab.html'?{values,completed:[true,true,true,true,true]}:values,restored=open(file,{[form.dataset.legacyStore]:JSON.stringify(legacy)});
 for(const [id,value] of Object.entries(values))assert.equal(restored.$(id).value,String(value));
}

const lab=open('labs/week3_lab.html');lab.$('d1').value='';lab.$('d1').closest('[data-check-group]').querySelector('[data-check]').click();assert.equal(lab.$('d1').getAttribute('aria-invalid'),'true');lab.$('d1').value='0';lab.$('d1').dispatch('input');lab.$('d1').closest('[data-check-group]').querySelector('[data-check]').click();assert.equal(lab.$('d1').getAttribute('aria-invalid'),'false');
const e=open('demos/center_spread.html'),set=(id,value,event='input')=>{e.$(id).value=value;e.$(id).dispatch(event);};
assert.equal(e.$('count').textContent,'5');assert.equal(e.$('mean').textContent,'50');assert.equal(e.$('median').textContent,'50');assert.equal(e.$('range').textContent,'2');assert.ok(e.$('sd').textContent.includes('0.707107'));assert.equal((e.$('c').innerHTML.match(/<circle/g)||[]).length,5);assert.ok(e.$('c').innerHTML.includes('role="img"'));
for(const button of e.document.querySelectorAll('[data-preset]')){button.click();assert.equal(e.$('dataError').textContent,'');assert.equal(e.$('dataResults').hidden,false);const total=e.$('binTable').querySelectorAll('tbody tr').reduce((n,r)=>n+Number(r.children[1].textContent),0);assert.equal(total,Number(e.$('count').textContent));}
set('data','0,0,0');assert.equal(e.$('dataResults').hidden,true);e.$('go').click();assert.equal(e.$('mean').textContent,'0');assert.equal(e.$('sd').textContent,'0');assert.equal(e.$('mode').textContent,'0');
set('data','7');e.$('data').dispatch('keydown',{key:'Enter',ctrlKey:true});assert.equal(e.$('count').textContent,'1');assert.equal(e.$('mean').textContent,'7');assert.ok(e.$('sd').textContent.includes('Not defined'));assert.ok(e.$('sdCalculation').textContent.includes('would be zero'));
for(const raw of ['',',,,','1,2,banana','1,Infinity']){set('data',raw);e.$('go').click();assert.equal(e.$('dataResults').hidden,true);assert.equal(e.$('c').innerHTML,'');assert.equal(e.$('frequencyTable').children.length,0);assert.equal(e.$('mean').textContent,'—');assert.notEqual(e.$('dataError').textContent,'');}
set('data','-5, 0, 5');e.$('go').click();assert.equal(e.$('mean').textContent,'0');assert.equal(e.$('range').textContent,'10');set('scaleMode','fit','change');assert.ok(e.$('plotNote').textContent.includes('fits the current data'));set('plotKind','histogram','change');assert.equal(e.$('binTable').querySelectorAll('tbody tr').length,6);assert.ok(e.$('c').innerHTML.includes('Number of observations'));
for(const invalid of ['',1,2.5,21]){set('binCount',invalid);assert.equal(e.$('dataResults').hidden,true);assert.equal(e.$('c').innerHTML,'');}set('binCount',10);assert.equal(e.$('dataResults').hidden,false);assert.equal(e.$('binTable').querySelectorAll('tbody tr').length,10);assert.equal(e.$('deviationTable').querySelectorAll('tbody tr').length,3);
set('outlierValue',11);assert.ok(e.$('outlierSummary').textContent.includes('Mean 8; median 8; range 6'));set('outlierValue',85);assert.ok(e.$('outlierSummary').textContent.includes('median 8'));assert.ok(e.$('outlierPlot').innerHTML.includes('<svg'));set('outlierValue',10);assert.equal(e.$('outlierPlot').innerHTML,'');assert.equal(e.$('outlierTable').children.length,0);
const ai=open('applications/week3_ai.html');for(const [preset,result] of [['given','7'],['equal','6.25'],['focus2','3.7']]){ai.$('weightPreset').value=preset;ai.$('weightPreset').dispatch('change');assert.ok(ai.$('weightSummary').textContent.includes('Weighted result '+result+'.'));assert.equal(ai.$('weightTable').querySelectorAll('tbody tr').length,4);assert.ok(ai.$('weightPlot').innerHTML.includes('<svg'));}
for(const [file,snapshot] of Object.entries(snapshots)){const root=fromJSON(snapshot),config=root.querySelectorAll('script').find(x=>x.textContent.includes('window.MathJax=')),c={window:{}};vm.runInNewContext(config.textContent,c);assert.equal(c.window.MathJax.tex.inlineMath[0][0],'\\(');assert.equal(c.window.MathJax.tex.displayMath[0][0],'\\[');}
console.log('PASS: 209 independent exact-statistics oracles, 120 weighted means, 101 exact histogram comparisons, transformation and boundary checks; seven actual page scripts, 61 original answers and option tokens, legacy/new restores, blank/zero handling, feedback, saved explanations, named printing, unavailable storage; presets, graph scales, histogram/deviation tables, outlier changes, weighted presets, invalid states, and math rendering configuration.');
