<?php
/**
 * Главная страница.
 */
get_header();
$ny = esc_url( home_url( '/novyj-god/' ) );
?>

<section class="hero" aria-label="Санаторий «Касимовские Зори»">
	<div class="hero__img"><?php echo sz_img( 'hero', 'Санаторий «Касимовские Зори» зимой на берегу Оки', true ); // phpcs:ignore ?></div>
	<div class="wrap hero__in">
		<p class="hero__kicker">Санаторий на берегу Оки, Рязанская область</p>
		<h1>Касимовские Зори</h1>
		<p class="hero__lead">Лечение позвоночника и суставов на собственной Сапожковской торфяной грязи. Своя диагностика, 13 лечебных программ и 10 гектаров леса у реки.</p>
		<div class="hero__btns">
			<a class="btn btn--sun" href="<?php echo $ny; // phpcs:ignore ?>">Новогодние предложения</a>
			<a class="btn btn--ghost-light" href="#programmy">Подобрать программу</a>
		</div>
	</div>
</section>

<div class="wrap book" id="podbor">
	<div class="book__box">
		<p class="book__title">Узнайте цену на ваши даты</p>
		<?php
		echo sz_form( array( // phpcs:ignore
			'anchor' => 'podbor',
			'topic'  => 'Подбор номера (главная)',
			'fields' => array( 'checkin', 'checkout', 'guests', 'phone' ),
			'button' => 'Узнать цену',
		) );
		?>
	</div>
</div>

<section class="ny" aria-label="Новый год 2027">
	<div class="wrap">
		<div class="ny__box">
			<div class="ny__txt">
				<p class="ny__label">Новый год 2027</p>
				<h2>Новогодние каникулы на Оке</h2>
				<p class="ny__dates">31 декабря 2026 — 10 января 2027</p>
				<ul class="ny__list">
					<li><span>Номер с завтраком</span><b>от 5 100 ₽ в сутки</b></li>
					<li><span>Путёвка «Лайт» с питанием и бассейном</span><b>от 6 150 ₽</b></li>
					<li><span>Коттедж до 5 гостей</span><b>от 12 150 ₽</b></li>
					<li><span>Лечебные программы с 3 января</span><b>от 6 800 ₽</b></li>
				</ul>
				<a class="btn btn--sun" href="<?php echo $ny; // phpcs:ignore ?>">Подробнее</a>
			</div>
			<a class="ny__media" href="<?php echo $ny; // phpcs:ignore ?>" aria-label="Новогодние предложения — подробнее"><?php echo sz_img( 'ny-banner', 'Зимний лес и коттеджи санатория' ); // phpcs:ignore ?></a>
		</div>
	</div>
</section>

<section class="tiles-sec" aria-label="Разделы санатория">
	<div class="wrap">
		<div class="tiles">
			<?php
			$alts = array(
				'lechenie'      => 'Кабинет водолечения',
				'kosmetologiya' => 'СПА-капсула',
				'spa'           => 'Бассейн СПА-комплекса',
				'varianty'      => 'Территория санатория летом',
				'sport'         => 'Бильярд',
				'prozhivanie'   => 'Номер санатория',
				'meropriyatiya' => 'Беседка с фонтаном',
			);
			foreach ( sz_sections() as $id => $label ) :
				?>
				<a class="tile" href="#<?php echo esc_attr( $id ); ?>">
					<span class="tile__img">
						<?php echo sz_img( 'tile-' . $id, $alts[ $id ] ); // phpcs:ignore ?>
						<span class="tile__label"><?php echo esc_html( 'meropriyatiya' === $id ? 'Праздники и мероприятия' : $label ); ?></span>
						<span class="tile__arrow" aria-hidden="true"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0A7246" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14"/><path d="M6 13l6 6 6-6"/></svg></span>
					</span>
					<span class="tile__btn">Подробнее</span>
				</a>
			<?php endforeach; ?>
		</div>
	</div>
</section>

