// Photo mode (Nov 23 2026, item 8): pose the mech, pick a backdrop, a lens and a light, then save or share a picture.
// Ideas borrowed from mech-builder games' photo / diorama modes (freeze a move on any frame, backdrops, low hero angles).
// The saved picture is only the 3D view, never the buttons. index.html calls MF_PHOTO.init(ctx) and reads MF_PHOTO.frozen.
(function () {
  let C, T, on = false, keep = null, bgTex = {}, shots = 0;
  const $ = id => document.getElementById(id);

  // ---------- backdrops: painted once on a canvas ----------
  const BACKS = { studio: 'Studio (dark)', white: 'White studio', sunset: 'Sunset', city: 'Night city', space: 'Space', hangar: 'Hangar', green: 'Green screen' };
  function rng(seed) { let a = seed; return () => { a = (a * 16807) % 2147483647; return (a - 1) / 2147483646; }; }
  function backdrop(kind) {
    if (bgTex[kind]) return bgTex[kind];
    const W = 512, H = 1024, cv = document.createElement('canvas'); cv.width = W; cv.height = H; const x = cv.getContext('2d'), r = rng(kind.length * 977 + 13);
    const grad = (stops) => { const g = x.createLinearGradient(0, 0, 0, H); stops.forEach(([p, c]) => g.addColorStop(p, c)); x.fillStyle = g; x.fillRect(0, 0, W, H); };
    if (kind === 'white') grad([[0, '#f4f5f7'], [.62, '#dfe2e8'], [.63, '#c9cdd6'], [1, '#aab0bc']]);
    else if (kind === 'sunset') { grad([[0, '#24184a'], [.35, '#7a2f6a'], [.55, '#e8643a'], [.66, '#ffc15a'], [.67, '#3a2230'], [1, '#150d18']]);
      const g = x.createRadialGradient(W * .5, H * .64, 0, W * .5, H * .64, 150); g.addColorStop(0, '#fff3c4'); g.addColorStop(.35, '#ffc45acc'); g.addColorStop(1, '#ffc45a00'); x.fillStyle = g; x.fillRect(0, H * .3, W, H * .37); }
    else if (kind === 'city') { grad([[0, '#060814'], [.5, '#141a3a'], [.7, '#2a2350'], [1, '#07080e']]);
      for (let layer = 0; layer < 3; layer++) { x.fillStyle = ['#0e1226', '#0a0d1c', '#060810'][layer]; let px = -10;
        while (px < W) { const w = 26 + r() * 46, h = 120 + r() * 260 - layer * 50, top = H * .72 - h + layer * 40; x.fillRect(px, top, w, H - top);
          for (let wy = top + 8; wy < H * .72 + layer * 40 - 6; wy += 11) for (let wx = px + 4; wx < px + w - 5; wx += 8) if (r() < .22) { x.fillStyle = r() < .8 ? '#ffd98a' : '#8ad8ff'; x.globalAlpha = .35 + r() * .5; x.fillRect(wx, wy, 3, 5); x.globalAlpha = 1; x.fillStyle = ['#0e1226', '#0a0d1c', '#060810'][layer]; }
          px += w + 2 + r() * 8; } } }
    else if (kind === 'space') { grad([[0, '#02030a'], [.5, '#080a1c'], [1, '#020308']]);
      for (let k = 0; k < 5; k++) { const cx = r() * W, cy = r() * H, rad = 120 + r() * 200, g = x.createRadialGradient(cx, cy, 0, cx, cy, rad); g.addColorStop(0, ['#5a2a8a55', '#1a4a8a55', '#8a2a5a44'][k % 3]); g.addColorStop(1, '#00000000'); x.fillStyle = g; x.fillRect(0, 0, W, H); }
      for (let k = 0; k < 520; k++) { x.fillStyle = r() < .85 ? '#ffffff' : '#ffe0a0'; x.globalAlpha = .3 + r() * .7; const s = r() < .93 ? 1 : 2; x.fillRect(r() * W, r() * H, s, s); } x.globalAlpha = 1; }
    else if (kind === 'hangar') { grad([[0, '#14171d'], [.6, '#2a2f38'], [.61, '#1b1e24'], [1, '#0d0f13']]);
      x.fillStyle = '#0c0e12'; for (let k = 0; k < 6; k++) x.fillRect(k * 100 - 10, 0, 22, H * .61);
      x.fillStyle = '#d8e6ff'; x.globalAlpha = .85; for (let k = 0; k < 5; k++) x.fillRect(k * 100 + 36, 60, 44, 7); x.globalAlpha = 1;
      for (let k = -1; k < 14; k++) { x.fillStyle = k % 2 ? '#141414' : '#e0b400'; x.beginPath(); x.moveTo(k * 40, H * .61); x.lineTo(k * 40 + 40, H * .61); x.lineTo(k * 40 + 20, H * .61 + 16); x.lineTo(k * 40 - 20, H * .61 + 16); x.fill(); } }
    const t = new T.CanvasTexture(cv); t.colorSpace = T.SRGBColorSpace; return (bgTex[kind] = t);
  }
  function setBack(kind) {
    if (kind === 'studio') C.scene.background = keep.bg;
    else if (kind === 'green') C.scene.background = new T.Color(0x00d000);
    else C.scene.background = backdrop(kind);
  }

  // ---------- pose: any move, frozen on any frame ----------
  function pose() {
    const name = $('phMove').value, a = C.moveFor(name); if (!a) return;
    C.mixer.stopAllAction(); a.reset(); a.play(); a.time = +$('phFrame').value * a.getClip().duration;
  }
  function light(kind) {
    const L = C.lights, b = keep.light, night = kind === 'night';
    const k = { day: [1, 1, 1], drama: [.3, 1.35, 2.2], night: [1, 1, 1] }[kind];
    if (window.MF_PAINT && MF_PAINT.setNight) MF_PAINT.setNight(night);
    if (!night) { L.hemi.intensity = b[0] * k[0]; L.sun.intensity = b[1] * k[1]; L.rim.intensity = b[2] * k[2]; }
  }
  const ANGLES = { hero: [[.55, -.12, .82], 1.08, 30], front: [[0, .1, 1], 1, 40], side: [[1, .1, 0], 1, 40], top: [[.35, 1, .6], 1.05, 40], face: [[.35, .05, 1], .3, 28] };
  function angle(kind) {
    const [d, far, fov] = ANGLES[kind], dir = new T.Vector3(...d).normalize();
    setFov(fov); $('phLens').value = fov;
    const box = C.bounds(), size = box.getSize(new T.Vector3()), target = box.getCenter(new T.Vector3());
    if (kind === 'face') target.y = box.min.y + size.y * .9;
    C.glide(target, target.clone().addScaledVector(dir, Math.max(C.frameDist(box) * far, 3)));   // frames the mech's real outline, and allows for the lens
  }
  function setFov(f) { C.camera.fov = f; C.camera.updateProjectionMatrix(); }

  // ---------- save / share ----------
  function shoot(share) {
    const r = C.renderer, pr = r.getPixelRatio(), want = Math.min(3, Math.max(pr, 2));
    C.camera.clearViewOffset();   // the picture is the whole view, centred (no room left for the buttons)
    C.outline.setPixelRatio(want); C.outline.setSize(innerWidth, innerHeight); C.outline.render(C.scene, C.camera);
    r.domElement.toBlob(blob => {
      C.outline.setPixelRatio(pr); C.outline.setSize(innerWidth, innerHeight);
      if (!blob) return say('Could not save the picture');
      const name = 'mythic-forge-' + (++shots) + '.png', file = new File([blob], name, { type: 'image/png' });
      if (share && navigator.canShare && navigator.canShare({ files: [file] })) { navigator.share({ files: [file], title: 'Mythic Forge' }).catch(() => {}); return; }
      const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name; document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 4000);
      say('Saved ' + name);
    }, 'image/png');
  }
  function say(t) { const el = $('phSay'); el.textContent = t; clearTimeout(say.t); say.t = setTimeout(() => el.textContent = 'Drag to turn the camera. The saved picture never shows the buttons.', 2500); }

  // ---------- in and out ----------
  function enter() {
    if (on) return; on = true; MF_PHOTO.frozen = true;
    C.closePanels();
    keep = { bg: C.scene.background, fov: C.camera.fov, polar: C.controls.maxPolarAngle, bones: C.skeleton() && C.skeleton().visible, grid: C.grid.visible,
      light: [C.lights.hemi.intensity, C.lights.sun.intensity, C.lights.rim.intensity], min: C.controls.minDistance };
    if (C.skeleton()) C.skeleton().visible = false;
    C.controls.maxPolarAngle = Math.PI * .56; C.controls.minDistance = 2;
    $('phMove').innerHTML = Object.keys(C.moves).filter(n => !/_L$/.test(n)).map(n => `<option value="${n}">${(window.MF_POSE && MF_POSE.label(n)) || n[0].toUpperCase() + n.slice(1)}</option>`).join('');
    $('phMove').value = (C.currentMove() || 'idle').replace(/_L$/, ''); $('phFrame').value = .3; $('phBack').value = 'studio'; $('phLight').value = 'day'; $('phLens').value = C.camera.fov;
    $('phGrid').classList.toggle('on', C.grid.visible); $('phShare').style.display = navigator.canShare ? '' : 'none';
    document.body.classList.add('photo'); pose(); say(''); setTimeout(() => C.viewAll('angle'), 80);
    requestAnimationFrame(() => window.dispatchEvent(new Event('resize')));
  }
  function leave() {
    if (!on) return; on = false; MF_PHOTO.frozen = false;
    light('day'); C.scene.background = keep.bg; setFov(keep.fov); C.controls.maxPolarAngle = keep.polar; C.controls.minDistance = keep.min;
    C.lights.hemi.intensity = keep.light[0]; C.lights.sun.intensity = keep.light[1]; C.lights.rim.intensity = keep.light[2];
    if (C.skeleton()) C.skeleton().visible = keep.bones; C.grid.visible = keep.grid;
    document.body.classList.remove('photo'); C.play('idle'); C.viewAll('angle');
    requestAnimationFrame(() => window.dispatchEvent(new Event('resize')));
  }

  window.MF_PHOTO = {
    frozen: false,
    init(ctx) {
      C = ctx; T = ctx.THREE;
      document.body.insertAdjacentHTML('beforeend', `<div id="photoBar">
        <div class="line"><button id="phDone">✖ Done</button><button id="phSave" class="on">📸 Save picture</button><button id="phShare">Share</button><small id="phSay"></small></div>
        <div class="line"><span>Pose</span><select id="phMove" aria-label="Move to pose"></select><input type="range" id="phFrame" aria-label="Which frame of the move" min="0" max="1" step=".01" value=".3"><span>Stance</span><select id="phStance" aria-label="Stance"><option value="ready">Ready</option><option value="relaxed">Relaxed</option><option value="action">Action</option></select></div>
        <div class="line"><span>Angle</span><button data-pha="hero">Hero (low)</button><button data-pha="front">Front</button><button data-pha="side">Side</button><button data-pha="top">Top</button><button data-pha="face">Face</button><span>Lens</span><input type="range" id="phLens" aria-label="Lens (zoom)" min="16" max="70" step="1" value="40"></div>
        <div class="line"><span>Backdrop</span><select id="phBack" aria-label="Backdrop">${Object.entries(BACKS).map(([k, n]) => `<option value="${k}">${n}</option>`).join('')}</select><span>Light</span><select id="phLight" aria-label="Light"><option value="day">Day</option><option value="drama">Dramatic</option><option value="night">Night glow</option></select><button id="phGrid">Floor grid</button></div></div>`);
      $('phDone').onclick = leave; $('phSave').onclick = () => shoot(false); $('phShare').onclick = () => shoot(true);
      $('phMove').onchange = pose; $('phFrame').oninput = pose;
      $('phStance').onchange = e => C.setStance(e.target.value);
      document.querySelectorAll('[data-pha]').forEach(b => b.onclick = () => angle(b.dataset.pha));
      $('phLens').oninput = e => setFov(+e.target.value);
      $('phBack').onchange = e => setBack(e.target.value);
      $('phLight').onchange = e => light(e.target.value);
      $('phGrid').onclick = e => { C.grid.visible = !C.grid.visible; e.target.classList.toggle('on', C.grid.visible); };
    },
    enter, leave, get on() { return on; }
  };
})();
