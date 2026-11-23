"""Mythic Forge 2.0 / Titan Clash 2.0 — WEAPONS KIT (T044) for mechs and kaiju, made in Blender from code.
Same standard: FRAME (hilt, core, barrel) + ARMOUR (blade, casing, plates), origin on the plug it fits, HITBOX on each.
Weapon space: origin = where it plugs in; +Z = the way it points (blade, barrel, shield face, spike).
  hand weapons  -> mech 'hand_kit' plug 'grip'  (or kaiju 'claw_hand' plug 'grip'); two-handers also have 'hand2'
  shields       -> mech forearm plug 'mount' (+Z faces out)
  pods/cannons  -> mech shoulder plug 'pod' (missile pods, cannon) or a shin (leg pods, origin = shin side)
  rocket fist   -> mech forearm plug 'wrist' (replaces the hand, fires off along +Z)
  kaiju         -> tail segment top, crystal mount plugs, head 'horn' plug, claw hand 'grip'
Extra plugs: 'tip' (melee trail / hit point), 'muzzle' (shots spawn here), 'hand2' (second hand).
Weapons use the mech colour keys (armor, armor2, frame, joint, accent, accent2, glow) so they recolour with any mech;
kaiju weapons use the beast keys (plate, claw, crystal, horn). Original designs only. By MajorasPride.
Run: python3 weapons_kit.py [render]  -> out_weapons/weapons_kit.json, .blend, (.glb), png/"""
import bpy, math, os, sys
from mathutils import Vector, Matrix, Euler
import mech_kit_R2 as mk
import beast_lib as B
import kaiju_kit as KK
from beast_lib import part, spike, limb, plate, RX, RY, RZ, R, UP, DOWN, FWD, BACK, OUT_

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out_weapons")
RENDER = "render" in sys.argv
for k, v in B.SCHEMES.items():
    v.setdefault("blade", "dfe4ec"); v.setdefault("grip", "2a2622")
    for kk, dv in (("armor", "c9ccd2"), ("armor2", "7a808c"), ("joint", "252a33"), ("accent", "d4a33a"), ("accent2", "d8343a")): v.setdefault(kk, dv)

Z = (0, 0, 1)
def W(pid, slot, name, about, plugs=None, kit="weapons"):
    p = {"tip": ((0, 0, 1), UP)}; p.update(plugs or {})
    return part(pid, slot, name, about, p, kit=kit)

def hilt(F, A, L=.36, r=.05, guard=.34, pommel=True, key="accent"):
    F.cyl("grip", (0, 0, 0), r, L, 'Z', 8)
    if pommel: A.ball(key, (0, 0, -L / 2 - .03), r * 1.5, 8)
    if guard: A.box(key, (0, 0, L / 2 + .03), (guard, .1, .06), (1, 1), .015)

def blade(A, key, z0, L, w, t=.04, tipL=.3, curve=0):
    """Flat blade from z0 up, in the X-Z plane, tip on top (curve = sideways bend at the tip)."""
    pts = [(-w / 2, 0), (-w / 2 + curve * .3, L - tipL), (curve, L), (w / 2 + curve * .3, L - tipL * 1.3), (w / 2, 0)]
    A.fin(key, (0, 0, z0), pts, t)

# ================================================================ MELEE (grip = origin, blade up +Z)
@W("energy_sword", "melee", "Energy sword", "Beam saber: metal hilt and a glowing blade.", {"tip": ((0, 0, 2.2), UP)})
def _(F, A):
    hilt(F, A, .42, .055, 0); A.cyl("armor2", (0, 0, .2), .07, .12, 'Z', 8); A.cyl("accent", (0, 0, .28), .08, .04, 'Z', 8)
    A.cyl("glow", (0, 0, 1.25), .06, 1.9, 'Z', 8, r2=.035)

@W("katana", "melee", "Katana", "Long single-edge blade with a slight curve and a round guard.", {"tip": ((.08, 0, 2.1), UP)})
def _(F, A):
    hilt(F, A, .5, .045, 0); A.cyl("accent", (0, 0, .28), .12, .03, 'Z', 12)
    blade(A, "blade", .3, 1.8, .12, .03, .3, curve=.1); A.box("armor2", (0, 0, .34), (.13, .045, .08), (1, 1), .01)

