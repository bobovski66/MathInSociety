"""Build the new Complexity, Chaos, and Fractals PDF from the Week 10 HTML reading.

Compile the generated complete source from readings/. The small template files
retain the existing typography and the chapter review. This keeps explanatory
material synchronized while preserving a standalone editable LaTeX deliverable.
"""
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
  return '\n\\par\\medskip\\noindent\\begin{minipage}{\\linewidth}\n\\centering\\includegraphics[width=\\linewidth,height=3.1in,keepaspectratio]{../assets/week10/'+name+'.pdf}\n\\captionof*{figure}{'+children(cap)+'}\n\\end{minipage}\\par\\medskip\n'
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
 if tag=='div' and 'route' in cls:return '\n\\[6\\to3\\to10\\to5\\to16\\to8\\to4\\to2\\to1.\\]\n'
 if tag=='div' and cls in ['eyebrow','kicker','meta','section-label']:return ''
 if tag=='div' and ('example' in cls or 'insight' in cls):
  h=e.find('h3');title=children(h) if h is not None else ''
  body=esc(e.text)+''.join(conv(c)+esc(c.tail) for c in e if c is not h)
  opts=',colback=warm,colbacktitle=warm,coltitle=gold,colframe=gold!35' if 'insight' in cls else ''
  return '\n\\begin{tcolorbox}[title={'+title+'},breakable'+opts+']\n'+body+'\n\\end{tcolorbox}\n'
 return content()
cover=r'''
\begin{document}
{\small\sffamily\color{olive}CHAPTER 10 / MATHEMATICAL RULES AND THEIR CONSEQUENCES\par}
\vspace{8pt}
{\fontsize{31}{35}\selectfont\bfseries\color{olive}Complexity, Chaos,\\and Fractals\par}
\vspace{10pt}
{\large Three different mathematical questions, explored through Collatz, the logistic map, and the Sierpi\'nski triangle.\par}

Repeated rules have appeared throughout the course. An account grows, a thermostat corrects a temperature, and a binary address extends one choice at a time. This chapter looks at three more rules. Their differences explain why a computation can be difficult, why a deterministic prediction can be sensitive, and why a geometric construction can repeat at every scale.

\begin{center}
\includegraphics[width=.96\linewidth]{../assets/week10/sierpinski-lesson.pdf}
\end{center}
{\small\color{teal}The Sierpi\'nski construction at stages zero through three: 1, 3, 9 and 27 surviving triangles.\par}

\begin{tcolorbox}[title={The three questions}]
\begin{enumerate}
\item \textbf{Complexity:} How much work does a computation require, and what has testing established?
\item \textbf{Chaos:} Why can a fixed rule give very different long-term trajectories from close starting values?
\item \textbf{Fractals:} What happens when the same geometric replacement is repeated at smaller scales?
\end{enumerate}
\end{tcolorbox}
The calculations require arithmetic, elementary algebra, and careful reading of a recursive rule. The fractal dimension calculation is an optional extension.

\medskip
\href{https://bobovski66.github.io/MathInSociety/readings/week10_reading.html}{Online reading}\quad\textperiodcentered\quad\href{https://bobovski66.github.io/MathInSociety/demos/fractal_recursion.html}{Interactive explorer}\quad\textperiodcentered\quad\href{https://bobovski66.github.io/MathInSociety/labs/week10_lab.html}{Guided laboratory}
'''
review_answers=r'''
\subsection*{Chapter review answers and guidance}
\begin{enumerate}
\item $10\to5\to16\to8\to4\to2\to1$. Six updates, peak $16$.
\item From $6$, eight updates and peak 16; from $7$, sixteen updates and peak 52. Each finite list is a calculation for specific inputs. The Collatz conjecture concerns \emph{all} positive integers.
\item $2^{10}=1{,}024$ strings for exhaustive search; a balanced search distinguishes 1,024 possibilities in ten binary choices, when the necessary structure is available.
\item $x_1=2.8(0.2)(0.8)=0.448$. Then $x_2=2.8(0.448)(0.552)=0.6924288$. Each step uses the preceding output.
\item $r=2.8$ settles toward a fixed point; $r=3.2$ approaches a period-two cycle; $r=3.9$ is a chaotic setting with sensitive dependence.
\item The initial gap is $0.0001$. Both starts follow exactly the same deterministic recurrence, but repeated updates can amplify the difference over time; the gap need not increase on every step.
\item The surviving piece count is $3^4=81$. The retained fraction of area is $(3/4)^4=81/256$.
\item Each small side is $(1/2)^3=1/8$ of the original. Each stage creates three children of one quarter the parent area, retaining three quarters of the previous filled area.
\item $D=\log 3/\log 2\approx1.585$ (the similarity dimension).
\item Good answers distinguish resources used by a procedure, sensitive dynamics, and self-similar geometric structure. Recursion alone does not establish any of the three.
\end{enumerate}
}
\end{document}
'''
if __name__=='__main__':
 tree=html.fromstring((ROOT/'readings/week10_reading.html').read_text(encoding='utf-8'))
 parts=[(PAGES/'week10_chapter_preamble.tex').read_text(encoding='utf-8'),cover]
 sections=['return-to-recursion','complexity','collatz','chaos','sensitivity','sierpinski','dimension','connections','sources']
 for section in sections:
  node=tree.get_element_by_id(section)
  # Start the major subject changes on fresh pages; preserve the reading's order.
  pagebreak='\n\\clearpage\n' if section in ('complexity','chaos','sierpinski','connections') else '\n'
  parts.append(pagebreak+conv(node))
 parts.extend(['\n\\clearpage\n',(PAGES/'week10_chapter_review.tex').read_text(encoding='utf-8'),
               '\n\\clearpage\n{\\small\\setlength{\\parskip}{3pt}\\setlist{itemsep=2pt,topsep=2pt}\\section*{Solutions}\\n'])
 for i,(q,a) in enumerate(checks,1):
  parts.append('\n\\paragraph{Check '+str(i)+'.} '+a)
 parts.append('\n'+review_answers)
 output=ROOT/'readings/Math107_Chapter_10.tex'
 output.write_text('\n'.join(line.rstrip() for line in ''.join(parts).splitlines())+'\n',encoding='utf-8')
 print('Generated new Week 10 TeX with',len(checks),'worked checks and',len(sections),'sections.')
 from chapter_editorial import polish_generated_chapters
 polish_generated_chapters([output])
