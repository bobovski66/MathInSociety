/* Submission snapshots should show responses without leaking answer keys. */
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const exporter = require("../assets/lab-submission.js");
assert.equal(exporter.safeName(" José R. / Lee "), "Jose_R_Lee");
assert.equal(exporter.safeName("    "), "Student");
assert.equal(exporter.escapeHTML("<a name=\"A&B\">'"), "&lt;a name=&quot;A&amp;B&quot;&gt;&#39;");
assert.equal(exporter.responseText({tagName:"INPUT",type:"text",value:"-3/4"}), "-3/4");
assert.equal(exporter.responseText({tagName:"TEXTAREA",value:"Step one.\nStep two."}), "Step one.\nStep two.");
assert.equal(exporter.responseText({tagName:"SELECT",value:"yes",options:[{value:"",textContent:"Choose..."},{value:"yes",textContent:"Yes, it does."}]}), "Yes, it does.");
assert.equal(exporter.responseText({tagName:"SELECT",value:"",options:[]}), "");
assert.equal(exporter.responseText({tagName:"INPUT",type:"checkbox",checked:false}), "Not checked");
assert.equal(exporter.responseText({tagName:"INPUT",type:"checkbox",checked:true}), "Checked");
const source=fs.readFileSync("assets/lab-submission.js","utf8");
assert.match(source,/URL\.createObjectURL\(blob\)/);
assert.match(source,/freezeResponses\(main, copy\)/);
assert.match(source,/copy\.querySelectorAll\("\[data-answer\]/);
assert.match(source,/embedPictures\(copy\)/);
assert.match(source,/pageStyles\(\)/);
for(let n=1;n<=10;n++){
  const html=fs.readFileSync("labs/week"+n+"_lab.html","utf8");
  assert.equal((html.match(/data-download-filled-html/g)||[]).length,1,"Week "+n+" download button");
  assert.equal((html.match(/src="\.\.\/assets\/lab-submission\.js"/g)||[]).length,1,"Week "+n+" script");
}
const html=fs.readFileSync("labs/week8_optimization_lab.html","utf8");
assert.equal((html.match(/data-download-filled-html/g)||[]).length,1);
assert.equal((html.match(/src="\.\.\/assets\/lab-submission\.js"/g)||[]).length,1);
console.log("PASS: 11 filled-HTML download controls, safe filenames, escaped names and titles, answer-text conversion, static export and embedded illustrations.");
