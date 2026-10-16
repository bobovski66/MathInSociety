"""Generate the standalone Week 9 LaTeX chapter from its explanatory web reading."""
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
  return '\n\\par\\medskip\\noindent\\begin{minipage}{\\linewidth}\n\\centering\\includegraphics[width=\\linewidth,height='+('4.1' if name in ['threshold-cascade','diffusion-rounds'] else '3.2')+'in,keepaspectratio]{../assets/week9/'+name+'.pdf}\n\\captionof*{figure}{'+children(cap)+'}\n\\end{minipage}\\par\\medskip\n'
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
cover=r'''
\begin{document}
{\small\sffamily\color{olive}CHAPTER 9 / NETWORKS AND COLLECTIVE SYSTEMS\par}
\vspace{10pt}
{\fontsize{31}{35}\selectfont\bfseries\color{olive}Small connections.\\Collective effects.\par}
\vspace{8pt}
{\large Follow a community alert through seven locations. Discover how direct contacts, alternate routes, and local decisions shape the whole system.\par}
\begin{center}\includegraphics[width=\linewidth]{../assets/week9/community-network.pdf}\end{center}
\begin{tcolorbox}[title={The question for the week}]
A community has seven locations and nine direct communication links. Can an alert reach everyone? How many rounds does it need? Which one-link improvement helps it survive an outage?
\end{tcolorbox}
This chapter begins with the meaning of a dot and a line, then builds a language for neighbors, paths, vulnerability, and spread. It uses arithmetic, fractions, averages, and repeated updates from Weeks 1--8. No earlier study of networks is assumed.

\medskip
\href{https://bobovski66.github.io/MathInSociety/readings/week9_reading.html}{Online reading}\quad\textperiodcentered\quad\href{https://bobovski66.github.io/MathInSociety/demos/network_systems.html}{Network explorer}\quad\textperiodcentered\quad\href{https://bobovski66.github.io/MathInSociety/labs/week9_lab.html}{Guided laboratory}
'''
ai=r'''
\clearpage
\section{AI connection: signals along weighted arrows}
Imagine a small program combining two indoor sensor scores. The heat score is $x_1=2$ and the motion score is $x_2=4$. The subscripts identify two different inputs. These invented scores are rescaled to numbers from 0 to 6; they are not temperatures or probabilities.

The diagram is a tiny \emph{linear signal network}. Every arrow has a multiplier called a weight. Each receiving node adds its incoming weighted signals. The intermediate nodes $H_1,H_2$ form a hidden layer: a set of calculations between the inputs and output. ``Hidden'' means intermediate, not secret.
\begin{center}\includegraphics[width=\linewidth,height=3.2in,keepaspectratio]{../assets/week9/neural-signals.pdf}\end{center}
\begin{tcolorbox}[title={Worked calculation: multiply, then add}]
At the first hidden node,
\[
H_1=0.50x_1+0.25x_2=0.50(2)+0.25(4)=1+1=2.
\]
At the other hidden node, one contribution is negative:
\[
H_2=-0.50x_1+0.75x_2=-0.50(2)+0.75(4)=-1+3=2.
\]
Now send those values through the two arrows to the output:
\[
O=1.50H_1-0.50H_2=1.50(2)-0.50(2)=3-1=2.
\]
The sign of a weight changes a contribution; the arrow determines the direction. A weight is a multiplier, not a transmission probability.
\end{tcolorbox}

\clearpage
\subsection*{A connected input can have no net effect}
Hold $x_1$ fixed and increase $x_2$ by 1. The path through $H_1$ adds $0.25(1.50)=0.375$ to the output. The path through $H_2$ adds $0.75(-0.50)=-0.375$. The effects cancel exactly. Changing the motion score changes both hidden values but leaves the output unchanged.

In fact, substituting the hidden formulas into the output gives
\[
O=1.50(0.50x_1+0.25x_2)-0.50(-0.50x_1+0.75x_2)=x_1.
\]
This algebra is an extension; the two path contributions already explain the cancellation. Connections show where influence \emph{can} travel. The weights determine how those influences combine.

\begin{tcolorbox}[title={Remove one edge and test again}]
With the original inputs 2 and 4, remove the arrow $x_2\to H_1$. The new hidden values are $H_1=0.50(2)=1$ and $H_2=2$. Thus $O=1.50(1)-0.50(2)=0.5$. The other motion-score path remains, so the earlier cancellation is broken.
\end{tcolorbox}

\subsection*{An activation rule adds another transformation}
The original model only multiplies by constants and adds. Combining such linear calculations still gives a linear relationship. Neural networks commonly add \emph{activation functions}, rules that transform a node's sum before sending it onward.

For example, ReLU keeps a nonnegative sum and replaces a negative sum by zero. With $x_1=4,x_2=0$, the raw hidden sums are 2 and $-2$. Without the extra rule, the output is $1.50(2)-0.50(-2)=4$. With ReLU at the hidden nodes only, the sent values are 2 and 0, so the output is 3. This introduces a nonlinear relationship. Real models also commonly add adjustable constants called biases; our model sets them to zero.

\subsection*{A forward pass is different from training}
A \emph{forward pass} uses current inputs and weights to calculate an output. Training uses examples with targets, compares outputs with those targets, and changes parameters in response to errors. That makes training a feedback process.

For the original prediction 2 and an invented target 3, define signed error as target minus prediction: $3-2=1$. If we change only the $H_1$-to-output weight from 1.50 to 2.00, the new output is $2.00(2)-0.50(2)=3$. This hand-chosen change matches one target; it does not establish accuracy on other examples. Backpropagation and an optimization method organize parameter updates in larger models.

The weights, scores, and targets here are invented and have not been fitted to sensor data. The output is a toy score. The online AI application lets you change inputs, remove an edge, and compare the two node rules.
'''
review=r'''
\clearpage
\section*{Chapter Review}
Use the seven-node base network with edges AB, AC, BC, BD, CD, DE, EF, EG, FG unless a question changes it. Links are two-way and unweighted. Show a count, route, or update sequence to support each answer. No centrality formula is required.
\begin{enumerate}
\item Find all seven degrees. Check the sum against the number of edges, then calculate the mean degree.
\item How many simple undirected links are possible among seven nodes? Find the base network's density as a fraction, decimal, and percentage. Explain what that percentage describes.
\item Find two different shortest paths from A to G. State their lengths. Find the distances from B to F and from D to every other node.
\item What are the connected components after DE is removed? Is the distance from A to F then zero, very large, or unreachable? Explain.
\item Which base-network edges are bridges? Which nodes are articulation points? Explain the difference between the two tests.
\item Add DF. Give an A-to-G route that survives loss of DE. Does this addition also protect against loss of D itself?
\item Compare adding AD with adding DF. With all links working, at which round is everyone informed from A under automatic sending? Which proposal meets the goal of surviving failure of DE?
\item In the adjacency table, find row A/column D, row D/column E, and row E/column E. What is the sum of row D? Explain why a zero at A/G does not mean G is unreachable from A.
\item A alone is informed at round 0. List the newly informed and total informed nodes after rounds 1--4 under the automatic rule. Explain why two senders contacting D do not count as two new locations.
\item Use the half-neighbor adoption rule. With seeds B,C, list the active sets at rounds 0,1,2. Repeat with seeds B,C,F. Which first-round activation makes the second case different on the right side?
\item A node has five neighbors and a 60\% threshold. How many active neighbors are required? Does that local count determine the outcome of the whole network?
\item For arrows $P\to Q$, $Q\to R$, can R reach P? State Q's in-degree and out-degree. Then compare a two-link trip of 12+12 minutes with a three-link trip of 4+4+4 minutes.
\item For the AI network with inputs 2 and 4, find $H_1,H_2,O$. Remove $x_2\to H_1$ and recalculate. Why does changing $x_2$ have no net effect in the original sum-only model?
\item With target 3 and prediction 2, use signed error = target minus prediction. Change only the $H_1$-to-output weight to 2.00 and recalculate. What does matching this one target establish, and what does it leave unknown?
\item Choose a real network. Define nodes, edges, a useful question, and one limitation of a simple undirected, unweighted representation.
\end{enumerate}
\medskip
\begin{tcolorbox}[title={A reliable explanation has four parts}]
State the model and question. Show a route or calculation. Interpret the result in the setting. Name an assumption that limits the conclusion.
\end{tcolorbox}
'''
answers=r'''
\subsection*{Chapter Review: solutions and reasoning}
\begin{enumerate}
\item In order A--G, degrees are $2,3,3,3,3,2,2$. Their sum is 18, which equals $2(9)$. The mean is $18/7\approx2.57$ neighbors.
\item There are $7(6)/2=21$ pairs. Density is $9/21=3/7\approx0.429$, about $42.9\%$. It is the fraction of possible \emph{pairs} with direct links, not a transmission probability.
\item A--B--D--E--G and A--C--D--E--G each use 4 edges. B-to-F distance is 3 via B--D--E--F. From D to A,B,C,E,F,G the distances are $2,1,1,1,2,2$; their sum is 9 and mean is 1.5.
\item The components are $\{A,B,C,D\}$ and $\{E,F,G\}$. F is unreachable from A. Waiting cannot create a missing path. Zero is the distance from A to itself.
\item DE is the only bridge. D and E are articulation points. An edge test removes one connection; a node test removes the location and every connection touching it.
\item A--B--D--F--G survives loss of DE. But removing D itself leaves $\{A,B,C\}$ separate from $\{E,F,G\}$ even with DF added. Both cross-region links depended on D.
\item AD gives complete delivery by round 3 with all links working; DF gives complete delivery by round 4. DF, unlike AD, supplies a cross-region route after DE fails. Both give 10 edges and density $10/21$ before failures.
\item The entries are 0,1,0; row D sums to 3. A zero at A/G only rules out a direct link; paths using intermediate locations still exist.
\item New nodes by rounds 1--4: $\{B,C\},\{D\},\{E\},\{F,G\}$. Cumulative totals: 3,4,5,7, including the initial A. Multiple message copies arriving at D inform the same one location.
\item Seeds BC give $BC\to ABCD\to ABCD$; the process stalls because E sees only one of its three neighbors active. Seeds BCF give $BCF\to ABCDFG\to ABCDEFG$. G activates in round 1 because F is one of its two neighbors. E uses the new D and G states beginning in round 2.
\item Three active neighbors, since $0.60(5)=3$. The outcome also depends on other thresholds, the network, and seeds.
\item No, R has no outgoing route to P. Q has one incoming and one outgoing arrow. The two-link trip takes 24 minutes; the three-link trip takes 12. Fewest links and least time need not agree.
\item $H_1=2,H_2=2,O=2$. After removal, $H_1=1,H_2=2,O=0.5$. The original two paths from $x_2$ contribute $+0.375$ and $-0.375$ per input unit, so their net effect is zero.
\item Error is 1. The new output is $2.00(2)-0.50(2)=3$, giving error 0 for this example. It matches one target; performance on other examples remains untested.
\item Answers vary. For a transit network, nodes might be stops and edges direct routes between stops. A useful question is whether a closure separates a neighborhood. An unweighted graph omits waiting and travel times; an undirected graph omits one-way service.
\end{enumerate}
\subsection*{Optional background}
\begin{itemize}
\item NIST, \href{https://xlinux.nist.gov/dads/HTML/graph.html}{\emph{Graph}} and \href{https://xlinux.nist.gov/dads/HTML/bridge.html}{\emph{Bridge}}, Dictionary of Algorithms and Data Structures.
\item Google Machine Learning Crash Course, \href{https://developers.google.com/machine-learning/crash-course/neural-networks/nodes-hidden-layers}{\emph{Nodes and hidden layers}} and \href{https://developers.google.com/machine-learning/crash-course/neural-networks/activation-functions}{\emph{Activation functions}}.
\end{itemize}
All networks, sensor weights, and scenarios in the exercises are constructed teaching examples. The mathematical calculations follow their stated assumptions.
}
\end{document}
'''
if __name__=='__main__':
 checks.clear()
 tree=html.fromstring((ROOT/'readings/week9_reading.html').read_text())
 parts=[(PAGES/'week9_chapter_preamble.tex').read_text(),cover,'\n\\clearpage\n']
 for id in ['start-here','language','degree','density','routes','failure','centrality','matrix','diffusion','thresholds','direction','connections']:
  node=tree.get_element_by_id(id);s=conv(node)
  if id=='start-here':s=s.replace(r'\section{Connections change what a community can do}',r'\section*{Start here: connections change what a community can do}')
  parts.append(('\n\\clearpage\n' if id in ['language','density','diffusion','thresholds','direction','connections'] else '\n')+s)
 parts.extend([ai,review,'\n\\clearpage\n{\\setlength{\\parskip}{3pt}\\setlist{itemsep=3pt,topsep=3pt}\\titlespacing*{\\paragraph}{0pt}{5pt}{.75em}\n\\section*{Solutions and Further Reading}\n'])
 for i,(q,a) in enumerate(checks,1):parts.append('\n\\paragraph{Short check '+str(i)+'.} '+a)
 parts.append('\n'+answers)
 out=ROOT/'readings/Math107_Chapter_09_Networks.tex'
 out.write_text('\n'.join(line.rstrip() for line in ''.join(parts).splitlines())+'\n')
 print('Built standalone chapter source with',len(checks),'short checks and 15 review problems.')
