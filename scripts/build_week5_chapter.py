"""Build the standalone, illustrated Week 5 chapter and complete review solutions."""
from pathlib import Path
import os,sys
from lxml import html
sys.dont_write_bytecode=True
from build_week8_chapters import conv,checks,translations
ROOT=Path(__file__).resolve().parents[1]
for c,tex in {'₋':r'$_{-}$','₃':r'$_3$','₄':r'$_4$','₅':r'$_5$','₆':r'$_6$','₇':r'$_7$','₈':r'$_8$','₉':r'$_9$','⁵':r'$^5$','ᴴ':r'$^H$','√':r'$\sqrt{\vphantom m}$'}.items():translations[c]=tex
preamble=(ROOT/'scripts/week8_chapter_preamble.tex').read_text().replace('8.\\arabic','5.\\arabic').replace('WEEK 8 / PART @PART@','WEEK 5').replace('@TOPIC@','Cybernetics and Feedback').replace('Week 8, Part @PART@:','Week 5:')+'\n\\widowpenalty=10000\n\\clubpenalty=10000\n'
cover=r'''
\begin{document}
{\small\sffamily\color{olive}WEEK 5 / MATHEMATICS IN SOCIETY / FEEDBACK AND INFORMATION\par}
\vspace{12pt}
{\fontsize{31}{35}\selectfont\bfseries\color{olive}When information changes what happens next\par}
\vspace{10pt}
{\large Build a loop from familiar sequences. Follow the state, the report, the correction, and the next state.\par}
\begin{center}\includegraphics[width=\linewidth,height=2.85in,keepaspectratio]{../assets/week5/immediate-delayed.pdf}\end{center}
\begin{tcolorbox}[title={The setting for the week}]
Two greenhouses start at $64^\circ$F and aim for $70^\circ$F. Both correct half of the reported difference each hourly step. One uses a current report; the other uses a one-hour-old report. The delayed path passes the target even though the controller is trying to correct a shortage.
\end{tcolorbox}
Cybernetics studies communication, feedback, and control in machines, living things, and social systems. We develop its basic questions using the recursive sequences of Week 1 and the measurements and variation of Weeks 3--4. No engineering or calculus is assumed.

Try each short check before consulting its explanation in the solutions. The review includes numerical updates, interpretation, historical questions, and complete solutions. Optional information-theory questions use powers of two before logarithms.

\medskip
\href{https://bobovski66.github.io/MathInSociety/readings/week5_reading.html}{Online reading}\quad\textperiodcentered\quad\href{https://bobovski66.github.io/MathInSociety/demos/cybernetics.html}{Feedback explorer}\quad\textperiodcentered\quad\href{https://bobovski66.github.io/MathInSociety/labs/week5_lab.html}{Guided laboratory}
\clearpage
'''
extensions=r'''
\clearpage
\section*{Two Further Worked Settings}
\subsection*{A school receives progress reports one week late}
A tutoring program's invented score model starts at 56 and aims for 80. Its rule is next score = current score $+0.5(80-\text{report})$. A step is one week. With delay, assume the pre-start score is also 56.

{\small\renewcommand{\arraystretch}{1.35}\begin{tabularx}{\linewidth}{@{}YYY@{}}\toprule
Week & Current-report score & One-week-old-report score\\\midrule
0 & 56 & 56\\
1 & 68 & 68\\
2 & 74 & 80\\
3 & 77 & 86\\
4 & 78.5 & 86\\
5 & 79.25 & 83\\\bottomrule
\end{tabularx}}

At week 2, the delayed score is already 80, but the available report describes week 1's score of 68. The next correction is $0.5(80-68)=6$, giving 86. The following report is 80, so it calls for zero correction and leaves the state at 86.

\begin{center}\includegraphics[width=\linewidth,height=2.9in,keepaspectratio]{../assets/week5/school-feedback.pdf}\end{center}
This model isolates report timing. It does not claim that practice produces an exact score increase, that a single test measures all learning, or that scores have no bounds. Students also respond to how they are assessed. The measurement and the goal are choices to examine, not neutral facts supplied by the equation.

\clearpage
\subsection*{A text predictor assigns probabilities to the next token}
A token is a model's unit of text; it may be a word, a word fragment, or punctuation. Suppose a predictor gives the token that actually occurs probability $p$. Its surprisal is $I=-\log_2 p$ bits. For $p=1/2^k$, the score is $k$ bits.

\begin{center}\includegraphics[width=\linewidth,height=2.7in,keepaspectratio]{../assets/week5/information-bits.pdf}\end{center}
For four observed tokens given probabilities $1/2,1/4,1/8,1/4$, the scores are 1, 2, 3, 2 bits. Total surprise is 8 bits; average surprise is 2 bits per token. This empirical mean negative log probability is commonly called cross-entropy loss for the observed sequence. Its perplexity is $2^2=4$, an effective uncertainty scale. It is not necessarily the number of choices offered at every position.

Under an idealized coding model, 100 tokens averaging 2 bits per token correspond to about 200 bits, apart from coding overhead. Actual coding methods approach this scale over sequences; a fractional-bit score need not be a literal fractional stored bit for an isolated token.

The score can supply information for a training update, but it is not a complete learning algorithm. Lower surprise on one observed token does not establish performance across a task, truthfulness, or usefulness. Entropy averages over possible source outcomes; empirical cross-entropy averages a model's surprise over observed outcomes. Natural-log software conventions give nats rather than bits without changing which probability has lower surprise.

\begin{tcolorbox}[title={An endpoint matters}]
If $p=1$, surprisal is 0. If a model assigns $p=0$ to an event that occurs, its surprise has no finite value. The finite surprise calculator requires $0<p\leq1$. In entropy calculations, the contribution $p\log p$ has limiting value 0 at $p=0$.
\end{tcolorbox}
'''
review=r'''
\clearpage
\section*{Chapter 5 Review}
Show the report used in each update. Temperatures are in degrees Fahrenheit unless otherwise stated. Keep internal precision; round displayed values only when requested. A short graph supports a claim about its displayed steps; identify any stronger conclusion that needs additional reasoning.
\begin{enumerate}
\item A sequence starts at $a_0=7$ and uses $a_{n+1}=a_n+4$. List $a_0$ through $a_4$. How many updates produced the last value? Explain what $a_{n-1}$ means when $n=3$.
\item Draw or describe a feedback loop for a water tank. Identify state, sensor, target, controller, actuator, and how the next measurement closes the loop. Contrast it with a valve opened on a fixed daily schedule.
\item A water level has target 100 cm, start 84 cm, and current reports. With response strength 0.25, compute two updates, listing current state, report, error, correction, and next state. What fraction of the old gap remains after one update?
\item The greenhouse has target 70, start 64, strength 0.5, and current reports. Find states $x_1$ through $x_4$. Explain why adding 3 at every step would describe a different rule.
\item Change only the report age to one step, with $x_{-1}=x_0=64$. Find $x_1$ through $x_7$. At the updates producing $x_3$ and $x_4$, separately name the current state, report, and correction. Why is $x_3$ above target?
\item A delayed inventory system has target 100 units, current stock 60, and a report of 80. It orders half the reported shortage. Compute the delayed order and compare with a current-report order. Name one real inventory effect missing from this update.
\item For current reports, target 10, and start 0, calculate three updates using strengths 0.5, 1.5, 2, and 2.5. Explain their different behavior using the remaining-gap factor $1-k$. What if the starting state were exactly 10?
\item A graph shows decreasing peaks over eight steps. What does that establish, and what does it not prove? Distinguish overshoot, oscillation, a shrinking envelope, and convergence.
\newpage
\item A sensor in a steady environment has approximately normal readings with mean 68 and standard deviation 2. Find z-scores for 72 and 65. Does either value alone prove a physical temperature change? Explain what assumption is being assessed.
\item Independent unbiased readings of a steady state have standard deviation 2 degrees. Find the standard deviation of averages of 1, 4, and 16 readings. If readings arrive one minute apart and the newest is current, how old is the oldest in each batch? What changes if every reading has the same +2-degree bias?
\item Classify the direction of feedback in a thermostat, microphone squeal, and an exposure index obeying $v_{n+1}=1.2v_n$. Starting with index 100, compute three updates. Explain why adaptive behavior is an additional feature rather than an opposite of corrective feedback.
\item A predictor uses $\widehat y=2w$, target 6, start $w_0=1$, and update $w_{n+1}=w_n+0.25(6-2w_n)$. Find the first four new weights and their predictions. Identify the weight target and prediction target. What does fitting this one example leave untested?
\item Keep that predictor but use step size 0.75 and current errors. Find two new weights and their predictions. Then return to step size 0.25 with a one-attempt-old error and history $w_{-1}=w_0=1$. Find the first three new weights. Explain one overshoot in each setting.
\item The data message is 1011. Append an even-parity bit. Show an example of a single-bit change detected by this check and a two-bit change that passes. Can the check establish that the original measurement was correct and current? For an event given probability $1/32$, find its surprisal.
\item Optional information extension: the observed tokens have model probabilities $1/2,1/4,1/8,1/4$. Compute total and average surprise and perplexity. Compare Models A and B assigning one observed token probabilities $1/2$ and $1/8$. Does the result rank all their abilities? Estimate the idealized bits for 100 tokens averaging 2 bits each.
\item Compare the central questions of Shannon, Wiener, and Mead using a linked historical source. Then identify a target, measurement, action, and possible unintended effect in a classroom or another institution. Explain a way to include feedback from people being measured.
\end{enumerate}
'''
answers=r'''
\subsection*{Chapter review: solutions}
\begin{enumerate}
\item The list is $7,11,15,19,23$, obtained by four updates. At $n=3$, $a_{n-1}=a_2=15$ is the preceding value. An index labels the term's place; it is not a power.
\item A float or level sensor measures water depth. A controller compares its report with a chosen depth and opens or closes a valve or adjusts a pump. The changed level produces the next reading. A fixed schedule does not use a level measurement to choose its next action. Other sensible designs are possible if the return path is explicit.
\item First row: current/report 84, error 16, correction 4, next 88 cm. Second: current/report 88, error 12, correction 3, next 91 cm. Each update removes one-quarter of the remaining gap and leaves three-quarters. The second correction is not another 4 cm.
\item States are 67, 68.5, 69.25, 69.625. The corrections are 3, 1.5, 0.75, 0.375. Adding 3 repeatedly ignores the changing reported error and eventually passes the target; it is not the stated half-gap controller.
\item States are 67, 70, 71.5, 71.5, 70.75, 70, 69.625. To produce $x_3$, current $x_2=70$ uses report $x_1=67$, error 3 and correction 1.5. To produce $x_4$, current $x_3=71.5$ uses report $x_2=70$, error and correction 0. The first correction acts on an earlier shortage that no longer describes the present.
\item The delayed order is $0.5(100-80)=10$ units. The current report would give $0.5(100-60)=20$. The model omits effects such as sales during delivery, pending orders, delivery time, whole-unit and minimum-order constraints, and finite storage. Specify which effect your explanation uses.
\item For $k=0.5$: $0,5,7.5,8.75$; half the gap remains on the same side. For 1.5: $0,15,7.5,11.25$; gaps switch side and halve. For 2: $0,20,0,20$; equal departures persist. For 2.5: $0,25,-12.5,43.75$; absolute gaps grow by factor 1.5. Starting exactly at 10 gives zero error and an unchanged state under all these ideal rules. The table's thresholds do not transfer unchanged to delayed rules.
\item The displayed peaks decrease in those eight steps, assuming the graph was read accurately. That alone does not prove all later peaks shrink or that the sequence converges. Overshoot is passing a reference; oscillation is repeated back-and-forth variation. A damped oscillation has a shrinking envelope of departures; convergence means later values approach one limit. A persistent equal-amplitude oscillation does not converge.
\newpage
\item $z=(72-68)/2=2$; $z=(65-68)/2=-1.5$. They describe distance from the assumed mean in standard-deviation units. Neither alone proves a change or a failure. A reading can be unusual under a steady-state noise model without being impossible. Further observations and sensor checks can help distinguish explanations.
\item Standard deviations of the averages are 2, 1, and 0.5 degrees. Oldest-reading ages are 0, 3, and 15 minutes. The shared +2-degree bias remains after averaging. Independence, unbiasedness, and a steady underlying state matter; correlated readings or a changing state require a different interpretation.
\item Thermostat: corrective, opposing a reported departure. Microphone squeal: amplifying, when speaker sound re-enters the microphone and reinforces the signal. The exposure index is amplifying, with values 100, 120, 144, 172.8. Decimals are appropriate for an index, not literal fractional people. An adaptive system changes its response rule or parameters using results; it can also use corrective feedback. Real amplification faces physical or social limits.
\item New weights are 2, 2.5, 2.75, 2.875, with predictions 4, 5, 5.5, 5.75. The weight target is 3, while the output target is 6. Success on this one fixed example does not test generalization, robustness, fairness, or performance on new data. Backpropagation and an optimization rule serve different roles in a larger network.
\newpage
\item With step size 0.75, first error 4 gives weight $1+0.75(4)=4$, prediction 8. The next error is $6-8=-2$, giving weight 2.5, prediction 5. The strong current response crosses the weight target 3. With delayed errors and step size 0.25, weights are 2, 3, 3.5. The third update uses the older weight 2 and its prediction 4, so a positive correction 0.5 is added when the current weight is already 3. The new prediction is 7, beyond output target 6.
\item Append 1 to make 10111, with four 1s. A single third-bit flip gives 10011 with three 1s, so the check fails. Flipping the first two bits gives 01111 with four 1s, so this two-bit change passes. Parity does not identify or repair the damage and does not check sensor truth or report age. Since $1/32=2^{-5}$, surprisal is 5 bits under that probability model.
\item Token scores are 1, 2, 3, 2 bits; total 8 and mean 2 bits per token. Perplexity is $2^2=4$. A has 1-bit surprise and B 3-bit surprise on the specified observed token, so A has lower loss there. This single comparison cannot rank their full-task performance or usefulness. The idealized coding scale is $100(2)=200$ bits, apart from overhead.
\item Shannon formalized message uncertainty, channels, noise, and communication limits. Wiener connected communication to action and regulation in feedback systems. Mead asked how a society studying cybernetics could apply those ideas to its own organization. In a classroom, quiz results may guide changed instruction, but focusing only on scores might encourage narrow preparation or miss deeper understanding. Student explanations, reflection, discussion, and feedback on assessment design can add evidence. A strong response names its specific goal, observation, action, return path, and historical source.
\end{enumerate}
\subsection*{Further exploration and historical sources}
The \href{https://bobovski66.github.io/MathInSociety/information_cybernetics_timeline.html}{illustrated history timeline} retains 63 milestones and offers guided routes on oscillation, reliable messages, and observers. It includes human computers, women in mathematics and information theory, Margaret Mead, and Janet Freed's organizational work at the Macy Conferences.

Primary and institutional sources include \href{https://www.nokia.com/bell-labs/publications-and-media/publications/a-mathematical-theory-of-communication/}{Shannon's 1948 paper, Bell Labs}; \href{https://mitpress.mit.edu/9780262537841/cybernetics-or-control-and-communication-in-the-animal-and-the-machine/}{Wiener's Cybernetics, MIT Press}; \href{https://www.asc-cybernetics.org/CofC/}{Mead's address, American Society for Cybernetics}; and \href{https://doi.org/10.1038/323533a0}{Rumelhart, Hinton, and Williams on backpropagation (1986)}.

Week 6 follows monetary balances through repeated updates. Keep the same habit: define the state and time unit, identify the report or base used, state the rule, and carry the result into the next update.
}
\end{document}
'''
tree=html.fromstring((ROOT/'readings/week5_reading.html').read_text());checks.clear();parts=[preamble,cover]
for id in ['s1','cybernetics','s2','s3','s4','s6','s7','three-loops','signals','history']:
 text=conv(tree.get_element_by_id(id)).replace('../assets/week8/','../assets/week5/').replace('height=3.2in','height=2.8in')
 if id=='s6':text=text.replace('height=2.8in','height=4.1in')
 parts.append(('\n\\clearpage\n' if id in ['s2','three-loops','history'] else '\n')+text)
parts.extend([extensions,review,'\n\\clearpage\n{\\setlength{\\parskip}{4pt}\\setlist{itemsep=5pt,topsep=3pt}\n\\section*{Solutions and Reasoning}\n'])
for n,(_,answer) in enumerate(checks,1):parts.append('\n\\paragraph{Short check '+str(n)+'.} '+answer)
parts.append('\n\\clearpage\n'+answers)
p=ROOT/'readings/Math107_Chapter_05.tex';t=p.with_suffix('.tmp')
with t.open('w') as f:f.write('\n'.join(line.rstrip() for line in ''.join(parts).replace('−',r'\ensuremath{-}').splitlines())+'\n');f.flush();os.fsync(f.fileno())
os.replace(t,p);os.sync();print('Built standalone chapter with',len(checks),'short checks and sixteen review problems with complete solutions.')

from chapter_editorial import polish_generated_chapters
polish_generated_chapters([ROOT / "readings/Math107_Chapter_05.tex"])
