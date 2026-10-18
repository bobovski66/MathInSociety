/* Counts, finite probability models, and independent repeated draws for Week 2. */
(function(root){
'use strict';
const Math2={
 number(raw){const s=String(raw).trim();if(!s)return NaN;const m=s.match(/^([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*\/\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))$/);if(m)return Number(m[2])===0?NaN:Number(m[1])/Number(m[2]);return /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(s)?Number(s):NaN;},
 sum(xs){let total=0,c=0;for(const x of xs){const y=x-c,t=total+y;c=(t-total)-y;total=t;}return total;},
 frequencies(counts){
  if(!Array.isArray(counts)||!counts.length||counts.length>100||!counts.every(x=>Number.isInteger(x)&&x>=0&&x<=1000000))throw Error('Use nonnegative whole-number counts, at most 1,000,000 per category.');
  const total=this.sum(counts),shares=total?counts.map(x=>x/total):null;return {counts:counts.slice(),total,shares,sum:shares?this.sum(shares):null};
 },
 distribution(ps){
  if(!Array.isArray(ps)||!ps.length||ps.length>100||!ps.every(x=>Number.isFinite(x)&&x>=0&&x<=1))throw Error('Every probability must be between 0 and 1.');
  const total=this.sum(ps);if(Math.abs(total-1)>1e-10)throw Error('The probabilities must add to 1.');return ps.map(p=>p/total);
 },
 intervals(ps){
  this.distribution(ps);
  // Add the input decimals exactly before making numeric boundaries. This keeps
  // 0.1 + 0.2 at the intended boundary 0.3 rather than 0.30000000000000004.
  const parts=ps.map(p=>{let [base,exponent='0']=String(p).split('e'),digits=base.replace('.',''),places=(base.split('.')[1]||'').length;return {n:BigInt(digits),power:Number(exponent)-places};});
  const power=Math.min(...parts.map(p=>p.power)),weights=parts.map(p=>p.n*10n**BigInt(p.power-power)),total=weights.reduce((a,b)=>a+b,0n),scale=10n**340n;
  const ratio=n=>n===0n?0:n===total?1:Number('0.'+((n*scale)/total).toString().padStart(340,'0'));
  let prefix=0n;return weights.map((n,i)=>{const lo=ratio(prefix);prefix+=n;return {index:i,lo,hi:i===weights.length-1?1:ratio(prefix),probability:Number(ps[i])/this.sum(ps)};});
 },
 sample(ps,u){if(!Number.isFinite(u)||u<0||u>=1)throw Error('Use a random number from 0 up to, but not including, 1.');const intervals=this.intervals(ps);return intervals.find(x=>u>=x.lo&&u<x.hi)?.index??intervals.length-1;},
 start(ps){return {probabilities:this.distribution(ps),intervals:this.intervals(ps),n:0,counts:ps.map(()=>0),history:[]};},
 advance(state,count,rng=Math.random){
  if(!Number.isInteger(count)||count<1||count>10000||state.n+count>10000)throw Error('Use at most 10,000 draws in one run. Restart to begin another run.');
  const counts=state.counts.slice(),history=state.history.slice();
  for(let j=1;j<=count;j++){
   const u=rng();if(!Number.isFinite(u)||u<0||u>=1)throw Error('A random draw must lie in [0,1).');
   const index=state.intervals.find(x=>u>=x.lo&&u<x.hi)?.index??counts.length-1;counts[index]++;history.push({n:state.n+j,counts:counts.slice()});
  }
  return {...state,n:state.n+count,counts,history};
 }
};
root.Math2=Math2;if(typeof module!=='undefined'&&module.exports)module.exports=Math2;
if(typeof document==='undefined')return;
const $=id=>document.getElementById(id),text=(id,v)=>{if($(id))$(id).textContent=v;},fmt=x=>Number(x.toPrecision(11)).toLocaleString('en-US',{maximumFractionDigits:6}),esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function table(id,headers,rows){const out=$(id);if(!out)return;const t=document.createElement('table'),head=document.createElement('thead'),tr=document.createElement('tr');for(const h of headers){const c=document.createElement('th');c.scope='col';c.textContent=h;tr.append(c);}head.append(tr);t.append(head);const body=document.createElement('tbody');for(const row of rows){const r=document.createElement('tr');for(const v of row){const c=document.createElement('td');c.textContent=v;r.append(c);}body.append(r);}t.append(body);out.replaceChildren(t);}
function frame(id,title,desc,{w=840,h=440,xmax=4,ymax=1,xlabel='Category',ylabel='Relative frequency',ticks=true}={}){
 const L=90,R=25,T=75,B=75,X=x=>L+(w-L-R)*x/xmax,Y=y=>h-B-(h-T-B)*y/ymax;
 let svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 '+w+' '+h+'" role="img" aria-labelledby="'+id+'Title '+id+'Desc"><title id="'+id+'Title">'+esc(title)+'</title><desc id="'+id+'Desc">'+esc(desc)+'</desc><rect width="100%" height="100%" fill="white"/><text x="'+L+'" y="30" font-size="18" fill="#33432f">'+esc(title)+'</text>';
 for(let i=0;i<=5;i++){const v=ymax*i/5,y=Y(v);svg+='<path d="M'+L+' '+y+'H'+(w-R)+'" stroke="#d8ddcd"/><text x="'+(L-12)+'" y="'+(y+5)+'" text-anchor="end" font-size="14" fill="#52604f">'+esc(fmt(v))+'</text>';}
 svg+='<path d="M'+L+' '+T+'V'+(h-B)+'H'+(w-R)+'" fill="none" stroke="#536240" stroke-width="1.5"/><text x="'+(L+(w-L-R)/2)+'" y="'+(h-14)+'" text-anchor="middle" font-size="15">'+esc(xlabel)+'</text><text transform="translate(23 '+(T+(h-T-B)/2)+') rotate(-90)" text-anchor="middle" font-size="15">'+esc(ylabel)+'</text>';
 return {svg,X,Y,L,R,T,B,w,h};
}
function barPlot(id,labels,series,title,ylabel,ymax=1){
 const p=frame(id,title,series.map(s=>s.name+': '+s.values.map((v,i)=>labels[i]+' '+(v===null?'undefined':fmt(v))).join(', ')).join('. '),{w:640,h:410,xmax:labels.length,ymax,xlabel:'Category',ylabel});let svg=p.svg;
 for(let i=0;i<labels.length;i++){
  for(let k=0;k<series.length;k++){
   const s=series[k],v=s.values[i];if(v===null)continue;const width=.65/series.length,x=p.X(i+.175+k*width),right=p.X(i+.175+(k+1)*width);
   svg+='<rect x="'+x+'" y="'+p.Y(v)+'" width="'+(right-x)+'" height="'+(p.Y(0)-p.Y(v))+'" fill="'+s.color+'"/>';
   if(series.length===1)svg+='<text x="'+((x+right)/2)+'" y="'+(p.Y(v)-9)+'" text-anchor="middle" font-size="16">'+esc(fmt(v))+'</text>';
  }
  svg+='<text x="'+p.X(i+.5)+'" y="'+(p.h-p.B+25)+'" text-anchor="middle" font-size="16">'+esc(labels[i])+'</text>';
 }
 if(series.length>1)series.forEach((s,i)=>{svg+='<rect x="'+(p.L+i*255)+'" y="45" width="16" height="12" fill="'+s.color+'"/><text x="'+(p.L+23+i*255)+'" y="56" font-size="14">'+esc(s.name)+'</text>';});
 $(id).innerHTML=svg+'</svg>';
}
function historyPlot(id,state,index,label){
 const p=frame(id,'Observed share of '+label+' across the trials','The fixed probability is '+state.probabilities[index]+'. The observed share changes after each independent draw.',{xmax:Math.max(10,state.n),ymax:1,xlabel:'Number of trials',ylabel:'Relative frequency',w:1000,h:430});let svg=p.svg;
 const expected=state.probabilities[index],y=p.Y(expected);svg+='<path d="M'+p.L+' '+y+'H'+(p.w-p.R)+'" stroke="#a55c21" stroke-width="2" stroke-dasharray="7 5"/><text x="'+(p.L+8)+'" y="54" font-size="15" fill="#a55c21">Fixed model probability: '+fmt(expected)+'</text>';
 for(let i=0;i<=5;i++){const n=Math.max(10,state.n)*i/5;svg+='<text x="'+p.X(n)+'" y="'+(p.h-p.B+26)+'" text-anchor="middle" font-size="14">'+fmt(n)+'</text>';}
 if(state.n){const step=Math.max(1,Math.ceil(state.history.length/1000)),points=state.history.filter((x,i)=>i%step===0||i===state.history.length-1);let path=points.map((x,i)=>(i?'L':'M')+p.X(x.n)+' '+p.Y(x.counts[index]/x.n)).join(' ');svg+='<path d="'+path+'" fill="none" stroke="#17677a" stroke-width="2"/>';}else svg+='<text x="'+p.X(5)+'" y="'+p.Y(.7)+'" text-anchor="middle" font-size="17">Draw some observations to start the path.</text>';
 $(id).innerHTML=svg+'</svg>';
}
function results(prefix,state,labels){
 table(prefix+'Table',['Outcome','Fixed probability','Expected count','Observed count','Observed share'],labels.map((label,i)=>[label,fmt(state.probabilities[i]),fmt(state.n*state.probabilities[i]),state.counts[i],state.n?fmt(state.counts[i]/state.n):'Undefined: no draws yet']));
 barPlot(prefix+'Plot',labels,[{name:'Fixed model probability',color:'#a55c21',values:state.probabilities},{name:'Observed share',color:'#17677a',values:state.counts.map(x=>state.n?x/state.n:null)}],'Model and observed shares','Probability or relative frequency',1);
}
function initCounts(){
 if(!$('countsPanel'))return;const labels=['A','B','C','D'],presets={original:[12,8,5,15],double:[24,16,10,30],onlyA:[30,0,0,0],empty:[0,0,0,0]};
 function update(){
  const f=Math2.frequencies(labels.map((_,i)=>Number($('count'+i).value)));labels.forEach((_,i)=>text('v'+i,f.counts[i]));text('tot',f.total);text('maxp',f.shares?fmt(Math.max(...f.shares)):'Undefined');text('sumP',f.shares?fmt(f.sum):'Undefined');
  text('countsStatus',f.total?'Relative frequencies describe the '+f.total+' observations in this table.':'There are no observations. Relative frequencies are undefined because the denominator is zero.');
  $('tbl').replaceChildren();for(let i=0;i<labels.length;i++){const row=document.createElement('tr');for(const value of [labels[i],f.counts[i],f.total?f.counts[i]+'/'+f.total:'Undefined',f.shares?fmt(f.shares[i]):'Undefined',f.shares?fmt(f.shares[i]*100)+'%':'Undefined']){const cell=document.createElement('td');cell.textContent=value;row.append(cell);}$('tbl').append(row);}
  barPlot('countPlot',labels,[{name:'Observed count',values:f.counts,color:'#536240'}],'Observed counts','Frequency',30);barPlot('sharePlot',labels,[{name:'Observed share',values:f.shares||labels.map(()=>null),color:'#17677a'}],'Shares of this sample','Relative frequency',1);
 }
 labels.forEach((_,i)=>$('count'+i).addEventListener('input',update));document.querySelectorAll('[data-count-preset]').forEach(b=>b.addEventListener('click',()=>{presets[b.dataset.countPreset].forEach((v,i)=>$('count'+i).value=v);update();}));update();
 let state=Math2.start([.25,.25,.25,.25]);
 function draw(){results('trial',state,labels);historyPlot('trialHistory',state,Number($('focusCategory').value),labels[Number($('focusCategory').value)]);text('trialStatus',state.n+' independent draws. Expected counts are comparisons, not required results.');text('modelStatus','Fixed model: '+labels.map((label,i)=>label+' = '+fmt(state.probabilities[i])).join('; ')+'. A new model starts a new run.');document.querySelectorAll('[data-draw]').forEach(b=>b.disabled=state.n+Number(b.dataset.draw)>10000);}
 $('equalModel').addEventListener('click',()=>{state=Math2.start([.25,.25,.25,.25]);draw();});$('freezeModel').addEventListener('click',()=>{const f=Math2.frequencies(labels.map((_,i)=>Number($('count'+i).value)));if(!f.total){text('modelStatus','Add at least one observation before making a model from these shares. The current experiment is unchanged.');return;}state=Math2.start(f.shares);draw();});
 document.querySelectorAll('[data-draw]').forEach(b=>b.addEventListener('click',()=>{state=Math2.advance(state,Number(b.dataset.draw));draw();}));$('resetTrials').addEventListener('click',()=>{state=Math2.start(state.probabilities);draw();});$('focusCategory').addEventListener('change',draw);draw();
}
function initTokens(){
 const panel=$('tokenSampler');if(!panel)return;const labels=JSON.parse(panel.dataset.labels),ps=JSON.parse(panel.dataset.probs);let state=Math2.start(ps);
 function draw(){results('token',state,labels);text('tokenStatus',state.n+' independent draws from the same fixed distribution.');panel.querySelectorAll('[data-token-draw]').forEach(b=>b.disabled=state.n+Number(b.dataset.tokenDraw)>10000);}
 panel.querySelectorAll('[data-token-draw]').forEach(b=>b.addEventListener('click',()=>{state=Math2.advance(state,Number(b.dataset.tokenDraw));draw();}));$('resetTokens').addEventListener('click',()=>{state=Math2.start(ps);draw();});draw();
}
function initInterval(){
 if(!$('intervalLab'))return;const ps=[.5,.2,.2,.1],labels=['mat','rug','chair','moon'];
 function update(){
  const u=Math2.number($('uInput').value);
  try{const index=Math2.sample(ps,u),intervals=Math2.intervals(ps),q=intervals[index];text('intervalStatus','u = '+fmt(u)+' belongs to ['+fmt(q.lo)+', '+fmt(q.hi)+'), so select '+labels[index]+'.');$('uInput').removeAttribute('aria-invalid');
   const w=1000,h=240,L=45,R=30,X=x=>L+(w-L-R)*x;let svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 '+w+' '+h+'" role="img" aria-labelledby="intervalLiveTitle intervalLiveDesc"><title id="intervalLiveTitle">Sampling interval</title><desc id="intervalLiveDesc">'+esc($('intervalStatus').textContent)+'</desc><rect width="100%" height="100%" fill="white"/>';
   intervals.forEach((q,i)=>{const c=['#17677a','#536240','#a55c21','#b18a22'][i];svg+='<rect x="'+X(q.lo)+'" y="90" width="'+(X(q.hi)-X(q.lo))+'" height="65" fill="'+c+'" stroke="white" stroke-width="2"/><text x="'+X((q.lo+q.hi)/2)+'" y="125" text-anchor="middle" fill="white" font-size="19">'+labels[i]+'</text><text x="'+X(q.lo)+'" y="181" text-anchor="middle" font-size="16">'+fmt(q.lo)+'</text>';});svg+='<text x="'+X(1)+'" y="181" text-anchor="middle" font-size="16">1</text><path d="M'+X(u)+' 65V155" stroke="#293329" stroke-width="3"/><text x="'+Math.min(w-90,Math.max(90,X(u)))+'" y="43" text-anchor="middle" font-size="20">u = '+fmt(u)+'</text><text x="'+(w/2)+'" y="220" text-anchor="middle" font-size="17">Each left endpoint is included; each right endpoint is excluded.</text></svg>';$('intervalPlot').innerHTML=svg;
  }catch(e){text('intervalStatus',e.message);$('intervalPlot').replaceChildren();$('uInput').setAttribute('aria-invalid','true');}
 }
 $('locateU').addEventListener('click',update);$('uInput').addEventListener('input',()=>{$('intervalPlot').replaceChildren();text('intervalStatus','Choose “Locate this number” to check the new value.');});$('randomU').addEventListener('click',()=>{$('uInput').value=String(Math.random());update();});update();
}
function initAnswers(){
 const form=document.querySelector('[data-answer-store]');if(!form)return;
 const fields=[...form.querySelectorAll('[data-answer],textarea[data-save]')],key=form.dataset.answerStore,legacy=form.dataset.legacyStore,groups=[...form.querySelectorAll('[data-check-group]')],done=new Set();let storageOK=true;
 function numericCorrect(el){const v=Math2.number(el.value);return Number.isFinite(v)&&Math.abs(v-Number(el.dataset.answer))<=Number(el.dataset.tolerance||.001);}
 const correct=el=>el.tagName==='SELECT'?el.value!==''&&el.value===el.dataset.answer:numericCorrect(el);
 function update(){text('progressText',`${done.size} / ${groups.length} sections checked`);if($('progressFill'))$('progressFill').style.width=(groups.length?100*done.size/groups.length:0)+'%';}
 function save(){let o={fields:{}};fields.forEach(el=>o.fields[el.id]=el.value);try{localStorage.setItem(key,JSON.stringify(o));text('saveStatus','Saved in this browser.');}catch{storageOK=false;text('saveStatus','Autosave is unavailable here. Print your completed work to keep a copy.');}}
 try{let raw=localStorage.getItem(key)||(legacy&&localStorage.getItem(legacy));if(raw){let o=JSON.parse(raw),data=o.fields||o.values||o;fields.forEach(el=>{if(Object.hasOwn(data,el.id))el.value=String(data[el.id]);});}}catch{storageOK=false;text('saveStatus','Autosave is unavailable here. Print your completed work to keep a copy.');}
 groups.forEach(group=>{
  const entries=[...group.querySelectorAll('[data-answer]')],id=group.dataset.checkGroup;
  group.querySelector('[data-check]')?.addEventListener('click',()=>{
   let count=0;entries.forEach(el=>{let ok=correct(el),q=el.closest('.question'),feedback=q.querySelector('.field-feedback');q.classList.toggle('correct',ok);q.classList.toggle('incorrect',!ok);el.setAttribute('aria-invalid',String(!ok));feedback.textContent=ok?(el.dataset.success||'Correct.'):(el.value.trim()?'Try again. ':'Enter a response. ')+(el.dataset.hint||'Use the worked example above.');if(ok)count++;});
   if(count===entries.length)done.add(id);else done.delete(id);
   const fb=group.querySelector('.section-feedback');if(fb)fb.textContent=count===entries.length?(group.querySelector('textarea')?'All numerical and choice responses are correct. Review the written explanation separately.':'Section complete. Every response is correct.'):`${count} of ${entries.length} correct. Use the feedback beside each response, then check again.`;
   update();save();
  });
  if(entries.length&&entries.every(correct))done.add(id);
 });
 fields.forEach(el=>el.addEventListener('input',()=>{const q=el.closest('.question');q?.classList.remove('correct','incorrect');el.removeAttribute('aria-invalid');if(q?.querySelector('.field-feedback'))q.querySelector('.field-feedback').textContent='';const group=el.closest('[data-check-group]');if(group){done.delete(group.dataset.checkGroup);let fb=group.querySelector('.section-feedback');if(fb)fb.textContent='';}update();save();}));
 form.querySelectorAll('[data-save-work]').forEach(b=>b.addEventListener('click',save));
 form.querySelectorAll('[data-clear-work]').forEach(b=>b.addEventListener('click',()=>{if(!window.confirm('Clear the responses for this Week 2 activity?'))return;fields.forEach(el=>{el.value='';el.removeAttribute('aria-invalid');const q=el.closest('.question');q?.classList.remove('correct','incorrect');const fb=q?.querySelector('.field-feedback');if(fb)fb.textContent='';});done.clear();groups.forEach(g=>{const fb=g.querySelector('.section-feedback');if(fb)fb.textContent='';});try{if(legacy){localStorage.removeItem(legacy);for(let i=1;i<=5;i++)localStorage.removeItem(legacy+'_part'+i);}}catch{}update();save();}));
 update();if(storageOK)text('saveStatus','Your responses save in this browser as you work.');
 const name=$('studentName');if(name){try{name.value=localStorage.getItem('math107_submission_student_name')||'';}catch{}name.addEventListener('input',()=>{try{localStorage.setItem('math107_submission_student_name',name.value);}catch{}});}
 document.querySelectorAll('[data-print-work]').forEach(b=>b.addEventListener('click',()=>{if(name&&!name.value.trim()){text('printStatus','Enter your name before printing your completed work.');name.focus();return;}save();window.print();}));
}
function preparePrint(){
 document.querySelectorAll('.print-answer').forEach(e=>e.remove());
 document.querySelectorAll('.question input,.question select,.question textarea').forEach(el=>{let s=document.createElement('div');s.className='print-answer';s.textContent=el.tagName==='SELECT'?(el.value?el.selectedOptions[0].textContent:'No response'):el.value||'';el.after(s);});
 const name=$('studentName');if(name){let out=$('printName');if(out)out.textContent='Student: '+(name.value||'');}
}



function init(){initAnswers();initCounts();initTokens();initInterval();document.querySelectorAll('[data-print-page]').forEach(b=>b.addEventListener('click',()=>window.print()));window.addEventListener('beforeprint',preparePrint);window.addEventListener('afterprint',()=>document.querySelectorAll('.print-answer').forEach(e=>e.remove()));}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})(typeof globalThis!=='undefined'?globalThis:this);
