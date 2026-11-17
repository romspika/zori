<?php
/**
 * Тема «Касимовские Зори» для san-zori.ru.
 */
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'SZ_VER', '1.1.0' );

/* ---------- Настройки темы ---------- */
add_action( 'after_setup_theme', function () {
	add_theme_support( 'title-tag' );
	add_theme_support( 'html5', array( 'search-form', 'gallery', 'caption', 'style', 'script' ) );
} );

add_action( 'wp_enqueue_scripts', function () {
	$css = get_theme_file_path( 'style.css' );
	$js  = get_theme_file_path( 'assets/js/main.js' );
	wp_enqueue_style( 'sz-style', get_stylesheet_uri(), array(), file_exists( $css ) ? filemtime( $css ) : SZ_VER );
	wp_enqueue_script( 'sz-main', get_theme_file_uri( 'assets/js/main.js' ), array(), file_exists( $js ) ? filemtime( $js ) : SZ_VER, true );
	wp_localize_script( 'sz-main', 'SZ', array(
		'metrika' => sz_metrika_id(),
		'sent'    => ( isset( $_GET['sent'] ) && '1' === $_GET['sent'] ) ? 1 : 0, // phpcs:ignore WordPress.Security.NonceVerification
	) );
	// На сайте нет блога — блочные стили WordPress не нужны.
	wp_dequeue_style( 'wp-block-library' );
	wp_dequeue_style( 'classic-theme-styles' );
	wp_dequeue_style( 'global-styles' );
}, 20 );

// Без эмодзи-скриптов и лишнего в <head>.
remove_action( 'wp_head', 'print_emoji_detection_script', 7 );
remove_action( 'wp_print_styles', 'print_emoji_styles' );
remove_action( 'wp_head', 'wp_generator' );

add_action( 'wp_head', function () {
	echo '<link rel="preload" href="' . esc_url( get_theme_file_uri( 'assets/fonts/golos-text-cyrillic-400-normal.woff2' ) ) . '" as="font" type="font/woff2" crossorigin>' . "\n";
	echo '<meta name="theme-color" content="#0E4E7A">' . "\n";
	if ( is_front_page() ) {
		echo '<meta name="description" content="Санаторий «Касимовские Зори» на берегу Оки в Рязанской области: лечение позвоночника и суставов, торфяная грязь с собственного участка, 13 лечебных программ, коттеджи. Бронирование: ' . esc_attr( sz_phone() ) . '">' . "\n";
	} elseif ( is_page( 'ceny' ) ) {
		echo '<meta name="description" content="Цены санатория «Касимовские Зори»: лечебные программы от 5 440 ₽ в сутки, номера с завтраком от 2 900 ₽, коттеджи, процедуры, баня, прокат и мероприятия.">' . "\n";
	} elseif ( is_page( 'novyj-god' ) ) {
		echo '<meta name="description" content="Новый год 2027 в санатории «Касимовские Зори» на Оке: номера с завтраком от 5 100 ₽ в сутки, коттеджи для компании, лечебные программы. 31 декабря — 10 января.">' . "\n";
	}
}, 1 );

add_filter( 'document_title_parts', function ( $parts ) {
	if ( is_front_page() ) {
		$parts['title'] = 'Санаторий «Касимовские Зори» на Оке — лечение и отдых';
		unset( $parts['tagline'] );
	}
	return $parts;
} );

/* ---------- Значения из «Настроить» ---------- */
function sz_mod( $key, $default = '' ) {
	$v = get_theme_mod( $key, $default );
	return is_string( $v ) ? trim( $v ) : $default;
}
function sz_phone() {
	return sz_mod( 'sz_phone', '+7 (495) 085-98-30' );
}
function sz_phone_href() {
	$d = preg_replace( '/[^0-9+]/', '', sz_phone() );
	return 'tel:' . $d;
}
function sz_email() {
	return sz_mod( 'sz_email', 'san-zori@bk.ru' );
}
function sz_hours() {
	return sz_mod( 'sz_hours', 'Ежедневно с 9:00 до 21:00' );
}
function sz_address() {
	return sz_mod( 'sz_address', '391333, Рязанская область, Касимовский муниципальный округ, село Телебукино, 7Е' );
}
function sz_metrika_id() {
	return preg_replace( '/\D/', '', sz_mod( 'sz_metrika', '' ) );
}

