"""Этап 4. Пакет для чата: handoff/ и handoff.zip.

Состав: README.md (из scripts/handoff-README.md), questions.md, content-model.md, content-map.csv, redirects.csv,
facts.csv, images.csv, vip-room-photos.csv, content/old/*.md, media/sheets/*.jpg.
handoff/ пересоздаётся целиком (в ней только сгенерированное).

Запуск (после stage4_map.py): python -I scripts/stage4_handoff.py
"""
import csv
import datetime
import shutil
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parent.parent
H = ROOT / 'handoff'
INV = ROOT / 'inventory'

if H.exists():
    for p in H.iterdir():
        shutil.rmtree(p) if p.is_dir() else p.unlink()
H.mkdir(exist_ok=True)

files = {
    INV / 'questions.md': 'questions.md',
    ROOT / 'content-model.md': 'content-model.md',
    INV / 'content-map.csv': 'content-map.csv',
    INV / 'redirects.csv': 'redirects.csv',
    INV / 'facts.csv': 'facts.csv',
    INV / 'images.csv': 'images.csv',
    INV / 'vip-room-photos.csv': 'vip-room-photos.csv',
}
for src, dst in files.items():
    shutil.copy2(src, H / dst)
(H / 'content' / 'old').mkdir(parents=True)
for f in sorted((ROOT / 'content' / 'old').glob('*.md')):
    shutil.copy2(f, H / 'content' / 'old' / f.name)
(H / 'media' / 'sheets').mkdir(parents=True)
for f in sorted((ROOT / 'media' / 'sheets').glob('*.jpg')):
    shutil.copy2(f, H / 'media' / 'sheets' / f.name)

n_map = sum(1 for _ in csv.DictReader(open(INV / 'content-map.csv', encoding='utf-8-sig')))
n_red = sum(1 for _ in csv.DictReader(open(INV / 'redirects.csv', encoding='utf-8-sig')))
n_sh = len(list((H / 'media' / 'sheets').glob('*.jpg')))
readme = (ROOT / 'scripts' / 'handoff-README.md').read_text(encoding='utf-8')
readme = (readme.replace('{{date}}', datetime.date.today().isoformat()).replace('{{map_rows}}', str(n_map))
          .replace('{{redirects}}', str(n_red)).replace('{{sheets}}', str(n_sh)))
(H / 'README.md').write_text(readme, encoding='utf-8')

zp = ROOT / 'handoff.zip'
if zp.exists():
    zp.unlink()
with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for p in sorted(H.rglob('*')):
        if p.is_file():
            z.write(p, p.relative_to(H).as_posix())
cnt = sum(1 for p in H.rglob('*') if p.is_file())
print(f'handoff/: {cnt} файлов, {sum(p.stat().st_size for p in H.rglob("*") if p.is_file()) / 1048576:.1f} МБ; handoff.zip: {zp.stat().st_size / 1048576:.1f} МБ')
with zipfile.ZipFile(zp) as z:
    print('в архиве:', len(z.namelist()), 'файлов; тест:', z.testzip())
