"""Mythic Forge 2.0 / Titan Clash 2.0 — KAIJU KIT (T043), made in Blender from code (bpy 5.x module).
Same standard as the mech kit: every part = inner FRAME (muscle / bone core) + ARMOUR (hide, scales, plates),
origin on its joint, PLUGS where the next part goes, invisible HITBOX (box + capsule). Original designs only.
Run:  python3 kaiju_kit.py          -> out_kaiju/kaiju_kit.json, .blend (+ .glb)
      python3 kaiju_kit.py render   -> also preview PNGs in out_kaiju/png/
By MajorasPride."""
import bpy, math, os, sys
from mathutils import Vector, Matrix
import mech_kit_R2 as mk
import beast_lib as B
from beast_lib import part, spike, limb, tuft, feather, plate, teeth, RX, RY, RZ, R, UP, DOWN, FWD, BACK, OUT_

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out_kaiju")
RENDER = "render" in sys.argv

# keys every beast part uses
BEAST_KEYS = dict(frame="4a3b3b", skin="5a6a58", skin2="b9b08a", plate="d8d3c0", claw="ece6d2", tooth="f4f0e2",
                  mouth="7a2430", eye="ffd23a", glow="5cf2ff", fur="7a5a3a", horn="d8cfb8", crystal="ff5ad8",
                  membrane="b0644a", feather="c9a46a")
def scheme(**kw): d = dict(BEAST_KEYS); d.update(kw); return d
B.SCHEMES["kit"].update({k: v for k, v in BEAST_KEYS.items() if k not in B.SCHEMES["kit"]})
B.SCHEMES["kit"].update(dict(skin="9aa3a8", skin2="d6d2c6", plate="e9e9e4", fur="b9b2a6", feather="d4d0c4", membrane="b8bcc4"))
B.SCHEMES.update({
    "gorvax":    scheme(frame="22262c", skin="33393f", skin2="4a5058", plate="c8d6dc", claw="d8d8d0", eye="ff9a2a", glow="5ce8ff"),
    "infernoth": scheme(frame="1c1830", skin="2c2a5a", skin2="4e3f8a", plate="ff5ad8", crystal="ff5ad8", claw="e8d8ff", eye="ffe14a", glow="ff5ad8"),
    "kongar":    scheme(frame="2a1e18", skin="5a3f2e", skin2="8a6a52", fur="4a3224", plate="6a4a36", claw="2a2420", eye="ffb02a", mouth="5a1e22"),
    "fenrak":    scheme(frame="2c2e34", skin="6a6e78", skin2="c8c8cc", fur="8a8e98", plate="5a5e68", claw="e8e8e0", eye="7af0ff", glow="7af0ff"),
    "skarn":     scheme(frame="2a3220", skin="4f6a2e", skin2="c2b46a", plate="7a8a3a", claw="e0d8b8", eye="ffe03a", mouth="c84a3a"),
    "grimjaw":   scheme(frame="262a1e", skin="4a5232", skin2="b8ae7a", plate="363c26", claw="e4dcc0", eye="ffcf3a", mouth="c8a080"),
    "shellmaw":  scheme(frame="2a2a22", skin="5e6248", skin2="a89a6a", plate="4a4e3a", horn="3e3a2e", claw="d8d0b8", eye="ff6a2a"),
    "sailback":  scheme(frame="26302e", skin="3e6a62", skin2="c4b890", plate="c8402e", membrane="d8603a", claw="ece4cc", eye="ffe06a"),
    "tyrantor":  scheme(frame="2e2420", skin="7a4a30", skin2="c8a47a", plate="5a3424", claw="eae2cc", eye="ffcc2a"),
    "razorclaw": scheme(frame="2e2a22", skin="b08a52", skin2="e2d2a8", feather="3a6ab0", fur="e86a2a", plate="2a4a80", claw="f0ead8", eye="ff3a3a"),
    "skyrend":   scheme(frame="26282e", skin="5a6070", skin2="c8ccd4", membrane="c86a3a", horn="e8a02a", plate="e8a02a", claw="e4e0d4", eye="ffe46a"),
})

# ================================================================ HIPS (root). origin = hip centre
def hips_plugs(w, l, hz, back_z=.4):
    return {"waist": ((0, -l / 2, .05), FWD), "hip_R": ((w, .05, hz), DOWN), "hip_L": ((-w, .05, hz), DOWN),
            "tail": ((0, l / 2, 0), BACK), "back": ((0, 0, back_z), UP)}

@part("hips_heavy", "hips", "Heavy hips", "Thick upright-kaiju hips with belly scales and big thigh sockets.", hips_plugs(.42, .8, -.25))
def _(F, A):
    F.box("frame", (0, 0, 0), (.84, .8, .7), (.9, 1), .06); F.cyl("frame", (0, .05, -.25), .16, 1.0, 'X', 8)
    A.box("skin", (0, 0, .04), (.98, .86, .76), (.85, .95), .08)
    A.box("skin2", (0, -.18, -.28), (.62, .5, .22), (1, 1), .05)

@part("hips_lean", "hips", "Lean hips", "Narrow hunter hips for horizontal theropods (rex, raptor, spino).", hips_plugs(.3, .8, -.2))
def _(F, A):
    F.box("frame", (0, 0, 0), (.6, .8, .55), (.9, 1), .05); F.cyl("frame", (0, .05, -.2), .13, .75, 'X', 8)
    A.box("skin", (0, 0, .04), (.7, .86, .6), (.75, .95), .07, front=(1.05, 1.05))
    A.box("skin2", (0, -.1, -.24), (.44, .5, .14), (1, 1), .04)

@part("hips_quad", "hips", "Four-leg hips", "Wide flat hips for four-legged beasts (wolf, lizard, croc, turtle).", hips_plugs(.38, .9, -.18, .3))
def _(F, A):
    F.box("frame", (0, 0, 0), (.76, .9, .5), (.9, 1), .05); F.cyl("frame", (0, .05, -.18), .14, .9, 'X', 8)
    A.box("skin", (0, 0, .04), (.9, .96, .56), (.8, .95), .07)
    A.box("skin2", (0, 0, -.25), (.6, .7, .1), (1, 1), .03)

@part("hips_ape", "hips", "Ape hips", "Short heavy primate hips with a fur skirt.", hips_plugs(.36, .6, -.25))
def _(F, A):
    F.box("frame", (0, 0, 0), (.8, .6, .6), (.9, 1), .06); F.cyl("frame", (0, .05, -.25), .15, .9, 'X', 8)
    A.box("fur", (0, 0, .02), (.94, .7, .66), (.85, .95), .08)
    for s in (-1, 1):
        for i in range(3): tuft(A, "fur", (s * .44, -.2 + i * .2, -.2), (s * .6, 0, -1), 3, .26, .06)

# ================================================================ CHEST. origin = waist (back end), runs to -Y
def chest_plugs(l, w, sz, nz, bz=.42, wing=None):
    p = {"neck": ((0, -l, nz), FWD), "shoulder_R": ((w, -l * .78, sz), DOWN), "shoulder_L": ((-w, -l * .78, sz), DOWN),
         "back": ((0, -l * .5, bz), UP)}
    if wing: p.update({"wing_R": ((wing[0], -l * .62, wing[1]), OUT_), "wing_L": ((-wing[0], -l * .62, wing[1]), (-1, 0, 0))})
    return p

