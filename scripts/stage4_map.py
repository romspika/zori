"""Этап 4. Карта контента и редиректы.

Вход:  content/old/*.md (секции и картинки, уже с новыми именами фото), inventory/images.csv.
Выход: inventory/content-map.csv, inventory/redirects.csv, inventory/vip-room-photos.csv.

Каждая секция `##` (а где нужно — и `###`) каждой старой страницы получает строку:
старый URL#якорь → новая страница → блок прототипа → тип → статус.
Правила «что куда» — таблицы в этом файле (PAGES, RULES и т.д.). Скрипт проверяет, что не осталось
ни одной непокрытой секции: непокрытое — ошибка, а не молчаливый пропуск.

Статусы:
  текст есть / текста нет (меньше 8 слов, либо только таблица цен: тогда в note «только прайс»);
  мало фото = 1–2 контентных фото, нет фото = 0 (для типов, где фото нужны: процедура, программа,
  проживание, акция, новость, и страниц/блоков с ph=True). Порог «мало» — меньше 3 фото (для новости — 0).
  Иконки, декор, фоны-мрамор не считаются. low_res — в отдельной колонке.

Запуск: python -I scripts/stage4_map.py
"""
import csv
import re
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OLD = ROOT / 'content' / 'old'
INV = ROOT / 'inventory'
BASE = 'https://kasimovskie-zori.ru'

# ---------------------------------------------------------------- разбор md
HEAD = re.compile(r'^(#{2,3}) (.*?)(?: \{#([^}]+)\})?\s*$')
IMG = re.compile(r'^- new: (.*?) \| src: (\S+)')
PLACEHOLDER = re.compile(r'\[НЕТ НА СТАРОМ САЙТЕ\]')


class Sec:
    def __init__(self, level, title, anchor):
        self.level, self.title, self.anchor = level, title, anchor
        self.text, self.imgs, self.children = [], [], []
        self.used = False

    def words(self, exclude=()):
        t = '\n'.join(self.text)
        n = self._wc(t)
        for c in self.children:
            if not any(c.title.startswith(e) for e in exclude):
                n += c.words()
        return n

    @staticmethod
    def _wc(t):
        t = PLACEHOLDER.sub('', t)
        t = re.sub(r'\|[\s:|-]+\|', ' ', t)
        return len(re.findall(r'\w+', t))

    def all_imgs(self, exclude=()):
        r = list(self.imgs)
        for c in self.children:
            if not any(c.title.startswith(e) for e in exclude):
                r += c.all_imgs()
        return r

    def alltext(self):
        return '\n'.join(self.text + [c.alltext() for c in self.children])


def parse(slug):
    t = (OLD / f'{slug}.md').read_text(encoding='utf-8')
    m = re.search(r'^old_url: "(.*?)"', t, re.M)
    old_url = m.group(1) if m else ''
    body = t.split('\n---\n', 1)[1] if t.startswith('---') else t
    secs, cur, par = [], None, None
    for line in body.splitlines():
        h = HEAD.match(line)
        if h:
            s = Sec(len(h.group(1)), h.group(2).strip(), h.group(3))
            if s.level == 2:
                secs.append(s)
                par = s
            else:
                if par is None:
                    par = Sec(2, '[?]', None)
                    secs.append(par)
                par.children.append(s)
            cur = s
            continue
        if cur is None:
            continue
        mi = IMG.match(line)
        if mi:
            cur.imgs.append((mi.group(1).strip(), mi.group(2)))
        elif line.strip() != '**Картинки секции:**':
            cur.text.append(line)
    return old_url, secs


# ---------------------------------------------------------------- картинки
IMGINFO = {}
for r in csv.DictReader(open(INV / 'images.csv', encoding='utf-8-sig')):
    nm = r['new_name'].replace('media/renamed/', '')
    if nm and (r['is_primary'] == 'yes'):
        IMGINFO[nm] = r
ROWS_BY_PAGE = defaultdict(list)       # для фото, не упомянутых в md (CSS-фоны корпуса 2)
for r in csv.DictReader(open(INV / 'images.csv', encoding='utf-8-sig')):
    for p in r['pages'].split('; '):
        ROWS_BY_PAGE[p].append(r)


def is_content(nm):
    r = IMGINFO.get(nm)
    if not r:
        return False
    return 'icon' not in r['flags'] and r['section'] not in ('_icons', 'obshchee')


def photo_names(imgs):
    seen, out = set(), []
    for nm, _src in imgs:
        if nm not in seen and is_content(nm):
            seen.add(nm)
            out.append(nm)
    return out


def low_count(names):
    return sum('low_res' in IMGINFO[n]['flags'] for n in names)


# ---------------------------------------------------------------- таблицы правил
PAGES = OrderedDict()   # slug -> (old_url, secs)
for f in sorted(OLD.glob('*.md')):
    PAGES[f.stem] = parse(f.stem)

OUT = []                # строки карты
REDIR_ANCH = []         # якорные редиректы (old#anchor → new)


def find(slug, key, n=0):
    _, secs = PAGES[slug]
    hits = []
    for s in secs:
        if key.startswith('#'):
            ok = s.anchor == key[1:]
        else:
            ok = s.title.startswith(key)
        if ok:
            hits.append(s)
    if len(hits) <= n:
        raise SystemExit(f'не найдено: {slug} {key!r} n={n}')
    return hits[n]


def find_h3(sec, key):
    for c in sec.children:
        if (key.startswith('#') and c.anchor == key[1:]) or (not key.startswith('#') and c.title.startswith(key)):
            return c
    raise SystemExit(f'нет ### {key!r} в {sec.title!r}')


PH_TYPES = {'процедура', 'программа', 'проживание', 'акция', 'новость'}


def add(slug, sec, url, block, typ, new_slug='', note='', ph=None, status=None, photos=None, words=None,
        old_url=None, anchor=True, price_only=False, min_ph=3, section_title=None, exclude=()):
    base = PAGES[slug][0] if old_url is None else old_url
    a = sec.anchor if (sec is not None and anchor) else None
    names = photos if photos is not None else (photo_names(sec.all_imgs(exclude)) if sec is not None else [])
    w = words if words is not None else (sec.words(exclude) if sec is not None else 0)
    need = (typ in PH_TYPES) if ph is None else ph
    st = []
    if typ == 'служебное' and not status:
        status = 'не переносится'
    if status:
        st = [status]
    else:
        st.append('текста нет' if (w < 8 or price_only) else 'текст есть')
        if need:
            if not names:
                st.append('нет фото')
            elif len(names) < min_ph:
                st.append('мало фото')
    if price_only and not note.startswith('только прайс'):
        note = ('только прайс (таблица цен), описания нет. ' + note).strip()
    title = section_title or (sec.title if sec is not None else '')
    OUT.append(dict(
        old_url=base + ('#' + a if a else ''), old_section=title, new_url=url, new_slug=new_slug, proto_block=block,
        type=typ, status='; '.join(st), words=w, photos=len(names), photos_low_res=low_count(names),
        photo_files=' '.join(names), note=note))
    if sec is not None:
        sec.used = True
    return OUT[-1]


