# Mythic Forge body parts: EVERY SPOT (Nov 22 2026). Run with the bpy module: python3 parts_all.py
# Uses his own Mech Kit (T042, mech_kit_R2.py from Nov 13, kept next to this file): same builder (inner frame +
# armor, bevelled edges, no perfectly cut edges) and the same original designs, plus a few new ones so every
# spot has at least 4 choices. Output: ../../models/parts_all.js (all parts, both sides) for Mythic Forge.
# How each spot fits (the app stretches parts to the mech's body shape):
#   box      chest / head / pelvis: stands on its bottom, centred, stretched to the spot's box
#   limb     upper arm / forearm / hand / thigh / shin: hangs from its joint, stretched along the bone
#   anchor   shoulder / foot: keeps the kit's own joint point, scaled to the mech's size
import bpy, os, json, base64, math
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "mech_kit_R2.py")).read()
src = src.split("# ---------------------------------------------------------------- assemble a mech")[0]   # parts only, no demo builds
NS = {"__file__": os.path.join(HERE, "mech_kit_R2.py")}
exec(compile(src, "mech_kit_R2.py", "exec"), NS)
PB, part, PARTS, R = NS["PB"], NS["part"], NS["PARTS"], NS["R"]
UA_PLUGS, TH_PLUGS, HAND_PLUGS = NS["UA_PLUGS"], NS["TH_PLUGS"], NS["HAND_PLUGS"]

# ---- new parts so every spot has 4+ choices (original designs)
@part("upperarm_piston", "upperarm", "Piston upper arm", "Open frame with twin hydraulic pistons and a top cap.", UA_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .11, .18, 'X', 8); F.box("frame", (0, 0, -.32), (.18, .20, .50), (1, 1), .02)
    for s in (-1, 1): A.cyl("joint", (s*.09, -.05, -.32), .035, .44, 'Z', 6)
    A.box("armor", (0, .02, -.14), (.26, .26, .18), (1, 1), .03); A.box("armor2", (0, .02, -.50), (.24, .24, .12), (1, 1), .02)
@part("upperarm_plated", "upperarm", "Plated upper arm", "Three stacked armour bands, knight style.", UA_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .10, .16, 'X', 8); F.box("frame", (0, 0, -.32), (.16, .18, .50), (1, 1), .02)
    for i in range(3): A.box("armor" if i % 2 == 0 else "armor2", (0, 0, -.14-i*.15), (.28-i*.01, .28-i*.01, .13), (.95, .95), .03)
@part("thigh_piston", "thigh", "Piston thigh", "Exposed frame with a big hydraulic ram on the front.", TH_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .14, .25, 'X', 8); F.box("frame", (0, 0, -.46), (.22, .24, .76), (1, 1), .02)
    A.cyl("joint", (0, -.15, -.46), .06, .62, 'Z', 8); A.cyl("armor2", (0, -.15, -.30), .085, .26, 'Z', 8)
    A.box("armor", (0, .06, -.40), (.30, .20, .62), (1.1, 1), .04)
@part("thigh_knight", "thigh", "Knight thigh", "Plated thigh with a hanging tasset plate.", TH_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .13, .24, 'X', 8); F.box("frame", (0, 0, -.46), (.20, .22, .76), (1, 1), .02)
    A.box("armor", (0, -.01, -.48), (.32, .34, .56), (1.1, 1.05), .05)
    A.box("armor2", (0, -.20, -.16), (.30, .05, .30), (1.15, 1), .02); A.box("accent", (0, -.23, -.04), (.30, .02, .04), (1, 1), 0)
@part("hand_claw", "hand", "Claw hand", "Three long talon fingers for beast and bio mechs.", HAND_PLUGS, side=True)
def _(F, A):
    HS = NS["HS"]
    F.cyl("joint", (0, 0, -.02*HS), .06*HS, .10*HS, 'X', 6)
    A.box("armor", (0, -.01*HS, -.11*HS), (.16*HS, .12*HS, .14*HS), (1.05, 1), .02*HS)
    for x in (-.05, 0, .05):
        A.box("armor2", (x*HS, -.03*HS, -.25*HS), (.035*HS, .04*HS, .16*HS), (.8, .8), .004*HS, rot=Matrix.Rotation(R(-18), 3, 'X'))
        A.box("accent", (x*HS, -.08*HS, -.37*HS), (.03*HS, .035*HS, .09*HS), (.2, .4), 0, rot=Matrix.Rotation(R(-35), 3, 'X'))

