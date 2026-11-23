# Mythic Forge (fresh start) — Plan & Rules

## Now
Mythic Forge rebuilt from the ground up (Nov 22, 2026). Phase 2 of 5 built, waiting for Clayton's OK before it's pushed: Body panel with 6 presets + 8 sliders reshaping the frame live, moves keep playing.
Live (Phase 1): https://majoraspride.github.io/mythic-forge/ once Pages is on.

## What it is (Blueprint)
- Blender is the factory (makes frames, parts, moves). Mythic Forge is the snap-together table. Titan Clash is the arena.
- v1.0 is for both: building mechs for Titan Clash AND a fun mech toy on the phone.
- Look: plain and simple for now.
- Base: a simple clean screen we build up ourselves (three.js), borrowing three.js editor pieces only when needed.
- Not in v1.0 yet: kaiju/dragon frames, painting, sculpting, sharing builds.

## Phases (one at a time, a finished phase only reopens for bugs)
0. Brainstorm — done Nov 22.
1. (done Nov 22) Smallest version that runs: Standard mech frame + idle, walk, run, punch buttons. Done when: it loads on the S23 Ultra and every button plays its move.
2. Real sliders: 6 presets (standard, heavy, sleek, squat, brawler, scout) + 8 sliders (height, leg, arm, shoulder, hip, chest, head, bulk) change the frame live.
3. Snap armor on (decided Nov 22 by voice): tap a bone Lego-style to put a part on it, with a body-part list as backup for small or hidden bones. Mirror toggle, ON by default (left part copies to the right). Every part can be resized, moved, rotated and colored, and it moves with the mech when it walks or punches. Simple blocks first.
4. First real parts: mech armor pieces built in Blender to fit the frame.
5. Save and export: your mech downloads as a game file Titan Clash can use.

## Add-ons (parking lot, reviewed at the end of each phase)
- Movement styles (decided Nov 22): two flavors, picked per mech.
  - Heavy / stompy (Pacific Rim): what the frame does now.
  - Fast / agile (Gundam + Transformers): boost dash (body leans forward, arms swept back, ends in a short hop), boost jump, quick sidestep bursts (side thrusters); martial-arts flips, spin kick, rolling dodge, roll-into-transform for mechs that turn into vehicles.
- Next moves for every mech: hit reaction (heavy stagger), block (arms up), jump with heavy landing, knockdown and get up.
- Special move only some mechs get: turn in place (e.g. heavy tank types pivot on the spot; others step to turn).
- Kaiju, dragon and other frames
- Fix and bring back blast (Mega Man buster pose), sword swing, slide
- More moves, painting, sculpting (SculptGL), sharing builds

## Skills
build-together, pro-3d-workflow, game-art, ponytail, repo-scout. Model: Opus.

## Rules
- Go through changes with Clayton before pushing.
- Never his real name anywhere public (use MajorasPride).
- Original work only; outside assets/libraries must be MIT/Apache/BSD/CC0 and go in the credits list.
- The old Mythic Forge ("Classic", inside the titan-clash repo) is frozen: nothing from it comes back unless he asks.
- Keep this file correct; update Now and the Log every session.

## Log (newest first)
- Nov 22, 2026: heads were too small (11 to 14 heads tall). Head size now follows the body: Standard is 9 heads tall like Gundam-style mechs (about 9 to 9.5); Heavy and Brawler about 10 (small Jaeger-style heads), Scout 9.4, Squat 8 (chunky). The Head slider still scales it.
- Nov 22, 2026 (voice): Phase 3 details decided, next moves picked, two movement styles (heavy / fast) added to Add-ons. Research notes: Gundams boost with main thrusters, turn with side thrusters (verniers) and by swinging their limbs as weights (AMBAC); Transformers fight like martial artists and keep wheels rolling while they transform.
- Nov 22, 2026: Phase 2 built: frame.js (same math as mech_frame.py) + Body panel. Joints move per slider, stand-in blocks are drawn per bone so they resize; moves made on Standard keep playing on any shape. Tested at phone size: no errors. Not pushed yet.
- Nov 22, 2026: fresh start. Phase 1 built: index.html loads the Standard mech frame (18 bones) with idle, walk, run, punch.

## Credits
- three.js (MIT)
