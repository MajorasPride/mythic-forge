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
  const blank = () => ({ skins: { slot: {}, part: {} }, tile: 1, bright: 1, glow: 1, groups: [], decals: [], swatches: [], bitsOn: true });

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
    const spot = pspot(h), id = pid(h);
    const ms = meshesOf(h);
    ms.forEach(m => { if (!m.userData.paintable) { m.userData.key = m.userData.key || m.material.userData.key || (m.userData.block ? 'block' : 'armor'); m.userData.col0 = m.material.color.getHex(); m.userData.paintable = true; } });
    if (spot && B[spot] && B[spot].id !== id) { delete B[spot]; store(); }                          // a new part in this spot: its old paint goes
    const first = !h.userData.paintLoaded; h.userData.paintLoaded = true;                // only a part that was just put on gets its saved paint back (never on top of live paint)
    if (first && spot && B[spot]) {
      for (const [i, d] of Object.entries(B[spot].m || {})) { const m = ms[+i]; if (!m) continue; prep(m);
        const n = m.geometry.attributes.position.count;
        try { m.userData.pt.pc.set(unpack(d.pc, 4, n)); m.userData.pt.g.set(unpack(d.g, 1, n));
          for (const l of d.L || []) { const L = addLayer(m, l.k); L.m.set(unpack(l.m, 1, n)); L.attr.needsUpdate = true; }
          m.geometry.attributes.paintC.needsUpdate = m.geometry.attributes.paintG.needsUpdate = true; } catch (e) {} } }
    ms.forEach(m => dressMesh(m, spot));
    if (spot) { growBits(h, spot);
      if (S.decals.some(d => d.spot === spot && d.pid !== id)) { S.decals = S.decals.filter(d => !(d.spot === spot && d.pid !== id)); store(); }
      if (!h.userData.decalsBuilt) { h.userData.decalsBuilt = true; for (const d of S.decals) if (d.spot === spot) buildDecal(d); } }
  }

  // ---------- getting a part piece ready for brush paint ----------
  function prep(m) {
    if (m.userData.pt) return m.userData.pt;
    let g = m.geometry; g.computeBoundingSphere(); m.userData.geo0 = g;   // the shape before it's split finer (edge wear and element bits read it)
    const P = g.parameters;
    if (g.type === 'BoxGeometry' || g.type === 'SphereGeometry') {   // frame pieces are remade when the Body sliders move: same vertex count every time so the paint fits back on
      const ng = g.type === 'BoxGeometry' ? new T.BoxGeometry(P.width, P.height, P.depth, 14, 14, 14) : new T.SphereGeometry(P.radius, 36, 22);
      ng.computeBoundingSphere(); const n = ng.attributes.position.count, pc = new Float32Array(n * 4), gl = new Float32Array(n);
      ng.setAttribute('paintC', new T.BufferAttribute(pc, 4)); ng.setAttribute('paintG', new T.BufferAttribute(gl, 1));
      m.geometry = ng; m.userData.pt = { pc, g: gl, L: [] }; dressMesh(m, spotOf(m)); return m.userData.pt;
    }
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
  // a "holder" = one paintable thing: a body part / weapon in a spot, a detail, or a frame piece (stand-in block, waist, joint cap)
  const pspot = h => h && h.userData ? (h.userData.paintSpot || h.userData.spot || null) : null;
  const pid = h => h && h.userData ? (h.userData.paintId || (h.userData.p && h.userData.p.id) || null) : null;
  const ALL = () => { const o = { ...C.held }; for (const x of C.extras()) if (pspot(x)) o[pspot(x)] = x; return o; };
  function spotOf(o) { while (o) { if (pspot(o)) return pspot(o); o = o.parent; } return null; }
  function holderOf(o) { while (o) { if (pspot(o) && pid(o)) return o; o = o.parent; } return null; }

  // ---------- brushes ----------
  let sec = 'brush', brush = null, withSkin = false, brushSkin = 'chrome', both = false, glowPaint = false;
  const col = { hex: '#ff3030' };
  const ray = () => new T.Raycaster();
  const paintables = () => { const a = []; for (const h of Object.values(ALL())) h.traverse(m => { if (m.isMesh && m.userData.paintable && m.visible) a.push(m); }); return a; };
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
    if (j < 0) { const free = pt.L.findIndex(l => !l.m.some(v => v > .01));
      if (free >= 0 && pt.L.length >= MAX_LAYERS) { j = free; pt.L[j].k = k; pt.L[j].mesh.material = skinMat(k, 'm'); }
      else if (pt.L.length >= MAX_LAYERS) { tip('This piece already has 4 brushed skins: the newest one gets painted over.'); j = MAX_LAYERS - 1; pt.L[j].k = k; pt.L[j].mesh.material = skinMat(k, 'm'); }
      else { addLayer(m, k); j = pt.L.length - 1; } }
    return j;
  }
  // small helpers for weathering: smooth 3D noise so dirt / rust look blotchy, and how close each point is to a hard edge
  const hash3 = (x, y, z) => { const h = Math.sin(x * 127.1 + y * 311.7 + z * 74.7) * 43758.5453; return h - Math.floor(h); };
  function noise3(x, y, z) { const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z), sm = t => t * t * (3 - 2 * t), u = sm(x - xi), v = sm(y - yi), w = sm(z - zi), L = (a, b, t) => a + (b - a) * t;
    return L(L(L(hash3(xi, yi, zi), hash3(xi + 1, yi, zi), u), L(hash3(xi, yi + 1, zi), hash3(xi + 1, yi + 1, zi), u), v), L(L(hash3(xi, yi, zi + 1), hash3(xi + 1, yi, zi + 1), u), L(hash3(xi, yi + 1, zi + 1), hash3(xi + 1, yi + 1, zi + 1), u), v), w); }
  const smooth = (a, b, x) => { const t = Math.max(0, Math.min(1, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
  function edgeOf(m) {
    const pt = m.userData.pt; if (pt.edge) return pt.edge;
    const P = m.geometry.attributes.position.array, n = P.length / 3, e = new Float32Array(n), src = new T.EdgesGeometry(m.userData.geo0 || m.geometry, 28).attributes.position.array, ne = src.length / 6;
    if (!m.geometry.boundingSphere) m.geometry.computeBoundingSphere();
    const wd = m.geometry.boundingSphere.radius * .1;
    for (let i = 0; i < n; i++) { const x = P[i * 3], y = P[i * 3 + 1], z = P[i * 3 + 2]; let best = 1e9;
      for (let k = 0; k < ne; k++) { const ax = src[k * 6], ay = src[k * 6 + 1], az = src[k * 6 + 2], bx = src[k * 6 + 3] - ax, by = src[k * 6 + 4] - ay, bz = src[k * 6 + 5] - az;
        let t = ((x - ax) * bx + (y - ay) * by + (z - az) * bz) / (bx * bx + by * by + bz * bz || 1e-9); t = t < 0 ? 0 : t > 1 ? 1 : t;
        const qx = ax + bx * t - x, qy = ay + by * t - y, qz = az + bz * t - z, d = qx * qx + qy * qy + qz * qz; if (d < best) best = d; }
      const d = Math.sqrt(best); e[i] = d >= wd ? 0 : 1 - d / wd; }
    return (pt.edge = e);
  }
  let wearKind = 'edge'; const WEAR = { edge: ['#c9cdd4', '#8d9199'], dirt: ['#3d2e20', '#1f1912'], rust: ['#a04a16', '#4d2610'], scorch: ['#0d0c0b', '#1c1814'] };
  // one dab of paint at a world point; how = 'color' | 'spray' | 'erase' | 'blotch' | 'blend' | 'wear'
  function dab(p, how, stamp) {
    const r = radius(), s = power();
    if (how === 'blend') return blendAt(p, r, s);
    const lin = new T.Color(col.hex || '#ff3030'), wear = how === 'wear' ? wearKind : null, wa = wear && new T.Color(WEAR[wear][0]), wb = wear && new T.Color(WEAR[wear][1]);
    for (const m of near(p, r)) {
      prep(m); remember(m);
      const pt = m.userData.pt, w = worldPos(m), n = w.length / 3, wantSkin = withSkin && how !== 'erase' && !wear, edge = wear === 'edge' ? edgeOf(m) : null; let sj = -1;
      let changed = false;
      for (let i = 0; i < n; i++) {
        const dx = w[i * 3] - p.x, dy = w[i * 3 + 1] - p.y, dz = w[i * 3 + 2] - p.z; let d = Math.sqrt(dx * dx + dy * dy + dz * dz);
        let rr = r;
        if (stamp) { const a = Math.atan2(dy, dx + dz) ; rr = r * stamp.shape(a); if (d > rr) { d = stamp.drop(w[i * 3], w[i * 3 + 1], w[i * 3 + 2]); if (d < 0) continue; rr = 1; } }
        if (d >= rr) continue;
        let f = 1 - d / rr; f = f * f * (3 - 2 * f);
        if (how === 'spray') { const mist = +$('pbMist').value, chance = .75 - mist * .67, h = Math.sin(i * 12.9898 + performance.now() * .37) * 43758.5453; if (h - Math.floor(h) > chance) continue; f *= (.12 + mist * .7); }
        else if (how === 'blotch') f = Math.min(1, f * 3);
        let cr = lin.r, cg = lin.g, cb = lin.b;
        if (wear) { const X = w[i * 3], Y = w[i * 3 + 1], Z = w[i * 3 + 2];
          if (wear === 'edge') f *= edge[i] * (.5 + .7 * noise3(X * 9, Y * 9, Z * 9));
          else if (wear === 'dirt') f *= smooth(.35, .7, noise3(X * 3.2, Y * 3.2, Z * 3.2) * .65 + noise3(X * 11, Y * 11, Z * 11) * .35);
          else if (wear === 'rust') f *= smooth(.38, .66, noise3(X * 6, Y * 1.5, Z * 6));       // stretched up-down so it streaks
          else f = Math.pow(f, .6) * (.5 + .5 * noise3(X * 5, Y * 5, Z * 5));                  // scorch: darkest in the middle
          const t = noise3(X * 14 + 7, Y * 14, Z * 14); cr = wa.r + (wb.r - wa.r) * t; cg = wa.g + (wb.g - wa.g) * t; cb = wa.b + (wb.b - wa.b) * t; }
        f *= s; if (f <= .002) continue; changed = true;
        if (wantSkin && sj < 0) sj = layerFor(m, brushSkin);
        if (how === 'erase') { pt.pc[i * 4 + 3] *= 1 - f; pt.g[i] *= 1 - f; for (const L of pt.L) L.m[i] *= 1 - f; continue; }
        if (sj >= 0) { const L = pt.L[sj]; L.m[i] += (1 - L.m[i]) * f; for (let k = sj + 1; k < pt.L.length; k++) pt.L[k].m[i] *= 1 - f; }
        else { const a = pt.pc[i * 4 + 3], na = a + (1 - a) * f, wOld = a * (1 - f) / Math.max(na, 1e-5), wNew = 1 - wOld;
          pt.pc[i * 4] = pt.pc[i * 4] * wOld + cr * wNew; pt.pc[i * 4 + 1] = pt.pc[i * 4 + 1] * wOld + cg * wNew; pt.pc[i * 4 + 2] = pt.pc[i * 4 + 2] * wOld + cb * wNew; pt.pc[i * 4 + 3] = na;
          for (const L of pt.L) L.m[i] *= 1 - f; }
        pt.g[i] = glowPaint && !wear ? pt.g[i] + (1 - pt.g[i]) * f : pt.g[i] * (1 - f);
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
  // 🌈 Gradient: fades the whole tapped part from the main colour (top / outside / front) to the second colour
  function gradHolder(h) {
    h.updateWorldMatrix(true, true);
    const ms = meshesOf(h).filter(m => m.visible), A = new T.Color(col.hex), Bc = new T.Color($('pbCol2').value), ax = +$('pbGradDir').value;
    let lo = 1e9, hi = -1e9;
    const W = ms.map(m => { prep(m); remember(m); const w = worldPos(m); for (let i = ax; i < w.length; i += 3) { const v = ax === 0 ? Math.abs(w[i]) : w[i]; if (v < lo) lo = v; if (v > hi) hi = v; } return w; });
    ms.forEach((m, k) => { const pt = m.userData.pt, w = W[k];
      for (let i = 0; i < pt.g.length; i++) { let t = ((ax === 0 ? Math.abs(w[i * 3]) : w[i * 3 + ax]) - lo) / Math.max(1e-6, hi - lo); t = t * t * (3 - 2 * t);
        pt.pc[i * 4] = Bc.r + (A.r - Bc.r) * t; pt.pc[i * 4 + 1] = Bc.g + (A.g - Bc.g) * t; pt.pc[i * 4 + 2] = Bc.b + (A.b - Bc.b) * t; pt.pc[i * 4 + 3] = 1; pt.g[i] = glowPaint ? 1 : 0; }
      for (const L of pt.L) L.m.fill(0); flag(m); });
  }
  // 💧 Pick: tap the mech to grab the colour that's there
  let lastBrush = 'color';
  function pickColour(hit) {
    const m = hit.object, base = baseCol(m), c = new T.Color(base.r, base.g, base.b), pt = m.userData.pt;
    if (pt) { const w = worldPos(m); let bi = 0, bd = 1e9;
      for (let i = 0; i < w.length / 3; i++) { const d = (w[i * 3] - hit.point.x) ** 2 + (w[i * 3 + 1] - hit.point.y) ** 2 + (w[i * 3 + 2] - hit.point.z) ** 2; if (d < bd) { bd = d; bi = i; } }
      const a = pt.pc[bi * 4 + 3]; c.setRGB(base.r * (1 - a) + pt.pc[bi * 4] * a, base.g * (1 - a) + pt.pc[bi * 4 + 1] * a, base.b * (1 - a) + pt.pc[bi * 4 + 2] * a);
      for (const L of pt.L) c.lerp(skinColour(L.k), L.m[bi]); }
    setColour('#' + c.getHexString()); brush = lastBrush; syncBrushUI(); tip('Picked that colour');
  }
  function setColour(hex) { col.hex = hex; $('pbCol').value = hex; withSkin = false; syncBrushUI(); }
  function addSwatch(hex) { if (!hex || S.swatches[0] === hex) return; S.swatches = [hex, ...S.swatches.filter(x => x !== hex)].slice(0, 8); drawSwatches(); }
  function drawSwatches() {
    const box = $('pSwatches'); if (!box) return; box.innerHTML = '<small>Colours:</small>';
    const c = C.colours(), seen = new Set();
    for (const hex of [...['armor', 'armor2', 'accent', 'glow', 'frame'].map(k => c[k] && '#' + String(c[k]).replace('#', '')), '#ffffff', '#111111', ...S.swatches]) {
      if (!hex || seen.has(hex.toLowerCase())) continue; seen.add(hex.toLowerCase());
      const b = document.createElement('button'); b.className = 'sw'; b.style.background = hex; b.title = hex; b.setAttribute('aria-label', 'Colour ' + hex); b.onclick = () => setColour(hex); box.append(b); }
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
    if (stroke && stroke.size) { undoStack.push(stroke); if (undoStack.length > 25) undoStack.shift(); saveBrush(); showLayers();
      if (!withSkin && ['color', 'spray', 'blotch', 'fill', 'grad'].includes(brush)) addSwatch(col.hex); }
    stroke = null; down = null; lastPt = null; lastStampAt = null;
  }
  function wirePointer() {
    const el = C.renderer.domElement;
    el.addEventListener('pointerdown', e => { pointers++; if (!open) return;
      if (pointers > 1) { endStroke(); return; }
      down = { x: e.clientX, y: e.clientY, t: e.timeStamp };   // the event's own time, so a slow frame can't turn a quick tap into a long press
      if (!brush) return;
      if (brush === 'pick') { const hit = hitAt(e.clientX, e.clientY); if (hit) pickColour(hit); return; }
      if (brush === 'grad') { const hit = hitAt(e.clientX, e.clientY), h = hit && holderOf(hit.object); if (h) { stroke = new Map(); gradHolder(h);
        if (both) { const o = nearestPiece(mirrorP(hit.point)), h2 = o && holderOf(o); if (h2 && h2 !== h) gradHolder(h2); } endStroke(); } return; }
      if (brush === 'fill') { const hit = hitAt(e.clientX, e.clientY); if (hit) { stroke = new Map(); fillMesh(hit.object);
        if (both) { const o = nearestPiece(mirrorP(hit.point)); if (o && o !== hit.object) fillMesh(o); } endStroke(); } return; }
      stroke = new Map(); strokeTo(e.clientX, e.clientY); });
    el.addEventListener('pointermove', e => { if (!open) return; ringAt(brush ? e.clientX : null, e.clientY); if (stroke && pointers === 1) strokeTo(e.clientX, e.clientY); });
    const up = e => { pointers = Math.max(0, pointers - 1); if (!open) return;
      if (down && !brush && Math.hypot(e.clientX - down.x, e.clientY - down.y) < 10 && e.timeStamp - down.t < 500) { if (sec === 'decal' && decalKind) placeDecal(e.clientX, e.clientY); else tapAt(e.clientX, e.clientY); }
      if (stroke) endStroke(); down = null; if (e.pointerType !== 'mouse') ringAt(null); };
    el.addEventListener('pointerup', up); el.addEventListener('pointercancel', up);
    el.addEventListener('pointerleave', () => ringAt(null));
  }
  function undo() {
    const st = undoStack.pop(); if (!st) return tip('Nothing to undo');
    for (const [m, d] of st) { const pt = m.userData.pt; pt.pc.set(d.pc); pt.g.set(d.g);
      while (pt.L.length > d.L.length) { const L = pt.L.pop(); m.remove(L.mesh); }
      d.L.forEach((l, k) => { pt.L[k].k = l.k; pt.L[k].m.set(l.m); pt.L[k].mesh.material = skinMat(l.k, 'm'); }); flag(m); }
    saveBrush(); showLayers();
  }
  function saveBrush() {
    for (const [spot, h] of Object.entries(ALL())) {
      const ms = meshesOf(h), m = {}; let any = false;
      ms.forEach((x, i) => { const pt = x.userData.pt; if (!pt) return;
        if (!pt.pc.some((v, k) => k % 4 === 3 && v > .002) && !pt.L.some(L => L.m.some(v => v > .002)) && !pt.g.some(v => v > .002)) return;
        m[i] = { pc: pack(pt.pc, 4), g: pack(pt.g, 1), L: pt.L.map(L => ({ k: L.k, m: pack(L.m, 1) })) }; any = true; });
      if (any) B[spot] = { id: pid(h), m }; else delete B[spot];
    }
    store();
  }
  function clearPaint(spots) {
    stroke = new Map();
    for (const s of spots) { const h = ALL()[s]; if (!h) continue; for (const m of meshesOf(h)) { const pt = m.userData.pt; if (!pt) continue; remember(m);
      pt.pc.fill(0); pt.g.fill(0); for (const L of pt.L) L.m.fill(0); flag(m); } }
    endStroke();
  }

  // ---------- picking parts: tap one, or mark several ----------
  let tapped = null, marking = false; const marks = new Set(); const boxes = new Map();
  function boxFor(spot, colr) { let b = boxes.get(spot); const h = ALL()[spot]; if (!h) return;
    if (!b) { b = new T.BoxHelper(h, colr); b.material.depthTest = false; b.renderOrder = 9; b.userData.ui = true; b.material.userData.outlineParameters = { visible: false }; C.scene.add(b); boxes.set(spot, b); }
    b.material.color.set(colr); b.setFromObject(h); }
  function refreshBoxes() {
    for (const [s, b] of boxes) { const want = open && (marks.has(s) || s === tapped); if (!want || !ALL()[s]) { C.scene.remove(b); boxes.delete(s); } }
    if (!open) return;
    for (const s of marks) if (ALL()[s]) boxFor(s, 0x38e8ff);
    if (tapped && ALL()[tapped] && !marks.has(tapped)) boxFor(tapped, 0xffc040);
  }
  function tapAt(x, y) {
    const hit = hitAt(x, y), h = hit && holderOf(hit.object), s = pspot(h);
    if (marking) { if (!s) return; marks.has(s) ? marks.delete(s) : marks.add(s); refreshBoxes(); showMarks(); return; }
    tapped = s || null; refreshBoxes(); numbers(); showLayers();
    if (s) { $('pTarget').value = 'part'; tip(nice(s) + ' picked: skins and Fill now go on it.'); }
  }
  const nice = s => /^frame:/.test(s) ? 'frame ' + s.slice(6).replace(/\.L$/, ' (left)').replace(/\.R$/, ' (right)') : /^cap:/.test(s) ? 'joint ' + s.slice(4).replace(/\.L$/, ' (left)').replace(/\.R$/, ' (right)') : /^det:/.test(s) ? 'detail' : s.replace(/\.L$/, ' (left)').replace(/\.R$/, ' (right)').replace('back', 'backpack').replace('weapon', 'hand weapon').replace('mount', 'shoulder weapon').replace('_', ' ');
  function showMarks() { $('pMarkInfo').textContent = marks.size ? marks.size + ' marked: ' + [...marks].map(nice).join(', ') : 'Nothing marked.'; }
  // paint by number: numbers on each piece of the tapped part; tap a number to fill that piece
  function numbers() {
    const box = $('pNums'); box.innerHTML = '';
    if (!open || !tapped || !ALL()[tapped] || !$('pNumBtn').classList.contains('on')) return;
    meshesOf(ALL()[tapped]).forEach((m, i) => { const b = document.createElement('button'); b.textContent = i + 1; b.className = 'pnum'; b.setAttribute('aria-label', 'Fill piece ' + (i + 1));
      b.onclick = () => { stroke = new Map(); fillMesh(m); endStroke(); }; b._m = m; box.append(b); });
  }
  function placeNumbers() {
    for (const b of $('pNums').children) { const m = b._m; if (!m.geometry.boundingSphere) m.geometry.computeBoundingSphere();
      const v = m.geometry.boundingSphere.center.clone().applyMatrix4(m.matrixWorld).project(C.camera);
      b.style.left = (v.x + 1) / 2 * innerWidth - 15 + 'px'; b.style.top = (1 - v.y) / 2 * innerHeight - 15 + 'px'; b.style.display = v.z < 1 ? 'block' : 'none'; }
  }

  // ---------- layer list: what's brushed on the picked part; remove a layer or bring a brushed skin to the top ----------
  function showLayers() {
    const box = $('pLayers'); if (!box) return; box.innerHTML = '';
    const h = tapped && ALL()[tapped]; if (!h) { box.textContent = 'Tap a part (brush off) to see its paint layers.'; return; }
    const keys = []; let hasCol = false, hasGlow = false;
    for (const m of meshesOf(h)) { const pt = m.userData.pt; if (!pt) continue;
      if (!hasCol) hasCol = pt.pc.some((v, k) => k % 4 === 3 && v > .02); if (!hasGlow) hasGlow = pt.g.some(v => v > .02);
      for (const L of pt.L) if (!keys.includes(L.k) && L.m.some(v => v > .02)) keys.push(L.k); }
    const row = (label, onDel, onTop) => { const d = document.createElement('span'); d.className = 'plyr'; d.append(label + ' ');
      if (onTop) { const t = document.createElement('button'); t.textContent = '⬆ Top'; t.setAttribute('aria-label', 'Bring ' + label + ' to the top'); t.onclick = onTop; d.append(t); }
      const x = document.createElement('button'); x.textContent = '✖'; x.setAttribute('aria-label', 'Remove ' + label); x.onclick = onDel; d.append(x); box.append(d); };
    [...keys].reverse().forEach((k, i) => row('🧴 ' + nameOf(k), () => editLayers(h, k, 'del'), i ? () => editLayers(h, k, 'top') : null));
    if (hasCol) row('🎨 Colour paint', () => editLayers(h, null, 'col'));
    if (hasGlow) row('✦ Glow', () => editLayers(h, null, 'glow'));
    if (!keys.length && !hasCol && !hasGlow) box.textContent = nice(tapped) + ': no brush paint yet.';
  }
  function editLayers(h, k, what) {
    stroke = new Map();
    for (const m of meshesOf(h)) { const pt = m.userData.pt; if (!pt) continue; remember(m);
      if (what === 'col') { for (let i = 3; i < pt.pc.length; i += 4) pt.pc[i] = 0; }
      else if (what === 'glow') pt.g.fill(0);
      else { const j = pt.L.findIndex(L => L.k === k); if (j < 0) continue;
        if (what === 'del') pt.L[j].m.fill(0);
        else { const top = pt.L.length - 1, kj = pt.L[j].k, mj = pt.L[j].m.slice();     // slide the ones above it down, put it on top
          for (let i = j; i < top; i++) { pt.L[i].k = pt.L[i + 1].k; pt.L[i].m.set(pt.L[i + 1].m); pt.L[i].mesh.material = skinMat(pt.L[i].k, 'm'); }
          pt.L[top].k = kj; pt.L[top].m.set(mj); pt.L[top].mesh.material = skinMat(kj, 'm'); } }
      flag(m); }
    endStroke(); showLayers();
  }

  // ---------- decals: numbers, hazard stripes and emblems, projected onto the surface (three.js DecalGeometry, MIT) ----------
  const DECALS = { num: '🔢 Text', hazard: '⚠ Hazard stripes', stripe: '▬ Stripe', star: '★ Star', chevron: '︽ Chevrons', arrow: '⬆ Arrow', warn: '△ Warning', ring: '◎ Roundel', bolt: '⚡ Bolt', cross: '✚ Cross' };
  let decalKind = null, lastDecals = []; const decalTex = {}, decalMats = {}, dBits = new Map();
  function decalImage(d) {
    const key = d.kind + '|' + (d.kind === 'num' ? d.text : '') + '|' + d.col; if (decalTex[key]) return decalTex[key];
    const cv = document.createElement('canvas'), FONT = 'bold 200px Impact, "Arial Black", "Helvetica Neue", sans-serif'; let W = 256; const H = 256;
    if (d.kind === 'num') { const x0 = cv.getContext('2d'); x0.font = FONT; W = Math.max(128, Math.min(1024, Math.ceil(x0.measureText(d.text || '01').width) + 40)); }
    if (d.kind === 'hazard') W = 768; if (d.kind === 'stripe') W = 1024;
    cv.width = W; cv.height = H; const x = cv.getContext('2d'); x.fillStyle = x.strokeStyle = d.col; x.lineJoin = 'round';
    const poly = pts => { x.beginPath(); pts.forEach(([a, b], i) => i ? x.lineTo(a, b) : x.moveTo(a, b)); x.closePath(); x.fill(); };
    if (d.kind === 'num') { x.font = FONT; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText(d.text || '01', W / 2, H / 2 + 8); }
    else if (d.kind === 'hazard') { x.save(); x.beginPath(); x.rect(0, 40, W, 176); x.clip(); x.fillStyle = '#f2c200'; x.fillRect(0, 0, W, H); x.fillStyle = '#141414';
      for (let k = -2; k < 10; k++) poly([[k * 96, 216], [k * 96 + 48, 216], [k * 96 + 136, 40], [k * 96 + 88, 40]]); x.restore(); }
    else if (d.kind === 'stripe') x.fillRect(0, 88, W, 80);
    else if (d.kind === 'star') { const p = []; for (let k = 0; k < 10; k++) { const a = -Math.PI / 2 + k * Math.PI / 5, r = k % 2 ? 48 : 118; p.push([128 + Math.cos(a) * r, 134 + Math.sin(a) * r]); } poly(p); }
    else if (d.kind === 'chevron') for (const y of [40, 116]) poly([[28, y + 64], [128, y], [228, y + 64], [228, y + 104], [128, y + 40], [28, y + 104]]);
    else if (d.kind === 'arrow') poly([[128, 14], [232, 130], [166, 130], [166, 242], [90, 242], [90, 130], [24, 130]]);
    else if (d.kind === 'warn') { x.fillStyle = '#141414'; poly([[128, 10], [250, 238], [6, 238]]); x.fillStyle = '#f2c200'; poly([[128, 50], [216, 218], [40, 218]]); x.fillStyle = '#141414'; x.fillRect(116, 104, 24, 62); x.fillRect(116, 178, 24, 22); }
    else if (d.kind === 'ring') { x.lineWidth = 34; x.beginPath(); x.arc(128, 128, 98, 0, 7); x.stroke(); x.beginPath(); x.arc(128, 128, 40, 0, 7); x.fill(); }
    else if (d.kind === 'bolt') poly([[150, 10], [58, 142], [118, 142], [92, 246], [200, 104], [138, 104]]);
    else if (d.kind === 'cross') { x.fillRect(96, 24, 64, 208); x.fillRect(24, 96, 208, 64); }
    const tex = new T.CanvasTexture(cv); tex.colorSpace = T.SRGBColorSpace; tex.anisotropy = 4;
    const m = C.toon(0xffffff); m.map = tex; m.transparent = true; m.alphaTest = .08; m.depthWrite = false; m.polygonOffset = true; m.polygonOffsetFactor = -4; m.polygonOffsetUnits = -4;
    m.userData.outlineParameters = { visible: false };
    return (decalTex[key] = { mat: m, aspect: W / H });
  }
  function killDecal(d) { for (const b of dBits.get(d.id) || []) { b.parent && b.parent.remove(b); b.geometry.dispose(); } dBits.delete(d.id); }
  function buildDecal(d) {       // (re)makes one decal's 3D pieces on its part; they ride on the part's own pieces so they move and stretch with it
    killDecal(d);
    const h = ALL()[d.spot]; if (!h) return;
    const ms = meshesOf(h), anchor = ms[d.mi]; if (!anchor) return;
    h.updateWorldMatrix(true, true);
    const p = new T.Vector3().fromArray(d.p).applyMatrix4(anchor.matrixWorld), n = new T.Vector3().fromArray(d.n).transformDirection(anchor.matrixWorld);
    const o = new T.Object3D(); o.position.copy(p); o.lookAt(p.clone().add(n)); o.rotateZ(d.turn * Math.PI / 180);
    const im = decalImage(d), size = new T.Vector3(d.size * im.aspect, d.size, Math.max(d.size * .8, .25)), bits = [];
    for (const m of ms) { if (!m.visible) continue; const g0 = m.geometry; if (!g0.boundingSphere) g0.computeBoundingSphere();
      const c = g0.boundingSphere.center.clone().applyMatrix4(m.matrixWorld), rr = g0.boundingSphere.radius * m.matrixWorld.getMaxScaleOnAxis();
      if (c.distanceTo(p) > rr + size.length() * .5) continue;
      let g; try { g = new C.Decal(m, p, o.rotation, size); } catch (e) { continue; }
      if (!g.attributes.position || !g.attributes.position.count) continue;
      g.applyMatrix4(m.matrixWorld.clone().invert());
      const dm = new T.Mesh(g, im.mat); dm.userData.overlay = true; dm.renderOrder = 8; dm.raycast = () => {}; m.add(dm); bits.push(dm); }
    dBits.set(d.id, bits);
  }
  function placeDecal(x, y) {
    const hit = hitAt(x, y); if (!hit) return tip('Tap on the mech to stick the decal on');
    lastDecals = [];
    const add = (m, pW, nW, flip) => { const h = holderOf(m); if (!h) return; const inv = m.matrixWorld.clone().invert();
      const d = { id: Math.random().toString(36).slice(2, 9), spot: pspot(h), pid: pid(h), mi: meshesOf(h).indexOf(m), p: pW.clone().applyMatrix4(inv).toArray(), n: nW.clone().transformDirection(inv).toArray(),
        kind: decalKind, text: ($('pdText').value || '01').slice(0, 8), col: $('pdCol').value, size: +$('pdSize').value, turn: +$('pdTurn').value * (flip ? -1 : 1), flip: !!flip };
      S.decals.push(d); buildDecal(d); lastDecals.push(d.id); };
    const nW = hit.face.normal.clone().transformDirection(hit.object.matrixWorld);
    add(hit.object, hit.point, nW, false);
    if (both) { const mp = mirrorP(hit.point), o = nearestPiece(mp); if (o) add(o, mp, new T.Vector3(-nW.x, nW.y, nW.z), true); }
    store(); decalInfo(); tip('Stuck on. Size and Turn still change this one.');
  }
  function decalInfo() { const el = $('pdInfo'); if (el) el.textContent = S.decals.length ? S.decals.length + ' decal' + (S.decals.length > 1 ? 's' : '') + ' on the mech' : 'No decals yet.'; }
  function dropDecals(test) { S.decals = S.decals.filter(d => { if (!test(d)) return true; killDecal(d); return false; }); store(); decalInfo(); }

  // ---------- element bits: small rocks / crystals / flames grown on a part that has an element (the old forge's "grow element bits") ----------
  const BITS = { Lava: ['rock', 14, .1, 'lavarock'], Fire: ['flame', 12, .12, 'fire'], Stone: ['rock', 14, .11, 'stone'], Crystal: ['crystal', 12, .12, 'crystal'], Forest: ['mound', 16, .1, 'mossy'],
    Water: ['drop', 14, .07, 'ocean'], Ice: ['crystal', 14, .12, 'ice'], Storm: ['puff', 10, .11, 'stormcloud'], Lightning: ['shard', 12, .1, 'lightning'], Cosmic: ['star', 12, .07, 'galaxy'],
    Gold: ['rock', 10, .08, 'gold'], Sand: ['mound', 12, .12, 'sand'], Void: ['shard', 12, .11, 'void'] };
  const bitGeo = {};
  function bitShape(kind) {       // each shape sits on the surface and points up (+Y)
    if (bitGeo[kind]) return bitGeo[kind]; let g;
    if (kind === 'rock') { g = new T.IcosahedronGeometry(1, 0); g.scale(1, .7, 1); g.translate(0, .3, 0); }
    else if (kind === 'mound') { g = new T.IcosahedronGeometry(1, 1); g.scale(1.2, .45, 1.2); g.translate(0, .1, 0); }
    else if (kind === 'crystal') { g = new T.ConeGeometry(.45, 2.2, 5); g.translate(0, .95, 0); }
    else if (kind === 'shard') { g = new T.ConeGeometry(.28, 2.6, 4); g.translate(0, 1.15, 0); }
    else if (kind === 'flame') { g = new T.ConeGeometry(.5, 1.8, 6); g.translate(0, .8, 0); }
    else if (kind === 'drop') { g = new T.SphereGeometry(.7, 8, 6); g.scale(1, .6, 1); g.translate(0, .2, 0); }
    else if (kind === 'puff') { g = new T.IcosahedronGeometry(1, 1); g.translate(0, .5, 0); }
    else { g = new T.OctahedronGeometry(1, 0); }
    return (bitGeo[kind] = g);
  }
  function seeded(str) { let a = 2166136261; for (let i = 0; i < str.length; i++) a = Math.imul(a ^ str.charCodeAt(i), 16777619);
    return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
  function growBits(h, spot) {
    const p = spot && S.skins.part[spot], want = p && p.el && p.bits !== false && BITS[p.el] ? p.el : null;
    if ((h.userData.bitsEl || null) === want) return;
    for (const b of h.userData.bits || []) b.parent && b.parent.remove(b);
    h.userData.bits = []; h.userData.bitsEl = want; if (!want) return;
    const [kind, count, size, skin] = BITS[want], rnd = seeded(spot + want), geo = bitShape(kind), mat = skinMat(skin, '');
    const ms = meshesOf(h).filter(m => m.visible && m.userData.key !== 'glow' && m.userData.key !== 'eye'), tris = []; let total = 0, R0 = 0;
    const a = new T.Vector3(), b = new T.Vector3(), c = new T.Vector3(), up = new T.Vector3(0, 1, 0);
    for (const m of ms) { const g = m.userData.geo0 || m.geometry, P = g.attributes.position, ix = g.index, nt = Math.floor((ix ? ix.count : P.count) / 3), step = Math.max(1, Math.floor(nt / 400));
      if (!g.boundingSphere) g.computeBoundingSphere(); R0 = Math.max(R0, g.boundingSphere.radius);
      for (let t = 0; t < nt; t += step) { const i0 = ix ? ix.getX(t * 3) : t * 3, i1 = ix ? ix.getX(t * 3 + 1) : t * 3 + 1, i2 = ix ? ix.getX(t * 3 + 2) : t * 3 + 2;
        a.fromBufferAttribute(P, i0); b.fromBufferAttribute(P, i1); c.fromBufferAttribute(P, i2);
        const ar = b.clone().sub(a).cross(c.clone().sub(a)).length() * .5 * step; if (!(ar > 0)) continue; total += ar; tris.push([m, P, i0, i1, i2, total]); } }
    if (!tris.length) return;
    for (let k = 0; k < count; k++) { const r = rnd() * total, [m, P, i0, i1, i2] = tris.find(t => t[5] >= r) || tris[tris.length - 1];
      a.fromBufferAttribute(P, i0); b.fromBufferAttribute(P, i1); c.fromBufferAttribute(P, i2);
      let u = rnd(), v = rnd(); if (u + v > 1) { u = 1 - u; v = 1 - v; }
      const e1 = b.clone().sub(a), e2 = c.clone().sub(a), pos = a.clone().addScaledVector(e1, u).addScaledVector(e2, v), nrm = e1.clone().cross(e2).normalize();
      const bit = new T.Mesh(geo, mat), s = R0 * size * (.6 + rnd() * .8);
      const tilt = new T.Vector3(nrm.x + (rnd() - .5) * .5, nrm.y + (rnd() - .5) * .5, nrm.z + (rnd() - .5) * .5).normalize();
      bit.position.copy(pos); if (kind === 'star') bit.position.addScaledVector(nrm, s * 1.8);
      bit.quaternion.setFromUnitVectors(up, tilt).multiply(new T.Quaternion().setFromAxisAngle(up, rnd() * 6.28));
      bit.scale.set(s, s * (.8 + rnd() * .6), s);
      bit.userData.ui = true; bit.userData.bit = true; bit.raycast = () => {}; m.add(bit); h.userData.bits.push(bit); }
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
    else { if (!sp.length) return; for (const s of sp) { const p = S.skins.part[s] || (S.skins.part[s] = {}); if (k) { p.all = k; p.keepGlow = true; } else { delete p.all; delete p.glowCol; delete p.el; } if (!Object.keys(p).length || (!p.all && !p.glowCol)) delete S.skins.part[s]; } }
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
    for (const s of sp) { const p = S.skins.part[s] = S.skins.part[s] || {}; p.all = k; p.keepGlow = true; p.el = name; p.bits = S.bitsOn; if (glowHex) p.glowCol = glowHex; else delete p.glowCol; }
    redressAll(); store();
  }

  // ---------- light: brightness, glow strength, night preview ----------
  let night = false, base = null;
  function light(redress = true) {
    if (!base) base = { hemi: C.lights.hemi.intensity, sun: C.lights.sun.intensity, rim: C.lights.rim.intensity, bg: C.scene.background.clone() };
    const k = S.bright * (night ? .22 : 1);
    C.lights.hemi.intensity = base.hemi * k; C.lights.sun.intensity = base.sun * k; C.lights.rim.intensity = base.rim * (night ? .6 : 1) * S.bright;
    if (C.scene.background && C.scene.background.isColor) C.scene.background.copy(night ? new T.Color(0x05060a) : base.bg);   // a photo backdrop stays as it is
    glowK.value = S.glow * (night ? 2.2 : 1);
    if (redress) redressAll();
  }

  // ---------- the panel ----------
  function tip(t) { const el = $('pTip'); if (el) { el.textContent = t; el.style.opacity = 1; clearTimeout(tip.t); tip.t = setTimeout(() => el.style.opacity = .65, 2500); } }
  function syncBrushUI() {
    document.querySelectorAll('[data-pb]').forEach(b => b.classList.toggle('on', (b.dataset.pb || '') === (brush || '')));
    $('pWith').textContent = withSkin ? '🧴 Paints with skin: ' + nameOf(brushSkin) : '🎨 Paints with colour';
    const inB = sec === 'brush';
    $('pBrushRow').style.display = inB && brush ? 'flex' : 'none'; $('pMistRow').style.display = inB && brush === 'spray' ? 'flex' : 'none';
    $('pWithRow').style.display = inB && ['color', 'spray', 'blotch', 'fill'].includes(brush) ? 'flex' : 'none';
    $('pGradRow').style.display = inB && brush === 'grad' ? 'flex' : 'none'; $('pWearRow').style.display = inB && brush === 'wear' ? 'flex' : 'none';
    $('pSwatches').style.display = inB && brush && !['erase', 'blend', 'wear'].includes(brush) ? 'flex' : 'none';
    document.querySelectorAll('[data-wear]').forEach(b => b.classList.toggle('on', b.dataset.wear === wearKind));
    C.controls.enableRotate = !brush;
    MF_PAINT.frozen = !!brush;
    $('pHint').textContent = brush ? (brush === 'fill' ? 'Tap a piece to fill it. Two fingers move the camera.' : brush === 'grad' ? 'Tap a part: it fades from your colour to the second colour.'
      : brush === 'pick' ? 'Tap the mech to grab the colour that is there.' : brush === 'wear' ? 'Drag to weather it: worn edges, dirt, rust streaks or scorch marks.' : 'Drag on the mech to paint. Two fingers move the camera.')
      : 'Pick a brush, then drag on the mech. Brush off: tap a part to pick it.';
  }
  function buildUI() {
    const groups = [...new Set(MATS().LIST.map(e => e[2]))];
    const panel = $('paint');
    panel.insertAdjacentHTML('afterbegin', `<div class="line" id="pTabs"><button data-pt="brush" class="on">🖌 Brushes</button><button data-pt="skin">🧴 Skins</button><button data-pt="mark">🔖 Mark</button><button data-pt="decal">🔢 Decals</button><button data-pt="more">💡 Light +</button></div>
      <p class="hint" id="pTip" style="opacity:.65;color:#ffd27a;min-height:1em"></p>`);
    panel.querySelectorAll(':scope > .line:not(#pTabs)').forEach(el => el.dataset.sec = 'skin');   // the colour scheme rows live under Skins
    panel.insertAdjacentHTML('beforeend', `
      <p class="hint" id="pHint" data-sec="brush"></p>
      <div class="line" data-sec="brush"><button data-pb="">👆 Off</button><button data-pb="color">🖌 Color</button><button data-pb="spray">🥫 Spray</button><button data-pb="blotch">🩸 Blotch</button><button data-pb="fill">🪣 Fill</button><button data-pb="grad">🌈 Gradient</button><button data-pb="blend">🌫 Blend</button><button data-pb="wear">🪙 Wear</button><button data-pb="erase">🧽 Eraser</button><button data-pb="pick">💧 Pick colour</button></div>
      <div class="line" data-sec="brush" id="pBrushRow"><input type="color" id="pbCol" aria-label="Brush colour" value="#ff3030"><span>Size</span><input type="range" id="pbSize" aria-label="Brush size" min=".08" max="2" step=".02" value=".45"><span>Strength</span><input type="range" id="pbPower" aria-label="Brush strength" min=".05" max="1" step=".05" value=".8"></div>
      <div class="line" data-sec="brush" id="pSwatches"></div>
      <div class="line" data-sec="brush" id="pGradRow"><span>Fades to</span><input type="color" id="pbCol2" aria-label="Second colour the gradient fades to" value="#1a2a6a"><select id="pbGradDir"><option value="1">Top to bottom</option><option value="0">Outside to middle</option><option value="2">Front to back</option></select></div>
      <div class="line" data-sec="brush" id="pWearRow"><button data-wear="edge">Worn edges</button><button data-wear="dirt">Dirt</button><button data-wear="rust">Rust</button><button data-wear="scorch">Scorch</button></div>
      <div class="line" data-sec="brush" id="pMistRow"><span>Mist</span><small>fine</small><input type="range" id="pbMist" aria-label="Spray mist, fine to speckles" min="0" max="1" step=".05" value=".25"><small>speckles</small></div>
      <div class="line" data-sec="brush" id="pWithRow"><button id="pWith"></button><button id="pGlowP">✦ Glow paint</button></div>
      <div class="line" data-sec="brush"><button id="pBoth">🪞 Both sides</button><button id="pUndo">↶ Undo</button><button id="pClearPart">Clear picked</button><button id="pClearAll">Clear all paint</button></div>
      <div class="line" data-sec="skin"><span>Put on:</span><select id="pTarget">${SLOTS.map(([k, n]) => `<option value="${k}">Whole mech: ${n}</option>`).join('')}<option value="part">Picked part</option><option value="marked">Marked parts</option></select></div>
      <div class="line" data-sec="skin"><select id="pGroup">${groups.map(g => `<option>${g}</option>`).join('')}</select><span>Pattern</span><input type="range" id="pTile" aria-label="Skin pattern size" min=".3" max="3" step=".1" value="1"><button id="pClearSkins">Clear skins</button></div>
      <div class="line" data-sec="skin" id="pSkins"></div>
      <div class="line" data-sec="mark"><button id="pMark">🔖 Mark parts</button><button id="pMarkClear">Clear marks</button><button id="pFillMarked">🪣 Fill marked</button></div>
      <div class="line" data-sec="mark"><small id="pMarkInfo">Nothing marked.</small></div>
      <div class="line" data-sec="mark"><input id="pGroupName" aria-label="Group name" placeholder="Group name" style="font:inherit;min-height:36px;border-radius:8px;background:#2c2c30;color:#eee;border:1px solid #4a4a4e;padding:0 8px;width:130px"><button id="pGroupSave">Save group</button><select id="pGroups"></select><button id="pGroupDel">Delete</button></div>
      <div class="line" data-sec="mark"><button id="pNumBtn">🔢 Paint by number (picked part)</button></div>
      <div class="line" data-sec="mark"><small>Layers:</small></div>
      <div class="line" data-sec="mark" id="pLayers" style="flex-wrap:wrap"></div>
      <div class="line" data-sec="decal" id="pdKinds">${Object.entries(DECALS).map(([k, n]) => `<button data-dk="${k}">${n}</button>`).join('')}</div>
      <div class="line" data-sec="decal"><input id="pdText" aria-label="Decal text" value="01" maxlength="8" placeholder="Text" style="font:inherit;min-height:36px;border-radius:8px;background:#2c2c30;color:#eee;border:1px solid #4a4a4e;padding:0 8px;width:84px"><input type="color" id="pdCol" aria-label="Decal colour" value="#ffffff"><span>Size</span><input type="range" id="pdSize" aria-label="Decal size" min=".15" max="2.5" step=".05" value=".6"><span>Turn</span><input type="range" id="pdTurn" aria-label="Decal turn" min="-180" max="180" step="5" value="0"></div>
      <div class="line" data-sec="decal"><button id="pdBoth">🪞 Both sides</button><button id="pdUndo">↶ Remove last</button><button id="pdClearPart">Clear picked part</button><button id="pdClearAll">Clear all decals</button></div>
      <div class="line" data-sec="decal"><small id="pdInfo"></small></div>
      <div class="line" data-sec="more"><span>Element:</span><select id="pElem"><option value="">On picked / marked part...</option>${Object.keys(ELEMENTS).map(k => `<option>${k}</option>`).join('')}</select><button id="pBits">🪨 Grow bits</button></div>
      <div class="line" data-sec="more"><span>Brightness</span><input type="range" id="pBright" aria-label="Brightness" min=".4" max="1.2" step=".05"></div>
      <div class="line" data-sec="more"><span>Glow</span><input type="range" id="pGlow" aria-label="Glow strength" min="0" max="3" step=".1"><button id="pNight">🌙 Night preview</button></div>`);
    const showSec = k => { panel.querySelectorAll('[data-sec]').forEach(el => el.hidden = el.dataset.sec !== k); panel.querySelectorAll('[data-pt]').forEach(b => b.classList.toggle('on', b.dataset.pt === k)); sec = k;
      if (k === 'decal') { brush = null; marking = false; $('pMark').classList.remove('on'); tip(decalKind ? 'Tap the mech to stick it on.' : 'Pick a decal, then tap the mech.'); } if (k === 'mark') showLayers(); syncBrushUI(); };
    panel.querySelectorAll('[data-pt]').forEach(b => b.onclick = () => showSec(b.dataset.pt));
    document.body.insertAdjacentHTML('beforeend', '<div id="pRing"></div><div id="pNums"></div>');
    document.querySelectorAll('[data-pb]').forEach(b => b.onclick = () => { if (b.dataset.pb === 'pick' && brush && brush !== 'pick') lastBrush = brush; brush = b.dataset.pb || null; if (brush === 'erase' || brush === 'blend') withSkin = false; marking = false; $('pMark').classList.remove('on'); syncBrushUI(); });
    $('pbCol').oninput = e => { col.hex = e.target.value; withSkin = false; syncBrushUI(); };
    document.querySelectorAll('[data-wear]').forEach(b => b.onclick = () => { wearKind = b.dataset.wear; syncBrushUI(); });
    document.querySelectorAll('[data-dk]').forEach(b => b.onclick = () => { decalKind = decalKind === b.dataset.dk ? null : b.dataset.dk;
      document.querySelectorAll('[data-dk]').forEach(x => x.classList.toggle('on', x.dataset.dk === decalKind)); tip(decalKind ? 'Tap the mech to stick it on.' : 'Pick a decal, then tap the mech.'); });
    const live = () => { for (const d of S.decals) if (lastDecals.includes(d.id)) { d.size = +$('pdSize').value; d.turn = +$('pdTurn').value * (d.flip ? -1 : 1); buildDecal(d); } };
    $('pdSize').oninput = live; $('pdTurn').oninput = live; $('pdSize').onchange = $('pdTurn').onchange = () => { live(); store(); };
    $('pdBoth').onclick = e => { both = !both; e.target.classList.toggle('on', both); $('pBoth').classList.toggle('on', both); };
    $('pdUndo').onclick = () => { const d = S.decals[S.decals.length - 1]; if (!d) return tip('No decals to remove'); dropDecals(x => x === d); };
    $('pdClearPart').onclick = () => tapped ? dropDecals(d => d.spot === tapped) : tip('Open another tab, tap a part to pick it, then come back');
    $('pdClearAll').onclick = () => dropDecals(() => true);
    decalInfo();
    $('pBits').classList.toggle('on', S.bitsOn);
    $('pBits').onclick = e => { S.bitsOn = !S.bitsOn; e.target.classList.toggle('on', S.bitsOn); for (const p of Object.values(S.skins.part)) if (p.el) p.bits = S.bitsOn; redressAll(); store(); };
    $('pWith').onclick = () => { withSkin = !withSkin; syncBrushUI(); if (withSkin) tip('Open 🧴 Skins and tap the skin the brush should paint with.'); };
    $('pGlowP').onclick = e => { glowPaint = !glowPaint; e.target.classList.toggle('on', glowPaint); };
    $('pBoth').onclick = e => { both = !both; e.target.classList.toggle('on', both); $('pdBoth').classList.toggle('on', both); };
    $('pUndo').onclick = undo;
    $('pClearPart').onclick = () => tapped ? clearPaint([tapped]) : tip('Tap a part first');
    $('pClearAll').onclick = () => clearPaint(Object.keys(ALL()));
    $('pGroup').onchange = showSkins;
    $('pTile').value = S.tile; $('pTile').onchange = e => { S.tile = +e.target.value; for (const h of Object.values(ALL())) h.userData.bitsEl = undefined; redressAll(); store(); };
    $('pClearSkins').onclick = () => { S.skins = { slot: {}, part: {} }; redressAll(); store(); };
    $('pMark').onclick = e => { marking = !marking; e.target.classList.toggle('on', marking); if (marking) { brush = null; syncBrushUI(); tip('Tap parts to mark them (tap again to unmark).'); } refreshBoxes(); };
    $('pMarkClear').onclick = () => { marks.clear(); refreshBoxes(); showMarks(); };
    $('pFillMarked').onclick = () => { if (!marks.size) return tip('Mark some parts first'); stroke = new Map(); for (const s of marks) if (ALL()[s]) meshesOf(ALL()[s]).forEach(fillMesh); endStroke(); };
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
    $('pGroup').value = 'Metal'; showSkins(); drawSwatches(); showSec('brush');
  }

  window.MF_PAINT = {
    frozen: false,
    _all: () => ALL(),
    init(ctx) {
      C = ctx; T = ctx.THREE;
      let d = null; try { d = JSON.parse(localStorage.getItem('mf-paint2')); } catch (e) {}
      S = Object.assign(blank(), d && d.S); B = (d && d.B) || {};
      buildUI(); wirePointer(); light(false); this.ready = true;
    },
    dress,
    setNight(v) { night = !!v; $('pNight').classList.toggle('on', night); light(); },
    setOpen(on) { open = on; document.body.classList.toggle('painting', on); requestAnimationFrame(() => window.dispatchEvent(new Event('resize'))); if (!on) { brush = null; marking = false; $('pMark').classList.remove('on'); syncBrushUI(); ringAt(null); } refreshBoxes(); numbers(); },
    frame(t) { if (MATS()) MATS().tick(t); if (open) { for (const [s, b] of boxes) if (ALL()[s]) b.setFromObject(ALL()[s]); placeNumbers(); } },
    _test: { decalBits: () => { let n = 0; for (const b of dBits.values()) n += b.length; return n; }, decal: (k, x, y) => { decalKind = k; placeDecal(x, y); }, wear: k => { wearKind = k; }, layers: () => showLayers(), tapped: () => tapped, hit: (x, y) => hitAt(x, y), dab: (p, how) => { stroke = new Map(); dab(p, how); endStroke(); }, fill: m => { stroke = new Map(); fillMesh(m); endStroke(); }, setBrush: b => { brush = b; syncBrushUI(); }, setColour: h => { col.hex = h; }, skin: k => putSkin(k), state: () => ({ S, B }), undo, element, tapAt, marks, both: v => { both = v; }, withSkin: (v, k) => { withSkin = v; if (k) brushSkin = k; } }
  };
})();
