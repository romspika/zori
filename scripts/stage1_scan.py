"""Этап 1: разбор зеркала raw/site.

python -I scripts/stage1_scan.py            # только отчёт
python -I scripts/stage1_scan.py --fetch    # + докачать недостающие ресурсы и документы

Выход:
  inventory/logs/urlmap.csv     url -> локальный файл, HTTP-статус (из лога wget2 и докачки)
  inventory/logs/missing.txt    ресурсы домена, на которые есть ссылки, но файла нет
  inventory/embeds.csv          внешние встраивания (iframe, виджеты, карты, видео) — не качаем
  inventory/documents.csv       документы (pdf/doc/xls...) и их статус
  inventory/pages.csv           url, status, title, h1, meta description, words, images, embeds
"""
import csv, re, sys, time, os
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit, unquote
from bs4 import BeautifulSoup
import requests

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / 'raw' / 'site'
INV = ROOT / 'inventory'
LOG = INV / 'logs'
HOSTS = {'kasimovskie-zori.ru', 'www.kasimovskie-zori.ru'}
BASE = 'https://kasimovskie-zori.ru/'
UA = 'Mozilla/5.0 (compatible; KZ-site-migration/1.0)'
DOC_EXT = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.rtf', '.odt', '.ppt', '.pptx', '.zip', '.rar', '.txt'}
IMG_EXT = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.ico', '.avif'}
ASSET_EXT = IMG_EXT | DOC_EXT | {'.css', '.js', '.woff', '.woff2', '.ttf', '.eot', '.otf', '.mp4', '.webm', '.mp3'}
EMBED_HINT = re.compile(r'youtube|youtu\.be|vimeo|rutube|vk\.com/video|yandex\.ru/map|api-maps|maps\.google|google\.com/maps|'
                        r'travelline|bnovo|tl-|realtycalendar|kuula|panoram|3dvista|matterport|tour|widget|jivo|'
                        r'mc\.yandex|metrika|googletagmanager|bitrix24|calltouch|roistat', re.I)
_EXTS = '|'.join(e[1:] for e in sorted(IMG_EXT | DOC_EXT))
URL_IN_TEXT = re.compile(r'''["'(]\s*((?:(?:https?:)?//[^"'()\s<>]+/)?[A-Za-z0-9_\-./%~]*\.(?:EXTS)(?:\?[^"'()\s<>]*)?)\s*["')]'''.replace('EXTS', _EXTS), re.I)
CSS_URL = re.compile(r'url\(\s*["\']?([^"\')]+)["\']?\s*\)', re.I)


def norm(u):
    s = urlsplit(u)
    host = (s.hostname or '').lower()
    if host.startswith('www.'):
        host = host[4:]
    return urlunsplit(('https', host, s.path or '/', s.query, ''))


def is_ours(u):
    return (urlsplit(u).hostname or '').lower() in HOSTS


def parse_wget_log():
    """url -> (local, status) из лога wget2."""
    m = {}
    cur = None
    for line in (LOG / 'wget.log').read_text(encoding='utf-8', errors='replace').splitlines():
        a = re.match(r"\[\d+\] Downloading '(.+)' \.\.\.", line)
        if a:
            cur = norm(a.group(1)); m.setdefault(cur, ['', '']); continue
        b = re.match(r"Saving '(.+)'", line)
        if b and cur:
            m[cur][0] = b.group(1); continue
        c = re.match(r'HTTP (?:ERROR )?response (\d+)\s.*\[(.+)\]', line)
        if c:
            m.setdefault(norm(c.group(2)), ['', ''])[1] = c.group(1)
    return m


def load_urlmap():
    m = {k: list(v) for k, v in parse_wget_log().items()}
    extra = LOG / 'fetched.csv'
    if extra.exists():
        for r in csv.DictReader(extra.open(encoding='utf-8')):
            m[r['url']] = [r['local'], r['status']]
    return m