# ---- 1. страницы целиком (для редиректов)
PAGE_REDIRECT = OrderedDict([
    ('/index.html', ('/', '')),
    ('/questions.html', ('/voprosy-otvety/', '')),
    ('/programms_all.html', ('/lechenie/', '')),
    ('/programms_treatment.html', ('/programmy/', '')),
    ('/programms_meduslugi.html', ('/procedury/', '')),
    ('/programms_izuminki.html', ('/procedury/', 'на странице 7 «изюминок»: процедуры, СПА и косметология; общий вход — каталог процедур')),
    ('/programms_equipment.html', ('/lechenie/#oborudovanie', 'блок «Своя диагностическая база» страницы «Лечение»')),
    ('/programms_medkabinets.html', ('/lechenie/#medkabinety', 'галерея медкабинетов в том же блоке')),
    ('/rooms.html', ('/prozhivanie/', '')),
    ('/nomera.html', ('/prozhivanie/#nomera', '')),
    ('/live_in_hotel.html', ('/prozhivanie/#nomera', 'цены на номера в корпусах — в карточках номеров')),
    ('/live_in_corpus1.html', ('/prozhivanie/#nomera', '')),
    ('/live_in_corpus2.html', ('/prozhivanie/vip-korpus/', '')),
    ('/live_in_cottegues.html', ('/prozhivanie/#kottedzhi', '')),
    ('/live_in_cottegues_newyear.html', ('/akcii/novyy-god-2026/', 'устарело (прайс 31.12.2025–11.01.2026): решить, что делать с новогодними предложениями')),
    ('/live_in_hotel_newyear.html', ('/akcii/novyy-god-2026/', 'страница-обёртка iframe с новогодним прайсом')),
    ('/live_in_hotel-embed.html', ('/prozhivanie/#nomera', 'iframe-версия прайса (с 01.09.2025), не страница для людей')),
    ('/dopuslugi-embed.html', ('/semyam/', 'iframe с прайсом доп. услуг; сам прайс раскладывается по блокам (СПА, семья, мероприятия)')),
    ('/pricehotel-newyear-embed.html', ('/akcii/novyy-god-2026/', 'iframe')),
    ('/dopuslugi.html', ('/semyam/', 'на странице: вступительный текст + iframe с прайсом доп. услуг')),
    ('/documents.html', ('/dokumenty/', '')),
    ('/contact.html', ('/kontakty/', '')),
    ('/booking.html', ('/bronirovanie/', '')),
    ('/news.html', ('/novosti/', 'то же для news.html?page=01…04')),
    ('/virtual.html', ('/territoriya/', 'страница закрыта robots.txt, не скачивалась; куда вести — решить вместе с вопросом о виртуальном туре')),
])
for n in range(201, 207):
    PAGE_REDIRECT[f'/corpus2/room{n}.html'] = (f'/prozhivanie/vip-korpus/#nomer-{n}', '')
for f in (3, 4):
    for n in range(1, 7):
        PAGE_REDIRECT[f'/corpus2/room{f}0{n}.html'] = (f'/prozhivanie/vip-korpus/#nomer-{f}0{n}', '')

# ---- 2. главная ----------------------------------------------------
H = 'Главная · '
add('home', find('home', '[вводная часть без заголовка]'), '/', H + '1 Hero', 'страница', 'home',
    'телефон +7 (985) 770-09-69; картинки — логотип и иконки. Заголовка и подзаголовка hero на старом сайте нет (h1 страницы — «Номер Люкс»)', ph=True)
add('home', find('home', 'Основной лечебный профиль'), '/lechenie/', H + '3 Лечение (вводный абзац)', 'страница', 'lechenie',
    'главный профиль: опорно-двигательный аппарат')
add('home', find('home', 'Лечебная база санатория'), '/lechenie/', H + '3 Лечение — Своя диагностическая база', 'страница', 'lechenie',
    'общий абзац о комплексном подходе, без конкретики о диагностике')
add('home', find('home', 'Документы для заселения'), '/kak-dobratsya/', H + '10 Как подготовиться к заезду', 'страница', 'kak-dobratsya',
    'одно предложение: паспорт РФ / свидетельство о рождении', anchor=False)
_h = find('home', 'Вопросы и ответы')
add('home', _h, '/voprosy-otvety/#sanatorno-kurortnaya-karta', 'Вопросы и ответы (FAQ)', 'FAQ', 'sanatorno-kurortnaya-karta',
    'дубль вопроса №3 из questions.html (список документов для санаторно-курортной карты); также блок «Как подготовиться к заезду»')
add('home', find('home', 'Фотографии санатория'), '/', H + '1 Hero (слайдер/галерея)', 'страница', 'home',
    'в тексте только повтор «КАСИМОВСКИЕ ЗОРИ санаторий»; 11 снимков шапки 1610×850 + 3 из них используются в «Проживании»', ph=True)
_p = find('home', '#lechprogs')
add('home', _p, '/programmy/', H + '3 Лечение — Программы лечения (на главной 4 карточки)', 'программа', 'programmy',
    'цены «от» для 14 программ и «Бронирование коттеджей»; в прототипе на главной: Гибкий позвоночник, Здоровое сердце, Свободное дыхание, Путёвка выходного дня', ph=False)
add('home', find('home', 'Почему клиенты выбирают'), '/', H + '1 Hero (цифры) / 3 Лечение', 'страница', 'home',
    'цифры: «14 лечебных программ», «450 номеров» — расходятся с другими страницами (см. вопросы); «торфяная грязь с собственного участка»', ph=False)
add('home', find('home', 'Основные медицинские услуги'), '/procedury/', H + '3 Лечение — Основные процедуры', 'процедура', 'procedury',
    'краткие описания 17 процедур (для карточек), 21 картинка = те же фото, что в процедурах', ph=False)
add('home', find('home', '#actionactions'), '/akcii/', H + '9 Акции', 'акция', 'akcii',
    'три карточки: ЕЦК, подарочный сертификат, специальные предложения; тексты акций — в _js-data.md', ph=False)
add('home', find('home', 'Виртуальный тур по санаторию'), '/territoriya/', H + '8 Территория (виртуальный тур)', 'страница', 'territoriya',
    'только заголовок и ссылка на /virtual.html (закрыта robots.txt, содержимое неизвестно)')
add('home', find('home', 'Наши лицензии'), '/dokumenty/licenzii/', 'Документы · лицензии (в прототипе отдельного блока нет)', 'документ', 'licenzii',
    'в секции нет текста, только 7 снимков лицензий и рейтинг «4.9 (653 отзыва)»; лицензии те же, что на documents.html', ph=False)
add('home', find('home', '[блок отзывов'), '/otzyvy/', 'нет блока в прототипе (отзывы)', 'отзыв', 'otzyvy',
    'виджет myreviews.dev + 34 отзыва в JS; блок в прототипе не предусмотрен — вопрос руководству', ph=False)