@W("great_sword", "melee", "Great sword", "Huge two-hand blade with a wide cross guard.", {"tip": ((0, 0, 2.6), UP), "hand2": ((0, 0, -.32), UP)})
def _(F, A):
    hilt(F, A, .8, .055, .7); F.box("frame", (0, 0, 1.2), (.08, .05, 1.8), (1, 1), 0)
    blade(A, "blade", .4, 2.2, .42, .06, .45); A.box("accent2", (0, 0, .7), (.12, .07, .5), (1, 1), .01)

@W("axe", "melee", "Battle axe", "Long haft with a big crescent head and a back spike.", {"tip": ((0, 0, 1.7), UP), "hand2": ((0, 0, -.4), UP)})
def _(F, A):
    F.cyl("grip", (0, 0, .5), .05, 2.0, 'Z', 8); A.cyl("accent", (0, 0, -.5), .07, .1, 'Z', 8)
    A.fin("blade", (0, 0, 1.25), [(0, -.25), (.32, -.42), (.6, -.12), (.62, .2), (.34, .5), (0, .3)], .06)
    spike(A, "armor2", (0, 0, 1.3), .06, .3, (-1, 0, .1), 4); spike(A, "armor2", (0, 0, 1.55), .05, .2, (0, 0, 1), 4)

@W("war_hammer", "melee", "War hammer", "Heavy block-head hammer with a spike.", {"tip": ((0, 0, 1.5), UP), "hand2": ((0, 0, -.4), UP)})
def _(F, A):
    F.cyl("grip", (0, 0, .4), .055, 1.8, 'Z', 8)
    A.box("armor", (0, 0, 1.35), (.7, .4, .4), (1, 1), .06); A.box("accent2", (.36, 0, 1.35), (.06, .44, .44), (1, 1), .02)
    A.box("accent2", (-.36, 0, 1.35), (.06, .44, .44), (1, 1), .02); spike(A, "blade", (0, 0, 1.55), .08, .3, Z, 4)

@W("lance", "melee", "Lance", "Knight lance: long cone with a hand guard.", {"tip": ((0, 0, 3.0), UP)})
def _(F, A):
    F.cyl("grip", (0, 0, 0), .05, .5, 'Z', 8); A.cyl("armor2", (0, 0, .35), .3, .25, 'Z', 12, r2=.08)
    A.cyl("armor", (0, 0, 1.65), .17, 2.7, 'Z', 8, r2=.01); A.cyl("accent", (0, 0, .5), .18, .06, 'Z', 8)

@W("drill_lance", "melee", "Drill lance", "Spinning drill cone with spiral ridges (super-robot style).", {"tip": ((0, 0, 2.2), UP)})
def _(F, A):
    F.cyl("grip", (0, 0, 0), .05, .5, 'Z', 8); A.cyl("armor2", (0, 0, .32), .26, .16, 'Z', 10)
    A.cyl("accent", (0, 0, 1.25), .3, 1.8, 'Z', 8, r2=.01)
    for i in range(10):
        t = i / 10; zr = .45 + t * 1.5; rr = .3 * (1 - t * .95)
        a = i * 70; A.box("armor", (math.cos(R(a)) * rr, math.sin(R(a)) * rr, zr), (.08, .05, .16), (1, 1), .01, rot=RZ(a) @ RX(30))

@W("chain_whip", "melee", "Chain whip", "Handle and a chain of 10 linked blades (each link can swing).", {"tip": ((0, 0, 2.4), UP)})
def _(F, A):
    hilt(F, A, .4, .05, .2)
    for i in range(10): A.box("blade" if i % 2 else "armor2", (0, 0, .4 + i * .2), (.1, .06, .16), (.5, 1), .01, rot=RZ(i * 90))
    spike(A, "blade", (0, 0, 2.38), .08, .2, Z, 4)

@W("scythe", "melee", "Scythe", "Long haft with a big curved reaper blade.", {"tip": ((.9, 0, 1.6), UP), "hand2": ((0, 0, -.5), UP)})
def _(F, A):
    F.cyl("grip", (0, 0, .5), .05, 2.2, 'Z', 8); A.box("accent", (0, 0, 1.6), (.14, .1, .14), (1, 1), .02)
    A.fin("blade", (0, 0, 1.6), [(0, -.05), (.4, .05), (.8, .0), (1.1, -.25), (.75, .15), (.35, .2), (0, .1)], .05)

