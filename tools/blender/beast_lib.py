"""Shared beast builder for the 2.0 KAIJU kit (T043) and DRAGON kit (T045). By MajorasPride.
Reuses the mech kit standard (mech_kit_R2.py): PB mesh builder, toon materials, plugs, frame + armour, hitboxes,
mesh_json packing, toon renders. Adds a SPINE body plan: hips -> chest -> neck chain -> head (+ jaw that opens),
hips -> tail chain, limbs aimed in world space so one kit makes upright, horizontal, four-legged and sprawled beasts.
Spine frame: z up, FRONT = -Y. Hips origin = hip centre. Every part's origin sits on the joint it hangs from."""
import bpy, bmesh, math, os, sys, json
from mathutils import Vector, Matrix, Euler
import mech_kit_R2 as mk

PB, M, SCHEMES, R = mk.PB, mk.M, mk.SCHEMES, mk.R
RX, RY, RZ = mk.RX, mk.RY, mk.RZ
UP, DOWN, FWD, BACK, OUT_ = mk.UP, mk.DOWN, mk.FWD, mk.BACK, mk.OUT_
mk.GLOWKEYS.update({"crystal", "glow", "eye"})

PARTS = {}
def part(pid, slot, name, about, plugs, side=False, kit="kaiju"):
    def deco(fn):
        PARTS[pid] = dict(id=pid, slot=slot, name=name, about=about, plugs=plugs, side=side, fn=fn, kit=kit)
        return fn
    return deco


def rot_to(d):
    return Vector((0, 0, 1)).rotation_difference(Vector(d).normalized()).to_matrix()


# ---------------------------------------------------------------- shape helpers
def spike(pb, key, at, r, L, d=(0, 0, 1), seg=5):
    """Cone with its base on `at`, pointing along d."""
    dv = Vector(d).normalized(); c = Vector(at) + dv * L / 2
    pb.cyl(key, tuple(c), r, L, 'Z', seg, r2=r * .04, rot=rot_to(dv))


def limb(pb, key, L, r_top, r_bot, at=(0, 0, 0), seg=8):
    """Tapered cylinder hanging down from `at` (a thigh, shin, arm)."""
    pb.cyl(key, (at[0], at[1], at[2] - L / 2), r_bot, L, 'Z', seg, r2=r_top)


def tuft(pb, key, at, d, n=5, L=.22, r=.05, spread=.12):
    """Fur tuft: a fan of thin spikes."""
    dv = Vector(d).normalized(); side = dv.cross(Vector((0, 0, 1)) if abs(dv.z) < .9 else Vector((1, 0, 0))).normalized()
    for i in range(n):
        o = (i - (n - 1) / 2) * spread
        spike(pb, key, tuple(Vector(at) + side * o * .6), r, L * (1 - abs(o) * .9), tuple(dv + side * o), 4)


def feather(pb, key, at, L=.4, w=.09, rot=None, thick=.02):
    """One flat feather (leaf outline) pointing -Z from `at` in the X-Z plane."""
    pts = [(0, 0), (w * .6, -L * .2), (w * .5, -L * .75), (0, -L), (-w * .5, -L * .75), (-w * .6, -L * .2)]
    pb.fin(key, at, pts, thick, rot)


def plate(pb, key, at, h=.3, w=.3, rot=None, thick=.04, crystal=False):
    """Dorsal plate in the Y-Z plane (thin in X): leaf / maple-style outline, base on `at`."""
    if crystal: pts = [(-w * .4, 0), (-w * .2, h * .7), (0, h), (w * .2, h * .7), (w * .4, 0)]
    else: pts = [(-w * .5, 0), (-w * .55, h * .35), (-w * .25, h * .45), (-w * .3, h * .75), (0, h), (w * .3, h * .75), (w * .25, h * .45), (w * .55, h * .35), (w * .5, 0)]
    m = RZ(90) if rot is None else rot @ RZ(90)
    pb.fin(key, at, pts, thick, m)


def teeth(pb, at, L, n, x, down=True, size=.035):
    """Row of teeth on both sides along -Y from `at` (y start), length L."""
    for s in (-1, 1):
        for i in range(n):
            y = at[1] - (i + .5) * L / n
            spike(pb, "tooth", (s * x, y, at[2]), size * .7, size * 1.6, (0, 0, -1 if down else 1), 4)