# ---- 3. вопросы-ответы ----------------------------------------------
FAQ_SLUGS = [
    'protivopokazaniya', 'dokumenty-dlya-prebyvaniya', 'sanatorno-kurortnaya-karta', 'platnye-uslugi-pri-putevke-bez-lecheniya',
    'putevki-menshe-7-dney', 'dopolnitelnoe-mesto', 'dokumenty-dlya-inostrantsev', 'zhivotnye', 'priezd-posle-14-00',
    'naznachenie-protsedur', 'spravka-dlya-nalogovoy', 'nachalo-sutok', 'oplata-putevki', 'kompensatsiya-invalidam',
    'novogodnie-prazdniki', 'kak-vybrat-kurs-pri-boli-v-poyasnitse', 'pitanie', 'period-putevki-pri-zabolevaniyah-oda']
FAQ_PREP = {1, 2, 3, 6, 8}    # индексы (с 0), которые заодно нужны в «Как подготовиться к заезду»
_q = find('questions', 'Вопросы и ответы')
assert len(_q.children) == len(FAQ_SLUGS), len(_q.children)
for i, (c, sl) in enumerate(zip(_q.children, FAQ_SLUGS)):
    add('questions', c, f'/voprosy-otvety/#{sl}', 'Вопросы и ответы (FAQ)', 'FAQ', sl,
        'также блок «Как подготовиться к заезду»' if i in FAQ_PREP else '', anchor=False)
_q.used = True

# ---- 4. лечение: хаб, программы, процедуры, оборудование ------------
add('programms_all', find('programms_all', '[вводная часть без заголовка]'), '/lechenie/', 'Лечение · хаб (карточки разделов)', 'страница', 'lechenie',
    '5 карточек-ссылок: программы, медуслуги, изюминки, оборудование, медкабинеты; 5 фото-карточек (rooms_6…10.jpg) — картинки-обложки, 690 px', ph=False)

PROGRAMS = [  # (anchor, slug)
    ('programbaze', 'bazovaya-lechebnaya'), ('programchildren', 'lechebno-ozdorovitelnaya-dlya-detey'),
    ('programheart', 'zdorovoe-serdce'), ('programbreath', 'svobodnoe-dykhanie'),
    ('programphysical', 'fizicheskaya-aktivnost'), ('programideal', 'stremlenie-k-sovershenstvu'),
    ('programflexy', 'gibkiy-pozvonochnik'), ('programcovid', 'profilaktika-reabilitaciya-covid-19'),
    ('programcvo', 'programma-dlya-uchastnikov-svo'), ('programprofsoyus', 'obshcheterapevticheskaya-dlya-profsoyuzov'),
    ('programvacancy', 'putevka-vykhodnogo-dnya'), ('programexpress', 'ekspress-otdykh'),
    ('programdetox', 'detoks'), ('programlite', 'ozdorovitelnaya-layt')]
PROTO4 = {'gibkiy-pozvonochnik', 'zdorovoe-serdce', 'svobodnoe-dykhanie', 'putevka-vykhodnogo-dnya'}

PROC_MED = [  # (ключ, slug)
    ('#vodolechenie', 'vodolechenie'), ('#teplolechenie', 'teplolechenie'),
    ('Лечебно-диагностические манипуляции', 'lechebno-diagnosticheskie-manipulyacii'),
    ('#vibromechanoterapy', 'vibro-mekhanoterapiya'), ('#apparatnayaphizioterapy', 'apparatnaya-fizioterapiya'),
    ('#commonterapy', 'obshcheukreplyayushchaya-terapiya'), ('#curegymnastic', 'lechebnaya-gimnastika'),
    ('#massage', 'massazh'), ('#cosmeticuslugi', 'kosmetologicheskie-uslugi'), ('#mechanoterapia', 'mekhanoterapiya'),
    ('#pnevmoterapia', 'pnevmokompressionnaya-terapiya'), ('#magnitoterapia', 'magnitoterapiya'),
    ('#svetolechenie', 'svetolechenie'), ('#ingalyacionnyaterapia', 'ingalyacionnaya-terapiya'),
    ('#lasernayaterapia', 'lazernaya-terapiya'), ('#ozonoterapia', 'ozonoterapiya'),
    ('#electrolechenie', 'elektrolechenie')]
PROC_IZ = [  # (ключ, n, slug, группа, блок)
    ('#gryazelechenie', 0, 'gryazelechenie', 'лечение', 'Шаблон процедуры «Грязелечение» (эталон)'),
    ('#soltcave', 0, 'solyanaya-peshchera', 'СПА', 'Главная · 4 СПА и банный комплекс — Соляная пещера'),
    ('#vlok', 0, 'vlok', 'лечение', 'Шаблон процедуры'),
    ('#ormed', 0, 'mekhanoterapevticheskiy-kompleks-ormed', 'лечение', 'Шаблон процедуры'),
    ('#cosmetology', 0, 'kosmetologicheskie-uslugi', 'СПА', 'Главная · 4 СПА и банный комплекс — Косметология'),
    ('#programideal', 0, 'penno-solodkovye-vanny', 'лечение', 'Шаблон процедуры'),
    ('#cosmetology', 1, 'ozonoterapiya', 'лечение', 'Шаблон процедуры')]
EQUIP = [  # (ключ, n, slug)
    ('Аппарат интерференцтерапии', 0, 'radius-01-inter'), ('Аппарат магнитотерапии', 0, 'polyus-2m'),
    ('Аппарат электролечения', 0, 'ampliimpuls-7'), ('Ванна 4-камерная', 0, 'istra-4k'),
    ('Кинезотерапевтический аппарат', 0, 'ormed-kinezo'), ('Свинг-машина', 0, 'sving-mashina-takasima'),
    ('Аппарат для реабилитации нижних', 0, 'ormed-fleks'), ('Многофункциональная', 0, 'okkervil-kombi')]


def zigzag(slug, items):
    """Фото на этих страницах идут «зигзагом» (то слева, то справа от текста), поэтому в md картинки
    прицеплены к соседней секции. Проверено по листу spa.jpg: k-я картинка страницы = k-й элемент.
    Условие: контентных картинок на странице ровно столько же, сколько элементов."""
    _, secs = PAGES[slug]
    seq = []
    for s in secs:
        seq += photo_names(s.all_imgs())      # картинки секции и её ###-подсекций в порядке документа
    seen, uniq = set(), []
    for n in seq:
        if n not in seen:
            seen.add(n)
            uniq.append(n)
    if len(uniq) != len(items):
        raise SystemExit(f'зигзаг {slug}: фото {len(uniq)}, элементов {len(items)}')
    return dict(zip(items, uniq))


def has(sec):
    t = sec.alltext()
    f = []
    if re.search(r'показани', t, re.I):
        f.append('показания')
    if re.search(r'противопоказ', t, re.I):
        f.append('противопоказания')
    if re.search(r'^\|.*[Цц]ена', t, re.M):
        f.append('прайс-таблица')
    if re.search(r'^\s*- ', t, re.M):
        f.append('списки')
    return ('в тексте есть: ' + ', '.join(f)) if f else 'в тексте нет показаний/противопоказаний/прайса'


# программы
_zz = zigzag('programms_treatment', [a for a, _ in PROGRAMS])
add('programms_treatment', find('programms_treatment', 'Лечебные программы'), '/programmy/', 'Лечение · Программы (шапка каталога)', 'страница', 'programmy',
    'заголовок раздела + баннер; счётчики «23k клиентов / 450 комнат / 12 программ» — из data-end-value', ph=False)