def local_for(url):
    s = urlsplit(url)
    p = unquote(s.path)
    if p.endswith('/'):
        p += 'index.html'
    name = p.lstrip('/')
    if s.query:
        name += '@' + s.query
    name = re.sub(r'[<>:"|*?\\]', '_', name)
    return 'kasimovskie-zori.ru/' + name


def refs_from_html(path, page_url):
    """Все ссылки страницы: (url, kind, context)."""
    soup = BeautifulSoup(path.read_bytes(), 'lxml')
    out = []
    def add(u, kind, ctx=''):
        u = (u or '').strip()
        if not u or u.startswith(('#', 'mailto:', 'tel:', 'javascript:', 'data:', 'whatsapp:', 'viber:', 'skype:')):
            return
        out.append((urljoin(page_url, u), kind, ctx))
    for t in soup.find_all(True):
        for attr, val in t.attrs.items():
            if isinstance(val, list):
                val = ' '.join(val)
            if attr in ('href', 'src', 'poster', 'action') or attr.startswith('data-') and re.search(r'\.\w{2,4}($|\?)', val or ''):
                add(val, f'{t.name}@{attr}')
            elif attr == 'srcset':
                for part in val.split(','):
                    add(part.strip().split(' ')[0], f'{t.name}@srcset')
            elif attr == 'style':
                for u in CSS_URL.findall(val):
                    add(u, 'inline-style')
    for st in soup.find_all('style'):
        for u in CSS_URL.findall(st.get_text()):
            add(u, 'style-tag')
    for sc in soup.find_all('script'):
        if not sc.get('src'):
            for u in URL_IN_TEXT.findall(sc.get_text()):
                add(u, 'inline-js')
    return soup, out


