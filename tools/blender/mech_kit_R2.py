"""Mythic Forge 2.0 / Titan Clash 2.0 — MECH KIT (T042), made in Blender from code (bpy 5.x module).
Model-kit style: every part = inner FRAME + ARMOR, origin on its joint, PLUGS where the next part goes,
and an invisible HITBOX (box + capsule). All designs original (inspired by model kits / mech anime, no copies).
Run:  python3 mech_kit.py          -> out/mech_kit.json, out/mech_kit.glb, out/mech_kit.blend
      python3 mech_kit.py render   -> also preview PNGs in out/png/
Kit scale: a mech stands ~4.6 kit units; x4 = Titan Clash game units (VALOR ~18). By MajorasPride."""
import bpy, bmesh, math, os, sys, json, base64, struct
from mathutils import Vector, Matrix, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out"); os.makedirs(os.path.join(OUT, "png"), exist_ok=True)
RENDER = "render" in sys.argv
R = lambda d: math.radians(d)

# ---------------------------------------------------------------- colour schemes (keys every part uses)
SCHEMES = {
    "kit":     dict(armor="e9e9e4", armor2="c9ccd2", frame="3b414d", joint="252a33", accent="2a7fd4", accent2="d8343a", glow="ffcf3a", eye="5cf2ff"),
    "vanguard": dict(armor="eeeeea", armor2="2f5fb8", frame="394050", joint="232833", accent="d8343a", accent2="f2c230", glow="ffd23f", eye="57f0ff"),
    "bulwark": dict(armor="6e7748", armor2="545b38", frame="2f3338", joint="1f2226", accent="e8a21c", accent2="c9c2a8", glow="ff8a2a", eye="ff4040"),
    "titanheart": dict(armor="d23a2e", armor2="1d2b5c", frame="3a3f4c", joint="242833", accent="f4c534", accent2="eef0f2", glow="7dfcff", eye="fff27a"),
}
GLOWKEYS = {"glow", "eye"}


def srgb(h):
    c = [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]
    return tuple(x/12.92 if x <= 0.04045 else ((x+0.055)/1.055)**2.4 for x in c)


MATS = {}
def M(scheme, key):
    nm = f"{scheme}.{key}"
    if nm in MATS: return MATS[nm]
    col = SCHEMES[scheme].get(key, "ff00ff")
    m = bpy.data.materials.new(nm); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*srgb(col), 1); b.inputs["Roughness"].default_value = .6
    if key in GLOWKEYS:
        b.inputs["Emission Color"].default_value = (*srgb(col), 1); b.inputs["Emission Strength"].default_value = 3.
    m.diffuse_color = (*srgb(col), 1); m["key"] = key
    MATS[nm] = m; return m


