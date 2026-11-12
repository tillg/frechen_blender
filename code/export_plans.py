"""Frechenlehen – the plan backend: the Blueprint as six 2D plan sheets (SVG) for the architect:
Grundriss EG / OG and Ansicht Nord / Ost / Süd / West, each A3 landscape at 1:100, sized in mm (printed
at 100 %, 1 m in the model measures 10 mm).

    python3 code/export_plans.py plans/
    python3 code/export_plans.py plans/ --generated     # GitHub Pages: the Berlin time in the title block

Standard library only, no Blender. Like build_house.py and export_gltf.py it only draws: every fact
about the house comes from the core (ADR-001-XEWL); this file knows cut heights, line weights, the sheet
layout and the dimension notation. The same model always gives byte-identical files: no date (the
title block names the model state, a hash of the geometry), numbers with fixed decimals, elements in
a stable order. Only --generated adds a date, for the sheets GitHub Pages publishes.
"""
import bisect, datetime, hashlib, math, sys, zoneinfo
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
import house_core, mesh_ops  # noqa: E402

PAGE_W, PAGE_H = 420, 297                     # A3 landscape, mm
S = 10                                        # 1:100: mm on paper per m in the model
FONT = "Helvetica, Arial, sans-serif"
CUT = {"EG": 1.80, "OG": 1.55}               # Schnitthöhe above the floor: above every sill, below every head
FLOOR = {"EG": 0.0, "OG": house_core.Z_OG}
CEIL = {"EG": house_core.Z_EG_TOP, "OG": house_core.Z_OG_TOP}
ROOM_CUT = {"EG": 2.19, "OG": 2.15}          # room regions: above every lintel, below the annex ceiling (2.27)
SHEETS = (("eg", "Grundriss EG"), ("og", "Grundriss OG"), ("nord", "Ansicht Nord"),
          ("ost", "Ansicht Ost"), ("sued", "Ansicht Süd"), ("west", "Ansicht West"))


def num(v):
    """A coordinate on the sheet: two decimals, never "-0.00"."""
    s = "%.2f" % v
    return "0.00" if s == "-0.00" else s


def model_state(bp):
    """Short hash of what the sheets are drawn from (the Blueprint geometry, doors, rooms, object
    classes and the cut heights): names the model a sheet came from, without a date. Only lists,
    dicts and tuples go in, so it does not depend on PYTHONHASHSEED."""
    h = hashlib.sha256()
    for k in sorted(bp.geo):
        g = bp.geo[k]
        h.update(repr((k, g["v"], g["f"], g["m"])).encode())
    h.update(repr((bp.doors, bp.plan_rooms, bp.plan, bp.stairs, CUT, ROOM_CUT, FLOOR, CEIL)).encode())
    return h.hexdigest()[:12]


# ---------------------------------------------------------------- 2D geometry
def bbox(pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), max(xs), min(ys), max(ys)


def inside(loops, x, y):
    """Even-odd point in polygon over all loops of one shape."""
    c = False
    for L in loops:
        for i in range(len(L)):
            (ax, ay), (bx, by) = L[i - 1], L[i]
            if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
                c = not c
    return c


def slice_faces(V, F, h):
    """Segments where the faces F (vertex index lists into V) cross the plane z = h."""
    segs = []
    for f in F:
        pts = []
        for i in range(len(f)):
            a, b = V[f[i - 1]], V[f[i]]
            if (a[2] - h) * (b[2] - h) < 0:
                s = (h - a[2]) / (b[2] - a[2])
                pts.append((a[0] + s * (b[0] - a[0]), a[1] + s * (b[1] - a[1])))
        pts.sort()                                    # along the cut line: a concave face gives pairs
        segs += [(pts[k], pts[k + 1]) for k in range(0, len(pts) - 1, 2)]
    return segs


def loops(segs):
    """Chain segments into loops (an open chain stays open)."""
    K = lambda p: (round(p[0], 6), round(p[1], 6))
    at = {}
    for i, (p, q) in enumerate(segs):
        at.setdefault(K(p), []).append(i)
        at.setdefault(K(q), []).append(i)
    used, out = [False] * len(segs), []
    for i in range(len(segs)):
        if used[i]:
            continue
        used[i] = True
        p, q = segs[i]
        loop, start, cur = [p, q], K(p), K(q)
        while cur != start:
            j = next((j for j in at[cur] if not used[j]), None)
            if j is None:
                break
            used[j] = True
            a, b = segs[j]
            r = b if K(a) == cur else a
            loop.append(r)
            cur = K(r)
        if cur == start:
            loop.pop()
        out.append(loop)
    return out


