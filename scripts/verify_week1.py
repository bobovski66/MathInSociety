"""Check resource integrity, accessibility hooks, and preservation of course state contracts."""
from pathlib import Path
from lxml import html
import json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
FILES=['readings/week1_reading.html','demos/number_systems.html','labs/week1_lab.html','applications/week1_application.html','applications/week1_ai.html','discussions/week1_discussion.html','applications/ai_week1.html']
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
  elif not el.get('data-answer-kind'):
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
if [w for w in bw if w['week']!=1]!=[w for w in nw if w['week']!=1]:fail('Other weeks were changed')
ba,na=const(base,'ASSESSMENTS'),const(now,'ASSESSMENTS')
if {k:v for k,v in ba.items() if k!='week1'}!={k:v for k,v in na.items() if k!='week1'}:fail('Other assessments were changed')
for old,new in zip(ba['week1']['questions'],na['week1']['questions']):
 for key in ['id','type','answer','tolerance','options','prompt']:
  if old.get(key)!=new.get(key):fail('Week 1 saved-mastery contract changed: '+old['id']+' / '+key)
if len(ba['week1']['questions'])!=len(na['week1']['questions']):fail('Week 1 assessment count changed')
for p in sorted((ROOT/'assets/week1').glob('*.svg')):
 from lxml import etree
 try:
  svg=etree.parse(str(p))
  if svg.getroot().get('viewBox') is None:fail(str(p)+': missing viewBox')
  pdf=p.with_suffix('.pdf')
  if not pdf.exists() or pdf.stat().st_size<1000:fail(str(pdf)+': missing or empty paired figure')
 except Exception as e:fail(str(p)+': '+str(e))

expected={
'labs/week1_lab.html':dict(zip(['class0','class1','class2','class3','class4','class5','diverExpr','diverFinal','pred0','pred1','pred2','pred3','cp1','cp2','eq1','cp3','cp4','eq2'],['N','Z','Q','R','Z','N','0-15+8-5',-12,'greater','less','greater','less',252,252,'yes',125,120,'no'])),
'applications/week1_application.html':dict(zip(['q2a','q2b','q2c','q3a','q3b','q4a','q4b'],['B',120,6,'A','B',3440,4024])),
'applications/week1_ai.html':dict(zip(['q1','q2','q3','q4'],['slept on the mat',13,'Lₙ = 10 + n','Which token is being referred to.'])),
'applications/ai_week1.html':dict(zip(['q1','q2','q3a','q3b','q4','q5'],[7,'4,9,12,7,3,15,1',15,256,'sat on the mat',9]))
}
for i in range(1,6):expected['labs/week1_lab.html'].update({'a'+str(i):1000+200*i,'b'+str(i):1000*1.15**i})
for i in range(1,5):expected['applications/week1_application.html'].update({'a'+str(i):2000+120*i,'b'+str(i):2000*1.06**i})
schemas=json.loads((ROOT/'scripts/week1_response_contracts.json').read_text())
for f,values in expected.items():
 t=html.fromstring((ROOT/f).read_text());actual={e.get('id'):e.get('data-answer') for e in t.xpath('//*[@data-answer]')}
 if set(actual)!=set(values):fail(f+': original graded IDs changed')
 for id,v in values.items():
  if isinstance(v,str):
   if actual.get(id)!=v:fail(f+': changed original option token '+id)
  elif float(actual.get(id,'nan'))!=v:fail(f+': changed answer '+id)
 for old in schemas[f]:
  id=old['attrs'].get('id')
  if id in ['printStudentName','uInput']:continue
  els=t.xpath('//*[@id=$id]',id=id)
  if not els:fail(f+': lost response '+str(id));continue
  if old['tag']=='select' and {o[0] for o in old['options']}!={o.get('value') for o in els[0].xpath('./option')}:fail(f+': original options changed for '+id)
if sum(len(x) for x in expected.values())!=53:fail('Expected 53 original graded responses')
if len(list((ROOT/'assets/week1').glob('*.svg')))!=25:fail('Expected twenty-five diagram pairs')
if ba!=na:fail('An assessment was changed')
if next(x for x in bw if x['week']==1)['discussion']!=next(x for x in nw if x['week']==1)['discussion']:fail('The Week 1 discussion metadata was changed')
old_discussion=subprocess.check_output(['git','show','HEAD:discussions/week1_discussion.html'],cwd=ROOT)
if old_discussion!=(ROOT/'discussions/week1_discussion.html').read_bytes():fail('The newly approved discussion was changed')
for f in FILES:
 t=html.fromstring((ROOT/f).read_text())
 for a in t.xpath('//footer//a'):
  if 'Illustrated chapter' in a.text_content() and a.get('href')!='../readings/Math107_Chapter_01.pdf':fail(f+': wrong chapter link')
if errors:raise SystemExit('\n'.join(errors))
if '--dom-json' in sys.argv:print(json.dumps(snapshots))
else:print('PASS: seven resources; links, labels, feedback, mathematical notation, 53 original graded responses and option tokens, unchanged assessments and discussion, and twenty-five diagram pairs.')
