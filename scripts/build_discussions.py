"""Build the ten experience-based discussion prompts from one source.

The other weekly page builders call build_discussion so regenerating a unit
does not bring back a retired discussion or its draft fields.
"""
from pathlib import Path
from html import escape
import argparse
import json
import os

ROOT = Path(__file__).resolve().parents[1]

DISCUSSIONS = {
    1: {
        "title": "A small change, repeated",
        "lead": "How can a simple number rule describe change in everyday life?",
        "tags": [],
        "intro": [
            "A score starts at 10 points and increases by 5 points each round. The rule is to add 5 to the current score after every round.",
            "A sequence records the starting amount and each new value. You can imagine a different setting where a similar rule might apply."
        ],
        "choose": "Use this number pattern and imagine a situation it could describe.",
        "questions": [
            "Starting at 10, calculate the scores after rounds 1, 2, and 3. Show the sequence, including the starting value.",
            "What might these numbers represent? In your situation, would a fractional or negative value make sense? Explain.",
            "How long might adding 5 each round remain reasonable? What could cause the rule to change?"
        ],
        "replies": [],
        "note": "Calculate three steps of an additive sequence, then explore what the numbers might mean and when the rule applies."
    },
    2: {
        "title": "Who gets asked?",
        "lead": "What can a small survey tell us, and whose answers might be missing?",
        "tags": [],
        "intro": [
            "At a community event, 20 people answer the question, “Would you attend an evening workshop?” Twelve answer yes.",
            "The fraction who answer yes describes the people surveyed. To interpret it for a larger community, consider how those 20 people were selected."
        ],
        "choose": "Use the survey above to calculate a percentage and think about the people represented.",
        "questions": [
            "What fraction and percentage of the 20 respondents said yes? Show the calculation.",
            "Imagine that the survey was given only to people already attending a community event. Who might be missing, and how could you reach them?",
            "Would these responses be enough to plan the workshop? Explain what else you would want to know."
        ],
        "replies": [],
        "note": "Calculate a survey percentage, then discuss sampling, missing viewpoints, and how the result could inform a decision."
    },
    3: {
        "title": "What does an average miss?",
        "lead": "How much can an average tell us about a set of measurements?",
        "tags": [],
        "intro": [
            "Four trips take 20, 25, 25, and 30 minutes. The times describe the same journey on different days.",
            "A mean summarizes the center of these observations. A range describes the difference between the longest and shortest trips."
        ],
        "choose": "Calculate the summaries for these four trips and consider how they might affect a decision.",
        "questions": [
            "Find the mean and range of the four travel times. Show your arithmetic and include units.",
            "Suppose you need to arrive at an appointment on time. How useful would the mean be, and which other value might matter?",
            "Imagine a fifth trip takes 50 minutes. How might this change your interpretation of the route?"
        ],
        "replies": [],
        "note": "Calculate mean and range for four trip times, then consider variation and the influence of an unusual trip."
    },
    4: {
        "title": "How close is close enough?",
        "lead": "When is an estimate precise enough to be useful?",
        "tags": [],
        "intro": [
            "A sample gives an estimated average waiting time of 12 minutes, with a reported margin of 3 minutes.",
            "Subtracting and adding the margin creates an interval of plausible values for the population mean under the study's method."
        ],
        "choose": "Use the reported estimate and margin to interpret a possible decision.",
        "questions": [
            "Calculate the lower and upper endpoints of the interval. Include units.",
            "Imagine you are planning a visit where waiting time matters. Would this estimate be useful? What would you want to know about how it was collected?",
            "Does the interval describe every individual's wait? Explain the difference between a population average and one person's experience."
        ],
        "replies": [],
        "note": "Calculate an interval from a reported estimate and margin, then discuss precision and interpretation."
    },
    5: {
        "title": "Making adjustments",
        "lead": "What helps us decide whether to make a change—or give it more time?",
        "tags": ["Feedback", "Delay", "Everyday choices"],
        "intro": [
            "You turn up a shower because the water feels cold. Nothing seems to happen, so you turn it up again. A few seconds later, the water is too hot.",
            "Each time, you used how the water felt to decide what to do next. That is feedback. But the water took time to respond.",
        ],
        "choose": "Choose something people adjust—such as room temperature, a recipe, a practice routine, or the amount of water a plant gets. Your example can be real or made up.",
        "questions": [
            "Describe what someone is trying to get right. What tells them whether their change is working?",
            "What could happen if they make a change that is too big?",
            "What could happen if it takes a while to see the result?",
            "Would everyone agree on what counts as “better”? Explain your thinking.",
        ],
        "replies": [
            "What would happen if you waited longer before changing it again?",
            "I think that could work because… Have you also thought about ___?",
        ],
        "note": "Choose an everyday example of feedback and answer all the questions about big changes, waiting, and what counts as better.",
    },
    6: {
        "title": "A payment that works for you",
        "lead": "How does your monthly payment affect the loan balance and your other priorities?",
        "tags": [],
        "intro": [
            "Imagine someone borrowed $500 for an expense of their choice. The loan charges 1% interest each month. They can make a monthly payment of either $30 or $75.",
            "Interest is added before each payment. Use ending balance = starting balance + interest − payment. Assume the interest rate stays fixed and there are no additional charges.",
        ],
        "choose": "Use the amounts above. You can invent the borrower's circumstances to explain their choice.",
        "questions": [
            "Calculate the first month's interest on $500. Then calculate the remaining balance after a $30 payment and after a $75 payment. Show your arithmetic.",
            "Imagine a reason for borrowing the money. Which payment would you choose for that situation, and what other expenses or priorities would influence the decision?",
            "Which choice leads to less interest in the second month? Explain using the balances you calculated. What might make the borrower reconsider their choice?",
        ],
        "replies": [],
        "note": "Compare two payment amounts for a $500 loan, calculate the first month's balances, and discuss how circumstances affect the choice.",
    },
    7: {
        "title": "Would it be worth offering?",
        "lead": "How do costs and revenue affect whether a small project is worthwhile?",
        "tags": [],
        "intro": [
            "Suppose a club sells handmade items for $8 each. Materials cost $3 per item, and the club pays a $60 setup fee. The club sells 20 items.",
            "The money collected is revenue. Total cost combines the setup fee and the materials. Profit is revenue minus cost."
        ],
        "choose": "Calculate the result for this club, then consider how someone might judge the plan.",
        "questions": [
            "For 20 sales, calculate revenue, total cost, and profit. Show your arithmetic.",
            "Would this be worth doing for the club? What might matter besides the profit shown by this model?",
            "Suppose only 10 items sell. How would that affect profit and your recommendation? Explain any other assumptions you would want to check."
        ],
        "replies": [],
        "note": "Calculate revenue, cost, and profit for a club sale, then consider uncertainty and nonfinancial goals."
    },
    8: {
        "title": "Making room for what matters",
        "lead": "How do we choose among plans when resources are limited?",
        "tags": [],
        "intro": [
            "A club has 3 hours and $20 for an afternoon. Activity A takes 2 hours and costs $12. Activity B takes 1 hour and costs $9.",
            "A plan is feasible when it fits both limits. Consider doing either activity or both."
        ],
        "choose": "Use the time and money limits above to compare possible plans.",
        "questions": [
            "Calculate the total time and cost of doing both activities. Does that plan meet each limit? Show the comparisons.",
            "Would you choose A, B, or a modified combination? Describe what you would value most in this situation.",
            "If the club could gain either one extra hour or $2 more, which would expand its options? Explain how you know."
        ],
        "replies": [],
        "note": "Check a plan against two resource constraints, then consider choices, goals, and changing the limits."
    },
    9: {
        "title": "Connections that matter",
        "lead": "How can one connection change the routes through a network?",
        "tags": [],
        "intro": [
            "Consider four locations A, B, C, and D. The undirected connections are A–B, B–C, C–D, and B–D.",
            "A route is a sequence of connected locations. Its length counts connections traveled."
        ],
        "choose": "Compare routes from A to D, then consider what connections mean in a real setting.",
        "questions": [
            "Find a shortest route from A to D and count its edges. Now remove B–D and find the new shortest route.",
            "Imagine these are roads, communication links, or contacts in a group. Why might the changed route matter?",
            "Suggest one new link that would improve the network for some purpose. What real-world detail would you need before choosing it?"
        ],
        "replies": [],
        "note": "Count shortest routes before and after removing a network link, then discuss why connections matter."
    },
    10: {
        "title": "How far would you trust a prediction?",
        "lead": "How far should we trust a prediction from a repeated rule?",
        "tags": [],
        "intro": [
            "Start with 5 and use the update rule “double the current number, then add 1.” Compare it with the same rule starting at 6.",
            "The starting amounts differ by 1. Both sequences follow exactly the same arithmetic rule."
        ],
        "choose": "Calculate both sequences and think about predictions made from measured starting values.",
        "questions": [
            "Calculate three updates from each starting amount. How far apart are the two results after the third update?",
            "Imagine the rule models a changing quantity. What might the difference between these predictions mean?",
            "What observations or changing conditions would help you decide how far ahead to trust either forecast?"
        ],
        "replies": [],
        "note": "Compare two three-step forecasts with nearby starting values, then discuss model assumptions and observational limits."
    },

}


