"""Add guided study and accessible experiment tables while preserving all 63 history entries."""
from pathlib import Path
import os,re

PHILOSOPHY = '<section class="philosophy container" id="philosophical-questions" aria-labelledby="philosophy-title">\n<h2 id="philosophy-title">Observation, goals, and control</h2>\n<p>A feedback model describes how information influences action. Applying that model also raises questions about what is observed, which goals are chosen, and how the people making decisions participate in the system.</p>\n<div class="philosophy-grid">\n<article><h3>Who chooses the goal?</h3><p>A controller can reduce a difference from a target, but the equation does not decide what the target should be. In a human institution, whose purposes does the goal serve, and how are competing goals considered?</p></article>\n<article><h3>What does a measurement represent?</h3><p>An observation records selected features of a situation. A temperature reading describes one physical quantity; an assessment score captures only part of learning. What is omitted when a complex condition is represented by a number?</p></article>\n<article><h3>How does the observer affect the system?</h3><p>A teacher changes instruction after a quiz. Students respond to the instruction and to what the quiz rewards. The next results therefore reflect an environment partly changed by the observer’s earlier decisions. Where should the boundary of the system be drawn?</p></article>\n<article><h3>How can the rules themselves be examined?</h3><p>A group can use feedback to reconsider its measurements, goals, and decision procedures. What evidence would justify a change? Who can question the measures, and how can the consequences of a revised rule be assessed?</p></article>\n</div>\n</section>'
PRESENTATION_REPLACEMENTS = [('A living history · Updated October 2026', 'Updated October 2026'),
 ('<div class="eyebrow">A visual history of interconnected ideas</div>', ''),
 ('<span>Four connected fields</span>', ''),
 ('<span>Built for first-year mathematics</span>', ''),
 ('From astronomical tables and handwritten algorithms to reliable messages, feedback controllers, and '
  'intelligent machines: explore how mathematicians, programmers, engineers, and other researchers shaped '
  'our understanding of information and its consequences.',
  'A selected history of probability, computation, information theory, and cybernetics, tracing the '
  'mathematical ideas, practical problems, and collaborative work behind communication and control.'),
 ('A history of mathematical ideas and the people who used them', 'Related fields'),
 ('Follow a question, not a list of names', 'Questions for historical study'),
 ('This page offers 63 milestones to explore. Start with one route below; you are not expected to memorize '
  'the entire chronology. First name the practical problem, then explain the mathematical idea it called '
  'for. Open the linked historical source to distinguish an inventor’s work from a later interpretation.',
  'The following groups of entries address three recurring problems. For each, identify the problem, explain '
  'the mathematical idea used to address it, and consult the linked sources for the historical context.'),
 ('<h3>3. Who observes and organizes?</h3><p>Read <a href="#y1946-new10">Mead at Macy (1946)</a>, <a '
  'href="#y1946-new11">Janet Freed (1946)</a>, and <a href="#y1968-new17">Mead’s later question (1968)</a>. '
  'Explain how a classroom or a research group can study its own communication and decisions.</p>',
  '<h3>3. How do institutions examine their own rules?</h3><p>Read about the <a href="#y1946-16">Macy '
  'Conferences (1946)</a>, <a href="#y1956-22">Ashby (1956)</a>, and <a href="#y1968-new17">Mead (1968)</a>. '
  'Compare regulation, adaptation, and a group’s examination of its own communication and decisions.</p>'),
 ('Keep the four questions distinct', 'Four mathematical questions'),
 ('After exploring, write a short explanation in the <a href="#history-notes">saved study notes</a>. Women’s '
  'contributions, human computing, and the organizational work of scientific communication remain part of '
  'the full chronology.',
  'In the <a href="#history-notes">study notes</a>, connect an entry to a mathematical example and explain '
  'the connection using evidence from its source.'),
 ('Two tiny experiments', 'Entropy and delayed feedback'),
 ('No calculus required. Move the controls and describe the pattern you notice.',
  'Vary the coin’s probability and the age of the thermostat report. Compare the resulting uncertainty and '
  'temperature sequences.'),
 ('How surprising is a coin toss?', 'Uncertainty in a coin toss'),
 ('Can delay make a thermostat oscillate?', 'Measurement delay and oscillation'),
 ('<h2 id="timeline-title">The timeline</h2>', '<h2 id="timeline-title">Chronology</h2>'),
 ('Questions worth carrying forward', 'Questions for discussion'),
 ('Keep an explanation you can bring to class', 'Study notes'),
 ('Choose one route or compare two milestones. Include a date and a source link. These drafts save in this '
  'browser; your instructor reviews their reasoning.',
  'Choose a group of entries or compare two milestones. Include dates and source links, and connect the '
  'historical problem to its mathematics. Notes save in this browser and can be printed.'),
 ('This selected chronology connects the development of probability, computing, information theory, and '
  'cybernetics. Each entry introduces one historical contribution and a question that can be explored using '
  'elementary mathematics. It is not an exhaustive account of these fields, and contemporary entries may '
  'describe continuing research.',
  'This chronology presents selected contributions to probability, computing, information theory, and '
  'cybernetics. Entries connect publications, projects, and research careers with the problems they '
  'addressed and provide links to historical or research sources.'),
 ('class="milestone spotlight-entry"', 'class="milestone"')]