@part("chest_heavy", "chest", "Heavy chest", "Barrel kaiju chest with belly plates and thick shoulders.", chest_plugs(1.1, .5, -.12, .18, wing=(.4, .3)))
def _(F, A):
    F.box("frame", (0, -.55, 0), (.8, 1.1, .78), (.95, 1), .06, front=(.82, .82))
    A.box("skin", (0, -.56, .03), (.96, 1.16, .9), (.9, 1), .08, front=(.78, .8))
    for i in range(4): A.box("skin2", (0, -.18 - i * .25, -.44), (.56 - i * .04, .22, .06), (1, 1), .02)
    for s in (-1, 1): A.ball("skin", (s * .44, -.86, -.06), .2, 8)

@part("chest_lean", "chest", "Lean chest", "Deep narrow theropod chest; small arms hang under the front.", chest_plugs(.95, .26, -.28, .1))
def _(F, A):
    F.box("frame", (0, -.47, -.02), (.56, .95, .62), (.95, 1), .05, front=(.7, .75))
    A.box("skin", (0, -.48, 0), (.66, 1.0, .72), (.85, 1), .07, front=(.66, .72))
    A.box("skin2", (0, -.52, -.34), (.4, .7, .1), (1, 1), .03)

@part("chest_ape", "chest", "Ape chest", "Huge primate chest and shoulders with a fur mantle.", chest_plugs(.9, .62, .05, .22, .5))
def _(F, A):
    F.box("frame", (0, -.45, 0), (1.0, .9, .86), (1.1, 1), .07, front=(.9, .9))
    A.box("skin", (0, -.5, -.06), (.8, .86, .7), (1, 1), .07, front=(.9, .9))       # bare chest skin
    A.box("fur", (0, -.38, .1), (1.2, .9, .9), (1.15, 1), .1, front=(.85, .85))
    for s in (-1, 1):
        A.ball("fur", (s * .6, -.72, .08), .26, 8)
        for i in range(3): tuft(A, "fur", (s * .62, -.4 + i * .2, .28), (s * .6, .3, 1), 3, .24, .05)

@part("chest_quad", "chest", "Four-leg chest", "Deep four-legged chest with front-leg sockets underneath.", chest_plugs(1.0, .36, -.2, .12, .36))
def _(F, A):
    F.box("frame", (0, -.5, 0), (.72, 1.0, .62), (.95, 1), .05, front=(.85, .9))
    A.box("skin", (0, -.5, .03), (.86, 1.06, .7), (.85, 1), .07, front=(.8, .85))
    A.box("skin2", (0, -.55, -.33), (.5, .8, .1), (1, 1), .03)

@part("chest_croc", "chest", "Croc chest", "Long low armoured chest with rows of back scutes.", chest_plugs(1.1, .42, -.12, .02, .26))
def _(F, A):
    F.box("frame", (0, -.55, 0), (.8, 1.1, .44), (.95, 1), .04, front=(.85, .9))
    A.box("skin", (0, -.55, .02), (.94, 1.14, .5), (.8, 1), .05, front=(.8, .9))
    A.box("skin2", (0, -.55, -.24), (.66, .9, .06), (1, 1), .02)
    for s in (-1, 0, 1):
        for i in range(5): A.box("plate", (s * .2, -.12 - i * .22, .3), (.12, .16, .08), (.5, .6), .01)

# ================================================================ NECK chain. origin = back end, runs to -Y
NECK = lambda l: {"next": ((0, -l, 0), FWD)}

@part("neck_thick", "neck", "Thick neck", "Short heavy neck segment (chain 1-2).", NECK(.36))
def _(F, A):
    F.cyl("frame", (0, -.18, 0), .3, .4, 'Y', 8, r2=.27); A.cyl("skin", (0, -.18, .02), .34, .38, 'Y', 8, r2=.3)
    A.box("skin2", (0, -.18, -.27), (.3, .3, .06), (1, 1), .02)

@part("neck_long", "neck", "Long neck", "Slim neck segment for spinos, pterosaurs and dragons (chain 2-5).", NECK(.34))
def _(F, A):
    F.cyl("frame", (0, -.17, 0), .16, .36, 'Y', 8, r2=.14); A.cyl("skin", (0, -.17, .01), .19, .34, 'Y', 8, r2=.17)
    A.box("skin2", (0, -.17, -.15), (.16, .28, .04), (1, 1), .01)

@part("neck_furry", "neck", "Fur ruff neck", "Short neck wrapped in a thick fur ruff (wolf, ape).", NECK(.3))
def _(F, A):
    F.cyl("frame", (0, -.15, 0), .22, .34, 'Y', 8, r2=.2); A.cyl("fur", (0, -.12, .02), .36, .3, 'Y', 8, r2=.3)
    for a in range(0, 360, 45):
        d = (math.cos(R(a)), .5, math.sin(R(a))); tuft(A, "fur", (d[0] * .3, -.05, d[2] * .3), d, 3, .2, .05)

# ================================================================ HEADS. origin = neck joint (back of skull), snout to -Y
def head_plugs(jaw, horn=None, crest=None):
    p = {"jaw": (jaw, FWD)}
    if horn: p["horn"] = (horn, UP)
    if crest: p["crest"] = (crest, crest[3] if len(crest) > 3 else BACK)
    return {k: ((v[0][0], v[0][1], v[0][2]), v[1]) for k, v in p.items()}

def skull(F, A, sk, sn, eye=(.18, -.3, .12), brow=True, key="skin", teeth_n=5, tooth_x=None):
    """sk / sn = (w, l, h) of skull and snout. Snout sits in front of the skull, a bit lower."""
    F.box("frame", (0, -sk[1] / 2, .02), (sk[0] * .8, sk[1] * .9, sk[2] * .8), (.9, 1), .03)
    A.box(key, (0, -sk[1] / 2, .04), sk, (.85, .9), .05, front=(.9, .9))
    A.box(key, (0, -sk[1] - sn[1] / 2 + .04, -.02), sn, (.85, .9), .03, front=(.75, .75))
    A.box("mouth", (0, -sk[1] - sn[1] / 2 + .04, -.02 - sn[2] / 2 + .01), (sn[0] * .82, sn[1] * .9, .02), (1, 1), 0)
    for s in (-1, 1):
        A.box("eye", (s * eye[0], eye[1], eye[2]), (.03, .09, .05), (1, 1), 0)
        if brow: A.box(key, (s * eye[0] * .9, eye[1], eye[2] + .06), (.12, .16, .05), (.8, 1), .01, rot=RY(s * -12))
    if teeth_n: teeth(A, (0, -sk[1] + .04, -.02 - sn[2] / 2 + .01), sn[1] * .9, teeth_n, tooth_x or sn[0] * .4)

@part("head_saurian", "head", "Saurian head", "Upright atomic-lizard head: heavy brow, short snout, tooth rows.", head_plugs((0, -.24, -.12), (0, -.3, .26)))
def _(F, A):
    skull(F, A, (.5, .5, .42), (.38, .36, .24), (.2, -.34, .12))
    for s in (-1, 1): spike(A, "plate", (s * .16, -.04, .12), .04, .14, (s * .4, 1, .6))

