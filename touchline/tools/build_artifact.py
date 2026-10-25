"""Build the claude.ai artifact page from the game file.

The artifact service wraps a page in its own <!doctype html><head>...<body>, so the page starts at <title> and <style>.
The home-screen tags (manifest, touch icon) are dropped: they point at files the artifact does not have. The game
itself is unchanged.

Usage: python3 touchline/tools/build_artifact.py [out.html]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'index.html')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', '..', 'artifact', 'touchline.html')
# The service's wrapper sets a white body in a system font; the game's own body rule is restated after it.
BODY_CSS = ("body{margin:0;background:var(--bg);color:var(--text);font-family:var(--body,system-ui),system-ui,-apple-system,"
            "'Segoe UI',Roboto,Arial,sans-serif;font-size:16px;line-height:normal}")

src = open(SRC, encoding='utf-8').read()
lines = src.split('\n')
head, css, body = lines[0], lines[1], lines[2]
assert head.startswith('<!doctype html>') and head.endswith('<style>'), 'line 1 should be the head ending in <style>'
assert body.startswith('</style></head><body>'), 'line 3 should close the style and open the body'
script = lines[3:]
while script and script[-1] == '':
    script.pop()
assert script[-1] == '</script></body></html>', 'the file should end with the main script'
script[-1] = '</script>'
out = '\n'.join(['<title>Touchline</title>', '<style>', css, BODY_CSS + body.replace('</style></head><body>', '</style>', 1)] + script) + '\n'
os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
open(OUT, 'w', encoding='utf-8').write(out)
print(len(out), 'bytes ->', os.path.abspath(OUT))
