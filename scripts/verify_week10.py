"""Validate the rebuilt Week 10 pages and their student response contracts."""
from pathlib import Path
import json, re
from lxml import html

ROOT=Path(__file__).resolve().parents[1]
FILES=[
  "readings/week10_reading.html",
  "demos/fractal_recursion.html",
  "labs/week10_lab.html",
  "applications/week10_application.html",
  "applications/week10_ai.html",
  "discussions/week10_discussion.html"
]
errors=[]
def check(condition,message):
    if not condition:errors.append(message)
def parse(path):
    return html.fromstring((ROOT/path).read_text(encoding="utf-8"))

for fname in FILES:
    source=(ROOT/fname).read_text(encoding="utf-8")
    tree=parse(fname)
    ids=[x.get("id") for x in tree.xpath("//*[@id]")]
    check(len(ids)==len(set(ids)),fname+": duplicate IDs")
    check(len(tree.xpath("//main"))==1,fname+": one <main> required")
    check(len(tree.xpath("//h1"))==1,fname+": one <h1> required")
    check("Complexity, Chaos, and Fractals" in source or "Collatz" in source,
          fname+": unrelated module content")
    for el in tree.xpath("//a[@href]|//link[@href]|//script[@src]|//img[@src]"):
        ref=el.get("href") or el.get("src")
        if not ref or re.match(r"^(https?:|data:|mailto:)",ref):continue
        file,sep,anchor=ref.partition("#")
        dest=(ROOT/fname).parent/file if file else ROOT/fname
        check(dest.exists(),fname+": unresolved local link "+ref)
        if dest.exists() and sep and anchor and dest.suffix==".html":
            check(bool(html.fromstring(dest.read_text(encoding="utf-8")).xpath('//*[@id=$target]',target=anchor)),fname+": missing target "+ref)
    for im in tree.xpath("//img"):
        check(bool(im.get("alt")),fname+": image missing alt text")
    for el in tree.xpath("//input|//select|//textarea"):
        ident=el.get("id")
        check(bool(ident) and bool(tree.xpath("//label[@for=$target]",target=ident)),fname+": input not associated with label "+str(ident))
    for field in tree.xpath("//*[@data-answer]"):
        ident=field.get("id")
        refs=(field.get("aria-describedby") or "").split()
        check(refs and all(t in ids for t in refs),fname+": missing feedback association "+str(ident))
        if field.tag=="select":
            choices=[option.get("value") for option in field.xpath("./option")]
            check(field.get("data-answer") in choices,fname+": invalid expected choice "+ident)
        else:
            try:
                float(field.get("data-answer"));float(field.get("data-tolerance") or ".001")
            except (ValueError,TypeError):
                errors.append(fname+": invalid numerical answer "+str(ident))
    for el in tree.xpath("//*[@aria-controls or @aria-labelledby]"):
        for key in ("aria-controls","aria-labelledby"):
            for target in (el.get(key) or "").split():
                check(target in ids,fname+": missing ARIA target "+target)
    text=" ".join(tree.xpath("//body//text()[not(ancestor::script) and not(ancestor::style)]"))
    for left,right in [(r"\(",r"\)"),(r"\[",r"\]")]:
        check(text.count(left)==text.count(right),fname+": unbalanced mathematics")
    for stale in ("Restoring furniture with limited time","Feasible Region Analysis","How far can a prediction go?"):
        check(stale not in text,fname+": old Week 10 material remains: "+stale)

index=(ROOT/"index.html").read_text(encoding="utf-8")
def parse_const(label):
    start=index.index("const "+label+" = ")+len("const "+label+" = ")
    return json.JSONDecoder().raw_decode(index[start:])[0]
weeks=parse_const("WEEKS");assess=parse_const("ASSESSMENTS")
check(len(weeks)==10,"Course should have 10 modules")
current=next(w for w in weeks if w["week"]==10)
check(current["title"]=="Complexity, Chaos, and Fractals","Week 10 title")
check(current["quiz"]=="week10","Week 10 quiz link")
check(current["reading"][0]["url"]==FILES[0],"Week 10 main reading link")
check(current["demos"][0]["url"]==FILES[1],"Week 10 explorer link")
check(current["weekly_lab"]["url"]==FILES[2],"Week 10 lab link")
check(len(current["application"])==2,"Two Week 10 applications")
quiz=assess["week10"]["questions"]
check(len(quiz)==12,"Week 10 quiz requires 12 questions")
check(len({q["id"] for q in quiz})==len(quiz),"Quiz question IDs must be unique")
check(all(q["id"].startswith("w10ccf") for q in quiz),"New mastery IDs for changed quiz content")
check(len(assess["final"]["questions"])==18,"Final exam keeps 18 items")
for q in quiz:
    if q["type"]=="mc":
        check(q["answer"] in q["options"],"Question has an answer outside its options: "+q["id"])
    else:
        check(isinstance(q["answer"],(int,float)),q["id"]+": numerical answer expected")
check((ROOT/"assets/week10/collatz-lesson.svg").is_file(),"Collatz figure")
check((ROOT/"assets/week10/logistic-lesson.svg").is_file(),"Logistic figure")
check((ROOT/"assets/week10/sierpinski-lesson.svg").is_file(),"Sierpiński figure")
for fid in ("ccGraph","clGraph","clDiffGraph","cfGraph"):
    check(bool(parse(FILES[1]).xpath('//*[@id=$target]',target=fid)), "Explorer plot missing: "+fid)
if errors:
    raise SystemExit("\n".join(errors))
print("PASS: Week 10 page links, definitions, input feedback, accessibility, figures, and course assessment.")
