"""Дописка в inventory/facts.csv фактов, которые не поймали регулярки extract.py.

Что ищется (в content/old/*.md, текст секций, без картинок и таблиц):
  - «N видов» (например, «Объем лечебных процедур более 70 видов»): в FACT_RX
    extract.py нет единицы «вид»;
  - рейтинг блока отзывов «4.9 (653 отзыва)» (otzivs/show_otzivs.js на главной):
    число и количество отзывов стоят в разных строках, регулярки их не берут.

Строки в формате facts.csv: тип, секция, что (контекст), значение, страница, якорь, slug.
Повторный запуск ничего не дублирует. extract.py перезаписывает facts.csv целиком,
поэтому после него этот скрипт нужно запустить снова.

Запуск: python -I scripts/facts_addendum.py [--dry-run]
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OLD = ROOT / 'content' / 'old'
FACTS = ROOT / 'inventory' / 'facts.csv'
PAGES = ROOT / 'inventory' / 'pages.csv'
LEGAL_ANCHORS = {'doczaschitaprav', 'docfreemedicine'}   # как в extract.py

RX_VIDOV = re.compile(r'(?<![\w.,])\d+(?:\s*[-–]\s*\d+)?\s*вид(?:ов|а)\b', re.I)
RX_RATING = re.compile(r'(?<![\w.,])(\d[.,]\d)\s+\((\d+)\s+(отзыв\w*)\)')
HEADER = re.compile(r'^#{2,4}\s+(.*?)(?:\s*\{#([^}]+)\})?\s*$')


def page_urls():
    urls = {}
    for p in csv.DictReader(open(PAGES, encoding='utf-8-sig')):
        path = p['url'].split('kasimovskie-zori.ru/', 1)[1].split('?')[0].split('#')[0]
        slug = 'home' if path in ('', 'index.html') else path[:-5].replace('/', '-')
        urls[slug] = p['url']
    return urls


def sections(md):
    """[(заголовок, якорь, текст)] — текст секции без строк картинок и таблиц."""
    body = md.split('\n---\n', 1)[-1]
    out, title, anchor, buf = [], '', '', []
    for line in body.split('\n'):
        m = HEADER.match(line)
        if m:
            out.append((title, anchor, buf))
            title, anchor, buf = m.group(1).strip(), (m.group(2) or ''), []
            continue
        if line.startswith('- new:') or line.startswith('|') or line.startswith('**Картинки'):
            continue
        buf.append(line)
    out.append((title, anchor, buf))
    return [(t, a, re.sub(r'\]\([^)]*\)', ']', '\n'.join(b))) for t, a, b in out]


def ctx(text, m):
    a, z = max(0, m.start() - 60), min(len(text), m.end() + 60)
    return re.sub(r'\s+', ' ', text[a:z]).replace('**', '').strip()


def find_rows():
    urls = page_urls()
    rows = []
    for fn in sorted(OLD.glob('*.md')):
        slug = fn.stem
        if slug.startswith('_'):
            continue
        url = urls.get(slug, '')
        for title, anchor, text in sections(fn.read_text(encoding='utf-8')):
            if anchor in LEGAL_ANCHORS:
                continue
            flat = re.sub(r'\s+', ' ', text)
            for m in RX_VIDOV.finditer(flat):
                rows.append(['цифра', title, ctx(flat, m), re.sub(r'\s+', ' ', m.group(0)), url, anchor, slug])
            for m in RX_RATING.finditer(flat):
                val = f'{m.group(1)} ({m.group(2)} {m.group(3)})'
                rows.append(['цифра', title, ctx(flat, m), val, url, anchor, slug])
    return rows


def main():
    dry = '--dry-run' in sys.argv
    existing = list(csv.reader(open(FACTS, encoding='utf-8-sig', newline='')))
    seen = {(r[0], r[3], r[4], r[5], r[2]) for r in existing[1:]}   # ключ дедупа как в extract.py
    new = []
    for r in find_rows():
        k = (r[0], r[3], r[4], r[5], r[2])
        if k not in seen:
            seen.add(k)
            new.append(r)
    sys.stdout.reconfigure(encoding='utf-8')
    print(f'facts.csv: {len(existing) - 1} строк; новых: {len(new)}' + (' (dry-run, не записано)' if dry else ''))
    for r in new:
        print(' |', r[6], '|', r[1], '|', r[5] or '-', '|', r[3], '|', r[2])
    if new and not dry:
        raw = FACTS.read_bytes()
        with open(FACTS, 'a', newline='', encoding='utf-8') as fh:
            if raw and not raw.endswith(b'\n'):
                fh.write('\r\n')
            csv.writer(fh).writerows(new)
        print(f'записано, теперь строк: {len(existing) - 1 + len(new)}')


if __name__ == '__main__':
    main()
