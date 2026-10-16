"""Build exact, reproducible vector diagrams for geometry and linear programming."""
from pathlib import Path
from io import BytesIO
import os
import itertools
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np
OUT=Path(__file__).resolve().parents[1]/'assets/week8';OUT.mkdir(exist_ok=True)
INK='#293329';OLIVE='#536240';TEAL='#17677a';GOLD='#a55c21';RED='#943c2d';SOFT='#eaf0e2';LINE='#d8ddcd'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12.5,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK,'svg.fonttype':'none','svg.hashsalt':'math107-week8','pdf.fonttype':42,'savefig.facecolor':'white'})
BASE=[(1,1,8,'le'),(2,1,12,'le')];VERTS=[(0,0),(6,0),(4,4),(0,8)]
def clip(poly,q):
 a,b,c,s=q;sign=1 if s=='le' else -1;out=[]
 for p,r in zip(poly,poly[1:]+poly[:1]):
  fp=sign*(a*p[0]+b*p[1]-c);fr=sign*(a*r[0]+b*r[1]-c)
  if fp<=1e-10:out.append(p)
  if (fp<=1e-10)!=(fr<=1e-10):
   t=fp/(fp-fr);out.append((p[0]+t*(r[0]-p[0]),p[1]+t*(r[1]-p[1])))
 return out
def region(ax,cons,xmax=9,ymax=13,color=OLIVE,alpha=.18,xmin=0,ymin=0):
 p=[(xmin,ymin),(xmax,ymin),(xmax,ymax),(xmin,ymax)]
 for q in cons:p=clip(p,q)
 if len(p)>=3:ax.add_patch(Polygon(p,facecolor=color,alpha=alpha,edgecolor='none',zorder=1))
 return p
def line(ax,a,b,c,color,label=None,ls='-',lw=2.2):
 x0,x1=ax.get_xlim();y0,y1=ax.get_ylim();pts=[]
 if b:
  for x in [x0,x1]:
   y=(c-a*x)/b
   if y0-1e-8<=y<=y1+1e-8:pts.append((x,y))
 if a:
  for y in [y0,y1]:
   x=(c-b*y)/a
   if x0-1e-8<=x<=x1+1e-8:pts.append((x,y))
 out=[]
 for p in pts:
  if p not in out:out.append(p)
 if len(out)>=2:ax.plot(*np.array([out[0],out[-1]]).T,color=color,lw=lw,ls=ls,label=label,zorder=2)
def setup(ax,xmax=9,ymax=13,xlabel='Type A packs, x',ylabel='Type B packs, y',xmin=0,ymin=0):
 ax.set_xlim(xmin,xmax);ax.set_ylim(ymin,ymax);ax.set_xlabel(xlabel,labelpad=7);ax.set_ylabel(ylabel,labelpad=7);ax.grid(color=LINE,lw=.7);ax.set_axisbelow(True)
 for s in ['top','right']:ax.spines[s].set_visible(False)
 for s in ['bottom','left']:ax.spines[s].set_color(INK)
def boundaries(ax,cons=BASE):
 for i,(a,b,c,s) in enumerate(cons):line(ax,a,b,c,TEAL if i==0 else GOLD,f'{a:g}x + {b:g}y '+('≤' if s=='le' else '≥')+f' {c:g}')
def dots(ax,verts=VERTS,color=INK,labels=True):
 for x,y in verts:
  ax.scatter(x,y,s=42,color=color,zorder=4,clip_on=False)
  if labels:ax.annotate(f'({x:g}, {y:g})',(x,y),xytext=(7,8),textcoords='offset points',fontsize=11.5,color=color,zorder=5)
def save(fig,name):
 for fmt in ['svg','pdf']:
  buf=BytesIO();opts={'metadata':{'CreationDate':None,'ModDate':None}} if fmt=='pdf' else {'metadata':{'Date':None}}
  fig.savefig(buf,format=fmt,bbox_inches='tight',pad_inches=.18,**opts);p=OUT/(name+'.'+fmt);tmp=p.with_suffix(p.suffix+'.tmp')
  with tmp.open('wb') as f:f.write(buf.getvalue());f.flush();os.fsync(f.fileno())
  tmp.replace(p)
 plt.close(fig)
