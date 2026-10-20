"""Build a standalone illustrated chapter from the explanatory Week 6 source."""
from pathlib import Path
import os,sys
from lxml import html
sys.dont_write_bytecode=True
from build_week8_chapters import conv,checks
ROOT=Path(__file__).resolve().parents[1]
preamble=(ROOT/'scripts/week8_chapter_preamble.tex').read_text().replace('8.\\arabic','6.\\arabic').replace('WEEK 8 / PART @PART@','WEEK 6').replace('@TOPIC@','Interest and Loans').replace('Week 8, Part @PART@:','Week 6:')+'\n\\widowpenalty=10000\n\\clubpenalty=10000\n'
cover=r'''
\begin{document}
{\small\sffamily\color{olive}WEEK 6 / CONTINUOUS MATH I / INTEREST AND LOANS\par}
\vspace{12pt}
{\fontsize{31}{35}\selectfont\bfseries\color{olive}Following the balance\par}
\vspace{10pt}
{\large Start with one amount. State the period and the rule. Use the ending balance as the next input.\par}
\begin{center}\includegraphics[width=\linewidth]{../assets/week6/growth-over-time.pdf}\end{center}
\begin{tcolorbox}[title={The setting for the week}]
A \$2,000 balance can grow through fixed dollar additions or a percentage of its current amount. A loan combines percentage growth with payments that subtract from the debt. Tables and graphs make the differences visible.
\end{tcolorbox}
This chapter develops the meaning of percentages, period rates, and repeated updates before using formulas. It distinguishes an ending balance from interest earned, a scheduled payment from principal reduction, and a simulation's stopping month from an actual payoff.

The core work uses arithmetic, powers, and simple equations. Try each short check before consulting its explanation. The review includes complete solutions and optional investigations of rounding and modeling assumptions.

\medskip
\href{https://bobovski66.github.io/MathInSociety/readings/week6_reading.html}{Online reading}\quad\textperiodcentered\quad\href{https://bobovski66.github.io/MathInSociety/demos/interest_loans.html}{Interest and loan explorer}\quad\textperiodcentered\quad\href{https://bobovski66.github.io/MathInSociety/labs/week6_lab.html}{Guided laboratory}
\clearpage
'''
extensions=r'''
\clearpage
\section*{Two Further Applications}
\subsection*{A fixed repayment comparison with full precision}
The online application starts with an \$8,000 balance, a nominal annual rate of 18\%, and monthly interest $i=0.015$. Interest is added first; fixed payments follow. There are no purchases, fees, or rate changes.

Both plans incur \$120 first-month interest. A \$160 payment reduces principal by \$40 and ends at \$7,960. A \$300 payment reduces principal by \$180 and ends at \$7,820. In month 2, their interest charges are \$119.40 and \$117.30 because the starting balances now differ.

{\small\renewcommand{\arraystretch}{1.4}\begin{tabularx}{\linewidth}{@{}YYYY@{}}\toprule
Regular payment & Payoff month & Total paid & Total interest\\\midrule
\$160 & 94 & \$14,897.89 & \$6,897.89\\
\$300 & 35 & \$10,293.42 & \$2,293.42\\\bottomrule
\end{tabularx}}

This table keeps full internal precision and rounds displayed money to cents. The actual final payments are approximately \$17.89 and \$93.42. The larger scheduled payment saves 59 months and about \$4,604.46 of interest when the difference is calculated before display rounding. Subtracting the displayed rounded interest totals gives a one-cent difference.

\begin{center}\includegraphics[width=\linewidth]{../assets/week6/card-repayment.pdf}\end{center}
The comparison describes the consequences of two stated schedules. Monthly affordability requires information beyond these model inputs. The \href{https://www.consumerfinance.gov/ask-cfpb/how-does-my-credit-card-company-calculate-the-amount-of-interest-i-owe-en-51/}{CFPB's explanation of actual interest calculations} also describes why a real card's daily-balance method can differ from our simplified monthly model.

\clearpage
\subsection*{A resource index can follow the same growth mathematics}
An invented computing-capacity index begins at 100 units. One plan adds 25 units each year: $A_k=100+25k$. A second grows by 25\%: $B_k=100(1.25)^k$.

Both give 125 after one year. After two, the additive plan gives 150 but percentage growth gives 156.25. Its second increase is 31.25 because it acts on the updated base 125. These are resource-index values, not counts of whole machines or measurements of intelligence.

Suppose a third plan grows by 25\% until a ceiling 400 is reached. Its rule is
\[
L_0=100,\qquad L_{k+1}=\min(400,1.25L_k).
\]
Here min means choose the smaller value. At year 6, the limited and uncapped percentage plans both have about 381.47. At year 7, the uncapped value is about 476.84 while the limited rule selects 400.

\begin{center}\includegraphics[width=\linewidth]{../assets/week6/ai-growth-limits.pdf}\end{center}
The ceiling changes the rule and thus the trajectory. It is an explicit hypothetical policy, not a forecast about any real AI operation. Learning, reliability, energy, and useful service each require suitable measures and observations.
'''
review=r'''
\clearpage
\section*{Chapter 6 Review}
Show units and at least one substituted expression or update. For savings formulas, keep precision until the final displayed answer. For loan tables, use monthly cent rounding unless the question explicitly says full precision. Assume no fees or new borrowing unless stated.
\begin{enumerate}
\item A \$5,000 account earns 4\% simple interest annually. Write its balance formula, give balances for years 0 through 5, and find the time to \$6,000. What is the fixed yearly interest? Also recover the simple annual rate when \$500 becomes \$560 in four years.
\item The same \$5,000 instead earns 4\% compounded annually. Give balances for years 0 through 5, compare the interest in year 1 with year 5, and find how much more it holds after five years than the simple model. Explain the source of the extra gain.
\item For \$1,000 at a 6\% nominal annual rate over ten years, compare annual, quarterly, monthly, and daily compounding. For daily, use 365 equal periods per year. Report balances, interest earned, and the monthly decimal rate and update count.
\item A 6\% nominal annual rate is compounded quarterly for two years. Find the rate per quarter, the number of factors, and the final balance on \$1,000. Separately, find the effective annual yield for a 3\% nominal annual rate compounded monthly, as both a decimal and a percentage.
\item Use the Rule of 72 to estimate (a) doubling at 12\% annually, (b) doubling at 7\%, (c) quadrupling at 7\%, and (d) the annual rate for doubling in six years. Explain why these are estimates under a continuing compound-growth rule.
\item A hypothetical unpaid \$30,000 balance grows by 6\% compounded annually, with no other charges. Estimate its balance after 12 years using the Rule of 72, then compute the compound value. Check the factors at years 11 and 12 to locate the first completed annual update reaching twice the original amount. Do not assume a real loan necessarily follows this no-payment rule.
\item A \$2,500 loan has monthly rate 0.01 and payment \$120. Build the first four monthly rows, with interest, actual payment, principal reduction, and ending balance. Compare a rough estimate based on a constant \$95 monthly principal reduction with the actual schedule's payoff in month 24. Why does the rough estimate differ?
\item For the reading's \$4,000 loan at 6\% nominal annual interest and \$200 monthly payment, verify the first two rows and the last-payment calculation. Use monthly cent rounding. Find total paid and total interest. Why would multiplying 22 by \$200 overstate the amount paid?
\newpage
\item Two \$5,000 loans use a 6\% nominal annual rate with monthly payments \$150 and \$250. Compare first-month interest, first ending balances, and second-month interest, using cent rounding. Predict which fixed schedule has lower total interest and explain the balance mechanism.
\item A \$1,000 debt has monthly rate 1\%. Classify fixed payments \$5, \$10, and \$50. Separately, how long does \$1,000 at zero interest take to repay with \$100 monthly payments? What if its payment is zero? What if the starting debt is zero?
\item Account A starts at \$1,000 with 5\% simple annual interest. Account B starts at \$1,000 with 4\% annual compounding. Compare balances at years 5, 10, 20, and 30. Check years 11 and 12 to find when B first overtakes A at a completed annual update. Why can B eventually lead despite its smaller percentage rate?
\item A hypothetical unpaid \$3,000 balance has a 24\% nominal annual rate divided across monthly updates. Find the monthly percentage. Apply the Rule of 72 in \emph{monthly periods} and compute balances after 12 and 36 months. Should the 12-month result already be double? Explain.
\item In the \$8,000 application, use full internal precision to compare \$160 and \$300 payments at nominal annual rate 18\%. Give payoff months, final actual payments, total paid, and total interest. Explain the first-month agreement and later divergence. Why can subtracting rounded displayed totals differ by one cent from rounding their unrounded difference?
\item Optional horizon investigation: a \$200,000 loan uses nominal annual rate 4.5\%, monthly interest, and a fixed payment rounded to \$1,013.37. Compute the budget estimate of 360 such payments, its amount above principal, and that excess as a percentage of principal. Then use cent rounding and a 360-month horizon in the explorer. Does the balance actually reach zero? Explain the residual and how a simulator must report it.
\item Compare the reading's \$4,000, 6\%, \$200-payment schedule using cent-rounded monthly interest versus full internal precision. Give payoff month, final payment, and total interest under each convention. What explains a small difference? What information should accompany a reported total?
\item A hypothetical capacity index begins at 100. Compare adding 25 per year, growing 25\% per year, and growing 25\% with a ceiling 400. Find all three values at year 2 and year 12, and locate the limited plan's first departure from the uncapped plan. Do equal endpoints establish identical paths? Name an important outcome this resource index does not measure.
\end{enumerate}
'''
answers=r'''
\subsection*{Chapter review: solutions}
\begin{enumerate}
\item $A(t)=5000(1+0.04t)=5000+200t$. Balances are 5000, 5200, 5400, 5600, 5800, 6000 dollars, so \$6,000 is reached at year 5. Each year adds \$200 based on the original principal. For \$500 growing to \$560 in four simple-interest years, $r=(560/500-1)/4=0.03$, or 3\% annually.
\item $B_t=5000(1.04)^t$ gives 5000.00, 5200.00, 5408.00, 5624.32, 5849.29, 6083.26 dollars. Year 1 earns \$200; year 5 earns approximately \$233.97. The extra balance over the simple model is approximately \$83.26. Earlier interest is included in later percentage calculations; the rate itself stays at 4\%.
\item Final balances are approximately 1790.85 annually, 1814.02 quarterly, 1819.40 monthly, and 1822.03 daily. Subtract 1000 to get interest 790.85, 814.02, 819.40, and 822.03 dollars. The monthly decimal rate is 0.06/12=0.005 and the count is 120. The comparison fixes the nominal annual rate, starting amount, and duration.
\item Quarterly rate is 0.06/4=0.015, or 1.5\%, with 8 factors. $1000(1.015)^8\approx1126.49$. The effective annual yield at 3\% nominal with monthly compounding is $(1+0.03/12)^{12}-1\approx0.030416$, or about 3.0416\%. Multiply the decimal yield by 100 to express it as a percentage.
\item (a) $72/12=6$ years. (b) $72/7\approx10.29$ years. (c) About $2(72/7)\approx20.57$ years. (d) About 12\% annually. The Rule of 72 is an approximation for continuing percentage growth, not an equality identifying an exact balance on a particular crediting date.
\item One estimated doubling gives approximately \$60,000. Direct calculation gives $30000(1.06)^{12}\approx60365.89$. Factors at years 11 and 12 are about 1.898 and 2.012. Thus the first completed annual update reaching twice the start is year 12. The small excess over two is consistent with the rule being an estimate.
\item Interest/end-balance pairs for months 1--4 are (25.00,2405.00), (24.05,2309.05), (23.09,2212.14), and (22.12,2114.26), all dollars. Subtract each interest from 120 to get principal reductions 95.00, 95.95, 96.91, and 97.88. A constant \$95 reduction gives $2500/95\approx26.32$ months, or 27 whole payments to clear the amount under that simplified rule. The actual schedule finishes in 24 months because the declining balance reduces interest and increases the principal part of later payments.
\item Month 1 is interest 20.00, payment 200, end 3820.00. Month 2 is interest 19.10, payment 200, end 3639.10. After 21 payments, 24.87 remains. Month 22 adds 0.12 interest, so actual payment is 24.99 and end is zero. Total paid is $21(200)+24.99=4224.99$; total interest is 224.99. Twenty-two full payments would count \$175.01 that is not owed under this schedule.
\newpage
\item Both first interest charges are \$25. With a \$150 payment the first end is \$4,875; with \$250 it is \$4,775. Second interest is \$24.38 versus \$23.88 after cent rounding. At the same fixed rate and without new charges, the larger payment leaves a smaller base for later interest, shortening the schedule and reducing total interest. The extra monthly commitment is a separate consideration.
\item The first interest charge is \$10. Payment 5 leaves growing debt; 10 keeps it constant; 50 reduces it and eventually repays it under the fixed rule. At zero interest, ten \$100 payments repay \$1,000. With zero payment it stays owed unchanged. A zero starting debt needs no payments and incurs no interest in this model.
\item A's balances are 1250, 1500, 2000, 2500 at years 5, 10, 20, 30. B's are approximately 1216.65, 1480.24, 2191.12, 3243.40. At year 11, A is 1550 while B is about 1539.45; at year 12, A is 1600 while B is about 1601.03. B first overtakes at year 12 among completed annual updates. Its dollar increases grow with its base, while A continues adding the fixed \$50.
\item Monthly rate is 0.24/12=0.02, or 2\%. The Rule of 72 estimates $72/2=36$ \emph{months} per doubling. After 12 months, $3000(1.02)^{12}\approx3804.73$; after 36, $3000(1.02)^{36}\approx6119.66$. The first value is not yet near a full doubling because only one of the estimated three years has passed. The approximation is consistent with the roughly doubled 36-month value.
\item The \$160 plan finishes in month 94 with a final payment about \$17.89, total paid \$14,897.89, and total interest \$6,897.89. The \$300 plan finishes in month 35 with final payment about \$93.42, total paid \$10,293.42, and interest \$2,293.42. Both first interest charges are \$120, calculated before payment. Their differing balances then produce different charges. Subtracting full-precision interest totals gives savings about \$4,604.46; subtracting the separately rounded displays gives \$4,604.47 because rounding is applied at a different stage.
\item The budget estimate is $360(1013.37)=364813.20$. Its excess above principal is 164813.20, or 82.4066\% of 200000. This total is a calculation about 360 scheduled amounts, not proof of exact payoff. With monthly cent rounding, \$0.63 still remains after payment 360. A fixed-payment simulation reports an outstanding balance at that horizon. Under the same capped-payment rule, a 361st actual payment of \$0.63 clears it; total paid is then \$364,813.83. An adjusted final closing payment would be another explicit schedule choice.
\item Both finish in month 22. Monthly cent rounding gives final payment \$24.99 and total interest \$224.99. Keeping full internal precision gives a final payment about \$25.00 and total interest about \$225.00. The one-cent displayed difference arises from the stages at which rounding occurs. Report the rate, timing, and rounding convention with the totals.
\item At year 2, additive gives 150; uncapped and limited percentage growth give 156.25. At year 12, additive gives 400, uncapped growth about 1455.19, and limited growth 400. The limited plan first differs in year 7: its cap gives 400 instead of the uncapped 476.84. Matching year-12 endpoints for the additive and limited plans do not imply matching earlier values. Learning, reliability, useful service, and energy impact require separate definitions and observations.
\end{enumerate}
\subsection*{Further reading}
\href{https://www.investor.gov/additional-resources/information/youth/teachers-classroom-resources/what-compound-interest}{Investor.gov: What is compound interest?} introduces compounding and the Rule of 72. The \href{https://www.investor.gov/financial-tools-calculators/calculators/compound-interest-calculator}{Investor.gov compound-interest calculator} can also include later contributions; this chapter's basic growth comparison uses none. The CFPB source linked in the loan application explains daily-balance calculations that can differ from our classroom monthly model.

}
\end{document}
'''
tree=html.fromstring((ROOT/'readings/week6_reading.html').read_text());checks.clear();parts=[preamble,cover]
for id in ['rates','simple','compound','frequency','doubling','loans','paymentparts','payoff','threshold','decisions']:
 text=conv(tree.get_element_by_id(id)).replace('../assets/week8/','../assets/week6/').replace('height=3.2in','height=2.9in')
 parts.append(('\n\\clearpage\n' if id in ['simple','frequency','decisions'] else '\n')+text)
parts.extend([extensions,review,'\n\\clearpage\n{\\setlength{\\parskip}{4pt}\\setlist{itemsep=5pt,topsep=3pt}\n\\section*{Solutions and Reasoning}\n'])
for n,(_,answer) in enumerate(checks,1):parts.append('\n\\paragraph{Short check '+str(n)+'.} '+answer)
parts.append('\n\\clearpage\n'+answers)
p=ROOT/'readings/Math107_Chapter_06.tex';t=p.with_suffix('.tmp')
with t.open('w') as f:f.write('\n'.join(line.rstrip() for line in ''.join(parts).replace('−',r'\ensuremath{-}').splitlines())+'\n');f.flush();os.fsync(f.fileno())
os.replace(t,p);os.sync();print('Built standalone chapter with',len(checks),'short checks and sixteen review problems with solutions.')

from chapter_editorial import polish_generated_chapters
polish_generated_chapters([ROOT / "readings/Math107_Chapter_06.tex"])
