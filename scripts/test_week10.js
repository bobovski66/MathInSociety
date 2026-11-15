/* Week 10: mathematical fixtures and consistency tests. */
"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const M=require("../assets/week10/week10.js");
const ROOT=path.resolve(__dirname,"..");
function close(a,b,e=1e-10){assert.ok(Math.abs(a-b)<e,String(a)+" != "+String(b))}
function read(file){return fs.readFileSync(path.join(ROOT,file),"utf8")}
for(const [start,steps,peak] of [[1,0,1],[3,7,16],[6,8,16],[7,16,52],[9,19,52],[10,6,16],[27,111,9232]]){
 const route=M.collatz(start);assert.equal(route.steps,steps);assert.equal(route.peak,peak);assert.equal(route.values.at(-1),1);
 assert.equal(route.reachedOne,true);assert.equal(route.values.length,steps+1);
 for(let i=1;i<route.values.length;i++){const n=route.values[i-1];assert.equal(route.values[i],n%2===0?n/2:3*n+1)}
}
assert.equal(M.collatz(27,5).reachedOne,false);
for(const n of [0,-1,1.2,NaN,100001])assert.throws(()=>M.collatz(n));
assert.throws(()=>M.collatz(7,0));assert.throws(()=>M.logistic(4.1,.2,5));
assert.throws(()=>M.logistic(3.9,-.01,5));assert.throws(()=>M.sierpinski(8));
let first=M.logistic(2.8,.2,2);close(first[1],.448);close(first[2],.6924288);
let a=M.logistic(3.9,.4,45),b=M.logistic(3.9,.4001,45);
close(a[1],.936);close(b[1],.936077961);
assert.equal(a.findIndex((v,i)=>Math.abs(v-b[i])>.1),14);
assert.ok(Math.abs(a[1]-b[1])<Math.abs(a[0]-b[0]));
const fixed=M.logistic(2.8,.2,200),cycle=M.logistic(3.2,.2,200);
close(fixed.at(-1),fixed.at(-2),1e-8);close(cycle.at(-1),cycle.at(-3),1e-8);
assert.ok(Math.abs(cycle.at(-1)-cycle.at(-2))>.1);
assert.deepEqual(M.logistic(4,.5,4),[.5,1,0,0,0]);
for(let n=0;n<=6;n++){const x=M.sierpinski(n);assert.equal(x.count,3**n);assert.equal(x.triangles.length,3**n);close(x.areaFraction,(.75)**n);close(x.sideFraction,(.5)**n);}
close(Math.log(3)/Math.log(2),1.584962500721156);
assert.deepEqual(M.searchTable(10),{possibilities:1024,balancedQuestions:10,sequentialWorst:1024});
const reading=read("readings/week10_reading.html");
for(const t of ["Collatz","Computational complexity","Sensitive dependence","Sierpiński","0.6924288","Math107_Chapter_10.pdf"])assert.ok(reading.includes(t),t);
const explorer=read("demos/fractal_recursion.html");
for(const id of ["ccStart","ccGraph","ccTable","clR","clGraph","clDiffGraph","cfGraph","cfPieces"])assert.ok(explorer.includes('id="'+id+'"'),id);
const lab=read("labs/week10_lab.html");assert.equal((lab.match(/data-check-group=/g)||[]).length,4);assert.ok((lab.match(/data-save/g)||[]).length>=18);
for(const term of ['data-answer="6"','data-answer="52"','data-answer="0.6924288"','data-answer="27"','data-answer="81"'])assert.ok(lab.includes(term),term);
const app=read("applications/week10_application.html");
for(const term of ['data-answer="0.936"','data-answer="0.936077961"','data-answer="0.000077961"'])assert.ok(app.includes(term),term);
const discussion=read("discussions/week10_discussion.html");
for(const term of ["Claim A","Claim B","Claim C","stage 5","initial post"])assert.ok(discussion.includes(term),term);
const index=read("index.html"),matched=index.match(/const ASSESSMENTS = (\{[\s\S]*?\});const STORAGE_KEY/);
assert.ok(matched,"Missing assessment JSON");
const assess=JSON.parse(matched[1]),quiz=assess.week10.questions;
assert.equal(quiz.length,12);assert.equal(new Set(quiz.map(x=>x.id)).size,12);
for(const q of quiz){if(q.type==="mc")assert.ok(q.options.includes(q.answer),q.id);if(q.type==="num")assert.ok(Number.isFinite(q.answer),q.id)}
assert.equal(assess.final.questions.length,18);
const byId=Object.fromEntries(quiz.map(q=>[q.id,q]));
assert.equal(byId.w10ccf1.answer,6);assert.equal(byId.w10ccf2.answer,52);
assert.equal(byId.w10ccf4.answer,256);close(byId.w10ccf6.answer,.448);
close(byId.w10ccf7.answer,.6924288);assert.equal(byId.w10ccf9.answer,27);
close(byId.w10ccf10.answer,.5625);
console.log("PASS: Collatz stopping-time fixtures, logistic stability/sensitivity, Sierpinski scaling, all six pages, and Week 10 assessments.");