# ---- BASE SETS (Nov 22): "Hero" (Gundam real-robot, his RX-78 reference) and "Heavy" (BattleTech / Archax walker, his references)
TP = NS["torso_plugs"]
RX = lambda d: Matrix.Rotation(R(d), 3, 'X')
RY = lambda d: Matrix.Rotation(R(d), 3, 'Y')
@part("torso_hero", "torso", "Hero chest", "Hero chest: big chevron plate over a blue upper block, yellow intakes, cockpit hatch, tall collar, narrow red abs.", TP(.58, .90, 1.10, .34))
def _(F, A):
    F.box("frame", (0, .02, .66), (.62, .48, .60), (1.2, 1))
    A.box("armor2", (0, -.02, .80), (1.0, .64, .46), (1.2, 1.0), .05, front=(.94, 1))    # upper chest block, wide at the shoulders
    A.box("armor", (0, -.02, .50), (.70, .54, .24), (1.32, 1.08), .04)                   # rib block, narrows toward the waist
    A.fin("armor", (0, -.355, .64), [(0, 0), (.50, .30), (.50, .42), (0, .15), (-.50, .42), (-.50, .30)], .05)   # big chest chevron
    A.box("accent", (0, -.335, .60), (.20, .05, .16), (1.25, 1), .02)                    # cockpit hatch under the chevron's point
    for s in (-1, 1):
        A.box("accent2", (s * .30, -.335, .705), (.24, .04, .10), (1, 1), .012, rot=RY(s * -31))     # intakes, tucked under the chevron wings
        for i in range(2): A.box("frame", (s * (.26 + i * .09), -.36, .67 + i * .055), (.07, .02, .05), (1, 1), 0, rot=RY(s * -31))
        A.box("armor", (s * .47, -.02, .70), (.07, .50, .30), (1, 1), .015)              # side plates
    A.box("armor", (0, .01, 1.085), (.56, .48, .14), (.8, .85), .03)                     # tall collar
    A.box("accent2", (0, -.20, 1.06), (.16, .04, .07), (1, 1), .01)
    A.box("accent", (0, -.05, .27), (.40, .40, .16), (1.1, 1), .03)                      # abs
    A.box("accent", (0, -.04, .11), (.32, .36, .14), (1.1, 1), .03)
@part("torso_walker", "torso", "Walker torso", "BattleTech / Archax heavy: huge box torso, sunk cockpit, missile rack, vents.", TP(.68, .82, 1.02, .42))
def _(F, A):
    F.box("frame", (0, .02, .62), (.80, .62, .60), (1.05, 1))
    A.box("armor", (0, -.02, .62), (1.16, .84, .74), (1.04, .82), .06, front=(1, .92))
    A.box("armor2", (0, -.43, .86), (.46, .05, .17), (1, 1), .02)                        # cockpit band
    A.box("glow", (0, -.46, .86), (.36, .01, .07), (1, 1), 0)
    A.box("armor2", (-.32, -.42, .54), (.34, .07, .30), (1, 1), .02)                    # missile rack
    for i in range(3):
        for j in range(2): A.cyl("joint", (-.42 + i * .1, -.465, .48 + j * .12), .035, .03, 'Y', 6)
    for i in range(4): A.box("frame", (.32, -.43, .44 + i * .07), (.30, .03, .035), (1, 1), 0)   # vent slats
    A.box("accent", (.32, -.43, .74), (.30, .02, .05), (1, 1), 0)
    A.box("armor2", (0, -.10, .21), (.62, .62, .20), (1.12, 1), .03)                       # belly
    A.box("armor2", (0, .06, 1.02), (.80, .60, .08), (.95, .95), .02)                      # roof
    for s in (-1, 1): A.box("armor2", (s * .60, -.02, .62), (.08, .70, .50), (1, 1), .02)  # side armor

