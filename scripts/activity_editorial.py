"""Keep student investigations lean when the course page builders are rerun.

Readings and applications are intentionally unaffected. Labs are questions and
data, not worked-example collections. Demos should invite exploration.
"""
import re

_DIV_TAG = re.compile(r"</?div\b[^>]*>", re.IGNORECASE)
_EXAMPLE = re.compile(r'<div\b[^>]*class=["\'][^"\']*\bexample\b[^"\']*["\'][^>]*>', re.IGNORECASE)
_QUICK_ANSWER = re.compile(
    r'(<div class="quick-check"><p>[\s\S]*?</p>)<details>[\s\S]*?</details>(</div>)',
    re.IGNORECASE
)

def _without_examples(text):
    while match := _EXAMPLE.search(text):
        level = 1
        finish = None
        for tag in _DIV_TAG.finditer(text, match.end()):
            level += -1 if tag.group().startswith("</") else 1
            if level == 0:
                finish = tag.end()
                break
        if finish is None:
            raise ValueError("Unclosed worked-example block")
        block = text[match.start():finish]
        if re.search(r"<(?:input|button|select|textarea)\b", block, re.I):
            raise ValueError("Attempt to remove an interactive field")
        text = text[:match.start()] + text[finish:]
    return text

def streamline_activity_html(path, text):
    if not path.startswith(("labs/", "demos/")):
        return text
    text = _without_examples(text)
    if path in ("demos/number_systems.html", "demos/probability_distribution.html"):
        text = _QUICK_ANSWER.sub(r"\1\2", text)
    return text
