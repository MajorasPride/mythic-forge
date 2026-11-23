# Mythic Forge — Handoff (updated Nov 23 2026, 4am)

Read this first in a new chat. The full plan, rules and log are in PLAN.md.

## Where things are
- Live app: https://majoraspride.github.io/mythic-forge/
- Repo: MajorasPride/mythic-forge (GitHub Pages serves the main branch). Never his real name anywhere public.
- His PC copy (C:\Users\cc492\Documents\Personal Claude\mythic-forge) is a plain folder, NOT a git clone, and is behind GitHub since Nov 23. GitHub is the truth. Sync it only when he connects that folder.
- The old Mythic Forge (creatures, 70 bodies) lives in the titan-clash repo under myth-forge/. This repo is the fresh start (mechs first).

## What is live
Standard mech frame + moves (idle, walk, run, punch), Body presets + sliders, Build (body parts for every spot, backpack, weapons, stances), Details, Part Maker, Starter mechs, Random, and since Nov 23: Paint, the Hero + Walker part sets, and Photo mode.

## Hero + Walker sets (live Nov 23)
Made in Blender from code with his own Mech Kit builder: tools/blender/parts_all.py (pip install bpy, then python3 parts_all.py writes models/parts_all.js). Hero = Gundam-style (10 parts), Walker = walking tank (11 parts incl. the Rotary cannon arm from his mech picture). Two starter mechs, Hero and Walker, are first in the Starter list, so starter numbers moved by 2. He has not given feedback on them yet.

## Stance by move (his rule, live Nov 23, first pass)
"Each stance has to be appropriate to its moves." Idle = the picked stance. Walk = Relaxed carry if the weapon has one, else Ready. Run = Ready. Punch = Ready and the free hand punches (mirrored clip punch_L when only the right hand holds a weapon). Action poses only on Idle. Code: moveNow / modeNow / moveFor in index.html. Not done yet: a real attack per weapon type, a carry for every weapon, blending between stances.

## Photo mode (live Nov 23)
photo.js. Photo button: freeze any move on any frame, stance, camera angles, lens, 7 backdrops, 3 lights, floor grid, Save picture / Share. index.html calls MF_PHOTO.init and reads MF_PHOTO.frozen.

## Paint (went live Nov 23)
Files: paint.js (all paint code), materials.js (379 skins, from the old forge), textures-bark.js (bark photos, Lynocs CC0). index.html calls MF_PAINT.init / dress / setOpen / frame.
Paint button, 5 tabs:
- Brushes: Color, Spray, Blotch, Fill, Gradient, Blend, Wear (worn edges, dirt, rust, scorch), Eraser, Pick colour. Paints with a colour or a skin, Glow paint, Both sides (off by default), Undo, swatches.
- Skins: colour scheme + My colours, skins on a whole colour slot, the picked part or marked parts.
- Mark: mark parts, fill marked, saved groups, paint by number, layer list (remove / bring to top).
- Decals: text, hazard stripes, stripe, star, chevrons, arrow, warning, roundel, bolt, cross.
- Light +: elements (skin + glow + grown bits), brightness, glow, night preview.
How it works: a piece is split finer the first time it is painted; paint lives in its points; brushed skins are see-through copies with a mask (4 per piece). Saved on the phone in 'mf-paint2'. Paint and decals leave when a different part goes in that spot; skins on a spot stay.
Phone layout: one scrolling bottom row, moves hide while painting, short panel, camera steps back so the mech sits above an open panel.

## Phone first (his rule, Nov 23)
He uses the phone mostly (Galaxy S23 Ultra). Every screen has a phone layout under 600px wide: tools row + moves row at the bottom, camera buttons behind the camera button (top right), short panels with rows that swipe sideways, part choices in one swipe row. The camera frames the mech in the free part of the screen (fitDist + coverPx in index.html). Root bug fixed Nov 23: the canvas used to go on the page wider than a phone, which made the phone lay the app out as a wide zoomed-out page; keep renderer.setSize before the canvas is added, and keep the pixel ratio cap of 2. Not yet tried on his real phone.

## Bots (run before pushing)
- python3 tools/bot/phone_bot.py -> must say ALL OK (every push)
- python3 tools/bot/paint_bot.py index.html  -> must say ALL OK (paint or phone-layout changes)
- python3 tools/bot/weapon_bot.py standard:0 heavy:1 brawler:4 squat:9 sleek:5 scout:6 -> 0 clips, 0 floating (anything that moves or holds parts; body:starter number, 0 = Hero, 1 = Walker)
- python3 tools/bot/shoulder_bot.py standard heavy -> all OK
They need playwright + chrome and three.js 0.170 at /tmp/t/node_modules/three (npm i three@0.170.0 in /tmp/t).
Last run Nov 23 4am on the live page: phone ALL OK, paint ALL OK, weapon 25/25 clean on all six bodies above, shoulder 72/72 ok on both.

## Next up, in order
1. His feedback from the real phone: does it now fit the screen, paint, the Hero + Walker sets, Photo mode (only the bots have tried it).
2. Stances: weapon attacks per weapon type (so Punch fits the weapon), a carry for every weapon, then the older notes (Relaxed shield closer, two sabers crossing). (Bazooka is done: it rests just above the shoulder part, level, clean on six bodies.)
3. Second pass on the sets from his notes; more variants per spot (his kit rule: think more than 3).
4. Item 7, More moves.
Parked ideas (Add-ons in PLAN.md): emblem editor, share codes, part scale / hide sub-pieces, diorama with several mechs, paint presets, Part Maker upgrades, more decals, bits slider, bloom + floating effects.

## Open questions for him (also at the bottom of PLAN.md)
- S3 Stance by move: are walk = carry low, run / punch = ready, free hand punches the right calls? What should Punch do for each weapon?
- S1 What looks off on the Hero + Walker sets?
- S2 Is the bazooka's new resting spot what he meant by 'flatter on the shoulder'?
- P1 What should change in paint after he tries it on the phone?
- P2 Keep the one-row phone layout? (default yes)
- P3 Joint caps follow the scheme's joint colour now. Keep? (default keep)
- P4 Which decals next? e.g. kill marks, squad logo, his own picture, glowing decals.
- P5 Element bits: 10-16 per part ok, or a "how many" slider?

## His rules that matter here
- Phone first: every screen must work on the phone; run the phone bot before every push (Nov 23).
- Every stance must fit the move being played (Nov 23).
- Go through changes with him before pushing; build together, floor by floor; show which skills are used.
- Don't rebuild the wheel: check free open-source first (MIT / Apache / BSD / CC0 only), credit in README.
- Check what he already has (Drive kits, project folders) before making or downloading assets.
- No screenshots or renders unless he asks. Links always clickable. Keep these docs up to date.
- Skills: build-together, pro-3d-workflow, game-art, ponytail, karpathy-guidelines, repo-scout. Model: Opus for most work.