<section class="stats" aria-label="Санаторий в цифрах">
	<div class="wrap">
		<div class="stats__row">
			<svg class="stats__sun" width="72" height="36" viewBox="0 0 72 36" aria-hidden="true"><path d="M0 36a36 36 0 0 1 72 0z" fill="#FFC21A"/></svg>
			<div class="stat"><b>13</b><span>лечебных программ</span></div>
			<div class="stat"><b>70</b><span>видов лечебных процедур</span></div>
			<div class="stat"><b>10 га</b><span>благоустроенной территории</span></div>
			<div class="stat"><b>450</b><span>мест для размещения</span></div>
		</div>
	</div>
</section>

<!-- Лечение -->
<section class="sec sec--white" id="lechenie">
	<div class="wrap">
		<div class="sec__head">
			<h2>Лечение</h2>
			<p>Санаторий многопрофильный, но главное направление — позвоночник, суставы и последствия травм. В каждой программе лечат основное заболевание и укрепляют организм в целом.</p>
		</div>
		<div class="flex">
			<div class="panel-dark mud">
				<div class="mud__txt">
					<p class="label-sun">Своя лечебная грязь</p>
					<h3>Сапожковская торфяная грязь</h3>
					<p>Санаторий добывает лечебную грязь на собственном участке. Сапожковскую торфяную грязь применяют в России больше 50 лет — в виде аппликаций и вместе с электрофорезом.</p>
					<p>Грязелечение назначают при болезнях суставов и позвоночника, после травм и операций на костях и суставах.</p>
				</div>
				<div class="ph"><?php echo sz_img( 'mud', 'Процедура грязелечения' ); // phpcs:ignore ?></div>
			</div>
			<div class="panel diag">
				<h3 class="h3">Своя диагностическая база</h3>
				<p class="muted">Анализы и обследования делают на месте, без поездок в город.</p>
				<ul class="lines">
					<li>Клинико-биохимическая лаборатория</li>
					<li>Функциональная диагностика</li>
					<li>Ультразвуковая диагностика</li>
				</ul>
			</div>
		</div>

		<h3 class="h3 sub">Основные процедуры</h3>
		<ul class="grid-list">
			<li>Грязелечение</li><li>Водолечение</li><li>Теплолечение</li><li>Пенно-солодковые ванны</li>
			<li>Озонотерапия</li><li>Лазерное облучение крови (ВЛОК)</li><li>Вибро-механотерапия</li><li>Механотерапия «Ормед»</li>
			<li>Аппаратная физиотерапия</li><li>Лечебная гимнастика</li><li>Массаж</li><li>Соляная пещера</li>
		</ul>
		<p class="note">Всего более 70 видов процедур. Курс назначает врач санатория с учётом диагноза и санаторно-курортной карты.</p>

		<h3 class="h3 sub">Оборудование</h3>
		<ul class="grid-list">
			<li>Аппарат интерференцтерапии «Радиус-01 Интер»</li>
			<li>Аппарат магнитотерапии «Полюс-2М»</li>
			<li>Аппарат электролечения «Амплиимпульс-7»</li>
			<li>Гальваническая ванна «Истра-4К»</li>
			<li>Кинезотерапевтический аппарат «Ормед-кинезо»</li>
			<li>Аппарат для реабилитации ног «Ормед-Флекс»</li>
			<li>Свинг-машина «Такасима»</li>
			<li>Пароуглекислая ванна «Оккервиль-Комби»</li>
		</ul>

		<div id="programmy">
			<h3 class="h3 sub">Программы лечения</h3>
			<div class="flex">
				<div class="card">
					<h3>Гибкий позвоночник</h3>
					<p>При остеохондрозе, грыжах межпозвонкового диска и других заболеваниях позвоночника.</p>
					<p class="price">от <b>6 440</b> ₽ в сутки</p>
				</div>
				<div class="card">
					<h3>Здоровое сердце</h3>
					<p>При ишемической болезни сердца и гипертонии, для восстановления после инфаркта, стентирования и инсульта.</p>
					<p class="price">от <b>6 320</b> ₽ в сутки</p>
				</div>
				<div class="card">
					<h3>Базовая лечебная</h3>
					<p>При болезнях суставов и позвоночника, органов дыхания, сердца и сосудов, нервной системы.</p>
					<p class="price">от <b>5 440</b> ₽ в сутки</p>
				</div>
				<div class="card">
					<h3>Путёвка выходного дня</h3>
					<p>Два дня оздоровительных процедур: заезд в пятницу, выезд в воскресенье.</p>
					<p class="price">от <b>9 120</b> ₽ в сутки</p>
				</div>
			</div>
			<p class="note">Цена — за одного человека в одноместном номере. Действует до 30 декабря 2026 года. Всего 13 программ, в том числе для детей с 3 лет, для участников СВО и их семей, для членов профсоюзов.</p>
			<div class="cta-row">
				<a class="btn btn--green" href="#zayavka">Подобрать программу</a>
				<a class="btn btn--ghost" href="<?php echo esc_url( home_url( '/ceny/#programmy' ) ); ?>">Цены всех программ</a>
				<a class="btn btn--ghost" href="<?php echo $ny; // phpcs:ignore ?>">Программы на новогодние каникулы</a>
			</div>
		</div>
	</div>