@part("foot_hero", "foot", "Hero foot", "Gundam foot (his reference): ankle guard ring, long wedge foot sloping to the toe, heel block, open arch.", NS["FT_PLUGS"], side=True)
def _(F, A):
    F.ball("joint", (0, 0, 0), .10, 8)
    A.box("armor", (0, .02, .05), (.27, .29, .12), (1.02, 1.02), .03)                       # ankle guard ring
    A.box("armor", (0, -.17, .0), (.20, .06, .16), (1, 1), .02, rot=Matrix.Rotation(R(18), 3, 'X'))   # front flap
    A.box("accent", (0, -.10, -.09), (.26, .48, .24), (.86, .42), .03, front=(.78, .5), shift=(.12, 0))   # tall wedge, top pushed back so it slopes down to the toe
    A.box("accent", (0, -.35, -.185), (.22, .16, .07), (.8, .5), .02)                        # shorter toe tip (his note Nov 22)
    A.box("accent", (0, .19, -.11), (.24, .18, .22), (.88, .75), .02)                        # taller heel block (his note Nov 22)
    A.box("frame", (0, -.05, -.20), (.18, .16, .03), (1, 1), .005)                            # arch (sits up off the ground)

# ---- HERO SET, the rest (Nov 23): sharp V shapes, layered plates, skirts, calves that widen toward the ankle. Original designs.
BK, SHP, FAP, SNP, FTP, HDP, PVP = NS["BACK_PLUGS"], NS["SH_PLUGS"], NS["FA_PLUGS"], NS["SN_PLUGS"], NS["FT_PLUGS"], NS["HEAD_PLUGS"], NS["PELVIS_PLUGS"]
@part("head_hero", "head", "Hero head", "Hero helm: wide visor, four-prong fin, chin guard, ear vents, back ridge.", HDP)
def _(F, A):
    F.cyl("joint", (0, 0, .06), .09, .14, 'Z', 6); F.box("frame", (0, 0, .24), (.24, .26, .22), (1, 1), .02)
    A.box("armor", (0, .02, .29), (.31, .35, .27), (.82, .88), .04)
    A.box("armor2", (0, -.165, .20), (.17, .06, .11), (.7, 1), .015)                      # lower mask
    A.box("accent2", (0, -.185, .145), (.10, .04, .05), (.8, 1), .01)                     # chin guard
    A.box("joint", (0, -.172, .30), (.26, .02, .075), (1, 1), 0)                          # visor recess
    A.box("eye", (0, -.182, .30), (.22, .01, .04), (1, 1), 0)
    A.box("accent2", (0, -.19, .385), (.055, .03, .055), (1, 1), .01)                     # forehead camera
    A.fin("accent", (0, -.195, .40), [(0, 0), (.25, .19), (.20, .20), (0, .06), (-.20, .20), (-.25, .19)], .03)   # main V (kept low so the helm itself stays big)
    A.fin("accent", (0, -.195, .385), [(0, 0), (.22, .05), (.20, .08), (0, .04), (-.20, .08), (-.22, .05)], .03)  # low prongs
    for s in (-1, 1):
        A.box("armor2", (s * .175, .02, .27), (.05, .17, .13), (1, .7), .012)             # ear vents
        for i in range(2): A.box("frame", (s * .203, .02, .245 + i * .05), (.01, .11, .02), (1, 1), 0)
    A.box("armor2", (0, .07, .435), (.06, .26, .05), (1, .8), .015)                       # back ridge

@part("pelvis_hero", "pelvis", "Hero skirt", "Split front skirts that kick out, V crotch block, side and rear skirts, belt.", PVP)
def _(F, A):
    F.box("frame", (0, 0, 0), (.52, .36, .28), (1.1, 1)); F.cyl("joint", (0, 0, -.06), .1, .64, 'X', 8)
    A.box("armor2", (0, 0, .115), (.60, .42, .08), (1.02, 1.02), .02)                     # belt
    A.box("accent2", (0, -.22, -.01), (.13, .10, .27), (1.3, 1), .02)                     # crotch block
    A.fin("accent", (0, -.28, .03), [(0, 0), (.075, .08), (.055, .09), (0, .03), (-.055, .09), (-.075, .08)], .02)
    for s in (-1, 1):
        A.box("armor", (s * .18, -.25, -.14), (.27, .06, .48), (1, 1), .025, rot=RX(-10), front=(.9, 1))   # front skirt
        A.box("accent2", (s * .18, -.318, -.29), (.16, .02, .08), (1, 1), 0, rot=RX(-10))
        A.box("armor", (s * .385, 0, -.15), (.08, .44, .50), (1, 1), .025, rot=RY(s * 10))                 # side skirt
        A.box("armor2", (s * .44, .02, -.20), (.02, .22, .22), (1, 1), 0, rot=RY(s * 10))
    A.box("armor", (0, .24, -.12), (.48, .06, .44), (1.15, 1), .025, rot=RX(9))           # rear skirt