add_action( 'customize_register', function ( $wp_customize ) {
	$wp_customize->add_section( 'sz_contacts', array(
		'title'    => 'Контакты, юрлицо и счётчик',
		'priority' => 25,
	) );
	$fields = array(
		'sz_phone'     => array( 'Телефон', '+7 (495) 085-98-30', 'text' ),
		'sz_email'     => array( 'Почта для заявок', 'san-zori@bk.ru', 'email' ),
		'sz_hours'     => array( 'Часы работы', 'Ежедневно с 9:00 до 21:00', 'text' ),
		'sz_address'   => array( 'Адрес', '391333, Рязанская область, Касимовский муниципальный округ, село Телебукино, 7Е', 'textarea' ),
		'sz_metrika'   => array( 'Номер счётчика Яндекс Метрики', '', 'text' ),
		'sz_company'   => array( 'Кто оказывает услуги (для подвала)', 'ООО «Касимовские Зори»', 'text' ),
		'sz_company_id' => array( 'ИНН / ОГРН (для подвала)', '', 'text' ),
		'sz_license'   => array( 'Лицензия: номер и дата', '', 'text' ),
		'sz_operator'  => array( 'Оператор персональных данных (название)', 'ООО «Касимовские Зори»', 'text' ),
		'sz_operator_id' => array( 'Оператор: ИНН / ОГРН', '', 'text' ),
		'sz_operator_addr' => array( 'Оператор: адрес', '391333, Рязанская область, Касимовский муниципальный округ, село Телебукино, 7Е', 'textarea' ),
	);
	foreach ( $fields as $id => $f ) {
		$wp_customize->add_setting( $id, array(
			'default'           => $f[1],
			'sanitize_callback' => 'textarea' === $f[2] ? 'sanitize_textarea_field' : 'sanitize_text_field',
		) );
		$wp_customize->add_control( $id, array(
			'label'   => $f[0],
			'section' => 'sz_contacts',
			'type'    => $f[2],
		) );
	}
} );

/* ---------- Яндекс Метрика ---------- */
add_action( 'wp_head', function () {
	$id = sz_metrika_id();
	if ( ! $id || is_user_logged_in() ) {
		return;
	}
	?>
<script>(function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};m[i].l=1*new Date();for(var j=0;j<document.scripts.length;j++){if(document.scripts[j].src===r){return;}}k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})(window,document,'script','https://mc.yandex.ru/metrika/tag.js','ym');ym(<?php echo (int) $id; ?>,'init',{clickmap:true,trackLinks:true,accurateTrackBounce:true,webvisor:true});</script>
<noscript><div><img src="https://mc.yandex.ru/watch/<?php echo (int) $id; ?>" style="position:absolute;left:-9999px" alt=""></div></noscript>
	<?php
}, 5 );

/* ---------- Картинки ---------- */
/**
 * Фото из assets/img/<slot>.jpg. Если файла нет — пустая строка,
 * а блок показывает свой цветной фон (сайт не ломается без фото).
 */
function sz_img( $slot, $alt = '', $eager = false ) {
	foreach ( array( 'webp', 'jpg', 'jpeg', 'png' ) as $ext ) {
		$rel  = 'assets/img/' . $slot . '.' . $ext;
		$path = get_theme_file_path( $rel );
		if ( file_exists( $path ) ) {
			$size = @getimagesize( $path ); // phpcs:ignore WordPress.PHP.NoSilencedErrors
			$wh   = $size ? ' width="' . (int) $size[0] . '" height="' . (int) $size[1] . '"' : '';
			$load = $eager ? ' fetchpriority="high"' : ' loading="lazy"';
			return '<img src="' . esc_url( get_theme_file_uri( $rel ) ) . '?v=' . filemtime( $path ) . '" alt="' . esc_attr( $alt ) . '"' . $wh . $load . ' decoding="async">';
		}
	}
	return '';
}

function sz_has_img( $slot ) {
	foreach ( array( 'webp', 'jpg', 'jpeg', 'png' ) as $ext ) {
		if ( file_exists( get_theme_file_path( 'assets/img/' . $slot . '.' . $ext ) ) ) {
			return true;
		}
	}
	return false;
}

