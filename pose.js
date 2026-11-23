// Pose + Animate (Nov 23 2026, his ask: "make it so I can change poses, and even do my own animations").
// Pose: tap a joint on the mech (or pick it), move three sliders (Bend / Twist / Tilt). Mirror copies it to the other side.
// Animate: a move is a row of frames; each frame is a pose. Add frames, pose each one, press Play: the mech glides from frame to frame.
// A saved move gets its own button next to Idle / Walk / Run / Punch and shows up in Photo mode. One frame = a pose you can hold.
// Angles are stored per joint in degrees from the joint's rest position, right-side rule (the left side mirrors itself),
// the same rule the weapon stances use. Saved on this phone ('mf-mymoves'). index.html calls MF_POSE.init / ready / setOpen / apply.
(function () {
  let C, T, open = false, joint = 'chest', mirror = true, frames = [], cur = 0, step = .5, loop = true, editId = null, previewing = null, helper = null, MY = [];
  const $ = id => document.getElementById(id);
  const ORDER = ['chest', 'waist', 'head', 'neck', 'pelvis', 'shoulder.R', 'shoulder.L', 'upper_arm.R', 'upper_arm.L', 'forearm.R', 'forearm.L', 'hand.R', 'hand.L', 'thigh.R', 'thigh.L', 'shin.R', 'shin.L', 'foot.R', 'foot.L'];
  const names = () => [...ORDER.filter(n => C.bones[n]), ...Object.keys(C.bones).filter(n => !ORDER.includes(n))];
  const nice = n => { const t = n.replace(/\.[LR]$/, '').replace('_', ' '); return (n.endsWith('.L') ? 'Left ' + t : n.endsWith('.R') ? 'Right ' + t : t[0].toUpperCase() + t.slice(1)).replace('Pelvis', 'Hips'); };
  const other = n => n.endsWith('.L') ? n.slice(0, -2) + '.R' : n.endsWith('.R') ? n.slice(0, -2) + '.L' : null;
  const sgn = n => n.endsWith('.L') ? -1 : 1;
  const rad = d => d * Math.PI / 180, r1 = v => Math.round(v * 10) / 10;
  const blank = () => ({ p: {}, h: 0 });
  const frame = () => frames[cur];

  // ---------- pose <-> joints ----------
  function quatOf(n, deg, out) { const e = new T.Euler(rad(deg[0]), rad(deg[1]) * sgn(n), rad(deg[2]) * sgn(n), 'XYZ'); return out.copy(C.bones[n].userData.restLocal).multiply(new T.Quaternion().setFromEuler(e)); }
  function capture() {          // read the pose the mech is in right now (move + weapon stance) so editing starts from what you see
    const f = blank(), q = new T.Quaternion(), e = new T.Euler();
    for (const n of names()) { const b = C.bones[n]; q.copy(b.userData.restLocal).invert().multiply(b.quaternion); e.setFromQuaternion(q, 'XYZ');
      f.p[n] = [r1(e.x * 180 / Math.PI), r1(e.y * 180 / Math.PI * sgn(n)), r1(e.z * 180 / Math.PI * sgn(n))]; }
    return f;
  }
  function apply() {            // called every frame by index.html while the Pose panel is open (after the move and the stances)
    if (!open || previewing) return;
    const f = frame(); if (!f) return;
    for (const [n, deg] of Object.entries(f.p)) if (C.bones[n]) quatOf(n, deg, C.bones[n].quaternion);
    C.bones.pelvis.position.y += f.h || 0;
    C.bones.pelvis.updateMatrixWorld(true);
  }

  // ---------- a move made of frames -> a clip the mech can play ----------
  function clipOf(mv) {
    const fs = mv.frames, n = fs.length, times = [], q = new T.Quaternion();
    const list = n === 1 ? [fs[0], fs[0]] : mv.loop ? [...fs, fs[0]] : fs;
    list.forEach((_, i) => times.push(n === 1 ? i : i * mv.step));
    const tracks = [];
    for (const name of names()) { const b = C.bones[name], v = [];
      for (const f of list) { quatOf(name, f.p[name] || [0, 0, 0], q); v.push(q.x, q.y, q.z, q.w); }
      tracks.push(new T.QuaternionKeyframeTrack(b.name + '.quaternion', times, v)); }
    const pv = C.bones.pelvis, sp = pv.userData.stdPos, pos = [];
    for (const f of list) pos.push(sp.x, sp.y + (f.h || 0), sp.z);
    tracks.push(new T.VectorKeyframeTrack(pv.name + '.position', times, pos));
    return new T.AnimationClip('my:' + mv.id, times[times.length - 1], tracks);
  }
  const keyOf = mv => 'my:' + mv.id;
  function register(mv) {        // (re)make the move's button and clip
    const k = keyOf(mv), old = C.moves[k];
    if (old) { old.stop(); C.mixer.uncacheClip(old.getClip()); }
    C.moves[k] = C.mixer.clipAction(clipOf(mv));
    if (mv.loop || mv.frames.length === 1) C.PLAY_ONCE.delete(k); else C.PLAY_ONCE.add(k);
    C.setMoveButton(k, '★ ' + mv.name);
  }
  function store() { try { localStorage.setItem('mf-mymoves', JSON.stringify(MY)); } catch (e) {} }

  // ---------- the panel ----------
  function say(t) { const el = $('poSay'); if (el) el.textContent = t; }
  function showJoint() {
    $('poJoint').value = joint; const f = frame(), d = (f && f.p[joint]) || [0, 0, 0];
    ['poX', 'poY', 'poZ'].forEach((id, i) => { $(id).value = d[i]; $(id + 'v').textContent = Math.round(d[i]) + '°'; });
    $('poH').value = (f && f.h) || 0; $('poHrow').style.display = joint === 'pelvis' ? 'flex' : 'none';
    box();
  }
  function box() {               // yellow box around the picked joint's part
    if (helper) { C.scene.remove(helper); helper = null; }
    if (!open || previewing) return;
    const b = C.bones[joint], target = C.held[joint] || (b && b.userData.block) || b; if (!target) return;
    helper = new T.BoxHelper(target, 0xffc040); helper.material.depthTest = false; helper.renderOrder = 9; helper.material.userData.outlineParameters = { visible: false }; C.scene.add(helper);
  }
  function setAngle(i, v) {
    const f = frame(); if (!f) return; stopPreview();
    const d = f.p[joint] || (f.p[joint] = [0, 0, 0]); d[i] = +v;
    const o = other(joint); if (mirror && o && C.bones[o]) f.p[o] = d.slice();
    $(['poX', 'poY', 'poZ'][i] + 'v').textContent = Math.round(v) + '°';
  }
  function showFrames() {
    const el = $('poFrames'); el.innerHTML = '';
    frames.forEach((_, i) => { const b = document.createElement('button'); b.textContent = i + 1; b.setAttribute('aria-label', 'Frame ' + (i + 1)); b.classList.toggle('on', i === cur);
      b.onclick = () => { stopPreview(); cur = i; showFrames(); showJoint(); }; el.append(b); });
    $('poCount').textContent = frames.length === 1 ? '1 frame = a pose you can hold' : frames.length + ' frames, ' + (frames.length * step).toFixed(1) + ' s' + (loop ? ' (loops)' : '');
    const cb = el.querySelector('.on'); if (cb) cb.scrollIntoView({ block: 'nearest', inline: 'center' });
  }
  function showMine() {
    $('poMine').innerHTML = '<option value="">My moves...</option>' + MY.map(m => `<option value="${m.id}">${m.name} (${m.frames.length})</option>`).join('');
    $('poMine').value = editId || '';
  }
  function current() { return { id: editId || 'preview', name: $('poName').value.trim() || 'My move', frames, step, loop }; }
  function stopPreview() {
    if (!previewing) return; previewing.stop(); C.mixer.uncacheClip(previewing.getClip()); previewing = null; MF_POSE.frozen = true; $('poPlay').textContent = '▶ Play'; $('poPlay').classList.remove('on'); box();
  }
  function preview() {
    if (previewing) return stopPreview();
    C.mixer.stopAllAction();
    const mv = { ...current(), id: 'preview' }; previewing = C.mixer.clipAction(clipOf(mv));
    previewing.setLoop(mv.loop || mv.frames.length === 1 ? T.LoopRepeat : T.LoopOnce); previewing.clampWhenFinished = true; previewing.reset().play();
    MF_POSE.frozen = false; $('poPlay').textContent = '■ Stop'; $('poPlay').classList.add('on'); box();
  }
  function startNew(fromNow) { stopPreview(); frames = [fromNow ? capture() : blank()]; cur = 0; editId = null; $('poName').value = ''; showFrames(); showJoint(); showMine(); }
  function saveMove() {
    stopPreview();
    const name = $('poName').value.trim() || (frames.length === 1 ? 'Pose ' : 'Move ') + (MY.length + 1);
    let mv = MY.find(m => m.id === editId);
    if (!mv) { mv = { id: Math.random().toString(36).slice(2, 8) }; MY.push(mv); editId = mv.id; }
    Object.assign(mv, { name, frames: JSON.parse(JSON.stringify(frames)), step, loop });
    register(mv); store(); $('poName').value = name; showMine(); say('Saved "' + name + '". It has its own ★ button with the moves, and it is in Photo mode.');
  }
  function buildUI() {
    $('pose').innerHTML = `
      <p class="hint" id="poSay">Tap a joint on the mech, then move the sliders. Add frames to make it move.</p>
      <div class="line"><select id="poJoint" aria-label="Joint">${names().map(n => `<option value="${n}">${nice(n)}</option>`).join('')}</select><button id="poMirror" class="on">🪞 Mirror</button><button id="poZero">Straighten joint</button><button id="poZeroAll">Straighten all</button><button id="poNow">Start from this stance</button></div>
      <div class="line"><span>Bend</span><input type="range" id="poX" aria-label="Bend" min="-180" max="180" step="1"><b id="poXv"></b></div>
      <div class="line"><span>Twist</span><input type="range" id="poY" aria-label="Twist" min="-180" max="180" step="1"><b id="poYv"></b></div>
      <div class="line"><span>Tilt</span><input type="range" id="poZ" aria-label="Tilt" min="-180" max="180" step="1"><b id="poZv"></b></div>
      <div class="line" id="poHrow"><span>Hips up / down</span><input type="range" id="poH" aria-label="Hips up or down" min="-4" max="4" step=".05"></div>
      <div class="line"><b>Frames</b><button id="poAdd">＋ Add frame</button><span id="poFrames" style="display:contents"></span><button id="poDel">🗑 Frame</button></div>
      <div class="line"><button id="poPlay">▶ Play</button><button id="poLoop" class="on">🔁 Loop</button><span>Speed</span><input type="range" id="poStep" aria-label="Seconds per frame" min=".1" max="1.5" step=".05" value=".5"><small id="poCount"></small></div>
      <div class="line"><input id="poName" aria-label="Name of the move" placeholder="Name it" maxlength="18" style="font:inherit;border-radius:8px;background:#2c2c30;color:#eee;border:1px solid #4a4a4e;padding:0 8px;width:120px"><button id="poSave">💾 Save move</button><select id="poMine" aria-label="My moves"></select><button id="poNew">New</button><button id="poKill">Delete</button></div>`;
    $('poJoint').onchange = e => { joint = e.target.value; showJoint(); };
    $('poMirror').onclick = e => { mirror = !mirror; e.target.classList.toggle('on', mirror); };
    ['poX', 'poY', 'poZ'].forEach((id, i) => $(id).oninput = e => setAngle(i, e.target.value));
    $('poH').oninput = e => { stopPreview(); frame().h = +e.target.value; };
    $('poZero').onclick = () => { stopPreview(); const f = frame(); f.p[joint] = [0, 0, 0]; const o = other(joint); if (mirror && o) f.p[o] = [0, 0, 0]; showJoint(); };
    $('poZeroAll').onclick = () => { stopPreview(); frames[cur] = blank(); showJoint(); };
    $('poNow').onclick = () => { stopPreview(); MF_POSE.skip = true; requestAnimationFrame(() => requestAnimationFrame(() => { frames[cur] = capture(); MF_POSE.skip = false; showJoint(); say('Copied the stance the mech was standing in.'); })); };
    $('poAdd').onclick = () => { stopPreview(); frames.splice(cur + 1, 0, JSON.parse(JSON.stringify(frame()))); cur++; showFrames(); showJoint(); say('Frame ' + (cur + 1) + ' is a copy of the last one. Change the pose, then Play.'); };
    $('poDel').onclick = () => { stopPreview(); if (frames.length < 2) return say('A move needs at least one frame.'); frames.splice(cur, 1); cur = Math.min(cur, frames.length - 1); showFrames(); showJoint(); };
    $('poPlay').onclick = preview;
    $('poLoop').onclick = e => { stopPreview(); loop = !loop; e.target.classList.toggle('on', loop); showFrames(); };
    $('poStep').oninput = e => { stopPreview(); step = +e.target.value; showFrames(); };
    $('poSave').onclick = saveMove;
    $('poMine').onchange = e => { const mv = MY.find(m => m.id === e.target.value); if (!mv) return; stopPreview(); editId = mv.id; frames = JSON.parse(JSON.stringify(mv.frames)); cur = 0; step = mv.step; loop = mv.loop;
      $('poName').value = mv.name; $('poStep').value = step; $('poLoop').classList.toggle('on', loop); showFrames(); showJoint(); say('Editing "' + mv.name + '". Save move keeps the changes.'); };
    $('poNew').onclick = () => { startNew(true); say('New move, starting from the stance the mech is in.'); };
    $('poKill').onclick = () => { const mv = MY.find(m => m.id === editId); if (!mv) return say('Pick one of your moves first.'); stopPreview();
      const k = keyOf(mv); if (C.moves[k]) { C.moves[k].stop(); C.mixer.uncacheClip(C.moves[k].getClip()); delete C.moves[k]; } C.setMoveButton(k, null);
      MY = MY.filter(m => m !== mv); store(); startNew(true); say('Deleted "' + mv.name + '".'); };
  }
  function wireTap() {           // tap (not drag) a part on the mech to pick its joint
    const el = C.renderer.domElement; let down = null;
    el.addEventListener('pointerdown', e => { down = { x: e.clientX, y: e.clientY, t: e.timeStamp }; });
    el.addEventListener('pointerup', e => { if (!open || !down || Math.hypot(e.clientX - down.x, e.clientY - down.y) > 10 || e.timeStamp - down.t > 500) return;
      const spot = C.spotAt(e.clientX, e.clientY), n = spot && C.BONE_OF(spot); if (n && C.bones[n]) { joint = n; showJoint(); say(nice(n) + ' picked.'); } });
  }

  window.MF_POSE = {
    frozen: false, skip: false, get busy() { return open; },
    init(ctx) { C = ctx; T = ctx.THREE; try { MY = JSON.parse(localStorage.getItem('mf-mymoves')) || []; } catch (e) { MY = []; } },
    ready() { buildUI(); wireTap(); for (const mv of MY) { try { register(mv); } catch (e) {} } showMine(); },
    setOpen(on) {
      if (on === open) return; open = on;
      if (on) { MF_POSE.frozen = true; if (!frames.length || !editId) startNew(true); else { showFrames(); showJoint(); } }
      else { stopPreview(); MF_POSE.frozen = false; if (helper) { C.scene.remove(helper); helper = null; } C.play('idle'); }
    },
    apply() { if (MF_POSE.skip) return; apply(); if (helper && open) helper.update(); },
    get mine() { return MY; }, label: k => { const mv = MY.find(m => keyOf(m) === k); return mv ? '★ ' + mv.name : null; },
    _test: { frames: () => frames, setAngle: (j, i, v) => { joint = j; showJoint(); setAngle(i, v); showJoint(); }, capture }
  };
})();