@W("beam_pistol", "gun", "Beam pistol", "Small sidearm with a glowing emitter.", {"muzzle": ((0, 0, .62), UP)})
def _(F, A):
    F.box("grip", (0, .06, -.02), (.08, .16, .22), (1, 1), .02, rot=RX(-20))
    A.box("armor2", (0, 0, .26), (.14, .18, .5), (1, 1), .03); A.cyl("glow", (0, 0, .56), .04, .1, 'Z', 8)

@W("beam_rifle", "gun", "Beam rifle", "Long rifle with scope and front grip.", {"muzzle": ((0, 0, 1.9), UP), "hand2": ((0, 0, .7), UP)})
def _(F, A):
    F.box("grip", (0, .1, -.02), (.08, .14, .24), (1, 1), .02, rot=RX(-20))
    A.box("armor", (0, 0, .5), (.16, .24, 1.2), (1, 1), .04); A.box("armor2", (0, -.01, -.2), (.12, .2, .4), (1, 1), .03)
    A.cyl("frame", (0, 0, 1.45), .05, .9, 'Z', 8); A.cyl("glow", (0, 0, 1.88), .06, .05, 'Z', 8)
    A.cyl("accent", (0, -.2, .6), .05, .4, 'Z', 8); A.box("frame", (0, .14, .7), (.06, .1, .14), (1, 1), .01)

@W("gatling", "gun", "Gatling gun", "Six spinning barrels and an ammo drum.", {"muzzle": ((0, 0, 1.5), UP)})
def _(F, A):
    F.box("grip", (0, .12, -.02), (.08, .14, .24), (1, 1), .02, rot=RX(-20))
    A.cyl("armor2", (0, 0, .3), .2, .5, 'Z', 10); A.cyl("armor", (.26, 0, .2), .18, .26, 'X', 10)
    for i in range(6): A.cyl("frame", (math.cos(R(i * 60)) * .1, math.sin(R(i * 60)) * .1, .95), .035, 1.1, 'Z', 6)
    A.cyl("accent", (0, 0, 1.0), .16, .06, 'Z', 10)

@W("bazooka", "gun", "Bazooka", "Shoulder tube launcher with a big rocket.", {"muzzle": ((0, 0, 1.3), UP), "hand2": ((0, 0, .45), UP)})
def _(F, A):
    F.box("grip", (0, .16, -.02), (.08, .14, .24), (1, 1), .02, rot=RX(-20))
    A.cyl("armor", (0, 0, .4), .17, 1.8, 'Z', 10); A.cyl("accent2", (0, 0, 1.25), .2, .14, 'Z', 10)
    A.cyl("accent", (0, 0, -.45), .2, .1, 'Z', 10); spike(A, "accent2", (0, 0, 1.32), .12, .2, Z, 8)

# ================================================================ SHIELDS (origin = forearm 'mount', +Z faces out)
@W("shield_round", "shield", "Round shield", "Round buckler with a raised boss.", {"tip": ((0, 0, .2), UP)})
def _(F, A):
    F.box("frame", (0, 0, .03), (.2, .2, .06), (1, 1), .01)
    A.cyl("armor", (0, 0, .1), .7, .1, 'Z', 14, r2=.62); A.cyl("accent", (0, 0, .18), .14, .08, 'Z', 10, r2=.06)
    A.cyl("armor2", (0, 0, .09), .72, .06, 'Z', 14)

@W("shield_tower", "shield", "Tower shield", "Tall heavy shield with a view slot.", {"tip": ((0, 0, .22), UP)})
def _(F, A):
    F.box("frame", (0, 0, .03), (.2, .2, .06), (1, 1), .01)
    A.box("armor", (0, -.2, .12), (1.0, 2.0, .12), (1, 1), .04); A.box("armor2", (0, -.2, .2), (.8, 1.8, .04), (1, 1), .01)
    A.box("joint", (0, -.95, .21), (.5, .06, .03), (1, 1), 0); A.box("accent", (0, .1, .23), (.2, .2, .03), (1, 1), .01)

@W("shield_kite", "shield", "Kite shield", "Knight kite shield with a crest bar.", {"tip": ((0, 0, .2), UP)})
def _(F, A):
    F.box("frame", (0, 0, .03), (.2, .2, .06), (1, 1), .01)
    A.fin("armor", (0, 0, .12), [(-.5, .7), (.5, .7), (.42, -.3), (0, -1.1), (-.42, -.3)], .1, rot=RX(90))
    A.fin("accent2", (0, 0, .18), [(-.08, .6), (.08, .6), (.08, -.9), (-.08, -.9)], .03, rot=RX(90))
    A.fin("accent2", (0, 0, .18), [(-.4, .3), (.4, .3), (.4, .16), (-.4, .16)], .03, rot=RX(90))