def main(fetch=False):
    urlmap = load_urlmap()
    by_local = {v[0].replace('\\', '/'): k for k, v in urlmap.items() if v[0]}
    files = [p for p in (SITE / 'kasimovskie-zori.ru').rglob('*') if p.is_file()]  # только наш домен
    html_files = [p for p in files if p.suffix.lower() in ('.html', '.htm', '.php') or '@' in p.name and p.suffix == '']

    refs = []           # (src_url, target, kind)
    embeds = []
    pages = {}
    for p in html_files:
        rel = p.relative_to(SITE).as_posix()
        page_url = by_local.get(rel) or norm('https://' + rel)
        try:
            soup, out = refs_from_html(p, page_url)
        except Exception as e:
            print('ERR', rel, e); continue
        pages[page_url] = (p, soup, out)
        for u, kind, _ in out:
            refs.append((page_url, u, kind))
    # CSS и JS файлы домена
    for p in files:
        if p.suffix.lower() == '.js' and ('/plugins/' in p.as_posix() or p.name.endswith('.min.js')):
            continue  # библиотеки: их внутренние строки — не контент
        if p.suffix.lower() in ('.css', '.js'):
            rel = p.relative_to(SITE).as_posix()
            src = by_local.get(rel) or norm('https://' + rel)
            txt = p.read_text(encoding='utf-8', errors='replace')
            if p.suffix.lower() == '.js':
                for u in re.findall(r'''(?:https?:)?//[A-Za-z0-9.-]+\.[a-z]{2,}[^"'\s<>)\\]*''', txt):
                    if not is_ours(urljoin(BASE, u)) and (EMBED_HINT.search(u) or 'iframe' in txt):
                        embeds.append((src, urljoin(BASE, u), 'js-string'))
            found = CSS_URL.findall(txt) if p.suffix.lower() == '.css' else URL_IN_TEXT.findall(txt)
            for u in found:
                if u.startswith('data:'):
                    continue
                # url() в CSS — относительно CSS-файла; строки в JS — относительно страницы (корня сайта)
                if p.suffix.lower() == '.css':
                    refs.append((src, urljoin(src, u.strip()), 'css'))
                else:
                    a, b = urljoin(BASE, u.strip()), urljoin(src, u.strip())
                    refs.append((src, a, 'js' if a == b else 'js-alt ' + norm(b)))
                    if a != b:
                        refs.append((src, b, 'js-alt ' + norm(a)))

    # недостающие ресурсы домена + документы + встраивания
    missing, docs = {}, {}
    for src, u, kind in refs:
        if not u.startswith(('http://', 'https://', '//')):
            continue
        if not is_ours(u):
            if kind.startswith(('iframe', 'embed', 'object', 'script@src', 'video', 'source')) or EMBED_HINT.search(u):
                embeds.append((src, u, kind))
            continue
        n = norm(u)
        ext = os.path.splitext(urlsplit(n).path)[1].lower()
        if ext in DOC_EXT:
            docs.setdefault(n, set()).add(src)
        if ext not in ASSET_EXT and kind.startswith('a@'):
            continue  # страницы — дело wget
        if n in urlmap and urlmap[n][1]:
            continue
        if (SITE / local_for(n)).exists():
            continue
        if kind.startswith('js-alt '):
            other = kind.split(' ', 1)[1]
            if (SITE / local_for(other)).exists() or (urlmap.get(other) or ['', ''])[1] == '200':
                continue
        missing.setdefault(n, set()).add(f'{kind} <- {src}')

    # js-вызовы страниц, которых нет (ссылки a@href на html вне зеркала)
    for src, u, kind in refs:
        if kind == 'a@href' and is_ours(u):
            n = norm(u)
            if n not in urlmap and n not in pages and not (SITE / local_for(n)).exists():
                path = urlsplit(n).path
                if path.endswith(('.html', '/')) or '.' not in path.rsplit('/', 1)[-1]:
                    missing.setdefault(n, set()).add(f'{kind} <- {src}')

    if fetch and missing:
        fetched = []
        sess = requests.Session(); sess.headers['User-Agent'] = UA
        ok = set()
        alt = {}
        for n, v in missing.items():
            for k in v:
                if k.startswith('js-alt '):
                    alt[n] = k.split(' ', 2)[1]
        # сначала варианты от корня сайта, вариант «относительно папки JS» — только если первый не нашёлся
        order = sorted(missing, key=lambda n: ('/js/' in n or n.count('/') > 5, n))
        for n in order:
            if n.split('?')[0].endswith('/virtual.html'):
                continue  # запрещено robots.txt
            if alt.get(n) in ok:
                continue
            loc = local_for(n)
            try:
                r = sess.get(n, timeout=30)
                st = str(r.status_code)
                if r.ok:
                    ok.add(n)
                    dst = SITE / loc
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_bytes(r.content)
                else:
                    loc = ''
            except Exception as e:
                st, loc = 'ERR ' + type(e).__name__, ''
            fetched.append({'url': n, 'local': loc, 'status': st})
            print(st, n)
            time.sleep(1)
        old = []
        f = LOG / 'fetched.csv'
        if f.exists():
            old = list(csv.DictReader(f.open(encoding='utf-8')))
        done = {r['url'] for r in fetched}
        with f.open('w', newline='', encoding='utf-8') as fh:
            w = csv.DictWriter(fh, ['url', 'local', 'status']); w.writeheader()
            w.writerows([r for r in old if r['url'] not in done] + fetched)
        return main(fetch=False)

    LOG.mkdir(parents=True, exist_ok=True)
    with (LOG / 'missing.txt').open('w', encoding='utf-8') as fh:
        for n in sorted(missing):
            fh.write(f'{n}\t{"; ".join(sorted(missing[n]))[:300]}\n')
    with (INV / 'embeds.csv').open('w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh); w.writerow(['source', 'embed_url', 'kind'])
        for row in sorted(set(embeds)):
            if not re.search(r'ajax\.googleapis|fonts\.(googleapis|gstatic)', row[1]):
                w.writerow(row)
    with (INV / 'documents.csv').open('w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh); w.writerow(['url', 'status', 'local', 'linked_from'])
        for n in sorted(docs):
            st, loc = (urlmap.get(n) or ['', ''])[1], (urlmap.get(n) or ['', ''])[0]
            if not loc and (SITE / local_for(n)).exists():
                loc = local_for(n)
            w.writerow([n, st, loc, ' '.join(sorted(docs[n]))])

    # pages.csv
    NOT_EMBED = re.compile(r'ajax\.googleapis|fonts\.(googleapis|gstatic)|code\.jquery|cdnjs', re.I)
    def emb_label(u):
        for k, v in [('frontdesk24', 'бронирование'), ('youtube', 'видео'), ('rutube', 'видео'), ('vk.com/video', 'видео'),
                     ('map-widget', 'карта'), ('maps.googleapis', 'карта'), ('api-maps', 'карта'), ('myreviews', 'отзывы'),
                     ('mc.yandex', 'метрика'), ('streamwood', 'виджет'), ('travelline', 'бронирование'), ('bnovo', 'бронирование')]:
            if k in u:
                return v
        return 'другое'
    js_emb, own_emb = {}, {}
    for src, u, kind in set(embeds):
        if NOT_EMBED.search(u):
            continue
        (js_emb if src.endswith('.js') else own_emb).setdefault(src, set()).add(u)
    def site_js(soup):
        out = []
        for sc in soup.find_all('script', src=True):
            u = norm(urljoin(BASE, sc['src']))
            if is_ours(u) and '/plugins/' not in u and not u.endswith('.min.js') and '/styles/' not in u:
                out.append(u)
        return out
    def read_js(u):
        f = SITE / local_for(u)
        if not f.exists():
            return ''
        b = f.read_bytes()
        try:
            return b.decode('utf-8')
        except UnicodeDecodeError:
            return b.decode('cp1251', 'replace')
    rows = []
    for url, (p, soup, out) in sorted(pages.items()):
        st = (urlmap.get(url) or ['', ''])[1] or '200?'
        title = soup.title.get_text(' ', strip=True) if soup.title else ''
        h1 = ' | '.join(h.get_text(' ', strip=True) for h in soup.find_all('h1'))
        md = soup.find('meta', attrs={'name': re.compile('^description$', re.I)})
        md = md.get('content', '').strip() if md else ''
        body = soup.body or soup
        for t in body.find_all(['script', 'style', 'noscript', 'template']):
            t.decompose()
        words = len(re.findall(r'\w+', body.get_text(' ', strip=True)))
        imgs = len(soup.find_all('img'))
        bg = sum(1 for t in soup.find_all(style=True) if CSS_URL.search(t['style']))
        js = site_js(soup)
        jtxt = ' '.join(read_js(u) for u in js)
        jtext = re.sub(r'<[^>]+>|\[nrt]|&nbsp;', ' ', jtxt)
        js_words = len(re.findall(r'[А-Яа-яЁё]+', jtext))
        js_imgs = len(set(re.findall(r'[\w/.-]+\.(?:jpe?g|png|gif|webp)', jtxt, re.I)))
        emb = set(own_emb.get(url, set()))
        for u in js:
            emb |= js_emb.get(u, set())
        emb_s = ' '.join(f'{emb_label(e)}: {e}' for e in sorted(emb))
        rows.append([url, st, title, h1, md, words, js_words, imgs, bg, js_imgs, emb_s, ' '.join(u[len(BASE):] for u in js), p.relative_to(SITE).as_posix()])
    with (INV / 'pages.csv').open('w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh)
        w.writerow(['url', 'http_status', 'title', 'h1', 'meta_description', 'words_html', 'words_in_site_js', 'img_tags', 'inline_bg_images', 'img_refs_in_js', 'external_embeds', 'site_js', 'local_file'])
        w.writerows(rows)
    # битые ссылки по логу
    bad = {k: v for k, v in urlmap.items() if v[1] and v[1] != '200'}
    print(f'pages={len(rows)} files={len(files)} refs={len(refs)} missing={len(missing)} docs={len(docs)} embeds={len(set(embeds))} non200={len(bad)}')
    for k, v in sorted(bad.items())[:40]:
        print('  ', v[1], k)


if __name__ == '__main__':
    main(fetch='--fetch' in sys.argv)
