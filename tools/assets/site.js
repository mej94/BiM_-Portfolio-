// Chukwunedum Mejeha · BIM portfolio · vanilla ES module, no dependencies
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
document.documentElement.classList.add('js');

/* ---------- toast ---------- */
const toastEl = $('.toast');
let toastT;
function toast(msg) {
  toastEl.textContent = msg; toastEl.classList.add('on');
  clearTimeout(toastT); toastT = setTimeout(() => toastEl.classList.remove('on'), 1800);
}

/* ---------- scroll progress + nav state ---------- */
const bar = $('.progress span'), nav = $('.nav');
const darkTop = $('.hero-s, .op');
function onScroll() {
  const h = document.documentElement;
  const p = h.scrollTop / Math.max(1, h.scrollHeight - h.clientHeight);
  bar.style.transform = `scaleX(${p})`;
  const lim = darkTop ? darkTop.offsetHeight - 70 : 10;
  nav.classList.toggle('solid', h.scrollTop > lim);
}
addEventListener('scroll', onScroll, { passive: true }); onScroll();

/* ---------- theme ---------- */
function setTheme(t) {
  document.documentElement.dataset.theme = t;
  try { localStorage.setItem('theme', t); } catch (e) {}
}
function toggleTheme() {
  setTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark');
  toast(`Theme: ${document.documentElement.dataset.theme}`);
}
$$('[data-theme-toggle]').forEach(b => b.addEventListener('click', toggleTheme));

