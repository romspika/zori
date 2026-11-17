<?php
/**
 * Страница «Цены». Данные — из прейскурантов ООО «Касимовские Зори», действующих до 30 декабря 2026 года.
 */
get_header();

// Программы 01.06–30.12.2026: [программа, 1 чел. одноместный стандарт, 2 чел. двухместный стандарт, 2 чел. с видом на Оку, полулюкс 2 чел., люкс 2 чел., ребёнок 3–14 доп. место].
$programs = array(
	array( 'Базовая лечебная', 5440, 10880, 11120, 12160, 12240, 0 ),
	array( 'Гибкий позвоночник', 6440, 12880, 13360, 14240, 14280, 5760 ),
	array( 'Физическая активность — суставы, мышцы, последствия травм', 6800, 13600, 14160, 15040, 15120, 6240 ),
	array( 'Здоровое сердце', 6320, 12640, 13120, 13920, 14000, 5680 ),
	array( 'Свободное дыхание', 6160, 12400, 12840, 13680, 13760, 5600 ),
	array( 'Стремление к совершенству — для снижения веса', 6000, 12000, 12560, 13360, 13340, 5360 ),
	array( 'Профилактика и реабилитация COVID-19', 5880, 11760, 12240, 13040, 13120, 5240 ),
	array( 'Для участников СВО и членов их семей', 6440, 12880, 13360, 14240, 14280, 0 ),
	array( 'Общетерапевтическая для членов профсоюзов', 4913, 9248, 9452, 0, 0, 0 ),
	array( 'Путёвка выходного дня — 2 дня, заезд в пятницу', 9120, 18240, 18560, 18960, 19120, 7520 ),
	array( 'Экспресс-отдых — 30 часов, заезд в любой день', 6720, 12080, 12400, 13360, 13440, 5440 ),
);
$programs_kids = array(
	array( 'Лечебно-оздоровительная для детей', 4120, 4040 ),
	array( 'Лечебно-оздоровительная для детей участников СВО', 4960, 4840 ),
);
// Номера с завтраком, ноябрь–декабрь 2026.
$rooms = array(
	array( 'Стандарт одноместный', 2900, 0, 0, 0, 0 ),
	array( 'Стандарт двухместный', 4100, 5800, 0, 2500, 2300 ),
	array( 'Стандарт двухместный с видом на Оку', 4300, 6200, 0, 2500, 2300 ),
	array( 'Стандарт трёхместный', 0, 6500, 8700, 2500, 2300 ),
	array( 'Полулюкс', 4700, 6600, 0, 0, 2300 ),
	array( 'Люкс', 5000, 7000, 0, 0, 2300 ),
);
// Коттеджи: [№, гостей, осень будни, осень выходные, зима будни, зима выходные] — каждая цена [1 сутки, от 2 суток].
$cottages = array(
	array( 1, 14, array( 39000, 34400 ), array( 46800, 41400 ), array( 30000, 26300 ), array( 36000, 31700 ) ),
	array( 2, 5, array( 9750, 8500 ), array( 11700, 10300 ), array( 7500, 6500 ), array( 9000, 7850 ) ),
	array( 3, 6, array( 11700, 10300 ), array( 14050, 12300 ), array( 9000, 7800 ), array( 10800, 9400 ) ),
	array( 4, 4, array( 13000, 11500 ), array( 16900, 15000 ), array( 10000, 8800 ), array( 13000, 11500 ) ),
	array( 5, 5, array( 9750, 8500 ), array( 11700, 10300 ), array( 7500, 6500 ), array( 9000, 7850 ) ),
	array( 6, 10, array( 19500, 17000 ), array( 23400, 20600 ), array( 15000, 13000 ), array( 18000, 15700 ) ),
	array( 7, 9, array( 23400, 20600 ), array( 27000, 23900 ), array( 18000, 15750 ), array( 21600, 19000 ) ),
	array( 8, 9, array( 23400, 20600 ), array( 27000, 23900 ), array( 18000, 15700 ), array( 21600, 19000 ) ),
	array( 9, 10, array( 19500, 17000 ), array( 23400, 20600 ), array( 15000, 13000 ), array( 18000, 15700 ) ),
	array( 10, 10, array( 19500, 17000 ), array( 23400, 20600 ), array( 15000, 13000 ), array( 18000, 15700 ) ),
	array( 11, 10, array( 19500, 17000 ), array( 23400, 20600 ), array( 15000, 13000 ), array( 18000, 15700 ) ),
);
$cot_cell = function ( $p ) {
	return '<td class="num">' . esc_html( sz_fmt( $p[0] ) ) . '<small>от 2 суток ' . esc_html( sz_fmt( $p[1] ) ) . '</small></td>';
};
?>