@part("head_rex", "head", "Tyrant head", "Big boxy theropod head with a deep jaw and brow horns.", head_plugs((0, -.3, -.14), (0, -.36, .26)))
def _(F, A):
    skull(F, A, (.52, .62, .46), (.42, .46, .28), (.22, -.4, .14), teeth_n=6)
    for s in (-1, 1): spike(A, "horn", (s * .2, -.42, .22), .04, .1, (s * .3, 0, 1))

@part("head_spino", "head", "Croc-snout head", "Long narrow fish-catcher snout with a little crest (spinosaur style).", head_plugs((0, -.22, -.08), (0, -.22, .2)))
def _(F, A):
    skull(F, A, (.34, .4, .32), (.22, .78, .17), (.14, -.26, .1), teeth_n=8)
    A.box("plate", (0, -.24, .2), (.04, .26, .1), (1, .6), .01)
    A.ball("skin", (0, -1.1, -.01), .1, 6)

@part("head_raptor", "head", "Raptor head", "Slim hunter head with a feather crest plug.", head_plugs((0, -.18, -.08), crest=(0, -.06, .14)))
def _(F, A):
    skull(F, A, (.3, .38, .28), (.2, .36, .16), (.13, -.24, .08), teeth_n=5)

@part("head_ape", "head", "Ape head", "Primate head: big brow ridge, flat muzzle, small ears.", head_plugs((0, -.26, -.1)))
def _(F, A):
    F.box("frame", (0, -.2, .1), (.4, .36, .4), (.9, 1), .04)
    A.box("fur", (0, -.18, .14), (.52, .44, .5), (.8, .85), .08)
    A.box("skin", (0, -.38, .06), (.4, .2, .3), (.9, .9), .05)                  # face
    A.box("skin", (0, -.46, -.02), (.34, .18, .16), (.9, .9), .04)              # muzzle
    A.box("skin", (0, -.44, .2), (.44, .14, .08), (1, 1), .02)                  # brow ridge
    for s in (-1, 1):
        A.box("eye", (s * .1, -.48, .14), (.08, .02, .04), (1, 1), 0)
        A.ball("skin", (s * .27, -.18, .14), .07, 6)
    tuft(A, "fur", (0, -.1, .38), (0, .3, 1), 5, .2, .05)

@part("head_wolf", "head", "Wolf head", "Long-muzzled wolf head with tall ears and a fur crown.", head_plugs((0, -.3, -.1)))
def _(F, A):
    skull(F, A, (.44, .42, .36), (.24, .44, .2), (.14, -.38, .1), brow=False, key="fur", teeth_n=4)
    A.ball("joint" if False else "mouth", (0, -.86, .02), .05, 6)
    for s in (-1, 1): A.fin("fur", (s * .14, -.12, .2), [(-.08, 0), (0, .26), (.08, 0)], .04, rot=RY(s * -15))
    tuft(A, "fur", (0, .02, .1), (0, 1, .4), 5, .22, .05)

@part("head_lizard", "head", "Lizard head", "Flat wide monitor-lizard head with a long jaw.", head_plugs((0, -.2, -.07)))
def _(F, A):
    skull(F, A, (.42, .34, .24), (.34, .44, .13), (.18, -.22, .07), teeth_n=0)
    for s in (-1, 1): A.box("plate", (s * .16, -.1, .12), (.08, .16, .04), (1, 1), .01)

@part("head_croc", "head", "Croc head", "Very long flat crocodile snout; eyes and nostrils on top, teeth outside.", head_plugs((0, -.18, -.06)))
def _(F, A):
    skull(F, A, (.46, .36, .24), (.32, .9, .12), (.15, -.2, .14), brow=False, teeth_n=9, tooth_x=.17)
    for s in (-1, 1): A.box("skin", (s * .15, -.2, .12), (.12, .14, .08), (.8, .8), .02)
    A.box("skin", (0, -1.2, .04), (.14, .1, .06), (.8, .8), .01)

@part("head_snapper", "head", "Snapper head", "Snapping-turtle head: hooked beak, ridged skull, no teeth.", head_plugs((0, -.22, -.1)))
def _(F, A):
    skull(F, A, (.44, .4, .34), (.3, .2, .22), (.17, -.28, .1), teeth_n=0)
    spike(A, "horn", (0, -.6, .0), .07, .14, (0, -.3, -1), 4)                       # beak hook
    A.box("horn", (0, -.52, .02), (.28, .16, .18), (.6, .7), .02)
    for i in range(3): A.box("plate", (0, -.1 - i * .12, .24), (.08, .1, .06), (.5, .6), .01)

@part("head_ptero", "head", "Pterosaur head", "Long pointed beak and a big swept-back crest plug.", head_plugs((0, -.18, -.06), crest=(0, -.12, .14)))
def _(F, A):
    skull(F, A, (.28, .3, .24), (.14, .8, .1), (.11, -.2, .07), teeth_n=0)
    A.box("horn", (0, -1.1, -.02), (.06, .2, .06), (.3, .3), .01)

# ---- JAWS (open with the "jaw" angle). origin = hinge, jaw runs to -Y
def jaw(L, w, h=.1, tn=5, key="skin", beak=False):
    def fn(F, A):
        F.box("frame", (0, -L / 2, -h / 2), (w * .8, L * .9, h * .6), (1, 1), .02, front=(.6, .7))
        A.box(key, (0, -L / 2, -h / 2), (w, L, h), (1, .9), .03, front=(.6, .7))
        A.box("mouth", (0, -L / 2, -.005), (w * .8, L * .9, .02), (1, 1), 0, front=(.6, 1))
        if tn: teeth(A, (0, -.05, 0), L * .85, tn, w * .38, down=False)
        if beak: A.box("horn", (0, -L + .06, -.04), (w * .6, .14, .1), (.6, .7), .02)
    return fn
for pid, nm, about, args in [
        ("jaw_saurian", "Saurian jaw", "Short heavy lower jaw with up-teeth.", (.6, .34, .12, 5)),
        ("jaw_rex", "Tyrant jaw", "Deep long lower jaw for the tyrant head.", (.82, .4, .16, 6)),
        ("jaw_long", "Long jaw", "Narrow long jaw for croc-snout and spino heads.", (1.02, .2, .09, 8)),
        ("jaw_raptor", "Raptor jaw", "Slim jaw for raptors.", (.5, .2, .08, 5)),
        ("jaw_ape", "Ape jaw", "Wide primate jaw with fangs.", (.34, .32, .12, 3)),
        ("jaw_wolf", "Wolf jaw", "Long wolf jaw with fangs.", (.62, .22, .1, 4)),
        ("jaw_lizard", "Lizard jaw", "Flat wide jaw, no teeth showing.", (.6, .32, .07, 0)),
        ("jaw_croc", "Croc jaw", "Very long croc jaw with outside teeth.", (1.08, .3, .08, 9)),
        ("jaw_beak", "Beak jaw", "Toothless beak jaw (snapper, pterosaur).", (.36, .28, .1, 0, "skin", True)),
        ("jaw_ptero", "Pterosaur jaw", "Very long toothless beak jaw.", (.86, .13, .06, 0, "skin", True))]:
    part(pid, "jaw", nm, about, {})(jaw(*args))

