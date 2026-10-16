"""Reproducible, exact vector charts for Week 5's feedback and information models."""
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
OUT=Path(__file__).resolve().parents[1]/'assets/week5';OUT.mkdir(exist_ok=True)
INK='#293329';OLIVE='#536240';TEAL='#17677a';RUST='#a55c21';GOLD='#b18a22';LINE='#d8ddcd';RED='#943c2d'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':14,'axes.titlesize':14,'text.parse_math':False,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK,'svg.fonttype':'none','svg.hashsalt':'math107-week5','pdf.fonttype':42,'savefig.facecolor':'white'})
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

def feedback(r=70,start=64,k=.5,d=0,N=12):
 xs=[start]
 for n in range(N):xs.append(xs[-1]+k*(r-xs[max(0,n-d)]))
 return np.array(xs)
def box(ax,x,y,text,w=2.9,h=.85,color=OLIVE):
 ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=.1,rounding_size=.15',facecolor='#f4f6ee',edgecolor=color,lw=1.5))
 ax.text(x,y,text,ha='center',va='center',fontsize=14,color=color,linespacing=1.3)
def arrow(ax,a,b,label=None,xy=None):
 ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','color':OLIVE,'lw':1.8})
 if label:ax.text(*xy,label,ha='center',va='center',fontsize=12,color=INK)

fig,ax=plt.subplots(figsize=(10,5),layout='constrained');ax.set_axis_off();ax.set_xlim(0,10);ax.set_ylim(.2,5.8)
box(ax,2,1.65,'State\nGreenhouse temperature');box(ax,2,3.8,'Sensor\nThermometer report');box(ax,8,3.8,'Controller\nCompare and choose');box(ax,8,1.65,'Actuator\nHeater or cooling fan')
arrow(ax,(2,2.18),(2,3.27));arrow(ax,(3.55,3.8),(6.45,3.8),'reported temperature',(5,4.1));arrow(ax,(8,3.27),(8,2.18));arrow(ax,(6.45,1.65),(3.55,1.65),'net temperature change',(5,1.32));ax.text(8,5.15,'Reference: 70°F',ha='center',color=GOLD,fontsize=15,weight='bold');arrow(ax,(8,4.95),(8,4.34));ax.text(5,.5,'The changed state supplies the next observation.',ha='center',fontsize=14,color=OLIVE);finish(fig,'feedback-loop')

fig,ax=plt.subplots(figsize=(10,3.4),layout='constrained');ax.set_axis_off();ax.set_xlim(-1.6,2.65);ax.set_ylim(-1.15,1.35);ax.annotate('',xy=(2.5,0),xytext=(-1.5,0),arrowprops={'arrowstyle':'->','color':OLIVE,'lw':2})
for x,a,b in [(-1,'x₋₁','Earlier history'),(0,'x₀','Starting state'),(1,'x₁','After 1 update'),(2,'x₂','After 2 updates')]:
 ax.scatter(x,0,s=70,color=TEAL if x>=0 else GOLD);ax.text(x,.36,a,ha='center',fontsize=23,color=TEAL if x>=0 else GOLD,weight='bold');ax.text(x,-.42,b,ha='center',fontsize=12)
ax.text(.55,-.94,'At step n:  xₙ₋₁ = previous,  xₙ = current,  xₙ₊₁ = next',ha='center',fontsize=14,color=OLIVE);finish(fig,'subscript-timeline')

fig,ax=plt.subplots(figsize=(10,3.5),layout='constrained');ax.set_xlim(62.8,71.1);ax.set_ylim(-1.25,1.8);ax.set_axis_off();ax.plot([63,71],[0,0],color=LINE,lw=3)
for v,s,c in [(64,'Current: 64°F',TEAL),(67,'Next: 67°F',OLIVE),(70,'Target: 70°F',GOLD)]:ax.scatter(v,0,s=80,color=c,zorder=4);ax.text(v,-.45,s,ha='center',color=c,fontsize=14,weight='bold')
ax.annotate('',xy=(70,1.05),xytext=(64,1.05),arrowprops={'arrowstyle':'<->','color':GOLD,'lw':2});ax.text(67,1.34,'Reported error = 70 − 64 = 6°F',ha='center',fontsize=15,color=GOLD);ax.annotate('',xy=(67,.35),xytext=(64,.35),arrowprops={'arrowstyle':'->','color':TEAL,'lw':2.5});ax.text(65.5,.61,'Correction = +3°F',ha='center',fontsize=13,color=TEAL);ax.text(67,-1,'64 + 0.5(70 − 64) = 67.  The remaining gap is 3°F.',ha='center',fontsize=15);finish(fig,'error-correction')