@part("shoulder_hero", "shoulder", "Hero pauldron", "Box pauldron with a sloped top, front vents, outer stripe and an under-thruster.", SHP, side=True)
def _(F, A):
    F.cyl("joint", (.08, 0, 0), .15, .22, 'X', 8)
    A.box("armor", (.22, 0, .08), (.50, .56, .38), (.64, .86), .05)                       # sloped: narrow top, wide bottom edge
    A.box("armor2", (.20, 0, .285), (.26, .40, .05), (.9, .9), .015)                      # top cap
    A.box("accent", (.465, 0, .03), (.03, .40, .10), (1, 1), 0)                           # outer stripe
    for i in range(2): A.box("frame", (.22, -.285, .0 + i * .08), (.26, .02, .035), (1, 1), 0)   # front vents
    A.box("frame", (.24, 0, -.125), (.30, .36, .05), (1, 1), .01); A.box("glow", (.24, 0, -.155), (.20, .24, .01), (1, 1), 0)

@part("upperarm_hero", "upperarm", "Hero upper arm", "Two-piece sleeve with a gap that shows the frame, side marker.", UA_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .10, .16, 'X', 8); F.box("frame", (0, 0, -.32), (.16, .18, .50), (1, 1), .02)
    A.box("armor", (0, -.01, -.21), (.25, .27, .26), (1.08, 1.05), .03)
    A.box("armor2", (0, -.01, -.47), (.23, .25, .14), (1, 1), .025)
    A.box("accent", (.13, 0, -.21), (.02, .16, .14), (1, 1), 0)

@part("forearm_hero", "forearm", "Hero forearm", "Gauntlet that widens toward the wrist, elbow guard, side hardpoint, wrist ring.", FAP, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .11, .22, 'X', 8); F.box("frame", (0, 0, -.36), (.16, .18, .56), (1, 1), .02)
    A.box("armor", (0, -.01, -.40), (.30, .32, .46), (.84, .88), .04)
    A.box("armor2", (0, .11, -.03), (.20, .14, .20), (.8, .8), .03)                       # elbow guard
    A.box("accent", (.155, -.01, -.40), (.02, .14, .26), (1, 1), 0); A.cyl("joint", (.172, -.01, -.40), .04, .03, 'X', 6)
    A.box("armor2", (0, -.01, -.635), (.26, .28, .05), (1, 1), .012)                      # wrist ring

@part("thigh_hero", "thigh", "Hero thigh", "Thigh that widens toward the hip, raised front plate, side marker.", TH_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .13, .24, 'X', 8); F.box("frame", (0, 0, -.46), (.20, .22, .76), (1, 1), .02)
    A.box("armor", (0, -.01, -.42), (.30, .33, .60), (1.18, 1.1), .04)
    A.box("armor2", (0, -.18, -.40), (.18, .03, .40), (1.12, 1), .015)
    A.box("accent", (.165, 0, -.30), (.02, .18, .16), (1, 1), 0)

@part("shin_hero", "shin", "Hero shin", "Pointed knee cap, calf that flares out toward the ankle, front ridge, rear vents.", SNP, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .12, .22, 'X', 8); F.box("frame", (0, 0, -.50), (.20, .22, .86), (1, 1), .02)
    A.box("armor2", (0, -.15, .03), (.24, .16, .27), (.72, .8), .03)                      # knee cap
    A.box("accent", (0, -.238, .03), (.12, .02, .10), (.6, 1), 0)
    A.box("armor", (0, -.01, -.54), (.38, .44, .80), (.72, .74), .05)                     # calf, wide at the ankle
    A.box("armor2", (0, -.20, -.50), (.16, .05, .58), (.8, 1), .015, rot=RX(-4.5))        # front ridge
    for i in range(3): A.box("frame", (0, .215, -.62 - i * .08), (.20, .03, .04), (1, 1), 0)   # rear vents
    A.box("glow", (0, .225, -.87), (.14, .02, .045), (1, 1), 0)

