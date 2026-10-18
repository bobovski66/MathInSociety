"""Check resource integrity, accessibility hooks, and preservation of course state contracts."""
from pathlib import Path
from lxml import html
import json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
FILES=['readings/week3_reading.html','demos/center_spread.html','labs/week3_lab.html','applications/week3_application.html','applications/week3_ai.html','discussions/week3_discussion.html','applications/ai_week3.html']
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
if [w for w in bw if w['week']!=3]!=[w for w in nw if w['week']!=3]:fail('Other weeks were changed')
ba,na=const(base,'ASSESSMENTS'),const(now,'ASSESSMENTS')
if {k:v for k,v in ba.items() if k!='week3'}!={k:v for k,v in na.items() if k!='week3'}:fail('Other assessments were changed')
for old,new in zip(ba['week3']['questions'],na['week3']['questions']):
 for key in ['id','type','answer','tolerance','options','prompt']:
  if old.get(key)!=new.get(key):fail('Week 3 saved-mastery contract changed: '+old['id']+' / '+key)
if len(ba['week3']['questions'])!=len(na['week3']['questions']):fail('Week 3 assessment count changed')
for p in sorted((ROOT/'assets/week3').glob('*.svg')):
 from lxml import etree
 try:
  svg=etree.parse(str(p))
  if svg.getroot().get('viewBox') is None:fail(str(p)+': missing viewBox')
  pdf=p.with_suffix('.pdf')
  if not pdf.exists() or pdf.stat().st_size<1000:fail(str(pdf)+': missing or empty paired figure')
 except Exception as e:fail(str(p)+': '+str(e))

expected={
'labs/week3_lab.html':dict(zip(['cMean','cMedian','cMode','cMean2','cMedian2','cMode2','meanEffect','modeEffect','totalSeven','missingScore','maxFromRange','meanA','rangeA','meanB','rangeB','driverConsistent','sdMean','d0','q0','d1','q1','d2','q2','d3','q3','sumSq','varPop','sdVal','sameMeanA','sameSdA','sameMeanB','sameSdB','largerPredict','moreConsistent','outMean','outMedian','outRange','bestCenter','outReason','cleanMean','cleanMedian','cleanRange'],[3,2.5,2,22/9,2,2,'down','same',560,82,55,13,4,13,10,'A',5,-2,4,0,0,0,0,2,4,8,8/3,(8/3)**.5,50,.5**.5,50,250**.5,'B','A',130/7,8,80,'median','outlier',8,8,6])),
'applications/week3_application.html':dict(zip(['meanA','rangeA','sdA','meanB','rangeB','sdB','choice','spec'],[250,2,.5**.5,250,10,4,'A','A'])),
'applications/week3_ai.html':dict(zip(['q1','q2','q3','q4'],[1,7,6.25,'It receives the largest weight, 0.60.'])),
'applications/ai_week3.html':dict(zip(['q1','q2','q3','q4','q5a','q5b','q5c'],[1,'ball',4.95,29,5,5,'A']))
}
schemas=json.loads((ROOT/'scripts/week3_response_contracts.json').read_text())
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
if sum(len(x) for x in expected.values())!=61:fail('Expected 61 original graded responses')
if len(list((ROOT/'assets/week3').glob('*.svg')))!=15:fail('Expected fifteen diagram pairs')
if ba!=na:fail('An assessment was changed')
if next(x for x in bw if x['week']==3)['discussion']!=next(x for x in nw if x['week']==3)['discussion']:fail('The Week 3 discussion metadata was changed')
old_discussion=subprocess.check_output(['git','show','HEAD:discussions/week3_discussion.html'],cwd=ROOT)
if old_discussion!=(ROOT/'discussions/week3_discussion.html').read_bytes():fail('The newly approved discussion was changed')
for f in FILES:
 t=html.fromstring((ROOT/f).read_text())
 for a in t.xpath('//footer//a'):
  if 'Illustrated chapter' in a.text_content() and a.get('href')!='../readings/Math107_Chapter_03.pdf':fail(f+': wrong chapter link')
if errors:raise SystemExit('\n'.join(errors))
if '--dom-json' in sys.argv:print(json.dumps(snapshots))
else:print('PASS: seven resources; links, labels, feedback, mathematical notation, 61 original graded responses and option tokens, unchanged assessments and discussion, and fifteen diagram pairs.')