fig,ax=plt.subplots(figsize=(10,4.9),layout='constrained');axis(ax,'Completed hourly updates n','Temperature (°F)');ns=np.arange(13);ax.axhline(70,color=GOLD,lw=1.8,ls='--',label='Target: 70°F');ax.plot(ns,feedback(),'o-',color=TEAL,lw=2.5,label='Current report');ax.plot(ns,feedback(d=1),'s--',color=RUST,lw=2.4,label='One-step-old report');ax.set_ylim(63,74.2);ax.set_xlim(-.3,12.6);ax.set_xticks(ns);note(ax,3,71.5,'First overshoot: 71.5°F',(10,25),RUST);note(ax,7,69.625,'First trough: 69.625°F',(5,-33),RUST);legend(ax,loc='upper right');ax.set_title('Same start 64°F, target 70°F, and strength 0.5; only report age changes',loc='left',fontweight='bold',fontsize=13,pad=13);finish(fig,'immediate-delayed')

fig,ax=plt.subplots(figsize=(10,4.2),layout='constrained');ax.set_axis_off();ax.set_xlim(0,10);ax.set_ylim(0,4.8);box(ax,2.2,3.5,'Current state x₂\n70°F',w=3.5,color=TEAL);box(ax,7.7,3.5,'Available report x₁\n67°F',w=3.5,color=RUST);ax.text(5,2.2,'Correction: 0.5(70 − 67) = +1.5°F',ha='center',fontsize=17,color=RUST,weight='bold');box(ax,5,.8,'Next state x₃ = 70 + 1.5 = 71.5°F',w=8.5,color=OLIVE);arrow(ax,(2.2,2.96),(3.1,1.32));arrow(ax,(7.7,2.96),(6.6,2.65));ax.text(5,4.45,'Step 2 → step 3: the report and the state have different times',ha='center',fontsize=14);finish(fig,'delay-decision')

fig,axs=plt.subplots(2,2,figsize=(10.5,7.2),layout='constrained')
for ax,k,desc in zip(axs.flat,[.5,1.5,2,2.3],['Approach from below','Shrinking swings','Equal-size swings','Growing swings']):
 xs=feedback(k=k,N=8);axis(ax,'Update n','Temperature (°F)');ax.axhline(70,color=GOLD,ls='--',lw=1.4);ax.plot(range(9),xs,'o-',color=TEAL if k<2 else RUST,lw=2);ax.set_ylim(15,125);ax.set_xticks([0,2,4,6,8]);ax.set_title(f'k = {k:g}: {desc}',loc='left',fontsize=13,fontweight='bold',pad=10)
finish(fig,'strength-comparison')

fig,axs=plt.subplots(1,3,figsize=(11.5,4.4),layout='constrained')
entries=[('Delayed','Current state: 70°F\nAvailable report: 67°F\n\nCorrect about the past.\nLate for this decision.',RUST),('Randomly noisy','Steady state: 68°F\nOne report: 72°F\n\nUnusual under a stated\nnoise model, but possible.',TEAL),('Biased','Steady state: 68°F\nTypical report: 70°F\n\nA persistent +2°F offset.\nAveraging will not fix it.',OLIVE)]
for ax,(title,copy,c) in zip(axs,entries):
 ax.set_axis_off();ax.add_patch(FancyBboxPatch((.01,.03),.98,.94,boxstyle='round,pad=.02',transform=ax.transAxes,facecolor='#f4f6ee',edgecolor=c,lw=1.5));ax.text(.08,.84,title,transform=ax.transAxes,color=c,fontsize=18,weight='bold');ax.text(.08,.66,copy,transform=ax.transAxes,fontsize=13,va='top',linespacing=1.7)
finish(fig,'noise-vs-delay')

fig,(ax,b)=plt.subplots(1,2,figsize=(10.7,4.7),layout='constrained');m=np.arange(1,26);axis(ax,'Readings in one average m','SD of average (°F)');ax.plot(m,2/np.sqrt(m),color=TEAL,lw=2.5);ax.set_ylim(0,2.6);ax.set_yticks([0,.5,1,1.5,2]);ax.yaxis.set_major_formatter(FuncFormatter(lambda y,_:f'{y:g}'));ax.set_xticks([1,4,9,16,25]);ax.set_title('Precision: 2 / √m',loc='left',weight='bold',pad=12)
for n,off in [(1,(8,12)),(4,(8,12)),(16,(-35,20))]:note(ax,n,2/np.sqrt(n),f'm = {n}: {2/np.sqrt(n):g}°F',off,TEAL)
axis(b,'Readings in one average m','Oldest reading’s age (minutes)');b.plot(m,m-1,color=RUST,lw=2.5);b.set_xticks([1,4,9,16,25]);b.set_yticks([0,5,10,15,20,25]);b.set_ylim(-1,28);b.set_title('Collection span: m − 1 minutes',loc='left',weight='bold',fontsize=13,pad=12);b.text(2,20,'One reading per minute;\nnewest reading is current.',fontsize=12,color=RUST);finish(fig,'averaging')