def boundary(shapes, d=1e-4, G=0.5):
    """Outline of the union of shapes (each a list of loops). Every edge is split where other edges
    touch or cross it; a piece stays only where one side is inside the union and the other is not, so
    abutting or overlapping shapes leave no seam. Returns [(shape index, p, q)] in input order."""
    E, boxes = [], []
    for k, S_ in enumerate(shapes):
        boxes.append(bbox([p for L in S_ for p in L]))
        for L in S_:
            for i in range(len(L)):
                p, q = L[i - 1], L[i]
                if abs(q[0] - p[0]) + abs(q[1] - p[1]) > 1e-7:
                    E.append((k, p, q))
    cells = lambda b: [(i, j) for i in range(math.floor(b[0] / G), math.floor(b[1] / G) + 1)
                       for j in range(math.floor(b[2] / G), math.floor(b[3] / G) + 1)]
    eb, buckets, sb = [], {}, {}
    for n, (k, p, q) in enumerate(E):
        eb.append(cells(bbox((p, q))))
        for c in eb[-1]:
            buckets.setdefault(c, []).append(n)
    for k, b in enumerate(boxes):
        for c in cells(b):
            sb.setdefault(c, []).append(k)

    def in_union(x, y):
        for k in sb.get((math.floor(x / G), math.floor(y / G)), ()):
            b = boxes[k]
            if b[0] <= x <= b[1] and b[2] <= y <= b[3] and inside(shapes[k], x, y):
                return True
        return False

    out, done = [], set()
    for n, (k, p, q) in enumerate(E):
        rx, ry = q[0] - p[0], q[1] - p[1]
        rr = rx * rx + ry * ry
        ts = {0.0, 1.0}
        for m in sorted({m for c in eb[n] for m in buckets[c]} - {n}):
            a, b = E[m][1:]
            sx, sy = b[0] - a[0], b[1] - a[1]
            wx, wy = a[0] - p[0], a[1] - p[1]
            den = rx * sy - ry * sx
            if abs(den) < 1e-12 * math.sqrt(rr * (sx * sx + sy * sy)):         # parallel
                if abs(wx * ry - wy * rx) < 1e-9 * math.sqrt(rr):                 # collinear: its end points
                    for e in (a, b):
                        t = ((e[0] - p[0]) * rx + (e[1] - p[1]) * ry) / rr
                        if 0 < t < 1:
                            ts.add(t)
                continue
            t, u = (wx * sy - wy * sx) / den, (wx * ry - wy * rx) / den
            if 1e-9 < t < 1 - 1e-9 and -1e-9 <= u <= 1 + 1e-9:
                ts.add(t)
        ts = sorted(ts)
        L = math.sqrt(rr)
        nx, ny = -ry / L * d, rx / L * d
        run = None
        for s, e in zip(ts, ts[1:]):
            if (e - s) * L < 1e-7:
                continue
            P0, P1 = (p[0] + s * rx, p[1] + s * ry), (p[0] + e * rx, p[1] + e * ry)
            key = tuple(sorted(((round(P0[0], 5), round(P0[1], 5)), (round(P1[0], 5), round(P1[1], 5)))))
            mx, my = (P0[0] + P1[0]) / 2, (P0[1] + P1[1]) / 2
            keep = key not in done and in_union(mx + nx, my + ny) != in_union(mx - nx, my - ny)
            done.add(key)
            if keep and run:
                run[1] = P1
            elif keep:
                run = [P0, P1]
            elif run:
                out.append((k, run[0], run[1]))
                run = None
        if run:
            out.append((k, run[0], run[1]))
    return out


# ---------------------------------------------------------------- Grundriss: the section
def is_wall(bp, obj, mat):
    pl = bp.plan
    return (obj.endswith(pl["wall_suffix"]) or obj in pl["wall_objects"]) and mat == pl["wall_mat"]


def plan_objects(bp, st):
    """What a Grundriss shows: the storey and its extras (balconies), without loose furniture, floors
    and ceilings."""
    pl = bp.plan
    return lambda c, o: ((c == st or c in pl["extra_collections"] or o in pl["extra_objects"]) and o not in bp.furniture
                         and o not in pl["stair_objects"] and not any(w in o for w in pl["skip_words"]))


def in_leaf(bp, st, pts):
    """Whether the points (x, y[, z]) all lie in the box of one of the storey's door leaves as built:
    the plan draws every door with the conventional 90 deg symbol instead (door_swings)."""
    for d in bp.doors:
        (x0, y0), (x1, y1) = d["leaf"]
        if d["c"] == st and all(x0 - 1e-6 <= p[0] <= x1 + 1e-6 and y0 - 1e-6 <= p[1] <= y1 + 1e-6 for p in pts):
            return True
    return False


def section(bp, st):
    """The storey cut at its cut height: wall loops (hatched), their union outline (heavy) and the
    loops of the other cut parts (thin)."""
    h, keep = FLOOR[st] + CUT[st], plan_objects(bp, st)
    walls, cut = [], []
    for (c, o) in sorted(bp.geo):
        if not keep(c, o):
            continue
        g = bp.geo[(c, o)]
        for first, n in bp.parts[(c, o)]:
            segs = slice_faces(g["v"], g["f"][first:first + n], h)
            if segs and not in_leaf(bp, st, [p for s_ in segs for p in s_]):
                (walls if is_wall(bp, o, g["m"][first]) else cut).append((o, loops(segs)))
    outline = [(p, q) for _, p, q in boundary([L for _, L in walls])]
    return {"h": h, "walls": walls, "cut": cut, "outline": outline}


# ---------------------------------------------------------------- projection (plans and elevations)
VIEWS = {   # name: (sheet u, v; depth, larger = farther; towards the viewer)
    "sued": (lambda p: (p[0], p[2]), lambda p: p[1], (0, -1, 0)),
    "nord": (lambda p: (-p[0], p[2]), lambda p: -p[1], (0, 1, 0)),
    "ost": (lambda p: (p[1], p[2]), lambda p: -p[0], (1, 0, 0)),
    "west": (lambda p: (-p[1], p[2]), lambda p: p[0], (-1, 0, 0)),
    "top": (lambda p: (p[0], p[1]), lambda p: -p[2], (0, 0, 1)),
}
RASTER = 0.02                                 # occupancy raster of the hidden-face cull, m


