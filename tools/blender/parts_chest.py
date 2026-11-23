# Mythic Forge body parts: CHESTS (Nov 22 2026). Run with the bpy module: python3 parts_chest.py
# Reuses his own Mech Kit (T042, mech_kit_R2.py, Nov 13): same builder (inner frame + armor, bevelled edges,
# no perfectly cut edges) and the same original chest designs. Each chest is exported on its own, standing on
# its bottom, centred, so Mythic Forge can stretch it to fit the chest bone of any body shape.
# The kit's lower waist block is skipped: the new frame has its own waist bone.
import bpy, bmesh, math, os, sys, json
from mathutils import Vector, Matrix, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "parts"); os.makedirs(OUT, exist_ok=True)
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



PARTS = {}
def part(pid, slot, name, about, plugs, side=False):
    def deco(fn):
        PARTS[pid] = dict(id=pid, slot=slot, name=name, about=about, fn=fn)
        return fn
    return deco
UP, DOWN, FWD, BACK, OUT_ = (0, 0, 1), (0, 0, -1), (0, -1, 0), (0, 1, 0), (1, 0, 0)
def torso_plugs(*a): return {}

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

@part("torso_sleek", "torso", "Sleek chest", "Tapered real-robot chest with intake vents and a collar.", torso_plugs(.55, .86, 1.08, .32))
def _(F, A):
    F.box("frame", (0, 0, .18), (.40, .32, .34), (1.15, 1)); F.box("frame", (0, .02, .66), (.62, .50, .62), (1.2, 1))
    for i in range(3): F.box("joint", (0, -.17, .08+i*.1), (.30-i*.02, .04, .06), (1, 1), .01)
    A.box("armor", (0, -.02, .70), (.78, .60, .58), (1.45, 1.05), .05, front=(1, 1))
    A.box("armor2", (0, -.33, .74), (.46, .06, .34), (1.35, 1), .02)
    for s in (-1, 1):
        A.box("joint", (s*.20, -.36, .86), (.16, .03, .10), (1, 1), .0); A.box("glow", (s*.20, -.375, .86), (.12, .01, .04), (1, 1), 0)
    A.box("armor2", (0, 0, 1.02), (.46, .40, .10), (.8, .8), .02)

@part("torso_emblem", "torso", "Emblem chest", "Super-robot chest: big V plate, glowing emblem, flared pecs.", torso_plugs(.62, .88, 1.10, .34))
def _(F, A):
    F.box("frame", (0, 0, .18), (.42, .34, .34), (1.15, 1)); F.box("frame", (0, .02, .66), (.66, .52, .62), (1.25, 1))
    A.box("armor", (0, -.02, .70), (.86, .62, .58), (1.5, 1.05), .05)
    for s in (-1, 1):
        A.box("armor2", (s*.24, -.33, .80), (.40, .08, .30), (1.2, 1), .02, rot=Matrix.Rotation(R(s*-14), 3, 'Y'))
    A.fin("accent", (0, -.38, .64), [(-.36, .26), (0, -.14), (.36, .26), (.26, .26), (0, .0), (-.26, .26)], .05)
    A.ball("glow", (0, -.37, .70), .07, 8)
    A.box("armor2", (0, 0, 1.04), (.48, .40, .10), (.8, .8), .02)

@part("torso_grunt", "torso", "Grunt hatch chest", "Boxy grunt chest with a round cockpit hatch and grab rails.", torso_plugs(.60, .84, 1.06, .36))
def _(F, A):
    F.box("frame", (0, 0, .18), (.44, .34, .34), (1.1, 1)); F.box("frame", (0, .02, .66), (.66, .52, .62), (1.1, 1))
    A.box("armor", (0, -.02, .68), (.86, .64, .60), (1.05, 1), .04)
    A.cyl("armor2", (0, -.34, .70), .17, .06, 'Y', 10); A.cyl("joint", (0, -.37, .70), .05, .02, 'Y', 6)
    for s in (-1, 1): A.box("accent", (s*.34, -.36, .70), (.03, .03, .36), (1, 1), 0)
    for i in range(2): A.box("accent2", (0, -.335, .44+i*.06), (.5, .01, .03), (1, 1), 0)

class NoWaist(PB):     # skip the kit's lower waist frame block (the new frame has a waist bone)
    def box(self, key, at, size, *a, **k):
        if key == "frame" and at[2] < .3: return
        return super().box(key, at, size, *a, **k)

ORDER = ["torso_cockpit", "torso_heavy", "torso_sleek", "torso_emblem", "torso_grunt"]
info = []
for pid in ORDER:
    for ob in list(bpy.data.objects): bpy.data.objects.remove(ob)
    F, A = NoWaist(), PB(); PARTS[pid]["fn"](F, A)
    objs = [F.to_obj(pid + "_frame", "kit"), A.to_obj(pid + "_armor", "kit")]
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active; ob.name = pid
    xs = [v.co.x for v in ob.data.vertices]; ys = [v.co.y for v in ob.data.vertices]; zs = [v.co.z for v in ob.data.vertices]
    off = Vector(((max(xs)+min(xs))/2, (max(ys)+min(ys))/2, min(zs)))
    for v in ob.data.vertices: v.co -= off                           # stand on its bottom, centred
    size = (max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs))
    path = os.path.join(OUT, pid + ".glb")
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True)
    info.append(dict(id=pid, name=PARTS[pid]["name"], about=PARTS[pid]["about"], size=[round(s, 3) for s in size], faces=len(ob.data.polygons)))
json.dump(info, open(os.path.join(OUT, "chests.json"), "w"), indent=1)
print(json.dumps(info, indent=1))
