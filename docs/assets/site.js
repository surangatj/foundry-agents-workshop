// Copy buttons on code blocks + light/dark toggle (remembered per browser).
document.querySelectorAll('.code').forEach(function (box) {
  var btn = document.createElement('button');
  btn.className = 'copy';
  btn.type = 'button';
  btn.textContent = 'Copy';
  btn.addEventListener('click', function () {
    var text = box.querySelector('pre').innerText.replace(/\n$/, '');
    function done() {
      btn.textContent = 'Copied!'; btn.classList.add('ok');
      setTimeout(function () { btn.textContent = 'Copy'; btn.classList.remove('ok'); }, 1500);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done).catch(fallback);
    } else { fallback(); }
    function fallback() {
      var ta = document.createElement('textarea'); ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); done(); } catch (e) {}
      document.body.removeChild(ta);
    }
  });
  var pre = box.querySelector('pre'), holder = document.createElement('div');
  holder.className = 'prewrap';
  pre.parentNode.insertBefore(holder, pre);
  holder.appendChild(pre);
  holder.appendChild(btn);
});

(function () {
  var root = document.documentElement, key = 'fw-theme';
  try { var saved = localStorage.getItem(key); if (saved) root.setAttribute('data-theme', saved); } catch (e) {}
  var b = document.createElement('button');
  b.className = 'theme'; b.type = 'button'; b.textContent = '◐ Theme';
  b.addEventListener('click', function () {
    var dark = root.getAttribute('data-theme') === 'dark' ||
      (!root.getAttribute('data-theme') && matchMedia('(prefers-color-scheme: dark)').matches);
    var next = dark ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem(key, next); } catch (e) {}
  });
  (document.querySelector('footer') || document.body).appendChild(b);
})();