def clip_below(P, h):
    """The part of the 3D polygon P with z <= h (Sutherland-Hodgman, one plane)."""
    out = []
    for i in range(len(P)):
        a, b = P[i - 1], P[i]
        if (a[2] <= h) != (b[2] <= h):
            s = (h - a[2]) / (b[2] - a[2])
            out.append((a[0] + s * (b[0] - a[0]), a[1] + s * (b[1] - a[1]), h))
        if b[2] <= h:
            out.append(b)
    return out


def solid_faces(bp):
    """Every face of the house's closed Parts, oriented outward: [(collection, object, material,
    points, closed)]. Loose furniture and the garden are left out. A box is convex, so its faces
    point away from its centre; other Parts are oriented by mesh_ops."""
    out = []
    for (c, o) in sorted(bp.geo):
        if o in bp.furniture or o in bp.plan["ground"]:
            continue
        g = bp.geo[(c, o)]
        V = g["v"]
        for first, n in bp.parts[(c, o)]:
            F = g["f"][first:first + n]
            idx = {i for f in F for i in f}
            if n == 6 and len(idx) == 8 and all(len(f) == 4 for f in F):
                m = [sum(V[i][k] for i in idx) / 8 for k in range(3)]
                fs = [f if mesh_ops.dot(mesh_ops.newell([V[i] for i in f]), mesh_ops.sub(V[f[0]], m)) >= 0
                      else f[::-1] for f in F]
                closed = True
            else:
                fs, is_open = mesh_ops.orient(V, F)
                closed = not is_open
            out += [(c, o, g["m"][first + j], [V[i] for i in f], closed) for j, f in enumerate(fs)]
    return out


def project(faces, view, clip=None):
    """Hidden-line view of faces [(…, object, material, points, closed)]: the faces turned towards the
    viewer, far to near (painter's algorithm; drawn white, so glass hides what lies behind it); faces
    fully covered by nearer rectangles on a 2 cm raster are dropped. A face's strokes are its share
    of the outline of its group of coplanar faces of one material, so no seam shows between them.
    clip = (z0, z1): only what lies between, cut off at z1 (a Grundriss looks down from its cut).
    Returns [(object, polygon, strokes)] in drawing order."""
    UV, D, T = VIEWS[view]
    items = []
    for _, o, m, P, closed in faces:
        if clip:
            zs = [p[2] for p in P]
            if min(zs) >= clip[1] or max(zs) < clip[0]:
                continue
            if max(zs) > clip[1]:
                P = clip_below(P, clip[1])
                if len(P) < 3:
                    continue
        N = mesh_ops.newell(P)
        L = math.sqrt(mesh_ops.dot(N, N))
        if L < 1e-10:
            continue
        c = mesh_ops.dot(N, T) / L
        if c <= 1e-6 and (closed or c >= -1e-6):                    # back face / edge-on
            continue
        plane = (m, tuple(round(v / L, 3) + 0.0 for v in N), round(mesh_ops.dot(N, P[0]) / L, 4))
        items.append((min(D(p) for p in P), o, [UV(p) for p in P], plane))
    if not items:
        return []
    items.sort(key=lambda it: -it[0])                               # far first; ties keep input order
    us = [p[0] for it in items for p in it[2]]
    vs = [p[1] for it in items for p in it[2]]
    U0, V0 = math.floor(min(us) / RASTER) - 1, math.floor(min(vs) / RASTER) - 1
    W = math.ceil(max(us) / RASTER) - U0 + 2
    grid = bytearray(W * (math.ceil(max(vs) / RASTER) - V0 + 2))
    keep = [False] * len(items)
    for i in range(len(items) - 1, -1, -1):                         # near to far
        uv = items[i][2]
        bu, bv = [p[0] for p in uv], [p[1] for p in uv]
        i0, j0 = math.floor(min(bu) / RASTER) - U0, math.floor(min(bv) / RASTER) - V0
        i1 = max(math.ceil(max(bu) / RASTER) - U0, i0 + 1)
        j1 = max(math.ceil(max(bv) / RASTER) - V0, j0 + 1)
        if not any(grid.find(0, j * W + i0, j * W + i1) >= 0 for j in range(j0, j1)):
            continue                                                # hidden behind nearer rectangles
        keep[i] = True
        if len(uv) == 4 and all(abs(uv[k][0] - uv[k - 1][0]) < 1e-9 or abs(uv[k][1] - uv[k - 1][1]) < 1e-9
                                for k in range(4)):                 # an upright rectangle covers its inner cells
            a0, a1 = math.ceil(min(bu) / RASTER) - U0, math.floor(max(bu) / RASTER) - U0
            if a1 > a0:
                ones = b"\x01" * (a1 - a0)
                for j in range(math.ceil(min(bv) / RASTER) - V0, math.floor(max(bv) / RASTER) - V0):
                    grid[j * W + a0:j * W + a1] = ones
    groups = {}
    for i, it in enumerate(items):
        if keep[i]:
            groups.setdefault(it[3], []).append(i)
    strokes = [[] for _ in items]
    for key in sorted(groups, key=repr):
        idx = groups[key]
        if len(idx) == 1:
            uv = items[idx[0]][2]
            strokes[idx[0]] = [(uv[k - 1], uv[k]) for k in range(len(uv))]
        else:
            for k, p, q in boundary([[items[i][2]] for i in idx]):
                strokes[idx[k]].append((p, q))
    return [(it[1], it[2], strokes[i]) for i, it in enumerate(items) if keep[i]]


