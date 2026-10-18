"""Reproducible, exact vector charts for Week 3's descriptive statistics and weighted averages."""
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
OUT=Path(__file__).resolve().parents[1]/'assets/week3';OUT.mkdir(exist_ok=True)
INK='#293329';OLIVE='#536240';TEAL='#17677a';RUST='#a55c21';GOLD='#b18a22';LINE='#d8ddcd';RED='#943c2d'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':14,'axes.titlesize':14,'text.parse_math':False,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK,'svg.fonttype':'none','svg.hashsalt':'math107-week3','pdf.fonttype':42,'savefig.facecolor':'white'})
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


from statistics import mean, median, stdev
from collections import Counter
from matplotlib.ticker import MaxNLocator

def dots(ax,values,limits,label,units='Value (original units)',show_median=False,spread=True):
 counts=Counter(values);m=mean(values)
 for v,c in counts.items():ax.scatter([v]*c,range(1,c+1),s=60,color=TEAL,zorder=4,edgecolor='white',linewidth=.7)
 axis(ax,units,'');ax.set_xlim(*limits);ax.set_ylim(0,max(counts.values())+2.1);ax.set_yticks([])
 ax.axvline(m,color=RUST,lw=2,ls='--',label=f'Mean {m:g}')
 if show_median:ax.axvline(median(values),color=OLIVE,lw=2,ls=':',label=f'Median {median(values):g}')
 if spread:ax.text(.02,.91,f'Range {max(values)-min(values):g}; sample s = {stdev(values):.2f}',transform=ax.transAxes,fontsize=12,color=OLIVE)
 ax.set_title(label,loc='left',fontsize=14,weight='bold',pad=12)
 legend(ax,loc='upper right')

fig,axs=plt.subplots(1,2,figsize=(10,4.6),layout='constrained')
for ax,vals,title in [(axs[0],[2,3,3,5,7],'Recorded hours: total 20'),(axs[1],[4]*5,'Same total shared equally: 4 each')]:
 ax.bar(range(1,6),vals,color=TEAL if ax==axs[0] else OLIVE,width=.62)
 axis(ax,'Observation','Study time (hours)');ax.set_ylim(0,8.5);ax.set_xticks(range(1,6));ax.axhline(4,color=RUST,ls='--',lw=1.8);ax.text(.03,.87,'Mean = 20 / 5 = 4 hours',transform=ax.transAxes,color=RUST,fontsize=12);ax.set_title(title,loc='left',fontsize=13,weight='bold',pad=12)
finish(fig,'mean-sharing')

fig,axs=plt.subplots(2,1,figsize=(10,4.8),layout='constrained')
for ax,values,centers,title,result in [(axs[0],[1,2,2,7,18],[2],'Five ordered values: choose position 3','Median = 2'),(axs[1],[2,3,5,8,10,12],[2,3],'Six ordered values: use positions 3 and 4','Median = (5 + 8) / 2 = 6.5')]:
 ax.set_axis_off();ax.set_xlim(.3,7.8);ax.set_ylim(-.7,1.6);ax.text(.5,1.25,title,fontsize=14,weight='bold')
 for i,v in enumerate(values):
  x=i+1;ax.add_patch(Rectangle((x-.38,.25),.76,.65,facecolor='#d7e7e8' if i in centers else '#eef3e8',edgecolor=TEAL if i in centers else LINE,lw=2 if i in centers else 1));ax.text(x,.56,str(v),ha='center',va='center',fontsize=18,color=TEAL if i in centers else INK);ax.text(x,.02,f'Position {i+1}',ha='center',va='top',fontsize=10)
 ax.text(.5,-.5,result,fontsize=14,color=TEAL)
finish(fig,'median-positions')

fig,axs=plt.subplots(2,1,figsize=(10,5.6),layout='constrained')
dots(axs[0],[10,12,13,14,101],(0,110),'Five recorded weekly amounts',units='Weekly amount ($)',show_median=True)
dots(axs[1],[10,12,13,14,16],(0,110),'Same first four values; last value changed to 16',units='Weekly amount ($)',show_median=True)
finish(fig,'outlier-center')

fig,axs=plt.subplots(1,2,figsize=(10,4.3),layout='constrained')
for ax,vals,title in [(axs[0],[2,4,4,6,6,8],'Two modes: 4 and 6'),(axs[1],[10,20,30,40],'No repeated value: report no mode')]:
 c=Counter(vals);xs=list(c);ax.bar(range(len(xs)),[c[x] for x in xs],color=[TEAL if c[x]>1 else OLIVE for x in xs],width=.6);ax.set_xticks(range(len(xs)),xs);axis(ax,'Recorded value','Frequency');ax.set_ylim(0,3.2);ax.yaxis.set_major_locator(MaxNLocator(integer=True));ax.set_title(title,loc='left',fontsize=13,weight='bold',pad=12)
