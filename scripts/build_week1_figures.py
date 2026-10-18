"""Reproducible vector diagrams for number systems, arithmetic, recursion, and token labels."""
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
OUT=Path(__file__).resolve().parents[1]/'assets/week1';OUT.mkdir(exist_ok=True)
INK='#293329';OLIVE='#536240';TEAL='#17677a';RUST='#a55c21';GOLD='#b18a22';LINE='#d8ddcd';RED='#943c2d'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':14,'axes.titlesize':14,'text.parse_math':False,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK,'svg.fonttype':'none','svg.hashsalt':'math107-week1','pdf.fonttype':42,'savefig.facecolor':'white'})
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

fig,ax=plt.subplots(figsize=(10,6),layout='constrained');ax.set_axis_off();ax.set_xlim(-.2,10.5);ax.set_ylim(-.5,6.6)
for x,y,w,h,label,c in [(0,0,10,6,'R: Real numbers', '#eef3e8'),(.3,.25,7,4.4,'Q: Rational numbers','#dfead6'),(.6,.5,4.5,2.8,'Z: Integers','#c9ddc3'),(.9,.75,2.3,1.2,'N: Naturals','#b5d4b5')]:
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.04',facecolor=c,edgecolor=OLIVE,lw=1.2));ax.text(x+.15,y+h-.4,label,fontsize=15,color=OLIVE,weight='bold')
for x,y,t in [(1.5,1.05,'1, 2, 7, …'),(3.5,1.1,'0, -5'),(5.5,2.4,'3/8, 0.6'),(8.2,3.3,'√2, π')]:ax.text(x,y,t,fontsize=17,color=INK)
ax.text(0,-.4,'Every inner box is included in every box around it.',fontsize=14,color=TEAL);finish(fig,'number-tower')

fig,ax=plt.subplots(figsize=(10,5.1),layout='constrained');ax.set_xlim(-9,13);ax.set_ylim(-.5,4);ax.set_yticks([]);ax.set_xticks(range(-8,13,2));axis(ax,'Position on the number line','');ax.grid(axis='x',color=LINE)
for y,start,end,label in [(3,-3,2,'-3 + 5 = 2'),(1.7,4,-3,'4 + (-7) = -3'),(.4,4,11,'4 - (-7) = 4 + 7 = 11')]:
 ax.plot([-8,12],[y,y],color=LINE,lw=1);ax.annotate('',xy=(end,y),xytext=(start,y),arrowprops=dict(arrowstyle='->',color=TEAL,lw=3));ax.scatter([start,end],[y,y],s=55,color=[OLIVE,TEAL],zorder=4);ax.text(-8,y+.35,label,fontsize=15,color=TEAL)
ax.set_title('Adding a signed change moves from a start to an end',loc='left',fontsize=15,weight='bold',pad=15);finish(fig,'signed-motion')

fig,ax=plt.subplots(figsize=(10,3.5),layout='constrained');axis(ax,'Temperature (degrees)','');ax.set_yticks([]);ax.set_xlim(-8,6);ax.set_ylim(0,2.5);ax.set_xticks(range(-8,7,2));ax.axhline(.9,color=LINE);ax.scatter([-5,3],[.9,.9],s=90,color=[OLIVE,TEAL],zorder=4);ax.annotate('',xy=(3,1.25),xytext=(-5,1.25),arrowprops=dict(arrowstyle='->',color=TEAL,lw=2.5));ax.text(-1,1.55,'Change: +8 degrees',ha='center',fontsize=15,color=TEAL);ax.text(-5,.45,'Start: -5',ha='center',fontsize=14);ax.text(3,.45,'End: 3',ha='center',fontsize=14);ax.set_title('A position and a change answer different questions',loc='left',fontsize=15,weight='bold',pad=15);finish(fig,'position-change')