# ---- HORNS and CRESTS (mount on head plugs, +Z = out of the plug)
@part("horn_pair", "horn", "Twin horns", "Two swept horns.", {})
def _(F, A):
    for s in (-1, 1): spike(A, "horn", (s * .12, 0, 0), .06, .34, (s * .5, .6, 1), 6)
@part("horn_nose", "horn", "Nose horn", "One rhino-style horn.", {})
def _(F, A): spike(A, "horn", (0, 0, 0), .08, .3, (0, -.3, 1), 6)
@part("crest_feather", "crest", "Feather crest", "Fan of crest feathers (raptor, feathered dragons).", {})
def _(F, A):
    for i in range(5): feather(A, "feather", (0, 0, 0), .34 - abs(i - 2) * .04, .07, rot=RX(180 + (i - 2) * 16))
@part("crest_ptero", "crest", "Sail crest", "Big swept pterosaur crest.", {})
def _(F, A): A.fin("horn", (0, 0, 0), [(0, 0), (-.05, .0), (0, .3), (.06, .5), (.1, .2)], .03, rot=RZ(90) @ RY(-30))

# ================================================================ BACK pieces (mount on the chest 'back' plug)
@part("back_plates", "back", "Dorsal plates", "Three rows of leaf-shaped spine plates (upright kaiju).", {})
def _(F, A):
    F.box("frame", (0, 0, -.02), (.3, 1.0, .08), (1, 1), .02)
    for i, (y, h) in enumerate([(.4, .34), (.16, .48), (-.1, .56), (-.36, .44)]):
        plate(A, "plate", (0, y, 0), h, .26)
        for s in (-1, 1): plate(A, "plate", (s * .16, y + .08, -.02), h * .62, .2, rot=RY(s * 22))

@part("back_crystal", "back", "Crystal mount", "Crystal back base with 4 crystal plugs (INFERNOTH style shoulder crystals).",
      {"c1": ((.34, -.28, .04), (.6, -.1, 1)), "c2": ((-.34, -.28, .04), (-.6, -.1, 1)), "c3": ((.14, .2, .06), (.3, .3, 1)), "c4": ((-.14, .2, .06), (-.3, .3, 1))})
def _(F, A):
    F.box("frame", (0, -.05, -.02), (.8, .9, .1), (1, 1), .02)
    A.box("skin", (0, -.05, .0), (.86, .94, .1), (.9, .9), .03)
    for i in range(4): plate(A, "crystal", (0, .4 - i * .26, .04), .26, .18, crystal=True)

@part("crystal_spire", "crystal", "Crystal spire", "Tall glowing crystal (plugs into the crystal mount).", {})
def _(F, A):
    F.cyl("frame", (0, 0, .04), .14, .1, 'Z', 6)
    A.cyl("crystal", (0, 0, .5), .02, .3, 'Z', 6, r2=.0)
    A.cyl("crystal", (0, 0, .24), .13, .44, 'Z', 6, r2=.1)
    A.cyl("crystal", (0, 0, .58), .1, .26, 'Z', 6, r2=.01)

@part("crystal_cluster", "crystal", "Crystal cluster", "Cluster of three smaller crystals.", {})
def _(F, A):
    F.cyl("frame", (0, 0, .03), .16, .08, 'Z', 6)
    for a, h in ((0, .5), (120, .36), (240, .3)):
        d = (math.cos(R(a)) * .35, math.sin(R(a)) * .35, 1)
        spike(A, "crystal", (math.cos(R(a)) * .06, math.sin(R(a)) * .06, 0), .08, h, d, 6)

@part("back_sail", "back", "Spine sail", "Tall spinosaur sail on a row of spines.", {})
def _(F, A):
    F.box("frame", (0, 0, -.02), (.2, 1.1, .08), (1, 1), .02)
    A.fin("membrane", (0, 0, 0), [(-.62, 0), (-.5, .5), (-.2, .9), (.1, 1.0), (.42, .78), (.62, .34), (.66, 0)], .04, rot=RZ(90))
    for i in range(7): A.box("plate", (0, .56 - i * .19, .42), (.06, .03, .84 - abs(i - 3) * .14), (1, 1), 0)

@part("back_fur", "back", "Fur mane", "Thick fur mane along the shoulders (wolf, ape).", {})
def _(F, A):
    F.box("frame", (0, 0, -.02), (.5, .9, .1), (1, 1), .02)
    A.box("fur", (0, 0, .04), (.66, .9, .18), (.8, .9), .06)
    for i in range(5):
        for s in (-1, 0, 1): tuft(A, "fur", (s * .2, .36 - i * .18, .1), (s * .4, .6, 1), 3, .26, .06)

@part("back_shell", "back", "Snapper shell", "Big ridged turtle shell that covers chest and hips.", {})
def _(F, A):
    F.box("frame", (0, .45, -.22), (1.0, 1.7, .2), (1, 1), .03)
    A.box("plate", (0, .45, -.12), (1.3, 1.95, .5), (.72, .8), .14)
    A.box("plate", (0, .45, -.38), (1.42, 2.05, .1), (1, 1), .03)
    for s in (-1, 0, 1):
        for i in range(4): spike(A, "horn", (s * .32, -.15 + i * .4, .1 - abs(s) * .06), .1, .18, (s * .3, 0, 1), 4)

@part("back_feathers", "back", "Feather mantle", "Rows of feathers down the back (raptor, feathered dragon).", {})
def _(F, A):
    F.box("frame", (0, 0, -.02), (.4, .9, .08), (1, 1), .02)
    for i in range(5):
        for s in (-1, 1): feather(A, "feather", (s * .12, -.36 + i * .2, .04), .36, .1, rot=RX(-70) @ RY(s * 30))

@part("back_scutes", "back", "Back scutes", "Extra rows of bony scutes (croc, lizard).", {})
def _(F, A):
    F.box("frame", (0, 0, -.02), (.5, .9, .06), (1, 1), .02)
    for s in (-1, 0, 1):
        for i in range(4): A.box("plate", (s * .18, -.3 + i * .22, .06), (.1, .14, .12), (.4, .6), .01)

# ================================================================ ARMS (front legs / arms / wings). origin = shoulder
ELB = lambda l: {"elbow": ((0, 0, -l), DOWN)}
WRI = lambda l: {"wrist": ((0, 0, -l), DOWN)}

def arm_part(pid, name, about, L, rt, rb, key="skin", up=True, extra=None):
    def fn(F, A):
        F.ball("frame", (0, 0, 0), rt * .9, 8); limb(F, "frame", L, rt * .7, rb * .7)
        limb(A, key, L * .9, rt, rb, (0, 0, -L * .04))
        if extra: extra(F, A, L)
    part(pid, "arm_up" if up else "arm_lo", name, about, ELB(L) if up else WRI(L), side=True)(fn)