# ---------------------------------------------------------------- build parts as objects
def make_part(pid, scheme, mirror=False, tag="", scale=1.0):
    P = PARTS[pid]; F, A = PB(), PB()
    P["fn"](F, A)
    nm = f"{tag}{pid}{'_L' if mirror else ('_R' if P['side'] else '')}"
    fo = F.to_obj(nm, scheme, mirror); ao = A.to_obj(nm + "_armor", scheme, mirror)
    ao.parent = fo; fo["part"] = pid; fo["kit"] = P["kit"]; ao["armor_of"] = nm
    plugs = {}
    for k, (pos, d) in P["plugs"].items():
        p = Vector(pos); dd = Vector(d)
        if mirror: p.x, dd.x = -p.x, -dd.x
        plugs[k] = (p, dd)
    if scale != 1.0: fo.scale = (scale, scale, scale)
    return fo, ao, plugs


def _upd(): bpy.context.view_layer.update()


def aim(fo, eul, mirror=False):
    """Give `fo` a WORLD rotation (degrees, XYZ), whatever its parent is doing."""
    e = Euler((R(eul[0]), R(eul[1]) * (-1 if mirror else 1), R(eul[2]) * (-1 if mirror else 1)))
    _upd(); Rp = fo.parent.matrix_world.to_3x3().normalized() if fo.parent else Matrix.Identity(3)
    fo.rotation_euler = (Rp.inverted() @ e.to_matrix()).to_euler()


def assemble(name, sheet, scheme, at=(0, 0, 0), pose=None):
    """sheet: hips, chest, neck=(id, n), head, jaw, back, back_extra{plug: id}, horn, arm_up, arm_lo, hand,
    thigh, shin, foot, tail=(id, n, decay), wings (back-mounted), legs4 (True = 4 legs leveled to the ground).
    pose: pitch (spine up, deg), chest, neck (per seg), head (world pitch), jaw (open deg), tail (per seg pitch),
    tail_yaw, arm=(shoulder, elbow, wrist) world eulers, leg=(hip, knee, ankle) world eulers, wing=(base, tip)."""
    pose = pose or {}; objs = []; feet = {"front": [], "back": []}
    root = bpy.data.objects.new(name, None); bpy.context.scene.collection.objects.link(root); root.location = at

    def attach(pid, parent, plug, mirror=False, local=None, world=None, scale=1.0):
        fo, ao, plugs = make_part(pid, scheme, mirror, name + ".", scale)
        fo.parent = parent; fo.location = plug
        if local is not None: fo.rotation_euler = Euler([R(v) for v in local])
        if world is not None: aim(fo, world, mirror)
        objs.extend([fo, ao]); return fo, plugs

    def plug_on(pid, parent, pp, plugname, mirror=False):
        """Mount a part (crystal, horn, plate) so its +Z follows the plug direction."""
        pos, d = pp[plugname]
        fo, plugs = attach(pid, parent, pos, mirror)
        fo.rotation_euler = rot_to(d).to_euler(); return fo, plugs

    hips, hp = attach(sheet["hips"], root, (0, 0, 3.0), local=(-pose.get("pitch", 0), 0, 0))
    chest, cp = attach(sheet["chest"], hips, hp["waist"][0], local=(-pose.get("chest", 0), 0, 0))
    par, pp = chest, cp; nk = sheet.get("neck")
    plug = "neck"
    if nk:
        nid, n = nk
        for i in range(n):
            nw = pose.get("neck_wave", 0) * math.sin(i * math.pi / 2.2)
            par, pp = attach(nid, par, pp[plug][0], local=(-pose.get("neck", 0) - nw, 0, 0)); plug = "next"
    head, hdp = attach(sheet["head"], par, pp[plug][0], world=(-pose.get("head", 0), 0, 0))
    if sheet.get("jaw"): attach(sheet["jaw"], head, hdp["jaw"][0], local=(pose.get("jaw", 0), 0, 0))
    if sheet.get("horn") and "horn" in hdp: plug_on(sheet["horn"], head, hdp, "horn")
    if sheet.get("crest") and "crest" in hdp: plug_on(sheet["crest"], head, hdp, "crest")
    if sheet.get("back"):
        bk, bp = attach(sheet["back"], chest, cp["back"][0])
        for k, pid in (sheet.get("back_extra") or {}).items():
            if k in bp: plug_on(pid, bk, bp, k)
    if sheet.get("hips_back") and "back" in hp: attach(sheet["hips_back"], hips, hp["back"][0])
    if sheet.get("wings"):
        wa = pose.get("wing", ((0, -70, 10), (0, -20, 0)))
        for side, m in (("R", False), ("L", True)):
            w1, w1p = attach(sheet["wings"][0], chest, cp["wing_" + side][0], m, world=wa[0])
            for k, pid in (sheet.get("wing_extra1") or {}).items(): plug_on(pid, w1, w1p, k, m)
            if len(sheet["wings"]) > 1:
                w2, w2p = attach(sheet["wings"][1], w1, w1p["tip"][0], m, world=wa[1])
                for k, pid in (sheet.get("wing_extra2") or {}).items(): plug_on(pid, w2, w2p, k, m)
    if sheet.get("tail"):
        tid, n, decay = sheet["tail"]; par, pp, plug = hips, hp, "tail"
        for i in range(n):
            sc = 1.0 if i == 0 else decay
            wave = pose.get("tail_wave", 0) * math.sin(i * math.pi / 2.2)
            par, pp = attach(tid, par, pp[plug][0], local=(-pose.get("tail", 0) - wave, 0, pose.get("tail_yaw", 0)), scale=sc); plug = "next"
        if sheet.get("tail_tip"): attach(sheet["tail_tip"], par, pp["next"][0])
    arm = pose.get("arm", ((-20, 0, 0), (-50, 0, 0), (-20, 0, 0))); leg = pose.get("leg", ((-10, 0, 0), (15, 0, 0), (0, 0, 0)))
    for side, m in (("R", False), ("L", True)):
        if sheet.get("arm_up"):
            ua, up = attach(sheet["arm_up"], chest, cp["shoulder_" + side][0], m, world=arm[0])
            la, lp = attach(sheet["arm_lo"], ua, up["elbow"][0], m, world=arm[1])
            hd, _ = attach(sheet["hand"], la, lp["wrist"][0], m, world=arm[2]); feet["front"].append(hd)
        if not sheet.get("thigh"): continue
        th, tp = attach(sheet["thigh"], hips, hp["hip_" + side][0], m, world=leg[0])
        sn, sp = attach(sheet["shin"], th, tp["knee"][0], m, world=leg[1])
        ft, _ = attach(sheet["foot"], sn, sp["ankle"][0], m, world=leg[2]); feet["back"].append(ft)
    _upd()
    meshes = lambda os_: [c for o in os_ for c in [o] + list(o.children_recursive) if c.type == 'MESH' and not c.get("hitbox")]
    if sheet.get("legs4"):   # tip the whole body so front and back feet both touch the ground
        for _i in range(3):
            fl = min((o.matrix_world @ Vector(c)).z for o in meshes(feet["front"]) for c in o.bound_box)
            bl = min((o.matrix_world @ Vector(c)).z for o in meshes(feet["back"]) for c in o.bound_box)
            fy = sum(o.matrix_world.translation.y for o in feet["front"]) / 2; by = sum(o.matrix_world.translation.y for o in feet["back"]) / 2
            root.rotation_euler.x += math.atan2(fl - bl, abs(by - fy)); _upd()
    low = min((o.matrix_world @ Vector(c)).z for o in objs if o.type == 'MESH' for c in o.bound_box)
    root.location.z -= low; _upd()
    return root, objs


