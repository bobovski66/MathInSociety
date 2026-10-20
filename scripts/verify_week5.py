"""Check resource integrity, accessibility hooks, and preservation of course state contracts."""
from pathlib import Path
from lxml import html
import json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
FILES=['readings/week5_reading.html','demos/cybernetics.html','labs/week5_lab.html','applications/week5_application.html','applications/week5_ai.html','discussions/week5_discussion.html','applications/ai_week5.html','information_cybernetics_timeline.html']
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
 if f!='information_cybernetics_timeline.html' and 'MathJax' not in s:fail(f+': missing math rendering')
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
if [w for w in bw if w['week']!=5]!=[w for w in nw if w['week']!=5]:fail('Other weeks were changed')
ba,na=const(base,'ASSESSMENTS'),const(now,'ASSESSMENTS')
if {k:v for k,v in ba.items() if k!='week5'}!={k:v for k,v in na.items() if k!='week5'}:fail('Other assessments were changed')
for old,new in zip(ba['week5']['questions'],na['week5']['questions']):
 for key in ['id','type','answer','tolerance','options']:
  if old.get(key)!=new.get(key):fail('Week 5 saved-mastery contract changed: '+old['id']+' / '+key)
if len(ba['week5']['questions'])!=len(na['week5']['questions']):fail('Week 5 assessment count changed')
for p in sorted((ROOT/'assets/week5').glob('*.svg')):
 from lxml import etree
 try:
  svg=etree.parse(str(p))
  if svg.getroot().get('viewBox') is None:fail(str(p)+': missing viewBox')
  pdf=p.with_suffix('.pdf')
  if not pdf.exists() or pdf.stat().st_size<1000:fail(str(pdf)+': missing or empty paired figure')
 except Exception as e:fail(str(p)+': '+str(e))
expected={
 'labs/week5_lab.html':{'p1state':'64','p1ref':'70','p1measure':'sensor','p1action':'heater','p2e0':6,'p2c0':3,'p2x1':67,'p2e1':3,'p2c1':1.5,'p2x2':68.5,'p3old2':67,'p3corr2':1.5,'p3x3':71.5,'p3old3':70,'p3corr3':0,'p3x4':71.5,'p4x5':70.75,'p4x6':70,'p4x7':69.625,'p4which':'delayed','p5z':2,'p5proof':'no','p6thermo':'corrective','p6viral':'amplifying'},
 'applications/week5_application.html':dict(zip(['now1','now2','now3','late1','late2','late3','choice','correction'],[67,68.5,69.25,67,70,71.5,'immediate',0])),
 'applications/week5_ai.html':dict(zip(['q1','q2','q3','q4'],[4,2,2.5,'feedback'])),
 'applications/ai_week5.html':dict(zip(['q1a','q1b','q1c','q2a','q2b','q3a','q3b','q3c','q4','q5'],[1,3,5,8,2,1,3,'A',4,200]))
}
schemas=json.loads((ROOT/'scripts/week5_response_contracts.json').read_text())
for f,values in expected.items():
 t=html.fromstring((ROOT/f).read_text());actual={e.get('id'):e.get('data-answer') for e in t.xpath('//*[@data-answer]')}
 if set(actual)!=set(values):fail(f+': saved answer IDs changed')
 for id,v in values.items():
  if isinstance(v,str):
   if actual.get(id)!=v:fail(f+': saved option token changed for '+id)
  elif float(actual.get(id,'nan'))!=v:fail(f+': mathematical answer changed for '+id)
 for old in schemas[f]:
  id=old['attrs'].get('id')
  if id=='printStudentName':continue
  els=t.xpath('//*[@id=$id]',id=id)
  if not els:fail(f+': lost original response '+str(id));continue
  el=els[0]
  if old['tag']=='textarea' and el.tag!='textarea':fail(f+': changed written response '+id)
  if old['tag']=='select':
   before={x[0] for x in old['options']};after={x.get('value') for x in el.xpath('./option')}
   if before!=after:fail(f+': changed option tokens '+id)
if sum(len(v) for v in expected.values())!=46:fail('Expected 46 original graded fields')
if len(list((ROOT/'assets/week5').glob('*.svg')))!=14:fail('Expected fourteen paired vector diagrams')
history=html.fromstring((ROOT/'information_cybernetics_timeline.html').read_text())
# This older revision predates the timeline on some repository histories.
try:
 oldhistory=html.fromstring(subprocess.check_output(['git','show','3c57a4424a4f04a376786141f67cb2a3ae635a7c:information_cybernetics_timeline.html'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL))
except subprocess.CalledProcessError:
 oldhistory=None
def events(t):return {e.get('id'):(e.get('data-year'),e.get('data-cat'),e.text_content(),e.xpath('.//a/@href')) for e in t.xpath('//article[contains(@class,"milestone")]')}
if len(events(history))!=63:fail('The 63 historical milestones must be preserved')
if oldhistory is not None and events(history)!=events(oldhistory):fail('Historical milestones and source links changed')
for token in ['Margaret Mead','Janet Freed','F. Jessie MacWilliams','Vera Pless','Muriel Médard']:
 if token not in history.text_content():fail('Historical perspective missing: '+token)
for f in FILES:
 t=html.fromstring((ROOT/f).read_text())
 for link in t.xpath('//footer//a'):
  if 'Illustrated chapter' in link.text_content() and link.get('href')!='../readings/Math107_Chapter_05.pdf':fail(f+': wrong chapter footer')
if errors:raise SystemExit('\n'.join(errors))
if '--dom-json' in sys.argv:print(json.dumps(snapshots))
else:print('PASS: eight resources; links, figures, labels, feedback, mathematical delimiters, 46 original graded fields and option tokens, unchanged other weeks, and all 63 history entries.')
