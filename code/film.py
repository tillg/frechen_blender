"""Walkthrough film: keys the camera "FL_Kamera_Rundgang" with the route of tour.py (baked
per-frame keys) and creates point lights in the collection "Innenlicht". Neither touches the
"Haus" collection. Re-running replaces both.
Run inside Blender: exec(open(".../code/film.py").read())
"""
import bpy, importlib, math, sys

sys.path.insert(0, "/Users/tgartner/git/frechen_blender/code")
import house_core; importlib.reload(house_core)        # pick up core edits in a long session
import tour; importlib.reload(tour)                    # the route (after the core it imports)
from house_core import ROOM_LIGHT_H, ROOM_LIGHTS


# ---------------------------------------------------------------- interior lights
# positions: ROOM_LIGHTS in house_core.py


def build_lights():
    c = bpy.data.collections.get("Innenlicht")
    if c:
        for ob in list(c.objects):
            bpy.data.objects.remove(ob)
    else:
        c = bpy.data.collections.new("Innenlicht")
        bpy.context.scene.collection.children.link(c)
    for i, (x, y, z) in enumerate(ROOM_LIGHTS):
        ld = bpy.data.lights.new(f"Innenlicht_{i:02d}", "POINT")
        ld.energy, ld.color, ld.shadow_soft_size = 120, (1.0, 0.9, 0.78), 0.3   # 250 W washed out
        ld.use_shadow = False       # fill light only; 23 shadow casters overflowed the shadow pool -> flicker
        ob = bpy.data.objects.new(ld.name, ld)
        ob.location = (x, y, z + ROOM_LIGHT_H)
        c.objects.link(ob)


# ---------------------------------------------------------------- camera
def build_camera():
    sc = bpy.context.scene
    old = bpy.data.objects.get("FL_Kamera_Rundgang")
    if old:
        bpy.data.objects.remove(old)
    cd = bpy.data.cameras.new("FL_Kamera_Rundgang")
    cd.clip_start, cd.clip_end, cd.sensor_width = 0.05, 300, 36
    cam = bpy.data.objects.new("FL_Kamera_Rundgang", cd)
    sc.collection.objects.link(cam)

    keys = tour.build_tour()
    cam.animation_data_create()
    act = bpy.data.actions.new("FL_Rundgang")
    cam.animation_data.action = act
    # write keys via keyframe_insert (robust across the Blender 5 layered-action API)
    for f, (x, y, z, yaw, pitch, lens) in enumerate(keys, 1):
        cam.location = (x, y, z)
        cam.rotation_euler = (math.pi / 2 + pitch, 0.0, yaw - math.pi / 2)
        cd.lens = lens
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
        cd.keyframe_insert("lens", frame=f)
    sc.frame_start, sc.frame_end = 1, len(keys)
    sc.render.fps = tour.FPS
    sc.camera = cam
    return len(keys)


def open_entrance_door():
    """Film only: swing the entrance door leaf (pivot = hinge, from build_house.py) inwards."""
    old = bpy.data.objects.get("Film_Haustuer_offen")      # box stand-in of earlier versions
    if old:
        bpy.data.objects.remove(old)
    bpy.data.objects["EG_Haustuer"].rotation_euler.z = math.radians(90)


def main():
    build_lights()
    open_entrance_door()
    n = build_camera()
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.view_settings.view_transform, sc.view_settings.look = "AgX", "AgX - Punchy"   # richer colours
    sc.eevee.taa_render_samples = 16
    sc.eevee.shadow_pool_size = "1024"
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1280, 720, 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = "/Users/tgartner/git/frechen_blender/tmp/film/frame_"
    return n


N_FRAMES = main()
