// Part Maker (Nov 22 2026, his idea): sketch your own body part from simple shapes in linked front / side / top / 3D views.
// Drag on empty space = new shape, drag a shape = move it, drag its yellow corner = resize, tap = select.
// Saved parts live on this phone (localStorage 'mf-myparts') and show up in Build next to the kit parts.
// Sketch units: y up from the ground, -z = the front, +x = the mech's left (you draw the LEFT part; the right one is mirrored).
(function () {
  const SLOTS = { head: 'Head', chest: 'Chest', pelvis: 'Hips', back: 'Backpack', shoulder: 'Shoulder', upper_arm: 'Upper arm', forearm: 'Forearm', hand: 'Hand', thigh: 'Thigh', shin: 'Shin', foot: 'Foot' };
  const PENS = { frame: ['#5a5e6a', 'Frame'], armor: ['#e8e8e8', 'Main'], armor2: ['#3b7bff', 'Second'], accent: ['#ff4848', 'Trim'], glow: ['#38d5ff', 'Glow'] };
  const TOOLS = { box: 'Box', wedge: 'Wedge', taper: 'Taper', cyl: 'Cylinder', pen: 'Pen' };
  const KEY = 'mf-myparts', K = 70, GY = 262, AX = { front: ['x', 'y'], side: ['z', 'y'], top: ['x', 'z'] };
  const STARTS = {   // a starting shape for each spot, so the pad is never blank (his Gundam foot: sole, sloped top, toe, heel, ankle)
    foot: [{ t: 'box', c: 'frame', x: 0, z: 0, y: 0, w: .9, h: .15, d: 1.8 }, { t: 'wedge', c: 'armor', x: 0, z: -.1, y: .15, w: .85, h: .6, d: 1.5 }, { t: 'taper', c: 'armor', x: 0, z: .35, y: .75, w: .6, h: .35, d: .6 }, { t: 'box', c: 'accent', x: 0, z: -.8, y: .15, w: .8, h: .2, d: .3 }, { t: 'box', c: 'armor2', x: 0, z: .75, y: .15, w: .7, h: .4, d: .35 }],
    limb: [{ t: 'cyl', c: 'frame', x: 0, z: 0, y: 0, w: .5, h: 2.4, d: .5 }, { t: 'box', c: 'armor', x: 0, z: -.05, y: .3, w: .8, h: 1.8, d: .75 }],
    box: [{ t: 'box', c: 'frame', x: 0, z: 0, y: 0, w: 1.4, h: 1.2, d: 1 }, { t: 'taper', c: 'armor', x: 0, z: -.05, y: .3, w: 1.8, h: 1.4, d: 1.2 }],
    shoulder: [{ t: 'box', c: 'armor', x: 0, z: 0, y: 0, w: 1.2, h: 1, d: 1.3 }, { t: 'wedge', c: 'armor2', x: .1, z: 0, y: 1, w: 1.1, h: .4, d: 1.2 }],
  };
  const startFor = s => JSON.parse(JSON.stringify(STARTS[s === 'foot' ? 'foot' : s === 'shoulder' ? 'shoulder' : /arm|thigh|shin|hand/.test(s) ? 'limb' : 'box']));
  const load = () => { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) { return []; } };
  const store = list => { try { localStorage.setItem(KEY, JSON.stringify(list)); } catch (e) {} };

  let slot = 'foot', tool = 'box', col = 'armor', G = { s: startFor('foot'), l: [] }, sel = -1, drag = null, hist = [], editId = null;
  const el = document.createElement('div'); el.id = 'maker';
  el.innerHTML = `<div class="mk-head"><b>Part Maker</b><button id="mkClose">Close</button></div>
  <div class="line" id="mkSlots"></div><div class="line" id="mkTools"></div>
  <canvas id="mkCv" width="600" height="600"></canvas>
  <div class="line" id="mkPens"></div>
  <div class="line"><button id="mkDup">Copy shape</button><button id="mkDel">Delete shape</button><button id="mkUndo">Undo</button><button id="mkClear">Clear</button></div>
  <p class="hint" id="mkMsg"></p>
  <div class="line"><input id="mkName" aria-label="Name your part" placeholder="Name your part" maxlength="24"><button id="mkSave" class="on">Save + put it on</button></div>
  <div class="line" id="mkMine"></div>`;
  document.body.append(el);
  const cv = el.querySelector('#mkCv'), x = cv.getContext('2d'), $ = s => el.querySelector(s);
  ['touchstart', 'touchmove', 'touchend'].forEach(t => cv.addEventListener(t, e => e.preventDefault(), { passive: false }));   // the page never moves while drawing

  const view = (px, py) => px < 300 && py < 300 ? 'front' : px >= 300 && py < 300 ? 'side' : px < 300 ? 'top' : 'iso';
  const P2 = { front: (px, py) => [(px - 150) / K, (GY - py) / K], side: (px, py) => [(px - 450) / K, (GY - py) / K], top: (px, py) => [(px - 150) / K, (450 - py) / K] };
  const proj = { front: p => [150 + p[0] * K, GY - p[1] * K], side: p => [450 + p[2] * K, GY - p[1] * K], top: p => [150 + p[0] * K, 450 - p[2] * K],
    iso: p => [450 + (p[0] - p[2]) * .866 * K * .55, 565 - p[1] * K * .55 + (p[0] + p[2]) * .5 * K * .55] };
  const hex = c => (PENS[c] || PENS.armor)[0];
  function unit(t) {
    if (t === 'cyl') { const n = 14, b = [], tp = []; for (let i = 0; i < n; i++) { const a = i / n * 6.283; b.push([Math.cos(a) / 2, 0, Math.sin(a) / 2]); tp.push([Math.cos(a) / 2, 1, Math.sin(a) / 2]); }
      const f = [tp.slice().reverse(), b.slice()]; for (let i = 0; i < n; i++) { const j = (i + 1) % n; f.push([b[i], b[j], tp[j], tp[i]]); } return f; }
    const v = [[-.5, 0, -.5], [.5, 0, -.5], [.5, 0, .5], [-.5, 0, .5], [-.5, 1, -.5], [.5, 1, -.5], [.5, 1, .5], [-.5, 1, .5]];
    if (t === 'wedge') { v[4][1] = .25; v[5][1] = .25; }          // slopes down toward the front
    if (t === 'taper') for (let i = 4; i < 8; i++) { v[i][0] *= .6; v[i][2] *= .6; }   // smaller on top
    return [[4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [0, 3, 2, 1]].map(f => f.map(i => v[i]));
  }
  const faces = s => unit(s.t).map(f => f.map(p => [s.x + p[0] * s.w, s.y + p[1] * s.h, s.z + p[2] * s.d]));
  // each shape as ranges on the three axes, so moving and resizing work the same in every view
  const range = (s, a) => a === 'y' ? [s.y, s.y + s.h] : a === 'x' ? [s.x - s.w / 2, s.x + s.w / 2] : [s.z - s.d / 2, s.z + s.d / 2];
  function setRange(s, a, lo, hi) { const r = n => Math.round(n * 100) / 100; if (hi - lo < .1) hi = lo + .1;
    if (a === 'y') { s.y = r(Math.max(0, lo)); s.h = r(hi - lo); } else if (a === 'x') { s.x = r((lo + hi) / 2); s.w = r(hi - lo); } else { s.z = r((lo + hi) / 2); s.d = r(hi - lo); } }
  function rect(s, v) { const [a, b] = AX[v], A = range(s, a), B = range(s, b), p0 = P2inv(v, A[0], B[0]), p1 = P2inv(v, A[1], B[1]); return [p0[0], p1[1], p1[0], p0[1]]; }   // x0,y0 (top),x1,y1
  function P2inv(v, a, b) { return v === 'front' ? [150 + a * K, GY - b * K] : v === 'side' ? [450 + a * K, GY - b * K] : [150 + a * K, 450 - b * K]; }
  function shade(c, f) { const n = parseInt(c.slice(1), 16); return `rgb(${(n >> 16) * f | 0},${(n >> 8 & 255) * f | 0},${(n & 255) * f | 0})`; }
  function poly(pts, v) { x.beginPath(); pts.forEach((p, k) => { const q = proj[v](p); k ? x.lineTo(...q) : x.moveTo(...q); }); x.closePath(); }

  function draw() {
    x.fillStyle = '#1b1c21'; x.fillRect(0, 0, 600, 600); x.strokeStyle = '#3a3c45'; x.lineWidth = 1; x.beginPath(); x.moveTo(300, 0); x.lineTo(300, 600); x.moveTo(0, 300); x.lineTo(600, 300); x.stroke();
    x.strokeStyle = '#30323a'; x.beginPath(); x.moveTo(0, GY); x.lineTo(600, GY); x.stroke();
    x.fillStyle = '#8a8d98'; x.font = '14px sans-serif'; x.fillText('front', 10, 20); x.fillText('side (front ←)', 310, 20); x.fillText('top (front ↓)', 10, 320); x.fillText('3D', 310, 320);
    for (const v of ['front', 'side', 'top']) G.s.forEach((s, i) => { for (const f of faces(s)) { poly(f, v); x.globalAlpha = .35; x.fillStyle = hex(s.c); x.fill(); x.globalAlpha = 1; x.strokeStyle = i === sel ? '#ffd23b' : shade(hex(s.c), .9); x.lineWidth = i === sel ? 2 : 1; x.stroke(); }
      if (i === sel) { const r = rect(s, v); x.fillStyle = '#ffd23b'; x.fillRect(r[2] - 9, r[1] - 9, 18, 18); } });
    const all = []; G.s.forEach((s, i) => faces(s).forEach((f, k) => { const c = f.reduce((a, p) => [a[0] + p[0], a[1] + p[1], a[2] + p[2]], [0, 0, 0]).map(n => n / f.length); all.push({ f, s, i, dep: c[0] + c[2] - c[1] * .2, lit: k === 0 ? 1 : .6 + .3 * ((k % 3) / 2) }); }));
    all.sort((a, b) => a.dep - b.dep); for (const o of all) { poly(o.f, 'iso'); x.fillStyle = shade(hex(o.s.c), o.lit); x.fill(); x.strokeStyle = o.i === sel ? '#ffd23b' : '#111'; x.lineWidth = o.i === sel ? 1.6 : .8; x.stroke(); }
    x.lineCap = x.lineJoin = 'round';
    for (const l of G.l.concat(drag && drag.line ? [drag.line] : [])) for (const v of ['front', 'side', 'top', 'iso']) { x.strokeStyle = hex(l.c); x.lineWidth = v === 'iso' ? 2 : 3; x.beginPath(); l.p.forEach((p, k) => { const q = proj[v](p); k ? x.lineTo(...q) : x.moveTo(...q); }); x.stroke(); }
    if (drag && drag.mode === 'new') { x.setLineDash([5, 4]); x.strokeStyle = '#fff'; x.lineWidth = 1.5; x.strokeRect(drag.a[0], drag.a[1], drag.b[0] - drag.a[0], drag.b[1] - drag.a[1]); x.setLineDash([]); }
  }
  const pos = e => { const r = cv.getBoundingClientRect(); return [(e.clientX - r.left) * 600 / r.width, (e.clientY - r.top) * 600 / r.height]; };
  function to3(p, v) { const s = G.s[sel], q = P2[v](...p), r = n => Math.round(n * 100) / 100;   // pen lines land on the selected shape's face
    if (v === 'front') return [r(q[0]), r(q[1]), s ? r(s.z - s.d / 2 - .02) : 0]; if (v === 'side') return [s ? r(s.x + s.w / 2 + .02) : 0, r(q[1]), r(q[0])]; return [r(q[0]), s ? r(s.y + s.h + .02) : 0, r(q[1])]; }
  function pick(p, v) { for (let i = G.s.length - 1; i >= 0; i--) { const r = rect(G.s[i], v); if (p[0] >= r[0] && p[0] <= r[2] && p[1] >= r[1] && p[1] <= r[3]) return i; } return -1; }
  const snap = () => hist.push(JSON.stringify(G));
  cv.onpointerdown = e => { cv.setPointerCapture(e.pointerId); const p = pos(e), v = view(...p);
    if (v === 'iso') { drag = null; return; }
    if (tool === 'pen') { drag = { v, line: { c: col, p: [to3(p, v)] } }; return; }
    const s = G.s[sel];
    if (s) { const r = rect(s, v); if (Math.abs(p[0] - r[2]) < 22 && Math.abs(p[1] - r[1]) < 22) { snap(); drag = { v, mode: 'size', a: p }; return; } }
    const i = pick(p, v);
    if (i >= 0) { snap(); sel = i; const [a, b] = AX[v]; drag = { v, mode: 'move', a: p, A: range(G.s[i], a), B: range(G.s[i], b), moved: false }; draw(); return; }
    drag = { v, mode: 'new', a: p, b: p }; };
  cv.onpointermove = e => { if (!drag) return; const p = pos(e), v = drag.v, [a, b] = AX[v];
    if (drag.line) { const q = to3(p, v), l = drag.line.p[drag.line.p.length - 1]; if (Math.hypot(q[0] - l[0], q[1] - l[1], q[2] - l[2]) > .06) drag.line.p.push(q); }
    else if (drag.mode === 'move') { const q0 = P2[v](...drag.a), q = P2[v](...p), s = G.s[sel]; let da = q[0] - q0[0], db = q[1] - q0[1];
      if (b === 'y' && drag.B[0] + db < 0) db = -drag.B[0]; drag.moved = drag.moved || Math.hypot(p[0] - drag.a[0], p[1] - drag.a[1]) > 6;
      setRange(s, a, drag.A[0] + da, drag.A[1] + da); setRange(s, b, drag.B[0] + db, drag.B[1] + db); }
    else if (drag.mode === 'size') { const s = G.s[sel], q = P2[v](...p); setRange(s, a, range(s, a)[0], q[0]); setRange(s, b, range(s, b)[0], q[1]); }
    else drag.b = p;
    draw(); };
  cv.onpointerup = () => { if (!drag) return; const d = drag; drag = null;
    if (d.line) { if (d.line.p.length > 1) { snap(); G.l.push(d.line); } }
    else if (d.mode === 'move' && !d.moved) hist.pop();                      // just a tap: select only
    else if (d.mode === 'new') { if (Math.hypot(d.b[0] - d.a[0], d.b[1] - d.a[1]) < 10) sel = -1;
      else { snap(); const v = d.v, [a, b] = AX[v], p1 = P2[v](...d.a), p2 = P2[v](...d.b), ref = G.s[sel], s = { t: tool, c: col, x: 0, y: 0, z: 0, w: .6, h: .6, d: .6 };
        if (ref) { s.x = ref.x; s.w = ref.w; s.z = ref.z; s.d = ref.d; s.y = ref.y; s.h = ref.h; }   // the depth you can't see in this view comes from the selected shape
        else if (b === 'y' || a === 'x') s.w = s.d = Math.max(.4, Math.abs(p2[0] - p1[0]) * .8);
        setRange(s, a, Math.min(p1[0], p2[0]), Math.max(p1[0], p2[0])); setRange(s, b, Math.min(p1[1], p2[1]), Math.max(p1[1], p2[1]));
        if (v === 'top') s.y = ref ? Math.round((ref.y + ref.h) * 100) / 100 : 0, s.h = .4;   // drawn from above: sits on top of the selected shape
        G.s.push(s); sel = G.s.length - 1; } }
    draw(); };

  function bar(id, items, cur, set) { const b = $(id); b.innerHTML = ''; for (const [k, l] of Object.entries(items)) { const n = document.createElement('button'); n.textContent = l; n.classList.toggle('on', k === cur); n.onclick = () => { set(k); render(); }; b.append(n); } }
  const HELP = { pen: 'Pen: draw lines on the selected shape (vents, cuts, panel lines).' };
  function render() {
    bar('#mkSlots', SLOTS, slot, k => { if (k !== slot) { slot = k; editId = null; G = { s: startFor(k), l: [] }; sel = -1; hist = []; $('#mkName').value = ''; } });
    bar('#mkTools', TOOLS, tool, k => tool = k);
    $('#mkMsg').textContent = HELP[tool] || 'Drag on empty space = new ' + TOOLS[tool].toLowerCase() + '. Drag a shape to move it, its yellow corner to resize. Tap to select. You draw the left one; the right is mirrored.';
    const pe = $('#mkPens'); pe.innerHTML = ''; for (const [k, [c, l]] of Object.entries(PENS)) { const b = document.createElement('button'); b.className = 'sw'; b.title = l; b.setAttribute('aria-label', l); b.style.background = c; b.style.outline = k === col ? '3px solid #fff' : '';
      b.onclick = () => { col = k; if (G.s[sel] && tool !== 'pen') { snap(); G.s[sel].c = k; } render(); }; pe.append(b); }
    const t = document.createElement('span'); t.textContent = PENS[col][1] + ' colour (Paint can still recolour it)'; t.style.opacity = .7; pe.append(t);
    const mine = $('#mkMine'); mine.innerHTML = ''; const list = load().filter(p => p.slot === slot);
    if (list.length) { const h = document.createElement('span'); h.textContent = 'My ' + SLOTS[slot].toLowerCase() + ' parts:'; mine.append(h); }
    for (const p of list) { const e = document.createElement('button'); e.textContent = '✎ ' + p.name; e.onclick = () => { editId = p.id; G = { s: JSON.parse(JSON.stringify(p.s)), l: JSON.parse(JSON.stringify(p.l || [])) }; sel = -1; hist = []; $('#mkName').value = p.name; draw(); };
      const d = document.createElement('button'); d.textContent = '✕'; d.title = 'Delete ' + p.name; d.onclick = () => { if (!confirmDelete(d)) return; store(load().filter(q => q.id !== p.id)); api.onDelete && api.onDelete(p); if (editId === p.id) editId = null; render(); };
      mine.append(e, d); }
    draw();
  }
  function confirmDelete(b) { if (b.dataset.sure) return true; b.dataset.sure = 1; b.textContent = 'Sure?'; setTimeout(() => { delete b.dataset.sure; b.textContent = '✕'; }, 2500); return false; }   // no pop-up dialogs
  $('#mkDup').onclick = () => { const s = G.s[sel]; if (!s) return; snap(); const c = { ...s, x: Math.round((s.x + .2) * 100) / 100 }; G.s.push(c); sel = G.s.length - 1; draw(); };
  $('#mkDel').onclick = () => { if (sel < 0) return; snap(); G.s.splice(sel, 1); sel = -1; draw(); };
  $('#mkUndo').onclick = () => { if (!hist.length) return; G = JSON.parse(hist.pop()); sel = -1; draw(); };
  $('#mkClear').onclick = () => { snap(); G = { s: [], l: [] }; sel = -1; draw(); };
  $('#mkClose').onclick = () => api.close();
  $('#mkSave').onclick = () => {
    if (!G.s.length) { $('#mkMsg').textContent = 'Make at least one shape first.'; return; }
    const list = load(), n = list.filter(p => p.slot === slot).length + 1;
    const p = { id: editId || 'my_' + slot + '_' + Date.now().toString(36), slot, name: ($('#mkName').value.trim() || 'My ' + SLOTS[slot].toLowerCase() + ' ' + n), s: G.s, l: G.l };
    const i = list.findIndex(q => q.id === p.id); if (i >= 0) list[i] = p; else list.push(p);
    store(list); editId = p.id; api.onSave && api.onSave(p); api.close();
  };
  const api = window.MF_MAKER = {
    parts: load,
    open(s) { if (s && SLOTS[s] && s !== slot) { slot = s; editId = null; G = { s: startFor(s), l: [] }; sel = -1; hist = []; $('#mkName').value = ''; } el.classList.add('open'); render(); },
    close() { el.classList.remove('open'); api.onClose && api.onClose(); },
    unit, SLOTS,
  };
})();