</section>

<!-- Косметология -->
<section class="sec" id="kosmetologiya">
	<div class="wrap">
		<div class="band band--sky">
			<div style="flex:1 1 420px;display:flex;flex-direction:column;gap:14px">
				<h2 style="font-size:clamp(32px,3.6vw,46px)">Косметология</h2>
				<p style="color:var(--blue-ink);max-width:52ch">СПА-капсула объединяет несколько процедур в одной: душ Виши, вибромассаж, ароматерапию, хромотерапию и паровую баню или инфракрасную сауну. В расширенных программах — обёртывание, скрабирование и маски для лица и тела.</p>
				<ul class="lines" style="max-width:520px">
					<li style="display:flex;justify-content:space-between;gap:16px"><span>СПА-капсула</span><b>2 100 ₽</b></li>
					<li style="display:flex;justify-content:space-between;gap:16px"><span>СПА-капсула «Детокс»</span><b>2 300 ₽</b></li>
					<li style="display:flex;justify-content:space-between;gap:16px"><span>«Детокс» с масками для лица и тела</span><b>2 600 ₽</b></li>
					<li style="display:flex;justify-content:space-between;gap:16px"><span>С обёртыванием и масками</span><b>3 100 ₽</b></li>
				</ul>
				<a class="btn btn--green" style="align-self:flex-start" href="#zayavka">Записаться</a>
			</div>
			<div class="ph ph--sky" style="flex:1 1 320px;min-height:300px;background:#BFE0F7"><?php echo sz_img( 'kosmetologiya', 'СПА-капсула' ); // phpcs:ignore ?></div>
		</div>
	</div>
</section>

