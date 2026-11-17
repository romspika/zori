# Модель данных нового сайта (предложение)

Тема WordPress не передана (`theme/` пуста), поэтому модель предлагается по прототипу и карте контента. Это отправная точка для этапов 5–6: названия типов записей и полей можно менять, пока не написан `build_json.py`. Тему и плагины здесь не создаём.

**Как читать.** «Источник» — где на старом сайте лежит материал (строки `inventory/content-map.csv`). «Нужно» — чего на старом сайте нет, ставится `[НЕТ НА СТАРОМ САЙТЕ]`, вопрос — в `inventory/questions.md`.

## 1. Общие правила

- **Ключ записи — slug** (латиница). Импорт идемпотентен: повторный запуск обновляет запись по паре (post_type, slug).
- Адреса: страницы — `/slug/`; записи — `/procedury/<slug>/`, `/programmy/<slug>/`, `/prozhivanie/<slug>/`, `/akcii/<slug>/`, `/dokumenty/<slug>/`, новости — `/novosti/<slug>/`. Slug'и предварительные, утвердим позже (`redirects.csv`).
- Поля в духе **ACF** (имя поля — латиницей, тип в скобках). Общие поля для всех страниц и записей:

| поле | тип | комментарий |
|---|---|---|
| `hero_title` | text | по умолчанию — заголовок записи |
| `hero_subtitle` | text | |
| `hero_image` | image | |
| `seo_title`, `seo_description` | text | плагин SEO уточнит; на старом сайте пригодного нет (16 из 42 title одинаковые) |
| `seo_text` | wysiwyg | «SEO-текст внизу» (блок 9 шаблона процедуры); на старом сайте нет |
| `legacy_urls` | textarea | старые адреса (по одному в строке) — для редиректов |
| `old_source` | text | ключ строки карты: `old_url#якорь` (служебное, для сверки) |

- **Фото**: поле `gallery` (gallery) и `*_image` (image) заполняются файлами из `media/renamed/<раздел>/…`. Раздел = slug новой страницы или блока: `glavnaya`, `lechenie` (хаб), `programmy`, `procedury`, `spa`, `oborudovanie`, `medkabinety`, `nomera`, `kottedzhi`, `vip-korpus`, `semyam`, `akcii`, `afisha`, `dokumenty`, `kontakty`, `otzyvy`, `novosti`, `prozhivanie`; `obshchee` и `_icons` — декор и иконки. `alt` на старом сайте нет ни у одного фото: пишется заново (поле `alt` у каждого изображения обязательно).
- **Цены** хранятся строками повторителя, не текстом. Период действия — отдельное поле (`price_date`).

## 2. Таксономии

| таксономия | для | термины (предложение) |
|---|---|---|
| `procedure_group` | procedure | `lechenie` (основные медуслуги), `izyuminki`, `spa`, `kosmetologiya`, `diagnostika` |
| `program_profile` | program | `oporno-dvigatelnyy`, `serdtse`, `dykhanie`, `deti`, `svo-semi`, `profsoyuzy`, `ozdorovlenie` |
| `accommodation_type` | accommodation | `nomer` (номера в корпусах), `kottedzh`, `vip-korpus` |
| `faq_group` | faq | `podgotovka-k-zaezdu`, `oplata-i-bronirovanie`, `lechenie`, `pitanie`, `deti-i-zhivotnye`, `dokumenty` |
| `document_type` | document | `dogovornye`, `pravila`, `normativnye-akty`, `licenzii` |
| `promo_type` | promo | `ecp`, `sertifikat`, `specpredlozhenie`, `sezonnoe` |
| категории WP | post (новости) | по годам или темам; решение — после ответа на вопрос A23 |

## 3. Типы записей

### 3.1 `procedure` — процедура / медуслуга (`/procedury/<slug>/`, архив `/procedury/`)

Шаблон — «Грязелечение» (`/procedury/gryazelechenie/`). Записей по карте: **24** (17 из «Медуслуг» + 7 из «Изюминок», из них 2 дубля, итого 22 уникальных; соляная пещера и косметология — группа СПА).