for a, sl in PROGRAMS:
    s = find('programms_treatment', '#' + a)
    blk = ('Главная · 3 Лечение — Программы лечения (карточка на главной); ' if sl in PROTO4 else '') + 'Страница программы'
    nt = 'фото — одно на программу (порядок на странице, см. примечание в README); ' + has(s)
    add('programms_treatment', s, f'/programmy/{sl}/', blk, 'программа', sl, nt, photos=[_zz[a]] if a in _zz else [])
    REDIR_ANCH.append((f'/programms_treatment.html#{a}', f'/programmy/{sl}/', ''))

# процедуры из «медуслуг»
_zm = zigzag('programms_meduslugi', [k for k, _ in PROC_MED])
add('programms_meduslugi', find('programms_meduslugi', 'Основные медицинские услуги'), '/procedury/', 'Лечение · Основные процедуры (шапка каталога)', 'страница', 'procedury',
    'заголовок + баннер', ph=False)
for k, sl in PROC_MED:
    s = find('programms_meduslugi', k)
    nt = has(s) + '; прайс-лист с 01.02.2026 — также в _js-data.md (js/meduslugi.js)'
    if sl == 'kosmetologicheskie-uslugi':
        nt = 'ДУБЛЬ с programms_izuminki#cosmetology (тексты различаются: 1316 и 1084 знаков), объединить; ' + nt
    if sl == 'ozonoterapiya':
        nt = 'ДУБЛЬ: текст идентичен programms_izuminki «Озонотерапия» (якорь там #cosmetology); ' + nt
    if sl == 'lechebno-diagnosticheskie-manipulyacii':
        nt = 'якорь на старом сайте закомментирован (ссылки с главной вели в никуда); ' + nt
    if sl == 'vodolechenie':
        nt += '; в прейскуранте есть «Ванна пенно-солодковая» — см. penno-solodkovye-vanny'
    add('programms_meduslugi', s, f'/procedury/{sl}/', 'Шаблон процедуры', 'процедура', sl, nt, photos=[_zm[k]])
    if s.anchor:
        REDIR_ANCH.append((f'/programms_meduslugi.html#{s.anchor}', f'/procedury/{sl}/', ''))

# «изюминки»
_zi = zigzag('programms_izuminki', [(k, n) for k, n, *_ in PROC_IZ])
add('programms_izuminki', find('programms_izuminki', 'Изюминки нашего санатория'), '/lechenie/', 'Лечение · Изюминки (шапка раздела)', 'страница', 'lechenie',
    'заголовок + баннер', ph=False)
for k, n, sl, grp, blk in PROC_IZ:
    s = find('programms_izuminki', k, n)
    nt = f'группа: {grp}; ' + has(s)
    if sl == 'gryazelechenie':
        nt = 'эталонная процедура прототипа; «Сапожковская торфяная грязь», «собственный участок добычи» — в тексте; ' + nt
    if sl == 'solyanaya-peshchera':
        nt += '; фото spa-01 — это именно соляная пещера'
    if sl == 'vlok':
        nt += '; фото procedury-… (лазер на руке) — ВЛОК, лежало в секции «Соляная пещера»'
    if sl == 'kosmetologicheskie-uslugi':
        nt = 'ДУБЛЬ с programms_meduslugi#cosmeticuslugi, объединить; ' + nt
    if sl == 'ozonoterapiya':
        nt = 'ДУБЛЬ: текст идентичен programms_meduslugi#ozonoterapia; на старой странице якорь #cosmetology повторяется; ' + nt
    if sl == 'penno-solodkovye-vanny':
        nt = 'на старой странице якорь #programideal совпадает с программой «Стремление к совершенству»; ' + nt
    add('programms_izuminki', s, f'/procedury/{sl}/', blk, 'процедура', sl, nt, photos=[_zi[(k, n)]], anchor=False)
    a = s.anchor
    REDIR_ANCH.append((f'/programms_izuminki.html#{a}', f'/procedury/{sl}/', 'якорь повторяется на странице; ведёт на первую по порядку процедуру' if k == '#cosmetology' or sl == 'penno-solodkovye-vanny' else ''))

# оборудование
_ze = zigzag('programms_equipment', [(k, n) for k, n, _ in EQUIP])
add('programms_equipment', find('programms_equipment', 'Наше оборудование'), '/lechenie/#oborudovanie', 'Лечение — Своя диагностическая база (оборудование)', 'страница', 'lechenie',
    'заголовок + баннер', ph=False)
for k, n, sl in EQUIP:
    s = find('programms_equipment', k, n)
    add('programms_equipment', s, f'/lechenie/#oborudovanie-{sl}', 'Лечение — Своя диагностическая база (оборудование)', 'страница', sl,
        'аппарат описан по принципу «название — для чего»; якорь на старой странице скопирован с других блоков и не соответствует; предлагается ACF-повторитель на странице «Лечение»; фото — одно на аппарат', ph=True,
        photos=[_ze[(k, n)]], anchor=False)
add('programms_medkabinets', find('programms_medkabinets', 'Фотографии медицинских кабинетов'), '/lechenie/#medkabinety', 'Лечение — Своя диагностическая база (галерея кабинетов)', 'страница', 'lechenie',
    'только фото (26 шт., все ≤ 900 px), подписей нет', ph=True)

# ---- 5. проживание ---------------------------------------------------
_r = find('rooms', '[вводная часть без заголовка]')
add('rooms', _r, '/prozhivanie/', 'Проживание · хаб (карточки: коттеджи, гостиница, ВИП, доп. услуги, номера)', 'страница', 'prozhivanie',
    'карточки-ссылки с картинками 690 px; «Цены действительны для бронирования физическими лицами»; карточка «Экскурсии» закомментирована', ph=False,
    exclude=('Санаторий «Касимовские Зори»',))
add('rooms', _r, '/territoriya/', 'Главная · 8 Территория («10 гектаров у Оки») — описание', 'страница', 'territoriya',
    'самый содержательный текст о территории: инфраструктура (магазин, площадка, беседка с фонтаном, пляж с прокатом, плавучая баня, спорткомплекс, ресторан); там же — абзац о лечебной базе («более 70 видов процедур», лаборатория, функциональная и УЗИ-диагностика) для блока «Лечение»; цифры «10 гектаров» нет нигде',
    ph=True, photos=[], words=find_h3(_r, 'Санаторий «Касимовские Зори»').words(), anchor=False, section_title='[rooms.html] Санаторий «Касимовские Зори» (### внутри вводной секции)')

_n = find('nomera', 'Наши номера')
_nt = '\n'.join(_n.text)
_parts = re.split(r'(?=Санаторий:)|(?=Корпус повышенной комфортности)', _nt)
_parts = [p for p in _parts if p.strip()]
ROOM_TYPES = [('ОДНОМЕСТНЫЙ НОМЕР', 'standart-odnomestnyy'), ('ДВУХМЕСТНЫЙ НОМЕР', 'standart-dvuhmestnyy'), ('ТРЁХМЕСТНЫЙ НОМЕР', 'standart-trehmestnyy'),
              ('НОМЕР ПОЛУЛЮКС', 'polulyuks'), ('НОМЕР ЛЮКС', 'lyuks'), ('Корпус повышенной комфортности', 'korpus-povyshennoy-komfortnosti')]