<section class="page-head">
	<div class="wrap">
		<h1>Цены</h1>
		<p>Цены санатория «Касимовские Зори» до 30 декабря 2026 года. Менеджер подберёт вариант под ваши даты и рассчитает точную стоимость.</p>
		<nav class="jump" aria-label="Разделы цен">
			<a class="hot" href="<?php echo esc_url( home_url( '/novyj-god/#ceny' ) ); ?>">Новый год</a>
			<a href="#programmy">Лечебные программы</a>
			<a href="#nomera">Номера</a>
			<a href="#kottedzhi">Коттеджи</a>
			<a href="#procedury">Процедуры</a>
			<a href="#banya">Баня и СПА</a>
			<a href="#sport-ceny">Спорт и прокат</a>
			<a href="#meropriyatiya-ceny">Мероприятия</a>
			<a href="#drugoe">Другие услуги</a>
		</nav>
		<div class="ny-strip">
			<p>С 31 декабря по 10 января — <b>новогодние цены</b>: номера с завтраком от 5 100 ₽ в сутки, коттеджи от 12 150 ₽.</p>
			<a class="btn btn--sun btn--sm" href="<?php echo esc_url( home_url( '/novyj-god/#ceny' ) ); ?>">Новогодние цены</a>
		</div>
	</div>
</section>

<section class="price-sec" id="programmy">
	<div class="wrap">
		<h2>Лечебные программы</h2>
		<p class="table-sub">1 июня — 30 декабря 2026 года. Цена за номер в сутки: проживание и процедуры по назначению врача. Нужна санаторно-курортная карта.</p>
		<div class="table-wrap"><table class="prices">
			<thead><tr><th>Программа</th><th class="num">1 человек, одноместный стандарт</th><th class="num">2 человека, двухместный стандарт</th><th class="num">2 человека, вид на Оку</th><th class="num">Полулюкс, 2 человека</th><th class="num">Люкс, 2 человека</th><th class="num">Ребёнок 3–14 лет, доп. место</th></tr></thead>
			<tbody>
			<?php foreach ( $programs as $p ) : ?>
				<tr><td><?php echo esc_html( $p[0] ); ?></td><?php for ( $i = 1; $i <= 6; $i++ ) : ?><td class="num"><?php echo esc_html( sz_fmt( $p[ $i ] ) ); ?></td><?php endfor; ?></tr>
			<?php endforeach; ?>
			</tbody>
		</table></div>
		<h3 class="table-title" style="margin-top:32px">Программы для детей 3–14 лет</h3>
		<p class="table-sub">Цена за ребёнка в сутки.</p>
		<?php echo sz_simple_table( array( 'Программа', 'Основное место', 'Дополнительное место' ), $programs_kids ); // phpcs:ignore ?>
		<p class="note">Одного человека в двухместном номере и трёхместные номера менеджер рассчитает отдельно. Имеются противопоказания, необходима консультация специалиста.</p>
	</div>
</section>

<section class="price-sec" id="nomera">
	<div class="wrap">
		<h2>Номера с завтраком</h2>
		<p class="table-sub">Ноябрь — декабрь 2026 года, корпус №1. Цена за номер в сутки.</p>
		<?php echo sz_room_table( $rooms ); // phpcs:ignore ?>
	</div>
</section>

