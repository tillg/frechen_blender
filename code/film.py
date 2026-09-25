"""Walkthrough camera: orbit around the house, enter via the east entrance (Windfang),
Stube -> Küche/Essen -> NW room (end of the corridor, right) -> Musikzimmer -> Arbeitszimmer
-> Windfang -> stairs -> OG Flur -> Schlafen (SE, peek into its Bad) -> peek into the NW Bad
-> Schlafen/Yoga (NW).

Creates camera "FL_Kamera_Rundgang" (baked per-frame keys) and point lights in the
collection "Innenlicht". Neither touches the "Haus" collection. Re-running replaces both.
Run inside Blender: exec(open(".../code/film.py").read())
"""
import bpy, math

FPS = 25
EYE = 1.65                  # eye height above floor
Z_OG = 2.70
WALK, STAIR_SPEED = 1.3, 0.8
HOUSE_C = (7.44, 6.44)


# ---------------------------------------------------------------- route
def orbit(a0, a1, secs, center=(7.44, 6.44), rx=20.0, ry=18.0, z=EYE, look=(7.44, 6.44, 3.0)):
    return ("orbit", a0, a1, secs, center, rx, ry, z, look)


ROUTE = [
    orbit(-45, -360, 24),
    ("path", [(27.44, 6.44), (18.0, 6.98), (14.9, 6.98), (13.6, 7.10), (12.3, 7.20),
              (11.4, 7.20), (11.4, 6.10), (11.6, 4.0)], EYE, WALK),
    ("look", [(11.8, 0.0), (15.0, 3.0), (9.8, 5.0), (8.8, 1.8)], 2.2),
    ("path", [(11.6, 4.0), (10.0, 2.65), (8.8, 2.65), (6.2, 2.65)], EYE, WALK),  # past the table
    ("look", [(3.0, 1.5), (6.5, 5.5)], 2.2),
    ("path", [(6.2, 2.65), (7.5, 4.5), (7.5, 6.1), (7.5, 7.0), (4.87, 7.2), (4.87, 8.5),
              (4.87, 9.6), (4.3, 10.6)], EYE, WALK),                      # NW room
    ("look", [(3.0, 12.4), (2.8, 9.2), (6.0, 11.5)], 2.2),
    ("path", [(4.3, 10.6), (4.87, 9.4), (4.87, 7.4), (7.75, 7.3), (7.8, 8.2), (7.85, 9.6),
              (8.6, 10.6)], EYE, WALK),                                   # Musikzimmer
    ("look", [(7.0, 12.4), (9.2, 9.0), (10.5, 11.5)], 2.2),
    ("path", [(8.6, 10.6), (10.3, 10.7), (11.2, 10.75), (12.4, 10.6)], EYE, WALK),  # Arbeitszimmer
    ("look", [(13.0, 12.4), (14.3, 10.8), (12.5, 9.2)], 2.2),
    ("path", [(12.4, 10.6), (13.9, 9.6), (14.0, 8.9), (14.0, 8.2), (13.6, 7.3), (12.3, 7.2),
              (11.8, 7.5), (11.6, 8.0), (11.19, 8.0)], EYE, WALK),       # Windfang -> stair
    ("stair", (11.19, 8.0, EYE), (7.62, 8.0, Z_OG + EYE), STAIR_SPEED),
    ("path", [(7.62, 8.0), (7.0, 8.0), (7.0, 7.1), (11.1, 7.1), (11.1, 6.2), (12.0, 3.8)],
     Z_OG + EYE, WALK),
    ("look", [(10.27, 0.0), (15.0, 4.6)], 2.2),
    ("path", [(12.0, 3.8), (9.6, 2.2)], Z_OG + EYE, WALK),              # to the en-suite Bad door
    ("look", [(6.0, 1.8)], 2.2),                                        # peek into the Bad
    ("path", [(9.6, 2.2), (10.9, 3.4), (11.1, 6.2), (11.1, 7.1), (3.3, 7.3), (3.3, 8.07)], Z_OG + EYE, WALK),
    ("look", [(1.0, 7.3), (1.0, 8.3)], 2.2),                            # peek into the NW Bad
    ("path", [(3.3, 8.07), (3.66, 8.3), (3.66, 8.7), (4.0, 10.6)], Z_OG + EYE, WALK),
    ("look", [(4.33, 13.0), (0.0, 9.5), (7.0, 13.0)], 2.2),
    ("hold", 1.5),
]


def polyline_samples(pts, speed):
    """Points along polyline at constant speed, one per frame."""
    segs = list(zip(pts[:-1], pts[1:]))
    lens = [math.dist(a, b) for a, b in segs]
    total = sum(lens)
    n = max(2, int(total / speed * FPS))
    out = []
    for i in range(n + 1):
        s, k = total * i / n, 0
        while k < len(lens) - 1 and s > lens[k]:
            s -= lens[k]; k += 1
        (ax, ay, *az), (bx, by, *bz) = segs[k]
        t = s / lens[k] if lens[k] else 0
        p = [ax + (bx - ax) * t, ay + (by - ay) * t]
        if az:
            p.append(az[0] + (bz[0] - az[0]) * t)
        out.append(p)
    return out