def write(path, content):
    target = ROOT / path
    temporary = target.with_suffix(target.suffix + ".tmp")
    with temporary.open("w") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, target)


def weeks_from_dashboard():
    source = (ROOT / "index.html").read_text()
    start = source.index("const WEEKS = ") + len("const WEEKS = ")
    return json.JSONDecoder().raw_decode(source[start:])[0]


def discussion_entry(week):
    item = DISCUSSIONS[week]
    return {
        "title": f"Module {week} Discussion — {item['title']}",
        "url": f"discussions/week{week}_discussion.html",
        "note": item["note"],
    }


def build_discussion(week):
    item = DISCUSSIONS[week]
    info = next(w for w in weeks_from_dashboard() if w["week"] == week)
    links = [("Reading", info["reading"][0]["url"])]
    for number, demo in enumerate(info["demos"]):
        label = "Explorer" if len(info["demos"]) == 1 else ["Feasible regions", "Optimizer"][number]
        links.append((label, demo["url"]))
    links.extend([
        ("Laboratory", info["weekly_lab"]["url"]),
        ("Application", info["application"][0]["url"]),
        ("Discussion", f"discussions/week{week}_discussion.html"),
    ])
    if week == 5:
        links.append(("History", "information_cybernetics_timeline.html"))
    nav = "".join(
        f'<a href="../{escape(url, quote=True)}"'
        + (' aria-current="page"' if label == "Discussion" else "")
        + f'>{escape(label)}</a>' for label, url in links
    )
    paragraphs = "".join(f"<p>{escape(p)}</p>" for p in item["intro"])
    if item.get("example"):
        paragraphs += '<div class="example">' + item["example"] + '</div>'
    questions = "".join(f"<li>{escape(q)}</li>" for q in item["questions"])
    replies = "".join(f"<li>“{escape(q)}”</li>" for q in item["replies"])
    tags = "".join(f'<span class="tag">{escape(tag)}</span>' for tag in item["tags"])
    tag_row = f'<div class="meta">{tags}</div>' if week == 5 else ''
    intro_heading = "An example" if week == 5 else "The situation"
    post_instruction = "Answer the four questions using your example, then post your response in Canvas." if week == 5 else "Post your answers in Canvas."
    reply_text = ("<p>Read a classmate's example and respond with a question, a suggestion, or a connection to your own experience.</p><p>You might start with:</p><ul>" + replies + "</ul><p>Include a sentence explaining your question or suggestion.</p>" if week == 5 else "<p>Read a classmate’s post. Ask a question, offer another consideration, or explain how a changed assumption might affect the result.</p>")
    unit = week if week >= 4 else 5
    previous = f'<a href="week{week-1}_discussion.html">← Week {week-1} discussion</a>' if week > 1 else '<a href="../index.html">← Course home</a>'
    following = f'<a href="week{week+1}_discussion.html">Week {week+1} discussion →</a>' if week < 10 else '<a href="../index.html">Course home →</a>'
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{escape(item['note'], quote=True)}"><title>Week {week} Discussion — {escape(item['title'])} | Math in Society</title>
<link rel="stylesheet" href="../assets/week{unit}/week{unit}.css">'''
    page += r'''<script>window.MathJax={tex:{inlineMath:[['\\(','\\)']],displayMath:[['\\[','\\]']]},options:{skipHtmlTags:['script','noscript','style','textarea','pre','code']}};</script><script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>'''
    page += f'''<script defer src="../assets/week{unit}/week{unit}.js"></script></head>
