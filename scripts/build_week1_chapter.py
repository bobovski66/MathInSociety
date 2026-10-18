"""Build the illustrated introductory chapter and all 28 original practice/review groups."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal as D,localcontext,ROUND_HALF_UP
import os,re,sys
sys.dont_write_bytecode=True
from lxml import html
from build_week8_chapters import conv,checks,translations
translations['⁵']=r'$^5$'
ROOT=Path(__file__).resolve().parents[1]
def write(path,text):
 p=ROOT/path;t=p.with_suffix(p.suffix+'.tmp')
 with t.open('w') as f:f.write('\n'.join(x.rstrip() for x in text.splitlines()).rstrip()+'\n');f.flush();os.fsync(f.fileno())
 os.replace(t,p)
def fraction(x):
 x=F(x);return str(x.numerator) if x.denominator==1 else r'\frac{'+str(x.numerator)+'}{'+str(x.denominator)+'}'
def money(x):
 with localcontext() as ctx:
  ctx.prec=80;q=D(x.numerator)/D(x.denominator);return f'{q.quantize(D(".01"),rounding=ROUND_HALF_UP):,.2f}'
def table(head,rows):
 return '\n'+r'\par\medskip{\small\renewcommand{\arraystretch}{1.25}\begin{tabularx}{\linewidth}[t]{@{}'+'Y'*len(head)+r'@{}}\toprule'+'\n'+' & '.join('{'+str(x)+'}' for x in head)+r'\\\midrule'+'\n'+'\n'.join(' & '.join('{'+str(x)+'}' for x in row)+r'\\' for row in rows)+'\n'+r'\bottomrule\end{tabularx}}\par\medskip'+'\n'
def figure(name,caption,height='2.65'):
 return '\n'+r'\par\medskip\noindent\begin{minipage}{\linewidth}\centering\includegraphics[width=\linewidth,height='+height+r'in,keepaspectratio]{../assets/week1/'+name+r'.pdf}\captionof*{figure}{'+caption+r'}\end{minipage}\par\medskip'+'\n'
def group(letter,title,answers):return '\n'+r'\Needspace{8\baselineskip}\subsection*{'+title+'}\n'+r'\begin{enumerate}[label='+letter+r'\arabic*.,leftmargin=2.5em,itemsep=10pt]'+'\n'+''.join('\\item '+x+'\n' for x in answers)+r'\end{enumerate}'+'\n'
preamble=(ROOT/'readings/Math107_Chapter_02.tex').read_text().split('\\begin{document}')[0].replace('2.\\arabic','1.\\arabic').replace('WEEK 2','WEEK 1').replace('Week 2:','Week 1:').replace('Frequency and Probability','Number Systems')
cover=r'''
\begin{document}
{\small\sffamily\color{olive}WEEK 1 / NUMBER SYSTEMS\par}
\vspace{12pt}
{\fontsize{30}{34}\selectfont\bfseries\color{olive}Counting, movement,\\scaling, and repeated change\par}
\vspace{9pt}
{\large Connect arithmetic to quantities, positions, fractions, and rules that act one step at a time.\par}
'''+figure('number-tower','Each smaller system is included in the systems around it. A number can have several correct descriptions.','2.9')+r'''
\begin{tcolorbox}[title={Start with what the number means}]
Seven can count books, identify a bus route, mark a temperature, or describe a change. The setting tells us which calculations make sense and what their answers mean.
\end{tcolorbox}
Try the short checks before reading the explanations in the solutions. The practice sets retain all 28 original exercise and review groups. A brief complex-number preview extends the picture; the classification exercises use N, Z, Q, and R. The situations and forecasts are hypothetical.

\medskip
\href{https://bobovski66.github.io/MathInSociety/readings/week1_reading.html}{Online reading}\quad\textperiodcentered\quad\href{https://bobovski66.github.io/MathInSociety/demos/number_systems.html}{Explorer}\quad\textperiodcentered\quad\href{https://bobovski66.github.io/MathInSociety/labs/week1_lab.html}{Laboratory}
\clearpage
'''
tree=html.fromstring((ROOT/'readings/week1_reading.html').read_text())
for e in tree.iter():
 if not isinstance(e.tag,str):continue
 for field in ['text','tail']:
  v=getattr(e,field)
  if not v:continue
  for name in ['a','b']:
   for sub,tex in [('ₙ₊₁','_{n+1}'),('₀','_0'),('₁','_1'),('₂','_2'),('₅','_5'),('ₙ','_n')]:v=v.replace(name+sub,'\\('+name+tex+'\\)')
  v=v.replace('rⁿ',r'\(r^n\)').replace('π',r'\(\pi\)')
  v=re.sub(r'√\(([^()]+)\)',lambda m:r'\(\sqrt{'+m[1]+'}'+r'\)',v)
  v=re.sub(r'√(\d+)',lambda m:r'\(\sqrt{'+m[1]+'}'+r'\)',v)
  setattr(e,field,v)
checks.clear();ids=['meaning','s0','s1','position','s3','fraction-operations','s2','percent','s4','irrational','complex','s5','models'];reading=[]
for id in ids:
 s=conv(tree.get_element_by_id(id)).replace('../assets/week8/','../assets/week1/').replace('height=3.2in','height=2.65in')
 for name,height in [('number-tower','3.2'),('unit-square-diagonal','3.0'),('complex-plane','3.0')]:s=s.replace('height=2.65in,keepaspectratio]{../assets/week1/'+name+'.pdf}','height='+height+'in,keepaspectratio]{../assets/week1/'+name+'.pdf}')
 reading.append(s)
extras=r'''
\Needspace{8\baselineskip}
\section*{More worked examples}
\subsection*{Two hypothetical balances}
Start both models at 100 dollars. A adds 20 dollars each month. B multiplies by 1.10, representing 10\% growth per month. Keep exact values while updating and round only the displayed amounts.
'''+table(['Month','A: add 20 dollars','B: multiply by 1.10'],[[n,money(F(100+20*n)),money(F(100)*F(11,10)**n)] for n in range(6)])+figure('savings-models','Both rules use a positive start. The factor 1.10 exceeds 1, so the repeated multiplication eventually leads if the rules continue.')+r'''
At month 12, A is 340.00 dollars and B is 313.84 dollars, so A still leads. At month 14, A is 380.00 and B is about 379.75. B first leads at month 15: 417.72 dollars versus A's 400.00. By month 48, the model values are 1,060.00 and 9,701.72 dollars. These are consequences of the stated update rules, not guarantees about actual accounts.

\Needspace{8\baselineskip}
\subsection*{Why the diagonal is not a fraction}
The unit-square diagonal has squared length $1^2+1^2=2$, so its exact length is $\sqrt2$. Here is a short argument that it cannot be a ratio of integers.

Suppose $\sqrt2=p/q$ in lowest terms, with positive integers p and q. Squaring gives $p^2=2q^2$. Thus $p^2$ is even, which forces p to be even: an odd number has an odd square. Write $p=2k$.

Substitution gives $4k^2=2q^2$, so $q^2=2k^2$. Then q is even too. Both p and q would share the factor 2, contradicting the assumption that the fraction was in lowest terms. This contradiction rules out a rational representation.

\Needspace{8\baselineskip}
\subsection*{Numbers that label text}
A token ID identifies a piece of text in a vocabulary. Its size does not measure meaning or dictate sentence order. In one invented vocabulary, the phrase ``cat sat on the mat'' has IDs $42,17,8,55,91$.
'''+figure('token-ids','The text gives the order of the labels. Rearranging the labels changes the text.')+r'''
If a prompt contains 4 tokens and one token is appended per step, its length is $L_n=4+n$. The length follows an additive rule. Which token is chosen is a different question, developed through probability in Week 2.

\subsection*{Activities and further reading}
Use the \href{https://bobovski66.github.io/MathInSociety/demos/number_systems.html}{explorer} to compare sequences and fraction locations. The \href{https://bobovski66.github.io/MathInSociety/applications/week1_application.html}{growth application} compares household forecasts; the \href{https://bobovski66.github.io/MathInSociety/applications/week1_ai.html}{text-and-numbers application} distinguishes labels from quantities. The \href{https://bobovski66.github.io/MathInSociety/discussions/week1_discussion.html}{discussion} asks you to interpret a repeated change of your own.

OpenStax reviews \href{https://openstax.org/books/elementary-algebra-2e/pages/1-8-the-real-numbers}{real numbers and square roots}. Hugging Face describes \href{https://huggingface.co/docs/transformers/main_classes/tokenizer}{tokenizers and token IDs}.
'''
solutions=['\n'+r'\clearpage\section*{Solutions and reasoning}'+'\n']
for i,(_,answer) in enumerate(checks,1):solutions.append('\n\\paragraph{Short check '+str(i)+'.} '+answer)
solutions.append('\n\\Needspace{8\\baselineskip}\n')
solutions.append(group('A','Practice A: Number systems',[
 r'(a) N. (b) Z. (c) Q. (d) R, real but irrational. (e) Z under the four listed choices. (f) $6/3=2$, so N. Every one is also real; the task asks for the smallest listed system.',
 r'(a) True: any integer k equals $k/1$. (b) False: $1/2$ is rational but not an integer. (c) True: $1/3$ is a ratio of integers. (d) True: $\sqrt2$ is one example.',
 r'$0.75=75/100=3/4$, so its smallest listed system is Q. The square root of a nonnegative integer that is not a perfect square is irrational; 3 is such an integer, so $\sqrt3$ is not a ratio of integers.',
]))
solutions.append(group('B','Practice B: Signed changes',[
 r'(a) $-3$. (b) $-8$. (c) $11$. (d) $-9$. (e) $1/2$. (f) $2/3+1/6=4/6+1/6=5/6$.',
 r'The signed updates are $-6+10=4$, followed by $4+(-14)=-10$. On a number line, mark $-6$, 4, and $-10$, with the first move right and the second left.'+figure('hiker-path','The graph records position after each move. The three marked values are the locations to place on a number line.'),
 r'$-230+500+(-185)=270-185=85$. The final balance is 85 dollars. The deposit is positive and the withdrawal is negative.',
]))
solutions.append(group('C','Practice C: Scaling',[
 r'(a) $-21$. (b) 20. (c) 2. (d) $10(5)=50$. (e) $6/12=1/2$. (f) $(5/6)(3)=15/6=5/2$.',
 r'Multiplication by $-1$ reverses direction across zero, so doing it twice returns to the original positive unit.',
 r'(a) Greater: the factor $3/2$ exceeds 1. (b) Less: the factor $1/2$ lies between 0 and 1. (c) Greater: division by $1/2$ multiplies by 2. (d) Less: division by 3 multiplies by $1/3$. These comparisons use a positive starting value.',
]))
solutions.append(group('D','Practice D: Equivalence',[
 r'(a) Equivalent: $4(9)=6(6)=36$. (b) Different: $5(25)=125$ and $8(15)=120$. (c) Equivalent: $7(33)=11(21)=231$. (d) Different: $3(20)=60$ and $7(9)=63$.',
 r'(a) $3/4$ after dividing by 4. (b) $3/7$ after dividing by 5. (c) $2/3$ after dividing by 12. (d) $2/5$ after dividing by 50.',
 r'$6/10=3/5$ after dividing numerator and denominator by 2. The cross-products agree: $6(5)=10(3)=30$.',
 r'$\sqrt4=2=2/1$ is rational, whereas $\sqrt2$ cannot be written as a ratio of integers, as the lowest-terms argument in the worked examples shows.',
]))
solutions.append(group('E','Practice E: Operations and roots',[
 r'(a) $-5$. (b) 4. (c) 6. (d) 27. (e) 49. (f) 12.',
 r'(a) $\sqrt{16}=4$, rational. (b) $\sqrt7$, irrational. (c) $\sqrt{100}=10$, rational. (d) $\sqrt{50}$, irrational because the nonnegative integer 50 is not a perfect square. It also equals $5\sqrt2$.',
 r'The first left side is $6(2)=12$; the right side is $\sqrt{144}=12$. In the second check, $\sqrt9\sqrt9=3(3)=9$ and $\sqrt{9\cdot9}=\sqrt{81}=9$. Products of principal square roots obey this rule for nonnegative real quantities under the roots.',
]))
solutions.append(group('F','Practice F: Recursion',[
 r'(a) $5,9,13,17,21,25$, additive.\par (b) $1,3,9,27,81,243$, multiplicative.\par (c) $100,90,80,70,60,50$, additive with change $-10$.\par (d) $2,1,1/2,1/4,1/8,1/16$, multiplicative with factor $1/2$.\par Six terms include the start and five updates.',
 r'$b_0=500$ and $b_{n+1}=2b_n$. The direct formula is $b_n=500(2^n)$.'+table(['Hour n','Model population'],[[n,500*2**n] for n in range(6)])+r'The doubled counts follow the mathematical rule; an actual culture can encounter limits.',
 r'The first six values are $18{,}000,16{,}500,15{,}000,13{,}500,12{,}000,10{,}500$ dollars. Solve $18{,}000-1{,}500n=0$ to obtain $n=12$ years.'+figure('car-value','The arithmetic becomes negative after year 12. That extension shows where the rule needs reconsideration as a model of car value.'),
 r'Predict B. By year 5, B is about 2,011.36 while A is 2,000, and B is already gaining more than 200 per year; its annual gain continues to increase under the fixed 15\% rule, so it remains ahead through year 20 if the rules continue.'+table(['Year','A: add 200','B: multiply by 1.15'],[[n,1000+200*n,money(F(1000)*F(23,20)**n)] for n in range(6)])+figure('recursion-comparison','A numerical check at year 20 gives A = 5,000 and B approximately 16,366.54. The prediction above uses only the behavior through year 5.'),
]))
solutions.append(group('R','Chapter 1 review',[
 r'(a) $8/4=2$: N. (b) $-17$: Z. (c) $\sqrt{11}$: R, real but irrational. (d) $-6/2=-3$: Z.',
 r'$0+(-15)=-15$, then $-15+8=-7$, then $-7+(-5)=-12$. The final position is $-12$ meters relative to the surface: the diver is 12 meters below it.'+figure('diver-path','Signed position and depth below the surface use different descriptions of the same stop.'),
 r'Both simplify to $4/7$: divide $8/14$ by 2 and $12/21$ by 3. The original cross-products agree: $8(21)=14(12)=168$.',
 r'$(2/3)(3/4)=6/12=1/2$ cup.'+figure('fraction-scale','Two thirds of the original three-quarter cup is half a cup.'),
 table(['Weeks','Two-week updates n','Model insects'],[[2*n,n,80*3**n] for n in range(5)])+r'The direct formula is $P_n=80(3^n)$, with one update every two weeks. This is multiplicative recursion; n is not the number of individual weeks.'+figure('insect-growth','The update interval must match the exponent in the model.'),
 r'This is additive with change 0.5: $a_n=5+0.5n$. At step 20, $a_{20}=5+0.5(20)=15$.',
 r'First take the square root and square: $8+9-((-4)\cdot2)$. Multiply inside the parentheses to get $8+9-(-8)$, then add the opposite: $8+9+8=25$.',
 r'The unit-square diagonal has a real length whose square is 2. If that length were a reduced fraction $p/q$, then $p^2=2q^2$ would force both p and q to be even, contradicting lowest terms, so the length is irrational.',
]))
practice=(ROOT/'scripts/week1_chapter_practice.tex').read_text()
write('readings/Math107_Chapter_01.tex',preamble+cover+''.join(reading)+extras+practice+''.join(solutions)+'\n\\end{document}\n')
os.sync();print('Built Chapter 1:',len(checks),'short checks and all 28 original exercise/review groups with solutions.')
