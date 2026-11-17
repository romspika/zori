"""Этап 3. Фото.

Вход:  raw/site/kasimovskie-zori.ru/ (картинки), content/old/*.md (где используются),
       work/rendered/ (alt/title из DOM после JS), raw/ftp-images/ (оригиналы с хостинга, если есть).
Выход: media/originals/<путь как на сайте>   — копии без изменений
       media/renamed/<раздел>/<раздел>-<nn>.<ext> — по одной копии на группу дублей (основная версия)
       media/sheets/<раздел>[-pNN].jpg      — листы-превью; _duplicates*.jpg — проверка почти-дублей
       inventory/images.csv

Раздел: предварительный slug новой страницы/блока (SECTION_* ниже) — карта контента будет на этапе 4,
после неё скрипт можно перезапустить (renamed/ и sheets/ пересоздаются целиком).

Запуск: python -I scripts/stage3_images.py [--no-copy]   (--no-copy: только расчёт и сводка, без файлов)
"""
import csv
import hashlib
import json
import math
import os
import re
import shutil
import sys
import urllib.parse
from collections import Counter, defaultdict
from pathlib import Path

import imagehash
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont, ImageOps

Image.MAX_IMAGE_PIXELS = None
ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / 'raw' / 'site' / 'kasimovskie-zori.ru'
FTP = ROOT / 'raw' / 'ftp-images'
OLD = ROOT / 'content' / 'old'
REND = ROOT / 'work' / 'rendered'
INV = ROOT / 'inventory'
MEDIA = ROOT / 'media'
CACHE = ROOT / 'work' / 'stage3_meta.json'
BASE = 'https://kasimovskie-zori.ru/'