def heading(dx, dy):
    return math.atan2(dy, dx)


def build_frames():
    frames = []              # (x, y, z, yaw, pitch, lens)
    lens_in, lens_out = 16.0, 24.0
    for seg in ROUTE:
        kind = seg[0]
        if kind == "orbit":
            _, a0, a1, secs, (cx, cy), rx, ry, z, (lx, ly, lz) = seg
            n = int(secs * FPS)
            for i in range(n + 1):
                a = math.radians(a0 + (a1 - a0) * i / n)
                x, y = cx + rx * math.cos(a), cy + ry * math.sin(a)
                d = math.dist((x, y), (lx, ly))
                frames.append((x, y, z, heading(lx - x, ly - y), math.atan2(lz - z, d), lens_out))
        elif kind in ("path", "stair"):
            if kind == "path":
                _, pts, z, speed = seg
                pts3 = [(x, y, z) for x, y in pts]
            else:
                _, a, b, speed = seg
                pts3 = [a, b]
            smp = polyline_samples(pts3, speed)
            look_ahead = int(1.8 / speed * FPS)
            for i, p in enumerate(smp):
                q = smp[min(i + look_ahead, len(smp) - 1)]
                if q == p:
                    yaw, pitch = frames[-1][3], 0.0
                else:
                    yaw = heading(q[0] - p[0], q[1] - p[1])
                    pitch = math.atan2(q[2] - p[2], math.dist(p[:2], q[:2])) * 0.6
                # zoom out while approaching the entrance, stay wide inside
                lens = lens_out if p[0] > 18 else (lens_in if p[0] < 15.5 or p[2] > 2 else
                                                   lens_in + (lens_out - lens_in) * (p[0] - 15.5) / 2.5)
                if frames and frames[-1][5] == lens_in:
                    lens = lens_in
                frames.append((p[0], p[1], p[2], yaw, pitch, lens))
        elif kind == "look":
            _, targets, secs = seg
            x, y, z, yaw0, _, lens = frames[-1]
            for tx, ty in targets:
                yaw1 = heading(tx - x, ty - y)
                while yaw1 - yaw0 > math.pi: yaw1 -= 2 * math.pi
                while yaw1 - yaw0 < -math.pi: yaw1 += 2 * math.pi
                n = int(secs * FPS)
                for i in range(1, n + 1):
                    t = i / n
                    t = t * t * (3 - 2 * t)            # ease in/out
                    frames.append((x, y, z, yaw0 + (yaw1 - yaw0) * t, -0.03, lens))
                yaw0 = yaw1
        elif kind == "hold":
            frames += [frames[-1]] * int(seg[1] * FPS)
    return frames


def unwrap(vals):
    out = [vals[0]]
    for v in vals[1:]:
        while v - out[-1] > math.pi: v -= 2 * math.pi
        while v - out[-1] < -math.pi: v += 2 * math.pi
        out.append(v)
    return out


def smooth(vals, w):
    n, h = len(vals), w // 2
    return [sum(vals[max(0, i - h):min(n, i + h + 1)]) / (min(n, i + h + 1) - max(0, i - h))
            for i in range(n)]


# ---------------------------------------------------------------- interior lights
ROOM_LIGHTS = [  # (x, y, floor z)
    (13.5, 7.5, 0), (5.0, 7.4, 0), (10.0, 7.0, 0), (11.7, 3.2, 0), (7.0, 4.5, 0), (5.5, 1.8, 0),
    (13.0, 10.7, 0), (10.2, 10.7, 0), (4.3, 10.7, 0), (7.6, 10.7, 0), (1.3, 11.3, 0),
    (1.3, 7.5, 0), (4.0, 4.3, 0),
    (5.0, 7.4, Z_OG), (10.0, 7.0, Z_OG), (12.0, 3.0, Z_OG), (4.0, 3.0, Z_OG), (7.0, 4.3, Z_OG),
    (7.0, 1.5, Z_OG), (3.0, 10.7, Z_OG), (7.6, 10.7, Z_OG), (11.8, 10.7, Z_OG), (1.4, 7.4, Z_OG),
]


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
        ob.location = (x, y, z + 2.1)
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

    fr = build_frames()
    xs, ys, zs = (smooth([f[k] for f in fr], 13) for k in range(3))
    yaws = smooth(unwrap([f[3] for f in fr]), 21)
    pitches = smooth([f[4] for f in fr], 21)
    lenses = smooth([f[5] for f in fr], 25)

    cam.animation_data_create()
    act = bpy.data.actions.new("FL_Rundgang")
    cam.animation_data.action = act
    # write keys via keyframe_insert (robust across the Blender 5 layered-action API)
    for i in range(len(fr)):
        f = i + 1
        cam.location = (xs[i], ys[i], zs[i])
        cam.rotation_euler = (math.pi / 2 + pitches[i], 0.0, yaws[i] - math.pi / 2)
        cd.lens = lenses[i]
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
        cd.keyframe_insert("lens", frame=f)
    sc.frame_start, sc.frame_end = 1, len(fr)
    sc.render.fps = FPS
    sc.camera = cam
    return len(fr)


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
