"""Этап 3: подставить новые имена фото в content/old/*.md вместо заглушки «new: (этап 3)».

Меняется только поле new: в строках картинок, остальной текст не трогается.
Источник имён — inventory/images.csv (после stage3_images.py). Повторный запуск обновляет
уже подставленные имена (если разделы пересчитаны). Перед первой заменой — копия в work/backup/.

Запуск: python -I scripts/fill_new_names.py
"""
import csv
import re
import shutil
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OLD = ROOT / 'content' / 'old'
BACKUP = ROOT / 'work' / 'backup' / 'content-old-before-stage3'
LINE = re.compile(r'^- new: (.*?) \| src: (\S.*?)( \|.*)?$')


def rel_of(url):
    p = urllib.parse.urlsplit(url)
    return urllib.parse.unquote(p.path.lstrip('/'))


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    names = {}
    for r in csv.DictReader(open(ROOT / 'inventory' / 'images.csv', encoding='utf-8-sig')):
        if r['status'] == 'missing_404':
            names[r['source_url']] = '[файл не скачан: 404]'
        elif r['status'] == 'junk_js':
            names[r['source_url']] = '[не картинка: кусок JS]'
        elif r['status'] == 'broken':
            names[rel_of(r['source_url'])] = '[битый файл]'
        else:
            names[r['local_path'].split('media/originals/', 1)[1]] = r['new_name'].split('media/renamed/', 1)[1]
    if not BACKUP.exists():
        shutil.copytree(OLD, BACKUP)
    total = changed = unknown = 0
    for fn in sorted(OLD.glob('*.md')):
        lines = fn.read_text(encoding='utf-8').split('\n')
        dirty = False
        for i, line in enumerate(lines):
            m = LINE.match(line)
            if not m:
                continue
            total += 1
            src = m.group(2)
            new = names.get(src) or names.get(rel_of(src))
            if not new:
                unknown += 1
                print('нет в images.csv:', fn.name, src)
                continue
            nl = f'- new: {new} | src: {src}{m.group(3) or ""}'
            if nl != line:
                lines[i], dirty = nl, True
                changed += 1
        if dirty:
            fn.write_text('\n'.join(lines), encoding='utf-8')
    print(f'строк картинок: {total}; изменено: {changed}; без имени: {unknown}; копия до замены: {BACKUP.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