<!-- СПА -->
<section class="sec sec--white" id="spa">
	<div class="wrap">
		<div class="sec__head">
			<h2>СПА-комплекс</h2>
			<p>Плавучая русская баня на Оке, хамам и финская сауна с бассейном, соляная пещера — чтобы восстановиться после процедур или просто отдохнуть.</p>
		</div>
		<div class="flex">
			<div class="spa-main">
				<div class="ph ph--sky"><?php echo sz_img( 'spa-main', 'Хамам' ); // phpcs:ignore ?></div>
				<h3 class="h3">Хамам с бассейном</h3>
				<p class="muted">Турецкая парная с мягким влажным паром и бассейн. До 6 человек, 2 часа — 3 850 ₽.</p>
			</div>
			<div class="spa-side">
				<?php
				$spa_rows = array(
					array( 'spa-banya', 'Русская дровяная баня на воде', 'Плавучая баня с купелью прямо на Оке. До 6 человек, 3 часа — 6 930 ₽.', 'ph--cream' ),
					array( 'spa-sauna', 'Финская сауна с бассейном', 'Сухой жар и прохладный бассейн. До 6 человек, 2 часа — 3 850 ₽.', '' ),
					array( 'spa-salt', 'Соляная пещера', 'Сеанс климатотерапии: воздух без пыли, насыщенный ионами соли. Полезна при бронхитах, аллергии и частых простудах.', 'ph--sky' ),
				);
				foreach ( $spa_rows as $r ) :
					?>
					<div class="spa-row">
						<?php if ( sz_has_img( $r[0] ) ) : ?><div class="ph <?php echo esc_attr( $r[3] ); ?>"><?php echo sz_img( $r[0], $r[1] ); // phpcs:ignore ?></div><?php endif; ?>
						<div><h3><?php echo esc_html( $r[1] ); ?></h3><p><?php echo esc_html( $r[2] ); ?></p></div>
					</div>
				<?php endforeach; ?>
			</div>
		</div>
		<p class="note">Простыню и полотенце выдают. Каждый следующий гость — 500–600 ₽, каждый следующий час — 1 500 ₽.</p>
	</div>
</section>

<!-- Варианты отдыха -->
<section class="sec" id="varianty">
	<div class="wrap">
		<div class="sec__head">
			<h2>Варианты отдыха</h2>
			<p>Программы, номера и услуги под вашу поездку.</p>
		</div>
		<div class="flex" style="gap:40px 24px">
			<a class="media-card" href="#lechenie" style="text-decoration:none;color:inherit">
				<div class="ph"><?php echo sz_img( 'var-health', 'Ванна для водолечения' ); // phpcs:ignore ?></div>
				<h3>Для здоровья</h3>
				<p>Лечебные программы с консультацией врача, диагностикой и ежедневными процедурами.</p>
				<span style="font-weight:600;color:var(--green)">Подробнее</span>
			</a>
			<a class="media-card" href="#sport" style="text-decoration:none;color:inherit">
				<div class="ph ph--sky"><?php echo sz_img( 'var-family', 'Территория санатория у реки' ); // phpcs:ignore ?></div>
				<h3>Семьям с детьми</h3>
				<p>Детская лечебная программа с 3 лет, бассейн и боулинг, зимой — лыжи, коньки и ватрушки.</p>
				<span style="font-weight:600;color:var(--green)">Подробнее</span>
			</a>
			<a class="media-card" href="#meropriyatiya" style="text-decoration:none;color:inherit">
				<div class="ph ph--cream"><?php echo sz_img( 'var-corp', 'Корпус санатория' ); // phpcs:ignore ?></div>
				<h3>Корпоративным клиентам</h3>
				<p>Конференц-зал до 100 человек, проживание и питание для группы, баня и спортзал.</p>
				<span style="font-weight:600;color:var(--green)">Подробнее</span>
			</a>
			<a class="media-card" href="#meropriyatiya" style="text-decoration:none;color:inherit">
				<div class="ph"><?php echo sz_img( 'var-celebr', 'Беседка с фонтаном' ); // phpcs:ignore ?></div>
				<h3>Для торжеств</h3>
				<p>Свадьбы, юбилеи и дни рождения: банкетный зал, выездная регистрация, проживание гостей.</p>
				<span style="font-weight:600;color:var(--green)">Подробнее</span>
			</a>
		</div>
	</div>
</section>