fig,ax=plt.subplots(figsize=(10,4.9),layout='constrained');ax.set_axis_off();ax.set_xlim(-2,12);ax.set_ylim(-.6,5.2)
for y,n,d in [(4,1,2),(2.8,2,4),(1.6,3,6),(.4,50,100)]:
 ax.text(-1.7,y+.3,f'{n}/{d}',va='center',fontsize=17,color=TEAL)
 for i in range(d):ax.add_patch(Rectangle((i*10/d,y),10/d,.6,facecolor=TEAL if i<n else '#eef3e8',edgecolor='white',lw=.6))
ax.text(5,-.35,'The whole stays the same; the pieces become smaller.',ha='center',fontsize=14,color=OLIVE);ax.set_title('Equivalent fractions cover the same share',loc='left',fontsize=16,weight='bold',pad=12);finish(fig,'fraction-equivalence')

fig,ax=plt.subplots(figsize=(10,4.3),layout='constrained');ax.set_axis_off();ax.set_xlim(-2.5,14.5);ax.set_ylim(-.5,4.2)
for y,n,label in [(2.8,4,'1/3 = 4/12'),(1.6,3,'1/4 = 3/12'),(.4,7,'Sum = 7/12')]:
 ax.text(-2.2,y+.3,label,va='center',fontsize=14)
 for i in range(12):ax.add_patch(Rectangle((i,y),.94,.6,facecolor=(TEAL if y!=1.6 and i<min(n,4) else OLIVE) if i<n else '#eef3e8',edgecolor='white'))
ax.set_title('Use the same-sized pieces before adding fractions',loc='left',fontsize=15,weight='bold',pad=14);finish(fig,'common-denominator')

fig,ax=plt.subplots(figsize=(10,4.6),layout='constrained');ax.set_axis_off();ax.set_aspect('equal');ax.set_xlim(-.4,10.4);ax.set_ylim(-.8,3.8)
for row in range(3):
 for col in range(4):ax.add_patch(Rectangle((col,2-row),1,1,facecolor=TEAL if col<3 and row<2 else '#c9ddc3' if col<3 else '#eef3e8',edgecolor='white',lw=2))
ax.text(4.7,2.55,'Original amount: 3/4 = 9/12 cup',fontsize=15,color=OLIVE);ax.text(4.7,1.5,'Take 2 of its 3 rows:',fontsize=15);ax.text(4.7,.6,'(2/3) × (3/4) = 6/12 = 1/2 cup',fontsize=15,color=TEAL);ax.text(0,-.6,'The full 4-by-3 rectangle represents one cup.',fontsize=13);finish(fig,'fraction-scale')

fig,ax=plt.subplots(figsize=(10,3.6),layout='constrained');ax.set_xlim(-.2,6.3);ax.set_ylim(-.6,2.2);ax.set_yticks([]);ax.set_xticks(range(7));ax.set_xlabel('Amount (cups)',labelpad=10)
for i in range(18):ax.add_patch(Rectangle((i/3,.3),1/3,.7,facecolor=TEAL if i%3==0 else OLIVE if i%3==1 else '#b18a22',edgecolor='white',lw=1.3))
ax.text(3,1.6,'6 cups ÷ (1/3 cup per portion) = 18 portions',ha='center',fontsize=16,color=TEAL);ax.text(3,-.35,'Each small rectangle is one third-cup portion.',ha='center',fontsize=13)
for side in ['left','top','right']:ax.spines[side].set_visible(False)
finish(fig,'division-portions')

fig,ax=plt.subplots(figsize=(10,4.6),layout='constrained');axis(ax,'Position relative to zero','');ax.set_yticks([]);ax.set_xlim(-7.5,7.5);ax.set_ylim(0,4);ax.set_xticks(range(-6,7,2));ax.axvline(0,color=OLIVE,lw=1)
for y,end,label in [(3,6,'3 × 2 = 6'),(1.9,1.5,'3 × 1/2 = 1.5'),(.8,-6,'3 × (-2) = -6')]:ax.annotate('',xy=(end,y),xytext=(0,y),arrowprops=dict(arrowstyle='->',color=TEAL,lw=3));ax.scatter(end,y,s=60,color=TEAL);ax.text(-7,y+.36,label,fontsize=14,color=TEAL)
ax.set_title('Scaling changes distance from zero; a negative factor also reflects',loc='left',fontsize=14,weight='bold',pad=14);finish(fig,'scale-factors')

