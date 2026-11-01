'use strict';
// Interactive candle-business model, used only by the Week 7 explorer.
(function runBusinessExplorer(){
  'use strict';
  const $ = id => document.getElementById(id);
  if (!$('businessPlot') || !window.Math7) return;

  const fmt = number => Number(number.toPrecision(10)).toLocaleString('en-US',{maximumFractionDigits:2});
  const money = number => (number < 0 ? '−' : '')+'$'+Math.abs(number).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});
  const show = (id,value) => { const node=$(id); if(node) node.textContent=value; };
  const maxQ=100;

  function graph(model,q){
    const width=920,height=530,left=104,right=32,top=58,bottom=72;
    const yMax=Math.max(1,model.values(maxQ).C,model.values(maxQ).R)*1.12;
    const X=x=>left+(width-left-right)*x/maxQ;
    const Y=y=>height-bottom-(height-top-bottom)*y/yMax;
    const selected=model.values(q);
    const lines=[
      ['Cost','#a55c21',model.F,model.values(maxQ).C],
      ['Revenue','#17677a',0,model.values(maxQ).R]
    ];
    let svg=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="businessGraphTitle businessGraphDesc">
<title id="businessGraphTitle">Monthly cost and revenue</title>
<desc id="businessGraphDesc">Cost increases from ${money(model.F)} by ${money(model.v)} per candle. Revenue increases by ${money(model.p)} per candle. At ${q} candles, cost is ${money(selected.C)}, revenue is ${money(selected.R)}, and profit is ${money(selected.P)}.</desc>
<rect width="${width}" height="${height}" fill="white"/>`;
    for(let i=0;i<=5;i++){
      const x=maxQ*i/5;
      const y=yMax*i/5;
      svg+=`<path d="M ${X(x)} ${top} V ${height-bottom} M ${left} ${Y(y)} H ${width-right}" fill="none" stroke="#e0e3d9" stroke-width="1"/>
<text x="${X(x)}" y="${height-bottom+28}" text-anchor="middle" font-size="14" fill="#52604f">${fmt(x)}</text>
<text x="${left-12}" y="${Y(y)+5}" text-anchor="end" font-size="14" fill="#52604f">$${fmt(y)}</text>`;
    }
    lines.forEach(([name,color,yStart,yEnd])=>{
      svg+=`<line x1="${X(0)}" y1="${Y(yStart)}" x2="${X(maxQ)}" y2="${Y(yEnd)}" stroke="${color}" stroke-width="4"/>`;
    });
    const breakEven=model.threshold;
    if(breakEven.kind==='unique' && breakEven.q>=0 && breakEven.q<=maxQ){
      const spot=model.values(breakEven.q);
      svg+=`<circle cx="${X(breakEven.q)}" cy="${Y(spot.R)}" r="6" fill="#293329" stroke="white" stroke-width="2"/>`;
    }
    svg+=`<path d="M ${X(q)} ${Y(0)} V ${Y(Math.max(selected.C,selected.R))}" stroke="#7f877c" stroke-dasharray="5 5" stroke-width="2"/>
<path d="M ${X(q)} ${Y(selected.C)} V ${Y(selected.R)}" stroke="#c7a345" stroke-width="7"/>
<circle cx="${X(q)}" cy="${Y(selected.C)}" r="6" fill="#a55c21" stroke="#fff" stroke-width="2"/>
<circle cx="${X(q)}" cy="${Y(selected.R)}" r="6" fill="#17677a" stroke="#fff" stroke-width="2"/>
<path d="M ${left} ${top} V ${height-bottom} H ${width-right}" fill="none" stroke="#293329" stroke-width="2"/>
<text x="${left+6}" y="30" font-size="17" fill="#a55c21">Cost</text>
<text x="${left+95}" y="30" font-size="17" fill="#17677a">Revenue</text>
<text x="${(left+width-right)/2}" y="${height-19}" text-anchor="middle" font-size="16" fill="#293329">Candles sold, q</text>
<text x="25" y="${(top+height-bottom)/2}" transform="rotate(-90 25 ${(top+height-bottom)/2})" text-anchor="middle" font-size="16" fill="#293329">Dollars per month</text>
</svg>`;
    $('businessPlot').innerHTML=svg;
  }

  function draw(){
    try{
      const F=Number($('F').value),v=Number($('v').value),p=Number($('p').value),q=Number($('q').value);
      if(![F,v,p,q].every(Number.isFinite)) throw Error('Choose valid slider values.');
      const model=window.Math7.linear(F,v,p);
      const value=model.values(q);
      show('FValue',money(F));
      show('vValue',money(v));
      show('pValue',money(p));
      show('qValue',fmt(q));
      show('businessCostFormula',`C(q) = ${fmt(F)} + ${fmt(v)}q`);
      show('businessRevenueFormula',`R(q) = ${fmt(p)}q`);
      show('businessProfitFormula',`P(q) = ${fmt(model.m)}q − ${fmt(F)}`);
      show('cost',money(value.C));
      show('rev',money(value.R));
      show('profit',money(value.P));
      const zero=Math.abs(value.P)<1e-9;
      const outcome=zero?'breaks even exactly':value.P>0?'earns '+money(value.P)+' in profit':'has a loss of '+money(-value.P);
      show('businessState',`At ${fmt(q)} candles sold, the business ${outcome}.`);
      show('businessError','');
      graph(model,q);
    }catch(error){show('businessError',error.message);}
  }

  ['F','v','p','q'].forEach(id=>$(id).addEventListener('input',draw));
  draw();
})();