<!-- Спорт -->
<section class="sec sec--white" id="sport">
	<div class="wrap">
		<div class="sec__head">
			<h2>Спорт</h2>
			<p>Большой спортивный зал, бассейн и тренажёрный зал — для отдыха и для командных мероприятий.</p>
		</div>
		<div class="hall">
			<?php if ( sz_has_img( 'sport-hall' ) ) : ?><div class="ph"><?php echo sz_img( 'sport-hall', 'Спортивный зал' ); // phpcs:ignore ?></div><?php endif; ?>
			<div class="hall__txt">
				<h3>Большой спортивный зал</h3>
				<div class="chips"><span>Мини-футбол</span><span>Баскетбол</span><span>Волейбол</span><span>Большой теннис</span></div>
				<p class="price" style="color:#CDEBDC">Аренда — <b>2 500</b> ₽ в час</p>
				<a class="btn btn--ghost-light" style="align-self:flex-start;border-color:#FFC21A" href="#zayavka">Забронировать зал</a>
			</div>
		</div>
		<div class="flex" style="gap:32px 24px;margin-top:48px">
			<div class="media-card">
				<div class="ph ph--sky"><?php echo sz_img( 'sport-pool', 'Бассейн' ); // phpcs:ignore ?></div>
				<h3>Бассейн и тренажёрный зал</h3>
				<p>Бассейн входит в путёвку «Лайт» и тариф с полным питанием. Тренажёрный зал — 500 ₽ в час.</p>
			</div>
			<div class="media-card">
				<div class="ph ph--cream"><?php echo sz_img( 'sport-bowling', 'Бильярд' ); // phpcs:ignore ?></div>
				<h3>Боулинг и бильярд</h3>
				<p>Боулинг — 1 500 ₽ в час за 2 дорожки. Бильярд и настольный теннис — 500 ₽ в час.</p>
			</div>
			<div class="media-card">
				<div class="ph ph--sky"><?php echo sz_img( 'sport-winter', 'Зимний лес у санатория' ); // phpcs:ignore ?></div>
				<h3>Зимой</h3>
				<p>Лыжи с ботинками и коньки — 500 ₽ в час, ватрушки — 300 ₽, санки — 350 ₽, ледянки бесплатно.</p>
			</div>
			<div class="media-card">
				<div class="ph"><?php echo sz_img( 'sport-summer', 'Берег Оки летом' ); // phpcs:ignore ?></div>
				<h3>Летом</h3>
				<p>Велосипеды, ролики, самокаты, гребные лодки и снасти для рыбалки — от 300 ₽ в час.</p>
			</div>
		</div>
		<div class="band band--mint" style="margin-top:56px">
			<div style="flex:1 1 420px;display:flex;flex-direction:column;gap:10px">
				<h3>Спортивные мероприятия для групп</h3>
				<p style="color:var(--green-dd);max-width:56ch">Турниры, корпоративные спартакиады и сборы команд с проживанием и питанием на территории санатория.</p>
			</div>
			<a class="btn btn--green" href="#zayavka">Получить консультацию</a>
		</div>
	</div>
</section>

<!-- Проживание -->
<section class="sec" id="prozhivanie">
	<div class="wrap">
		<div class="sec__head">
			<h2>Проживание</h2>
			<p>Номера пяти категорий в корпусе №1, 11 коттеджей и корпус №2 повышенной комфортности — всего 450 мест. Из многих номеров видна Ока.</p>
		</div>
		<div class="flex">
			<div class="stay">
				<div class="ph"><?php echo sz_img( 'stay-rooms', 'Номер в корпусе №1' ); // phpcs:ignore ?></div>
				<div class="stay__body">
					<h3>Номера в корпусе №1</h3>
					<p>Одноместные, двухместные, трёхместные, полулюкс и люкс. В каждом — ванная с душевой кабиной, кондиционер, телевизор и холодильник.</p>
					<p class="price">от <b>2 900</b> ₽ в сутки с завтраком</p>
					<a class="btn btn--ghost btn--sm" href="#zayavka">Узнать цену на даты</a>
				</div>
			</div>
			<div class="stay">
				<div class="ph ph--sky"><?php echo sz_img( 'stay-cottages', 'Коттедж на берегу Оки' ); // phpcs:ignore ?></div>
				<div class="stay__body">
					<h3>Коттеджи</h3>
					<p>11 домов на 4–14 гостей, от 120 до 420 м²: кухня, гостиная, спальни, Wi-Fi. В некоторых — камин, сауна или бильярд.</p>
					<p class="price">от <b>6 500</b> ₽ в сутки за дом</p>
					<a class="btn btn--ghost btn--sm" href="#zayavka">Выбрать коттедж</a>
				</div>
			</div>
			<div class="stay stay--dark">
				<div class="ph ph--green"><?php echo sz_img( 'stay-korpus2', 'Номер корпуса №2' ); // phpcs:ignore ?></div>
				<div class="stay__body">
					<p class="label-sun">Отдельный корпус</p>
					<h3>Корпус №2 повышенной комфортности</h3>
					<p>18 просторных номеров в отдельном корпусе. Гостям доступны все услуги и лечебные программы санатория.</p>
					<a class="btn btn--ghost-light btn--sm" style="border-color:#FFC21A" href="#zayavka">Узнать подробности</a>
				</div>
			</div>
		</div>
		<div class="band band--mint" style="margin-top:32px">
			<div style="flex:1 1 420px;display:flex;flex-direction:column;gap:8px">
				<h3>Питание</h3>
				<p style="color:var(--green-dd);max-width:60ch">Трёхразовое, по системе «шведский стол». Если выбрали тариф без питания, его можно добавить — цену подскажет администратор.</p>
			</div>
		</div>
		<p class="note">Цены на номера — за одноместный стандарт в ноябре–декабре 2026 года, на коттеджи — в будни зимнего сезона при заезде от 2 суток.</p>
	</div>
