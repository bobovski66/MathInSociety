/* Week 6: explicit period rates, complete repayment status, and two rounding conventions. */
(function(root){
'use strict';
const Math6={
 number(raw){const s=String(raw).trim();if(!s)return NaN;const m=s.match(/^([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*\/\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))$/);if(m)return Number(m[2])===0?NaN:Number(m[1])/Number(m[2]);return /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(s)?Number(s):NaN;},
 cents(x){if(!Number.isFinite(x)||x<0||x>1000000||Math.abs(x*100-Math.round(x*100))>1e-6)throw Error('Use nonnegative dollar amounts up to 1,000,000 with at most two decimal places.');return Math.round(x*100);},
 rate(r){if(!Number.isFinite(r)||r<0||r>1||Math.abs(r*10000-Math.round(r*10000))>1e-6)throw Error('Use a nonnegative annual percentage with at most two decimal places.');return Math.round(r*10000);},
 savings(P,r,t,n){this.cents(P);this.rate(r);if(!Number.isInteger(t)||t<0||t>40||![1,2,4,12,365].includes(n))throw Error('Use whole years from 0 to 40 and a listed compounding frequency.');const amount=k=>P*Math.exp(n*k*Math.log1p(r/n)),rows=Array.from({length:t+1},(_,k)=>({k,simple:P*(1+r*k),compound:amount(k)}));return {P,r,t,n,periodRate:r/n,periods:n*t,simple:P*(1+r*t),compound:amount(t),yield:Math.expm1(n*Math.log1p(r/n)),doubling:r>0?72/(r*100):null,rows};},
 loan(P,r,M,{rounding='cents',limit=1200}={}){
  const pc=this.cents(P),mc=this.cents(M),basis=this.rate(r);if(!['cents','full'].includes(rounding)||!Number.isInteger(limit)||limit<1||limit>1200)throw Error('Choose a listed rounding rule and 1–1,200 simulation months.');
  const i=r/12,centMode=rounding==='cents',firstInterest=centMode?Math.round(pc*basis/120000)/100:P*i,firstActual=Math.min(M,P+firstInterest),firstReduction=firstActual-firstInterest;
  if(pc===0)return {status:'paid',months:0,simulated:0,rows:[],points:[[0,0]],balance:0,totalPaid:0,totalInterest:0,finalPayment:0,firstInterest:0,firstActual:0,firstReduction:0,rounding,i};
  const tol=32*Number.EPSILON*Math.max(1,M,firstInterest),relation=M-firstInterest,status0=Math.abs(relation)<=tol?'constant':relation<0?'growing':'decreasing',steps=status0==='decreasing'?limit:Math.min(limit,24),rows=[],points=[[0,P]];
  let bal=P,bc=pc,totalPaid=0,totalInterest=0,paidC=0,interestC=0,status=status0;
  for(let month=1;month<=steps;month++){
   const start=bal;let interest,payment;
   if(centMode){const ic=Math.round(bc*basis/120000),due=bc+ic,actual=Math.min(mc,due);bc=due-actual;bal=bc/100;interest=ic/100;payment=actual/100;paidC+=actual;interestC+=ic;totalPaid=paidC/100;totalInterest=interestC/100;}
   else{interest=start*i;const due=start+interest,tolerance=32*Number.EPSILON*Math.max(1,P,due,M);payment=due<=M+tolerance?due:M;bal=due-payment;totalPaid+=payment;totalInterest+=interest;}
   rows.push({month,start,interest,payment,reduction:payment-interest,end:bal});points.push([month,bal]);
   if(bal===0){status='paid';break;}
  }
  if(status==='decreasing')status='horizon';return {status,months:status==='paid'?rows.length:null,simulated:rows.length,rows,points,balance:bal,totalPaid,totalInterest,finalPayment:status==='paid'?rows.at(-1).payment:null,firstInterest,firstActual,firstReduction,rounding,i};
 },
 growth(years,cap){if(!Number.isInteger(years)||years<0||years>20||!Number.isInteger(cap)||cap<100||cap>2000)throw Error('Use 0–20 whole years and a whole ceiling from 100 to 2,000 units.');const rows=[{k:0,add:100,compound:100,limited:100}];for(let k=1;k<=years;k++)rows.push({k,add:100+25*k,compound:100*1.25**k,limited:Math.min(cap,rows[k-1].limited*1.25)});return {rows,cap,capYear:rows.find(x=>x.limited===cap)?.k??null,divergeYear:rows.find(x=>x.limited<x.compound)?.k??null};}
};
root.Math6=Math6;if(typeof module!=='undefined'&&module.exports)module.exports=Math6;
if(typeof document==='undefined')return;
const $=id=>document.getElementById(id),text=(id,v)=>{if($(id))$(id).textContent=v;},fmt=x=>(Math.abs(x)>=1e9||(x!==0&&Math.abs(x)<.00001))?x.toExponential(4):Number(x.toPrecision(10)).toLocaleString('en-US',{maximumFractionDigits:5}),money=x=>(x<0?'−':'')+'$'+Math.abs(x).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function read(id,max,integer=false){const x=Math6.number($(id).value);if(!Number.isFinite(x)||x<0||x>max||(integer&&!Number.isInteger(x)))throw Error('Enter a '+(integer?'whole ':'')+'number from 0 to '+fmt(max)+' in '+$(id).previousElementSibling.textContent+'.');return x;}
function table(id,headers,rows){const out=$(id);if(!out)return;const t=document.createElement('table'),head=document.createElement('thead'),tr=document.createElement('tr');for(const h of headers){const c=document.createElement('th');c.scope='col';c.textContent=h;tr.append(c);}head.append(tr);t.append(head);const body=document.createElement('tbody');for(const row of rows){const r=document.createElement('tr');for(const v of row){const c=document.createElement('td');c.textContent=v;r.append(c);}body.append(r);}t.append(body);out.replaceChildren(t);}
function chart(id,series,{xlabel='Time',ylabel='Balance ($)',title='Balance updates',currency=true}={}){
 const w=940,h=550,L=105,R=30,T=60,B=80,maxX=Math.max(1,...series.flatMap(s=>s.points.map(p=>p[0]))),maxY=Math.max(1,...series.flatMap(s=>s.points.map(p=>p[1])))*1.1,X=x=>L+(w-L-R)*x/maxX,Y=y=>h-B-(h-T-B)*y/maxY;
 let svg=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" role="img" aria-labelledby="${id}-title ${id}-desc"><title id="${id}-title">${esc(title)}</title><desc id="${id}-desc">${esc(series.map(s=>s.name+': starts at '+s.points[0].join(', ')+', ends at '+s.points.at(-1).join(', ')).join('; '))}. Both axes and the numerical table use the stated time unit.</desc><rect width="940" height="550" fill="white"/>`;
 for(let k=0;k<=5;k++){const x=maxX*k/5,y=maxY*k/5;svg+=`<path d="M${X(x)} ${T}V${h-B}M${L} ${Y(y)}H${w-R}" stroke="#d8ddcd"/><text x="${X(x)}" y="${h-B+25}" text-anchor="middle" font-size="13">${fmt(x)}</text><text x="${L-12}" y="${Y(y)+5}" text-anchor="end" font-size="13">${currency?'$':''}${fmt(y)}</text>`;}
 series.forEach((s,i)=>{svg+=`<text x="${L+i*265}" y="25" font-size="15" fill="${s.color}">${esc(s.name)}</text><polyline points="${s.points.map(p=>X(p[0])+','+Y(p[1])).join(' ')}" fill="none" stroke="${s.color}" stroke-width="3" ${s.dashed?'stroke-dasharray="7 5"':''}/>`;if(s.points.length<=45)for(const p of s.points)svg+=`<circle cx="${X(p[0])}" cy="${Y(p[1])}" r="3.5" fill="${s.color}"/>`;});
 svg+=`<path d="M${L} ${T}V${h-B}H${w-R}" fill="none" stroke="#293329" stroke-width="2"/><text x="${(L+w-R)/2}" y="${h-20}" text-anchor="middle" font-size="16">${esc(xlabel)}</text><text x="22" y="${(T+h-B)/2}" transform="rotate(-90 22 ${(T+h-B)/2})" text-anchor="middle" font-size="16">${esc(ylabel)}</text></svg>`;$(id).innerHTML=svg;
}
function loanRows(id,r,all=false){const rows=all?r.rows:r.rows.filter((x,k)=>k<6||k===r.rows.length-1);table(id,['Month','Start balance','Interest','Actual payment','Principal reduction','End balance'],rows.map(x=>[x.month,money(x.start),money(x.interest),money(x.payment),money(x.reduction),money(x.end)]));}
function initSavings(){
 if(!$('sP'))return;
 function draw(){try{const P=read('sP',1000000),rate=read('sr',30),t=read('st',40,true),n=Number($('sn').value),r=Math6.savings(P,rate/100,t,n);$('savingsResults').hidden=false;text('savingsError','');text('simpleOut',money(r.simple));text('compoundOut',money(r.compound));text('diffOut',money(r.compound-r.simple));text('savingsModel',`Simple: A = ${fmt(P)}(1 + ${fmt(rate/100)} × ${t}). Compound: A = ${fmt(P)}(1 + ${fmt(rate/100)}/${n})^${n*t}.`);text('savingsSummary',`One compound period uses rate approximately ${fmt(r.periodRate)} as a decimal, or ${fmt(r.periodRate*100)}% (rounded for display). There are ${r.periods} completed periods in ${t} years. No later deposits or withdrawals are included.`);table('savingsTable',['Year','Simple balance','Compound balance','Compound minus simple'],r.rows.map(x=>[x.k,money(x.simple),money(x.compound),money(x.compound-x.simple)]));chart('savingsPlot',[{name:'Simple interest',color:'#a55c21',points:r.rows.map(x=>[x.k,x.simple])},{name:'Compound interest',color:'#17677a',points:r.rows.map(x=>[x.k,x.compound])}],{xlabel:'Years from the initial deposit',title:'Savings under two stated growth rules'});text('savingsYield',`Effective annual yield for this compound rule: about ${fmt(r.yield*100)}%. This is the one-year percentage gain, including compounding.`);text('savingsDoubling',P===0?'A zero starting balance stays zero in both models without new deposits. A doubling-time claim needs a positive starting amount.':rate===0?'At a zero growth rate, this positive balance does not double. The Rule of 72 does not divide by zero.':`Rule-of-72 estimate at ${fmt(rate)}%: about ${fmt(r.doubling)} years per doubling. It is a scale estimate, not an exact crossing or a prediction of a loan’s payoff.`);}catch(e){text('savingsError',e.message);$('savingsResults').hidden=true;}}
 for(const id of ['sP','sr','st'])$(id).addEventListener('input',draw);$('sn').addEventListener('change',draw);draw();
}
function initLoan(){
 if(!$('loanPreset'))return;
 const presets={reading:[4000,6,200,'cents'],lab:[3000,9,150,'cents'],cardA:[8000,18,160,'full'],cardB:[8000,18,300,'full'],discussion:[5000,18,225,'cents'],flat:[1000,12,10,'cents'],growing:[1000,12,5,'cents'],zero:[1000,0,100,'cents']};
 function draw(){try{const P=read('lP',1000000),apr=read('lr',40),M=read('lpay',1000000),limit=read('loanHorizon',1200,true),rounding=$('loanRounding').value,r=Math6.loan(P,apr/100,M,{rounding,limit});$('loanResults').hidden=false;text('loanError','');text('loanFirst',money(r.firstInterest));text('loanActual',money(r.firstActual));text('loanReduction',money(r.firstReduction));text('loanModel',`Monthly rate i = ${fmt(apr/100)} / 12 ≈ ${fmt(r.i)} (${fmt(r.i*100)}%). While a full payment is due: next balance = current balance × (1 + i) − ${fmt(M)}. ${rounding==='cents'?'Round each month’s interest to cents.':'Keep full internal precision; display money to cents.'}`);
  let note;if(r.status==='paid')note=P===0?'The starting balance is already zero: payoff needs 0 payments and no interest.':`Paid off in month ${r.months}. The actual final payment is ${money(r.finalPayment)}. The ending balance is zero.`;else if(r.status==='constant')note='The payment exactly covers each interest charge under this rounding rule. The balance stays unchanged and does not pay off.';else if(r.status==='growing')note='The payment is smaller than the interest charge. The balance grows; this fixed-payment model does not pay off.';else note=`Not paid within the ${limit}-month simulation horizon. The remaining balance is ${money(r.balance)}. This stopping month is not a payoff result.`;
  text('loanSummary',note);text('loanTotals',r.status==='paid'?`Total paid ${money(r.totalPaid)}; total interest ${money(r.totalInterest)}. With no fees or new borrowing, total paid minus ${money(P)} principal equals total interest.`:`Through ${r.simulated} simulated months: payments ${money(r.totalPaid)}, interest added ${money(r.totalInterest)}, balance still owed ${money(r.balance)}. These are totals so far, not lifetime totals.`);chart('loanPlot',[{name:'Amount still owed',color:'#536240',points:r.points}],{xlabel:'Months after the initial balance',title:'Loan balance after each actual payment'});text('loanPlotNote',`Month 0 is the initial balance; later points are after payment. ${['growing','constant'].includes(r.status)?'For a nonpaying-off model, the preview shows at most 24 months. ':''}${r.status==='horizon'?'The plot stops at the chosen horizon while debt remains. ':''}The vertical axis starts at zero.`);loanRows('loanTable',r,$('showAllMonths').checked);
 }catch(e){text('loanError',e.message);$('loanResults').hidden=true;}}
 function setup(){const a=presets[$('loanPreset').value];['lP','lr','lpay'].forEach((id,k)=>$(id).value=a[k]);$('loanRounding').value=a[3];$('loanHorizon').value=1200;draw();}
 $('loanPreset').addEventListener('change',setup);for(const id of ['lP','lr','lpay','loanHorizon'])$(id).addEventListener('input',draw);for(const id of ['loanRounding','showAllMonths'])$(id).addEventListener('change',draw);setup();
}
function initComparison(){
 if(!$('run'))return;let plans=null;
 function trace(){if(plans)loanRows('repayTrace',plans[$('repayPlan').value]);}
 function run(){plans={A:Math6.loan(8000,.18,160,{rounding:'full'}),B:Math6.loan(8000,.18,300,{rounding:'full'})};$('appResults').hidden=false;text('aMonths',plans.A.months+' months');text('bMonths',plans.B.months+' months');text('aInt',money(plans.A.totalInterest));text('bInt',money(plans.B.totalInterest));table('repayTotals',['Plan','Regular payment','Payoff month','Actual last payment','Total paid','Total interest'],Object.entries(plans).map(([k,r])=>[k,money(k==='A'?160:300),r.months,money(r.finalPayment),money(r.totalPaid),money(r.totalInterest)]));chart('repayPlot',[{name:'Plan A: $160 payment',color:'#536240',points:plans.A.points},{name:'Plan B: $300 payment',color:'#17677a',points:plans.B.points}],{xlabel:'Months after the initial $8,000 balance',title:'Two payments, the same initial balance and rate'});trace();}
 $('run').addEventListener('click',run);$('repayPlan').addEventListener('change',trace);
}
function initGrowth(){
 if(!$('growthYears'))return;
 function draw(){try{const years=read('growthYears',20,true),cap=read('growthCap',2000,true),g=Math6.growth(years,cap),last=g.rows.at(-1);text('growthSummary',`At year ${years}: fixed additions ${fmt(last.add)}, uncapped percentage growth ${fmt(last.compound)}, limited growth ${fmt(last.limited)} capacity units. ${g.capYear===null?'The limited path has not reached its ceiling within the shown years.':'It first reaches the ceiling in year '+g.capYear+'.'} ${g.divergeYear===null?'No difference from the uncapped path is yet visible in the shown rows.':'It first differs from the uncapped percentage path in year '+g.divergeYear+'.'}`);table('growthTable',['Year','Add 25 units','Grow by 25%','Grow by 25%, with ceiling'],g.rows.map(x=>[x.k,fmt(x.add),fmt(x.compound),fmt(x.limited)]));chart('growthPlot',[{name:'Add 25 units',color:'#a55c21',points:g.rows.map(x=>[x.k,x.add])},{name:'Grow by 25%',color:'#17677a',points:g.rows.map(x=>[x.k,x.compound])},{name:'Percentage, with ceiling',color:'#536240',dashed:true,points:g.rows.map(x=>[x.k,x.limited])}],{xlabel:'Years from the initial state',ylabel:'Capacity index (units)',title:'Constructed compute-capacity growth rules',currency:false});}catch(e){text('growthSummary',e.message);$('growthTable').replaceChildren();$('growthPlot').replaceChildren();}}
 for(const id of ['growthYears','growthCap'])$(id).addEventListener('input',draw);draw();
}

function initAnswers(){
 const form=document.querySelector('[data-answer-store]');if(!form)return;
 const fields=[...form.querySelectorAll('[data-answer],textarea[data-save]')],key=form.dataset.answerStore,legacy=form.dataset.legacyStore,groups=[...form.querySelectorAll('[data-check-group]')],done=new Set();let storageOK=true;
 function numericCorrect(el){const v=Math6.number(el.value);return Number.isFinite(v)&&Math.abs(v-Number(el.dataset.answer))<=Number(el.dataset.tolerance||.001);}
 const correct=el=>el.tagName==='SELECT'?el.value!==''&&el.value===el.dataset.answer:numericCorrect(el);
 function update(){text('progressText',`${done.size} / ${groups.length} sections checked`);if($('progressFill'))$('progressFill').style.width=(groups.length?100*done.size/groups.length:0)+'%';}
 function save(){let o={fields:{}};fields.forEach(el=>o.fields[el.id]=el.value);try{localStorage.setItem(key,JSON.stringify(o));text('saveStatus','Saved in this browser.');}catch{storageOK=false;text('saveStatus','Autosave is unavailable here. Print your completed work to keep a copy.');}}
 try{let raw=localStorage.getItem(key)||(legacy&&localStorage.getItem(legacy));if(raw){let o=JSON.parse(raw),data=o.fields||o.values||o;fields.forEach(el=>{if(Object.hasOwn(data,el.id))el.value=String(data[el.id]);});}}catch{storageOK=false;text('saveStatus','Autosave is unavailable here. Print your completed work to keep a copy.');}
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


function init(){initAnswers();initSavings();initLoan();initComparison();initGrowth();document.querySelectorAll('[data-print-page]').forEach(b=>b.addEventListener('click',()=>window.print()));window.addEventListener('beforeprint',preparePrint);window.addEventListener('afterprint',()=>document.querySelectorAll('.print-answer').forEach(e=>e.remove()));}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})(typeof globalThis!=='undefined'?globalThis:this);
