/* Week 7: explicit units, cent-based money inputs, and comparisons over stated choices. */
(function(root){
'use strict';
const Math7={
 number(raw){const s=String(raw).trim();if(!s)return NaN;const m=s.match(/^([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*\/\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))$/);if(m)return Number(m[2])===0?NaN:Number(m[1])/Number(m[2]);return /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(s)?Number(s):NaN;},
 cents(x){if(!Number.isFinite(x)||x<0||Math.abs(x*100-Math.round(x*100))>1e-6||x>100000)throw Error('Use nonnegative money amounts with at most two decimal places.');return Math.round(x*100);},
 linear(F,v,p){const fc=this.cents(F),vc=this.cents(v),pc=this.cents(p),mc=pc-vc,m=mc/100;let threshold,nonnegative=null,positive=null;
  if(mc>0){threshold={kind:'unique',q:fc/mc};nonnegative=Math.ceil(fc/mc);positive=Math.floor(fc/mc)+1;}
  else if(fc===0&&mc===0){threshold={kind:'all'};nonnegative=0;}
  else if(fc===0){threshold={kind:'unique',q:0};nonnegative=0;}
  else threshold={kind:'none'};
  const values=q=>{if(!Number.isFinite(q)||q<0)throw Error('Quantity must be a nonnegative finite number.');return {q,C:(fc+vc*q)/100,R:pc*q/100,P:(mc*q-fc)/100};};
  return {F:fc/100,v:vc/100,p:pc/100,m,threshold,nonnegative,positive,values,
   best(capacity,whole=true){if(!Number.isFinite(capacity)||capacity<0)throw Error('Capacity must be a nonnegative finite number.');const top=whole?Math.floor(capacity):capacity,q=mc>0?top:0;return {...values(q),q,tie:mc===0&&top>0,top};}
  };
 },
 inventory(n,s){if(![n,s].every(x=>Number.isSafeInteger(x)&&x>=0))throw Error('Prepared and sold counts must be nonnegative whole numbers.');if(s>n)throw Error('Meals sold cannot exceed meals prepared.');return {C:(24000+350*n)/100,R:950*s/100,P:(950*s-24000-350*n)/100,unsold:n-s};},
 service(capacity,minimum,goal){if(![capacity,minimum].every(x=>Number.isSafeInteger(x)&&x>=0))throw Error('Capacity and commitment must be nonnegative whole session counts.');if(!['profit','cost','sessions'].includes(goal))throw Error('Choose a supported objective.');if(minimum>capacity)return {status:'infeasible'};const q=goal==='cost'?minimum:capacity;return {status:'optimal',...this.linear(6000,.4,2.4).values(q),minimum,capacity};}
};
root.Math7=Math7;if(typeof module!=='undefined'&&module.exports)module.exports=Math7;
if(typeof document==='undefined')return;
const $=id=>document.getElementById(id),text=(id,v)=>{if($(id))$(id).textContent=v;},fmt=x=>Number(x.toPrecision(10)).toLocaleString('en-US',{maximumFractionDigits:4}),money=x=>(x<0?'−':'')+'$'+Math.abs(x).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function table(id,headers,rows){const out=$(id);if(!out)return;const t=document.createElement('table'),head=document.createElement('thead'),tr=document.createElement('tr');for(const h of headers){const c=document.createElement('th');c.scope='col';c.textContent=h;tr.append(c);}head.append(tr);t.append(head);const body=document.createElement('tbody');for(const row of rows){const r=document.createElement('tr');for(const v of row){const c=document.createElement('td');c.textContent=v;r.append(c);}body.append(r);}t.append(body);out.replaceChildren(t);}
function read(id,max,integer=false){const x=Math7.number($(id).value);if(!Number.isFinite(x)||x<0||x>max||(integer&&!Number.isInteger(x)))throw Error('Enter a '+(integer?'whole ':'')+'number from 0 to '+fmt(max)+' in '+$(id).previousElementSibling.textContent+'.');return x;}
function businessPlot(g,q,capacity){
 const id='businessPlot',w=940,h=560,L=110,R=30,T=55,B=85,xmax=Math.max(10,capacity*1.2,q*1.15),ymax=Math.max(1,g.values(xmax).C,g.values(xmax).R)*1.1,X=x=>L+(w-L-R)*x/xmax,Y=y=>h-B-(h-T-B)*y/ymax,r=g.values(q),be=g.threshold;
 let s=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" role="img" aria-labelledby="${id}-title ${id}-desc"><title id="${id}-title">Cost and revenue at the same quantity</title><desc id="${id}-desc">Cost C(q)=${g.F}+${g.v}q; revenue R(q)=${g.p}q. Selected quantity ${q}: cost ${r.C}, revenue ${r.R}, profit ${r.P} dollars. Capacity is ${capacity}. The numerical table provides nearby values.</desc><rect width="940" height="560" fill="white"/><rect x="${X(capacity)}" y="${T}" width="${X(xmax)-X(capacity)}" height="${h-B-T}" fill="#f2f0e9"/>`;
 for(let i=0;i<=5;i++){const x=xmax*i/5,y=ymax*i/5;s+=`<path d="M${X(x)} ${T}V${h-B}M${L} ${Y(y)}H${w-R}" stroke="#d8ddcd"/><text x="${X(x)}" y="${h-B+25}" text-anchor="middle" font-size="13">${fmt(x)}</text><text x="${L-12}" y="${Y(y)+5}" text-anchor="end" font-size="13">$${fmt(y)}</text>`;}
 s+=`<line x1="${L}" y1="${Y(g.F)}" x2="${X(xmax)}" y2="${Y(g.values(xmax).C)}" stroke="#a55c21" stroke-width="3.5"/><line x1="${L}" y1="${Y(0)}" x2="${X(xmax)}" y2="${Y(g.values(xmax).R)}" stroke="#17677a" stroke-width="3.5"/><path d="M${X(capacity)} ${T}V${h-B}" stroke="#536240" stroke-width="2" stroke-dasharray="7 5"/><text x="${X(capacity)-6}" y="${T-12}" text-anchor="end" font-size="14">Capacity ${fmt(capacity)}</text>`;
 s+=`<path d="M${X(q)} ${Y(0)}V${Y(Math.max(r.C,r.R))}" stroke="#797e70" stroke-dasharray="4 4"/><line x1="${X(q)}" y1="${Y(r.C)}" x2="${X(q)}" y2="${Y(r.R)}" stroke="#b18a22" stroke-width="7"/><circle cx="${X(q)}" cy="${Y(r.C)}" r="5" fill="#a55c21"/><circle cx="${X(q)}" cy="${Y(r.R)}" r="5" fill="#17677a"/>`;
 if(be.kind==='unique'&&be.q<=xmax){s+=`<circle cx="${X(be.q)}" cy="${Y(g.values(be.q).R)}" r="6" fill="#293329"/>`;}
 s+=`<path d="M${L} ${T}V${h-B}H${w-R}" fill="none" stroke="#293329" stroke-width="2"/><text x="${(L+w-R)/2}" y="${h-25}" text-anchor="middle" font-size="16">Quantity in one period, q</text><text x="24" y="${(T+h-B)/2}" transform="rotate(-90 24 ${(T+h-B)/2})" text-anchor="middle" font-size="16">Dollars for that period</text><text x="${L}" y="25" fill="#17677a" font-size="16">Revenue R(q)</text><text x="${L+190}" y="25" fill="#a55c21" font-size="16">Cost C(q)</text><text x="${L+370}" y="25" fill="#80610f" font-size="16">Selected gap: ${esc(money(r.P))} profit</text></svg>`;
 $(id).innerHTML=s;
}
function initBusiness(){
 if(!$('businessPreset'))return;
 const presets={candles:[180,4,10,50,60,true,'q counts candles made and sold in one month.'],tutor:[200,5,25,14,20,false,'q measures tutoring hours delivered and billed in one week; fractional hours can be meaningful.'],cards:[48,1.5,6,16,20,true,'q counts cards made and sold at one craft fair.'],food:[240,3.5,9.5,55,80,true,'q counts meals prepared and sold at one festival.'],thin:[600,12,14,80,400,true,'q counts items made and sold in one period; the $2 margin requires many sales to cover $600.'],zero:[180,4,4,50,60,true,'Equal price and variable cost leave the $180 fixed expense uncovered at every quantity.'],negative:[180,5,4,50,60,true,'Each sale adds $4 revenue but $5 variable cost, so the modeled loss grows with quantity.'],free:[0,4,4,20,60,true,'With no fixed expense and equal price and variable cost, all quantities break even.']};
 function draw(){try{
  const F=read('F',100000),v=read('v',1000),p=read('p',1000),q=read('q',10000),capacity=read('capacity',10000),whole=$('wholeUnits').checked,g=Math7.linear(F,v,p),r=g.values(q),best=g.best(capacity,whole),valid=q<=capacity&&(!whole||Number.isInteger(q));
  $('businessResults').hidden=false;text('businessError','');text('cost',money(r.C));text('rev',money(r.R));text('profit',money(r.P));text('businessFormula',`C(q) = ${fmt(F)} + ${fmt(v)}q; R(q) = ${fmt(p)}q; P(q) = (${fmt(p)} − ${fmt(v)})q − ${fmt(F)} = ${fmt(g.m)}q − ${fmt(F)}.`);
  const zero=Math.abs(r.P)<=32*Number.EPSILON*Math.max(1,F,Math.abs(g.m*q));text('businessState',`At q=${fmt(q)}, the modeled outcome is ${zero?'exact break-even':r.P<0?'a loss of '+money(-r.P):'a profit of '+money(r.P)}.`);
  text('businessFeasible',valid?'This selected quantity is allowed by the capacity and unit rule.':`This quantity is unavailable: ${q>capacity?'it exceeds capacity. ':''}${whole&&!Number.isInteger(q)?'whole units are required.':''} Its predicted outcome is shown for comparison.`);
  const t=g.threshold,crossing=t.kind==='unique'?(Number.isInteger(t.q)?'q* = '+fmt(t.q):'q* = '+fmt(g.F)+' / '+fmt(g.m)+' ≈ '+fmt(t.q)):'';let note=t.kind==='all'?'Every nonnegative quantity breaks even exactly: both fixed cost and margin are zero.':t.kind==='none'?'There is no nonnegative break-even quantity: a nonpositive margin cannot cover this positive fixed expense.':`Continuous break-even: ${crossing}. Common cost and revenue: ${money(g.values(t.q).C)}. ${g.nonnegative!==null?'First whole count avoiding a loss: '+fmt(g.nonnegative)+'. ':''}${g.positive!==null?'First whole count with strictly positive profit: '+fmt(g.positive)+'.':'No positive quantity has positive profit.'}`;
  if(t.kind==='unique'&&t.q>capacity)note+=' The exact threshold is beyond the current capacity.';
  text('businessBreakEven',note);text('businessMarginal',`Marginal cost ${money(v)} per unit; marginal revenue ${money(p)}; marginal profit ${money(g.m)}. This is a change per extra unit, not total profit.`);
  text('businessBest',best.tie?`Every allowed quantity from 0 to ${fmt(best.top)} ties at profit ${money(best.P)}. ${whole?'Only whole-number quantities are allowed.':''}`:`To maximize modeled profit under the stated limit, choose q=${fmt(best.q)}, giving ${money(best.P)}. ${best.P<0?'Even the best allowed plan has a loss under this fixed-cost model. ':''}${whole&&capacity!==best.top?'The largest allowed whole count is the floor of capacity.':''}`);
  const qs=[q-2,q-1,q,q+1,q+2].filter(x=>x>=0);table('businessTable',['Quantity','Cost ($)','Revenue ($)','Profit ($)','Change from prior row ($)','Available?'],qs.map((x,i)=>{const a=g.values(x);return [fmt(x),money(a.C),money(a.R),money(a.P),i?money(a.P-g.values(qs[i-1]).P):'—',x<=capacity&&(!whole||Number.isInteger(x))?'yes':'no'];}));businessPlot(g,q,capacity);
 }catch(e){text('businessError',e.message);$('businessResults').hidden=true;}}
 function setup(){const a=presets[$('businessPreset').value];['F','v','p','q','capacity'].forEach((id,i)=>$(id).value=a[i]);$('wholeUnits').checked=a[5];text('businessContext',a[6]);draw();}
 $('businessPreset').addEventListener('change',setup);for(const id of ['F','v','p','q','capacity'])$(id).addEventListener('input',draw);$('wholeUnits').addEventListener('change',draw);setup();
}
function initFood(){
 if(!$('lowerSales'))return;
 function compare(){try{const q=read('lowerSales',300,true),r=Math7.linear(240,3.5,8.5).values(q),base=Math7.linear(240,3.5,9.5).values(80);text('foodCompare',`At the lower price with ${q} sales, profit is ${money(r.P)}. This is ${r.P===base.P?'equal to':r.P>base.P?money(r.P-base.P)+' above':money(base.P-r.P)+' below'} the original plan’s $240 profit at 80 sales.`);table('foodCompareTable',['Scenario','Sales','Cost','Revenue','Profit'],[['$9.50 price',80,money(base.C),money(base.R),money(base.P)],['$8.50 price',q,money(r.C),money(r.R),money(r.P)]]);}catch(e){text('foodCompare',e.message);$('foodCompareTable').replaceChildren();}}
 function inventory(){try{const n=read('preparedMeals',300,true),s=read('soldMeals',300,true),r=Math7.inventory(n,s);text('inventorySummary',`${n} prepared, ${s} sold: ${r.unsold} unsold. Cost ${money(r.C)}, revenue ${money(r.R)}, profit ${money(r.P)}. Costs include every prepared meal.`);table('inventoryTable',['Calculation','Dollars'],[['Cost: 240 + 3.50 × '+n,money(r.C)],['Revenue: 9.50 × '+s,money(r.R)],['Profit: revenue − cost',money(r.P)]]);}catch(e){text('inventorySummary',e.message);$('inventoryTable').replaceChildren();}}
 $('lowerSales').addEventListener('input',compare);for(const id of ['preparedMeals','soldMeals'])$(id).addEventListener('input',inventory);compare();inventory();
}
function initService(){
 if(!$('aiGoal'))return;
 function draw(){try{const cap=read('aiCapacity',10000,true),min=read('aiMinimum',10000,true),goal=$('aiGoal').value,r=Math7.service(cap,min,goal);if(r.status==='infeasible'){text('aiDecision',`No feasible plan: the minimum commitment ${min} exceeds capacity ${cap}. An objective cannot repair conflicting limits.`);$('aiDecisionTable').replaceChildren();return;}
  const label={cost:'minimize cost',profit:'maximize modeled profit',sessions:'maximize completed sessions'}[goal];text('aiDecision',`To ${label} over the allowed whole counts ${min} through ${cap}, choose ${r.q} sessions: cost ${money(r.C)}, revenue ${money(r.R)}, profit ${money(r.P)}. ${goal==='sessions'?'This positive-margin model makes profit maximization choose the same quantity.':''}`);
  const qs=[...new Set([min,cap])];table('aiDecisionTable',['Feasible endpoint','Sessions','Cost','Revenue','Profit','Chosen?'],qs.map(q=>{const a=Math7.linear(6000,.4,2.4).values(q);return [q===min?'minimum commitment':'capacity',q,money(a.C),money(a.R),money(a.P),q===r.q?'yes':'no'];}));
 }catch(e){text('aiDecision',e.message);$('aiDecisionTable').replaceChildren();}}
 for(const id of ['aiCapacity','aiMinimum'])$(id).addEventListener('input',draw);$('aiGoal').addEventListener('change',draw);draw();
}

function initAnswers(){
 const form=document.querySelector('[data-answer-store]');if(!form)return;
 const fields=[...form.querySelectorAll('[data-answer],textarea[data-save]')],key=form.dataset.answerStore,legacy=form.dataset.legacyStore,groups=[...form.querySelectorAll('[data-check-group]')],done=new Set();let storageOK=true;
 function numericCorrect(el){const v=Math7.number(el.value);return Number.isFinite(v)&&Math.abs(v-Number(el.dataset.answer))<=Number(el.dataset.tolerance||.001);}
 const correct=el=>el.tagName==='SELECT'?el.value!==''&&el.value===el.dataset.answer:numericCorrect(el);
 function update(){text('progressText',`${done.size} / ${groups.length} sections checked`);if($('progressFill'))$('progressFill').style.width=(groups.length?100*done.size/groups.length:0)+'%';}
 function save(){let o={fields:{}};fields.forEach(el=>o.fields[el.id]=el.value);try{localStorage.setItem(key,JSON.stringify(o));text('saveStatus','Saved in this browser.');}catch{storageOK=false;text('saveStatus','Autosave is unavailable here. Print your completed work to keep a copy.');}}
 try{let raw=localStorage.getItem(key)||(legacy&&localStorage.getItem(legacy));if(raw){let o=JSON.parse(raw),data=o.fields||o;fields.forEach(el=>{if(Object.hasOwn(data,el.id))el.value=String(data[el.id]);});}}catch{storageOK=false;text('saveStatus','Autosave is unavailable here. Print your completed work to keep a copy.');}
 groups.forEach(group=>{
  const entries=[...group.querySelectorAll('[data-answer]')],id=group.dataset.checkGroup;
  group.querySelector('[data-check]')?.addEventListener('click',()=>{
   let count=0;entries.forEach(el=>{let ok=correct(el),q=el.closest('.question'),feedback=q.querySelector('.field-feedback');q.classList.toggle('correct',ok);q.classList.toggle('incorrect',!ok);el.setAttribute('aria-invalid',String(!ok));feedback.textContent=ok?(el.dataset.success||'Correct.'):(el.value.trim()?'Try again. ':'Enter a response. ')+(el.dataset.hint||'Use the worked example above.');if(ok)count++;});
   if(count===entries.length)done.add(id);else done.delete(id);
   const fb=group.querySelector('.section-feedback');if(fb)fb.textContent=count===entries.length?'Section complete. Every response is correct.':`${count} of ${entries.length} correct. Use the feedback beside each response, then check again.`;
   update();save();
  });
  if(entries.length&&entries.every(correct))done.add(id);
 });
 fields.forEach(el=>el.addEventListener('input',()=>{const q=el.closest('.question');q?.classList.remove('correct','incorrect');el.removeAttribute('aria-invalid');if(q?.querySelector('.field-feedback'))q.querySelector('.field-feedback').textContent='';const group=el.closest('[data-check-group]');if(group){done.delete(group.dataset.checkGroup);let fb=group.querySelector('.section-feedback');if(fb)fb.textContent='';}update();save();}));
 update();if(storageOK)text('saveStatus','Your responses save in this browser as you work.');
 const name=$('studentName');if(name){try{name.value=localStorage.getItem('math107_submission_student_name')||'';}catch{}name.addEventListener('input',()=>{try{localStorage.setItem('math107_submission_student_name',name.value);}catch{}});}
 document.querySelectorAll('[data-print-work]').forEach(b=>b.addEventListener('click',()=>{if(name&&!name.value.trim()){text('printStatus','Enter your name before printing your completed work.');name.focus();return;}save();window.print();}));
}
function preparePrint(){
 document.querySelectorAll('.print-answer').forEach(e=>e.remove());
 document.querySelectorAll('.question input,.question select,.question textarea').forEach(el=>{let s=document.createElement('div');s.className='print-answer';s.textContent=el.tagName==='SELECT'?(el.value?el.selectedOptions[0].textContent:'No response'):el.value||'';el.after(s);});
 const name=$('studentName');if(name){let out=$('printName');if(out)out.textContent='Student: '+(name.value||'');}
}

function init(){initAnswers();initBusiness();initFood();initService();document.querySelectorAll('[data-print-page]').forEach(b=>b.addEventListener('click',()=>window.print()));window.addEventListener('beforeprint',preparePrint);window.addEventListener('afterprint',()=>document.querySelectorAll('.print-answer').forEach(e=>e.remove()));}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})(typeof globalThis!=='undefined'?globalThis:this);
