"""Check resource integrity, accessibility hooks, and preservation of course state contracts."""
from pathlib import Path
from lxml import html
import json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
FILES=['readings/week6_reading.html','demos/interest_loans.html','labs/week6_lab.html','applications/week6_application.html','applications/week6_ai.html','discussions/week6_discussion.html']
errors=[];snapshots={}
def fail(message):errors.append(message)
def dump(e):
 return {'tag':e.tag,'attrs':dict(e.attrib),'text':e.text or '', 'tail':e.tail or '', 'children':[dump(c) for c in e if isinstance(c.tag,str)]}
for f in FILES:
 s=(ROOT/f).read_text();tree=html.fromstring(s);snapshots[f]=dump(tree)
 ids=[x.get('id') for x in tree.xpath('//*[@id]')]
 if len(ids)!=len(set(ids)):fail(f+': duplicate IDs')
 for el in tree.xpath('//a[@href] | //img[@src] | //link[@href] | //script[@src]'):
  ref=el.get('href') or el.get('src')
  if not ref or re.match(r'^(https?:|data:|mailto:)',ref):continue
  path,sep,anchor=ref.partition('#');target=(ROOT/f).parent/path
  if not path:target=ROOT/f
  if not target.exists():fail(f+': missing target '+ref)
  if sep and target.suffix=='.html' and target.exists() and anchor:
   if not html.fromstring(target.read_text()).xpath('//*[@id=$id]',id=anchor):fail(f+': missing anchor '+ref)
 for img in tree.xpath('//img'):
  if not img.get('alt'):fail(f+': missing image alt text')
 for el in tree.xpath('//input | //select | //textarea'):
  id=el.get('id')
  if not id or not tree.xpath('//label[@for=$id]',id=id):fail(f+': missing control label '+str(id))
 for el in tree.xpath('//*[@data-answer]'):
  id=el.get('id');feedback=el.get('aria-describedby')
  if not feedback or feedback not in ids:fail(f+': feedback is not associated with '+str(id))
  if el.tag=='select':
   choices=[x.get('value') for x in el.xpath('./option')]
   if el.get('data-answer') not in choices:fail(f+': correct choice missing for '+id)
  else:
   try:float(el.get('data-answer'));float(el.get('data-tolerance'))
   except:fail(f+': invalid numerical answer '+id)
 for field in ['aria-controls','aria-labelledby']:
  for el in tree.xpath('//*[@'+field+']'):
   for id in el.get(field).split():
    if id not in ids:fail(f+': missing ARIA target '+id)
 if 'MathJax' not in s:fail(f+': missing math rendering')
 if len(tree.xpath('//main'))!=1 or len(tree.xpath('//h1'))!=1:fail(f+': main/title structure')
 # Check delimited mathematics for accidental unpaired delimiters.
 for a,b in [('\\(','\\)'),('\\[','\\]')]:
  # Configuration script intentionally also names the delimiters.
  body=''.join(tree.xpath('//body//text()[not(parent::script)]'))
  if body.count(a)!=body.count(b):fail(f+': unbalanced math delimiters')
base=subprocess.check_output(['git','show','HEAD:index.html'],cwd=ROOT,text=True)
now=(ROOT/'index.html').read_text()
def const(s,name):return json.JSONDecoder().raw_decode(s[s.index('const '+name+' = ')+len('const '+name+' = '):])[0]
bw,nw=const(base,'WEEKS'),const(now,'WEEKS')
if [w for w in bw if w['week']!=6]!=[w for w in nw if w['week']!=6]:fail('Other weeks were changed')
ba,na=const(base,'ASSESSMENTS'),const(now,'ASSESSMENTS')
if {k:v for k,v in ba.items() if k!='week6'}!={k:v for k,v in na.items() if k!='week6'}:fail('Other assessments were changed')
for old,new in zip(ba['week6']['questions'],na['week6']['questions']):
 for key in ['id','type','answer','tolerance','options']:
  if old.get(key)!=new.get(key):fail('Week 6 saved-mastery contract changed: '+old['id']+' / '+key)
if len(ba['week6']['questions'])!=len(na['week6']['questions']):fail('Week 6 assessment count changed')
for p in sorted((ROOT/'assets/week6').glob('*.svg')):
 from lxml import etree
 try:
  svg=etree.parse(str(p))
  if svg.getroot().get('viewBox') is None:fail(str(p)+': missing viewBox')
  pdf=p.with_suffix('.pdf')
  if not pdf.exists() or pdf.stat().st_size<1000:fail(str(pdf)+': missing or empty paired figure')
 except Exception as e:fail(str(p)+': '+str(e))
# Saved-response schemas retain the old field IDs and correct option tokens.
expected={
 'labs/week6_lab.html':{**dict(zip(['p1'+x for x in 'abcdef'],[1680,1040,3,5,60,1560])),**dict(zip(['p2'+x for x in 'abcdefg'],[1215.51,629.86,2541.48,2400,2686.27,2729.10,'s-a-m'])),**dict(zip(['p3'+x for x in 'abcdefg'],[1790.85,1819.40,1822.03,120,.5,3.0416,'diminish'])),**dict(zip(['p4'+x for x in 'abcdef'],[18,9,6,36,8,24])),**{'p5'+k+str(n):v for n,i,b in [(1,22.5,2872.5),(2,21.54,2744.04),(3,20.58,2614.62),(4,19.61,2484.23)] for k,v in [('i',i),('b',b)]},'p5p':127.5,'p5s':'both'},
 'applications/week6_application.html':dict(zip(['a1','a2','a3','b1','b2','b3','c1','c2','c3','c4'],[120,40,7960,120,180,7820,59,4604.46,'samebase','balance'])),
 'applications/week6_ai.html':dict(zip(['q1','q2','q3','q4'],[200,156.25,6,'Repeated percentage growth']))
}
for f,values in expected.items():
 t=html.fromstring((ROOT/f).read_text())
 actual={e.get('id'):e.get('data-answer') for e in t.xpath('//*[@data-answer]')}
 if set(actual)!=set(values):fail(f+': saved answer IDs changed')
 for id,v in values.items():
  if isinstance(v,str):
   if actual.get(id)!=v:fail(f+': saved option token changed for '+id)
  elif float(actual.get(id,'nan'))!=v:fail(f+': mathematical answer changed for '+id)
if len(list((ROOT/'assets/week6').glob('*.svg')))!=12:fail('Expected twelve figure pairs')
if sum(len(v) for v in expected.values())!=50:fail('Expected 50 original graded fields')
if errors:raise SystemExit('\n'.join(errors))
if '--dom-json' in sys.argv:print(json.dumps(snapshots))
else:print('PASS: six pages; links, images, labels, feedback, math delimiters, unchanged other weeks, and saved-mastery compatibility.')
