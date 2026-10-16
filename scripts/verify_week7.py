"""Check resource integrity, accessibility hooks, and preservation of course state contracts."""
from pathlib import Path
from lxml import html
import json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
FILES=['readings/week7_reading.html','demos/business_models.html','labs/week7_lab.html','applications/week7_application.html','applications/week7_ai.html','discussions/week7_discussion.html']
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
if [w for w in bw if w['week']!=7]!=[w for w in nw if w['week']!=7]:fail('Other weeks were changed')
ba,na=const(base,'ASSESSMENTS'),const(now,'ASSESSMENTS')
if {k:v for k,v in ba.items() if k!='week7'}!={k:v for k,v in na.items() if k!='week7'}:fail('Other assessments were changed')
for old,new in zip(ba['week7']['questions'],na['week7']['questions']):
 for key in ['id','type','answer','tolerance','options']:
  if old.get(key)!=new.get(key):fail('Week 7 saved-mastery contract changed: '+old['id']+' / '+key)
if len(ba['week7']['questions'])!=len(na['week7']['questions']):fail('Week 7 assessment count changed')
for p in sorted((ROOT/'assets/week7').glob('*.svg')):
 from lxml import etree
 try:
  svg=etree.parse(str(p))
  if svg.getroot().get('viewBox') is None:fail(str(p)+': missing viewBox')
  pdf=p.with_suffix('.pdf')
  if not pdf.exists() or pdf.stat().st_size<1000:fail(str(pdf)+': missing or empty paired figure')
 except Exception as e:fail(str(p)+': '+str(e))
# Saved-response schemas retain the old field IDs and correct option tokens.
expected={
 'labs/week7_lab.html':{**dict(zip(['p1'+x for x in 'abcdef'],[300,7,15,580,600,'right'])),**dict(zip(['p2'+x for x in 'abcdefg'],[1.5,6,4.5,4.5,-48,48/4.5,11])),**dict(zip(['p3'+x for x in 'abcdefgh'],[-48,-12,-3,6,24,42,'loss','profit'])),**dict(zip(['p4'+x for x in 'abcdefgh'],[7,15,8,60,40,200,600,150])),**dict(zip(['p5'+x for x in 'abcd'],[10,-80,80,'revenue']))},
 'applications/week7_application.html':{**dict(zip(['a'+str(i) for i in range(1,6)],[240,3.5,9.5,6,-240])),**dict(zip(['b'+str(i) for i in range(1,4)],[40,380,'loss'])),**dict(zip(['c'+str(i) for i in range(1,7)],[-72,0,90,240,6,60])),**dict(zip(['d'+str(i) for i in range(1,5)],[5,48,160,'9.5']))},
 'applications/week7_ai.html':dict(zip(['q1','q2','q3','q4'],[6400,2400,3000,2]))
}
for f,values in expected.items():
 t=html.fromstring((ROOT/f).read_text())
 actual={e.get('id'):e.get('data-answer') for e in t.xpath('//*[@data-answer]')}
 if set(actual)!=set(values):fail(f+': saved answer IDs changed')
 for id,v in values.items():
  if isinstance(v,str):
   if actual.get(id)!=v:fail(f+': saved option token changed for '+id)
  elif float(actual.get(id,'nan'))!=v:fail(f+': mathematical answer changed for '+id)
if len(list((ROOT/'assets/week7').glob('*.svg')))!=12:fail('Expected twelve figure pairs')
if sum(len(v) for v in expected.values())!=55:fail('Expected 55 original graded fields')
if errors:raise SystemExit('\n'.join(errors))
if '--dom-json' in sys.argv:print(json.dumps(snapshots))
else:print('PASS: six pages; links, images, labels, feedback, math delimiters, unchanged other weeks, and saved-mastery compatibility.')
