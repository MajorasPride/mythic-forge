# Mythic Forge

Build your own mechs (and later monsters), snap armor on, test their moves, and send them to Titan Clash.
Fresh start, Nov 2026. Plan, rules and log: [PLAN.md](PLAN.md).

Open `index.html` in a browser. Frames and moves are made in Blender by the scripts in `tools/blender/`.

Paint test page (not live yet): `test.html` (skins, brushes, Blend, weathering, gradient, decals, Mark, layers, elements, glow / night). Phone test bot: `python3 tools/bot/paint_bot.py`. Paint code: `paint.js`; skins: `materials.js` (brought over from the old Mythic Forge in the titan-clash repo).

## Credits
- three.js (MIT): rendering, OutlineEffect, TessellateModifier (smooth brush paint), DecalGeometry (decals).
- Tree bark photos in `textures-bark.js`: "Texture Pack" by Lynocs (https://lynocs.itch.io/texture-pack), CC0 1.0.
