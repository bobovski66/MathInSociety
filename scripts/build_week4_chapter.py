"""Build a standalone illustrated chapter with corrected interpretations and complete solutions."""
from pathlib import Path
import os,sys,re
from lxml import html
sys.dont_write_bytecode=True
from build_week8_chapters import conv,checks,translations
ROOT=Path(__file__).resolve().parents[1]
translations.update({'μ':r'$\mu$','σ':r'$\sigma$','±':r'$\pm$','₋':r'$_{-}$','₃':r'$_3$','₄':r'$_4$','₅':r'$_5$','₆':r'$_6$','₇':r'$_7$','₈':r'$_8$','₉':r'$_9$'})
preamble=(ROOT/'scripts/week8_chapter_preamble.tex').read_text().replace('8.\\arabic','4.\\arabic').replace('WEEK 8 / PART @PART@','WEEK 4').replace('@TOPIC@','Statistical Inference').replace('Week 8, Part @PART@:','Week 4:')+'\n\\widowpenalty=10000\n\\clubpenalty=10000\n'
cover=r'''
\begin{document}
{\small\sffamily\color{olive}WEEK 4 / NORMAL DISTRIBUTIONS AND STATISTICAL INFERENCE\par}
\vspace{12pt}
{\fontsize{30}{34}\selectfont\bfseries\color{olive}Individual variation\\and population estimates\par}
\vspace{10pt}
{\large Locate an individual measurement, describe a normal region, and interpret uncertainty in an estimate from a sample.\par}
\begin{center}\includegraphics[width=\linewidth,height=3.15in,keepaspectratio]{../assets/week4/bottle-two-questions.pdf}\end{center}
\begin{tcolorbox}[title={Two questions about one process}]
A bottle at 516 mL is compared with a normal model centered at 500 mL with standard deviation 8 mL. A separate sample gives mean 503 mL and margin 2 mL. The first question concerns an individual bottle; the second concerns the process mean. A correct calculation must answer the intended question.
\end{tcolorbox}
Week 3 introduced center and spread. This chapter adds normal models, standardized position, sampling variability, and confidence intervals. Its core interval exercises supply their margins. The standard-error and repeated-sampling examples explain the meaning of those margins under stated assumptions.

Try the short checks before reading their explanations. Review exercises retain the principal numerical settings used in the course and include complete solutions. All examples are hypothetical.

\medskip
\href{https://bobovski66.github.io/MathInSociety/readings/week4_reading.html}{Online reading}\quad\textperiodcentered\quad\href{https://bobovski66.github.io/MathInSociety/demos/normal_z.html}{Statistical explorer}\quad\textperiodcentered\quad\href{https://bobovski66.github.io/MathInSociety/labs/week4_lab.html}{Laboratory}
\clearpage
'''
extensions=r'''
\section*{Applications of the Same Distinctions}
\subsection*{A nutrition label and a planned larger sample}
A label claims a mean of 230 calories per serving. A random sample of 64 boxes has mean 243 and a reported margin of 8 calories. The supplied interval is
\[
[243-8,243+8]=[235,251]\text{ calories}.
\]
It excludes 230. This is a comparison of a proposed population mean with an interval estimate, not a conclusion about every individual serving or an explanation of the discrepancy.

For a planning comparison, increase the sample size to 256 while holding the confidence level, variability, design, and estimated center fixed. The planned margin becomes
\[
8\sqrt{64/256}=4,
\]
so the planned interval is $[239,247]$. An actual new sample could change the center as well as the estimated margin.

\begin{center}\includegraphics[width=\linewidth,height=2.8in,keepaspectratio]{../assets/week4/nutrition-intervals.pdf}\end{center}
The main application retains these calculations. A fuller interpretation also requires the population definition, selection method, measurement procedure, and the method used to obtain the reported margin.

\clearpage
\subsection*{A benchmark score is a sample statistic}
A hypothetical model answers 171 of 200 test questions correctly. Its observed accuracy is $171/200=0.855$, or 85.5\%. With a supplied margin of five percentage points, its reported interval is $[80.5\%,90.5\%]$, equivalently $[0.805,0.905]$.

\begin{center}\includegraphics[width=\linewidth,height=3.5in,keepaspectratio]{../assets/week4/benchmark-estimate.pdf}\end{center}
The population is the defined collection of tasks that the sample can represent. This interval does not describe every possible request, every language, or every future answer. More data can reduce random sampling uncertainty without repairing an unrepresentative task collection or an inconsistent scoring rule.

Separate reported intervals also do not by themselves supply a formal test of a difference. Model A at $78\pm4$ and B at $80\pm4$ have overlapping intervals. That neither proves equality nor establishes superiority on every task. A suitable comparison may need task-level outcomes, especially if the same prompts were used for both models.
'''
review=r'''
\clearpage
\section*{Chapter 4 Review}
For normal-region questions, use the Empirical Rule approximations unless stated otherwise. Retain signs and measurement units. For interval questions, use the reported margin; do not substitute the individual standard deviation for it. Explain the population quantity being estimated.
\begin{enumerate}
\item Apple weights are approximately normal with mean 180 g and SD 15 g. Find the percentage between 165 and 195, the percentage above 210, and both endpoints of the middle 95\%. For commute times with mean 35 minutes and SD 8 minutes, find the percentage between 19 and 51, the z-score of 59, and the percentage below 27.
\item A normal model has mean 50 and SD 6. Give the central one-, two-, and three-SD intervals. Estimate the percentage below 44 and between 38 and 62. Explain why the central percentages must not be added together.
\item For mean 100 and SD 15, find z-scores of 115, 85, 100, and 130. For mean 40 and SD 5, recover the raw values at z = 2, $-1$, 0.5, and $-3$. What does a negative z-score establish?
\item An athlete runs a mile in 400 seconds. Comparable times have mean 480 seconds and SD 60 seconds. Calculate and interpret the z-score. Why might a negative score be preferred in this setting? Does calculating z require the population to be normal?
\item Student A scores 520 on a test with mean 500 and SD 100. Student B scores 28 on a test with mean 21 and SD 5. Compare their standardized positions and explain the limit of comparing tests of different subjects. Separately, compare scores 88 with mean 80 and SD 10, and 74 with mean 65 and SD 6.
\item Identify the parameter and statistic in each study: (a) 1,200 voters surveyed, 58\% support; (b) 40 fish measured, mean length 31.2 cm; (c) 50 cereal boxes measured, mean weight 368 g. State why the sample count is not the target proportion or mean.
\item A school wants the mean number of books read per student in a year. Describe a simple random sample of 100 from 800 enrolled students. Explain one possible source of nonresponse or measurement bias. Would a larger biased sample automatically remove it?
\item Construct the supplied intervals for (a) 82 with margin 4; (b) 3.7 hours with margin 0.5; (c) 47\% with margin six percentage points. Give each full width and identify the units.
\newpage
\item A mean estimate is 4.2 hours with margin 0.3. Does its interval lie entirely above 4 hours? A poll estimates 38\% with margin four percentage points. Is a value above 40\% excluded? Does the interval establish that the population share is above 40\%? Distinguish compatibility from such a conclusion.
\item Use the original nutrition-label study: claim 230 calories, sample mean 243, reported margin 8, n = 64. Construct the interval and interpret the comparison. Plan a sample of 256 with other conditions and center fixed. Find its margin and interval. Explain what is assumed about the new center.
\item A study with n = 200 seeks half its current margin. Find the approximate required n. Starting from n = 100 and margin 10 units, calculate the planned margins at n = 200, 400, and 900. Name the quantities held fixed and explain why precision does not establish freedom from bias.
\item A distribution has mean 200 and SD 25. Locate the individual value 245 with a z-score. A separate sample of 50 produces mean 212 with reported margin 7. Construct its interval. Is the known model mean 200 included? Could a valid confidence procedure sometimes miss its target?
\item A distribution has mean 60 and SD 12. Is an individual value 78 within two SD? A separate sample of 80 has mean 63 and margin 3. Does its interval include 60? Explain why an endpoint counts as inside and why the two calculations address different questions.
\item For independent samples of size 25 from a normal population with mean 70 and known SD 10, compute the SE and the approximately 95\% known-SD margin using 1.96. A sample mean is 75; construct its interval and check 70. Must exactly 95\% of 50 intervals contain the mean? What stays fixed when the procedure is repeated?
\item Bulb lifetimes are approximately normal with mean 1,200 hours and SD 100. Estimate the percentage between 1,000 and 1,400, the percentage above 1,400, and the middle-68\% interval. Find and interpret z for 940. Separately, with mean 80 and SD 6, recover x at z = 2.5. Can the Empirical Rule alone give that cutoff's exact tail percentage?
\item A model answers 171 of 200 sampled tasks correctly. Give its decimal and percentage accuracy and its interval with a supplied five-percentage-point margin. What population could it estimate? Models A and B report mean scores $78\pm4$ and $80\pm4$. State what those reports show and what additional evidence could help compare their performance.
\end{enumerate}
'''
answers=r'''
\subsection*{Chapter review: solutions}
\begin{enumerate}
\item Apple answers are about 68\%, about 2.5\%, and 150--210 g. The commute interval is $35\pm2(8)$, giving about 95\%. The value 59 has z = 3. Below 27 is below one SD under the mean, giving about 16\%. Tail answers use a complement followed by symmetry.
\item The intervals are [44,56], [38,62], and [32,68]. Below 44 is about 16\%; between 38 and 62 is about 95\%. The regions are nested: the 95\% region already includes the central 68\%, so adding those percentages would count the same outcomes repeatedly.
\item The z-scores are 1, $-1$, 0, 2. The recovered values are 50, 35, 42.5, 25. Negative z means below the mean. It does not require a negative original measurement and does not determine whether the outcome is desirable.
\item $z=(400-480)/60=-4/3\approx-1.33$. The time is about 1.33 SD below the comparable mean. A lower time means a faster run. Calculating z requires a finite mean and positive SD, not normality; using normal-tail percentages requires a suitable distributional assumption.
\item The original two scores give $z_A=0.2$, $z_B=1.4$, so B is farther above its own group's mean. The additional scores give 0.8 and 1.5, respectively. Relative position is not an absolute measurement of identical skills across different tests, nor a complete basis for judging a person.
\item (a) Parameter: population support proportion; statistic: 58\%. (b) Parameter: mean length in the defined fish population; statistic: 31.2 cm. (c) Parameter: mean box weight in the defined production population; statistic: 368 g. Counts 1,200, 40, and 50 describe how many units were observed, not the estimated mean or share.
\item Use a complete enrollment list with one identifier per student; select 100 distinct identifiers uniformly without replacement. Every subset of size 100 then has the same chance. Follow up consistently and define how books are counted. Nonresponse and recall or reporting errors can bias the result; collecting more observations by a biased procedure does not automatically remove that bias.
\item (a) [78,86], width 8 in the estimate's units. (b) [3.2,4.2] hours, width 1 hour. (c) [41\%,53\%], width twelve percentage points. Margin is half-width. A six-percentage-point adjustment differs from six percent of the estimate.
\newpage
\item The hours interval is [3.9,4.5], so it includes 4 and values below 4; it is not entirely above 4. The poll gives [34\%,42\%]. Values such as 41\% are compatible with that interval, but values at or below 40\% are also included. The interval therefore does not establish that the population share exceeds 40\%. Compare the full range, not only the point estimate.
\item The interval is [235,251] calories and excludes the claimed mean 230. Under the stated planning assumptions, $E_{\rm new}=8\sqrt{64/256}=4$, and the held-center interval is [239,247]. It also excludes 230. Keeping center 243 is an explicit comparison assumption, not a prediction of the next sample. Neither interval describes every individual box or identifies a cause of the discrepancy.
\item Required n is about 800. From baseline n = 100 and E = 10, planned margins are $10/\sqrt2\approx7.07$ at 200, 5 at 400, and $10/3\approx3.33$ at 900. The comparison keeps confidence, variability, and design comparable. Reduced random sampling variability does not correct an unrepresentative selection or a systematic measurement error.
\item The individual z-score is $(245-200)/25=1.8$. The sample interval is [205,219], which excludes the known model mean 200. That can occur even under a valid procedure: coverage below 100\% permits misses. A z-score describes an individual against the model; the interval comes from the separate observed sample.
\item $z=(78-60)/12=1.5$, so 78 is within two SD. The sample interval is [60,66], including 60 at its lower endpoint. Its endpoints are included in the supplied interval comparison. Neither the z-score nor this parameter interval substitutes for the other.
\item SE is $10/\sqrt{25}=2$ and margin is $1.96(2)=3.92$. The sample interval is [71.08,78.92], which misses 70. A set of 50 intervals need not have exactly 95\% coverage; 47.5 containing intervals is not even a possible count. The population parameter remains fixed while samples, means, and interval locations vary. Individual SD stays 10 when n changes.
\newpage
\item About 95\% lie between 1,000 and 1,400 hours; about 2.5\% lie above 1,400; the central 68\% spans 1,100--1,300 hours. For 940, $z=(940-1200)/100=-2.6$, or 2.6 SD below the mean. In the separate model, $x=80+2.5(6)=95$. The Empirical Rule provides no exact tail percentage at z = 2.5. Its one-tail approximations place that tail between the values at 2 and 3 SD; a normal-distribution calculation is needed for a more precise value.
\item Accuracy is $171/200=0.855=85.5\%$. Its supplied-margin interval is [80.5\%,90.5\%], or [0.805,0.905]. An appropriate population is a defined collection of tasks represented by the sample under the specified scoring conditions. A and B have intervals [74,82] and [76,84]; their point estimates differ by 2 and their intervals overlap. Overlap alone is not a formal test of the difference and does not prove equality. Task-level results, the relation between the two samples, and an interval or other suitable analysis for the performance difference could add evidence. No such mean comparison establishes a ranking on every task.
\end{enumerate}
\subsection*{References and activities}
The NIST Engineering Statistics Handbook provides accounts of the \href{https://www.itl.nist.gov/div898/handbook/eda/section3/eda3661.htm}{normal distribution}, \href{https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm}{confidence limits for a mean}, and \href{https://www.itl.nist.gov/div898/handbook/prc/section1/prc14.htm}{confidence interpretation and known-SD intervals}. The online explorer uses repeated samples from a specified normal population to illustrate coverage; the laboratory's core interval questions use supplied margins.

The \href{https://bobovski66.github.io/MathInSociety/applications/week4_application.html}{nutrition-label application}, \href{https://bobovski66.github.io/MathInSociety/applications/week4_ai.html}{AI evaluation application}, and \href{https://bobovski66.github.io/MathInSociety/discussions/week4_discussion.html}{bottle-fill discussion} apply the same distinction between individual observations and estimated population quantities. Week 5 considers how measurements then guide actions in a feedback loop.
}
\end{document}
'''
tree=html.fromstring((ROOT/'readings/week4_reading.html').read_text())
def normalize(t):
 t=t.replace('x̄',r'\(\bar x\)').replace('p̂',r'\(\widehat p\)')
 return re.sub(r'√(\d+|[a-z])',lambda m:r'\(\sqrt{'+m[1]+r'}\)',t)
