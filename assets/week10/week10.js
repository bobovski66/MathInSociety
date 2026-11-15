/* Week 10 — Complexity, Chaos, and Fractals.
   Core mathematics kept separate from the page controls for transparent testing. */
(function(root){
"use strict";
const Math10={
  collatz(start,limit=500){
    if(!Number.isSafeInteger(start)||start<1||start>100000)throw Error("Choose an integer from 1 to 100,000.");
    if(!Number.isSafeInteger(limit)||limit<1||limit>5000)throw Error("Choose a limit between 1 and 5,000 updates.");
    let x=start,values=[x],peak=x;
    for(let i=0;i<limit&&x!==1;i++){
      x=(x%2===0)?x/2:3*x+1;
      if(!Number.isSafeInteger(x))throw Error("The calculation exceeded exact integer precision.");
      values.push(x);peak=Math.max(x,peak);
    }
    return {start,values,steps:values.length-1,peak,reachedOne:x===1};
  },
  logistic(r,start,steps=40){
    if(!Number.isFinite(r)||r<0||r>4)throw Error("Use 0 ≤ r ≤ 4.");
    if(!Number.isFinite(start)||start<0||start>1)throw Error("Start between zero and one.");
    if(!Number.isSafeInteger(steps)||steps<0||steps>1000)throw Error("Use 0–1,000 updates.");
    const values=[start];let x=start;
    for(let i=0;i<steps;i++){x=r*x*(1-x);values.push(x)}
    return values;
  },
  sierpinski(stage){
    if(!Number.isInteger(stage)||stage<0||stage>7)throw Error("Choose a stage 0–7.");
    let tris=[[[50,575],[650,575],[350,55]]];
    for(let k=0;k<stage;k++){
      const mid=(a,b)=>[(a[0]+b[0])/2,(a[1]+b[1])/2];
      const next=[];
      for(const [a,b,c] of tris){
        const ab=mid(a,b),bc=mid(b,c),ca=mid(c,a);
        next.push([a,ab,ca],[ab,b,bc],[ca,bc,c]);
      }
      tris=next;
    }
    return {stage,triangles:tris,count:3**stage,areaFraction:(3/4)**stage,sideFraction:1/(2**stage)};
  },
  searchTable(bits){if(!Number.isInteger(bits)||bits<0||bits>30)throw Error("Bits must be from 0 to 30.");return {possibilities:2**bits,balancedQuestions:bits,sequentialWorst:2**bits}}
};
root.Math10=Math10;
if(typeof module!=="undefined"&&module.exports)module.exports=Math10;
if(typeof document==="undefined")return;
const $=id=>document.getElementById(id);
const fmt=(x,d=5)=>Number.isInteger(x)?x.toLocaleString("en-US"):Number(x).toFixed(d).replace(/0+$/,"").replace(/\.$/,"");
const escape=s=>String(s).replace(/[&<>"']/g,ch=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
function getNum(id,fallback){const node=$(id),v=node?Number(node.value):NaN;return Number.isFinite(v)?v:fallback}
function svg(tag,attributes){const e=document.createElementNS("http://www.w3.org/2000/svg",tag);for(const [name,value] of Object.entries(attributes||{}))e.setAttribute(name,String(value));return e}
function pointChart(id,series,{maxY=1,minY=0,labels=[],logarithmic=false}={}){
  const node=$(id);if(!node)return;
  node.replaceChildren();node.setAttribute("viewBox","0 0 740 270");
  const w=740,h=270,left=45,top=18,right=13,bottom=37,innerW=w-left-right,innerH=h-top-bottom;
  const N=Math.max(1,...series.map(x=>x.values.length-1));
  const transform=v=>logarithmic?Math.log10(Math.max(1,v)):v;
  const upper=Math.max(.00001,transform(maxY)),lower=transform(minY);
  const xx=i=>left+innerW*i/N,yy=v=>top+innerH*(1-(transform(v)-lower)/(upper-lower||1));
  for(let i=0;i<=4;i++){
    const y=top+innerH*i/4;
    node.appendChild(svg("line",{x1:left,y1:y,x2:w-right,y2:y,stroke:"#e0e5d9","stroke-width":1}));
    const label=svg("text",{x:left-8,y:y+4,"text-anchor":"end","font-size":12,fill:"#52604f"});
    const value=lower+(upper-lower)*(1-i/4);
    label.textContent=logarithmic?(10**value).toPrecision(2):fmt(value,2);
    node.appendChild(label);
  }
  for(const i of [0,Math.round(N/2),N]){
    const t=svg("text",{x:xx(i),y:h-10,"text-anchor":"middle","font-size":12,fill:"#52604f"});t.textContent="step "+i;node.appendChild(t)
  }
  series.forEach((line,j)=>{
    const points=line.values.map((value,i)=>xx(i).toFixed(2)+","+yy(value).toFixed(2)).join(" ");
    node.appendChild(svg("polyline",{points,fill:"none",stroke:line.color||["#17677a","#a55c21"][j%2],"stroke-width":2.6,"stroke-linejoin":"round"}))
  });
}
function dataTable(id,heads,rows){const el=$(id);if(!el)return;const table=document.createElement("table");
  const thead=document.createElement("thead"),hr=document.createElement("tr");
  heads.forEach(head=>{const cell=document.createElement("th");cell.textContent=head;hr.appendChild(cell)});
  thead.appendChild(hr);table.appendChild(thead);const tbody=document.createElement("tbody");
  rows.forEach(row=>{const tr=document.createElement("tr");row.forEach((value,i)=>{const td=document.createElement(i===0?"th":"td");td.textContent=String(value);tr.appendChild(td)});tbody.appendChild(tr)});
  table.appendChild(tbody);el.replaceChildren(table)
}
function setText(id,value){if($(id))$(id).textContent=String(value)}
function renderCollatz(){
 if(!$("ccStart"))return;
 const start=getNum("ccStart",7),limit=Math.round(getNum("ccLimit",300));
 try{
 const result=Math10.collatz(start,limit);
 setText("ccSteps",result.reachedOne?result.steps:result.steps+"+");
 setText("ccPeak",fmt(result.peak));setText("ccEnd",result.reachedOne?"Reached 1":"Not reached within limit");
 setText("ccExplanation",result.reachedOne?
   "This start reached 1 in "+result.steps+" updates; the highest value was "+fmt(result.peak)+". That is a result for this start only.":
   "The sequence has not reached 1 within the displayed "+limit+" updates. That does not establish that it will never reach 1.");
 const max=Math.max(...result.values,1),log=$("ccLog")?.checked;
 pointChart("ccGraph",[{values:result.values,color:"#17677a"}],{minY:log?1:0,maxY:max,logarithmic:log});
 const entries=result.values;const indices=entries.length<=27?entries.map((_,i)=>i):[...Array.from({length:17},(_,i)=>i),...Array.from({length:10},(_,i)=>entries.length-10+i)];
 dataTable("ccTable",["Update","Value"],indices.map(i=>[i,fmt(entries[i])]));
 }catch(e){setText("ccExplanation",e.message);setText("ccEnd","Check input");if($("ccGraph"))$("ccGraph").replaceChildren()}
}
function renderLogistic(){
 if(!$("clR"))return;
 const r=getNum("clR",3.9),x=getNum("clX",0.4),delta=getNum("clDelta",.0001),steps=Math.round(getNum("clSteps",45));
 setText("clRLabel",fmt(r,2));setText("clDeltaLabel",fmt(delta,6));
 try{
 if(x+delta>1||x+delta<0)throw Error("The second starting value must also be between zero and one.");
 const a=Math10.logistic(r,x,steps),b=Math10.logistic(r,x+delta,steps);
 const difference=a.map((v,i)=>Math.abs(v-b[i]));
 const crossing=difference.findIndex(d=>d>0.1);
 setText("clFirst",fmt(a[1],6));setText("clGap",fmt(difference.at(-1),6));
 setText("clCross",crossing>=0?"Step "+crossing:"Not within "+steps+" steps");
 setText("clDescription","Both trajectories follow xₙ₊₁ = r xₙ(1−xₙ) with the same r. The separation need not grow on every single update.");
 pointChart("clGraph",[{values:a,color:"#17677a"},{values:b,color:"#a55c21"}],{minY:0,maxY:1});
 pointChart("clDiffGraph",[{values:difference,color:"#a55c21"}],{minY:0,maxY:1});
 const indices=[0,1,2,3,4,5,10,15,20,30,steps].filter((n,i,all)=>n<=steps&&all.indexOf(n)===i);
 dataTable("clTable",["Update","First start","Second start","Absolute gap"],indices.map(i=>[i,fmt(a[i],6),fmt(b[i],6),fmt(difference[i],6)]));
 }catch(e){setText("clDescription",e.message);setText("clCross","Check input")}
}
function renderSierpinski(){
 if(!$("cfStage"))return;
 const stage=Math.round(getNum("cfStage",3));
 try{
 const data=Math10.sierpinski(stage);
 setText("cfStageLabel",String(stage));
 setText("cfPieces",fmt(data.count));setText("cfArea",fmt(data.areaFraction,6));setText("cfSide","1/"+(2**stage));
 const stageSvg=$("cfGraph");if(stageSvg){
   stageSvg.replaceChildren();stageSvg.setAttribute("viewBox","0 0 700 610");
   data.triangles.forEach(tri=>stageSvg.appendChild(svg("polygon",{points:tri.map(p=>p.join(",")).join(" "),fill:"#536240",stroke:stage<=4?"#fffefa":"none","stroke-width":.5})));
 }
 const n=Math.max(0,Math.min(stage,7));dataTable("cfTable",["Stage","Number of triangles","Fraction of original area"],Array.from({length:n+1},(_,i)=>[i,fmt(3**i),fmt((3/4)**i,6)]));
 setText("cfDescription","At stage "+stage+", each small triangle has side length 1/"+(2**stage)+" of the original. There are "+data.count+" pieces, but they cover only "+fmt(100*data.areaFraction,2)+"% of the original area.");
 }catch(e){setText("cfDescription",e.message)}
}
function initExplorer(){
 const workspace=$("w10Explorer");if(!workspace)return;
 const tabs=[...workspace.querySelectorAll("[data-w10-tab]")];
 function select(tab){
   tabs.forEach(b=>{const on=b.dataset.w10Tab===tab;b.setAttribute("aria-pressed",String(on));});
   [...workspace.querySelectorAll("[data-w10-pane]")].forEach(e=>e.hidden=e.dataset.w10Pane!==tab);
   [...workspace.querySelectorAll("[data-w10-controls]")].forEach(e=>e.hidden=e.dataset.w10Controls!==tab);
 }
 tabs.forEach(b=>b.addEventListener("click",()=>select(b.dataset.w10Tab)));
 for(const id of ["ccStart","ccLimit","ccLog"]){const e=$(id);if(e)e.addEventListener(id==="ccLog"?"change":"input",renderCollatz)}
 for(const id of ["clR","clX","clDelta","clSteps"]){const e=$(id);if(e)e.addEventListener("input",renderLogistic)}
 if($("cfStage"))$("cfStage").addEventListener("input",renderSierpinski);
 for(const b of workspace.querySelectorAll("[data-logistic-preset]")){
   b.addEventListener("click",()=>{if($("clR"))$("clR").value=b.dataset.logisticPreset;renderLogistic()});
 }
 for(const b of workspace.querySelectorAll("[data-collatz-preset]")){
   b.addEventListener("click",()=>{if($("ccStart"))$("ccStart").value=b.dataset.collatzPreset;renderCollatz()});
 }
 select("collatz");renderCollatz();renderLogistic();renderSierpinski();
}
function initAnswers(){
 const container=$("main");if(!container)return;
 const keyBase=container.dataset.answerStore||"math107_week10_ccf_v1";
 const fields=[...container.querySelectorAll("input[data-save],textarea[data-save],select[data-save]")];
 const load=(k)=>{try{return localStorage.getItem(k)}catch(_){return null}};
 const save=(k,v)=>{try{localStorage.setItem(k,v);setText("saveStatus","Saved in this browser.")}catch(e){setText("saveStatus","Saving is unavailable. Print or download your completed work.")}};
 for(const field of fields){
   const k=keyBase+"_"+field.id;
   const original=load(k);if(original!==null)field.value=original;
   field.addEventListener("input",()=>save(k,field.value));
   field.addEventListener("change",()=>save(k,field.value))
 }
 const name=$("studentName"),prior=load(keyBase+"_studentName");if(name){
   if(prior!==null)name.value=prior;
   name.addEventListener("input",()=>save(keyBase+"_studentName",name.value))
 }
 const groups=[...container.querySelectorAll("[data-check-group]")];
 for(const group of groups){
   const marker=group.dataset.checkGroup;const button=group.querySelector("[data-check]");
   const status=group.querySelector(".section-feedback");
   const prior=load(keyBase+"_section_"+marker);if(prior==="done")group.dataset.checked="true";
   if(button)button.addEventListener("click",()=>{
     const graded=[...group.querySelectorAll("[data-answer]")];
     let all=true;
     graded.forEach(input=>{
       const raw=(input.value||"").trim(),expected=input.dataset.answer;
       const tolerance=Number(input.dataset.tolerance||"0.001");
       let correct=false;
       if(raw){if(input.dataset.answerType==="text")correct=raw.toLowerCase()===expected.toLowerCase();else {
        const value=raw.includes("/")?(()=>{const [a,b]=raw.split("/").map(Number);return b? a/b : NaN})():Number(raw);
        correct=Number.isFinite(value)&&Math.abs(value-Number(expected))<=tolerance;
       }}
       input.setAttribute("aria-invalid",String(!correct));
       const feedback=group.querySelector('[data-feedback-for="'+input.id+'"]');
       if(feedback)feedback.textContent=correct?"Correct.":(input.dataset.hint||"Check your calculation and try again.");
       if(!correct)all=false;
     });
     if(all){
       group.dataset.checked="true";save(keyBase+"_section_"+marker,"done");
       if(status)status.textContent="Section checked. Explain your reasoning in the written responses.";
     }else if(status)status.textContent="Revise the marked calculations; your written responses are still saved.";
     updateCount()
   })
 }
 function updateCount(){setText("sectionCount",groups.filter(g=>g.dataset.checked==="true").length+" / "+groups.length+" sections checked")}
 updateCount();
}
function initPrint(){
 document.querySelectorAll("[data-print-page],[data-print-work]").forEach(b=>b.addEventListener("click",()=>root.print&&root.print()));
 if(!root.addEventListener)return;
 root.addEventListener("beforeprint",()=>{
   const name=$("studentName");if($("printName"))$("printName").textContent=name&&name.value?"Student: "+name.value:"";
   document.querySelectorAll("textarea[data-save]").forEach(el=>{
     if(el.value){el.style.height="auto";el.style.height=Math.max(95,el.scrollHeight+8)+"px"}
   })
 });
}
function init(){initExplorer();initAnswers();initPrint()}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);else init();
})(typeof globalThis!=="undefined"?globalThis:this);