def plan_view(bp, faces, st):
    """What a Grundriss sees below its cut (built-ins, stairs, sills, balconies), from above."""
    keep = plan_objects(bp, st)
    return project([f for f in faces if keep(f[0], f[1]) and not in_leaf(bp, st, f[3])], "top",
                   (FLOOR[st] - 0.3, FLOOR[st] + CUT[st]))


# ---------------------------------------------------------------- rooms: regions and net areas
def fmt_area(a):
    """Net area in the architect's notation: "24,06 m²"."""
    return ("%.2f" % a).replace(".", ",") + " m²"


def room_regions(bp, st):
    """The storey's rooms as regions of a section just below the ceiling (ROOM_CUT): every door
    opening is closed by its lintel there, exterior openings reaching higher are closed on the wall's
    inner face. Walls and built-ins reaching the ceiling divide (the Speis cabinet stands where a wall
    was; gaps of 5 mm to the walls are closed). The region is filled exactly on the grid of the unique
    wall coordinates; a built-in touching one region only counts towards its area.
    Returns (regions [dict(area, outside)], {PLAN_ROOMS index: region index})."""
    h, keep, top = FLOOR[st] + ROOM_CUT[st], plan_objects(bp, st), CEIL[st] - 0.01
    rects, polys = [], []                                           # (x0, x1, y0, y1, wall?), (loops, bbox, wall?)
    for (c, o) in sorted(bp.geo):
        if not keep(c, o) or o.endswith(bp.plan["frame_suffix"]):
            continue
        g = bp.geo[(c, o)]
        for first, n in bp.parts[(c, o)]:
            F = g["f"][first:first + n]
            wall = is_wall(bp, o, g["m"][first])
            if not wall and max(g["v"][i][2] for f in F for i in f) < top:
                continue                                            # a built-in below the ceiling
            ss = slice_faces(g["v"], F, h)
            if not ss:
                continue
            b = bbox([p for s_ in ss for p in s_])
            if n == 6 and all(abs(p[0] - q[0]) < 1e-9 or abs(p[1] - q[1]) < 1e-9 for p, q in ss):
                d = 0.0 if wall else 0.005
                rects.append((b[0] - d, b[1] + d, b[2] - d, b[3] + d, wall))
            else:
                polys.append((loops(ss), b, wall))
    walls = [r for r in rects if r[4]]
    for o in house_core.OPENINGS:                                   # close the exterior openings on the inner face
        if not (o["sill"] < h < o["head"]):
            continue
        f = o["face"]
        for r in walls:
            a0, a1 = (r[0], r[1]) if o["ax"] == "x" else (r[2], r[3])   # along the wall
            t0, t1 = (r[2], r[3]) if o["ax"] == "x" else (r[0], r[1])   # across it
            if a0 < o["a"] - 0.005 < a1 and t0 - 1e-6 <= f <= t1 + 1e-6:
                g_ = t1 if abs(t0 - f) < 1e-6 else t0
                rects.append((o["a"], o["b"], g_ - 0.002, g_ + 0.002, True) if o["ax"] == "x"
                             else (g_ - 0.002, g_ + 0.002, o["a"], o["b"], True))
                break
    R = lambda v: round(v, 4)
    X0, X1 = house_core.ANNEX[0] - 2, house_core.W_OUT + 2
    XS = sorted({R(v) for r in rects for v in r[:2]} | {R(p[0]) for L, *_ in polys for l in L for p in l} | {X0, X1})
    YS = sorted({R(v) for r in rects for v in r[2:4]} | {R(p[1]) for L, *_ in polys for l in L for p in l}
                | {-2.0, house_core.D_OUT + 2})
    nx, ny = len(XS) - 1, len(YS) - 1
    ix = lambda v: bisect.bisect_left(XS, R(v))
    iy = lambda v: bisect.bisect_left(YS, R(v))
    cell = {}                                                       # (i, j) -> True wall / False built-in
    for x0, x1, y0, y1, wall in rects:
        for i in range(ix(x0), ix(x1)):
            for j in range(iy(y0), iy(y1)):
                cell[(i, j)] = cell.get((i, j), False) or wall
    for L, (x0, x1, y0, y1), wall in polys:
        for i in range(ix(x0), ix(x1)):
            for j in range(iy(y0), iy(y1)):
                if inside(L, (XS[i] + XS[i + 1]) / 2, (YS[j] + YS[j + 1]) / 2):
                    cell[(i, j)] = cell.get((i, j), False) or wall
    area = lambda i, j: (XS[i + 1] - XS[i]) * (YS[j + 1] - YS[j])
    nb = lambda i, j: ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1))

    def flood(seed, ok):
        comp, stack = {seed}, [seed]
        while stack:
            for c in nb(*stack.pop()):
                if 0 <= c[0] < nx and 0 <= c[1] < ny and c not in comp and ok(c):
                    comp.add(c)
                    stack.append(c)
        return comp

    region, regions = {}, []
    for i in range(nx):
        for j in range(ny):
            if (i, j) in cell or (i, j) in region:
                continue
            comp = flood((i, j), lambda c: c not in cell)
            for c in comp:
                region[c] = len(regions)
            regions.append({"area": sum(area(*c) for c in comp),
                            "outside": any(c[0] in (0, nx - 1) or c[1] in (0, ny - 1) for c in comp)})
    seen = set()
    for c0 in sorted(c for c, w in cell.items() if not w):          # built-ins: towards the one room they touch
        if c0 in seen:
            continue
        comp = flood(c0, lambda c: cell.get(c) is False)
        seen |= comp
        touch = {region[c] for b in comp for c in nb(*b) if c in region}
        if len(touch) == 1:
            regions[touch.pop()]["area"] += sum(area(*c) for c in comp)
    anchors = {}
    for k, (name, s_, x, y) in enumerate(bp.plan_rooms):
        if s_ == st:
            anchors[k] = region.get((ix(x) - 1, iy(y) - 1))
            if anchors[k] is None:
                raise ValueError(f"PLAN_ROOMS: the anchor of {name!r} ({st}, {x}, {y}) lies in no room (wall or built-in)")
    return regions, anchors


