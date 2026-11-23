# Part Maker shapes (Nov 22 2026): the box, wedge, taper and cylinder the Part Maker builds with, made in Blender with soft
# beveled edges (pro-3d rule: nothing in the real world has perfectly cut edges). Writes models/maker_shapes.js (window.MF_SHAPES).
# Unit size, in the sketch pad's space after glTF (y up): x and z from -0.5 to 0.5, y from 0 to 1, front = -z.
# In Blender (z up) that front is +Y, because glTF turns Blender +Y into -z.
# Run: python3 tools/blender/maker_shapes.py
import bpy, bmesh, os, base64, json, tempfile, math

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BEVEL = 0.035   # soft edge on a 1-unit shape; it shrinks with the shape when you make it thin


def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def block(top_y_front=1.0, top_scale=1.0):
    """Box, wedge or taper: 8 corners, the top ones moved."""
    bm = bmesh.new()
    v = []
    for zt in (0, 1):
        for (x, y) in ((-.5, .5), (.5, .5), (.5, -.5), (-.5, -.5)):   # y = +.5 is the front
            if zt:
                x, y = x * top_scale, y * top_scale
                z = top_y_front if y > 0 else 1.0
            else:
                z = 0.0
            v.append(bm.verts.new((x, y, z)))
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([v[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def cylinder():
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=.5, radius2=.5, depth=1.0)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, .5))
    return bm


def make(name, bm):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    mod = ob.modifiers.new('bevel', 'BEVEL'); mod.width = BEVEL; mod.segments = 2; mod.limit_method = 'ANGLE'; mod.angle_limit = math.radians(30)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    bpy.ops.object.modifier_apply(modifier='bevel')
    for p in me.polygons: p.use_smooth = True
    me.set_sharp_from_angle(angle=math.radians(40)) if hasattr(me, 'set_sharp_from_angle') else None
    return ob


out = {}
for name, fn in (('box', lambda: block()), ('wedge', lambda: block(top_y_front=.25)), ('taper', lambda: block(top_scale=.6)), ('cyl', cylinder)):
    clear()
    ob = make(name, fn())
    path = os.path.join(tempfile.gettempdir(), f'mk_{name}.glb')
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True)
    out[name] = base64.b64encode(open(path, 'rb').read()).decode()
    print(name, len(ob.data.polygons), 'faces')

with open(os.path.join(ROOT, 'models', 'maker_shapes.js'), 'w') as f:
    f.write('// made by tools/blender/maker_shapes.py: beveled Part Maker shapes (glb, base64)\nwindow.MF_SHAPES = ' + json.dumps(out) + ';\n')
print('wrote models/maker_shapes.js')
