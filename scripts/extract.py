"""Этап 2. Извлечение текстов старого сайта в content/old/*.md + inventory/facts.csv + проверка полноты.

Вход: work/rendered/<file>.html — DOM после выполнения JS (scripts/serve_mirror.py + scripts/render_pages.py),
      inventory/pages.csv (метаданные страниц, этап 1).
Выход:
  content/old/<slug>.md          — по файлу на страницу, тексты дословно, секции `## Заголовок {#якорь}`
  content/old/_common.md         — шапка, меню, подвал, навигация корпуса 2 (один раз)
  inventory/facts.csv            — цены, телефоны, e-mail, адреса, часы, цифры
  inventory/text-completeness.csv — слова на странице (без общих блоков) vs слова в .md
Тексты не переписываются: берётся видимый текст DOM как есть; удаляются только общие блоки,
служебные элементы интерфейса (кнопки «Подробнее», стрелки слайдеров, клоны карусели) — их слова считаются отдельно.
"""
import csv, re, sys
from collections import OrderedDict
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup, NavigableString, Comment, Tag

ROOT = Path(__file__).resolve().parent.parent
REND = ROOT / 'work' / 'rendered'
OUT = ROOT / 'content' / 'old'
INV = ROOT / 'inventory'
BASE = 'https://kasimovskie-zori.ru/'
W = re.compile(r'\w+')
NOIMG = '(этап 3)'

BLOCK = {'div', 'p', 'section', 'article', 'ul', 'ol', 'li', 'table', 'tr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
         'header', 'footer', 'nav', 'form', 'blockquote', 'center', 'main', 'aside', 'dl', 'dt', 'dd', 'figure',
         'figcaption', 'hr', 'pre', 'address', 'tbody', 'thead', 'iframe', 'label', 'body', 'html'}
H2_CLASSES = {'section_title'}
H3_CLASSES = {'pb_title', 'side-title', 'slideQ-title', 'icon_box_title', 'rooms_title', 'room_title'}
# блоки без заголовка на сайте — помечаем секцией-меткой в [скобках]
SYNTH_SECTIONS = [('otziv-allcontent', '[блок отзывов — otzivs/show_otzivs_text.js, без заголовка на сайте]')]
# элементы интерфейса: удаляются, слова считаются как «UI»
UI_SELECTORS = ['.owl-nav', '.owl-dots', '.slider-nav', '.gallery_overlay', 'label.side-button-1', 'label.side-button-2',
                '.side-b', '.new-vidget-button', '#colorbox', '#cboxOverlay', 'form#search_form', '.search_box',
                '#start-widget', '.parallax-mirror', '.blog_button', '.room_button', '.rooms_button', '.home_button',
                '.booking_button', '.menu_button', '.hamburger']
CLONE_SELECTORS = ['.owl-item.cloned']


def words(t):
    return len(W.findall(t or ''))


def text_of(el):
    return el.get_text(' ', strip=True) if el else ''


def clean_ws(s):
    s = s.replace('\xa0', ' ')
    s = re.sub(r'<br\s*/?>', ' ', s)          # литералы <br/> в текстовых узлах (цены из JS)
    return re.sub(r'[ \t\r\f\v\n]+', ' ', s)


def abs_url(u, page_url):
    u = (u or '').strip().strip('"\'')
    if not u or u.startswith(('data:', 'javascript:', 'mailto:', 'tel:', '#')):
        return u
    return urljoin(page_url, u)


IMG_EXT = re.compile(r'\.(jpe?g|png|gif|webp|svg|bmp)(\?.*)?$', re.I)
CSS_URL = re.compile(r'url\(\s*([^)]+?)\s*\)', re.I)


class Section:
    def __init__(self, level, title, anchor=None):
        self.level, self.title, self.anchor = level, title, anchor
        self.blocks, self.images, self.embeds = [], OrderedDict(), []

    def has_content(self):
        return bool(self.blocks or self.images)