def room_labels(bp, st, T):
    regions, anchors = room_regions(bp, st)
    out = ['<g id="rooms">']
    for k, r in sorted(anchors.items()):
        name, _, x, y = bp.plan_rooms[k]
        sx, sy = T((x, y))
        a = regions[r]["area"]
        lines, size = ([name], 2.5) if a >= 2.0 else (name.split(" "), 1.6)    # small rooms: small, wrapped
        out += [text(sx, sy + i * size * 1.15, ln, size, "middle") for i, ln in enumerate(lines)]
        out.append(text(sx, sy + len(lines) * size * 1.15 + 0.3, fmt_area(a), size * 0.88, "middle"))
    return "".join(out) + "</g>"


# ---------------------------------------------------------------- dimension chains
def half_cm(v):
    """A position rounded to half centimetres: chains are rounded first, so their segments sum exactly."""
    return math.floor(v * 200 + 0.5) / 200


def fmt_dim(m):
    """The architect's notation: from 1 m in metres with two decimals ("2.05"), below in centimetres
    ("31"); a remaining half centimetre is a superscript 5 ("4.01⁵", "41⁵")."""
    h = math.floor(m * 200 + 0.5)
    cm, half = divmod(h, 2)
    s = "%d.%02d" % divmod(cm, 100) if cm >= 100 else "%d" % cm
    return s + ("⁵" if half else "")


SIDES = {"N": ("y", 1), "S": ("y", -1), "E": ("x", 1), "W": ("x", -1)}   # facade normal: axis, sign


def chains(bp, st, sec):
    """Three chains per side of a Grundriss, from the drawing outwards: the facade's openings, its
    walls and rooms (scanned through the wall section just inside the main house's facade), the
    overall length. Positions in m, rounded to half centimetres: {side: [openings, walls, overall]}."""
    F = house_core.FOOT
    ext = {"x": (min(r[0] for r in F), max(r[1] for r in F)), "y": (min(r[2] for r in F), max(r[3] for r in F))}
    out = {}
    for side, (ax, sgn) in SIDES.items():
        along = "y" if ax == "x" else "x"
        lo, hi = ext[along]
        k = 0 if along == "x" else 1                                # coordinate index along the side
        span = lambda r: (r[1] - r[0]) if along == "x" else (r[3] - r[2])
        rect = max(F, key=span)                                     # the main house's full-length part
        face = {("y", 1): rect[3], ("y", -1): rect[2], ("x", 1): rect[1], ("x", -1): rect[0]}[(ax, sgn)]
        facade = ext[ax][1] if sgn > 0 else ext[ax][0]

        def crossings(line, k=k):                                   # outline crossings of a line, coordinate k
            r = []
            for p, q in sec["outline"]:
                a, b = p[1 - k], q[1 - k]
                if (a - line) * (b - line) < 0:
                    r.append(p[k] + (line - a) / (b - a) * (q[k] - p[k]))
            return sorted(r)

        # the scan line lies 5 cm beyond the thickest part of the facade wall: probed every 10 cm
        # along the side, from the facade inwards; a thickness counts where it holds for 0.5 m and is
        # at most 0.6 m (not a wall abutting the facade)
        runs = []
        for i in range(int((hi - lo) / 0.1)):
            ts = crossings(lo + 0.05 + 0.1 * i, 1 - k)
            at = [j for j, t in enumerate(ts) if abs(t - face) < 1e-3]
            run = abs(ts[at[0] - sgn] - face) if at and 0 <= at[0] - sgn < len(ts) else None
            runs.append(round(run, 3) if run is not None else None)
        held = [r for i, r in enumerate(runs) if r is not None and r <= 0.6 and runs[i:i + 5] == [r] * 5]
        line = face - sgn * (max(held, default=0.3) + 0.05)
        walls = [half_cm(t) for t in crossings(line) if lo < t < hi]
        ops = sorted({half_cm(v) for o in house_core.OPENINGS
                      if o["ax"] == along and abs(o["face"] - facade) < 1e-6 and FLOOR[st] <= o["sill"] < CEIL[st]
                      for v in (o["a"], o["b"])})
        ends = [half_cm(lo), half_cm(hi)]
        out[side] = [sorted(set(ops) | set(ends)), sorted(set(walls) | set(ends)), ends]
    return out