/* ---------- reveal + count up ---------- */
function countUp(el) {
  const raw = el.dataset.count, target = parseFloat(raw.replace(/,/g, ''));
  if (reduce || !isFinite(target)) return;
  const comma = raw.includes(','), dur = 1400, t0 = performance.now();
  const fmt = v => comma ? Math.round(v).toLocaleString('en-GB') : String(Math.round(v));
  const step = t => {
    const k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 4);
    el.textContent = fmt(target * e);
    if (k < 1) requestAnimationFrame(step); else el.textContent = raw;
  };
  requestAnimationFrame(step);
}
const io = new IntersectionObserver(es => es.forEach(e => {
  if (!e.isIntersecting) return;
  e.target.classList.add('in');
  $$('[data-count]', e.target).forEach(countUp);
  if (e.target.matches('[data-count]')) countUp(e.target);
  io.unobserve(e.target);
}), { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
$$('.reveal').forEach(el => io.observe(el));
$$('.hero, .op-figs').forEach(el => io.observe(el));

/* ---------- code scramble ---------- */
$$('[data-scramble]').forEach(el => {
  if (reduce) return;
  const final = el.textContent, chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-';
  let f = 0;
  const run = () => {
    el.textContent = final.split('').map((c, i) => (c === '-' || i < f / 2) ? c : chars[Math.random() * chars.length | 0]).join('');
    if (f++ < final.length * 2) requestAnimationFrame(run); else el.textContent = final;
  };
  setTimeout(run, 300);
});

/* ---------- opener crossfade ---------- */
$$('[data-fade]').forEach(box => {
  const ims = $$('img', box); if (ims.length < 2 || reduce) return;
  let i = 0;
  setInterval(() => { ims[i].classList.remove('on'); i = (i + 1) % ims.length; ims[i].classList.add('on'); }, 6500);
});

/* ---------- terminal typer ---------- */
const typer = $('[data-typer]');
if (typer) {
  const L = [
    ['<span class="p">$</span> mej audit --portfolio 2027 --projects all', 'cmd'],
    ['<span class="dim">loading 4 Revit 2027 models and 1 Navisworks federation…</span>'],
    [''],
    ['<b>[MHH ]</b> federated 7 discipline models on one origin'],
    ['       1,123 raw <span class="dim">→</span> 430 live clashes <span class="dim">→</span> <b>94 owned issues</b>, 2 RFIs'],
    ['<b>[ACL ]</b> 43 rooms <span class="dim">·</span> 718 m² <span class="dim">·</span> <b>16 sheets</b> issued at P01'],
    ['<b>[AOB ]</b> 62 rooms on Uniclass 2015 <span class="dim">·</span> IFC4 RV <span class="dim">·</span> <b>0 schema errors</b>'],
    ['<b>[PRJC]</b> warnings 56 <span class="dim">→</span> <b>7</b> <span class="dim">·</span> 609 unused elements purged'],
    [''],
    ['<span class="ok">✓</span> 4 projects ready for review'],
    ['<span class="p">$</span> ', 'end'],
  ];
  const plain = h => { const d = document.createElement('div'); d.innerHTML = h; return d.textContent; };
  if (reduce) { typer.innerHTML = L.map(l => l[0]).join('\n') + '<span class="cursor"></span>'; }
  else {
    let li = 0;
    const cursor = '<span class="cursor"></span>';
    const done = [];
    const next = () => {
      if (li >= L.length) return;
      const [h, kind] = L[li]; const txt = plain(h);
      if (kind === 'end') { typer.innerHTML = done.join('\n') + '\n' + h + cursor; return; }
      if (kind === 'cmd') {
        let c = 0;
        const t = setInterval(() => {
          typer.innerHTML = (done.length ? done.join('\n') + '\n' : '') + '<span class="p">$</span>' + txt.slice(1, ++c + 1).replace(/</g, '&lt;') + cursor;
          if (c >= txt.length - 1) { clearInterval(t); done.push(h); li++; setTimeout(next, 380); }
        }, 34);
      } else { done.push(h); typer.innerHTML = done.join('\n') + cursor; li++; setTimeout(next, h ? 230 : 90); }
    };
    setTimeout(next, 700);
  }
}

/* ---------- live BIM model in canvas ---------- */
const cv = $('#bim');
if (cv) {
  const ctx = cv.getContext('2d');
  const B = 6, NX = 7, NY = 4, LV = [0, 4.2, 8.4, 12.6];
  const S = [], D = [], P = [], K = [];   // structure, ducts, pipes, clashes
  const cx = (NX - 1) * B / 2, cy = (NY - 1) * B / 2, cz = LV[LV.length - 1] / 2;
  const pt = (x, y, z) => [x - cx, y - cy, z - cz];
  for (let i = 0; i < NX; i++) for (let j = 0; j < NY; j++) S.push([pt(i * B, j * B, 0), pt(i * B, j * B, LV[3])]);
  LV.forEach((z, k) => {
    for (let j = 0; j < NY; j++) S.push([pt(0, j * B, z), pt((NX - 1) * B, j * B, z)]);
    for (let i = 0; i < NX; i++) S.push([pt(i * B, 0, z), pt(i * B, (NY - 1) * B, z)]);
    if (k === 0) return;
    const dz = z - 0.35, dy = 1.5 * B + 0.6;
    D.push([pt(0.5 * B, dy, dz), pt((NX - 1.5) * B, dy, dz)]);
    D.push([pt((NX - 1.5) * B, dy, dz), pt((NX - 1.5) * B, 0.3 * B, dz)]);
    P.push([pt(2.5 * B, 0.2 * B, z - 1.1), pt(2.5 * B, (NY - 1.2) * B, z - 1.1)]);
    P.push([pt(4.5 * B + 0.4, 0.2 * B, z - 0.2), pt(4.5 * B + 0.4, (NY - 1.2) * B, z - 0.2)]);
    for (let i = 1; i < NX - 1; i++) if ((i + k) % 2) K.push({ p: pt(i * B, dy, dz), ph: Math.random() * 6.28 });
    K.push({ p: pt(4.5 * B + 0.4, 1 * B, z - 0.2), ph: Math.random() * 6.28 });
  });
  let W = 0, H = 0, dpr = 1, yaw = -0.7, pitch = 0.55, tYaw = 0, tPitch = 0.55, mx = 0, run = true;
  const size = () => {
    dpr = Math.min(2, devicePixelRatio || 1);
    W = cv.clientWidth; H = cv.clientHeight; cv.width = W * dpr; cv.height = H * dpr;
  };
  size(); addEventListener('resize', size);
  addEventListener('pointermove', e => { mx = e.clientX / W - .5; tPitch = 0.42 + (e.clientY / H) * 0.32; }, { passive: true });
  const proj = (p, sc, ox, oy) => {
    const cyw = Math.cos(yaw), syw = Math.sin(yaw);
    let x = p[0] * cyw - p[1] * syw, y = p[0] * syw + p[1] * cyw, z = p[2];
    const cp = Math.cos(pitch), sp = Math.sin(pitch);
    const y2 = y * cp - z * sp, z2 = y * sp + z * cp;
    const f = 90 / (90 + y2);
    return [ox + x * sc * f, oy - z2 * sc * f, y2];
  };
  const line = (a, b, sc, ox, oy) => { const A = proj(a, sc, ox, oy), B2 = proj(b, sc, ox, oy); ctx.moveTo(A[0], A[1]); ctx.lineTo(B2[0], B2[1]); return (A[2] + B2[2]) / 2; };
  let t = 0;
  const frame = () => {
    if (!run) return;
    t += 1 / 60;
    if (!reduce) tYaw += 0.0016;
    yaw += ((tYaw - 0.7 + mx * 1.2) - yaw) * 0.04; pitch += (tPitch - pitch) * 0.05;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, W, H);
    const wide = W > 980, sc = Math.min(W, H * 1.4) / (wide ? 70 : 58), ox = wide ? W * 0.6 : W * 0.5, oy = H * (wide ? 0.52 : 0.4);
    const plane = (Math.sin(t * 0.35) * 0.5 + 0.5) * LV[3] - cz;   // moving section plane
    // structure
    ctx.lineWidth = 1;
    S.forEach(s => {
      const near = Math.abs((s[0][2] + s[1][2]) / 2 - plane) < 0.7 && s[0][2] === s[1][2];
      ctx.beginPath(); line(s[0], s[1], sc, ox, oy);
      ctx.strokeStyle = near ? 'rgba(244,148,36,.55)' : 'rgba(242,241,237,.16)'; ctx.stroke();
    });
    // services
    ctx.lineWidth = 2.2; ctx.strokeStyle = 'rgba(126,170,205,.55)';
    ctx.beginPath(); D.forEach(s => line(s[0], s[1], sc, ox, oy)); ctx.stroke();
    ctx.lineWidth = 1.4; ctx.strokeStyle = 'rgba(123,199,149,.45)'; ctx.setLineDash([5, 4]);
    ctx.beginPath(); P.forEach(s => line(s[0], s[1], sc, ox, oy)); ctx.stroke(); ctx.setLineDash([]);
    // section plane outline
    const c = [pt(-1, -1, 0), pt((NX - 1) * B + 1, -1, 0), pt((NX - 1) * B + 1, (NY - 1) * B + 1, 0), pt(-1, (NY - 1) * B + 1, 0)].map(p => [p[0], p[1], plane]);
    ctx.beginPath(); c.forEach((p, i) => { const q = proj(p, sc, ox, oy); i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); }); ctx.closePath();
    ctx.fillStyle = 'rgba(244,148,36,.035)'; ctx.fill(); ctx.strokeStyle = 'rgba(244,148,36,.25)'; ctx.lineWidth = 1; ctx.stroke();
    // clashes
    K.forEach(k => {
      const q = proj(k.p, sc, ox, oy), a = (Math.sin(t * 2.2 + k.ph) * 0.5 + 0.5);
      ctx.beginPath(); ctx.arc(q[0], q[1], 3.2, 0, 6.283); ctx.fillStyle = '#F49424'; ctx.fill();
      ctx.beginPath(); ctx.arc(q[0], q[1], 4 + a * 10, 0, 6.283); ctx.strokeStyle = `rgba(244,148,36,${0.5 * (1 - a)})`; ctx.lineWidth = 1.2; ctx.stroke();
    });
    if (!reduce) requestAnimationFrame(frame);
  };
  new IntersectionObserver(([e]) => { const was = run; run = e.isIntersecting; if (run && !was) requestAnimationFrame(frame); }).observe(cv);
  requestAnimationFrame(frame);
}

