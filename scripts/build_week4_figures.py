"""Reproducible, exact vector charts for Week 4's normal models and inference examples."""
from decimal import Decimal,ROUND_HALF_UP
from matplotlib.patches import Rectangle, FancyBboxPatch
from pathlib import Path
from io import BytesIO
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
OUT=Path(__file__).resolve().parents[1]/'assets/week4';OUT.mkdir(exist_ok=True)
INK='#293329';OLIVE='#536240';TEAL='#17677a';RUST='#a55c21';GOLD='#b18a22';LINE='#d8ddcd';RED='#943c2d'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':14,'axes.titlesize':14,'text.parse_math':False,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK,'svg.fonttype':'none','svg.hashsalt':'math107-week4','pdf.fonttype':42,'savefig.facecolor':'white'})
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

from scipy.stats import norm
from matplotlib.ticker import MaxNLocator

def density_axis(ax,xlabel='Measurement value (units)'):
 axis(ax,xlabel,'Probability density (per unit)');ax.yaxis.set_major_formatter(FuncFormatter(lambda y,_:f'{y:g}'))
def cirow(ax,y,lo,hi,center,color=TEAL,label=None):
 ax.plot([lo,hi],[y,y],color=color,lw=3);ax.plot([lo,lo],[y-.07,y+.07],color=color,lw=2);ax.plot([hi,hi],[y-.07,y+.07],color=color,lw=2);ax.scatter([center],[y],s=44,color=color,zorder=4)
 if label:ax.text(lo,y+.15,label,color=color,fontsize=12)
def ciaxis(ax,xlabel):
 axis(ax,xlabel,'');ax.spines['left'].set_visible(False);ax.set_yticks([]);ax.set_ylim(-.5,1.5)

fig,ax=plt.subplots(figsize=(9.7,4.8),layout='constrained');x=np.linspace(15,85,1000);density_axis(ax)
for sd,c in [(5,TEAL),(10,RUST)]:ax.plot(x,norm.pdf(x,50,sd),color=c,lw=2.6,label=f'Mean 50, SD {sd}')
ax.set_ylim(bottom=0);ax.axvline(50,color=GOLD,ls='--',lw=1.4);legend(ax,loc='upper right');ax.set_title('Equal centers; different spreads; area 1 under each full curve',loc='left',weight='bold',pad=13,fontsize=14);finish(fig,'normal-shape')

fig,axs=plt.subplots(3,1,figsize=(9.5,7.3),layout='constrained');z=np.linspace(-3.8,3.8,1200)
for ax,k,p,c in zip(axs,[1,2,3],[68,95,99.7],[TEAL,OLIVE,RUST]):
 ax.plot(z,norm.pdf(z),color=INK,lw=1.8);ax.fill_between(z,0,norm.pdf(z),where=np.abs(z)<=k,color=c,alpha=.3);ax.axvline(-k,color=c,ls='--');ax.axvline(k,color=c,ls='--');ax.set_xlim(-3.8,3.8);ax.set_ylim(0,.46);ax.set_xticks(range(-3,4),['−3σ','−2σ','−σ','μ','+σ','+2σ','+3σ']);ax.set_yticks([]);ax.spines[['top','right','left']].set_visible(False);ax.tick_params(labelsize=12);ax.text(.02,.84,f'Within {k}σ: about {p}%',transform=ax.transAxes,color=c,fontsize=14,weight='bold')
axs[-1].set_xlabel('Distance from the mean',labelpad=9);finish(fig,'empirical-bands')

fig,ax=plt.subplots(figsize=(10,4.8),layout='constrained');x=np.linspace(14,46,1200);y=norm.pdf(x,30,4);density_axis(ax,'Delivery time (minutes)');ax.plot(x,y,color=INK,lw=2)
for mask,c in [(x<22,RUST),((x>=22)&(x<=38),TEAL),(x>38,RUST)]:ax.fill_between(x,0,y,where=mask,color=c,alpha=.3)
ax.set_ylim(0,.13);ax.set_xticks([18,22,26,30,34,38,42]);ax.text(30,.08,'Middle ≈ 95%',ha='center',color=TEAL,fontsize=16,weight='bold');ax.annotate('Lower tail ≈ 2.5%',xy=(20,.003),xytext=(15,.078),fontsize=13,color=RUST,arrowprops={'arrowstyle':'->','color':RUST});ax.annotate('Upper tail ≈ 2.5%',xy=(40,.003),xytext=(35,.078),fontsize=13,color=RUST,arrowprops={'arrowstyle':'->','color':RUST});ax.set_title('Mean 30 minutes, SD 4 minutes: split the outside 5% equally',loc='left',fontsize=14,weight='bold',pad=14);finish(fig,'empirical-tails')

