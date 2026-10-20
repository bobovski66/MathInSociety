"""Build a standalone illustrated chapter from the Week 7 reading and solved review."""
from pathlib import Path
import os,sys
from lxml import html
sys.dont_write_bytecode=True
from build_week8_chapters import conv, checks
ROOT=Path(__file__).resolve().parents[1]
preamble=(ROOT/'scripts/week8_chapter_preamble.tex').read_text().replace('8.\\arabic','7.\\arabic').replace('WEEK 8 / PART @PART@','WEEK 7').replace('@TOPIC@','Choosing What Best Means').replace('Week 8, Part @PART@:','Week 7:')
preamble+='\n\\widowpenalty=10000\n\\clubpenalty=10000\n'
cover=r'''
\begin{document}
{\small\sffamily\color{olive}WEEK 7 / OPTIMIZATION / COST, REVENUE, AND PROFIT\par}
\vspace{12pt}
{\fontsize{30}{35}\selectfont\bfseries\color{olive}Choosing what ``best'' means\par}
\vspace{10pt}
{\large Begin with a choice. Build a model of its consequences. Compare outcomes only after stating the goal and the available options.\par}
\begin{center}\includegraphics[width=\linewidth]{../assets/week7/cost-revenue-gap.pdf}\end{center}
\begin{tcolorbox}[title={A concrete setting for the week}]
A candle maker pays \$180 for a monthly stall and equipment, plus \$4 per candle made. Each candle sells for \$10. We will distinguish money received, money spent, money left over, and the change caused by one additional sale.
\end{tcolorbox}
This chapter assumes no previous business mathematics or calculus. Function notation, units, and graph reading are developed alongside the calculations. Work the short checks as you read; explanations appear at the end, followed by complete review solutions.

Week 6 studied balances changing over time. Here, quantity is the input: different sales plans for one month or event. Week 8 will extend these ideas to two production quantities and resource constraints.

\medskip
\href{https://bobovski66.github.io/MathInSociety/readings/week7_reading.html}{Online reading}\quad\textperiodcentered\quad\href{https://bobovski66.github.io/MathInSociety/demos/business_models.html}{Profit explorer}\quad\textperiodcentered\quad\href{https://bobovski66.github.io/MathInSociety/labs/week7_lab.html}{Guided laboratory}
\clearpage
'''
worked=r'''
\clearpage
\section*{Further Worked Models}
\subsection*{Rebuild a linear cost rule from two observations}
Suppose a company's modeled cost is \$1,800 at 100 items and \$2,600 at 200 items, for the same month and operation. We are told to assume the cost relationship is linear.

The quantity increases by 100 while total cost increases by \$800. Therefore the variable cost is
\[
v=\frac{2600-1800}{200-100}=\$8\text{ per item}.
\]
Substitute into $C(q)=F+8q$: $1800=F+8(100)$, so $F=1000$. The cost rule is $C(q)=1000+8q$.

Check the second value: $C(200)=1000+1600=2600$. The fixed expense is the extrapolated cost at q=0 under the stated linear assumption. Two observations alone do not establish that a real cost rule is linear outside the range; the model supplied that assumption.

\subsection*{What a profit formula does not identify}
If $P(q)=7q-420$, then fixed cost is \$420 and the margin is \$7 per item. But the price and variable cost are not separately determined. Both $p=12,v=5$ and $p=15,v=8$ produce that same margin and profit rule.

The extra statement $P(80)=140$ would not distinguish them: it already follows from $7(80)-420=140$. To recover price and variable cost separately, we need new information such as the sale price or a cost observation.

\begin{tcolorbox}[title={Information and assumptions}]
An equation can answer the question its data determine. A missing price cannot be recovered merely by rearranging the difference $p-v$ in a second way. Recognizing missing information is part of solving a model correctly.
\end{tcolorbox}

\clearpage
\subsection*{Same break-even quantity, different profit at a chosen volume}
A food cart has $F=350$, $v=4$, and $p=9$ for one event. Its profit is $P(q)=5q-350$, exact break-even is 70 meals, and profit at 100 sales is \$150.

Compare two changes separately. Option A raises price to \$11 without changing the other costs. Option B reduces fixed cost to \$250 while keeping the original price.

{\small\renewcommand{\arraystretch}{1.4}\begin{tabularx}{\linewidth}{@{}YYYY@{}}\toprule
Plan & Profit rule & Exact threshold & Profit at 100 sales\\\midrule
Original & $5q-350$ & 70 & \$150\\
A: price \$11 & $7q-350$ & 50 & \$350\\
B: fixed cost \$250 & $5q-250$ & 50 & \$250\\\bottomrule
\end{tabularx}}

Both changes give a 50-meal threshold, but A has a larger profit at 100 sales because it has a larger margin. The threshold alone does not describe the complete comparison. We also held the sales count fixed; a price increase or a smaller location could change actual sales.

\subsection*{An additional observation can change the recommendation}
Suppose a separate, invented sales estimate predicts 70 meals under A and 100 under B. Then A's profit is $7(70)-350=140$, while B's remains \$250. Under those estimates, B has the larger profit.

The estimates do not follow from the algebra. They are additional inputs that can be tested against observations. The calculation makes the consequences of each estimate visible.

\begin{tcolorbox}[title={A conclusion with its conditions}]
``At 100 sales under either plan, A gives \$100 more profit than B'' is supported by the first comparison. ``A is always the better real business decision'' is a stronger claim that the fixed-sales model does not establish.
\end{tcolorbox}
'''
review=r'''
\clearpage
\section*{Chapter 7 Review}
Use the stated period and units. Unless a question separates production from sales, assume every item made is sold. For whole items, distinguish the exact continuous threshold from the first usable whole-item count. Show enough work to make the comparison checkable.
\begin{enumerate}
\item A printing company has monthly fixed cost \$800 and variable cost \$3 per pamphlet. Pamphlets sell for \$8 each. Write C, R, and P. Find exact break-even. Make a table of all three outputs at $q=0,80,160,200,240$. Explain P(240).
\item A mobile car wash has fixed cost \$600 per month, price \$25 per car, and supplies cost \$7 per car. Write all three functions and find the margin. Find exact break-even and the first whole-car count avoiding a loss. What whole-car count first gives a profit of at least \$360?
\item For $C(q)=900+12q$ and $R(q)=21q$, find exact break-even and profit at q=150. Sketch both lines and label the intercepts, slopes, and intersection. On a separate profit graph, what is the vertical coordinate at break-even?
\item A freelance designer charges \$80 per billed hour and has fixed monthly cost \$320. The model includes \$20 per hour in materials and time cost. Write the modeled profit, find exact break-even hours, and find the hours needed for \$1,000 profit. Fractional hours are allowed.
\item A product sells for \$16, has variable cost \$7, and fixed cost \$540. Find exact break-even and profit at q=80. Repeat after lowering price to \$13, holding quantity and costs fixed. By how much does the threshold increase? What additional information is needed to compare actual pricing outcomes?
\item Two bakeries sell bread for \$7 per loaf. A has $F=400,v=2$; B has $F=200,v=4$. Write both profits, find exact thresholds, and find their equal-profit quantity. Which is better at q=60 and at q=140? Explain using both fixed cost and margin.
\item Describe the additive recursions for C, R, and P at whole quantities. Give the starting value and step for each in terms of F, v, and p. Why is the input here not automatically elapsed time?
\item A linear cost model gives C(100)=1800 and C(200)=2600. Recover v, F, and C(q), then verify both values. If you know only P(q)=7q−420, which parameters can you recover and which cannot be recovered separately?
\newpage
\item Cards have F=48, v=1.50, and p=6. Find the exact threshold and the smallest whole count avoiding a loss. Find P(10), P(11), and P(12). Does any whole count break even exactly?
\item Classify break-even when (a) F=100, p=v=4; (b) F=100, p=3, v=4; (c) F=0, p=v=4; (d) F=0, p=3, v=4. Avoid dividing by zero or interpreting a negative crossing as a usable sale count.
\item A candle maker has P(q)=6q−180 and capacity 25 this month. Find the best quantity and profit among whole counts from 0 to 25. Compare with the exact threshold. What changes if an explicitly separate option of not opening avoids all costs?
\item A table gives P(30)=90, P(40)=140, P(50)=150, P(60)=120. What best-choice claim is justified from these values alone? Can you conclude that 49 or 51 cannot do better? Explain what information is missing.
\item A candle seller has F=180 and v=4. Compare price \$10 with 60 sales against price \$12 with 35 sales. Which plan has greater modeled profit? At the \$12 price, what whole sales count would first exceed the other plan's profit?
\item A food stand has F=240 and v=3.50 for every meal prepared. Each sold meal brings \$9.50. If 80 are prepared and 60 are sold, find cost, revenue, and profit, assuming unsold meals have no further value. Compare with using q=60 in P(q)=6q−240; explain the difference.
\item The AI-service example has $C(q)=6000+0.40q$ and $R(q)=2.40q$. With whole counts from 4,000 through 5,000, compare profit maximization, session maximization, and cost minimization. What if the minimum commitment rises to 5,001 while capacity remains 5,000? Name a learning outcome the dollar model does not measure.
\item A nonprofit has fixed event cost \$1,200 and variable cost \$8 per attendee. Compare exact break-even at ticket prices \$20 and \$15. At the lower price, what whole attendance first avoids a loss? Check the cost, revenue, and profit there. Explain one reason the nonprofit might consider more than profit.
\end{enumerate}
'''
answers=r'''
\subsection*{Chapter review: solutions}
\begin{enumerate}
\item $C(q)=800+3q$, $R(q)=8q$, and $P(q)=5q-800$. Exact break-even is 160 pamphlets. For q-values 0, 80, 160, 200, 240, costs are 800, 1040, 1280, 1400, 1520; revenues are 0, 640, 1280, 1600, 1920; profits are $-800,-400,0,200,400$. At 240 sales, \$400 remains after the costs included in this model.
\item $C=600+7q$, $R=25q$, $P=18q-600$; margin is \$18 per car. The exact crossing is $600/18=33\tfrac13$, so 34 cars first avoid a loss. For profit at least \$360, solve $18q-600\geq360$, obtaining $q\geq53\tfrac13$. The first whole count is 54, with P(54)=372; P(53)=354 is insufficient.
\item Margin is 9 and threshold is 100. P(150)=450. Cost begins at (0,900) and has slope 12 dollars per item; revenue begins at (0,0) and has slope 21. Their intersection is (100,2100). On the profit graph, break-even is (100,0); the zero is profit, not the common cost and revenue.
\item $P(q)=60q-320$. Exact break-even is $320/60=16/3$ hours. For \$1,000 profit, solve $60q-320=1000$, obtaining q=22 billed hours. The modeled profit includes the listed time cost; costs not named are not automatically included.
\item Originally P=9q−540, the threshold is 60 and P(80)=180. At the lower price, P=6q−540, the threshold is 90 and P(80)=−60. The threshold increases by 30 items. The fixed-sales comparison does not predict whether lower price attracts enough additional sales; a demand observation or explicit estimate is needed.
\item $P_A=5q-400$, $P_B=3q-200$. Their exact thresholds are 80 and $66\tfrac23$. Equality gives $2q=200$, so q=100 and both profits are \$100. At 60, A gives −\$100 and B −\$20, so B has the smaller loss. At 140, A gives \$300 and B \$220, so A is higher. A has a larger fixed expense but a larger margin; the crossover is not a zero-profit crossing.
\item $C(0)=F$ and $C(q+1)=C(q)+v$. $R(0)=0$ and $R(q+1)=R(q)+p$. $P(0)=-F$ and $P(q+1)=P(q)+(p-v)$. The input counts units made and sold in one period; it compares possible volumes rather than automatically tracking days or months.
\item The cost change is \$800 for 100 extra items, so v=8. Then F=1800−8(100)=1000 and C=1000+8q. Substitution gives 1800 and 2600 at the stated quantities. From P=7q−420, F=420 and p−v=7; p and v separately require additional information.
\item $P=4.5q-48$, with exact threshold $32/3=10\tfrac23$. The first whole count avoiding loss is 11. P(10)=−3, P(11)=1.50, and P(12)=6 dollars. No whole count makes P exactly zero because the unique zero is not an integer.
\newpage
\item (a) P=−100 at every quantity, so none break even. (b) P=−q−100 is negative for every nonnegative q, so none break even. (c) P=0 at every nonnegative q, so every quantity breaks even. (d) P=−q, so only q=0 breaks even; positive quantities lose money.
\item Positive margin makes the largest allowed quantity best: q=25, P=−30. The exact threshold q=30 is beyond capacity. Under the original fixed-cost model even the best plan loses \$30. The explicitly separate no-opening option gives profit 0 if it avoids all costs, and would outperform that loss. We must not silently remove a fixed expense from one of the original plans.
\item Quantity 50 gives the largest profit among the four listed options. The table does not determine profit at 49, 51, or unlisted choices, so it cannot establish a global maximum. We need more allowed-choice values or a justified function and domain.
\item At \$10 with 60 sales, P=6(60)−180=180. At \$12 with 35 sales, P=8(35)−180=100. The lower-price plan is higher under these particular sales assumptions. To exceed 180 at the higher price, $8q-180>180$, so q>45. At least 46 whole sales are needed; 45 only ties.
\item Cost is 240+3.5(80)=520, revenue 9.5(60)=570, profit \$50. The one-count formula at 60 gives \$120 because it charges variable cost for only 60 prepared meals. The 20 additional prepared but unsold meals cost 20(3.5)=70 dollars, explaining the difference. Sales do not erase production costs.
\item Profit and session maximization choose q=5000, giving cost 8000, revenue 12000, profit 4000 dollars. Cost minimization chooses q=4000, giving cost 7600, revenue 9600, profit 2000. The two maximizing goals coincide here because margin is positive and all paid sessions have the same modeled revenue and cost. A minimum of 5001 with capacity 5000 is infeasible. Learning, accuracy, and affordability need separate evidence and criteria.
\item At \$20, margin is 12 and exact break-even is 100 attendees. At \$15, margin is 7 and the crossing is $1200/7=171\tfrac37$; 172 first avoid a loss. At 172, cost is 1200+8(172)=2576, revenue is 15(172)=2580, and profit is \$4. Access, mission, attendance, and service quality may also matter; the formula does not choose their priority.
\end{enumerate}
\subsection*{Continue with constraints}
Week 8 asks which combinations of two production quantities are feasible. Use the same habits: define variables and units, identify every limit, state the objective, compare only allowable plans, and return the result to the situation.
}
\end{document}
'''
tree=html.fromstring((ROOT/'readings/week7_reading.html').read_text());checks.clear();parts=[preamble,cover]
for id in ['choices','cost','profit','graphs','breakeven','marginal','optimize','tradeoffs','pricing','decisions']:
 text=conv(tree.get_element_by_id(id)).replace('../assets/week8/','../assets/week7/').replace('height=3.2in','height=3.0in')
 parts.append(('\n\\clearpage\n' if id in ['cost','graphs','decisions'] else '\n')+text)
parts.extend([worked,review,'\n\\clearpage\n{\\setlength{\\parskip}{4pt}\\setlist{itemsep=5pt,topsep=3pt}\n\\section*{Solutions and Reasoning}\n'])
for n,(_,answer) in enumerate(checks,1):parts.append('\n\\paragraph{Short check '+str(n)+'.} '+answer)
parts.append('\n\\clearpage\n'+answers)
target=ROOT/'readings/Math107_Chapter_07.tex';temp=target.with_suffix('.tmp')
with temp.open('w') as f:f.write('\n'.join(line.rstrip() for line in ''.join(parts).replace('−',r'\ensuremath{-}').splitlines())+'\n');f.flush();os.fsync(f.fileno())
os.replace(temp,target);os.sync();print('Built standalone chapter with',len(checks),'short checks and 16 review problems with solutions.')

from chapter_editorial import polish_generated_chapters
polish_generated_chapters([ROOT / "readings/Math107_Chapter_07.tex"])