@part("back_hero", "back", "Hero pack", "Compact pack: two bell thrusters, swept stabiliser wings, two hilts.", BK)
def _(F, A):
    F.box("frame", (0, .10, 0), (.50, .20, .50), (1, 1), .03)
    A.box("armor", (0, .17, .06), (.46, .22, .44), (.9, .95), .04)
    A.box("accent", (0, .285, .10), (.20, .02, .16), (.7, 1), 0)
    for s in (-1, 1):
        A.cyl("armor2", (s * .13, .22, -.25), .13, .22, 'Z', 8, .085); A.cyl("glow", (s * .13, .22, -.365), .11, .02, 'Z', 8)
        A.fin("accent2", (s * .25, .20, .08), [(0, -.10), (s * .28, .18), (s * .24, .24), (0, .10)], .04)
        A.box("armor2", (s * .15, .20, .36), (.06, .06, .24), (.8, .8), .012, rot=RX(-18))

# ---- HEAVY (WALKER) SET, the rest (Nov 23, his references: big walking tanks): heavy boxes, built-in weapons, pistons, hoses, bolts, warning bars. Original designs.
@part("head_walker", "head", "Walker head", "Low sensor head sunk into the body: visor slit, lens pod, two antenna stalks, roof plate.", HDP)
def _(F, A):
    F.cyl("joint", (0, 0, .05), .10, .10, 'Z', 6); F.box("frame", (0, 0, .16), (.30, .28, .16), (1, 1), .02)
    A.box("armor2", (0, .02, .19), (.42, .38, .22), (.9, .85), .04, front=(.9, .8))
    A.box("joint", (0, -.185, .20), (.30, .03, .07), (1, 1), 0); A.box("eye", (0, -.202, .20), (.24, .01, .035), (1, 1), 0)
    A.box("armor", (0, .0, .315), (.32, .28, .05), (.9, .9), .015)                        # roof plate
    A.cyl("armor", (.25, -.04, .25), .07, .18, 'Y', 8); A.cyl("glow", (.25, -.135, .25), .05, .012, 'Y', 8)   # lens pod
    A.cyl("joint", (-.15, .12, .47), .012, .36, 'Z', 5); A.cyl("joint", (-.09, .14, .43), .012, .27, 'Z', 5)  # antenna stalks
    for s in (-1, 1): A.box("armor", (s * .225, .0, .12), (.06, .30, .12), (1, .8), .015)

@part("pelvis_walker", "pelvis", "Walker hip", "Wide hip block: belt slab, thick hip guards with bolts, front plate with a warning bar, hoses.", PVP)
def _(F, A):
    F.box("frame", (0, 0, 0), (.64, .44, .30), (1.05, 1)); F.cyl("joint", (0, 0, -.06), .14, .76, 'X', 8)
    A.box("armor2", (0, 0, .08), (.74, .52, .16), (1.02, 1.02), .03)
    A.box("armor", (0, -.275, -.07), (.34, .08, .30), (1.2, 1), .025); A.box("accent", (0, -.318, -.02), (.26, .02, .06), (1, 1), 0)
    for s in (-1, 1):
        A.box("armor2", (s * .44, 0, -.05), (.14, .50, .30), (1, 1), .03); A.cyl("joint", (s * .44, -.26, -.05), .05, .03, 'Y', 6)
        A.cyl("frame", (s * .18, .25, -.06), .035, .26, 'Z', 6)                            # hoses
    A.box("armor", (0, .255, -.05), (.44, .08, .26), (1.1, 1), .025)

