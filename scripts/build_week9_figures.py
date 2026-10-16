"""Build exact vector diagrams for the Week 9 network investigations."""
from pathlib import Path
from io import BytesIO
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/week9';OUT.mkdir(exist_ok=True)
INK='#293329';OLIVE='#536240';TEAL='#17677a';GOLD='#a55c21';PALE='#d8ddcd';RED='#943c2d';SOFT='#eaf0e2'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':INK,'axes.labelcolor':INK,'svg.fonttype':'none','pdf.fonttype':42,'savefig.facecolor':'white'})
N=list('ABCDEFG');E=['AB','AC','BC','BD','CD','DE','EF','EG','FG']
P={'A':(.5,1.5),'B':(2.1,2.8),'C':(2.1,.2),'D':(3.7,1.5),'E':(5.5,1.5),'F':(7.1,2.7),'G':(7.1,.3)}
LOC={'A':'Coordinator','B':'Library','C':'Clinic','D':'School','E':'Shelter','F':'North Block','G':'Community Center'}
def key(e):return ''.join(sorted(e))
def graph(ax,edges=E,active=(),new=(),path=(),labels=False,rounds=None,ghost=(),r=.24,pos=None):
 p=P if pos is None else pos
 ax.set_xlim(-.05,7.7);ax.set_ylim(-.65,3.5);ax.set_aspect('equal');ax.axis('off')
 paths={key(e) for e in path}
 for uv in ghost:
  u,v=uv;ax.plot([p[u][0],p[v][0]],[p[u][1],p[v][1]],color=RED,lw=2,ls=(0,(3,3)),zorder=0)
 for uv in edges:
  u,v=uv;ax.plot([p[u][0],p[v][0]],[p[u][1],p[v][1]],color=GOLD if key(uv) in paths else PALE if active else OLIVE,lw=3.5 if key(uv) in paths else 2,zorder=1)
 for n in N:
  x,y=p[n];fill=TEAL if n in active else OLIVE if not active else '#f4f5ee'
  ax.add_patch(Circle((x,y),r,facecolor=fill,edgecolor=INK if n in new else fill,lw=2.5,zorder=3))
  if n in new:ax.add_patch(Circle((x,y),r+.065,fill=False,edgecolor=GOLD,lw=1.7,zorder=3))
  ax.text(x,y,n,ha='center',va='center',color='white' if n in active or not active else INK,fontsize=12,fontweight='bold',zorder=4)
  if labels:ax.text(x,y-r-.2,LOC[n],ha='center',va='top',fontsize=9)
  if rounds is not None:ax.text(x,y-r-.14,f'round {rounds[n]}',ha='center',va='top',fontsize=9,color=TEAL)
def save(fig,name):
 for fmt in ['svg','pdf']:
  buf=BytesIO()
  opts={'metadata':{'CreationDate':None,'ModDate':None}} if fmt=='pdf' else {}
  fig.savefig(buf,format=fmt,bbox_inches='tight',pad_inches=.14,**opts)
  final=OUT/(name+'.'+fmt);tmp=OUT/(name+'.'+fmt+'.tmp')
  with tmp.open('wb') as f:
   f.write(buf.getvalue());f.flush();os.fsync(f.fileno())
  tmp.replace(final)
 plt.close(fig)
fig,ax=plt.subplots(figsize=(11,4.8));graph(ax,labels=True,path=['DE']);ax.text(4.6,1.85,'D–E: one link between regions',ha='center',fontsize=10,color=GOLD);ax.set_title('Seven locations. Nine two-way communication links.',loc='left',fontweight='bold',pad=10);fig.text(.13,.04,'The drawing shows who can contact whom directly. It is not a geographic map.',fontsize=10,color=TEAL);save(fig,'community-network')
fig,axs=plt.subplots(1,2,figsize=(11,4));allpairs=[u+v for i,u in enumerate(N) for v in N[i+1:]]
for ax,edges,title in zip(axs,[allpairs,E],['All possible pairs: 21 links','Links actually present: 9']):
 graph(ax,edges,pos={n:(3.8+3.1*np.cos(np.pi/2+2*np.pi*i/7),1.4+1.7*np.sin(np.pi/2+2*np.pi*i/7)) for i,n in enumerate(N)});ax.set_title(title,loc='left',fontsize=13,fontweight='bold')
fig.text(.13,.06,'Density = present ÷ possible = 9 ÷ 21 ≈ 0.429 = 42.9%',color=TEAL,fontsize=12);save(fig,'density-pairs')
fig,ax=plt.subplots(figsize=(11,4.8));dist={'A':0,'B':1,'C':1,'D':2,'E':3,'F':4,'G':4};graph(ax,active=N,path=['AB','BD','DE','EG'],rounds=dist);ax.set_title('Shortest-path distance from A = earliest arrival round',loc='left',fontweight='bold',pad=8);fig.text(.13,.05,'Highlighted route: A → B → D → E → G. Four links, so length 4.',fontsize=11,color=GOLD);save(fig,'path-layers')
fig,axs=plt.subplots(1,2,figsize=(11,4.6));cut=[e for e in E if e!='DE'];graph(axs[0],cut,active=list('ABCD'),ghost=['DE']);graph(axs[1],cut+['DF'],active=N,path=['AB','BD','DF','FG'],ghost=['DE']);axs[0].set_title('D–E fails: two components',loc='left',fontweight='bold',fontsize=12);axs[1].set_title('Add D–F: an alternate route survives',loc='left',fontweight='bold',fontsize=12);fig.text(.13,.09,'Left: A cannot reach E, F, or G.   Right: A → B → D → F → G still reaches G.',fontsize=10,color=TEAL);fig.text(.13,.03,'Dashed D–E is unavailable in both pictures. A new D–F link supplies the second route.',fontsize=9);save(fig,'failure-repair')
fig,axs=plt.subplots(2,3,figsize=(11,6.5));rounds=[['A'],list('ABC'),list('ABCD'),list('ABCDE'),N];new=[['A'],['B','C'],['D'],['E'],['F','G']]
for i,ax in enumerate(axs.flat):
 if i<5:
  graph(ax,active=rounds[i],new=new[i]);ax.set_title(f'Round {i} · '+('start A' if i==0 else 'new: '+', '.join(new[i])),loc='left',fontsize=11,fontweight='bold')
 else:
  ax.axis('off');ax.text(.02,.65,'One link per round.\nNewly informed locations wait\nuntil the next round to relay.\n\nA gold ring marks a first arrival.',transform=ax.transAxes,fontsize=11,va='top',linespacing=1.6)