/* ---------- project card spotlight + tilt ---------- */
$$('.pc').forEach(c => {
  c.addEventListener('pointermove', e => {
    const r = c.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
    c.style.setProperty('--mx', x * 100 + '%'); c.style.setProperty('--my', y * 100 + '%');
    if (!reduce && matchMedia('(hover:hover)').matches) c.style.transform = `perspective(1400px) rotateX(${(0.5 - y) * 2.2}deg) rotateY(${(x - 0.5) * 2.2}deg)`;
  });
  c.addEventListener('pointerleave', () => { c.style.transform = ''; });
});

/* ---------- skills matrix column highlight ---------- */
const mx = $('.mx');
if (mx) $$('thead a', mx).forEach(a => {
  const on = v => { $$(`td[data-p="${a.dataset.p}"]`, mx).forEach(td => td.classList.toggle('on', v)); a.classList.toggle('on', v); };
  a.addEventListener('mouseenter', () => on(true)); a.addEventListener('mouseleave', () => on(false));
  a.addEventListener('focus', () => on(true)); a.addEventListener('blur', () => on(false));
});

/* ---------- copy email ---------- */
$$('[data-copy]').forEach(b => b.addEventListener('click', async () => {
  try { await navigator.clipboard.writeText(b.dataset.copy); toast('Email copied'); }
  catch (e) { location.href = 'mailto:' + b.dataset.copy; }
}));

