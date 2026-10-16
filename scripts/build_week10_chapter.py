"""Build the chapter's LaTeX body from the student-facing HTML reading.

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
 if tag=='div' and cls in ['eyebrow','kicker','meta']:return ''
 if tag=='div' and ('example' in cls or 'insight' in cls):
  h=e.find('h3');title=children(h) if h is not None else ''
  body=esc(e.text)+''.join(conv(c)+esc(c.tail) for c in e if c is not h)
  opts=',colback=warm,colbacktitle=warm,coltitle=gold,colframe=gold!35' if 'insight' in cls else ''
  return '\n\\begin{tcolorbox}[title={'+title+'},breakable'+opts+']\n'+body+'\n\\end{tcolorbox}\n'
 return content()
cover=r'''
\begin{document}
{\small\sffamily\color{olive}CHAPTER 10 / COMPLEXITY AND THE LIMITS OF PREDICTION\par}
\vspace{8pt}
{\fontsize{31}{35}\selectfont\bfseries\color{olive}Simple rules.\\Surprising worlds.\par}
\vspace{8pt}
{\large Follow a number through a maze, build a curve that keeps getting longer, and discover why an exact rule can still leave a forecast uncertain.\par}

Repeated updates are already familiar: a balance earns interest; a controller acts on a temperature reading. This chapter builds on those examples from Weeks 1--9, using arithmetic, percentages, tables, and graph reading to investigate less familiar patterns.

\begin{center}\includegraphics[width=\linewidth]{../assets/week10/logistic-behaviors.pdf}\end{center}
{\small\color{teal}Three patterns we will learn to read: settling toward one value, repeating between two values, and moving irregularly within fixed bounds. Each plot follows one value through repeated updates.\par}

\begin{tcolorbox}[title={The question for the week}]
If we know the rule, do we know the future? Begin by defining the quantity, what one update means, the starting information, and the question we want the calculation to answer.
\end{tcolorbox}
By the end, you can trace Collatz routes, distinguish tested examples from proof, calculate fractal counts and measures, compare logistic forecasts, and report a measurement together with its observation scale.

Work through the examples before the short checks. The explorer handles long calculations; no prior study of chaos or fractals is assumed. The dimension extension is optional. Solutions to the short checks and the chapter review appear at the end.

\medskip
\href{https://bobovski66.github.io/MathInSociety/readings/week10_reading.html}{Online reading}\quad\textperiodcentered\quad\href{https://bobovski66.github.io/MathInSociety/demos/fractal_recursion.html}{Week 10 explorer}\quad\textperiodcentered\quad\href{https://bobovski66.github.io/MathInSociety/labs/week10_lab.html}{Guided laboratory}
'''
extra_ai=r'''
\Needspace{7\baselineskip}\subsection*{The AI connection: the output becomes the next input}
A language model uses its current text context to predict a next token, appends the chosen token, and then repeats with the updated context. A token is a piece of text; a probability distribution gives the weights of possible next pieces. This repeated process is called autoregressive generation.

The invented tree below treats each listed word or punctuation mark as a toy token. Begin at the prompt and follow one arrow at a time. Each second set of probabilities belongs to the first token already chosen.
\begin{center}\includegraphics[width=\linewidth]{../assets/week10/ai-branches.pdf}\end{center}
For a relative-frequency picture, imagine 100 hypothetical runs divided in the stated proportions. Of the 45 that choose ``moving,'' 60\% then choose ``slowly'': $45(0.60)=27$ out of the original 100, giving a path probability of 0.27. The path ``flickering then faintly'' has probability $0.35(0.80)=0.28$.

This is why we multiply along a path. The notation $P(\text{slowly}\mid\text{moving})$ means the probability of ``slowly'' \emph{given} that ``moving'' was chosen. A likely continuation still needs observations or sources to establish whether a claim about an actual light is true. The online AI application develops this example with a selectable tree.
'''
review_answers=r'''
\subsection*{Review answers}
\begin{enumerate}
\item From 11: 14 updates, peak 52. Routes that reach 11 follow its future route.
\item $256$ segments, each of length $1/81$, total $256/81\approx3.1605$. From a 9-meter original, total length is $9(256/81)=256/9\approx28.4444$ meters.
\item $81$ triangles; area $81/256\approx0.3164$. Each new triangle has one-quarter its parent's area; the three remaining pieces together retain only three quarters.
\item First update $0.448$; nonzero fixed point $1-1/2.8\approx0.642857$. The first depends on the chosen start; the second is unchanged by the update.
\item Update 4, with gap approximately 0.078197. The preceding three gaps are about 0.007220, 0.022805, and 0.035779.
\item 40,000 and 40,010 fish; first gaps above 1,000 and 10,000 fish occur at generations 8 and 14. At generation 14, the gap is approximately 19,074 fish. The reference population is a scale chosen for this toy model, rather than a fitted carrying capacity for a real lake.
\item 13 km using the 50-meter ruler; 14.5 km using the 25-meter ruler.
\item The tested interval only. Every power of 2 reaches 1 by repeated halving.
\item $0.45(0.60)=0.27<0.35(0.80)=0.28$. Model continuation probabilities do not verify claims about the world.
\end{enumerate}
\subsection*{Further reading}
These sources provide background, not additional required assignments.
\begin{itemize}
\item R. M. May (1976), \emph{Simple mathematical models with very complicated dynamics}. \href{https://doi.org/10.1038/261459a0}{Nature 261, 459--467}.
\item R. De Leo and J. A. Yorke (2021), \emph{The graph of the logistic map is a tower}. \href{https://doi.org/10.3934/dcds.2021075}{DCDS 41, 5243--5269}.
\item A.-S. Elsenhans (2026), \href{https://www.antsxvii.org/papers/antsxvii-elsenhans-paper.pdf}{\emph{Numerical verification of the Collatz conjecture for billion digit random numbers}}.
\item B. Mandelbrot (1967), \emph{How long is the coast of Britain?} \href{https://doi.org/10.1126/science.156.3775.636}{Science 156, 636--638}.
\item A. Vaswani et al. (2017), \href{https://arxiv.org/abs/1706.03762}{\emph{Attention Is All You Need}}.
\end{itemize}
}
\end{document}
'''
if __name__=='__main__':
 tree=html.fromstring((ROOT/'readings/week10_reading.html').read_text())
 parts=[(PAGES/'week10_chapter_preamble.tex').read_text(),cover]
 for id in ['start-here','recursion','collatz','evidence','fractals','logistic','prediction','scale','connections']:
  node=tree.get_element_by_id(id);s=conv(node)
  if id=='start-here':s=s.replace(r'\section{A quantity, a rule, and a question}',r'\section*{Start here: a quantity, a rule, and a question}')
  # Begin the largest subject changes on a fresh page; let related explanations flow.
  parts.append(('\n\\clearpage\n' if id in ['start-here','recursion','fractals','logistic','prediction','scale'] else '\n')+s)
  if id=='connections':parts.append(extra_ai)
 parts.extend(['\n\\clearpage\n',(PAGES/'week10_chapter_review.tex').read_text(),'\n\\clearpage\n{\\small\\setlength{\\parskip}{3pt}\\setlist{itemsep=2pt,topsep=2pt}\\titlespacing*{\\paragraph}{0pt}{4pt}{.75em}\n\\section*{Solutions and Further Reading}\n'])
 for i,(q,a) in enumerate(checks,1):parts.append('\n\\paragraph{Check '+str(i)+'.} '+a)
 parts.append('\n'+review_answers)
 (ROOT/'readings/Math107_Chapter_10.tex').write_text('\n'.join(line.rstrip() for line in ''.join(parts).splitlines())+'\n')
 print('Built complete LaTeX source with',len(checks),'short checks.')