class Renderer:
    def __init__(self, page_url, anchors):
        self.page_url, self.anchors = page_url, anchors
        self.sections = [Section(2, '[вводная часть без заголовка]')]
        self.pending_anchor = None
        self.buf = []

    # ---------- секции ----------
    @property
    def cur(self):
        return self.sections[-1]

    def new_section(self, level, title):
        self.flush()
        s = Section(level, title, self.pending_anchor)
        self.pending_anchor = None
        self.sections.append(s)

    def anchor(self, name):
        self.flush()
        if self.pending_anchor:                     # два якоря подряд без контента — первый получает пустую секцию
            self.sections.append(Section(2, '[без заголовка]', self.pending_anchor))
        self.pending_anchor = name

    def add_block(self, md):
        if not md.strip():
            return
        if self.pending_anchor:                     # якорь, после которого сразу текст без заголовка
            self.sections.append(Section(2, '[без заголовка]', self.pending_anchor))
            self.pending_anchor = None
        self.cur.blocks.append(md)

    def add_image(self, src, alt, kind, link=''):
        src = abs_url(src, self.page_url)
        if not src or src.startswith('data:'):
            return
        sec = self.cur
        if src not in sec.images:
            sec.images[src] = (alt or '', kind, link)
        elif link and not sec.images[src][2]:
            sec.images[src] = sec.images[src][:2] + (link,)

    # ---------- текст ----------
    def flush(self):
        if not self.buf:
            return
        raw = ''.join(self.buf)
        self.buf = []
        lines = [re.sub(r' +', ' ', l).strip() for l in raw.split('\n')]
        out, para = [], []
        for l in lines:
            if not l or l in ('**', '****', '**  **', '*', '__'):
                if para:
                    out.append(para); para = []
                continue
            if l.startswith(('• ', '•', '· ')):
                l = '- ' + l.lstrip('•· ').strip()
            para.append(l)
        if para:
            out.append(para)
        for p in out:
            # подряд идущие строки — с переносом «двумя пробелами», списки — как есть
            md = '\n'.join(x if x.startswith('- ') else x + ('  ' if i < len(p) - 1 else '') for i, x in enumerate(p))
            self.add_block(md)

    def inline(self, node):
        if isinstance(node, Comment):
            return ''
        if isinstance(node, NavigableString):
            return clean_ws(str(node))
        if not isinstance(node, Tag):
            return ''
        n = node.name
        if n == 'br':
            return '\n'
        if n == 'img':
            self.add_image(node.get('src'), node.get('alt') or node.get('title'), 'img')
            return ''
        self.style_images(node)
        inner = ''.join(self.inline(c) for c in node.children)
        if n in ('strong', 'b') and inner.strip():
            lead, core, trail = re.match(r'^(\s*)(.*?)(\s*)$', inner, re.S).groups()
            return f'{lead}**{core}**{trail}' if '\n' not in core else inner
        if n in ('em', 'i') and inner.strip() and '\n' not in inner.strip():
            lead, core, trail = re.match(r'^(\s*)(.*?)(\s*)$', inner, re.S).groups()
            return f'{lead}*{core}*{trail}'
        if n == 'a':
            href = node.get('href', '')
            if href and IMG_EXT.search(href):
                self.add_image(href, node.get('title') or '', 'a[href]')
            elif href and not href.startswith(('javascript', '#')) and not inner.strip():
                for im in node.find_all('img'):
                    self.add_image(im.get('src'), im.get('alt') or im.get('title'), 'img', abs_url(href, self.page_url))
            if node.get('name') and node['name'] in self.anchors:
                self.anchor_inline(node['name'])
            if href and not href.startswith(('javascript', '#')) and inner.strip() and not IMG_EXT.search(href):
                return f'[{inner.strip()}]({abs_url(href, self.page_url)})'
        return inner

    def anchor_inline(self, name):
        # якорь внутри строки: сбрасываем накопленный текст и открываем ожидание секции
        self.flush()
        self.anchor(name)

    def style_images(self, el):
        st = el.get('style') or ''
        for m in CSS_URL.findall(st):
            self.add_image(m, '', 'css-bg')

    # ---------- блоки ----------
    def is_heading(self, el):
        if re.fullmatch(r'h[1-6]', el.name):
            return 2 if el.name in ('h1', 'h2') else 3
        cls = set(el.get('class') or [])
        if 'slideToggle' in (el.get('onclick') or '') and 3 < words(text_of(el)) <= 60:
            return 3
        if cls & H2_CLASSES and words(text_of(el)) <= 30:
            return 2
        if cls & H3_CLASSES and words(text_of(el)) <= 30:
            return 3
        return 0

    def heading_text(self, el):
        for img in el.find_all('img'):
            self.add_image(img.get('src'), img.get('alt'), 'img')
        t = re.sub(r'<br\s*/?>', ' ', el.get_text(' ', strip=True).replace('\xa0', ' '))
        return re.sub(r'\s+', ' ', t).strip()

    def block(self, el):
        for c in el.children:
            if isinstance(c, Comment):
                continue
            if isinstance(c, NavigableString):
                self.buf.append(clean_ws(str(c)))
                continue
            if not isinstance(c, Tag):
                continue
            n = c.name
            ident = c.get('id') or (c.get('name') if n == 'a' else None)
            if ident and ident in self.anchors and n != 'a':
                self.anchor(ident)
            if n == 'a' and c.get('name') in self.anchors and not c.get_text(strip=True):
                self.anchor(c['name'])
                continue
            if n not in BLOCK:
                # строчный тег (font/span/a/strong), внутри которого блоки или якоря, — разбираем как блок
                if c.find(list(BLOCK - {'label'})) is not None or c.find('a', attrs={'name': True}) is not None:
                    if n == 'a' and c.get('name') in self.anchors:
                        self.anchor(c['name'])
                    self.style_images(c)
                    self.block(c)
                else:
                    self.buf.append(self.inline(c))
                continue
            self.flush()
            self.style_images(c)
            for sel, label in SYNTH_SECTIONS:
                if c.get('id') == sel or sel in (c.get('class') or []):
                    self.new_section(2, label)
            lvl = self.is_heading(c)
            if lvl:
                t = self.heading_text(c)
                if t:
                    self.new_section(lvl, t)
                continue
            if n == 'iframe':
                self.add_block(f'[встраивание: {c.get("src", "")}]')
            elif n in ('ul', 'ol'):
                self.list_(c, 0)
            elif n == 'table':
                self.table(c)
            elif n == 'hr':
                pass
            else:
                self.block(c)
                self.flush()

    def list_(self, el, depth):
        items = []
        for i, li in enumerate(el.find_all('li', recursive=False), 1):
            sub = [x for x in li.find_all(['ul', 'ol'], recursive=False)]
            for s in sub:
                s.extract()
            t = re.sub(r'\s*\n\s*', ' ', ''.join(self.inline(x) for x in li.children)).strip()
            t = re.sub(r' +', ' ', t)
            mark = f'{i}.' if el.name == 'ol' else '-'
            if t:
                items.append('  ' * depth + f'{mark} {t}')
            for s in sub:
                saved = self.cur.blocks
                tmp = Renderer(self.page_url, self.anchors)
                tmp.list_(s, depth + 1)
                for b in tmp.sections[0].blocks:
                    items.append(b)
                for k, v in tmp.sections[0].images.items():  # (alt, kind, link)
                    self.cur.images.setdefault(k, v)
        if items:
            self.add_block('\n'.join(items))

    def table(self, el):
        rows = [tr for tr in el.find_all('tr') if tr.find_parent('table') is el]
        grid = []
        for tr in rows:
            cells = []
            for td in tr.find_all(['td', 'th'], recursive=False):
                t = ''.join(self.inline(x) for x in td.children)
                t = re.sub(r'\s*\n\s*', ' <br> ', t.strip())
                t = re.sub(r' +', ' ', t).replace('|', '\\|').strip()
                t = re.sub(r'^(<br> )+|( <br>)+$', '', t)
                cells.append(t)
                for _ in range(int(td.get('colspan', 1) or 1) - 1 if str(td.get('colspan', 1)).isdigit() else 0):
                    cells.append('')
            if any(cells):
                grid.append(cells)
        if not grid:
            return
        ncol = max(len(r) for r in grid)
        long_cell = any(len(c) > 400 for r in grid for c in r)
        if ncol == 1 or long_cell:                    # таблица-раскладка: разворачиваем в абзацы
            for r in grid:
                for c in r:
                    if c:
                        self.add_block(c.replace(' <br> ', '  \n'))
            return
        grid = [r + [''] * (ncol - len(r)) for r in grid]
        md = ['| ' + ' | '.join(grid[0]) + ' |', '|' + '---|' * ncol]
        md += ['| ' + ' | '.join(r) + ' |' for r in grid[1:]]
        self.add_block('\n'.join(md))

    def run(self, root):
        self.block(root)
        self.flush()
        if self.pending_anchor:
            self.sections.append(Section(2, '[без заголовка]', self.pending_anchor))
        for sec in self.sections:
            if sec.title == '[без заголовка]' and sec.blocks:
                b = sec.blocks[0]
                flat = re.sub(r'\s*\n\s*', ' ', b).strip()
                plain = flat.replace('**', '').strip()
                letters = re.sub(r'[^A-Za-zА-Яа-яЁё]', '', b.split('\n')[0])
                if (not b.startswith(('- ', '|', '[')) and 0 < words(plain) <= 20 and
                        (re.fullmatch(r'\*\*[^*]+\*\*', flat) or (letters and letters == letters.upper()))):
                    sec.title = plain
                    sec.blocks.pop(0)
        return [s for s in self.sections if s.has_content() or s.anchor or s.title != '[вводная часть без заголовка]']


