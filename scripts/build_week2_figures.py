"""Reproducible vector charts for Week 2's samples, frequencies, and probability models."""
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
OUT=Path(__file__).resolve().parents[1]/'assets/week2';OUT.mkdir(exist_ok=True)
INK='#293329';OLIVE='#536240';TEAL='#17677a';RUST='#a55c21';GOLD='#b18a22';LINE='#d8ddcd';RED='#943c2d'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':14,'axes.titlesize':14,'text.parse_math':False,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK,'svg.fonttype':'none','svg.hashsalt':'math107-week2','pdf.fonttype':42,'savefig.facecolor':'white'})
def finish(fig,name):
 for ext in ['svg','pdf']:
  b=BytesIO();fig.savefig(b,format=ext,bbox_inches='tight',pad_inches=.2,metadata={'Date':None} if ext=='svg' else {'CreationDate':None,'ModDate':None});p=OUT/(name+'.'+ext);t=p.with_suffix('.tmp')
  data=b.getvalue()
  if ext=='svg':data=('\n'.join(line.rstrip() for line in data.decode().splitlines())+'\n').encode()
  with t.open('wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
  os.replace(t,p)
 plt.close(fig);print(name)
def axis(ax,xlabel='',ylabel=''):
 ax.set_xlabel(xlabel,labelpad=9);ax.set_ylabel(ylabel,labelpad=8);ax.grid(color=LINE,lw=.7);ax.set_axisbelow(True)
 for side in ['top','right']:ax.spines[side].set_visible(False)
 for side in ['bottom','left']:ax.spines[side].set_color(OLIVE)
 ax.yaxis.set_major_formatter(FuncFormatter(lambda y,_:f'{y:,.0f}'));ax.tick_params(labelsize=12)
def note(ax,x,y,text,offset=(10,12),color=INK):
 ax.scatter([x],[y],s=35,color=color,zorder=5);ax.annotate(text,(x,y),xytext=offset,textcoords='offset points',fontsize=13,color=color,arrowprops={'arrowstyle':'-','color':color,'lw':.7})
def legend(ax,**kw):ax.legend(frameon=True,facecolor='white',edgecolor=LINE,fontsize=12,**kw)

from collections import Counter
from matplotlib.ticker import MaxNLocator

def bars(name,labels,values,title,xlabel='',ylabel='Frequency',probability=False,colors=None,touching=False):
 fig,ax=plt.subplots(figsize=(10,4.5),layout='constrained')
 ax.bar(range(len(labels)),values,color=colors or TEAL,width=1 if touching else .62,edgecolor='white' if touching else None)
 axis(ax,xlabel,ylabel);ax.set_xticks(range(len(labels)),labels)
 ax.set_ylim(0,1.06 if probability else max(values)*1.27)
 ax.yaxis.set_major_formatter(FuncFormatter(lambda y,_:f'{y:g}'))
 if not probability:ax.yaxis.set_major_locator(MaxNLocator(integer=True))
 for i,y in enumerate(values):ax.text(i,y+(.025 if probability else max(values)*.035),(f'{y:.3f}'.rstrip('0').rstrip('.') if probability else f'{y:g}'),ha='center',fontsize=13)
 ax.set_title(title,loc='left',fontsize=14,weight='bold',pad=14);finish(fig,name)

def histogram(name,edges,counts,title,xlabel,ylabel='Frequency',relative=False):
 fig,ax=plt.subplots(figsize=(10,4.5),layout='constrained');values=np.array(counts)/sum(counts) if relative else counts
 ax.bar(edges[:-1],values,width=np.diff(edges),align='edge',edgecolor='white',color=TEAL,alpha=.83)
 axis(ax,xlabel,ylabel);ax.set_xticks(edges);ax.set_xlim(edges[0],edges[-1]);ax.set_ylim(0,max(values)*1.3)
 ax.yaxis.set_major_formatter(FuncFormatter(lambda y,_:f'{y:g}'))
 if not relative:ax.yaxis.set_major_locator(MaxNLocator(integer=True))
 for a,b,y,c in zip(edges[:-1],edges[1:],values,counts):ax.text((a+b)/2,y+max(values)*.04,f'{c}' if not relative else f'{c}/{sum(counts)}',ha='center',fontsize=12)
 ax.set_title(title,loc='left',fontsize=14,weight='bold',pad=14);finish(fig,name)

fig,axs=plt.subplots(1,2,figsize=(10,4.7),layout='constrained')
for ax,chosen,title in [(axs[0],{0,1,2,6,7,8},'Only records from one corner'),(axs[1],{1,5,9,14,18,23},'One possible random selection')]:
 ax.set_axis_off();ax.set_xlim(-.8,6);ax.set_ylim(-1.1,4.4)
 for i in range(24):
  x=i%6;y=3-i//6;ax.scatter(x,y,s=400,color=TEAL if i in chosen else '#eef3e8',edgecolor=TEAL if i in chosen else LINE,lw=1.5);ax.text(x,y,str(i+1),ha='center',va='center',fontsize=11,color='white' if i in chosen else INK)
 ax.text(2.5,-.85,'Population: all 24 records\nSample: the 6 colored records',ha='center',fontsize=13,color=OLIVE)
 ax.set_title(title,loc='left',fontsize=13,weight='bold',pad=15)
finish(fig,'population-sample')

fig,ax=plt.subplots(figsize=(10,4.8),layout='constrained');ax.set_axis_off();ax.set_xlim(-.8,11.5);ax.set_ylim(-.8,5.6)
colors=[TEAL]*11+[OLIVE]*9+[GOLD]*5
for i,c in enumerate(colors):ax.add_patch(Rectangle((i%5,4-i//5),.86,.86,facecolor=c,edgecolor='white',lw=1))
for y,label,c in [(4.5,'Library: 11 / 25 = 0.44 = 44%',TEAL),(2.9,'Home: 9 / 25 = 0.36 = 36%',OLIVE),(1.3,'Café: 5 / 25 = 0.20 = 20%',GOLD)]:
 ax.add_patch(Rectangle((5.6,y-.12),.3,.3,facecolor=c));ax.text(6.1,y,label,va='center',fontsize=14,color=c)
ax.text(0,-.5,'Each square is one response; all 25 squares are the whole sample.',fontsize=13)
ax.set_title('A fraction names a share of the whole group',loc='left',fontsize=16,weight='bold',pad=15);finish(fig,'relative-frequency')

fig,axs=plt.subplots(1,2,figsize=(10,4.7),layout='constrained')
for ax,ys,ylabel,title,top in [(axs[0],[6,12],'Number answering yes','Compare counts',16),(axs[1],[.6,.4],'Share answering yes','Compare shares of each group',1)]:
 ax.bar([0,1],ys,color=[TEAL,OLIVE],width=.55);axis(ax,'',ylabel);ax.set_xticks([0,1],['Group A\n10 responses','Group B\n30 responses']);ax.set_ylim(0,top);ax.yaxis.set_major_formatter(FuncFormatter(lambda y,_:f'{y:g}'))
 for i,y in enumerate(ys):ax.text(i,y+top*.025,f'{y:g}',ha='center',fontsize=14)
 ax.set_title(title,loc='left',fontsize=14,weight='bold',pad=15)
fig.suptitle('More yes answers can still be a smaller share',fontsize=16,color=OLIVE,weight='bold');finish(fig,'sample-size-comparison')

fig,axs=plt.subplots(1,2,figsize=(10,4.8),layout='constrained')
ax=axs[0];ax.bar([0,1,2],[11,9,5],width=.58,color=OLIVE);axis(ax,'Study location','Responses');ax.set_xticks([0,1,2],['Library','Home','Café']);ax.set_ylim(0,14);ax.yaxis.set_major_locator(MaxNLocator(integer=True));ax.set_title('Separate categories: bar chart',loc='left',fontsize=12,weight='bold',pad=15)
ax=axs[1];ax.bar([0,10,20,30],[3,7,6,4],width=10,align='edge',edgecolor='white',color=TEAL);axis(ax,'Commute time (minutes)','Commuters');ax.set_xticks([0,10,20,30,40]);ax.set_xlim(0,40);ax.set_ylim(0,9);ax.yaxis.set_major_locator(MaxNLocator(integer=True));ax.set_title('Numerical intervals: histogram',loc='left',fontsize=12,weight='bold',pad=15)
finish(fig,'bar-and-histogram')

fig,ax=plt.subplots(figsize=(10,3.8),layout='constrained');axis(ax,'Age (years)','');ax.set_yticks([]);ax.set_xlim(19,36);ax.set_ylim(0,2.4);ax.set_xticks([20,25,30,35]);ax.grid(False)
for a,b,y,c in [(20,25,.8,TEAL),(25,30,1.5,OLIVE),(30,35,.8,TEAL)]:
 ax.plot([a,b],[y,y],color=c,lw=4);ax.scatter([a],[y],s=90,color=c,zorder=3);ax.scatter([b],[y],s=90,facecolor='white',edgecolor=c,lw=2,zorder=3);ax.text((a+b)/2,y+.23,f'[{a}, {b})',ha='center',fontsize=15,color=c)
ax.text(27.5,2.1,'25 belongs in [25, 30), not [20, 25).',ha='center',fontsize=14,color=OLIVE);finish(fig,'bin-boundaries')

fig,ax=plt.subplots(figsize=(10,4.2),layout='constrained');ax.set_axis_off();ax.set_xlim(-.8,11.8);ax.set_ylim(-1.1,3.5)
for i,c in enumerate([RUST]*4+[TEAL]*3+[OLIVE]*5):ax.scatter(i%6,2-i//6,s=600,color=c,edgecolor='white',lw=1)
for y,label,c in [(2.5,'Red: 4 / 12 = 1 / 3',RUST),(1.15,'Blue: 3 / 12 = 1 / 4',TEAL),(-.2,'Green: 5 / 12',OLIVE)]:ax.text(6.3,y,label,fontsize=16,color=c,va='center')
ax.text(0,-.9,'Model assumption: each of the 12 marbles is equally likely to be drawn.',fontsize=13);ax.set_title('Count equally likely individual outcomes first',loc='left',fontsize=16,weight='bold',pad=12);finish(fig,'marble-model')

fig,ax=plt.subplots(figsize=(10,2.9),layout='constrained');ax.set_axis_off();ax.set_xlim(-.05,1.05);ax.set_ylim(-.5,1.1)
for a,w,label,c in [(0,.35,'Event A\n0.35',TEAL),(.35,.65,'Not A\n0.65',OLIVE)]:ax.add_patch(Rectangle((a,0),w,.55,facecolor=c,edgecolor='white',lw=2));ax.text(a+w/2,.275,label,ha='center',va='center',fontsize=15,color='white')
ax.text(.5,.85,'The two parts cover the whole: 0.35 + 0.65 = 1',ha='center',fontsize=15);ax.text(.5,-.35,'P(not A) = 1 - P(A)',ha='center',fontsize=16,color=OLIVE);finish(fig,'probability-complement')

fig,ax=plt.subplots(figsize=(8.5,6.4),layout='constrained');ax.set_xlim(.5,6.5);ax.set_ylim(6.5,.5);ax.set_xticks(range(1,7));ax.set_yticks(range(1,7));ax.set_xlabel('Second die',labelpad=12);ax.set_ylabel('First die',labelpad=12);ax.set_aspect('equal')
for a in range(1,7):
 for b in range(1,7):ax.add_patch(Rectangle((b-.5,a-.5),1,1,facecolor=TEAL if a+b==7 else '#eef3e8',edgecolor='white',lw=2));ax.text(b,a,str(a+b),ha='center',va='center',color='white' if a+b==7 else INK,fontsize=16)
ax.set_title('36 equally likely ordered pairs; 6 produce a sum of 7',fontsize=14,weight='bold',pad=16);finish(fig,'dice-outcomes')

fig,ax=plt.subplots(figsize=(10,4.7),layout='constrained');sums=np.arange(2,13);ways=[1,2,3,4,5,6,5,4,3,2,1];ps=np.array(ways)/36
ax.bar(sums,ps,color=[TEAL if x==7 else OLIVE for x in sums],width=.7);axis(ax,'Sum of two dice','Probability');ax.set_xticks(sums);ax.set_ylim(0,.22);ax.yaxis.set_major_formatter(FuncFormatter(lambda y,_:f'{y:g}'))
for x,y,w in zip(sums,ps,ways):ax.text(x,y+.006,f'{w}/36',ha='center',fontsize=11)
ax.set_title('The sums are not equally likely',loc='left',fontsize=16,weight='bold',pad=13);finish(fig,'dice-distribution')

fig,ax=plt.subplots(figsize=(10,4.6),layout='constrained');rng=np.random.default_rng(10702);n=np.arange(1,501)
for c,label in [(TEAL,'First run'),(RUST,'A fresh run')]:xs=(rng.random(500)<.5).astype(int);ax.plot(n,np.cumsum(xs)/n,color=c,lw=1.5,label=label)
ax.axhline(.5,color=OLIVE,ls='--',lw=1.7,label='Model P(heads) = 0.5');axis(ax,'Number of independent flips','Relative frequency of heads');ax.set_xlim(1,500);ax.set_ylim(0,1);ax.yaxis.set_major_formatter(FuncFormatter(lambda y,_:f'{y:g}'));legend(ax,loc='upper right');ax.set_title('A stable probability can produce different observed paths',loc='left',fontsize=14,weight='bold',pad=13);finish(fig,'repeated-trials')

fig,axs=plt.subplots(1,3,figsize=(10,4.1),layout='constrained')
for ax,ps,title in [(axs[0],[.05,.1,.2,.3,.2,.1,.05],'Symmetric'),(axs[1],[.4,.25,.15,.1,.06,.03,.01],'Skewed right'),(axs[2],[.01,.03,.06,.1,.15,.25,.4],'Skewed left')]:
 ax.bar(range(1,8),ps,width=1,color=TEAL,edgecolor='white');axis(ax,'Value','Probability' if ax==axs[0] else '');ax.set_ylim(0,.47);ax.set_xticks([1,4,7]);ax.yaxis.set_major_formatter(FuncFormatter(lambda y,_:f'{y:g}'));ax.set_title(title,loc='left',fontsize=13,weight='bold',pad=15)
finish(fig,'distribution-shapes')

bars('transport-survey',['Drive','Transit','Bike','Walk'],[38,18,10,14],'80 working residents: one usual commuting method each','Commuting method')
bars('employee-transport',['Car','Bus','Bike','Walk'],[10,4,3,3],'20 employees: one usual travel method each','Travel method')
bars('document-errors',['0','1','2','3','4'],[.5,.3,.12,.05,.03],'A model for document errors: the tail extends toward larger counts','Errors per document','Probability',True,touching=True)

def interval(name,labels,ps,u,title):
 fig,ax=plt.subplots(figsize=(10,3.7),layout='constrained');ax.set_xlim(0,1);ax.set_ylim(-.8,1.7);ax.set_yticks([]);ax.set_xticks([0]+list(np.cumsum(ps)));ax.tick_params(axis='x',labelsize=11);ax.set_xlabel('Random number u from 0 up to (but not including) 1',labelpad=10)
 a=0
 for label,p,c in zip(labels,ps,[TEAL,OLIVE,RUST,GOLD]):
  ax.add_patch(Rectangle((a,0),p,.65,facecolor=c,edgecolor='white',lw=2));ax.text(a+p/2,.98,label,ha='center',fontsize=13,color=c);ax.text(a+p/2,.32,f'{p:g}',ha='center',va='center',fontsize=12,color='white');a+=p
 ax.annotate(f'u = {u:g}',xy=(u,.64),xytext=(u,1.52),ha='center',fontsize=14,color=INK,arrowprops=dict(arrowstyle='-|>',color=INK,lw=1.5));ax.text(.01,-.5,'A wider interval has a greater chance of being hit.',fontsize=13,color=OLIVE)
 for side in ['top','left','right']:ax.spines[side].set_visible(False)
 ax.spines['bottom'].set_color(OLIVE);ax.set_title(title,loc='left',fontsize=14,weight='bold',pad=15);finish(fig,name)
interval('next-token-intervals',['bed','sofa','floor','moon'],[.5,.25,.2,.05],.82,'One draw: 0.82 falls in the floor interval [0.75, 0.95)')
interval('token-sampling',['mat','rug','chair','moon'],[.5,.2,.2,.1],.73,'One draw: 0.73 falls in the chair interval [0.70, 0.90)')

fig,ax=plt.subplots(figsize=(10,4.7),layout='constrained');x=np.arange(4);ax.bar(x-.18,[.8,.1,.08,.02],width=.36,color=OLIVE,label='Cold illustration');ax.bar(x+.18,[.35,.25,.22,.18],width=.36,color=TEAL,label='Hot illustration');axis(ax,'Possible next token','Probability');ax.set_xticks(x,['mat','rug','chair','moon']);ax.set_ylim(0,1);ax.yaxis.set_major_formatter(FuncFormatter(lambda y,_:f'{y:g}'));legend(ax,loc='upper right')
for offset,ps in [(-.18,[.8,.1,.08,.02]),(.18,[.35,.25,.22,.18])]:
 for i,p in enumerate(ps):ax.text(i+offset,p+.022,f'{p:.2f}',ha='center',fontsize=11)
ax.set_title('Two illustrative distributions: concentrated versus more evenly spread',loc='left',fontsize=13,weight='bold',pad=14);finish(fig,'generation-choices')

fig,ax=plt.subplots(figsize=(10,4.6),layout='constrained');ax.set_axis_off();ax.set_xlim(-.3,10);ax.set_ylim(-.8,4.8)
nodes=[(.5,2,'The',OLIVE),(4.4,3.4,'The cat',TEAL),(4.4,.4,'Another next token',OLIVE),(8.4,4.2,'The cat sat',TEAL),(8.4,2.5,'The cat + another token',OLIVE)]
for x,y,label,c in nodes:ax.text(x,y,label,ha='center',va='center',fontsize=13,color=c,bbox=dict(boxstyle='round,pad=.5',facecolor='#eef3e8',edgecolor=LINE))
for start,end,label,xy,c in [((1.1,2.2),(3.4,3.25),'0.40',(2.25,3.15),TEAL),((1.1,1.8),(3.3,.55),'0.60',(2.1,.72),OLIVE),((5.2,3.6),(7.55,4.1),'0.50',(6.3,4.25),TEAL),((5.2,3.2),(7.1,2.6),'0.50',(6.2,2.55),OLIVE)]:ax.annotate('',xy=end,xytext=start,arrowprops=dict(arrowstyle='->',color=c,lw=2));ax.text(*xy,label,fontsize=13,color=c)
ax.text(5,-.55,'Path probability: 0.40 × 0.50 = 0.20',ha='center',fontsize=17,color=TEAL);ax.set_title('Use the chance at the second step after the first choice',loc='left',fontsize=15,weight='bold',pad=14);finish(fig,'conditional-path')

calls=[5,8,6,7,9,5,6,8,7,6,7,8,5,9,7,6,8,7,6,5,8,7,6,9,7,8,6,7,5,8];counts=Counter(calls)
bars('daily-calls',[str(x) for x in range(5,10)],[counts[x]/30 for x in range(5,10)],'30 observed days: 7 calls occurred on 8 days','Calls per day','Relative frequency',True)
histogram('quiz-scores',[25,30,35,40,45,50],[3,7,12,7,3],'32 quiz scores: a symmetric grouped display','Score (out of 50)')
bars('seasons',['Spring','Summer','Fall','Winter'],[6,10,5,4],'25 recorded favorite-season responses','Favorite season')
bars('book-club',['0','1','2','3','4'],[2,8,5,3,2],'Books read last month by 20 club members','Books read','Members')
bars('lunch-locations',['Cafeteria','Restaurant','Desk','Outside'],[18/40,10/40,8/40,4/40],'40 office workers: preferred lunch location','Preferred location','Relative frequency',True)
ages=[22,25,31,28,35,22,29,40,33,27,25,38,30,26,42,23,31,29,35,24,27,33,28,36];counts,_=np.histogram(ages,bins=[20,25,30,35,40,45])
histogram('volunteer-ages',[20,25,30,35,40,45],counts.tolist(),'24 volunteers: counts in five-year age bins','Age (years)','Relative frequency',True)
histogram('social-hours',[0,5,10,15,20,25,30],[3,8,10,6,4,2],'Weekly social-media hours for 33 students','Hours per week')
bars('quality-defects',['0','1','2','3'],[.56,.28,.12,.04],'50 inspected products: relative frequencies of defects','Defects per product','Relative frequency',True,touching=True)
histogram('commute-review',[0,15,30,45,60],[12,22,18,8],'Travel-to-work times for 60 commuters','Travel time (minutes)','Relative frequency',True)
bars('sleep-review',['4','5','6','7','8','9'],[2/30,4/30,8/30,10/30,5/30,1/30],'Sleep the previous night for 30 students','Sleep (hours)','Relative frequency',True,touching=True)
bars('chip-distribution',['Red','Blue','Green'],[3/12,4/12,5/12],'One chip drawn from 3 red, 4 blue, and 5 green chips','Chip color','Probability',True,colors=[RUST,TEAL,OLIVE])
os.sync()