IMG_EXT = {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico', '.bmp'}
LOW_RES = 1200      # длинная сторона меньше — low_res
ICON_MAX = 200      # длинная сторона меньше — icon
PHASH_MAX, DHASH_MAX, AR_TOL = 4, 6, 0.10   # почти-дубли: оба хэша близки и пропорции почти равны

# ---------- разделы (сверены с картой контента этапа 4; slug раздела = slug новой страницы/блока) ----------
PAGE_SECTION = {
    'home': 'glavnaya',
    'programms_treatment': 'programmy',
    'programms_meduslugi': 'procedury',
    'programms_izuminki': 'procedury',
    'programms_equipment': 'oborudovanie',
    'programms_medkabinets': 'medkabinety',
    'programms_all': 'lechenie',
    'nomera': 'nomera', 'live_in_hotel': 'nomera', 'live_in_hotel-embed': 'nomera',
    'live_in_hotel_newyear': 'nomera', 'pricehotel-newyear-embed': 'nomera',
    'live_in_corpus1': 'korpus-1',
    'live_in_corpus2': 'vip-korpus',
    'live_in_cottegues': 'kottedzhi', 'live_in_cottegues_newyear': 'kottedzhi',
    'rooms': 'prozhivanie',
    'dopuslugi': 'semyam', 'dopuslugi-embed': 'semyam',
    'news': 'novosti',
    'documents': 'dokumenty',
    'contact': 'kontakty',
    'questions': 'voprosy',
    'booking': 'bronirovanie',
    '_common': 'obshchee',
}
# (slug, подстрока заголовка или #якорь) -> раздел; проверяются по порядку
SECTION_OVERRIDES = [
    ('home', '#lechprogs', 'programmy'),
    ('home', 'Основные медицинские услуги', 'procedury'),
    ('home', '#actionactions', 'akcii'),
    ('home', 'Наши лицензии', 'dokumenty'),
    ('home', 'блок отзывов', 'otzyvy'),
    ('home', 'Номер Люкс', 'nomera'),
    ('home', 'Проживание', 'prozhivanie'),
    ('home', 'Спортзал и бассейн', 'semyam'),
    ('programms_izuminki', '#soltcave', 'spa'),          # в прототипе соляная пещера — блок СПА
    ('rooms', 'Дополнительные услуги', 'semyam'),
    ('_js-data', '`akcias`', 'akcii'),
    ('_js-data', '`otziv`', 'otzyvy'),
    ('*', 'Санаторий «Касимовские Зори»', 'prozhivanie'),  # нижний блок-ссылки «коттеджи / гостиница / ВИП»
    ('*', '[вводная часть без заголовка]', 'obshchee'),
]
# по папке файла — сильнее страницы (папка однозначно говорит, что на фото)
PATH_SECTION = [
    ('images/programms/izuminki-003', 'procedury'),      # фото ВЛОК (лежит в секции «Соляная пещера» из-за зигзаг-вёрстки)
    ('otzivs/', 'otzyvy'), ('images/afisha/', 'afisha'), ('images/akcia/', 'akcii'),
    ('images/licenzias/', 'dokumenty'), ('images/cottagues/', 'kottedzhi'), ('images/rooms2020/', 'nomera'),
    ('images/med/', 'medkabinety'), ('corpus2/', 'vip-korpus'), ('news/', 'novosti'), ('doc/', 'dokumenty'),
    ('images/social/', 'obshchee'), ('plugins/', 'obshchee'),
    ('images/mramor/', 'obshchee'),                      # мраморные фоны блоков — декор
]
# если фото в нескольких местах — берётся самый конкретный раздел
PRIORITY = ['vip-korpus', 'korpus-1', 'kottedzhi', 'nomera', 'medkabinety', 'oborudovanie', 'spa', 'procedury',
            'programmy', 'semyam', 'akcii', 'afisha', 'otzyvy', 'dokumenty', 'kontakty', 'prozhivanie', 'lechenie',
            'voprosy', 'bronirovanie', 'glavnaya', 'novosti', 'obshchee']


def section_for(slug, title, anchor, rel):
    for p, sec in PATH_SECTION:
        if rel and rel.startswith(p):
            return sec
    for s, key, sec in SECTION_OVERRIDES:
        if s in (slug, '*') and ((key.startswith('#') and anchor == key[1:]) or (not key.startswith('#') and key in title)):
            return sec
    return PAGE_SECTION.get(slug, slug.replace('_', '-'))


# ---------- источники ----------

def page_slugs():
    out = []
    for p in csv.DictReader(open(INV / 'pages.csv', encoding='utf-8-sig')):
        path = p['url'].split('kasimovskie-zori.ru/', 1)[1].split('?')[0].split('#')[0]
        out.append(('home' if path in ('', 'index.html') else path[:-5].replace('/', '-'), p['url'], path or 'index.html'))
    return out


def list_images():
    files = []
    for dp, dn, fn in os.walk(SITE):
        if 'fonts' in Path(dp).parts:
            continue
        for f in fn:
            if Path(f).suffix.lower() in IMG_EXT:
                files.append(Path(dp, f).relative_to(SITE).as_posix())
    return sorted(files)


def url_to_rel(u):
    p = urllib.parse.urlsplit(u)
    if p.netloc and p.netloc != 'kasimovskie-zori.ru':
        return None
    return urllib.parse.unquote(p.path.lstrip('/'))


LINE_RX = re.compile(r'^- new: .*?\| src: (\S.*?)(?: \| alt: "(.*?)")?(?: \| via: ([^|]+?))?(?: \| link: (.*))?$')
HEAD_RX = re.compile(r'^#{2,4}\s+(.*?)(?:\s*\{#([^}]+)\})?\s*$')


def md_usages(order):
    """[(url, slug, title, anchor, alt, via, order_key)] из content/old в порядке страниц."""
    out = []
    for pi, slug in enumerate(order):
        fn = OLD / f'{slug}.md'
        if not fn.exists():
            continue
        title = anchor = ''
        for ln, line in enumerate(fn.read_text(encoding='utf-8').split('\n')):
            m = HEAD_RX.match(line)
            if m:
                title, anchor = m.group(1).strip(), m.group(2) or ''
                continue
            if line.startswith('- new:'):
                m = LINE_RX.match(line)
                if m:
                    out.append((m.group(1).strip(), slug, title, anchor, m.group(2) or '', (m.group(3) or '').strip(), (pi, ln)))
    return out


def raw_usages(missing_rels, pages):
    """Картинки, которых нет в .md: ищем имя файла в HTML/CSS/JS зеркала и привязываем к страницам."""
    texts = {}
    for dp, dn, fn in os.walk(SITE):
        if 'fonts' in Path(dp).parts:
            continue
        for f in fn:
            if Path(f).suffix.lower() in ('.html', '.css', '.js'):
                rel = Path(dp, f).relative_to(SITE).as_posix()
                texts[rel] = Path(dp, f).read_bytes().decode('cp1251', errors='replace')
    # какие css/js подключает каждая страница
    res_pages = defaultdict(list)
    for slug, url, path in pages:
        html = texts.get(path, '')
        base = path.rsplit('/', 1)[0] + '/' if '/' in path else ''
        for ref in re.findall(r'(?:href|src)\s*=\s*["\']([^"\'#?]+\.(?:css|js))', html, re.I):
            r = ref if ref.startswith('/') else base + ref
            res_pages[os.path.normpath(r.lstrip('/')).replace('\\', '/')].append(slug)
    page_of = {path: slug for slug, url, path in pages}
    out = defaultdict(list)
    for rel in missing_rels:
        name = rel.rsplit('/', 1)[-1]
        for trel, t in texts.items():
            if name not in t or not re.search(r'(?<![\w-])' + re.escape(name), t):
                continue
            kind = trel.rsplit('.', 1)[-1]
            if kind == 'html':
                if trel in page_of:
                    out[rel].append((page_of[trel], f'[в HTML страницы, не видно после рендера]', '', kind))
            else:
                for slug in res_pages.get(trel, []):
                    out[rel].append((slug, f'[фон/слайдер из {trel}]', '', kind))
    return out


def dom_titles():
    """alt/title картинок из отрендеренного DOM: rel -> (alts, titles)."""
    alts, titles = defaultdict(set), defaultdict(set)
    for fn in REND.rglob('*.html'):
        page_rel = fn.relative_to(REND).as_posix()
        page_url = BASE + page_rel
        soup = BeautifulSoup(fn.read_text(encoding='utf-8', errors='replace'), 'lxml')
        for img in soup.find_all('img', src=True):
            rel = url_to_rel(urllib.parse.urljoin(page_url, img['src'].strip()))
            if not rel:
                continue
            if img.get('alt', '').strip():
                alts[rel].add(img['alt'].strip())
            t = img.get('title', '').strip() or (img.parent.get('title', '').strip() if img.parent and img.parent.name == 'a' else '')
            if t:
                titles[rel].add(t)
    return alts, titles


# ---------- метаданные ----------

def svg_size(p):
    t = p.read_text(encoding='utf-8', errors='replace')[:3000]
    w = re.search(r'<svg[^>]*\swidth="([\d.]+)', t)
    h = re.search(r'<svg[^>]*\sheight="([\d.]+)', t)
    if w and h:
        return int(float(w.group(1))), int(float(h.group(1)))
    vb = re.search(r'viewBox="[\d.\-]+[ ,]+[\d.\-]+[ ,]+([\d.]+)[ ,]+([\d.]+)', t)
    return (int(float(vb.group(1))), int(float(vb.group(2)))) if vb else (0, 0)


def flat_rgb(im):
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA')
        bg = Image.new('RGB', im.size, 'white')
        bg.paste(im, mask=im.split()[-1])
        return bg
    return im.convert('RGB')


def meta_for(p, cache):
    st = p.stat()
    key = p.relative_to(ROOT).as_posix()
    c = cache.get(key)
    if c and c['bytes'] == st.st_size and c['mtime'] == int(st.st_mtime):
        return c
    data = p.read_bytes()
    m = {'bytes': st.st_size, 'mtime': int(st.st_mtime), 'sha1': hashlib.sha1(data).hexdigest(),
         'w': 0, 'h': 0, 'format': p.suffix.lower().lstrip('.'), 'alpha': False, 'phash': '', 'dhash': '', 'error': ''}
    if p.suffix.lower() == '.svg':
        m['w'], m['h'] = svg_size(p)
        m['format'] = 'svg'
    else:
        try:
            with Image.open(p) as im:
                m['format'] = (im.format or m['format']).lower()
                im.seek(0)
                im = ImageOps.exif_transpose(im)
                m['w'], m['h'] = im.size
                m['alpha'] = im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info)
                rgb = flat_rgb(im)
                m['phash'], m['dhash'] = str(imagehash.phash(rgb)), str(imagehash.dhash(rgb))
        except Exception as e:      # битый файл (например, HTML-страница 404 под именем .jpg)
            m['error'] = f'{type(e).__name__}: {e}'[:120]
            if data[:200].lstrip().lower().startswith((b'<!doctype', b'<html')):
                m['error'] = 'не картинка: HTML (вероятно, страница ошибки)'
    cache[key] = m
    return m


