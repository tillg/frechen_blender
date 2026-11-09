"""The walkthrough route ("Rundgang"): orbit around the house, in through the east entrance and
the Windfang round the sofa to the Stube's seating corner (slow turn, pause at the sofa and Ofen) -> Essen, end of the table
(turn, pause) -> peek into the Speis -> Küche -> Großeltern: into their Bad (look into the shower,
then the WC, pausing at each), then turn at the wall beside the balcony door -> along the Flur to the back door (turn, pause) -> Bibliothek, back corner (turn, pause at the
piano) -> stairs -> OG: peeks into the first room on the right and the Waschküche -> Schlafen SE,
back corner (turn, pause at the Kamin), peek into its Bad -> peek into the NE room opposite ->
peeks into the SW room and the Bad at the end -> Yoga, back corner (turn) -> down the stairs, out
to the start point, turn to face the house, pause (closed route: the viewer can loop it).

Pure Python (no bpy), like house_core. build_tour() bakes ROUTE into smoothed per-frame camera
keys (x, y, z, yaw, pitch, lens) in model coordinates (z up; lens in mm, 36 mm sensor width).
Two consumers: film.py keys FL_Kamera_Rundgang with them, export_gltf.py writes them to the
viewer's .glb (scene.extras.tour), where web/src/tour.js plays them.
"""
import math

from house_core import HOUSE_C, Z_OG

FPS = 25
EYE = 1.60                  # camera height above the floor: the eyes of the person walking through
WALK, STAIR_SPEED = 1.3, 0.8
TURN = 30.0                 # "slow turn": every turn and head swing, in degrees per second
PAUSE = 2.0                 # the pauses during a turn, in seconds
L, R = 1, -1                # turn direction: left = counter-clockwise seen from above
OG = Z_OG + EYE


# ---------------------------------------------------------------- route
def orbit(a0, a1, secs, center=HOUSE_C, rx=20.0, ry=18.0, z=EYE, look=(*HOUSE_C, 3.0)):
    return ("orbit", a0, a1, secs, center, rx, ry, z, look)


def turn(target, side=None):
    """Turn on the spot at TURN until facing target (x, y) or (x, y, z); side L/R, else the shorter way."""
    return ("turn", target, side)


def peek(left, right):
    """Head into a room: look along its left wall, then swing slowly right along its right wall."""
    return [turn(left), turn(right, R)]


START = (HOUSE_C[0] + 20.0 * math.cos(math.radians(-45)),      # the orbit's start pose
         HOUSE_C[1] + 18.0 * math.sin(math.radians(-45)))

