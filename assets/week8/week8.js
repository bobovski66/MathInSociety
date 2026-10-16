/* Exact two-variable geometry, LP results, and Week 8 student controls. */
(function(root){
'use strict';
const EPS=1e-8,near=(a,b)=>Math.abs(a-b)<=EPS*Math.max(1,Math.abs(a),Math.abs(b));
const scoreNear=(a,b)=>Math.abs(a-b)<=32*Number.EPSILON*Math.max(Math.abs(a),Math.abs(b),Number.MIN_VALUE);
const rayTolerance=(g,r)=>32*Number.EPSILON*(Math.abs(g.cx*r[0])+Math.abs(g.cy*r[1]));
const C=(a,b,c,s='le')=>({a,b,c,s}),model=(cons,cx,cy,dir,context,xlabel='x',ylabel='y')=>({cons,cx,cy,dir,context,xlabel,ylabel});
const Math8={
 number(raw){const s=String(raw).trim();if(!s)return NaN;const m=s.match(/^([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*\/\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))$/);if(m)return Number(m[2])===0?NaN:Number(m[1])/Number(m[2]);return /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(s)?Number(s):NaN;},
 constraints(g){return [...g.cons,C(1,0,0,'ge'),C(0,1,0,'ge')];},
 feasible(p,g){return p.every(Number.isFinite)&&this.constraints(g).every(q=>q.s==='le'?q.a*p[0]+q.b*p[1]<=q.c+EPS:q.a*p[0]+q.b*p[1]>=q.c-EPS);},
 intersection(q,r){const d=q.a*r.b-r.a*q.b;if(Math.abs(d)<1e-12)return null;return [(q.c*r.b-r.c*q.b)/d,(q.a*r.c-r.a*q.c)/d].map(x=>Math.abs(x)<EPS?0:x);},
 unique(points){const out=[];for(const p of points)if(!out.some(q=>near(p[0],q[0])&&near(p[1],q[1])))out.push(p);return out;},
 vertices(g){const lines=this.constraints(g),pts=[];for(let i=0;i<lines.length;i++)for(let j=i+1;j<lines.length;j++){const p=this.intersection(lines[i],lines[j]);if(p&&this.feasible(p,g))pts.push(p);}const v=this.unique(pts);if(v.length>2){const mid=v.reduce((s,p)=>[s[0]+p[0]/v.length,s[1]+p[1]/v.length],[0,0]);v.sort((a,b)=>Math.atan2(a[1]-mid[1],a[0]-mid[0])-Math.atan2(b[1]-mid[1],b[0]-mid[0]));}else v.sort((a,b)=>a[0]-b[0]||a[1]-b[1]);return v;},
 rays(g){const candidates=[[1,0],[0,1]];for(const q of g.cons)candidates.push([q.b,-q.a],[-q.b,q.a]);return this.unique(candidates.filter(p=>Math.hypot(...p)>EPS).map(p=>p.map(x=>Math.abs(x)<EPS?0:x/Math.hypot(...p))).filter(p=>p[0]>=-EPS&&p[1]>=-EPS&&g.cons.every(q=>q.s==='le'?q.a*p[0]+q.b*p[1]<=EPS:q.a*p[0]+q.b*p[1]>=-EPS)));},
 solve(g){const vertices=this.vertices(g);if(!vertices.length)return {status:'infeasible',vertices:[],rays:[],best:[],value:null,bounded:false,flatRays:[]};const rays=this.rays(g),bounded=rays.length===0,improving=rays.filter(r=>(g.cx*r[0]+g.cy*r[1])*(g.dir==='max'?1:-1)>rayTolerance(g,r));if(improving.length)return {status:'unbounded',vertices,rays,best:[],value:null,bounded,improving,flatRays:[]};const values=vertices.map(p=>g.cx*p[0]+g.cy*p[1]),value=(g.dir==='max'?Math.max:Math.min)(...values),best=vertices.filter((p,i)=>scoreNear(values[i],value)),flatRays=rays.filter(r=>Math.abs(g.cx*r[0]+g.cy*r[1])<=rayTolerance(g,r));return {status:'optimal',vertices,rays,best,value,bounded,flatRays,constant:g.cx===0&&g.cy===0};},
 clip(poly,q){if(!poly.length)return [];const out=[],sign=q.s==='le'?1:-1;for(let i=0;i<poly.length;i++){const a=poly[i],b=poly[(i+1)%poly.length],fa=sign*(q.a*a[0]+q.b*a[1]-q.c),fb=sign*(q.a*b[0]+q.b*b[1]-q.c);if(fa<=EPS)out.push(a);if((fa<=EPS)!==(fb<=EPS)){const t=fa/(fa-fb);out.push([a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])]);}}return this.unique(out);},
 polygon(g,xmax,ymax){return g.cons.reduce((p,q)=>this.clip(p,q),[[0,0],[xmax,0],[xmax,ymax],[0,ymax]]);},
 whole(g,cap=15000){const s=this.solve(g);if(s.status==='infeasible')return {status:'infeasible',points:[],best:[],value:null};if(!s.bounded)return {status:'unavailable',points:[],best:[],value:null};const mx=Math.floor(Math.max(...s.vertices.map(p=>p[0]))+EPS),my=Math.floor(Math.max(...s.vertices.map(p=>p[1]))+EPS);if((mx+1)*(my+1)>cap)return {status:'unavailable',points:[],best:[],value:null};const points=[];for(let x=0;x<=mx;x++)for(let y=0;y<=my;y++)if(this.feasible([x,y],g))points.push([x,y]);if(!points.length)return {status:'infeasible',points:[],best:[],value:null};const values=points.map(p=>g.cx*p[0]+g.cy*p[1]),value=(g.dir==='max'?Math.max:Math.min)(...values);return {status:'optimal',points,best:points.filter((p,i)=>scoreNear(values[i],value)),value};},
 mix(points,amounts){if(points.length!==amounts.length||!points.length||amounts.some(x=>!Number.isFinite(x)||x<0))throw Error('Use a nonnegative amount for every input.');const total=amounts.reduce((s,x)=>s+x,0);if(!Number.isFinite(total)||total<=0)throw Error('Use at least one positive amount; zero total cannot be normalized.');const n=points[0].length;if(points.some(p=>p.length!==n||p.some(x=>!Number.isFinite(x))))throw Error('All vectors must have the same number of finite coordinates.');const weights=amounts.map(x=>x/total),point=Array.from({length:n},(_,j)=>points.reduce((s,p,i)=>s+weights[i]*p[j],0));return {weights,point,total};}
};
Math8.models={
 snacks:model([C(1,1,8),C(2,1,12)],3,2,'max','x = type-A snack packs, y = type-B packs. Packing has 8 slots; ingredients have 12 portions. Maximize contribution dollars.','Type A packs, x','Type B packs, y'),
 lab:model([C(2,1,10),C(1,1,7)],1,1,'max','x and y are production quantities. The lab example has limits 2x+y≤10 and x+y≤7.','Product A quantity, x','Product B quantity, y'),
 workshop:model([C(2,4,40),C(1,1,14)],30,50,'max','x = chairs per week, y = tables. Wood allows 40 units; assembly allows 14 slots. Contribution is in dollars.','Chairs per week, x','Tables per week, y'),
 textbook:model([C(3,2,120),C(1,2,60)],4,5,'max','Two production quantities share resources with allowances 120 and 60. Each coefficient is resource use per unit.','Product A quantity, x','Product B quantity, y'),
 furniture:model([C(2,3,120),C(1,2,70)],40,70,'max','x = chairs and y = desks per week. Two resource totals may not exceed 120 and 70. Contribution dollars: 40x+70y.','Chairs, x','Desks, y'),
 tomatoes:model([C(1,2,80),C(1,1,50)],25,40,'max','x = tomato crates, y = pepper crates. Two resource allowances are 80 and 50. Revenue dollars: 25x+40y.','Tomato crates, x','Pepper crates, y'),
 nutrition:model([C(4,2,16,'ge'),C(2,5,15,'ge')],1.5,2,'min','x and y are liters of two invented ingredient blends. Each liter supplies respectively (4,2) or (2,5) units of two required components. At least 16 and 15 units are needed; costs are $1.50 and $2 per liter.','Liters of blend A, x','Liters of blend B, y'),
 tie:model([C(1,1,5),C(1,0,4)],1,1,'max','Production quantities satisfy x+y≤5 and x≤4. Equal objective coefficients reward only the total quantity.','Quantity x','Quantity y'),
 integer:model([C(1,2,8),C(3,2,10)],5,8,'max','Two batch counts use resources in ratios 1:2 and 3:2, with limits 8 and 10. Compare the continuous score with feasible whole-number plans.','A batches, x','B batches, y'),
 empty:model([C(1,1,4),C(1,1,6,'ge')],1,1,'max','The same total is required to be at most 4 and at least 6. No point can satisfy both.','x','y'),
 unbounded:model([C(1,1,6,'ge')],1,1,'max','Only a minimum total of 6 is required. With no upper resource limits, x+y can increase without bound.','x','y')
};
root.Math8=Math8;if(typeof module!=='undefined'&&module.exports)module.exports=Math8;
if(typeof document==='undefined')return;
const $=id=>document.getElementById(id),text=(id,v)=>{if($(id))$(id).textContent=v;},fmt=(x,p=3)=>x!==0&&Math.abs(x)<.001?Number(x.toPrecision(4)).toString():Math.abs(x-Math.round(x))<1e-8?String(Math.round(x)):x.toFixed(p).replace(/0+$/,'').replace(/\.$/,''),point=p=>'('+p.map(x=>fmt(x)).join(', ')+')';
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function table(id,headers,rows){const out=$(id);if(!out)return;const t=document.createElement('table'),head=document.createElement('thead'),tr=document.createElement('tr');for(const h of headers){const c=document.createElement('th');c.scope='col';c.textContent=h;tr.append(c);}head.append(tr);t.append(head);const body=document.createElement('tbody');for(const row of rows){const r=document.createElement('tr');for(const v of row){const c=document.createElement('td');c.textContent=v;r.append(c);}body.append(r);}t.append(body);out.replaceChildren(t);}
function expression(a,b){const parts=[];if(a)parts.push((a===1?'':fmt(a))+'x');if(b)parts.push((parts.length?' + ':'')+(b===1?'':fmt(b))+'y');return parts.join('')||'0';}
function equation(q,equal=false){return expression(q.a,q.b)+(equal?' = ':q.s==='le'?' ≤ ':' ≥ ')+fmt(q.c);}
function constraints(g){return g.cons.map(q=>equation(q)).join('; ')+'; x ≥ 0; y ≥ 0.';}
function plot(id,g,{test=null,half=false,labels=true,solution=null,integer=null,title='Feasible choices and true vertices'}={}){
 const target=$(id);if(!target)return;const s=solution||Math8.solve(g),verts=s.vertices,intercepts=g.cons.flatMap(q=>[q.a>0&&q.c>0?q.c/q.a:0,q.b>0&&q.c>0?q.c/q.b:0]);
 let mx=Math.max(2,...verts.map(p=>p[0]),...g.cons.filter(q=>q.a>0&&q.c>0).map(q=>q.c/q.a)),my=Math.max(2,...verts.map(p=>p[1]),...g.cons.filter(q=>q.b>0&&q.c>0).map(q=>q.c/q.b));
 if(!s.bounded){mx=Math.max(mx,8)*1.2;my=Math.max(my,8)*1.2;}mx*=1.12;my*=1.12;
 const w=920,h=560,L=82,R=32,T=32,B=85,pw=w-L-R,ph=h-T-B,X=x=>L+pw*x/mx,Y=y=>h-B-ph*y/my,colors=['#17677a','#a55c21','#70578b'];
 let svg=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" role="img" aria-labelledby="${id}-title ${id}-desc"><title id="${id}-title">${esc(title)}</title><desc id="${id}-desc">${esc(constraints(g))} True feasible vertices: ${verts.map(point).join('; ')||'none'}. ${!s.bounded&&s.status!=='infeasible'?'The shaded region continues beyond the viewing window. ':''}The table gives numerical values.</desc><defs><clipPath id="${id}-clip"><rect x="${L}" y="${T}" width="${pw}" height="${ph}"/></clipPath></defs><rect width="920" height="560" fill="white"/>`;
 const shape=(poly,fill,opacity)=>poly.length>=3?`<polygon points="${poly.map(p=>X(p[0])+','+Y(p[1])).join(' ')}" fill="${fill}" opacity="${opacity}"/>`:'';
 svg+=`<g clip-path="url(#${id}-clip)">`;
 if(half)g.cons.forEach((q,i)=>svg+=shape(Math8.polygon({cons:[q]},mx,my),colors[i%3],.10));
 svg+=shape(Math8.polygon(g,mx,my),'#536240',.23)+'</g>';
 for(let i=0;i<=5;i++){const x=mx*i/5,y=my*i/5;svg+=`<path d="M${X(x)} ${T}V${h-B}" stroke="#d8ddcd"/><path d="M${L} ${Y(y)}H${w-R}" stroke="#d8ddcd"/><text x="${X(x)}" y="${h-B+25}" text-anchor="middle" font-size="13" fill="#52604f">${fmt(x)}</text><text x="${L-12}" y="${Y(y)+5}" text-anchor="end" font-size="13" fill="#52604f">${fmt(y)}</text>`;}
 const line=(a,b,c,color,dash=false,width=3)=>{const ps=[];if(Math.abs(b)>EPS)for(const x of [0,mx]){const y=(c-a*x)/b;if(y>=-EPS&&y<=my+EPS)ps.push([x,y]);}if(Math.abs(a)>EPS)for(const y of [0,my]){const x=(c-b*y)/a;if(x>=-EPS&&x<=mx+EPS)ps.push([x,y]);}const p=Math8.unique(ps);return p.length>=2?`<line x1="${X(p[0][0])}" y1="${Y(p[0][1])}" x2="${X(p.at(-1)[0])}" y2="${Y(p.at(-1)[1])}" stroke="${color}" stroke-width="${width}" ${dash?'stroke-dasharray="8 5"':''}/>`:'';};
 g.cons.forEach((q,i)=>{svg+=line(q.a,q.b,q.c,colors[i%3]);});
 if(s.status==='optimal'&&!s.constant){svg+=line(g.cx,g.cy,s.value,'#a55c21',true,2);for(let i=0;i<verts.length;i++){const a=verts[i],b=verts[(i+1)%verts.length];if(s.best.includes(a)&&s.best.includes(b)&&verts.length>1)svg+=`<line x1="${X(a[0])}" y1="${Y(a[1])}" x2="${X(b[0])}" y2="${Y(b[1])}" stroke="#a55c21" stroke-width="6"/>`;}}
 svg+=`<path d="M${L} ${T}V${h-B}H${w-R}" fill="none" stroke="#293329" stroke-width="2"/>`;
 if(integer&&integer.points.length<=400)for(const p of integer.points)svg+=`<circle cx="${X(p[0])}" cy="${Y(p[1])}" r="2.8" fill="#536240" opacity=".65"/>`;
 for(const p of verts){const x=X(p[0]),y=Y(p[1]),best=s.best.includes(p);svg+=`<circle cx="${x}" cy="${y}" r="${best?7:5}" fill="${best?'#a55c21':'#293329'}"/>`;if(best)svg+=`<text x="${x}" y="${y+7}" text-anchor="middle" font-size="23" fill="#a55c21">★</text>`;if(labels)svg+=`<text x="${x+(p[0]>.75*mx?-10:9)}" y="${y-11}" text-anchor="${p[0]>.75*mx?'end':'start'}" font-size="14" fill="#293329">${esc(point(p))}</text>`;}
 if(integer)for(const p of integer.best){const x=X(p[0]),y=Y(p[1]);svg+=`<path d="M${x} ${y-9}L${x+9} ${y}L${x} ${y+9}L${x-9} ${y}Z" fill="#293329" stroke="white" stroke-width="1.5"/>`;}
 if(test&&test.every(Number.isFinite)&&test[0]>=0&&test[1]>=0&&test[0]<=mx&&test[1]<=my){const ok=Math8.feasible(test,g),x=X(test[0]),y=Y(test[1]);svg+=`<circle cx="${x}" cy="${y}" r="10" fill="none" stroke="${ok?'#17677a':'#943c2d'}" stroke-width="3"/><text x="${x+14}" y="${y+20}" font-size="15" fill="${ok?'#17677a':'#943c2d'}">P ${esc(point(test))}</text>`;}
 if(!s.bounded&&s.status!=='infeasible')svg+=`<text x="${w-R-8}" y="${T+22}" text-anchor="end" font-size="13" fill="#17677a">↗ Shading continues beyond this window</text>`;
 svg+=`<text x="${L+pw/2}" y="${h-18}" text-anchor="middle" font-size="16" fill="#293329">${esc(g.xlabel||'x')}</text><text x="18" y="${T+ph/2}" transform="rotate(-90 18 ${T+ph/2})" text-anchor="middle" font-size="16" fill="#293329">${esc(g.ylabel||'y')}</text>`;
 g.cons.forEach((q,i)=>{svg+=`<text x="${L+i*265}" y="${h-47}" font-size="13" fill="${colors[i%3]}">${i+1}. ${esc(equation(q))}</text>`;});target.innerHTML=svg+'</svg>';
}
function initAnswers(){
 const form=document.querySelector('[data-answer-store]');if(!form)return;
 const fields=[...form.querySelectorAll('[data-answer],textarea[data-save]')],key=form.dataset.answerStore,legacy=form.dataset.legacyStore,groups=[...form.querySelectorAll('[data-check-group]')],done=new Set();let storageOK=true;
 function numericCorrect(el){const v=Math8.number(el.value);return Number.isFinite(v)&&Math.abs(v-Number(el.dataset.answer))<=Number(el.dataset.tolerance||.001);}
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
function initGeometry(){
 if(!$('geomPreset'))return;
 const info={snacks:['type-A packs','type-B packs','packing slots','ingredient portions'],lab:['A quantity','B quantity','resource-1 units','resource-2 units'],workshop:['chairs per week','tables per week','wood units','assembly slots'],textbook:['product-A units','product-B units','resource-1 units','resource-2 units']};
 function current(){const b=Math8.models[$('geomPreset').value];return {...b,cons:b.cons.map((q,i)=>({...q,c:+$(i?'c2':'c1').value}))};}
 function draw(){const g=current(),s=Math8.solve(g),i=info[$('geomPreset').value],x=Math8.number($('testX').value),y=Math8.number($('testY').value),valid=[x,y].every(Number.isFinite);text('c1v',g.cons[0].c);text('c2v',g.cons[1].c);text('geomContext',`x = ${i[0]}; y = ${i[1]}. Current allowances: ${g.cons[0].c} ${i[2]} and ${g.cons[1].c} ${i[3]}.`);text('geomConstraints',constraints(g));text('geomCount',s.vertices.length);text('geomShape',s.vertices.length===1?'Single feasible point':s.vertices.length===2?'Feasible line segment':'Bounded polygon');plot('geomPlot',g,{test:valid?[x,y]:null,half:$('showHalf').checked,labels:$('showLabels').checked,title:'The intersection of the current resource limits'});
 table('geomVertices',['True feasible vertex','Binding boundaries'],s.vertices.map(p=>[point(p),Math8.constraints(g).map((q,j)=>near(q.a*p[0]+q.b*p[1],q.c)?j<g.cons.length?'Resource '+(j+1):j===g.cons.length?'x = 0':'y = 0':null).filter(Boolean).join('; ')]));
 if(!valid){text('geomTest','Enter two finite coordinates to test a plan. A blank value is not zero.');$('geomChecks').replaceChildren();return;}
 const ok=Math8.feasible([x,y],g);text('geomTest',`Plan P = ${point([x,y])} is ${ok?'feasible: every condition passes.':'infeasible: at least one condition fails.'}`);table('geomChecks',['Condition','Calculated left side','Passes?'],Math8.constraints(g).map(q=>{const value=q.a*x+q.b*y,ok=q.s==='le'?value<=q.c+EPS:value>=q.c-EPS;return [equation(q),fmt(value),ok?'yes':'no'];}));
 }
 function setup(){const g=Math8.models[$('geomPreset').value];for(let i=0;i<2;i++){const el=$(i?'c2':'c1');el.min=0;el.max=Math.max(20,g.cons[i].c*2.5);el.step=$('geomPreset').value==='textbook'?5:1;el.value=g.cons[i].c;}$('testX').value=$('geomPreset').value==='snacks'?4:0;$('testY').value=$('geomPreset').value==='snacks'?4:0;draw();}
 $('geomPreset').addEventListener('change',setup);for(const id of ['c1','c2','showHalf','showLabels','testX','testY'])$(id).addEventListener('input',draw);setup();
}
function resultText(g,s){
 if(s.status==='infeasible')return 'No plan satisfies every constraint, so there is no feasible plan to optimize.';
 if(s.status==='unbounded')return `No finite ${g.dir==='max'?'maximum':'minimum'} exists. A feasible plan can move in direction ${point(s.improving[0])} repeatedly and keep improving the objective. The finite corner table alone does not bound this score.`;
 if(s.constant)return 'Both coefficients are zero. Every feasible point has objective value 0; the best set is the entire feasible region.';
 let message=`The ${g.dir==='max'?'maximum':'minimum'} value is ${fmt(s.value)}, attained at ${s.best.map(point).join(' and ')}.`;
 if(s.best.length>1)message+=' The segment between tied best vertices is optimal too.';
 if(s.flatRays.length)message+=' There are also unbounded feasible directions along which this best score stays unchanged.';
 return message;
}
function initOptimizer(){
 if(!$('lpPreset'))return;
 function draw(){
  const b=Math8.models[$('lpPreset').value],cx=Math8.number($('cx').value),cy=Math8.number($('cy').value);text('lpContext','Starting scenario: '+b.context+' The coefficient and direction fields define the current objective.');
  if(![cx,cy].every(x=>Number.isFinite(x)&&x>=0&&x<=100)){text('lpError','Enter a coefficient from 0 to 100 in each field. Blank values are not zero.');for(const id of ['lpPlot','lpTable','wholeTable'])$(id).replaceChildren();for(const id of ['lpBest','lpPlan'])text(id,'—');text('lpStatus','Enter valid coefficients');text('lpConclusion','');text('wholeSummary','');$('wholeOnly').disabled=true;return;}
  text('lpError','');const g={...b,cx,cy,dir:$('lpDirection').value},s=Math8.solve(g),whole=Math8.whole(g,2000),available=whole.status==='optimal';$('wholeOnly').disabled=!available;if(!available)$('wholeOnly').checked=false;const show=available&&$('wholeOnly').checked;
  text('lpConstraints',constraints(g));text('lpObjective',`${g.dir==='max'?'Maximize':'Minimize'} f = ${expression(cx,cy)}.`);plot('lpPlot',g,{solution:s,integer:show?whole:null,title:'Feasible region and current objective'});
  text('lpStatus',s.status==='infeasible'?'No feasible plans':s.status==='unbounded'?'Unbounded score':s.best.length>1||s.flatRays.length||s.constant?'Tied best plans':'Finite optimum');text('lpBest',s.value===null?'—':fmt(s.value));text('lpPlan',s.best.map(point).join(' and ')||'—');text('lpConclusion',resultText(g,s));
  table('lpTable',['Feasible vertex','Objective value','Continuous status'],s.vertices.map(p=>[point(p),fmt(cx*p[0]+cy*p[1]),s.best.includes(p)?'best vertex':'']));
  text('wholeNote',available?`This model has ${whole.points.length} feasible whole-number plans within its bounded region. Toggle the comparison to enumerate them.`:s.status==='infeasible'?'There are no feasible plans in this model.':'This comparison is limited to bounded models whose enclosing integer grid has at most 2,000 points. Choose the small fractional-versus-whole preset to investigate rounding.');
  if(show){text('wholeSummary',`Continuous best: ${fmt(s.value)}. Best whole-number value: ${fmt(whole.value)} at ${whole.best.map(point).join(' and ')}. Integer choices are tested directly, not rounded from the continuous answer.`);table('wholeTable',['Whole-number plan','Objective value','Status'],whole.points.map(p=>({p,value:cx*p[0]+cy*p[1]})).sort((a,b)=>(g.dir==='max'?-1:1)*(a.value-b.value)||a.p[0]-b.p[0]).map(r=>[point(r.p),fmt(r.value),whole.best.includes(r.p)?'best whole plan':'']));}else{text('wholeSummary','');$('wholeTable').replaceChildren();}
 }
 function setup(){const g=Math8.models[$('lpPreset').value];$('cx').value=g.cx;$('cy').value=g.cy;$('lpDirection').value=g.dir;$('wholeOnly').checked=$('lpPreset').value==='integer';draw();}
 $('lpPreset').addEventListener('change',setup);for(const id of ['cx','cy'])$(id).addEventListener('input',draw);for(const id of ['lpDirection','wholeOnly'])$(id).addEventListener('change',draw);setup();
}
function initWorkshop(){
 if(!$('workshopScenario'))return;
 function draw(){const choice=$('workshopScenario').value,b=Math8.models.workshop,g={...b,cons:b.cons.map(q=>({...q}))};if(choice==='wood')g.cons[0].c=48;if(choice==='slots')g.cons[1].c=18;if(choice==='values'){g.cx=50;g.cy=10;}const s=Math8.solve(g);text('workshopModel',constraints(g)+` Maximize contribution P = ${expression(g.cx,g.cy)}.`);plot('workshopPlot',g,{solution:s,title:'Current workshop production scenario'});text('workshopSummary',`Best plan: ${s.best.map(p=>`${fmt(p[0])} chairs and ${fmt(p[1])} tables`).join(' or ')}. Contribution: $${fmt(s.value)}. This continuous best plan has whole coordinates and is also best among feasible whole-number plans.`);table('workshopTable',['Feasible corner','Wood units used','Assembly slots used','Contribution dollars','Status'],s.vertices.map(p=>[point(p),fmt(2*p[0]+4*p[1]),fmt(p[0]+p[1]),fmt(g.cx*p[0]+g.cy*p[1]),s.best.includes(p)?'best':'']));}
 $('workshopScenario').addEventListener('change',draw);draw();
}
function mixturePlot(id,points,p){
 const labels=['A','B','C'],W=850,H=600,L=100,T=35,B=70,scale=(H-T-B)/8,X=x=>L+x*scale,Y=y=>H-B-y*scale,plotW=10*scale;let s=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" role="img" aria-labelledby="${id}-title ${id}-desc"><title id="${id}-title">Weighted point in its convex hull</title><desc id="${id}-desc">${points.map((q,i)=>labels[i]+' '+point(q)).join('; ')}. Weighted point P ${point(p)}. Both coordinate axes share the same unit scale.</desc><rect width="850" height="600" fill="white"/>`;
 for(let k=0;k<=10;k++)s+=`<path d="M${X(k)} ${T}V${H-B}" stroke="#d8ddcd"/><text x="${X(k)}" y="${H-B+23}" text-anchor="middle" font-size="13">${k}</text>`;for(let k=0;k<=8;k++)s+=`<path d="M${L} ${Y(k)}H${L+plotW}" stroke="#d8ddcd"/><text x="${L-15}" y="${Y(k)+5}" text-anchor="end" font-size="13">${k}</text>`;
 s+=points.length===2?`<line x1="${X(points[0][0])}" y1="${Y(points[0][1])}" x2="${X(points[1][0])}" y2="${Y(points[1][1])}" stroke="#17677a" stroke-width="3"/>`:`<polygon points="${points.map(q=>X(q[0])+','+Y(q[1])).join(' ')}" fill="#eaf0e2" stroke="#17677a" stroke-width="2.5"/>`;
 points.forEach((q,i)=>s+=`<circle cx="${X(q[0])}" cy="${Y(q[1])}" r="6" fill="#536240"/><text x="${X(q[0])+8}" y="${Y(q[1])-14}" font-size="16" fill="#293329">${labels[i]} ${esc(point(q))}</text>`);s+=`<circle cx="${X(p[0])}" cy="${Y(p[1])}" r="8" fill="#a55c21"/><text x="${X(p[0])+10}" y="${Y(p[1])+26}" font-size="17" fill="#a55c21">P ${esc(point(p))}</text><path d="M${L} ${T}V${H-B}H${L+plotW}" fill="none" stroke="#293329" stroke-width="2"/><text x="${L+plotW/2}" y="${H-18}" text-anchor="middle" font-size="16">Coordinate 1</text><text x="25" y="${T+(H-T-B)/2}" transform="rotate(-90 25 ${T+(H-T-B)/2})" text-anchor="middle" font-size="16">Coordinate 2</text></svg>`;$(id).innerHTML=s;
}
function initMixtures(){
 if(!$('mixWeight'))return;const points=[[2,1],[8,5],[2,7]];
 function pair(){const w=+$('mixWeight').value,r=Math8.mix(points.slice(0,2),[w,1-w]);text('mixWeightValue',w.toFixed(2));text('mixSummary',`Weights: A ${w.toFixed(2)}, B ${(1-w).toFixed(2)}. Weighted point P = ${point(r.point)}.`);mixturePlot('mixPlot',points.slice(0,2),r.point);table('mixTable',['Input','Weight','Coordinate 1 contribution','Coordinate 2 contribution'],points.slice(0,2).map((p,i)=>[['A','B'][i],fmt(r.weights[i]),fmt(r.weights[i])+' × '+p[0]+' = '+fmt(r.weights[i]*p[0]),fmt(r.weights[i])+' × '+p[1]+' = '+fmt(r.weights[i]*p[1])]).concat([['Total','1',fmt(r.point[0]),fmt(r.point[1])]]));}
 function triple(){try{const amounts=['amountA','amountB','amountC'].map(id=>Math8.number($(id).value)),r=Math8.mix(points,amounts);text('triangleError','');text('triangleSummary',`Total amount ${fmt(r.total)}. Normalized weights ${r.weights.map(x=>fmt(x)).join(', ')} (rounded for display). P = ${point(r.point)}; calculations use unrounded weights.`);mixturePlot('trianglePlot',points,r.point);table('triangleTable',['Input vector','Amount','Normalized weight','Coordinate 1 contribution','Coordinate 2 contribution'],points.map((p,i)=>[['A','B','C'][i]+' '+point(p),fmt(amounts[i]),fmt(r.weights[i]),fmt(r.weights[i]*p[0]),fmt(r.weights[i]*p[1])]).concat([['Total',fmt(r.total),'1',fmt(r.point[0]),fmt(r.point[1])]]));}catch(e){text('triangleError',e.message);text('triangleSummary','No convex combination is defined for these inputs.');$('trianglePlot').replaceChildren();$('triangleTable').replaceChildren();}}
 $('mixWeight').addEventListener('input',pair);for(const id of ['amountA','amountB','amountC'])$(id).addEventListener('input',triple);pair();triple();
}
function init(){initAnswers();initGeometry();initOptimizer();initWorkshop();initMixtures();document.querySelectorAll('[data-print-page]').forEach(b=>b.addEventListener('click',()=>window.print()));window.addEventListener('beforeprint',preparePrint);window.addEventListener('afterprint',()=>document.querySelectorAll('.print-answer').forEach(e=>e.remove()));}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})(typeof globalThis!=='undefined'?globalThis:this);
