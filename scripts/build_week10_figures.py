"""Rebuild the exact, labeled Week 10 figures (SVG for the web, PDF for LaTeX)."""
from pathlib import Path
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyBboxPatch
import numpy as np
OUT=Path(__file__).resolve().parents[1]/'assets'/'week10'
OUT.mkdir(parents=True,exist_ok=True)
INK='#293329'; OLIVE='#536240'; GOLD='#a55c21'; TEAL='#17677a'; GRID='#deded2'; MUTED='#5a655c'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'text.color':INK,'axes.labelcolor':INK,'xtick.color':MUTED,'ytick.color':MUTED,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':GRID,'svg.fonttype':'none','pdf.fonttype':42,'savefig.facecolor':'white'})
def save(fig,name):
 fig.savefig(OUT/(name+'.svg'),bbox_inches='tight',pad_inches=.16)
 fig.savefig(OUT/(name+'.pdf'),bbox_inches='tight',pad_inches=.16)
 plt.close(fig)
def logseq(r,x,n):
 out=[x]
 for _ in range(n):x=r*x*(1-x);out.append(x)
 return out
def collatz(n):
 a=[n]
 while n!=1:n=n//2 if n%2==0 else 3*n+1;a.append(n)
 return a
def koch(n,a=0j,b=1+0j):
 if n==0:return [a,b]
 d=(b-a)/3;p=a+d;q=a+2*d;c=p+d*complex(.5,math.sqrt(3)/2)
 out=[]
 for x,y in [(a,p),(p,c),(c,q),(q,b)]:out.extend(koch(n-1,x,y)[:-1])
 return out+[b]
def triangles(n,a=np.array([0.,0.]),b=np.array([1.,0.]),c=np.array([.5,math.sqrt(3)/2])):
 if not n:return [(a,b,c)]
 ab=(a+b)/2;bc=(b+c)/2;ca=(c+a)/2
 return triangles(n-1,a,ab,ca)+triangles(n-1,ab,b,bc)+triangles(n-1,ca,bc,c)
# One rule, three different parameter choices.
fig,axs=plt.subplots(1,3,figsize=(10.4,2.8),sharey=True,layout='constrained')
for ax,r,title in zip(axs,[2.8,3.2,3.9],['Settles toward one value','Settles toward two values','Irregular over these steps']):
 s=logseq(r,.4,40);ax.plot(range(41),s,color=TEAL,lw=1.25,marker='o',ms=2.2)
 ax.set(title=f'r = {r}\n{title}',xlabel='Update number n',ylim=(-.02,1.04),xticks=[0,10,20,30,40],yticks=[0,.25,.5,.75,1]);ax.grid(axis='y',color=GRID,alpha=.7)
axs[0].set_ylabel('State xₙ');save(fig,'logistic-behaviors')
fig,ax=plt.subplots(figsize=(10,3.6),layout='constrained')
for n,color,ls in [(26,OLIVE,'--'),(27,GOLD,'-')]:
 s=collatz(n);ax.plot(range(len(s)),s,color=color,lw=2,ls=ls,label=f'Start {n}: {len(s)-1} updates; peak {max(s):,}')
 ax.scatter([len(s)-1],[1],color=color,zorder=5)
ax.set(yscale='log',xlabel='Update number (the starting value is at n = 0)',ylabel='Current integer (log scale)',xlim=(0,115),ylim=(.7,18000),yticks=[1,10,100,1000,10000]);ax.set_yticklabels(['1','10','100','1,000','10,000']);ax.grid(axis='y',color=GRID)
ax.annotate('Peak 9,232 at update 77',xy=(77,9232),xytext=(48,14000),fontsize=11,arrowprops={'arrowstyle':'->','color':GOLD});ax.legend(loc='upper left',frameon=False,fontsize=11);save(fig,'collatz-comparison')
fig,ax=plt.subplots(figsize=(9.7,2.8));ax.set(xlim=(0,10),ylim=(0,3));ax.axis('off')
def box(x,y,w,h,t,c):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.08',facecolor=c,edgecolor=GRID));ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=13)
box(.1,1.05,1.65,.8,'Current\ninteger n','#f2f4e9');box(2.45,1.05,1.7,.8,'Is n even?','#fff2db');box(5.1,1.95,1.8,.65,'Yes: n ÷ 2','#e8f2f1');box(5.1,.3,1.8,.65,'No: 3n + 1','#f9ecdf');box(7.9,1.05,1.75,.8,'Next\ninteger','#f2f4e9')
for a,b in [((1.9,1.45),(2.35,1.45)),((4.25,1.65),(5,2.2)),((4.25,1.2),(5,.65)),((7,2.2),(7.8,1.65)),((7,.65),(7.8,1.2))]:ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','lw':1.5,'color':OLIVE})
ax.text(5,-.12,'Repeat with the new integer. Stop the recorded trajectory at its first 1.',ha='center',fontsize=12);save(fig,'collatz-rule')
for which in ['koch','sierpinski']:
 fig,axs=plt.subplots(1,4,figsize=(10,2.6),layout='constrained')
 for n,ax in enumerate(axs):
  if which=='koch':
   z=koch(n);ax.plot([p.real for p in z],[p.imag for p in z],color=TEAL,lw=1.6);ax.set_ylim(-.05,.50);txt=f'{4**n} segments\nLength = {(4/3)**n:.3f}'
  else:
   for t in triangles(n):ax.add_patch(Polygon(t,closed=True,facecolor=OLIVE,edgecolor='white',linewidth=.5))
   ax.set_ylim(-.04,.92);txt=f'{3**n} filled '+('triangle' if n==0 else 'triangles')+f'\nArea = {(3/4)**n:.4f}'
  ax.set_xlim(-.03,1.03);ax.set_aspect('equal');ax.axis('off');ax.set_title(f'Stage {n}',fontweight='bold',fontsize=13);ax.text(.5,-.18,txt,transform=ax.transAxes,ha='center',va='top',fontsize=11)
 save(fig,which+'-stages')
