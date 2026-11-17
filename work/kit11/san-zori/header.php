<!doctype html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo( 'charset' ); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1">
<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<a class="sr-only" href="#main">Перейти к содержимому</a>
<header class="site-header">
	<div class="wrap hdr-top">
		<a class="logo" href="<?php echo esc_url( home_url( '/' ) ); ?>">
			<?php echo sz_logo_svg(); // phpcs:ignore ?>
			<span><span class="logo__name">Касимовские Зори</span><span class="logo__sub">санаторий на Оке</span></span>
		</a>
		<nav class="hdr-links" aria-label="Служебное меню">
			<a class="pill" href="<?php echo esc_url( home_url( '/novyj-god/' ) ); ?>">Новый год</a>
			<a href="<?php echo esc_url( home_url( '/ceny/' ) ); ?>">Цены</a>
			<a href="<?php echo esc_url( home_url( '/#doroga' ) ); ?>">Как добраться</a>
			<a href="<?php echo esc_url( home_url( '/#zayavka' ) ); ?>">Контакты</a>
		</nav>
		<div class="hdr-cta">
			<a class="hdr-phone" href="<?php echo esc_attr( sz_phone_href() ); ?>"><b><?php echo esc_html( sz_phone() ); ?></b><span><?php echo esc_html( sz_hours() ); ?></span></a>
			<a class="btn btn--sun btn--sm" href="<?php echo esc_url( sz_form_link() ); ?>">Забронировать</a>
		</div>
	</div>
	<div class="wrap">
		<nav class="hdr-nav" aria-label="Разделы санатория">
			<?php foreach ( sz_sections() as $id => $label ) : ?>
				<a href="<?php echo esc_url( home_url( '/#' . $id ) ); ?>"><?php echo sz_icon( $id ); // phpcs:ignore ?><?php echo esc_html( $label ); ?></a>
			<?php endforeach; ?>
		</nav>
	</div>
</header>
<main id="main">
