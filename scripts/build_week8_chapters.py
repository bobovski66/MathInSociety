"""Build two standalone Week 8 chapters from the shared explanatory HTML source."""
from pathlib import Path
import re
from lxml import html
ROOT=Path(__file__).resolve().parents[1]
PAGES=ROOT/'scripts'
checks=[]
translations={'→':r'$\to$','←':r'$\leftarrow$','×':r'$\times$','÷':r'$\div$','≈':r'$\approx$','−':r'$-$','≥':r'$\ge$','≤':r'$\le$','₀':r'$_0$','₁':r'$_1$','₂':r'$_2$','ₙ':r'$_n$','ℓ':r'$\ell$','²':r'$^2$','³':r'$^3$','⁴':r'$^4$','ⁿ':r'$^n$','—':' -- ','–':'--','’':"'",'‘':"'",'“':'``','”':"''",'…':r'\ldots{}','·':r'\textperiodcentered{}','↗':''}
def esc(t):
 def plain(s):
  out=''
  for c in s:
   if c in translations:out+=translations[c]
   elif c in '&%$#_{}':out+='\\'+c
   elif c=='~':out+=r'\textasciitilde{}'
   elif c=='^':out+=r'\textasciicircum{}'
   elif c=='\\':out+=r'\textbackslash{}'
   elif c=='<':out+=r'\textless{}'
   elif c=='>':out+=r'\textgreater{}'
   else:out+=c
  return out
 parts=re.split(r'(\\\(.*?\\\)|\\\[.*?\\\])',t or '',flags=re.S)
 return ''.join(x if x.startswith(('\\(','\\[')) else plain(x) for x in parts)
def children(e):return esc(e.text)+''.join(conv(c)+esc(c.tail) for c in e)
def conv(e):
 tag=e.tag;cls=e.get('class','');content=lambda:children(e)
 if tag in ['script','style','button','nav'] or 'no-print' in cls:return ''
 if tag=='figure':
  img=e.find('img');name=Path(img.get('src')).stem;cap=e.find('figcaption')
  return '\n\\par\\medskip\\noindent\\begin{minipage}{\\linewidth}\n\\centering\\includegraphics[width=\\linewidth,height='+('3.8' if name in ['feasible-vertices','whole-number-plans','workshop-production'] else '3.2')+'in,keepaspectratio]{../assets/week8/'+name+'.pdf}\n\\captionof*{figure}{'+children(cap)+'}\n\\end{minipage}\\par\\medskip\n'
 if tag=='img':return ''
 if tag=='h2':return '\n\\Needspace{6\\baselineskip}\\section{'+content()+'}\n'
 if tag=='h3':return '\n\\Needspace{5\\baselineskip}\\subsection*{'+content()+'}\n'
 if tag=='h4':return '\n\\paragraph{'+content()+'}\n'
 if tag=='p':return '\n'+content()+'\n\n'
 if tag=='em':return r'\emph{'+content()+'}'
 if tag=='strong':return r'\textbf{'+content()+'}'
 if tag=='code':return r'\texttt{'+content()+'}'
 if tag=='a':
  url=e.get('href','')
  if url.startswith('http'):return r'\href{'+url+'}{'+content()+'}'
  return content()
 if tag in ['ul','ol']:
  env='itemize' if tag=='ul' else 'enumerate'
  return '\n\\begin{'+env+'}\n'+content()+'\n\\end{'+env+'}\n'
 if tag=='li':return '\\item '+content()+'\n'
 if tag=='table':
  rows=e.xpath('.//tr');n=max(len(r) for r in rows)
  out='\n\\par\\medskip{\\small\\renewcommand{\\arraystretch}{1.35}\\begin{tabularx}{\\linewidth}{@{}'+'Y'*n+'@{}}\\toprule\n'
  for i,row in enumerate(rows):out+=' & '.join(children(c) for c in row)+r'\\'+'\n'+('\\midrule\n' if i==0 else '')
  return out+'\\bottomrule\\end{tabularx}}\\par\\medskip\n'
 if tag=='details':
  summary=e.find('summary');body=esc(e.text)+''.join(conv(c)+esc(c.tail) for c in e if c.tag!='summary')
  return '\n\\begin{tcolorbox}[title={'+children(summary)+'},colback=warm,colbacktitle=warm,coltitle=gold,colframe=gold!35,breakable]\n'+body+'\n\\end{tcolorbox}\n'
 if tag=='summary':return ''
 if tag=='div' and 'quick-check' in cls:
  p=e.find('p');answer=e.find('details');num=len(checks)+1
  checks.append((children(p),''.join(conv(c) for c in answer if c.tag!='summary')))
  return '\n\\begin{tcolorbox}[title={Pause and try '+str(num)+'},breakable]\n'+children(p)+'\n\\end{tcolorbox}\n'
 if tag=='div' and cls in ['eyebrow','kicker','meta']:return ''
 if tag=='div' and ('example' in cls or 'insight' in cls):
  h=e.find('h3');title=children(h) if h is not None else ''
  body=esc(e.text)+''.join(conv(c)+esc(c.tail) for c in e if c is not h)
  opts=',colback=warm,colbacktitle=warm,coltitle=gold,colframe=gold!35' if 'insight' in cls else ''
  return '\n\\begin{tcolorbox}[title={'+title+'},breakable'+opts+']\n'+body+'\n\\end{tcolorbox}\n'
 return content()
