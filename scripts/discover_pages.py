"""Ищет в зеркале ссылки на страницы домена, которых ещё нет (в т.ч. в JS/document.write/onclick).
python -I scripts/discover_pages.py [extra_name.html ...]  -> печатает новые URL (по одному в строке)
"""
import re, sys
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / 'raw' / 'site' / 'kasimovskie-zori.ru'
SKIP = {'/virtual.html'}  # robots.txt Disallow
PAT = re.compile(rb'''(?:(?:https?:)?//(?:www\.)?kasimovskie-zori\.ru)?(/?[A-Za-z0-9_\-./]*[A-Za-z0-9_\-]\.(?:html?|php))(?=["'#?\s)<>\\]|$)''')

have = set()
for p in SITE.rglob('*'):
    if p.is_file():
        have.add('/' + p.relative_to(SITE).as_posix())
have.add('/')

found = set()
for p in SITE.rglob('*'):
    if not p.is_file() or p.suffix.lower() not in ('.html', '.htm', '.js', '.css', '.php', '.txt', '.xml', ''):
        continue
    if '/plugins/' in p.as_posix() or p.name.endswith('.min.js'):
        continue
    rel = '/' + p.relative_to(SITE).as_posix()
    data = p.read_bytes()
    for m in PAT.finditer(data):
        s = m.group(1).decode('ascii', 'ignore')
        start = m.start()
        # отбросить чужие домены: перед совпадением не должно быть '//чужой.хост'
        pre = data[max(0, start - 80):start]
        if re.search(rb'//[A-Za-z0-9.-]+$', pre) and not re.search(rb'kasimovskie-zori\.ru$', pre):
            continue
        # html-страницы считаем относительно корня (JS подключается из страниц в корне)
        base = 'https://kasimovskie-zori.ru' + (rel if rel.endswith(('.html', '.htm')) else '/')
        path = urlsplit(urljoin(base, s)).path
        found.add(path)

for name in sys.argv[1:]:
    found.add('/' + name.lstrip('/'))

for path in sorted(found - have - SKIP):
    if '/plugins/' in path or '/newsite/' in path and False:
        continue
    print('https://kasimovskie-zori.ru' + path)
