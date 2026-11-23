# Basic mech frame (v0.2, Nov 22 2026) - Mythic Forge / Titan Clash master skeleton #1.
# Blocks and pivots, not a human spine: box pelvis (root), one waist joint, chest block with
# shoulder pivots on its sides, head in a socket, bar limbs, block hands and feet. 18 bones.
# Body types = PRESETS (starting points) + SLIDERS (the numbers in each preset; 1.0 = Standard).
# Mech parts are rigid, so every block is weighted 100% to one bone.
# Standard is about 10 m tall. Front faces -Y (Blender front view). Left side = +X (.L).
# Run: python with the bpy module, or  blender -b -P mech_frame.py
#   -> mech_frames.blend (all presets side by side) + glb/mech_frame_<preset>.glb
import bpy, bmesh, os
from mathutils import Vector

OUT = os.path.dirname(os.path.abspath(__file__))

# ---- SLIDERS: what each number does (1.0 = Standard)
#  height   = whole mech bigger / smaller
#  leg      = leg length          arm   = arm length
#  shoulder = shoulder width      hip   = hip width (stance)
#  chest    = chest block size    head  = head size
#  bulk     = how thick limbs, hands and feet are
STANDARD = dict(height=1.0, leg=1.0, arm=1.0, shoulder=1.0, hip=1.0, chest=1.0, head=1.0, bulk=1.0)

# ---- PRESETS (start here, then nudge the sliders). Inspired-by feel only, original designs.
PRESETS = {
    "standard": {},                                                                                       # balanced hero frame
    "heavy":    dict(leg=.85, arm=.95, shoulder=1.3, hip=1.25, chest=1.35, head=.9, bulk=1.5),            # wide tank, short legs
    "sleek":    dict(leg=1.15, arm=1.05, shoulder=.9, hip=.85, chest=.85, bulk=.8),                       # slim, tall model-kit look
    "squat":    dict(leg=.7, arm=.8, shoulder=1.2, hip=1.3, chest=1.2, head=1.15, bulk=1.4),                # low, heavy walker
    "brawler":  dict(leg=.9, arm=1.3, shoulder=1.25, chest=1.2, head=.9, bulk=1.3),                       # long gorilla arms
    "scout":    dict(leg=1.25, shoulder=.85, hip=.8, chest=.8, head=.95, bulk=.7),                         # tall, light, fast
}

def frame(p):
    """Bone list and stand-in blocks for one set of slider values."""
    ankle = .63
    knee = ankle + 2.39 * p["leg"]
    hipz = knee + 2.51 * p["leg"]
    pel_b, pel_t = hipz - .25, hipz + .70
    wst_t = pel_t + .56
    ch_t = wst_t + 2.21 * p["chest"]
    sh_z = wst_t + 1.76 * p["chest"]
    hd_b = ch_t + .09
    hh = hd_b / 8 * p["head"]; hd_t = hd_b + hh   # head follows the body: Standard = 9 heads tall (Gundam-style)
    hx, sx = 1.0 * p["hip"], 1.83 * p["shoulder"]
    a = p["arm"]
    el = (sx + .31 * a, sh_z - 2.01 * a); wr = (el[0] + .06 * a, el[1] - 1.73 * a); hn = wr[1] - .71 * a
    bones = [
        ("pelvis", None,     (0, 0, pel_b), (0, 0, pel_t - .03)),   # root: move this and the whole mech moves
        ("waist",  "pelvis", (0, 0, pel_t), (0, 0, wst_t)),         # the one joint between pelvis box and chest
        ("chest",  "waist",  (0, 0, wst_t), (0, 0, ch_t)),
        ("head",   "chest",  (0, 0, hd_b), (0, 0, hd_t)),           # sits in a socket, almost no neck
    ]
    left = [
        ("shoulder",  "chest",     (.9 * p["shoulder"], 0, sh_z), (sx, 0, sh_z)),   # mount for shoulder armor
        ("upper_arm", "shoulder",  (sx, 0, sh_z), (el[0], 0, el[1])),               # head = shoulder pivot
        ("forearm",   "upper_arm", (el[0], 0, el[1]), (wr[0], 0, wr[1])),           # elbow
        ("hand",      "forearm",   (wr[0], 0, wr[1]), (wr[0], 0, hn)),              # wrist
        ("thigh",     "pelvis",    (hx, 0, hipz), (hx + .13, 0, knee)),             # hip pivot on the pelvis box side
        ("shin",      "thigh",     (hx + .13, 0, knee), (hx + .13, 0, ankle)),      # knee
        ("foot",      "shin",      (hx + .13, 0, ankle), (hx + .13, -.9, .10)),     # ankle, toes forward
    ]
    for side, s in ((".L", 1), (".R", -1)):
        for n, par, h, t in left:
            bones.append((n + side, par if par in ("chest", "pelvis") else par + side, (s * h[0], h[1], h[2]), (s * t[0], t[1], t[2])))
    b = p["bulk"]
    blocks = [
        ("pelvis", (0, 0, (pel_b + pel_t) / 2), (1.6 * p["hip"], 1.0, pel_t - pel_b), None),
        ("waist",  (0, 0, (pel_t + wst_t) / 2), (.5 * b, .5 * b, wst_t - pel_t), None),
        ("chest",  (0, 0, (wst_t + ch_t) / 2), (2 * sx - .56, 1.6 * p["chest"], ch_t - wst_t), None),
        ("head",   (0, -.1, (hd_b + hd_t) / 2), (1.05 * hh, 1.0 * hh, hd_t - hd_b), None),
    ]
    thick = {"shoulder": .55, "upper_arm": .45, "forearm": .5, "hand": .7, "thigh": .6, "shin": .55}
    for side, s in ((".L", 1), (".R", -1)):
        for n, t in thick.items():
            h0, t0 = next((Vector(r[2]), Vector(r[3])) for r in bones if r[0] == n + side)
            blocks.append((n + side, tuple((h0 + t0) / 2), (t * b, t * b, (t0 - h0).length), (h0, t0)))
        blocks.append(("foot" + side, (s * (hx + .13), -.35, .28), (1.1 * b, 1.7 * b ** .5, .56), None))
    k = p["height"]
    sc = lambda v: tuple(x * k for x in v)
    return ([(n, par, sc(h), sc(t)) for n, par, h, t in bones],
            [(n, sc(c), sc(sz), None if ht is None else (ht[0] * k, ht[1] * k)) for n, c, sz, ht in blocks])

