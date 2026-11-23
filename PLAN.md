# Mythic Forge (fresh start) — Plan & Rules

## Now
Mythic Forge rebuilt from the ground up (Nov 22, 2026). Phase 3 done and live (Nov 22): every spot has body parts (4 to 10 choices each), toon shading + outlines. Next: Phase 5 save/export: Body panel with 6 presets + 8 sliders reshaping the frame live, moves keep playing.
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
2. (done Nov 22) Real sliders: 6 presets (standard, heavy, sleek, squat, brawler, scout) + 8 sliders (height, leg, arm, shoulder, hip, chest, head, bulk) change the frame live.
3. Body parts (redone Nov 22; he meant body parts, not loose armor): every spot on the frame is a slot (head, chest, pelvis, shoulders, arms, hands, legs, feet). Tap a spot (or pick it from the list), pick a body part for it. Mirror ON by default for left/right spots. Parts are made in Blender, styled low-poly with toon shading + outlines, and stretch to fit any body shape. Done when: every spot has at least 4 choices. DONE Nov 22: chest 8, head 10, pelvis 4, shoulder 7, upper arm 4, forearm 6, hand 4 (fist, open, grip, claw), thigh 4, shin 5, foot 5. Waist stays part of the frame for now.
4. (merged into 3) First real parts.
4. First real parts: mech armor pieces built in Blender to fit the frame.
5. Save and export: your mech downloads as a game file Titan Clash can use.

## Build list he picked Nov 22 ("let's get to 9"), in order, each shown before push
1. Backpack spot (7 from his kit) - built
2. Paint schemes (his kit's colour sets) + My colours (Main / Second / Trim / Glow) - built. Later: bring over the OLD Mythic Forge paint (brushes, skins, ethereal paint, layers in materials.js) instead of rebuilding it.
3. Starter mechs (his kit's 10 build sheets, each with a body preset + colours) - built
4. Random mech button - built
5. Weapons: energy swords, shields, missile pods, rifles (hands, shoulders, back)
6. Details: vents, antennas, spikes, emblems stuck anywhere
7. More moves: hit, block, jump + heavy landing, knockdown; fast style: boost dash, sidestep, rolling dodge
8. Photo mode: pose, background, save a picture
9. Sounds: stomps, servo whirs (Sound Lab idea)

## Add-ons (parking lot, reviewed at the end of each phase)
- Details: extra loose shapes (vents, antennas, spikes) stuck on top of body parts, with size / move / turn / color. Built once on Nov 22 by mistake as 'armor', removed from the app; comes back later.
- Recolor body parts (paint schemes).
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
- Go through changes with he before pushing.
- Never his real name anywhere public (use MajorasPride).
- Original work only; outside assets/libraries must be MIT/Apache/BSD/CC0 and go in the credits list.
- The old Mythic Forge ("Classic", inside the titan-clash repo) is frozen: nothing from it comes back unless he asks.
- Keep this file correct; update Now and the Log every session.

## Log (newest first)
- Nov 22, 2026: items 1-4 built: Backpack spot, Paint (11 kit schemes + My colours), Starter mechs (Vanguard, Bulwark, Titanheart, Ranger, Falcon, Paladin, Wraith, Mule, Patrol, Lionheart), Random. Parts now carry their material keys so they can be repainted. Tested at phone size: all starters, random, custom colour, backpack sits on the back, kept after reload, no errors. He reminded that old Mythic Forge has paint: logged to bring it over later. He said it works; pushed.
- Nov 22, 2026: he said moving the camera is hard. Camera now: smooth drag, can't go under the floor, 2 fingers zoom + slide, Front / Side / 3/4 / Back buttons, picking a spot glides in on it, closing Build glides back out, and the picture lifts above an open panel. Pushed with his OK.
- Nov 22, 2026: still hard on his phone: added press-and-hold buttons (turn left/right, zoom in/out, look higher/lower) under the view buttons; no finger dragging needed. Then added Slide left/right and labels, in a 2-column grid.
- Nov 22, 2026: he said Heavy looked weird (huge flat chest slab, tiny head). Heavy preset toned down (chest 1.1, shoulder 1.15, head 1.0, bulk 1.35; now 9 heads tall) in frame.js and mech_frame.py; body parts now keep their own shape (width/depth can only stretch 20% away from their height scale). Pushed with his OK.
- Nov 22, 2026: all spots filled (he said 'work them all now'). tools/blender/parts_all.py reuses his Mech Kit (mech_kit_R2.py, now kept in the repo) + 5 new designs (Piston and Plated upper arms, Piston and Knight thighs, Claw hand) and writes models/parts_all.js (both sides, ~1.9 MB). Fit modes: box (chest/head/pelvis), limb (arms/hands/legs), anchor (shoulder pads, feet). Checked every spot with numbers: parts line up with their spots, mirrored right side matches, feet on the floor, works on the Heavy body and while walking, no errors. Pushed with his OK.
- Nov 22, 2026: he found the loose-armor build 'looks like ass' and said he meant body parts. Mistake: start-checklist and skills were not run/loaded before building, and his art direction (toon + outlines) was ignored. Redo: toon shading (3 light bands) + black outlines (three.js OutlineEffect, MIT) + darker stage with a rim light; Build panel now = pick a spot, pick a body part. Chest slot first: 5 chests reused from his own Mech Kit T042 designs (Cockpit, Heavy, Sleek, Emblem, Grunt hatch) via tools/blender/parts_chest.py. Each chest stretches to fit the chest spot exactly (checked on Standard and Heavy) and is kept between visits.
- Nov 22, 2026: Phase 3 built and pushed: Build panel. Tap a body part (or pick from the list), add Block / Plate / Tube / Wedge, edit Size / Move / Turn / Color, Delete. Mirror on by default (the twin is a true mirror image on the other side). Pieces ride on the bones so they walk/run/punch with the mech and follow body-shape changes. Build is kept on the phone between visits (localStorage; real save/export is Phase 5). Tested at phone size: tapping, list, mirror, edits, reload, no errors.
- Nov 22, 2026: heads were too small (11 to 14 heads tall). Head size now follows the body: Standard is 9 heads tall like Gundam-style mechs (about 9 to 9.5); Heavy and Brawler about 10 (small Jaeger-style heads), Scout 9.4, Squat 8 (chunky). The Head slider still scales it.
- Nov 22, 2026 (voice): Phase 3 details decided, next moves picked, two movement styles (heavy / fast) added to Add-ons. Research notes: Gundams boost with main thrusters, turn with side thrusters (verniers) and by swinging their limbs as weights (AMBAC); Transformers fight like martial artists and keep wheels rolling while they transform.
- Nov 22, 2026: Phase 2 built: frame.js (same math as mech_frame.py) + Body panel. Joints move per slider, stand-in blocks are drawn per bone so they resize; moves made on Standard keep playing on any shape. Tested at phone size: no errors. Not pushed yet.
- Nov 22, 2026: fresh start. Phase 1 built: index.html loads the Standard mech frame (18 bones) with idle, walk, run, punch.

## Credits
- three.js (MIT)
