# Mythic Forge — Handoff (updated Nov 23 2026, 1:40am)

Read this first in a new chat. The full plan, rules and log are in PLAN.md.

## Where things are
- Live app: https://majoraspride.github.io/mythic-forge/
- Repo: MajorasPride/mythic-forge (GitHub Pages serves the main branch). Never his real name anywhere public.
- His PC copy (C:\Users\cc492\Documents\Personal Claude\mythic-forge) is a plain folder, NOT a git clone, and is behind GitHub since Nov 23. GitHub is the truth. Sync it only when he connects that folder.
- The old Mythic Forge (creatures, 70 bodies) lives in the titan-clash repo under myth-forge/. This repo is the fresh start (mechs first).

## What is live
Standard mech frame + moves (idle, walk, run, punch), Body presets + sliders, Build (body parts for every spot, backpack, weapons, stances), Details, Part Maker, Starter mechs, Random, and since Nov 23: Paint.

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

## Bots (run before pushing)
- python3 tools/bot/paint_bot.py index.html  -> must say ALL OK (paint or phone-layout changes)
- python3 tools/bot/weapon_bot.py standard:0 -> 0 clips, 0 floating (anything that moves or holds parts)
- python3 tools/bot/shoulder_bot.py standard -> all OK
They need playwright + chrome and three.js 0.170 at /tmp/t/node_modules/three (npm i three@0.170.0 in /tmp/t).
Last run Nov 23 on the live page: paint ALL OK, weapon 25/25 clean, shoulder 56/56 ok.

## Next up, in order
1. His phone feedback on paint (not tested on a real phone yet, only the bot).
2. Bazooka stance fix: flatter on the shoulder, weapon bot must be fully clean on every body (it clipped on some bodies; only standard:0 was re-run Nov 23).
3. Other stance notes: Relaxed shield closer, two sabers crossing.
4. Hero / Heavy part sets (bigger hero torso; hero foot with taller heel, shorter toe). His heavy-set references: BattleTech-style walkers, Archax.
5. Item 7, More moves.
Parked ideas: Part Maker upgrades (angled cuts, depth + layering, stamps, trace a picture, undo + snap, export), more decals, bits slider. See Add-ons in PLAN.md.

## Open questions for him (also at the bottom of PLAN.md)
- P1 What should change in paint after he tries it on the phone?
- P2 Keep the one-row phone layout? (default yes)
- P3 Joint caps follow the scheme's joint colour now. Keep? (default keep)
- P4 Which decals next? e.g. kill marks, squad logo, his own picture, glowing decals.
- P5 Element bits: 10-16 per part ok, or a "how many" slider?

## His rules that matter here
- Go through changes with him before pushing; build together, floor by floor; show which skills are used.
- Don't rebuild the wheel: check free open-source first (MIT / Apache / BSD / CC0 only), credit in README.
- Check what he already has (Drive kits, project folders) before making or downloading assets.
- No screenshots or renders unless he asks. Links always clickable. Keep these docs up to date.
- Skills: build-together, pro-3d-workflow, game-art, ponytail, karpathy-guidelines, repo-scout. Model: Opus for most work.
