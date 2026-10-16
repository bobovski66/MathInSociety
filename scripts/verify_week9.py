"""Check resource integrity, accessibility hooks, and preservation of course state contracts."""
from pathlib import Path
from lxml import html
import json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
FILES=['readings/week9_reading.html','demos/network_systems.html','labs/week9_lab.html','applications/week9_application.html','applications/week9_ai.html','discussions/week9_discussion.html']
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
if [w for w in bw if w['week']!=9]!=[w for w in nw if w['week']!=9]:fail('Other weeks were changed')
ba,na=const(base,'ASSESSMENTS'),const(now,'ASSESSMENTS')
if {k:v for k,v in ba.items() if k!='week9'}!={k:v for k,v in na.items() if k!='week9'}:fail('Other assessments were changed')
for old,new in zip(ba['week9']['questions'],na['week9']['questions']):
 for key in ['id','type','answer','tolerance','options']:
  if old.get(key)!=new.get(key):fail('Week 9 saved-mastery contract changed: '+old['id']+' / '+key)
if len(ba['week9']['questions'])!=len(na['week9']['questions']):fail('Week 9 assessment count changed')
# A single adjacency table in the reading must encode the stated edge list.
tree=html.fromstring((ROOT/'readings/week9_reading.html').read_text())
rows=tree.get_element_by_id('matrix').xpath('.//tbody/tr')
edges={'AB','AC','BC','BD','CD','DE','EF','EG','FG'}
for row,n in zip(rows,'ABCDEFG'):
 vals=[int(x.text_content()) for x in row.xpath('./td')[1:]]
 expected=[int(n!=v and ''.join(sorted(n+v)) in edges) for v in 'ABCDEFG']
 if vals!=expected:fail('Adjacency row '+n+' does not match the edge list')
if len(rows)!=7:fail('Adjacency table does not have seven rows')
for p in sorted((ROOT/'assets/week9').glob('*.svg')):
 from lxml import etree
 try:
  svg=etree.parse(str(p))
  if svg.getroot().get('viewBox') is None:fail(str(p)+': missing viewBox')
  pdf=p.with_suffix('.pdf')
  if not pdf.exists() or pdf.stat().st_size<1000:fail(str(pdf)+': missing or empty paired figure')
 except Exception as e:fail(str(p)+': '+str(e))
if errors:raise SystemExit('\n'.join(errors))
if '--dom-json' in sys.argv:print(json.dumps(snapshots))
else:print('PASS: six pages; links, images, labels, feedback, math delimiters, unchanged other weeks, and saved-mastery compatibility.')
