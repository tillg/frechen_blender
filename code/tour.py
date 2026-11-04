"""The walkthrough route ("Rundgang"): orbit around the house, enter via the east entrance
(Windfang), Stube -> Küche/Essen -> NW room (end of the corridor, right) -> Musikzimmer ->
Arbeitszimmer -> Windfang -> stairs -> OG Flur -> Schlafen (SE, peek into its Bad) -> peek into
the NW Bad -> Schlafen/Yoga (NW) -> down the stairs, out of the entrance, step back facing the
house and orbit to the start pose (closed route: the viewer can loop it).

Pure Python (no bpy), like house_core. build_tour() bakes ROUTE into smoothed per-frame camera
keys (x, y, z, yaw, pitch, lens) in model coordinates (z up; lens in mm, 36 mm sensor width).
Two consumers: film.py keys FL_Kamera_Rundgang with them, export_gltf.py writes them to the
viewer's .glb (scene.extras.tour), where web/src/tour.js plays them.
"""
import math

from house_core import HOUSE_C, Z_OG

FPS = 25
EYE = 1.65                  # eye height above floor
WALK, STAIR_SPEED = 1.3, 0.8


# ---------------------------------------------------------------- route
def orbit(a0, a1, secs, center=HOUSE_C, rx=20.0, ry=18.0, z=EYE, look=(*HOUSE_C, 3.0)):
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
    # back to the start: down the stairs, out through the Windfang, turn, orbit to -45°
    ("path", [(4.0, 10.6), (3.66, 8.7), (3.66, 8.3), (3.3, 8.07), (3.3, 7.3), (7.0, 7.2), (7.0, 8.0),
              (7.62, 8.0)], Z_OG + EYE, WALK),
    ("stair", (7.62, 8.0, Z_OG + EYE), (11.19, 8.0, EYE), STAIR_SPEED),
    ("path", [(11.19, 8.0), (11.6, 8.0), (11.8, 7.5), (12.3, 7.2), (13.6, 7.10), (14.9, 6.98),
              (17.0, 6.98)], EYE, WALK),
    ("look", [HOUSE_C], 2.2),                                           # turn round to the house
    ("path", [(17.0, 6.98), (27.44, 6.44)], EYE, WALK, (*HOUSE_C, 3.0)),   # step back, eyes on it
    orbit(0, -45, 24 * 45 / 315),                                       # same pace as the first orbit
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
                _, pts, z, speed, *look_at = seg          # optional fixed look-at point (x, y, z)
                pts3 = [(x, y, z) for x, y in pts]
            else:
                _, a, b, speed = seg
                pts3, look_at = [a, b], None
            smp = polyline_samples(pts3, speed)
            look_ahead = int(1.8 / speed * FPS)
            for i, p in enumerate(smp):
                q = smp[min(i + look_ahead, len(smp) - 1)]
                if look_at:
                    lx, ly, lz = look_at[0]
                    yaw = heading(lx - p[0], ly - p[1])
                    pitch = math.atan2(lz - p[2], math.dist(p[:2], (lx, ly)))
                elif q == p:
                    yaw, pitch = frames[-1][3], 0.0
                else:
                    yaw = heading(q[0] - p[0], q[1] - p[1])
                    pitch = math.atan2(q[2] - p[2], math.dist(p[:2], q[:2])) * 0.6
                # wide inside, zoom in again between the entrance and 18 m east
                lens = lens_out if p[0] > 18 else (lens_in if p[0] < 15.5 or p[2] > 2 else
                                                   lens_in + (lens_out - lens_in) * (p[0] - 15.5) / 2.5)
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


def smooth(vals, w, closed=False):
    """Moving average over w frames; closed: the last value repeats the first (+ an offset such as
    a full turn of yaw), so the window wraps around and the ends stay equal."""
    n, h = len(vals), w // 2
    if closed:
        d = vals[-1] - vals[0]
        ext = [v - d for v in vals[-h - 1:-1]] + vals + [v + d for v in vals[1:h + 1]]
        return [sum(ext[i:i + w]) / w for i in range(n)]
    return [sum(vals[max(0, i - h):min(n, i + h + 1)]) / (min(n, i + h + 1) - max(0, i - h))
            for i in range(n)]


def build_tour():
    """Smoothed camera keys, one per frame at FPS: [(x, y, z, yaw, pitch, lens), ...]. A route
    that ends where it starts is smoothed cyclically, so it loops without a jump."""
    fr = build_frames()
    c = math.dist(fr[0][:3], fr[-1][:3]) < 1e-6
    xs, ys, zs = (smooth([f[k] for f in fr], 13, c) for k in range(3))
    yaws = smooth(unwrap([f[3] for f in fr]), 21, c)
    pitches = smooth([f[4] for f in fr], 21, c)
    lenses = smooth([f[5] for f in fr], 25, c)
    return list(zip(xs, ys, zs, yaws, pitches, lenses))
