</main>
<footer class="site-footer">
	<div class="wrap">
		<div class="ft-top">
			<div class="ft-brand">
				<a class="logo" href="<?php echo esc_url( home_url( '/' ) ); ?>"><?php echo sz_logo_svg( '#8CC6EC' ); // phpcs:ignore ?><span class="logo__name">Касимовские Зори</span></a>
				<a class="ft-phone" href="<?php echo esc_attr( sz_phone_href() ); ?>"><?php echo esc_html( sz_phone() ); ?></a>
				<p><?php echo esc_html( sz_hours() ); ?></p>
				<p><a href="mailto:<?php echo esc_attr( sz_email() ); ?>"><?php echo esc_html( sz_email() ); ?></a></p>
				<p class="small" style="color:#A9C1D6"><?php echo esc_html( sz_address() ); ?></p>
			</div>
			<nav class="ft-col" aria-label="Лечение и отдых">
				<p class="ttl">Санаторий</p>
				<?php foreach ( sz_sections() as $id => $label ) : ?>
					<a href="<?php echo esc_url( home_url( '/#' . $id ) ); ?>"><?php echo esc_html( $label ); ?></a>
				<?php endforeach; ?>
			</nav>
			<nav class="ft-col" aria-label="Гостям">
				<p class="ttl">Гостям</p>
				<a href="<?php echo esc_url( home_url( '/novyj-god/' ) ); ?>">Новый год 2027</a>
				<a href="<?php echo esc_url( home_url( '/ceny/' ) ); ?>">Цены</a>
				<a href="<?php echo esc_url( home_url( '/#zaezd' ) ); ?>">Подготовка к заезду</a>
				<a href="<?php echo esc_url( home_url( '/#doroga' ) ); ?>">Как добраться</a>
				<a href="<?php echo esc_url( home_url( '/#zayavka' ) ); ?>">Контакты</a>
			</nav>
		</div>
		<p class="ft-warn">Имеются противопоказания. Необходима консультация специалиста.</p>
		<div class="ft-legal">
			<?php
			$company = sz_mod( 'sz_company', 'ООО «Касимовские Зори»' );
			$cid     = sz_mod( 'sz_company_id', '' );
			$lic     = sz_mod( 'sz_license', '' );
			?>
			<?php if ( $company ) : ?><p>Услуги оказывает <?php echo esc_html( $company ); ?><?php echo $cid ? ', ' . esc_html( $cid ) : ''; ?></p><?php endif; ?>
			<?php if ( $lic ) : ?><p>Лицензия на медицинскую деятельность <?php echo esc_html( $lic ); ?></p><?php endif; ?>
			<p><a href="<?php echo esc_url( home_url( '/politika/' ) ); ?>">Политика обработки персональных данных</a></p>
			<p><a href="<?php echo esc_url( home_url( '/soglasie/' ) ); ?>">Согласие на обработку данных</a></p>
			<p>Цены на сайте носят справочный характер и не являются публичной офертой.</p>
		</div>
	</div>
</footer>
<div class="mbar">
	<a class="btn btn--ghost" href="<?php echo esc_attr( sz_phone_href() ); ?>">Позвонить</a>
	<a class="btn btn--sun" href="<?php echo esc_url( sz_form_link() ); ?>">Заявка</a>
</div>
<div class="cookie" id="sz-cookie" hidden>
	<span>Сайт использует cookie и сервис Яндекс Метрика, чтобы понимать, как им пользуются. Подробнее — в <a href="<?php echo esc_url( home_url( '/politika/' ) ); ?>">политике</a>.</span>
	<button type="button" class="btn btn--sun btn--sm" id="sz-cookie-ok">Понятно</button>
</div>
<?php wp_footer(); ?>
</body>
</html>