assert len(_parts) == len(ROOM_TYPES), len(_parts)
_nphotos = photo_names(_n.all_imgs())
for (ttl, sl), p in zip(ROOM_TYPES, _parts):
    add('nomera', _n, f'/prozhivanie/{sl}/', 'Проживание · Номера в корпусах', 'проживание', sl,
        f'{len(_nphotos)} фото на всю страницу общим списком (не по типам) — соответствие по листу nomera.jpg; названия категорий в прайсе (live_in_hotel): СТАНДАРТ одно-/двух-/трёхместный, ПОЛУЛЮКС, ЛЮКС' +
        ('; что такое «Корпус повышенной комфортности» — вопрос (VIP-корпус №2?)' if sl.startswith('korpus') else ''),
        words=Sec._wc(p), anchor=False, photos=_nphotos, section_title=f'Наши номера → {ttl}')
_n.used = True
add('live_in_hotel', find('live_in_hotel', 'Проживание в гостинице и санатории'), '/prozhivanie/#nomera', 'Проживание · Номера в корпусах — цены', 'проживание', 'nomera',
    'прейскурант «С ПОЛНЫМ ПИТАНИЕМ» с 13.01.2026 (включая бассейн и тренажёрный зал); цены по периодам май–декабрь, для 6 категорий; в JS (js/changeprice.js) — ещё тарифы «ЛАЙТ» и «С ЗАВТРАКОМ», см. _js-data.md', price_only=True)
add('live_in_corpus1', find('live_in_corpus1', 'Проживание в гостинице и санатории'), '/prozhivanie/#nomera', 'Проживание · Номера в корпусах — контакты брони', 'проживание', 'nomera',
    'адрес и телефоны бронирования (дублируют contact.html) + текст «Коттеджи расположены…» — КОПИЯ блока со страницы corpus2 (на странице корпуса 1 опечатка «по вопросам проживания в корпусе 2»)', ph=False)
add('live_in_corpus2', find('live_in_corpus2', 'Проживание в VIP-корпусе'), '/prozhivanie/vip-korpus/', 'Главная · 5 Проживание — VIP-корпус «[Название]»', 'проживание', 'vip-korpus',
    'про сам корпус текста нет: контакты + ссылка на номера + текст «Коттеджи расположены…» (скопирован с коттеджей); название корпуса на сайте — «VIP-корпус №2»; фото корпуса — только номера (см. vip-room-photos.csv)', ph=True,
    photos=[n for n in {x['new_name'].replace('media/renamed/', '') for x in ROWS_BY_PAGE.get('live_in_corpus2', []) if x['section'] == 'vip-korpus'}])
for n in range(201, 207):
    pass
_cott_slugs = {f'cott{i}': f'kottedzh-{i}' for i in range(1, 12)}
add('live_in_cottegues', find('live_in_cottegues', 'Проживание в коттеджах'), '/prozhivanie/#kottedzhi', 'Проживание · Коттеджи (заголовок раздела)', 'страница', 'prozhivanie',
    'пустой заголовок: «Проживание в коттеджах», цены вынесены в JS', ph=False)
for a, sl in _cott_slugs.items():
    s = find('live_in_cottegues', '#' + a)
    nt = 'площадь, вместимость, расчётный час, оснащение; цены по сезонам — в _js-data.md (js/price_cottages.js)'
    if a == 'cott1':
        nt = 'ПЛОЩАДЬ 420 кв.м в HTML и 355 кв.м в JS — какая верна? ' + nt
    add('live_in_cottegues', s, f'/prozhivanie/{sl}/', 'Главная · 5 Проживание — Коттеджи', 'проживание', sl, nt)
    REDIR_ANCH.append((f'/live_in_cottegues.html#{a}', f'/prozhivanie/{sl}/', ''))
# корпус 2: номера 201–406
for n in [f'{f}0{i}' for f in (2, 3, 4) for i in range(1, 7)]:
    slug = f'corpus2-room{n}'
    s = find(slug, '[вводная часть без заголовка]')
    rows = [x for x in ROWS_BY_PAGE.get(slug, [])]
    names = sorted({x['new_name'].replace('media/renamed/', '') for x in rows if x['section'] == 'vip-korpus'})
    add(slug, s, f'/prozhivanie/vip-korpus/#nomer-{n}', 'Главная · 5 Проживание — VIP-корпус (номер)', 'проживание', f'vip-korpus-nomer-{n}',
        'текст — только слоган («Звоните и бронируйте — отдыхайте и наслаждайтесь»); фото — CSS-фоны слайдера, в md их нет: см. inventory/vip-room-photos.csv и листы vip-korpus-p01…03',
        photos=names, anchor=False, words=s.words(), ph=True)
# новогодние
add('live_in_cottegues_newyear', find('live_in_cottegues_newyear', '[вводная часть без заголовка]'), '/akcii/novyy-god-2026/', 'Главная · 9 Акции — Специальные предложения', 'акция', 'novyy-god-2026',
    'прайс коттеджей «НОВЫЙ ГОД-2026» (31.12.2025–02.01.2026) и каникулы до 08.01.2026 (в заголовке) / 11.01.2026 (в таблице) — расходятся; период прошёл', ph=False)
for a in ('price2part', 'price3part'):
    add('live_in_cottegues_newyear', find('live_in_cottegues_newyear', '#' + a), '/akcii/novyy-god-2026/', 'Главная · 9 Акции — Специальные предложения', 'акция', 'novyy-god-2026',
        'пустая якорная секция [НЕТ НА СТАРОМ САЙТЕ]', ph=False)
add('live_in_cottegues_newyear', find('live_in_cottegues_newyear', '#price4part'), '/akcii/novyy-god-2026/', 'Главная · 9 Акции — Специальные предложения', 'акция', 'novyy-god-2026',
    'таблица цен по всем коттеджам на период нового года', price_only=True, ph=False)
add('live_in_hotel_newyear', find('live_in_hotel_newyear', '[вводная часть без заголовка]'), '/akcii/novyy-god-2026/', 'Главная · 9 Акции — Специальные предложения', 'акция', 'novyy-god-2026',
    'страница-обёртка: на ней iframe pricehotel-newyear-embed.html (прайс гостиницы без питания на нов. год), собственного текста нет', ph=False)
add('pricehotel-newyear-embed', find('pricehotel-newyear-embed', '[вводная часть без заголовка]'), '/akcii/novyy-god-2026/', 'Главная · 9 Акции — Специальные предложения', 'акция', 'novyy-god-2026',
    'прайс гостиницы и санатория без питания «НОВЫЙ ГОД-2026» (31.12.2025–11.01.2026)', price_only=True, ph=False)
add('live_in_hotel-embed', find('live_in_hotel-embed', '[вводная часть без заголовка]'), '—', '— (не переносится: устаревшая iframe-версия прайса гостиницы с 01.09.2025)', 'служебное', '',
    'дубль live_in_hotel.html по структуре, но цены на сен.–дек. 2025: устарели', price_only=True, ph=False)

