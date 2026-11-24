/* Flipper-Guide – persönliche Pinball-Strategie-App (statisch, offline)
   Bedienkonzept: Tisch wählen → unten ein Ziel wählen (Strategie, Multiball, Modus, Nachschlagen)
   → Guide Schritt für Schritt. Jeder Schritt zeigt seine Schüsse nummeriert im Spielfeld, eine Kugel
   spielt sie langsam in der Reihenfolge nach. */
(() => {
  'use strict';
  const $ = (q, el = document) => el.querySelector(q);
  const h = (tag, attrs = {}, ...kids) => {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v == null || v === false) continue;
      if (k === 'class') el.className = v;
      else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
      else if (k === 'html') el.innerHTML = v;
      else el.setAttribute(k, v === true ? '' : v);
    }
    for (const c of kids.flat()) if (c != null && c !== false) el.append(c.nodeType ? c : document.createTextNode(c));
    return el;
  };
  const SVGNS = 'http://www.w3.org/2000/svg';
  const s = (tag, attrs = {}) => { const el = document.createElementNS(SVGNS, tag); for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v); return el; };
  const store = {
    get(k, d) { try { const v = localStorage.getItem('fg.' + k); return v == null ? d : JSON.parse(v); } catch { return d; } },
    set(k, v) { try { localStorage.setItem('fg.' + k, JSON.stringify(v)); } catch { /* privat/blockiert */ } },
  };
  const toast = (msg, ms = 2600) => { const t = $('#toast'); t.textContent = msg; t.hidden = false; clearTimeout(toast._t); toast._t = setTimeout(() => (t.hidden = true), ms); };
  const FL = { L: 'linker Flipper', R: 'rechter Flipper', beide: 'beide Flipper', UL: 'oberer linker Flipper', UR: 'oberer rechter Flipper', ML: 'mittlerer linker Flipper' };
  const ICON = {
    chev: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg>',
    back: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>',
    close: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    fsOn: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg>',
    fsOff: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 4v5H4M15 4v5h5M9 20v-5H4M15 20v-5h5"/></svg>',
    replay: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12a8 8 0 1 0 2.4-5.7M4 4v4h4"/></svg>',
  };

  // ---------- Zustand ----------
  const st = {
    tables: [], data: null, view: store.get('view', 'real'),
    mode: 'menu',          // menu | guide | shot | shots
    guide: null,           // { kind, title, kicker, steps, idx }
    shotInfo: null, prevMode: null,
    sel: null,             // aktuelle Route { items:[…], single }
    curLeg: 0, corr: store.get('corr', {}), corrMode: false,
    tf: { s: 1, x: 0, y: 0 }, fit: 1, anim: null, labels: [],
  };

  // ---------- Start ----------
  async function boot() {
    registerSW();
    try {
      st.tables = await (await fetch('data/tables.json')).json();
    } catch (e) { document.body.innerHTML = '<p style="padding:24px">Daten konnten nicht geladen werden. Bitte einmal mit Internet öffnen.</p>'; return; }
    window.addEventListener('hashchange', route);
    $('#btnLib').onclick = () => {
      if (st.fromLib) { st.fromLib = false; history.back(); }
      else { history.replaceState(null, '', location.pathname + location.search); route(); }
    };
    $('#btnInfo').onclick = openInfo;
    $('#btnInfoClose').onclick = () => { $('#infoSheet').hidden = true; };
    route();
    // Test-Einstieg: ?demo=<art>:<id>:<schritt>:<schuss>:<anteil>  (art = strat|mb|mode), z. B. ?demo=mb:brick:0:0:0.6#labyrinth
    const demo = new URLSearchParams(location.search).get('demo');
    if (demo) {
      const [kind, id, si, li, fr] = demo.split(':');
      const go = () => {
        const G = guideList().flatMap(g => g[1]).find(x => x.kind === kind && x.id === id); if (!G) return;
        startGuide(G, G.kicker); st.guide.idx = +si || 0; showStep();
        setTimeout(() => { if (st.anim) st.anim.freeze(+li || 0, fr == null ? 0.6 : +fr); }, 400);
      };
      const wait = () => (st.data && $('#pfImg').complete ? setTimeout(go, 300) : setTimeout(wait, 100));
      wait();
    }
  }
  function route() {
    const id = location.hash.slice(1);
    const t = st.tables.find(x => x.id === id);
    if (t) openTable(t); else showLibrary();
  }

  // ---------- Bibliothek ----------
  function showLibrary() {
    st.fromLib = false; stopAnim(); document.title = 'Flipper-Guide';
    if ($('#table').classList.contains('fs')) toggleFs(false);
    $('#infoSheet').hidden = true;
    $('#table').hidden = true; $('#library').hidden = false;
    const list = $('#libList'); list.innerHTML = '';
    for (const t of st.tables) {
      list.append(h('button', { class: 'lib-card', style: `--card-accent:${t.accent}`, onclick: () => { st.fromLib = true; location.hash = t.id; } },
        h('div', { class: 'thumb', style: `background-image:url(${t.thumb})` }),
        h('div', { class: 'meta' }, h('div', { class: 'nm' }, t.name), h('div', { class: 's' }, `${t.manufacturer} ${t.year}`),
          h('div', { class: 's' }, t.versions), h('div', { class: 'ok', 'data-offline': t.id }, ''))));
    }
    offlineStatus().then(ok => {
      $('#libOffline').textContent = ok ? 'Alle Inhalte sind auf diesem Gerät gespeichert und funktionieren ohne Internet.' : 'Noch nicht vollständig offline gespeichert – einmal mit Internet öffnen und kurz warten.';
      document.querySelectorAll('[data-offline]').forEach(el => (el.textContent = ok ? '✓ offline verfügbar' : ''));
    });
  }

  // ---------- Tisch ----------
  async function openTable(t) {
    $('#library').hidden = true; $('#table').hidden = false;
    if (!st.data || st.data.table.id !== t.id) {
      st.data = await (await fetch(t.data)).json();
      st.sel = null; st.guide = null; st.mode = 'menu'; st.shotInfo = null;
      prepTable();
    }
    const T = st.data.table;
    document.documentElement.style.setProperty('--table', T.accent);
    $('#tName').textContent = T.name;
    $('#tSub').textContent = `${T.manufacturer} ${T.year} · ${T.system}`;
    document.title = T.name + ' – Flipper-Guide';
    if (!st.data.views[st.view]) st.view = Object.keys(st.data.views)[0];
    renderViewSeg(); setupStage(); renderPanel();
    loadImage();
  }
  // Flipperspitzen (Startpunkte der Zielrichtungen) und typische Kugelgröße je Ansicht sammeln
  function prepTable() {
    st.meta = {};
    for (const vk of Object.keys(st.data.views)) {
      const tips = [], balls = [];
      for (const sh of Object.values(st.data.shots)) {
        const g = sh.geom[vk]; if (!g) continue;
        for (const a of g.aim || []) if (a[0][1] > 0.7) tips.push(a[0]);
        for (const b of g.aimBall || []) if (b && b[0]) balls.push(b[0]);
        for (const b of g.pathBall || []) if (b) balls.push(b);
      }
      balls.sort((a, b) => a - b);
      const left = tips.length ? tips.reduce((m, p) => (p[0] < m[0] ? p : m)) : [0.4, 0.92];
      const right = tips.length ? tips.reduce((m, p) => (p[0] > m[0] ? p : m)) : [0.6, 0.92];
      st.meta[vk] = { left, right, ball: balls.length ? balls[balls.length >> 1] : 0.05 };
    }
  }

  function renderViewSeg() {
    const seg = $('#viewSeg'); seg.innerHTML = '';
    for (const k of Object.keys(st.data.views)) {
      seg.append(h('button', { role: 'tab', 'aria-selected': String(k === st.view), onclick: () => { if (st.view === k) return; st.view = k; store.set('view', k); renderViewSeg(); loadImage(); } },
        k === 'real' ? 'Echt' : k === 'art' ? 'Grafik' : 'VPX'));
    }
    seg.hidden = Object.keys(st.data.views).length < 2;
  }

  // ---------- Spielfeld: Bild, Zoom, Pan ----------
  const stage = () => $('#stage');
  function loadImage() {
    const v = st.data.views[st.view];
    const img = $('#pfImg'), wrap = $('#pfWrap'), svg = $('#pfSvg');
    wrap.style.width = v.w + 'px'; wrap.style.height = v.h + 'px';
    svg.setAttribute('viewBox', `0 0 ${v.w} ${v.h}`);
    const done = () => { if (st.sel) { st.sel = buildRoute(st.sel.steps, st.sel.opts); } fitAll(false); redraw(); if (st.sel && st.sel.items.length) focusSel(false); };
    img.onload = done;
    img.src = v.image;
    if (img.complete && img.naturalWidth) done();
  }
  function stageSize() { const r = stage().getBoundingClientRect(); return { w: r.width, h: r.height }; }
  function applyTf(animate) {
    const w = $('#pfWrap');
    w.classList.toggle('anim', !!animate);
    w.style.transform = `translate(${st.tf.x}px, ${st.tf.y}px) scale(${st.tf.s})`;
    placeLabels();
  }
  function clampTf() {
    const v = st.data.views[st.view], S = stageSize();
    st.tf.s = Math.min(Math.max(st.tf.s, st.fit * 0.9), st.fit * 6);
    const w = v.w * st.tf.s, hh = v.h * st.tf.s;
    st.tf.x = w < S.w ? (S.w - w) / 2 : Math.min(40, Math.max(S.w - w - 40, st.tf.x));
    st.tf.y = hh < S.h ? (S.h - hh) / 2 : Math.min(40, Math.max(S.h - hh - 40, st.tf.y));
  }
  function fitAll(animate = true) {
    const v = st.data.views[st.view], S = stageSize();
    if (!S.w || !S.h) return;
    st.fit = Math.min(S.w / v.w, S.h / v.h);
    st.tf = { s: st.fit, x: (S.w - v.w * st.fit) / 2, y: (S.h - v.h * st.fit) / 2 };
    applyTf(animate);
  }
  function zoomToBox(b, animate = true) {
    const v = st.data.views[st.view], S = stageSize();
    if (!S.w || !S.h) return;
    st.fit = Math.min(S.w / v.w, S.h / v.h);
    // Ganze Strecke vom Flipper bis zum Ziel soll sichtbar bleiben: nur mäßig zoomen
    const pad = 46;
    const bw = (b.x1 - b.x0) * v.w, bh = (b.y1 - b.y0) * v.h;
    let sc = Math.min((S.w - pad * 2) / Math.max(bw, 1), (S.h - pad * 2) / Math.max(bh, 1));
    sc = Math.min(Math.max(sc, st.fit), st.fit * 2.2);
    const cx = (b.x0 + b.x1) / 2 * v.w, cy = (b.y0 + b.y1) / 2 * v.h;
    st.tf = { s: sc, x: S.w / 2 - cx * sc, y: S.h / 2 - cy * sc };
    clampTf(); applyTf(animate);
  }

  function setupStage() {
    const el = stage();
    if (el._setup) return; el._setup = true;
    const pts = new Map(); let last = null, moved = false, dragShot = null, lastTap = 0;
    el.addEventListener('pointerdown', e => {
      if (e.target.closest('.stage-ui > *')) return;
      const disc = e.target.closest('.disc[data-leg]');
      if (disc && !st.corrMode) { jumpLeg(+disc.dataset.leg); return; }
      const lblEl = e.target.closest('.lbl');
      if (lblEl && !st.corrMode) { const [k, id] = lblEl.dataset.hit.split(':'); openDetail(k, id); return; }
      el.setPointerCapture(e.pointerId);
      pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
      moved = false;
      if (pts.size === 1) {
        last = { x: e.clientX, y: e.clientY };
        dragShot = null;
        if (st.corrMode && st.sel && st.sel.items.length === 1) {
          const it = st.sel.items[0];
          const under = document.elementFromPoint(e.clientX, e.clientY);
          const hitEl = under && under.closest('[data-hit]');
          if (hitEl && hitEl.dataset.hit === it.key) dragShot = { it, sx: e.clientX, sy: e.clientY, base: getCorr(it.key) };
        }
      }
    });
    el.addEventListener('pointermove', e => {
      if (!pts.has(e.pointerId)) return;
      const prev = pts.get(e.pointerId); pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
      if (pts.size === 1) {
        const dx = e.clientX - last.x, dy = e.clientY - last.y;
        moved = moved || Math.hypot(dx, dy) > 6;
        if (dragShot) {
          const v = st.data.views[st.view];
          const ox = (e.clientX - dragShot.sx) / (st.tf.s * v.w), oy = (e.clientY - dragShot.sy) / (st.tf.s * v.h);
          setCorr(dragShot.it.key, [dragShot.base[0] + ox, dragShot.base[1] + oy], false);
          st.sel = buildRoute(st.sel.steps, st.sel.opts);
          redraw(true);
          return;
        }
        if (!moved) return;
        st.tf.x += e.clientX - prev.x; st.tf.y += e.clientY - prev.y; clampTf(); applyTf(false);
      } else if (pts.size === 2) {
        moved = true;
        const [a, b] = [...pts.values()];
        const other = [...pts.entries()].find(([id]) => id !== e.pointerId)[1];
        const d0 = Math.hypot(prev.x - other.x, prev.y - other.y), d1 = Math.hypot(a.x - b.x, a.y - b.y);
        zoomAt((a.x + b.x) / 2, (a.y + b.y) / 2, d1 / Math.max(d0, 1));
      }
    });
    const end = e => {
      if (!pts.has(e.pointerId)) return;
      pts.delete(e.pointerId);
      if (dragShot) { setCorr(dragShot.it.key, getCorr(dragShot.it.key), true); dragShot = null; redraw(); toast('Korrektur gespeichert'); return; }
      if (pts.size === 0 && !moved) {
        const now = Date.now();
        const under = document.elementFromPoint(e.clientX, e.clientY);
        const hitEl = under && under.closest('[data-hit]');
        if (now - lastTap < 300) { if (st.tf.s > st.fit * 1.3) fitAll(); else zoomAt(e.clientX, e.clientY, 2.2, true); lastTap = 0; return; }
        lastTap = now;
        if (hitEl) { const [kind, id] = hitEl.dataset.hit.split(':'); setTimeout(() => { if (Date.now() - lastTap >= 280) openDetail(kind, id); }, 300); }
      }
      if (pts.size === 1) last = [...pts.values()][0];
    };
    el.addEventListener('pointerup', end); el.addEventListener('pointercancel', end);
    el.addEventListener('wheel', e => { e.preventDefault(); zoomAt(e.clientX, e.clientY, e.deltaY < 0 ? 1.15 : 1 / 1.15); }, { passive: false });
    // Größe der Bühne ändert sich (Panel, Vollbild, Drehen) → neu einpassen
    let rz = null;
    new ResizeObserver(() => { if ($('#table').hidden || !st.data) return; clearTimeout(rz); rz = setTimeout(() => (st.sel && st.sel.items.length ? focusSel(false) : fitAll(false)), 60); }).observe(el);
    $('#btnFit').onclick = () => fitAll();
    $('#btnFs').onclick = () => toggleFs();
    document.addEventListener('keydown', e => {
      if ($('#table').hidden) return;
      if (e.key === 'Escape' && $('#table').classList.contains('fs')) toggleFs(false);
      if (st.mode === 'guide' && e.key === 'ArrowRight') stepNav(1);
      if (st.mode === 'guide' && e.key === 'ArrowLeft') stepNav(-1);
    });
    $('#btnCorrReset').onclick = () => { if (!st.sel) return; st.sel.items.forEach(it => setCorr(it.key, [0, 0], true)); st.sel = buildRoute(st.sel.steps, st.sel.opts); redraw(); toast('Korrektur zurückgesetzt'); };
  }
  function toggleFs(on) {
    const t = $('#table'); on = on ?? !t.classList.contains('fs');
    t.classList.toggle('fs', on);
    $('#btnFs').setAttribute('aria-label', on ? 'Vollbild verlassen' : 'Vollbild');
    $('#btnFs').innerHTML = on ? ICON.fsOff : ICON.fsOn;
    try { if (on && document.documentElement.requestFullscreen && !document.fullscreenElement) document.documentElement.requestFullscreen().catch(() => {}); if (!on && document.fullscreenElement) document.exitFullscreen().catch(() => {}); } catch { /* iOS: CSS-Vollbild reicht */ }
  }
  function zoomAt(cx, cy, f, animate) {
    const r = stage().getBoundingClientRect();
    const px = cx - r.left, py = cy - r.top;
    const ns = Math.min(Math.max(st.tf.s * f, st.fit * 0.9), st.fit * 6);
    const k = ns / st.tf.s;
    st.tf.x = px - (px - st.tf.x) * k; st.tf.y = py - (py - st.tf.y) * k; st.tf.s = ns;
    clampTf(); applyTf(animate);
  }

  // ---------- Korrekturen ----------
  const corrKey = () => `${st.data.table.id}.${st.view}`;
  function getCorr(key) { return (st.corr[corrKey()] || {})[key] || [0, 0]; }
  function setCorr(key, off, persist) {
    const ck = corrKey(); st.corr[ck] = st.corr[ck] || {};
    if (Math.abs(off[0]) < 1e-4 && Math.abs(off[1]) < 1e-4) delete st.corr[ck][key]; else st.corr[ck][key] = [+off[0].toFixed(4), +off[1].toFixed(4)];
    if (persist) store.set('corr', st.corr);
  }
  const shiftPts = (pts, o) => pts.map(p => [p[0] + o[0], p[1] + o[1]]);
  const centroid = pts => [pts.reduce((a, p) => a + p[0], 0) / pts.length, pts.reduce((a, p) => a + p[1], 0) / pts.length];

  // ---------- Route: Schüsse eines Schritts als nummerierte Abfolge ----------
  function geomFor(kind, id) {
    if (kind === 'shot') { const sh = st.data.shots[id]; const g = sh && sh.geom[st.view]; return g && (g.outline || []).length ? g : null; }
    const ins = st.data.inserts[id]; return ins && ins.geom[st.view];
  }
  const isBumper = (id, sh) => /bump|jet|pop|sling/i.test(id + ' ' + sh.kind + ' ' + sh.en);
  const isTarget = (id, sh) => /ziel|target|drop|stand|fallziel|captive|gefangen/i.test(id + ' ' + sh.kind + ' ' + sh.en);
  const isLaneSet = (id, sh) => /lane|rollover|bahnen|inlane|outlane/i.test(id + ' ' + sh.kind + ' ' + sh.en);
  const isPlunger = (id, sh) => /plunger|launch|abschuss|shooter/i.test(id + ' ' + sh.kind + ' ' + sh.en);
  const ALT_RE = /\boder\b|eine[nrms]? der\b|beliebig|wahlweise|irgendein/i;
  const stepText = st2 => ['title', 'text', 'go', 'prep'].map(k => st2[k] || '').join(' ');

  // steps: [{ step, ph? }] – mehrere Schritte (Gesamtablauf) oder einer
  // opts: { badges, ins }  →  { items, single, steps, opts }
  function buildRoute(steps, opts = {}) {
    const items = []; let n = 0;
    for (const { step } of steps) {
      const ids = (step.shots || []).filter(id => st.data.shots[id]);
      const alt = ids.length > 1 && ALT_RE.test(stepText(step));
      if (alt) n++;
      ids.forEach((id, k) => {
        const sh = st.data.shots[id], g = geomFor('shot', id);
        if (!g) { items.push({ kind: 'shot', id, key: 'shot:' + id, missing: true }); return; }
        const parts = (g.outline || []).length > 1 && !isBumper(id, sh) && (isTarget(id, sh) || isLaneSet(id, sh)) ? g.outline.map((_, i) => i) : [null];
        // Teilziele von links nach rechts, dann von oben nach unten
        if (parts.length > 1) parts.sort((a, b) => { const ca = centroid(g.outline[a]), cb = centroid(g.outline[b]); return Math.abs(ca[0] - cb[0]) > 0.02 ? ca[0] - cb[0] : ca[1] - cb[1]; });
        parts.forEach((part, pi) => {
          const num = alt ? `${n}${String.fromCharCode(97 + k)}` : String(++n);
          items.push({ kind: 'shot', id, part, nParts: parts.length, pIdx: pi, key: 'shot:' + id, num, alt, stepRef: step });
        });
      });
    }
    for (const id of opts.ins || []) if (st.data.inserts[id]) items.push({ kind: 'ins', id, key: 'ins:' + id });
    const avail = items.filter(it => !it.missing && geomFor(it.kind, it.id));
    const shotsAvail = avail.filter(it => it.kind === 'shot');
    if (shotsAvail.length === 1 && !shotsAvail[0].alt) shotsAvail[0].num = null;
    return { items: avail, missing: items.filter(it => it.missing || !geomFor(it.kind, it.id)), single: shotsAvail.length <= 1, steps, opts };
  }

  function showRoute(steps, opts = {}) {
    st.sel = buildRoute(steps, opts);
    st.curLeg = 0;
    if (st.sel.missing.length && !st.sel.items.length && (steps.some(x => (x.step.shots || []).length) || (opts.ins || []).length))
      toast(Object.keys(st.data.views).length > 1 ? 'In dieser Ansicht nicht markiert – andere Ansicht oben rechts wählen.' : 'Für diesen Schritt gibt es keine feste Stelle im Spielfeld.');
    else if (st.sel.missing.length) toast('Einige Stellen sind in dieser Ansicht nicht markiert.');
    $('#corrBar').hidden = !(st.corrMode && st.sel.items.length === 1);
    redraw();
    // erst nach dem Neuaufbau des Panels einpassen (dessen Höhe bestimmt die Spielfeldgröße)
    requestAnimationFrame(() => { if (!st.sel) return; if (st.sel.items.length) focusSel(true); else fitAll(); });
  }
  function clearRoute() { st.sel = null; $('#corrBar').hidden = true; redraw(); requestAnimationFrame(() => fitAll()); }

  function itemGeom(it) {
    const g = geomFor(it.kind, it.id), o = getCorr(it.key);
    if (it.kind === 'ins') return { outlines: [], center: null, g, o };
    const outlines = (it.part != null ? [g.outline[it.part]] : g.outline || []).map(ol => shiftPts(ol, o));
    const center = it.part != null ? centroid(outlines[0]) : g.center ? [g.center[0] + o[0], g.center[1] + o[1]] : topPoint(outlines.flat());
    return { outlines, center, g, o };
  }
  function selBox() {
    const b = { x0: 1, y0: 1, x1: 0, y1: 0 };
    const add = p => { b.x0 = Math.min(b.x0, p[0]); b.y0 = Math.min(b.y0, p[1]); b.x1 = Math.max(b.x1, p[0]); b.y1 = Math.max(b.y1, p[1]); };
    for (const it of st.sel.items) {
      const ig = itemGeom(it);
      if (it.kind === 'ins') { for (const p of shiftPts(ig.g.points, ig.o)) add(p); continue; }
      ig.outlines.flat().forEach(add);
      for (const a of ig.g.aim || []) add(a[0]);
      if (!(ig.g.aim || []).length && st.meta && !isPlunger(it.id, st.data.shots[it.id]) && !isLaneSet(it.id, st.data.shots[it.id])) add(ig.center[0] < 0.5 ? st.meta[st.view].right : st.meta[st.view].left);
    }
    return b;
  }
  function focusSel(animate) { if (!st.sel || !st.sel.items.length) return; zoomToBox(selBox(), animate); }
  function topPoint(pts) { let t = pts[0]; for (const p of pts) if (p[1] < t[1]) t = p; const cx = pts.reduce((a, p) => a + p[0], 0) / pts.length; return [cx, t[1]]; }

  // ---------- Zeichnen ----------
  function redraw(keepAnim) {
    const svg = $('#pfSvg'); const v = st.data.views[st.view];
    if (!keepAnim) stopAnim();
    svg.innerHTML = '';
    svg.classList.toggle('corr', st.corrMode);
    const P = p => `${(p[0] * v.w).toFixed(1)},${(p[1] * v.h).toFixed(1)}`;
    const labels = [];
    if (st.sel) {
      const shotItems = st.sel.items.filter(it => it.kind === 'shot');
      st.sel.items.forEach(it => {
        const ig = itemGeom(it);
        if (it.kind === 'shot') {
          const sh = st.data.shots[it.id];
          const leg = shotItems.indexOf(it);
          const grp = s('g', { class: 'tgt', 'data-leg': leg });
          for (const ol of ig.outlines) {
            const pts = ol.map(P).join(' ');
            grp.append(s('polygon', { class: 'shot-glow', points: pts }));
            grp.append(s('polygon', { class: 'shot-outline', points: pts }));
            grp.append(s('polygon', { class: 'hit', points: pts, 'data-hit': it.key }));
          }
          svg.append(grp);
          const bmap = (it.stepRef && it.stepRef.badges) || st.sel.opts.badges;
          const bdgKey = bmap && bmap[it.id];
          const bdg = bdgKey && st.data.icons && st.data.icons[bdgKey];
          const partTxt = it.nParts > 1 ? ` · Ziel ${it.pIdx + 1}/${it.nParts}` : '';
          // Laufrichtung der Kugel am Ziel (Nummer wird dahinter gesetzt, damit Ziel und Kugel frei bleiben)
          let dir = [0, -1];
          try { const lg = legFor(it); const a = lg.pts[0], b = [ig.center[0] * v.w, ig.center[1] * v.h]; const L = Math.hypot(b[0] - a[0], b[1] - a[1]); if (L > 1) dir = [(b[0] - a[0]) / L, (b[1] - a[1]) / L]; } catch { /* Richtung bleibt oben */ }
          labels.push({ c: ig.center, dir, name: (bdg ? bdg.name : sh.name), sub: (bdg ? sh.name : sh.en) + partTxt, icon: bdg ? bdg.img : null, num: it.num, leg, kind: 'shot', key: it.key });
        } else {
          const r = ig.g.r * v.w;
          for (const p of shiftPts(ig.g.points, ig.o)) {
            svg.append(s('circle', { class: 'ins-mark', cx: p[0] * v.w, cy: p[1] * v.h, r: r * 1.25 }));
            svg.append(s('circle', { class: 'hit', cx: p[0] * v.w, cy: p[1] * v.h, r: r * 1.6, 'data-hit': it.key }));
          }
          const ins = st.data.inserts[it.id];
          shiftPts(ig.g.points, ig.o).forEach((p, j) => labels.push({ c: p, name: j === 0 ? ins.name : '', sub: 'Anzeige (Einsatz) – kein Ziel', kind: 'ins', key: it.key, ringOnly: j > 0, leg: -1 }));
        }
      });
      if (shotItems.length) runAnim(shotItems);
    }
    st.labels = labels;
    markLeg(st.curLeg);
  }
  function markLeg(i) {
    st.curLeg = i;
    document.querySelectorAll('#pfSvg .tgt').forEach(g => g.classList.toggle('cur', +g.dataset.leg === i || !st.sel || st.sel.single));
    placeLabels();
    document.querySelectorAll('#panel .rchip').forEach(c => c.classList.toggle('on', +c.dataset.leg === i));
  }

  function placeLabels() {
    let layer = $('#stage .labels');
    if (!layer) { layer = h('div', { class: 'labels' }); stage().insertBefore(layer, $('#stage .stage-ui')); }
    layer.innerHTML = '';
    if (!st.labels || !st.data || !st.sel) return;
    const v = st.data.views[st.view], S = stageSize();
    const toS = p => [st.tf.x + p[0] * v.w * st.tf.s, st.tf.y + p[1] * v.h * st.tf.s];
    const many = st.labels.filter(L => L.kind === 'shot').length > 1;
    const boxes = [];
    const lineSvg = document.createElementNS(SVGNS, 'svg'); lineSvg.setAttribute('class', 'leaders');
    layer.append(lineSvg);
    const items = st.labels.map(L => ({ L, c: toS(L.c) }));
    // Punkte entlang der aktuellen Kugelbahn (Bildschirmkoordinaten) – Beschriftungen weichen ihr aus
    const pathPts = [];
    if (st.curPath && st.curPath.length > 1) {
      for (let i = 1; i < st.curPath.length; i++) {
        const a = st.curPath[i - 1], b = st.curPath[i];
        for (let k = 0; k <= 12; k++) { const t = k / 12; pathPts.push([st.tf.x + (a[0] + (b[0] - a[0]) * t) * st.tf.s, st.tf.y + (a[1] + (b[1] - a[1]) * t) * st.tf.s]); }
      }
    }
    // Marker: nummerierte Scheiben (Abfolge) bzw. Zielring (einzelner Schuss).
    // Liegen Ziele dicht beieinander, werden die Scheiben auseinandergeschoben; ein Punkt markiert die echte Stelle.
    const OFF = 30;
    const dpos = items.map(it => (it.L.num ? [it.c[0] + it.L.dir[0] * OFF, it.c[1] + it.L.dir[1] * OFF] : [it.c[0], it.c[1]]));
    const numbered = items.map((it, i) => (it.L.num ? i : -1)).filter(i => i >= 0);
    const MIN = 36;
    for (let iter = 0; iter < 40; iter++) {
      let movedAny = false;
      for (let a = 0; a < numbered.length; a++) for (let b = a + 1; b < numbered.length; b++) {
        const A = dpos[numbered[a]], B = dpos[numbered[b]];
        let dx = B[0] - A[0], dy = B[1] - A[1]; let d = Math.hypot(dx, dy);
        if (d >= MIN) continue;
        if (d < 0.01) { dx = 1; dy = 0; d = 1; }
        const push = (MIN - d) / 2; A[0] -= dx / d * push; A[1] -= dy / d * push; B[0] += dx / d * push; B[1] += dy / d * push; movedAny = true;
      }
      if (!movedAny) break;
    }
    items.forEach((it, i) => {
      const L = it.L;
      if (L.num) {
        const [x, y] = dpos[i];
        const ln = document.createElementNS(SVGNS, 'line'); ln.setAttribute('x1', it.c[0]); ln.setAttribute('y1', it.c[1]); ln.setAttribute('x2', x); ln.setAttribute('y2', y); ln.setAttribute('class', 'tick'); lineSvg.append(ln);
        layer.append(h('div', { class: 'spot' + (L.leg === st.curLeg ? ' cur' : ''), style: `left:${it.c[0]}px;top:${it.c[1]}px` }));
        it.anchor = [x, y];
        layer.append(h('div', { class: 'disc' + (L.leg === st.curLeg ? ' cur' : '') + (L.num.length > 2 ? ' sm' : '') + (numbered.length > 4 ? ' small' : '') + (L.icon ? ' has-ico' : ''), style: `left:${x}px;top:${y}px`, 'data-leg': L.leg, role: 'button', 'aria-label': 'Schuss ' + L.num + ' ' + L.name },
          L.icon ? [h('img', { src: L.icon, alt: '' }), h('span', { class: 'dn' }, L.num)] : L.num));
      } else layer.append(h('div', { class: 'ring' + (L.kind === 'ins' ? ' ins' : ''), style: `left:${it.c[0]}px;top:${it.c[1]}px` }));
    });
    // Beschriftung: bei einer Abfolge nur für den gerade gespielten Schuss
    const show = items.filter(it => !it.L.ringOnly && (!many || it.L.kind !== 'shot' || it.L.leg === st.curLeg));
    for (const it of show.sort((a, b) => a.c[1] - b.c[1])) {
      const ac = it.anchor || it.c;
      const L = it.L, w = Math.min(250, (L.icon ? 38 : 0) + 30 + Math.max(L.name.length, (L.sub || '').length * 0.85) * 7.4), hh = 44;
      const rr = L.num ? 24 : 18;
      const cands = [[0, -(hh / 2 + rr + 12)], [0, hh / 2 + rr + 12], [-(w / 2 + rr + 10), 0], [w / 2 + rr + 10, 0], [0, -(hh / 2 + 64)], [0, hh / 2 + 64],
        [-(w / 2 + rr), -(hh / 2 + rr)], [w / 2 + rr, -(hh / 2 + rr)], [-(w / 2 + rr), hh / 2 + rr], [w / 2 + rr, hh / 2 + rr], [0, -(hh / 2 + 110)]];
      let best = null, bestScore = Infinity;
      for (const [dx, dy] of cands) {
        let x = ac[0] + dx, y = ac[1] + dy;
        x = Math.min(Math.max(x, w / 2 + 6), S.w - w / 2 - 6); y = Math.min(Math.max(y, hh / 2 + 8), S.h - hh / 2 - 6);
        const r = { x0: x - w / 2, x1: x + w / 2, y0: y - hh / 2, y1: y + hh / 2 };
        let score = Math.hypot(x - ac[0], y - ac[1]) * 0.05;
        for (const b of boxes) { const ox = Math.min(r.x1, b.x1) - Math.max(r.x0, b.x0), oy = Math.min(r.y1, b.y1) - Math.max(r.y0, b.y0); if (ox > 0 && oy > 0) score += ox * oy; }
        for (const o of items) { const dx2 = Math.max(r.x0 - o.c[0], 0, o.c[0] - r.x1), dy2 = Math.max(r.y0 - o.c[1], 0, o.c[1] - r.y1); if (Math.hypot(dx2, dy2) < 22) score += 400; }
        for (const q of pathPts) if (q[0] > r.x0 - 8 && q[0] < r.x1 + 8 && q[1] > r.y0 - 8 && q[1] < r.y1 + 8) score += 120;
        if (score < bestScore) { bestScore = score; best = { x, y, r }; }
      }
      boxes.push(best.r);
      const ln = document.createElementNS(SVGNS, 'line');
      ln.setAttribute('x1', ac[0]); ln.setAttribute('y1', ac[1]); ln.setAttribute('x2', best.x); ln.setAttribute('y2', best.y);
      ln.setAttribute('class', L.kind === 'ins' ? 'ins' : '');
      lineSvg.append(ln);
      layer.append(h('div', { class: 'lbl' + (L.kind === 'ins' ? ' ins' : ''), style: `left:${best.x}px;top:${best.y}px`, 'data-hit': L.key },
        L.icon ? h('img', { class: 'ico', src: L.icon, alt: '' }) : null,
        h('span', { class: 'lt' }, h('b', {}, L.num ? h('span', { class: 'num' }, L.num) : null, L.name), L.sub ? h('i', {}, L.sub) : null)));
    }
  }

  // ---------- Kugel-Animation ----------
  // Jeder Schuss bekommt einen Weg: vom Flipper entlang der Zielrichtung in den Eingang, weiter entlang der
  // Bahn (wenn bekannt), sonst kurz hinein bzw. bei Zielen zurückprallen. Mehrere Schüsse laufen nacheinander.
  function stopAnim() { if (st.anim) cancelAnimationFrame(st.anim.raf); st.anim = null; }
  function legFor(it) {
    const v = st.data.views[st.view], M = st.meta[st.view], sh = st.data.shots[it.id];
    const ig = itemGeom(it), g = ig.g, o = ig.o;
    const W = v.w, Hh = v.h;
    const px = p => [p[0] * W, p[1] * Hh];
    const D = M.ball * W;
    let pts = [], d = [], aimLine = null, pathLines = [];
    const target = ig.center;
    const pickAim = () => {
      const A = g.aim || []; if (!A.length) return null;
      const idx = A.map((a, i) => i);
      if (A.length === 1) return 0;
      const fl = sh.flipper;
      const low = idx.filter(i => A[i][0][1] > 0.7);
      if ((fl === 'L' || fl === 'R') && low.length) return low.sort((a, b) => A[a][0][0] - A[b][0][0])[fl === 'L' ? 0 : low.length - 1];
      // beide Flipper: den gegenüberliegenden nehmen (flacherer, sicherer Winkel)
      return idx.sort((a, b) => Math.abs(A[b][0][0] - target[0]) - Math.abs(A[a][0][0] - target[0]))[0];
    };
    const ai = pickAim();
    if (ai != null) {
      let a = g.aim[ai].map(p => [p[0] + o[0], p[1] + o[1]]);
      a[0] = g.aim[ai][0]; // Flipperspitze bleibt fest
      if (it.part != null) a = [a[0], target];
      pts = a.map(px);
      const ab = (g.aimBall || [])[ai] || [M.ball, M.ball];
      d = pts.map((_, i) => (ab[0] + (ab[1] - ab[0]) * (i / Math.max(pts.length - 1, 1))) * W);
      aimLine = pts.slice();
      if (it.part == null && g.path) {
        const pp = g.path.map(p => px([p[0] + o[0], p[1] + o[1]]));
        pathLines.push(pp);
        pts = pts.concat(pp); d = d.concat(pp.map((_, i) => ((g.pathBall || [])[i] || M.ball) * W));
        if (g.path2) { const p2 = g.path2.map(p => px([p[0] + o[0], p[1] + o[1]])); pathLines.push(p2); pts = pts.concat(p2); d = d.concat(p2.map((_, i) => ((g.path2Ball || [])[i] || M.ball) * W)); }
        return { pts, d, aimLine, pathLines, stub: null };
      }
    } else {
      const poly = ig.outlines[0] || [target];
      const lo = poly.reduce((m, p) => (p[1] > m[1] ? p : m)), hi = poly.reduce((m, p) => (p[1] < m[1] ? p : m));
      if (isPlunger(it.id, sh)) { pts = [px(lo), px(hi)]; d = [D, D]; return { pts, d, aimLine: null, pathLines, stub: null }; }
      if (isLaneSet(it.id, sh)) { const top = [target[0], hi[1]], bot = [target[0], lo[1]]; pts = [px([top[0], top[1] - 0.03]), px(bot), px([bot[0], bot[1] + 0.02])]; d = [D, D, D]; return { pts, d, aimLine: null, pathLines, stub: null }; }
      const tip = target[0] < 0.5 ? M.right : M.left;
      pts = [px(tip), px(target)]; d = [D, D];
      aimLine = pts.slice();
    }
    // Ende: bei Zielen zurückprallen, sonst ein Stück in den Schuss hinein
    const n = pts.length, a = pts[n - 2], b = pts[n - 1];
    const L = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1, ux = (b[0] - a[0]) / L, uy = (b[1] - a[1]) / L;
    const k = (isTarget(it.id, sh) || isBumper(it.id, sh)) ? -0.05 : 0.05;
    pts = pts.concat([[b[0] + ux * W * k, b[1] + uy * W * k]]); d = d.concat([d[n - 1]]);
    return { pts, d, aimLine, pathLines, stub: k < 0 ? 'bounce' : 'in' };
  }
  function jumpLeg(i) { if (st.anim && st.anim.jump) st.anim.jump(i); else markLeg(i); }
  function runAnim(items) {
    stopAnim();
    const svg = $('#pfSvg'), v = st.data.views[st.view];
    const layer = s('g'); svg.append(layer);
    const legs = items.map(it => legFor(it));
    const many = legs.length > 1;
    if (!many) for (const pl of legs[0].pathLines) layer.append(s('polyline', { class: 'path', points: pl.map(p => p.join(',')).join(' ') }));
    const ballG = s('g', { class: 'ballg' });
    const TRAIL = 4, trail = [];
    for (let i = TRAIL; i >= 1; i--) { const t = s('image', { href: 'img/ball.png', class: 'trail', opacity: (0.22 * (1 - i / (TRAIL + 1))).toFixed(2) }); trail.push(t); ballG.append(t); }
    const shadow = s('ellipse', { class: 'ball-shadow' });
    const ball = s('image', { href: 'img/ball.png', class: 'ball-img' });
    ballG.append(shadow); ballG.append(ball);
    layer.append(ballG); ballG.style.opacity = 0;
    const hit = s('circle', { class: 'hitfx', r: 1 }); layer.append(hit);
    const extra = [];
    const seglen = pts => { const L = [0]; for (let i = 1; i < pts.length; i++) L.push(L[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])); return L; };
    const speed = v.w * 0.24; // Bildpixel pro Sekunde – bewusst ruhig
    const LEAD = 900, HOLD = 1300, GAP = many ? 500 : 1400;
    legs.forEach(q => { q.L = seglen(q.pts); q.total = q.L[q.L.length - 1]; q.runDur = Math.max(1600, q.total / speed * 1000); q.dur = LEAD + q.runDur + HOLD + GAP; });
    let idx = 0, t0 = performance.now();
    const setup = () => {
      extra.forEach(e => e.remove()); extra.length = 0;
      const q = legs[idx];
      if (q.aimLine) {
        const pts = q.aimLine.map(p => p.join(',')).join(' ');
        const u = s('polyline', { class: 'aim-under', points: pts }); layer.insertBefore(u, ballG); extra.push(u);
        const l = s('polyline', { class: 'aim run', points: pts }); layer.insertBefore(l, ballG); extra.push(l);
      }
      if (many) for (const pl of q.pathLines) { const l = s('polyline', { class: 'path', points: pl.map(p => p.join(',')).join(' ') }); layer.insertBefore(l, ballG); extra.push(l); }
      hit.style.opacity = 0;
      st.curPath = q.pts; // Beschriftung soll die Kugelbahn nicht verdecken
      markLeg(idx);
    };
    const posAt = (q, dist) => {
      const L = q.L; let i = 1; while (i < L.length - 1 && L[i] < dist) i++;
      const k = Math.min(Math.max((dist - L[i - 1]) / Math.max(L[i] - L[i - 1], 1e-6), 0), 1);
      const p0 = q.pts[i - 1], p1 = q.pts[i], d0 = q.d[i - 1] || 20, d1 = q.d[i] || d0;
      return [p0[0] + (p1[0] - p0[0]) * k, p0[1] + (p1[1] - p0[1]) * k, d0 + (d1 - d0) * k];
    };
    const place = (el, p) => { el.setAttribute('x', p[0] - p[2] / 2); el.setAttribute('y', p[1] - p[2] / 2); el.setAttribute('width', p[2]); el.setAttribute('height', p[2]); };
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    // Zeitpunkt, an dem die Kugel den Eingang/das Ziel erreicht (Ende der Zielrichtung)
    legs.forEach(q => { const aimEnd = q.aimLine ? seglen(q.aimLine).slice(-1)[0] : q.total; q.hitAt = aimEnd; });
    setup();
    const tick = now => {
      let q = legs[idx]; let t = now - t0;
      if (t > q.dur) { idx = (idx + 1) % legs.length; t0 = now; setup(); q = legs[idx]; t = 0; }
      const tr = t - LEAD;
      if (!reduce && q.total && tr >= 0 && tr <= q.runDur + HOLD) {
        const e = Math.min(tr / q.runDur, 1);
        const ease = e < 0.5 ? 2 * e * e : 1 - Math.pow(-2 * e + 2, 2) / 2; // sanft anrollen und auslaufen
        const dist = ease * q.total;
        const p = posAt(q, dist);
        p[2] = Math.max(p[2], 16 / st.tf.s); // in der Gesamtansicht nicht kleiner als 16 Bildschirmpunkte
        place(ball, p);
        shadow.setAttribute('cx', p[0] + p[2] * 0.12); shadow.setAttribute('cy', p[1] + p[2] * 0.22);
        shadow.setAttribute('rx', p[2] * 0.5); shadow.setAttribute('ry', p[2] * 0.42);
        trail.forEach((el, i) => { const tp = posAt(q, Math.max(0, dist - (TRAIL - i) * p[2] * 0.45)); tp[2] = p[2]; place(el, tp); });
        ballG.style.opacity = tr > q.runDur ? Math.max(0, 1 - (tr - q.runDur) / HOLD) : Math.min(1, tr / 250);
        // Treffer-Puls, sobald die Kugel ankommt
        if (dist >= q.hitAt - 1) {
          const hp = posAt(q, q.hitAt); const age = Math.min(1, (dist - q.hitAt) / Math.max(q.total - q.hitAt, 1) * 0.5 + (tr > q.runDur ? (tr - q.runDur) / HOLD : 0));
          hit.setAttribute('cx', hp[0]); hit.setAttribute('cy', hp[1]); hit.setAttribute('r', hp[2] * (0.6 + age * 1.6)); hit.style.opacity = Math.max(0, 0.9 - age);
        } else hit.style.opacity = 0;
      } else { ballG.style.opacity = 0; hit.style.opacity = 0; }
      st.anim.raf = requestAnimationFrame(tick);
    };
    st.anim = { raf: requestAnimationFrame(tick), jump: i => { idx = Math.max(0, Math.min(legs.length - 1, i)); t0 = performance.now(); setup(); },
      // Test-Hilfe: Animation an einer Stelle anhalten (Schuss i, Anteil f der Strecke)
      freeze: (i, f) => { cancelAnimationFrame(st.anim.raf); idx = i; setup(); const now = performance.now(); t0 = now - (LEAD + legs[i].runDur * f); tick(now); cancelAnimationFrame(st.anim.raf); } };
  }

  // ---------- Guides ----------
  const PH = { way: 'Ablauf', prep: 'Vorbereiten', start: 'Starten', score: 'Punkten' };
  function mbSteps(mb) {
    const prep = (mb.prep || []).map(x => ({ ...x, ph: 'prep' }));
    const start = mb.start ? [{ ...mb.start, ph: 'start' }] : [];
    const score = (mb.score || []).map(x => ({ ...x, ph: 'score' }));
    const way = [...prep, ...start].filter(x => (x.shots || []).length && !x.optional);
    const steps = [...prep, ...start, ...score];
    if (way.length > 1 || (way.length === 1 && way[0].shots.length > 1)) {
      steps.unshift({ ph: 'way', title: 'So startest du ' + mb.name, way, text: '' });
    }
    return steps;
  }
  function guideList() {
    const D = st.data, g = [];
    if (D.strategies?.length) g.push(['Strategie', D.strategies.map(S => ({ kicker: 'Strategie', kind: 'strat', id: S.id, title: S.title, sub: S.subtitle, steps: () => S.steps })) ]);
    if (D.multiballs?.length) g.push(['Multibälle', D.multiballs.map(mb => ({ kicker: 'Multiball', kind: 'mb', id: mb.id, title: mb.name, sub: [mb.tag, mb.balls].filter(Boolean).join(' · '), steps: () => mbSteps(mb) }))]);
    if (D.modes?.length) g.push(['Modi', D.modes.map(m => ({ kicker: 'Modus', kind: 'mode', id: m.id, title: m.name, sub: [m.film, m.time].filter(x => x && x !== '–').join(' · '), steps: () => (m.steps && m.steps.length ? m.steps : [{ title: m.name, text: m.text || '', shots: m.shots || [] }]) }))]);
    return g;
  }
  function startGuide(G, kicker) {
    const steps = G.steps();
    const off = steps[0] && steps[0].ph === 'way' ? 0 : 1;
    st.guide = { ...G, kicker, steps, idx: 0, ph0: i => i + off };
    st.mode = 'guide'; renderPanel(); showStep();
  }
  function stepRoute(step) {
    if (step.ph === 'way') return step.way.map(x => ({ step: x }));
    return [{ step }];
  }
  function showStep() {
    const G = st.guide, step = G.steps[G.idx];
    renderPanel();
    showRoute(stepRoute(step), { badges: step.badges });
    renderPanel(); // Route-Chips brauchen die Nummern
  }
  function stepNav(d) {
    const G = st.guide; if (!G) return;
    const n = G.idx + d;
    if (n >= G.steps.length) { closeGuide(); toast('Guide beendet'); return; }
    if (n < 0) return;
    G.idx = n; showStep();
  }
  function closeGuide() { st.guide = null; st.mode = 'menu'; clearRoute(); renderPanel(); }

  // ---------- Panel unten (bzw. rechts) ----------
  function renderPanel() {
    const p = $('#panel'); p.innerHTML = ''; p.className = 'panel ' + st.mode;
    ({ menu: panelMenu, guide: panelGuide, shot: panelShot, shots: panelShots })[st.mode](p);
  }
  function panelMenu(p) {
    p.append(h('div', { class: 'p-head' }, h('div', { class: 'p-title' }, 'Was möchtest du spielen?'), h('div', { class: 'p-hint' }, 'Ziel wählen – die Kugel zeigt dir Schuss für Schuss den Weg.')));
    const body = h('div', { class: 'p-body' });
    for (const [grp, list] of guideList()) {
      if (!list.length) continue;
      body.append(h('div', { class: 'grp' }, grp));
      const box = h('div', { class: 'rows' });
      for (const G of list) {
        const n = G.steps().length;
        box.append(h('button', { class: 'row-item', onclick: () => startGuide(G, G.kicker) },
          h('span', { class: 'ri-main' }, h('span', { class: 'ri-t' }, G.title), h('span', { class: 'ri-s' }, [G.sub, `${n} Schritt${n === 1 ? '' : 'e'}`].filter(Boolean).join(' · '))),
          h('span', { class: 'ri-chev', html: ICON.chev })));
      }
      body.append(box);
    }
    body.append(h('div', { class: 'grp' }, 'Nachschlagen'));
    body.append(h('div', { class: 'rows' },
      h('button', { class: 'row-item', onclick: () => { st.mode = 'shots'; renderPanel(); } },
        h('span', { class: 'ri-main' }, h('span', { class: 'ri-t' }, 'Alle Schüsse und Ziele'), h('span', { class: 'ri-s' }, `${Object.keys(st.data.shots).length} Schüsse · antippen zeigt Weg und Erklärung`)), h('span', { class: 'ri-chev', html: ICON.chev })),
      h('button', { class: 'row-item', onclick: openInfo },
        h('span', { class: 'ri-main' }, h('span', { class: 'ri-t' }, 'Info, Quellen und Korrekturen'), h('span', { class: 'ri-s' }, 'Tischfassung, Regelstand, Offline, Begriffe')), h('span', { class: 'ri-chev', html: ICON.chev }))));
    p.append(body);
  }
  function panelGuide(p) {
    const G = st.guide, step = G.steps[G.idx], last = G.idx === G.steps.length - 1;
    p.append(h('div', { class: 'g-top' },
      h('button', { class: 'icon-btn sm', 'aria-label': 'Guide schließen', onclick: closeGuide, html: ICON.close }),
      h('div', { class: 'g-name' }, h('span', { class: 'g-kicker' }, G.kicker), h('span', { class: 'g-title' }, G.title)),
      h('button', { class: 'icon-btn sm', 'aria-label': 'Animation neu starten', onclick: () => jumpLeg(0), html: ICON.replay })));
    // Fortschritt: antippbare Schritte
    const dots = h('div', { class: 'g-dots', role: 'tablist' });
    G.steps.forEach((x, i) => dots.append(h('button', { class: 'dot' + (i === G.idx ? ' on' : '') + (i < G.idx ? ' done' : '') + (x.ph ? ' ' + x.ph : ''), 'aria-label': `Schritt ${i + 1}: ${x.title}`, onclick: () => { G.idx = i; showStep(); } }, x.ph === 'way' ? '★' : String(G.ph0(i)))));
    p.append(dots);
    const body = h('div', { class: 'g-body' });
    body.append(h('div', { class: 'g-step' },
      h('div', { class: 'g-n' + (step.ph ? ' ' + step.ph : '') }, step.ph === 'way' ? '★' : String(G.ph0(G.idx))),
      h('div', { class: 'g-st' }, step.ph ? h('span', { class: 'ph ' + step.ph }, PH[step.ph] + (step.optional ? ' · optional' : '')) : null, h('div', { class: 'g-stt' }, step.title))));
    if (step.ph === 'way') {
      // Zusammenfassung: welche Nummern gehören zu welchem Schritt
      const parts = []; for (const x of step.way) { const its = st.sel ? st.sel.items.filter(it => it.stepRef === x) : []; if (!its.length) continue; const a = its[0].num, b = its[its.length - 1].num; parts.push(`${a === b ? a : a + '–' + b} ${x.title}`); }
      body.append(h('div', { class: 'g-text' }, parts.join(' · ') || 'Die Schritte im Überblick.'));
      const opt = G.steps.filter(x => x.optional && (x.shots || []).length);
      if (opt.length) body.append(h('div', { class: 'g-note' }, 'Optional: ' + opt.map(x => x.title).join(', ') + '.'));
    } else {
      const det = h('div', { class: 'g-text' });
      if (step.prep) det.append(h('div', {}, h('em', {}, 'Vorbereiten '), step.prep));
      if (step.go) det.append(h('div', {}, h('em', {}, 'Wohin '), step.go));
      if (step.why) det.append(h('div', {}, h('em', {}, 'Bringt '), step.why));
      if (step.text) det.append(h('div', {}, step.text));
      if (step.sources) det.append(h('div', { class: 'src' }, srcText(step.sources)));
      body.append(det);
    }
    // Abfolge der Schüsse dieses Schritts (antippen = Kugel dorthin)
    if (st.sel) {
      const shots = st.sel.items.filter(it => it.kind === 'shot');
      if (shots.length > 1) {
        const rc = h('div', { class: 'rchips' });
        shots.forEach((it, i) => rc.append(h('button', { class: 'rchip' + (i === st.curLeg ? ' on' : ''), 'data-leg': i, onclick: () => jumpLeg(i) }, h('b', {}, it.num), it.nParts > 1 ? (it.pIdx === 0 ? st.data.shots[it.id].name + ' – Ziel 1' : `Ziel ${it.pIdx + 1}`) : st.data.shots[it.id].name)));
        body.append(rc);
        const anyAlt = shots.some(it => it.alt);
        const free = step.ph !== 'way' && !anyAlt && shots.length > 1 && !/dann|danach|zuerst|anschließend|→|reihenfolge/i.test(stepText(step));
        if (anyAlt) body.append(h('div', { class: 'g-note' }, 'Buchstaben (2a, 2b …) = eine davon reicht.'));
        else if (free) body.append(h('div', { class: 'g-note' }, 'Alle nötig, Reihenfolge laut Regeln frei.'));
      } else if (!shots.length && !(step.shots || []).length && step.ph !== 'way') body.append(h('div', { class: 'g-note' }, 'Kein fester Schuss – Hinweis lesen.'));
      else if (!shots.length) body.append(h('div', { class: 'g-note warn' }, 'Diese Stelle ist im Spielfeldbild nicht markiert (siehe Info → Grenzen).'));
      if (shots.length && st.sel.missing.length) body.append(h('div', { class: 'g-note warn' }, 'Nicht markiert: ' + [...new Set(st.sel.missing.map(it => st.data.shots[it.id].name))].join(', ') + '.'));
    }
    p.append(body);
    p.append(h('div', { class: 'g-nav' },
      h('button', { class: 'pill ghost', disabled: G.idx === 0, onclick: () => stepNav(-1) }, '‹ Zurück'),
      h('div', { class: 'g-count' }, `${G.idx + 1} / ${G.steps.length}`),
      h('button', { class: 'pill primary', onclick: () => stepNav(1) }, last ? 'Fertig ✓' : 'Weiter ›')));
  }
  function openDetail(kind, id) {
    if (st.mode !== 'shot') st.prevMode = st.mode;
    st.shotInfo = { kind, id };
    st.mode = 'shot'; renderPanel();
    showRoute([{ step: { shots: kind === 'shot' ? [id] : [] } }], { ins: kind === 'ins' ? [id] : [] });
  }
  function backFromDetail() {
    st.mode = st.prevMode && st.prevMode !== 'shot' ? st.prevMode : 'menu';
    if (st.mode === 'guide' && st.guide) showStep(); else { if (st.mode !== 'shots') clearRoute(); renderPanel(); }
  }
  function panelShot(p) {
    const D = st.shotInfo;
    p.append(h('div', { class: 'g-top' },
      h('button', { class: 'icon-btn sm', 'aria-label': 'Zurück', onclick: backFromDetail, html: ICON.back }),
      h('div', { class: 'g-name' }, h('span', { class: 'g-kicker' }, D.kind === 'shot' ? 'Schuss' : 'Anzeige (Einsatz)'), h('span', { class: 'g-title' }, D.kind === 'shot' ? st.data.shots[D.id].name : st.data.inserts[D.id].name))));
    const body = h('div', { class: 'p-body detail' });
    if (D.kind === 'shot') {
      const sh = st.data.shots[D.id];
      body.append(h('div', { class: 'en' }, `${sh.en} · ${sh.kind}`),
        h('div', { class: 'row' }, h('span', { class: 'k' }, 'Schießen von'), sh.flipper ? FL[sh.flipper] || sh.flipper : 'nicht direkt – siehe Beschreibung'),
        sh.icon && st.data.icons && st.data.icons[sh.icon] ? h('div', { class: 'row icon-row' }, h('span', { class: 'k' }, 'Sammelt'), h('span', { class: 'ir' }, h('img', { src: st.data.icons[sh.icon].img, alt: '' }), st.data.icons[sh.icon].name)) : null,
        h('div', { class: 'row' }, h('span', { class: 'k' }, 'Was ist das?'), sh.what),
        h('div', { class: 'row' }, h('span', { class: 'k' }, 'Wohin läuft die Kugel?'), sh.returns),
        h('div', { class: 'row' }, h('span', { class: 'k' }, 'Bringt'), h('ul', {}, (sh.awards || []).map(a => h('li', {}, a)))),
        h('div', { class: 'row' }, h('span', { class: 'k' }, 'Im Bild'), sh.visibility, getCorr('shot:' + D.id)[0] || getCorr('shot:' + D.id)[1] ? h('span', { class: 'badge warn' }, 'von dir korrigiert') : null),
        h('div', { class: 'src' }, srcText(sh.sources)));
    } else {
      const ins = st.data.inserts[D.id];
      body.append(h('div', { class: 'en' }, `${ins.en} · Anzeige, kein Ziel`), h('div', { class: 'row' }, ins.text),
        !ins.geom[st.view] ? h('div', { class: 'row muted' }, 'In dieser Ansicht nicht markiert.') : null);
    }
    p.append(body);
  }
  function panelShots(p) {
    p.append(h('div', { class: 'g-top' },
      h('button', { class: 'icon-btn sm', 'aria-label': 'Zurück', onclick: () => { st.mode = 'menu'; clearRoute(); renderPanel(); }, html: ICON.back }),
      h('div', { class: 'g-name' }, h('span', { class: 'g-kicker' }, 'Nachschlagen'), h('span', { class: 'g-title' }, 'Schüsse und Ziele'))));
    const body = h('div', { class: 'p-body' });
    const grid = h('div', { class: 'shot-grid' });
    for (const [id, sh] of Object.entries(st.data.shots)) {
      grid.append(h('button', { class: 'shot-btn', onclick: () => openDetail('shot', id) },
        h('b', {}, sh.name), h('span', {}, `${sh.en}${sh.flipper ? ' · ' + (sh.flipper === 'beide' ? 'L/R' : sh.flipper) : ''}${geomFor('shot', id) ? '' : ' · nicht markiert'}`)));
    }
    body.append(grid);
    if (Object.keys(st.data.inserts || {}).length) {
      body.append(h('div', { class: 'grp' }, 'Anzeigen (Einsätze) – nur Lichter, keine Ziele'));
      const g2 = h('div', { class: 'shot-grid' });
      for (const [id, ins] of Object.entries(st.data.inserts)) g2.append(h('button', { class: 'shot-btn ins', onclick: () => openDetail('ins', id) }, h('b', {}, ins.name), h('span', {}, ins.en)));
      body.append(g2);
    }
    p.append(body);
  }
  function srcText(ids) {
    if (!ids || !ids.length) return 'Keine Quelle – ehrlich offen.';
    const names = { rules: st.data && st.data.table.id === 'harrypotter' ? 'Regel-Flowchart' : 'Rulesheet', manual: 'Hersteller-Handbuch', vpw: 'VPX-Tischdatei', vpx: 'VPX-Tischdatei', photo: 'Foto', rules10: 'Rulesheet 1.0', script: 'Tisch-Script', card: 'Spielanleitung' };
    return 'Quelle: ' + ids.map(i => names[i] || i).join(', ');
  }

  // ---------- Info (eigenes Blatt) ----------
  function openInfo() {
    const body = $('#infoBody'); body.innerHTML = '';
    infoContent(body);
    $('#infoSheet').hidden = false; body.scrollTop = 0;
  }
  function infoContent(body) {
    const T = st.data.table, v = st.data.views[st.view];
    body.append(h('div', { class: 'sec-h' }, 'Tischfassung'));
    body.append(h('dl', { class: 'card kv' },
      h('dt', {}, 'Tisch'), h('dd', {}, `${T.name} (${T.manufacturer}, ${T.year})`),
      h('dt', {}, 'System'), h('dd', {}, `${T.system}${T.design ? ', Design ' + T.design : ''}`),
      h('dt', {}, 'Fassungen'), h('dd', {}, T.editions || ''),
      h('dt', {}, 'Regelstand'), h('dd', {}, T.ruleVersion || ''),
      h('dt', {}, 'Ansicht'), h('dd', {}, `${v.label}: ${v.note}`),
      h('dt', {}, 'Inhaltsstand'), h('dd', {}, T.contentDate ? new Date(T.contentDate).toLocaleDateString('de-DE') : '')));

    body.append(h('div', { class: 'sec-h' }, 'So funktioniert die Anleitung'));
    body.append(h('ul', { class: 'card info', style: 'padding:12px 14px 12px 30px' },
      h('li', {}, 'Große Zahlen im Spielfeld = Reihenfolge der Schüsse. Die Kugel spielt sie nacheinander nach; Zahl antippen springt dorthin.'),
      h('li', {}, 'Gestrichelte Linie = Zielrichtung vom Flipper. Blaue Linie = bekannter Bahnverlauf (Rampe).'),
      h('li', {}, 'Grüne Kreise = Anzeigen (Einsätze), keine Ziele.'),
      h('li', {}, 'Beschriftung antippen zeigt die Erklärung zum Schuss. Doppeltipp zoomt.')));

    body.append(h('div', { class: 'sec-h' }, 'Für unterwegs'));
    const off = h('div', { class: 'card', style: 'padding:12px 14px' }, h('div', { id: 'offTxt' }, 'Prüfe Offline-Speicher …'));
    off.append(h('div', { class: 'btn-row' }, h('button', { class: 'btn', onclick: updateNow }, 'Nach Aktualisierung suchen')));
    body.append(off);
    offlineStatus().then(ok => { const t = $('#offTxt'); if (t) t.textContent = ok ? '✓ Sammlung vollständig auf diesem Gerät gespeichert – funktioniert ohne Internet, auch nach Neustart. Eine fehlgeschlagene Aktualisierung lässt den gespeicherten Stand unverändert.' : 'Noch nicht vollständig gespeichert. App einmal mit Internet geöffnet lassen, bis hier ein Haken erscheint. Tipp iPhone: Teilen → „Zum Home-Bildschirm“.'; });

    body.append(h('div', { class: 'sec-h' }, 'Markierungen korrigieren'));
    const cb = h('input', { type: 'checkbox', id: 'corrToggle' }); cb.checked = st.corrMode;
    cb.onchange = () => { st.corrMode = cb.checked; $('#corrBar').hidden = !(st.corrMode && st.sel && st.sel.items.length === 1); redraw(); toast(st.corrMode ? 'Korrekturmodus an: einen Schuss wählen und im Spielfeld verschieben' : 'Korrekturmodus aus'); };
    body.append(h('div', { class: 'card' }, h('div', { class: 'switch-row' }, cb, h('label', { for: 'corrToggle' }, 'Korrekturmodus (Markierung mit dem Finger verschieben)'))));
    const n = Object.values(st.corr).reduce((a, o) => a + Object.keys(o).length, 0);
    const ta = h('textarea', { class: 'export', readonly: true }); ta.value = JSON.stringify({ app: 'flipper-guide', table: T.id, date: new Date().toISOString().slice(0, 10), corrections: st.corr }, null, 1);
    body.append(h('div', { class: 'card', style: 'padding:12px 14px' },
      h('div', {}, `${n} Korrektur(en) gespeichert. Zum Übernehmen in die App diesen Text an Claude schicken:`),
      h('div', { class: 'btn-row' },
        h('button', { class: 'btn primary', onclick: () => shareText(ta.value) }, 'Korrekturen teilen/kopieren'),
        h('button', { class: 'btn', onclick: () => { if (confirm('Alle eigenen Korrekturen löschen?')) { st.corr = {}; store.set('corr', {}); redraw(); openInfo(); } } }, 'Alle löschen')),
      ta));

    body.append(h('div', { class: 'sec-h' }, 'Quellen'));
    body.append(h('ul', { class: 'card srcs info', style: 'padding:12px 14px 4px 30px' }, (st.data.sources || []).map(sr => h('li', {}, h('div', {}, sr.title), h('div', { class: 'muted', style: 'font-size:13px' }, sr.use), sr.url ? h('a', { class: 'u', href: sr.url, target: '_blank', rel: 'noopener' }, sr.url) : null))));
    body.append(h('div', { class: 'sec-h' }, 'Grenzen dieser Anleitung'));
    body.append(h('ul', { class: 'card info', style: 'padding:12px 14px 12px 30px' }, (st.data.limits || []).map(l => h('li', {}, l))));
    if ((st.data.glossary || []).length) {
      body.append(h('div', { class: 'sec-h' }, 'Begriffe'));
      body.append(h('dl', { class: 'card gl', style: 'padding:4px 14px 14px' }, st.data.glossary.flatMap(g => [h('dt', {}, g.term), h('dd', {}, g.text)])));
    }
    body.append(h('p', { class: 'muted', style: 'font-size:12px;margin:16px 4px' }, `App-Stand ${window.FG_VERSION || ''} · Private Nutzung.`));
  }
  async function shareText(t) {
    try { if (navigator.share) { await navigator.share({ title: 'Flipper-Guide Korrekturen', text: t }); return; } } catch { /* abgebrochen */ }
    try { await navigator.clipboard.writeText(t); toast('In die Zwischenablage kopiert'); } catch { toast('Bitte den Text unten markieren und kopieren'); }
  }

  // ---------- Offline ----------
  function registerSW() {
    if (!('serviceWorker' in navigator)) return;
    // Neue Version: sobald sie vollständig gespeichert und aktiv ist, lädt die Seite einmal neu
    const hadCtrl = !!navigator.serviceWorker.controller; let reloaded = false;
    navigator.serviceWorker.addEventListener('controllerchange', () => { if (!hadCtrl || reloaded) return; reloaded = true; location.reload(); });
    navigator.serviceWorker.register('sw.js', { updateViaCache: 'none' }).then(reg => {
      reg.addEventListener('updatefound', () => { if (reg.installing && navigator.serviceWorker.controller) toast('Neue Version wird geladen …', 4000); });
      document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible') reg.update().catch(() => {}); });
    }).catch(() => {});
  }
  async function offlineStatus() {
    try {
      if (!('caches' in window) || !navigator.serviceWorker) return false;
      await navigator.serviceWorker.ready;
      const r = await fetch('sw-manifest.json', { cache: 'no-store' }).catch(() => null) || await caches.match('sw-manifest.json');
      const man = await r.json(); window.FG_VERSION = man.version;
      const c = await caches.open('fg-' + man.version);
      for (const a of man.assets) if (!(await c.match(a))) return false;
      return true;
    } catch { return false; }
  }
  async function updateNow() {
    if (!navigator.serviceWorker) return;
    const reg = await navigator.serviceWorker.getRegistration();
    if (!reg) { toast('Kein Offline-Speicher aktiv'); return; }
    try { await reg.update(); toast(reg.installing || reg.waiting ? 'Neue Version wird gespeichert …' : 'Du hast den aktuellen Stand.'); } catch { toast('Keine Verbindung – gespeicherter Stand bleibt erhalten.'); }
  }

  boot();
})();