arm_part("arm_up_heavy", "Heavy upper arm", "Thick kaiju upper arm.", .7, .2, .16)
arm_part("arm_up_small", "Small upper arm", "Short tyrant-style upper arm.", .34, .1, .08)
arm_part("arm_up_ape", "Ape upper arm", "Long furry primate upper arm.", .95, .24, .2, "fur",
         extra=lambda F, A, L: tuft(A, "fur", (.18, .05, -.4), (1, .4, -.4), 4, .26, .06))
arm_part("arm_up_quad", "Foreleg upper", "Front-leg upper for four-legged beasts.", .62, .19, .15)
arm_part("arm_up_wing", "Wing arm upper", "Strong pterosaur wing-arm upper with membrane root.", .6, .16, .12,
         extra=lambda F, A, L: A.fin("membrane", (0, 0, 0), [(0, 0), (0, -L), (.5, -L * .9), (.6, -.1)], .02, rot=RZ(90)))
arm_part("arm_lo_heavy", "Heavy forearm", "Thick kaiju forearm with a spike.", .66, .16, .13, up=False,
         extra=lambda F, A, L: spike(A, "plate", (0, .12, -.2), .05, .2, (0, 1, .3)))
arm_part("arm_lo_small", "Small forearm", "Short tyrant forearm.", .3, .08, .07, up=False)
arm_part("arm_lo_ape", "Ape forearm", "Long primate forearm for knuckle walking.", .9, .2, .17, "fur", up=False)
arm_part("arm_lo_quad", "Foreleg lower", "Front-leg lower for four-legged beasts.", .64, .14, .1, up=False)
arm_part("arm_lo_feather", "Feathered forearm", "Raptor forearm with a row of feathers.", .42, .09, .07, up=False,
         extra=lambda F, A, L: [feather(A, "feather", (0, .05, -i * .1), .3, .08, rot=RZ(90) @ RX(20)) for i in range(4)])
arm_part("arm_lo_wing", "Wing forearm", "Long pterosaur wing forearm with the main membrane.", 1.1, .1, .08, up=False,
         extra=lambda F, A, L: A.fin("membrane", (0, 0, 0), [(0, 0), (0, -L), (.9, -L * .7), (1.0, -.1)], .02, rot=RZ(90)))

# ---- HANDS. origin = wrist
GRIP = {"grip": ((0, -.06, -.16), FWD)}
@part("claw_hand", "hand", "Claw hand", "Kaiju hand with 3 hooked claws (plug 'grip' holds weapons).", GRIP, side=True)
def _(F, A):
    F.ball("frame", (0, 0, 0), .1, 8); A.box("skin", (0, -.04, -.12), (.24, .2, .2), (1, 1), .04)
    for x in (-.08, 0, .08): spike(A, "claw", (x, -.12, -.16), .04, .18, (0, -1, -.8), 4)
@part("small_claw", "hand", "Little claws", "Two-finger tyrant hand.", GRIP, side=True)
def _(F, A):
    A.box("skin", (0, -.02, -.06), (.12, .1, .1), (1, 1), .02)
    for x in (-.03, .03): spike(A, "claw", (x, -.06, -.08), .02, .1, (0, -1, -1), 4)
@part("ape_fist", "hand", "Ape fist", "Big knuckle fist for knuckle walking and punching.", GRIP, side=True)
def _(F, A):
    F.ball("frame", (0, 0, 0), .14, 8); A.box("skin", (0, -.04, -.16), (.34, .3, .3), (1, 1), .06)
    for x in (-.1, -.03, .04, .11): A.box("skin2", (x, -.18, -.24), (.06, .06, .08), (1, 1), .015)
@part("paw", "hand", "Paw", "Wolf paw with 4 toes and claws (front or back).", GRIP, side=True)
def _(F, A):
    F.ball("frame", (0, 0, 0), .1, 8); A.box("fur", (0, -.08, -.1), (.24, .3, .16), (.9, .8), .05)
    for x in (-.08, -.03, .03, .08): spike(A, "claw", (x, -.24, -.14), .025, .08, (0, -1, -.6), 4)
@part("lizard_hand", "hand", "Lizard hand", "Spread 5-toe reptile hand (front or back).", GRIP, side=True)
def _(F, A):
    F.ball("frame", (0, 0, 0), .09, 8); A.box("skin", (0, -.06, -.08), (.22, .2, .1), (1, 1), .03)
    for a in (-50, -25, 0, 25, 50):
        d = Vector((math.sin(R(a)), -math.cos(R(a)), -.15))
        A.box("skin", tuple(Vector((0, -.12, -.1)) + d * .1), (.04, .16, .04), (1, 1), .01, rot=RZ(-a))
        spike(A, "claw", tuple(Vector((0, -.12, -.1)) + d * .2), .015, .06, tuple(d), 4)
@part("wing_hand", "hand", "Wing finger", "Pterosaur hand: 3 small claws and a huge wing finger with membrane.", {"tip": ((0, 0, -1.2), DOWN)}, side=True)
def _(F, A):
    F.ball("frame", (0, 0, 0), .07, 6); limb(F, "frame", 1.2, .05, .02)
    A.fin("membrane", (0, 0, 0), [(0, 0), (0, -1.2), (.4, -.5), (.6, -.05)], .02, rot=RZ(90))
    for x in (-.04, 0, .04): spike(A, "claw", (x, -.06, -.04), .015, .07, (0, -1, -.4), 4)

# ================================================================ LEGS. origin = hip / knee / ankle
KNEE = lambda l: {"knee": ((0, 0, -l), DOWN)}
ANK = lambda l: {"ankle": ((0, 0, -l), DOWN)}
def leg_part(pid, slot, name, about, L, rt, rb, key="skin", extra=None):
    def fn(F, A):
        F.ball("frame", (0, 0, 0), rt * .85, 8); limb(F, "frame", L, rt * .7, rb * .7)
        limb(A, key, L * .92, rt, rb, (0, 0, -L * .03))
        if extra: extra(F, A, L)
    part(pid, slot, name, about, KNEE(L) if slot == "thigh" else ANK(L), side=True)(fn)

leg_part("thigh_heavy", "thigh", "Heavy thigh", "Huge kaiju thigh.", .95, .34, .26)
leg_part("thigh_lean", "thigh", "Lean thigh", "Muscular theropod thigh.", .8, .26, .18)
leg_part("thigh_quad", "thigh", "Four-leg thigh", "Back-leg thigh for four-legged beasts.", .66, .24, .17)
leg_part("thigh_ape", "thigh", "Ape thigh", "Short furry primate thigh.", .62, .25, .2, "fur")
leg_part("shin_heavy", "shin", "Heavy shin", "Column shin with knee plate.", .92, .25, .22,
         extra=lambda F, A, L: A.box("skin2", (0, -.22, -.12), (.26, .08, .24), (1, 1), .03))
leg_part("shin_digi", "shin", "Bird shin", "Long thin theropod shin (walks on toes).", .9, .16, .1)
leg_part("shin_quad", "shin", "Four-leg shin", "Back-leg shin with a hock.", .62, .15, .1)
leg_part("shin_ape", "shin", "Ape shin", "Short primate shin.", .56, .2, .16, "fur")