fig,ax=plt.subplots(figsize=(10,4.6),layout='constrained');vals=[50,55,49.5];ax.bar(range(3),vals,color=[OLIVE,TEAL,RUST],width=.55);axis(ax,'','Price ($)');ax.set_xticks(range(3),['Start','Increase 10%\n× 1.10','Decrease 10%\n× 0.90']);ax.set_ylim(0,68)
for i,v in enumerate(vals):ax.text(i,v+1.3,f'${v:.2f}',ha='center',fontsize=15)
ax.set_title('The second percentage uses a different starting amount',loc='left',fontsize=15,weight='bold',pad=14);finish(fig,'percent-round-trip')

fig,ax=plt.subplots(figsize=(8,5.5),layout='constrained');ax.set_aspect('equal');ax.set_xlim(-.4,1.8);ax.set_ylim(-.4,1.45);ax.set_axis_off();ax.add_patch(Rectangle((0,0),1,1,facecolor='#eef3e8',edgecolor=OLIVE,lw=2));ax.plot([0,1],[0,1],color=TEAL,lw=3);ax.text(.5,-.15,'1',ha='center',fontsize=17);ax.text(-.16,.5,'1',va='center',fontsize=17);ax.text(.27,.62,'√2',color=TEAL,fontsize=20);ax.text(1.12,.7,'Diagonal² = 1² + 1²\n= 2',fontsize=14,color=TEAL);ax.text(0,-.33,'√2 ≈ 1.41421, but the finite decimal is only an approximation.',fontsize=12);finish(fig,'unit-square-diagonal')

fig,ax=plt.subplots(figsize=(10,4.4),layout='constrained');ax.set_aspect('equal');ax.set_axis_off();ax.set_xlim(-.4,9);ax.set_ylim(-1.1,4.1)
for x,side,area in [(0,2,4),(3,3,9),(7.7,.5,.25)]:ax.add_patch(Rectangle((x,0),side,side,facecolor='#dcebdc',edgecolor=OLIVE,lw=2));ax.text(x+side/2,side+.22,f'Area {area:g}',ha='center',fontsize=14);ax.text(x+side/2,-.42,f'Side {side:g}',ha='center',fontsize=14,color=TEAL)
ax.text(4.2,3.75,'Square the side to find area; take the square root to recover the side.',ha='center',fontsize=13,color=OLIVE);finish(fig,'powers-and-roots')

fig,ax=plt.subplots(figsize=(8.6,5.5),layout='constrained');axis(ax,'Real part','Imaginary part');ax.set_aspect('equal');ax.set_xlim(-1.3,4.2);ax.set_ylim(-1.1,3.2);ax.set_xticks(range(-1,5));ax.set_yticks(range(-1,4));ax.axhline(0,color=OLIVE,lw=1.4);ax.axvline(0,color=OLIVE,lw=1.4);ax.plot([3,3,0],[0,2,2],ls='--',color=TEAL,lw=1.6);ax.scatter([3,0],[2,1],s=80,color=[TEAL,RUST],zorder=4);ax.text(3.12,2.13,'3 + 2i',fontsize=17,color=TEAL);ax.text(.15,1.1,'i',fontsize=17,color=RUST);ax.set_title('A complex number uses two coordinates; i² = -1',loc='left',fontsize=14,weight='bold',pad=15);finish(fig,'complex-plane')

