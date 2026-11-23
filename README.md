# Mythic Forge

Build your own mechs (and later monsters), snap armor on, test their moves, and send them to Titan Clash.
Fresh start, Nov 2026. Start here: [HANDOFF.md](HANDOFF.md). Plan, rules and log: [PLAN.md](PLAN.md).

Open `index.html` in a browser. Frames and moves are made in Blender by the scripts in `tools/blender/`.

Paint (live since Nov 23 2026; `paint.js` + `materials.js`): (skins, brushes, Blend, weathering, gradient, decals, Mark, layers, elements, glow / night). Phone test bot: `python3 tools/bot/paint_bot.py`. Paint code: `paint.js`; skins: `materials.js` (brought over from the old Mythic Forge in the titan-clash repo).

Photo mode: `photo.js`. Body parts are made in Blender from code: `tools/blender/parts_all.py` (uses the Blender `bpy` Python module, GPL, as a build tool only; nothing from Blender ships in the app).

## Credits
- three.js (MIT): rendering, OutlineEffect, TessellateModifier (smooth brush paint), DecalGeometry (decals).
- Tree bark photos in `textures-bark.js`: "Texture Pack" by Lynocs (https://lynocs.itch.io/texture-pack), CC0 1.0.
