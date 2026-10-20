"""Preserve student-facing reading edits when weekly source pages are regenerated."""
import json
import re
from pathlib import Path
from functools import lru_cache

@lru_cache(maxsize=1)
def _rules():
    return json.loads((Path(__file__).parent / "reading_copy_edits.json").read_text())

def _plain(s):
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def _remove_intro_grid(s):
    pos = s.find('<div class="grid">')
    if pos < 0 or not re.search(r"By the end|Build the model|Build and read|What you will calculate", s[pos:pos+280]):
        return s
    depth = 1
    tag = re.compile(r"</?div\b[^>]*>", re.I)
    for m in tag.finditer(s, pos + len('<div class="grid">')):
        depth += -1 if m.group().startswith("</") else 1
        if depth == 0:
            return s[:pos] + s[m.end():]
    raise ValueError("Unbalanced introductory grid")

def streamline_reading_html(path, text):
    name = Path(path).name
    m = re.fullmatch(r"week(\d+)_reading\.html", name)
    if not path.startswith("readings/") or not m:
        return text
    rules = _rules().get(m.group(1), {})
    for tag, original, revised in rules.get("headings", []):
        text = text.replace(f"<{tag}>{original}</{tag}>", f"<{tag}>{revised}</{tag}>", 1)
    for prefix, replacement in rules.get("paragraphs", []):
        found = [False]
        def swap(m):
            if found[0] or not _plain(m.group(2)).startswith(prefix):
                return m.group(0)
            found[0] = True
            return m.group(1) + replacement + "</p>"
        text = re.sub(r"(<p\b[^>]*>)([\s\S]*?)</p>", swap, text, flags=re.I)
    if rules.get("removeIntroGrid"):
        text = _remove_intro_grid(text)
    return text
