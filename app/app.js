/* Flipper-Guide – persönliche Pinball-Strategie-App (statisch, offline) */
(() => {
  'use strict';
  const $ = (s, el = document) => el.querySelector(s);
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
  const FL = { L: 'linker Flipper', R: 'rechter Flipper', beide: 'beide Flipper' };

  // ---------- Zustand ----------
  const st = {
    tables: [], data: null, view: store.get('view', 'real'), tab: store.get('tab', 'strategy'),
    strat: store.get('strat', 'solid'), openMb: null, sel: null, seq: null, seqIdx: -1,
    shotDetail: null, corr: store.get('corr', {}), corrMode: false,
    tf: { s: 1, x: 0, y: 0 }, fit: 1, anim: null,
  };

  // ---------- Start ----------
  async function boot() {
    registerSW();
    try {
      st.tables = await (await fetch('data/tables.json')).json();
    } catch (e) { document.body.innerHTML = '<p style="padding:24px">Daten konnten nicht geladen werden. Bitte einmal mit Internet öffnen.</p>'; return; }
    window.addEventListener('hashchange', route);
    route();
  }
  function route() {
    const id = location.hash.slice(1);
    const t = st.tables.find(x => x.id === id);
    if (t) openTable(t);
    else if (!id && st.tables.length === 1 && !store.get('libVisited', false)) { location.replace('#' + st.tables[0].id); }
    else showLibrary();
  }

  // ---------- Bibliothek ----------
  function showLibrary() {
    store.set('libVisited', true);
    stopAnim();
    $('#table').hidden = true; $('#library').hidden = false;
    const list = $('#libList'); list.innerHTML = '';
    for (const t of st.tables) {
      list.append(h('button', { class: 'lib-card', style: `--card-accent:${t.accent}`, onclick: () => (location.hash = t.id) },
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
      st.sel = null; st.seq = null; st.shotDetail = null;
    }
    const T = st.data.table;
    document.documentElement.style.setProperty('--table', T.accent);
    $('#tName').textContent = T.name;
    $('#tSub').textContent = `${T.manufacturer} ${T.year} · ${T.system}`;
    document.title = T.name + ' – Flipper-Guide';
    if (!st.data.views[st.view]) st.view = Object.keys(st.data.views)[0];
    renderViewSeg(); renderTabs(); setupStage(); setupSheet();
    loadImage();
  }

  function renderViewSeg() {
    const seg = $('#viewSeg'); seg.innerHTML = '';
    for (const [k, v] of Object.entries(st.data.views)) {
      seg.append(h('button', { role: 'tab', 'aria-selected': String(k === st.view), onclick: () => { if (st.view === k) return; st.view = k; store.set('view', k); renderViewSeg(); loadImage(); } },
        k === 'real' ? 'Echt' : 'VPX'));
    seg.hidden = Object.keys(st.data.views).length < 2;
    }
  }

  // ---------- Spielfeld: Bild, Zoom, Pan ----------
  const stage = () => $('#stage');
  function loadImage() {
    const v = st.data.views[st.view];
    const img = $('#pfImg'), wrap = $('#pfWrap'), svg = $('#pfSvg');
    wrap.style.width = v.w + 'px'; wrap.style.height = v.h + 'px';
    svg.setAttribute('viewBox', `0 0 ${v.w} ${v.h}`);
    const done = () => { fitAll(false); redraw(); if (st.sel && st.sel.items.length) focusSel(false); };
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
    const mx = Math.max(40, S.w - w), my = Math.max(40, S.h - hh);
    st.tf.x = w < S.w ? (S.w - w) / 2 : Math.min(40, Math.max(S.w - w - 40, st.tf.x));
    st.tf.y = hh < S.h ? (S.h - hh) / 2 : Math.min(40, Math.max(S.h - hh - 40, st.tf.y));
    void mx; void my;
  }
  function fitAll(animate = true) {
    const v = st.data.views[st.view], S = stageSize();
    st.fit = Math.min(S.w / v.w, S.h / v.h);
    st.tf = { s: st.fit, x: (S.w - v.w * st.fit) / 2, y: (S.h - v.h * st.fit) / 2 };
    applyTf(animate);
  }
  function zoomToBox(b, animate = true) {
    const v = st.data.views[st.view], S = stageSize();
    st.fit = Math.min(S.w / v.w, S.h / v.h);
    const pad = 70;
    const bw = (b.x1 - b.x0) * v.w, bh = (b.y1 - b.y0) * v.h;
    let sc = Math.min((S.w - pad * 2) / Math.max(bw, 1), (S.h - pad * 2 - 40) / Math.max(bh, 1));
    sc = Math.min(Math.max(sc, st.fit), st.fit * 2.4);
    const cx = (b.x0 + b.x1) / 2 * v.w, cy = (b.y0 + b.y1) / 2 * v.h;
    st.tf = { s: sc, x: S.w / 2 - cx * sc, y: S.h / 2 + 16 - cy * sc };
    clampTf(); applyTf(animate);
  }

  function setupStage() {
    const el = stage();
    if (el._setup) return; el._setup = true;
    const pts = new Map(); let last = null, moved = false, dragShot = null, lastTap = 0;
    el.addEventListener('pointerdown', e => {
      if (e.target.closest('.stage-ui > *')) return;
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
        if (Math.abs(e.clientX - prev.x) + Math.abs(e.clientY - prev.y) > 0) moved = moved || Math.hypot(dx, dy) > 6;
        if (dragShot) {
          const v = st.data.views[st.view];
          const ox = (e.clientX - dragShot.sx) / (st.tf.s * v.w), oy = (e.clientY - dragShot.sy) / (st.tf.s * v.h);
          setCorr(dragShot.it.key, [dragShot.base[0] + ox, dragShot.base[1] + oy], false);
          redraw(true);
          return;
        }
        if (!moved) return;
        st.tf.x += e.clientX - prev.x; st.tf.y += e.clientY - prev.y; clampTf(); applyTf(false);
      } else if (pts.size === 2) {
        moved = true;
        const [a, b] = [...pts.values()];
        const pa = prev, other = [...pts.entries()].find(([id]) => id !== e.pointerId)[1];
        const d0 = Math.hypot(pa.x - other.x, pa.y - other.y), d1 = Math.hypot(a.x - b.x, a.y - b.y);
        const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
        zoomAt(mx, my, d1 / Math.max(d0, 1));
      }
    });
    const end = e => {
      if (!pts.has(e.pointerId)) return;
      pts.delete(e.pointerId);
      if (dragShot) { setCorr(dragShot.it.key, getCorr(dragShot.it.key), true); dragShot = null; toast('Korrektur gespeichert'); return; }
      if (pts.size === 0 && !moved) {
        const now = Date.now();
        const under = document.elementFromPoint(e.clientX, e.clientY);
        const hitEl = under && under.closest('[data-hit]');
        if (now - lastTap < 300) { // Doppeltipp
          if (st.tf.s > st.fit * 1.3) fitAll(); else zoomAt(e.clientX, e.clientY, 2.2, true);
          lastTap = 0; return;
        }
        lastTap = now;
        if (hitEl) { const [kind, id] = hitEl.dataset.hit.split(':'); setTimeout(() => { if (Date.now() - lastTap >= 280) openDetail(kind, id); }, 300); }
      }
      if (pts.size === 1) last = [...pts.values()][0];
    };
    el.addEventListener('pointerup', end); el.addEventListener('pointercancel', end);
    el.addEventListener('wheel', e => { e.preventDefault(); zoomAt(e.clientX, e.clientY, e.deltaY < 0 ? 1.15 : 1 / 1.15); }, { passive: false });
    window.addEventListener('resize', () => { if (!$('#table').hidden) { st.sel ? focusSel(false) : fitAll(false); } });
    $('#btnFit').onclick = () => fitAll();
    $('#btnFs').onclick = () => toggleFs();
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && $('#table').classList.contains('fs')) toggleFs(false); });
    $('#btnClear').onclick = () => clearSel();
    $('#btnNext').onclick = () => stepNav(1);
    $('#btnPrev').onclick = () => stepNav(-1);
    $('#btnCorrReset').onclick = () => { if (!st.sel) return; st.sel.items.forEach(it => setCorr(it.key, [0, 0], true)); redraw(); toast('Korrektur zurückgesetzt'); };
  }
  function toggleFs(on) {
    const t = $('#table'); on = on ?? !t.classList.contains('fs');
    t.classList.toggle('fs', on);
    $('#btnFs').setAttribute('aria-label', on ? 'Vollbild verlassen' : 'Vollbild');
    $('#btnFs').innerHTML = on ? '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 4v5H4M15 4v5h5M9 20v-5H4M15 20v-5h5"/></svg>' : '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg>';
    try { if (on && document.documentElement.requestFullscreen && !document.fullscreenElement) document.documentElement.requestFullscreen().catch(() => {}); if (!on && document.fullscreenElement) document.exitFullscreen().catch(() => {}); } catch { /* iOS: CSS-Vollbild reicht */ }
    setTimeout(() => (st.sel && st.sel.items.length ? focusSel(false) : fitAll(false)), 60);
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

  // ---------- Auswahl & Zeichnen ----------
  function geomFor(kind, id) {
    if (kind === 'shot') { const sh = st.data.shots[id]; return sh && sh.geom[st.view]; }
    const ins = st.data.inserts[id]; return ins && ins.geom[st.view];
  }
  function select(items, opts = {}) {
    // items: [{kind:'shot'|'ins', id}]
    items = items.map(it => ({ ...it, key: `${it.kind}:${it.id}` }));
    const avail = items.filter(it => geomFor(it.kind, it.id));
    const missing = items.filter(it => !geomFor(it.kind, it.id));
    st.sel = { items: avail, banner: opts.banner || null, numbered: opts.numbered ?? avail.length > 1, badges: opts.badges || null };
    if (missing.length && !avail.length) toast(st.view === 'vpw' && st.data.views.real ? 'In der VPX-Ansicht nicht markiert – auf „Echt“ wechseln.' : 'Für diesen Schritt gibt es keine feste Stelle im Spielfeld.');
    else if (missing.length) toast('Einige Stellen sind in dieser Ansicht nicht markiert.');
    $('#btnClear').hidden = !avail.length && !opts.banner;
    $('#corrBar').hidden = !(st.corrMode && avail.length === 1);
    redraw(); focusSel(true);
  }
  function clearSel() {
    st.sel = null; st.seq = null; st.seqIdx = -1;
    $('#btnClear').hidden = true; $('#navBtns').hidden = true; $('#stepBanner').hidden = true; $('#corrBar').hidden = true;
    document.querySelectorAll('.card.sel').forEach(c => c.classList.remove('sel'));
    document.querySelectorAll('.chip.on, .shot-btn.on').forEach(c => c.classList.remove('on'));
    redraw(); fitAll();
  }
  function selBox() {
    const b = { x0: 1, y0: 1, x1: 0, y1: 0 };
    for (const it of st.sel.items) {
      const g = geomFor(it.kind, it.id), o = getCorr(it.key);
      const pts = it.kind === 'shot' ? (g.outline || []).flat() : g.points;
      for (const p of pts) { b.x0 = Math.min(b.x0, p[0] + o[0]); b.y0 = Math.min(b.y0, p[1] + o[1]); b.x1 = Math.max(b.x1, p[0] + o[0]); b.y1 = Math.max(b.y1, p[1] + o[1]); }
    }
    return b;
  }
  function focusSel(animate) { if (!st.sel || !st.sel.items.length) return; zoomToBox(selBox(), animate); }

  function redraw(keepAnim) {
    const svg = $('#pfSvg'); const v = st.data.views[st.view];
    if (!keepAnim) stopAnim();
    svg.innerHTML = '';
    svg.classList.toggle('corr', st.corrMode);
    const P = p => `${(p[0] * v.w).toFixed(1)},${(p[1] * v.h).toFixed(1)}`;
    const labels = [];
    if (st.sel) {
      const single = st.sel.items.length === 1;
      st.sel.items.forEach((it, i) => {
        const g = geomFor(it.kind, it.id), o = getCorr(it.key);
        if (it.kind === 'shot') {
          const sh = st.data.shots[it.id];
          const grp = s('g');
          for (const ol of g.outline || []) {
            const pts = shiftPts(ol, o).map(P).join(' ');
            grp.append(s('polygon', { class: 'shot-glow', points: pts }));
            grp.append(s('polygon', { class: 'shot-outline pulse', points: pts }));
            grp.append(s('polygon', { class: 'hit', points: pts, 'data-hit': it.key }));
          }
          svg.append(grp);
          const top = topPoint(g.outline.flat().map(p => [p[0] + o[0], p[1] + o[1]]));
          const bdg = st.sel.badges && st.sel.badges[it.id] && st.data.icons && st.data.icons[st.sel.badges[it.id]];
          labels.push({ c: g.center ? [g.center[0] + o[0], g.center[1] + o[1]] : top, name: bdg ? bdg.name : sh.name, en: bdg ? sh.name : sh.en, sub: bdg ? sh.name : null, icon: bdg ? bdg.img : null, num: !bdg && st.sel.numbered ? i + 1 : null, kind: 'shot', key: it.key });
        } else {
          const r = g.r * v.w;
          for (const p of shiftPts(g.points, o)) {
            svg.append(s('circle', { class: 'ins-mark', cx: p[0] * v.w, cy: p[1] * v.h, r: r * 1.25 }));
            svg.append(s('circle', { class: 'hit', cx: p[0] * v.w, cy: p[1] * v.h, r: r * 1.6, 'data-hit': it.key }));
          }
          const ins = st.data.inserts[it.id];
          shiftPts(g.points, o).forEach((p, j) => labels.push({ c: p, name: j === 0 ? ins.name : '', en: 'Anzeige (Einsatz) – kein Ziel', kind: 'ins', key: it.key, ringOnly: j > 0 }));
        }
      });
      // Animation: Zielrichtung + Bahnverlauf (nur für Schüsse)
      const animItems = st.sel.items.filter(it => it.kind === 'shot');
      if (animItems.length) runAnim(animItems, single);
    }
    st.labels = labels;
    placeLabels();
  }
  function topPoint(pts) { let t = pts[0]; for (const p of pts) if (p[1] < t[1]) t = p; const cx = pts.reduce((a, p) => a + p[0], 0) / pts.length; return [cx, t[1]]; }

  function placeLabels() {
    let layer = $('#stage .labels');
    if (!layer) { layer = h('div', { class: 'labels' }); stage().insertBefore(layer, $('#stage .stage-ui')); }
    layer.innerHTML = '';
    if (!st.labels || !st.data) return;
    const v = st.data.views[st.view], S = stageSize();
    const toS = p => [st.tf.x + p[0] * v.w * st.tf.s, st.tf.y + p[1] * v.h * st.tf.s];
    const compact = st.labels.filter(L => !L.ringOnly).length > 1;
    const boxes = [];
    const lineSvg = document.createElementNS(SVGNS, 'svg'); lineSvg.setAttribute('class', 'leaders');
    layer.append(lineSvg);
    // Zielringe zuerst (Position fest), dann Beschriftungen mit Kollisionsvermeidung
    const items = st.labels.map(L => ({ L, c: toS(L.c) }));
    for (const it of items) {
      layer.append(h('div', { class: 'ring' + (it.L.kind === 'ins' ? ' ins' : ''), style: `left:${it.c[0]}px;top:${it.c[1]}px` }));
    }
    const order = items.filter(it => !it.L.ringOnly).sort((a, b) => a.c[1] - b.c[1]);
    for (const it of order) {
      const L = it.L, w = compact ? (L.icon ? 30 : 0) + Math.min(170, 24 + Math.max(L.name.length * 6.6, L.sub ? L.sub.length * 5.4 : 0)) : Math.min(260, (L.icon ? 38 : 0) + 30 + Math.max(L.name.length, (L.sub || L.en).length * 0.85) * 7.4), hh = compact ? (L.sub ? 34 : 26) : 44;
      const cands = [[0, -(hh / 2 + 26)], [0, hh / 2 + 26], [-(w / 2 + 24), 0], [w / 2 + 24, 0], [0, -(hh / 2 + 62)], [0, hh / 2 + 62], [-(w / 2 + 24), -40], [w / 2 + 24, -40]];
      let best = null, bestScore = Infinity;
      for (const [dx, dy] of cands) {
        let x = it.c[0] + dx, y = it.c[1] + dy;
        x = Math.min(Math.max(x, w / 2 + 6), S.w - w / 2 - 6); y = Math.min(Math.max(y, hh / 2 + 52), S.h - hh / 2 - 6);
        const r = { x0: x - w / 2, x1: x + w / 2, y0: y - hh / 2, y1: y + hh / 2 };
        let score = Math.hypot(x - it.c[0], y - it.c[1]) * 0.05;
        for (const b of boxes) { const ox = Math.min(r.x1, b.x1) - Math.max(r.x0, b.x0), oy = Math.min(r.y1, b.y1) - Math.max(r.y0, b.y0); if (ox > 0 && oy > 0) score += ox * oy; }
        for (const o of items) { const dx2 = Math.max(r.x0 - o.c[0], 0, o.c[0] - r.x1), dy2 = Math.max(r.y0 - o.c[1], 0, o.c[1] - r.y1); if (Math.hypot(dx2, dy2) < 18) score += 400; }
        if (score < bestScore) { bestScore = score; best = { x, y, r }; }
      }
      boxes.push(best.r);
      const ln = document.createElementNS(SVGNS, 'line');
      ln.setAttribute('x1', it.c[0]); ln.setAttribute('y1', it.c[1]); ln.setAttribute('x2', best.x); ln.setAttribute('y2', best.y);
      ln.setAttribute('class', L.kind === 'ins' ? 'ins' : '');
      lineSvg.append(ln);
      const el = h('div', { class: 'lbl' + (L.kind === 'ins' ? ' ins' : '') + (compact ? ' compact' : ''), style: `left:${best.x}px;top:${best.y}px`, 'data-hit': L.key },
        L.icon ? h('img', { class: 'ico', src: L.icon, alt: '' }) : null,
        h('span', { class: 'lt' }, h('b', {}, L.num ? h('span', { class: 'num' }, String(L.num)) : null, L.name), (compact && !L.sub) ? null : h('i', {}, L.sub || L.en)));
      layer.append(el);
    }
  }
  // Animation (Zielrichtung als laufende Linie, danach Lichtpunkt entlang der Bahn)
  function stopAnim() { if (st.anim) cancelAnimationFrame(st.anim.raf); st.anim = null; }
  function runAnim(items, single) {
    stopAnim();
    const svg = $('#pfSvg'), v = st.data.views[st.view];
    const layer = s('g'); svg.append(layer);
    const toPx = (pts, o) => pts.map(p => [(p[0] + o[0]) * v.w, (p[1] + o[1]) * v.h]);
    const seqs = items.map(it => {
      const g = geomFor('shot', it.id), o = getCorr(it.key);
      const segs = [];
      if (g.path) segs.push({ pts: toPx(g.path, o), d: (g.pathBall || []).map(x => x * v.w) });
      if (g.path2) segs.push({ pts: toPx(g.path2, o), d: (g.path2Ball || []).map(x => x * v.w) });
      return { aims: (g.aim || []).map(a => toPx(a, o)), segs };
    });
    if (single) for (const [i, sg] of seqs[0].segs.entries()) layer.append(s('polyline', { class: 'path' + (i ? ' p2' : ''), points: sg.pts.map(p => p.join(',')).join(' ') }));
    // Kugel: Foto einer polierten Stahlkugel, maßstabsgetreu (1 1/16 Zoll), mit Schatten und kurzer Spur
    const ballG = s('g', { class: 'ballg' });
    const TRAIL = 4, trail = [];
    for (let i = TRAIL; i >= 1; i--) { const t = s('image', { href: 'img/ball.png', class: 'trail', opacity: (0.22 * (1 - i / (TRAIL + 1))).toFixed(2) }); trail.push(t); ballG.append(t); }
    const shadow = s('ellipse', { class: 'ball-shadow' });
    const ball = s('image', { href: 'img/ball.png', class: 'ball-img' });
    ballG.append(shadow); ballG.append(ball);
    layer.append(ballG); ballG.style.opacity = 0;
    const aimEls = [];
    let idx = 0, t0 = performance.now();
    const seglen = pts => { const L = [0]; for (let i = 1; i < pts.length; i++) L.push(L[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])); return L; };
    const speed = v.w * 0.42; // Bildpixel pro Sekunde (halbes Tempo gegenüber der ersten Fassung)
    const setup = () => {
      aimEls.forEach(e => e.remove()); aimEls.length = 0;
      const q = seqs[idx];
      for (const a of q.aims) { const l = s('polyline', { class: 'aim run', points: a.map(p => p.join(',')).join(' ') }); layer.insertBefore(l, ballG); aimEls.push(l); }
      if (!single) for (const sg of q.segs) { const l = s('polyline', { class: 'path', points: sg.pts.map(p => p.join(',')).join(' ') }); layer.insertBefore(l, ballG); aimEls.push(l); }
      q.segs.forEach(sg => { sg.L = seglen(sg.pts); });
      q.total = q.segs.reduce((a, sg) => a + sg.L[sg.L.length - 1], 0);
      q.aimDur = q.aims.length ? 1700 : 300;
      q.runDur = q.total / speed * 1000;
      q.dur = q.aimDur + q.runDur + 1400;
    };
    const posAt = (q, dist) => {
      for (const sg of q.segs) {
        const L = sg.L, tot = L[L.length - 1];
        if (dist <= tot) {
          let i = 1; while (i < L.length - 1 && L[i] < dist) i++;
          const k = (dist - L[i - 1]) / Math.max(L[i] - L[i - 1], 1e-6);
          const p0 = sg.pts[i - 1], p1 = sg.pts[i];
          const d0 = sg.d[i - 1] || sg.d[0] || 20, d1 = sg.d[i] || d0;
          return [p0[0] + (p1[0] - p0[0]) * k, p0[1] + (p1[1] - p0[1]) * k, d0 + (d1 - d0) * k];
        }
        dist -= tot;
      }
      const sg = q.segs[q.segs.length - 1]; const p = sg.pts[sg.pts.length - 1]; return [p[0], p[1], sg.d[sg.d.length - 1] || 20];
    };
    const place = (el, p) => { el.setAttribute('x', p[0] - p[2] / 2); el.setAttribute('y', p[1] - p[2] / 2); el.setAttribute('width', p[2]); el.setAttribute('height', p[2]); };
    setup();
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const tick = now => {
      const q = seqs[idx]; let t = now - t0;
      if (t > q.dur) { idx = (idx + 1) % seqs.length; t0 = now; setup(); t = 0; }
      const tr = t - q.aimDur;
      if (!reduce && q.total && tr >= 0 && tr <= q.runDur + 500) {
        const e = Math.min(tr / q.runDur, 1);
        const ease = e < 0.5 ? 2 * e * e : 1 - Math.pow(-2 * e + 2, 2) / 2; // sanft anrollen und auslaufen
        const dist = ease * q.total;
        const p = posAt(q, dist);
        place(ball, p);
        shadow.setAttribute('cx', p[0] + p[2] * 0.12); shadow.setAttribute('cy', p[1] + p[2] * 0.22);
        shadow.setAttribute('rx', p[2] * 0.5); shadow.setAttribute('ry', p[2] * 0.42);
        trail.forEach((el, i) => place(el, posAt(q, Math.max(0, dist - (TRAIL - i) * p[2] * 0.45))));
        ballG.style.opacity = tr > q.runDur ? Math.max(0, 1 - (tr - q.runDur) / 500) : Math.min(1, tr / 200);
      } else ballG.style.opacity = 0;
      st.anim.raf = requestAnimationFrame(tick);
    };
    st.anim = { raf: requestAnimationFrame(tick) };
  }

  // ---------- Schritt-Navigation ----------
  function setSeq(list, idx, cardEls) {
    st.seq = { list, cards: cardEls }; st.seqIdx = idx; showStep();
  }
  function showStep() {
    const { list, cards } = st.seq; const step = list[st.seqIdx];
    cards.forEach((c, i) => c.classList.toggle('sel', i === st.seqIdx));
    cards[st.seqIdx]?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    const b = $('#stepBanner'); b.hidden = false; b.innerHTML = '';
    const det = h('div', { class: 'bd' });
    if (step.prep) det.append(h('div', {}, h('em', {}, 'Vorbereiten '), step.prep));
    if (step.go) det.append(h('div', {}, h('em', {}, 'Wohin '), step.go));
    if (step.why) det.append(h('div', {}, h('em', {}, 'Bringt '), step.why));
    if (step.text) det.append(h('div', {}, step.text));
    b.append(h('div', { class: 'bt' }, h('span', { class: 'k' }, `${st.seqIdx + 1}/${list.length}`), h('span', {}, step.title), h('span', { class: 'more', 'aria-hidden': 'true' }, '▾')), det);
    b.onclick = () => b.classList.toggle('open');
    $('#navBtns').hidden = list.length < 2;
    $('#btnPrev').disabled = st.seqIdx === 0; $('#btnPrev').style.opacity = st.seqIdx === 0 ? .4 : 1;
    $('#btnNext').textContent = st.seqIdx === list.length - 1 ? 'Fertig ✓' : 'Weiter ›';
    select((step.shots || []).map(id => ({ kind: 'shot', id })), { banner: step.title, badges: step.badges });
  }
  function stepNav(d) {
    if (!st.seq) return;
    const n = st.seqIdx + d;
    if (n >= st.seq.list.length) { clearSel(); return; }
    if (n < 0) return;
    st.seqIdx = n; showStep();
  }

  // ---------- Bottom-Sheet ----------
  const TABS = [['strategy', 'Strategie'], ['mb', 'Multibälle'], ['modes', 'Modi'], ['shots', 'Schüsse'], ['info', 'Info']];
  function renderTabs() {
    const nav = $('#tabs'); nav.innerHTML = '';
    for (const [k, l] of TABS) nav.append(h('button', { role: 'tab', 'aria-selected': String(k === st.tab), onclick: () => { st.tab = k; store.set('tab', k); renderTabs(); } }, l));
    renderBody();
  }
  function setupSheet() {
    const g = $('#grab'); if (g._setup) return; g._setup = true;
    let y0 = null, moved = false;
    g.addEventListener('pointerdown', e => { y0 = e.clientY; moved = false; g.setPointerCapture(e.pointerId); });
    g.addEventListener('pointermove', e => { if (y0 != null && Math.abs(e.clientY - y0) > 20) moved = true; });
    g.addEventListener('pointerup', e => {
      const sh = $('#sheet');
      if (!moved) sh.classList.toggle('big'); else sh.classList.toggle('big', e.clientY < y0);
      y0 = null; setTimeout(() => (st.sel ? focusSel(true) : fitAll()), 320);
    });
  }
  function renderBody() {
    const body = $('#sheetBody'); body.innerHTML = ''; body.scrollTop = 0;
    ({ strategy: tabStrategy, mb: tabMb, modes: tabModes, shots: tabShots, info: tabInfo })[st.tab](body);
  }
  const shotName = id => (st.data.shots[id] ? st.data.shots[id].name : id);
  function chips(ids) {
    if (!ids || !ids.length) return null;
    return h('div', { class: 'chips' }, ids.map(id => h('button', { class: 'chip', onclick: e => { e.stopPropagation(); document.querySelectorAll('.chip.on').forEach(c => c.classList.remove('on')); e.currentTarget.classList.add('on'); select([{ kind: 'shot', id }]); } }, shotName(id))));
  }
  function srcLine(ids) {
    if (!ids || !ids.length) return h('div', { class: 'src' }, 'Keine Quelle – ehrlich offen.');
    const names = { rules: 'Rulesheet 1.1', manual: 'Stern-Handbuch', vpw: 'VPW-Tischdatei', photo: 'Foto', rules10: 'Rulesheet 1.0' };
    return h('div', { class: 'src' }, 'Quelle: ' + ids.map(i => names[i] || i).join(', '));
  }

  function stepCard(step, i, onSel) {
    const card = h('div', { class: 'card' });
    const btn = h('button', { class: 'step', onclick: () => onSel(i) },
      h('div', { class: 'step-h' }, h('span', { class: 'n' }, String(i + 1)), h('span', { class: 'step-t' }, step.title)));
    if (step.prep || step.go || step.why) {
      btn.append(h('dl', {}, step.prep ? [h('dt', {}, 'Vorbereiten'), h('dd', {}, step.prep)] : null,
        step.go ? [h('dt', {}, 'Wohin'), h('dd', {}, step.go)] : null, step.why ? [h('dt', {}, 'Bringt'), h('dd', {}, step.why)] : null));
    } else if (step.text) btn.append(h('p', {}, step.text));
    card.append(btn);
    const c = chips(step.shots); if (c) card.append(c);
    if (step.sources) card.append(srcLine(step.sources));
    return card;
  }

  function tabStrategy(body) {
    const seg = h('div', { class: 'seg seg-wide' });
    for (const S of st.data.strategies) seg.append(h('button', { 'aria-selected': String(S.id === st.strat), onclick: () => { st.strat = S.id; store.set('strat', S.id); renderBody(); } }, S.title));
    body.append(seg);
    const S = st.data.strategies.find(x => x.id === st.strat) || st.data.strategies[0];
    body.append(h('p', { class: 'sub' }, S.subtitle + ' · Schritt antippen = Ziel im Spielfeld'));
    const cards = [];
    S.steps.forEach((step, i) => { const c = stepCard(step, i, idx => setSeq(S.steps, idx, cards)); cards.push(c); body.append(c); });
  }

  function tabMb(body) {
    body.append(h('p', { class: 'intro' }, 'Jeder Multiball in drei Teilen: Vorbereitung, Start, Punkten. Schritt antippen zeigt die Stelle.'));
    for (const mb of st.data.multiballs) {
      const open = st.openMb === mb.id;
      const wrap = h('div', { class: 'card mb' + (open ? ' open' : '') });
      wrap.append(h('button', { class: 'mb-head', onclick: () => { st.openMb = open ? null : mb.id; renderBody(); if (!open) setTimeout(() => wrap.scrollIntoView({ block: 'start', behavior: 'smooth' }), 30); } },
        h('div', {}, h('div', { class: 'mb-n' }, mb.name), h('div', { class: 'mb-tag' }, `${mb.tag} · ${mb.balls}`)),
        h('span', { html: '<svg class="chev" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7"/></svg>' })));
      if (open) {
        const b = h('div', { class: 'mb-body' });
        const flat = [...mb.prep.map(x => ({ ...x, ph: 'prep' })), { ...mb.start, ph: 'start' }, ...mb.score.map(x => ({ ...x, ph: 'score' }))];
        const cards = []; let lastPh = null;
        const label = { prep: '① Vorbereiten', start: '② Starten', score: '③ Punkten im Multiball' };
        flat.forEach((step, i) => {
          if (step.ph !== lastPh) { b.append(h('div', { class: 'phase ' + step.ph }, label[step.ph])); lastPh = step.ph; }
          const c = stepCard(step, i, idx => setSeq(flat, idx, cards)); cards.push(c); b.append(c);
        });
        wrap.append(b);
      }
      body.append(wrap);
    }
  }

  function tabModes(body) {
    body.append(h('p', { class: 'intro' }, st.data.modesIntro));
    for (const m of st.data.modes) {
      const wrap = h('div', { class: 'card mb' + (st.openMb === 'mode:' + m.id ? ' open' : '') });
      const open = st.openMb === 'mode:' + m.id;
      wrap.append(h('button', { class: 'mb-head', onclick: () => { st.openMb = open ? null : 'mode:' + m.id; renderBody(); } },
        h('div', {}, h('div', { class: 'mb-n' }, m.name), h('div', { class: 'mb-tag' }, `${m.film} · ${m.time}`)),
        h('span', { html: '<svg class="chev" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7"/></svg>' })));
      if (open) {
        const b = h('div', { class: 'mb-body' }); const cards = [];
        m.steps.forEach((step, i) => { const c = stepCard({ ...step, sources: ['rules'] }, i, idx => setSeq(m.steps, idx, cards)); cards.push(c); b.append(c); });
        wrap.append(b);
        setTimeout(() => setSeq(m.steps, 0, cards), 0);
      }
      body.append(wrap);
    }
  }

  function openDetail(kind, id) {
    st.shotDetail = { kind, id };
    if (st.tab !== 'shots') { st.tab = 'shots'; store.set('tab', 'shots'); renderTabs(); } else renderBody();
    select([{ kind, id }]);
  }
  function tabShots(body) {
    const D = st.shotDetail;
    if (D) {
      if (D.kind === 'shot') {
        const sh = st.data.shots[D.id];
        const card = h('div', { class: 'card detail' },
          h('h3', {}, sh.name), h('div', { class: 'en' }, `${sh.en} · ${sh.kind}`),
          sh.flipper ? h('div', { class: 'row' }, h('span', { class: 'k' }, 'Schießen von'), FL[sh.flipper] + (sh.flipper !== 'beide' ? ' (aus der Geometrie abgeleitet)' : '')) : h('div', { class: 'row' }, h('span', { class: 'k' }, 'Schießen von'), 'nicht direkt – siehe Beschreibung'),
          sh.icon && st.data.icons[sh.icon] ? h('div', { class: 'row icon-row' }, h('span', { class: 'k' }, 'Sammelt'), h('span', { class: 'ir' }, h('img', { src: st.data.icons[sh.icon].img, alt: '' }), st.data.icons[sh.icon].name + ' (Symbol wie in der Gefährten-Reihe)')) : null,
          h('div', { class: 'row' }, h('span', { class: 'k' }, 'Was ist das?'), sh.what),
          h('div', { class: 'row' }, h('span', { class: 'k' }, 'Wohin läuft die Kugel?'), sh.returns),
          h('div', { class: 'row' }, h('span', { class: 'k' }, 'Bringt'), h('ul', {}, sh.awards.map(a => h('li', {}, a)))),
          h('div', { class: 'row' }, h('span', { class: 'k' }, 'Im Bild'), sh.visibility, getCorr('shot:' + D.id)[0] || getCorr('shot:' + D.id)[1] ? h('span', { class: 'badge warn' }, 'von dir korrigiert') : null),
          srcLine(sh.sources));
        body.append(card);
      } else {
        const ins = st.data.inserts[D.id];
        body.append(h('div', { class: 'card detail' }, h('h3', { style: 'color:var(--insert)' }, ins.name), h('div', { class: 'en' }, `${ins.en} · Anzeige, kein Ziel`), h('div', { class: 'row' }, ins.text),
          !ins.geom[st.view] ? h('div', { class: 'row muted' }, 'In dieser Ansicht nicht markiert (VPW hat diese Einsätze anders angeordnet).') : null));
      }
    }
    body.append(h('div', { class: 'sec-h' }, 'Schüsse und Ziele'));
    const grid = h('div', { class: 'shot-grid' });
    for (const [id, sh] of Object.entries(st.data.shots)) {
      grid.append(h('button', { class: 'shot-btn' + (D && D.kind === 'shot' && D.id === id ? ' on' : ''), onclick: () => openDetail('shot', id) },
        h('b', {}, sh.name), h('span', {}, `${sh.en}${sh.flipper ? ' · ' + (sh.flipper === 'beide' ? 'L/R' : sh.flipper) : ''}`)));
    }
    body.append(grid);
    body.append(h('div', { class: 'sec-h' }, 'Anzeigen (Einsätze) – nur Lichter, keine Ziele'));
    const g2 = h('div', { class: 'shot-grid' });
    for (const [id, ins] of Object.entries(st.data.inserts)) {
      g2.append(h('button', { class: 'shot-btn ins' + (D && D.kind === 'ins' && D.id === id ? ' on' : ''), onclick: () => openDetail('ins', id) }, h('b', {}, ins.name), h('span', {}, ins.en)));
    }
    body.append(g2);
  }

  function tabInfo(body) {
    const T = st.data.table, v = st.data.views[st.view];
    body.append(h('div', { class: 'sec-h' }, 'Tischfassung'));
    body.append(h('dl', { class: 'card kv' },
      h('dt', {}, 'Tisch'), h('dd', {}, `${T.name} (${T.manufacturer}, ${T.year})`),
      h('dt', {}, 'System'), h('dd', {}, `${T.system}, Design ${T.design}`),
      h('dt', {}, 'Fassungen'), h('dd', {}, T.editions),
      h('dt', {}, 'Regelstand'), h('dd', {}, T.ruleVersion),
      h('dt', {}, 'Ansicht'), h('dd', {}, `${v.label}: ${v.note}`),
      h('dt', {}, 'Inhaltsstand'), h('dd', {}, new Date(T.contentDate).toLocaleDateString('de-DE'))));

    body.append(h('div', { class: 'sec-h' }, 'Für unterwegs'));
    const off = h('div', { class: 'card', style: 'padding:12px 14px' }, h('div', { id: 'offTxt' }, 'Prüfe Offline-Speicher …'));
    const btns = h('div', { class: 'btn-row' }, h('button', { class: 'btn', onclick: updateNow }, 'Nach Aktualisierung suchen'));
    off.append(btns); body.append(off);
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
        h('button', { class: 'btn', onclick: () => { if (confirm('Alle eigenen Korrekturen löschen?')) { st.corr = {}; store.set('corr', {}); redraw(); renderBody(); } } }, 'Alle löschen')),
      ta));

    body.append(h('div', { class: 'sec-h' }, 'Quellen'));
    body.append(h('ul', { class: 'card srcs info', style: 'padding:12px 14px 4px 30px' }, st.data.sources.map(sr => h('li', {}, h('div', {}, sr.title), h('div', { class: 'muted', style: 'font-size:13px' }, sr.use), h('a', { class: 'u', href: sr.url, target: '_blank', rel: 'noopener' }, sr.url)))));
    body.append(h('div', { class: 'sec-h' }, 'Grenzen dieser Anleitung'));
    body.append(h('ul', { class: 'card info', style: 'padding:12px 14px 12px 30px' }, st.data.limits.map(l => h('li', {}, l))));
    body.append(h('div', { class: 'sec-h' }, 'Begriffe'));
    body.append(h('dl', { class: 'card gl', style: 'padding:4px 14px 14px' }, st.data.glossary.flatMap(g => [h('dt', {}, g.term), h('dd', {}, g.text)])));
    body.append(h('p', { class: 'muted', style: 'font-size:12px;margin:16px 4px' }, `App-Stand ${window.FG_VERSION || ''} · Private Nutzung.`));
  }
  async function shareText(t) {
    try { if (navigator.share) { await navigator.share({ title: 'Flipper-Guide Korrekturen', text: t }); return; } } catch { /* abgebrochen */ }
    try { await navigator.clipboard.writeText(t); toast('In die Zwischenablage kopiert'); } catch { toast('Bitte den Text unten markieren und kopieren'); }
  }

  // ---------- Offline ----------
  function registerSW() {
    if (!('serviceWorker' in navigator)) return;
    navigator.serviceWorker.register('sw.js').then(reg => {
      reg.addEventListener('updatefound', () => {
        const nw = reg.installing; if (!nw) return;
        nw.addEventListener('statechange', () => { if (nw.state === 'installed' && navigator.serviceWorker.controller) toast('Neue Version gespeichert – wird beim nächsten Öffnen aktiv.', 4000); });
      });
    }).catch(() => {});
    navigator.serviceWorker.addEventListener('message', e => { if (e.data && e.data.version) window.FG_VERSION = e.data.version; });
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