# ---- 6. доп. услуги: прайс раскладываем по блокам прототипа ---------
_de = find('dopuslugi-embed', '[вводная часть без заголовка]')
_dt = '\n'.join(_de.text)
_groups = [m for m in re.finditer(r'^\*\*(.+?)\*\*', _dt, re.M)]
DOP = {
    'ПРЕЙСКУРАНТ': ('—', '— (заголовок прайса)', 'служебное', '', ''),
    'ПИТАНИЕ': ('/prozhivanie/', 'Проживание · питание (блока в прототипе нет)', 'страница', 'pitanie', 'завтрак 500, обед 700, ужин 600 — одинаково для всех типов размещения'),
    'БАННЫЙ КОМПЛЕКС': ('/spa/', 'Главная · 4 СПА и банный комплекс — Дровяная баня на воде / Хамам / Финская сауна', 'страница', 'spa', 'только цены; описаний бань на сайте нет (в тексте коттеджей: «деревянная баня на воде с собственной купелью»)'),
    'СПОРТКОМПЛЕКС': ('/semyam/', 'Главная · 6 Отдых всей семьёй — Спортивный комплекс', 'страница', 'semyam', 'тренажёрный и спортзал, настольный теннис; хамам и сауна повторены из бань'),
    'БОУЛИНГ КЛУБ': ('/semyam/', 'Главная · 6 Отдых всей семьёй — Боулинг-клуб', 'страница', 'semyam', 'боулинг (2 дорожки) и бильярд'),
    'УСЛУГИ ПРАЧЕЧНОЙ': ('/prozhivanie/', 'Проживание · прочие услуги (блока в прототипе нет)', 'страница', 'prozhivanie', ''),
    'ДОПОЛНИТЕЛЬНЫЕ УСЛУГИ': ('/prozhivanie/', 'Проживание · прочие услуги (блока в прототипе нет)', 'страница', 'prozhivanie', 'животные в коттедже, стоянка и слип лодок'),
    'ДОПОЛНИТЕЛЬНЫЕ БЕСПЛАТНЫЕ УСЛУГИ': ('/prozhivanie/', 'Проживание · бесплатные услуги (блока в прототипе нет)', 'страница', 'prozhivanie', 'автостоянка, Wi-Fi, гладильная, детская комната, шезлонги, настольные игры'),
    'АРЕНДА И ПРОКАТ ЗИМНЕГО': ('/semyam/', 'Главная · 6 Отдых всей семьёй — Прокат зимой', 'страница', 'semyam', 'лыжи, коньки, санки, ватрушки, клюшки'),
    'АРЕНДА И ПРОКАТ ЛЕТНЕГО': ('/semyam/', 'Главная · 6 Отдых всей семьёй — Прокат летом', 'страница', 'semyam', 'велосипеды, ролики, самокаты, спиннинг, лодка, ракетки'),
    'АРЕНДА КОНФЕРЕНЦ-ЗАЛА': ('/meropriyatiya/', 'Главная · 7 Праздники и мероприятия — Бизнес-мероприятия', 'страница', 'meropriyatiya', 'конференц-зал до 30/60/100 человек, экран и проектор'),
    'АРЕНДА БАНКЕТНОГО ЗАЛА': ('/meropriyatiya/', 'Главная · 7 Праздники и мероприятия — Свадьбы / Дни рождения и юбилеи', 'страница', 'meropriyatiya', 'банкетный зал (ресторан, 2 этаж), барбекю, лавки для выездной регистрации, беседка'),
}
OLDURL_DOP = PAGES['dopuslugi-embed'][0]
for i, m in enumerate(_groups):
    nm = m.group(1).strip()
    end = _groups[i + 1].start() if i + 1 < len(_groups) else len(_dt)
    chunk = _dt[m.start():end]
    key = next(k for k in DOP if nm.upper().startswith(k))
    url, blk, typ, ns, nt = DOP[key]
    po = key not in ('ПРЕЙСКУРАНТ',)
    add('dopuslugi-embed', _de, url, blk, typ, ns, nt + ('' if typ != 'служебное' else 'с 01.02.2026 по 30.12.2026'), words=Sec._wc(chunk), price_only=po,
        anchor=False, ph=(key not in ('ПРЕЙСКУРАНТ',)) if typ != 'служебное' else False, photos=[], section_title='ПРЕЙСКУРАНТ на дополнительные услуги → ' + nm.title() if key != 'ПРЕЙСКУРАНТ' else 'ПРЕЙСКУРАНТ на дополнительные услуги (заголовок)')
_de.used = True
add('dopuslugi', find('dopuslugi', 'Дополнительные услуги'), '/territoriya/', 'Территория — вводный текст (и SEO-текст страниц)', 'страница', 'territoriya',
    'два абзаца: «санаторий в Рязани… чаща лесного массива, берег Оки, лечебные торфяные залежи; из Москвы на машине около 6 часов»; на странице стоит iframe с прайсом (dopuslugi-embed)', ph=True)

# ---- 7. контакты, как добраться, бронирование, документы -----------
add('contact', find('contact', 'Контакты'), '/kontakty/', 'Контакты', 'страница', 'kontakty',
    'адрес, 8 телефонов с часами, e-mail, Яндекс-карта (iframe, oid=29901253222); адрес: «с. Телебукино» (contact) и «д. Телебукино, д. 7Е» (documents) — какой верен?', ph=True)
add('contact', find('contact', 'Как до нас добраться'), '/kak-dobratsya/', 'Главная · 10 Как добраться', 'страница', 'kak-dobratsya',
    'только автобусы из Н. Новгорода, Мурома, Рязани, Москвы (автовокзалы и телефоны); про автомобиль, трансфер и схему проезда на сайте нет (в dopuslugi: «из Москвы на машине за 6 часов»)', ph=False)
add('contact', find('contact', 'Документы'), '/dokumenty/', '— (навигационные плитки на документы; не переносится)', 'служебное', '',
    'плитки-ссылки на документы (дубль documents.html); 8 картинок — карточки программ из подвала, не документы', ph=False)
add('booking', find('booking', 'Бронирование путевок'), '/bronirovanie/', 'Главная · 11 Форма «Вам перезвонить?» / страница бронирования', 'страница', 'bronirovanie',
    'текст: путёвка рекомендуется от 6 дней + телефон; сама форма — виджет frontdesk24 (pms.frontdesk24.ru, внешний, не скачивался)', ph=False)

# документы
D = 'Документы'
for a, sl, nt in [
        ('docbronirovanie', 'polozhenie-o-bronirovanii', ''),
        ('docprojivanie', 'pravila-prozhivaniya', ''),
        ('docvozvrat', 'poryadok-vozvrata-denezhnyh-sredstv', ''),
        ('docraspiska', 'raspiska-o-nesovershennoletnem', 'есть файл doc/raspiska.docx (скачан)'),
        ('docpersondata', 'soglasie-na-obrabotku-pd', 'ссылка на doc/agreement_personal_data.doc — 404; текст есть на странице'),
        ('doczaschitaprav', 'o-zashchite-prav-potrebiteley', 'без заголовка на странице; ≈13,7 тыс. слов — фактически закон; решить: переносить текстом, ссылкой или PDF'),
        ('docfreemedicine', 'programma-besplatnoy-medpomoshchi', 'без заголовка; ≈10,7 тыс. слов — тот же вопрос')]:
    s = find('documents', '#' + a)
    add('documents', s, f'/dokumenty/{sl}/', D + ' (CPT document)', 'документ', sl, nt, ph=False)
    REDIR_ANCH.append((f'/documents.html#{a}', f'/dokumenty/{sl}/', ''))