fig,(a,b)=plt.subplots(2,1,figsize=(10,4.0),sharex=True,layout='constrained',gridspec_kw={'height_ratios':[1.6,1]})
s=logseq(3.9,.4,20);t=logseq(3.9,.4001,20);n=range(21);d=[abs(x-y) for x,y in zip(s,t)]
a.plot(n,s,color=TEAL,lw=1.8,marker='o',ms=3,label='Start 0.4000');a.plot(n,t,color=GOLD,ls='--',lw=1.8,marker='s',ms=2.5,label='Start 0.4001');a.set(ylabel='State',ylim=(0,1.03));a.legend(loc='lower left',ncol=2,framealpha=.9,fontsize=11);a.grid(axis='y',color=GRID)
b.plot(n,d,color=OLIVE,marker='o',lw=1.5,ms=3);b.axhline(.01,color=TEAL,ls=':',lw=1);b.axhline(.1,color=GOLD,ls='--',lw=1);b.scatter([8,14],[d[8],d[14]],color=[TEAL,GOLD],zorder=5);b.annotate('First > 0.01: n = 8',xy=(8,d[8]),xytext=(.02,.88),textcoords='axes fraction',fontsize=11,color=TEAL,arrowprops={'arrowstyle':'->','color':TEAL});b.annotate('First > 0.10: n = 14',xy=(14,d[14]),xytext=(.55,.88),textcoords='axes fraction',fontsize=11,color=GOLD,arrowprops={'arrowstyle':'->','color':GOLD});b.set(xlabel='Generation n',ylabel='Absolute gap',xticks=list(range(0,21,2)),ylim=(-.015,.65));b.grid(axis='y',color=GRID);save(fig,'forecast-sensitivity')
fig,axs=plt.subplots(1,2,figsize=(10,2.8),layout='constrained')
for ax,n,title in zip(axs,[1,3],['Coarse approximation: 4 segments','Finer approximation: 64 segments']):
 target=koch(5);ax.plot([z.real for z in target],[z.imag for z in target],color='#bfc7c0',lw=1)
 z=koch(n);ax.plot([p.real for p in z],[p.imag for p in z],color=GOLD,lw=1.9,marker='o',ms=2)
 ax.set_aspect('equal');ax.set(xlim=(-.02,1.02),ylim=(-.05,.4));ax.axis('off');ax.set_title(title,fontsize=13);ax.text(.5,-.12,f'Approximate length = (4/3)^{n} = {(4/3)**n:.3f} units',transform=ax.transAxes,ha='center',fontsize=11)
save(fig,'scale-measurement')
# Branch probabilities; this is a deliberately invented word-level model.
fig,ax=plt.subplots(figsize=(10,3.5),layout='constrained');ax.set(xlim=(0,10),ylim=(0,6));ax.axis('off')
ax.text(.1,3,'The light in the\nforest was ...',fontsize=13,ha='left',va='center',bbox={'boxstyle':'round,pad=.6','fc':'#f2f4e9','ec':GRID})
branches=[('moving',.45,[('slowly',.60),('away',.40)],5),('flickering',.35,[('faintly',.80),('brightly',.20)],3),('Venus',.20,[('period (.)',.90),('again',.10)],1)]
for word,p,leaves,y in branches:
 ax.annotate('',xy=(3.5,y),xytext=(2,3),arrowprops={'arrowstyle':'->','color':OLIVE});ax.text(3.6,y,f'{word}  ({p:.2f})',va='center',fontsize=13,color=TEAL)
 for i,(leaf,q) in enumerate(leaves):
  yy=y+(.36 if i==0 else -.36);ax.annotate('',xy=(6.7,yy),xytext=(5.3,y),arrowprops={'arrowstyle':'->','color':OLIVE});ax.text(6.9,yy,f'{leaf}  ({q:.2f})   →   path {p*q:.2f}',va='center',fontsize=12,color=INK)
save(fig,'ai-branches')
print('Built',len(list(OUT.glob('*.svg'))),'SVG/PDF figure pairs')
