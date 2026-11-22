# Mech frame animation set v0.2 (Nov 22 2026). Run after mech_frame.py.
# Clips on the Standard frame: idle, walk, run, punch, blast (arm-cannon pose), sword, slide.
# Every key sets EVERY bone (unset = rest), so clips switch cleanly in the game.
# Feet are auto-grounded: at every key the pelvis is raised/lowered so the lowest foot touches the floor.
# Rotation signs (checked in Blender):
#   arms/legs: -X swings forward, +X back. Elbow bends with -X on the forearm, knee bends with +X on the shin.
#   arm/leg out to the side: .L uses -Z, .R uses +Z (helper OUT handles this).
#   chest/waist: +X leans forward, +Y twists the RIGHT shoulder forward.
import bpy, math, os
OUT = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(OUT, "mech_frames.blend"))
rig = bpy.data.objects["MechFrame_standard"]; rig.location.x = 0
pb = rig.pose.bones
for b in pb: b.rotation_mode = 'XYZ'
R = math.radians
FLOOR = 0.10

def legs(l_th, l_sh, r_th, r_sh):   # thigh/shin pairs; feet stay roughly flat
    return {"thigh.L": (l_th, 0, 0), "shin.L": (l_sh, 0, 0), "foot.L": (-(l_th + l_sh) * .8, 0, 0),
            "thigh.R": (r_th, 0, 0), "shin.R": (r_sh, 0, 0), "foot.R": (-(r_th + r_sh) * .8, 0, 0)}
def arms(l_ua, l_fa, r_ua, r_fa, l_out=0, r_out=0):
    return {"upper_arm.L": (l_ua, 0, -l_out), "forearm.L": (l_fa, 0, 0),
            "upper_arm.R": (r_ua, 0, r_out), "forearm.R": (r_fa, 0, 0)}
def body(waist=(0, 0, 0), chest=(0, 0, 0), head=(0, 0, 0)):
    return {"waist": waist, "chest": chest, "head": head}
def pose(*parts, sway=0.0):
    d = {}
    for p in parts: d.update(p)
    d["_sway"] = sway
    return d

def ground():
    bpy.context.view_layer.update()
    low = 99
    for s in (".L", ".R"):
        f = pb["foot" + s]
        low = min(low, (rig.matrix_world @ f.tail).z, (rig.matrix_world @ f.head).z - .53)
    return low

def make_clip(name, keys, cycle=False):
    act = bpy.data.actions.new(name); act.use_fake_user = True
    rig.animation_data_create(); rig.animation_data.action = act
    for frame, p in keys:
        for b in pb:
            b.rotation_euler = tuple(R(v) for v in p.get(b.name, (0, 0, 0)))
            b.location = (0, 0, 0)
        pb["pelvis"].location = (p["_sway"], 0, 0)
        pb["pelvis"].location = (p["_sway"], FLOOR - ground(), 0)   # auto-ground: lowest foot on the floor
        for b in pb:
            b.keyframe_insert("rotation_euler", frame=frame)
        pb["pelvis"].keyframe_insert("location", frame=frame)
    return act

CLIPS = {}
# ---- idle: slow heavy breathing, 2 s
CLIPS["idle"] = [(1, pose(legs(-4, 6, -4, 6), arms(6, -15, 6, -15), body(chest=(0, 0, 0)))),
                 (25, pose(legs(-6, 10, -6, 10), arms(8, -20, 8, -20), body(chest=(3, 0, 0), head=(-3, 0, 0)))),
                 (49, pose(legs(-4, 6, -4, 6), arms(6, -15, 6, -15), body()))]
# ---- walk: heavy stomp, 2 s per cycle (the one you liked)
W = [(-25, 5, 20, 15, 15, -15, 8, 0), (0, 5, 0, 45, 0, 0, 0, .12), (20, 15, -25, 5, -15, 15, -8, 0), (0, 45, 0, 5, 0, 0, 0, -.12)]
CLIPS["walk"] = [(1 + 12 * i, pose(legs(a, b, c, d), arms(e, -15, f, -15), body(waist=(0, -t * .4, 0), chest=(0, t, 0)), sway=s))
                 for i, (a, b, c, d, e, f, t, s) in enumerate(W + W[:1])]
# ---- run: leaning forward, 1 s per cycle, big arm pump
RN = [(-45, 15, 35, 30, 35, -35, 10, 0), (-5, 15, 5, 95, 0, 0, 0, .08), (35, 30, -45, 15, -35, 35, -10, 0), (5, 95, -5, 15, 0, 0, 0, -.08)]
CLIPS["run"] = [(1 + 6 * i, pose(legs(a, b, c, d), arms(e, -70, f, -70), body(waist=(10, -t * .4, 0), chest=(6, t, 0), head=(-12, 0, 0)), sway=s))
                for i, (a, b, c, d, e, f, t, s) in enumerate(RN + RN[:1])]