@W("shield_energy", "shield", "Energy shield", "Glowing hex barrier from an emitter (used for the beam clash).", {"tip": ((0, 0, .2), UP)})
def _(F, A):
    F.cyl("frame", (0, 0, .04), .16, .08, 'Z', 6); A.cyl("armor2", (0, 0, .09), .12, .04, 'Z', 6)
    A.cyl("glow", (0, 0, .14), .95, .03, 'Z', 6)

# ================================================================ MOUNTS
@W("cannon_shoulder", "mount", "Shoulder cannon", "Long cannon on a turret for the shoulder 'pod' plug.", {"muzzle": ((0, -2.0, .3), FWD)})
def _(F, A):
    F.cyl("frame", (0, 0, .08), .14, .16, 'Z', 8); A.box("armor2", (0, 0, .3), (.34, .5, .28), (1, 1), .04)
    A.cyl("armor", (0, -1.0, .3), .1, 1.6, 'Y', 8); A.cyl("accent", (0, -1.8, .3), .13, .12, 'Y', 8)

@W("missile_pod", "mount", "Missile pod", "Box of 6 missiles for the shoulder 'pod' plug.", {"muzzle": ((0, -.32, .3), FWD)})
def _(F, A):
    F.cyl("frame", (0, 0, .06), .12, .12, 'Z', 8); A.box("armor", (0, 0, .3), (.46, .6, .4), (1, 1), .04)
    for i in range(3):
        for j in range(2): A.cyl("accent2", (-.13 + i * .13, -.3, .22 + j * .16), .045, .04, 'Y', 6)

@W("missile_pod_leg", "mount", "Leg missile pod", "Slim 4-missile pod for the side of a shin.", {"muzzle": ((0, -.22, .0), FWD)})
def _(F, A):
    F.box("frame", (0, 0, .04), (.1, .2, .3), (1, 1), .01); A.box("armor2", (0, 0, .12), (.18, .44, .6), (1, 1), .03, rot=RY(90))
    for j in range(4): A.cyl("accent2", (0, -.22, -.21 + j * .14), .04, .04, 'Y', 6)

@W("rocket_fist", "mount", "Rocket fist", "Armoured fist with boosters; plugs on the forearm 'wrist' and fires off along +Z.", {"tip": ((0, 0, .55), UP)})
def _(F, A):
    F.cyl("frame", (0, 0, .05), .1, .1, 'Z', 8); A.box("armor", (0, 0, .35), (.36, .32, .42), (1, 1), .06)
    for x in (-.12, -.04, .04, .12): A.box("armor2", (x, -.1, .57), (.07, .14, .1), (1, 1), .015)
    for s in (-1, 1): A.cyl("glow", (s * .1, .0, .06), .05, .1, 'Z', 6)
    A.cyl("accent", (0, 0, .14), .2, .1, 'Z', 8)

# ================================================================ KAIJU WEAPONS (beast colour keys)
@W("tail_blades", "kaiju", "Tail blades", "Blade fin for the top of each tail segment (tail-whip attack).", {"tip": ((0, 0, .5), UP)})
def _(F, A):
    F.box("frame", (0, 0, .03), (.12, .4, .06), (1, 1), .01)
    A.fin("claw", (0, 0, 0), [(-.3, 0), (.0, .5), (.3, .1), (.25, 0)], .05, rot=RZ(90))

@W("crystal_spikes", "kaiju", "Crystal spikes", "Spike launcher crystal for the crystal mount plugs (fires shards).", {"tip": ((0, 0, .8), UP), "muzzle": ((0, 0, .8), UP)})
def _(F, A):
    F.cyl("frame", (0, 0, .03), .16, .06, 'Z', 6)
    for a in range(0, 360, 72): spike(A, "crystal", (math.cos(R(a)) * .08, math.sin(R(a)) * .08, .02), .05, .4, (math.cos(R(a)) * .5, math.sin(R(a)) * .5, 1), 5)
    spike(A, "crystal", (0, 0, .02), .1, .8, Z, 6)

@W("claw_set", "kaiju", "Claw set", "Three long blade claws worn over a kaiju hand (plugs on 'grip').", {"tip": ((0, 0, .7), UP)})
def _(F, A):
    F.box("frame", (0, 0, 0), (.3, .16, .14), (1, 1), .02); A.box("plate", (0, 0, 0), (.34, .2, .16), (1, 1), .03)
    for x in (-.1, 0, .1): A.fin("claw", (x, 0, .05), [(-.04, 0), (.0, .66), (.06, .5), (.04, 0)], .04, rot=RZ(90))