<section class="price-sec" id="kottedzhi">
	<div class="wrap">
		<h2>Коттеджи</h2>
		<p class="table-sub">Без питания, цена за весь дом в сутки. При заезде от 2 суток — дешевле. Дополнительное место — 2 000 ₽ в сутки. Заезд в 14:00, выезд в 12:00.</p>
		<div class="table-wrap"><table class="prices">
			<thead><tr><th>Коттедж</th><th class="num">Гостей</th><th class="num">Ноябрь, будни</th><th class="num">Ноябрь, выходные</th><th class="num">Декабрь, будни</th><th class="num">Декабрь, выходные</th></tr></thead>
			<tbody>
			<?php foreach ( $cottages as $c ) : ?>
				<tr><td>№<?php echo (int) $c[0]; ?></td><td class="num"><?php echo (int) $c[1]; ?></td><?php echo $cot_cell( $c[2] ) . $cot_cell( $c[3] ) . $cot_cell( $c[4] ) . $cot_cell( $c[5] ); // phpcs:ignore ?></tr>
			<?php endforeach; ?>
			</tbody>
		</table></div>
		<p class="note">Цены декабря действуют до 29 декабря. Что есть в каждом коттедже — в <a href="<?php echo esc_url( home_url( '/novyj-god/#ceny-kottedzhi' ) ); ?>">таблице на странице «Новый год»</a>.</p>
	</div>
</section>

<section class="price-sec" id="procedury">
	<div class="wrap">
		<h2>Отдельные процедуры</h2>
		<p class="table-sub">Прейскурант с 1 февраля 2026 года, цена за одну процедуру в рублях. Курс назначает врач санатория.</p>
		<div class="acc">
			<?php foreach ( sz_procedure_prices() as $group => $rows ) : ?>
				<details>
					<summary><?php echo esc_html( $group ); ?><span><?php echo count( $rows ); ?></span></summary>
					<?php echo sz_simple_table( array( 'Процедура', 'Цена, ₽' ), $rows ); // phpcs:ignore ?>
				</details>
			<?php endforeach; ?>
		</div>
	</div>
</section>

<section class="price-sec" id="banya">
	<div class="wrap">
		<h2>Баня и СПА</h2>
		<p class="table-sub">Простыню и полотенце выдают. Цены в рублях.</p>
		<?php
		echo sz_simple_table( // phpcs:ignore
			array( 'Услуга', 'До 6 человек', 'Каждый следующий гость', 'Каждый следующий час' ),
			array(
				array( 'Русская дровяная баня на воде, 3 часа', 6930, 600, 1500 ),
				array( 'Хамам с бассейном, 2 часа', 3850, 500, 1500 ),
				array( 'Финская сауна с бассейном, 2 часа', 3850, 500, 1500 ),
			)
		);
		?>
		<p class="note">СПА-капсула и соляная пещера — в разделе «Отдельные процедуры».</p>
	</div>
</section>