def dim_chains(bp, st, sec, T, box):
    """Draw the chains outside the drawing's bounding box (model m): ticks, length above the line."""
    out = ['<g id="dims" stroke="#000" stroke-width="0.13" fill="none">']
    txt = []
    for side, cs in chains(bp, st, sec).items():
        ax, sgn = SIDES[side]
        base = {"N": box[3], "S": box[2], "E": box[1], "W": box[0]}[side]
        for i, ch in enumerate(cs):
            c = base + sgn * (0.8 + 0.7 * i)                        # the chain's line, m
            P = (lambda v, c=c: (v, c)) if ax == "y" else (lambda v, c=c: (c, v))
            out.append(f'<path d="M{pt(T, P(ch[0]))}L{pt(T, P(ch[-1]))}"/>')
            for v in ch:                                            # 45 deg ticks
                x, y = T(P(v))
                out.append(f'<path stroke-width="0.25" d="M{num(x - 0.8)} {num(y + 0.8)}L{num(x + 0.8)} {num(y - 0.8)}"/>')
            lift = 0
            for a, b in zip(ch, ch[1:]):
                s = fmt_dim(b - a)
                small = (b - a) * S < 1.1 * len(s) + 0.5
                lift = (lift + 1) % 2 if small else 0               # short segments alternate above
                x, y = T(P((a + b) / 2))
                d = 0.8 + 2.0 * lift
                if ax == "y":
                    txt.append(text(x, y - d, s, 2.0, "middle"))
                else:
                    txt.append(text(x - d, y, s, 2.0, "middle", rot=-90))
    return "".join(out) + "</g>" + "".join(txt)


# ---------------------------------------------------------------- elevation annotation
def fmt_level(z):
    """A level above OK FFB EG in the architect's notation: "±0,00", "+2,70"."""
    return "±0,00" if abs(z) < 0.005 else ("%+.2f" % z).replace(".", ",")


def levels():
    """The Höhenkoten of every Ansicht: OK FFB EG and OG, the eaves (roof top over the outer wall), the ridge."""
    return [(0.0, "OK FFB EG"), (house_core.Z_OG, "OK FFB OG"), (house_core.roof_top(0.0), "Traufe"),
            (house_core.RIDGE_Z, "First")]


def width_chain(side):
    """Positions (sheet u, m) of the facade's corners as seen from side: house and annex."""
    rects = list(house_core.FOOT) + [house_core.ANNEX]
    k = (0, 1) if side in ("sued", "nord") else (2, 3)
    sgn = -1 if side in ("nord", "west") else 1
    return sorted({half_cm(sgn * r[i]) for r in rects for i in k})


# ---------------------------------------------------------------- drawing
STYLE = ('<style>.f{fill:#fff;stroke:none}.e{fill:none;stroke:#000;stroke-width:.13;stroke-linecap:round}'
         '.fe{fill:#fff;stroke:#000;stroke-width:.13;stroke-linejoin:round}'
         '.c{fill:#fff;stroke:#000;stroke-width:.18;stroke-linejoin:round}.w{fill:url(#hatch);stroke:none}'
         '.o{fill:none;stroke:#000;stroke-width:.5;stroke-linecap:square}'
         '#rooms text{paint-order:stroke;stroke:#fff;stroke-width:.8;stroke-linejoin:round}</style>'
         '<defs><pattern id="hatch" width="1" height="1" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
         '<rect width="1" height="1" fill="#fff"/><path d="M0.5 0V1" stroke="#000" stroke-width="0.1"/></pattern></defs>')


def plan_to_sheet():
    """Model (x, y) -> sheet mm: the footprint (house and annex) centred in the drawing area; the same
    for both storeys, so EG and OG lie on top of each other."""
    cx, cy = (house_core.ANNEX[0] + house_core.W_OUT) / 2, house_core.D_OUT / 2
    return lambda p: (205 + (p[0] - cx) * S, 128 - (p[1] - cy) * S)


def pt(T, p):
    x, y = T(p)
    return num(x) + " " + num(y)


def poly(T, loops_):
    return "".join("M" + "L".join(pt(T, p) for p in L) + "Z" for L in loops_)


def segs(T, ss):
    return "".join(f"M{pt(T, p)}L{pt(T, q)}" for p, q in ss)


def drawn(T, items):
    """Projected faces in drawing order: each a white fill, then its strokes."""
    out = []
    for _, uv, ss in items:
        d = "M" + "L".join(pt(T, p) for p in uv) + "Z"
        if ss == [(uv[k - 1], uv[k]) for k in range(len(uv))]:            # stroked all round: one path
            out.append(f'<path class="fe" d="{d}"/>')
            continue
        out.append(f'<path class="f" d="{d}"/>')
        if ss:
            out.append(f'<path class="e" d="{segs(T, ss)}"/>')
    return out