finish(fig,'mode-counts')

fig,axs=plt.subplots(2,1,figsize=(10,5.5),layout='constrained')
dots(axs[0],[50,51,50,49,50],(25,75),'Set A: values stay near 50')
dots(axs[1],[30,40,50,60,70],(25,75),'Set B: the same mean, more spread')
finish(fig,'same-mean-spread')

fig,axs=plt.subplots(2,1,figsize=(10,5.4),layout='constrained')
dots(axs[0],[0,4,5,6,10],(-1,11),'Set A: most values nearer the middle',spread=False);axs[0].text(.02,.91,'Range 10',transform=axs[0].transAxes,fontsize=12,color=OLIVE)
dots(axs[1],[0,0,5,10,10],(-1,11),'Set B: more values at the extremes',spread=False);axs[1].text(.02,.91,'Range 10',transform=axs[1].transAxes,fontsize=12,color=OLIVE)
finish(fig,'same-range')

fig,ax=plt.subplots(figsize=(10,4.8),layout='constrained');values=[2,4,4,6]
for j,v in enumerate(values):
 y=4-j;ax.plot([4,v],[y,y],color=TEAL,lw=3);ax.scatter(v,y,s=75,color=TEAL,zorder=4);ax.text(6.6,y,f'{v} - 4 = {v-4:+g}',va='center',fontsize=14,color=TEAL)
ax.axvline(4,color=RUST,ls='--',lw=1.8);axis(ax,'Observed value (units)','Observation');ax.set_xlim(.8,8.7);ax.set_xticks([2,3,4,5,6]);ax.set_ylim(.35,5.2);ax.set_yticks([1,2,3,4],['4','3','2','1']);ax.text(4,4.7,'Mean = 4',ha='center',color=RUST,fontsize=14);ax.set_title('Signed deviations: below is negative; above is positive',loc='left',weight='bold',pad=13,fontsize=14)
finish(fig,'signed-deviations')

fig,ax=plt.subplots(figsize=(10,4.5),layout='constrained');ax.set_axis_off();ax.set_aspect('equal');ax.set_xlim(-.5,10);ax.set_ylim(-1.8,3.9)
for x,lab,c in [(0,'Deviation -2',TEAL),(5,'Deviation +2',OLIVE)]:
 ax.add_patch(Rectangle((x,0),2,2,facecolor=c,alpha=.22,edgecolor=c,lw=2));ax.text(x+1,1,'Area 4',ha='center',va='center',fontsize=17,color=c);ax.text(x+1,2.4,lab,ha='center',fontsize=14,color=c)
ax.text(4.6,-.55,'Squares: 4 + 0 + 0 + 4 = 8 squared units',ha='center',fontsize=14);ax.text(4.6,-1.12,'Sample variance: 8 / 3 ≈ 2.67 squared units',ha='center',fontsize=14,color=OLIVE);ax.text(4.6,-1.65,'Square root: sample s ≈ 1.63 original units',ha='center',fontsize=14,color=TEAL)
finish(fig,'squares-and-units')

fig,axs=plt.subplots(3,1,figsize=(10,7.1),layout='constrained')
for ax,vals,title in [(axs[0],[2,4,4,6],'Starting values'),(axs[1],[12,14,14,16],'Add 10 to every value: center moves; spread stays'),(axs[2],[4,8,8,12],'Multiply every value by 2: center and spread double')]:dots(ax,vals,(0,18),title)
finish(fig,'shift-and-scale')

fig,ax=plt.subplots(figsize=(10,4.7),layout='constrained');edges=np.arange(50,111,10);counts=np.array([3,7,14,13,9,4]);raw=np.repeat((edges[:-1]+edges[1:])/2,counts)
ax.bar(edges[:-1],counts,width=10,align='edge',edgecolor='white',color=TEAL,alpha=.75);axis(ax,'Score (points)','Number of observations');ax.set_xticks(edges);ax.set_ylim(0,19);ax.yaxis.set_major_locator(MaxNLocator(integer=True));ax.axvline(mean(raw),color=RUST,lw=2,ls='--',label=f'Mean {mean(raw):g}');ax.axvline(median(raw),color=OLIVE,lw=2,ls=':',label=f'Median {median(raw):g}');legend(ax,loc='upper left')
for x,c in zip(edges[:-1]+5,counts):ax.text(x,c+.3,str(c),ha='center',fontsize=12)
ax.set_title('50 recorded scores: the tallest bin does not define the mean',loc='left',fontsize=14,weight='bold',pad=13);finish(fig,'histogram-center')