fig,ax=plt.subplots(figsize=(10,3.6),layout='constrained');ax.set_axis_off();ax.set_xlim(48,94);ax.set_ylim(-1.2,1.8);ax.plot([50,90],[0,0],color=LINE,lw=3)
for value,lab in [(50,'−2'),(60,'−1'),(70,'0'),(80,'+1'),(90,'+2')]:
 ax.plot([value,value],[-.08,.08],color=OLIVE,lw=2);ax.text(value,-.38,str(value),ha='center',fontsize=13);ax.text(value,-.88,'z = '+lab,ha='center',fontsize=12,color=OLIVE)
ax.scatter(85,0,s=90,color=RUST,zorder=3);ax.text(85,.25,'x = 85',ha='center',color=RUST,fontsize=16,weight='bold');ax.annotate('',xy=(85,.85),xytext=(70,.85),arrowprops={'arrowstyle':'<->','color':TEAL,'lw':2});ax.text(77.5,1.15,'15 points ÷ 10 points per SD = 1.5 SD',ha='center',color=TEAL,fontsize=14);ax.text(70,.25,'μ = 70',ha='center',fontsize=14,color=OLIVE);finish(fig,'z-score-distance')

fig,axs=plt.subplots(2,1,figsize=(10,5.5),layout='constrained')
for ax,mu,sd,value,name,c in [(axs[0],80,10,88,'Exam A',TEAL),(axs[1],65,6,74,'Exam B',RUST)]:
 x=np.linspace(mu-3*sd,mu+3*sd,600);density_axis(ax,'Raw score (points)');ax.plot(x,norm.pdf(x,mu,sd),color=c,lw=2);ax.axvline(mu,color=GOLD,ls='--');ax.axvline(value,color=c,lw=2.3);ax.text(.02,.85,f'{name}: mean {mu}, SD {sd}, score {value}; z = {(value-mu)/sd:g}',transform=ax.transAxes,color=c,fontsize=14,weight='bold');ax.set_ylim(0,norm.pdf(mu,mu,sd)*1.4)
finish(fig,'standardized-comparison')

fig,ax=plt.subplots(figsize=(10,4.8),layout='constrained');x=np.linspace(15,85,1400);density_axis(ax)
for sd,label,c in [(10,'Individual values: SD 10',RUST),(2,'Sample means, n = 25: SE 2',TEAL)]:ax.plot(x,norm.pdf(x,50,sd),color=c,lw=2.6,label=label)
ax.set_ylim(bottom=0);ax.axvline(50,color=GOLD,ls='--',lw=1.3);legend(ax,loc='upper left');ax.set_title('The sampling distribution concerns means, not individual measurements',loc='left',fontsize=13,weight='bold',pad=13);finish(fig,'sampling-means')

fig,ax=plt.subplots(figsize=(10,3.5),layout='constrained');ciaxis(ax,'Value (original units)');ax.set_xlim(68.5,75.5);cirow(ax,.3,70,74,72);ax.set_xticks([70,71,72,73,74]);ax.text(70,.62,'Lower: 70',ha='center',color=TEAL,fontsize=14);ax.text(72,.62,'Estimate: 72',ha='center',color=TEAL,fontsize=14);ax.text(74,.62,'Upper: 74',ha='center',color=TEAL,fontsize=14)
for end in [70,74]:ax.annotate('',xy=(end,1.05),xytext=(72,1.05),arrowprops={'arrowstyle':'<->','color':GOLD,'lw':1.8})
ax.text(71,1.25,'Margin 2',ha='center',color=GOLD,fontsize=14);ax.text(73,1.25,'Margin 2',ha='center',color=GOLD,fontsize=14);finish(fig,'interval-anatomy')

fig,ax=plt.subplots(figsize=(10,4.2),layout='constrained');ciaxis(ax,'Population mean under consideration (hours)');ax.set_xlim(3.65,4.75);ax.set_ylim(-.5,1.7);ax.axvline(4,color=GOLD,ls='--',lw=2);cirow(ax,1,3.9,4.5,4.2,TEAL);cirow(ax,0,4.1,4.3,4.2,RUST);ax.text(3.9,1.35,'4.2 ± 0.3 gives [3.9, 4.5]: includes 4',color=TEAL,fontsize=14);ax.text(4.1,.32,'4.2 ± 0.1 gives [4.1, 4.3]: entirely above 4',color=RUST,fontsize=13);ax.text(4,-.32,'Comparison: 4',ha='center',color=GOLD,fontsize=12);finish(fig,'interval-comparisons')

fig,ax=plt.subplots(figsize=(8.8,7),layout='constrained');rng=np.random.default_rng(10704);means=rng.normal(70,10,(50,25)).mean(axis=1);E=1.96*10/5;inside=np.abs(means-70)<=E
for n,(mean,ok) in enumerate(zip(means,inside),1):ax.plot([mean-E,mean+E],[n,n],color=TEAL if ok else RUST,lw=1.6,ls='-' if ok else '--');ax.scatter(mean,n,s=10,color=TEAL if ok else RUST)
ax.axvline(70,color=GOLD,lw=2,ls='--');axis(ax,'Interval for the population mean (units)','Study number');ax.set_ylim(51,0);ax.set_yticks([1,10,20,30,40,50]);ax.set_title(f'{inside.sum()} of 50 intervals contain the fixed mean in this run',loc='left',fontsize=14,weight='bold',pad=13);ax.text(.02,.02,'Solid: contains 70    Dashed: misses 70',transform=ax.transAxes,color=OLIVE,fontsize=12,bbox={'facecolor':'white','edgecolor':LINE,'pad':6});finish(fig,'repeated-intervals')