FOOT = {"ground": ((0, -.12, -.2), DOWN)}
@part("foot_heavy", "foot", "Stomp foot", "Elephant-wide kaiju foot with 3 big toe claws.", FOOT, side=True)
def _(F, A):
    F.ball("frame", (0, 0, 0), .2, 8); A.box("skin", (0, -.1, -.12), (.46, .56, .2), (.9, .85), .06)
    for x in (-.14, 0, .14): spike(A, "claw", (x, -.36, -.14), .06, .16, (0, -1, -.3), 4)
@part("foot_bird", "foot", "Bird foot", "Theropod foot: 3 long toes and a raised sickle claw.", FOOT, side=True)
def _(F, A):
    F.ball("frame", (0, 0, 0), .1, 8); A.box("skin", (0, -.05, -.12), (.18, .2, .14), (1, 1), .03)
    for a in (-22, 0, 22):
        d = Vector((math.sin(R(a)), -math.cos(R(a)), 0))
        A.box("skin", tuple(Vector((0, -.12, -.16)) + d * .18), (.07, .36, .07), (1, 1), .015, rot=RZ(-a))
        spike(A, "claw", tuple(Vector((0, -.12, -.16)) + d * .36), .03, .1, tuple(d + Vector((0, 0, -.5))), 4)
    spike(A, "claw", (.08, -.06, -.06), .03, .18, (.2, -.6, 1), 4)            # sickle claw (raised)
@part("foot_paw", "foot", "Hind paw", "Wolf hind paw.", FOOT, side=True)
def _(F, A):
    F.ball("frame", (0, 0, 0), .1, 8); A.box("fur", (0, -.1, -.12), (.24, .32, .16), (.9, .8), .05)
    for x in (-.08, -.03, .03, .08): spike(A, "claw", (x, -.27, -.16), .025, .08, (0, -1, -.6), 4)
@part("foot_lizard", "foot", "Lizard foot", "Spread-toe reptile hind foot.", FOOT, side=True)
def _(F, A):
    F.ball("frame", (0, 0, 0), .09, 8); A.box("skin", (0, -.06, -.1), (.24, .22, .1), (1, 1), .03)
    for a in (-45, -20, 0, 20, 45):
        d = Vector((math.sin(R(a)), -math.cos(R(a)), 0))
        A.box("skin", tuple(Vector((0, -.14, -.12)) + d * .12), (.045, .2, .04), (1, 1), .01, rot=RZ(-a))
        spike(A, "claw", tuple(Vector((0, -.14, -.12)) + d * .24), .016, .06, tuple(d), 4)
@part("foot_ape", "foot", "Ape foot", "Flat primate foot with a big toe.", FOOT, side=True)
def _(F, A):
    F.ball("frame", (0, 0, 0), .14, 8); A.box("skin", (0, -.12, -.12), (.32, .48, .14), (1, 1), .04)
    A.box("skin", (-.16, -.28, -.14), (.08, .14, .08), (1, 1), .02)

# ================================================================ TAILS. origin = front end, runs to +Y; chain + decay
TAIL = lambda l: {"next": ((0, l, 0), BACK)}
def tail_part(pid, name, about, L, w, h, key="skin", extra=None):
    def fn(F, A):
        F.box("frame", (0, L / 2, 0), (w * .64, L, h * .64), (1, 1), .03, front=(1.25, 1.25))
        A.box(key, (0, L / 2, .01), (w * .8, L * 1.02, h * .8), (1, 1), .05, front=(1.25, 1.25))
        if extra: extra(F, A, L, w, h)
    part(pid, "tail", name, about, TAIL(L))(fn)

tail_part("tail_heavy", "Heavy tail", "Thick dragging kaiju tail segment.", .72, .7, .62)
tail_part("tail_plated", "Plated tail", "Heavy tail segment with dorsal plates.", .72, .7, .62,
          extra=lambda F, A, L, w, h: [plate(A, "plate", (0, L * .5, h * .4), .3, .26)])
tail_part("tail_whip", "Whip tail", "Slim tail segment (lizard, raptor, rex).", .6, .4, .36)
tail_part("tail_croc", "Croc tail", "Flat-sided croc tail with twin scute ridges.", .66, .5, .48,
          extra=lambda F, A, L, w, h: [A.box("plate", (s * w * .16, L * .5, h * .42), (.06, L * .6, .12), (.3, 1), .01) for s in (-1, 1)])
tail_part("tail_fluffy", "Fur tail", "Bushy wolf tail segment.", .5, .44, .44, "fur",
          extra=lambda F, A, L, w, h: [tuft(A, "fur", (0, L * .5, 0), (math.cos(R(a)), .4, math.sin(R(a))), 3, .2, .05) for a in (0, 90, 180, 270)])
tail_part("tail_feather", "Feather tail", "Slim tail with side feathers (raptor, feathered dragon).", .6, .36, .3,
          extra=lambda F, A, L, w, h: [feather(A, "feather", (s * w * .3, L * .5, 0), .4, .1, rot=RZ(s * 90) @ RX(90) @ RY(0)) for s in (-1, 1)])
tail_part("tail_stub", "Stub tail", "Short pointed turtle tail.", .4, .3, .26)

