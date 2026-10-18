"""Build the illustrated Week 2 chapter with all 26 original practice/review groups."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import os,re,sys
sys.dont_write_bytecode=True
from lxml import html
from build_week8_chapters import conv,checks,translations

ROOT=Path(__file__).resolve().parents[1]
translations.update({'σ':r'$\sigma$','μ':r'$\mu$','±':r'$\pm$'})
def write(path,text):
 p=ROOT/path;t=p.with_suffix(p.suffix+'.tmp')
 with t.open('w') as f:f.write('\n'.join(x.rstrip() for x in text.splitlines()).rstrip()+'\n');f.flush();os.fsync(f.fileno())
 os.replace(t,p)
def fraction(x):
 x=F(x);return str(x.numerator) if x.denominator==1 else r'\frac{'+str(x.numerator)+'}{'+str(x.denominator)+'}'
def probability_table(labels,counts):
 n=sum(counts);rows=[]
 for label,count in zip(labels,counts):rows.append('{'+str(label)+'} & '+str(count)+' & $'+fraction(F(count,n))+'$ & '+f'{count/n:.4f}'+r'\\')
 return r'\par\medskip{\small\renewcommand{\arraystretch}{1.25}\begin{tabularx}{\linewidth}[t]{@{}YYYY@{}}\toprule'+'\n'+r'Outcome & Frequency & Fraction & Decimal\\\midrule'+'\n'+'\n'.join(rows)+'\n'+f'Total & {n} & 1 & 1.0000'+r'\\\bottomrule\end{tabularx}}\par\medskip'+'\n'
def figure(name,caption,height='2.6'):
 return '\n'+r'\par\medskip\noindent\begin{minipage}{\linewidth}\centering\includegraphics[width=\linewidth,height='+height+r'in,keepaspectratio]{../assets/week2/'+name+r'.pdf}\captionof*{figure}{'+caption+r'}\end{minipage}\par\medskip'+'\n'
def group(letter,title,answers):
 return '\n'+r'\Needspace{8\baselineskip}\subsection*{'+title+'}\n'+r'\begin{enumerate}[label='+letter+r'\arabic*.,leftmargin=2.5em,itemsep=10pt]'+'\n'+''.join('\\item '+a+'\n' for a in answers)+r'\end{enumerate}'+'\n'

preamble=(ROOT/'readings/Math107_Chapter_03.tex').read_text().split('\\begin{document}')[0]
preamble=preamble.replace('3.\\arabic','2.\\arabic').replace('WEEK 3','WEEK 2').replace('Week 3:','Week 2:').replace('Center and Spread','Frequency and Probability')
cover=r'''
\begin{document}
{\small\sffamily\color{olive}WEEK 2 / FREQUENCY, PROBABILITY, AND DISTRIBUTIONS\par}
\vspace{12pt}
{\fontsize{30}{34}\selectfont\bfseries\color{olive}From counts to\\statements about chance\par}
\vspace{10pt}
{\large Use a sample, a fraction, and a graph to explain what a collection of observations tells us.\par}
'''+figure('relative-frequency','A count, a fraction, a decimal, and a percentage can describe the same part of a whole.','2.8')+r'''
\begin{tcolorbox}[title={What does a survey result mean?}]
If 11 of 25 respondents choose the library, the observed library share is 44\%. Extending that result to everyone at the college requires another question: who had a chance to be included, and who was missed?
\end{tcolorbox}
Week 1 used fractions as parts of a whole. This chapter uses that idea to organize observations, compare groups, read graphs, and describe probability models. We keep observed results separate from predictions about future trials or a larger population.

Try the short checks before reading their explanations. Additional examples follow the reading. The 26 practice and review groups retain the earlier chapter's datasets and questions, with corrections to ambiguous graph labels and sampling language. Complete solutions follow. The situations are hypothetical.

\medskip
\href{https://bobovski66.github.io/MathInSociety/readings/week2_reading.html}{Online reading}\quad\textperiodcentered\quad\href{https://bobovski66.github.io/MathInSociety/demos/probability_distribution.html}{Counts and chance explorer}\quad\textperiodcentered\quad\href{https://bobovski66.github.io/MathInSociety/labs/week2_lab.html}{Laboratory}
\clearpage
'''

tree=html.fromstring((ROOT/'readings/week2_reading.html').read_text());checks.clear()
ids=['s0','s1','s2','compare','s3','bins','models','s4','events','dice','trials','s5'];reading=[]
for id in ids:
 text=conv(tree.get_element_by_id(id)).replace('../assets/week8/','../assets/week2/').replace('height=3.2in','height=2.65in')
 text=text.replace('height=2.65in,keepaspectratio]{../assets/week2/dice-outcomes.pdf}','height=3.8in,keepaspectratio]{../assets/week2/dice-outcomes.pdf}')
 reading.append(text)

calls=[5,8,6,7,9,5,6,8,7,6,7,8,5,9,7,6,8,7,6,5,8,7,6,9,7,8,6,7,5,8]
defects=[0,1,0,2,1,0,1,3,0,1,2,0,1,0,1,0,2,1,0,1]
extras=r'''
\Needspace{8\baselineskip}
\section*{More worked examples}
\subsection*{A selection plan needs a population}
A school surveys one advisory class to learn about all students in the school. The school is the population; that advisory class is the sample. If the advisory contains only seniors, other grade levels are missing. Asking more students from the same advisory does not solve that coverage problem.

A biologist weighs 50 fish caught at randomly chosen locations in a lake. The intended population is all fish in the lake; the observed sample is the 50 captured fish. Spreading locations can reach different habitats, but it does not automatically give every fish an equal chance of being caught. The gear and the fish's behavior can matter too.

\subsection*{Count defects before calculating shares}
For 20 inspected products, the recorded numbers of defects are
\begin{quote}0, 1, 0, 2, 1, 0, 1, 3, 0, 1, 2, 0, 1, 0, 1, 0, 2, 1, 0, 1.\end{quote}
'''+probability_table(range(4),[Counter(defects)[i] for i in range(4)])+r'''
Both zero defects and one defect occur eight times. The sample share with at least one defect is $(8+3+1)/20=12/20=0.60$. Equivalently, subtract the zero-defect share from 1: $1-8/20=0.60$. These calculations describe the inspected items.

\Needspace{8\baselineskip}
\subsection*{Read a category bar chart}
'''+figure('seasons',r'The recorded counts total 25. Summer has the largest count, 10; this is 40\%, not a majority.')+r'''
The share preferring Fall is $5/25=0.20$. The probability is exactly 0.20 when we choose uniformly from these 25 responses. Applying it to all students would be an estimate requiring information about how the respondents were selected.

\Needspace{8\baselineskip}
\subsection*{Check a table against its raw data}
The business records calls on 30 days:
\begin{quote}5, 8, 6, 7, 9, 5, 6, 8, 7, 6, 7, 8, 5, 9, 7, 6, 8, 7, 6, 5, 8, 7, 6, 9, 7, 8, 6, 7, 5, 8.\end{quote}
'''+probability_table(range(5,10),[Counter(calls)[i] for i in range(5,10)])+figure('daily-calls','The most common observed count is 7 calls, on 8 of the 30 days. The fractions account for exactly 30 days.')+r'''
The table must agree with the list, not just look plausible. Treating these proportions as predictions for future days assumes that the conditions remain relevant. An observed peak does not guarantee the next day's count.

\Needspace{8\baselineskip}
\subsection*{Read grouped quiz scores carefully}
'''+figure('quiz-scores','Bins are [25,30), [30,35), [35,40), [40,45), and [45,50]. The final bin includes 50, the highest possible score.')+r'''
The five counts are 3, 7, 12, 7, and 3, totaling 32 students. The tallest bin is [35,40), and the bin heights form a symmetric pattern. We know each score's interval, but not every exact score. These bars do not determine the exact average or prove that the raw scores are perfectly symmetric.
'''

solutions=['\n'+r'\clearpage\section*{Solutions and reasoning}'+'\n']
for i,(_,answer) in enumerate(checks,1):solutions.append('\n\\paragraph{Short check '+str(i)+'.} '+answer)
solutions.append('\n\\clearpage\n')
solutions.append(group('A','Practice A: Populations and samples',[
 r'(a) The population is all ER patients during the month; the sample is the patients recorded last Tuesday. Other days and times may have different workloads or wait times. (b) The population is all registered voters in the group of interest; the selected sample is the 1,000 registered voters. Random selection gives voters a chance to be included, but unavailable phone numbers or nonresponse can still change who actually answers. (c) The intended population is the coffee shop\textquotesingle s customers; the sample is the Monday-morning customers who answer. People visiting at other times are missed, and current morning visitors may have different preferences.',
 r'From a complete list of the city\textquotesingle s teenagers, randomly select a fixed number of different names so every group of that size has the same chance. Survey those selected and record nonresponses. Asking only members of an online gaming club would favor teenagers who participate in that club and could overrepresent particular screen-use patterns.',
 'A larger sample collected by the same limited method can repeat the same omission many more times. It gives more information about the people that method reaches, without automatically supplying information about the people it misses.',
]))
siblings=[4,7,5,2];transport=[10,4,3,3]
solutions.append(group('B','Practice B: Frequency tables',[
 probability_table(range(4),siblings)+r'The frequencies are 4, 7, 5, and 2, adding to 18. One sibling is the most common answer, occurring seven times.',
 probability_table(['Car','Bus','Bike','Walk'],transport)+r'Car is most common, with 10 responses. The other methods account for $4+3+3=10$ employees.',
 r'The known counts total $8+12+5=25$. The missing category has $30-25=5$ observations.',
]))
solutions.append(group('C','Practice C: Relative frequency and probability',[
 probability_table(range(4),siblings)+r'The exact total is $(4+7+5+2)/18=1$. The chance of exactly one sibling, within this group, is $7/18\approx0.3889$. More than one sibling combines the counts for 2 and 3: $(5+2)/18=7/18\approx0.3889$. These happen to be equal in this dataset.',
 r'Each of the five equally sized sections has probability $1/5=0.20$. Not red has probability $4/5=0.80$. Red or orange has probability $2/5=0.40$. This assumes a fair spinner.',
 r'Outcomes 1, 2, 3, 4, 5, and 6 each have probability $1/6$. P(4) is $1/6$. P(even) is $3/6=1/2$, from 2, 4, 6. P(greater than 4) is $2/6=1/3$, from 5 and 6.',
 r'$p=1-(0.15+0.30+0.25)=0.30$. The listed outcomes cover all the probability, so their shares must sum to 1.',
]))
solutions.append(group('D','Practice D: Bar charts',[
 probability_table(['Car','Bus','Bike','Walk'],transport)+figure('employee-transport','For a relative-frequency version, use bar heights 0.50, 0.20, 0.15, and 0.15 instead of the raw counts.')+r'Any pair containing car and one other method exceeds half: car + bus is 0.70, car + bike is 0.65, and car + walk is 0.65. No pair without car exceeds half. There is more than one correct pair.',
 r'The total is $2+8+5+3+2=20$ members. Exactly one book gives $8/20=0.40$. More than two books combines 3 and 4: $(3+2)/20=0.25$.',
 probability_table(['Cafeteria','Restaurant','Desk','Outside'],[18,10,8,4])+figure('lunch-locations','Cafeteria is the most common preference; outside is the least common. The vertical axis shows shares, not counts.'),
]))
solutions.append(group('E','Practice E: Histograms',[
 probability_table(['[20,25)','[25,30)','[30,35)','[35,40)','[40,45)'],[4,9,5,4,2])+figure('volunteer-ages',r'The largest bin is [25,30), with 9 of 24 observations: 0.375, or 37.5\%.')+r'The age 25 goes in the second bin, not the first. The five bin counts total 24.',
 r'The counts total $3+8+10+6+4+2=33$. The [10,15) bin has share $10/33\approx0.3030$. The display is somewhat skewed right: after the main cluster near 10--15 hours, the small bars extend farther toward larger hours than toward smaller hours.',
 'A bar chart compares separate categories, such as preferred study locations, using separate bars. A histogram groups numerical measurements into ordered intervals, such as commute time in 15-minute bins, with adjacent bars touching.',
]))
solutions.append(group('F','Practice F: Probability distributions',[
 r'(a) Valid: entries are between 0 and 1 and sum to 1. (b) Invalid: the sum is 1.2. (c) Invalid: one probability is negative; the sum is also only 0.4. (d) Valid: four entries of 0.25 sum to 1.',
 probability_table(['Red','Blue','Green'],[3,4,5])+figure('chip-distribution','The probabilities are 1/4, 1/3, and 5/12, based on equally likely individual chips.')+r'P(not blue) $=1-4/12=8/12=2/3$. Red and green together give the same result: $(3+5)/12=2/3$.',
 r'Sums 2 through 6 account for $1+2+3+4+5=15$ of the 36 equally likely pairs, so P(sum $\leq6$) $=15/36=5/12$. Sums 8 through 12 also account for $5+4+3+2+1=15$ pairs. Symmetry around 7 explains the equality. The six pairs summing to 7 belong to neither event.',
 r'All entries lie between 0 and 1, and $0.50+0.30+0.12+0.05+0.03=1$. P(at least one error) $=1-P(0)=0.50$; adding the four positive-error probabilities also gives 0.50.'+figure('document-errors','The tail extends toward larger error counts, so this display is skewed right.'),
]))
solutions.append(group('R','Chapter 2 review',[
 probability_table(range(4),[28,14,6,2])+figure('quality-defects','Width-one bins are centered at the integer defect counts. Most items have no defects; small bars extend toward larger counts.')+r'P(at least one defect) $=1-28/50=22/50=0.44$. The distribution is skewed right.',
 probability_table(['[0,15)','[15,30)','[30,45)','[45,60)'],[12,22,18,8])+figure('commute-review','All bins are 15 minutes wide. Their heights show relative frequencies.')+r'At least 15 and less than 45 minutes combines the middle two bins: $(22+18)/60=40/60=2/3\approx0.6667$. The stated endpoint rule includes 15 and excludes 45.',
 r'The three known probabilities total $1/3+1/4+1/6=4/12+3/12+2/12=9/12=3/4$. Therefore $p=1/4$. The first two sections have combined probability $1/3+1/4=7/12$.',
 'An empirical distribution comes from observed counts, such as the proportions of 80 surveyed workers using different commuting methods. A theoretical distribution comes from model assumptions, such as assigning each face of a fair die probability 1/6.',
 probability_table(range(4,10),[2,4,8,10,5,1])+figure('sleep-review','Most observations lie around 6--7 hours, with reported values from 4 through 9 hours.')+r'The shape is roughly mound-like, with a slightly longer tail toward the lower hours. A rough center is around 6--7 hours; the observed span is 4--9 hours. This description does not require the formal mean or standard deviation introduced next week. Fewer than 7 hours combines 4, 5, and 6: $(2+4+8)/30=14/30=7/15\approx0.4667$.',
 r'The population is all 400 students; the sample is the 20 students in that advisory. Every sampled student is a senior, while only 100 of 400 students in the school are seniors. The sample leaves out the other 300 students in three grade levels, so it cannot directly reveal their views.',
]))
solutions.append(r'''
\subsection*{Activities and further reading}
Use the \href{https://bobovski66.github.io/MathInSociety/demos/probability_distribution.html}{explorer} to distinguish observed counts and shares from a fixed model. The \href{https://bobovski66.github.io/MathInSociety/applications/week2_application.html}{transportation application} uses 80 survey responses; the \href{https://bobovski66.github.io/MathInSociety/applications/week2_ai.html}{next-token application} uses a four-outcome model for repeated draws. The \href{https://bobovski66.github.io/MathInSociety/discussions/week2_discussion.html}{discussion} asks you to design a survey about something that matters to you.

OpenStax provides additional explanations of \href{https://openstax.org/books/introductory-statistics-2e/pages/1-2-data-sampling-and-variation-in-data-and-sampling}{data and sampling} and \href{https://openstax.org/books/introductory-statistics-2e/pages/2-2-histograms-frequency-polygons-and-time-series-graphs}{histograms}. The AI activities refer to Hugging Face's \href{https://huggingface.co/docs/transformers/generation_strategies}{generation strategies} for the distinction between sampling and choosing a most probable token.
''')
practice=(ROOT/'scripts/week2_chapter_practice.tex').read_text()
references=solutions.pop()
write('readings/Math107_Chapter_02.tex',preamble+cover+''.join(reading)+references+extras+practice+''.join(solutions)+'\n\\end{document}\n')
os.sync();print('Built Chapter 2:',len(checks),'short checks and all 26 original exercise/review groups with complete solutions.')
