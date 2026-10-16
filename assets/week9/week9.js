/* Exact graph computations and student controls for Week 9. */
(function(root){
'use strict';
const N=[...'ABCDEFG'],E=['AB','AC','BC','BD','CD','DE','EF','EG','FG'].map(s=>[...s]);
const clone=edges=>({nodes:[...N],edges:edges.map(e=>[...e])});
const Math9={
 nodes:N,edges:E,
 presets:{bridge:clone(E),mesh:clone([...E,['D','F']]),disconnected:clone(E.filter(e=>e.join('')!=='DE')),star:clone(N.filter(n=>n!=='D').map(n=>['D',n]))},
 number(raw){const s=String(raw).trim();if(!s)return NaN;const m=s.match(/^([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*\/\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))$/);if(m)return Number(m[2])===0?NaN:Number(m[1])/Number(m[2]);return /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(s)?Number(s):NaN;},
 key(e){return [...e].sort().join('');},
 adjacency(g){const a=Object.fromEntries(g.nodes.map(n=>[n,[]]));for(const [u,v] of g.edges){a[u].push(v);a[v].push(u);}return a;},
 components(g){const a=this.adjacency(g),seen=new Set(),groups=[];for(const n of g.nodes)if(!seen.has(n)){const q=[n],part=[];seen.add(n);while(q.length){const u=q.shift();part.push(u);for(const v of a[u])if(!seen.has(v)){seen.add(v);q.push(v);}}groups.push(part.sort());}return groups;},
 distances(g,start){const a=this.adjacency(g),d=Object.fromEntries(g.nodes.map(n=>[n,Infinity])),prev={};if(!Object.hasOwn(a,start))throw Error('Start must be a node in the network.');d[start]=0;const q=[start];while(q.length){const u=q.shift();for(const v of a[u])if(d[v]===Infinity){d[v]=d[u]+1;prev[v]=u;q.push(v);}}return {d,prev};},
 path(g,start,end){const {d,prev}=this.distances(g,start);if(!Number.isFinite(d[end]))return null;const p=[end];while(p[0]!==start)p.unshift(prev[p[0]]);return p;},
 bridges(g){const c=this.components(g).length;return g.edges.filter(e=>this.components({...g,edges:g.edges.filter(x=>x!==e)}).length>c).map(e=>this.key(e));},
 step(g,active,rule='automatic'){if(!['automatic','half'].includes(rule))throw Error('Unknown spreading rule.');const a=this.adjacency(g),old=new Set(active),fresh=g.nodes.filter(n=>!old.has(n)&&a[n].length>0&&a[n].filter(x=>old.has(x)).length>=(rule==='half'?Math.ceil(a[n].length/2):1));return {active:g.nodes.filter(n=>old.has(n)||fresh.includes(n)),new:fresh};},
 sequence(g,seeds,rule='automatic'){const active=g.nodes.filter(n=>seeds.includes(n)),h=[{active,new:active}];for(let k=0;k<g.nodes.length&&h.at(-1).active.length<g.nodes.length;k++){h.push(this.step(g,h.at(-1).active,rule));if(!h.at(-1).new.length)break;}return h;},
 signal(x1,x2,{drop=false,relu=false,outputWeight=1.5}={}){if(![x1,x2,outputWeight].every(Number.isFinite))throw Error('Signals and weights must be finite.');const raw1=.5*x1+(drop?0:.25*x2),raw2=-.5*x1+.75*x2,h1=relu?Math.max(0,raw1):raw1,h2=relu?Math.max(0,raw2):raw2;return {raw1,raw2,h1,h2,o:outputWeight*h1-.5*h2};}
};
root.Math9=Math9;if(typeof module!=='undefined'&&module.exports)module.exports=Math9;
if(typeof document==='undefined')return;
const $=id=>document.getElementById(id),text=(id,value)=>{if($(id))$(id).textContent=value;};
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function table(id,headers,rows){const target=$(id);if(!target)return;const t=document.createElement('table'),h=document.createElement('thead'),r=document.createElement('tr');for(const v of headers){const c=document.createElement('th');c.scope='col';c.textContent=v;r.append(c);}h.append(r);t.append(h);const body=document.createElement('tbody');for(const row of rows){const r=document.createElement('tr');for(const v of row){const c=document.createElement('td');c.textContent=v;r.append(c);}body.append(r);}t.append(body);target.replaceChildren(t);}
function options(id,items,chosen=''){const s=$(id);s.replaceChildren();for(const [value,label] of items){const o=document.createElement('option');o.value=value;o.setAttribute('value',value);o.textContent=label;s.append(o);}s.value=chosen;}
const edgeLabel=e=>[...e].join('–');
function graph(id,g,{start='A',path=null,active=null,first=null,removed='',added='',star=false,title='Community communication network',missingFirstLabel='waiting'}={}){
 const target=$(id);if(!target)return;const p=star?{D:[440,205],A:[160,85],B:[440,65],C:[720,85],E:[720,325],F:[440,350],G:[160,325]}:{A:[80,210],B:[235,95],C:[235,325],D:[400,210],E:[570,210],F:[735,95],G:[735,325]};
 const pathEdges=new Set(path?path.slice(1).map((n,i)=>Math9.key([path[i],n])):[]),activeSet=active===null?null:new Set(active);
 let s=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 425" role="img" aria-labelledby="${id}-title ${id}-desc"><title id="${id}-title">${esc(title)}</title><desc id="${id}-desc">Available links: ${g.edges.map(edgeLabel).join(', ')}. ${path?'Selected path: '+path.join(' to ')+'. ':''}${active?'Active now: '+active.join(', ')+'. ':''}A table gives the same network information.</desc>`;
 if(removed){const [u,v]=[...removed];s+=`<line x1="${p[u][0]}" y1="${p[u][1]}" x2="${p[v][0]}" y2="${p[v][1]}" stroke="#943c2d" stroke-width="2" stroke-dasharray="5 5"/><text x="${(p[u][0]+p[v][0])/2}" y="${(p[u][1]+p[v][1])/2-12}" text-anchor="middle" font-size="13" fill="#943c2d">unavailable</text>`;}
 for(const e of g.edges){const [u,v]=e,k=Math9.key(e),isPath=pathEdges.has(k);s+=`<line data-edge="${k}" x1="${p[u][0]}" y1="${p[u][1]}" x2="${p[v][0]}" y2="${p[v][1]}" stroke="${isPath?'#a55c21':k===added?'#17677a':'#abb69e'}" stroke-width="${isPath?6:3}"/>`;if(k===added)s+=`<text x="${(p[u][0]+p[v][0])/2+10}" y="${(p[u][1]+p[v][1])/2-9}" font-size="13" fill="#17677a">new link</text>`;}
 for(const n of g.nodes){const [x,y]=p[n],on=activeSet===null||activeSet.has(n);if(n===start)s+=`<circle cx="${x}" cy="${y}" r="33" fill="none" stroke="#a55c21" stroke-width="2"/>`;s+=`<circle cx="${x}" cy="${y}" r="26" fill="${on?'#536240':'#fffef8'}" stroke="#536240" stroke-width="2"/><text x="${x}" y="${y+6}" text-anchor="middle" font-size="19" font-weight="700" fill="${on?'white':'#293329'}">${n}</text>`;if(first)s+=`<text x="${x}" y="${y+53}" text-anchor="middle" font-size="13" fill="#17677a">${Object.hasOwn(first,n)?'round '+first[n]:missingFirstLabel}</text>`;}
 target.innerHTML=s+'</svg>';
}
function initAnswers(){
 const form=document.querySelector('[data-answer-store]');if(!form)return;
 const fields=[...form.querySelectorAll('[data-answer],textarea[data-save]')],key=form.dataset.answerStore,legacy=form.dataset.legacyStore,groups=[...form.querySelectorAll('[data-check-group]')],done=new Set();let storageOK=true;
 function numericCorrect(el){const v=Math9.number(el.value);return Number.isFinite(v)&&Math.abs(v-Number(el.dataset.answer))<=Number(el.dataset.tolerance||.001);}
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
function initExplorer(){
 if(!$('preset'))return;
 let history=[],chosenPath=null;
 const names={bridge:'Original network: nine links, one component, and the bridge D–E.',mesh:'The original nine links plus D–F. It has alternate cross-region routes.',disconnected:'The original network with D–E absent. The two regions are separate components.',star:'Every outer location connects only to D. D has six neighbors; the other nodes each have one.'};
 function current(){const base=Math9.presets[$('preset').value],rem=$('remove').value,add=$('add').value;return {nodes:[...base.nodes],edges:[...base.edges.filter(e=>Math9.key(e)!==rem),...(add?[[...add]]:[])]};}
 function seeds(){return $('spreadSeeds').value==='bc'?['B','C']:$('spreadSeeds').value==='bcf'?['B','C','F']:[$('start').value];}
 function restart(message){const active=seeds();history=[{active,new:active}];chosenPath=null;text('message',message||'Round 0 restored. No transmission or adoption update has occurred.');render();}
 function setup(){const g=Math9.presets[$('preset').value];options('start',g.nodes.map(n=>[n,n]),'A');options('end',g.nodes.map(n=>[n,n]),'G');options('remove',[['','None'],...g.edges.map(e=>[Math9.key(e),edgeLabel(e)])]);const absent=[];for(let i=0;i<N.length;i++)for(let j=i+1;j<N.length;j++){const k=N[i]+N[j];if(!g.edges.some(e=>Math9.key(e)===k))absent.push([k,edgeLabel(k)]);}options('add',[['','None'],...absent]);restart(names[$('preset').value]);}
 function render(){const g=current(),a=Math9.adjacency(g),start=$('start').value,{d}=Math9.distances(g,start),parts=Math9.components(g),last=history.at(-1),first={};history.forEach((state,i)=>state.new.forEach(n=>{if(!Object.hasOwn(first,n))first[n]=i;}));
 graph('graph',g,{start,path:chosenPath,active:chosenPath?null:last.active,first:chosenPath?null:first,removed:$('remove').value,added:$('add').value,star:$('preset').value==='star',title:'Current editable network'});
 text('presetNote',names[$('preset').value]+' The add/remove menus modify this preset.');text('mNodes',g.nodes.length);text('mEdges',g.edges.length);text('mDensity',(g.edges.length/21).toFixed(3));text('mComponents',parts.length);text('mDegree',a[start].length);text('mReach',g.nodes.filter(n=>Number.isFinite(d[n])).length+' / '+g.nodes.length);text('neighbors',`${start} has direct neighbors: ${a[start].join(', ')||'none'}. Components: ${parts.map(p=>'{'+p.join(', ')+'}').join(' and ')}.`);
 const bridges=Math9.bridges(g);text('bridges',bridges.length?'Current bridge edges: '+bridges.map(edgeLabel).join(', ')+'. Removing any one increases the component count.':'No single available edge is a bridge in this network.');
 table('networkTable',['Node','Neighbors','Degree','Distance from '+start,'Active now','First active round'],g.nodes.map(n=>[n,a[n].join(', ')||'none',a[n].length,Number.isFinite(d[n])?d[n]:'unreachable',last.active.includes(n)?'yes':'no',Object.hasOwn(first,n)?first[n]:'not yet']));
 const rows=g.nodes.map(n=>{const ds=Object.values(Math9.distances(g,n).d),ok=ds.every(Number.isFinite),sum=ok?ds.reduce((s,x)=>s+x,0):null;return [n,a[n].length,(a[n].length/6).toFixed(3),sum??'—',sum===null?'—':(6/sum).toFixed(3)];});table('centrality',['Node','Degree','Degree ÷ 6','Distance sum','Closeness = 6 ÷ sum'],rows);const top=Math.max(...g.nodes.map(n=>a[n].length));text('centralNote','Highest degree: '+g.nodes.filter(n=>a[n].length===top).join(', ')+` (${top}). These scores use the current links, including your changes.`);
 const k=history.length-1,finished=last.active.length===g.nodes.length,stopped=k>0&&!last.new.length;
 text('spreadRuleNote',$('spreadRule').value==='automatic'?'Automatic rule: an inactive node becomes active if at least one neighbor was active in the previous snapshot.':'Half-neighbor rule: an inactive node with neighbors needs at least half of them active in the previous snapshot; round the required count up. Isolated non-seeds stay inactive.');
 text('spreadInfo',`Round ${k}: active = ${last.active.join(', ')} (${last.active.length} total). ${k?'New this round: '+(last.new.join(', ')||'none')+'.':'These are the starting seeds.'}${finished?' All seven are active.':stopped?' The process has stopped: no new activations, so later snapshots will be identical.':''}`);$('spreadBtn').disabled=finished||stopped;table('spreadTable',['Round','Newly active','All active','Total'],history.map((h,i)=>[i,h.new.join(', ')||'none',h.active.join(', '),h.active.length]));
 }
 $('preset').addEventListener('change',setup);
 for(const id of ['start','end','remove','add','spreadRule','spreadSeeds'])$(id).addEventListener('change',()=>restart('Experiment restarted at round 0 after your selection changed.'));
 $('pathBtn').addEventListener('click',()=>{const start=$('start').value,end=$('end').value;chosenPath=Math9.path(current(),start,end);text('message',chosenPath?`A shortest path is ${chosenPath.join(' → ')}. Length = ${chosenPath.length-1} edge${chosenPath.length===2?'':'s'}.`:`No path exists from ${start} to ${end} using the available links. A missing route is not a distance of zero.`);render();});
 $('spreadBtn').addEventListener('click',()=>{history.push(Math9.step(current(),history.at(-1).active,$('spreadRule').value));chosenPath=null;text('message','The picture now shows the active set after this round. First-activation rounds appear below the nodes.');render();});
 $('resetBtn').addEventListener('click',()=>restart());$('spreadReset').addEventListener('click',()=>restart());setup();
}
function initLab(){
 if(!$('labNode'))return;const g=Math9.presets.bridge,a=Math9.adjacency(g),states=Math9.sequence(g,['A']);
 function neighbor(){const n=$('labNode').value;text('labNeighbors',`${n}: direct neighbors ${a[n].join(', ')}. Degree = ${a[n].length}.`);}
 function round(){const k=+$('labRound').value,h=states[k],first={};states.slice(0,k+1).forEach((s,i)=>s.new.forEach(n=>first[n]=i));text('labRoundValue',k);graph('labSpreadPlot',g,{active:h.active,first,title:'Automatic alert spread from A'});text('labSpreadInfo',`Round ${k}: ${k?'newly informed':'initial source'} ${h.new.join(', ')}; all informed ${h.active.join(', ')} (${h.active.length} total).`);}
 $('labNode').addEventListener('change',neighbor);$('labRound').addEventListener('input',round);neighbor();round();
}
function initApplication(){
 if(!$('appScenario'))return;
 function draw(){const choice=$('appScenario').value,failed=['failed','df-failed'].includes(choice),added=choice==='ad'?'AD':['df','df-failed'].includes(choice)?'DF':'',g={nodes:[...N],edges:[...E.filter(e=>!failed||Math9.key(e)!=='DE'),...(added?[[...added]]:[])]},{d}=Math9.distances(g,'A'),reach=N.filter(n=>Number.isFinite(d[n])),first=Object.fromEntries(reach.map(n=>[n,d[n]]));graph('appPlot',g,{active:reach,first,removed:failed?'DE':'',added,path:Math9.path(g,'A','G'),title:'Selected community-alert scenario',missingFirstLabel:'unreachable'});table('appTable',['Location','First arrival round','One shortest path from A'],N.map(n=>[n,Number.isFinite(d[n])?d[n]:'unreachable',Math9.path(g,'A',n)?.join(' → ')||'no path']));text('appSummary',reach.length===7?`All seven locations are reachable. The last first-arrival round is ${Math.max(...Object.values(d))}.`:`Only ${reach.length} of 7 locations are reachable from A. ${N.filter(n=>!Number.isFinite(d[n])).join(', ')} are unreachable; more rounds cannot create a missing path.`);}
 $('appScenario').addEventListener('change',draw);draw();
}
function signalGraph(a,b,v,drop,relu){
 const pos={x1:[95,110],x2:[95,310],h1:[470,110],h2:[470,310],o:[760,210]},values={x1:a,x2:b,h1:v.h1,h2:v.h2,o:v.o},labels={x1:'x₁',x2:'x₂',h1:'H₁',h2:'H₂',o:'O'},links=[['x1','h1',.5,270,82],['x2','h1',.25,365,220],['x1','h2',-.5,200,220],['x2','h2',.75,270,344],['h1','o',1.5,617,136],['h2','o',-.5,617,280]];
 let s='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 870 425" role="img" aria-labelledby="signal-title signal-desc"><title id="signal-title">Current weighted-signal calculation</title><desc id="signal-desc">'+esc(`Inputs ${a}, ${b}; hidden values ${v.h1}, ${v.h2}; output ${v.o}. ${drop?'The x2 to H1 edge is absent. ':''}${relu?'Negative hidden sums are replaced by zero. ':''}The table lists contributions and values.`)+'</desc><defs><marker id="signal-arrow-positive" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#17677a"/></marker><marker id="signal-arrow-negative" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#a55c21"/></marker></defs>';
 for(const [u,w,weight,tx,ty] of links){if(drop&&u==='x2'&&w==='h1')continue;const [x,y]=pos[u],[xx,yy]=pos[w],d=Math.hypot(xx-x,yy-y),dx=(xx-x)/d,dy=(yy-y)/d,color=weight<0?'#a55c21':'#17677a';s+=`<line x1="${x+dx*29}" y1="${y+dy*29}" x2="${xx-dx*34}" y2="${yy-dy*34}" stroke="${color}" stroke-width="2.8" ${weight<0?'stroke-dasharray="6 4"':''} marker-end="url(#signal-arrow-${weight<0?'negative':'positive'})"/><rect x="${tx-38}" y="${ty-17}" width="76" height="26" rx="4" fill="white"/><text x="${tx}" y="${ty+2}" text-anchor="middle" font-size="15" fill="${color}">× ${weight.toFixed(2)}</text>`;}
 for(const n of Object.keys(pos)){const [x,y]=pos[n];s+=`<circle cx="${x}" cy="${y}" r="28" fill="#536240"/><text x="${x}" y="${y+6}" text-anchor="middle" fill="white" font-size="19">${labels[n]}</text><text x="${x}" y="${y+54}" text-anchor="middle" font-size="15" fill="#17677a">${values[n].toFixed(2)}</text>`;}
 s+='<text x="95" y="35" text-anchor="middle" font-size="16">Inputs</text><text x="470" y="35" text-anchor="middle" font-size="16">Hidden values</text><text x="760" y="35" text-anchor="middle" font-size="16">Output</text></svg>';$('liveNetwork').innerHTML=s;
}
function initAI(){
 if(!$('x1'))return;
 function draw(){const a=+$('x1').value,b=+$('x2').value,drop=$('dropEdge').checked,relu=$('useRelu').checked,v=Math9.signal(a,b,{drop,relu}),f=n=>n.toFixed(2);text('x1v',a);text('x2v',b);text('liveH1',f(v.h1));text('liveH2',f(v.h2));text('liveO',f(v.o));signalGraph(a,b,v,drop,relu);table('liveTable',['Receiving node','Incoming weighted contributions','Raw sum','Value sent onward'],[['H₁',`0.50 × ${a}`+(drop?' (motion edge removed)':` + 0.25 × ${b}`),f(v.raw1),f(v.h1)],['H₂',`−0.50 × ${a} + 0.75 × ${b}`,f(v.raw2),f(v.h2)],['O',`1.50 × ${f(v.h1)} − 0.50 × ${f(v.h2)}`,f(v.o),f(v.o)]]);text('liveRule',(drop?'The x₂ → H₁ contribution is absent. ':'All six arrows are present. ')+(relu?'Hidden nodes send max(0, raw sum). The output still just adds its weighted inputs.':'Every node sends its raw sum. ')+(!drop&&!relu?'The two x₂ paths cancel, so the output equals x₁.':''));}
 for(const id of ['x1','x2','dropEdge','useRelu'])$(id).addEventListener('input',draw);$('aiReset').addEventListener('click',()=>{$('x1').value=2;$('x2').value=4;$('dropEdge').checked=false;$('useRelu').checked=false;draw();});draw();
}
function init(){initAnswers();initExplorer();initLab();initApplication();initAI();document.querySelectorAll('[data-print-page]').forEach(b=>b.addEventListener('click',()=>window.print()));window.addEventListener('beforeprint',preparePrint);window.addEventListener('afterprint',()=>document.querySelectorAll('.print-answer').forEach(e=>e.remove()));}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})(typeof globalThis!=='undefined'?globalThis:this);