fig,axs=plt.subplots(1,3,figsize=(11.8,4.3),layout='constrained')
for ax in axs:ax.set_axis_off()
for ax,(title,copy,c) in zip(axs,[('Corrective','Report below target\n→ correction upward\n→ smaller departure\n\nCan still overshoot.',TEAL),('Amplifying','More exposure\n→ more sharing\n→ more exposure\n\nChange reinforces change.',RUST),('Adaptive','Attempt and result\n→ measured error\n→ updated parameter\n\nThe response can change.',OLIVE)]):
 ax.text(.03,.9,title,fontsize=19,weight='bold',color=c);ax.plot([.03,.95],[.79,.79],transform=ax.transAxes,color=c,lw=3);ax.text(.03,.68,copy,fontsize=13,va='top',linespacing=1.6);ax.set_xlim(0,1);ax.set_ylim(0,1)
finish(fig,'feedback-types')

fig,(a,b)=plt.subplots(1,2,figsize=(10.6,4.7),layout='constrained');n=np.arange(9);w=3-2*.5**n
for ax,ys,target,ylabel,c in [(a,w,3,'Weight wₙ',OLIVE),(b,2*w,6,'Prediction 2wₙ',TEAL)]:
 axis(ax,'Completed updates n',ylabel);ax.axhline(target,color=GOLD,ls='--',label=f'Target: {target}');ax.plot(n,ys,'o-',color=c,lw=2.6);ax.set_ylim(0,target*1.2);ax.yaxis.set_major_formatter(FuncFormatter(lambda y,_:f'{y:g}'));ax.set_xticks([0,2,4,6,8]);legend(ax,loc='lower right');ax.set_title('The adjustable parameter' if ax is a else 'The resulting prediction',loc='left',fontsize=14,weight='bold',pad=12)
finish(fig,'learning-updates')

fig,ax=plt.subplots(figsize=(10,4.6),layout='constrained');ax.set_axis_off();ax.set_xlim(0,10);ax.set_ylim(.2,5.5);box(ax,2,3.8,'Assessment results\nA partial measure',w=3.1,color=TEAL);box(ax,8,3.8,'Teacher decisions\nInstruction and assessment',w=3.4);box(ax,5,1.4,'Students respond\nLearning, study, and feedback',w=4.4,color=RUST);arrow(ax,(3.65,3.8),(6.2,3.8));arrow(ax,(8,3.25),(6.5,1.94));arrow(ax,(3.5,1.94),(2,3.25));ax.text(5,5,'Who chooses the goal and what counts as evidence?',ha='center',color=OLIVE,fontsize=15,weight='bold');ax.text(5,.44,'Students can also comment on how learning is measured.',ha='center',fontsize=13);finish(fig,'observer-loop')

fig,ax=plt.subplots(figsize=(10,3.9),layout='constrained');ax.set_axis_off();ax.set_xlim(0,10);ax.set_ylim(0,4.7)
for y,bits,label in [(3.4,'10111','Sent: 4 ones (even)'),(1.6,'10011','One flip: 3 ones (odd)')]:
 for j,bit in enumerate(bits):
  x=1.05+j*.9;ax.add_patch(Rectangle((x-.34,y-.42),.68,.84,facecolor='#f8ecd6' if j==4 else '#e6eff0',edgecolor=GOLD if j==4 else TEAL,lw=1.4));ax.text(x,y,bit,ha='center',va='center',fontsize=21,color=GOLD if j==4 else TEAL,weight='bold')
 ax.text(5.9,y,label,va='center',fontsize=16,color=OLIVE if y>2 else RUST)
ax.text(4.65,4.25,'Parity bit',ha='center',color=GOLD,fontsize=12);ax.text(2.85,.4,'The changed third bit is detected, but parity alone cannot locate it.',fontsize=13);finish(fig,'bit-parity')

fig,ax=plt.subplots(figsize=(9.3,4.8),layout='constrained');axis(ax,'Probability assigned to the observed event','Surprise (bits)');xs=np.arange(4);ax.bar(xs,[1,2,3,4],color=[TEAL,OLIVE,RUST,GOLD],width=.6);ax.set_xticks(xs,['1/2','1/4','1/8','1/16']);ax.set_yticks([0,1,2,3,4,5]);ax.set_ylim(0,5.2)
for x,n in zip(xs,[1,2,3,4]):ax.text(x,n+.16,f'{n} bit'+('s' if n>1 else ''),ha='center',fontsize=15)
ax.set_title('Halve the probability; add one bit of surprise',loc='left',weight='bold',pad=14);finish(fig,'information-bits')

fig,ax=plt.subplots(figsize=(10,4.9),layout='constrained');axis(ax,'Completed weekly updates n','Modeled mastery score');ns=np.arange(13);ax.axhline(80,color=GOLD,lw=1.8,ls='--',label='Reference: 80');ax.plot(ns,feedback(r=80,start=56),'o-',color=TEAL,lw=2.5,label='Current report');ax.plot(ns,feedback(r=80,start=56,d=1),'s--',color=RUST,lw=2.4,label='One-week-old report');ax.set_ylim(52,94);ax.set_xlim(-.2,12.5);ax.set_xticks(ns);note(ax,3,86,'86: overshoot',(12,16),RUST);legend(ax,loc='lower right');ax.set_title('A feedback model of scores, not a rule that guarantees learning',loc='left',weight='bold',fontsize=14,pad=14);finish(fig,'school-feedback')
os.sync()