for e in tree.iter():
 if isinstance(e.tag,str):
  if e.text:e.text=normalize(e.text)
  if e.tail:e.tail=normalize(e.tail)
checks.clear();parts=[preamble,cover]
for id in ['normal','empirical','tails','zscores','sampling','variability','intervals','confidence','precision','questions']:
 text=conv(tree.get_element_by_id(id)).replace('../assets/week8/','../assets/week4/').replace('height=3.2in','height=2.8in')
 for name,height in [('empirical-bands','4.7'),('repeated-intervals','4.1'),('standardized-comparison','3.35'),('bottle-two-questions','3.4')]:
  text=re.sub(r'height=2\.8in,keepaspectratio\]\{(\.\./assets/week4/'+re.escape(name)+r'\.pdf)\}',lambda m:'height='+height+'in,keepaspectratio]{'+m[1]+'}',text)
 parts.append(('\n\\clearpage\n' if id in ['empirical','sampling','intervals','confidence'] else '\n')+text)
parts.extend([extensions,review,'\n\\clearpage\n{\\setlength{\\parskip}{4pt}\\setlist{itemsep=5pt,topsep=3pt}\n\\section*{Solutions and Reasoning}\n'])
for n,(_,answer) in enumerate(checks,1):parts.append('\n\\paragraph{Short check '+str(n)+'.} '+answer)
parts.append('\n\\clearpage\n'+answers)
p=ROOT/'readings/Math107_Chapter_04.tex';t=p.with_suffix('.tmp')
with t.open('w') as f:f.write('\n'.join(line.rstrip() for line in ''.join(parts).replace('−',r'\ensuremath{-}').splitlines())+'\n');f.flush();os.fsync(f.fileno())
os.replace(t,p);os.sync();print('Built standalone Week 4 chapter:',len(checks),'short checks and sixteen review problems with complete solutions.')

from chapter_editorial import polish_generated_chapters
polish_generated_chapters([ROOT / "readings/Math107_Chapter_04.tex"])
