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
@part("torso_hero", "torso", "Hero chest", "Gundam-style: tall V chest, yellow intakes, cockpit hatch, collar and abs.", TP(.58, .90, 1.10, .34))
def _(F, A):
    F.box("frame", (0, .02, .66), (.66, .50, .62), (1.2, 1))
    A.box("armor", (0, -.02, .68), (.92, .62, .62), (1.28, 1.02), .05)
    A.box("armor2", (0, 0, 1.04), (.50, .44, .12), (.85, .85), .02)                      # collar
    A.box("armor2", (0, -.34, .58), (.30, .05, .30), (1.12, 1), .02)                     # cockpit hatch
    for s in (-1, 1):
        A.box("accent", (s * .27, -.34, .82), (.22, .05, .17), (1, 1), .015)            # intakes
        for i in range(3): A.box("frame", (s * .27, -.37, .77 + i * .05), (.18, .02, .02), (1, 1), 0)
        A.box("armor2", (s * .44, -.02, .62), (.06, .46, .40), (1, 1), .015)           # side plates
    A.box("armor", (0, -.05, .25), (.42, .40, .16), (1.06, 1), .03)                       # abs
    A.box("armor", (0, -.04, .09), (.34, .36, .14), (1.08, 1), .03)
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
    A.box("accent", (0, -.14, -.09), (.26, .56, .24), (.86, .38), .03, front=(.78, .5), shift=(.14, 0))   # tall wedge, top pushed back so it slopes down to the toe
    A.box("accent", (0, -.43, -.185), (.22, .2, .07), (.8, .5), .02)                         # toe tip, tucked into the wedge
    A.box("accent", (0, .18, -.15), (.24, .17, .14), (.9, .8), .02)                          # heel block
    A.box("frame", (0, -.05, -.20), (.18, .16, .03), (1, 1), .005)                            # arch (sits up off the ground)

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
open(OUTJS, "w").write("window.MF_PARTS = " + json.dumps(LIB) + ";\nwindow.MF_SCHEMES = " + json.dumps(SCHEMES) +
                       ";\nwindow.MF_STARTERS = " + json.dumps(STARTERS) + ";\n")
print({k: [p["name"] for p in v] for k, v in LIB.items()})
print("bytes", os.path.getsize(OUTJS))