ROUTE = [
    orbit(-45, -360, 24),
    ("path", [(27.44, 6.44), (18.0, 6.98), (14.9, 6.98), (13.6, 7.10), (12.3, 7.20), (11.4, 7.20),
              (11.4, 6.10), (11.75, 5.2), (13.1, 4.9), (13.55, 3.6), (13.1, 2.2)], EYE, WALK),  # Stube: round the sofa
    turn((10.0, 5.2), L), ("hold", PAUSE),                                # the sofa and the Ofen
    turn((8.8, 1.74), L),                                                 # passage to the Essen
    ("path", [(13.1, 2.2), (11.2, 1.9), (9.6, 2.3), (8.3, 2.75), (3.9, 2.75), (3.35, 1.6)], EYE, WALK),  # end of the table
    turn((8.0, 3.3), L), ("hold", PAUSE),                                 # passage to the Stube + Küche
    ("path", [(3.35, 1.6), (3.8, 2.72), (5.0, 2.7), (5.95, 2.72), (6.05, 3.6), (5.95, 4.79)], EYE, WALK),
    turn((3.0, 4.79)),                                                    # down the Speis aisle
    ("path", [(5.95, 4.79), (6.55, 4.6), (6.55, 6.9), (5.3, 7.25), (4.87, 8.0),   # Küche door to the Flur
              (4.87, 9.25), (3.45, 9.8), (2.5, 10.3), (1.2, 10.35)], EYE, WALK),   # Großeltern: into their Bad
    turn((0.6, 12.2, 1.2)), ("hold", PAUSE),                              # the walk-in shower
    turn((0.79, 8.9, 0.6), L), ("hold", PAUSE),                           # the WC in the niche
    ("path", [(1.2, 10.35), (2.5, 10.6), (3.3, 12.0)], EYE, WALK),        # left of the balcony door
    turn((4.87, 8.75), L),                                                # round to the door
    ("path", [(3.3, 12.0), (3.45, 10.0), (4.87, 9.2), (4.87, 8.0), (3.0, 7.95), (0.95, 7.92)],
     EYE, WALK),                                                          # right, to the back door
    turn((14.0, 7.92), L), ("hold", PAUSE),                               # straight down the Flur
    ("path", [(0.95, 7.92), (2.5, 7.95), (4.5, 7.9), (7.0, 7.8), (7.8, 8.3), (7.85, 9.6), (9.2, 9.95),
              (10.5, 10.45), (12.9, 10.75), (14.0, 11.95)], EYE, WALK),   # Bibliothek: back left corner
    turn((8.6, 11.2), L), ("hold", PAUSE),                                # the piano
    turn((14.05, 8.73), L),                                               # door to the Flur/Windfang
    ("path", [(14.0, 11.95), (14.05, 9.3), (14.0, 8.4), (13.6, 7.4), (12.3, 7.3), (11.8, 7.5),
              (11.6, 8.0), (11.19, 8.0)], EYE, WALK),
    ("stair", (11.19, 8.0, EYE), (7.62, 8.0, OG), STAIR_SPEED),
    ("path", [(7.62, 8.0), (7.62, 8.72)], OG, WALK),                      # first room on the right
    *peek((6.5, 12.2), (8.8, 10.4)),                       # left: past the open leaf
    ("path", [(7.62, 8.72), (7.45, 8.2), (7.5, 7.0), (7.66, 6.3)], OG, WALK),   # Waschküche
    *peek((8.3, 4.5), (5.9, 4.5)),
    ("path", [(7.66, 6.3), (7.9, 6.85), (11.1, 6.85), (11.1, 6.2), (11.2, 5.2), (13.3, 4.6), (14.0, 3.9),
              (14.0, 1.5), (13.95, 0.9)], OG, WALK),                      # Schlafen SE: past the bed, back corner
    turn((9.12, 3.44), L), ("hold", PAUSE),                               # the Kamin
    turn((8.65, 2.1), L),                                                 # the Bad door
    ("path", [(13.95, 0.9), (11.4, 0.75), (10.4, 0.95), (8.8, 2.12)], OG, WALK),
    *peek((7.3, 0.7), (7.3, 2.35)),                                       # its Bad
    ("path", [(8.8, 2.12), (9.9, 2.6), (10.6, 3.6), (10.75, 4.6), (11.2, 5.3), (11.1, 6.2), (11.4, 7.3),
              (12.74, 7.9), (12.74, 9.7)], OG, WALK),                     # the NE room opposite
    *peek((10.2, 11.6, Z_OG + 0.5), (14.4, 10.2)),         # in to the end of the open leaf; the beds
    ("path", [(12.74, 9.7), (12.6, 7.7), (11.1, 7.15), (4.45, 7.15), (4.45, 6.3)], OG, WALK),  # back left in the Flur
    *peek((5.14, 4.5), (3.0, 0.7)),                        # right: past the open leaf
    ("path", [(4.45, 6.3), (4.2, 7.4), (3.4, 8.07), (2.8, 8.07)], OG, WALK),    # the Bad at the end
    *peek((1.5, 6.85), (1.5, 8.3)),
    ("path", [(2.8, 8.07), (3.66, 8.3), (3.66, 9.2), (5.6, 12.0)], OG, WALK),   # Yoga: back right corner
    turn((3.66, 8.9), L),                                                 # round to the door
    ("path", [(5.6, 12.0), (3.66, 9.2), (3.66, 8.3), (4.2, 7.6), (6.9, 7.6), (7.25, 8.0), (7.62, 8.0)],
     OG, WALK),
    ("stair", (7.62, 8.0, OG), (11.19, 8.0, EYE), STAIR_SPEED),
    ("path", [(11.19, 8.0), (11.6, 8.0), (11.8, 7.5), (12.3, 7.2), (13.6, 7.10), (14.9, 6.98), (17.0, 6.6),
              START], EYE, WALK),                                         # out to the start point
    turn((*HOUSE_C, 3.0), L), ("hold", PAUSE),                            # face the house
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


def turn_frames(last, yaw1, pitch1, side=None):
    """Frames turning on the spot from the pose last to yaw1 at TURN (side L/R, else the shorter
    way), the pitch following linearly."""
    x, y, z, yaw0, pitch0, lens = last
    d = math.remainder(yaw1 - yaw0, 2 * math.pi)
    if side and d * side < 0:
        d += side * 2 * math.pi
    n = round(abs(math.degrees(d)) / TURN * FPS)
    return [(x, y, z, yaw0 + d * i / n, pitch0 + (pitch1 - pitch0) * i / n, lens) for i in range(1, n + 1)]


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
            walk = []
            for i, p in enumerate(smp):
                q = smp[min(i + look_ahead, len(smp) - 1)]
                if q == p:
                    yaw, pitch = walk[-1][3], 0.0
                else:
                    yaw = heading(q[0] - p[0], q[1] - p[1])
                    pitch = math.atan2(q[2] - p[2], math.dist(p[:2], q[:2])) * 0.6
                # wide inside, zoom in again between the entrance and 18 m east
                lens = lens_out if p[0] > 18 else (lens_in if p[0] < 15.5 or p[2] > 2 else
                                                   lens_in + (lens_out - lens_in) * (p[0] - 15.5) / 2.5)
                walk.append((p[0], p[1], p[2], yaw, pitch, lens))
            if frames:                                   # face the way before walking off
                frames += turn_frames(frames[-1], walk[0][3], walk[0][4])
            frames += walk
        elif kind == "turn":
            _, (tx, ty, *tz), side = seg
            x, y, z = frames[-1][:3]
            pitch = math.atan2(tz[0] - z, math.dist((x, y), (tx, ty))) if tz else -0.03
            frames += turn_frames(frames[-1], heading(tx - x, ty - y), pitch, side)
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
