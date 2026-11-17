<?php
/**
 * Страница «Новый год 2027» — посадочная для рекламы.
 * Цены — из прейскурантов ООО «Касимовские Зори» на «Новый год 2027».
 */
get_header();

$fmt = 'sz_fmt';

// Номера: [категория, 1 гость, 2 гостя, 3 гостя, ребёнок осн. место, ребёнок доп. место].
$rooms_breakfast = array(
	array( 'Стандарт одноместный', 5100, 0, 0, 0, 0 ),
	array( 'Стандарт двухместный', 7200, 10200, 0, 3750, 3450 ),
	array( 'Стандарт двухместный с видом на Оку', 7450, 10800, 0, 3750, 3450 ),
	array( 'Стандарт трёхместный', 0, 11400, 15300, 3750, 3450 ),
	array( 'Полулюкс', 8100, 11550, 0, 0, 3450 ),
	array( 'Люкс', 8700, 12250, 0, 0, 3450 ),
);
$rooms_lite = array(
	array( 'Стандарт одноместный', 6150, 0, 0, 0, 0 ),
	array( 'Стандарт двухместный', 8250, 12300, 0, 4800, 4500 ),
	array( 'Стандарт двухместный с видом на Оку', 8500, 12900, 0, 4800, 4500 ),
	array( 'Стандарт трёхместный', 0, 13500, 18450, 4800, 4500 ),
	array( 'Полулюкс', 9150, 13650, 0, 0, 4500 ),
	array( 'Люкс', 9750, 14350, 0, 0, 4500 ),
);
// Коттеджи: [№, гостей, что в доме, 31.12–02.01, 02.01–10.01].
$cottages = array(
	array( 1, 14, '7 спален, гостиная с камином, кухня-гостиная, 6 санузлов', 54000, 48600 ),
	array( 2, 5, '3 спальни, гостиная с камином, мини-кухня, 2 санузла', 13500, 12150 ),
	array( 3, 6, '3 спальни, гостиная с камином, 2 санузла', 16200, 14600 ),
	array( 4, 4, '2 спальни, финская сауна, бассейн, бильярд, кухня', 19500, 17550 ),
	array( 5, 5, '3 спальни, кухня-гостиная с камином, 4 санузла', 13500, 12150 ),
	array( 6, 10, '5 спален, кухня-гостиная, 3 санузла', 27000, 24300 ),
	array( 7, 9, '5 спален, кухня-гостиная, сауна и бильярд на цокольном этаже', 32400, 29200 ),
	array( 8, 9, '5 спален, кухня-гостиная, сауна и бильярд на цокольном этаже', 32400, 29200 ),
	array( 9, 10, '5 спален, кухня-гостиная, 3 санузла', 27000, 24300 ),
	array( 10, 10, '5 спален, кухня-гостиная, 3 санузла', 27000, 24300 ),
	array( 11, 10, '5 спален, кухня-гостиная, 3 санузла', 27000, 24300 ),
);
// Программы 03.01–10.01.2027: [название, 1 человек в одноместном стандарте, 2 человека в двухместном стандарте, ребёнок 3–14 на доп. месте].
$programs = array(
	array( 'Базовая лечебная', 6800, 13600, 0 ),
	array( 'Гибкий позвоночник', 8050, 16100, 7200 ),
	array( 'Физическая активность — суставы, мышцы, последствия травм', 8500, 17000, 7800 ),
	array( 'Здоровое сердце', 7900, 15800, 7100 ),
	array( 'Свободное дыхание', 7700, 15500, 7000 ),
	array( 'Стремление к совершенству — для снижения веса', 7500, 15000, 6700 ),
	array( 'Профилактика и реабилитация COVID-19', 7350, 14700, 6550 ),
	array( 'Для участников СВО и членов их семей', 8050, 16100, 0 ),
	array( 'Общетерапевтическая для членов профсоюзов', 5780, 11560, 4293 ),
);
$programs_kids = array(
	array( 'Лечебно-оздоровительная для детей', 5150, 5050 ),
	array( 'Лечебно-оздоровительная для детей участников СВО', 6200, 6050 ),
);
$programs_short = array(
	array( 'Путёвка выходного дня — 2 дня, заезд в пятницу, выезд в воскресенье', 11400, 22800, 9400 ),
	array( 'Экспресс-отдых — 30 часов, заезд в любой день', 8400, 15100, 6800 ),
);