</section>

<!-- Мероприятия -->
<section class="sec sec--white" id="meropriyatiya">
	<div class="wrap">
		<div class="sec__head">
			<h2>Праздники и мероприятия</h2>
			<p>Организуем событие и разместим гостей на территории санатория.</p>
		</div>
		<div class="events">
			<div class="event event--wide">
				<?php echo sz_img( 'ev-wedding', 'Беседка с фонтаном на территории' ); // phpcs:ignore ?>
				<div class="event__card"><h3>Свадьбы</h3><p>Банкетный зал, выездная регистрация, проживание гостей.</p></div>
			</div>
			<div class="event" style="background:var(--sky)">
				<?php echo sz_img( 'ev-business', 'Корпус санатория' ); // phpcs:ignore ?>
				<div class="event__card"><h3>Бизнес-мероприятия</h3><p>Конференц-зал до 30, 60 или 100 человек, проектор, проживание и питание группы.</p></div>
			</div>
			<div class="event" style="background:var(--cream)">
				<?php echo sz_img( 'ev-birthday', 'Территория санатория' ); // phpcs:ignore ?>
				<div class="event__card"><h3>Дни рождения и юбилеи</h3><p>Банкетный зал, баня, зона барбекю и беседки.</p></div>
			</div>
			<div class="event event--wide">
				<?php echo sz_img( 'ev-kids', 'Зимняя территория санатория' ); // phpcs:ignore ?>
				<div class="event__card"><h3>Семейные праздники</h3><p>Банкет для взрослых, а для детей — зимние забавы, бассейн и боулинг.</p></div>
			</div>
		</div>
		<p class="note">Банкетный зал — 1 000 ₽ с человека, конференц-зал — от 4 000 ₽ в час, зона барбекю — 3 000 ₽ в час.</p>
		<div class="cta-row"><a class="btn btn--green" href="#zayavka">Обсудить мероприятие</a></div>
	</div>
</section>

<!-- Территория -->
<section class="sec" id="territoriya">
	<div class="wrap">
		<div class="sec__head">
			<h2>10 гектаров у Оки</h2>
			<p>Санаторий стоит в лесу на берегу Оки, в экологически чистом районе. На территории — пляж с прокатом лодок, беседка с фонтаном, детская площадка, яблоневый сад, магазин, спортивный комплекс и ресторан.</p>
		</div>
		<div class="flex">
			<div class="ph" style="flex:2 1 420px;min-height:340px"><?php echo sz_img( 'terr-1', 'Территория санатория и Ока' ); // phpcs:ignore ?></div>
			<div class="ph ph--sky" style="flex:1 1 260px;min-height:340px"><?php echo sz_img( 'terr-2', 'Корпус санатория' ); // phpcs:ignore ?></div>
			<div class="ph ph--cream" style="flex:1 1 260px;min-height:340px"><?php echo sz_img( 'terr-3', 'Корпус с верандой' ); // phpcs:ignore ?></div>
		</div>
	</div>