# ---------------------------------------------------------------- mesh builder (z up, FRONT = -Y)
class PB:
    """Collects shapes for one mesh. Each face gets a material key."""
    def __init__(self):
        self.bm = bmesh.new(); self.keys = []

    def _mi(self, key):
        if key not in self.keys: self.keys.append(key)
        return self.keys.index(key)

    def _finish(self, before, key, rot=None, at=(0, 0, 0)):
        new_v = [v for v in self.bm.verts if v not in before[0]]
        if rot is not None: bmesh.ops.rotate(self.bm, verts=new_v, cent=(0, 0, 0), matrix=rot)
        bmesh.ops.translate(self.bm, verts=new_v, vec=Vector(at))
        i = self._mi(key)
        for f in self.bm.faces:
            if f not in before[1]: f.material_index = i

    def _snap(self): return (set(self.bm.verts), set(self.bm.faces))

    def box(self, key, at, size, top=(1, 1), bevel=.035, rot=None, front=(1, 1), shift=(0, 0)):
        """Chamfered box centred on `at`. top = (x, y) scale of the top face (taper);
        front = (x, z) scale of the front (-Y) face; shift = (y, x) offset of the top face (lean)."""
        b = self._snap()
        r = bmesh.ops.create_cube(self.bm, size=1); vs = r["verts"]
        for v in vs:
            if v.co.z > 0:
                v.co.x *= top[0]; v.co.y *= top[1]; v.co.y += shift[0] / max(size[1], 1e-3); v.co.x += shift[1] / max(size[0], 1e-3)
            if v.co.y < 0:
                v.co.x *= front[0]; v.co.z *= front[1]
            v.co.x *= size[0]; v.co.y *= size[1]; v.co.z *= size[2]
        if bevel:
            edges = list({e for v in vs for e in v.link_edges})
            bmesh.ops.bevel(self.bm, geom=edges, offset=bevel, segments=1, affect='EDGES', profile=.5, clamp_overlap=True)
        self._finish(b, key, rot, at)

    def cyl(self, key, at, r, depth, axis='Z', seg=8, r2=None, rot=None):
        b = self._snap()
        res = bmesh.ops.create_cone(self.bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=depth)
        nv = res["verts"]
        if axis == 'X': bmesh.ops.rotate(self.bm, verts=nv, cent=(0, 0, 0), matrix=Matrix.Rotation(R(90), 3, 'Y'))
        elif axis == 'Y': bmesh.ops.rotate(self.bm, verts=nv, cent=(0, 0, 0), matrix=Matrix.Rotation(R(90), 3, 'X'))
        self._finish(b, key, rot, at)

    def ball(self, key, at, r, seg=8):
        b = self._snap()
        bmesh.ops.create_uvsphere(self.bm, u_segments=seg, v_segments=max(4, seg//2), radius=r)
        self._finish(b, key, None, at)

    def fin(self, key, at, pts, thick=.04, rot=None):
        """Flat plate from a 2D outline in the X-Z plane (crests, fins, wings, spikes)."""
        b = self._snap(); bm = self.bm
        f0 = [bm.verts.new((x, -thick/2, z)) for x, z in pts]; f1 = [bm.verts.new((x, thick/2, z)) for x, z in pts]
        bm.faces.new(f0); bm.faces.new(list(reversed(f1)))
        n = len(pts)
        for k in range(n): bm.faces.new([f0[(k+1) % n], f0[k], f1[k], f1[(k+1) % n]])
        self._finish(b, key, rot, at)

    def to_obj(self, name, scheme, mirror=False):
        bm = self.bm
        if mirror:
            for v in bm.verts: v.co.x = -v.co.x
            for f in bm.faces: f.normal_flip()
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        for k in self.keys: me.materials.append(M(scheme, k))
        for p in me.polygons: p.use_smooth = False
        ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
        return ob


# ---------------------------------------------------------------- the parts
# Each part: slot, name, about, frame(pb), armor(pb), plugs {name: (pos, dir)} in its own space
# (origin = the joint it hangs from). Right-side parts are built at +X; left side = mirrored copy.
PARTS = {}
def part(pid, slot, name, about, plugs, side=False):
    def deco(fn):
        PARTS[pid] = dict(id=pid, slot=slot, name=name, about=about, plugs=plugs, side=side, fn=fn)
        return fn
    return deco

UP, DOWN, FWD, BACK, OUT_ = (0, 0, 1), (0, 0, -1), (0, -1, 0), (0, 1, 0), (1, 0, 0)

# ---- PELVIS (root). origin = centre of the hips
PELVIS_PLUGS = {"waist": ((0, 0, .17), UP), "hip_R": ((.25, 0, -.06), DOWN), "hip_L": ((-.25, 0, -.06), DOWN)}

@part("pelvis_skirt", "pelvis", "Skirt pelvis", "Front and side skirt plates over a slim frame block.", PELVIS_PLUGS)
def _(F, A):
    F.box("frame", (0, 0, 0), (.56, .38, .30), (1.1, 1)); F.cyl("joint", (0, 0, -.06), .1, .66, 'X', 8)
    A.box("armor2", (0, -.23, -.04), (.30, .07, .38), (1.25, 1), .025, front=(.85, 1))
    A.box("accent", (0, -.27, .03), (.12, .03, .10), (1, 1), .01)
    for s in (-1, 1):
        A.box("armor", (s*.37, -.02, -.10), (.08, .40, .40), (1, 1), .025, rot=Matrix.Rotation(R(s*8), 3, 'Y'))
    A.box("armor2", (0, .22, -.02), (.40, .07, .30), (1.2, 1), .025)

@part("pelvis_heavy", "pelvis", "Heavy hip block", "Wide armoured hip with a belt band and thick side guards.", PELVIS_PLUGS)
def _(F, A):
    F.box("frame", (0, 0, 0), (.60, .42, .30), (1.1, 1)); F.cyl("joint", (0, 0, -.06), .12, .70, 'X', 8)
    A.box("armor", (0, 0, .10), (.70, .48, .12), (1.05, 1.05), .02)
    A.box("accent", (0, -.25, .10), (.22, .02, .08), (1, 1), .01)
    for s in (-1, 1):
        A.box("armor2", (s*.42, 0, -.06), (.14, .46, .34), (1, 1), .03)
    A.box("armor2", (0, -.24, -.08), (.26, .08, .26), (1.3, 1), .02)

# ---- TORSO. origin = waist (top of pelvis)
def torso_plugs(sh_x, sh_z, neck_z, back_y):
    return {"neck": ((0, .02, neck_z), UP), "shoulder_R": ((sh_x, 0, sh_z), OUT_), "shoulder_L": ((-sh_x, 0, sh_z), (-1, 0, 0)),
            "back": ((0, back_y, .72), BACK), "chest_emblem": ((0, -.42, .74), FWD)}

@part("torso_sleek", "torso", "Sleek chest", "Tapered real-robot chest with intake vents and a collar.", torso_plugs(.55, .86, 1.08, .32))
def _(F, A):
    F.box("frame", (0, 0, .18), (.40, .32, .34), (1.15, 1)); F.box("frame", (0, .02, .66), (.62, .50, .62), (1.2, 1))
    for i in range(3): F.box("joint", (0, -.17, .08+i*.1), (.30-i*.02, .04, .06), (1, 1), .01)
    A.box("armor", (0, -.02, .70), (.78, .60, .58), (1.45, 1.05), .05, front=(1, 1))
    A.box("armor2", (0, -.33, .74), (.46, .06, .34), (1.35, 1), .02)
    for s in (-1, 1):
        A.box("joint", (s*.20, -.36, .86), (.16, .03, .10), (1, 1), .0); A.box("glow", (s*.20, -.375, .86), (.12, .01, .04), (1, 1), 0)
    A.box("armor2", (0, 0, 1.02), (.46, .40, .10), (.8, .8), .02)

@part("torso_heavy", "torso", "Heavy chest", "Blocky siege chest: thick plates, rivet bars, low collar.", torso_plugs(.66, .84, 1.06, .38))
def _(F, A):
    F.box("frame", (0, 0, .18), (.46, .36, .34), (1.1, 1)); F.box("frame", (0, .02, .66), (.70, .56, .62), (1.1, 1))
    A.box("armor", (0, -.02, .68), (1.00, .70, .64), (1.15, 1.0), .05)
    A.box("armor2", (0, -.36, .62), (.70, .06, .40), (1.1, 1), .02)
    for s in (-1, 1):
        for i in range(3): A.cyl("joint", (s*.28, -.395, .50+i*.12), .025, .02, 'Y', 6)
    A.box("accent", (0, -.39, .80), (.36, .02, .08), (1, 1), 0)
    A.box("armor2", (0, 0, 1.00), (.70, .52, .10), (.9, .9), .02)
    A.box("armor2", (0, -.20, .20), (.40, .06, .24), (1.2, 1), .02)

@part("torso_emblem", "torso", "Emblem chest", "Super-robot chest: big V plate, glowing emblem, flared pecs.", torso_plugs(.62, .88, 1.10, .34))
def _(F, A):
    F.box("frame", (0, 0, .18), (.42, .34, .34), (1.15, 1)); F.box("frame", (0, .02, .66), (.66, .52, .62), (1.25, 1))
    A.box("armor", (0, -.02, .70), (.86, .62, .58), (1.5, 1.05), .05)
    for s in (-1, 1):
        A.box("armor2", (s*.24, -.33, .80), (.40, .08, .30), (1.2, 1), .02, rot=Matrix.Rotation(R(s*-14), 3, 'Y'))
    A.fin("accent", (0, -.38, .64), [(-.36, .26), (0, -.14), (.36, .26), (.26, .26), (0, .0), (-.26, .26)], .05)
    A.ball("glow", (0, -.37, .70), .07, 8)
    A.box("armor2", (0, 0, 1.04), (.48, .40, .10), (.8, .8), .02)

# ---- HEAD. origin = neck joint
HEAD_PLUGS = {"crest": ((0, -.05, .48), UP)}

@part("head_vanguard", "head", "Vanguard head", "Knight-style helm: V-fin crest, twin eyes, face plate.", HEAD_PLUGS)
def _(F, A):
    F.cyl("joint", (0, 0, .06), .09, .14, 'Z', 6); F.box("frame", (0, 0, .24), (.24, .26, .22), (1, 1), .02)
    A.box("armor", (0, .02, .29), (.32, .34, .26), (.85, .9), .04)
    A.box("armor2", (0, -.17, .22), (.18, .05, .12), (.6, 1), .015)            # face plate
    A.box("joint", (0, -.165, .31), (.24, .02, .06), (1, 1), 0)
    for s in (-1, 1): A.box("eye", (s*.06, -.175, .31), (.07, .01, .035), (1, 1), 0, rot=Matrix.Rotation(R(s*-10), 3, 'Y'))
    A.fin("accent2", (0, -.19, .41), [(0, 0), (.30, .26), (.24, .27), (0, .06), (-.24, .27), (-.30, .26)], .03)  # V-fin
    A.box("accent", (0, -.19, .40), (.06, .03, .06), (1, 1), .01)
    for s in (-1, 1): A.box("armor2", (s*.17, 0, .28), (.04, .14, .14), (1, .6), .01)

@part("head_bulwark", "head", "Bulwark head", "Heavy dome helm with a narrow visor slit and cheek guards.", HEAD_PLUGS)
def _(F, A):
    F.cyl("joint", (0, 0, .06), .10, .14, 'Z', 6); F.box("frame", (0, 0, .23), (.26, .26, .20), (1, 1), .02)
    A.box("armor", (0, 0, .30), (.38, .38, .28), (.7, .75), .05)
    A.box("joint", (0, -.18, .30), (.28, .03, .05), (1, 1), 0); A.box("eye", (0, -.195, .30), (.22, .01, .025), (1, 1), 0)
    for s in (-1, 1): A.box("armor2", (s*.17, -.06, .20), (.06, .24, .18), (1, .7), .015)
    A.box("accent", (0, 0, .46), (.08, .30, .05), (1, .8), .01)

@part("head_scout", "head", "Scout head", "Rounded helm with a mono-eye rail and a whip antenna.", HEAD_PLUGS)
def _(F, A):
    F.cyl("joint", (0, 0, .06), .08, .14, 'Z', 6)
    A.cyl("armor", (0, 0, .28), .17, .26, 'Z', 10, .13)
    A.box("joint", (0, -.13, .28), (.26, .06, .06), (1, 1), .01, rot=None)
    A.ball("eye", (.05, -.16, .28), .035, 8)
    A.cyl("armor2", (0, 0, .43), .12, .06, 'Z', 10, .06)
    A.box("accent", (.12, .04, .52), (.015, .015, .34), (1, 1), 0, rot=Matrix.Rotation(R(-14), 3, 'Y'))
    for s in (-1, 1): A.cyl("armor2", (s*.17, 0, .26), .05, .04, 'X', 6)

@part("head_titanheart", "head", "Titanheart head", "Super-robot helm: tall crest, mouth plate, horn ears.", HEAD_PLUGS)
def _(F, A):
    F.cyl("joint", (0, 0, .06), .09, .14, 'Z', 6); F.box("frame", (0, 0, .24), (.24, .26, .22), (1, 1), .02)
    A.box("armor", (0, .02, .30), (.34, .34, .28), (.9, .9), .04)
    A.box("armor2", (0, -.17, .21), (.20, .05, .12), (.7, 1), .015)
    for i in range(3): A.box("joint", (0, -.20, .18+i*.035), (.12, .01, .012), (1, 1), 0)
    A.box("joint", (0, -.165, .32), (.26, .02, .07), (1, 1), 0)
    for s in (-1, 1): A.box("eye", (s*.065, -.175, .32), (.09, .01, .04), (1, 1), 0, rot=Matrix.Rotation(R(s*-14), 3, 'Y'))
    A.fin("accent", (0, .0, .44), [(-.05, 0), (.05, 0), (.03, .30), (0, .34), (-.03, .30)], .14)
    for s in (-1, 1): A.fin("accent", (s*.19, 0, .33), [(0, 0), (s*.14, .22), (s*.06, .04)], .05)

# ---- BACKPACK. origin = back plug
BACK_PLUGS = {"dock": ((0, .30, 0), BACK)}   # combine plug: another mech / jet locks on here

@part("back_thrusters", "back", "Twin thrusters", "Two big bell thrusters with glowing nozzles.", BACK_PLUGS)
def _(F, A):
    F.box("frame", (0, .10, 0), (.56, .22, .52), (1, 1), .03)
    for s in (-1, 1):
        A.cyl("armor2", (s*.17, .22, -.04), .11, .40, 'Z', 8, .15); A.cyl("joint", (s*.17, .22, -.30), .14, .10, 'Z', 8, .17)
        A.cyl("glow", (s*.17, .22, -.36), .12, .02, 'Z', 8)
    A.box("armor", (0, .16, .18), (.50, .20, .18), (.9, 1), .03)

@part("back_wings", "back", "Wing binders", "Two angled wing plates with thruster strips, fold up or out.", BACK_PLUGS)
def _(F, A):
    F.box("frame", (0, .08, 0), (.44, .18, .44), (1, 1), .03)
    for s in (-1, 1):
        rot = Matrix.Rotation(R(s*-12), 3, 'Y') @ Matrix.Rotation(R(22), 3, 'X')
        wing = [(0, .05), (s*.35, .55), (s*1.05, .72), (s*1.12, .46), (s*.60, .06), (s*.16, -.26)]
        if s < 0: wing = list(reversed(wing))
        A.fin("armor", (s*.18, .20, .06), wing, .05, rot)
        stripe = [(s*.30, .30), (s*.95, .58), (s*1.0, .48), (s*.40, .16)]
        if s < 0: stripe = list(reversed(stripe))
        A.fin("accent", (s*.18, .17, .06), stripe, .06, rot)
        A.cyl("glow", (s*.16, .20, -.24), .07, .04, 'Z', 6)
    A.box("armor2", (0, .14, .02), (.36, .14, .30), (1, 1), .02)

@part("back_reactor", "back", "Reactor pack", "Heavy cylinder reactor with a glowing core window and vents.", BACK_PLUGS)
def _(F, A):
    F.box("frame", (0, .08, 0), (.56, .18, .56), (1, 1), .03)
    A.cyl("armor2", (0, .30, .02), .26, .56, 'Z', 10)
    A.box("glow", (0, .14, .02), (.10, .30, .30), (1, 1), 0)
    for i in range(3): A.cyl("joint", (0, .30, -.18+i*.18), .275, .04, 'Z', 10)
    A.cyl("accent", (0, .30, .33), .18, .08, 'Z', 10, .12)

# ---- SHOULDER (joint + pauldron). origin = shoulder plug on the torso
SH_PLUGS = {"arm": ((.18, 0, -.10), DOWN), "pod": ((.20, .05, .26), UP)}  # pod = weapon pod plug (missiles etc.)

@part("shoulder_round", "shoulder", "Round pauldron", "Smooth curved shoulder armour.", SH_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (.08, 0, 0), .15, .22, 'X', 8)
    A.box("armor", (.20, 0, .08), (.40, .50, .34), (.7, .8), .07)
    A.box("accent", (.38, 0, .06), (.03, .36, .20), (1, 1), 0)

@part("shoulder_block", "shoulder", "Heavy block", "Big square shoulder with vents, room for a weapon pod.", SH_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (.08, 0, 0), .17, .24, 'X', 8)
    A.box("armor2", (.22, 0, .06), (.52, .62, .40), (.95, .95), .04)
    for i in range(3): A.box("joint", (.49, 0, -.04+i*.08), (.02, .40, .04), (1, 1), 0)
    A.box("accent", (.22, -.32, .06), (.30, .02, .06), (1, 1), 0)

@part("shoulder_fin", "shoulder", "Fin pauldron", "Super-robot shoulder with a swept fin spike.", SH_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (.08, 0, 0), .15, .22, 'X', 8)
    A.box("armor", (.21, 0, .06), (.44, .54, .36), (.8, .85), .05)
    A.fin("accent", (.28, 0, .22), [(-.10, 0), (.12, 0), (.30, .34), (.20, .32)], .06)
    A.ball("glow", (.44, -.02, .04), .05, 6)

# ---- UPPER ARM. origin = top of the arm (under the shoulder)
UA_PLUGS = {"elbow": ((0, 0, -.62), DOWN)}

@part("upperarm_sleek", "upperarm", "Sleek upper arm", "Slim frame bar with a fitted armour sleeve.", UA_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .10, .16, 'X', 8); F.box("frame", (0, 0, -.32), (.16, .18, .50), (1, 1), .02)
    A.box("armor", (0, -.01, -.30), (.24, .26, .36), (1.08, 1.05), .03)
    A.box("armor2", (.13, 0, -.30), (.02, .18, .22), (1, 1), 0)

@part("upperarm_heavy", "upperarm", "Heavy upper arm", "Thick bicep armour, piston on the back.", UA_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .12, .18, 'X', 8); F.box("frame", (0, 0, -.32), (.20, .22, .50), (1, 1), .02)
    A.box("armor2", (0, -.02, -.28), (.32, .32, .40), (1.1, 1.1), .04)
    A.cyl("joint", (0, .18, -.34), .04, .40, 'Z', 6)

# ---- FOREARM. origin = elbow
FA_PLUGS = {"wrist": ((0, 0, -.66), DOWN), "mount": ((.16, 0, -.34), OUT_)}   # mount = shield / blade plug

@part("forearm_gauntlet", "forearm", "Gauntlet", "Tapered forearm guard with a glow stripe.", FA_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .11, .22, 'X', 8); F.box("frame", (0, 0, -.36), (.16, .18, .56), (1, 1), .02)
    A.box("armor", (0, -.01, -.38), (.28, .30, .52), (1.15, 1.1), .04)
    A.box("glow", (.145, -.01, -.40), (.01, .06, .30), (1, 1), 0)

@part("forearm_cuff", "forearm", "Heavy cuff", "Big armoured cuff, good for punching and shields.", FA_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .13, .24, 'X', 8); F.box("frame", (0, 0, -.36), (.18, .20, .56), (1, 1), .02)
    A.box("armor2", (0, -.01, -.42), (.38, .40, .44), (.9, .9), .05)
    A.box("accent", (0, -.21, -.42), (.20, .02, .20), (1, 1), 0)

@part("forearm_rocket", "forearm", "Rocket-fist housing", "Forearm with an exhaust ring at the wrist so the fist can fire off.", FA_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .11, .22, 'X', 8); F.box("frame", (0, 0, -.36), (.16, .18, .56), (1, 1), .02)
    A.box("armor", (0, -.01, -.34), (.30, .32, .44), (1.0, 1.0), .04)
    A.cyl("joint", (0, 0, -.62), .15, .10, 'Z', 8); A.cyl("glow", (0, 0, -.665), .12, .02, 'Z', 8)
    A.fin("accent", (.15, 0, -.30), [(0, -.18), (.10, .12), (0, .16)], .04)

# ---- HAND (real hand: palm + 4 fingers x 2 segments + thumb). origin = wrist
HS = 1.75   # hand scale (hands were too small)
HAND_PLUGS = {"grip": ((0, -.02*HS, -.20*HS), FWD)}

@part("hand_kit", "hand", "Model-kit hand", "Palm with 4 two-piece fingers and a thumb; poses open, fist or grip.", HAND_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, -.02*HS), .06*HS, .10*HS, 'X', 6)
    A.box("armor", (0, -.01*HS, -.12*HS), (.17*HS, .12*HS, .16*HS), (1.05, 1), .02*HS)
    A.box("armor2", (.0, -.075*HS, -.11*HS), (.13*HS, .02*HS, .10*HS), (1, 1), 0)

FINGERS = [(-.06, .045), (-.02, .05), (.02, .05), (.06, .045)]   # x, length of segment

# ---- PELVIS-down: THIGH. origin = hip joint
TH_PLUGS = {"knee": ((0, 0, -.90), DOWN)}

@part("thigh_sleek", "thigh", "Sleek thigh", "Long slim thigh with side armour.", TH_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .13, .24, 'X', 8); F.box("frame", (0, 0, -.46), (.20, .22, .76), (1, 1), .02)
    A.box("armor", (0, -.01, -.44), (.30, .32, .60), (1.15, 1.08), .04)
    A.box("armor2", (.16, 0, -.46), (.03, .22, .40), (1, 1), 0)

@part("thigh_heavy", "thigh", "Heavy thigh", "Thick thigh block with a hip thruster.", TH_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .15, .26, 'X', 8); F.box("frame", (0, 0, -.46), (.24, .26, .76), (1, 1), .02)
    A.box("armor2", (0, -.01, -.42), (.38, .40, .62), (1.12, 1.08), .05)
    A.cyl("glow", (.21, .06, -.30), .05, .03, 'X', 6)

# ---- SHIN. origin = knee
SN_PLUGS = {"ankle": ((0, 0, -.98), DOWN)}

@part("shin_sleek", "shin", "Sleek shin", "Shin with a knee guard and a calf thruster.", SN_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .12, .22, 'X', 8); F.box("frame", (0, 0, -.50), (.20, .22, .86), (1, 1), .02)
    A.box("accent", (0, -.17, .0), (.22, .10, .22), (.7, .8), .03)
    A.box("armor", (0, -.01, -.52), (.34, .38, .80), (.78, .85), .05)
    A.box("joint", (0, .19, -.62), (.14, .04, .26), (1, 1), 0); A.box("glow", (0, .21, -.74), (.10, .02, .06), (1, 1), 0)

@part("shin_heavy", "shin", "Heavy shin", "Massive boot-shin with a big knee block.", SN_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .14, .24, 'X', 8); F.box("frame", (0, 0, -.50), (.22, .24, .86), (1, 1), .02)
    A.box("armor2", (0, -.12, .02), (.32, .18, .28), (.8, .8), .03)
    A.box("armor", (0, -.01, -.56), (.44, .48, .78), (.8, .8), .05)
    for i in range(2): A.box("joint", (0, -.255, -.42-i*.16), (.26, .02, .05), (1, 1), 0)

@part("shin_super", "shin", "Flared boot", "Super-robot shin that flares wide at the top like a boot.", SN_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .12, .22, 'X', 8); F.box("frame", (0, 0, -.50), (.20, .22, .86), (1, 1), .02)
    A.box("armor", (0, -.01, -.54), (.34, .38, .74), (1.35, 1.3), .05)
    A.fin("accent", (0, -.24, -.18), [(-.18, .10), (.18, .10), (0, -.20)], .05)
    A.box("armor2", (0, -.01, -.94), (.36, .40, .10), (1, 1), .02)

# ---- FOOT. origin = ankle (ankle sits .22 above the ground)
FT_PLUGS = {"ground": ((0, -.10, -.22), DOWN)}

@part("foot_heeled", "foot", "Heeled foot", "Pointed toe, heel spur, hinged toe plate.", FT_PLUGS, side=True)
def _(F, A):
    F.ball("joint", (0, 0, 0), .10, 8)
    A.box("armor", (0, -.10, -.13), (.30, .62, .18), (.85, .7), .03, front=(.7, .8))
    A.box("armor2", (0, -.46, -.17), (.24, .14, .10), (.8, .6), .02)
    A.fin("joint", (0, .20, -.12), [(-.04, .04), (.04, .04), (0, -.10)], .10, rot=Matrix.Rotation(R(-90), 3, 'Z') @ Matrix.Rotation(R(0), 3, 'X'))
    A.box("joint", (0, .22, -.18), (.12, .14, .08), (1, 1), .01)

@part("foot_tread", "foot", "Heavy tread", "Wide flat foot with a tread sole for big stomps.", FT_PLUGS, side=True)
def _(F, A):
    F.ball("joint", (0, 0, 0), .11, 8)
    A.box("armor2", (0, -.08, -.12), (.40, .70, .20), (.9, .85), .04)
    A.box("joint", (0, -.08, -.21), (.42, .72, .04), (1, 1), .01)
    for i in range(4): A.box("frame", (0, -.36+i*.18, -.235), (.42, .04, .02), (1, 1), 0)

@part("foot_talon", "foot", "Talon foot", "Three-toe clawed foot for beast-style mechs.", FT_PLUGS, side=True)
def _(F, A):
    F.ball("joint", (0, 0, 0), .10, 8)
    A.box("armor", (0, -.02, -.12), (.26, .26, .16), (.8, .8), .03)
    for ang in (-24, 0, 24):
        rot = Matrix.Rotation(R(ang), 3, 'Z')
        mid = rot @ Vector((0, -.24, 0)); A.box("armor2", (mid.x, mid.y, -.16), (.08, .36, .07), (.6, .9), .01, rot=rot)
        tip = rot @ Vector((0, -.46, 0)); A.box("accent", (tip.x, tip.y, -.17), (.06, .12, .05), (.2, .5), 0, rot=rot)
    A.box("armor2", (0, .16, -.16), (.06, .20, .06), (.5, .9), .01)



# ================================================================ ROUND 2 (Nov 13): more mech families, same plugs
# real robot (Ranger), transforming jet (Falcon), knight (Paladin), bio/horror (Wraith), grunt (Mule),
# police/work (Patrol), super robot extras (Lionheart). All original designs.
SCHEMES.update({
    "ranger": dict(armor="e6e3da", armor2="3d4a5c", frame="3a404c", joint="22262e", accent="e0b230", accent2="c8302c", glow="ff7a3a", eye="7dff8a"),
    "falcon": dict(armor="dfe3ea", armor2="2b3a52", frame="3a404c", joint="21252d", accent="e86a1c", accent2="2a2d33", glow="6ad8ff", eye="6ad8ff"),
    "paladin": dict(armor="c9c3b4", armor2="6d1f2a", frame="35383f", joint="1e2026", accent="d4a33a", accent2="efe9da", glow="8fe8ff", eye="8fe8ff"),
    "wraith": dict(armor="4b2f6b", armor2="2b6b3a", frame="2a2633", joint="17141d", accent="9be24a", accent2="e8a020", glow="ff4f9a", eye="f8ff5a"),
    "mule": dict(armor="c8a13a", armor2="6f6a5c", frame="3a3d40", joint="202224", accent="2a2a2a", accent2="d43c2a", glow="ffd060", eye="ff3030"),
    "patrol": dict(armor="f2f2f2", armor2="1c2d63", frame="333844", joint="1d2029", accent="e83a3a", accent2="2f6fe8", glow="ffffff", eye="8af6ff"),
    "lionheart": dict(armor="2a2f6e", armor2="e6e2d6", frame="383c48", joint="20232c", accent="f2b51e", accent2="d0302a", glow="ff9a2a", eye="fff07a"),
})
RX = lambda d: Matrix.Rotation(R(d), 3, 'X'); RY = lambda d: Matrix.Rotation(R(d), 3, 'Y'); RZ = lambda d: Matrix.Rotation(R(d), 3, 'Z')

# ---- heads
@part("head_ranger", "head", "Ranger head", "Real-robot head: goggle visor, twin antennae, chin vents, side guns.", HEAD_PLUGS)
def _(F, A):
    F.cyl("joint", (0, 0, .06), .09, .14, 'Z', 6); F.box("frame", (0, 0, .24), (.24, .26, .22), (1, 1), .02)
    A.box("armor", (0, .02, .30), (.30, .32, .26), (.88, .9), .04)
    A.box("joint", (0, -.16, .32), (.26, .03, .07), (1, 1), 0); A.box("eye", (0, -.175, .32), (.22, .01, .045), (1, 1), 0)
    A.box("armor2", (0, -.17, .21), (.14, .05, .09), (.7, 1), .015)
    for i in (-1, 1): A.box("joint", (i*.03, -.20, .20), (.02, .01, .06), (1, 1), 0)
    for s in (-1, 1):
        A.box("accent", (s*.08, -.10, .48), (.025, .025, .22), (1, 1), 0, rot=RY(s*24))
        A.cyl("joint", (s*.17, -.06, .36), .025, .10, 'Y', 6)

@part("head_falcon", "head", "Falcon head", "Fighter-canopy head with a pointed nose and small fins (jet mechs).", HEAD_PLUGS)
def _(F, A):
    F.cyl("joint", (0, 0, .06), .08, .14, 'Z', 6)
    A.box("armor", (0, .02, .27), (.26, .40, .22), (.8, .9), .03, front=(.45, .6))
    A.box("glow", (0, -.04, .40), (.12, .22, .06), (.6, .7), .015)
    A.box("joint", (0, -.20, .26), (.18, .02, .05), (1, 1), 0); A.box("eye", (0, -.215, .26), (.14, .01, .025), (1, 1), 0)
    for s in (-1, 1): A.fin("accent", (s*.13, .10, .30), [(0, 0), (s*.10, .14), (s*.10, .04)], .03)

@part("head_paladin", "head", "Paladin head", "Knight helm: T-slit visor, front-to-back crest, cheek guards.", HEAD_PLUGS)
def _(F, A):
    F.cyl("joint", (0, 0, .06), .09, .14, 'Z', 6)
    A.box("armor", (0, 0, .30), (.32, .36, .34), (.85, .9), .05)
    A.box("joint", (0, -.18, .34), (.20, .02, .04), (1, 1), 0); A.box("joint", (0, -.18, .27), (.04, .02, .12), (1, 1), 0)
    A.box("eye", (0, -.19, .34), (.16, .01, .02), (1, 1), 0)
    A.fin("armor2", (0, 0, .47), [(-.22, 0), (.18, 0), (.10, .14), (-.24, .10)], .05, rot=RZ(90))
    for s in (-1, 1): A.box("accent", (s*.17, -.04, .24), (.04, .22, .16), (1, .7), .01)

@part("head_wraith", "head", "Wraith head", "Bio/horror head: long jaw, open teeth, single horn, wild eyes.", HEAD_PLUGS)
def _(F, A):
    F.cyl("joint", (0, 0, .06), .08, .14, 'Z', 6)
    A.box("armor", (0, .0, .32), (.26, .34, .24), (.8, .9), .03, front=(.7, .8))
    A.box("armor", (0, -.10, .18), (.20, .30, .08), (.8, .9), .02)          # jaw
    for i in range(4): A.box("accent2", (-.06+i*.04, -.22, .23), (.02, .02, .05), (.4, .4), 0)
    for s in (-1, 1): A.box("eye", (s*.07, -.17, .36), (.06, .01, .05), (1, 1), 0, rot=RY(s*-25))
    A.fin("armor2", (0, -.06, .44), [(-.04, 0), (.04, 0), (0, .30)], .06, rot=RX(-20))

@part("head_mule", "head", "Mule head", "Grunt box head with a three-lens camera turret.", HEAD_PLUGS)
def _(F, A):
    F.cyl("joint", (0, 0, .06), .09, .14, 'Z', 6)
    A.box("armor", (0, 0, .27), (.30, .30, .24), (.95, .95), .03)
    A.cyl("armor2", (0, -.16, .28), .09, .06, 'Y', 8)
    for i, (dx, dz) in enumerate(((0, .03), (-.04, -.025), (.04, -.025))):
        A.cyl("eye", (dx, -.20, .28+dz), .025 if i else .032, .03, 'Y', 6)
    A.box("joint", (.12, .06, .44), (.02, .02, .14), (1, 1), 0)

@part("head_patrol", "head", "Patrol head", "Police / work head with a light bar on top.", HEAD_PLUGS)
def _(F, A):
    F.cyl("joint", (0, 0, .06), .09, .14, 'Z', 6)
    A.cyl("armor", (0, 0, .29), .16, .26, 'Z', 10, .14)
    A.box("joint", (0, -.13, .30), (.24, .06, .07), (1, 1), .01); A.box("eye", (0, -.16, .30), (.20, .01, .04), (1, 1), 0)
    A.box("armor2", (0, 0, .44), (.26, .10, .04), (1, 1), .01)
    A.box("accent", (-.07, 0, .48), (.11, .08, .05), (1, 1), .01); A.box("accent2", (.07, 0, .48), (.11, .08, .05), (1, 1), .01)

# ---- chests
@part("torso_cockpit", "torso", "Cockpit chest", "Real-robot chest: cockpit hatch, twin upper vents, tall collar.", torso_plugs(.56, .86, 1.08, .32))
def _(F, A):
    F.box("frame", (0, 0, .18), (.40, .32, .34), (1.15, 1)); F.box("frame", (0, .02, .66), (.62, .50, .62), (1.2, 1))
    A.box("armor2", (0, -.02, .70), (.80, .60, .58), (1.35, 1.05), .05)
    A.box("armor", (0, -.33, .62), (.28, .06, .34), (1, 1), .02)
    for s in (-1, 1):
        A.box("armor", (s*.24, -.30, .86), (.22, .06, .18), (1, 1), .02)
        for i in range(3): A.box("joint", (s*.24, -.335, .81+i*.05), (.16, .01, .02), (1, 1), 0)
    A.box("accent", (0, -.02, 1.02), (.40, .38, .10), (.8, .8), .02)
    A.box("accent2", (0, -.24, .26), (.20, .06, .14), (1, 1), .01)

@part("torso_lion", "torso", "Beast-face chest", "Super-robot chest with a roaring beast face, glowing eyes and fangs.", torso_plugs(.64, .88, 1.10, .34))
def _(F, A):
    F.box("frame", (0, 0, .18), (.42, .34, .34), (1.15, 1)); F.box("frame", (0, .02, .66), (.66, .52, .62), (1.25, 1))
    A.box("armor", (0, -.02, .70), (.88, .62, .58), (1.45, 1.05), .05)
    A.box("accent", (0, -.33, .70), (.56, .08, .44), (1.15, 1), .03)                # face plate
    for s in (-1, 1):
        A.box("eye", (s*.13, -.38, .80), (.12, .01, .05), (1, 1), 0, rot=RY(s*-15))
        A.fin("armor2", (s*.07, -.38, .56), [(-.03, .06), (.03, .06), (0, -.08)], .03)  # fangs
        A.fin("accent2", (s*.27, -.34, .90), [(0, 0), (s*.12, .16), (s*.06, -.02)], .05)  # ears
    A.box("joint", (0, -.385, .70), (.08, .02, .06), (1, 1), 0)

@part("torso_knight", "torso", "Tabard chest", "Knight chest: breastplate with a long tabard hanging in front.", torso_plugs(.58, .86, 1.08, .32))
def _(F, A):
    F.box("frame", (0, 0, .18), (.40, .32, .34), (1.15, 1)); F.box("frame", (0, .02, .66), (.62, .50, .62), (1.2, 1))
    A.box("armor", (0, -.02, .72), (.78, .58, .54), (1.3, 1.05), .06, front=(1, .9))
    A.box("armor2", (0, -.31, .30), (.30, .03, .80), (1, 1), .01)
    A.fin("accent", (0, -.335, .74), [(-.08, -.10), (.08, -.10), (.08, .06), (0, .14), (-.08, .06)], .02)
    A.box("accent", (0, -.02, .40), (.66, .48, .06), (1, 1), .01)

@part("torso_bio", "torso", "Ribbed bio chest", "Bio/horror chest: rib bars over a glowing core.", torso_plugs(.54, .86, 1.10, .30))
def _(F, A):
    F.box("frame", (0, 0, .18), (.36, .30, .34), (1.15, 1)); F.box("frame", (0, .02, .66), (.58, .46, .62), (1.25, 1))
    A.ball("glow", (0, -.20, .66), .12, 10)
    for i in range(4):
        A.box("armor", (0, -.06, .48+i*.13), (.70-abs(i-1.5)*.08, .48, .07), (1, 1), .015)
    A.box("armor", (0, .05, .80), (.62, .40, .40), (1.1, 1), .04)
    A.box("armor2", (0, -.02, 1.02), (.36, .30, .10), (.8, .8), .02)

@part("torso_grunt", "torso", "Grunt hatch chest", "Boxy grunt chest with a round cockpit hatch and grab rails.", torso_plugs(.60, .84, 1.06, .36))
def _(F, A):
    F.box("frame", (0, 0, .18), (.44, .34, .34), (1.1, 1)); F.box("frame", (0, .02, .66), (.66, .52, .62), (1.1, 1))
    A.box("armor", (0, -.02, .68), (.86, .64, .60), (1.05, 1), .04)
    A.cyl("armor2", (0, -.34, .70), .17, .06, 'Y', 10); A.cyl("joint", (0, -.37, .70), .05, .02, 'Y', 6)
    for s in (-1, 1): A.box("accent", (s*.34, -.36, .70), (.03, .03, .36), (1, 1), 0)
    for i in range(2): A.box("accent2", (0, -.335, .44+i*.06), (.5, .01, .03), (1, 1), 0)

# ---- backpacks
BACK2 = {"dock": ((0, .30, 0), BACK)}
@part("back_jetfold", "back", "Jet fold-pack", "Transforming jet parts: nose cone, intakes and tail fins fold onto the back.", BACK2)
def _(F, A):
    F.box("frame", (0, .08, 0), (.44, .18, .44), (1, 1), .03)
    A.box("armor", (0, .26, .30), (.30, .22, .70), (.3, .3), .03)                 # nose cone up
    A.box("glow", (0, .20, .52), (.10, .10, .20), (.5, .5), .01)                  # canopy
    for s in (-1, 1):
        A.box("armor2", (s*.24, .22, -.10), (.16, .24, .30), (1, 1), .02); A.box("joint", (s*.24, .22, .07), (.12, .20, .04), (1, 1), 0)
        A.fin("accent", (s*.30, .32, -.28), [(0, 0), (s*.28, -.16), (s*.30, -.04), (s*.04, .14)], .04)
    A.cyl("glow", (0, .22, -.30), .08, .04, 'Z', 8)

@part("back_sabers", "back", "Saber rack", "Real-robot pack: two beam-saber hilts and small thrusters.", BACK2)
def _(F, A):
    F.box("frame", (0, .08, 0), (.50, .18, .48), (1, 1), .03)
    A.box("armor2", (0, .16, .04), (.46, .14, .40), (.9, 1), .03)
    for s in (-1, 1):
        A.cyl("armor", (s*.16, .26, .36), .04, .30, 'Z', 6, rot=RY(s*-20)); A.cyl("joint", (s*.22, .26, .52), .045, .04, 'Z', 6)
        A.cyl("joint", (s*.15, .24, -.24), .07, .14, 'Z', 8, .09); A.cyl("glow", (s*.15, .24, -.32), .07, .02, 'Z', 8)

@part("back_ammo", "back", "Ammo pack", "Grunt pack: ammo drum, feed belt and a radio antenna.", BACK2)
def _(F, A):
    F.box("frame", (0, .08, 0), (.52, .18, .50), (1, 1), .03)
    A.box("armor2", (0, .22, 0), (.56, .28, .52), (1, 1), .03)
    A.cyl("armor", (-.14, .40, .04), .14, .44, 'Z', 10)
    for i in range(4): A.box("accent2", (.12+i*.03, .37, -.10+i*.07), (.06, .04, .04), (1, 1), 0)
    A.box("joint", (.22, .26, .52), (.02, .02, .60), (1, 1), 0)

@part("back_pylons", "back", "Spine pylons", "Bio/horror pack: two tall spine pylons with glowing tips.", BACK2)
def _(F, A):
    F.box("frame", (0, .08, 0), (.42, .18, .44), (1, 1), .03)
    for s in (-1, 1):
        A.box("armor2", (s*.14, .22, .38), (.10, .10, .90), (.3, .3), .02, rot=RY(s*-12))
        A.ball("glow", (s*.24, .22, .84), .05, 6)
    A.box("armor", (0, .18, -.02), (.34, .14, .36), (1, 1), .03)

# ---- shoulders
@part("shoulder_layered", "shoulder", "Layered pauldron", "Knight shoulder: three overlapping plates with a gold trim.", SH_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (.08, 0, 0), .15, .22, 'X', 8)
    for i in range(3):
        A.box("armor" if i % 2 == 0 else "armor2", (.24+i*.03, 0, .14-i*.13), (.46-i*.04, .56-i*.04, .14), (.9, .9), .02, rot=RY(-18-i*8))
    A.box("accent", (.27, 0, .22), (.42, .54, .03), (.9, .9), 0, rot=RY(-18))

@part("shoulder_pylon", "shoulder", "Pylon shoulder", "Bio/horror shoulder with a tall pylon fin.", SH_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (.08, 0, 0), .14, .22, 'X', 8)
    A.box("armor", (.20, 0, .02), (.34, .40, .30), (.8, .8), .04)
    A.box("armor2", (.24, 0, .40), (.14, .30, .60), (.4, .6), .02, rot=RY(-10))
    A.ball("glow", (.36, -.12, .02), .045, 6)

@part("shoulder_spike", "shoulder", "Spiked roller", "Super-robot shoulder: round guard with three spikes.", SH_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (.08, 0, 0), .15, .22, 'X', 8)
    A.cyl("armor", (.22, 0, .06), .24, .36, 'X', 10)
    for ang in (-35, 0, 35):
        rot = RX(ang); A.box("accent", tuple(rot @ Vector((0, 0, .26)) + Vector((.22, 0, .06))), (.08, .08, .18), (.1, .1), 0, rot=rot)

@part("shoulder_siren", "shoulder", "Siren shoulder", "Police / work shoulder block with a warning light.", SH_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (.08, 0, 0), .15, .22, 'X', 8)
    A.box("armor2", (.22, 0, .06), (.44, .52, .36), (.95, .95), .04)
    A.box("armor", (.22, -.27, .06), (.36, .02, .20), (1, 1), 0)
    A.cyl("accent", (.22, 0, .28), .07, .08, 'Z', 8)

# ---- forearms
@part("forearm_intake", "forearm", "Intake gauntlet", "Jet-mech forearm with an air intake and a fin.", FA_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .11, .22, 'X', 8); F.box("frame", (0, 0, -.36), (.16, .18, .56), (1, 1), .02)
    A.box("armor", (0, -.01, -.38), (.28, .32, .52), (1.1, 1.05), .04)
    A.box("joint", (0, -.17, -.20), (.18, .02, .12), (1, 1), 0)
    A.fin("accent", (.14, .06, -.42), [(0, -.20), (.12, .10), (0, .16)], .03)

@part("forearm_bracer", "forearm", "Knight bracer", "Flared knight bracer with a gold rim.", FA_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .11, .22, 'X', 8); F.box("frame", (0, 0, -.36), (.16, .18, .56), (1, 1), .02)
    A.box("armor", (0, -.01, -.40), (.34, .36, .48), (.7, .7), .04)
    A.box("accent", (0, -.01, -.62), (.36, .38, .05), (1, 1), .01)

@part("forearm_spines", "forearm", "Spined forearm", "Bio/horror forearm with a row of back spines.", FA_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .10, .20, 'X', 8); F.box("frame", (0, 0, -.36), (.14, .16, .56), (1, 1), .02)
    A.box("armor", (0, 0, -.36), (.22, .24, .50), (1.15, 1.1), .04)
    for i in range(3): A.box("armor2", (.10, .08, -.20-i*.14), (.04, .04, .16), (.1, .1), 0, rot=RY(-40))

# ---- pelvis
@part("pelvis_longskirt", "pelvis", "Long skirt", "Real-robot hip: split long front skirts and big side skirts.", PELVIS_PLUGS)
def _(F, A):
    F.box("frame", (0, 0, 0), (.56, .38, .30), (1.1, 1)); F.cyl("joint", (0, 0, -.06), .1, .66, 'X', 8)
    for s in (-1, 1):
        A.box("armor", (s*.12, -.23, -.14), (.20, .06, .44), (1.1, 1), .02, rot=RX(10))
        A.box("armor2", (s*.38, -.01, -.16), (.06, .44, .48), (1, 1), .02, rot=RY(s*10))
    A.box("accent2", (0, -.25, .06), (.14, .04, .08), (1, 1), .01)

@part("pelvis_fauld", "pelvis", "Fauld skirt", "Knight hip: overlapping plate bands all round.", PELVIS_PLUGS)
def _(F, A):
    F.box("frame", (0, 0, 0), (.56, .38, .30), (1.1, 1)); F.cyl("joint", (0, 0, -.06), .1, .66, 'X', 8)
    for i in range(3):
        A.box("armor" if i % 2 == 0 else "armor2", (0, -.01, .06-i*.12), (.74+i*.04, .50+i*.04, .12), (.95, .95), .02)
    A.box("accent", (0, -.29, .06), (.16, .02, .08), (1, 1), 0)

# ---- shins and feet
@part("shin_nacelle", "shin", "Engine nacelle", "Jet-mech shin: an engine with a big nozzle that becomes the jet's engine.", SN_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .12, .22, 'X', 8); F.box("frame", (0, 0, -.50), (.20, .22, .86), (1, 1), .02)
    A.cyl("armor", (0, .02, -.50), .19, .76, 'Z', 10, .21)
    A.cyl("joint", (0, .02, -.92), .20, .10, 'Z', 10, .23); A.cyl("glow", (0, .02, -.97), .16, .02, 'Z', 10)
    A.box("armor2", (0, -.18, -.40), (.16, .06, .44), (1, 1), .02)
    A.fin("accent", (.17, .08, -.30), [(0, -.16), (.14, .10), (0, .14)], .03)

@part("shin_bio", "shin", "Bio shin", "Long thin bio/horror shin with a back spur.", SN_PLUGS, side=True)
def _(F, A):
    F.cyl("joint", (0, 0, 0), .10, .20, 'X', 8); F.box("frame", (0, 0, -.50), (.16, .18, .86), (1, 1), .02)
    A.box("armor", (0, -.02, -.48), (.22, .26, .80), (.7, .8), .04)
    A.box("armor2", (0, .14, -.22), (.06, .06, .30), (.1, .1), 0, rot=RX(-35))

@part("foot_roller", "foot", "Roller foot", "Grunt foot with dash wheels in the sole.", FT_PLUGS, side=True)
def _(F, A):
    F.ball("joint", (0, 0, 0), .10, 8)
    A.box("armor2", (0, -.08, -.10), (.34, .62, .16), (.9, .85), .03)
    for y in (-.32, .12):
        A.cyl("joint", (0, y, -.18), .07, .30, 'X', 8); A.cyl("accent", (.16, y, -.18), .04, .02, 'X', 6)

@part("foot_sabaton", "foot", "Sabaton", "Knight foot: pointed armoured boot in overlapping plates.", FT_PLUGS, side=True)
def _(F, A):
    F.ball("joint", (0, 0, 0), .10, 8)
    for i in range(3): A.box("armor" if i % 2 == 0 else "armor2", (0, -.06-i*.16, -.13), (.30-i*.05, .20, .16-i*.02), (.9, .9), .02)
    A.box("armor", (0, -.54, -.16), (.10, .16, .08), (.2, .3), .01)
    A.box("accent", (0, .16, -.16), (.24, .12, .10), (1, 1), .01)


# ---------------------------------------------------------------- build parts as objects
def make_part(pid, scheme, mirror=False, tag=""):
    P = PARTS[pid]; F, A = PB(), PB()
    P["fn"](F, A)
    nm = f"{tag}{pid}{'_L' if mirror else ('_R' if P['side'] else '')}"
    fo = F.to_obj(nm, scheme, mirror); ao = A.to_obj(nm + "_armor", scheme, mirror)
    ao.parent = fo; fo["part"] = pid; fo["kit"] = "mech"; ao["armor_of"] = nm
    plugs = {}
    for k, (pos, d) in P["plugs"].items():
        p = Vector(pos); dd = Vector(d)
        if mirror: p.x, dd.x = -p.x, -dd.x
        plugs[k] = (p, dd)
    fo["plugs"] = {k: list(v[0]) for k, v in plugs.items()}
    return fo, ao, plugs


def make_hand(scheme, mirror, tag, pose="fist"):
    """Hand = palm part + finger segments, each its own object with its origin on its knuckle."""
    fo, ao, plugs = make_part("hand_kit", scheme, mirror, tag)
    sx = -1 if mirror else 1
    curl = {"fist": (85, 95), "open": (8, 6), "grip": (70, 80)}[pose]
    segs = []
    for i, (x, ln) in enumerate(FINGERS):
        parent = fo; z = -.20*HS
        for j in range(2):
            pb = PB(); L = (ln*1.6 if j == 0 else ln*1.3)*HS
            pb.box("frame" if j == 0 else "armor2", (0, 0, -L/2), (.035*HS, .045*HS, L), (.9, .9), .006*HS)
            o = pb.to_obj(f"{fo.name}_f{i}{j}", scheme, mirror)
            o.parent = parent; o.location = (sx*x*HS, -.01*HS, z) if j == 0 else (0, 0, -ln*1.6*HS)
            o.rotation_euler.x = R(-curl[j])
            o["finger"] = f"{i}{j}"; segs.append(o); parent = o
    parent = fo
    for j in range(2):
        pb = PB(); pb.box("frame" if j == 0 else "armor2", (0, 0, -.04*HS), (.04*HS, .05*HS, .08*HS), (.9, .9), .006*HS)
        o = pb.to_obj(f"{fo.name}_t{j}", scheme, mirror); o.parent = parent
        o.location = (sx*.09*HS, -.04*HS, -.08*HS) if j == 0 else (0, 0, -.08*HS)
        o.rotation_euler = Euler((R(-curl[0]*.6), 0, R(sx*35))) if j == 0 else Euler((R(-curl[1]*.5), 0, 0))
        o["finger"] = f"t{j}"; segs.append(o); parent = o
    return fo, ao, plugs, segs


# ---------------------------------------------------------------- assemble a mech from a build sheet
def assemble(name, sheet, scheme, at=(0, 0, 0), pose=None, hands="fist"):
    pose = pose or {}
    objs = []
    root = bpy.data.objects.new(name, None); bpy.context.scene.collection.objects.link(root); root.location = at
    def attach(pid, parent, plug_pos, mirror=False, joint=None):
        fo, ao, plugs = make_part(pid, scheme, mirror, name + ".")
        fo.parent = parent; fo.location = plug_pos
        if joint in pose:
            e = pose[joint]; fo.rotation_euler = Euler((R(e[0]), R(e[1] * (-1 if mirror else 1)), R(e[2] * (-1 if mirror else 1))))
        objs.extend([fo, ao]); return fo, plugs
    pel, pp = attach(sheet["pelvis"], root, (0, 0, 2.18), joint="pelvis")
    tor, tp = attach(sheet["torso"], pel, pp["waist"][0], joint="waist")
    hd, _ = attach(sheet["head"], tor, tp["neck"][0], joint="neck")
    bk, _ = attach(sheet["back"], tor, tp["back"][0])
    for side, m in (("R", False), ("L", True)):
        sh, sp = attach(sheet["shoulder"], tor, tp["shoulder_" + side][0], m, "shoulder")
        ua, up = attach(sheet["upperarm"], sh, sp["arm"][0], m, "upperarm")
        fa, fp = attach(sheet["forearm"], ua, up["elbow"][0], m, "elbow")
        hpose = hands if isinstance(hands, str) else hands[side]
        h, ha, hp, segs = make_hand(scheme, m, name + ".", hpose)
        h.parent = fa; h.location = fp["wrist"][0]; objs += [h, ha] + segs
        th, thp = attach(sheet["thigh"], pel, pp["hip_" + side][0], m, "hip")
        sn, snp = attach(sheet["shin"], th, thp["knee"][0], m, "knee")
        ft, _ = attach(sheet["foot"], sn, snp["ankle"][0], m, "ankle")
    bpy.context.view_layer.update()
    # stand on the ground: drop the root so the lowest point touches z=0
    low = min((o.matrix_world @ Vector(c)).z for o in objs if o.type == 'MESH' for c in o.bound_box)
    root.location.z -= low
    bpy.context.view_layer.update()
    return root, objs


# ---------------------------------------------------------------- hitboxes (box + capsule) and export
def world_bbox(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def local_bbox(o, extra=()):
    pts = [Vector(c) for c in o.bound_box]
    for e in extra: pts += [o.matrix_world.inverted() @ (e.matrix_world @ Vector(c)) for c in e.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def hitbox_of(lo, hi):
    c = (lo+hi)/2; s = hi-lo
    ax = max(range(3), key=lambda i: s[i]); others = [s[i] for i in range(3) if i != ax]
    r = max(others)/2*.92
    cap = {"axis": "xyz"[ax], "radius": round(r, 3), "length": round(max(s[ax]-2*r, 0), 3)}
    yup = lambda v: [round(v.x, 3), round(v.z, 3), round(-v.y, 3)]
    return {"box": {"centre": yup(c), "size": [round(s.x, 3), round(s.z, 3), round(s.y, 3)]}, "capsule": {**cap, "centre": yup(c)}}


def add_hitbox_obj(fo, lo, hi, show=False):
    me = bpy.data.meshes.new("HB_" + fo.name); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x*(hi.x-lo.x), v.co.y*(hi.y-lo.y), v.co.z*(hi.z-lo.z))) + (lo+hi)/2
    bm.to_mesh(me); bm.free(); hb = bpy.data.objects.new("HB_" + fo.name, me); bpy.context.scene.collection.objects.link(hb)
    hb.parent = fo; hb.display_type = 'WIRE'; hb.hide_render = not show; hb["hitbox"] = True
    return hb


def pack(arr): return base64.b64encode(struct.pack("<%dh" % len(arr), *[int(round(v*200)) for v in arr])).decode()


def mesh_json(o):
    """Triangles grouped by material key, three.js axes (x, z, -y), packed int16 / 200."""
    me = o.data; me.calc_loop_triangles(); keys = [s.material["key"] for s in o.material_slots]
    g = {}
    for t in me.loop_triangles:
        arr = g.setdefault(keys[t.material_index], [])
        for vi in t.vertices:
            v = me.vertices[vi].co; arr += [v.x, v.z, -v.y]
    return {k: pack(v) for k, v in g.items()}


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True); MATS.clear()