def growth(name,start,d,r,end,title,unit='Value',step_label='Step number n',mark=None):
 n=np.arange(end+1);a=start+d*n;b=start*r**n;fig,ax=plt.subplots(figsize=(10,4.8),layout='constrained');ax.plot(n,a,'o-',color=OLIVE,ms=4,label=f'Add {d:g} each step');ax.plot(n,b,'o-',color=TEAL,ms=4,label=f'Multiply by {r:g} each step');axis(ax,step_label,unit);ax.set_xlim(0,end);ax.set_ylim(bottom=0);legend(ax,loc='upper left');ax.set_title(title,loc='left',fontsize=14,weight='bold',pad=15)
 if mark is not None:
  ax.axvline(mark,color=RUST,ls=':',lw=1.5);ax.text(mark+.3,max(max(a),max(b))*.5,f'First strict lead\nfor × {r:g}: step {mark}',fontsize=12,color=RUST)
 finish(fig,name)
growth('recursion-steps',4,3,1.5,5,'Start at 4: a constant difference versus a constant factor')
growth('recursion-comparison',1000,200,1.15,20,'Two population rules: same start, different later behavior','Model population','Year',5)
growth('growth-forecasts',2000,120,1.06,12,'Two service-demand forecasts: fixed addition and 6% growth','Model households','Month',2)
growth('savings-models',100,20,1.10,24,'Two hypothetical balances: add $20 or grow by 10%','Model balance ($)','Month',15)

fig,ax=plt.subplots(figsize=(10,4.6),layout='constrained');n=np.arange(9)
ax.plot(n,2*(.5**n),'o-',color=OLIVE,label='Start 2, multiply by 1/2');ax.plot(n,2*((-.5)**n),'o-',color=TEAL,label='Start 2, multiply by -1/2');axis(ax,'Step number n','Value');ax.set_xticks(n);ax.set_ylim(-1.5,2.7);ax.axhline(0,color=OLIVE,lw=1.2);ax.yaxis.set_major_formatter(FuncFormatter(lambda y,_:f'{y:g}'));legend(ax,loc='upper right');ax.set_title('A repeated factor can shrink a value or alternate its sign',loc='left',fontsize=14,weight='bold',pad=15);finish(fig,'shrink-and-alternate')

fig,ax=plt.subplots(figsize=(10,3.5),layout='constrained');ax.set_axis_off();ax.set_xlim(-.5,7.6);ax.set_ylim(-.6,2.7)
for i,(word,id) in enumerate(zip(['cat','sat','on','the','mat'],[42,17,8,55,91])):
 x=i*1.5;ax.add_patch(FancyBboxPatch((x,.8),1.2,.65,boxstyle='round,pad=.07',facecolor='#eef3e8',edgecolor=LINE));ax.text(x+.6,1.125,word,ha='center',va='center',fontsize=17,color=TEAL);ax.text(x+.6,.2,str(id),ha='center',fontsize=19,color=OLIVE)
ax.text(3.5,2.25,'Text order chooses the order of the IDs.',ha='center',fontsize=16);ax.text(3.5,-.4,'42, 17, 8, 55, 91 — an ordered list of labels, not amounts.',ha='center',fontsize=14);finish(fig,'token-ids')

fig,ax=plt.subplots(figsize=(10,4.7),layout='constrained');ax.set_axis_off();ax.set_xlim(-2,9);ax.set_ylim(-.5,4.7)
words=['cat','sat','on','the','mat']
for j,k in enumerate(range(2,6)):
 y=3.5-j;ax.text(-1.8,y+.2,f'Step {j}',fontsize=14);ax.text(7.4,y+.2,f'Length {k}',fontsize=14,color=OLIVE)
 for i,word in enumerate(words[:k]):ax.add_patch(Rectangle((i*1.35,y),1.2,.6,facecolor=TEAL if i==k-1 and j>0 else '#e6eddf',edgecolor='white'));ax.text(i*1.35+.6,y+.3,word,ha='center',va='center',fontsize=14,color='white' if i==k-1 and j>0 else INK)
ax.text(2.9,4.35,'Appending one token increases the length by 1.',ha='center',fontsize=15,color=TEAL);finish(fig,'token-append')

