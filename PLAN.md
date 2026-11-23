# Mythic Forge (fresh start) — Plan & Rules

## Now
Nov 23 (after midnight): Paint port (item 2b) F1-F5 + round 2 + round 3 are on the TEST page only (test.html, live index untouched). He said his phone screen 'can't see everything' and 'run a bot': fixed the phone layout and added tools/bot/paint_bot.py (ALL OK). Waiting for his look on the phone before paint goes into index.html (see Questions at the bottom). Bazooka stance fix still waiting after it.
Nov 22 late: items 1-6 + Part Maker are LIVE. Next: bazooka stance fix (bot must go clean), then the other stance notes (Relaxed shield closer, two sabers crossing), then 7 More moves.
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
5. Weapons (his T044 Weapons kit + 2 new): 17 hand weapons (9 swords/axes/lances, 4 guns, 4 shields) and 4 shoulder weapons; each hand + each shoulder has its own spot; shields strap on the forearm; picking one makes the hand grip; starters come with his kit's loadouts - LIVE Nov 22. Easy to reach: Weapons row in Build (Right hand / Left hand / Shoulders). Wrists auto-bend so held weapons point forward and out, hand weapons are sized to the arm, shields to the forearm. Later: leg pods, rocket fist, back-mounted weapons, weapon moves (with 7).
6. Details (made in Blender with his kit's shape tools, tools/blender/parts_details.py): 21 in 5 groups (Antennas, Vents, Spikes, Fins, Emblems). Details button: pick one, tap the mech, it sticks flat on that spot and moves with that body part; Size, Turn, Mirror (on by default), Delete, Clear all; saved; takes the paint - LIVE Nov 22. Known gap: changing body sliders after placing can leave a detail a little off the surface (re-tap to fix); fix later by re-dropping onto the surface.
2b. Paint port (his ask Nov 22 late: "all the paint we had before + the ideas for it, blending etc, from old Mythic Forge"). Copy, don't rebuild: old code lives in titan-clash/myth-forge (materials.js = 379 skins in 31 groups, self-contained FORGE_MATS {LIST, makeMat, tex}, triplanar so no UVs needed; brushes in forge-core.js paintStroke / skinStroke / eraseStroke / blendStroke; Mark groups in forge-m.js). Floors, each shown before push:
   F1. Skins + light: copy materials.js; pick a skin for a whole colour slot (Main / Second / Trim / Frame) or for one picked body part; skin groups incl. Ethereal + animated FX skins; Brightness slider (40-120%, default 85%). Saved with the build.
   F2. Brushes: Color, Spray can (Mist slider), Blotch, Eraser; Size / Strength; Both sides toggle (OFF by default); Undo. Paint saved with the build and follows slider reshaping.
   F3. Skin brush + layers: brush a skin on (up to 4 brushed skins per part, newest on top); Blend mixes colours and skin tones over the whole mech across part edges, softening only the top overlay where one exists.
   F4. Mark: mark several parts (both arms, all armor...), paint them together, save named groups.
   F5. Old extras: Glow slot + Night preview, Paint by number (numbered panels), Element on a part (lava, ice, crystal...).
   BUILT Nov 22 night (test.html, all floors at once, he said "work on it all"): paint.js + materials.js + textures-bark.js. Paint button opens a panel with 4 tabs:
     Brushes (Color, Spray + Mist, Blotch splats with droplets, Fill = tap a piece, Blend, Eraser; Size / Strength; Paints with colour or a skin; Glow paint; Both sides off by default; Undo 25 steps; Clear picked / all). The mech holds still and one finger paints while a brush is on; two fingers or the view buttons move the camera.
     Skins (colour scheme + My colours moved here from Build; Put on: Whole mech Main / Second / Trim / Frame / Glow bits, Picked part, Marked parts; 31 groups; pattern size; Clear skins). Tap a part (brush Off) to pick it (yellow box).
     Mark (tap to mark, cyan boxes; Fill marked; save / load / delete named groups; Paint by number = numbered pieces on the picked part, tap a number to fill it).
     Light + (Elements on picked / marked parts: Lava, Fire, Stone, Crystal, Forest, Water, Ice, Storm, Lightning, Cosmic, Gold, Sand, Void = skin + glow colour; Brightness; Glow strength; Night preview).
     How it works: a part piece is split finer (TessellateModifier) the first time it's painted; paint lives in its vertices (colour + cover + glow); brushed skins are see-through copies on top with a mask, up to 4 per piece, newest on top; Blend mixes colours and skin tones across part edges and only softens a skin overlay's edge where one is on top. Saved on the phone in 'mf-paint2' (squeezed); paint stays with a spot until a different part goes on it; skins on a part stay through part swaps.
     Round 2 (Nov 22 late): the gray stand-in blocks, the waist and the joint caps take skins + brushes too (frame pieces are remade with a fixed number of points, so their paint stays on when the Body sliders move); details take brushes (each detail got a lasting id, d.uid). Picked / marked boxes and paint by number work on all of them. Old "grow element bits" (lava rocks etc.) not brought over, elements are skin + glow only.
     Round 3 (Nov 23, he said "build what you can"), all on test.html:
       Phone fit: on a narrow screen the bottom bar is ONE scrolling row, the move buttons + Bones hide while Paint is open, the paint panel is short (rows scroll sideways), view buttons are smaller, and the camera steps back so the whole mech sits above an open panel (fitDist in test.html: screen shape + open panel). A tap is timed by the event's own clock so a slow frame can't turn it into a long press.
       Paint bot: python3 tools/bot/paint_bot.py [page]. S23 Ultra screen (384x824), real touch events. Checks the mech fits above the panel, every control in all 5 tabs can be reached, every brush paints with a finger, undo, pick colour, gradient, skin brush, skins, tap to pick, layer list, elements + bits, mark + fill marked, decals, and that paint / decals / bits come back after a reload. It caught a real bug (a freshly painted part got its brushed skins doubled on the next recolour) - fixed.
       New brushes: Gradient (tap a part: fades from the colour to a second colour; top-bottom / outside-middle / front-back), Wear (Worn edges = bare metal only along hard edges, Dirt, Rust streaks, Scorch), Pick colour (eyedropper), colour swatches (scheme colours + last 8 used).
       Decals tab (three.js DecalGeometry, MIT): Text (up to 8 letters, e.g. 01), Hazard stripes, Stripe, Star, Chevrons, Arrow, Warning, Roundel, Bolt, Cross. Pick one, tap the mech; Size / Turn keep changing the one just placed; Both sides; Remove last / Clear picked part / Clear all. Decals wrap onto the surface, ride on the part's pieces (move + stretch with it), are saved, and go away when a different part is put in that spot.
       Layer list (Mark tab): what's brushed on the picked part (each brushed skin, Colour paint, Glow) with remove, and bring-to-top for skins. A 5th skin on a piece now reuses an emptied layer first.
       Element bits (the old forge's "grow element bits"): an element on a part grows 10-16 small pieces on it (Lava / Stone / Gold rocks, Ice / Crystal crystals, Fire flames, Water drops, Storm puffs, Lightning / Void shards, Cosmic floating stars, Forest / Sand mounds). Same spots every time (seeded), saved; "Grow bits" button turns them off.
       Checked: paint bot ALL OK; weapon bot standard:0 25/25 clean and shoulder bot standard 56/56 ok on test.html.
   New paint ideas: gradient fill, eyedropper, swatches, decals, weathering brushes and the layer list are BUILT (round 3). Still ideas: your own picture as a decal, kill marks / squad logos, bits density slider, glow decals, paint on the live page's Photo mode.
6b. Part Maker (his idea Nov 22, 'the best for Mythic Forge'; pulled out of Add-ons) - LIVE Nov 22. Make button opens a sketch pad: pick the spot, build from Box / Wedge / Taper / Cylinder + Pen lines in linked front / side / top / 3D views. Drag empty space = new shape, drag a shape = move, yellow corner = resize, tap = select; Copy / Delete / Undo / Clear; colours Frame / Main / Second / Trim / Glow (Paint still recolours). Save + put it on: the part shows as a star in Build, plugs into the same joint as the kit's parts (sized and centred like the spot's first kit part), right side mirrored, saved on the phone (localStorage mf-myparts), edit or delete from the pad. Shapes are beveled in Blender (tools/blender/maker_shapes.py -> models/maker_shapes.js). Next: send a part to Blender for extra polish; shape turning; lines that follow a moved shape.
7. More moves: hit, block, jump + heavy landing, knockdown; fast style: boost dash, sidestep, rolling dodge
8. Photo mode: pose, background, save a picture
9. Sounds: stomps, servo whirs (Sound Lab idea)

## Add-ons (parking lot, reviewed at the end of each phase)
- Part Maker upgrades (Nov 22 ideas): angled cuts / chamfers (three-bvh-csg, MIT), side view depth + plate layering, detail stamps (vents, bolts, panel lines, hatches), trace a reference picture behind the pad, undo/redo + grid snap, colour per shape, export a part (.json / .glb).
- Cool-look phase (Nov 22, his references: comic-inked Gunpla, RX-78/Jegan/Zaku/GM): bold ink lines (three.js fat lines), colour blocking, bulk, then redesign parts as layered plates. He'll draw parts on the design pad (real -> shapes -> joints -> elaborate).
- UI from noclip.website (MIT): hide-all-UI key for Photo mode, fly camera (drag look, WASD, Shift faster), slide-out side panels. OMGLORD = colour/UI inspiration only.
- Asset sources checked Nov 22: TheBaseMesh (CC0) has no body parts; only Kitbash A-F (61) + 2 breastplates - he said nothing for us right now. Quaternius Animated Mech Pack (CC0) is in his Drive - not wanted for now.
- More bulk (Nov 22): he wants beefier robots overall; parked, he said not now.
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
Paint port: build-together, ponytail, karpathy-guidelines, game-art.
build-together, pro-3d-workflow, game-art, ponytail, repo-scout. Model: Opus.

## Rules
- Before pushing anything that moves or holds parts, run the weapon bot (tools/bot/weapon_bot.py); it must be 0 clips and 0 floating; shoulder_bot.py must be all OK.
- Go through changes with him before pushing.
- Rebuild the Part Maker shapes after changing them: python3 tools/blender/maker_shapes.py.
- Never his real name anywhere public (use MajorasPride).
- Original work only; outside assets/libraries must be MIT/Apache/BSD/CC0 and go in the credits list.
- The old Mythic Forge ("Classic", inside the titan-clash repo) is frozen: nothing from it comes back unless he asks.
- Keep this file correct; update Now and the Log every session.

## Log (newest first)
- Nov 22 (late): Part Maker built and pushed with Weapons, Details and stances (he said push). Bots: weapon bot clean on standard:0, brawler:2; fixed whip hitting the floor (arm lifts when a weapon dips below the floor) and axe/hammer hitting the shoulder on punch (arm lifts using a pad box that turns with the pad); bot no longer calls stand-mounted shoulder weapons 'floating'. Shoulder bot 56/56 OK. KNOWN, he OK'd pushing anyway: bazooka still clips its shoulder/upper arm on punch and run (standard:2, heavy:0, squat:7) - fix next with his 'bazooka flatter on the shoulder' note.
- Nov 22: feet toned down (he: 'a little wild'). foot_hero built from his Gundam foot reference (white ankle ring, blue wedge sloping to the toe, heel block, raised arch). He sent a 10-foot concept sheet (nomansnodead/dipo_muh) - use as inspiration only for our own foot variants (treads, claws, pistons, wedge, dome toe).
- Nov 22: he chose BOTH base sets on one skeleton: Hero (Gundam) + Heavy (BattleTech/Archax walker, his refs). First parts: torso_hero (V chest, intakes, hatch, collar, abs) and torso_walker (box torso, cockpit band, missile rack, vents, belly). Waist block now dark frame; shoulder pads 2.6. Next: his feedback on the chests, then pelvis/skirt, shoulders, legs for each set.
- Nov 22: step 1 'bold silhouette' started from his Gundam base reference (FM/RE100 RX-78 line art): thicker limbs in frame.js, wider waist block, small elbow/knee caps, bigger shoulders and feet, new 'gundam' body preset. Slider tuning hits a ceiling: the kit's chest/pelvis are too small and clamped. Next: build a Gundam-base part set in Blender to his reference (tall boxy chest + collar, abs block, big skirt, box shoulders touching the chest, long box thighs, flared calves + ankle guard, box feet, bigger fists), shown part by part. Bots not rerun since these shape changes.
- Nov 22: Stance: Action added (full-body action poses from his reference photos: slash wind-up, overhead katana, great-sword wind-up, lance charge, whip crack, side-on pistol, rifle aim in a lunge, braced gatling, kneeling bazooka, braced shield). Hips drop/lift so feet stay on the floor. Ink lines on part edges are on (thin, 1px; fat lines later). Bot pass on Action still to do.
- Nov 22: weapon stances built from his reference photos (Gunpla/anime): Ready = rifle two hands across chest, katana two hands blade up, energy sword raised back over the shoulder, heavy weapons on the shoulder two-handed, lance tucked, gatling chainsaw grip at hip, bazooka resting on the shoulder (arm lifts itself clear of the pad), pistol aimed, shield low in front. Relaxed = rifle/pistol hanging by the leg, sword down, shield upright at the side. Stance switch in Build. Off hand grabs two-handed weapons (2-bone reach). 4 more shoulder weapons (radar dome, mini gatling, flare launcher, saber rack). Bots: clean except small touches (squat bazooka during punch/run, whip on brawler while running) - next pass.
- Nov 22: action poses (attack moves) researched for item 7: anticipation -> strike -> hold -> recovery; heavy machines sell weight in the wind-up and the return.
- Nov 22 (his sketch): spiked roller tipped 40 deg out so its spikes fan up and out; shoulder weapons always sit on top, and on a bumpy top (spikes, fins) they ride on a stand with 4 legs above the bumps. Side mounts + brackets tried and dropped (not what he meant). Lesson: when he says 'to the side', ask for a sketch early. Sketch pad: inline widget with Send to Claude (strokes come back as text).
- Nov 22: item 6 Details built (21 details).
- Nov 22: floating fixed (shoulder weapons now stand on the real top-middle of the shoulder part and step forward/out only if a backpack is in the way; shields flush on the forearm; guns back in the grip). Bot now also checks nothing floats, and uses boxes that turn with each part (straight boxes gave false clips when the chest twisted). Mistake logged: test attachment, not just clipping.
- Nov 22: run 'tearing' fixed: Blender keys start at frame 1, so every loop froze a frame then snapped; moves now shifted to start at 0 (copy the shared time list first, or it stacks). Weapon clip bot (tools/bot/weapon_bot.py): 21 weapons x 6 body types x 4 moves, left and right, 0 clips with any body part or the floor.
- Nov 22: item 5 Weapons built (tools/blender/parts_weapons.py -> models/parts_weapons.js, 400 KB). Checked by numbers: weapons sit in the hands pointing forward, shields on the outside of the forearm, pods on the shoulder tops, saves and reloads, no errors.
- Nov 22, 2026: he said some heads still look off. Cause: heads were stretched so crests/horns/antennae counted as head height (Titanheart's face got squashed, Bulwark got big). Now every head uses one even size and crests stick up. Pushed with his OK.
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

## Questions for him (answer when you can; nothing here blocks the next step)
- P1 (Nov 23) Paint is only on the test page. After you try it on the phone: move it into the live Mythic Forge as is, or change things first?
- P2 (Nov 23) Phone layout on the test page: one scrolling button row at the bottom, and the move buttons hide while you paint. Keep that for the live page too? (Default: yes.)
- P3 (Nov 23) Joint caps (elbows, knees) now take the colour scheme's joint colour instead of always dark gray. Keep? (Default: keep.)
- P4 (Nov 23) Decals: which emblems do you want next? Examples: kill marks, squad logo, your own picture, glowing decals. (Default: wait for your picks.)
- P5 (Nov 23) Element bits: is 10-16 pieces per part the right amount, or do you want a "how many" slider? (Default: leave as is.)