# ---------------- подготовка DOM ----------------

def load(path):
    return BeautifulSoup(path.read_text(encoding='utf-8'), 'lxml')


def strip_noise(soup):
    for t in soup(['script', 'style', 'noscript', 'template', 'link', 'meta']):
        t.decompose()
    for c in soup.find_all(string=lambda x: isinstance(x, Comment)):
        c.extract()
    for el in soup.select('.milestone_counter[data-end-value]'):   # счётчики анимируются JS с 0
        el.string = el['data-end-value'] + el.get('data-sign-after', '')


def remove(soup, selectors, maxwords=None):
    n = 0
    for sel in selectors:
        for el in soup.select(sel):
            if el.decomposed if hasattr(el, 'decomposed') else False:
                continue
            w = words(text_of(el))
            if 'slideToggle' in (el.get('onclick') or '') and w > 3:
                continue
            if maxwords is not None and w > maxwords:
                continue
            n += w
            el.decompose()
    return n


def common_selectors(soup, slug):
    sels = ['header.header', 'div.menu', 'footer.footer', 'footer']
    if slug.startswith('corpus2-room'):
        sels += ['.codrops-top span.right', 'div.container > header']
    if slug == 'news':
        sels += ['div.allpages']
    return sels


def ui_cleanup(soup):
    ui = remove(soup, UI_SELECTORS, maxwords=6)
    for sp in soup.select('ul.cb-slideshow li > span'):          # «Image 01» — подложки слайд-шоу
        if re.fullmatch(r'Image \d+', sp.get_text(strip=True)):
            ui += words(sp.get_text()); sp.decompose()
    for el in soup.select('[class*=button]'):
        if el.decomposed if hasattr(el, 'decomposed') else False:
            continue
        t = text_of(el)
        if 'slideToggle' in (el.get('onclick') or '') and words(t) > 3:
            continue
        if 0 < words(t) <= 3 and el.find(['p', 'h1', 'h2', 'h3', 'table']) is None:
            ui += words(t); el.decompose()
    return ui