<body><a class="skip" href="#main">Skip to content</a><header class="topbar"><a href="../index.html">← MATH&amp; 107 · Math in Society</a><span>Centralia College · Dr Lee</span></header>
<nav class="unit-nav" aria-label="Week {week} materials">{nav}</nav>
<main class="wrap" id="main"><header class="hero"><div class="eyebrow">Week {week} / Discussion</div><h1>{escape(item['title'])}</h1><p class="lead">{escape(item['lead'])}</p>{tag_row}</header>
<section class="card"><h2>{intro_heading}</h2>{paragraphs}</section>
<section class="card" id="your-post"><h2>Your post</h2><p>{escape(item['choose'])}</p><p>{post_instruction}</p><ol class="tasks">{questions}</ol></section>
<section class="card" id="replies"><h2>Reply to a classmate</h2>{reply_text}</section>
<div class="actions no-print"><button type="button" data-print-page>Print this discussion prompt</button></div>
<div class="next">{previous}{following}</div>
<footer class="footer"><span>MATH&amp; 107 · Week {week} · Discussion</span><a href="../{info['reading'][0]['url']}">Return to the Week {week} reading ↗</a></footer></main></body></html>
'''
    write(f"discussions/week{week}_discussion.html", page)


def update_dashboard(selected):
    path = ROOT / "index.html"
    source = path.read_text()
    start = source.index("const WEEKS = ") + len("const WEEKS = ")
    weeks, length = json.JSONDecoder().raw_decode(source[start:])
    for week in weeks:
        if week["week"] in selected:
            week["discussion"][0].update(discussion_entry(week["week"]))
    updated = json.dumps(weeks, ensure_ascii=False, separators=(",", ":"))
    write("index.html", source[:start] + updated + source[start + length:])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--week", type=int, choices=range(1, 11), action="append")
    args = parser.parse_args()
    selected = args.week or list(DISCUSSIONS)
    for week in selected:
        build_discussion(week)
    update_dashboard(selected)
    os.sync()
    print(f"Built {len(selected)} discussions with personal examples, all-question prompts, and reply starters.")