# ---------------------------------------------------------------- export + renders
def local_bbox(o, extra=()): return mk.local_bbox(o, extra)


def export_kit(kitname, ticket, parts_ids, sheets, out, extra_meta=None):
    os.makedirs(os.path.join(out, "png"), exist_ok=True)
    yup = lambda v: [round(v.x, 3), round(v.z, 3), round(-v.y, 3)]
    used_schemes = {k: {kk: "#" + vv for kk, vv in SCHEMES[k].items()} for k in ["kit"] + [s for s in sheets_schemes(sheets)]}
    kit = {"kit": kitname, "version": 1, "made": "Nov 13, 2026", "by": "MajorasPride", "ticket": ticket,
           "units": "kit units: same scale as the mech kit (mech ~4.6 tall); x4 = Titan Clash game units",
           "axes": "three.js y-up (x, z, -y from Blender); front = -z in three.js",
           "body_plan": "hips (root) -> chest -> neck chain -> head + jaw; hips -> tail chain (each segment scaled by decay); "
                        "limbs aimed in world space; see 'builds' for sheets and 'poses' for joint angles",
           "schemes": used_schemes, "glow": sorted(mk.GLOWKEYS), "parts": [],
           "builds": {k: {kk: vv for kk, vv in v["sheet"].items()} for k, v in sheets.items()},
           "poses": {k: v.get("pose", {}) for k, v in sheets.items()}}
    if extra_meta: kit.update(extra_meta)
    objs = {}
    for pid in parts_ids:
        P = PARTS[pid]
        fo, ao, plugs = make_part(pid, "kit", False, "kit."); _upd()
        lo, hi = local_bbox(fo, [ao]); mk.add_hitbox_obj(fo, lo, hi)
        e = {"id": pid, "slot": P["slot"], "name": P["name"], "about": P["about"], "sided": P["side"], "from_kit": P["kit"],
             "origin": "joint", "plugs": {k: {"at": yup(p), "dir": yup(d)} for k, (p, d) in plugs.items()},
             "frame": mk.mesh_json(fo), "armor": mk.mesh_json(ao), "hitbox": mk.hitbox_of(lo, hi),
             "faces": len(fo.data.polygons) + len(ao.data.polygons)}
        kit["parts"].append(e); objs[pid] = fo
    js = os.path.join(out, f"{kitname}_kit.json"); json.dump(kit, open(js, "w"), separators=(",", ":"))
    print("json", os.path.getsize(js) // 1024, "KB,", len(parts_ids), "parts")
    return kit, objs


def sheets_schemes(sheets): return sorted({v["scheme"] for v in sheets.values()})


def contact_sheet(objs, slot_rows, fname, colw=2.0, W=2400, H=1200, z0=-200, turn=None):
    """Every part in kit colours, one row per slot, with a name label under each."""
    s = bpy.context.scene; vis = []; y = z0; ncol = 0
    for slot in slot_rows:
        items = [fo for fo in objs.values() if PARTS[fo["part"]]["slot"] == slot]
        if not items: continue
        ncol = max(ncol, len(items)); boxes = []
        for fo in items:
            fo.rotation_euler = (0, 0, 0); fo.location = (0, 0, 0); _upd()
            if PARTS[fo["part"]]["slot"] in ("tail", "neck", "hips", "chest", "head", "jaw", "back"): fo.rotation_euler.z = R(90); _upd()
            if turn and PARTS[fo["part"]]["slot"] in turn: fo.rotation_euler = [R(v) for v in turn[PARTS[fo["part"]]["slot"]]]; _upd()
            boxes.append(mk.world_bbox([x for x in [fo] + list(fo.children_recursive) if x.type == 'MESH' and not x.get("hitbox")]))
        hmax = max(hi.z - lo.z for lo, hi in boxes); base = y - hmax
        for c, (fo, (lo, hi)) in enumerate(zip(items, boxes)):
            fo.location = (c * colw - (lo.x + hi.x) / 2, 40 - (lo.y + hi.y) / 2, base - lo.z)
            vis += [x for x in [fo] + list(fo.children_recursive) if x.type == 'MESH' and not x.get("hitbox")]
            vis.append(mk.label(PARTS[fo["part"]]["name"], (c * colw, 38, base - .28), .15, "armor"))
        vis.append(mk.label(slot.upper(), (-1.9, 38, base + hmax / 2 - .1), .22, "glow"))
        y = base - .8
    x0, x1 = -2.9, (ncol - 1) * colw + 1.1
    w, h = x1 - x0, (z0 - y) + .3
    H = int(min(max(W * h / w * 1.08, 500), 2400))
    mk.only(vis); s.render.resolution_x, s.render.resolution_y = W, H
    mk.cam_at(((x0 + x1) / 2, 40, (z0 + y) / 2 + .15), max(w, h * W / H) * 1.05, el=0, az=0, dist=30); mk.shot(fname)
    for fo in objs.values(): fo.location.y = 400   # park


def all_mesh(root): return [o for o in root.children_recursive if o.type == 'MESH' and not o.get("hitbox")]


def ground():
    bpy.ops.mesh.primitive_plane_add(size=600, location=(0, 0, 0)); g = bpy.context.object; g.name = "ground"
    B_ = SCHEMES.setdefault("stage", dict(floor="56607a")); g.data.materials.append(M("stage", "floor")); return g


def hitbox_overlay(objs):
    hbs = []
    for o in [o for o in objs if o.get("part")]:
        lo, hi = local_bbox(o, [c for c in o.children if c.get("armor_of")])
        hb = mk.add_hitbox_obj(o, lo, hi, show=True); hb.display_type = 'SOLID'
        hb.data.materials.append(M("kit", "eye")); mod = hb.modifiers.new("w", 'WIREFRAME'); mod.thickness = .025
        hbs.append(hb)
    return hbs
