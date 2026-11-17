<?php
get_header();
?>
<section class="sec sec--white">
	<div class="wrap doc">
		<h1>Страница не найдена</h1>
		<p>Возможно, она переехала. Начните с главной или позвоните нам: <a href="<?php echo esc_attr( sz_phone_href() ); ?>"><?php echo esc_html( sz_phone() ); ?></a>.</p>
		<p><a class="btn btn--green" href="<?php echo esc_url( home_url( '/' ) ); ?>">На главную</a> <a class="btn btn--ghost" href="<?php echo esc_url( home_url( '/novyj-god/' ) ); ?>">Новый год 2027</a></p>
	</div>
</section>
<?php
get_footer();