def fragment_targets():
    """Все якоря, на которые где-либо ссылаются (#x), плюс все <a name>."""
    t = set()
    for f in REND.rglob('*.html'):
        s = f.read_text(encoding='utf-8')
        t |= set(re.findall(r'href=["\'][^"\'#]*#([\w-]+)', s))
        t |= set(re.findall(r'<a[^>]+name=["\']([\w-]+)', s))
        t |= set(re.findall(r'location\.href\s*=\s*["\'][^"\'#]*#([\w-]+)', s))
    for f in (ROOT / 'raw' / 'site' / 'kasimovskie-zori.ru').rglob('*.js'):
        if '.min.' in f.name:
            continue
        b = f.read_bytes().decode('cp1251', 'replace')
        t |= set(re.findall(r'\.html#([\w-]+)', b))
    return t - {'', 'top', 'page'}


def slug_of(local_file):
    p = local_file.split('/', 1)[1]
    s = p[:-5] if p.endswith('.html') else p
    s = s.replace('/', '-')
    return 'home' if s == 'index' else s


# ---------------- markdown ----------------

def yaml_q(s):
    return '"' + (s or '').replace('\\', '\\\\').replace('"', '\\"') + '"'


def write_md(path, meta, sections):
    L = ['---']
    for k, v in meta.items():
        L.append(f'{k}: {yaml_q(v)}')
    L += ['---', '']
    for s in sections:
        h = '#' * s.level + ' ' + s.title + (f' {{#{s.anchor}}}' if s.anchor else '')
        L += [h, '']
        if not s.blocks and s.anchor:
            L += ['[НЕТ НА СТАРОМ САЙТЕ]' if not s.images else '_(текста нет, только картинки)_', '']
        for b in s.blocks:
            L += [b, '']
        if s.images:
            L.append('**Картинки секции:**')
            for src, (alt, kind, link) in s.images.items():
                L.append(f'- new: {NOIMG} | src: {src} | alt: {yaml_q(alt)}' + ('' if kind == 'img' else f' | via: {kind}')
                         + (f' | link: {link}' if link else ''))
            L.append('')
    path.write_text('\n'.join(L).rstrip() + '\n', encoding='utf-8')