| поле | тип | блок шаблона | источник / нужно |
|---|---|---|---|
| заголовок записи | title | 1 Hero | h2 секции |
| `hero_image` | image | 1 Hero | по одному фото на процедуру (порядок «зигзагом», см. README) |
| `short_description` | textarea | карточка на главной и в каталоге | `home` «Основные медицинские услуги» (одна строка на процедуру) |
| `about_text` | wysiwyg | 2 О методе | основной текст секции |
| `about_badges` | repeater (`title`, `text`) | 2 О методе | для грязелечения: «Сапожковская торфяная грязь», «Собственный участок добычи» — есть в тексте |
| `kinds` | repeater (`name`, `description`) | 3 Виды процедур | списки «Методики…» в тексте; для грязелечения — аппликации, электрогрязь (обёртываний на сайте нет) |
| `steps` | repeater (`title`, `text`) ×4 | 4 Как проходит лечение | **нет**: Консультация врача / Подготовка / Процедура / Отдых. Общий шаблон шагов — в опциях (`options.procedure_steps`) |
| `indications` | wysiwyg | 5 Показания | часть процедур — одной фразой; по каждой процедуре нужна медицинская правка |
| `contraindications` | wysiwyg | 5 Противопоказания | общий список — в FAQ; **нет** по процедурам |
| `doctor` | post_object → doctor | 6 Врач | **нет** (врачей на сайте нет) |
| `price_date` | text | 7 Стоимость | «с 01 февраля 2026» (`js/meduslugi.js`) |
| `price_list` | repeater (`num`, `service`, `price`, `note`) | 7 Стоимость | `_js-data.md` (`meduslugi`) и таблицы в секции; ≈100 позиций |
| `related_programs` | relationship → program | 7 Программы | выводится из текстов программ (какие процедуры в них входят) |
| `question_title` | text | 8 Форма «Вопрос о …?» | по умолчанию «Вопрос о [название]?» |
| `seo_text` | wysiwyg | 9 SEO | нет |
| `gallery` | gallery | — | фото из секции, если есть |
| `featured_home` | true/false | главная, блок «Лечение» | ставится руками |
| `menu_order` | число | порядок | порядок на старой странице |

Дубли, которые нужно слить при импорте: «Косметологические услуги» (`meduslugi#cosmeticuslugi` и `izuminki#cosmetology`, тексты разные) и «Озонотерапия» (идентичны).

### 3.2 `program` — программа лечения (`/programmy/<slug>/`, архив `/programmy/`)

Записей: **14** (`programms_treatment`). На главной 4 карточки: Гибкий позвоночник, Здоровое сердце, Свободное дыхание, Путёвка выходного дня (`featured_home`).

| поле | тип | источник / нужно |
|---|---|---|
| заголовок | title | h2 секции |
| `hero_image` | image | по одному фото на программу (1724×1400, не low_res) |
| `short_description` | textarea | первый абзац секции |
| `description` | wysiwyg | основной текст |
| `included` | repeater (`group`, `items`) | перечень процедур программы из текста |
| `indications`, `contraindications` | wysiwyg | в тексте программ «показания» встречаются 29 раз, «противопоказания» 10 — разнести по полям |
| `price_from` | number | `js/price_programs.js` («от», руб/сутки), на главной тот же перечень |
| `price_unit` | text | «руб/сутки» (у «Путёвки выходного дня» — «руб») |
| `min_days` | number | «путёвка рекомендуется от 6 дней» (`booking`), «менее 7 дней не реализуются» (FAQ) — уточнить |
| `profile` | taxonomy `program_profile` | |
| `related_procedures` | relationship → procedure | |
| `featured_home` | true/false | 4 карточки на главной |
| `lite_prices` | repeater | только у «Лайт»: цены по категориям номеров и периодам (`js/changeprice.js`), либо ссылка на accommodation |

### 3.3 `accommodation` — проживание (`/prozhivanie/<slug>/`)

