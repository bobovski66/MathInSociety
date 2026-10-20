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
        "lead": "Where do repeated changes appear in everyday life?",
        "tags": ["Numbers", "Repeated changes"],
        "intro": [
            "Someone practices for 10 minutes on Monday, then adds 5 minutes each day. The next three practice times are 15, 20, and 25 minutes. The practice times form the sequence 10, 15, 20, 25.",
            "We see sequences like this in savings, game scores, and everyday routines.",
        ],
        "choose": "Choose a number you might keep track of: minutes of practice, items collected, points in a game, or something else that matters to you. A real or made-up example is fine.",
        "questions": [
            "What are you keeping track of, and why does it matter to you?",
            "Choose a starting number and one change to repeat, such as adding 5 each day or taking away 2 each round. Show the next three numbers. What does one step mean in your example?",
            "Would a fraction or a negative number make sense in your example? Give a reason.",
            "How long could your pattern reasonably continue? What might make it change?",
        ],
        "replies": [
            "What would happen if you changed by ___ each time instead?",
            "Would half of a ___ make sense here? I am thinking about…",
        ],
        "note": "Choose something you track, repeat a small change, and explain what the numbers mean in your life.",
    },
    2: {
        "title": "Who gets asked?",
        "lead": "How could the people you ask change the answer you get?",
        "tags": ["Samples", "Percentages"],
        "intro": [
            "You ask 10 people at a library whether they prefer printed books. Eight say yes. That is 8 ÷ 10 × 100 = 80% of the people you asked.",
            "Would you expect the same result if you asked somewhere else? The place and the people could make a difference.",
        ],
        "choose": "Think of a yes-or-no question you would like answered about your class, neighborhood, workplace, or a hobby. Make up a small survey result for this discussion.",
        "questions": [
            "What would you ask, and whose opinions do you want to learn about?",
            "Where or how would you ask? Imagine getting 10 answers. Choose how many say yes, then calculate that percentage: number of yes answers ÷ 10 × 100.",
            "Who might be left out by the way you ask? How could you hear from them?",
            "Would these answers be enough to help you make a decision? Explain what you would still want to know.",
        ],
        "replies": [
            "Would you get different answers if you asked ___?",
            "How could you hear from people who ___? Their answers might matter because…",
        ],
        "note": "Create a survey about something you care about, calculate a percentage, and consider whose answers might be missing.",
    },
    3: {
        "title": "What does an average miss?",
        "lead": "Does a typical number tell you what you need to know?",
        "tags": ["Averages", "Variation"],
        "intro": [
            "Three trips take 20, 25, and 30 minutes. Their mean, or average, is (20 + 25 + 30) ÷ 3 = 25 minutes. Their range is 30 − 20 = 10 minutes.",
            "The average is useful, but you might also care about the longest trip—especially if you need to arrive on time.",
        ],
        "choose": "Choose something in your day that varies: travel time, waiting time, practice time, or another measurement you care about. Use three to five values. They can be real or made up.",
        "questions": [
            "What do your values measure, and why do you care about them? Include the units, such as minutes or dollars.",
            "List your values. Find the mean by adding them and dividing by how many there are. Find the range by subtracting the smallest from the largest.",
            "Does the average give a useful picture of your example? Use one of your values to explain what it might miss.",
            "Would you want the values to stay close together, or would some variety be welcome? Explain how that would affect you.",
        ],
        "replies": [
            "Would the average still be helpful if one day ___?",
            "I would care most about ___ in your example because… What do you think?",
        ],
        "note": "Use a few everyday measurements to calculate an average and a range, then explain what each tells you.",
    },
    4: {
        "title": "How close is close enough?",
        "lead": "When would a range of estimates help you make a decision?",
        "tags": ["Estimates", "Margins", "Decisions"],
        "intro": [
            "A café reports an estimated average wait of 12 minutes, with a margin of 3 minutes. Subtracting and adding 3 gives an interval from 9 to 15 minutes for the average wait.",
            "That interval is about the café’s average. An individual customer could wait longer or shorter. Whether the estimate is useful also depends on the decision you need to make.",
        ],
        "choose": "Choose an average you would find useful: a waiting time, a cost, or time spent on an activity. Imagine a study reports an estimated average and a margin. Make up these two numbers for your example.",
        "questions": [
            "What average would you like to know? Describe the people, items, or days it would be about, and why it matters to you.",
            "Choose the reported average and margin. Subtract and add the margin to find the interval. Include the units.",
            "Would that range be close enough for a decision you care about? Explain why or why not.",
            "Would the interval mean every individual value falls inside it? Explain the difference between the average and one person’s or item’s measurement.",
        ],
        "replies": [
            "Would you make the same choice if the margin were twice as large?",
            "What would you want to know about how the study got its numbers? I would wonder about…",
        ],
        "note": "Choose an average that matters to you, build an interval from a supplied margin, and discuss whether it is useful for a decision.",
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
        "lead": "How would you balance paying something off with the other things you need money for?",
        "tags": ["Interest", "Payments", "Choices"],
        "intro": [
            "Suppose you owe $400. In a made-up loan, the monthly interest is 1%, so the first month adds $400 × 0.01 = $4. A $50 payment then leaves $400 + $4 − $50 = $354 owed.",
            "A bigger payment would leave less owed. It would also leave less money for other things that month. Both parts can matter when choosing a payment.",
        ],
        "choose": "Imagine borrowing for a repair, a useful item, a class, or another project you care about. Choose a starting amount and two possible monthly payments. You can invent all the amounts. Use the same made-up monthly interest rate of 1%. Add interest first, then take off the payment.",
        "questions": [
            "What would the borrowed money help you do? How much would you start out owing?",
            "Find the first month’s interest: starting amount × 0.01. For each payment, calculate starting amount + interest − payment. Choose payments smaller than your starting balance, and round money to cents.",
            "Which payment would you choose, and why? What else would you need to consider that month?",
            "In this model, next month’s interest is 1% of the balance left. Which payment would lead to less interest next month? Explain how the changing balance makes that happen.",
        ],
        "replies": [
            "What would happen to the balance if you paid $10 more each month?",
            "What other cost might affect which payment you choose? I am thinking about…",
        ],
        "note": "Choose a purpose and invented loan amounts, compare two one-month payment calculations, and explain which choice fits your priorities.",
    },
    7: {
        "title": "Would it be worth offering?",
        "lead": "What would make a small sale or service worth your time?",
        "tags": ["Cost", "Profit", "What matters"],
        "intro": [
            "Imagine selling 10 handmade items for $5 each. Getting started costs $20, and materials cost $2 per item. Money collected is 10 × $5 = $50. Total cost is $20 + 10 × $2 = $40. Profit is $50 − $40 = $10.",
            "That $10 is what remains after the costs counted here. Your time or other costs could change whether the idea feels worthwhile.",
        ],
        "choose": "Imagine offering something you know how to make or do: food at an event, handmade items, a lesson, or a small service. Choose a price, a cost for each sale, a one-time setup cost, and an expected number of sales. Estimates or made-up amounts are fine. Assume you only prepare what you sell.",
        "questions": [
            "What would you offer, and who might want it? State your price, cost per sale, setup cost, and expected sales.",
            "Calculate money collected = price × sales. Calculate total cost = setup cost + cost per sale × sales. Subtract cost from money collected to find profit. What does the result tell you?",
            "Would this feel worth doing? Explain one thing besides money that matters to you, such as time, enjoyment, affordability, or helping someone.",
            "Choose a smaller number of sales and calculate the profit again. Does that change your opinion of the idea? Why?",
        ],
        "replies": [
            "What would happen if you charged $1 less? Would you expect more sales?",
            "Would you want to count ___ as a cost? It might matter because…",
        ],
        "note": "Choose a small sale or service, calculate profit for two sales counts, and discuss whether the idea is worth your time.",
    },
    8: {
        "title": "Making room for what matters",
        "lead": "How do you choose when your time and money will only go so far?",
        "tags": ["Limits", "Possible plans", "Goals"],
        "intro": [
            "You have 3 hours and $20 for an afternoon project. Baking takes 2 hours and costs $12. Making a card takes 1 hour and costs $5. Doing them one after the other uses 3 hours and $17, so it fits both limits.",
            "Another plan might also fit. Choosing between possible plans means thinking about what you want from the afternoon.",
        ],
        "choose": "Plan something you would enjoy or find useful: a day off, a club event, or a small project. Choose two activities or items. Estimate the time and money each needs, then set your available time and money. Made-up amounts are fine.",
        "questions": [
            "What are you planning? State your two choices, their costs and times, and your time and money limits.",
            "Make two plans you could consider. Add up the time and money for each plan. Which ones fit both limits? Show your totals.",
            "Which plan would you choose, or how would you change one to make it work? What are you trying to get more of or use less of, and why does that matter to you?",
            "If you could increase just one limit—time or money—which would you choose? Give it a larger amount and check whether that would change what you can do.",
        ],
        "replies": [
            "Would your choice change if you had one more hour?",
            "Could you make room for ___ by doing less of ___? I wonder whether…",
        ],
        "note": "Plan an activity you care about, check two plans against time and money limits, and explain which goal guides your choice.",
    },
    9: {
        "title": "Connections that matter",
        "lead": "What could one changed connection mean in a network you know?",
        "tags": ["Networks", "Routes", "Connections"],
        "intro": [
            "Suppose A passes a message to B, B to C, and C to D. Getting from A to D takes three connections. If A and D can contact each other directly, that route takes just one connection: two fewer.",
            "We can use the same kind of drawing for routes between places, contacts in a group, or connections between devices. The meaning of a useful change depends on the situation.",
        ],
        "choose": "Choose a network from your life or interests: roads, a game group, a workplace, a club, or something else. Sketch four to six points and the connections between them. Label the points A, B, C, and so on. For this drawing, treat each connection as working in both directions.",
        "questions": [
            "What do your points and connections stand for? Why does this network matter to you? Include your sketch or describe the connections in words.",
            "Choose two points that are connected by a route. Find the route using the fewest connections. Show it and count the connections, rather than the points.",
            "Add one connection or remove one. Check the route between the same two points again. How many connections are needed now, or is there no route? What could that change mean for the people using the network?",
            "What would it take to make that change in real life? What important detail might your drawing leave out?",
        ],
        "replies": [
            "What would happen if the connection between ___ and ___ stopped working?",
            "Could a connection from ___ to ___ help in a different way? I am thinking about…",
        ],
        "note": "Draw a small network from your life, count a route before and after changing a connection, and discuss what the result could mean.",
    },
    10: {
        "title": "How far would you trust a prediction?",
        "lead": "What can a repeated rule tell you—and what would you still need to find out?",
        "tags": ["Repeated rules", "Starting numbers", "Forecasts"],
        "intro": [
            "We predict things when we plan a trip, practice a skill, or expect a project to grow. A number can help us think ahead, but we also need to ask where it came from.",
            "This week’s activities show that repeating a clear rule can lead to surprising results. Here, try a simple rule for something you know and consider how much you would trust it.",
        ],
        "example": '<h3>One short example</h3><p>A made-up forecast doubles an amount each round. Starting with 5 and starting with 6 gives:</p><div class="table-wrap"><table><thead><tr><th scope="col">Start</th><th scope="col">After 1 round</th><th scope="col">After 2</th><th scope="col">After 3</th></tr></thead><tbody><tr><td>5</td><td>10</td><td>20</td><td>40</td></tr><tr><td>6</td><td>12</td><td>24</td><td>48</td></tr></tbody></table></div><p>The starting gap is 1; after three rounds it is 8. This doubling rule still has a predictable pattern.</p>',
        "choose": "Choose something you might try to predict, such as practice time, progress on a project, or the number of people joining an activity. Make up a simple rule that could fit it: add a fixed amount, multiply by the same number, or take half of what is left.",
        "questions": [
            "What are you trying to predict, and why would the prediction matter to you? State your starting number, rule, and what one step means.",
            "Use your rule for three steps. Then change the starting number a little and repeat the same three steps. Show both sets of numbers and the difference between their final values.",
            "What might happen in your real example that your rule leaves out? Would the same pattern keep working? Explain with a specific possibility.",
            "How far ahead would you trust this forecast, and why? What would you check as new information arrives?",
        ],
        "replies": [
            "Would changing the starting number by ___ change your decision?",
            "What new information might make you revise the rule? I would watch for…",
        ],
        "note": "Choose a situation to forecast, compare three updates from two nearby starts, and explain how far you would trust the result.",
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
<main class="wrap" id="main"><header class="hero"><div class="eyebrow">Week {week} / Discussion</div><h1>{escape(item['title'])}</h1><p class="lead">{escape(item['lead'])}</p><div class="meta">{tags}</div></header>
<section class="card"><h2>An example</h2>{paragraphs}</section>
<section class="card" id="your-post"><h2>Your post</h2><p>{escape(item['choose'])}</p><p>Answer the four questions using your example, then post your response in Canvas.</p><ol class="tasks">{questions}</ol></section>
<section class="card" id="replies"><h2>Reply to a classmate</h2><p>Read a classmate's example and respond with a question, a suggestion, or a connection to your own experience.</p><p>You might start with:</p><ul>{replies}</ul><p>Include a sentence explaining your question or suggestion.</p></section>
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