/* ---------- Значки разделов ---------- */
function sz_icon( $name ) {
	$p = array(
		'lechenie'     => '<path d="M9 3.5h6v5.5h5.5v6H15v5.5H9V15H3.5V9H9z"/>',
		'kosmetologiya'=> '<path d="M12 3.5c3.2 4.2 6 7.6 6 11a6 6 0 0 1-12 0c0-3.4 2.8-6.8 6-11z"/>',
		'spa'          => '<path d="M4 20h16"/><path d="M8 16c-1.5-1.5 1.5-3 0-4.5s1.5-3 0-4.5"/><path d="M12 16c-1.5-1.5 1.5-3 0-4.5s1.5-3 0-4.5"/><path d="M16 16c-1.5-1.5 1.5-3 0-4.5s1.5-3 0-4.5"/>',
		'varianty'     => '<circle cx="8" cy="7" r="2.5"/><circle cx="16.5" cy="9" r="2"/><path d="M3.5 20v-3a4.5 4.5 0 0 1 9 0v3"/><path d="M13.5 20v-2.5a3 3 0 0 1 6 0V20"/>',
		'sport'        => '<circle cx="12" cy="12" r="8.5"/><path d="M12 3.5v17"/><path d="M3.5 12h17"/><path d="M6.5 5.5c2.8 3 2.8 10 0 13"/><path d="M17.5 5.5c-2.8 3-2.8 10 0 13"/>',
		'prozhivanie'  => '<path d="M4 11l8-6.5 8 6.5V20H4z"/><path d="M10 20v-5h4v5"/>',
		'meropriyatiya'=> '<path d="M12 3.5l1.8 5.2 5.2 1.8-5.2 1.8L12 17.5l-1.8-5.2-5.2-1.8 5.2-1.8z"/><path d="M18.5 15.5l.7 1.8 1.8.7-1.8.7-.7 1.8-.7-1.8-1.8-.7 1.8-.7z"/>',
	);
	return '<svg viewBox="0 0 24 24" aria-hidden="true">' . ( isset( $p[ $name ] ) ? $p[ $name ] : '' ) . '</svg>';
}

/** Ссылка на форму заявки: на своей странице — якорь, на остальных — главная. */
function sz_form_link() {
	return ( is_front_page() || is_page( array( 'novyj-god', 'ceny' ) ) ) ? '#zayavka' : home_url( '/#zayavka' );
}

function sz_sections() {
	return array(
		'lechenie'      => 'Лечение',
		'kosmetologiya' => 'Косметология',
		'spa'           => 'СПА-комплекс',
		'varianty'      => 'Варианты отдыха',
		'sport'         => 'Спорт',
		'prozhivanie'   => 'Проживание',
		'meropriyatiya' => 'Мероприятия',
	);
}

function sz_logo_svg( $wave = '#1366A8' ) {
	return '<svg width="46" height="46" viewBox="0 0 46 46" aria-hidden="true"><path d="M11 26a12 12 0 0 1 24 0z" fill="#FFC21A"/><path d="M5 31.5c3-2.4 6-2.4 9 0s6 2.4 9 0 6-2.4 9 0 6 2.4 9 0" fill="none" stroke="' . esc_attr( $wave ) . '" stroke-width="2.2" stroke-linecap="round"/><path d="M9 37.5c3-2.4 6-2.4 9 0s6 2.4 9 0 6-2.4 9 0" fill="none" stroke="' . esc_attr( $wave ) . '" stroke-width="2.2" stroke-linecap="round" opacity=".55"/></svg>';
}

/* ---------- Заявки ---------- */
add_action( 'init', function () {
	register_post_type( 'sz_lead', array(
		'labels'          => array(
			'name'          => 'Заявки',
			'singular_name' => 'Заявка',
			'menu_name'     => 'Заявки',
			'all_items'     => 'Все заявки',
			'edit_item'     => 'Заявка',
			'add_new'       => 'Добавить заявку',
			'add_new_item'  => 'Новая заявка',
			'search_items'  => 'Найти заявку',
			'not_found'     => 'Заявок пока нет',
		),
		'public'          => false,
		'show_ui'         => true,
		'show_in_menu'    => true,
		'menu_position'   => 3,
		'menu_icon'       => 'dashicons-email-alt',
		'supports'        => array( 'title', 'editor' ),
		'capability_type' => 'post',
		'map_meta_cap'    => true,
		'show_in_rest'    => false,
	) );
} );