# ================================================================ SAMPLE KAIJU (all built only from the plugs)
UPRIGHT_LEG = ((-8, 0, 0), (16, 0, 0), (0, 0, 0))
SHEETS = {
    "Gorvax": dict(scheme="gorvax", note="Upright atomic lizard (classic city stomper).",
                   sheet=dict(hips="hips_heavy", chest="chest_heavy", neck=("neck_thick", 1), head="head_saurian", jaw="jaw_saurian",
                              back="back_plates", arm_up="arm_up_heavy", arm_lo="arm_lo_heavy", hand="claw_hand",
                              thigh="thigh_heavy", shin="shin_heavy", foot="foot_heavy", tail=("tail_plated", 6, .84)),
                   pose=dict(pitch=62, chest=6, neck=-8, head=4, jaw=26, tail=-7, tail_yaw=4,
                             arm=((-30, -10, 0), (-70, 0, 0), (-40, 0, 0)), leg=UPRIGHT_LEG)),
    "Infernoth": dict(scheme="infernoth", note="Crystal kaiju: giant shoulder crystals and a crystal spine.",
                      sheet=dict(hips="hips_heavy", chest="chest_heavy", neck=("neck_thick", 1), head="head_saurian", jaw="jaw_saurian", horn="horn_pair",
                                 back="back_crystal", back_extra=dict(c1="crystal_spire", c2="crystal_spire", c3="crystal_cluster", c4="crystal_cluster"),
                                 arm_up="arm_up_heavy", arm_lo="arm_lo_heavy", hand="claw_hand",
                                 thigh="thigh_heavy", shin="shin_heavy", foot="foot_heavy", tail=("tail_heavy", 6, .84)),
                      pose=dict(pitch=66, chest=4, neck=-6, head=6, jaw=34, tail=-6, tail_yaw=-4,
                                arm=((-40, -20, 0), (-80, 0, 0), (-50, 0, 0)), leg=UPRIGHT_LEG)),
    "Kongar": dict(scheme="kongar", note="Rampage-style giant ape, knuckle stance.",
                   sheet=dict(hips="hips_ape", chest="chest_ape", neck=("neck_furry", 1), head="head_ape", jaw="jaw_ape",
                              arm_up="arm_up_ape", arm_lo="arm_lo_ape", hand="ape_fist",
                              thigh="thigh_ape", shin="shin_ape", foot="foot_ape"),
                   pose=dict(pitch=50, chest=10, neck=-30, head=0, jaw=24,
                             arm=((-12, -10, 0), (-4, 0, 0), (0, 0, 0)), leg=((-20, -6, 0), (14, 0, 0), (0, 0, 0)))),
    "Fenrak": dict(scheme="fenrak", note="Giant wolf on four legs.",
                   sheet=dict(hips="hips_quad", chest="chest_quad", neck=("neck_furry", 2), head="head_wolf", jaw="jaw_wolf", back="back_fur",
                              arm_up="arm_up_quad", arm_lo="arm_lo_quad", hand="paw",
                              thigh="thigh_quad", shin="shin_quad", foot="foot_paw", tail=("tail_fluffy", 5, .92), legs4=True),
                   pose=dict(pitch=6, chest=4, neck=18, head=-6, jaw=20, tail=14,
                             arm=((-6, 0, 0), (8, 0, 0), (0, 0, 0)), leg=((-30, 0, 0), (34, 0, 0), (0, 0, 0)))),
    "Skarn": dict(scheme="skarn", note="Giant monitor lizard, sprawled crawl.",
                  sheet=dict(hips="hips_quad", chest="chest_quad", neck=("neck_long", 2), head="head_lizard", jaw="jaw_lizard", back="back_scutes",
                             arm_up="arm_up_quad", arm_lo="arm_lo_quad", hand="lizard_hand",
                             thigh="thigh_quad", shin="shin_quad", foot="foot_lizard", tail=("tail_whip", 8, .88), legs4=True),
                  pose=dict(pitch=0, neck=6, head=0, jaw=18, tail=2, tail_yaw=9,
                            arm=((-14, -74, 0), (-6, -22, 0), (0, 0, 0)), leg=((14, -74, 0), (6, -22, 0), (0, 0, 0)))),
    "Grimjaw": dict(scheme="grimjaw", note="Giant crocodile, low crawl (stand pose in 03_grimjaw_two_poses).",
                    sheet=dict(hips="hips_quad", chest="chest_croc", neck=("neck_thick", 1), head="head_croc", jaw="jaw_croc", back="back_scutes",
                               arm_up="arm_up_quad", arm_lo="arm_lo_quad", hand="lizard_hand",
                               thigh="thigh_quad", shin="shin_quad", foot="foot_lizard", tail=("tail_croc", 7, .86), legs4=True),
                    pose=dict(pitch=0, neck=0, head=0, jaw=30, tail=1, tail_yaw=-7,
                              arm=((-6, -84, 0), (-10, -30, 0), (0, 0, 0)), leg=((10, -84, 0), (10, -30, 0), (0, 0, 0)))),
    "Shellmaw": dict(scheme="shellmaw", note="Snapping-turtle shell beast.",
                     sheet=dict(hips="hips_quad", chest="chest_quad", neck=("neck_thick", 2), head="head_snapper", jaw="jaw_beak", back="back_shell",
                                arm_up="arm_up_quad", arm_lo="arm_lo_quad", hand="lizard_hand",
                                thigh="thigh_quad", shin="shin_quad", foot="foot_lizard", tail=("tail_stub", 3, .8), legs4=True),
                     pose=dict(pitch=0, neck=10, head=-6, jaw=32, tail=8,
                               arm=((-10, -78, 0), (-6, -26, 0), (0, 0, 0)), leg=((10, -78, 0), (6, -26, 0), (0, 0, 0)))),
    "Sailback": dict(scheme="sailback", note="Spinosaurus-style river hunter with a sail.",
                     sheet=dict(hips="hips_lean", chest="chest_lean", neck=("neck_long", 3), head="head_spino", jaw="jaw_long", back="back_sail",
                                arm_up="arm_up_heavy", arm_lo="arm_lo_heavy", hand="claw_hand",
                                thigh="thigh_lean", shin="shin_digi", foot="foot_bird", tail=("tail_whip", 7, .87)),
                     pose=dict(pitch=14, chest=4, neck=10, head=-4, jaw=24, tail=-2, tail_yaw=5,
                               arm=((-30, -8, 0), (-70, 0, 0), (-40, 0, 0)), leg=((-24, 0, 0), (32, 0, 0), (0, 0, 0)))),
    "Tyrantor": dict(scheme="tyrantor", note="Tyrant-lizard (T-rex style) with a huge head.",
                     sheet=dict(hips="hips_lean", chest="chest_lean", neck=("neck_thick", 1), head="head_rex", jaw="jaw_rex", horn="horn_nose",
                                arm_up="arm_up_small", arm_lo="arm_lo_small", hand="small_claw",
                                thigh="thigh_lean", shin="shin_digi", foot="foot_bird", tail=("tail_whip", 7, .86)),
                     pose=dict(pitch=10, chest=2, neck=8, head=0, jaw=36, tail=1, tail_yaw=-5,
                               arm=((-40, 0, 0), (-80, 0, 0), (-60, 0, 0)), leg=((-20, 0, 0), (30, 0, 0), (0, 0, 0)))),
    "Razorclaw": dict(scheme="razorclaw", note="Feathered raptor with sickle claws.",
                      sheet=dict(hips="hips_lean", chest="chest_lean", neck=("neck_long", 2), head="head_raptor", jaw="jaw_raptor", crest="crest_feather",
                                 back="back_feathers", arm_up="arm_up_small", arm_lo="arm_lo_feather", hand="claw_hand",
                                 thigh="thigh_lean", shin="shin_digi", foot="foot_bird", tail=("tail_feather", 7, .88)),
                      pose=dict(pitch=18, chest=0, neck=16, head=-10, jaw=22, tail=-1,
                                arm=((-50, -20, 0), (-20, 0, 0), (-30, 0, 0)), leg=((-30, 0, 0), (40, 0, 0), (0, 0, 0)))),
    "Skyrend": dict(scheme="skyrend", note="Pterosaur, wings spread on a landing.",
                    sheet=dict(hips="hips_lean", chest="chest_lean", neck=("neck_long", 3), head="head_ptero", jaw="jaw_ptero", crest="crest_ptero",
                               arm_up="arm_up_wing", arm_lo="arm_lo_wing", hand="wing_hand",
                               thigh="thigh_lean", shin="shin_digi", foot="foot_bird", tail=("tail_whip", 3, .7)),
                    pose=dict(pitch=40, chest=6, neck=-12, head=-16, jaw=14,
                              arm=((0, -140, 0), (0, -120, 0), (0, -112, 0)), leg=((-14, 0, 0), (20, 0, 0), (0, 0, 0)))),
}
SLOTS = ["head", "jaw", "horn", "crest", "neck", "chest", "back", "crystal", "hips", "tail", "arm_up", "arm_lo", "hand", "thigh", "shin", "foot"]


