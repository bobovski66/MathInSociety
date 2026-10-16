"""Check resource integrity, accessibility hooks, and preservation of course state contracts."""
from pathlib import Path
from lxml import html
import json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
FILES=['readings/week8_reading.html','demos/convex_geometry.html','demos/linear_programming.html','labs/week8_lab.html','labs/week8_optimization_lab.html','applications/week8_application.html','applications/week8_ai.html','discussions/week8_discussion.html']
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
if [w for w in bw if w['week']!=8]!=[w for w in nw if w['week']!=8]:fail('Other weeks were changed')
ba,na=const(base,'ASSESSMENTS'),const(now,'ASSESSMENTS')
if {k:v for k,v in ba.items() if k!='week8'}!={k:v for k,v in na.items() if k!='week8'}:fail('Other assessments were changed')
for old,new in zip(ba['week8']['questions'],na['week8']['questions']):
 for key in ['id','type','answer','tolerance','options']:
  if old.get(key)!=new.get(key):fail('Week 8 saved-mastery contract changed: '+old['id']+' / '+key)
if len(ba['week8']['questions'])!=len(na['week8']['questions']):fail('Week 8 assessment count changed')
for p in sorted((ROOT/'assets/week8').glob('*.svg')):
 from lxml import etree
 try:
  svg=etree.parse(str(p))
  if svg.getroot().get('viewBox') is None:fail(str(p)+': missing viewBox')
  pdf=p.with_suffix('.pdf')
  if not pdf.exists() or pdf.stat().st_size<1000:fail(str(pdf)+': missing or empty paired figure')
 except Exception as e:fail(str(p)+': '+str(e))
# Saved-response schemas retain the old field IDs and correct option tokens.
expected={
 'labs/week8_lab.html': {'p1a':'yes','p1b':'no','p1c':'yes','p1d':'no','p1e':'quadrant','p2a':8,'p2b':4,'p2c':'yes','p2d':'yes','p2e':'no','p3a':20,'p3b':30,'p3c':'yes','p3d':'no','p3e':50,'p3f':61,'p4a':3,'p4b':4,'p4c':5,'p4d':7,'p4e':4,'p4f':'right',**dict(zip(['p5'+x for x in 'abcdefghijkl'],[0,18,18,10,0,6,16,20,18,2,20,'right']))},
 'labs/week8_optimization_lab.html': {'p1a':'right','p1b':'right','p1c':200,'p1d':150,'p1e':'max',**dict(zip(['p2'+x for x in 'abcdefgh'],[4,6,0,40,68,64,68,'right'])),**dict(zip(['p3'+x for x in 'abcdefg'],[2,6,24,36,50,24,'right'])),**dict(zip(['p4'+x for x in 'abcdefghijkl'],[80,98,72,120,107,48,32,44,36,'54','80','80'])),**dict(zip(['p5'+x for x in 'abcdefg'],[0,12,15,15,15,2,'right']))},
 'applications/week8_application.html': {**dict(zip(['a'+str(i) for i in range(1,6)],[20,10,8,6,'right'])),**dict(zip(['b'+str(i) for i in range(1,7)],[36,13,'yes',40,15,'no'])),**dict(zip(['c'+str(i) for i in range(1,7)],[0,420,540,500,540,'right']))},
 'applications/week8_ai.html': {'q1':'Yes','q2':3.5,'q3':2,'q4':'On the line segment joining A and B'}
}
for f,values in expected.items():
 t=html.fromstring((ROOT/f).read_text())
 actual={e.get('id'):e.get('data-answer') for e in t.xpath('//*[@data-answer]')}
 if set(actual)!=set(values):fail(f+': saved answer IDs changed')
 for id,v in values.items():
  if isinstance(v,str):
   if actual.get(id)!=v:fail(f+': saved option token changed for '+id)
  elif float(actual.get(id,'nan'))!=v:fail(f+': mathematical answer changed for '+id)
if errors:raise SystemExit('\n'.join(errors))
if '--dom-json' in sys.argv:print(json.dumps(snapshots))
else:print('PASS: eight pages; links, images, labels, feedback, math delimiters, unchanged other weeks, and saved-mastery compatibility.')
