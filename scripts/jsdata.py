"""Данные из JS-массивов сайта (цены, медуслуги, акции, отзывы) — полностью, включая то, что на странице
не отрисовано (другие периоды цен, закомментированные таблицы коттеджей, слайды за кадром).
Используется из extract.py -> content/old/_js-data.md. Подписи строк в таблицах цен гостиницы — из комментариев JS
(других подписей у массивов нет); это помечено в файле."""
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / 'raw' / 'site' / 'kasimovskie-zori.ru'
FILES = ['js/changeprice.js', 'js/price_cottages.js', 'js/price_programs.js', 'js/meduslugi.js',
         'akcias/show_akcias_text.js', 'otzivs/show_otzivs_text.js']
# где используется (для навигации)
USED_ON = {
    'js/changeprice.js': 'live_in_hotel.html, programms_treatment.html',
    'js/price_cottages.js': 'live_in_cottegues.html, live_in_corpus1.html, live_in_corpus2.html',
    'js/price_programs.js': 'почти все страницы (функция show_price_program)',
    'js/meduslugi.js': 'programms_meduslugi.html',
    'akcias/show_akcias_text.js': 'index.html (блок «Действующие акции»)',
    'otzivs/show_otzivs_text.js': 'index.html (блок отзывов)',
}


def read(rel):
    b = (SITE / rel).read_bytes()
    if b.startswith(b'\xef\xbb\xbf'):
        return b.decode('utf-8-sig', 'replace')
    try:
        return b.decode('utf-8')
    except UnicodeDecodeError:
        return b.decode('cp1251')


class P:
    """Мини-парсер JS-литералов: строки, числа, массивы; комментарии собираются как подписи элементов."""
    def __init__(self, s, i):
        self.s, self.i = s, i

    def ws(self):
        comments = []
        s = self.s
        while self.i < len(s):
            c = s[self.i]
            if c in ' \t\r\n﻿':
                self.i += 1
            elif s.startswith('//', self.i):
                j = s.find('\n', self.i)
                j = len(s) if j < 0 else j
                comments.append(s[self.i + 2:j].strip())
                self.i = j
            elif s.startswith('/*', self.i):
                j = s.find('*/', self.i + 2)
                comments.append(s[self.i + 2:j].strip())
                self.i = j + 2
            else:
                break
        return [c for c in comments if c]

    def value(self):
        self.ws()
        c = self.s[self.i]
        if c == '[':
            return self.array()
        if c in '"\'':
            return self.string()
        m = re.compile(r'-?[\d.]+|true|false|null|[\w.]+').match(self.s, self.i)
        self.i = m.end()
        return m.group(0)

    def string(self):
        q = self.s[self.i]; self.i += 1
        out = []
        while True:
            c = self.s[self.i]
            if c == '\\':
                n = self.s[self.i + 1]
                out.append({'n': '\n', 't': '\t', 'r': ''}.get(n, n)); self.i += 2
            elif c == q:
                self.i += 1
                break
            else:
                out.append(c); self.i += 1
        s = ''.join(out)
        # конкатенация 'a' + 'b'
        save = self.i
        self.ws()
        if self.i < len(self.s) and self.s[self.i] == '+':
            self.i += 1; self.ws()
            if self.s[self.i] in '"\'':
                return s + self.string()
        self.i = save
        return s

    def array(self):
        self.i += 1
        items, labels = [], []
        while True:
            com = self.ws()
            if self.s[self.i] == ']':
                self.i += 1
                return Arr(items, labels)
            if self.s[self.i] == ',':
                self.i += 1
                continue
            items.append(self.value())
            labels.append(com)


class Arr(list):
    def __init__(self, items, labels):
        super().__init__(items)
        self.labels = labels


def arrays_in(text):
    """{name: (value, comments_before_var)} — последнее определение побеждает (как в браузере)."""
    out = {}
    for m in re.finditer(r'var\s+(\w+)\s*=\s*', text):
        j = m.end()
        while j < len(text) and text[j] in ' \t\r\n':
            j += 1
        if j >= len(text) or text[j] not in '["\'':
            continue
        pre = text[max(0, m.start() - 300):m.start()]
        pre_c = re.findall(r'//\s*(.+)', pre.split(';')[-1])
        try:
            p = P(text, j)
            out[m.group(1)] = (p.value(), [c.strip() for c in pre_c])
        except Exception as e:                                   # noqa
            out[m.group(1)] = (f'[не разобрано: {e}]', [])
    return out