@W("horn_ram", "kaiju", "Horn ram", "Battering-ram horn plate for the head 'horn' plug (charge attack).", {"tip": ((0, -.5, .3), FWD)})
def _(F, A):
    F.box("frame", (0, 0, .03), (.3, .3, .06), (1, 1), .01); A.box("horn", (0, -.1, .1), (.5, .5, .14), (.8, .8), .04)
    spike(A, "horn", (0, -.2, .12), .14, .55, (0, -1, .5), 6)
    for s in (-1, 1): spike(A, "horn", (s * .2, -.1, .12), .08, .32, (s * .7, -.6, .5), 5)

SLOTS = ["melee", "gun", "shield", "mount", "kaiju"]


# ================================================================ previews: mechs and kaiju holding them
POSE_ARMED = {"shoulder": (-24, -10, 0), "elbow": (-70, 0, 0), "hip": (0, -6, 0), "knee": (8, 0, 0), "ankle": (-3, 6, 0), "neck": (-4, 0, 0)}
LOADOUTS = {   # mech: (sheet, scheme, {mount: weapon})
    "Vanguard": dict(R="energy_sword", Lshield="shield_energy", pod="missile_pod"),
    "Bulwark": dict(R="gatling", Lshield="shield_tower", pod="cannon_shoulder"),
    "Titanheart": dict(R="great_sword", Lwrist="rocket_fist", pod="missile_pod"),
    "Ranger": dict(R="beam_rifle", Lshield="shield_round", shin="missile_pod_leg"),
    "Paladin": dict(R="lance", Lshield="shield_kite"),
    "Falcon": dict(R="katana", L="beam_pistol", pod="missile_pod"),
    "Mule": dict(R="bazooka", L="war_hammer"),
    "Wraith": dict(R="scythe", L="chain_whip"),
    "Lionheart": dict(R="drill_lance", L="axe"),
}


def wpn(pid, scheme, parent, at, d=UP, tag=""):
    fo, ao, plugs = B.make_part(pid, scheme, False, tag)
    fo.parent = parent; fo.location = at; fo.rotation_euler = B.rot_to(d).to_euler(); return [fo, ao]


def arm_mech(name, sheet, scheme, at, load):
    root, objs = mk.assemble(name, sheet, scheme, at=at, pose=POSE_ARMED, hands={"R": "grip", "L": "grip"})
    extra = []; B._upd()
    find = lambda pfx: [o for o in objs if o.name.startswith(f"{name}.{pfx}") and not o.get("armor_of")]
    hands = {("L" if o.name.endswith("_L") else "R"): o for o in objs if o.get("part") == "hand_kit"}
    fore = {("L" if o.name.endswith("_L") else "R"): o for o in objs if mk.PARTS.get(o.get("part"), {}).get("slot") == "forearm"}
    sh = {("L" if o.name.endswith("_L") else "R"): o for o in objs if mk.PARTS.get(o.get("part"), {}).get("slot") == "shoulder"}
    shin = {("L" if o.name.endswith("_L") else "R"): o for o in objs if mk.PARTS.get(o.get("part"), {}).get("slot") == "shin"}
    grip = Vector(mk.HAND_PLUGS["grip"][0])
    for side in ("R", "L"):
        g = grip.copy(); sx = -1 if side == "L" else 1
        if side in load: extra += wpn(load[side], scheme, hands[side], g, FWD, f"{name}.")
        if side + "shield" in load:
            fa = fore[side]; mp = Vector(mk.PARTS[fa["part"]]["plugs"]["mount"][0]); mp.x *= sx
            extra += wpn(load[side + "shield"], scheme, fa, mp, (sx, 0, 0), f"{name}.")
        if side + "wrist" in load:
            fa = fore[side]; wp = Vector(mk.PARTS[fa["part"]]["plugs"]["wrist"][0])
            for o in [hands[side]] + list(hands[side].children_recursive): o.hide_render = True; o["hidden"] = True
            extra += wpn(load[side + "wrist"], scheme, fa, wp, DOWN, f"{name}.")
    if "pod" in load:
        for side, sx in (("R", 1), ("L", -1)):
            s_ = sh[side]; pp = Vector(mk.PARTS[s_["part"]]["plugs"]["pod"][0]); pp.x *= sx
            extra += wpn(load["pod"], scheme, s_, pp, UP, f"{name}.")
    if "shin" in load:
        for side, sx in (("R", 1), ("L", -1)): extra += wpn(load["shin"], scheme, shin[side], (sx * .26, 0, -.45), (sx, 0, 0), f"{name}.")
    B._upd()
    return root, [o for o in objs + extra if not o.get("hidden")]


