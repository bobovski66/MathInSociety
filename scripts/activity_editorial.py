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
    """Apply the reviewed lab layout on future page rebuilds."""
    import json
    from pathlib import Path
    data = json.loads((Path(__file__).parent / "lab_copy_edits.json").read_text())
    name = Path(path).name
    match = re.search(r"week(\d+)_lab\.html", name)
    key = "extension" if name == "week8_optimization_lab.html" else (match.group(1) if match else None)
    if key is None:
        return text
    unused_figures = data["remove"].get(key, [])
    if unused_figures:
        def keep_relevant(m):
            return "" if any("/" + name in m.group(0) for name in unused_figures) else m.group(0)
        text = re.sub(r"<figure\b[^>]*>[\s\S]*?</figure>", keep_relevant, text, flags=re.I)
    replacements = data["ext"] if key == "extension" else data["edits"].get(key, [])
    def plain(value):
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", value)).strip()
    for prefix, replacement in replacements:
        found = [False]
        def swap(m):
            if not found[0] and plain(m.group(2)).startswith(prefix):
                found[0] = True
                return m.group(1) + replacement + "</p>" if replacement else ""
            return m.group(0)
        text = re.sub(r"(<p\b[^>]*>)([\s\S]*?)</p>", swap, text, flags=re.I)
    for original, revised in data["titles"].get(key, []):
        for tag in ("h2", "h3"):
            current = "<" + tag + ">" + original + "</" + tag + ">"
            if current in text:
                text = text.replace(current, "<" + tag + ">" + revised + "</" + tag + ">", 1)
                break
    if "lab-focus.css" not in text:
        text = re.sub(r"</head>", '<link rel="stylesheet" href="../assets/lab-focus.css"></head>', text, count=1, flags=re.I)
    text = re.sub(r"<body>", '<body class="lab-focus">', text, count=1, flags=re.I)
    return text

def streamline_activity_html(path, text):
    if not path.startswith(("labs/", "demos/")):
        return text
    text = _without_examples(text)
    if path.startswith('labs/'):
        text = _focus_lab(path, text)
        if 'data-download-filled-html' not in text:
            text, count = re.subn(
                r'(<button\b[^>]*\bdata-print-work\b[^>]*>[\s\S]*?</button>)',
                r'\1<button type="button" data-download-filled-html>Download filled HTML</button>',
                text, count=1, flags=re.I
            )
            if count != 1:
                raise ValueError('Lab needs a print button for filled-HTML download: ' + path)
        if 'lab-submission.js' not in text:
            text = re.sub(r'</head>', '<script defer src="../assets/lab-submission.js"></script></head>', text, count=1, flags=re.I)
        text = text.replace('Your name for the printed copy', 'Your name for the printed or downloaded copy')
    if path in ("demos/number_systems.html", "demos/probability_distribution.html"):
        text = _QUICK_ANSWER.sub(r"\1\2", text)
    return text