cover1=r'''
\begin{document}
{\small\sffamily\color{olive}WEEK 8 / PART I / CONVEX GEOMETRY\par}
\vspace{10pt}
{\fontsize{31}{35}\selectfont\bfseries\color{olive}What is possible?\par}
\vspace{8pt}
{\large Turn resource limits into a picture of allowable plans. Learn what a point means, what a boundary means, and why every condition must hold.\par}
\begin{center}\includegraphics[width=\linewidth]{../assets/week8/constraints-overlap.pdf}\end{center}
\begin{tcolorbox}[title={The setting for the week}]
A school club makes two kinds of snack packs. It has eight packing slots and twelve ingredient portions. Type A uses twice as many portions as type B. Which complete production plans can it actually carry out?
\end{tcolorbox}
Week 7 compared costs, revenue, and profit. Here we add limits. Use multiplication, fractions, coordinate pairs, and simple equations to describe what is allowed before choosing what is best. No previous study of linear programming is assumed.

By the end of Part I, you can define variables and units, test a plan, draw a boundary and its permitted side, locate every feasible corner, and explain why the continuous region is convex. Part II uses that region to compare objectives and identify the limits of the method.

\medskip
\href{https://bobovski66.github.io/MathInSociety/readings/week8_reading.html}{Complete online reading}\quad\textperiodcentered\quad\href{https://bobovski66.github.io/MathInSociety/demos/convex_geometry.html}{Feasible-region explorer}\quad\textperiodcentered\quad\href{https://bobovski66.github.io/MathInSociety/labs/week8_lab.html}{Guided laboratory}
'''
cover2=r'''
\begin{document}
\setcounter{section}{5}
{\small\sffamily\color{olive}WEEK 8 / PART II / LINEAR PROGRAMMING\par}
\vspace{10pt}
{\fontsize{31}{35}\selectfont\bfseries\color{olive}Which plan is best?\par}
\vspace{8pt}
{\large Keep the allowable choices fixed, state a goal, and compare the consequences. A mathematical optimum answers the question you actually put into the model.\par}
\begin{center}\includegraphics[width=\linewidth]{../assets/week8/objective-levels.pdf}\end{center}
\begin{tcolorbox}[title={From geometry to a decision}]
The club's feasible region has corners $(0,0),(6,0),(4,4),(0,8)$. With contribution $P=3x+2y$, four packs of each type give the largest total. A different goal can choose a different corner, or leave an entire edge tied.
\end{tcolorbox}
Part I developed the variables, inequalities, and feasible geometry. Part II combines them with an objective. We study maximum and minimum values, tied solutions, infeasible models, unbounded scores, and whole-number restrictions. Worked examples and review solutions show how to verify each conclusion.

For the core method you need only substitution and comparison. Equal-score lines and convex mixtures explain why the method works. The whole-number investigation is an extension.

\medskip
\href{https://bobovski66.github.io/MathInSociety/readings/week8_reading.html}{Online reading}\quad\textperiodcentered\quad\href{https://bobovski66.github.io/MathInSociety/demos/linear_programming.html}{Optimizer}\quad\textperiodcentered\quad\href{https://bobovski66.github.io/MathInSociety/labs/week8_optimization_lab.html}{Optimization extension}
'''
review1=r'''
\clearpage
\section*{Part I Review}
Use nonnegative real coordinates unless the question explicitly asks for whole numbers. Show a substitution, boundary calculation, or segment argument.
\begin{enumerate}
\item Define variables for a workshop making chairs and tables. What does the plan $(5,2)$ mean? Explain why $(2,5)$ is different.
\item A type-A item uses 3 labor-hours and a type-B item 2. Write a 60-hour upper limit with units. Test $(10,10)$ and $(15,8)$ and report slack or the shortfall.
\item For $x+2y\leq8$, find both boundary intercepts. Identify the permitted side by testing a point off the boundary. Classify $(2,3)$ and $(4,3)$.
\item Find every feasible corner for $x+y\leq7$, $2x+y\leq10$, $x,y\geq0$. Show the intersection calculation. Why is $(7,0)$ not a corner of the feasible region?
\item Find the corners for $3x+2y\leq120$, $x+2y\leq60$, $x,y\geq0$. Test $(20,20)$ and $(25,20)$ against both resource limits.
\item For the workshop constraints $2x+4y\leq40$, $x+y\leq14$, find the four corners. Check proposed plans $(8,5)$ and $(10,5)$.
\item Which sets are convex: a filled disk, a circle's circumference alone, a filled rectangle, a ring, a line segment? Explain a counterexample segment for each nonconvex set.
\item Why is an intersection of convex sets convex? Give a counterexample showing that a union need not be convex.
\item For the club's region, average $(6,0)$ and $(0,8)$. Check the resulting plan against $x+y\leq8$ and $2x+y\leq12$. Why need a midpoint of two whole-number plans not be a whole-number plan?
\item Keep the club's packing limit at 8 and raise the ingredient allowance from 12 to 16. Do old feasible plans remain feasible? Give one newly feasible plan.
\item If $x+y\leq8$ is already imposed, does adding $x+y\leq10$ remove any choices? What does it mean for a constraint to be redundant?
\item Describe the feasible sets for (a) $x+y\leq4$ and $x+y\geq6$; (b) $x+y\leq0$ with $x,y\geq0$. Why should we not assume every system creates a filled four-sided polygon?
\end{enumerate}
'''
answers1=r'''
\subsection*{Part I Review: solutions}
\begin{enumerate}
\item Let $x$ count chairs per week and $y$ tables per week. $(5,2)$ means five chairs and two tables. Switching the coordinates switches the products, which may change resource use and value.
\item $3x+2y\leq60$ hours, where the coefficients are hours per item. $(10,10)$ uses $30+20=50$ hours, leaving 10. $(15,8)$ uses $45+16=61$ hours and exceeds the allowance by 1.
\item Intercepts are $(8,0)$ and $(0,4)$. The origin gives $0\leq8$, so its side is permitted. $(2,3)$ is on the included boundary; $(4,3)$ is outside because its total is 10.
\item Subtract $x+y=7$ from $2x+y=10$: $x=3$, then $y=4$. Corners are $(0,0),(5,0),(3,4),(0,7)$. $(7,0)$ uses 14 under the second limit, exceeding 10.
\item Subtract the resource equations to get $2x=60$, so $x=30,y=15$. Corners are $(0,0)$, $(40,0)$, $(30,15)$, and $(0,30)$. At $(20,20)$, use is 100 and 60: feasible. At $(25,20)$, use is 115 and 65: the second limit fails.
\item Divide the first boundary by 2 and subtract $x+y=14$ from $x+2y=20$, obtaining $y=6,x=8$. Corners are $(0,0),(14,0),(8,6),(0,10)$. $(8,5)$ uses 36 wood units and 13 slots: feasible. $(10,5)$ uses 40 wood units but 15 slots: infeasible.
\newpage
\item The filled disk, filled rectangle, and line segment are convex. Opposite points of a circle's circumference have a segment through the missing interior. Opposite sides of a ring have a segment through the hole. These counterexamples establish nonconvexity.
\item If two points lie in every set, their joining segment lies in every convex set and thus in the intersection. For a union, take two separated filled rectangles and join a point of one to a point of the other: the segment crosses a gap.
\item The midpoint is $(3,4)$, using 7 slots and 10 ingredient portions. It is feasible. But the midpoint of whole-number points $(1,0)$ and $(0,1)$ is $(0.5,0.5)$, which is not a whole-number plan.
\item Every old feasible plan remains feasible because the ingredient upper limit is relaxed. $(8,0)$ is newly feasible: it uses 8 slots and 16 portions.
\item No choices are removed: a total at most 8 is automatically at most 10. A redundant constraint adds no restriction beyond those already imposed.
\item (a) The set is empty: one total cannot be at most 4 and at least 6. (b) Only $(0,0)$ is feasible. Other systems can produce triangles, larger polygons, line segments, or unbounded sets. The shape must be established from the actual conditions.
\end{enumerate}
\subsection*{Continue with Part II}
Now add an objective to the feasible region. The online optimizer and Part II explain which conditions justify a corner comparison, what ties mean, and why the best continuous plan may not be a usable whole-number plan.
}
\end{document}
'''
extra2=r'''
\clearpage
\section*{Further Worked Models}
\subsection*{Furniture: compare every feasible corner}
A furniture maker produces chairs $x$ and desks $y$ per week. Two resource constraints are $2x+3y\leq120$ and $x+2y\leq70$, with nonnegativity. Maximize contribution $P=40x+70y$.

The first boundary has intercepts $(60,0)$ and $(0,40)$; the second has $(70,0)$ and $(0,35)$. The tighter axis limits give $(60,0)$ and $(0,35)$. To find the non-axis intersection, double $x+2y=70$ and subtract $2x+3y=120$: $y=20$, then $x=30$.

{\renewcommand{\arraystretch}{1.35}\begin{tabularx}{\linewidth}{@{}YYYY@{}}\toprule
Corner & First resource & Second resource & Contribution\\\midrule
$(0,0)$ & 0 & 0 & \$0\\
$(60,0)$ & 120 & 60 & \$2,400\\
$(30,20)$ & 120 & 70 & \$2,600\\
$(0,35)$ & 105 & 70 & \$2,450\\\bottomrule
\end{tabularx}}

All four corners pass both limits. The maximum is \$2,600 at 30 chairs and 20 desks. The plan and its value are different quantities; both belong in the recommendation.

\subsection*{A resource limit can be redundant}
Suppose a different model has limits $x+2y\leq20$ and $x+2y\leq24$. Every point passing the first also passes the second. The second is redundant. This differs from merely having slack at one plan: a constraint can be slack at a particular optimum yet still exclude other choices elsewhere.

\clearpage
\subsection*{A third real constraint can create a fifth corner}
A print shop has three limits:
\[
x+2y\leq60,\quad x+y\leq40,\quad2x+y\leq70,\quad x,y\geq0.
\]
Here $x$ counts posters and $y$ banners. Maximize the invented contribution $P=15x+35y$.

Intersect the first two non-axis boundaries to get $(20,20)$; the third total is 60, so it passes. Intersect the second and third to get $(30,10)$; the first total is 50, so it passes. The first and third meet at $(80/3,50/3)$, but this candidate has $x+y=130/3>40$, so it must be discarded.

The x-axis corner is $(35,0)$: the third constraint is tighter there than the other two. The y-axis corner is $(0,30)$: the first constraint is tighter there. Together with the origin and the two valid non-axis intersections, these give five corners.

{\renewcommand{\arraystretch}{1.35}\begin{tabularx}{\linewidth}{@{}YYY@{}}\toprule
Feasible corner & Calculation & Contribution\\\midrule
$(0,0)$ & $15(0)+35(0)$ & \$0\\
$(35,0)$ & $15(35)+35(0)$ & \$525\\
$(30,10)$ & $15(30)+35(10)$ & \$800\\
$(20,20)$ & $15(20)+35(20)$ & \$1,000\\
$(0,30)$ & $15(0)+35(30)$ & \$1,050\\\bottomrule
\end{tabularx}}

The maximum is \$1,050 at $(0,30)$. All three resource constraints matter to this feasible region; none is redundant. A calculation at a visually prominent intersection, such as $(20,20)$, is not a substitute for comparing all corners.

\begin{tcolorbox}[title={A useful distinction}]
A constraint is \emph{binding at a plan} when it holds with equality there. It is \emph{redundant in a model} when removing it leaves the entire feasible set unchanged. These are different claims.
\end{tcolorbox}
'''
review2=r'''
\clearpage
\section*{Part II Review}
Use nonnegative variables and included boundaries. Show a corner table or explicit calculation and report both a plan and its objective value.
\begin{enumerate}
\item For the club's corners $(0,0),(6,0),(4,4),(0,8)$, maximize $P=3x+2y$. What is the minimum if there is no lower production requirement?
\item On the same region, maximize $R=x+4y$ and then $T=x+y$. Describe the complete optimal edge for $T$, including its whole-number points.
\item Maximize $f=5x+8y$ subject to $x+2y\leq16$, $3x+2y\leq24$. Find all corners and compare. Check resource use at the best plan.
\item Minimize $C=3x+5y$ subject to $x+y\geq8$, $2x+y\geq10$. Find the boundary vertices. Explain why the mixed boundary intersection is not automatically best.
\item For the furniture model in the worked example, compare the best plan with producing only desks. Does the higher per-item contribution determine the answer by itself?
\item For the three-limit print shop, why is $(80/3,50/3)$ not a feasible corner? Which corner maximizes $15x+35y$?
\item A toy workshop has $3x+y\leq120$, $x+2y\leq80$, and contribution $P=8x+5y$. Find the corners and best plan. Then change the contribution to $5x+8y$ and compare.
\item A municipality divides an invented \$500-thousand budget between roads $x$ and parks $y$, measured in thousands of dollars. Require $x\geq100$, $y\geq80$, $x+y\leq500$. Maximize an invented score $S=3x+4y$. What does the score leave for people to decide?
\item A polygon has corners $(0,0),(8,0),(5,4),(0,6)$. For cost $C=4x+6y$, which of the three listed nonzero corners is cheapest? Why is that not the minimum over the full polygon? Give a different positive feasible plan with lower cost.
\item For $x+2y\leq8$, $3x+2y\leq10$, maximize $5x+8y$ continuously and then using whole numbers. Check rounding up and rounding down from the continuous best point.
\item Compute $0.75A+0.25B$ for $A=(2,1),B=(8,5)$. Add $C=(2,7)$ and normalize amounts $2,1,1$. Where do the resulting points lie? Why do weights $1.2,-0.2$ fail the convex-combination test?
\item Explain the difference between an infeasible model and an unbounded objective. Give an example of an unbounded region with a finite minimum. Explain why $0\leq x<1$ has no largest allowable x.
\item Keep $x+y\leq8$ and increase the club's ingredient allowance from 12 to 16, then 20. Maximize $3x+2y$ at each stage. Why does the extra ingredient allowance eventually stop helping?
\item Recommend a plan for the original chair-and-table workshop with wood limit 40, assembly limit 14, and contribution $30x+50y$. Use resource totals and a comparison with another feasible plan. Name a relevant missing feature.
\end{enumerate}
'''
answers2=r'''
\subsection*{Part II Review: solutions}
\begin{enumerate}
\item Corner values are $0,18,20,16$. Maximum \$20 is at $(4,4)$. With only upper limits and nonnegativity, minimum contribution is 0 at zero production. A minimum-cost model may need minimum service requirements.
\item R-values are $0,6,20,32$, so $(0,8)$ is best. T reaches 8 along the edge from $(4,4)$ to $(0,8)$. Its whole-number plans are $(0,8),(1,7),(2,6),(3,5),(4,4)$.
\item Subtraction gives $x=4,y=6$. Corners are $(0,0),(8,0),(4,6),(0,8)$; scores are $0,40,68,64$. The maximum is 68 at $(4,6)$, using 16 units of the first resource and 24 of the second.
\item Corners are $(8,0),(2,6),(0,10)$, with costs $24,36,50$. The minimum is 24 at $(8,0)$. It provides 8 of the first requirement and 16 of the second, exceeding its 10-unit minimum by 6. A feasible axis corner can outperform a mixed intersection.
\item $(30,20)$ gives \$2,600; desks only gives $(0,35)$ and \$2,450. The best mix depends on both resource limits, not just the larger contribution per item.
\item That intersection has $x+y=130/3>40$ and violates the middle constraint. The maximum is \$1,050 at $(0,30)$, which passes all three limits.
\item Corners are $(0,0),(40,0),(32,24),(0,40)$. Original scores are $0,320,376,200$, so $(32,24)$ is best at 376. Under $5x+8y$, scores are $0,200,352,320$; the same plan remains best but its score changes. Changing an objective need not always move the optimum.
\item Corners are $(100,80),(420,80),(100,400)$. Scores are $620,1580,1900$. The score selects roads \$100,000 and parks \$400,000. Its coefficients and minimum allocations are modeling choices, not facts establishing what a community ought to value.
\item The three costs are 32,44,36, so $(8,0)$ is cheapest among those candidates. The full polygon includes $(0,0)$ at cost 0 and, for example, $(1,0)$ at cost 4. A real production floor needs an explicit constraint, not deletion of one point.
\item Continuous maximum 33 is at $(1,3.5)$. Rounding up to $(1,4)$ gives resource totals 9 and 11, both too large. Rounding down to $(1,3)$ is feasible but scores 29. The best whole plan is $(0,4)$ at 32; enumerate y-values 0--4 to verify.
\item The first point is $(3.5,2)$, on the A--B segment. Normalized amounts give weights $(0.5,0.25,0.25)$ and point $(3.5,3.5)$ inside the triangle. A negative weight violates nonnegativity even if the weights sum to 1.
\item Infeasible means no plan satisfies every condition. Unbounded objective means feasible plans improve the score without finite limit. The supply-order model $x+y\geq6$, $2x+y\geq8$ has unbounded choices but minimum $4x+3y=20$ at $(2,4)$. Under $0\leq x<1$, any allowed x can be increased while remaining below 1; the limiting bound 1 is excluded.
\item With allowance 12, the maximum is 20 at $(4,4)$. At 16 and 20, it is 24 at $(8,0)$. The packing limit permits at most eight packs, and each contributes at most 3; no plan can exceed 24 while that limit stays fixed. Beyond 16, the ingredient constraint is redundant.
\item Produce 8 chairs and 6 tables: wood use $2(8)+4(6)=40$, assembly use $8+6=14$, contribution \$540. Ten tables alone are feasible but contribute \$500. Demand, waste, setup time, resource uncertainty, and variable production rates are examples of missing features that could change a real recommendation.
\end{enumerate}
\subsection*{Optional primary source for the AI connection}
Vaswani et al., \href{https://arxiv.org/html/1706.03762v7#S3.SS2}{\emph{Attention Is All You Need}, Section 3.2}. The geometry applies to the normalized weighted value combination at that step; later transformations can move a representation beyond the original hull. The vectors and weights in this unit are constructed examples.
}
\end{document}
'''
if __name__=='__main__':
 tree=html.fromstring((ROOT/'readings/week8_reading.html').read_text())
 groups=[('I','Feasible Choices and Convex Geometry','Math107_Chapter_08.tex',cover1,['plans','inequalities','halfplanes','vertices','convexity'],review1,answers1),('II','Best Choices and Linear Programming','Math107_Chapter_09.tex',cover2,['objectives','corners','ties','minimum','outcomes','integers','mixtures','decisions'],review2,answers2)]
 for part,topic,filename,cover,ids,review,answers in groups:
  checks.clear();preamble=(PAGES/'week8_chapter_preamble.tex').read_text().replace('@PART@',part).replace('@TOPIC@',topic);chunks=[preamble,cover,'\n\\clearpage\n']
  for id in ids:
   text=conv(tree.get_element_by_id(id))
   if id=='integers':text=text.replace(r'\section{A fractional optimum is a useful bound, not an automatic plan}',r'\section*{Extension: whole-number plans}')
   chunks.append(('\n\\clearpage\n' if id in ['halfplanes','vertices','minimum','integers','mixtures'] else '\n')+text)
  if part=='II':chunks.append(extra2)
  chunks.extend([review,'\n\\clearpage\n{\\setlength{\\parskip}{4pt}\\setlist{itemsep=4pt,topsep=3pt}\\titlespacing*{\\paragraph}{0pt}{5pt}{.75em}\n\\section*{Solutions and Reasoning}\n'])
  for i,(_,answer) in enumerate(checks,1):chunks.append('\n\\paragraph{Short check '+str(i)+'.} '+answer)
  chunks.append('\n'+answers);out=ROOT/'readings'/filename;out.write_text('\n'.join(line.rstrip() for line in ''.join(chunks).splitlines())+'\n');print('Built Part',part,'with',len(checks),'short checks:',out.name)

from chapter_editorial import polish_generated_chapters
polish_generated_chapters([ROOT / "readings/Math107_Chapter_08.tex", ROOT / "readings/Math107_Chapter_09.tex"])
