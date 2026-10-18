"""Build the illustrated Week 3 chapter, retaining its practice sets and adding solutions."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import math
import os
import re
import sys
sys.dont_write_bytecode = True
from lxml import html
from build_week8_chapters import conv, checks, translations

ROOT = Path(__file__).resolve().parents[1]
translations.update({'σ': r'$\sigma$', 'μ': r'$\mu$', '±': r'$\pm$'})


def write(path, text):
    p = ROOT / path
    temporary = p.with_suffix(p.suffix + '.tmp')
    with temporary.open('w') as stream:
        stream.write('\n'.join(line.rstrip() for line in text.splitlines()).rstrip() + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, p)


def rational(x):
    q = F(x)
    return str(q.numerator) if q.denominator == 1 else r'\frac{' + str(q.numerator) + '}{' + str(q.denominator) + '}'


def exact(x):
    q = F(x)
    return '$' + rational(q) + (r'\approx ' + f'{float(q):.4f}'.rstrip('0').rstrip('.') if q.denominator != 1 else '') + '$'


def stats(values):
    xs = [F(str(x)) for x in values]
    ordered = sorted(xs)
    n = len(xs)
    mu = sum(xs) / n
    med = ordered[n // 2] if n % 2 else (ordered[n // 2 - 1] + ordered[n // 2]) / 2
    counts = Counter(xs)
    high = max(counts.values())
    modes = sorted(x for x, count in counts.items() if count == high) if high > 1 else []
    deviations = [x - mu for x in xs]
    squares = [x * x for x in deviations]
    ss = sum(squares)
    return dict(xs=xs, n=n, mean=mu, median=med, modes=modes, range=ordered[-1]-ordered[0], deviations=deviations, squares=squares, ss=ss, variance=ss/(n-1), sd=math.sqrt(ss/(n-1)))


def summary(values, spread=True):
    s = stats(values)
    modes = ', '.join(exact(x) for x in s['modes']) or 'no repeated value, so no mode under the course convention'
    text = 'Mean ' + exact(s['mean']) + '; median ' + exact(s['median']) + '; mode(s): ' + modes + '.'
    if spread:
        text += ' Range ' + exact(s['range']) + '; sample variance ' + exact(s['variance']) + '; sample SD $s=' + f'{s["sd"]:.4f}' + '$.'
    return text


def deviation_table(values, label=''):
    s = stats(values)
    rows = ''.join('$' + rational(x) + '$ & $' + rational(d) + '$ & $' + rational(q) + r'$\\' + '\n' for x, d, q in zip(s['xs'], s['deviations'], s['squares']))
    return (r'\par\medskip\noindent\begin{minipage}{\linewidth}' + label + r'\par{\small\renewcommand{\arraystretch}{1.2}\begin{tabularx}{\linewidth}{@{}YYY@{}}\toprule' + '\n'
            + r'Value & Deviation & Squared deviation\\\midrule' + '\n' + rows
            + r'\bottomrule\end{tabularx}}\par\medskip' + '\n'
            + 'Mean ' + exact(s['mean']) + '. Squared-deviation sum ' + exact(s['ss']) + '. Divide by ' + str(s['n'] - 1) + ' for sample variance ' + exact(s['variance'])
            + r'. Then $s=\sqrt{' + rational(s['variance']) + r'}\approx ' + f'{s["sd"]:.4f}' + '$ in the original units.' + r'\par\end{minipage}\par\medskip' + '\n')


def answer_group(letter, title, answers):
    return '\n\\Needspace{8\\baselineskip}\n\\subsection*{' + title + '}\n\\begin{enumerate}[label=' + letter + r'\arabic*.,leftmargin=2.5em,itemsep=10pt]' + '\n' + ''.join('\\item ' + x + '\n' for x in answers) + '\\end{enumerate}\n'


preamble = (ROOT / 'scripts/week8_chapter_preamble.tex').read_text()
preamble = preamble.replace('[11pt,letterpaper]', '[12pt,letterpaper]').replace('margin=.8in', 'margin=1in')
preamble = preamble.replace('8.\\arabic', '3.\\arabic').replace('WEEK 8 / PART @PART@', 'WEEK 3').replace('@TOPIC@', 'Center and Spread').replace('Week 8, Part @PART@:', 'Week 3:')
preamble += '\n\\widowpenalty=10000\n\\clubpenalty=10000\n'
cover = r'''
\begin{document}
{\small\sffamily\color{olive}WEEK 3 / BASIC STATISTICS\par}
\vspace{12pt}
{\fontsize{30}{34}\selectfont\bfseries\color{olive}Describing center\\and variation\par}
\vspace{10pt}
{\large Use numerical summaries and graphs to explain what a set of observations tells us.\par}
\begin{center}\includegraphics[width=\linewidth,height=3in,keepaspectratio]{../assets/week3/mean-sharing.pdf}\end{center}
\begin{tcolorbox}[title={A typical value is only part of the story}]
Two routes can average the same travel time while one varies much more from day to day. A useful description asks both where the observations sit and how much they differ. The setting, units, and graph help us interpret the calculations.
\end{tcolorbox}
Week 2 organized observations with frequency tables, relative frequencies, and graphs. This chapter develops the mean, median, mode, range, and sample standard deviation. Weighted averages connect those methods to a numerical model of attention.

Try the short checks before reading their explanations. The practice sets retain the chapter's numerical questions, with corrected interpretation prompts. Complete solutions follow the exercises. The examples are hypothetical.

\medskip
\href{https://bobovski66.github.io/MathInSociety/readings/week3_reading.html}{Online reading}\quad\textperiodcentered\quad\href{https://bobovski66.github.io/MathInSociety/demos/center_spread.html}{Center and spread explorer}\quad\textperiodcentered\quad\href{https://bobovski66.github.io/MathInSociety/labs/week3_lab.html}{Laboratory}
\clearpage
\input{chapter3/part1.tex}
\input{chapter3/part2.tex}
\input{chapter3/part3.tex}
\end{document}
'''

tree = html.fromstring((ROOT / 'readings/week3_reading.html').read_text())
for e in tree.iter():
    if not isinstance(e.tag, str):
        continue
    for field in ['text', 'tail']:
        value = getattr(e, field)
        if value:
            value = value.replace('x̄', r'\(\bar x\)')
            value = re.sub(r'√(\d+|[a-z])', lambda m: r'\(\sqrt{' + m[1] + r'}\)', value)
            setattr(e, field, value)
checks.clear()
ids = ['data', 'mean', 'median', 'mode', 'range', 'deviations', 'sample-sd', 'comparison', 'weighted', 'changes', 'meaning']
converted = []
for id in ids:
    text = conv(tree.get_element_by_id(id)).replace('../assets/week8/', '../assets/week3/').replace('height=3.2in', 'height=2.65in')
    for name, height in [('median-positions', '2.7'), ('same-mean-spread', '3.0'), ('outlier-center', '3.1'), ('shift-and-scale', '3.6'), ('signed-deviations', '2.9')]:
        text = re.sub(r'height=2\.65in,keepaspectratio\]\{(\.\./assets/week3/' + re.escape(name) + r'\.pdf)\}', lambda m: 'height=' + height + 'in,keepaspectratio]{' + m[1] + '}', text)
    converted.append('\n' + text)

solutions = ['\n\\clearpage\n\\section*{Solutions and Reasoning}\n']
for n, (_, answer) in enumerate(checks, 1):
    solutions.append('\n\\paragraph{Short check ' + str(n) + '.} ' + answer)
solutions.append('\n\\clearpage\n')
solutions.append(answer_group('A', 'Practice A: Center', [
    '(a) ' + summary([4,7,7,9,11,13,7,6], False) + '\n\n(b) ' + summary([22,18,30,22,25,18,29,22,31], False) + '\n\n(c) ' + summary([.5,1.2,.8,1.5,.9,1.1], False),
    r'The ten-day total is 30: mean 3, median 2.5, mode 2. Removing 8 leaves total 22 across nine days: mean $22/9\approx2.4444$, median 2, mode 2. Both the total and count change. The mode stays fixed here; a median need not remain fixed when an observation is removed.',
    'The mean is much higher than the median, suggesting some high prices are pulling the total-per-home upward. The median describes a middle observed home price; the mean describes the total divided by the count. These two summaries do not reveal the complete shape or prove how many homes are affordable to a particular buyer.',
    '$7(80)=560$ points in all. The six known scores total 478. The missing score is $560-478=82$.',
]))
solutions.append(answer_group('B', 'Practice B: Range', [
    '(a) $31-9=22$. (b) $8-(-7)=15$. (c) $1.8-0.3=1.5$. The result has the original measurement units.',
    'Driver A totals 65: mean 13 and range $15-11=4$. Driver B also totals 65: mean 13 and range $18-8=10$. A is more consistent in these five recorded days under the range comparison. Equal means do not describe equal daily variation.',
    'Maximum minus 15 equals 40, so the maximum is 55.',
]))
solutions.append(answer_group('C', 'Practice C: Sample standard deviation', [
    deviation_table([3,5,5,7], '(a)') + deviation_table([10,20,30,40], '(b)') + deviation_table([6,6,9,9], '(c)'),
    r'(a) B has the greater sample SD: its values are farther from the common mean 50. The calculated SDs are $\sqrt{0.5}\approx0.7071$ and $\sqrt{250}\approx15.8114$. (b) D has greater spread. All C values equal 2, giving $s_C=0$; D varies, with $s_D=\sqrt{2.5}\approx1.5811$. The zero-SD statement requires at least two observations.',
    r'The squared deviations total 10. With five observations, sample variance is $10/4=2.5$ and $s=\sqrt{2.5}\approx1.5811$. The given squared deviations suffice because they already supply the departures from the mean.',
    r'Both means are 250 mL. A has squared-deviation sum 2, giving variance $2/4=0.5$ and $s_A\approx0.7071$ mL. B has squared-deviation sum 64, giving variance 16 and $s_B=4$ mL. A is more consistent in the observed samples. This does not guarantee every future fill.',
]))
solutions.append(answer_group('D', 'Practice D: Interpreting summaries', [
    '(a) ' + summary([12,14,14,15,16,17,14]) + '\n\n(b) ' + summary([5,6,7,8,9,10,85]) + '\n\nThe second list has six values from 5 through 10 and one at 85. Its median 8 better describes that main cluster, while its mean still correctly accounts for the full total. The range and SD are both sensitive to the distant value. Reporting a median does not make the range resistant.',
    r'Rainfall totals 3.8 inches over 14 days, giving mean $3.8/14\approx0.2714$ inch per day. Ten values are zero, so median and mode are zero. For a typical observed day, zero conveys that most days were dry. The mean is still useful for the total-per-day rainfall over the full period.',
    'Draw both histograms centered at 20, with the first concentrated more tightly and the second extending more widely. A larger sample SD indicates greater spread around the common mean. The two summary numbers do not determine unique histograms or establish a normal shape.',
]))
solutions.append(answer_group('E', 'Practice E: Reading graphs', [
    r'(a) The 66-to-below-70-inch interval has the largest count, 12. That is $12/40=30\%$, not a majority. (b) The bars are roughly mound-shaped and approximately symmetric, with small differences between the two sides. (c) That shape suggests the mean and median will be reasonably close. Exact raw-data means and medians cannot generally be recovered from these bin counts alone.',
    'One valid sketch uses the two data sets shown in the chapter figure: both center at 50, with one much narrower than the other. The narrow sample has values close to 50; the wide sample places observations farther from 50. A graph should label a shared measurement scale so the widths can be compared.',
    'The distances are $(36-30)/2=3$ sample SDs and $(36-30)/8=0.75$ sample SD. The observation is farther from the mean in SD units in the first data set. Without further information about shape, these distances do not supply exact tail percentages.',
]))
solutions.append(answer_group('F', 'Practice F: Weighted averages', [
    '$0.25(70)+0.75(90)=17.5+67.5=85$. The ordinary mean is 80. The weighted result is between 70 and 90 and closer to the more heavily weighted score 90.',
    'The weights total 1. Contributions are 0.2, 1, 4.8, and 1; their sum is 7. The ordinary mean is 6.25. Weight 0.60 makes the value 8 strongly influential in this particular combination; it does not certify that its information is correct.',
    '$0.10(2)+0.05(3)+0.70(5)+0.05(6)+0.10(8)=0.2+0.15+3.5+0.3+0.8=4.95$. This is a numerical center of weighted positions, not a token at a fractional position. The complete-sentence table includes position 8 after the word at position 7. A next-token generator must mask unavailable future text; otherwise it would use information that it does not have when generating.',
]))
solutions.append(answer_group('G', 'Practice G: Changing every value', [
    '(a) The mean becomes 25 and SD stays 3: every observation and its mean move by the same 5, preserving deviations. (b) The original mean doubles to 40 and SD doubles to 6: deviations double, squared deviations quadruple, and the final square root doubles the spread measure.',
]))
solutions.append('\n\\Needspace{8\\baselineskip}\n')
solutions.append(answer_group('R', 'Chapter 3 review', [
    'Mean 6 hours, median 6 hours, mode 6 hours, and range 5 hours.\n' + deviation_table([4,7,5,8,6,5,9,4,6,6]) + 'The sample centers at 6 weekly homework-hours, with observed values from 4 to 9 hours and sample SD about 1.63 hours.',
    r'The total is 26 days, giving mean $26/8=3.25$ and median 1. The median better describes the middle employee in these observations. Removing 18 leaves total 8 across seven observations: mean $8/7\approx1.1429$ and median 1. The unusually large value substantially changes the mean, while the median stays fixed in this particular comparison.',
    r'B should have greater sample SD. A has squared-deviation sum 10 and $s_A=\sqrt{10/4}\approx1.5811$. B has sum 1,000 and $s_B=\sqrt{1000/4}\approx15.8114$. Both means are 80, but B varies much more.',
    'Six values with mean 14 total 84. The five known values total 70. The missing value is 14.',
    'A left-skewed histogram has a longer tail toward the smaller values. Such low values tend to pull the mean toward that tail, so one generally expects the mean to be below the median in this setting. This is an interpretation of the displayed shape, not a formula for exact numerical values.',
    r'City A has mean 69 degrees F, range 4 degrees F, and $s_A=\sqrt{2.5}\approx1.5811$ degrees F. City B has mean 71 degrees F, range 30 degrees F, and $s_B=\sqrt{151.5}\approx12.3085$ degrees F. A has the more consistent observed temperatures according to both spread measures.',
    r'The mean diameter is 10.00 mm. Squared deviations total 0.001 square mm. Sample variance is $0.001/5=0.0002$ square mm and $s=\sqrt{0.0002}\approx0.014142$ mm. The permitted interval is [9.97,10.03] mm. Every sampled bearing meets it; the sample alone does not establish that every future bearing will meet it.',
]))
solutions.append(r'''
\subsection*{References and activities}
The NIST Engineering Statistics Handbook discusses \href{https://www.itl.nist.gov/div898/handbook/eda/section3/eda351.htm}{measures of location} and \href{https://www.itl.nist.gov/div898/handbook/eda/section3/eda356.htm}{measures of scale}. The weighted-average application uses the value-combination structure described in Vaswani and colleagues' \href{https://arxiv.org/html/1706.03762v7}{Attention Is All You Need}.

Use the \href{https://bobovski66.github.io/MathInSociety/demos/center_spread.html}{explorer} to compare a common axis with fitted axes and to inspect every deviation. The \href{https://bobovski66.github.io/MathInSociety/applications/week3_application.html}{filling-machine application} separates a target, observed consistency, and an acceptance rule. The \href{https://bobovski66.github.io/MathInSociety/discussions/week3_discussion.html}{discussion} asks what an average misses in an example from your own experience. Week 4 uses these distinctions when describing normal models and uncertainty in population estimates.
''')
practice = (ROOT / 'scripts/week3_chapter_practice.tex').read_text()
practice = practice.replace('\\clearpage', '\\Needspace{8\\baselineskip}')
write('readings/chapter3/part1.tex', ''.join(converted[:5]))
write('readings/chapter3/part2.tex', ''.join(converted[5:8]))
write('readings/chapter3/part3.tex', ''.join(converted[8:]) + '\n' + practice + ''.join(solutions))
write('readings/Math107_Chapter_03.tex', preamble + cover)
os.sync()
print('Built Chapter 3:', len(checks), 'short checks; all 24 original practice/review groups plus four new groups, with complete solutions.')