def refine_presentation(s):
 s=re.sub(r'<section class="(?:mead-feature|philosophy container)"[^>]*>.*?</section>',lambda _:PHILOSOPHY,s,flags=re.S)
 s=re.sub(r'<(?:div|span) class="section-label">.*?</(?:div|span)>','',s)
 s='\n'.join(line for line in s.split('\n') if not line.startswith(('.mead-feature{','@media(max-width:780px){.mead-layout','@media print{.mead-layout')))
 for old,new in PRESENTATION_REPLACEMENTS:s=s.replace(old,new)
 return s

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'information_cybernetics_timeline.html';s=p.read_text()
if '<!-- week5-guided-route -->' not in s:
 s=s.replace('</head>','<link rel="stylesheet" href="assets/week5/history.css"><script defer src="assets/week5/week5.js"></script><script defer src="assets/week5/history.js"></script></head>')
 nav='<nav class="history-unit-nav" aria-label="Week 5 materials">'+''.join(f'<a href="{u}">{t}</a>' for t,u in [('Reading','readings/week5_reading.html'),('Explorer','demos/cybernetics.html'),('Laboratory','labs/week5_lab.html'),('Greenhouse','applications/week5_application.html'),('Learning','applications/week5_ai.html'),('Discussion','discussions/week5_discussion.html'),('History','information_cybernetics_timeline.html')])+'</nav>'
 s=s.replace('<main id="main">',nav+'<main id="main" data-answer-store="math107_week5_history_v1">')
 route='''<!-- week5-guided-route -->
<section class="study-route container" id="study-route" aria-labelledby="study-route-title"><div class="section-label">Week 5 / A guided way to read</div><h2 id="study-route-title">Follow a question, not a list of names</h2><p>This page offers 63 milestones to explore. Start with one route below; you are not expected to memorize the entire chronology. First name the practical problem, then explain the mathematical idea it called for. Open the linked historical source to distinguish an inventor’s work from a later interpretation.</p><div class="route-grid"><article><h3>1. Why can correction oscillate?</h3><p>Read <a href="#y1868-5">Maxwell (1868)</a>, <a href="#y1948-18">Wiener (1948)</a>, and <a href="#y1952-21">Ashby (1952)</a>. Use a greenhouse update to connect regulation, report timing, and adaptation. Which question can our simple model answer?</p></article><article><h3>2. How do messages survive noise?</h3><p>Read <a href="#y1948-17">Shannon (1948)</a>, <a href="#y1963-new15">MacWilliams (1963)</a>, and <a href="#y1963-new16">Pless (1963)</a>. Compare uncertainty about a message with a check that detects a damaged message. What does a parity check leave unresolved?</p></article><article><h3>3. Who observes and organizes?</h3><p>Read <a href="#y1946-new10">Mead at Macy (1946)</a>, <a href="#y1946-new11">Janet Freed (1946)</a>, and <a href="#y1968-new17">Mead’s later question (1968)</a>. Explain how a classroom or a research group can study its own communication and decisions.</p></article></div><div class="route-terms"><h3>Keep the four questions distinct</h3><p><b>Probability:</b> how likely are the possible outcomes? <b>Computation:</b> what repeatable steps perform the task? <b>Information:</b> what can a message convey through a noisy channel? <b>Control:</b> how does a received report change an action? A person’s work can connect several of these, even though the filters give each milestone one main category.</p></div><p>After exploring, write a short explanation in the <a href="#history-notes">saved study notes</a>. Women’s contributions, human computing, and the organizational work of scientific communication remain part of the full chronology.</p></section>
'''
 s=s.replace('<section class="lab"',route+'<section class="lab"',1)
 s=s.replace('<svg id="feedbackGraph" class="mini-chart" viewBox="0 0 470 126" role="img" aria-label="Graph of greenhouse temperatures over 10 steps"></svg>','<div id="feedbackGraph" class="history-chart"></div><div id="historyFeedbackTable" class="history-table" aria-label="Greenhouse temperatures by step"></div>')
 s=s.replace('A binary result has its greatest uncertainty when both outcomes are equally likely. Slide the chance of heads to see the information entropy change.','Entropy is average surprise across both possible outcomes, not the surprise of a particular toss. A fair coin has the greatest uncertainty: either outcome is equally likely. A coin certain to land heads has zero uncertainty. Slide the probability and compare the numbers below.')
 s=s.replace('<div class="keyline"><b>Formula:</b> H = −p log₂(p) − (1−p) log₂(1−p)</div>','<div class="keyline"><b>Formula:</b> H = −p log₂(p) − (1−p) log₂(1−p). At p = 0 or 1, use the limiting value 0.</div><div id="historyEntropyTable" class="history-table"></div><p class="experiment-note">Try 0%, 25%, 50%, 75%, and 100%. Explain why the two extreme cases are certain and why 25% and 75% give the same average uncertainty.</p>')
 s=s.replace("Both controllers start at 64°F and aim for 70°F. Choose whether the correction uses the temperature now or the previous step's reading.","Both controllers start at 64°F, aim for 70°F, and correct half of the reported difference each hourly step. Choose the report age. The delayed history is x₋₁ = x₀ = 64°F. Reports are exact about their own times. Compare steps 2, 3, and 4 in the table.")
 s=s.replace('<span class="result-desc" id="feedbackExplain">','<span class="result-desc" id="feedbackExplain" aria-live="polite">')
 s=s.replace('id="resultCount"','id="resultCount" aria-live="polite"')
 # The existing search is already inside a label; give it an explicit association too.
 pos=s.index('id="searchEvents"');start=s.rfind('<label',0,pos);end=s.index('>',start)
 s=s[:end]+(' for="searchEvents"' if 'for=' not in s[start:end] else '')+s[end:]
 notes='''<section class="study-route container" id="history-notes" aria-labelledby="notes-title"><div class="section-label">Connect history to mathematics</div><h2 id="notes-title">Keep an explanation you can bring to class</h2><p>Choose one route or compare two milestones. Include a date and a source link. These drafts save in this browser; your instructor reviews their reasoning.</p><div class="question"><label for="historyProblem">What practical or theoretical problem was being studied, and what mathematical idea helped?</label><textarea id="historyProblem" rows="5" data-save></textarea></div><div class="question"><label for="historyConnection">Connect a milestone to a specific calculation, graph, or feedback loop from Week 5.</label><textarea id="historyConnection" rows="5" data-save></textarea></div><div class="question"><label for="historyPerspective">Whose contribution or perspective changes how you understand the story? Explain using evidence from an entry or source.</label><textarea id="historyPerspective" rows="5" data-save></textarea></div><div class="history-student-bar"><div><label for="studentName">Your name for the printed copy</label><input id="studentName" autocomplete="name"></div><button type="button" data-print-work>Print / save completed notes</button><p id="saveStatus" class="save-status" aria-live="polite"></p><p id="printStatus" role="status"></p></div><p class="print-name" id="printName"></p></section>'''
 s=s.replace('<section class="references"',notes+'<section class="references"',1)
 a=s.rfind('<script>');b=s.index('</script>',a)+len('</script>');s=s[:a]+s[b:]
s=refine_presentation(s)
t=p.with_suffix('.tmp')
with t.open('w') as f:f.write(s);f.flush();os.fsync(f.fileno())
os.replace(t,p);os.sync()
print('Updated history presentation, questions, and study tools; preserved all 63 milestones.')