fig,ax=plt.subplots(figsize=(10,4.7),layout='constrained');n=np.arange(50,1701);axis(ax,'Sample size n','Approximate margin (units)');ax.plot(n,10*np.sqrt(100/n),color=TEAL,lw=2.6);ax.set_xlim(0,1750);ax.set_ylim(0,16);ax.set_xticks([100,400,900,1600]);
for v,offset in [(100,(15,12)),(400,(15,12)),(900,(0,20)),(1600,(-90,22))]:note(ax,v,10*np.sqrt(100/v),f'n = {v}: E ≈ {10*np.sqrt(100/v):.2f}',offset,TEAL)
ax.set_title('Same confidence, variability, and sampling design; E₀ = 10 at n₀ = 100',loc='left',fontsize=13,weight='bold',pad=13);finish(fig,'precision-scaling')

fig,ax=plt.subplots(figsize=(10,4.2),layout='constrained');ciaxis(ax,'Population mean calories per serving');ax.set_xlim(225,257);ax.axvline(230,color=RUST,ls='--',lw=2);cirow(ax,1,235,251,243,TEAL);cirow(ax,0,239,247,243,OLIVE);ax.text(235,1.25,'n = 64: 243 ± 8',fontsize=14,color=TEAL);ax.text(239,.25,'Planned n = 256: 243 ± 4',fontsize=14,color=OLIVE);ax.text(230,-.25,'Claim: 230',ha='center',color=RUST,fontsize=12);ax.set_title('The planned comparison holds the center at 243',loc='left',fontsize=14,weight='bold',pad=13);finish(fig,'nutrition-intervals')

fig,(grid,ci)=plt.subplots(2,1,figsize=(10,6.6),layout='constrained',gridspec_kw={'height_ratios':[1.6,1]});grid.set_aspect('equal');grid.set_axis_off();grid.set_xlim(-.5,20);grid.set_ylim(-.5,10.5)
for j in range(200):grid.add_patch(Rectangle((j%20,j//20),.8,.8,facecolor=TEAL if j<171 else '#e4c29c',edgecolor='white',lw=.3))
grid.set_title('Observed sample: 171 correct, 29 incorrect, 200 tested',loc='left',fontsize=14,weight='bold',pad=10);ciaxis(ci,'Population accuracy (%)');ci.set_xlim(74,96);ci.set_ylim(-.5,1.3);cirow(ci,.3,80.5,90.5,85.5);ci.text(85.5,.73,'85.5% ± 5 percentage points',ha='center',color=TEAL,fontsize=15);ci.set_xticks([75,80.5,85.5,90.5,95]);finish(fig,'benchmark-estimate')

fig,(ax,b)=plt.subplots(2,1,figsize=(10,6.1),layout='constrained');x=np.linspace(468,532,800);density_axis(ax,'Individual fill volume (mL)');y=norm.pdf(x,500,8);ax.plot(x,y,color=TEAL,lw=2.4);ax.fill_between(x,0,y,where=x>=516,color=RUST,alpha=.4);ax.axvline(500,color=GOLD,ls='--');ax.axvline(516,color=RUST,lw=2);ax.set_ylim(0,.067);ax.text(.02,.84,'Individual 516 mL: z = (516 − 500)/8 = 2',transform=ax.transAxes,fontsize=14,color=TEAL,weight='bold');ciaxis(b,'Process mean under consideration (mL)');b.set_xlim(497,508);b.axvline(500,color=GOLD,ls='--',lw=2);cirow(b,.25,501,505,503,OLIVE);b.text(501,.72,'Separate sample: 503 ± 2 gives [501, 505]',color=OLIVE,fontsize=14);b.text(500,-.25,'Target: 500',ha='center',color=GOLD,fontsize=12);b.set_ylim(-.5,1.25);finish(fig,'bottle-two-questions')

fig,ax=plt.subplots(figsize=(10,4),layout='constrained');ciaxis(ax,'Population mean task score');ax.set_xlim(70,88);cirow(ax,1,74,82,78,TEAL);cirow(ax,0,76,84,80,RUST);ax.axvspan(76,82,color=GOLD,alpha=.1);ax.text(74,1.27,'Model A: 78 ± 4',fontsize=14,color=TEAL);ax.text(76,.27,'Model B: 80 ± 4',fontsize=14,color=RUST);ax.set_title('Separate intervals overlap; uncertainty in the difference is another question',loc='left',fontsize=13,weight='bold',pad=13);finish(fig,'benchmark-overlap')
os.sync()