fig,ax=plt.subplots(figsize=(9.5,5.6));setup(ax,9,9);ax.set_xticks(range(0,10));ax.set_yticks(range(0,10));dots(ax,[(4,4),(2,6),(6,1)])
ax.plot([0,4,4],[4,4,0],ls='--',color=TEAL);ax.annotate('',xy=(4,0),xytext=(0,0),arrowprops={'arrowstyle':'->','color':GOLD,'lw':2});ax.text(2,.35,'4 of type A',ha='center',color=GOLD);ax.text(.2,2,'4 of type B',color=TEAL,rotation=90,va='center');ax.set_title('One point records one complete plan',loc='left',fontweight='bold',pad=15);save(fig,'plan-coordinates')
fig,axs=plt.subplots(1,2,figsize=(11,4.8))
for ax in axs:setup(ax,10,6,xlabel='x',ylabel='y',xmin=-1,ymin=-1);line(ax,1,2,8,TEAL);dots(ax,[(8,0),(0,4)],TEAL)
region(axs[1],[(1,2,8,'le')],10,6,xmin=-1,ymin=-1);dots(axs[1],[(0,0)],GOLD);axs[0].set_title('Equation: x + 2y = 8',loc='left',fontweight='bold');axs[1].set_title('Inequality: x + 2y ≤ 8',loc='left',fontweight='bold');fig.tight_layout();save(fig,'half-plane')
fig,axs=plt.subplots(1,3,figsize=(12.5,4.4))
for i,ax in enumerate(axs):
 setup(ax,9,13,xlabel='x packs',ylabel='y packs');cons=BASE if i==2 else [BASE[i]];region(ax,cons,color=OLIVE if i==2 else TEAL if i==0 else GOLD);boundaries(ax,cons) if i==2 else line(ax,*cons[0][:3],TEAL if i==0 else GOLD)
 ax.set_title(['Packing: x + y ≤ 8','Ingredients: 2x + y ≤ 12','Both limits at once'][i],loc='left',fontsize=12,fontweight='bold')
 if i==2:dots(ax,labels=False)

for ax in axs:
 ax.tick_params(labelsize=13);ax.xaxis.label.set_size(14);ax.yaxis.label.set_size(14);ax.title.set_fontsize(14)
fig.tight_layout();save(fig,'constraints-overlap')
fig,ax=plt.subplots(figsize=(9.5,6));setup(ax);region(ax,BASE);boundaries(ax);dots(ax)
for p in [(8,0),(0,12)]:
 ax.scatter(*p,marker='x',s=90,color=RED,zorder=4,clip_on=False);ax.annotate(f'{p}: not feasible',p,xytext=(-90,-24) if p[0] else (8,-16),textcoords='offset points',fontsize=10,color=RED)
ax.legend(loc='upper right',frameon=True,facecolor='white');ax.set_title('Four feasible corners; not every intercept survives',loc='left',fontweight='bold',pad=16);save(fig,'feasible-vertices')
fig,axs=plt.subplots(1,2,figsize=(11,5))
setup(axs[0],7,9,xlabel='x',ylabel='y');region(axs[0],BASE,7,9);boundaries(axs[0]);axs[0].plot([6,0],[0,8],color=TEAL,lw=2.6);dots(axs[0],[(6,0),(0,8),(3,4)],TEAL);axs[0].set_title('Convex: the whole segment stays',loc='left',fontsize=12,fontweight='bold')
ax=axs[1];poly=[(0,0),(5,0),(5,1.5),(1.5,1.5),(1.5,5),(0,5)];ax.add_patch(Polygon(poly,facecolor=SOFT,edgecolor=OLIVE,lw=2));ax.plot([1,4],[4,1],color=GOLD,ls='--',lw=2.6);ax.scatter([1,4],[4,1],color=GOLD,s=55);ax.text(2.2,2.8,'This part leaves\nthe filled region.',fontsize=11,color=GOLD);ax.set_xlim(-.4,5.7);ax.set_ylim(-.4,5.7);ax.set_aspect('equal');ax.axis('off');ax.set_title('Not convex: one segment is enough',loc='left',fontsize=12,fontweight='bold');fig.tight_layout();save(fig,'convex-segments')
fig,axs=plt.subplots(1,2,figsize=(11.5,5.3))
for ax,(a,b,opt,k,title) in zip(axs,[(3,2,(4,4),20,'Maximize P = 3x + 2y'),(1,4,(0,8),32,'Maximize R = x + 4y')]):
 setup(ax,9,10,xlabel='x packs',ylabel='y packs');region(ax,BASE,9,10);boundaries(ax);dots(ax,labels=False)
 for value in ([10,16,20] if a==3 else [12,24,32]):line(ax,a,b,value,GOLD,ls='--',lw=1.6)
 ax.scatter(*opt,marker='*',s=220,color=GOLD,zorder=5,clip_on=False);ax.annotate(f'best {opt}\nvalue {k}',opt,xytext=(18,15),textcoords='offset points',color=GOLD,fontsize=11);ax.set_title(title,loc='left',fontsize=13,fontweight='bold')
