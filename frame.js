// Mythic Forge — the mech frame math (same numbers as tools/blender/mech_frame.py, keep them in step).
// Sliders in, bone positions + stand-in block sizes out. 1.0 = Standard. Coordinates are Blender's:
// x = mech's left (+) / right (-), y = back (+) / front (-), z = up. Metres; Standard is about 10 m tall.
window.MF_FRAME = (() => {
  const STANDARD = { height: 1, leg: 1, arm: 1, shoulder: 1, hip: 1, chest: 1, head: 1, bulk: 1 };
  const PRESETS = {
    standard: {},
    heavy:   { leg: .9, arm: 1.0, shoulder: 1.15, hip: 1.2, chest: 1.1, head: 1.0, bulk: 1.35 },   // toned down Nov 22: chest was a huge slab, head tiny
    sleek:   { leg: 1.15, arm: 1.05, shoulder: .9, hip: .85, chest: .85, bulk: .8 },
    squat:   { leg: .7, arm: .8, shoulder: 1.2, hip: 1.3, chest: 1.2, head: 1.15, bulk: 1.4 },
    brawler: { leg: .9, arm: 1.3, shoulder: 1.25, chest: 1.2, head: .9, bulk: 1.3 },
    scout:   { leg: 1.25, shoulder: .85, hip: .8, chest: .8, head: .95, bulk: .7 },
  };
  const SLIDERS = [  // name, what it does, min, max
    ['height', 'Whole mech size', .6, 1.6], ['leg', 'Leg length', .6, 1.5], ['arm', 'Arm length', .6, 1.5],
    ['shoulder', 'Shoulder width', .7, 1.6], ['hip', 'Hip width', .7, 1.6], ['chest', 'Chest size', .7, 1.6],
    ['head', 'Head size', .5, 1.6], ['bulk', 'Thickness', .5, 1.8],
  ];

  // bones: name -> { head:[x,y,z], tail:[x,y,z] }   blocks: name -> [width, depth] (length runs head -> tail)
  function build(p) {
    const ankle = .63, knee = ankle + 2.39 * p.leg, hipz = knee + 2.51 * p.leg;
    const pelB = hipz - .25, pelT = hipz + .70, wstT = pelT + .56;
    const chT = wstT + 2.21 * p.chest, shZ = wstT + 1.76 * p.chest;
    const hdB = chT + .09;
    // head size follows the body: Standard is 9 heads tall (Gundam-style mechs are about 9 to 9.5 heads tall)
    const hh = hdB / 8 * p.head, hdT = hdB + hh;
    const hx = 1.0 * p.hip, sx = 1.83 * p.shoulder, a = p.arm;
    const el = [sx + .31 * a, shZ - 2.01 * a], wr = [el[0] + .06 * a, el[1] - 1.73 * a], hn = wr[1] - .71 * a;
    const B = {
      pelvis: [[0, 0, pelB], [0, 0, pelT - .03]], waist: [[0, 0, pelT], [0, 0, wstT]],
      chest: [[0, 0, wstT], [0, 0, chT]], head: [[0, 0, hdB], [0, 0, hdT]],
    };
    const left = {
      shoulder: [[.9 * p.shoulder, 0, shZ], [sx, 0, shZ]], upper_arm: [[sx, 0, shZ], [el[0], 0, el[1]]],
      forearm: [[el[0], 0, el[1]], [wr[0], 0, wr[1]]], hand: [[wr[0], 0, wr[1]], [wr[0], 0, hn]],
      thigh: [[hx, 0, hipz], [hx + .13, 0, knee]], shin: [[hx + .13, 0, knee], [hx + .13, 0, ankle]],
      foot: [[hx + .13, 0, ankle], [hx + .13, -.9, .10]],
    };
    for (const [side, s] of [['.L', 1], ['.R', -1]])
      for (const [n, [h, t]] of Object.entries(left)) B[n + side] = [[s * h[0], h[1], h[2]], [s * t[0], t[1], t[2]]];
    const b = p.bulk, k = p.height;
    const W = { pelvis: [1.6 * p.hip, 1.0], waist: [.5 * b, .5 * b], chest: [2 * sx - .56, 1.6 * p.chest], head: [1.05 * hh, 1.0 * hh] };
    const T = { shoulder: .55, upper_arm: .45, forearm: .5, hand: .7, thigh: .6, shin: .55 };
    for (const side of ['.L', '.R']) {
      for (const [n, t] of Object.entries(T)) W[n + side] = [t * b, t * b];
      W['foot' + side] = [1.1 * b, .56];
    }
    const bones = {};
    for (const [n, [h, t]] of Object.entries(B)) bones[n] = { head: h.map(v => v * k), tail: t.map(v => v * k), size: W[n].map(v => v * k) };
    return bones;
  }
  return { STANDARD, PRESETS, SLIDERS, build, withPreset: name => ({ ...STANDARD, ...PRESETS[name] }) };
})();