IMG = re.compile(r'^[\w/.-]+\.(jpe?g|png|gif|webp)$', re.I)


def build(Section, html_to_md):
    secs = []
    intro = Section(2, '[О файле]')
    intro.blocks.append('Полные данные массивов из JS сайта. На страницах часть этих данных не видна без клика '
                        '(другие периоды цен), закомментирована в HTML (таблицы цен большинства коттеджей) '
                        'или вставляется по одной позиции. Текст значений — дословно; HTML внутри строк переведён в markdown.')
    secs.append(intro)
    for rel in FILES:
        data = arrays_in(read(rel))
        top = Section(2, f'{rel}')
        top.blocks.append(f'Используется: {USED_ON.get(rel, "?")}')
        secs.append(top)
        scalars = [(k, v) for k, (v, _) in data.items() if isinstance(v, str)]
        if scalars:
            top.blocks.append('\n'.join(f'- `{k}` = {html_to_md(v)}' for k, v in scalars))
        one_d = {k: v for k, (v, _) in data.items() if isinstance(v, list) and v and all(isinstance(x, str) for x in v)}
        for name, (val, pre) in data.items():
            if not isinstance(val, list) or not val:
                continue
            if all(isinstance(x, str) for x in val):
                used_as_header = 'period' in name.lower() and any(k.lower().startswith('pricein') for k in data)
                if not used_as_header and not all(IMG.match(x) for x in val if x):
                    s = Section(3, f'`{name}`' + (f' — {" / ".join(pre)}' if pre else ''))
                    s.blocks.append('\n'.join(f'- {html_to_md(x)}' for x in val))
                    secs.append(s)
                continue
            rows = [r for r in val if isinstance(r, list)]
            s = Section(3, f'`{name}`' + (f' — {" / ".join(pre)}' if pre else ''))
            secs.append(s)
            first = rows[0]
            has_header = all(isinstance(c, str) and c and len(c) < 40 and not re.fullmatch(r'[\d\s.,]+', c) for c in first)                 and len({len(r) for r in rows}) == 1 and len(rows) > 1
            long = not has_header and any(isinstance(c, str) and len(c) > 150 for r in rows for c in r)
            if long:                                            # записи (акции, отзывы)
                for n, r in enumerate(rows, 1):
                    lines = []
                    for c in r:
                        if isinstance(c, list):
                            c = ', '.join(x for x in c if x)
                        if not c:
                            continue
                        if IMG.match(c):
                            s.images.setdefault('https://kasimovskie-zori.ru/' + c, ('', 'js', ''))
                            lines.append(f'`{c}`')
                        else:
                            lines.append(html_to_md(c))
                    s.blocks.append(f'**[{n}]**  \n' + '  \n'.join(lines))
                continue
            ncol = max(len(r) for r in rows)
            # заголовок: одномерный массив периодов той же длины (changeprice) или первая строка-шапка
            header = None
            for k, v in one_d.items():
                if 'period' in k.lower() and len(v) == ncol and name.lower().startswith('pricein') and \
                        k.lower().replace('priceperiods', '') == name.lower().replace('priceinperiod', ''):
                    header = [html_to_md(x).replace('  \n', ' ') for x in v]
            body = rows
            labels = list(getattr(val, 'labels', [[]] * len(rows)))
            label_col = any(labels[1:]) if len(labels) > 1 else False
            if header is None:
                header, body, labels = [html_to_md(str(x)) for x in rows[0]], rows[1:], labels[1:]
            cat, lab = '', ''
            md = []
            if label_col:
                s.blocks.append('_Подписи строк — из комментариев в JS (на странице те же категории/размещения)._')
                header = ['строка (из комментария JS)'] + header
            md.append('| ' + ' | '.join(h.replace('|', '\\|') for h in header) + ' |')
            md.append('|' + '---|' * len(header))
            for r, com in zip(body, labels):
                cells = [html_to_md(str(c)).replace('  \n', ' <br> ').replace('|', '\\|') for c in r]
                cells += [''] * (len(header) - len(cells) - (1 if label_col else 0))
                if label_col:
                    for c in com:
                        if re.match(r'^\d+\s*-', c):
                            lab = re.sub(r'^\d+\s*-\s*', '', c)
                        else:
                            cat = c
                    cells = [f'{cat} / {lab}' if cat else lab] + cells
                md.append('| ' + ' | '.join(cells) + ' |')
            s.blocks.append('\n'.join(md))
    return secs