fig,ax=plt.subplots(figsize=(8.5,5.5),layout='constrained');ax.set_axis_off();ax.set_xlim(-1.1,4.3);ax.set_ylim(-.6,4.2)
for i,a in enumerate('ABC'):
 ax.text(-.65,2.5-i,a,ha='center',fontsize=17,color=OLIVE);ax.text(i+.5,3.35,a,ha='center',fontsize=17,color=OLIVE)
 for j,b in enumerate('ABC'):ax.add_patch(Rectangle((j,2-i),.94,.8,facecolor='#eef3e8',edgecolor='white'));ax.text(j+.47,2.4-i,a+b,ha='center',va='center',fontsize=17,color=TEAL)
ax.text(1.2,3.95,'Second token',ha='center',fontsize=14);ax.text(-1,1.4,'First token',rotation=90,va='center',fontsize=14);ax.text(1.2,-.4,'3 choices × 3 choices = 3² = 9 ordered strings',ha='center',fontsize=14,color=TEAL);finish(fig,'token-strings')

fig,ax=plt.subplots(figsize=(10,3.3),layout='constrained');ax.set_axis_off();ax.set_xlim(-.4,8.4);ax.set_ylim(-.5,2.3)
for i,(word,id) in enumerate(zip(['The','cat','sat','on','the','mat','.'],[4,9,12,7,3,15,1])):
 x=i*1.2;ax.add_patch(Rectangle((x,.75),1.05,.55,facecolor='#eef3e8',edgecolor=LINE));ax.text(x+.525,1.02,word,ha='center',va='center',fontsize=15,color=TEAL);ax.text(x+.525,.15,str(id),ha='center',fontsize=17,color=OLIVE)
ax.text(4,1.9,'Seven toy tokens, including the period',ha='center',fontsize=16);ax.text(4,-.4,'Capital The and lowercase the have different labels in this toy table.',ha='center',fontsize=13);finish(fig,'toy-tokenizer')

fig,ax=plt.subplots(figsize=(10,4.6),layout='constrained');n=np.arange(5);values=80*3**n;ax.plot(2*n,values,'o-',color=TEAL);axis(ax,'Weeks (one update every two weeks)','Model insects');ax.set_xticks(2*n);ax.set_ylim(0,7700)
for x,y in zip(2*n,values):ax.text(x,y+200,f'{y:,}',ha='center',fontsize=13)
ax.set_title('Tripling every two weeks: n counts updates, not individual weeks',loc='left',fontsize=14,weight='bold',pad=15);finish(fig,'insect-growth')

fig,ax=plt.subplots(figsize=(10,4.5),layout='constrained');n=np.arange(16);vals=18000-1500*n;ax.plot(n[:13],vals[:13],'o-',color=OLIVE,label='Model through zero');ax.plot(n[12:],vals[12:],'o--',color=RUST,label='Continuing the arithmetic rule');axis(ax,'Years after the starting value','Model car value ($)');ax.set_xlim(0,15);ax.set_ylim(-6000,21000);ax.axhline(0,color=OLIVE);ax.axvspan(12,15,color=RUST,alpha=.06);ax.text(7,2500,'Zero at year 12',fontsize=14,color=OLIVE);legend(ax,loc='upper right');ax.set_title('A rule can keep calculating after its setting stops making sense',loc='left',fontsize=14,weight='bold',pad=15);finish(fig,'car-value')

def path(name,values,title,unit):
 fig,ax=plt.subplots(figsize=(10,4.5),layout='constrained');n=np.arange(len(values));axis(ax,'Move number',unit);ax.set_xticks(n);ax.plot(n,values,'o-',color=TEAL,lw=2.5);ax.axhline(0,color=OLIVE,lw=1);ax.set_ylim(min(values)-5,max(values)+5)
 for i,v in enumerate(values):ax.text(i,v+1.1,str(v),ha='center',fontsize=15,color=TEAL)
 ax.set_title(title,loc='left',fontsize=15,weight='bold',pad=14);finish(fig,name)
path('diver-path',[0,-15,-7,-12],'Diver: descend 15, rise 8, descend 5','Position relative to the surface (m)')
path('hiker-path',[-6,4,-10],'Hiker: start at -6, add 10, then add -14','Trail position (units)')
os.sync()