add('documents', find('documents', '#licenzias'), '/dokumenty/licenzii/', D + ' · лицензии', 'документ', 'licenzii',
    'сканы лицензий (images/licenzias/) + 54 слова названий; сканы низкого разрешения — нужны оригиналы', ph=True)
REDIR_ANCH.append(('/documents.html#licenzias', '/dokumenty/licenzii/', ''))
add('documents', find('documents', 'Документы'), '/dokumenty/', '— (навигационные плитки; не переносится)', 'служебное', '', 'плитки-ссылки на разделы документов', ph=False)

# новости
_ns = PAGES['news'][1]
cur_page, last_year = None, None
N_ITEMS = 0
seen_anchor = Counter()
for s in _ns:
    mm = re.match(r'\[news\.html\?page=(\d+)', s.title)
    if mm:
        cur_page = mm.group(1)
        s.used = True
        add('news', s, '/novosti/', '— (маркер: страница архива новостей)', 'служебное', '', f'маркер страницы news.html?page={cur_page}', anchor=False,
            old_url=f'{BASE}/news.html?page={cur_page}', ph=False)
        continue
    if s.title == '[вводная часть без заголовка]':
        s.used = True
        continue
    if not s.children:
        continue
    s.used = True
    kids = s.children
    add('news', s, '/novosti/', f'— (раздел архива, {len(kids)} новостей; блока в прототипе нет)', 'служебное', '', 'контейнер: новости переносятся поштучно (строки ниже)',
        anchor=False, old_url=f'{BASE}/news.html?page={cur_page}', status='контейнер', words=0, photos=[], ph=False, section_title=s.title)
    # собственное превью новости: «-mini» с префиксом якоря; в md оно прицеплено к предыдущему элементу
    all_lists = [c.imgs for c in kids]
    for i, c in enumerate(kids):
        own = list(c.imgs)
        if own and re.search(r'-mini\.', own[-1][1]) and i + 1 < len(kids) and kids[i + 1].anchor and own[-1][1].split('/')[-1].startswith(kids[i + 1].anchor):
            own = own[:-1]       # хвостовое превью следующей новости
        if i == 0:
            own = list(s.imgs) + own
        elif all_lists[i - 1] and re.search(r'-mini\.', all_lists[i - 1][-1][1]) and all_lists[i - 1][-1][1].split('/')[-1].startswith(c.anchor or '\0'):
            own = [all_lists[i - 1][-1]] + own
        seen_anchor[c.anchor] += 1
        dup = seen_anchor[c.anchor] > 1
        ph_n = photo_names(own)
        add('news', c, f'/novosti/{c.anchor}/', '— (в прототипе нет)', 'новость', c.anchor,
            'опубликована на двух страницах-годах (дубль): оставить одну' if dup else '', photos=ph_n, min_ph=1, old_url=f'{BASE}/news.html?page={cur_page}')
        N_ITEMS += 1
        REDIR_ANCH.append((f'/news.html?page={cur_page}#{c.anchor}', f'/novosti/{c.anchor}/', 'дубль якоря на двух страницах' if dup else ''))

# ---- 8. служебные: общие блоки и JS-данные -------------------------
for t, note in [('Шапка', 'логотип, телефон, соцсети — в ACF options темы'), ('Меню', 'структура меню старого сайта (18 пунктов), новое меню — по прототипу'),
                ('Подвал', 'подвал с соцсетями, адрес; общий на всех страницах'), ('Навигация страниц корпуса 2', 'навигация по 18 номерам — не переносится (заменяется страницей VIP-корпуса)')]:
    add('_common', find('_common', t), '—', f'— (шапка/меню/подвал темы)' if t != 'Навигация страниц корпуса 2' else '— (не переносится)', 'служебное', '', note,
        status='' if t == 'Навигация страниц корпуса 2' else 'в настройки темы',
        old_url=BASE + '/js/' + {'Шапка': 'header.js', 'Меню': 'menu.js', 'Подвал': 'footer.js'}.get(t, 'menu.js'), anchor=False, ph=False)
add('_js-data', find('_js-data', '[О файле]'), '—', '— (описание файла)', 'служебное', '', '', ph=False, old_url=BASE + '/js/', anchor=False, section_title='[О файле]')
add('_js-data', find('_js-data', 'js/changeprice.js'), '/prozhivanie/#nomera', 'Проживание · Номера в корпусах — цены по периодам и тарифам', 'проживание', 'nomera',
    'тарифы «С ЗАВТРАКОМ И УЖИНОМ (ЛАЙТ)» и «С ЗАВТРАКОМ»; на странице видны только май–июнь; полное питание — в HTML live_in_hotel', price_only=True, ph=False, old_url=BASE + '/js/changeprice.js', anchor=False)
add('_js-data', find('_js-data', 'js/price_cottages.js'), '/prozhivanie/#kottedzhi', 'Проживание · Коттеджи — цены по сезонам', 'проживание', 'kottedzhi',
    'все 11 коттеджей × сезоны (зима/весна/лето/осень × будни/выходные) + доп. место; коттедж №1 — 355 кв.м (в HTML 420); период в JS «09.01.2025–30.12.2025», сезоны подписаны 2026', price_only=True, ph=False, old_url=BASE + '/js/price_cottages.js', anchor=False)
add('_js-data', find('_js-data', 'js/price_programs.js'), '/programmy/', 'Лечение · Программы — цены «от»', 'программа', 'programmy',
    'цены «от» руб/сутки по 14 программам + «Основная оздоровительная» и «Бронирование коттеджей»', price_only=True, ph=False, old_url=BASE + '/js/price_programs.js', anchor=False)
add('_js-data', find('_js-data', 'js/meduslugi.js'), '/procedury/', 'Лечение · Процедуры — прайс-лист (с 01.02.2026)', 'процедура', 'procedury',
    'прайс 17 групп процедур построчно (номер, услуга, цена); раскладывается по карточкам процедур (поле price_list)', price_only=True, ph=False, old_url=BASE + '/js/meduslugi.js', anchor=False)
add('_js-data', find('_js-data', 'akcias/show_akcias_text.js'), '/akcii/', 'Главная · 9 Акции — Подарочный сертификат / ЕЦК / Специальные предложения', 'акция', 'akcii',
    '3 акции с текстами: ЕЦК (скидка 3% / 5%), подарочный сертификат на 5400 руб (состав), специальное предложение; картинки 690×591', ph=True, old_url=BASE + '/akcias/show_akcias_text.js', anchor=False)
add('_js-data', find('_js-data', 'otzivs/show_otzivs_text.js'), '/otzyvy/', 'нет блока в прототипе (отзывы)', 'отзыв', 'otzyvy',
    '34 отзыва с именем, датой и оценкой, 25 аватарок; на странице заявлено 653 отзыва (4.9)', ph=False, old_url=BASE + '/otzivs/show_otzivs_text.js', anchor=False)