SHEETS = {
    "Vanguard": dict(pelvis="pelvis_skirt", torso="torso_sleek", head="head_vanguard", back="back_wings", shoulder="shoulder_round",
                     upperarm="upperarm_sleek", forearm="forearm_gauntlet", thigh="thigh_sleek", shin="shin_sleek", foot="foot_heeled"),
    "Bulwark": dict(pelvis="pelvis_heavy", torso="torso_heavy", head="head_bulwark", back="back_reactor", shoulder="shoulder_block",
                    upperarm="upperarm_heavy", forearm="forearm_cuff", thigh="thigh_heavy", shin="shin_heavy", foot="foot_tread"),
    "Titanheart": dict(pelvis="pelvis_skirt", torso="torso_emblem", head="head_titanheart", back="back_thrusters", shoulder="shoulder_fin",
                       upperarm="upperarm_sleek", forearm="forearm_rocket", thigh="thigh_heavy", shin="shin_super", foot="foot_heeled"),
}
SHEETS.update({
    "Ranger": dict(pelvis="pelvis_longskirt", torso="torso_cockpit", head="head_ranger", back="back_sabers", shoulder="shoulder_round",
                   upperarm="upperarm_sleek", forearm="forearm_gauntlet", thigh="thigh_sleek", shin="shin_sleek", foot="foot_heeled"),
    "Falcon": dict(pelvis="pelvis_skirt", torso="torso_sleek", head="head_falcon", back="back_jetfold", shoulder="shoulder_round",
                   upperarm="upperarm_sleek", forearm="forearm_intake", thigh="thigh_sleek", shin="shin_nacelle", foot="foot_heeled"),
    "Paladin": dict(pelvis="pelvis_fauld", torso="torso_knight", head="head_paladin", back="back_thrusters", shoulder="shoulder_layered",
                    upperarm="upperarm_heavy", forearm="forearm_bracer", thigh="thigh_heavy", shin="shin_heavy", foot="foot_sabaton"),
    "Wraith": dict(pelvis="pelvis_skirt", torso="torso_bio", head="head_wraith", back="back_pylons", shoulder="shoulder_pylon",
                   upperarm="upperarm_sleek", forearm="forearm_spines", thigh="thigh_sleek", shin="shin_bio", foot="foot_talon"),
    "Mule": dict(pelvis="pelvis_heavy", torso="torso_grunt", head="head_mule", back="back_ammo", shoulder="shoulder_block",
                 upperarm="upperarm_heavy", forearm="forearm_cuff", thigh="thigh_heavy", shin="shin_heavy", foot="foot_roller"),
    "Patrol": dict(pelvis="pelvis_skirt", torso="torso_heavy", head="head_patrol", back="back_reactor", shoulder="shoulder_siren",
                   upperarm="upperarm_sleek", forearm="forearm_cuff", thigh="thigh_sleek", shin="shin_sleek", foot="foot_tread"),
    "Lionheart": dict(pelvis="pelvis_skirt", torso="torso_lion", head="head_titanheart", back="back_thrusters", shoulder="shoulder_spike",
                      upperarm="upperarm_heavy", forearm="forearm_rocket", thigh="thigh_heavy", shin="shin_super", foot="foot_heeled"),
})
POSE_HERO = {"shoulder": (0, -12, 0), "elbow": (-18, 0, 0), "hip": (0, -5, 0), "knee": (8, 0, 0), "ankle": (-3, 5, 0), "neck": (-4, 0, 0)}


