// Paint (Nov 22 2026): the OLD Mythic Forge paint brought over, not rebuilt (his ask: "all the paint we had before + blending").
// Skins come from the old materials.js (FORGE_MATS: 379 skins in 31 groups, triplanar so no UVs needed).
// Brushes paint into the part's own vertices (parts are split finer the first time you paint them so strokes look smooth):
//   paintC = colour + how much it covers, paintG = how much it glows. Brushed skins are see-through copies of the part on top
//   with their own mask (up to 4 per part piece, newest on top). Saved on this phone ('mf-paint2').
// index.html calls: MF_PAINT.init(ctx), MF_PAINT.dress(holder), MF_PAINT.setOpen(on), MF_PAINT.frame(t), MF_PAINT.frozen.
(function () {
  let T, C, S, B, open = false;
  const MATS = () => window.FORGE_MATS;
  const $ = id => document.getElementById(id);
  const glowK = { value: 1 };
  const MAX_LAYERS = 4;
  const SLOTS = [['armor', 'Main'], ['armor2', 'Second'], ['accent', 'Trim'], ['frame', 'Frame'], ['glow', 'Glow bits']];
  const ELEMENTS = { Lava: ['lavarock', 'ff5a1a'], Fire: ['fire', 'ff8a2a'], Stone: ['stone'], Crystal: ['crystal', '6ad8ff'], Forest: ['mossy', '8aff6a'],
    Water: ['ocean', '4ab8ff'], Ice: ['ice', 'a8f0ff'], Storm: ['stormcloud', 'c8b4ff'], Lightning: ['lightning', 'ffe84a'], Cosmic: ['galaxy', 'c86aff'],
    Gold: ['gold', 'ffd84a'], Sand: ['sand'], Void: ['void', '9a4aff'] };
  const blank = () => ({ skins: { slot: {}, part: {} }, tile: 1, bright: 1, glow: 1, groups: [] });

  // ---------- saving: paint arrays are squeezed into bytes, runs of the same value stored once ----------
  function pack(f32, unit) {
    const n = f32.length / unit, out = [];
    let i = 0;
    while (i < n) {
      let j = i + 1;
      same: while (j < n && j - i < 65535) { for (let u = 0; u < unit; u++) if (Math.round(f32[j * unit + u] * 255) !== Math.round(f32[i * unit + u] * 255)) break same; j++; }
      const run = j - i; out.push(run & 255, run >> 8);
      for (let u = 0; u < unit; u++) out.push(Math.max(0, Math.min(255, Math.round(f32[i * unit + u] * 255))));
      i = j;
    }
    let s = ''; for (let k = 0; k < out.length; k += 8192) s += String.fromCharCode.apply(null, out.slice(k, k + 8192));
    return btoa(s);
  }
  function unpack(b64, unit, n) {
    const s = atob(b64), f = new Float32Array(n * unit); let k = 0, i = 0;
    while (k < s.length && i < n) { const run = s.charCodeAt(k) | (s.charCodeAt(k + 1) << 8); k += 2;
      const v = []; for (let u = 0; u < unit; u++) v.push(s.charCodeAt(k++) / 255);
      for (let r = 0; r < run && i < n; r++, i++) for (let u = 0; u < unit; u++) f[i * unit + u] = v[u]; }
    return f;
  }
  function store() {
    try { localStorage.setItem('mf-paint2', JSON.stringify({ S, B })); }
    catch (e) { tip('Your phone is out of save space for paint. Clear some paint to keep saving.'); }
  }

  // ---------- materials ----------
  function inject(mat, tag) {   // adds the brushed colour + glow to any material (toon or skin)
    const prev = mat.onBeforeCompile, prevKey = mat.customProgramCacheKey && mat.customProgramCacheKey !== T.Material.prototype.customProgramCacheKey ? mat.customProgramCacheKey.bind(mat) : () => mat.type;
    mat.onBeforeCompile = (sh, r) => {
      if (prev) prev.call(mat, sh, r);
      sh.uniforms.uGlowK = glowK;
      sh.vertexShader = 'attribute vec4 paintC; attribute float paintG; varying vec4 vPC; varying float vPG;\n' + sh.vertexShader.replace('#include <begin_vertex>', '#include <begin_vertex>\n vPC = paintC; vPG = paintG;');
      sh.fragmentShader = 'uniform float uGlowK; varying vec4 vPC; varying float vPG;\n' + sh.fragmentShader
        .replace('#include <color_fragment>', '#include <color_fragment>\n diffuseColor.rgb = mix(diffuseColor.rgb, vPC.rgb, vPC.a);')
        .replace('#include <lights_fragment_begin>', 'totalEmissiveRadiance = totalEmissiveRadiance * (1.0 - vPC.a) + vPC.rgb * vPG * uGlowK * 1.6;\n#include <lights_fragment_begin>');
    };
    mat.customProgramCacheKey = () => prevKey() + '|paint' + (tag || '');
    return mat;
  }
  function maskify(mat) {      // a brushed skin layer: the skin, shown only where its mask is painted
    const prev = mat.onBeforeCompile, prevKey = mat.customProgramCacheKey.bind(mat);
    mat.onBeforeCompile = (sh, r) => {
      if (prev) prev.call(mat, sh, r);
      sh.vertexShader = 'attribute float lmask; varying float vLM;\n' + sh.vertexShader.replace('#include <begin_vertex>', '#include <begin_vertex>\n vLM = lmask;');
      sh.fragmentShader = 'varying float vLM;\n' + sh.fragmentShader.replace('#include <opaque_fragment>', '#include <opaque_fragment>\n gl_FragColor.a *= clamp(vLM, 0.0, 1.0); if (gl_FragColor.a < .01) discard;');
    };
    mat.customProgramCacheKey = () => prevKey() + '|mask';
    mat.transparent = true; mat.depthWrite = false; mat.polygonOffset = true; mat.polygonOffsetFactor = -2; mat.polygonOffsetUnits = -2;
    mat.userData.outlineParameters = { visible: false };
    return mat;
  }
  const skinCache = {};
  function skinMat(key, kind) {   // kind: '' plain, 'p' takes brush paint, 'm' a mask layer
    const k = key + '|' + kind + '|' + S.tile;
    if (!skinCache[k]) { let m = MATS().makeMat(T, key, null, S.tile * .3); if (kind === 'p') m = inject(m, key); if (kind === 'm') m = maskify(m); m.userData.skin = key; skinCache[k] = m; }
    return skinCache[k];
  }
  const avgCache = {};
  function skinColour(key) {    // one colour that stands for a skin (used by Blend to mix skin tones)
    if (avgCache[key]) return avgCache[key];
    const e = MATS().LIST.find(l => l[0] === key), c = new T.Color(e ? e[4] : 0xffffff);
    try { const t = MATS().tex(T, e[3]), img = t.image;
      if (img && (img.width || img.naturalWidth)) { const cv = document.createElement('canvas'); cv.width = cv.height = 8; const x = cv.getContext('2d'); x.drawImage(img, 0, 0, 8, 8);
        const d = x.getImageData(0, 0, 8, 8).data; let r = 0, g = 0, b = 0; for (let i = 0; i < d.length; i += 4) { r += d[i]; g += d[i + 1]; b += d[i + 2]; }
        c.multiply(new T.Color().setRGB(r / 64 / 255, g / 64 / 255, b / 64 / 255, T.SRGBColorSpace)); } } catch (e) {}
    return (avgCache[key] = c);
  }

  // ---------- dressing a part: scheme colour or skin, plus any brushed paint ----------
  const meshesOf = h => { const a = []; h.traverse(m => { if (m.isMesh && !m.userData.overlay && !m.userData.ui) a.push(m); }); return a; };
  function skinFor(spot, key) {
    const p = spot && S.skins.part[spot];
    if (p && p[key] !== undefined) return p[key];
    if (p && p.all !== undefined && !(p.keepGlow && (key === 'glow' || key === 'eye'))) return p.all;
    return S.skins.slot[key] || null;
  }
  function dressMesh(m, spot) {
    const u = m.userData, key = u.key, c = C.colours(), painted = !!u.pt;
    const p = spot && S.skins.part[spot], hex = (p && (key === 'glow' || key === 'eye') && p.glowCol) || c[key];
    const skin = skinFor(spot, key);
    if (skin) { m.material = skinMat(skin, painted ? 'p' : ''); }
    else {
      const glow = key === 'glow' || key === 'eye';
      const slot = painted ? 'tmP' : 'tm';
      if (!u[slot]) { u[slot] = C.toon(u.col0, glow); u[slot].userData.key = key; if (painted) inject(u[slot]); }
      const mat = u[slot]; mat.color.set(hex ? '#' + String(hex).replace('#', '') : u.col0);
      if (glow) { mat.emissive.copy(mat.color); mat.emissiveIntensity = S.glow * (night ? 2.2 : 1); }
      m.material = mat;
    }
    m.material.userData.key = key;
    for (const L of (u.pt ? u.pt.L : [])) L.mesh.material = skinMat(L.k, 'm');
  }
  function dress(h) {
    const spot = h.userData && h.userData.spot, id = h.userData && h.userData.p && h.userData.p.id;
    const ms = meshesOf(h);
    ms.forEach(m => { if (m.userData.key === undefined) { m.userData.key = m.material.userData.key || 'armor'; m.userData.col0 = m.material.color.getHex(); m.userData.paintable = true; } });
    if (spot && B[spot] && B[spot].id !== id) { delete B[spot]; store(); }                          // a new part in this spot: its old paint goes
    if (spot && B[spot] && !h.userData.paintLoaded) { h.userData.paintLoaded = true;      // bring back saved paint
      for (const [i, d] of Object.entries(B[spot].m || {})) { const m = ms[+i]; if (!m) continue; prep(m);
        const n = m.geometry.attributes.position.count;
        try { m.userData.pt.pc.set(unpack(d.pc, 4, n)); m.userData.pt.g.set(unpack(d.g, 1, n));
          for (const l of d.L || []) { const L = addLayer(m, l.k); L.m.set(unpack(l.m, 1, n)); L.attr.needsUpdate = true; }
          m.geometry.attributes.paintC.needsUpdate = m.geometry.attributes.paintG.needsUpdate = true; } catch (e) {} } }
    ms.forEach(m => dressMesh(m, spot));
  }

  // ---------- getting a part piece ready for brush paint ----------
  function prep(m) {
    if (m.userData.pt) return m.userData.pt;
    let g = m.geometry; g.computeBoundingSphere();
    const edge = g.boundingSphere.radius * 2 / 34;
    let tess = new C.Tessellate(edge, 6).modify(g);
    if (tess.attributes.position.count > 90000) tess = new C.Tessellate(edge * 2, 6).modify(g);
    tess.computeBoundingSphere();
    const n = tess.attributes.position.count, pc = new Float32Array(n * 4), gl = new Float32Array(n);
    tess.setAttribute('paintC', new T.BufferAttribute(pc, 4)); tess.setAttribute('paintG', new T.BufferAttribute(gl, 1));
    m.geometry = tess;
    m.userData.pt = { pc, g: gl, L: [] };
    dressMesh(m, spotOf(m));
    return m.userData.pt;
  }
  function addLayer(m, k) {
    const pt = m.userData.pt, g = m.geometry, n = g.attributes.position.count, mk = new Float32Array(n);
    const lg = new T.BufferGeometry(); lg.setAttribute('position', g.attributes.position); if (g.attributes.normal) lg.setAttribute('normal', g.attributes.normal);
    const attr = new T.BufferAttribute(mk, 1); lg.setAttribute('lmask', attr); lg.boundingSphere = g.boundingSphere;
    const mesh = new T.Mesh(lg, skinMat(k, 'm')); mesh.userData.overlay = true; mesh.renderOrder = 2 + pt.L.length; mesh.raycast = () => {};
    m.add(mesh); const L = { k, m: mk, attr, mesh }; pt.L.push(L); return L;
  }
  function spotOf(o) { while (o) { if (o.userData && o.userData.spot) return o.userData.spot; o = o.parent; } return null; }
  function holderOf(o) { while (o) { if (o.userData && o.userData.spot && o.userData.p) return o; o = o.parent; } return null; }

  // ---------- brushes ----------
  let sec = 'brush', brush = null, withSkin = false, brushSkin = 'chrome', both = false, glowPaint = false;
  const col = { hex: '#ff3030' };
  const ray = () => new T.Raycaster();
  const paintables = () => { const a = []; for (const h of Object.values(C.held)) h.traverse(m => { if (m.isMesh && m.userData.paintable && m.visible) a.push(m); }); return a; };
  function hitAt(x, y) {
    const r = ray(); r.setFromCamera(new T.Vector2(x / innerWidth * 2 - 1, -(y / innerHeight) * 2 + 1), C.camera);
    return r.intersectObjects(paintables(), false)[0] || null;
  }
  const radius = () => +$('pbSize').value;
  const power = () => +$('pbPower').value;
  function near(p, r) {    // part pieces whose bounds reach the brush
    const out = [];
    for (const m of paintables()) { const g = m.geometry; if (!g.boundingSphere) g.computeBoundingSphere();
      const c = g.boundingSphere.center.clone().applyMatrix4(m.matrixWorld), rr = g.boundingSphere.radius * m.matrixWorld.getMaxScaleOnAxis();
      if (c.distanceTo(p) <= rr + r) out.push(m); }
    return out;
  }
  function worldPos(m) { const P = m.geometry.attributes.position, n = P.count, w = new Float32Array(n * 3), e = m.matrixWorld.elements;
    for (let i = 0; i < n; i++) { const x = P.array[i * 3], y = P.array[i * 3 + 1], z = P.array[i * 3 + 2];
      w[i * 3] = e[0] * x + e[4] * y + e[8] * z + e[12]; w[i * 3 + 1] = e[1] * x + e[5] * y + e[9] * z + e[13]; w[i * 3 + 2] = e[2] * x + e[6] * y + e[10] * z + e[14]; }
    return w; }
  // undo: remember a piece before the first change of each stroke
  const undoStack = []; let stroke = null;
  function remember(m) {
    if (!stroke || stroke.has(m)) return; const pt = m.userData.pt;
    stroke.set(m, { pc: pt.pc.slice(), g: pt.g.slice(), L: pt.L.map(l => ({ k: l.k, m: l.m.slice() })) });
  }
  function layerFor(m, k) {
    const pt = m.userData.pt; let j = pt.L.findIndex(l => l.k === k);
    if (j < 0) { if (pt.L.length >= MAX_LAYERS) { tip('This piece already has 4 brushed skins: the newest one gets painted over.'); j = MAX_LAYERS - 1; pt.L[j].k = k; pt.L[j].mesh.material = skinMat(k, 'm'); }
      else { addLayer(m, k); j = pt.L.length - 1; } }
    return j;
  }
  // one dab of paint at a world point; how = 'color' | 'spray' | 'erase' | 'blotch' | 'blend'
  function dab(p, how, stamp) {
    const r = radius(), s = power();
    if (how === 'blend') return blendAt(p, r, s);
    const lin = new T.Color(col.hex || '#ff3030');
    for (const m of near(p, r)) {
      prep(m); remember(m);
      const pt = m.userData.pt, w = worldPos(m), n = w.length / 3, wantSkin = withSkin && how !== 'erase'; let sj = -1;
      let changed = false;
      for (let i = 0; i < n; i++) {
        const dx = w[i * 3] - p.x, dy = w[i * 3 + 1] - p.y, dz = w[i * 3 + 2] - p.z; let d = Math.sqrt(dx * dx + dy * dy + dz * dz);
        let rr = r;
        if (stamp) { const a = Math.atan2(dy, dx + dz) ; rr = r * stamp.shape(a); if (d > rr) { d = stamp.drop(w[i * 3], w[i * 3 + 1], w[i * 3 + 2]); if (d < 0) continue; rr = 1; } }
        if (d >= rr) continue;
        let f = 1 - d / rr; f = f * f * (3 - 2 * f);
        if (how === 'spray') { const mist = +$('pbMist').value, chance = .75 - mist * .67, h = Math.sin(i * 12.9898 + performance.now() * .37) * 43758.5453; if (h - Math.floor(h) > chance) continue; f *= (.12 + mist * .7); }
        else if (how === 'blotch') f = Math.min(1, f * 3);
        f *= s; if (f <= 0) continue; changed = true;
        if (wantSkin && sj < 0) sj = layerFor(m, brushSkin);
        if (how === 'erase') { pt.pc[i * 4 + 3] *= 1 - f; pt.g[i] *= 1 - f; for (const L of pt.L) L.m[i] *= 1 - f; continue; }
        if (sj >= 0) { const L = pt.L[sj]; L.m[i] += (1 - L.m[i]) * f; for (let k = sj + 1; k < pt.L.length; k++) pt.L[k].m[i] *= 1 - f; }
        else { const a = pt.pc[i * 4 + 3], na = a + (1 - a) * f, wOld = a * (1 - f) / Math.max(na, 1e-5), wNew = 1 - wOld;
          pt.pc[i * 4] = pt.pc[i * 4] * wOld + lin.r * wNew; pt.pc[i * 4 + 1] = pt.pc[i * 4 + 1] * wOld + lin.g * wNew; pt.pc[i * 4 + 2] = pt.pc[i * 4 + 2] * wOld + lin.b * wNew; pt.pc[i * 4 + 3] = na;
          for (const L of pt.L) L.m[i] *= 1 - f; }
        pt.g[i] = glowPaint ? pt.g[i] + (1 - pt.g[i]) * f : pt.g[i] * (1 - f);
      }
      if (changed) flag(m);
    }
  }
  function flag(m) { const g = m.geometry, pt = m.userData.pt; g.attributes.paintC.needsUpdate = g.attributes.paintG.needsUpdate = true; for (const L of pt.L) L.attr.needsUpdate = true; }
  function baseCol(m) { const mat = m.material; return mat.userData.skin ? skinColour(mat.userData.skin) : mat.color; }
  // 🌫 Blend: mixes colours and skin tones over the whole mech, across part edges. Where a brushed skin sits on top it only softens that skin's edge.
  function blendAt(p, r, s) {
    const ms = near(p, r), pts = [], cell = Math.max(r * .32, 1e-3), grid = new Map();
    for (const m of ms) { prep(m); remember(m); const pt = m.userData.pt, w = worldPos(m), base = baseCol(m), n = w.length / 3;
      for (let i = 0; i < n; i++) { const x = w[i * 3], y = w[i * 3 + 1], z = w[i * 3 + 2], d = Math.hypot(x - p.x, y - p.y, z - p.z); if (d > r * 1.3) continue;
        const a = pt.pc[i * 4 + 3]; let cr = base.r * (1 - a) + pt.pc[i * 4] * a, cg = base.g * (1 - a) + pt.pc[i * 4 + 1] * a, cb = base.b * (1 - a) + pt.pc[i * 4 + 2] * a;
        const br = cr, bg = cg, bb = cb; let cover = 0;
        for (const L of pt.L) { const sc = skinColour(L.k), t = L.m[i]; cr += (sc.r - cr) * t; cg += (sc.g - cg) * t; cb += (sc.b - cb) * t; cover = Math.max(cover, t); }
        const q = { m, i, x, y, z, d, c: [cr, cg, cb], b: [br, bg, bb], base, cover, L: pt.L.map(L => L.m[i]) }; pts.push(q);
        const key = Math.floor(x / cell) + ',' + Math.floor(y / cell) + ',' + Math.floor(z / cell); (grid.get(key) || grid.set(key, []).get(key)).push(q); } }
    for (const q of pts) { if (q.d >= r) continue;
      let f = 1 - q.d / r; f = f * f * (3 - 2 * f) * s * .5; if (f <= 0) continue;
      const cx = Math.floor(q.x / cell), cy = Math.floor(q.y / cell), cz = Math.floor(q.z / cell); let sr = 0, sg = 0, sb = 0, n = 0; const lm = q.L.map(() => 0); let ln = 0;
      for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) for (let c = -1; c <= 1; c++) for (const o of grid.get((cx + a) + ',' + (cy + b) + ',' + (cz + c)) || []) {
        sr += o.c[0]; sg += o.c[1]; sb += o.c[2]; n++; if (o.m === q.m) { o.L.forEach((v, k) => lm[k] += v); ln++; } }
      const pt = q.m.userData.pt, i = q.i;
      if (ln) pt.L.forEach((L, k) => { L.m[i] += (lm[k] / ln - L.m[i]) * f * 2; });
      if (q.cover > .5 || !n) continue;               // an overlay is on top here: only its edge got softened
      const tr = q.b[0] + (sr / n - q.b[0]) * f * 2, tg = q.b[1] + (sg / n - q.b[1]) * f * 2, tb = q.b[2] + (sb / n - q.b[2]) * f * 2;
      const a = pt.pc[i * 4 + 3], na = Math.min(1, a + (1 - a) * f * 2), cl = v => Math.max(0, Math.min(1, v));
      pt.pc[i * 4] = cl((tr - q.base.r * (1 - na)) / na); pt.pc[i * 4 + 1] = cl((tg - q.base.g * (1 - na)) / na); pt.pc[i * 4 + 2] = cl((tb - q.base.b * (1 - na)) / na); pt.pc[i * 4 + 3] = na;
    }
    ms.forEach(flag);
  }
  // 🩸 Blotch: a splat with a ragged edge and a few droplets around it
  function makeStamp(p, r) {
    const ph = [0, 1, 2, 3].map(() => Math.random() * 6.28), k = [3, 5, 7, 11];
    const drops = [0, 1, 2, 3, 4].slice(0, 2 + Math.floor(Math.random() * 4)).map(() => { const a = Math.random() * 6.28, b = Math.random() * 3.14, d = r * (1.15 + Math.random() * .55);
      return { x: p.x + Math.cos(a) * Math.sin(b) * d, y: p.y + Math.cos(b) * d, z: p.z + Math.sin(a) * Math.sin(b) * d, r: r * (.12 + Math.random() * .16) }; });
    return { shape: a => .72 + .14 * Math.sin(k[0] * a + ph[0]) + .1 * Math.sin(k[1] * a + ph[1]) + .07 * Math.sin(k[2] * a + ph[2]) + .05 * Math.sin(k[3] * a + ph[3]),
      drop: (x, y, z) => { for (const d of drops) { const dd = Math.hypot(x - d.x, y - d.y, z - d.z); if (dd < d.r) return dd / d.r; } return -1; } };
  }
  // 🪣 Fill: a whole piece (paint by number) or every piece of the marked parts
  function fillMesh(m) {
    prep(m); remember(m); const pt = m.userData.pt, n = pt.g.length, lin = new T.Color(col.hex || '#ff3030');
    if (withSkin) { const j = layerFor(m, brushSkin); pt.L[j].m.fill(1); for (let k = j + 1; k < pt.L.length; k++) pt.L[k].m.fill(0); }
    else { for (let i = 0; i < n; i++) { pt.pc[i * 4] = lin.r; pt.pc[i * 4 + 1] = lin.g; pt.pc[i * 4 + 2] = lin.b; pt.pc[i * 4 + 3] = 1; } for (const L of pt.L) L.m.fill(0); }
    pt.g.fill(glowPaint ? 1 : 0); flag(m);
  }
  const mirrorP = p => new T.Vector3(-p.x, p.y, p.z);
  function nearestPiece(p) { let best = null, bd = 1e9; for (const m of near(p, .3)) { const w = worldPos(m); for (let i = 0; i < w.length; i += 9) { const d = Math.hypot(w[i] - p.x, w[i + 1] - p.y, w[i + 2] - p.z); if (d < bd) { bd = d; best = m; } } } return bd < .5 ? best : null; }

  // ---------- pointer: one finger paints while a brush is on (two fingers still zoom / slide) ----------
  let down = null, lastPt = null, stamp = null, lastStampAt = null, pointers = 0;
  const ringEl = () => $('pRing');
  function ringAt(x, y) { const el = ringEl(); if (!brush || x == null) { el.style.display = 'none'; return; }
    const dist = C.camera.position.distanceTo(C.controls.target), px = radius() / (dist * Math.tan(C.camera.fov * Math.PI / 360)) * innerHeight / 2;
    Object.assign(el.style, { display: 'block', left: x - px + 'px', top: y - px + 'px', width: px * 2 + 'px', height: px * 2 + 'px' }); }
  function strokeTo(x, y) {
    const steps = lastPt ? Math.max(1, Math.ceil(Math.hypot(x - lastPt[0], y - lastPt[1]) / 10)) : 1;
    for (let k = 1; k <= steps; k++) {
      const sx = lastPt ? lastPt[0] + (x - lastPt[0]) * k / steps : x, sy = lastPt ? lastPt[1] + (y - lastPt[1]) * k / steps : y;
      const hit = hitAt(sx, sy); if (!hit) continue;
      const p = hit.point, how = brush;
      if (how === 'blotch') { if (lastStampAt && lastStampAt.distanceTo(p) < radius() * 1.4) continue; lastStampAt = p.clone();
        stamp = makeStamp(p, radius()); dab(p, 'blotch', stamp); if (both) dab(mirrorP(p), 'blotch', makeStamp(mirrorP(p), radius())); continue; }
      dab(p, how); if (both) dab(mirrorP(p), how);
    }
    lastPt = [x, y];
  }
  function endStroke() {
    if (stroke && stroke.size) { undoStack.push(stroke); if (undoStack.length > 25) undoStack.shift(); saveBrush(); }
    stroke = null; down = null; lastPt = null; lastStampAt = null;
  }
  function wirePointer() {
    const el = C.renderer.domElement;
    el.addEventListener('pointerdown', e => { pointers++; if (!open) return;
      if (pointers > 1) { endStroke(); return; }
      down = { x: e.clientX, y: e.clientY, t: performance.now() };
      if (!brush) return;
      if (brush === 'fill') { const hit = hitAt(e.clientX, e.clientY); if (hit) { stroke = new Map(); fillMesh(hit.object);
        if (both) { const o = nearestPiece(mirrorP(hit.point)); if (o && o !== hit.object) fillMesh(o); } endStroke(); } return; }
      stroke = new Map(); strokeTo(e.clientX, e.clientY); });
    el.addEventListener('pointermove', e => { if (!open) return; ringAt(brush ? e.clientX : null, e.clientY); if (stroke && pointers === 1) strokeTo(e.clientX, e.clientY); });
    const up = e => { pointers = Math.max(0, pointers - 1); if (!open) return;
      if (down && !brush && Math.hypot(e.clientX - down.x, e.clientY - down.y) < 8 && performance.now() - down.t < 400) tapAt(e.clientX, e.clientY);
      if (stroke) endStroke(); down = null; if (e.pointerType !== 'mouse') ringAt(null); };
    el.addEventListener('pointerup', up); el.addEventListener('pointercancel', up);
    el.addEventListener('pointerleave', () => ringAt(null));
  }
  function undo() {
    const st = undoStack.pop(); if (!st) return tip('Nothing to undo');
    for (const [m, d] of st) { const pt = m.userData.pt; pt.pc.set(d.pc); pt.g.set(d.g);
      while (pt.L.length > d.L.length) { const L = pt.L.pop(); m.remove(L.mesh); }
      d.L.forEach((l, k) => { pt.L[k].k = l.k; pt.L[k].m.set(l.m); pt.L[k].mesh.material = skinMat(l.k, 'm'); }); flag(m); }
    saveBrush();
  }
  function saveBrush() {
    for (const [spot, h] of Object.entries(C.held)) {
      const ms = meshesOf(h), m = {}; let any = false;
      ms.forEach((x, i) => { const pt = x.userData.pt; if (!pt) return;
        if (!pt.pc.some((v, k) => k % 4 === 3 && v > .002) && !pt.L.some(L => L.m.some(v => v > .002)) && !pt.g.some(v => v > .002)) return;
        m[i] = { pc: pack(pt.pc, 4), g: pack(pt.g, 1), L: pt.L.map(L => ({ k: L.k, m: pack(L.m, 1) })) }; any = true; });
      if (any) B[spot] = { id: h.userData.p.id, m }; else delete B[spot];
    }
    store();
  }
  function clearPaint(spots) {
    stroke = new Map();
    for (const s of spots) { const h = C.held[s]; if (!h) continue; for (const m of meshesOf(h)) { const pt = m.userData.pt; if (!pt) continue; remember(m);
      pt.pc.fill(0); pt.g.fill(0); for (const L of pt.L) L.m.fill(0); flag(m); } }
    endStroke();
  }

  // ---------- picking parts: tap one, or mark several ----------
  let tapped = null, marking = false; const marks = new Set(); const boxes = new Map();
  function boxFor(spot, colr) { let b = boxes.get(spot); const h = C.held[spot]; if (!h) return;
    if (!b) { b = new T.BoxHelper(h, colr); b.material.depthTest = false; b.renderOrder = 9; b.userData.ui = true; b.material.userData.outlineParameters = { visible: false }; C.scene.add(b); boxes.set(spot, b); }
    b.material.color.set(colr); b.setFromObject(h); }
  function refreshBoxes() {
    for (const [s, b] of boxes) { const want = open && (marks.has(s) || s === tapped); if (!want || !C.held[s]) { C.scene.remove(b); boxes.delete(s); } }
    if (!open) return;
    for (const s of marks) if (C.held[s]) boxFor(s, 0x38e8ff);
    if (tapped && C.held[tapped] && !marks.has(tapped)) boxFor(tapped, 0xffc040);
  }
  function tapAt(x, y) {
    const hit = hitAt(x, y), h = hit && holderOf(hit.object), s = h && h.userData.spot;
    if (marking) { if (!s) return; marks.has(s) ? marks.delete(s) : marks.add(s); refreshBoxes(); showMarks(); return; }
    tapped = s || null; refreshBoxes(); numbers();
    if (s) { $('pTarget').value = 'part'; tip(nice(s) + ' picked: skins and Fill now go on it.'); }
  }
  const nice = s => s.replace(/\.L$/, ' (left)').replace(/\.R$/, ' (right)').replace('back', 'backpack').replace('weapon', 'hand weapon').replace('mount', 'shoulder weapon').replace('_', ' ');
  function showMarks() { $('pMarkInfo').textContent = marks.size ? marks.size + ' marked: ' + [...marks].map(nice).join(', ') : 'Nothing marked.'; }
  // paint by number: numbers on each piece of the tapped part; tap a number to fill that piece
  function numbers() {
    const box = $('pNums'); box.innerHTML = '';
    if (!open || !tapped || !C.held[tapped] || !$('pNumBtn').classList.contains('on')) return;
    meshesOf(C.held[tapped]).forEach((m, i) => { const b = document.createElement('button'); b.textContent = i + 1; b.className = 'pnum';
      b.onclick = () => { stroke = new Map(); fillMesh(m); endStroke(); }; b._m = m; box.append(b); });
  }
  function placeNumbers() {
    for (const b of $('pNums').children) { const m = b._m; if (!m.geometry.boundingSphere) m.geometry.computeBoundingSphere();
      const v = m.geometry.boundingSphere.center.clone().applyMatrix4(m.matrixWorld).project(C.camera);
      b.style.left = (v.x + 1) / 2 * innerWidth - 15 + 'px'; b.style.top = (1 - v.y) / 2 * innerHeight - 15 + 'px'; b.style.display = v.z < 1 ? 'block' : 'none'; }
  }

  // ---------- skins on whole slots / parts ----------
  function targets() {
    const t = $('pTarget').value;
    if (t === 'part') return tapped ? [tapped] : (tip('Tap a part on the mech first'), []);
    if (t === 'marked') return marks.size ? [...marks] : (tip('Turn on Mark and tap some parts first'), []);
    return null;   // a whole-mech colour slot
  }
  function putSkin(k) {
    if (brush && k) { brushSkin = k; withSkin = true; syncBrushUI(); tip('Brush now paints with ' + nameOf(k)); return; }
    const t = $('pTarget').value, sp = targets();
    if (sp === null) { if (k) S.skins.slot[t] = k; else delete S.skins.slot[t]; }
    else { if (!sp.length) return; for (const s of sp) { const p = S.skins.part[s] || (S.skins.part[s] = {}); if (k) { p.all = k; p.keepGlow = true; } else { delete p.all; delete p.glowCol; } if (!Object.keys(p).length || (!p.all && !p.glowCol)) delete S.skins.part[s]; } }
    redressAll(); store();
  }
  function redressAll() { C.paintAll(); }
  const nameOf = k => { const e = MATS().LIST.find(l => l[0] === k); return e ? e[1] : k; };
  function showSkins() {
    const g = $('pGroup').value, box = $('pSkins'); box.innerHTML = '';
    const plain = document.createElement('button'); plain.textContent = '✖ No skin'; plain.onclick = () => putSkin(null); box.append(plain);
    for (const e of MATS().LIST) if (e[2] === g) { const b = document.createElement('button'); b.textContent = e[1]; b.onclick = () => putSkin(e[0]);
      const sc = skinColour(e[0]); b.style.borderLeft = '8px solid #' + sc.getHexString(); box.append(b); }
  }
  function element(name) {
    const sp = targets(); if (!sp || !sp.length) { if (sp === null) tip('Elements go on a tapped or marked part: set "Put on" to one of those'); return; }
    const [k, glowHex] = ELEMENTS[name];
    for (const s of sp) { const p = S.skins.part[s] = S.skins.part[s] || {}; p.all = k; p.keepGlow = true; if (glowHex) p.glowCol = glowHex; else delete p.glowCol; }
    redressAll(); store();
  }

  // ---------- light: brightness, glow strength, night preview ----------
  let night = false, base = null;
  function light(redress = true) {
    if (!base) base = { hemi: C.lights.hemi.intensity, sun: C.lights.sun.intensity, rim: C.lights.rim.intensity, bg: C.scene.background.clone() };
    const k = S.bright * (night ? .22 : 1);
    C.lights.hemi.intensity = base.hemi * k; C.lights.sun.intensity = base.sun * k; C.lights.rim.intensity = base.rim * (night ? .6 : 1) * S.bright;
    C.scene.background.copy(night ? new T.Color(0x05060a) : base.bg);
    glowK.value = S.glow * (night ? 2.2 : 1);
    if (redress) redressAll();
  }

  // ---------- the panel ----------
  function tip(t) { const el = $('pTip'); if (el) { el.textContent = t; el.style.opacity = 1; clearTimeout(tip.t); tip.t = setTimeout(() => el.style.opacity = .65, 2500); } }
  function syncBrushUI() {
    document.querySelectorAll('[data-pb]').forEach(b => b.classList.toggle('on', (b.dataset.pb || null) === (brush || '')));
    $('pWith').textContent = withSkin ? '🧴 Paints with skin: ' + nameOf(brushSkin) : '🎨 Paints with colour';
    const inB = sec === 'brush';
    $('pBrushRow').style.display = inB && brush ? 'flex' : 'none'; $('pMistRow').style.display = inB && brush === 'spray' ? 'flex' : 'none';
    $('pWithRow').style.display = inB && brush && brush !== 'erase' && brush !== 'blend' ? 'flex' : 'none';
    C.controls.enableRotate = !brush;
    MF_PAINT.frozen = !!brush;
    $('pHint').textContent = brush ? (brush === 'fill' ? 'Tap a piece to fill it. Two fingers (or the view buttons) still move the camera.' : 'Drag on the mech to paint. Two fingers (or the view buttons) still move the camera; the mech holds still while a brush is on.')
      : 'Tap a part to pick it. Pick a skin to put it on the picked part, or on a whole colour slot.';
  }
  function buildUI() {
    const groups = [...new Set(MATS().LIST.map(e => e[2]))];
    const panel = $('paint');
    panel.insertAdjacentHTML('afterbegin', `<div class="line" id="pTabs"><button data-pt="brush" class="on">🖌 Brushes</button><button data-pt="skin">🧴 Skins</button><button data-pt="mark">🔖 Mark</button><button data-pt="more">💡 Light +</button></div>
      <p class="hint" id="pTip" style="opacity:.65;color:#ffd27a;min-height:1em"></p>`);
    panel.querySelectorAll(':scope > .line:not(#pTabs)').forEach(el => el.dataset.sec = 'skin');   // the colour scheme rows live under Skins
    panel.insertAdjacentHTML('beforeend', `
      <p class="hint" id="pHint" data-sec="brush"></p>
      <div class="line" data-sec="brush"><button data-pb="">👆 Off</button><button data-pb="color">🖌 Color</button><button data-pb="spray">🥫 Spray</button><button data-pb="blotch">🩸 Blotch</button><button data-pb="fill">🪣 Fill</button><button data-pb="blend">🌫 Blend</button><button data-pb="erase">🧽 Eraser</button></div>
      <div class="line" data-sec="brush" id="pBrushRow"><input type="color" id="pbCol" value="#ff3030"><span>Size</span><input type="range" id="pbSize" min=".08" max="2" step=".02" value=".45"><span>Strength</span><input type="range" id="pbPower" min=".05" max="1" step=".05" value=".8"></div>
      <div class="line" data-sec="brush" id="pMistRow"><span>Mist</span><small>fine</small><input type="range" id="pbMist" min="0" max="1" step=".05" value=".25"><small>speckles</small></div>
      <div class="line" data-sec="brush" id="pWithRow"><button id="pWith"></button><button id="pGlowP">✦ Glow paint</button></div>
      <div class="line" data-sec="brush"><button id="pBoth">🪞 Both sides</button><button id="pUndo">↶ Undo</button><button id="pClearPart">Clear picked</button><button id="pClearAll">Clear all paint</button></div>
      <div class="line" data-sec="skin"><span>Put on:</span><select id="pTarget">${SLOTS.map(([k, n]) => `<option value="${k}">Whole mech: ${n}</option>`).join('')}<option value="part">Picked part</option><option value="marked">Marked parts</option></select></div>
      <div class="line" data-sec="skin"><select id="pGroup">${groups.map(g => `<option>${g}</option>`).join('')}</select><span>Pattern</span><input type="range" id="pTile" min=".3" max="3" step=".1" value="1"><button id="pClearSkins">Clear skins</button></div>
      <div class="line" data-sec="skin" id="pSkins"></div>
      <div class="line" data-sec="mark"><button id="pMark">🔖 Mark parts</button><button id="pMarkClear">Clear marks</button><button id="pFillMarked">🪣 Fill marked</button></div>
      <div class="line" data-sec="mark"><small id="pMarkInfo">Nothing marked.</small></div>
      <div class="line" data-sec="mark"><input id="pGroupName" placeholder="Group name" style="font:inherit;min-height:36px;border-radius:8px;background:#2c2c30;color:#eee;border:1px solid #4a4a4e;padding:0 8px;width:130px"><button id="pGroupSave">Save group</button><select id="pGroups"></select><button id="pGroupDel">Delete</button></div>
      <div class="line" data-sec="mark"><button id="pNumBtn">🔢 Paint by number (picked part)</button></div>
      <div class="line" data-sec="more"><span>Element:</span><select id="pElem"><option value="">On picked / marked part...</option>${Object.keys(ELEMENTS).map(k => `<option>${k}</option>`).join('')}</select></div>
      <div class="line" data-sec="more"><span>Brightness</span><input type="range" id="pBright" min=".4" max="1.2" step=".05"></div>
      <div class="line" data-sec="more"><span>Glow</span><input type="range" id="pGlow" min="0" max="3" step=".1"><button id="pNight">🌙 Night preview</button></div>`);
    const showSec = k => { panel.querySelectorAll('[data-sec]').forEach(el => el.hidden = el.dataset.sec !== k); panel.querySelectorAll('[data-pt]').forEach(b => b.classList.toggle('on', b.dataset.pt === k)); sec = k; syncBrushUI(); };
    panel.querySelectorAll('[data-pt]').forEach(b => b.onclick = () => showSec(b.dataset.pt));
    document.body.insertAdjacentHTML('beforeend', '<div id="pRing"></div><div id="pNums"></div>');
    document.querySelectorAll('[data-pb]').forEach(b => b.onclick = () => { brush = b.dataset.pb || null; if (brush === 'erase' || brush === 'blend') withSkin = false; marking = false; $('pMark').classList.remove('on'); syncBrushUI(); });
    $('pbCol').oninput = e => { col.hex = e.target.value; withSkin = false; syncBrushUI(); };
    $('pWith').onclick = () => { withSkin = !withSkin; syncBrushUI(); if (withSkin) tip('Open 🧴 Skins and tap the skin the brush should paint with.'); };
    $('pGlowP').onclick = e => { glowPaint = !glowPaint; e.target.classList.toggle('on', glowPaint); };
    $('pBoth').onclick = e => { both = !both; e.target.classList.toggle('on', both); };
    $('pUndo').onclick = undo;
    $('pClearPart').onclick = () => tapped ? clearPaint([tapped]) : tip('Tap a part first');
    $('pClearAll').onclick = () => clearPaint(Object.keys(C.held));
    $('pGroup').onchange = showSkins;
    $('pTile').value = S.tile; $('pTile').onchange = e => { S.tile = +e.target.value; redressAll(); store(); };
    $('pClearSkins').onclick = () => { S.skins = { slot: {}, part: {} }; redressAll(); store(); };
    $('pMark').onclick = e => { marking = !marking; e.target.classList.toggle('on', marking); if (marking) { brush = null; syncBrushUI(); tip('Tap parts to mark them (tap again to unmark).'); } refreshBoxes(); };
    $('pMarkClear').onclick = () => { marks.clear(); refreshBoxes(); showMarks(); };
    $('pFillMarked').onclick = () => { if (!marks.size) return tip('Mark some parts first'); stroke = new Map(); for (const s of marks) if (C.held[s]) meshesOf(C.held[s]).forEach(fillMesh); endStroke(); };
    const groupsUI = () => { $('pGroups').innerHTML = '<option value="">Saved groups...</option>' + S.groups.map((g, i) => `<option value="${i}">${g.n} (${g.s.length})</option>`).join(''); };
    $('pGroupSave').onclick = () => { if (!marks.size) return tip('Mark some parts first'); const n = $('pGroupName').value.trim() || 'Group ' + (S.groups.length + 1); S.groups.push({ n, s: [...marks] }); $('pGroupName').value = ''; groupsUI(); store(); tip('Saved "' + n + '"'); };
    $('pGroups').onchange = e => { const g = S.groups[+e.target.value]; if (!g) return; marks.clear(); g.s.forEach(s => marks.add(s)); refreshBoxes(); showMarks(); $('pTarget').value = 'marked'; };
    $('pGroupDel').onclick = () => { const i = $('pGroups').value; if (i === '') return tip('Pick a saved group first'); S.groups.splice(+i, 1); groupsUI(); store(); };
    groupsUI();
    $('pNumBtn').onclick = e => { e.target.classList.toggle('on'); if (!tapped) tip('Tap a part to see its numbered pieces'); numbers(); };
    $('pElem').onchange = e => { if (e.target.value) element(e.target.value); e.target.value = ''; };
    $('pBright').value = S.bright; $('pBright').oninput = e => { S.bright = +e.target.value; light(); store(); };
    $('pGlow').value = S.glow; $('pGlow').oninput = e => { S.glow = +e.target.value; light(); store(); };
    $('pNight').onclick = e => { night = !night; e.target.classList.toggle('on', night); light(); };
    $('pGroup').value = 'Metal'; showSkins(); showSec('brush');
  }

  window.MF_PAINT = {
    frozen: false,
    init(ctx) {
      C = ctx; T = ctx.THREE;
      let d = null; try { d = JSON.parse(localStorage.getItem('mf-paint2')); } catch (e) {}
      S = Object.assign(blank(), d && d.S); B = (d && d.B) || {};
      buildUI(); wirePointer(); light(false);
    },
    dress,
    setOpen(on) { open = on; if (!on) { brush = null; marking = false; $('pMark').classList.remove('on'); syncBrushUI(); ringAt(null); } refreshBoxes(); numbers(); },
    frame(t) { if (MATS()) MATS().tick(t); if (open) { for (const [s, b] of boxes) if (C.held[s]) b.setFromObject(C.held[s]); placeNumbers(); } },
    _test: { hit: (x, y) => hitAt(x, y), dab: (p, how) => { stroke = new Map(); dab(p, how); endStroke(); }, fill: m => { stroke = new Map(); fillMesh(m); endStroke(); }, setBrush: b => { brush = b; syncBrushUI(); }, setColour: h => { col.hex = h; }, skin: k => putSkin(k), state: () => ({ S, B }), undo, element, tapAt, marks, both: v => { both = v; }, withSkin: (v, k) => { withSkin = v; if (k) brushSkin = k; } }
  };
})();