?>

<section class="hero hero--page" aria-label="Новый год 2027">
	<div class="hero__img"><?php echo sz_img( 'ny-hero', 'Зимний лес и коттеджи санатория «Касимовские Зори»', true ); // phpcs:ignore ?></div>
	<div class="wrap hero__in">
		<p class="hero__kicker">Новый год 2027 в санатории «Касимовские Зори»</p>
		<h1>Новый год на Оке</h1>
		<p class="hero__lead">Встречайте 2027 год в лесу на берегу Оки: праздничный банкет и шоу-программа, баня на воде, бассейн, лыжи и коньки. Номера, коттеджи для компании и лечебные программы.</p>
		<div class="hero__facts"><span>31 декабря — 10 января</span><span>от 5 100 ₽ в сутки</span><span>Дети с 3 лет</span></div>
		<div class="hero__btns">
			<a class="btn btn--sun" href="#zayavka">Забронировать</a>
			<a class="btn btn--ghost-light" href="<?php echo esc_attr( sz_phone_href() ); ?>"><?php echo esc_html( sz_phone() ); ?></a>
		</div>
	</div>
</section>

<section class="sec" id="predlozheniya">
	<div class="wrap">
		<div class="sec__head">
			<h2>Новогодние предложения</h2>
			<p>Выберите формат отдыха — менеджер проверит свободные номера на ваши даты и забронирует.</p>
		</div>
		<div class="offers">
			<div class="offer">
				<div class="ph"><?php echo sz_img( 'ny-rooms', 'Номер в корпусе №1' ); // phpcs:ignore ?></div>
				<div class="offer__body">
					<p class="offer__dates">31 декабря — 10 января</p>
					<h3>Номер с завтраком</h3>
					<p>Проживание в корпусе №1 и завтрак «шведский стол». Номера от одноместного стандарта до люкса.</p>
					<p class="price">от <b>5 100</b> ₽ в сутки</p>
					<a class="btn btn--green btn--sm" href="#ceny-zavtrak">Все цены</a>
				</div>
			</div>
			<div class="offer">
				<div class="ph ph--sky"><?php echo sz_img( 'ny-lite', 'Бассейн санатория' ); // phpcs:ignore ?></div>
				<div class="offer__body">
					<p class="offer__dates">31 декабря — 10 января</p>
					<h3>Путёвка «Лайт»</h3>
					<p>Проживание, завтрак, обед, ужин и бассейн. Санаторно-курортная карта не нужна.</p>
					<p class="price">от <b>6 150</b> ₽ в сутки</p>
					<a class="btn btn--green btn--sm" href="#ceny-lait">Все цены</a>
				</div>
			</div>
			<div class="offer">
				<div class="ph ph--cream"><?php echo sz_img( 'ny-cottages', 'Коттедж на берегу Оки' ); // phpcs:ignore ?></div>
				<div class="offer__body">
					<p class="offer__dates">31 декабря — 10 января</p>
					<h3>Коттедж для семьи или компании</h3>
					<p>Отдельный дом на 4–14 гостей с кухней и гостиной, без питания. В некоторых — камин, сауна или бильярд.</p>
					<p class="price">от <b>12 150</b> ₽ в сутки за дом</p>
					<a class="btn btn--green btn--sm" href="#ceny-kottedzhi">Все цены</a>
				</div>
			</div>
			<div class="offer">
				<div class="ph"><?php echo sz_img( 'ny-programs', 'Кабинет водолечения' ); // phpcs:ignore ?></div>
				<div class="offer__body">
					<p class="offer__dates">3 — 10 января</p>
					<h3>Лечебные программы</h3>
					<p>13 программ: позвоночник и суставы, сердце, дыхание, детская и другие. Проживание и процедуры по назначению врача.</p>
					<p class="price">от <b>6 800</b> ₽ в сутки</p>
					<a class="btn btn--green btn--sm" href="#ceny-programmy">Все цены</a>
				</div>
			</div>
		</div>
	</div>