def main():
    reset()
    kit = {"kit": "mech", "version": 1, "made": "Nov 13, 2026", "by": "MajorasPride", "ticket": "T042",
           "units": "kit units: mech ~4.6 tall; x4 = Titan Clash game units", "axes": "three.js y-up (x, z, -y from Blender)",
           "schemes": {k: {kk: "#"+vv for kk, vv in v.items()} for k, v in SCHEMES.items()}, "glow": sorted(GLOWKEYS),
           "slots": ["pelvis", "torso", "head", "back", "shoulder", "upperarm", "forearm", "hand", "thigh", "shin", "foot"],
           "parts": [], "builds": {k: v for k, v in SHEETS.items()}}
    # 1) every part on its own (kit colours) for the json + contact sheet
    sheet_objs = {}
    for pid, P in PARTS.items():
        if pid == "hand_kit":
            fo, ao, plugs, segs = make_hand("kit", False, "kit.", "open"); extra = [ao] + segs
        else:
            fo, ao, plugs = make_part(pid, "kit", False, "kit."); segs = []; extra = [ao]
        bpy.context.view_layer.update()
        lo, hi = local_bbox(fo, extra)
        add_hitbox_obj(fo, lo, hi)
        yup = lambda v: [round(v.x, 3), round(v.z, 3), round(-v.y, 3)]
        e = {"id": pid, "slot": P["slot"], "name": P["name"], "about": P["about"], "sided": P["side"],
             "origin": "joint", "plugs": {k: {"at": yup(p), "dir": yup(d)} for k, (p, d) in plugs.items()},
             "frame": mesh_json(fo), "armor": mesh_json(ao), "hitbox": hitbox_of(lo, hi),
             "faces": len(fo.data.polygons) + len(ao.data.polygons) + sum(len(s.data.polygons) for s in segs)}
        if segs:
            e["fingers"] = [{"name": s["finger"], "parent": s.parent.name.split("_")[-1] if s.parent != fo else "palm",
                             "at": yup(s.location), "mesh": mesh_json(s)} for s in segs]
        kit["parts"].append(e); sheet_objs[pid] = (fo, [ao] + segs)
        print(f"  {pid:18s} {P['slot']:9s} {e['faces']:4d} faces  plugs: {', '.join(plugs)}")
    js = os.path.join(OUT, "mech_kit.json"); json.dump(kit, open(js, "w"), separators=(",", ":"))
    print("json", os.path.getsize(js)//1024, "KB,", len(PARTS), "parts")
    # 2) three sample mechs built only from the plugs
    builds = {}
    for i, (nm, sh) in enumerate(SHEETS.items()):
        root, objs = assemble(nm, sh, nm.lower(), at=(30 + i*3.2, 0, 0), pose=POSE_HERO,
                              hands={"R": "fist", "L": "open"} if nm != "Bulwark" else "fist")
        builds[nm] = (root, objs)
        faces = sum(len(o.data.polygons) for o in objs if o.type == 'MESH')
        lo, hi = world_bbox([o for o in objs if o.type == 'MESH'])
        print(f"  build {nm}: {faces} faces, {len([o for o in objs if o.get('part')])} parts, height {hi.z-lo.z:.2f}")
    # lay the contact sheet out by slot (rows) so the .blend is easy to browse
    rows = {}
    for pid, (fo, _) in sheet_objs.items(): rows.setdefault(PARTS[pid]["slot"], []).append(fo)
    for r, slot in enumerate(kit["slots"]):
        for c, fo in enumerate(rows.get(slot, [])): fo.location = (c*1.6, 0, -r*1.5)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "mech_kit.blend"))
    try:
        bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "mech_kit.glb"), export_format='GLB', export_extras=True)
    except Exception as ex: print("glb export skipped:", ex)
    if RENDER: renders(sheet_objs, rows, kit["slots"], builds)