Записей: **6 типов номеров** + **11 коттеджей** + **1 VIP-корпус** (с повторителем 18 номеров) = **18**.

| поле | тип | комментарий / источник |
|---|---|---|
| заголовок | title | «Коттедж №1», «Двухместный номер», «VIP-корпус «[Название]»» |
| `type` | taxonomy `accommodation_type` | |
| `description` | wysiwyg | текст секции (коттеджи — «К вашим услугам…») |
| `area_m2` | number | коттедж №1: 420 (HTML) / 355 (JS) — вопрос B4 |
| `capacity` | number | «14 (+доп. место)» |
| `extra_bed` | true/false | «+доп.место» |
| `check_in`, `check_out` | text | «14:00», «12:00» (у коттеджей) |
| `amenities` | repeater (`item`) | «Кухня, гостиная с камином, 7 спален…» — разбор списка при подготовке текстов |
| `equipment_list` | textarea | «Оборудование коттеджа: …» |
| `gallery` | gallery | у коттеджей 4–10 фото на каждый; у номеров 15 фото общим списком на тип-страницу (соответствие по листу `nomera.jpg`) |
| `price_table` | repeater (`period`, `weekday`, `weekend`, `extra_bed`) | коттеджи: сезоны ЗИМА/ВЕСНА/ЛЕТО/ОСЕНЬ × будни/выходные (`js/price_cottages.js`) |
| `price_by_period` | repeater (`tariff`, `category`, `placement`, `period`, `price`) | номера: тарифы «Полное питание», «Лайт», «С завтраком» × размещение × месяцы (`live_in_hotel`, `js/changeprice.js`) |
| `price_date` | text | «с 13.01.2026» |
| `rooms` | repeater (`number`, `floor`, `slogan`, `gallery`) | только VIP-корпус: 18 номеров 201–406; фото — `inventory/vip-room-photos.csv` |
| `external_url` | url | ссылка на отдельный сайт VIP-корпуса (позже) |
| `booking_url` | url | виджет бронирования |
| `featured_home` | true/false | блок «Проживание» на главной (номера / коттеджи / VIP) |

### 3.4 `promo` — акция (`/akcii/<slug>/`, архив `/akcii/`)

Записей: **3** активных (`akcias`) + новогодние предложения 2026 (`novyy-god-2026`, период прошёл — вопрос C3).

| поле | тип | источник |
|---|---|---|
| заголовок | title | «В санаторий со скидкой по ЕЦК», «Подарочный сертификат на сумму 5400 руб», «Специальные предложения» |
| `type` | taxonomy `promo_type` | |
| `short_text`, `conditions` | textarea / wysiwyg | тексты в `_js-data.md` |
| `price` | number | 5400 (сертификат) |
| `discount_text` | text | «3% на программу, 5% на проживание» (ЕЦК) |
| `includes` | repeater (`group`, `items`) | состав сертификата (массаж, водолечение, вибро-механотерапия…) |
| `valid_from`, `valid_to` | date | «до 31 декабря» (ЕЦК) |
| `image` | image | `akcii-01…06`, 500–690 px (low_res) |
| `cta_text`, `cta_url` | text, url | |

### 3.5 `faq` — вопрос-ответ (без отдельных страниц; выводится на `/voprosy-otvety/`)

Записей: **18** (`questions`; `home` дублирует вопрос №3).

| поле | тип | |
|---|---|---|
| заголовок | title | вопрос |
| `answer` | wysiwyg | ответ дословно |
| `group` | taxonomy `faq_group` | |
| `show_in_prepare` | true/false | показывать в блоке «Как подготовиться к заезду» (вопросы: документы, санаторно-курортная карта, СНГ, дополнительное место, животные) |
| `menu_order` | число | порядок на старой странице |

### 3.6 `doctor` — врач

Записей: **0** на старом сайте. Заготовка под блок 6 шаблона процедуры.