def md_words(sections):
    n = 0
    for s in sections:
        if s.title not in ('[без заголовка]', '[вводная часть без заголовка]'):
            n += words(s.title)
        for b in s.blocks:
            if b.startswith('[встраивание:'):
                continue
            b = re.sub(r'\]\([^)]*\)', ']', b)           # URL ссылок не считаем
            b = b.replace('<br>', ' ')
            n += words(b)
    return n


# ---------------- facts ----------------

FACT_RX = [
    ('телефон', re.compile(r'(?:\+7|(?<![\d-])8)[\s\-‑]*\(?\d{3,5}\)?[\s\-‑]*\d{1,3}[\-‑]\d{2}[\-‑]\d{2}(?!\d)')),
    ('e-mail', re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')),
    ('цена', re.compile(r'(?:от\s+|до\s+)?\d[\d  ]{0,9}(?:[.,]\d+)?\s*(?:руб\w*\.?|р\.|₽)(?:\s*/\s*[а-я]+)*', re.I)),
    ('часы', re.compile(r'с\s*\d{1,2}[.:]\d{2}\s*ч?\.?\s*(?:до|-|–)\s*\d{1,2}[.:]\d{2}\s*ч?\.?|(?:круглосуточно)', re.I)),
    ('время', re.compile(r'(?:заезд|выезд|расчетн\w+ час|расчётн\w+ час)[^.\n]{0,40}?\d{1,2}[.:]\d{2}', re.I)),
    ('период/дата', re.compile(r'с\s+\d{1,2}[.]\d{2}[.]\d{2,4}\s*(?:г\.?)?\s*по\s+\d{1,2}[.]\d{2}[.]\d{2,4}|с\s+\d{1,2}\s+[а-я]+\s+\d{4}', re.I)),
    ('цифра', re.compile(r'(?<![\w.,])\d+(?:[.,]\d+)?(?:\s*[-–]\s*\d+)?\s*(?:га\b|гектар\w*|кв\.?\s?м\.?|м2|м²|км\b|километр\w*|корпус\w*|номер(?:ов|а)?\b|мест\w*|человек\w*|чел\.|коттедж\w*|программ\w*|процедур\w*|дн(?:ей|я)\b|день\b|сут(?:ок|ки)\b|ноч\w*|спал(?:ен|ьн\w*)|кроват\w*|этаж\w*|комнат\w*|врач\w*|специалист\w*|кабинет\w*|бассейн\w*|бан\w*|лет\b|года?\b|минут\w*|мин\.|%)', re.I)),
    ('адрес', re.compile(r'(?:\d{6},?\s*)?(?:Рязанская обл\w*\.?|Касимовский р-н|Касимовский район|с\.\s*Телебукино|г\.\s*Касимов(?![а-я]))[^\n]{0,100}')),
    ('адрес', re.compile(r'(?:ул\.|улица|пр-т|проспект|пер\.)\s*[А-ЯЁ][\w\- ]{1,40}(?:,\s*(?:д\.|дом)\s*\d+\w*)?')),
    ('реквизиты', re.compile(r'(?<![А-Яа-яЁё])(?:ИНН|КПП|ОГРН|ОКПО|БИК|ОКВЭД|р/с|к/с)(?![А-Яа-яЁё])\s*[:№]?\s*[\d\- ]{6,30}|[Лл]ицензи\w+\s*№\s*[\w\-/.]{3,40}')),
]


LEGAL_ANCHORS = {'doczaschitaprav', 'docfreemedicine'}


def facts_for(slug, url, sections):
    out = []
    for s in sections:
        anchor = s.anchor or ''
        where = s.title
        for b in s.blocks:
            if b.startswith('|'):
                rows = [r.strip('|').split(' | ') for r in b.split('\n') if not r.startswith('|---')]
                rows = [[c.strip() for c in r] for r in rows]
                head = rows[0]
                for r in rows[1:]:
                    for j, c in enumerate(r[1:], 1):
                        if re.fullmatch(r'[\d  .,]+(?:\s*руб\.?)?', c) and re.search(r'\d', c):
                            what = f'{r[0]} / {head[j] if j < len(head) else ""}'.replace('<br>', ' ')
                            out.append(['таблица', where, re.sub(r'\*', '', what), c, url, anchor, slug])
                text = ' '.join(' '.join(r) for r in rows)
            else:
                text = b
            text = re.sub(r'\]\([^)]*\)', ']', text)
            for typ, rx in FACT_RX:
                if typ == 'период/дата' and slug == 'news':
                    continue
                if typ in ('цифра', 'цена') and anchor in LEGAL_ANCHORS:   # тексты федеральных актов
                    continue
                for m in rx.finditer(text):
                    v = re.sub(r'\s+', ' ', m.group(0)).strip(' ,;:')
                    if typ == 'цифра' and re.fullmatch(r'\d{4}\s*года?', v):    # годы
                        continue
                    if typ == 'адрес' and len(v) < 12:
                        continue
                    a, z = max(0, m.start() - 60), min(len(text), m.end() + 60)
                    ctx = re.sub(r'\s+', ' ', text[a:z]).replace('**', '').strip()
                    out.append([typ, where, ctx, v, url, anchor, slug])
    return out


# ---------------- main ----------------

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pages = list(csv.DictReader(open(INV / 'pages.csv', encoding='utf-8-sig')))
    anchors = fragment_targets()
    facts, comp = [], []

    # общие блоки — один раз
    common = []
    s = load(REND / 'index.html'); strip_noise(s)
    for title, sel in [('Шапка (js/header.js)', 'header.header'), ('Меню (js/menu.js)', 'div.menu'),
                       ('Подвал (js/footer.js)', 'footer')]:
        el = s.select_one(sel)
        r = Renderer(BASE, set())
        r.block(el); r.flush()
        sec = [x for x in r.sections if x.has_content()]
        common.append(Section(2, title))
        for x in sec:
            if x.title.startswith('[') and common[-1].blocks == []:
                common[-1].blocks, common[-1].images = x.blocks, x.images
            else:
                common.append(x)
    rs = load(REND / 'corpus2' / 'room201.html'); strip_noise(rs)
    r = Renderer(BASE + 'corpus2/room201.html', set())
    for el in rs.select('.codrops-top span.right, div.container > header'):
        r.block(el); r.flush()
    common.append(Section(2, 'Навигация страниц корпуса 2 (corpus2/room*.html)'))
    for x in r.sections:
        common[-1].blocks += x.blocks
    write_md(OUT / '_common.md', OrderedDict(source='общие блоки: header.js, menu.js, footer.js — на 25 страницах; навигация corpus2 — на 18'), common)
    facts += facts_for('_common', BASE, common)

    for p in pages:
        lf = p['local_file'].split('/', 1)[1]
        slug = slug_of(p['local_file'])
        url = p['url']
        if slug == 'news':
            files = [('СВЕЖИЕ НОВОСТИ', 'news_page04.html'), ('НОВОСТИ 2025 года', 'news_page03.html'),
                     ('НОВОСТИ 2024 года', 'news_page02.html'), ('НОВОСТИ 2023 года', 'news_page01.html')]
        else:
            files = [(None, lf)]
        sections, page_w, common_w, ui_w, clone_w = [], 0, 0, 0, 0
        for group, fn in files:
            soup = load(REND / fn)
            strip_noise(soup)
            body = soup.body or soup
            page_w_all = words(text_of(body))
            common_w += remove(soup, common_selectors(soup, slug))
            clone_w += remove(soup, CLONE_SELECTORS)
            ui_w += ui_cleanup(soup)
            if slug == 'news':
                for bp in soup.select('div.blog_post'):              # превью дублирует лид полной новости
                    for el in bp.select('.pb_text, .bp_date'):
                        if el.find_parent(class_='textblock') is None:
                            clone_w += words(text_of(el)); el.decompose()
                    tb = bp.select_one('.textblock[id]')
                    t = bp.select_one('.pb_title')
                    if tb and t:
                        a = soup.new_tag('a'); a['name'] = tb['id']; t.insert_before(a)
                        for aa in tb.find_all('a', attrs={'name': tb['id']}):
                            aa.decompose()
                        del tb['id']
                anchors_here = anchors | {a['name'] for a in soup.select('div.blog_post a[name]')}
            else:
                anchors_here = anchors
            page_w += page_w_all
            r = Renderer(url, anchors_here)
            secs = r.run(body)
            if group:
                secs.insert(0, Section(2, f'[news.html?page={fn[-7:-5]} — раздел «{group}»]'))
                secs = [x for x in secs if x.has_content() or x.anchor or x.title.startswith('[news.html')]
            sections += secs
        meta = OrderedDict(old_url=url, title=p['title'], meta_description=p['meta_description'], h1=p['h1'],
                           slug=slug, source='work/rendered/' + (lf if slug != 'news' else 'news_page0[1-4].html') + ' (DOM после JS)')
        write_md(OUT / f'{slug}.md', meta, sections)
        mw = md_words(sections)
        content_w = page_w - common_w
        diff = (mw - content_w) / content_w * 100 if content_w else 0.0
        explained = (mw - (content_w - ui_w - clone_w)) / max(1, content_w - ui_w - clone_w) * 100
        comp.append([url, slug, page_w, common_w, content_w, ui_w, clone_w, mw, f'{diff:.1f}', f'{explained:.1f}',
                     len(sections), sum(len(x.images) for x in sections)])
        facts += facts_for(slug, url, sections)

    # данные JS-массивов целиком (цены всех периодов, коттеджи, акции, отзывы)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import jsdata
    def html_to_md(x):
        sp = BeautifulSoup(f'<div>{x}</div>', 'lxml')
        rr = Renderer(BASE, set()); rr.block(sp.div); rr.flush()
        return '  \n'.join(b for sec in rr.sections for b in sec.blocks)
    jsecs = jsdata.build(Section, html_to_md)
    write_md(OUT / '_js-data.md', OrderedDict(source='массивы данных из JS сайта: ' + ', '.join(jsdata.FILES)), jsecs)
    facts += facts_for('_js-data', 'js', jsecs)

    # facts: дедуп по (тип, значение, страница, якорь, контекст)
    seen, fx = set(), []
    for f in facts:
        k = (f[0], f[3], f[4], f[5], f[2])
        if k not in seen:
            seen.add(k); fx.append(f)
    with open(INV / 'facts.csv', 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh)
        w.writerow(['тип', 'секция', 'что (контекст)', 'значение', 'страница', 'якорь', 'slug'])
        w.writerows(fx)
    with open(INV / 'text-completeness.csv', 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh)
        w.writerow(['url', 'slug', 'words_page_all', 'words_common_removed', 'words_page_content', 'words_ui_removed',
                    'words_dupes_removed', 'words_md', 'diff_pct_vs_content', 'diff_pct_after_ui_dupes', 'sections', 'images'])
        w.writerows(comp)
    print('pages', len(comp), 'facts', len(fx), 'anchors', len(anchors))


if __name__ == '__main__':
    main()