<section class="price-sec" id="sport-ceny">
	<div class="wrap">
		<h2>Спорт и прокат</h2>
		<?php
		echo sz_simple_table( // phpcs:ignore
			array( 'Спорт', 'Цена' ),
			array(
				array( 'Большой спортивный зал: мини-футбол, баскетбол, волейбол, большой теннис', '2 500 ₽ в час' ),
				array( 'Тренажёрный зал', '500 ₽ в час' ),
				array( 'Настольный теннис', '500 ₽ в час' ),
				array( 'Боулинг, 2 дорожки', '1 500 ₽ в час' ),
				array( 'Бильярд', '500 ₽ в час' ),
			)
		);
		?>
		<h3 class="table-title" style="margin-top:32px">Прокат зимой</h3>
		<?php
		echo sz_simple_table( // phpcs:ignore
			array( 'Что', 'Цена' ),
			array(
				array( 'Лыжи, палки и ботинки', '500 ₽ в час' ),
				array( 'Коньки', '500 ₽ в час' ),
				array( 'Ватрушка (тюбинг)', '300 ₽ в час' ),
				array( 'Хоккейные клюшки и шайба', '300 ₽ в час' ),
				array( 'Санки', '350 ₽' ),
				array( 'Ледянки', 'бесплатно' ),
			)
		);
		?>
		<h3 class="table-title" style="margin-top:32px">Прокат летом</h3>
		<?php
		echo sz_simple_table( // phpcs:ignore
			array( 'Что', 'Цена' ),
			array(
				array( 'Велосипед детский', '500 ₽ в час' ),
				array( 'Велосипед взрослый', '600 ₽ в час' ),
				array( 'Роликовые коньки с защитой', '500 ₽ в час' ),
				array( 'Самокат маленький / большой', '500 / 600 ₽ в час' ),
				array( 'Скейтборд', '500 ₽ в час' ),
				array( 'Гребная лодка (залог 1 000 ₽)', '500 ₽ в час' ),
				array( 'Спиннинг или удочка', '350 ₽ за 12 часов' ),
				array( 'Садок', '300 ₽ за 12 часов' ),
				array( 'Волейбольный мяч', '300 ₽ за 2 часа' ),
				array( 'Ракетки для бадминтона или настольного тенниса', '300 ₽ в час' ),
				array( 'Ракетки для большого тенниса', '500 ₽ в час' ),
			)
		);
		?>
	</div>
</section>

<section class="price-sec" id="meropriyatiya-ceny">
	<div class="wrap">
		<h2>Мероприятия</h2>
		<?php
		echo sz_simple_table( // phpcs:ignore
			array( 'Услуга', 'Цена' ),
			array(
				array( 'Конференц-зал до 30 человек', '4 000 ₽ в час' ),
				array( 'Конференц-зал до 60 человек', '5 000 ₽ в час' ),
				array( 'Конференц-зал до 100 человек', '7 500 ₽ в час' ),
				array( 'Экран и проектор', '5 000 ₽' ),
				array( 'Банкетный зал (ресторан, 2 этаж), с 12:00 до 23:00', '1 000 ₽ с человека' ),
				array( 'Зона барбекю', '3 000 ₽ в час' ),
				array( 'Лавки для выездной регистрации', '1 000 ₽ за штуку' ),
				array( 'Дальняя беседка', '1 500 ₽ в час' ),
			)
		);
		?>
	</div>
</section>

<section class="price-sec" id="drugoe">
	<div class="wrap">
		<h2>Другие услуги</h2>
		<?php
		echo sz_simple_table( // phpcs:ignore
			array( 'Услуга', 'Цена' ),
			array(
				array( 'Проживание с домашним животным в коттедже', '650 ₽ в сутки' ),
				array( 'Стирка белья, до 5 кг', '250 ₽' ),
				array( 'Стоянка моторной лодки без проживания', '500 ₽ в сутки' ),
				array( 'Спуск лодки или катера на воду без проживания', '750 ₽' ),
			)
		);
		?>
	</div>
</section>

<section class="sec" id="zayavka">
	<div class="wrap contact">
		<div class="contact__form">
			<h2>Рассчитать стоимость</h2>
			<p class="muted">Напишите даты и состав гостей — менеджер подберёт вариант и назовёт точную цену.</p>
			<?php
			echo sz_form( array( // phpcs:ignore
				'anchor' => 'zayavka',
				'topic'  => 'Расчёт стоимости (страница цен)',
				'fields' => array( 'name', 'phone', 'interest', 'comment' ),
				'button' => 'Рассчитать',
			) );
			?>
		</div>
		<div class="contact__info">
			<p class="label-sun">Отдел бронирования</p>
			<a class="big" href="<?php echo esc_attr( sz_phone_href() ); ?>"><?php echo esc_html( sz_phone() ); ?></a>
			<p><?php echo esc_html( sz_hours() ); ?></p>
			<a href="mailto:<?php echo esc_attr( sz_email() ); ?>"><?php echo esc_html( sz_email() ); ?></a>
			<p><?php echo esc_html( sz_address() ); ?></p>
		</div>
	</div>
</section>

<?php
get_footer();