fig.tight_layout();save(fig,'objective-levels')
fig,ax=plt.subplots(figsize=(9,5.5));setup(ax,9,10);region(ax,BASE,9,10);boundaries(ax);dots(ax);ax.plot([4,0],[4,8],color=GOLD,lw=6,zorder=3);ax.scatter(2,6,color=GOLD,s=90,zorder=5);ax.annotate('(2, 6): also totals 8',(2,6),xytext=(18,20),textcoords='offset points',color=GOLD);ax.set_title('Maximize x + y: an entire edge ties at 8',loc='left',fontweight='bold',pad=15);save(fig,'optimal-edge')
MIN=[(1,1,6,'ge'),(2,1,8,'ge')]
fig,ax=plt.subplots(figsize=(9.5,5.9));setup(ax,10,11,xlabel='Bundle A count, x',ylabel='Bundle B count, y');region(ax,MIN,10,11);boundaries(ax,MIN);dots(ax,[(0,8),(2,4),(6,0)]);line(ax,4,3,20,GOLD,ls='--');ax.scatter(2,4,marker='*',s=250,color=GOLD,zorder=5);ax.annotate('minimum cost $20',(2,4),xytext=(45,-22),textcoords='offset points',color=GOLD);ax.annotate('feasible region continues',xy=(9.5,10.5),xytext=(4.4,8.7),arrowprops={'arrowstyle':'->','color':TEAL,'lw':2},color=TEAL);ax.legend(loc='upper right',bbox_to_anchor=(1,.82));ax.set_title('Minimum requirements: the region extends without bound',loc='left',fontweight='bold',fontsize=13,pad=16);save(fig,'minimum-requirements')
fig,axs=plt.subplots(1,3,figsize=(12.5,4.5))
for ax in axs:setup(ax,9,9,xlabel='x',ylabel='y')
region(axs[0],BASE,9,9);boundaries(axs[0]);dots(axs[0],labels=False);axs[0].set_title('Bounded choices',loc='left',fontweight='bold',fontsize=13)
region(axs[1],[(1,1,4,'le')],9,9,color=TEAL);region(axs[1],[(1,1,6,'ge')],9,9,color=GOLD);line(axs[1],1,1,4,TEAL);line(axs[1],1,1,6,GOLD);axs[1].text(1,7.5,'x + y ≤ 4\nand x + y ≥ 6\ncannot both hold.',fontsize=11);axs[1].set_title('No feasible choices',loc='left',fontweight='bold',fontsize=13)
region(axs[2],[(1,1,6,'ge')],9,9);line(axs[2],1,1,6,TEAL);axs[2].annotate('x + y can keep growing',xy=(8.5,8.5),xytext=(1,6.5),arrowprops={'arrowstyle':'->','color':GOLD,'lw':2},color=GOLD,fontsize=10);axs[2].set_title('No finite maximum of x + y',loc='left',fontweight='bold',fontsize=12);
for ax in axs:
 ax.tick_params(labelsize=13);ax.xaxis.label.set_size(14);ax.yaxis.label.set_size(14);ax.title.set_fontsize(14)
 for t in ax.texts:t.set_fontsize(13)