class DSU:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a != b:
            self.p[max(a, b)] = min(a, b)


# ---------- листы-превью ----------

def font(sz):
    for f in ('arial.ttf', 'C:/Windows/Fonts/arial.ttf', 'DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(f, sz)
        except OSError:
            pass
    return ImageFont.load_default()


TW, TH, COLS, PER_SHEET = 240, 180, 6, 48


def thumb(path):
    if path.suffix.lower() == '.svg':
        return None
    try:
        with Image.open(path) as im:
            im.seek(0)
            im = flat_rgb(ImageOps.exif_transpose(im))
            im.thumbnail((TW, TH))
            return im
    except Exception:
        return None


def draw_sheet(items, title, out):
    """items: [(path, line1, line2, mark)]"""
    f1, f2, ft = font(14), font(12), font(18)
    cw, ch = TW + 16, TH + 48
    rows = math.ceil(len(items) / COLS)
    sheet = Image.new('RGB', (COLS * cw + 16, rows * ch + 56), 'white')
    d = ImageDraw.Draw(sheet)
    d.text((16, 14), title, fill='black', font=ft)
    for i, (path, l1, l2, mark) in enumerate(items):
        x, y = 16 + (i % COLS) * cw, 48 + (i // COLS) * ch
        d.rectangle([x - 1, y - 1, x + TW, y + TH], outline='#cccccc')
        t = thumb(path)
        if t:
            sheet.paste(t, (x + (TW - t.width) // 2, y + (TH - t.height) // 2))
        else:
            d.text((x + 8, y + TH // 2 - 8), path.suffix.upper().lstrip('.') or '?', fill='#888888', font=f1)
        d.text((x, y + TH + 4), l1, fill='black', font=f1)
        d.text((x, y + TH + 22), l2, fill='#c00000' if mark else '#555555', font=f2)
    sheet.save(out, quality=82)


def make_sheets(section_items, dup_rows):
    out_dir = MEDIA / 'sheets'
    made = []
    for sec, items in sorted(section_items.items()):
        pages = math.ceil(len(items) / PER_SHEET)
        for k in range(pages):
            chunk = items[k * PER_SHEET:(k + 1) * PER_SHEET]
            name = f'{sec}.jpg' if pages == 1 else f'{sec}-p{k + 1:02d}.jpg'
            draw_sheet(chunk, f'{sec}  —  {len(items)} фото' + (f', лист {k + 1}/{pages}' if pages > 1 else ''), out_dir / name)
            made.append(name)
    # проверка почти-дублей: группа = подряд, основная версия первой
    if dup_rows:
        per = PER_SHEET
        pages = math.ceil(len(dup_rows) / per)
        for k in range(pages):
            name = '_duplicates.jpg' if pages == 1 else f'_duplicates-p{k + 1:02d}.jpg'
            draw_sheet(dup_rows[k * per:(k + 1) * per], f'Почти-дубли (perceptual hash), основная — первая в группе; лист {k + 1}/{pages}', out_dir / name)
            made.append(name)
    return made


# ---------- main ----------

def main():
    no_copy = '--no-copy' in sys.argv
    sys.stdout.reconfigure(encoding='utf-8')
    pages = page_slugs()
    order = [s for s, _, _ in pages] + ['_common', '_js-data']
    files = list_images()
    cache = json.loads(CACHE.read_text(encoding='utf-8')) if CACHE.exists() else {}

    # использование
    uses = defaultdict(list)            # rel -> [(slug, title, anchor, alt, via, order)]
    missing = {}                        # url -> (status, uses)
    for url, slug, title, anchor, alt, via, ok in md_usages(order):
        rel = url_to_rel(url)
        if rel in set(files):
            uses[rel].append((slug, title, anchor, alt, via or 'img', ok))
        else:
            st = 'junk_js' if '+' in url or '[' in url else 'missing_404'
            missing.setdefault(url, (st, []))[1].append((slug, title, anchor, alt, via or 'img', ok))
    no_md = [r for r in files if r not in uses]
    raw = raw_usages(no_md, pages)
    big = (len(order) + 1, 0)
    for rel, lst in raw.items():
        for slug, title, alt, via in lst:
            uses[rel].append((slug, title, '', alt, via, (order.index(slug) if slug in order else big[0], 10 ** 6)))
    dom_alts, dom_tit = dom_titles()

    # метаданные
    meta = {}
    for i, rel in enumerate(files):
        meta[rel] = meta_for(SITE / rel, cache)
        if i % 200 == 0:
            print(f'  метаданные {i}/{len(files)}', flush=True)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding='utf-8')

    # оригиналы с хостинга (если появятся): по имени и хэшу, берём более крупную версию
    ftp_better = {}
    if FTP.exists():
        ftp_files = [p for p in FTP.rglob('*') if p.is_file() and p.suffix.lower() in IMG_EXT]
        by_name = defaultdict(list)
        for p in ftp_files:
            by_name[p.name.lower()].append(p)
        for rel in files:
            for p in by_name.get(rel.rsplit('/', 1)[-1].lower(), []):
                fm = meta_for(p, cache)
                same = fm['sha1'] == meta[rel]['sha1'] or (fm['phash'] and meta[rel]['phash'] and
                       imagehash.hex_to_hash(fm['phash']) - imagehash.hex_to_hash(meta[rel]['phash']) <= PHASH_MAX)
                if same and fm['w'] * fm['h'] > meta[rel]['w'] * meta[rel]['h']:
                    ftp_better[rel] = (p, fm)
        CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding='utf-8')

    # флаги
    def flags(rel):
        m = meta[rel]
        fl = []
        if m['error']:
            fl.append('broken')
            return fl
        long = max(m['w'], m['h'])
        if m['format'] in ('svg', 'ico', 'gif') or long < ICON_MAX:
            fl.append('icon')
        elif m['format'] == 'png' and m['alpha'] and long < 600:
            fl.append('icon')                              # png-пиктограммы с прозрачностью
        if m['format'] != 'svg' and long < LOW_RES and 'icon' not in fl:
            fl.append('low_res')
        if not uses.get(rel):
            fl.append('unused')
        return fl
    fl = {r: flags(r) for r in files}

    # дубли
    idx = {r: i for i, r in enumerate(files)}
    dsu = DSU(len(files))
    by_sha = defaultdict(list)
    for r in files:
        by_sha[meta[r]['sha1']].append(r)
    for lst in by_sha.values():
        for r in lst[1:]:
            dsu.union(idx[lst[0]], idx[r])
    cand = [r for r in files if meta[r]['phash'] and 'icon' not in fl[r] and 'broken' not in fl[r]]
    ph = {r: int(meta[r]['phash'], 16) for r in cand}
    dh = {r: int(meta[r]['dhash'], 16) for r in cand}
    ar = {r: meta[r]['w'] / meta[r]['h'] for r in cand}
    near_pairs = 0
    for i, a in enumerate(cand):
        for b in cand[i + 1:]:
            if bin(ph[a] ^ ph[b]).count('1') <= PHASH_MAX and bin(dh[a] ^ dh[b]).count('1') <= DHASH_MAX \
                    and abs(ar[a] - ar[b]) / max(ar[a], ar[b]) <= AR_TOL:
                if dsu.find(idx[a]) != dsu.find(idx[b]):
                    near_pairs += 1
                dsu.union(idx[a], idx[b])
    groups = defaultdict(list)
    for r in files:
        groups[dsu.find(idx[r])].append(r)

    def area(r):
        b = ftp_better.get(r)
        m = b[1] if b else meta[r]
        return (m['w'] * m['h'], m['bytes'])

    rows, gid_of, primary_of, kind_of = {}, {}, {}, {}
    gnum = 0
    for root_i, members in sorted(groups.items()):
        prim = max(members, key=lambda r: (area(r), -files.index(r)))
        if len(members) > 1:
            gnum += 1
            g = f'g{gnum:04d}'
            exact = len({meta[r]['sha1'] for r in members}) == 1
        else:
            g, exact = '', True
        for r in members:
            gid_of[r], primary_of[r] = g, prim
            kind_of[r] = '' if not g else ('exact' if exact else ('exact' if meta[r]['sha1'] == meta[prim]['sha1'] else 'near'))
            if g and not exact:
                kind_of[r] = 'near'

    # раздел группы и порядок
    def best_section(members):
        secs, first = [], None
        for r in members:
            for slug, title, anchor, alt, via, ok in uses.get(r, []):
                secs.append(section_for(slug, title, anchor, r))
                first = ok if first is None or ok < first else first
        if any('icon' in fl[r] for r in members) and all('icon' in fl[r] for r in members):
            return '_icons', first
        if not secs:
            secs = [section_for('', '', '', members[0])] if any(members[0].startswith(p) for p, _ in PATH_SECTION) else ['_unused']
        return min(secs, key=lambda s: PRIORITY.index(s) if s in PRIORITY else len(PRIORITY)), first

    sec_members = defaultdict(list)
    for root_i, members in groups.items():
        prim = primary_of[members[0]]
        if 'broken' in fl[prim]:
            continue
        sec, first = best_section(members)
        sec_members[sec].append((first if first is not None else (10 ** 6, 10 ** 6), prim, members))
    new_name = {}
    for sec, lst in sec_members.items():
        lst.sort(key=lambda x: (x[0], x[1]))
        width = max(2, len(str(len(lst))))
        for n, (first, prim, members) in enumerate(lst, 1):
            src = ftp_better.get(prim, (SITE / prim, meta[prim]))[1]
            ext = 'jpg' if src['format'] in ('jpeg', 'jpg', 'mpo') else src['format']
            nm = f'{sec}/{sec}-{n:0{width}d}.{ext}'
            for r in members:
                new_name[r] = nm

    # сводка
    c = Counter()
    for r in files:
        for f in fl[r]:
            c[f] += 1
    multi = [g for g in groups.values() if len(g) > 1]
    print(f'файлов-картинок: {len(files)}; используются в .md: {len(files) - len(no_md)}; найдено в HTML/CSS/JS: {len(raw)}; нигде: {c["unused"]}')
    print(f'не скачаны (404) / мусор из JS: {sum(1 for v in missing.values() if v[0] == "missing_404")} / {sum(1 for v in missing.values() if v[0] == "junk_js")}')
    print(f'флаги: {dict(c)}')
    print(f'группы дублей: {len(multi)} (в них файлов {sum(len(g) for g in multi)}); почти-дублей добавлено связей: {near_pairs}; '
          f'уникальных фото: {len(groups)}; с ftp лучше: {len(ftp_better)}')
    print('разделы:', ', '.join(f'{s}={len(v)}' for s, v in sorted(sec_members.items(), key=lambda x: -len(x[1]))))
    if no_copy:
        return

    # копии
    orig_dir, ren_dir, sh_dir = MEDIA / 'originals', MEDIA / 'renamed', MEDIA / 'sheets'
    for d in (ren_dir, sh_dir):                      # пересоздаются целиком: чистим содержимое, папку оставляем
        d.mkdir(parents=True, exist_ok=True)
        for x in d.iterdir():
            shutil.rmtree(x) if x.is_dir() else x.unlink()
    for r in files:
        dst = orig_dir / r
        if not dst.exists() or dst.stat().st_size != meta[r]['bytes']:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SITE / r, dst)
    done = set()
    for r in files:
        if r in new_name and primary_of[r] == r and new_name[r] not in done:
            src = ftp_better[r][0] if r in ftp_better else orig_dir / r
            dst = ren_dir / new_name[r]
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            done.add(new_name[r])

    # images.csv
    def uses_str(r_uses):
        pages_ = list(dict.fromkeys(u[0] for u in r_uses))
        secs = list(dict.fromkeys(f'{u[0]}{"#" + u[2] if u[2] else ""}: {u[1]}' for u in r_uses))
        alts = list(dict.fromkeys(u[3] for u in r_uses if u[3]))
        vias = list(dict.fromkeys(u[4] for u in r_uses))
        return '; '.join(pages_), ' || '.join(secs), alts, '; '.join(vias)

    cols = ['source_url', 'local_path', 'status', 'section', 'new_name', 'is_primary', 'dup_group', 'dup_kind', 'primary_url',
            'flags', 'width', 'height', 'bytes', 'format', 'pages', 'sections', 'alt', 'title', 'used_via', 'sha1', 'phash', 'ftp_source', 'note']
    out = []
    for r in files:
        m = meta[r]
        p_, s_, alts, via = uses_str(uses.get(r, []))
        alts = list(dict.fromkeys(alts + sorted(dom_alts.get(r, []))))
        out.append({
            'source_url': BASE + urllib.parse.quote(r), 'local_path': f'media/originals/{r}',
            'status': 'broken' if m['error'] else 'ok', 'section': new_name.get(r, '/').split('/')[0] if r in new_name else '',
            'new_name': f'media/renamed/{new_name[r]}' if r in new_name else '',
            'is_primary': 'yes' if primary_of[r] == r else 'no', 'dup_group': gid_of[r], 'dup_kind': kind_of[r],
            'primary_url': '' if primary_of[r] == r else BASE + urllib.parse.quote(primary_of[r]),
            'flags': ';'.join(fl[r]), 'width': m['w'], 'height': m['h'], 'bytes': m['bytes'], 'format': m['format'],
            'pages': p_, 'sections': s_, 'alt': ' | '.join(alts), 'title': ' | '.join(sorted(dom_tit.get(r, []))),
            'used_via': via, 'sha1': m['sha1'], 'phash': m['phash'],
            'ftp_source': ftp_better[r][0].relative_to(ROOT).as_posix() if r in ftp_better else '', 'note': m['error'],
        })
    for url, (st, us) in missing.items():
        p_, s_, alts, via = uses_str(us)
        out.append({k: '' for k in cols} | {'source_url': url, 'status': st, 'pages': p_, 'sections': s_, 'alt': ' | '.join(alts),
                    'used_via': via, 'flags': 'missing',
                    'note': 'ссылка есть, файл не скачан (404, см. broken-links.csv)' if st == 'missing_404' else 'не картинка: кусок JS-шаблона'})
    with open(INV / 'images.csv', 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(out)

    # листы-превью
    section_items = defaultdict(list)
    for sec, lst in sec_members.items():
        for first, prim, members in lst:
            nm = new_name[prim]
            m = ftp_better.get(prim, (None, meta[prim]))[1]
            f = [x for x in fl[prim] if x in ('low_res', 'unused')]
            l2 = f'{m["w"]}×{m["h"]} · {m["bytes"] // 1024} KB' + (f' · {" ".join(f)}' if f else '') + (f' · ×{len(members)}' if len(members) > 1 else '')
            section_items[sec].append((ren_dir / nm, nm.split('/')[1], l2, bool(f)))
    dup_items = []
    for members in multi:
        if all(kind_of[r] == 'exact' for r in members) or primary_of[members[0]] not in new_name:
            continue
        prim = primary_of[members[0]]
        for r in [prim] + [x for x in members if x != prim]:
            m = meta[r]
            dup_items.append((SITE / r, r[-30:], f'{m["w"]}×{m["h"]} · {gid_of[r]}' + (' · основная' if r == prim else ''), r == prim))
    made = make_sheets(section_items, dup_items)
    print(f'originals: {len(files)}; renamed: {len(done)}; листов-превью: {len(made)}; images.csv: {len(out)} строк')


if __name__ == '__main__':
    main()