/* ---------- section scrollspy ---------- */
const toc = $('[data-toc]');
if (toc) {
  const links = $$('a', toc), map = new Map(links.map(a => [a.getAttribute('href').slice(1), a]));
  const spy = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return;
    links.forEach(l => l.classList.remove('on'));
    const a = map.get(e.target.id); if (a) { a.classList.add('on'); a.scrollIntoView({ block: 'nearest', inline: 'center', behavior: reduce ? 'auto' : 'smooth' }); }
  }), { rootMargin: '-45% 0px -50% 0px' });
  $$('.sheet').forEach(s => spy.observe(s));
}

/* ---------- before / after sliders ---------- */
$$('.ba-slider').forEach(s => {
  const set = v => { v = Math.max(0, Math.min(100, v)); s.style.setProperty('--pos', v + '%'); s.setAttribute('aria-valuenow', Math.round(v)); };
  const fromE = e => { const r = s.getBoundingClientRect(); set((e.clientX - r.left) / r.width * 100); };
  let down = false;
  s.addEventListener('pointerdown', e => { down = true; s.setPointerCapture(e.pointerId); fromE(e); });
  s.addEventListener('pointermove', e => { if (down) fromE(e); });
  s.addEventListener('pointerup', () => { down = false; });
  s.addEventListener('keydown', e => {
    const v = parseFloat(s.style.getPropertyValue('--pos')) || 50;
    if (e.key === 'ArrowLeft') { set(v - 5); e.preventDefault(); }
    if (e.key === 'ArrowRight') { set(v + 5); e.preventDefault(); }
  });
  // a short sweep the first time it scrolls into view, so people see it moves
  if (!reduce) new IntersectionObserver(([e], o) => {
    if (!e.isIntersecting) return; o.disconnect();
    const t0 = performance.now();
    const go = t => { const k = Math.min(1, (t - t0) / 1600); set(50 + Math.sin(k * Math.PI * 2) * 22); if (k < 1) requestAnimationFrame(go); else set(50); };
    requestAnimationFrame(go);
  }, { threshold: 0.6 }).observe(s);
});