def plan_body(bp, faces, st):
    T, sec, items = plan_to_sheet(), section(bp, st), plan_view(bp, faces, st)
    out = [STYLE] + drawn(T, items)
    out += [f'<path class="c" d="{poly(T, L)}"/>' for _, L in sec["cut"]]
    out += [f'<path class="w" d="{poly(T, L)}"/>' for _, L in sec["walls"]]
    out.append(f'<path class="o" d="{segs(T, sec["outline"])}"/>')
    out.append(stair_symbols(bp, st, T))
    out.append(door_swings(bp, st, T))
    out.append(room_labels(bp, st, T))
    out.append(dim_chains(bp, st, sec, T, bbox([p for _, uv, _ in items for p in uv] +
                                               [p for _, L in sec["walls"] + sec["cut"] for l in L for p in l])))
    return "\n".join(out)


def stair_symbols(bp, st, T):
    """Treppe as in the architect's plan, in every storey it serves: outline, a line at each riser,
    the walking line from a circle at the bottom step to an arrow at the top (always up the stair),
    and in the bottom storey the step count with rise/run in cm ("15 STG 18.0/25.5")."""
    out = ['<g id="stairs" fill="none" stroke="#000" stroke-width="0.18">']
    for s in bp.stairs:
        if st not in s["storeys"]:
            continue
        (x0, y0), (x1, y1), rs, y = s["lo"], s["hi"], s["risers"], s["y"]
        out.append(f'<path class="outline" fill="#fff" d="M{pt(T, (x0, y0))}L{pt(T, (x1, y0))}L{pt(T, (x1, y1))}'
                   f'L{pt(T, (x0, y1))}Z"/>')
        out += [f'<path class="riser" d="M{pt(T, (x, y0))}L{pt(T, (x, y1))}"/>' for x in rs[1:-1]]
        (bx, by), (tx, ty) = T((rs[0], y)), T((rs[-1], y))
        ux, uy = (tx - bx) / math.hypot(tx - bx, ty - by), (ty - by) / math.hypot(tx - bx, ty - by)
        out.append(f'<path class="walk" d="M{num(bx)} {num(by)}L{num(tx)} {num(ty)}"/>')
        out.append(f'<circle cx="{num(bx + 0.8 * ux)}" cy="{num(by + 0.8 * uy)}" r="0.6"/>')
        a, w = 1.6, 0.8                                                    # arrowhead length, half width (mm)
        out.append(f'<path class="arrow" d="M{num(tx - a * ux - w * uy)} {num(ty - a * uy + w * ux)}L{num(tx)} {num(ty)}'
                   f'L{num(tx - a * ux + w * uy)} {num(ty - a * uy - w * ux)}"/>')
        if st == s["storeys"][0]:
            mx, my = T(((rs[0] + rs[-1]) / 2, (y + y1) / 2))
            out.append(text(mx, my + 1.0, f'{len(rs)} STG {s["rise"] * 100:.1f}/{s["run"] * 100:.1f}', 2.5, "middle")
                       .replace("<text ", '<text stroke="none" fill="#000" '))
    return "".join(out) + "</g>"


def door_swings(bp, st, T):
    """Türaufschlag: each hinged leaf of the storey drawn opened 90 deg into its room, with the
    quarter arc from its closed position (DOORS)."""
    out = ['<g id="doors" fill="none" stroke="#000" stroke-width="0.18">']
    for d in bp.doors:
        if d["c"] != st:
            continue
        h, w = d["hinge"], d["w"]
        o = (h[0] + w * d["open"][0], h[1] + w * d["open"][1])
        c = (h[0] + w * d["closed"][0], h[1] + w * d["closed"][1])
        (hx, hy), (ox, oy), (cx, cy) = T(h), T(o), T(c)
        sweep = 1 if (cx - hx) * (oy - hy) - (cy - hy) * (ox - hx) > 0 else 0   # on the sheet, y runs down
        r = num(w * S)
        out.append(f'<path d="M{pt(T, o)}L{pt(T, h)}M{pt(T, c)}A{r} {r} 0 0 {sweep} {pt(T, o)}"/>')
    return "".join(out) + "</g>"


def elevation_body(faces, side):
    """An Ansicht: the facade seen from its side, centred; below ±0,00 a grey ground band."""
    items = project(faces, side)
    us = [p[0] for _, uv, _ in items for p in uv]
    vs = [p[1] for _, uv, _ in items for p in uv]
    cu, top = (min(us) + max(us)) / 2, max(vs)
    T = lambda p: (205 + (p[0] - cu) * S, 135 - (p[1] - top / 2) * S)
    u0, u1 = min(us) - 1.0, max(us) + 1.0
    band = [(u0, 0.0), (u1, 0.0), (u1, -0.6), (u0, -0.6)]
    out = [STYLE] + drawn(T, items) + [
        f'<path fill="#d9d9d9" d="M{"L".join(pt(T, p) for p in band)}Z"/>',
        f'<path class="o" d="M{pt(T, (u0, 0.0))}L{pt(T, (u1, 0.0))}"/>']
    out.append('<g id="levels" stroke="#000" stroke-width="0.18">')          # Höhenkoten, left of the facade
    for z, name in levels():
        x, y = T((u0 - 0.5, z))
        out.append(f'<path d="M{num(x - 19)} {num(y)}H{num(x + 1.5)}"/>'
                   f'<path fill="#000" d="M{num(x)} {num(y)}L{num(x - 1)} {num(y - 1.6)}H{num(x + 1)}Z"/>')
        out.append(text(x - 19, y - 0.8, f"{fmt_level(z)} {name}", 2.0).replace("<text", '<text stroke="none"'))
    out.append('</g><g id="width" stroke="#000" stroke-width="0.13">')       # the facade's width, below the band
    ch = width_chain(side)
    for i, c in enumerate((ch, [ch[0], ch[-1]])):
        v = -0.6 - 0.8 - 0.7 * i
        out.append(f'<path d="M{pt(T, (c[0], v))}L{pt(T, (c[-1], v))}"/>')
        for u in c:
            x, y = T((u, v))
            out.append(f'<path stroke-width="0.25" d="M{num(x - 0.8)} {num(y + 0.8)}L{num(x + 0.8)} {num(y - 0.8)}"/>')
        for a, b in zip(c, c[1:]):
            x, y = T(((a + b) / 2, v))
            out.append(text(x, y - 0.8, fmt_dim(b - a), 2.0, "middle").replace("<text", '<text stroke="none"'))
    out.append("</g>")
    return "\n".join(out)


