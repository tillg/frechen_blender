"""Headless fingerprint of the Blender build, for the parity test.

blender -b --factory-startup --python tests/blender/snapshot.py -- out.json
blender -b frechenlehen.blend --python tests/blender/snapshot.py -- out.json --saved
Per object in collection "Haus": vertex/face counts, bounding box, unique material names,
rnd checksum, origin.
"""
import bpy, hashlib, json, sys
from mathutils import Vector
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = sys.argv[sys.argv.index("--") + 1]


G = {"__name__": "__main__"}          # one namespace for all scripts, as in the MCP rebuild


def run(script):
    exec(open(ROOT / "code" / script).read(), G)


def r5(x):
    return round(x, 5) + 0.0          # + 0.0 turns -0.0 into 0.0


def mesh_entry(ob):
    me = ob.data
    co = [ob.matrix_world @ v.co for v in me.vertices]
    bb = [r5(min(p[i] for p in co)) for i in range(3)] + [r5(max(p[i] for p in co)) for i in range(3)]
    rnd = me.attributes.get("rnd")
    chk = (hashlib.sha1(",".join(f"{d.value:.6f}" for d in rnd.data).encode()).hexdigest()[:16]
           if rnd else "none")
    return {"verts": len(me.vertices), "faces": len(me.polygons), "bbox": bb,
            "materials": sorted({m.name for m in me.materials if m}), "rnd": chk,
            "origin": [r5(c) for c in ob.location]}


def objects(coll):
    return {ob.name: mesh_entry(ob) for ob in coll.all_objects if ob.type == "MESH"}


def bbox_entry(ob):
    pts = [ob.matrix_world @ Vector(b) for b in ob.bound_box]
    return {"bbox": [r5(min(p[i] for p in pts)) for i in range(3)] + [r5(max(p[i] for p in pts)) for i in range(3)]}


if "--saved" not in sys.argv:          # --saved: fingerprint the opened .blend as it is
    for script in ("build_house.py", "paint.py", "windrose.py", "garden.py", "film.py"):
        run(script)
bpy.context.view_layer.update()
snap = objects(bpy.data.collections["Haus"])
snap.update(objects(bpy.data.collections["Garten"]))           # emitter cells = GA_Wiese faces
snap.update({ob.name: bbox_entry(ob) for ob in bpy.data.collections["Windrose"].objects})
snap["_shrubs"] = sum(ob.name.startswith("GA_Strauch") for ob in bpy.data.collections["Garten"].objects)
snap["_paint"] = {n: [r5(c) for c in bpy.data.materials[n].node_tree.nodes["Principled BSDF"]
                      .inputs["Base Color"].default_value]
                  for n in ("FL_Putz", "FL_Rahmen", "FL_Laden")}
snap["_room_lights"] = sorted([r5(c) for c in ob.location]
                              for ob in bpy.data.collections["Innenlicht"].objects)
Path(OUT).write_text(json.dumps(snap, indent=1, sort_keys=True))