/* ---------- lightbox with zoom and pan ---------- */
const lb = $('.lightbox');
if (lb) {
  const stage = $('.lb-stage', lb), img = $('img', lb), cap = $('.lb-cap', lb);
  let s = 1, x = 0, y = 0, fit = 1, last = null;
  const pts = new Map(); let pinch0 = 0, s0 = 1;
  const apply = () => { img.style.transform = `translate(${x}px,${y}px) scale(${s})`; };
  const reset = () => {
    const r = stage.getBoundingClientRect();
    fit = Math.min((r.width - 40) / img.naturalWidth, (r.height - 40) / img.naturalHeight, 1.5);
    s = fit; x = -img.naturalWidth * s / 2; y = -img.naturalHeight * s / 2; apply();
  };
  const zoomAt = (k, cx, cy) => {
    const r = stage.getBoundingClientRect(), px = cx - r.left - r.width / 2, py = cy - r.top - r.height / 2;
    const ns = Math.max(fit * 0.8, Math.min(fit * 10, s * k)); const f = ns / s;
    x = px - (px - x) * f; y = py - (py - y) * f; s = ns; apply();
  };
  let opener = null;
  const open = (src, text) => {
    opener = document.activeElement;
    lb.hidden = false; document.body.style.overflow = 'hidden'; cap.textContent = text || '';
    img.onload = reset; img.src = src; if (img.complete && img.naturalWidth) reset();
    $('.lb-x', lb).focus();
  };
  const close = () => { lb.hidden = true; document.body.style.overflow = ''; img.removeAttribute('src'); if (opener) opener.focus(); };
  $$('.zoom').forEach(b => b.addEventListener('click', () => {
    const fig = b.closest('figure'); open(b.dataset.full, fig ? $$('.cap', fig).map(c => c.textContent.trim()).join('  ') : '');
  }));
  $('.lb-x', lb).addEventListener('click', close);
  stage.addEventListener('wheel', e => { e.preventDefault(); zoomAt(Math.exp(-e.deltaY * 0.0015), e.clientX, e.clientY); }, { passive: false });
  stage.addEventListener('dblclick', e => zoomAt(s > fit * 1.5 ? fit / s : 2.5, e.clientX, e.clientY));
  stage.addEventListener('pointerdown', e => {
    stage.setPointerCapture(e.pointerId); pts.set(e.pointerId, e); stage.classList.add('drag'); last = e;
    if (pts.size === 2) { const [a, b] = [...pts.values()]; pinch0 = Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY); s0 = s; }
  });
  stage.addEventListener('pointermove', e => {
    if (!pts.has(e.pointerId)) return; pts.set(e.pointerId, e);
    if (pts.size === 2) {
      const [a, b] = [...pts.values()], d = Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
      zoomAt((s0 * d / pinch0) / s, (a.clientX + b.clientX) / 2, (a.clientY + b.clientY) / 2); return;
    }
    x += e.clientX - last.clientX; y += e.clientY - last.clientY; last = e; apply();
  });
  const up = e => { pts.delete(e.pointerId); if (!pts.size) stage.classList.remove('drag'); last = [...pts.values()][0] || null; };
  stage.addEventListener('pointerup', up); stage.addEventListener('pointercancel', up);
  addEventListener('keydown', e => { if (!lb.hidden && e.key === 'Escape') close(); });
  addEventListener('resize', () => { if (!lb.hidden) reset(); });
}