def build_roster(names, x0=0, gap=5.2, z=0, poses=None, y=0):
    out = {}
    for i, nm in enumerate(names):
        S = SHEETS[nm]; p = dict(S["pose"]); p.update((poses or {}).get(nm, {}))
        root, objs = B.assemble(nm, S["sheet"], S["scheme"], at=(x0 + i * gap, y, z), pose=p)
        root.rotation_euler.z += R(90)   # face +X in the line-up (side-on to the camera at az -28)
        out[nm] = (root, objs)
    B._upd(); return out


def main():
    mk.reset(); mk.OUT = OUT; os.makedirs(os.path.join(OUT, "png"), exist_ok=True)
    ids = [p for p, P in B.PARTS.items() if P["kit"] == "kaiju"]
    kit, objs = B.export_kit("kaiju", "T043", ids, SHEETS, OUT,
                             {"slots": SLOTS, "notes": {k: v["note"] for k, v in SHEETS.items()},
                              "jaw": "rotate the jaw part on X (opening angle, deg) at the head 'jaw' plug",
                              "tail": "chain: segment i scaled by decay^i; each segment has a 'next' plug"})
    roster = list(SHEETS)
    builds = build_roster(roster, x0=0)
    for nm, (r, o) in builds.items():
        ms = [x for x in o if x.type == 'MESH']; lo, hi = mk.world_bbox(ms)
        print(f"  {nm:10s} {sum(len(x.data.polygons) for x in ms):6d} faces, {len([x for x in o if x.get('part')]):3d} parts, "
              f"size {hi.x-lo.x:.1f} x {hi.y-lo.y:.1f} x {hi.z-lo.z:.1f}")
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "kaiju_kit.blend"))
    try: bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "kaiju_kit.glb"), export_format='GLB', export_extras=True)
    except Exception as ex: print("glb skipped", ex)
    if RENDER: renders(builds, objs)


def renders(builds, objs):
    g = B.ground(); s = mk.setup_render(1600, 1000, bg="3a4660"); s.view_settings.exposure = .7
    def frame_shot(names, fname, el=10, az=-30, W=2600, H=1100, pad=1.0, gap=.9):
        roots = [builds[n][0] for n in names]; keep = [r.location.copy() for r in roots]
        x = 0
        for r in roots:   # line them up side by side for this shot
            r.location.y = 0; B._upd(); lo, hi = mk.world_bbox(B.all_mesh(r))
            r.location.x += x - lo.x; B._upd(); x += (hi.x - lo.x) + gap
        ms = [o for r in roots for o in B.all_mesh(r)]
        lo, hi = mk.world_bbox(ms); c = (lo + hi) / 2
        s.render.resolution_x, s.render.resolution_y = W, H
        w = (hi.x - lo.x) * abs(math.cos(R(az))) + (hi.y - lo.y) * abs(math.sin(R(az))); h = hi.z - lo.z
        mk.only(ms + [g]); mk.cam_at((c.x, c.y, c.z), max(w, h * W / H * 1.1) * pad + .6, el=el, az=az); mk.shot(fname)
        for r, k in zip(roots, keep): r.location = k
        B._upd()
    # line-up rows
    up = ["Gorvax", "Infernoth", "Kongar", "Sailback", "Tyrantor", "Razorclaw", "Skyrend"]
    low = ["Fenrak", "Skarn", "Grimjaw", "Shellmaw"]
    frame_shot(list(builds), "01_kaiju_roster", el=12, az=-12, W=3200, H=900)
    frame_shot(up, "01a_upright_kaiju", el=8, az=-24, W=2600, H=1000)
    frame_shot(low, "01b_four_legged_kaiju", el=20, az=-24, W=2400, H=1000)
    frame_shot(up, "02a_upright_back", el=12, az=165, W=2600, H=1000)
    frame_shot(low, "02b_four_legged_back", el=20, az=160, W=2400, H=1000)
    for nm in ("Gorvax", "Infernoth", "Kongar", "Tyrantor"):
        frame_shot([nm], f"0{['Gorvax','Infernoth','Kongar','Tyrantor'].index(nm)+4}_{nm.lower()}", el=8, az=-55, W=1400, H=1200, pad=1.05)
    # Grimjaw crawl and stand side by side
    stand = B.assemble("GrimjawStand", SHEETS["Grimjaw"]["sheet"] | {"legs4": False}, "grimjaw", at=(0, 30, 0),
                       pose=dict(pitch=58, chest=8, neck=-10, head=4, jaw=34, tail=-10, tail_yaw=3,
                                 arm=((-40, -20, 0), (-60, 0, 0), (-20, 0, 0)), leg=((-10, -10, 0), (16, 0, 0), (0, 0, 0))))
    stand[0].rotation_euler.z = R(90)
    crawl = B.assemble("GrimjawCrawl", SHEETS["Grimjaw"]["sheet"], "grimjaw", at=(-7, 30, 0), pose=SHEETS["Grimjaw"]["pose"])
    crawl[0].rotation_euler.z = R(90); B._upd()
    builds["_st"] = stand; builds["_cr"] = crawl
    frame_shot(["_cr", "_st"], "03_grimjaw_two_poses", el=10, az=-24, W=2000, H=1100, gap=1.5)
    # hitboxes on Gorvax
    r, o = builds["Gorvax"]; hbs = B.hitbox_overlay(o)
    ms = B.all_mesh(r); lo, hi = mk.world_bbox(ms); c = (lo + hi) / 2
    s.render.resolution_x, s.render.resolution_y = 1400, 1200
    mk.only(ms + hbs + [g], show_hb=True); mk.cam_at(tuple(c), (hi.z - lo.z) * 1.15, el=8, az=-55); mk.shot("08_hitboxes")
    for hb in hbs: hb.hide_render = True
    # model-kit look: frame only vs frame + hide (Tyrantor)
    fr = B.assemble("TyFrame", SHEETS["Tyrantor"]["sheet"], "tyrantor", at=(0, -40, 0), pose=SHEETS["Tyrantor"]["pose"])
    fr[0].rotation_euler.z = R(90)
    full = B.assemble("TyFull", SHEETS["Tyrantor"]["sheet"], "tyrantor", at=(0, -33, 0), pose=SHEETS["Tyrantor"]["pose"])
    full[0].rotation_euler.z = R(90); B._upd()
    vis = [x for x in B.all_mesh(fr[0]) if not x.get("armor_of")] + B.all_mesh(full[0])
    lo, hi = mk.world_bbox(vis); c = (lo + hi) / 2
    s.render.resolution_x, s.render.resolution_y = 1800, 1000
    mk.only(vis + [g]); mk.cam_at(tuple(c), (hi.y - lo.y) * 1.1, el=10, az=-70); mk.shot("09_frame_and_hide")
    # contact sheets
    g.location.z = -400
    s.display.shading.background_color = mk.srgb("2b3754")
    B.contact_sheet(objs, ["head", "jaw", "horn", "crest"], "10_parts_heads", colw=1.7)
    B.contact_sheet(objs, ["neck", "chest", "hips", "back", "crystal"], "11_parts_body", colw=2.3)
    B.contact_sheet(objs, ["arm_up", "arm_lo", "hand"], "12_parts_arms", colw=1.5)
    B.contact_sheet(objs, ["thigh", "shin", "foot", "tail"], "13_parts_legs_tails", colw=1.4)


if __name__ == "__main__":
    main()