# ---- 9. всё, что без текста и осталось: баннеры шапок ---------------
for slug, (u, secs) in PAGES.items():
    for s in secs:
        if s.used or any(c.used for c in s.children):
            continue
        if s.title == '[вводная часть без заголовка]' and s.words() < 8:
            add(slug, s, '—', '— (баннер шапки старой страницы; не переносится)', 'служебное', '', 'на странице: картинка-баннер (images/index2.png и т.п.)', ph=False, anchor=False)
            continue
        if s.title.startswith('Документы') and slug == 'documents':
            continue
        raise SystemExit(f'не покрыта секция: {slug} → {s.title!r} (w={s.words()})')

# ---- 10. страницы и файлы вне md ------------------------------------
OUT.append(dict(old_url=BASE + '/virtual.html', old_section='(страница не скачана: Disallow в robots.txt)', new_url='/territoriya/#virtualnyy-tur', new_slug='territoriya',
                proto_block='Главная · 8 Территория (виртуальный тур)', type='страница', status='текста нет', words=0, photos=0, photos_low_res=0, photo_files='',
                note='содержимое неизвестно; нужен URL тура от санатория'))
OUT.append(dict(old_url=BASE + '/doc/raspiska.docx', old_section='файл (скачан в raw/site/.../doc/)', new_url='/dokumenty/raspiska-o-nesovershennoletnem/', new_slug='raspiska-o-nesovershennoletnem',
                proto_block=D + ' (вложение)', type='документ', status='текст есть', words=0, photos=0, photos_low_res=0, photo_files='', note='docx не разбирался; текст расписки есть на documents.html#docraspiska'))
OUT.append(dict(old_url=BASE + '/doc/agreement_personal_data.doc', old_section='файл (404 на старом сайте)', new_url='/dokumenty/soglasie-na-obrabotku-pd/', new_slug='soglasie-na-obrabotku-pd',
                proto_block=D + ' (вложение)', type='документ', status='текста нет', words=0, photos=0, photos_low_res=0, photo_files='', note='файл не отдаётся; текст согласия есть на documents.html#docpersondata'))

# ================================================================ запись
FIELDS = ['old_url', 'old_section', 'new_url', 'new_slug', 'proto_block', 'type', 'status', 'words', 'photos', 'photos_low_res', 'photo_files', 'note']
with open(INV / 'content-map.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, FIELDS)
    w.writeheader()
    w.writerows(OUT)

# ---------------------------------------------------------------- редиректы
broken = {r['url'].replace(BASE, ''): r for r in csv.DictReader(open(INV / 'broken-links.csv', encoding='utf-8-sig'))}
BROKEN = OrderedDict([
    ('/program_covid.html', ('/programmy/profilaktika-reabilitaciya-covid-19/', 'ссылка была в закомментированном блоке главной (карточка «Профилактика и реабилитация COVID-19»)')),
    ('/program_child_svo.html', ('/programmy/', 'ссылка в закомментированном слайдере главной; точная программа неясна («дети + СВО»?)')),
    ('/contacts.html', ('/kontakty/', 'ссылка «КОНТАКТЫ» на страницах corpus2/room*.html (опечатка: страница называется contact.html)')),
    ('/exkursii.html', ('/territoriya/', 'закомментированная карточка «Экскурсии» на rooms.html; в новой структуре страницы экскурсий нет — уточнить')),
    ('/price_corpus2.html', ('/prozhivanie/vip-korpus/', 'ссылка «НАЗАД» на страницах corpus2/room*.html')),
    ('/newsite/booking.html', ('/bronirovanie/', 'адрес возврата виджета бронирования frontdesk24 (js/frontdesk.js)')),
    ('/bron_san/index.php', ('/bronirovanie/', 'старая система бронирования; ссылки закомментированы в live_in_cottegues_newyear')),
])
for p in BROKEN:
    assert p in broken, p
assert len(BROKEN) == sum(1 for r in broken.values() if r['type'] == 'страница')

RFIELDS = ['old_url', 'kind', 'new_url', 'action', 'note']
rr = []
for p, (u, n) in PAGE_REDIRECT.items():
    rr.append(dict(old_url=p, kind='страница', new_url=u, action='301', note=n))
rr.append(dict(old_url='/news.html?page=01', kind='страница (query)', new_url='/novosti/', action='301', note='то же для page=02…04; в nginx/Redirection учесть параметр query'))
for p, (u, n) in BROKEN.items():
    rr.append(dict(old_url=p, kind='битая страница (404 на старом сайте)', new_url=u, action='301 (необязательно)', note=n))
rr.append(dict(old_url='/doc/raspiska.docx', kind='файл', new_url='/dokumenty/raspiska-o-nesovershennoletnem/', action='301 (после импорта; файл в медиатеке)', note=''))
rr.append(dict(old_url='/doc/agreement_personal_data.doc', kind='битый файл (404)', new_url='/dokumenty/soglasie-na-obrabotku-pd/', action='301 (необязательно)', note='файл не отдавался; текст согласия есть на новом сайте'))
_seen = OrderedDict()
for old, new, n in REDIR_ANCH:
    if old in _seen:      # якорь повторяется на старой странице: остаётся первая по порядку цель
        _seen[old][2] = 'якорь повторяется на старой странице; ведёт на первую по порядку цель'
        continue
    _seen[old] = [old, new, n]
for old, new, n in _seen.values():
    rr.append(dict(old_url=old, kind='якорь', new_url=new, action='JS (фрагмент до сервера не доходит)', note=n))
with open(INV / 'redirects.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, RFIELDS)
    w.writeheader()
    w.writerows(rr)

# ---------------------------------------------------------------- фото номеров VIP-корпуса
FP = ['room', 'old_page', 'new_name', 'width', 'height', 'flags', 'dup_group', 'sheet', 'source_url']
sec_names = sorted({r['new_name'].replace('media/renamed/', '') for r in csv.DictReader(open(INV / 'images.csv', encoding='utf-8-sig')) if r['section'] == 'vip-korpus'})
vrows = []
for n in [f'{f}0{i}' for f in (2, 3, 4) for i in range(1, 7)]:
    for x in ROWS_BY_PAGE.get(f'corpus2-room{n}', []):
        nm = x['new_name'].replace('media/renamed/', '')
        if x['section'] != 'vip-korpus':
            continue
        idx = sec_names.index(nm)
        pp = idx // 48 + 1
        pr = IMGINFO.get(nm, x)
        vrows.append(dict(room=n, old_page=f'{BASE}/corpus2/room{n}.html', new_name=nm, width=x['width'], height=x['height'], flags=x['flags'],
                          dup_group=x['dup_group'], sheet=f'vip-korpus-p{pp:02d}.jpg', source_url=x['source_url']))
with open(INV / 'vip-room-photos.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, FP)
    w.writeheader()
    w.writerows(vrows)

# ---------------------------------------------------------------- итоги
sys.stdout.reconfigure(encoding='utf-8')
print('строк карты:', len(OUT), '| редиректов:', len(rr), '(якорей:', len(REDIR_ANCH), ') | фото VIP-номеров:', len(vrows))
print('по типам:', dict(Counter(r['type'] for r in OUT)))
print('по статусам:', dict(Counter(r['status'] for r in OUT)))