# ---------------------------------------------------------------- preview renders (toon: flat colour + outlines)
def setup_render(w, h, bg="222b40"):
    s = bpy.context.scene; s.render.engine = 'BLENDER_WORKBENCH'
    sh = s.display.shading; sh.color_type = 'MATERIAL'; sh.light = 'STUDIO'; sh.show_specular_highlight = False
    sh.show_object_outline = True; sh.object_outline_color = (0, 0, 0)
    sh.show_cavity = True; sh.cavity_type = 'WORLD'; sh.cavity_ridge_factor = .6; sh.cavity_valley_factor = 1
    sh.show_shadows = True; sh.shadow_intensity = .3
    s.display.render_aa = '8'; s.world = s.world or bpy.data.worlds.new("W")
    sh.background_type = 'VIEWPORT'; sh.background_color = srgb(bg)
    s.render.resolution_x, s.render.resolution_y = w, h
    s.view_settings.view_transform = 'Standard'; s.render.image_settings.file_format = 'PNG'
    return s


def cam_at(target, ortho, el=12, az=-28, dist=60, persp=False):
    s = bpy.context.scene
    cam = s.camera or bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    if not s.camera: s.collection.objects.link(cam); s.camera = cam
    cam.data.type = 'PERSP' if persp else 'ORTHO'; cam.data.ortho_scale = ortho; cam.data.lens = 50; cam.data.clip_end = 500
    e, a = R(el), R(az)
    cam.location = Vector(target) + Vector((math.sin(a)*math.cos(e), -math.cos(a)*math.cos(e), math.sin(e)))*dist
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat('-Z', 'Y').to_euler()


