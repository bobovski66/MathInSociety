/* Independent numerical checks and DOM-level student interaction tests. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),{execFileSync}=require('node:child_process');
const M=require('../assets/week8/week8.js');const close=(a,b,t=1e-8)=>assert.ok(Math.abs(a-b)<=t*Math.max(1,Math.abs(a),Math.abs(b)),`${a} != ${b}`);
const snapshots=JSON.parse(execFileSync('python3',['scripts/verify_week8.py','--dom-json'],{encoding:'utf8'}));
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
 const sandbox={document,window,localStorage:{getItem:k=>{if(initial.__failStorage)throw Error('Storage disabled');return data[k]??null;},setItem:(k,v)=>{if(initial.__failStorage)throw Error('Storage disabled');data[k]=String(v);}},Math,console};sandbox.globalThis=sandbox;vm.runInNewContext(fs.readFileSync('assets/week8/week8.js','utf8'),sandbox,{filename:'week8.js'});return{root,document,window,data,$:id=>document.getElementById(id),events};
}
assert.ok(Number.isNaN(M.number('')));assert.ok(Number.isNaN(M.number('1/0')));assert.ok(Number.isNaN(M.number('2+2')));close(M.number('7/2'),3.5);
for(const [name,value,best] of [['snacks',20,[[4,4]]],['workshop',540,[[8,6]]],['textbook',195,[[30,15]]],['furniture',2600,[[30,20]]],['tomatoes',1700,[[20,30]]],['nutrition',8.1875,[[3.125,1.75]]],['integer',33,[[1,3.5]]]]){const s=M.solve(M.models[name]);assert.equal(s.status,'optimal',name);close(s.value,value);assert.deepEqual(s.best,best);}
assert.deepEqual(M.solve(M.models.snacks).vertices,[[0,0],[6,0],[4,4],[0,8]]);assert.equal(M.feasible([5,3],M.models.snacks),false);assert.equal(M.feasible([3,3],M.models.snacks),true);
assert.deepEqual(M.solve(M.models.tie).best,[[4,1],[0,5]]);assert.equal(M.solve(M.models.empty).status,'infeasible');assert.equal(M.solve(M.models.unbounded).status,'unbounded');
assert.equal(M.solve({...M.models.nutrition,dir:'max'}).status,'unbounded');const flat=M.solve({...M.models.nutrition,cx:1,cy:0});assert.equal(flat.status,'optimal');assert.ok(flat.flatRays.length>0);const zero=M.solve({...M.models.nutrition,cx:0,cy:0});assert.equal(zero.constant,true);assert.equal(zero.value,0);
for(const scale of [1e-12,1e-6,1,1e6]){const s=M.solve({...M.models.snacks,cx:3*scale,cy:2*scale});assert.deepEqual(s.best,[[4,4]]);close(s.value/scale,20);assert.equal(M.solve({...M.models.unbounded,cx:scale,cy:0}).status,'unbounded');}
const whole=M.whole(M.models.integer);assert.equal(whole.value,32);assert.deepEqual(whole.best,[[0,4]]);assert.equal(M.feasible([1,4],M.models.integer),false);assert.equal(M.feasible([1,3],M.models.integer),true);assert.equal(5*1+8*3,29);
assert.equal(M.whole(M.models.nutrition).status,'unavailable');assert.equal(M.whole({cons:[{a:1,b:0,c:.2,s:'ge'},{a:1,b:0,c:.8,s:'le'},{a:0,b:1,c:0,s:'le'}],cx:1,cy:1,dir:'max'}).status,'infeasible');
assert.deepEqual(M.mix([[2,1],[8,5]],[.75,.25]).point,[3.5,2]);assert.deepEqual(M.mix([[2,1],[8,5],[2,7]],[2,1,1]).point,[3.5,3.5]);assert.throws(()=>M.mix([[1,2],[3,4]],[0,0]));assert.throws(()=>M.mix([[1,2],[3,4]],[1,-.1]));assert.throws(()=>M.mix([[1,2],[3,4]],[NaN,1]));
// HiGHS solves independently rather than repeating this implementation's vertex method.
const fixtures=JSON.parse(execFileSync('python3',['-c',String.raw`
import json,random
from scipy.optimize import linprog
r=random.Random(10708);out=[]
for i in range(320):
 cons=[]
 for j in range(r.randrange(0,5)):
  a,b=r.randrange(-2,6),r.randrange(-2,6)
  if not (a or b):a=1
  cons.append({'a':a,'b':b,'c':r.randrange(-5,36),'s':r.choice(['le','le','ge'])})
 cx,cy=r.randrange(-4,9),r.randrange(-4,9);direction=r.choice(['max','min'])
 A=[];B=[]
 for q in cons:
  sign=1 if q['s']=='le' else -1;A.append([sign*q['a'],sign*q['b']]);B.append(sign*q['c'])
 result=linprog([(-1 if direction=='max' else 1)*cx,(-1 if direction=='max' else 1)*cy],A_ub=A or None,b_ub=B or None,bounds=[(0,None),(0,None)],method='highs')
 if result.status not in [0,2,3]:raise RuntimeError(result.message)
 out.append({'g':{'cons':cons,'cx':cx,'cy':cy,'dir':direction},'status':{0:'optimal',2:'infeasible',3:'unbounded'}[result.status],'value':(-result.fun if direction=='max' else result.fun) if result.status==0 else None})
print(json.dumps(out))
`],{encoding:'utf8',maxBuffer:2e6}));
for(const f of fixtures){const s=M.solve(f.g);assert.equal(s.status,f.status,JSON.stringify(f.g));if(f.status==='optimal')close(s.value,f.value,1e-7);for(const p of s.vertices)assert.equal(M.feasible(p,f.g),true);}
for(const file of Object.keys(snapshots)){
 const t=open(file),form=t.document.querySelector('[data-answer-store]');assert.ok(t.document.querySelector('h1'));
 // MathJax receives a single slash plus the delimiter character.
 const cfg=fs.readFileSync(file,'utf8').match(/<script>(window.MathJax=.*?)<\/script>/s)[1],box={window:{}};vm.runInNewContext(cfg,box);assert.equal(box.window.MathJax.tex.inlineMath[0][0],'\\(');
 if(form){const fields=t.document.querySelectorAll('[data-answer]'),writing=t.document.querySelectorAll('textarea[data-save]'),groups=t.document.querySelectorAll('[data-check-group]');if(groups.length){groups[0].querySelector('[data-check]').click();assert.ok(fields[0].closest('.question').className.includes('incorrect'));for(const f of fields){f.value=f.dataset.answer;f.dispatch('input');}for(const g of groups)g.querySelector('[data-check]').click();assert.equal(t.$('progressText').textContent,`${groups.length} / ${groups.length} sections checked`);fields[0].value='';fields[0].dispatch('input');assert.equal(t.$('progressText').textContent,`${groups.length-1} / ${groups.length} sections checked`);}
  for(const w of writing){w.value='My resource totals establish feasibility.\nThe objective compares feasible plans.';w.dispatch('input');}const again=open(file,t.data);for(const w of writing)assert.equal(again.$(w.id).value,w.value);if(fields.length>1)assert.equal(again.$(fields[1].id).value,fields[1].value);
  t.document.querySelector('[data-print-work]').click();assert.equal(t.window.prints,0);t.$('studentName').value='Test Student';t.document.querySelector('[data-print-work]').click();assert.equal(t.window.prints,1);assert.equal(t.document.querySelectorAll('.print-answer').length,fields.length+writing.length);assert.equal(t.$('printName').textContent,'Student: Test Student');assert.equal(t.$('main').children[1].id,'printName','printed name is next to the assignment title');for(const fn of t.events.afterprint||[])fn();assert.equal(t.document.querySelectorAll('.print-answer').length,0);
 }
}
let old=open('labs/week8_lab.html',{math107_week8_lab_v3:JSON.stringify({p1a:'yes',p1b:'no',p1c:'yes',p1d:'no',p1e:'quadrant',done:[true,true,true,true,true]})});assert.equal(old.$('p1a').value,'yes');assert.equal(old.$('progressText').textContent,'1 / 5 sections checked');
old=open('labs/week8_optimization_lab.html',{math107_week8_optimization_lab_v1:JSON.stringify({p1a:'right',p1b:'right',p1c:'200',p1d:'150',p1e:'max',done:[true,true,true,true,true]})});assert.equal(old.$('progressText').textContent,'1 / 5 sections checked');
old=open('applications/week8_application.html',{math107_week8_application_v2:JSON.stringify({b1:36,b2:13,b3:'yes',b4:40,b5:15,b6:'no'})});assert.equal(old.$('progressText').textContent,'1 / 3 sections checked');
old=open('applications/week8_ai.html',{math107_ai_module_8_v4:JSON.stringify({q1:'Yes',q2:3.5,q3:2,q4:'On the line segment joining A and B'})});assert.equal(old.$('progressText').textContent,'3 / 3 sections checked');
const unavailable=open('labs/week8_lab.html',{__failStorage:true});assert.ok(unavailable.$('saveStatus').textContent.includes('unavailable'));unavailable.$('p2a').value='8';unavailable.$('p2a').dispatch('input');assert.ok(unavailable.$('saveStatus').textContent.includes('unavailable'));
const geo=open('demos/convex_geometry.html');assert.equal(geo.$('geomCount').textContent,'4');assert.ok(geo.$('geomTest').textContent.includes('feasible:'));geo.$('testX').value=5;geo.$('testY').value=3;geo.$('testX').dispatch('input');assert.ok(geo.$('geomTest').textContent.includes('infeasible:'));geo.$('c1').value=0;geo.$('c1').dispatch('input');assert.equal(geo.$('geomCount').textContent,'1');assert.equal(geo.$('geomShape').textContent,'Single feasible point');geo.$('testX').value='';geo.$('testX').dispatch('input');assert.ok(geo.$('geomTest').textContent.includes('blank value is not zero'));
const lp=open('demos/linear_programming.html');assert.equal(lp.$('lpBest').textContent,'20');lp.$('cx').value=1;lp.$('cy').value=4;lp.$('cx').dispatch('input');assert.equal(lp.$('lpBest').textContent,'32');assert.equal(lp.$('lpPlan').textContent,'(0, 8)');lp.$('cx').value=1;lp.$('cy').value=1;lp.$('cx').dispatch('input');assert.equal(lp.$('lpStatus').textContent,'Tied best plans');assert.ok(lp.$('lpConclusion').textContent.includes('segment'));
for(const [preset,status] of [['empty','No feasible plans'],['unbounded','Unbounded score']]){lp.$('lpPreset').value=preset;lp.$('lpPreset').dispatch('change');assert.equal(lp.$('lpStatus').textContent,status);assert.equal(lp.$('lpBest').textContent,'—');}
lp.$('lpPreset').value='nutrition';lp.$('lpPreset').dispatch('change');assert.equal(lp.$('lpBest').textContent,'8.188');lp.$('lpDirection').value='max';lp.$('lpDirection').dispatch('change');assert.equal(lp.$('lpStatus').textContent,'Unbounded score');lp.$('lpDirection').value='min';lp.$('cx').value=0;lp.$('cy').value=0;lp.$('cy').dispatch('input');assert.ok(lp.$('lpConclusion').textContent.includes('Every feasible point'));
lp.$('lpPreset').value='integer';lp.$('lpPreset').dispatch('change');assert.equal(lp.$('lpBest').textContent,'33');assert.ok(lp.$('wholeSummary').textContent.includes('value: 32 at (0, 4)'));lp.$('cx').value='';lp.$('cx').dispatch('input');assert.equal(lp.$('lpStatus').textContent,'Enter valid coefficients');assert.equal(lp.$('lpPlot').children.length,0);
const app=open('applications/week8_application.html');assert.ok(app.$('workshopSummary').textContent.includes('$540'));for(const [scenario,expected] of [['wood','$620'],['slots','$580'],['values','$700']]){app.$('workshopScenario').value=scenario;app.$('workshopScenario').dispatch('change');assert.ok(app.$('workshopSummary').textContent.includes(expected));}
const ai=open('applications/week8_ai.html');assert.ok(ai.$('mixSummary').textContent.includes('(3.5, 2)'));ai.$('mixWeight').value=1;ai.$('mixWeight').dispatch('input');assert.ok(ai.$('mixSummary').textContent.includes('(2, 1)'));ai.$('mixWeight').value=0;ai.$('mixWeight').dispatch('input');assert.ok(ai.$('mixSummary').textContent.includes('(8, 5)'));assert.ok(ai.$('triangleSummary').textContent.includes('(3.5, 3.5)'));for(const id of ['amountA','amountB','amountC'])ai.$(id).value=0;ai.$('amountA').dispatch('input');assert.ok(ai.$('triangleError').textContent.includes('positive amount'));ai.$('amountA').value=-1;ai.$('amountA').dispatch('input');assert.ok(ai.$('triangleError').textContent.includes('nonnegative'));assert.equal(ai.$('trianglePlot').children.length,0);
console.log('PASS: all fixed examples; 320 independent HiGHS comparisons; finite/infeasible/unbounded/flat cases; whole-number optima; mixtures; all eight page initializations; 94 original answer contracts; individual feedback; legacy restores; saving, writing, and printing; storage failure; both explorers; workshop changes; and valid/invalid mixture inputs.');
