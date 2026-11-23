# Mythic Forge DETAILS (Nov 22 2026): small pieces you stick anywhere on the mech (item 6).
# Built with his mech kit's shape tools (mech_kit_R2.py PB: box / cyl / fin) and beast_lib's spike, like his Weapons kit.
# Detail space: origin = the spot where it touches the surface, +Z = straight out from the surface.
# Output: ../../models/parts_details.js -> window.MF_DETAILS = [{id, name, group, about, size, glb}]
import bpy, os, sys, json, base64, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import beast_lib as B
R, RX, RY, RZ = B.R, B.RX, B.RY, B.RZ
D = {}
def det(pid, group, name, about):
    def deco(fn):
        B.PARTS[pid] = dict(id=pid, slot="detail", name=name, about=about, plugs={}, side=False, fn=fn, kit="details"); D[pid] = group
        return fn
    return deco

# ---------------- ANTENNAS
@det("ant_whip", "Antennas", "Whip antenna", "One long thin whip on a small base.")
def _(F, A):
    F.cyl("frame", (0, 0, .04), .07, .08, 'Z', 8); A.cyl("accent", (0, 0, .62), .018, 1.1, 'Z', 6, r2=.008)
    A.ball("glow", (0, 0, 1.18), .035, 6)
@det("ant_twin", "Antennas", "Twin rods", "Two short rods side by side, like a radio mast.")
def _(F, A):
    F.box("frame", (0, 0, .04), (.22, .1, .08), (1, 1), .015)
    for x, L in ((-.06, .55), (.06, .4)): A.cyl("accent", (x, 0, .08 + L / 2), .02, L, 'Z', 6)
@det("ant_blade", "Antennas", "Blade antenna", "Flat swept blade, Gundam-style.")
def _(F, A):
    F.cyl("frame", (0, 0, .03), .06, .06, 'Z', 8)
    A.fin("accent2", (0, 0, .04), [(-.05, 0), (.05, 0), (.22, .62), (.16, .64)], .03)
@det("ant_dish", "Antennas", "Sensor dish", "Small radar dish on a stalk.")
def _(F, A):
    F.cyl("frame", (0, 0, .12), .03, .24, 'Z', 6)
    A.cyl("armor2", (0, 0, .28), .2, .05, 'Z', 12, r2=.06); A.ball("glow", (0, 0, .33), .03, 6)

# ---------------- VENTS
@det("vent_slats", "Vents", "Slat vent", "Box vent with 4 cooling slats.")
def _(F, A):
    A.box("armor2", (0, 0, .03), (.42, .3, .06), (1, 1), .015)
    for i in range(4): A.box("frame", (0, -.105 + i * .07, .075), (.36, .03, .04), (1, 1), .006)
@det("vent_round", "Vents", "Round vent", "Round fan grill with a glowing core.")
def _(F, A):
    A.cyl("armor2", (0, 0, .03), .2, .06, 'Z', 12)
    for a in range(0, 180, 45): A.box("frame", (0, 0, .07), (.34, .025, .03), (1, 1), .004, rot=RZ(a))
    A.cyl("glow", (0, 0, .075), .05, .03, 'Z', 8)
@det("vent_grill", "Vents", "Heat grill", "Long grill with a glow strip under it.")
def _(F, A):
    A.box("armor2", (0, 0, .03), (.6, .2, .06), (1, 1), .015); A.box("glow", (0, 0, .055), (.52, .12, .02), (1, 1), .003)
    for i in range(6): A.box("frame", (-.225 + i * .09, 0, .075), (.03, .18, .04), (1, 1), .005)
@det("vent_exhaust", "Vents", "Exhaust pipes", "Two short exhaust stacks, angled up.")
def _(F, A):
    F.box("frame", (0, 0, .03), (.3, .16, .06), (1, 1), .01)
    for x in (-.07, .07): A.cyl("armor", (x, 0, .2), .055, .32, 'Z', 8); A.cyl("glow", (x, 0, .36), .045, .02, 'Z', 8)

# ---------------- SPIKES
@det("spike_one", "Spikes", "Spike", "One sharp cone spike.")
def _(F, A):
    A.cyl("armor2", (0, 0, .03), .1, .06, 'Z', 8); B.spike(A, "accent", (0, 0, .05), .08, .45, (0, 0, 1), 6)
@det("spike_row", "Spikes", "Spike row", "Three spikes in a row, middle one tallest.")
def _(F, A):
    A.box("armor2", (0, 0, .03), (.46, .14, .06), (1, 1), .015)
    for x, L in ((-.15, .26), (0, .38), (.15, .26)): B.spike(A, "accent", (x, 0, .05), .055, L, (0, 0, 1), 6)
@det("spike_crystal", "Spikes", "Crystal spike", "Glowing crystal cluster (from his Weapons kit idea).")
def _(F, A):
    A.cyl("frame", (0, 0, .02), .12, .04, 'Z', 6)
    B.spike(A, "glow", (0, 0, .02), .07, .42, (0, 0, 1), 6)
    for a in (0, 120, 240): B.spike(A, "glow", (math.cos(R(a)) * .05, math.sin(R(a)) * .05, .02), .04, .24, (math.cos(R(a)) * .45, math.sin(R(a)) * .45, 1), 5)
