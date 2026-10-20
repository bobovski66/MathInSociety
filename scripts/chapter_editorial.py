"""Introduce chapter mathematics without describing earlier editing work."""
from pathlib import Path
PARAGRAPHS = {"Math107_Chapter_01.tex":[["Try the short checks before reading the explanations in the solutions.","Natural numbers count objects, integers describe signed changes, rational numbers describe ratios, and real numbers locate points on the number line. Repeated additions and multiplications provide two different rules for change."]],"Math107_Chapter_02.tex":[["Try the short checks before reading their explanations.","An observed proportion describes a particular sample; a probability model describes how outcomes are expected to occur under its assumptions. Comparing the two requires attention to the selection process and the denominator."]],"Math107_Chapter_03.tex":[["Try the short checks before reading their explanations.","The mean distributes a total equally, the median identifies the middle position, and the standard deviation measures variation about the mean. The graph supplies context for those summaries."]],"Math107_Chapter_04.tex":[["Try the short checks before reading their explanations.","A z-score places an individual observation relative to the model mean and standard deviation. An interval estimate uses a sample to draw conclusions about an unknown population quantity."]],"Math107_Chapter_05.tex":[["Try each short check before consulting its explanation in the solutions.","A controller acts on the report it receives. When information arrives late, its next correction can respond to a condition that has already changed. The resulting sequence may overshoot or oscillate."]],"Math107_Chapter_06.tex":[["The core work uses arithmetic, powers, and simple equations.","A fixed-dollar addition gives linear growth, while a percentage of the current balance gives compound growth. A loan combines percentage growth with payments, and the order of the updates affects the next balance."]],"Math107_Chapter_07.tex":[["This chapter assumes no previous business mathematics or calculus.","Quantity is the input in our business model. Cost, revenue, and profit assign dollar values to each choice; their formulas let us locate break-even and compare feasible quantities."]],"Math107_Chapter_08.tex":[["By the end of Part I, you can define variables and units,","Each resource constraint defines a set of possible plans. Their intersection is the feasible region. Its boundaries and vertices reveal how the resource limits act together."]],"Math107_Chapter_09.tex":[["Part I developed the variables, inequalities, and feasible geometry.","A feasible point represents an allowable plan. A linear objective assigns a score to each plan; examining the feasible region identifies the highest or lowest attainable score, including ties and possible unboundedness."]],"Math107_Chapter_09_Networks.tex":[["This chapter begins with the meaning of a dot and a line,","Nodes stand for locations; edges stand for direct contacts. Paths make communication possible between distant nodes, while failures and spreading rules determine how the network responds."]],"Math107_Chapter_10.tex":[["By the end, you can trace Collatz routes,","One rule can produce a long number trajectory, intricate geometry, or sensitivity to a starting measurement. We will distinguish calculation for chosen examples from the stronger conclusions that require proof."],["Work through the examples before the short checks.","Repeated updates show how a result develops. Calculating many particular cases helps us investigate a pattern, but it does not by itself establish a claim for every starting value."]]}
TITLES = {"Math107_Chapter_05.tex":[["When information changes what happens next","Feedback, information, and control"]],"Math107_Chapter_06.tex":[["Following the balance","Interest, growth, and loan payments"]],"Math107_Chapter_07.tex":[["Choosing what ``best'' means","Costs, revenue, and profit"]],"Math107_Chapter_09_Networks.tex":[["Small connections.\\\\Collective effects.","Networks, paths, and spreading"]],"Math107_Chapter_10.tex":[["Simple rules.\\\\Surprising worlds.","Recursion, fractals, and prediction"]]}
def polish_generated_chapters(paths):
    for raw in paths:
        path=Path(raw);name=path.name
        source=path.read_text()
        start=source.find(r"\begin{document}")
        end=source.find(r"\clearpage",start+1)
        if start<0 or end<0:
            raise ValueError("Missing cover for "+name)
        cover=source[:end];remainder=source[end:]
        for old,new in TITLES.get(name,[]):
            cover=cover.replace(old,new)
        for prefix,new in PARAGRAPHS.get(name,[]):
            ls=cover.splitlines(keepends=True)
            hits=0
            for i,line in enumerate(ls):
                if line.strip().startswith(prefix):
                    ls[i]=new+chr(10);hits+=1
            cover="".join(ls)
            if hits>1:raise ValueError("Ambiguous paragraph in "+name)
        source=cover+remainder
        if name=="Math107_Chapter_02.tex":
            source=source.replace("These are the chapter's original practice situations. Name the group of interest before discussing what the selection method may miss.", "For each study, identify the intended population and the group actually observed. Consider which observations the selection method might miss.")
        path.write_text(source)
