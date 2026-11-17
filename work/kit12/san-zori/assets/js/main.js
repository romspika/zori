(function () {
  var cfg = window.SZ || {};
  var id = parseInt(cfg.metrika, 10);

  function goal(name) {
    if (id && typeof window.ym === 'function') {
      try { window.ym(id, 'reachGoal', name); } catch (e) {}
    }
  }

  // Клик по телефону — цель «phone».
  document.addEventListener('click', function (e) {
    var a = e.target.closest ? e.target.closest('a[href^="tel:"]') : null;
    if (a) goal('phone');
  });

  // Заявка отправлена — цель «lead», и убираем ?sent=1 из адреса, чтобы обновление страницы не засчитало её второй раз.
  if (cfg.sent) {
    goal('lead');
    try {
      var url = new URL(window.location.href);
      url.searchParams.delete('sent');
      url.searchParams.delete('f');
      window.history.replaceState(null, '', url.pathname + url.search + url.hash);
    } catch (e) {}
  }

  // Минимальная дата выезда — не раньше заезда.
  document.querySelectorAll('form.sz-form').forEach(function (f) {
    var ci = f.querySelector('input[name="checkin"]');
    var co = f.querySelector('input[name="checkout"]');
    var today = new Date().toISOString().slice(0, 10);
    if (ci) ci.min = today;
    if (co) co.min = today;
    if (ci && co) {
      ci.addEventListener('change', function () {
        co.min = ci.value || today;
        if (co.value && co.value < ci.value) co.value = '';
      });
    }
  });

  // Уведомление о cookie.
  var box = document.getElementById('sz-cookie');
  var ok = document.getElementById('sz-cookie-ok');
  var seen = false;
  try { seen = window.localStorage.getItem('sz-cookie') === '1'; } catch (e) {}
  if (box && !seen) box.hidden = false;
  if (ok) ok.addEventListener('click', function () {
    box.hidden = true;
    try { window.localStorage.setItem('sz-cookie', '1'); } catch (e) {}
  });
})();