| поле | тип | |
|---|---|---|
| заголовок | title | ФИО |
| `position`, `speciality` | text | |
| `experience` | text | |
| `photo` | image | |
| `bio` | wysiwyg | |
| `procedures` | relationship → procedure | |
| `consent_publish` | true/false | согласие на публикацию (обязательно) |

### 3.7 `document` — документ (`/dokumenty/<slug>/`, архив `/dokumenty/`)

Записей: **7** + лицензии (`licenzii`).

| поле | тип | источник |
|---|---|---|
| заголовок | title | |
| `type` | taxonomy `document_type` | |
| `body` | wysiwyg | текст документа (дословно) |
| `file` | file | `doc/raspiska.docx` (есть); согласие ПД (файл 404 — только текст) |
| `scans` | gallery | только `licenzii`: сканы (images/licenzias/, 8 шт.) |
| `show_in_footer` | true/false | |

Два федеральных акта (`o-zashchite-prav-potrebiteley`, `programma-besplatnoy-medpomoshchi`, ≈24 тыс. слов) — вопрос A24: текстом, PDF или ссылкой.

### 3.8 Необязательные (после ответов на вопросы A22–A23)

- `review` — отзыв: `author`, `date`, `rating`, `text`, `avatar`, `source` (34 шт. в JS; либо виджет myreviews.dev).
- Записи WP `post` — новости: `date` (из старой даты), `gallery`, анкор-slug (145 шт.; 4 дубля на двух страницах-годах).

## 4. Страницы

Каждая страница — шаблон с блоками; ниже поля блоков. Имена блоков — как в прототипе.

### `home` — Главная (`/`)

| блок | поля | источник |
|---|---|---|
| 1 Hero | `hero_title`, `hero_subtitle`, `slides` (gallery), `stats` (repeater `value`, `label`) | 11 фото `glavnaya`; цифры — **утвердить** (B3) |
| 2 Какой отдых вам нужен | `audiences` (repeater ×4: `title`, `text`, `link`, `image`) | нет (A2) |
| 3 Лечение | `mud_*` (заголовок, текст, фото, ссылка), `diagnostics_*`, `procedures_featured` (relationship ≤6), `programs_featured` (relationship ×4) | `home`, `lechenie`; программы и процедуры — из записей |
| 4 СПА и банный комплекс | `spa_cards` (relationship → `spa`-страница / procedure) | карточки собираются со страницы `spa` |
| 5 Проживание | `accommodation_featured` (relationship ×3: номера / коттеджи / VIP) | |
| 6 Отдых всей семьёй | `family_cards` (из страницы `semyam`) | |
| 7 Праздники и мероприятия | `event_cards` (из страницы `meropriyatiya`) | |
| 8 Территория | `territory_*` (текст, «10 гектаров» — число утвердить, фото, `virtual_tour_url`) | |
| 9 Акции | `promos_featured` (relationship ×3) | |
| 10 Подготовка к заезду / Как добраться | `prepare_cards`, ссылка на `kak-dobratsya` | |
| 11 Форма «Вам перезвонить?» | берётся из опций (`options.callback_form`) | нет формы на старом сайте |

### `lechenie` — Лечение (`/lechenie/`)

`profile_text`; `mud_block` (title, text, badges, image); `diagnostics_text`; **`equipment`** — повторитель аппаратов (`name`, `description`, `image`, `procedure` → procedure): 8 шт. (`programms_equipment`), по 1 фото; `medcabinets_gallery` (26 фото, ≤900 px); `procedures_featured`; `programs_featured`; `seo_text`.

### `spa` — СПА и банный комплекс (`/spa/`)

`intro`; `facilities` — повторитель (`title`, `description`, `image`, `prices` (повторитель: `service`, `capacity`, `price`, `extra_person`, `extra_hour`)) для бани на воде, хамама, финской сауны (**только цены**, A5); `procedures` (relationship → соляная пещера, косметология, группа `spa`); `seo_text`.

### `prozhivanie` — Проживание (`/prozhivanie/`)