# ---- punch: guard -> wind up -> straight right -> back to guard, 1 s
STANCE = legs(-18, 18, 12, 14)
GUARD = arms(-45, -100, -40, -105)
CLIPS["punch"] = [(1, pose(STANCE, GUARD, body())),
                  (8, pose(STANCE, arms(-45, -100, -15, -115), body(waist=(0, -8, 0), chest=(0, -18, 0)))),
                  (12, pose(legs(-24, 22, 18, 10), arms(-35, -110, -92, -5), body(waist=(6, 12, 0), chest=(4, 28, 0)))),
                  (16, pose(legs(-24, 22, 18, 10), arms(-35, -110, -90, -8), body(waist=(6, 12, 0), chest=(4, 26, 0)))),
                  (25, pose(STANCE, GUARD, body()))]
# ---- blast: Mega Man buster pose. Body turned sideways, cannon (right) arm straight out at shoulder height,
#      left hand braces under the cannon arm, deep lunge: front leg bent, back leg straight behind. Fire, recoil, hold.
LUNGE = legs(32, 6, -40, 48)                                 # left leg back and straight, right leg forward and bent
AIM = {**arms(-75, -75, -90, 0), "upper_arm.L": (-75, 0, 32)}  # left arm reaches across to brace the cannon arm
TURN = body(waist=(6, 22, 0), chest=(6, 38, 0), head=(-4, -40, 0))   # shoulders turned, head looks down the barrel
KICK = body(waist=(2, 18, 0), chest=(-4, 32, 0), head=(-8, -36, 0))
CLIPS["blast"] = [(1, pose(legs(-4, 6, -4, 6), arms(6, -15, 6, -15), body())),
                  (8, pose(LUNGE, AIM, TURN, sway=-.15)),
                  (11, pose(LUNGE, {**arms(-75, -75, -74, -14), "upper_arm.L": (-68, 0, 30)}, KICK, sway=-.1)),   # fire: recoil kicks the arm up
                  (18, pose(LUNGE, AIM, TURN, sway=-.15)),
                  (37, pose(LUNGE, AIM, TURN, sway=-.15))]
# ---- sword: ready -> raise overhead -> diagonal slash across -> follow through -> ready, 1.3 s
READY = arms(-20, -40, -35, -70)
CLIPS["sword"] = [(1, pose(STANCE, READY, body())),
                  (10, pose(legs(-12, 14, 14, 12), arms(-20, -40, -165, -25, r_out=25), body(waist=(-4, -10, 0), chest=(-6, -22, 0)))),
                  (15, pose(legs(-32, 30, 22, 8), arms(-25, -45, -45, -10, r_out=-28), body(waist=(10, 14, 0), chest=(8, 30, 0)))),
                  (21, pose(legs(-32, 30, 22, 8), arms(-25, -45, 10, -5, r_out=-38), body(waist=(12, 18, 0), chest=(10, 36, 0)))),
                  (32, pose(STANCE, READY, body()))]
# ---- slide: drop low, front leg out, back leg tucked, lean back, hold, get up, 1 s
SLIDE = pose(legs(-75, 8, 40, 105), arms(-35, -60, 25, -20), body(waist=(-12, 0, 0), chest=(-8, 0, 0), head=(14, 0, 0)))
CLIPS["slide"] = [(1, pose(legs(-20, 25, 15, 30), arms(25, -60, -25, -60), body(waist=(8, 0, 0), chest=(5, 0, 0)))),
                  (6, SLIDE), (18, SLIDE),
                  (25, pose(legs(-4, 6, -4, 6), arms(6, -15, 6, -15), body()))]

# Nov 22: he found blast, sword and slide a little weird; dropped for now (left above for reference only).
for n in ('blast', 'sword', 'slide'): CLIPS.pop(n)
sc = bpy.context.scene; sc.render.fps = 24
old = bpy.data.actions.get("walk")
if old: bpy.data.actions.remove(old)
made = {n: make_clip(n, k) for n, k in CLIPS.items()}
rig.animation_data.action = made["idle"]
# put every clip on its own NLA track so the exporter sees all of them
for n, a in made.items():
    tr = rig.animation_data.nla_tracks.new(); tr.name = n; tr.strips.new(n, int(a.frame_range[0]), a); tr.mute = True
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "mech_frames.blend"))
bpy.ops.object.select_all(action='DESELECT'); rig.select_set(True); bpy.data.objects["MechFrame_standard_blocks"].select_set(True)
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "glb", "mech_frame_standard_anims.glb"), export_format='GLB',
                          use_selection=True, export_skins=True, export_animations=True, export_animation_mode='ACTIONS')
# checks: lowest foot per key and where the right hand ends up on the big moments
for n, keys in CLIPS.items():
    rig.animation_data.action = made[n]
    out = []
    for f, _ in keys:
        sc.frame_set(f); bpy.context.view_layer.update()
        h = rig.matrix_world @ pb["hand.R"].tail
        out.append("f%d floor %.2f handR(y %.1f z %.1f)" % (f, ground(), h.y, h.z))
    print("CLIP", n, " | ".join(out))