@det("spike_horn", "Spikes", "Horn", "Curved-look horn, two cones bent forward.")
def _(F, A):
    A.cyl("armor2", (0, 0, .03), .1, .06, 'Z', 8)
    B.spike(A, "accent2", (0, 0, .05), .08, .25, (0, .2, 1), 6); B.spike(A, "accent2", (0, .05, .28), .05, .25, (0, .8, .6), 6)

# ---------------- FINS
@det("fin_v", "Fins", "V-fin crest", "Classic V crest for a head or chest.")
def _(F, A):
    F.cyl("frame", (0, 0, .03), .05, .06, 'Z', 8)
    A.fin("accent2", (0, -.04, .03), [(0, 0), (.34, .32), (.27, .33), (0, .07), (-.27, .33), (-.34, .32)], .03, rot=RX(65))   # leans back along the surface
@det("fin_swept", "Fins", "Swept fin", "Back-swept fin, like a jet tail.")
def _(F, A):
    A.box("armor2", (0, 0, .03), (.1, .32, .06), (1, 1), .01)
    A.fin("armor", (0, 0, .04), [(-.16, 0), (.16, 0), (.34, .42), (.22, .44)], .04, rot=RZ(90))
@det("fin_blade", "Fins", "Blade fin", "Tall flat blade with an accent edge.")
def _(F, A):
    A.box("armor2", (0, 0, .03), (.1, .34, .06), (1, 1), .01)
    A.fin("armor", (0, 0, .04), [(-.15, 0), (.15, 0), (.06, .52), (-.04, .5)], .035, rot=RZ(90))
    A.fin("accent", (0, 0, .04), [(.15, 0), (.2, 0), (.09, .5), (.06, .52)], .04, rot=RZ(90))
@det("fin_ear", "Fins", "Ear fins", "Pair of small side fins, like a helmet's ears.")
def _(F, A):
    F.box("frame", (0, 0, .03), (.3, .1, .06), (1, 1), .01)
    for s in (-1, 1): A.fin("accent", (s * .1, 0, .04), [(0, 0), (s * .14, .26), (s * .05, .05)], .04)

# ---------------- EMBLEMS (flat badges)
@det("emb_star", "Emblems", "Star", "Five-point star badge.")
def _(F, A):
    pts = [((.2 if i % 2 == 0 else .085) * math.sin(R(i * 36)), (.2 if i % 2 == 0 else .085) * math.cos(R(i * 36))) for i in range(10)]
    A.cyl("armor2", (0, 0, .015), .24, .03, 'Z', 16); A.fin("accent", (0, 0, .035), pts, .02, rot=RX(90))
@det("emb_v", "Emblems", "V emblem", "Bold V badge with a glow centre.")
def _(F, A):
    A.fin("accent", (0, 0, .02), [(-.24, .16), (0, -.2), (.24, .16), (.14, .16), (0, -.05), (-.14, .16)], .04, rot=RX(90))
    A.cyl("glow", (0, -.03, .035), .04, .03, 'Z', 8)
@det("emb_core", "Emblems", "Power core", "Round glowing core in a ring (super-robot chest).")
def _(F, A):
    A.cyl("armor2", (0, 0, .03), .2, .06, 'Z', 16); A.cyl("glow", (0, 0, .05), .13, .04, 'Z', 16)
@det("emb_chevron", "Emblems", "Chevrons", "Three stacked chevron stripes (rank marks).")
def _(F, A):
    for i in range(3): A.fin("accent", (0, -.1 + i * .1, .02), [(-.2, 0), (0, .07), (.2, 0), (.2, .04), (0, .11), (-.2, .04)], .025, rot=RX(90))
@det("emb_skull", "Emblems", "Skull plate", "Simple skull-face badge.")
def _(F, A):
    A.cyl("armor2", (0, .02, .02), .17, .04, 'Z', 12); A.box("armor2", (0, -.14, .02), (.18, .1, .04), (1, 1), .01)
    for x in (-.065, .065): A.cyl("glow", (x, .03, .045), .045, .02, 'Z', 8)

def clear():
    for ob in list(bpy.data.objects): bpy.data.objects.remove(ob)
def build(pid):
    clear(); B.make_part(pid, "kit"); bpy.context.view_layer.update()
    for o in list(bpy.context.scene.objects):
        mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
    for o in bpy.context.scene.objects:
        bpy.context.view_layer.objects.active = o; o.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True); o.select_set(False)
    obs = [o for o in bpy.context.scene.objects if o.type == 'MESH' and len(o.data.vertices)]
    bpy.ops.object.select_all(action='DESELECT')
    for o in obs: o.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]; bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active; vs = ob.data.vertices
    size = [round(max(v.co[i] for v in vs) - min(v.co[i] for v in vs), 3) for i in range(3)]
    low = round(min(v.co[2] for v in vs), 3)
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True)
    p = "/tmp/mf_detail.glb"; bpy.ops.export_scene.gltf(filepath=p, export_format='GLB', use_selection=True)
    return size, low, base64.b64encode(open(p, "rb").read()).decode()

LIB = []
for pid, group in D.items():
    size, low, g = build(pid); P = B.PARTS[pid]
    LIB.append(dict(id=pid, name=P["name"], group=group, about=P["about"], size=size, low=low, glb=g))
out = os.path.join(HERE, "..", "..", "models", "parts_details.js")
open(out, "w").write("window.MF_DETAILS = " + json.dumps(LIB) + ";\n")
print([(d["name"], d["size"], d["low"]) for d in LIB], os.path.getsize(out))