</section>

<!-- Подготовка и дорога -->
<section class="sec sec--white" id="zaezd">
	<div class="wrap flex" style="gap:56px">
		<div style="flex:1 1 440px;display:flex;flex-direction:column;gap:20px">
			<h2 style="font-size:clamp(32px,3.4vw,44px)">Как подготовиться к заезду</h2>
			<div class="faq">
				<details open>
					<summary>Какие документы взять с собой?</summary>
					<p>Паспорт гражданина РФ, для детей — свидетельство о рождении. Для лечебных программ нужна ещё санаторно-курортная карта.</p>
				</details>
				<details>
					<summary>Что нужно для санаторно-курортной карты?</summary>
					<ul>
						<li>паспорт и СНИЛС;</li>
						<li>справка об эпидокружении за 14 дней до заезда;</li>
						<li>флюорография, рентген или КТ грудной клетки за последний год;</li>
						<li>общий анализ крови и мочи, глюкоза крови, ЭКГ;</li>
						<li>для женщин — заключение гинеколога, при инвалидности — справка МСЭ.</li>
					</ul>
				</details>
				<details>
					<summary>Можно ли оформить карту в санатории?</summary>
					<p>Да, если привезти документы из списка. Карта, оформленная заранее, ускорит заселение.</p>
				</details>
				<details>
					<summary>Когда сдают анализы?</summary>
					<p>Во вторник, среду и пятницу с 8:15 до 9:00. Если заезжаете в эти дни, приезжайте до 8:00.</p>
				</details>
				<details>
					<summary>Нужна ли карта для путёвки «Лайт» и проживания?</summary>
					<p>Нет. Санаторно-курортная карта нужна только для лечебных программ.</p>
				</details>
			</div>
		</div>
		<div id="doroga" style="flex:1 1 440px;display:flex;flex-direction:column;gap:20px">
			<h2 style="font-size:clamp(32px,3.4vw,44px)">Как добраться</h2>
			<p class="muted"><?php echo esc_html( sz_address() ); ?></p>
			<div>
				<div class="route"><b>На машине</b><span>Около 6 часов от Москвы. В навигаторе: село Телебукино, 7Е, Касимовский округ.</span></div>
				<div class="route"><b>Из Москвы</b><span>Автобус от автовокзала «Щёлковский» до Касимова, +7 (499) 748-80-29</span></div>
				<div class="route"><b>Из Рязани</b><span>Автобус от автовокзала «Приокский» до Касимова, +7 (4912) 28-17-19</span></div>
				<div class="route"><b>Из Мурома</b><span>Автобус от автовокзала Мурома до Касимова, +7 (49234) 3-24-65</span></div>
				<div class="route"><b>Из Нижнего Новгорода</b><span>Автобус от ТПУ «Канавинский» до Касимова, +7 (831) 211-31-93</span></div>
			</div>
			<p class="muted small">Как добраться от Касимова до санатория — подскажет администратор при бронировании.</p>
		</div>
	</div>
</section>

<!-- Заявка -->
<section class="sec" id="zayavka">
	<div class="wrap contact">
		<div class="contact__form">
			<h2>Вам перезвонить?</h2>
			<p class="muted">Поможем выбрать программу, даты и номер. <?php echo esc_html( sz_hours() ); ?>.</p>
			<?php
			echo sz_form( array( // phpcs:ignore
				'anchor' => 'zayavka',
				'topic'  => 'Обратный звонок (главная)',
				'fields' => array( 'name', 'phone', 'interest', 'comment' ),
				'button' => 'Перезвоните мне',
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