@part("shoulder_walker", "shoulder", "Missile shoulder", "Huge box shoulder with a six-tube missile rack in the front, roof slab, warning bar, bolts.", SHP, side=True)
def _(F, A):
    F.cyl("joint", (.08, 0, 0), .17, .24, 'X', 8)
    A.box("armor2", (.24, 0, .08), (.56, .66, .46), (.96, .96), .04)
    A.box("armor", (.24, 0, .335), (.60, .70, .06), (.95, .95), .02)                      # roof slab
    A.box("frame", (.24, -.332, .10), (.42, .02, .32), (1, 1), 0)                         # rack
    for i in range(3):
        for j in range(2): A.cyl("joint", (.12 + i * .12, -.345, .03 + j * .14), .045, .03, 'Y', 6)
    A.box("accent", (.523, 0, -.09), (.02, .50, .07), (1, 1), 0)                          # warning bar
    for y in (-.22, .22): A.cyl("joint", (.525, y, .14), .035, .02, 'X', 6)

@part("upperarm_walker", "upperarm", "Walker upper arm", "Thick arm: armour block, twin front pistons, a hose down the back.", UA_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .13, .20, 'X', 8); F.box("frame", (0, 0, -.32), (.22, .24, .50), (1, 1), .02)
    A.box("armor2", (0, 0, -.20), (.36, .36, .24), (1.05, 1.05), .04)
    A.box("armor", (0, 0, -.48), (.32, .32, .14), (1, 1), .03)
    for s in (-1, 1): A.cyl("joint", (s * .10, -.165, -.36), .03, .34, 'Z', 6)
    A.cyl("frame", (0, .185, -.34), .045, .40, 'Z', 6)

@part("forearm_walker", "forearm", "Gun forearm", "Heavy box forearm with a twin-barrel gun built into the outer side.", FAP, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .14, .26, 'X', 8); F.box("frame", (0, 0, -.36), (.20, .22, .56), (1, 1), .02)
    A.box("armor2", (0, -.01, -.38), (.42, .44, .50), (.92, .92), .05)
    A.box("armor", (0, -.01, -.13), (.46, .48, .10), (1, 1), .02)                         # elbow collar
    A.box("accent", (0, -.236, -.40), (.24, .02, .08), (1, 1), 0)
    A.box("armor", (.245, 0, -.28), (.10, .24, .18), (1, 1), .02)                         # gun housing
    for dy in (-.06, .06): A.cyl("joint", (.25, dy, -.50), .04, .30, 'Z', 6)

@part("forearm_rotary", "forearm", "Rotary cannon arm", "Forearm with a six-barrel rotary cannon slung on the outer side and an ammo box at the elbow.", FAP, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .13, .24, 'X', 8); F.box("frame", (0, 0, -.36), (.18, .20, .56), (1, 1), .02)
    A.box("armor2", (0, -.01, -.36), (.32, .34, .50), (.95, .95), .04)
    A.box("armor", (.02, .16, -.12), (.26, .14, .20), (1, 1), .025)                       # ammo box
    A.cyl("armor", (.27, 0, -.21), .13, .26, 'Z', 8)                                      # drum
    for k in range(6): A.cyl("joint", (.27 + .075 * math.cos(k * math.pi / 3), .075 * math.sin(k * math.pi / 3), -.49), .028, .30, 'Z', 6)
    A.cyl("frame", (.27, 0, -.45), .115, .03, 'Z', 8); A.cyl("accent", (.27, 0, -.625), .12, .035, 'Z', 8)   # barrel clamp + muzzle ring

@part("thigh_walker", "thigh", "Walker thigh", "Thick thigh block with a bolted side plate, a front piston and a warning bar.", TH_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .16, .28, 'X', 8); F.box("frame", (0, 0, -.46), (.26, .28, .76), (1, 1), .02)
    A.box("armor2", (0, -.01, -.40), (.42, .44, .58), (1.08, 1.05), .05)
    A.box("armor", (.225, 0, -.38), (.05, .36, .46), (1, 1), .02)
    for z in (-.22, -.54): A.cyl("joint", (.255, 0, z), .035, .02, 'X', 6)
    A.cyl("joint", (0, -.245, -.46), .045, .46, 'Z', 6); A.box("accent", (0, -.238, -.15), (.26, .02, .06), (1, 1), 0)