def build(name, p, x_offset=0.0):
    bones, blocks = frame(p)
    arm_data = bpy.data.armatures.new(name); arm_data.display_type = 'STICK'
    rig = bpy.data.objects.new(name, arm_data); bpy.context.collection.objects.link(rig)
    for k2, v in p.items(): rig[k2] = v          # sliders stored on the rig (Object > Custom Properties)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode='EDIT')
    for n, par, h, t in bones:
        eb = arm_data.edit_bones.new(n); eb.head, eb.tail = Vector(h), Vector(t); eb.roll = 0
        if par:
            eb.parent = arm_data.edit_bones[par]
            eb.use_connect = (Vector(h) - arm_data.edit_bones[par].tail).length < 1e-3
    bpy.ops.object.mode_set(mode='OBJECT')
    rig.show_in_front = True
    parts = []
    for bone, c, size, ht in blocks:
        me = bpy.data.meshes.new(bone); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts: v.co.x *= size[0]; v.co.y *= size[1]; v.co.z *= size[2]
        if ht:  # limb bar lies along its bone
            q = Vector((0, 0, 1)).rotation_difference((ht[1] - ht[0]).normalized())
            for v in bm.verts: v.co = q @ v.co
        for v in bm.verts: v.co += Vector(c)
        bm.to_mesh(me); bm.free()
        ob = bpy.data.objects.new(bone, me); bpy.context.collection.objects.link(ob)
        ob.vertex_groups.new(name=bone).add(list(range(len(me.vertices))), 1.0, 'REPLACE')
        parts.append(ob)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in parts: ob.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]; bpy.ops.object.join()
    body = bpy.context.view_layer.objects.active; body.name = name + "_blocks"
    body.data.materials.append(MAT); body.parent = rig
    body.modifiers.new("Armature", 'ARMATURE').object = rig
    rig.location.x = x_offset
    return rig, body

bpy.ops.wm.read_factory_settings(use_empty=True)
MAT = bpy.data.materials.new("frame_gray"); MAT.diffuse_color = (.55, .55, .52, 1)
os.makedirs(os.path.join(OUT, "glb"), exist_ok=True)
made = []
for i, (pname, over) in enumerate(PRESETS.items()):
    p = dict(STANDARD, **over)
    rig, body = build("MechFrame_" + pname, p, x_offset=i * 7.0)
    made.append((pname, rig, body))
for pname, rig, body in made:   # one game-ready file per preset (placed at the origin)
    x = rig.location.x; rig.location.x = 0
    bpy.ops.object.select_all(action='DESELECT'); rig.select_set(True); body.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "glb", f"mech_frame_{pname}.glb"), export_format='GLB',
                              use_selection=True, export_skins=True, export_animations=False)
    rig.location.x = x
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "mech_frames.blend"))
print("PRESETS", [m[0] for m in made])