fig.tight_layout();save(fig,'model-outcomes')
IC=[(1,2,8,'le'),(3,2,10,'le')]
fig,ax=plt.subplots(figsize=(9.5,6));setup(ax,4.5,5.2,xlabel='Whole batches of A, x',ylabel='Whole batches of B, y');region(ax,IC,4.5,5.2);boundaries(ax,IC)
for x,y in itertools.product(range(5),range(6)):
 if all(a*x+b*y<=c+1e-10 for a,b,c,_ in IC):ax.scatter(x,y,s=24,color=OLIVE,zorder=3)
for p,label,col,offset,marker in [((1,3.5),'Continuous best: 33',TEAL,(32,0),'*'),((1,4),'Rounded up: infeasible',RED,(45,35),'x'),((1,3),'Rounded down: 29',GOLD,(45,-13),'o'),((0,4),'Best whole plan: 32',INK,(20,68),'*')]:
 ax.scatter(*p,s=150,marker=marker,color=col,zorder=6,clip_on=False);ax.annotate(label,p,xytext=offset,textcoords='offset points',color=col,fontsize=10,arrowprops={'arrowstyle':'-','color':col})
ax.set_title('Rounding a fractional optimum is a separate decision',loc='left',fontweight='bold',pad=16);save(fig,'whole-number-plans')
WC=[(2,4,40,'le'),(1,1,14,'le')]
fig,ax=plt.subplots(figsize=(9.5,6));setup(ax,23,16,xlabel='Chairs per week, x',ylabel='Tables per week, y');region(ax,WC,23,16);boundaries(ax,WC);dots(ax,[(0,0),(14,0),(8,6),(0,10)]);line(ax,30,50,540,GOLD,ls='--');ax.scatter(8,6,marker='*',s=250,color=GOLD,zorder=5);ax.annotate('8 chairs + 6 tables\ncontribution $540',(8,6),xytext=(32,28),textcoords='offset points',color=GOLD,arrowprops={'arrowstyle':'-','color':GOLD});ax.legend(loc='upper right');ax.set_title('Workshop: two resources, one production decision',loc='left',fontweight='bold',pad=15);save(fig,'workshop-production')
fig,axs=plt.subplots(1,2,figsize=(11.5,5.7));A=np.array([2,1]);B=np.array([8,5]);C=np.array([2,7]);P=.75*A+.25*B;Q=.5*A+.25*B+.25*C
for ax in axs:setup(ax,10,9,xlabel='Coordinate 1',ylabel='Coordinate 2');ax.set_aspect('equal')
axs[0].plot([2,8],[1,5],color=TEAL,lw=3);dots(axs[0],[A,B],labels=False);axs[0].scatter(*P,s=85,color=GOLD,zorder=4);axs[0].annotate('A = (2, 1)',A,xytext=(5,-22),textcoords='offset points');axs[0].annotate('B = (8, 5)',B,xytext=(0,12),textcoords='offset points',ha='center');axs[0].annotate('P = (3.5, 2)\n0.75A + 0.25B',P,xytext=(15,-5),textcoords='offset points',color=GOLD,fontsize=10);axs[0].set_title('Two points: a segment',loc='left',fontweight='bold',fontsize=13)
axs[1].add_patch(Polygon([A,B,C],facecolor=SOFT,edgecolor=TEAL,lw=2));dots(axs[1],[A,B,C],labels=False);axs[1].scatter(*Q,s=85,color=GOLD,zorder=4)
for p,t,ofs in [(A,'A = (2, 1)',(5,-22)),(B,'B = (8, 5)',(-4,12)),(C,'C = (2, 7)',(6,12))]:axs[1].annotate(t,p,xytext=ofs,textcoords='offset points',fontsize=10)
axs[1].annotate('Q = (3.5, 3.5)\n0.50A + 0.25B + 0.25C',Q,xytext=(16,-44),textcoords='offset points',color=GOLD,fontsize=10,arrowprops={'arrowstyle':'-','color':GOLD});axs[1].set_title('Three points: a triangle',loc='left',fontweight='bold',fontsize=13);
for ax in axs:
 ax.tick_params(labelsize=12);ax.xaxis.label.set_size(13);ax.yaxis.label.set_size(13);ax.title.set_fontsize(14)
 for t in ax.texts:t.set_fontsize(12)
fig.tight_layout();save(fig,'weighted-mixtures')
print('Built 12 exact SVG/PDF figure pairs.')