fig.tight_layout(h_pad=1.7);save(fig,'diffusion-rounds')
fig,axs=plt.subplots(2,3,figsize=(11,6.6));cases=[[list('BC'),list('ABCD'),list('ABCD')],[list('BCF'),list('ABCDFG'),N]]
for row in range(2):
 for col in range(3):
  now=cases[row][col];fresh=now if col==0 else [n for n in now if n not in cases[row][col-1]]
  graph(axs[row,col],active=now,new=fresh);axs[row,col].set_title(f'Round {col} · {len(now)} active'+(' (stopped)' if row==0 and col==2 else ''),loc='left',fontsize=11,fontweight='bold')
fig.text(.12,.97,'Seeds B, C: the cascade stops before E',fontsize=12,color=TEAL,fontweight='bold');fig.text(.12,.49,'Add F as a seed: the cascade reaches all seven locations',fontsize=12,color=TEAL,fontweight='bold');fig.subplots_adjust(hspace=.7,top=.89,bottom=.03);save(fig,'threshold-cascade')
fig,ax=plt.subplots(figsize=(10.5,4));ax.set_xlim(-.6,7);ax.set_ylim(-1.1,2.9);ax.set_aspect('equal');ax.axis('off');p={'A':(0,1),'B':(3,2.4),'D':(6,1),'C':(2,-.2),'E':(4,-.2)}
for u,v,w in [('A','B',12),('B','D',12),('A','C',4),('C','E',4),('E','D',4)]:
 a,b=p[u],p[v];ax.plot([a[0],b[0]],[a[1],b[1]],color=GOLD if w==12 else TEAL,lw=3);x,y=(np.array(a)+np.array(b))/2;ax.text(x,y+.16,str(w)+' min',ha='center',fontsize=10,bbox={'facecolor':'white','edgecolor':'none','pad':2})
for n,(x,y) in p.items():ax.add_patch(Circle((x,y),.23,color=OLIVE,zorder=3));ax.text(x,y,n,ha='center',va='center',fontweight='bold',color='white',zorder=4)
ax.set_title('Fewest links and least time answer different questions',loc='left',fontweight='bold',fontsize=13);fig.text(.13,.035,'A–B–D: 2 links, 24 minutes.     A–C–E–D: 3 links, 12 minutes.',color=TEAL,fontsize=11);save(fig,'weighted-routes')
fig,ax=plt.subplots(figsize=(11,5.9));ax.set_xlim(-.8,8.1);ax.set_ylim(-1.45,3.1);ax.set_aspect('equal');ax.axis('off')
p={'x₁':(0,2),'x₂':(0,0),'H₁':(4,2),'H₂':(4,0),'O':(7,1)}
links=[('x₁','H₁',.5,(1.8,2.27)),('x₂','H₁',.25,(2.85,1.12)),('x₁','H₂',-.5,(1.15,1.12)),('x₂','H₂',.75,(1.8,-.28)),('H₁','O',1.5,(5.5,1.82)),('H₂','O',-.5,(5.5,.18))]
for u,v,w,t in links:
 color=TEAL if w>0 else GOLD;ax.add_patch(FancyArrowPatch(p[u],p[v],shrinkA=24,shrinkB=24,arrowstyle='-|>',mutation_scale=17,lw=2.2,color=color,linestyle='-' if w>0 else (0,(5,3)),zorder=1));ax.text(*t,('× ' if w>0 else '× −')+f'{abs(w):.2f}',fontsize=11,ha='center',va='center',color=color,bbox={'facecolor':'white','edgecolor':'none','pad':3},zorder=2)
for n,(x,y) in p.items():
 ax.add_patch(Circle((x,y),.33,color=OLIVE,zorder=3));ax.text(x,y,n,color='white',fontsize=14,ha='center',va='center',zorder=4,fontweight='bold');ax.text(x,y-.6,'value '+str({'x₁':2,'x₂':4,'H₁':2,'H₂':2,'O':2}[n]),fontsize=11,ha='center',color=TEAL)
for x,t in [(0,'Inputs'),(4,'Hidden layer'),(7,'Output')]:ax.text(x,2.85,t,ha='center',fontweight='bold',fontsize=12)
ax.text(3.7,-1.18,'At each receiving node: multiply along each incoming arrow, then add.',ha='center',fontsize=11,color=TEAL);save(fig,'neural-signals')
print('Built 8 exact SVG/PDF figure pairs in',OUT)