`intro`; карточки по `accommodation_type` (выводятся из записей); `meals` (текст, `prices`: завтрак 500 / обед 700 / ужин 600 — нужно описание питания, A21); `extra_services` (прачечная, животные в коттедже 650, стоянка и слип лодок); `free_services` (автостоянка, Wi-Fi, гладильная, детская комната, шезлонги, настольные игры); `contacts_booking` (телефоны брони).

### `semyam` — Отдых всей семьёй (`/semyam/`)

`sports` (текст, фото, `prices`: тренажёрный зал 500, спортзал 2500, настольный теннис 500); `bowling` (боулинг 1500/час на 2 дорожки, бильярд 500); `rental_winter` (6 позиций проката); `rental_summer` (13 позиций); всё — **только цены** (A9).

### `meropriyatiya` — Праздники и мероприятия (`/meropriyatiya/`)

`event_types` — повторитель ×4: Свадьбы / Бизнес-мероприятия / Дни рождения и юбилеи / Семейные и детские праздники (`title`, `text`, `image`, `prices`); цены есть для конференц-зала (до 30 / 30–60 / 50–100 чел., экран+проектор), банкетного зала (1000 руб/чел.), барбекю, лавок для выездной регистрации, беседки; описаний нет (A10).

### `territoriya` — Территория (`/territoriya/`)

`intro` (из `rooms` и `dopuslugi`), `hectares` (число, A11), `infrastructure` — повторитель (`title`, `text`, `image`), `virtual_tour_url` (после ответа B1), `gallery`.

### `kak-dobratsya` — Как добраться и подготовиться (`/kak-dobratsya/`)

`routes` — повторитель (`from`, `station`, `phone`): Н. Новгород, Муром, Рязань, Москва (`contact`); `by_car` (текст, координаты — нет); `transfer` (нет); `prepare` — чек-лист (`title`, `text`) и ссылки на FAQ-вопросы с `show_in_prepare`; «документы для заселения» — одна строка из `home`.

### Остальные

| страница | что |
|---|---|
| `kontakty` | выводит поля опций (адрес, телефоны, e-mail, карта); Яндекс-карта `oid=29901253222` (iframe, не качали) |
| `voprosy-otvety` | список `faq` по группам |
| `bronirovanie` | текст («путёвка рекомендуется от 6 дней») + виджет frontdesk24 (`options.booking_widget`) |
| `dokumenty` | архив `document` |
| `novosti` | страница записей WP (после решения A23) |

## 5. Опции сайта (ACF Options page «Санаторий»)

| группа | поля |
|---|---|
| Контакты | `address`, `phones` (repeater: `label`, `number`, `hours`, `free_for`), `email`, `work_hours`, `map_oid` |
| Соцсети | ссылки (`js/footer.js`) |
| Цифры | `stat_programs`, `stat_procedures`, `stat_hectares`, `stat_beds` — **утвердить** (B3) |
| Формы | `callback_form` (заголовок, текст, согласие на обработку ПД, адресат — вопрос A15), `question_form_text` |
| Бронирование | `booking_widget` (код frontdesk24 или ссылка) |
| Процедуры | `procedure_steps` (4 шага «Как проходит лечение») |
| Подвал | `footer_text`, `footer_docs` (relationship → document) |

Телефоны на старом сайте (всего 107 вхождений, значимых ≈10): +7 (985) 770-09-69 (бесплатно для Москвы и МО), 8 (910) 610-01-92 (МТС, бесплатно для Рязанской обл.), (49131) 4-52-06 / 4-52-07 / 4-52-08 / 4-52-23, 8-910-610-01-93 (запись на медпроцедуры), e-mail telebukino-2012@mail.ru — все в `inventory/facts.csv`.

## 6. Что понадобится для `build_json.py` (этап 6)

Формат JSON (ключ — slug): `{post_type, slug, title, status, acf{поле: значение}, taxonomies{…}, media[{field, file, alt}], legacy_urls[], old_source}`. Валидация: обязательные поля (title, slug, тип) заполнены; все файлы из `media/renamed/` существуют; `alt` не пустой; slug уникален внутри типа; ссылки relationship ведут на существующие slug'и.