/**
 * Форма заявки. $a: anchor (id блока), topic (тема для письма), fields (набор полей), button.
 */
function sz_form( $a ) {
	$a = wp_parse_args( $a, array(
		'anchor' => 'zayavka',
		'topic'  => 'Заявка с сайта',
		'fields' => array( 'name', 'phone' ),
		'button' => 'Отправить',
		'class'  => '',
	) );
	$sent = isset( $_GET['sent'] ) && '1' === $_GET['sent'] && isset( $_GET['f'] ) && $a['anchor'] === $_GET['f']; // phpcs:ignore
	$err  = isset( $_GET['err'] ) && isset( $_GET['f'] ) && $a['anchor'] === $_GET['f']; // phpcs:ignore
	ob_start();
	if ( $sent ) {
		echo '<p class="notice" role="status">Спасибо! Заявка принята — менеджер перезвонит в ближайшее время. ' . esc_html( sz_hours() ) . '.</p>';
	} elseif ( $err ) {
		echo '<p class="notice notice--err" role="alert">Проверьте номер телефона и отметьте согласие на обработку данных.</p>';
	}
	$uid = 'f-' . sanitize_key( $a['anchor'] );
	?>
	<form class="sz-form <?php echo esc_attr( $a['class'] ); ?>" method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>">
		<input type="hidden" name="action" value="sz_lead">
		<input type="hidden" name="topic" value="<?php echo esc_attr( $a['topic'] ); ?>">
		<input type="hidden" name="anchor" value="<?php echo esc_attr( $a['anchor'] ); ?>">
		<input type="hidden" name="ts" value="<?php echo esc_attr( time() ); ?>">
		<?php wp_referer_field(); ?>
		<div class="hp" aria-hidden="true"><label>Сайт <input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
		<div class="form-row">
			<?php foreach ( $a['fields'] as $f ) : ?>
				<?php if ( 'name' === $f ) : ?>
					<label class="field">Имя<input type="text" name="name" autocomplete="name"></label>
				<?php elseif ( 'phone' === $f ) : ?>
					<label class="field">Телефон<input type="tel" name="phone" required autocomplete="tel" inputmode="tel" placeholder="+7"></label>
				<?php elseif ( 'checkin' === $f ) : ?>
					<label class="field">Заезд<input type="date" name="checkin"></label>
				<?php elseif ( 'checkout' === $f ) : ?>
					<label class="field">Выезд<input type="date" name="checkout"></label>
				<?php elseif ( 'guests' === $f ) : ?>
					<label class="field">Гости<select name="guests"><option>2 взрослых</option><option>1 взрослый</option><option>2 взрослых и ребёнок</option><option>2 взрослых и 2 детей</option><option>Компания, больше 4 человек</option></select></label>
				<?php elseif ( 'ny_offer' === $f ) : ?>
					<label class="field">Что интересует<select name="offer"><option>Номер с завтраком</option><option>Путёвка «Лайт» с питанием</option><option>Лечебная программа</option><option>Коттедж</option><option>Пока не знаю, нужна консультация</option></select></label>
				<?php elseif ( 'interest' === $f ) : ?>
					<label class="field">Тема<select name="offer"><option>Бронирование и цены</option><option>Новый год</option><option>Лечебные программы</option><option>Коттеджи</option><option>Мероприятие или праздник</option><option>Другое</option></select></label>
				<?php elseif ( 'comment' === $f ) : ?>
					<label class="field field--wide">Комментарий<textarea name="comment" rows="3"></textarea></label>
				<?php elseif ( 'submit' === $f ) : ?>
					<button type="submit" class="btn btn--green"><?php echo esc_html( $a['button'] ); ?></button>
				<?php endif; ?>
			<?php endforeach; ?>
			<?php if ( ! in_array( 'submit', $a['fields'], true ) ) : ?>
				<button type="submit" class="btn btn--green"><?php echo esc_html( $a['button'] ); ?></button>
			<?php endif; ?>
		</div>
		<label class="consent" for="<?php echo esc_attr( $uid ); ?>-c"><input type="checkbox" name="consent" value="1" id="<?php echo esc_attr( $uid ); ?>-c" required><span>Даю <a href="<?php echo esc_url( home_url( '/soglasie/' ) ); ?>" target="_blank">согласие на обработку персональных данных</a> в соответствии с <a href="<?php echo esc_url( home_url( '/politika/' ) ); ?>" target="_blank">политикой</a></span></label>
	</form>
	<?php
	return ob_get_clean();
}