@part("shin_walker", "shin", "Walker shin", "Big knee block, three overlapping shin plates that get wider toward the ground, ankle collar, rear pistons.", SNP, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .15, .26, 'X', 8); F.box("frame", (0, 0, -.50), (.24, .26, .86), (1, 1), .02)
    A.box("armor", (0, -.16, .04), (.38, .22, .34), (.8, .8), .04); A.box("accent", (0, -.275, .04), (.22, .02, .07), (1, 1), 0)   # knee block
    for i in range(3): A.box("armor2", (0, -.03, -.30 - i * .21), (.42 + i * .04, .46 + i * .04, .27), (.88, .88), .04)
    A.box("armor", (0, -.02, -.915), (.54, .58, .11), (1, 1), .03)                        # ankle collar
    for s in (-1, 1): A.cyl("joint", (s * .10, .275, -.50), .03, .56, 'Z', 6)

@part("foot_walker", "foot", "Walker foot", "Wide stomping pad with two toe blocks and a heel block, ankle housing, pistons.", FTP, side=True)
def _(F, A):
    F.ball("joint", (0, 0, 0), .11, 8)
    A.box("armor2", (0, -.03, -.02), (.34, .36, .16), (.85, .85), .03)                    # ankle housing
    A.box("armor", (0, -.06, -.15), (.44, .62, .14), (.92, .9), .03)                      # main pad
    for s in (-1, 1):
        A.box("armor2", (s * .125, -.42, -.16), (.18, .22, .12), (.9, .7), .025)          # toe blocks
        A.cyl("joint", (s * .19, .11, -.05), .03, .20, 'Z', 6)
    A.box("armor2", (0, .30, -.16), (.26, .18, .12), (.9, .75), .025)                     # heel block
    A.box("accent", (0, -.372, -.085), (.38, .02, .04), (1, 1), 0)

@part("back_walker", "back", "Engine block", "Big engine pack: radiator slats, two exhaust stacks with glowing tops, an antenna.", BK)
def _(F, A):
    F.box("frame", (0, .10, 0), (.60, .22, .56), (1, 1), .03)
    A.box("armor2", (0, .20, .02), (.64, .30, .56), (.95, .95), .04)
    for i in range(5): A.box("frame", (0, .357, -.14 + i * .08), (.50, .03, .04), (1, 1), 0)
    for s in (-1, 1): A.cyl("joint", (s * .24, .26, .42), .06, .36, 'Z', 8); A.cyl("glow", (s * .24, .26, .605), .045, .012, 'Z', 8)
    A.cyl("joint", (.30, .10, .56), .012, .52, 'Z', 5)

SLOT = {"torso": "chest", "head": "head", "pelvis": "pelvis", "shoulder": "shoulder", "upperarm": "upper_arm",
        "forearm": "forearm", "hand": "hand", "thigh": "thigh", "shin": "shin", "foot": "foot", "back": "back"}
MODE = {"chest": "box", "head": "box", "pelvis": "box", "shoulder": "anchor", "foot": "anchor", "back": "anchor"}
HAND_POSES = [("hand_kit", "fist", "Fist", "Model-kit hand closed into a fist."),
              ("hand_kit", "open", "Open hand", "Model-kit hand with open fingers."),
              ("hand_kit", "grip", "Grip hand", "Model-kit hand curled to hold a weapon."),
              ("hand_claw", None, "Claw hand", PARTS["hand_claw"]["about"])]

def clear():
    for ob in list(bpy.data.objects): bpy.data.objects.remove(ob)
def join_all():
    obs = list(bpy.context.scene.objects)
    bpy.ops.object.select_all(action='DESELECT')
    for o in obs: o.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]; bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.parent = None; ob.matrix_world = Matrix.Identity(4)
    return ob
_box = PB.box
def no_waist(self, key, at, size, *a, **k):        # chests: skip the kit's lower waist block (the new frame has a waist bone)
    if key == "frame" and at[2] < .3: return
    return _box(self, key, at, size, *a, **k)
def build(pid, mirror, pose):
    clear()
    PB.box = no_waist if PARTS[pid]["slot"] == "torso" else _box
    if pose: NS["make_hand"]("kit", mirror, "", pose)
    else: NS["make_part"](pid, "kit", mirror)
    bpy.context.view_layer.update()
    for o in list(bpy.context.scene.objects):     # bake parents into world space before joining
        mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
    bpy.context.view_layer.update()
    for o in bpy.context.scene.objects:
        bpy.context.view_layer.objects.active = o; o.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True); o.select_set(False)
    return join_all()