/* ---------- command palette ---------- */
const pal = $('.palette');
if (pal) {
  const input = $('.pal-in', pal), list = $('.pal-list', pal);
  let items = [], shown = [], sel = 0;
  const actions = [
    { t: 'Toggle dark mode', g: 'Actions', s: 'T', run: toggleTheme },
    { t: 'Copy email address', g: 'Actions', run: () => navigator.clipboard.writeText('mejehaarc@gmail.com').then(() => toast('Email copied')) },
    { t: 'Email Chukwunedum', g: 'Actions', h: 'mailto:mejehaarc@gmail.com' },
    { t: 'Open LinkedIn', g: 'Actions', h: 'https://www.linkedin.com/in/nedum-mejeha', ext: 1 },
    { t: 'Open GitHub', g: 'Actions', h: 'https://github.com/mej94', ext: 1 },
    { t: 'View the source of this site', g: 'Actions', h: 'https://github.com/mej94/bim-portfolio', ext: 1 },
  ];
  fetch('/assets/nav.json').then(r => r.json()).then(n => { items = [...n, ...actions]; }).catch(() => { items = actions; });
  const score = (q, s) => {
    if (!q) return 1; q = q.toLowerCase(); s = s.toLowerCase();
    if (s.includes(q)) return 100 - s.indexOf(q);
    let i = 0, sc = 0; for (const ch of s) { if (ch === q[i]) { i++; sc++; } if (i === q.length) return sc; } return 0;
  };
  const render = () => {
    const q = input.value.trim();
    shown = items.map(it => ({ it, sc: score(q, `${it.t} ${it.g} ${it.s || ''}`) })).filter(o => o.sc > 0)
      .sort((a, b) => q ? b.sc - a.sc : 0).slice(0, 40).map(o => o.it);
    sel = Math.min(sel, Math.max(0, shown.length - 1));
    let g = null, html = '';
    shown.forEach((it, i) => {
      if (!q && it.g !== g) { g = it.g; html += `<li class="g" role="presentation">${g}</li>`; }
      html += `<li role="option" data-i="${i}" class="${i === sel ? 'sel' : ''}"><span>${it.t}</span><small>${it.s || (q ? it.g : '')}</small></li>`;
    });
    list.innerHTML = html || '<li class="g">No match</li>';
    const el = $('.sel', list); if (el) el.scrollIntoView({ block: 'nearest' });
  };
  const go = it => {
    if (!it) return; closeP();
    if (it.run) return it.run();
    if (it.ext) return window.open(it.h, '_blank', 'noopener');
    location.href = it.h;
  };
  const openP = () => { pal.hidden = false; input.value = ''; sel = 0; render(); input.focus(); };
  const closeP = () => { pal.hidden = true; };
  input.addEventListener('input', () => { sel = 0; render(); });
  input.addEventListener('keydown', e => {
    if (e.key === 'ArrowDown') { sel = Math.min(shown.length - 1, sel + 1); render(); e.preventDefault(); }
    if (e.key === 'ArrowUp') { sel = Math.max(0, sel - 1); render(); e.preventDefault(); }
    if (e.key === 'Enter') go(shown[sel]);
    if (e.key === 'Escape') closeP();
  });
  list.addEventListener('click', e => { const li = e.target.closest('li[data-i]'); if (li) go(shown[+li.dataset.i]); });
  pal.addEventListener('click', e => { if (e.target === pal) closeP(); });
  $$('[data-palette]').forEach(b => b.addEventListener('click', openP));
  addEventListener('keydown', e => {
    const typing = /INPUT|TEXTAREA/.test(document.activeElement.tagName);
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); pal.hidden ? openP() : closeP(); }
    else if (!typing && e.key === '/' && pal.hidden) { e.preventDefault(); openP(); }
    else if (!typing && e.key.toLowerCase() === 't' && !e.ctrlKey && !e.metaKey && pal.hidden && (!lb || lb.hidden)) toggleTheme();
  });
}

/* ---------- console signature ---------- */
console.log('%cChukwunedum Mejeha%c  BIM Technician\nHand built: Python pipeline, vanilla JS, Canvas 2D. Source: https://github.com/mej94/bim-portfolio',
  'font:600 16px IBM Plex Sans,sans-serif;color:#F49424', 'font:14px IBM Plex Sans,sans-serif');