add_action( 'admin_post_nopriv_sz_lead', 'sz_handle_lead' );
add_action( 'admin_post_sz_lead', 'sz_handle_lead' );
function sz_handle_lead() {
	// phpcs:disable WordPress.Security.NonceVerification
	$back   = wp_get_referer();
	$back   = $back ? $back : home_url( '/' );
	$back   = preg_replace( '/#.*$/', '', $back );
	$back   = remove_query_arg( array( 'sent', 'err', 'f' ), $back );
	$anchor = sanitize_key( isset( $_POST['anchor'] ) ? wp_unslash( $_POST['anchor'] ) : 'zayavka' );
	$ok_url = add_query_arg( array( 'sent' => '1', 'f' => $anchor ), $back ) . '#' . $anchor;

	// Ловушка для ботов: скрытое поле заполнено или форма отправлена быстрее чем за 2 секунды.
	$ts = isset( $_POST['ts'] ) ? (int) $_POST['ts'] : 0;
	if ( ! empty( $_POST['website'] ) || ( $ts && time() - $ts < 2 ) ) {
		wp_safe_redirect( $ok_url );
		exit;
	}

	$get = function ( $k ) {
		return isset( $_POST[ $k ] ) ? sanitize_text_field( wp_unslash( $_POST[ $k ] ) ) : '';
	};
	$phone   = $get( 'phone' );
	$digits  = preg_replace( '/\D/', '', $phone );
	$consent = ! empty( $_POST['consent'] );

	if ( strlen( $digits ) < 10 || ! $consent ) {
		wp_safe_redirect( add_query_arg( array( 'err' => '1', 'f' => $anchor ), $back ) . '#' . $anchor );
		exit;
	}

	$rows = array(
		'Тема'        => $get( 'topic' ),
		'Имя'         => $get( 'name' ),
		'Телефон'     => $phone,
		'Интересует'  => $get( 'offer' ),
		'Заезд'       => $get( 'checkin' ),
		'Выезд'       => $get( 'checkout' ),
		'Гости'       => $get( 'guests' ),
		'Комментарий' => isset( $_POST['comment'] ) ? sanitize_textarea_field( wp_unslash( $_POST['comment'] ) ) : '',
		'Страница'    => esc_url_raw( $back ),
		'Время'       => wp_date( 'd.m.Y H:i' ),
	);
	// phpcs:enable
	$lines = array();
	foreach ( $rows as $k => $v ) {
		if ( '' !== $v ) {
			$lines[] = $k . ': ' . $v;
		}
	}
	$body  = implode( "\n", $lines );
	$title = ( $rows['Имя'] ? $rows['Имя'] : 'Без имени' ) . ' — ' . $phone;

	$post_id = wp_insert_post( array(
		'post_type'    => 'sz_lead',
		'post_status'  => 'private',
		'post_title'   => $title,
		'post_content' => $body,
	) );

	$subject = 'Заявка с сайта ' . wp_parse_url( home_url(), PHP_URL_HOST ) . ': ' . $rows['Тема'];
	$mailed  = wp_mail( sz_email(), $subject, $body, array( 'Content-Type: text/plain; charset=UTF-8' ) );
	if ( $post_id && ! is_wp_error( $post_id ) ) {
		update_post_meta( $post_id, '_sz_mail', $mailed ? 'письмо отправлено' : 'письмо НЕ отправлено' );
	}

	wp_safe_redirect( $ok_url );
	exit;
}

// Колонки в списке заявок.
add_filter( 'manage_sz_lead_posts_columns', function ( $cols ) {
	return array(
		'cb'      => $cols['cb'],
		'title'   => 'Имя и телефон',
		'sz_info' => 'Заявка',
		'sz_mail' => 'Почта',
		'date'    => 'Дата',
	);
} );
add_action( 'manage_sz_lead_posts_custom_column', function ( $col, $id ) {
	if ( 'sz_info' === $col ) {
		echo nl2br( esc_html( wp_trim_words( get_post_field( 'post_content', $id ), 40 ) ) );
	} elseif ( 'sz_mail' === $col ) {
		echo esc_html( get_post_meta( $id, '_sz_mail', true ) );
	}
}, 10, 2 );

