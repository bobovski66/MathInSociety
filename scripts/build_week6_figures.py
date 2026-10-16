"""Reproducible, exact vector charts for Week 6's constructed business models."""
from decimal import Decimal,ROUND_HALF_UP
from matplotlib.patches import Rectangle
from pathlib import Path
from io import BytesIO
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
OUT=Path(__file__).resolve().parents[1]/'assets/week6';OUT.mkdir(exist_ok=True)
INK='#293329';OLIVE='#536240';TEAL='#17677a';RUST='#a55c21';GOLD='#b18a22';LINE='#d8ddcd';RED='#943c2d'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':14,'axes.titlesize':14,'text.parse_math':False,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK,'svg.fonttype':'none','svg.hashsalt':'math107-week6','pdf.fonttype':42,'savefig.facecolor':'white'})
def finish(fig,name):
 for ext in ['svg','pdf']:
  b=BytesIO();fig.savefig(b,format=ext,bbox_inches='tight',pad_inches=.2,metadata={'Date':None} if ext=='svg' else {'CreationDate':None,'ModDate':None});p=OUT/(name+'.'+ext);t=p.with_suffix('.tmp')
  data=b.getvalue()
  if ext=='svg':data=('\n'.join(line.rstrip() for line in data.decode().splitlines())+'\n').encode()
  with t.open('wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
  os.replace(t,p)
 plt.close(fig);print(name)
def axis(ax,xlabel='Years from the initial balance',ylabel='Balance ($)'):
 ax.set_xlabel(xlabel,labelpad=9);ax.set_ylabel(ylabel,labelpad=8);ax.grid(color=LINE,lw=.7);ax.set_axisbelow(True)
 for side in ['top','right']:ax.spines[side].set_visible(False)
 for side in ['bottom','left']:ax.spines[side].set_color(OLIVE)
 ax.yaxis.set_major_formatter(FuncFormatter(lambda y,_:f'{y:,.0f}'));ax.tick_params(labelsize=12)
def note(ax,x,y,text,offset=(10,12),color=INK):
 ax.scatter([x],[y],s=35,color=color,zorder=5);ax.annotate(text,(x,y),xytext=offset,textcoords='offset points',fontsize=13,color=color,arrowprops={'arrowstyle':'-','color':color,'lw':.7})
def legend(ax,**kw):ax.legend(frameon=True,facecolor='white',edgecolor=LINE,fontsize=12,**kw)

def schedule(P,rate,pay,cents=True):
 b=Decimal(str(P));r=Decimal(str(rate))/12;m=Decimal(str(pay));rows=[];total=Decimal(0)
 for k in range(1,1201):
  interest=b*r
  if cents:interest=interest.quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
  actual=min(m,b+interest);end=b+interest-actual;total+=actual;rows.append((k,float(b),float(interest),float(actual),float(end)));b=end
  if b==0:break
 return rows,float(total),float(total-Decimal(str(P)))

fig,(ax,txt)=plt.subplots(1,2,figsize=(10,4.3),gridspec_kw={'width_ratios':[1,1.15]},layout='constrained');ax.set_aspect('equal');ax.set_xlim(0,10);ax.set_ylim(0,10)
for k in range(100):ax.add_patch(Rectangle((k%10,k//10),.9,.9,facecolor=TEAL if k<3 else '#e9eedf',edgecolor='white',lw=.6))
ax.set_axis_off();ax.set_title('3 shaded cells out of 100',loc='left',fontweight='bold',pad=13);txt.set_axis_off();txt.text(.02,.87,'3% = 3/100 = 0.03',fontsize=20,color=TEAL,weight='bold');txt.text(.02,.65,'If the whole is $2,000,\neach cell represents $20.',fontsize=15,linespacing=1.7);txt.text(.02,.38,'Interest: 0.03 × $2,000 = $60\nNew balance: $2,000 + $60 = $2,060',fontsize=14,linespacing=1.8);txt.text(.02,.1,'Growth factor: 1.03',fontsize=19,color=OLIVE,weight='bold');finish(fig,'percent-and-factor')

fig,ax=plt.subplots(figsize=(9.2,4.6),layout='constrained');years=np.arange(6);vals=2000+60*years;axis(ax);ax.plot(years,vals,'o-',color=RUST,lw=2.7,markersize=6)
for x,y in zip(years,vals):ax.annotate(f'${y:,}',(x,y),xytext=(0,13),textcoords='offset points',ha='center',fontsize=12)
ax.set_xlim(-.3,5.4);ax.set_ylim(0,2900);ax.set_xticks(years);ax.annotate('Every yearly update adds $60',(2.5,2150),xytext=(1,550),fontsize=15,color=OLIVE,arrowprops={'arrowstyle':'->','color':OLIVE});ax.set_title('Simple interest: start at $2,000, add 3% of that original amount',loc='left',fontweight='bold',fontsize=14,pad=13);finish(fig,'simple-updates')

fig,(ax,bars)=plt.subplots(1,2,figsize=(10.6,4.6),layout='constrained');ys=np.arange(6);bs=2000*1.03**ys;axis(ax);ax.plot(ys,bs,'o-',color=TEAL,lw=2.7);ax.set_ylim(0,2900);ax.set_xticks(ys);ax.set_title('The balance grows',loc='left',fontweight='bold',fontsize=14,pad=13);note(ax,5,bs[-1],'$2,318.55',(-70,22));axis(bars,xlabel='Year whose interest is added',ylabel='Interest earned that year ($)');inc=np.diff(bs);bars.bar(range(1,6),inc,color=TEAL,width=.6);bars.set_ylim(0,85);bars.set_xticks(range(1,6));bars.set_title('Each 3% increase uses a larger base',loc='left',fontweight='bold',fontsize=13,pad=13)
for n,v in enumerate(inc,1):bars.text(n,v+3,f'${v:.2f}',ha='center',fontsize=12)
finish(fig,'compound-updates')

fig,ax=plt.subplots(figsize=(9.2,5),layout='constrained');years=np.arange(31);simple=2000*(1+.03*years);comp=2000*1.03**years;axis(ax);ax.plot(years,simple,color=RUST,lw=2.7,label='Simple: $60 added each year');ax.plot(years,comp,color=TEAL,lw=2.7,label='Compound: 3% of the current balance');ax.scatter(years[::5],simple[::5],s=22,color=RUST);ax.scatter(years[::5],comp[::5],s=22,color=TEAL);ax.set_xlim(0,32);ax.set_ylim(0,6000);note(ax,30,simple[-1],'$3,800.00',(-105,-20),RUST);note(ax,30,comp[-1],'$4,854.52',(-105,22),TEAL);legend(ax,loc='upper left');ax.set_title('Same principal and annual rate; different update rules',loc='left',fontweight='bold',pad=13);finish(fig,'growth-over-time')

fig,ax=plt.subplots(figsize=(9.2,4.9),layout='constrained');ns=[1,2,4,12,365];interest=[1000*((1+.06/n)**(n*10)-1) for n in ns];axis(ax,xlabel='Compounding schedule at the same 6% nominal annual rate',ylabel='Interest earned over ten years ($)');ax.bar(range(5),interest,color=[RUST,OLIVE,OLIVE,TEAL,TEAL],width=.6);ax.set_xticks(range(5),['Annual','Twice/year','Quarterly','Monthly','Daily']);ax.set_ylim(0,1000)
for k,v in enumerate(interest):ax.text(k,v+23,f'${v:.2f}',ha='center',fontsize=12)
ax.set_title('A $1,000 principal: more updates, smaller extra gains',loc='left',fontweight='bold',pad=13);finish(fig,'compounding-frequency')

fig,ax=plt.subplots(figsize=(9.2,4.9),layout='constrained');ys=np.arange(25);factor=1.06**ys;axis(ax,ylabel='Balance ÷ starting amount');ax.plot(ys,factor,'o-',color=TEAL,lw=2.5,markersize=3);ax.axhline(2,color=OLIVE,ls=':',lw=1.2);ax.axhline(4,color=OLIVE,ls=':',lw=1.2);note(ax,12,factor[12],'Year 12: about 2×\nActually 2.012×',(-123,50));note(ax,24,factor[24],'Year 24: about 4×\nActually 4.049×',(-140,-20));ax.set_xlim(0,25);ax.set_ylim(0,5.2);ax.set_xticks([0,6,12,18,24]);ax.set_title('At 6% annual growth: about 12 years per doubling',loc='left',fontweight='bold',pad=13);finish(fig,'doubling-estimates')

fig,ax=plt.subplots(figsize=(10,3.6),layout='constrained');ax.set_xlim(0,10);ax.set_ylim(0,4);ax.set_axis_off()
for x,title,value,col in [(0.1,'Starting balance','$4,000',OLIVE),(3.7,'After interest','$4,020',RUST),(7.3,'After payment','$3,820',TEAL)]:
 ax.add_patch(Rectangle((x,1.2),2.6,1.5,facecolor='#eef3e8',edgecolor=col,lw=1.3));ax.text(x+1.3,2.25,title,ha='center',fontsize=14,color=col,weight='bold');ax.text(x+1.3,1.6,value,ha='center',fontsize=24,color=col)
for a,b,label in [(2.7,3.7,'Add $20\ninterest'),(6.3,7.3,'Subtract $200\npayment')]:ax.annotate('',(b,1.9),(a,1.9),arrowprops={'arrowstyle':'->','lw':1.8,'color':INK});ax.text((a+b)/2,3.05,label,ha='center',fontsize=12)
ax.text(5,.35,'$200 payment = $20 interest + $180 principal reduction',ha='center',fontsize=16,color=OLIVE);finish(fig,'loan-one-month')

rows,total,interest=schedule(4000,.06,200);fig,ax=plt.subplots(figsize=(9.2,4.9),layout='constrained');selected=[rows[n-1] for n in [1,5,10,20]];ints=[r[2] for r in selected];principal=[200-v for v in ints];axis(ax,xlabel='Month of the $200 payment',ylabel='Dollars within the payment');ax.bar(range(4),principal,color=OLIVE,width=.58,label='Reduces principal');ax.bar(range(4),ints,bottom=principal,color=RUST,width=.58,label='Covers interest');ax.set_xticks(range(4),['1','5','10','20']);ax.set_ylim(0,285)
for k,v in enumerate(ints):ax.text(k,208,f'Interest ${v:.2f}',ha='center',fontsize=12)
legend(ax,loc='upper left',ncol=2);ax.set_title('Same payment; a changing split as the balance falls',loc='left',fontweight='bold',pad=13);finish(fig,'payment-parts')

fig,ax=plt.subplots(figsize=(9.2,5),layout='constrained');axis(ax,xlabel='Months after the initial balance',ylabel='Balance still owed ($)')
for pay,col in [(150,RUST),(200,OLIVE),(300,TEAL)]:
 rows,total,interest=schedule(4000,.06,pay);pts=np.array([[0,4000]]+[[r[0],r[4]] for r in rows]);ax.plot(pts[:,0],pts[:,1],color=col,lw=2.6,label=f'${pay}/month: {len(rows)} payments');note(ax,len(rows),0,f'Month {len(rows)}',(-37,16),col)
ax.set_xlim(0,31);ax.set_ylim(0,5200);legend(ax,loc='upper right');ax.set_title('A $4,000 loan at 6%: payments reshape the later balance',loc='left',fontweight='bold',fontsize=14,pad=13);finish(fig,'repayment-paths')

fig,ax=plt.subplots(figsize=(9.2,4.9),layout='constrained');axis(ax,xlabel='Months after the initial $1,000 balance',ylabel='Balance still owed ($)')
for pay,col in [(5,RUST),(10,OLIVE),(50,TEAL)]:
 b=Decimal(1000);ps=[1000]
 for _ in range(12):b+= (b*Decimal('.01')).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)-Decimal(pay);ps.append(float(b))
 ax.plot(range(13),ps,color=col,lw=2.6,label=f'${pay} monthly payment')
ax.set_xlim(0,12.5);ax.set_ylim(0,1450);legend(ax,loc='upper left');ax.set_title('At 1% per month, the first interest charge is $10',loc='left',fontweight='bold',pad=13);finish(fig,'payment-threshold')

fig,(ax,bars)=plt.subplots(1,2,figsize=(10.6,4.8),gridspec_kw={'width_ratios':[1.3,1]},layout='constrained');axis(ax,xlabel='Months from the initial balance',ylabel='Balance still owed ($)');totals=[];ints=[]
for pay,col in [(160,OLIVE),(300,TEAL)]:
 rows,total,interest=schedule(8000,.18,pay,cents=False);pts=np.array([[0,8000]]+[[r[0],r[4]] for r in rows]);ax.plot(pts[:,0],pts[:,1],color=col,lw=2.6,label=f'${pay}/month: {len(rows)} payments');totals.append(total);ints.append(interest)
ax.set_xlim(0,100);ax.set_ylim(0,10500)
ax.legend(loc='upper right',frameon=True,facecolor='white',edgecolor=LINE,fontsize=10);ax.set_title('One initial debt, two paths',loc='left',fontweight='bold',fontsize=14,pad=13);axis(bars,xlabel='Scheduled monthly payment',ylabel='Total dollars paid');bars.bar([0,1],[8000,8000],width=.55,color='#d8e4cc',label='Original principal');bars.bar([0,1],ints,bottom=8000,width=.55,color=[OLIVE,TEAL],label='Interest');bars.set_xticks([0,1],['$160','$300']);bars.set_ylim(0,18500);bars.set_title('Principal plus interest',loc='left',fontweight='bold',fontsize=14,pad=13)
for k,v in enumerate(ints):bars.text(k,totals[k]+500,f'Interest\n${v:,.2f}',ha='center',fontsize=12)
bars.text(.5,4000,'$8,000 principal in each',ha='center',fontsize=12);finish(fig,'card-repayment')

fig,ax=plt.subplots(figsize=(9.2,5),layout='constrained');axis(ax,xlabel='Years from the initial capacity index',ylabel='Capacity index (units)');ys=np.arange(13);raw=100*1.25**ys;ax.plot(ys,100+25*ys,'o-',color=RUST,lw=2.5,markersize=4,label='Add 25 units per year');ax.plot(ys,raw,'o-',color=TEAL,lw=2.5,markersize=4,label='Grow by 25% per year');ax.plot(ys,np.minimum(raw,400),'o--',color=OLIVE,lw=2.5,markersize=4,label='Grow by 25%, with ceiling 400');ax.axhline(400,color=OLIVE,ls=':',lw=1);note(ax,7,400,'Ceiling reached\nin year 7',(28,30));ax.set_xlim(0,12.5);ax.set_ylim(0,1750);legend(ax,loc='upper left');ax.set_title('Constructed growth rules for a computing resource',loc='left',fontweight='bold',pad=13);finish(fig,'ai-growth-limits')
os.sync()
