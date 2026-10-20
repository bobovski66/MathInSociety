"""Check that every student lab keeps only problem-relevant visuals and stable layout."""
from pathlib import Path
from lxml import html
from activity_editorial import streamline_activity_html

ROOT = Path(__file__).resolve().parents[1]
FILES = [f"labs/week{n}_lab.html" for n in range(1, 11)] + ["labs/week8_optimization_lab.html"]
EXPECTED = {
    1: ["recursion-comparison.svg"],
    2: ["document-errors.svg"],
    3: ["same-mean-spread.svg"],
    4: [],
    5: ["immediate-delayed.svg"],
    6: [],
    7: ["tutoring-graph.svg"],
    8: [],
    9: ["community-network.svg"],
    10: ["koch-stages.svg"],
    "extension": [],
}
total_questions = 0
total_figures = 0
for name in FILES:
    key = "extension" if "optimization" in name else int(name.split("week")[1].split("_")[0])
    markup = (ROOT / name).read_text()
    tree = html.fromstring(markup)
    body = tree.xpath("//body")
    assert len(body) == 1 and "lab-focus" in body[0].get("class", "").split(), f"{name}: focus style missing"
    assert tree.xpath('//link[@href="../assets/lab-focus.css"]'), f"{name}: shared stylesheet missing"
    assert not tree.xpath('//header[contains(concat(" ", normalize-space(@class), " "), " hero ")]//div[contains(concat(" ", normalize-space(@class), " "), " meta ")]'), f"{name}: decorative badge row returned"
    buttons = tree.xpath('//*[@data-download-filled-html]')
    assert len(buttons) == 1 and buttons[0].tag == "button", f"{name}: expected one filled-HTML download button"
    assert tree.xpath('//script[@src="../assets/lab-submission.js"]'), f"{name}: HTML download script missing"
    imgs = [img.get("src", "").rsplit("/", 1)[-1] for img in tree.xpath("//figure//img")]
    assert imgs == EXPECTED[key], f"{name}: unexpected pictures: {imgs}"
    assert not tree.xpath('//div[contains(concat(" ",normalize-space(@class)," ")," example ")]'), f"{name}: worked example returned"
    groups = tree.xpath('//section[@data-check-group]')
    assert len(groups) >= (4 if key == 5 else 5), f"{name}: unexpected number of problems"
    for group in groups:
        assert group.xpath("./h2"), f"{name}: missing problem heading"
        assert group.xpath('.//input | .//textarea | .//select'), f"{name}: no response fields"
    total_questions += len(tree.xpath('//div[contains(concat(" ", normalize-space(@class), " "), " question ")]'))
    total_figures += len(imgs)
    assert streamline_activity_html(name, markup) == markup, f"{name}: rebuilding would change the live lab"

sample = '<html><head></head><body><main><p>Work through the five investigations. Sample instructions.</p><figure><img src="../assets/week1/number-tower.svg"></figure><section class="card" data-check-group="1"><h2>Try this</h2><input id="ans" data-answer="2"></section><button type="button" data-print-work>Print</button></main></body></html>'
out = streamline_activity_html("labs/week1_lab.html", sample)
assert "number-tower.svg" not in out
assert '<input id="ans" data-answer="2">' in out
assert 'lab-focus.css' in out
assert 'lab-submission.js' in out and 'data-download-filled-html' in out
assert 'Five investigations cover' in out
sample_with_badges = '<html><head></head><body><header class="hero"><h1>Sample lab</h1><div class="meta"><span class="tag">Feedback beside each answer</span></div></header><main><button type="button" data-print-work>Print</button></main></body></html>'
result = streamline_activity_html("labs/week5_lab.html", sample_with_badges)
assert '<h1>Sample lab</h1>' in result
assert 'Feedback beside each answer' not in result
assert 'class="meta"' not in result
print(f"PASS: {len(FILES)} labs, {total_questions} response groups, {total_figures} problem-specific images, and rebuild idempotence.")
