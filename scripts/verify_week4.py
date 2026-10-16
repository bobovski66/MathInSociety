"""Check resource integrity, accessibility hooks, and preservation of course state contracts."""
from pathlib import Path
from lxml import html
import json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
FILES=['readings/week4_reading.html','demos/normal_z.html','labs/week4_lab.html','applications/week4_application.html','applications/week4_ai.html','discussions/week4_discussion.html','applications/ai_week4.html']
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
if [w for w in bw if w['week']!=4]!=[w for w in nw if w['week']!=4]:fail('Other weeks were changed')
ba,na=const(base,'ASSESSMENTS'),const(now,'ASSESSMENTS')
if {k:v for k,v in ba.items() if k!='week4'}!={k:v for k,v in na.items() if k!='week4'}:fail('Other assessments were changed')
for old,new in zip(ba['week4']['questions'],na['week4']['questions']):
 for key in ['id','type','answer','tolerance','options','prompt']:
  if old.get(key)!=new.get(key):fail('Week 4 saved-mastery contract changed: '+old['id']+' / '+key)
if len(ba['week4']['questions'])!=len(na['week4']['questions']):fail('Week 4 assessment count changed')
for p in sorted((ROOT/'assets/week4').glob('*.svg')):
 from lxml import etree
 try:
  svg=etree.parse(str(p))
  if svg.getroot().get('viewBox') is None:fail(str(p)+': missing viewBox')
  pdf=p.with_suffix('.pdf')
  if not pdf.exists() or pdf.stat().st_size<1000:fail(str(pdf)+': missing or empty paired figure')
 except Exception as e:fail(str(p)+': '+str(e))
expected={
'labs/week4_lab.html':dict(zip(['apple68','appleHigh','appleLo','appleHi','commute95','commuteZ','commuteLow','z115','z85','z100','z130','x2','xm1','x05','xm3','studentAZ','studentBZ','betterStudent','pollParam','pollStat','fishParam','fishStat','cerealParam','cerealStat','ci1lo','ci1hi','ci2lo','ci2hi','ci3lo','ci3hi','cerealLo','cerealHi','cerealInside','newN','finalZ','within2','contains60','tool1','tool2','tool3'],[68,2.5,150,210,95,3,16,1,-1,0,2,50,35,42.5,25,.2,1.4,'B','prop','58','mean','31.2','mean','368',78,86,3.2,4.2,41,53,235,251,'no',800,1.5,'yes','yes','z','emp','ci'])),
'applications/week4_application.html':dict(zip(['lo','hi','inside','decision','newE','newLo','newHi','newInside'],[235,251,'no','notconsistent',4,239,247,'no'])),
'applications/week4_ai.html':dict(zip(['q1','q2','q3','q4'],[.855,80.5,90.5,'The benchmark estimates performance on the kinds of tasks represented by its questions.'])),
'applications/ai_week4.html':dict(zip(['q1a','q1b','q2a','q2b','q3','q4','q5'],['sample','statistic',74,82,'mean',400,'careful']))
}
schemas=json.loads((ROOT/'scripts/week4_response_contracts.json').read_text())
for f,values in expected.items():
 t=html.fromstring((ROOT/f).read_text());actual={e.get('id'):e.get('data-answer') for e in t.xpath('//*[@data-answer]')}
 if set(actual)!=set(values):fail(f+': original graded IDs changed')
 for id,v in values.items():
  if isinstance(v,str):
   if actual.get(id)!=v:fail(f+': changed original option token '+id)
  elif float(actual.get(id,'nan'))!=v:fail(f+': changed answer '+id)
 for old in schemas[f]:
  id=old['attrs'].get('id')
  if id=='printStudentName':continue
  els=t.xpath('//*[@id=$id]',id=id)
  if not els:fail(f+': lost response '+str(id));continue
  if old['tag']=='select' and {o[0] for o in old['options']}!={o.get('value') for o in els[0].xpath('./option')}:fail(f+': original options changed for '+id)
if sum(len(x) for x in expected.values())!=59:fail('Expected 59 original graded responses')
if len(list((ROOT/'assets/week4').glob('*.svg')))!=14:fail('Expected fourteen diagram pairs')
for f in FILES:
 t=html.fromstring((ROOT/f).read_text())
 for a in t.xpath('//footer//a'):
  if 'Illustrated chapter' in a.text_content() and a.get('href')!='../readings/Math107_Chapter_04.pdf':fail(f+': wrong chapter link')
if errors:raise SystemExit('\n'.join(errors))
if '--dom-json' in sys.argv:print(json.dumps(snapshots))
else:print('PASS: seven resources; links, labels, feedback, mathematical notation, 59 original graded responses and option tokens, unchanged quiz prompts and other weeks, and fourteen diagram pairs.')