def text(x, y, s, size=2.5, anchor="start", weight=None, rot=0):
    t = f' transform="rotate({num(rot)} {num(x)} {num(y)})"' if rot else ""
    w = f' font-weight="{weight}"' if weight else ""
    return f'<text x="{num(x)}" y="{num(y)}" font-size="{num(size)}" text-anchor="{anchor}"{w}{t}>{escape(s)}</text>'


def scale_bar(x, y):
    """5 m in 1 m blocks (= 50 mm at 1:100), labelled 0 … 5 m."""
    out = ['<g id="scale" stroke="#000" stroke-width="0.18">']
    out += [f'<rect x="{num(x + i * S)}" y="{num(y)}" width="{num(S)}" height="1.50" '
            f'fill="{"#000" if i % 2 == 0 else "#fff"}"/>' for i in range(5)]
    out += ['</g>'] + [text(x + i * S, y - 1.2, str(i), 2.0, "middle") for i in range(6)]
    out.append(text(x + 5 * S + 2.5, y + 1.4, "m", 2.0))
    return "".join(out)


def north_arrow(x, y):
    """North is up on the floor plans (+y of the model)."""
    return (f'<g id="north" stroke="#000" stroke-width="0.25"><circle cx="{num(x)}" cy="{num(y)}" r="7" fill="none"/>'
            f'<path d="M{num(x)} {num(y - 7)}L{num(x + 2.5)} {num(y + 4)}L{num(x)} {num(y + 2)}L{num(x - 2.5)} {num(y + 4)}Z" '
            f'fill="#000"/></g>' + text(x, y - 8.5, "N", 3.5, "middle", "bold"))


MONTHS = ("Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober",
          "November", "Dezember")


def generated(when):
    """'generiert: 12. November 2026 20:34 Uhr' for an aware datetime, in Berlin time."""
    t = when.astimezone(zoneinfo.ZoneInfo("Europe/Berlin"))
    return f"generiert: {t.day}. {MONTHS[t.month - 1]} {t.year} {t:%H:%M} Uhr"


def sheet(name, body, state, north=False, stamp=None):
    """One A3 page: frame, the drawing (already in sheet mm), title block (stamp: the generation time,
    right in its top row), scale bar."""
    tx, ty = PAGE_W - 130, PAGE_H - 40                                  # title block, lower right
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{PAGE_W}mm" height="{PAGE_H}mm" '
           f'viewBox="0 0 {PAGE_W} {PAGE_H}" font-family="{FONT}">',
           f'<rect width="{PAGE_W}" height="{PAGE_H}" fill="#fff"/>',
           f'<rect x="10" y="10" width="{PAGE_W - 20}" height="{PAGE_H - 20}" fill="none" stroke="#000" stroke-width="0.5"/>',
           body,
           f'<g fill="none" stroke="#000" stroke-width="0.35"><rect x="{tx}" y="{ty}" width="120" height="30"/>'
           f'<path d="M{tx} {ty + 10}H{tx + 120}M{tx} {ty + 20}H{tx + 120}M{tx + 60} {ty + 20}V{ty + 30}"/></g>',
           text(tx + 3, ty + 7, "Frechenlehen", 5, weight="bold"),
           text(tx + 3, ty + 17, name, 4.5),
           text(tx + 3, ty + 26.5, "M 1:100", 3.5),
           text(tx + 63, ty + 26.5, f"Modellstand {state}", 2.5),
           scale_bar(tx, ty - 6)]
    if stamp:
        out.append(text(tx + 117, ty + 6.5, stamp, 2.5, "end"))
    if north:
        out.append(north_arrow(PAGE_W - 25, 32))
    out.append('</svg>\n')
    return "\n".join(out)


def export(outdir, stamp=None):
    bp = house_core.default_layout(house_core.build())   # the sheets show the default layout
    state = model_state(bp)
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    faces = solid_faces(bp)
    for key, name in SHEETS:
        body = plan_body(bp, faces, key.upper()) if key in ("eg", "og") else elevation_body(faces, key)
        (out / f"{key}.svg").write_text(sheet(name, body, state, north=key in ("eg", "og"), stamp=stamp), encoding="utf-8")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--generated"]
    export(args[0] if args else "plans",
           generated(datetime.datetime.now(datetime.timezone.utc)) if "--generated" in sys.argv else None)