</section>

<section class="sec sec--white" id="prazdnik">
	<div class="wrap poster">
		<div class="ph"><?php echo sz_img( 'ny-poster', 'Афиша новогодней программы «Новогодние приключения в Касимовских Зорях»' ); // phpcs:ignore ?></div>
		<div class="poster__txt">
			<p class="label-sun" style="color:var(--blue-m)">31 декабря</p>
			<h2 style="font-size:clamp(32px,3.6vw,46px)">Новогодняя ночь</h2>
			<p>Праздничный банкет и развлекательная программа «Новогодние приключения в Касимовских Зорях». Меню и стоимость банкета уточняйте у администратора.</p>
			<h3 class="h3" style="margin-top:12px">Чем заняться на каникулах</h3>
			<ul class="lines">
				<li>Русская баня на воде, хамам и финская сауна с бассейном</li>
				<li>Бассейн и соляная пещера</li>
				<li>Лыжи, коньки, ватрушки и санки</li>
				<li>Боулинг, бильярд и настольный теннис</li>
				<li>Прогулки по зимнему лесу вдоль Оки</li>
			</ul>
			<a class="btn btn--sun" style="align-self:flex-start;margin-top:8px" href="#zayavka">Забронировать</a>
		</div>
	</div>
</section>

<section class="sec" id="ceny">
	<div class="wrap">
		<div class="sec__head" style="margin-bottom:0">
			<h2>Цены на Новый год</h2>
			<p>Цены в рублях за номер или коттедж в сутки. Дети до 3 лет без отдельного места — уточняйте у администратора.</p>
		</div>

		<h3 class="table-title" id="ceny-zavtrak">Номера с завтраком</h3>
		<p class="table-sub">31 декабря 2026 — 10 января 2027, корпус №1</p>
		<?php echo sz_room_table( $rooms_breakfast ); // phpcs:ignore ?>

		<h3 class="table-title" id="ceny-lait">Путёвка «Лайт»: проживание, трёхразовое питание и бассейн</h3>
		<p class="table-sub">31 декабря 2026 — 10 января 2027, корпус №1</p>
		<?php echo sz_room_table( $rooms_lite ); // phpcs:ignore ?>

		<h3 class="table-title" id="ceny-kottedzhi">Коттеджи, без питания</h3>
		<p class="table-sub">Цена за весь дом в сутки. Дополнительное место — 3 000 ₽ в сутки. Заезд в 14:00, выезд в 12:00.</p>
		<div class="table-wrap"><table class="prices">
			<thead><tr><th>Коттедж</th><th class="num">Гостей</th><th>Что в доме</th><th class="num">Новый год, 31.12–02.01</th><th class="num">Каникулы, 02.01–10.01</th></tr></thead>
			<tbody>
			<?php foreach ( $cottages as $c ) : ?>
				<tr><td>№<?php echo (int) $c[0]; ?></td><td class="num"><?php echo (int) $c[1]; ?></td><td><?php echo esc_html( $c[2] ); ?></td><td class="num"><?php echo esc_html( $fmt( $c[3] ) ); ?></td><td class="num"><?php echo esc_html( $fmt( $c[4] ) ); ?></td></tr>
			<?php endforeach; ?>
			</tbody>
		</table></div>

		<h3 class="table-title" id="ceny-programmy">Лечебные программы</h3>
		<p class="table-sub">3 — 10 января 2027. Цена за номер в сутки: проживание и процедуры по назначению врача. Нужна санаторно-курортная карта.</p>
		<div class="table-wrap"><table class="prices">
			<thead><tr><th>Программа</th><th class="num">1 человек, одноместный стандарт</th><th class="num">2 человека, двухместный стандарт</th><th class="num">Ребёнок 3–14 лет, доп. место</th></tr></thead>
			<tbody>
			<?php foreach ( $programs as $p ) : ?>
				<tr><td><?php echo esc_html( $p[0] ); ?></td><td class="num"><?php echo esc_html( $fmt( $p[1] ) ); ?></td><td class="num"><?php echo esc_html( $fmt( $p[2] ) ); ?></td><td class="num"><?php echo esc_html( $fmt( $p[3] ) ); ?></td></tr>
			<?php endforeach; ?>
			<tr class="grp"><td colspan="4">Программы для детей 3–14 лет — цена за ребёнка: основное место / доп. место</td></tr>
			<?php foreach ( $programs_kids as $p ) : ?>
				<tr><td><?php echo esc_html( $p[0] ); ?></td><td class="num"><?php echo esc_html( $fmt( $p[1] ) ); ?></td><td class="num">—</td><td class="num"><?php echo esc_html( $fmt( $p[2] ) ); ?></td></tr>
			<?php endforeach; ?>
			<tr class="grp"><td colspan="4">Короткие программы</td></tr>
			<?php foreach ( $programs_short as $p ) : ?>
				<tr><td><?php echo esc_html( $p[0] ); ?></td><td class="num"><?php echo esc_html( $fmt( $p[1] ) ); ?></td><td class="num"><?php echo esc_html( $fmt( $p[2] ) ); ?></td><td class="num"><?php echo esc_html( $fmt( $p[3] ) ); ?></td></tr>
			<?php endforeach; ?>
			</tbody>
		</table></div>
		<p class="note">В полулюксах, люксах и номерах с видом на Оку цены программ выше — менеджер рассчитает стоимость под ваш номер. Имеются противопоказания, необходима консультация специалиста. Цены до 30 декабря — на <a href="<?php echo esc_url( home_url( '/ceny/' ) ); ?>">странице цен</a>.</p>
	</div>
