# S Pen numbers (measured on his Galaxy S23 Ultra)

Where this came from: DataBud's Tester Lab (the S Pen drills), first real test Nov 9 2026, 6:48-6:58 PM.
Phone: SM-S918U1, Android 16, One UI 8.5, screen in FHD+ mode (1080x2316). Added here Nov 27 2026.
Use these numbers when building pen support in Mythic Forge. Nothing in the app uses them yet.

## The numbers
| What | Measured | 
|---|---|
| Pressure, lightest touch | 0.005 |
| Pressure, pressing hard on purpose | 0.899 (never reached 1.0) |
| Pressure in normal relaxed drawing | tops out around 0.54 |
| Pressure steps in one stroke | about 1,000 different values (smooth, no visible stepping) |
| Tilt | 6 degrees (nearly upright) to 62 degrees (leaned right over) |
| Hover | works; held still in the air the tip wobbles about 1 mm |
| Side button | works while hovering and while drawing (Android button code 32) |
| Samples per second while drawing | about 575 |
| Longest gap between samples | 3-6 ms, never over 25 ms |
| Delay from pen to app | 2-3 ms (worst 8 ms) |
| Tap accuracy | about 1 mm off centre, worst 1.5 mm |
| Tracing a line | about 0.8 mm off the line |
| Fastest scribble | about 2,650 mm per second; biggest jump between two samples 3 mm |
| Air Actions (pen as a remote) | all 8 gestures arrive |
| Palm rejection | NOT settled: two runs let 5+ hand touches through while the pen was in use, one run was clean |

## What they mean for Mythic Forge
1. **Pressure needs a curve.** His normal drawing only reaches about half pressure. If a brush treats 1.0 as full,
   his lines stay thin and faint. Treat about 0.55 as full by default, and let hard presses (up to 0.9) go a little past.
2. **No smoothing needed for lag.** 575 samples a second with no gaps is plenty; a stroke only needs light smoothing
   for hand wobble (about 1 mm), not for missing data.
3. **Small targets are fine with the pen.** He lands within about 1 mm, so pen-only controls can be smaller than the
   44px finger size. Finger controls stay 44px.
4. **Tilt is usable** (a 56 degree range): e.g. lean the pen for a wider spray.
5. **Side button is free to use** as a quick action (he asked on Nov 9 for one he picks, e.g. eraser or pick colour).
6. **Don't trust the phone's palm rejection.** Mythic Forge should ignore finger touches for brushes while the pen is
   near (pen seen in the last second or so), and keep two-finger camera moves working.
7. **Hover** can show the brush ring before the pen touches.

## Not checked yet
- These were measured inside an Android app. Mythic Forge is a web page, and the browser passes pen data on its own
  way (pointer events: pressure 0-1, tilt in degrees, pen button, hover). The scale should match, but it has not been
  measured in the browser. First step of any pen work: a tiny "test my pen" readout on the test page to confirm.
- Palm rejection needs 2-3 more DataBud runs to know how often hand touches get through.
- Nothing measured on the PC or with a drawing tablet.

## Where the code would go (for whoever builds it)
- paint.js: the brush pointer handlers (pointerdown / pointermove / pointerup near the top-level `el.addEventListener`
  calls) are where pressure, tilt, pen-only strokes and the hover ring plug in.
- maker.js: the Part Maker pad (`cv.onpointerdown` / `onpointermove`) for pen lines.
- The raw strokes behind these numbers are in DataBud's Lab report / pen data file (not copied here; too big).
