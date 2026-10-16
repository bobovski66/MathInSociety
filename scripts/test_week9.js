/* Verify exact network results and real page event handlers without a browser. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),{execFileSync}=require('node:child_process');
const M=require('../assets/week9/week9.js'),g=M.presets.bridge;
const close=(a,b,t=1e-12)=>assert.ok(Math.abs(a-b)<t,`${a} != ${b}`);
const snapshots=JSON.parse(execFileSync('python3',['scripts/verify_week9.py','--dom-json'],{encoding:'utf8'}));
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
 const sandbox={document,window,localStorage:{getItem:k=>data[k]??null,setItem:(k,v)=>data[k]=String(v)},Math,console};sandbox.globalThis=sandbox;vm.runInNewContext(fs.readFileSync('assets/week9/week9.js','utf8'),sandbox,{filename:'week9.js'});return{root,document,window,data,$:id=>document.getElementById(id),events};
}
assert.ok(Number.isNaN(M.number('')));assert.ok(Number.isNaN(M.number('1/0')));assert.ok(Number.isNaN(M.number('2+2')));assert.ok(Number.isNaN(M.number('Infinity')));close(M.number('9 / 21'),3/7);close(M.number('-1/2'),-.5);
assert.deepEqual(Object.values(M.adjacency(g)).map(a=>a.length),[2,3,3,3,3,2,2]);
assert.deepEqual(M.bridges(g),['DE']);assert.deepEqual(M.bridges(M.presets.mesh),[]);
assert.deepEqual(M.components(M.presets.disconnected),[[...'ABCD'],[...'EFG']]);
assert.equal(M.path(M.presets.disconnected,'A','G'),null);assert.deepEqual(M.path(g,'A','A'),['A']);assert.deepEqual(M.path(g,'A','G'),[...'ABDEG']);
assert.deepEqual(Object.values(M.distances(g,'A').d),[0,1,1,2,3,4,4]);assert.deepEqual(Object.values(M.distances(g,'D').d),[2,1,1,0,1,2,2]);
assert.deepEqual(M.nodes.map(n=>Object.values(M.distances(g,n).d).reduce((a,b)=>a+b)),[15,11,11,9,10,14,14]);
assert.deepEqual(M.sequence(g,['A']).map(s=>s.new),[['A'],['B','C'],['D'],['E'],['F','G']]);
assert.deepEqual(M.sequence(g,['B','C'],'half').map(s=>s.active),[[...'BC'],[...'ABCD'],[...'ABCD']]);
assert.deepEqual(M.sequence(g,['B','C','F'],'half').map(s=>s.active),[[...'BCF'],[...'ABCDFG'],[...'ABCDEFG']]);
const isolated={nodes:['A','B'],edges:[]};assert.deepEqual(M.step(isolated,['A'],'half'),{active:['A'],new:[]});assert.deepEqual(M.sequence(g,[],'half').at(-1).active,[]);assert.throws(()=>M.step(g,['A'],'unknown'));
// Independent all-pairs matrix calculation verifies every single add/remove combination.
const missing=[];for(let i=0;i<7;i++)for(let j=i+1;j<7;j++){const e=[M.nodes[i],M.nodes[j]];if(!g.edges.some(x=>M.key(x)===M.key(e)))missing.push(e);}
for(const rem of [null,...g.edges])for(const add of [null,...missing]){
 const test={nodes:g.nodes,edges:[...g.edges.filter(e=>e!==rem),...(add?[add]:[])]},d=g.nodes.map((_,i)=>g.nodes.map((_,j)=>i===j?0:Infinity));
 for(const [u,v] of test.edges){const i=g.nodes.indexOf(u),j=g.nodes.indexOf(v);d[i][j]=d[j][i]=1;}
 for(let k=0;k<7;k++)for(let i=0;i<7;i++)for(let j=0;j<7;j++)d[i][j]=Math.min(d[i][j],d[i][k]+d[k][j]);
 assert.equal(Object.values(M.adjacency(test)).reduce((s,a)=>s+a.length,0),2*test.edges.length);
 for(let i=0;i<7;i++){assert.deepEqual(Object.values(M.distances(test,g.nodes[i]).d),d[i]);const h=M.sequence(test,[g.nodes[i]]),first={};h.forEach((r,k)=>r.new.forEach(n=>first[n]=k));for(let j=0;j<7;j++)assert.equal(first[g.nodes[j]]??Infinity,d[i][j]);}
}
for(let a=0;a<=6;a+=.5)for(let b=0;b<=6;b+=.5){close(M.signal(a,b).o,a);close(M.signal(a,b,{drop:true}).o,a-.375*b);}
assert.deepEqual(M.signal(2,4),{raw1:2,raw2:2,h1:2,h2:2,o:2});close(M.signal(2,4,{drop:true}).o,.5);close(M.signal(4,0,{relu:true}).o,3);close(M.signal(2,4,{outputWeight:2}).o,3);assert.throws(()=>M.signal(NaN,4));
for(const file of Object.keys(snapshots)){
 const t=open(file),form=t.document.querySelector('[data-answer-store]');assert.ok(t.document.querySelector('h1'));
 if(form){
  const fields=t.document.querySelectorAll('[data-answer]'),written=t.document.querySelectorAll('textarea[data-save]'),groups=t.document.querySelectorAll('[data-check-group]');
  if(groups.length){groups[0].querySelector('[data-check]').click();assert.ok(fields[0].closest('.question').className.includes('incorrect'),'a blank answer must fail, including a zero-answer field');for(const f of fields){f.value=f.dataset.answer;f.dispatch('input');}for(const group of groups)group.querySelector('[data-check]').click();assert.equal(t.$('progressText').textContent,`${groups.length} / ${groups.length} sections checked`);for(const f of fields)assert.equal(f.getAttribute('aria-invalid'),'false');fields[0].value='';fields[0].dispatch('input');assert.equal(t.$('progressText').textContent,`${groups.length-1} / ${groups.length} sections checked`);}
  for(const w of written){w.value='An explicit route supports my claim.\nA limitation needs more data.';w.dispatch('input');}
  const again=open(file,t.data);for(const w of written)assert.equal(again.$(w.id).value,w.value,'open responses survive reload');if(fields.length>1)assert.equal(again.$(fields[1].id).value,fields[1].value);
  t.document.querySelector('[data-print-work]').click();assert.equal(t.window.prints,0);t.$('studentName').value='Test Student';t.document.querySelector('[data-print-work]').click();assert.equal(t.window.prints,1);assert.equal(t.document.querySelectorAll('.print-answer').length,fields.length+written.length);assert.equal(t.$('printName').textContent,'Student: Test Student');for(const fn of t.events.afterprint||[])fn();assert.equal(t.document.querySelectorAll('.print-answer').length,0);
 }
}
const e=open('demos/network_systems.html');assert.equal(e.$('mEdges').textContent,'9');assert.equal(e.$('mComponents').textContent,'1');assert.equal(e.$('mReach').textContent,'7 / 7');assert.ok(e.$('bridges').textContent.includes('D–E'));
e.$('pathBtn').click();assert.ok(e.$('message').textContent.includes('A → B → D → E → G'));assert.ok(e.$('message').textContent.includes('4 edges'));
assert.equal((e.$('graph').innerHTML.match(/stroke="#a55c21" stroke-width="6"/g)||[]).length,4,'exactly the path edges are highlighted');
e.$('remove').value='DE';e.$('remove').dispatch('change');assert.equal(e.$('mComponents').textContent,'2');assert.equal(e.$('mReach').textContent,'4 / 7');e.$('pathBtn').click();assert.ok(e.$('message').textContent.includes('No path exists'));
e.$('add').value='DF';e.$('add').dispatch('change');assert.equal(e.$('mComponents').textContent,'1');assert.equal(e.$('mReach').textContent,'7 / 7');assert.equal(e.$('mEdges').textContent,'9');
e.$('preset').value='bridge';e.$('preset').dispatch('change');for(let i=0;i<4;i++)e.$('spreadBtn').click();assert.ok(e.$('spreadInfo').textContent.includes('7 total'));assert.equal(e.$('spreadBtn').disabled,true);
e.$('spreadRule').value='half';e.$('spreadRule').dispatch('change');e.$('spreadSeeds').value='bc';e.$('spreadSeeds').dispatch('change');e.$('spreadBtn').click();assert.ok(e.$('spreadInfo').textContent.includes('4 total'));assert.ok(e.$('spreadInfo').textContent.includes('A, D'));e.$('spreadBtn').click();assert.ok(e.$('spreadInfo').textContent.includes('process has stopped'));assert.equal(e.$('spreadBtn').disabled,true);
e.$('spreadSeeds').value='bcf';e.$('spreadSeeds').dispatch('change');e.$('spreadBtn').click();assert.ok(e.$('spreadInfo').textContent.includes('6 total'));e.$('spreadBtn').click();assert.ok(e.$('spreadInfo').textContent.includes('7 total'));
e.$('preset').value='star';e.$('preset').dispatch('change');e.$('spreadRule').value='automatic';e.$('spreadRule').dispatch('change');e.$('spreadSeeds').value='start';e.$('spreadSeeds').dispatch('change');assert.equal(e.$('mEdges').textContent,'6');e.$('remove').value='AD';e.$('remove').dispatch('change');assert.equal(e.$('mReach').textContent,'1 / 7');assert.equal(e.$('mDegree').textContent,'0');e.$('spreadBtn').click();assert.equal(e.$('spreadBtn').disabled,true);
const lab=open('labs/week9_lab.html');lab.$('labRound').value='2';lab.$('labRound').dispatch('input');assert.ok(lab.$('labSpreadInfo').textContent.includes('4 total'));lab.$('labNode').value='E';lab.$('labNode').dispatch('change');assert.ok(lab.$('labNeighbors').textContent.includes('D, F, G'));
const app=open('applications/week9_application.html');assert.ok(app.$('appSummary').textContent.includes('round is 4'));app.$('appScenario').value='ad';app.$('appScenario').dispatch('change');assert.ok(app.$('appSummary').textContent.includes('round is 3'));app.$('appScenario').value='failed';app.$('appScenario').dispatch('change');assert.ok(app.$('appSummary').textContent.includes('Only 4 of 7'));app.$('appScenario').value='df-failed';app.$('appScenario').dispatch('change');assert.ok(app.$('appSummary').textContent.includes('All seven'));
const ai=open('applications/week9_ai.html');assert.equal(ai.$('liveO').textContent,'2.00');ai.$('x2').value=6;ai.$('x2').dispatch('input');assert.equal(ai.$('liveH2').textContent,'3.50');assert.equal(ai.$('liveO').textContent,'2.00');ai.$('aiReset').click();ai.$('dropEdge').checked=true;ai.$('dropEdge').dispatch('input');assert.equal(ai.$('liveO').textContent,'0.50');ai.$('aiReset').click();ai.$('x1').value=4;ai.$('x2').value=0;ai.$('useRelu').checked=true;ai.$('useRelu').dispatch('input');assert.equal(ai.$('liveH2').textContent,'0.00');assert.equal(ai.$('liveO').textContent,'3.00');
// The clarified fifth quiz question has exactly one option producing the requested split.
const index=fs.readFileSync('index.html','utf8'),assessments=JSON.parse(index.split('const ASSESSMENTS = ')[1].split(';const STORAGE_KEY')[0]),q=assessments.week9.questions[4];
const four={nodes:[...'ABCD'],edges:[['A','B'],['B','C'],['C','D']]};let valid=four.edges.filter(edge=>JSON.stringify(M.components({...four,edges:four.edges.filter(e=>e!==edge)}))===JSON.stringify([['A','B'],['C','D']]));assert.deepEqual(valid,[['B','C']]);assert.equal(q.answer,'B–C');
console.log('PASS: exact degrees, paths, components, bridges, 130 add/remove cases against independent all-pairs distances, synchronous spread, isolated thresholds, signed signals, all six page initializations, per-answer feedback, autosave/reload, written responses, printing, scenario controls, AI sliders, and unambiguous quiz wording.');