def main():
    mk.reset(); mk.OUT = OUT; os.makedirs(os.path.join(OUT, "png"), exist_ok=True)
    ids = [p for p, P in B.PARTS.items() if P["kit"] == "weapons"]
    sheets = {k: dict(scheme=k.lower(), sheet=v) for k, v in LOADOUTS.items()}
    kit, objs = B.export_kit("weapons", "T044", ids, sheets, OUT, {
        "slots": SLOTS, "how_to_fit": __doc__.split("Extra plugs")[0].split("Weapon space:")[1].strip(),
        "loadouts": LOADOUTS, "builds": {}, "poses": {"armed": POSE_ARMED}})
    print(len(ids), "weapons")
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "weapons_kit.blend"))
    try: bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "weapons_kit.glb"), export_format='GLB', export_extras=True)
    except Exception as ex: print("glb skipped", ex)
    if RENDER: renders(objs)


def renders(objs):
    s = mk.setup_render(1600, 1000, bg="3a4660"); s.view_settings.exposure = .7
    s.display.shading.background_color = mk.srgb("2b3754")
    B.contact_sheet(objs, ["melee", "gun"], "01_weapon_sheet_hand", colw=1.5)
    B.contact_sheet(objs, ["shield", "mount", "kaiju"], "02_weapon_sheet_mounts_kaiju", colw=2.3,
                    turn={"shield": (-90, 0, 0), "mount": (0, 0, 70), "kaiju": (0, 0, 70)})
    g = B.ground(); s.display.shading.background_color = mk.srgb("3a4660")
    mechs = []
    for i, (nm, load) in enumerate(LOADOUTS.items()):
        root, objs_ = arm_mech(nm, mk.SHEETS[nm], nm.lower(), (i * 4.0, 0, 0), load); mechs.append((root, objs_))
    def shot(group, fname, W=2600, H=1100, el=8, az=-24):
        ms = [o for r, os_ in group for o in os_ if o.type == 'MESH' and not o.get("hitbox")]
        lo, hi = mk.world_bbox(ms); c = (lo + hi) / 2
        s.render.resolution_x, s.render.resolution_y = W, H
        w = (hi.x - lo.x) * abs(math.cos(R(az))) + (hi.y - lo.y) * abs(math.sin(R(az)))
        mk.only(ms + [g]); mk.cam_at(tuple(c), max(w, (hi.z - lo.z) * W / H * 1.1) + .8, el=el, az=az); mk.shot(fname)
    shot(mechs[:5], "03_mechs_armed_a"); shot(mechs[5:], "04_mechs_armed_b", W=2200)
    shot(mechs[:5], "05_mechs_armed_back", az=160)
    # kaiju with kaiju weapons
    kai = []
    for i, nm in enumerate(["Gorvax", "Infernoth", "Tyrantor", "Kongar"]):
        S = KK.SHEETS[nm]; sh = dict(S["sheet"])
        if nm == "Infernoth": sh["back_extra"] = dict(c1="crystal_spikes", c2="crystal_spikes", c3="crystal_cluster", c4="crystal_cluster")
        if nm == "Tyrantor": sh["horn"] = "horn_ram"
        if nm == "Kongar": sh["hand"] = "claw_hand"
        root, o = B.assemble(nm, sh, S["scheme"], at=(i * 6.5, 30, 0), pose=S["pose"]); root.rotation_euler.z = R(90); B._upd()
        ex = []
        if nm == "Gorvax":
            for t in [x for x in o if x.get("part") == "tail_plated"]: ex += wpn("tail_blades", S["scheme"], t, (0, .36, .3), UP, "G.")
        if nm == "Kongar":
            for h in [x for x in o if x.get("part") == "claw_hand"]: ex += wpn("claw_set", S["scheme"], h, KK.GRIP["grip"][0], (0, -1, -.6), "K.")
        kai.append((root, o + ex))
    B._upd(); shot(kai, "06_kaiju_weapons", W=2600, H=1100, el=10, az=-30)


if __name__ == "__main__":
    main()
