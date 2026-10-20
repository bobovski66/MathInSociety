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


def _focus_lab(path, text):
    """Apply the same reviewed copy and diagram selection on future rebuilds."""
    import json
    from pathlib import Path
    data = json.loads((Path(__file__).parent / 'lab_copy_edits.json').read_text())
    name = Path(path).name
    match = re.search(r'week(\\d+)_lab\\.html', name)
    key = 'extension' if name == 'week8_optimization_lab.html' else (match.group(1) if match else None)
    if key is None:
        return text
    for filename in data['remove'].get(key, []):
        pattern = r'<figure\\b[^>]*>[\\s\\S]*?<img\\b[^>]*src=["\\'][^"\\']*/' + re.escape(filename) + r'["\\'][\\s\\S]*?</figure>'
        text = re.sub(pattern, '', text, flags=re.I)
    replacements = data['ext'] if key == 'extension' else data['edits'].get(key, [])
    def plain(value):
        value = re.sub(r'<[^>]+>', ' ', value)
        return re.sub(r'\\s+', ' ', value).strip()
    for prefix, replacement in replacements:
        found = [False]
        def swap(m):
            if not found[0] and plain(m.group(2)).startswith(prefix):
                found[0] = True
                return m.group(1) + replacement + '</p>' if replacement else ''
            return m.group(0)
        text = re.sub(r'(<p\\b[^>]*>)([\\s\\S]*?)</p>', swap, text, flags=re.I)
    for original, revised in data['titles'].get(key, []):
        text = text.replace('>' + original + '</h', '>' + revised + '</h', 1)
    if 'lab-focus.css' not in text:
        text = re.sub(r'</head>', '<link rel="stylesheet" href="../assets/lab-focus.css"></head>', text, count=1, flags=re.I)
    text = re.sub(r'<body>', '<body class="lab-focus">', text, count=1, flags=re.I)
    return text

def streamline_activity_html(path, text):
    if not path.startswith(("labs/", "demos/")):
        return text
    text = _without_examples(text)
    if path.startswith('labs/'):
        text = _focus_lab(path, text)
    if path in ("demos/number_systems.html", "demos/probability_distribution.html"):
        text = _QUICK_ANSWER.sub(r"\1\2", text)
    return text
