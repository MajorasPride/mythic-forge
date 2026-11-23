# Mythic Forge WEAPONS (Nov 22 2026). Run with the bpy module: python3 parts_weapons.py
# Uses his own Weapons kit (T044, weapons_kit.py from Nov 14, kept next to this file) + 6 new shoulder weapons.
# Weapon space (from the kit): origin = where it plugs in, +Z = the way it points. Exported as is ("anchor").
# Output: ../../models/parts_weapons.js  ->  window.MF_WEAPONS = { hand: [...], shoulder: [...] }
import bpy, os, sys, json, base64, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import weapons_kit as wk
import beast_lib as B
W, RX, RY, R, UP, FWD = wk.W, B.RX, B.RY, B.R, B.UP, B.FWD

# ---- 2 new shoulder weapons so the shoulder has 4 (original designs)
@W("beam_cannon_twin", "mount", "Twin beam cannon", "Two glowing beam barrels on a swivel turret.", {"muzzle": ((0, -1.4, .3), FWD)})
def _(F, A):
    F.cyl("frame", (0, 0, .08), .14, .16, 'Z', 8); A.box("armor2", (0, -.05, .3), (.42, .46, .26), (1, 1), .04)
    for s in (-1, 1):
        A.cyl("armor", (s * .12, -.75, .32), .07, 1.2, 'Y', 8); A.cyl("glow", (s * .12, -1.37, .32), .06, .06, 'Y', 8)
@W("rocket_rack", "mount", "Rocket rack", "Open rack of 4 big rockets with fins.", {"muzzle": ((0, -.6, .3), FWD)})
def _(F, A):
    F.cyl("frame", (0, 0, .06), .12, .12, 'Z', 8); A.box("armor2", (0, .05, .22), (.5, .5, .1), (1, 1), .02)
    for x in (-.15, .15):
        for z in (.36, .58):
            A.cyl("armor", (x, -.15, z), .07, .8, 'Y', 8, r2=.07); A.cyl("accent2", (x, -.58, z), .07, .1, 'Y', 8, r2=.01)

@W("radar_dome", "mount", "Radar dome", "Spinning sensor dish on a short mast, with a glowing core.", {"muzzle": ((0, -.3, .5), FWD)})
def _(F, A):
    F.cyl("frame", (0, 0, .08), .12, .16, 'Z', 8); A.cyl("armor2", (0, 0, .24), .05, .2, 'Z', 6)
    A.cyl("armor", (0, -.02, .42), .34, .06, 'Y', 14, r2=.12, rot=RX(70)); A.ball("glow", (0, -.08, .44), .06, 8)
@W("gatling_turret", "mount", "Mini gatling turret", "Small turret with a six-barrel spinner.", {"muzzle": ((0, -1.0, .3), FWD)})
def _(F, A):
    F.cyl("frame", (0, 0, .08), .14, .16, 'Z', 8); A.box("armor2", (0, 0, .3), (.36, .4, .26), (1, 1), .04)
    for i in range(6):
        a = R(i * 60); A.cyl("frame", (math.cos(a) * .06, -.6, .3 + math.sin(a) * .06), .025, .7, 'Y', 6)
    A.cyl("accent", (0, -.32, .3), .11, .08, 'Y', 10); A.cyl("accent", (0, -.9, .3), .11, .05, 'Y', 10)
@W("flare_launcher", "mount", "Flare launcher", "Angled box of 8 decoy flares, tips glowing.", {"muzzle": ((0, -.2, .5), UP)})
def _(F, A):
    F.cyl("frame", (0, 0, .06), .12, .12, 'Z', 8); A.box("armor", (0, .05, .28), (.44, .36, .3), (1, 1), .04, rot=RX(-25))
    for i in range(4):
        for j in range(2): A.cyl("glow", (-.15 + i * .1, -.06 + j * .14, .46 + j * .06), .035, .04, 'Z', 6)
@W("saber_rack", "mount", "Beam saber rack", "Two beam saber hilts stowed upright, ready to draw.", {"tip": ((0, 0, .7), UP)})
def _(F, A):
    F.box("frame", (0, 0, .05), (.34, .2, .1), (1, 1), .02)
    for x in (-.09, .09):
        A.cyl("armor2", (x, 0, .3), .045, .36, 'Z', 8); A.cyl("accent", (x, 0, .5), .055, .05, 'Z', 8); A.cyl("glow", (x, 0, .56), .02, .08, 'Z', 6)

def clear():
    for ob in list(bpy.data.objects): bpy.data.objects.remove(ob)
def build(pid):
    clear(); B.make_part(pid, "kit"); bpy.context.view_layer.update()
    for o in list(bpy.context.scene.objects):
        mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
    for o in bpy.context.scene.objects:
        bpy.context.view_layer.objects.active = o; o.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True); o.select_set(False)
    obs = [o for o in bpy.context.scene.objects if o.type == 'MESH' and not o.get("hitbox")]
    bpy.ops.object.select_all(action='DESELECT')
    for o in obs: o.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]; bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    vs = ob.data.vertices
    size = [round(max(v.co[i] for v in vs) - min(v.co[i] for v in vs), 3) for i in range(3)]
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True)
    p = "/tmp/mf_weapon.glb"; bpy.ops.export_scene.gltf(filepath=p, export_format='GLB', use_selection=True)
    return size, base64.b64encode(open(p, "rb").read()).decode()

GROUP = {"melee": "hand", "gun": "hand", "shield": "hand", "mount": "shoulder"}
SKIP = {"missile_pod_leg", "rocket_fist"}          # leg pods and rocket fists come later
LIB = {"hand": [], "shoulder": []}
for pid, P in B.PARTS.items():
    if P.get("kit") != "weapons" or P["slot"] not in GROUP or pid in SKIP: continue
    size, g = build(pid)
    LIB[GROUP[P["slot"]]].append(dict(id=pid, name=P["name"], about=P["about"], kind=P["slot"], size=size, glb=g))
out = os.path.join(HERE, "..", "..", "models", "parts_weapons.js")
# starter loadouts from his kit: right hand, left hand (or shield), shoulder pod
LOAD = {n: dict(R=d.get("R"), L=d.get("Lshield") or d.get("L"), pod=d.get("pod")) for n, d in wk.LOADOUTS.items()}
open(out, "w").write("window.MF_WEAPONS = " + json.dumps(LIB) + ";\nwindow.MF_LOADOUTS = " + json.dumps(LOAD) + ";\n")
print({k: [w["name"] for w in v] for k, v in LIB.items()}, os.path.getsize(out))
