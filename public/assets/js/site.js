// Mobile navigation toggle
(function () {
  var nav = document.getElementById('site-nav');
  var shade = document.querySelector('.nav-shade');
  var openBtn = document.querySelector('.nav-toggle');
  var closeBtn = document.querySelector('.nav-close');
  if (!nav || !openBtn) return;
  function set(open) {
    nav.classList.toggle('open', open);
    if (shade) shade.classList.toggle('open', open);
    openBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    document.body.style.overflow = open ? 'hidden' : '';
    if (open && closeBtn) closeBtn.focus();
  }
  openBtn.addEventListener('click', function () { set(true); });
  if (closeBtn) closeBtn.addEventListener('click', function () { set(false); openBtn.focus(); });
  if (shade) shade.addEventListener('click', function () { set(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && nav.classList.contains('open')) { set(false); openBtn.focus(); } });
})();