def place(ob, mode):
    vs = ob.data.vertices; xs, ys, zs = [v.co.x for v in vs], [v.co.y for v in vs], [v.co.z for v in vs]
    if mode == "box": off = Vector(((max(xs)+min(xs))/2, (max(ys)+min(ys))/2, min(zs)))
    elif mode == "limb": off = Vector(((max(xs)+min(xs))/2, (max(ys)+min(ys))/2, max(zs)))
    else: off = Vector((0, 0, 0))                               # anchor: keep the kit's joint point
    for v in vs: v.co -= off
    xs, ys, zs = [v.co.x for v in vs], [v.co.y for v in vs], [v.co.z for v in vs]
    return [round(max(xs)-min(xs), 3), round(max(ys)-min(ys), 3), round(max(zs)-min(zs), 3)]
def glb(ob):
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True)
    p = os.path.join("/tmp", "mf_part.glb")
    bpy.ops.export_scene.gltf(filepath=p, export_format='GLB', use_selection=True)
    return base64.b64encode(open(p, "rb").read()).decode()

LIB = {}
jobs = [(pid, None, PARTS[pid]["name"], PARTS[pid]["about"]) for pid in PARTS if PARTS[pid]["slot"] in SLOT and pid not in ("hand_kit", "hand_claw")] + HAND_POSES
for pid, pose, name, about in jobs:
    slot = SLOT[PARTS[pid]["slot"]]; mode = MODE.get(slot, "limb"); side = PARTS[pid]["side"]
    e = dict(id=pid + ("_" + pose if pose else ""), name=name, about=about, mode=mode)
    ob = build(pid, False, pose); e["size"] = place(ob, mode); e["glb"] = glb(ob)          # built at +X = mech's left
    if side: ob = build(pid, True, pose); place(ob, mode); e["glbR"] = glb(ob)              # mirrored copy for the right
    LIB.setdefault(slot, []).append(e)
OUTJS = os.path.join(HERE, "..", "..", "models", "parts_all.js")
# paint schemes (colour per material key) and starter mechs (his kit's build sheets + a body preset each)
SCHEMES = {k: v for k, v in NS["SCHEMES"].items()}
BODY = {"Vanguard": "standard", "Bulwark": "heavy", "Titanheart": "brawler", "Ranger": "sleek", "Falcon": "scout",
        "Paladin": "standard", "Wraith": "sleek", "Mule": "squat", "Patrol": "standard", "Lionheart": "brawler"}
src2 = open(os.path.join(HERE, "mech_kit_R2.py")).read()
sheets_src = src2[src2.index("SHEETS = {"):src2.index("POSE_HERO")]
NS2 = {}; exec(sheets_src, NS2)
STARTERS = [dict(name=n, preset=BODY[n], scheme=n.lower(), parts={SLOT[k]: v for k, v in sh.items()}) for n, sh in NS2["SHEETS"].items()]
STARTERS = [dict(name="Hero", preset="standard", scheme="vanguard", parts=dict(chest="torso_hero", head="head_hero", pelvis="pelvis_hero", shoulder="shoulder_hero",
                 upper_arm="upperarm_hero", forearm="forearm_hero", thigh="thigh_hero", shin="shin_hero", foot="foot_hero", back="back_hero")),
            dict(name="Walker", preset="heavy", scheme="bulwark", parts=dict(chest="torso_walker", head="head_walker", pelvis="pelvis_walker", shoulder="shoulder_walker",
                 upper_arm="upperarm_walker", forearm="forearm_walker", thigh="thigh_walker", shin="shin_walker", foot="foot_walker", back="back_walker"))] + STARTERS
open(OUTJS, "w").write("window.MF_PARTS = " + json.dumps(LIB) + ";\nwindow.MF_SCHEMES = " + json.dumps(SCHEMES) +
                       ";\nwindow.MF_STARTERS = " + json.dumps(STARTERS) + ";\n")
print({k: [p["name"] for p in v] for k, v in LIB.items()})
print("bytes", os.path.getsize(OUTJS))
