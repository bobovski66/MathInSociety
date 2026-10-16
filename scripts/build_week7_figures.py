"""Reproducible, exact vector charts for Week 7's constructed business models."""
from pathlib import Path
from io import BytesIO
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
OUT=Path(__file__).resolve().parents[1]/'assets/week7';OUT.mkdir(exist_ok=True)
INK='#293329';OLIVE='#536240';TEAL='#17677a';RUST='#a55c21';GOLD='#b18a22';LINE='#d8ddcd';RED='#943c2d'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12.5,'text.parse_math':False,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK,'svg.fonttype':'none','svg.hashsalt':'math107-week7','pdf.fonttype':42,'savefig.facecolor':'white'})
def finish(fig,name):
 for ext in ['svg','pdf']:
  b=BytesIO();fig.savefig(b,format=ext,bbox_inches='tight',pad_inches=.2,metadata={'Date':None} if ext=='svg' else {'CreationDate':None,'ModDate':None});p=OUT/(name+'.'+ext);t=p.with_suffix('.tmp')
  data=b.getvalue()
  if ext=='svg':data=('\n'.join(line.rstrip() for line in data.decode().splitlines())+'\n').encode()
  with t.open('wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
  os.replace(t,p)
 plt.close(fig);print(name)
def axis(ax,xlabel='Candles made and sold this month, q',ylabel='Dollars for the month'):
 ax.set_xlabel(xlabel,labelpad=9);ax.set_ylabel(ylabel,labelpad=8);ax.grid(color=LINE,lw=.7);ax.set_axisbelow(True)
 for side in ['top','right']:ax.spines[side].set_visible(False)
 for side in ['bottom','left']:ax.spines[side].set_color(OLIVE)
 ax.yaxis.set_major_formatter(FuncFormatter(lambda y,_:f'{y:,.0f}'));ax.tick_params(labelsize=11)
def note(ax,x,y,text,offset=(10,12),color=INK):
 ax.scatter([x],[y],s=35,color=color,zorder=5);ax.annotate(text,(x,y),xytext=offset,textcoords='offset points',fontsize=12,color=color,arrowprops={'arrowstyle':'-','color':color,'lw':.7})
def legend(ax,**kw):ax.legend(frameon=True,facecolor='white',edgecolor=LINE,fontsize=11,**kw)

fig,ax=plt.subplots(figsize=(9.1,4.9),layout='constrained');qs=np.array([0,20,40,60]);ax.bar(qs,180,width=11,color=OLIVE,label='Fixed cost: $180');ax.bar(qs,4*qs,bottom=180,width=11,color='#a8c6cd',label='Variable cost: $4 × q')
for q in qs:ax.text(q,180+4*q+10,f'${180+4*q}',ha='center',fontsize=13)
axis(ax);ax.set_ylim(0,570);ax.set_xticks(qs);ax.set_title('Total cost = fixed expense + cost of the items',loc='left',fontweight='bold',pad=13);legend(ax,loc='upper left');finish(fig,'cost-components')

fig,ax=plt.subplots(figsize=(9.1,5.25),layout='constrained');q=np.linspace(0,65,201);axis(ax);ax.plot(q,180+4*q,color=RUST,lw=2.7,label='Cost C(q) = 180 + 4q');ax.plot(q,10*q,color=TEAL,lw=2.7,label='Revenue R(q) = 10q');ax.fill_between(q,180+4*q,10*q,where=q<=30,color=RED,alpha=.09);ax.fill_between(q,180+4*q,10*q,where=q>=30,color=OLIVE,alpha=.11);ax.vlines(50,380,500,color=GOLD,lw=5);ax.vlines(50,0,380,color=OLIVE,ls=':',lw=1);note(ax,30,300,'Same cost and revenue\n(30, $300)',(-123,40));ax.annotate('Profit at q=50:\n$500 − $380 = $120',(50,440),xytext=(39,15),textcoords='offset points',fontsize=12,color=OLIVE,arrowprops={'arrowstyle':'-','color':OLIVE});ax.set_xlim(0,66);ax.set_ylim(0,720);legend(ax,loc='upper left');ax.set_title('Read both heights above the same quantity',loc='left',fontweight='bold',pad=13);finish(fig,'cost-revenue-gap')

fig,ax=plt.subplots(figsize=(9.1,4.8),layout='constrained');axis(ax,ylabel='Profit in dollars');q=np.linspace(0,65,150);ax.axhline(0,color=INK,lw=1.2);ax.plot(q,6*q-180,color=OLIVE,lw=3);ax.fill_between(q,6*q-180,0,where=q<=30,color=RED,alpha=.1);ax.fill_between(q,6*q-180,0,where=q>=30,color=OLIVE,alpha=.12);note(ax,0,-180,'P(0) = −$180',(18,10));note(ax,30,0,'Break-even (30, $0)',(-115,22));note(ax,50,120,'P(50) = $120',(-45,25));ax.text(8,-50,'Loss',color=RED);ax.text(45,35,'Positive profit',color=OLIVE);ax.set_xlim(-1,66);ax.set_ylim(-220,250);ax.set_title('Plot the difference directly: P(q) = 6q − 180',loc='left',fontweight='bold',pad=13);finish(fig,'profit-line')

fig,ax=plt.subplots(figsize=(9.1,4.8),layout='constrained');axis(ax,xlabel='Cards made and sold at the fair, q',ylabel='Profit in dollars');q=np.linspace(8,13,100);ax.axhline(0,color=INK,lw=1.3);ax.plot(q,4.5*q-48,color=OLIVE,lw=2.5);ax.scatter(range(8,14),[4.5*x-48 for x in range(8,14)],s=55,color=OLIVE,zorder=4);note(ax,10,-3,'10 cards: −$3',(-105,-20));note(ax,11,1.5,'11 cards: $1.50',(25,18));ax.axvline(48/4.5,color=RUST,ls='--',lw=1.3);ax.annotate('Exact crossing: 10⅔ cards',(48/4.5,0),xytext=(-80,75),textcoords='offset points',fontsize=12,color=RUST,arrowprops={'arrowstyle':'->','color':RUST});ax.set_xlim(7.8,13.3);ax.set_ylim(-15,15);ax.set_xticks(range(8,14));ax.set_title('Whole-item choices do not move the exact crossing',loc='left',fontweight='bold',pad=13);finish(fig,'whole-item-threshold')

fig,ax=plt.subplots(figsize=(9.1,4.6),layout='constrained');axis(ax,ylabel='Total profit in dollars');ax.plot([20,21,22],[-60,-54,-48],color=OLIVE,lw=2.5);ax.scatter([20,21,22],[-60,-54,-48],color=OLIVE,s=65,zorder=4)
for x,y in [(20,-60),(21,-54),(22,-48)]:ax.annotate(f'({x}, −${abs(y)})',(x,y),xytext=(0,14),textcoords='offset points',ha='center',fontsize=12)
for x,y in [(20,-60),(21,-54)]:ax.plot([x,x+1,x+1],[y,y,y+6],ls='--',color=RUST,lw=1.4);ax.text(x+.5,y-1.8,'+1 candle',ha='center',fontsize=11);ax.annotate('+$6',(x+1,y+3),xytext=(10,0),textcoords='offset points',color=RUST,fontsize=12)
ax.set_xlim(19.65,22.6);ax.set_ylim(-66,-43);ax.set_xticks([20,21,22]);ax.set_title('A positive change can make a loss smaller',loc='left',fontweight='bold',pad=13);finish(fig,'marginal-steps')

fig,axes=plt.subplots(1,2,figsize=(10.5,4.65),layout='constrained')
for ax,cap in zip(axes,[25,60]):
 axis(ax,xlabel='Candles, q',ylabel='Profit ($)');q=np.linspace(0,65,160);ax.axhline(0,color=INK,lw=1);ax.plot(q,6*q-180,color=OLIVE,lw=2.5);ax.axvspan(cap,65,color='#e9e6da',alpha=.6);ax.axvline(cap,color=RUST,ls='--');note(ax,cap,6*cap-180,f'Best allowed:\nq={cap}, P=${6*cap-180}',(-125,-10) if cap==60 else (-65,40));ax.set_xlim(0,65);ax.set_ylim(-205,235);ax.set_title(f'Capacity = {cap} candles',loc='left',fontweight='bold',pad=12)
finish(fig,'capacity-and-best')

fig,ax=plt.subplots(figsize=(9.1,5.0),layout='constrained');axis(ax,xlabel='Items made and sold per month, q',ylabel='Monthly profit ($)');q=np.linspace(0,155,150);ax.axhline(0,color=INK,lw=1);ax.plot(q,12*q-800,color=TEAL,lw=2.6,label='A: P(q) = 12q − 800');ax.plot(q,8*q-400,color=RUST,lw=2.6,label='B: P(q) = 8q − 400');note(ax,100,400,'Equal profit:\n100 items, $400',(-105,55));ax.vlines(100,0,400,ls=':',color=OLIVE);ax.set_xlim(0,155);ax.set_ylim(-900,1250);legend(ax,loc='upper left');ax.set_title('A smaller fixed expense versus a larger margin',loc='left',fontweight='bold',pad=13);finish(fig,'business-crossover')

fig,ax=plt.subplots(figsize=(9.1,4.9),layout='constrained');axis(ax,ylabel='Monthly profit ($)');q=np.linspace(0,65,150);ax.axhline(0,color=INK,lw=1);ax.plot(q,6*q-180,color=OLIVE,lw=2.7,label='Original: 6q − 180');ax.plot(q,6*q-240,color=RUST,lw=2.3,label='Fixed cost +$60: 6q − 240');ax.plot(q,8*q-180,color=TEAL,lw=2.3,label='Price +$2: 8q − 180');ax.set_xlim(0,65);ax.set_ylim(-265,400);ax.set_title('Change one parameter while keeping quantity fixed',loc='left',fontweight='bold',pad=13);legend(ax,loc='upper left');finish(fig,'parameter-effects')

fig,axes=plt.subplots(1,2,figsize=(10.5,4.7),layout='constrained')
for ax,values,title,qs in zip(axes,[[0,160],[150,70]],['Hold both sales counts at 40','Use invented demand estimates'],[[40,40],[70,30]]):
 axis(ax,xlabel='Selling price per bar',ylabel='Profit at that sales count ($)');bars=ax.bar([0,1],values,width=.55,color=[OLIVE,TEAL]);ax.axhline(0,color=INK,lw=1);ax.set_xticks([0,1],['$8 price','$12 price']);ax.set_ylim(-25,235);ax.set_title(title,fontsize=14,loc='left',fontweight='bold',pad=12)
 for i,(val,qty) in enumerate(zip(values,qs)):ax.text(i,val+10,f'${val}\n{qty} sold',ha='center',fontsize=12)
finish(fig,'price-and-demand')

fig,ax=plt.subplots(figsize=(9.1,5.1),layout='constrained');axis(ax,xlabel='Tutoring hours delivered and billed per week, q',ylabel='Weekly dollars');q=np.linspace(0,20,160);ax.plot(q,200+5*q,color=RUST,lw=2.7,label='Cost C(q) = 200 + 5q');ax.plot(q,25*q,color=TEAL,lw=2.7,label='Revenue R(q) = 25q');note(ax,10,250,'Break-even:\n10 hours, $250',(-140,40));ax.vlines([6,14],[150,270],[230,350],color=GOLD,lw=4);ax.set_xlim(0,21);ax.set_ylim(0,570);legend(ax,loc='upper left');ax.set_title('At 6 hours: loss $80. At 14 hours: profit $80.',loc='left',fontweight='bold',pad=13);finish(fig,'tutoring-graph')

fig,ax=plt.subplots(figsize=(9.1,4.7),layout='constrained');axis(ax,xlabel='Meals prepared and sold during the festival, q',ylabel='Profit for the event ($)');qs=[28,40,55,80];vals=[-72,0,90,240];ax.axhline(0,color=INK,lw=1.3);ax.bar([0,1,2,3],vals,width=.6,color=[RED,OLIVE,OLIVE,TEAL]);ax.set_xticks([0,1,2,3],list(map(str,qs)));ax.set_ylim(-130,310)
for i,val in enumerate(vals):ax.text(i,val+(12 if val>=0 else -16),('−' if val<0 else '')+f'${abs(val)}',ha='center',va='bottom' if val>=0 else 'top',fontsize=13)
ax.set_title('Same model, different quantities: P(q) = 6q − 240',loc='left',fontweight='bold',pad=13);finish(fig,'food-stand-profit')

fig,ax=plt.subplots(figsize=(9.1,4.9),layout='constrained');axis(ax,xlabel='Completed paid sessions per month, q',ylabel='Monthly profit ($)');q=np.linspace(0,5500,150);ax.axhline(0,color=INK,lw=1.2);ax.plot(q,2*q-6000,color=OLIVE,lw=2.8);note(ax,1000,-4000,'1,000 sessions:\n−$4,000',(-40,30));note(ax,3000,0,'Break-even:\n3,000 sessions',(-120,35));note(ax,5000,4000,'5,000 sessions:\n$4,000',(-145,-15));ax.set_xlim(0,5600);ax.set_ylim(-6500,6000);ax.set_title('A constructed AI-service model: P(q) = 2q − 6,000',loc='left',fontweight='bold',pad=13);finish(fig,'ai-service-profit')
os.sync()
