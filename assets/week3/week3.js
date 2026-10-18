/* Week 3: observed center/spread, exact-value counts, and normalized weighted means. */
(function(root){
'use strict';
const Math3={
 number(raw){const s=String(raw).trim();if(!s)return NaN;const m=s.match(/^([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*\/\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))$/);if(m)return Number(m[2])===0?NaN:Number(m[1])/Number(m[2]);return /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(s)?Number(s):NaN;},
 sum(xs){let total=0,c=0;for(const x of xs){const y=x-c,t=total+y;c=(t-total)-y;total=t;}return total;},
 parse(raw){const tokens=String(raw).trim().split(/[,\s]+/).filter(Boolean);if(!tokens.length)throw Error('Enter at least one observation. A blank entry is not zero.');if(tokens.length>200)throw Error('Use at most 200 observations for this explorer.');const xs=tokens.map(x=>this.number(x));for(let i=0;i<xs.length;i++)if(!Number.isFinite(xs[i])||Math.abs(xs[i])>1000000)throw Error('Observation '+(i+1)+' must be a valid number from -1,000,000 to 1,000,000. Check “'+tokens[i]+'”.');return xs;},
 summary(values){
  if(!Array.isArray(values)||values.length<1||values.length>200||!values.every(x=>Number.isFinite(x)&&Math.abs(x)<=1000000))throw Error('Use 1–200 finite observations with magnitude at most 1,000,000.');
  const xs=values.slice(),sorted=xs.slice().sort((a,b)=>a-b),n=xs.length,mean=xs[0]+this.sum(xs.map(x=>x-xs[0]))/n,middle=Math.floor(n/2),median=n%2?sorted[middle]:sorted[middle-1]+(sorted[middle]-sorted[middle-1])/2,deviations=xs.map(x=>x-mean),squares=deviations.map(d=>d*d),ss=this.sum(squares),frequency=[];
  for(const x of sorted){const last=frequency[frequency.length-1];if(last&&last.value===x)last.count++;else frequency.push({value:x,count:1});}
  const highest=Math.max(...frequency.map(x=>x.count)),modes=highest>1?frequency.filter(x=>x.count===highest).map(x=>x.value):[],sampleVariance=n>1?ss/(n-1):null,sampleSD=n>1?Math.sqrt(sampleVariance):null;
  return {values:xs,sorted,n,total:this.sum(xs),mean,median,min:sorted[0],max:sorted[n-1],range:sorted[n-1]-sorted[0],frequency,modes,deviations,squares,ss,sampleVariance,sampleSD,populationVariance:ss/n,populationSD:Math.sqrt(ss/n)};
 },
 window(f,mode='fixed'){if(!['fixed','fit'].includes(mode))throw Error('Choose a listed graph scale.');const pad=f.range?f.range*.08:Math.max(1,Math.abs(f.mean)*.05);return mode==='fit'?{lo:f.min-pad,hi:f.max+pad}:{lo:Math.min(0,f.min-pad*(f.min<0)),hi:Math.max(100,f.max+pad*(f.max>100))};},
 histogram(values,count=6,lo,hi){
  const f=this.summary(values);if(!Number.isInteger(count)||count<2||count>20)throw Error('Use a whole number of histogram intervals from 2 to 20.');
  if(lo===undefined&&hi===undefined){lo=f.min;hi=f.max;if(lo===hi){lo-=.5;hi+=.5;}}
  if(!Number.isFinite(lo)||!Number.isFinite(hi)||hi<=lo||!Number.isFinite(hi-lo)||f.min<lo||f.max>hi)throw Error('The histogram window must contain all observations.');
  const width=(hi-lo)/count,bins=Array.from({length:count},(_,i)=>({lo:lo+i*width,hi:i===count-1?hi:lo+(i+1)*width,count:0,last:i===count-1}));
  for(const x of f.values){const ratio=(x-lo)/width,nearest=Math.round(ratio),adjusted=Math.abs(ratio-nearest)<=32*Number.EPSILON*Math.max(1,Math.abs(ratio))?nearest:ratio;bins[Math.min(count-1,Math.max(0,Math.floor(adjusted)))].count++;}
  return {lo,hi,width,bins,total:f.n};
 },
 weighted(values,weights){
  if(!Array.isArray(values)||!Array.isArray(weights)||values.length!==weights.length||!values.length||!values.every(Number.isFinite)||!weights.every(w=>Number.isFinite(w)&&w>=0))throw Error('Use matching finite values and nonnegative weights.');
  const sum=this.sum(weights);if(Math.abs(sum-1)>1e-10)throw Error('These weights must add to 1.');
  const normalized=weights.map(w=>w/sum),products=values.map((v,i)=>v*normalized[i]);return {values:values.slice(),weights:normalized,products,totalWeight:sum,result:this.sum(products)};
 },
 outlier(value){if(!Number.isFinite(value)||value<11||value>150)throw Error('Use a final value from 11 to 150.');return this.summary([5,6,7,8,9,10,value]);}
};
root.Math3=Math3;if(typeof module!=='undefined'&&module.exports)module.exports=Math3;
if(typeof document==='undefined')return;
const $=id=>document.getElementById(id),text=(id,v)=>{if($(id))$(id).textContent=v;},fmt=x=>(Math.abs(x)>=1e8||(x!==0&&Math.abs(x)<.000001))?x.toExponential(4):Number(x.toPrecision(11)).toLocaleString('en-US',{maximumFractionDigits:6});
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function read(id){const x=Math3.number($(id).value);if(!Number.isFinite(x))throw Error('Enter a valid number for '+$(id).previousElementSibling.textContent+'.');return x;}
function table(id,headers,rows){const out=$(id);if(!out)return;const t=document.createElement('table'),head=document.createElement('thead'),tr=document.createElement('tr');for(const h of headers){const c=document.createElement('th');c.scope='col';c.textContent=h;tr.append(c);}head.append(tr);t.append(head);const body=document.createElement('tbody');for(const row of rows){const r=document.createElement('tr');for(const v of row){const c=document.createElement('td');c.textContent=v;r.append(c);}body.append(r);}t.append(body);out.replaceChildren(t);}
function frame(id,{xmin,xmax,ymin=0,ymax=1,xlabel,ylabel,title,desc,w=1000,h=520,yticks=true}){
 const L=105,R=35,T=75,B=80,X=x=>L+(w-L-R)*(x-xmin)/(xmax-xmin),Y=y=>h-B-(h-T-B)*(y-ymin)/(ymax-ymin);
 let svg=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" role="img" aria-labelledby="${id}-title ${id}-desc"><title id="${id}-title">${esc(title)}</title><desc id="${id}-desc">${esc(desc)}</desc><rect width="${w}" height="${h}" fill="white"/>`;
 for(let j=0;j<=5;j++){const x=xmin+(xmax-xmin)*j/5;svg+=`<path d="M${X(x)} ${T}V${h-B}" stroke="#d8ddcd"/><text x="${X(x)}" y="${h-B+25}" text-anchor="middle" font-size="14">${fmt(x)}</text>`;if(yticks){const y=ymin+(ymax-ymin)*j/5;svg+=`<path d="M${L} ${Y(y)}H${w-R}" stroke="#d8ddcd"/><text x="${L-10}" y="${Y(y)+5}" text-anchor="end" font-size="13">${fmt(y)}</text>`;}}
 svg+=`<path d="M${L} ${T}V${h-B}H${w-R}" fill="none" stroke="#293329" stroke-width="1.5"/><text x="${(L+w-R)/2}" y="${h-18}" text-anchor="middle" font-size="16">${esc(xlabel)}</text><text x="23" y="${(T+h-B)/2}" transform="rotate(-90 23 ${(T+h-B)/2})" text-anchor="middle" font-size="16">${esc(ylabel)}</text>`;
 return {svg,X,Y,L,R,T,B,w,h};
}

function drawData(f,mode,kind,count,id='c'){
 const domain=Math3.window(f,mode),hist=Math3.histogram(f.values,count,domain.lo,domain.hi),maxCount=Math.max(...f.frequency.map(x=>x.count)),ymax=kind==='histogram'?Math.max(5,Math.ceil(Math.max(...hist.bins.map(x=>x.count))/5)*5):maxCount+2;
 const p=frame(id,{xmin:domain.lo,xmax:domain.hi,ymax,xlabel:'Value (your original units)',ylabel:kind==='histogram'?'Number of observations':'One dot per observation',title:kind==='histogram'?'Observed frequencies in equal-width intervals':'Observed values, mean, and median',desc:'There are '+f.n+' observations. Mean '+f.mean+', median '+f.median+', range '+f.range+'. The exact values and counts are in the accompanying tables.',yticks:kind==='histogram'});
 let svg=p.svg;
 if(kind==='histogram'){
  for(const bin of hist.bins){const x=p.X(bin.lo),w=p.X(bin.hi)-x,y=p.Y(bin.count);svg+='<rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+(p.Y(0)-y)+'" fill="#b7d0d2" stroke="white"/>';if(bin.count)svg+='<text x="'+(x+w/2)+'" y="'+(y-7)+'" text-anchor="middle" font-size="13">'+bin.count+'</text>';}
 }else{
  const step=(p.h-p.T-p.B)/ymax,r=Math.min(6,Math.max(.6,step*.35));
  for(const row of f.frequency)for(let j=1;j<=row.count;j++)svg+='<circle cx="'+p.X(row.value)+'" cy="'+p.Y(j)+'" r="'+r+'" fill="#17677a"><title>Value '+esc(row.value)+', observation '+j+' of '+row.count+' at this value</title></circle>';
 }
 svg+='<path d="M'+p.X(f.mean)+' '+p.T+'V'+(p.h-p.B)+'" stroke="#a55c21" stroke-width="2.5"/><path d="M'+p.X(f.median)+' '+p.T+'V'+(p.h-p.B)+'" stroke="#536240" stroke-width="2.5" stroke-dasharray="5 4"/><text x="'+p.L+'" y="27" font-size="16" fill="#a55c21">Mean: '+fmt(f.mean)+'</text><text x="'+(p.L+350)+'" y="27" font-size="16" fill="#536240">Median: '+fmt(f.median)+'</text></svg>';
 $(id).innerHTML=svg;return hist;
}
function initExplorer(){if(!$('go')||!$('data'))return;
 const presets={tight:[50,51,50,49,50],wide:[30,40,50,60,70],outlier:[5,6,7,8,9,10,85],complaints:[3,0,5,2,1,4,2,8,2,3]};
 function analyze(){
  try{
   const f=Math3.summary(Math3.parse($('data').value)),count=read('binCount'),mode=$('scaleMode').value,kind=$('plotKind').value;
   if(!['dots','histogram'].includes(kind))throw Error('Choose a listed graph.');
   const hist=drawData(f,mode,kind,count);$('dataResults').hidden=false;text('dataError','');
   for(const [id,value] of Object.entries({count:f.n,mean:fmt(f.mean),median:fmt(f.median),mode:f.modes.length?f.modes.map(fmt).join(', '):'No repeated value',range:fmt(f.range),sd:f.sampleSD===null?'Not defined for n = 1':fmt(f.sampleSD)}))text(id,value);
   text('plotNote',(mode==='fixed'?'The horizontal window starts at 0–100 and extends if needed to show every observation. Keep it fixed when comparing the two same-mean presets.':'This window fits the current data, so its width can change between data sets. Check the axis before comparing spread.')+' Solid orange marks the mean; dashed olive marks the median. They can overlap.');
   text('note',f.n===1?'One observation has a center and zero observed range, but no sample SD. Add another observation to use the n − 1 rule.':'These '+f.n+' observations have mean '+fmt(f.mean)+' and sample SD '+fmt(f.sampleSD)+'. Compare the individual values as well as the summaries; equal centers need not mean equal spreads.');
   table('frequencyTable',['Observed value','Frequency'],f.frequency.map(x=>[fmt(x.value),x.count]));
   table('binTable',['Histogram interval','Frequency'],hist.bins.map(x=>['['+fmt(x.lo)+', '+fmt(x.hi)+(x.last?']':')'),x.count]));
   table('deviationTable',['Observation','Value','Deviation from mean','Squared deviation'],f.values.map((x,i)=>[i+1,fmt(x),fmt(f.deviations[i]),fmt(f.squares[i])]));
   text('sdCalculation',f.n===1?'There is no sample variance or sample SD for one observation: n − 1 would be zero.':'Squared deviations sum to '+fmt(f.ss)+'. Divide by n − 1 = '+(f.n-1)+' to get sample variance '+fmt(f.sampleVariance)+' squared units. Its square root is '+fmt(f.sampleSD)+' original units.');
  }catch(e){
   text('dataError',e.message);$('dataResults').hidden=true;for(const id of ['count','mean','median','mode','range','sd'])text(id,'—');for(const id of ['c','frequencyTable','binTable','deviationTable'])$(id).replaceChildren();text('sdCalculation','');
  }
 }
 $('go').addEventListener('click',analyze);$('data').addEventListener('keydown',e=>{if(e.key==='Enter'&&e.ctrlKey){e.preventDefault();analyze();}});$('data').addEventListener('input',()=>{$('dataResults').hidden=true;text('dataError','Select Analyze to update results for the edited data.');});
 document.querySelectorAll('[data-preset]').forEach(button=>button.addEventListener('click',()=>{$('data').value=presets[button.dataset.preset].join(', ');analyze();}));
 for(const id of ['plotKind','scaleMode'])$(id).addEventListener('change',analyze);$('binCount').addEventListener('input',analyze);
 function outlier(){
  try{const f=Math3.outlier(read('outlierValue'));text('outlierReadout',fmt(f.values[6]));text('outlierSummary','Values: '+f.values.map(fmt).join(', ')+'. Mean '+fmt(f.mean)+'; median '+fmt(f.median)+'; range '+fmt(f.range)+'; sample SD '+fmt(f.sampleSD)+'. Only the final observation moved.');drawData(f,'fixed','dots',6,'outlierPlot');table('outlierTable',['Mean','Median','Range','Sample SD'],[[fmt(f.mean),fmt(f.median),fmt(f.range),fmt(f.sampleSD)]]);}catch(e){text('outlierSummary',e.message);$('outlierPlot').replaceChildren();$('outlierTable').replaceChildren();}
 }
 $('outlierValue').addEventListener('input',outlier);analyze();outlier();
}
function initWeights(){if(!$('weightPreset'))return;
 const weights={given:[.1,.2,.6,.1],equal:[.25,.25,.25,.25],focus2:[.7,.1,.1,.1]},values=[2,5,8,10];
 function update(){
  try{const f=Math3.weighted(values,weights[$('weightPreset').value]);text('weightSummary','Weight total '+fmt(f.totalWeight)+'. Weighted result '+fmt(f.result)+'. Ordinary mean 6.25. The values stay the same while their shares change.');table('weightTable',['Value','Weight','Value × weight'],values.map((v,i)=>[v,fmt(f.weights[i]),fmt(f.products[i])]));
   const p=frame('weightPlot',{xmin:1,xmax:11,ymax:1,xlabel:'Feature value',ylabel:'',title:'Fixed feature values and a weighted result',desc:'Feature values 2, 5, 8, and 10. Weighted result '+f.result+'. Ordinary mean 6.25.',h:320,yticks:false});let svg=p.svg;
   for(const v of values)svg+='<circle cx="'+p.X(v)+'" cy="175" r="7" fill="#17677a"/>';
   svg+='<path d="M'+p.X(f.result)+' '+p.T+'V'+(p.h-p.B)+'" stroke="#a55c21" stroke-width="3"/><path d="M'+p.X(6.25)+' '+p.T+'V'+(p.h-p.B)+'" stroke="#536240" stroke-width="2" stroke-dasharray="5 4"/><text x="'+p.L+'" y="27" font-size="16" fill="#a55c21">Weighted result: '+fmt(f.result)+'</text><text x="'+(p.L+420)+'" y="27" font-size="16" fill="#536240">Ordinary mean: 6.25</text></svg>';$('weightPlot').innerHTML=svg;
  }catch(e){text('weightSummary',e.message);$('weightPlot').replaceChildren();$('weightTable').replaceChildren();}
 }
 $('weightPreset').addEventListener('change',update);update();
}
function initAnswers(){
 const form=document.querySelector('[data-answer-store]');if(!form)return;
 const fields=[...form.querySelectorAll('[data-answer],textarea[data-save]')],key=form.dataset.answerStore,legacy=form.dataset.legacyStore,groups=[...form.querySelectorAll('[data-check-group]')],done=new Set();let storageOK=true;
 function numericCorrect(el){const v=Math3.number(el.value);return Number.isFinite(v)&&Math.abs(v-Number(el.dataset.answer))<=Number(el.dataset.tolerance||.001);}
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
 update();if(storageOK)text('saveStatus','Your responses save in this browser as you work.');
 const name=$('studentName');if(name){try{name.value=localStorage.getItem('math107_submission_student_name')||'';}catch{}name.addEventListener('input',()=>{try{localStorage.setItem('math107_submission_student_name',name.value);}catch{}});}
 document.querySelectorAll('[data-print-work]').forEach(b=>b.addEventListener('click',()=>{if(name&&!name.value.trim()){text('printStatus','Enter your name before printing your completed work.');name.focus();return;}save();window.print();}));
}
function preparePrint(){
 document.querySelectorAll('.print-answer').forEach(e=>e.remove());
 document.querySelectorAll('.question input,.question select,.question textarea').forEach(el=>{let s=document.createElement('div');s.className='print-answer';s.textContent=el.tagName==='SELECT'?(el.value?el.selectedOptions[0].textContent:'No response'):el.value||'';el.after(s);});
 const name=$('studentName');if(name){let out=$('printName');if(out)out.textContent='Student: '+(name.value||'');}
}



function init(){initAnswers();initExplorer();initWeights();document.querySelectorAll('[data-print-page]').forEach(b=>b.addEventListener('click',()=>window.print()));window.addEventListener('beforeprint',preparePrint);window.addEventListener('afterprint',()=>document.querySelectorAll('.print-answer').forEach(e=>e.remove()));}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})(typeof globalThis!=='undefined'?globalThis:this);
