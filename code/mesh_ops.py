"""Mesh jobs that bmesh does for the Blender backend and the glTF backend does itself:
triangulating planar n-gons (may be concave) and orienting each Part outward. Plain Python."""

EPS = 1e-12


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def newell(pts):
    """Polygon normal scaled to twice its area (robust for concave polygons)."""
    nx = ny = nz = 0.0
    for i, p in enumerate(pts):
        q = pts[(i + 1) % len(pts)]
        nx += (p[1] - q[1]) * (p[2] + q[2])
        ny += (p[2] - q[2]) * (p[0] + q[0])
        nz += (p[0] - q[0]) * (p[1] + q[1])
    return (nx, ny, nz)


def _cr(o, p, q):
    return (p[0] - o[0]) * (q[1] - o[1]) - (p[1] - o[1]) * (q[0] - o[0])


def triangulate(pts):
    """Ear clipping of one planar, simple polygon (no holes). Returns index triples in the
    polygon's own winding."""
    n = len(pts)
    if n == 3:
        return [(0, 1, 2)]
    N = newell(pts)
    k = max(range(3), key=lambda i: abs(N[i]))           # drop the dominant axis
    a, b = ((1, 2), (2, 0), (0, 1))[k]
    s = 1 if N[k] > 0 else -1
    P = [(p[a], p[b] * s) for p in pts]                   # counter-clockwise in 2D
    idx, tris = list(range(n)), []
    while len(idx) > 3:
        m, best = len(idx), None
        for j in range(m):
            i0, i1, i2 = idx[j - 1], idx[j], idx[(j + 1) % m]
            A, B, C = P[i0], P[i1], P[i2]
            c = _cr(A, B, C)
            if best is None or c > best[0]:
                best = (c, j)
            if c <= EPS:
                continue                                  # reflex or collinear tip
            if any(_cr(A, B, P[o]) >= -EPS and _cr(B, C, P[o]) >= -EPS and _cr(C, A, P[o]) >= -EPS
                   and P[o] not in (A, B, C) for o in idx if o not in (i0, i1, i2)):
                continue                                  # another vertex inside: not an ear
            break
        else:
            j = best[1]                                   # degenerate rest: clip the most convex
        tris.append((idx[j - 1], idx[j], idx[(j + 1) % m]))
        idx.pop(j)
    tris.append(tuple(idx))
    return tris


def signed_volume(verts, faces):
    vol = 0.0
    for f in faces:
        p0 = verts[f[0]]
        for i in range(1, len(f) - 1):
            vol += dot(p0, cross(verts[f[i]], verts[f[i + 1]]))
    return vol / 6


def orient(verts, faces):
    """Consistent winding over each piece of one Part connected by manifold edges (an arch sweep
    that pinches to an edge with 4 users is two pieces); a closed piece is turned so its signed
    volume is positive (outward normals, as bmesh.ops.recalc_face_normals).
    Returns (faces, is_open); an open Part keeps the winding seeded by its first face."""
    key = lambda i: tuple(round(c, 7) for c in verts[i])
    faces = [list(f) for f in faces]
    kf = [[key(i) for i in f] for f in faces]

    def edges(fi):
        f = kf[fi]
        return [(f[j], f[(j + 1) % len(f)]) for j in range(len(f)) if f[j] != f[(j + 1) % len(f)]]

    users = {}
    for fi in range(len(faces)):
        for a, b in edges(fi):
            users.setdefault(frozenset((a, b)), []).append(fi)
    is_open = False
    seen = [False] * len(faces)
    for start in range(len(faces)):
        if seen[start]:
            continue
        seen[start], comp, stack, comp_open = True, [start], [start], False
        while stack:
            fi = stack.pop()
            for a, b in edges(fi):
                us = users[frozenset((a, b))]
                comp_open |= len(us) == 1
                if len(us) != 2:
                    continue                              # open or pinched edge: no propagation
                for g in us:
                    if seen[g]:
                        continue
                    if (a, b) in edges(g):                # same direction as fi: flip g
                        faces[g].reverse(); kf[g].reverse()
                    seen[g] = True
                    comp.append(g); stack.append(g)
        is_open |= comp_open
        if not comp_open and signed_volume(verts, [faces[i] for i in comp]) < 0:
            for i in comp:
                faces[i].reverse(); kf[i].reverse()
    return faces, is_open