def shot(name):
    s = bpy.context.scene; s.render.filepath = os.path.join(OUT, "png", name + ".png"); bpy.ops.render.render(write_still=True)


def only(objs, show_hb=False):
    keep = set(objs)
    for o in bpy.context.scene.objects:
        if o.type == 'MESH':
            o.hide_render = not (o in keep and (show_hb or not o.get("hitbox")))


def all_mesh(root): return [o for o in root.children_recursive if o.type == 'MESH']


def label(text, at, size=.22, key="eye", rot=(R(90), 0, 0)):
    cu = bpy.data.curves.new("lbl", 'FONT'); cu.body = text; cu.size = size; cu.align_x = 'CENTER'
    o = bpy.data.objects.new("lbl_" + text, cu); bpy.context.scene.collection.objects.link(o)
    o.location = at; o.rotation_euler = rot; o.data.materials.append(M("kit", key))
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get(); me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    t = bpy.data.objects.new("txt_" + text, me); bpy.context.scene.collection.objects.link(t)
    t.matrix_world = o.matrix_world.copy(); bpy.data.objects.remove(o)
    return t


def renders(sheet_objs, rows, slots, builds):
    bpy.ops.mesh.primitive_plane_add(size=300, location=(20, 0, 0)); g = bpy.context.object; g.name = "ground"
    g.data.materials.append(M("kit", "joint"))
    s = setup_render(1600, 1000)
    # 01: the three sample mechs, 3/4 view
    trio = [o for r, objs in builds.values() for o in all_mesh(r)]
    only(trio + [g]); cam_at((33.2, 0, 2.3), 10.5, el=10, az=-30); shot("01_three_mechs")
    # 02: front + back
    only(trio + [g]); cam_at((33.2, 0, 2.3), 10.5, el=4, az=0); shot("02_front")
    cam_at((33.2, 0, 2.3), 10.5, el=8, az=180); shot("03_back")
    # 01b/01c: round-2 roster (7 new mechs), front 3/4 and back
    new = [n for n in builds if n not in ("Vanguard", "Bulwark", "Titanheart")]
    xs = [builds[n][0].location.x for n in new]; cx = (min(xs) + max(xs))/2
    s.render.resolution_x, s.render.resolution_y = 2400, 1000
    only([o for n in new for o in all_mesh(builds[n][0])] + [g]); cam_at((cx, 0, 2.3), (max(xs)-min(xs))+3.6, el=10, az=-22); shot("01b_round2_mechs")
    cam_at((cx, 0, 2.3), (max(xs)-min(xs))+3.6, el=8, az=160); shot("01c_round2_back")
    s.render.resolution_x, s.render.resolution_y = 1600, 1000
    # 04: model-kit look: Vanguard frame only next to full armour
    vr, vobjs = builds["Vanguard"]
    frame_copy_root, fobjs = assemble("VFrame", SHEETS["Vanguard"], "vanguard", at=(26.6, 0, 0), pose=POSE_HERO, hands={"R": "fist", "L": "open"})
    armor = [o for o in all_mesh(frame_copy_root) if o.get("armor_of")]
    vis = [o for o in all_mesh(frame_copy_root) if o not in armor] + all_mesh(vr) + [g]
    s.render.resolution_x, s.render.resolution_y = 1400, 1000
    only(vis); cam_at((28.2, 0, 2.3), 7.2, el=10, az=-24); shot("04_frame_and_armor")
    # 05: hitboxes on Bulwark
    br, bobjs = builds["Bulwark"]
    hbs = []
    for o in [o for o in bobjs if o.get("part")]:
        fing = [c for c in o.children_recursive if c.get("finger")] if o.get("part") == "hand_kit" else []
        lo, hi = local_bbox(o, [c for c in o.children if c.get("armor_of")] + fing)
        hb = add_hitbox_obj(o, lo, hi, show=True); hb.display_type = 'SOLID'
        hb.data.materials.append(M("kit", "eye")); mod = hb.modifiers.new("w", 'WIREFRAME'); mod.thickness = .025
        hbs.append(hb)
    only(all_mesh(br) + hbs + [g], show_hb=True); cam_at((33.2, 0, 2.05), 6.4, el=10, az=-30); shot("05_hitboxes")
    for hb in hbs: hb.hide_render = True
    # 06/07: contact sheets of every part (kit colours), grouped by slot, with labels under each part
    def sheet(slot_list, colw=2.1):
        y = 0; vis = [g]; ncol = 0
        for slot in slot_list:
            items = rows.get(slot, []); ncol = max(ncol, len(items))
            boxes = []
            for fo in items:
                fo.rotation_euler = (0, 0, 0); fo.location = (0, 0, 0); bpy.context.view_layer.update()
                boxes.append(local_bbox(fo, [x for x in fo.children_recursive if x.type == 'MESH' and not x.get("hitbox")]))
            hmax = max(hi.z - lo.z for lo, hi in boxes)
            base = y - hmax
            for c, (fo, (lo, hi)) in enumerate(zip(items, boxes)):
                if slot == "back":   # show thrusters / wings from behind
                    fo.rotation_euler.z = math.pi; fo.location = (c*colw + (lo.x + hi.x)/2, 40 + (lo.y + hi.y)/2, base - lo.z)
                else:
                    fo.location = (c*colw - (lo.x + hi.x)/2, 40 - (lo.y + hi.y)/2, base - lo.z)
                vis += [fo] + [x for x in fo.children_recursive if x.type == 'MESH']
                vis.append(label(PARTS[fo["part"]]["name"], (c*colw, 38.5, base - .30), .17, "armor"))
            vis.append(label(slot.upper(), (-1.9, 38.5, base + hmax/2 - .1), .24, "glow"))
            y = base - .85
        x0, x1 = -2.9, (ncol - 1)*colw + 1.2
        return vis, ((x0 + x1)/2, (y + .3)/2), (x1 - x0, -y + .3)
    g.location.z = -60
    W, H = 1600, 1200
    s.render.resolution_x, s.render.resolution_y = W, H
    s.display.shading.background_color = srgb("2b3754")
    for nm, slots in (("06_parts_upper", ["head", "torso", "back", "shoulder"]), ("07_parts_lower", ["pelvis", "upperarm", "forearm", "hand"]),
                      ("07b_parts_legs", ["thigh", "shin", "foot"])):
        for o in bpy.context.scene.objects:
            if o.get("part") and o.name.startswith("kit."): o.location.y = 200
        vis, (cx, cz), (w, h) = sheet(slots)
        only(vis); cam_at((cx, 40, cz), max(w, h*W/H)*1.06, el=0, az=0, dist=30); shot(nm)
    s.display.shading.background_color = srgb("1e2638")
    # 08: hands close-up (open, grip, fist)
    hs = []
    for i, pose in enumerate(("open", "grip", "fist")):
        h, ha, hp, segs = make_hand("vanguard", False, f"H{i}.", pose); h.location = (i*.75, 60, 1); h.rotation_euler = (0, 0, R(-20))
        hs += [h, ha] + segs
    only(hs); s.render.resolution_x, s.render.resolution_y = 1400, 700; cam_at((.75, 60, .62), 2.6, el=14, az=-35); shot("08_hands")


if __name__ == "__main__":
    main()