</section>

<section class="sec sec--white">
	<div class="wrap">
		<div class="sec__head"><h2>Как забронировать</h2></div>
		<ol class="steps">
			<li><h3>Оставьте заявку</h3><p>Через форму ниже или по телефону <?php echo esc_html( sz_phone() ); ?>. <?php echo esc_html( sz_hours() ); ?>.</p></li>
			<li><h3>Менеджер подберёт номер</h3><p>Проверит свободные номера и коттеджи на ваши даты и рассчитает стоимость.</p></li>
			<li><h3>Подтвердите бронь</h3><p>Менеджер расскажет, как оплатить, и пришлёт подтверждение бронирования.</p></li>
		</ol>
	</div>
</section>

<section class="sec" id="zayavka">
	<div class="wrap contact">
		<div class="contact__form">
			<h2>Забронировать Новый год</h2>
			<p class="muted">Новогодние даты разбирают быстро — оставьте заявку, и менеджер перезвонит.</p>
			<?php
			echo sz_form( array( // phpcs:ignore
				'anchor' => 'zayavka',
				'topic'  => 'Новый год 2027',
				'fields' => array( 'name', 'phone', 'ny_offer', 'guests', 'comment' ),
				'button' => 'Отправить заявку',
			) );
			?>
		</div>
		<div class="contact__info">
			<p class="label-sun">Отдел бронирования</p>
			<a class="big" href="<?php echo esc_attr( sz_phone_href() ); ?>"><?php echo esc_html( sz_phone() ); ?></a>
			<p><?php echo esc_html( sz_hours() ); ?></p>
			<a href="mailto:<?php echo esc_attr( sz_email() ); ?>"><?php echo esc_html( sz_email() ); ?></a>
			<p><?php echo esc_html( sz_address() ); ?></p>
			<a class="btn btn--sun" style="align-self:flex-start;margin-top:auto" href="<?php echo esc_url( home_url( '/' ) ); ?>">О санатории</a>
		</div>
	</div>
</section>

<?php
get_footer();
