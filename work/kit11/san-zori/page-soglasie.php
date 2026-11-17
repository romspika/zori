<?php
get_header();
?>
<section class="sec sec--white">
	<div class="wrap doc">
		<h1>Согласие на обработку персональных данных</h1>
		<?php echo sz_consent_html(); // phpcs:ignore ?>
	</div>
</section>
<?php
get_footer();
