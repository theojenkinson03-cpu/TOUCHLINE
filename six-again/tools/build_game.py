"""Builds web/index.html: the Touchline engine with the 6 Again patch set applied, the page shell and the player database.

Usage: python3 tools/build_game.py   (then `npm run build:game` to refresh the copy the app bundles)
"""
import glob, importlib.util, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'touchline-engine.js')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'web', 'index.html')
DB = os.path.join(HERE, 'players.json')

class PatchError(Exception):
    pass

def rep(text, old, new, count=1, name=''):
    n = text.count(old)
    if count is not None and n != count:
        raise PatchError(f'[{name}] expected {count} match(es), found {n}: {old[:160]!r}')
    if n == 0:
        raise PatchError(f'[{name}] not found: {old[:160]!r}')
    return text.replace(old, new)

def resub(text, pattern, new, count=1, name='', flags=0):
    out, n = re.subn(pattern, new, text, flags=flags)
    if count is not None and n != count:
        raise PatchError(f'[{name}] regex expected {count}, found {n}: {pattern[:160]!r}')
    return out

def replace_function(text, fname, new_src, name=''):
    """Replace a whole top-level `function fname(...){...}` (brace-matched, string-aware) with new_src."""
    m = re.search(r'(?:^|(?<=[;}\n]))(async )?function ' + re.escape(fname) + r'\(', text, flags=re.M)
    if not m:
        raise PatchError(f'[{name}] function {fname} not found')
    start = m.start() if text[m.start()] not in ';}\n' else m.start()
    i = text.index('{', m.end() - 1 + text[m.end() - 1:].index(')'))
    # find matching brace, skipping strings and template literals and regex-free code
    depth, j, n = 0, i, len(text)
    stack = []
    while j < n:
        c = text[j]
        top = stack[-1] if stack else None
        if top in ("'", '"'):
            if c == '\\': j += 2; continue
            if c == top: stack.pop()
            j += 1; continue
        if top == '`':
            if c == '\\': j += 2; continue
            if c == '`': stack.pop(); j += 1; continue
            if c == '$' and j + 1 < n and text[j + 1] == '{':
                stack.append(('$', depth)); depth += 1; j += 2; continue
            j += 1; continue
        if c in '\'"`':
            stack.append(c); j += 1; continue
        if c == '/' and j + 1 < n and text[j + 1] == '/':
            k = text.find('\n', j); j = n if k < 0 else k; continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if isinstance(top, tuple) and top[1] == depth:
                stack.pop(); j += 1; continue
            if depth == 0:
                return text[:start] + new_src + text[j + 1:]
        j += 1
    raise PatchError(f'[{name}] unbalanced function {fname}')

def main():
    js = open(SRC, encoding='utf-8').read()
    for path in sorted(glob.glob(os.path.join(HERE, 'patches', 'p*.py'))):
        spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        js = mod.apply(js, rep, resub, replace_function)
    head = open(os.path.join(HERE, 'shell.html'), encoding='utf-8').read()
    for path in sorted(glob.glob(os.path.join(HERE, 'patches', 'h*.py'))):
        spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        head = mod.apply(head, rep, resub)
    subprocess.run([sys.executable, os.path.join(HERE, 'build_db.py'), DB], check=True, stdout=subprocess.DEVNULL)
    db = open(DB, encoding='utf-8').read()
    html = head + '<script id="database" type="application/json">' + db + '</script><script>\n' + js
    open(OUT, 'w', encoding='utf-8').write(html)
    print('wrote', OUT, len(html))

if __name__ == '__main__':
    try:
        main()
    except PatchError as e:
        print('PATCH FAILED:', e)
        sys.exit(1)