fig,axs=plt.subplots(2,1,figsize=(10,5.7),layout='constrained')
for ax,vals,title in [(axs[0],[250,251,249,250,250],'Machine A: five test fills'),(axs[1],[245,255,248,253,249],'Machine B: five test fills')]:
 dots(ax,vals,(243,257),title,units='Fill volume (mL)');ax.axvspan(246,254,color=OLIVE,alpha=.08);ax.axvline(246,color=OLIVE,ls=':',lw=1);ax.axvline(254,color=OLIVE,ls=':',lw=1)
 for v,c in Counter(vals).items():
  if v<246 or v>254:ax.scatter([v]*c,range(1,c+1),s=60,color=RUST,zorder=5,edgecolor='white',linewidth=.7)
finish(fig,'machine-comparison')

fig,axs=plt.subplots(1,2,figsize=(10,4.5),layout='constrained');values=[2,5,8,10];weights=[.1,.2,.6,.1];labels=['Value 2','Value 5','Value 8','Value 10']
for ax,ys,ylabel,title in [(axs[0],weights,'Weight (share of 1)','How much weight each value receives'),(axs[1],[x*w for x,w in zip(values,weights)],'Weighted contribution','Multiply each value by its weight')]:
 ax.bar(range(4),ys,color=[OLIVE,OLIVE,TEAL,OLIVE],width=.6);ax.set_xticks(range(4),labels);axis(ax,'',ylabel);ax.yaxis.set_major_formatter(FuncFormatter(lambda y,_:f'{y:g}'));ax.set_ylim(0,max(ys)*1.35)
 for i,y in enumerate(ys):ax.text(i,y+max(ys)*.04,f'{y:g}',ha='center',fontsize=13)
 ax.set_title(title,loc='left',fontsize=12,weight='bold',pad=14)
fig.suptitle('Weighted result: 0.2 + 1 + 4.8 + 1 = 7',fontsize=15,color=TEAL,weight='bold');finish(fig,'weighted-contributions')

fig,axs=plt.subplots(2,1,figsize=(10,5.5),gridspec_kw={'height_ratios':[3,1]},layout='constrained');tokens=['dog (2)','chased (3)','ball (5)','because (6)','rolled (8)'];weights=[.1,.05,.7,.05,.1]
axs[0].bar(range(5),weights,color=[OLIVE,OLIVE,TEAL,OLIVE,OLIVE],width=.58);axis(axs[0],'Token and position in the complete sentence','Attention weight');axs[0].yaxis.set_major_formatter(FuncFormatter(lambda y,_:f'{y:g}'));axs[0].set_xticks(range(5),tokens);axs[0].set_ylim(0,.95)
for i,w in enumerate(weights):axs[0].text(i,w+.025,f'{w:.2f}',ha='center',fontsize=13)
axs[0].set_title('Whole-sentence toy example for “it”: the strongest weight is on “ball”',loc='left',fontsize=13,weight='bold',pad=14)
ax=axs[1];axis(ax,'Position in the sentence','');ax.set_yticks([]);ax.set_xlim(1,9);ax.set_ylim(0,1);ax.axvline(4.95,color=RUST,lw=2,ls='--');ax.text(4.95,.65,'Weighted position = 4.95',ha='center',fontsize=14,color=RUST)
finish(fig,'token-weights')

fig,axs=plt.subplots(2,1,figsize=(10,5.4),layout='constrained')
dots(axs[0],[4,5,5,5,6],(0,10),'Head A: positions concentrate near 5',units='Token position')
dots(axs[1],[1,3,5,7,9],(0,10),'Head B: the same mean position, wider coverage',units='Token position')
finish(fig,'attention-spread')

fig,ax=plt.subplots(figsize=(10,4.6),layout='constrained');edges=np.arange(58,83,4);counts=[2,7,12,11,6,2]
ax.bar(edges[:-1],counts,width=4,align='edge',color=OLIVE,alpha=.72,edgecolor='white');axis(ax,'Height (inches)','Number of observations');ax.set_xticks(edges);ax.set_ylim(0,15);ax.yaxis.set_major_locator(MaxNLocator(integer=True))
for x,c in zip(edges[:-1]+2,counts):ax.text(x,c+.25,str(c),ha='center',fontsize=12)
ax.set_title('40 measured heights: each bar counts a four-inch interval',loc='left',fontsize=14,weight='bold',pad=13);finish(fig,'height-histogram')
os.sync()