/* ---------- Страницы темы ---------- */
/** Создаёт недостающие страницы темы. Срабатывает при активации и после обновления темы. */
function sz_ensure_pages() {
	$pages = array(
		'novyj-god' => 'Новый год 2027 в санатории «Касимовские Зори»',
		'ceny'      => 'Цены',
		'politika'  => 'Политика обработки персональных данных',
		'soglasie'  => 'Согласие на обработку персональных данных',
	);
	foreach ( $pages as $slug => $title ) {
		if ( ! get_page_by_path( $slug ) ) {
			wp_insert_post( array(
				'post_type'    => 'page',
				'post_status'  => 'publish',
				'post_name'    => $slug,
				'post_title'   => $title,
				'post_content' => '',
			) );
		}
	}
	if ( '/%postname%/' !== get_option( 'permalink_structure' ) ) {
		update_option( 'permalink_structure', '/%postname%/' );
	}
	flush_rewrite_rules();
	update_option( 'sz_pages_ver', SZ_VER );
}

add_action( 'after_switch_theme', function () {
	if ( ! get_option( 'timezone_string' ) ) {
		update_option( 'timezone_string', 'Europe/Moscow' );
	}
	update_option( 'blogname', 'Санаторий «Касимовские Зори»' );
	update_option( 'blogdescription', 'Лечение и отдых на берегу Оки' );
	sz_ensure_pages();
} );

add_action( 'init', function () {
	if ( get_option( 'sz_pages_ver' ) !== SZ_VER ) {
		sz_ensure_pages();
	}
}, 30 );

// Страницу политики WordPress тоже считает «политикой конфиденциальности».
add_action( 'init', function () {
	$p = get_page_by_path( 'politika' );
	if ( $p && (int) get_option( 'wp_page_for_privacy_policy' ) !== (int) $p->ID ) {
		update_option( 'wp_page_for_privacy_policy', $p->ID );
	}
}, 20 );

require_once get_theme_file_path( 'inc/legal.php' );
require_once get_theme_file_path( 'inc/prices-procedures.php' );

/* ---------- Таблицы цен ---------- */
function sz_fmt( $n ) {
	if ( is_string( $n ) && ! is_numeric( $n ) ) {
		return $n;
	}
	return $n ? number_format( (int) $n, 0, ',', ' ' ) : '—';
}

/** Таблица номеров: строки [категория, 1 гость, 2 гостя, 3 гостя, ребёнок осн. место, ребёнок доп. место]. */
function sz_room_table( $rows ) {
	ob_start();
	?>
	<div class="table-wrap"><table class="prices">
		<thead><tr><th>Категория номера</th><th class="num">1 гость</th><th class="num">2 гостя</th><th class="num">3 гостя</th><th class="num">Ребёнок 3–14 лет, основное место</th><th class="num">Ребёнок 3–14 лет, доп. место</th></tr></thead>
		<tbody>
		<?php foreach ( $rows as $r ) : ?>
			<tr><td><?php echo esc_html( $r[0] ); ?></td><?php for ( $i = 1; $i <= 5; $i++ ) : ?><td class="num"><?php echo esc_html( sz_fmt( $r[ $i ] ) ); ?></td><?php endfor; ?></tr>
		<?php endforeach; ?>
		</tbody>
	</table></div>
	<?php
	return ob_get_clean();
}

/** Простая таблица: $head — заголовки, $rows — строки; колонки после первой выравниваются по правому краю. */
function sz_simple_table( $head, $rows ) {
	ob_start();
	?>
	<div class="table-wrap"><table class="prices">
		<thead><tr><?php foreach ( $head as $i => $h ) : ?><th<?php echo $i ? ' class="num"' : ''; ?>><?php echo esc_html( $h ); ?></th><?php endforeach; ?></tr></thead>
		<tbody>
		<?php foreach ( $rows as $r ) : ?>
			<tr><?php foreach ( $r as $i => $c ) : ?><td<?php echo $i ? ' class="num"' : ''; ?>><?php echo esc_html( $i ? sz_fmt( $c ) : $c ); ?></td><?php endforeach; ?></tr>
		<?php endforeach; ?>
		</tbody>
	</table></div>
	<?php
	return ob_get_clean();
}
