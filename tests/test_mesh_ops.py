"""mesh_ops: what bmesh does for the Blender backend, for the glTF backend in plain Python."""
import math, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "code"))
import mesh_ops  # noqa: E402
import house_core  # noqa: E402


def area2(a, b, c):
    return mesh_ops.cross(mesh_ops.sub(b, a), mesh_ops.sub(c, a))


def norm(v):
    return math.sqrt(sum(x * x for x in v))


def poly_area(pts):
    return norm(mesh_ops.newell(pts)) / 2


def inside(p, poly):
    """Even-odd test in 2D (u, v)."""
    c, n = False, len(poly)
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        if (y0 > p[1]) != (y1 > p[1]) and p[0] < x0 + (p[1] - y0) * (x1 - x0) / (y1 - y0):
            c = not c
    return c


def check_triangulation(pts3, uv):
    tris = mesh_ops.triangulate(pts3)
    assert len(tris) == len(pts3) - 2
    total = sum(norm(area2(*(pts3[i] for i in t))) / 2 for t in tris)
    assert abs(total - poly_area(pts3)) < 1e-9
    n = mesh_ops.newell(pts3)
    for t in tris:
        assert sum(a * b for a, b in zip(area2(*(pts3[i] for i in t)), n)) >= -1e-12   # same winding
        cu = sum(uv[i][0] for i in t) / 3, sum(uv[i][1] for i in t) / 3
        assert inside(cu, uv), t


def test_triangulates_a_concave_notched_board():
    uv = [(0, 0), (3, 0), (3, 2), (2, 2), (2, 1), (1, 1), (1, 2), (0, 2)]          # U shape
    check_triangulation([(0.5, u, z) for u, z in uv], uv)                           # yz plane


def test_triangulates_a_baluster_cut_out_profile():
    ub, ua, zr0, zr1, ct, cb = 0.12, 0.0, 0.0, 0.905, 0.745, 0.16
    ss = [i / 24 for i in range(25)]
    right = [(ub, zr0)] + [(ub - house_core.baluster_cut(q), ct - (ct - cb) * q) for q in reversed(ss)] + [(ub, zr1)]
    left = [(ua, zr1)] + [(ua + house_core.baluster_cut(q), ct - (ct - cb) * q) for q in ss] + [(ua, zr0)]
    uv = right + left                      # collinear runs on both edges, concave cut-outs
    check_triangulation([(u, 0.3, z) for u, z in uv], uv)                          # xz plane


BOX_V = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]


def outward(verts, faces):
    c = [sum(v[k] for v in verts) / len(verts) for k in range(3)]
    for f in faces:
        n = mesh_ops.newell([verts[i] for i in f])
        fc = [sum(verts[i][k] for i in f) / len(f) for k in range(3)]
        if sum(a * (b - cc) for a, b, cc in zip(n, fc, c)) <= 0:
            return False
    return True


def test_orients_a_box_with_mixed_winding_outward():
    faces = [(0, 3, 2, 1), (4, 7, 6, 5), (0, 1, 5, 4), (2, 1, 5, 6), (2, 3, 7, 6), (3, 0, 4, 7)]
    out, is_open = mesh_ops.orient(BOX_V, faces)
    assert not is_open and outward(BOX_V, out)


def test_flips_an_inside_out_prism():
    pts = [(0, 0), (2, 0), (2, 1), (1, 0.4), (0, 1)]                                  # concave
    n = len(pts)
    v = [(u, 0, z) for u, z in pts] + [(u, 1, z) for u, z in pts]
    f = [list(range(n))[::-1], list(range(n, 2 * n))]
    f += [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]               # all inward
    assert mesh_ops.signed_volume(v, f) < 0
    out, is_open = mesh_ops.orient(v, f)
    assert not is_open and mesh_ops.signed_volume(v, out) > 0


def test_orients_two_lobes_pinched_at_one_edge():
    """Like an arch sweep whose band pinches to zero: two boxes sharing one edge (used 4 times)."""
    v = BOX_V + [(x + 1, y, z + 1) for x, y, z in BOX_V]     # second box at (1, 0, 1): edge x=1,z=1
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    f2 = [tuple(i + 8 for i in q[::-1]) for q in f]         # second box inside out
    out, is_open = mesh_ops.orient(v, f + f2)
    assert not is_open
    for faces in (out[:6], out[6:]):
        assert mesh_ops.signed_volume(v, faces) > 0


def test_every_blueprint_part_is_consistently_wound():
    """Every manifold edge (2 users) is used in opposite directions, in every Part of the house
    (the arch sweeps pinch to a 4-user edge; the winding must not cross it)."""
    bp = house_core.build()
    bad = []
    for key, g in bp.geo.items():
        k = lambda i: tuple(round(c, 7) for c in g["v"][i])
        for first, n in bp.parts[key]:
            out, _ = mesh_ops.orient(g["v"], g["f"][first:first + n])
            uses = {}
            for f in out:
                ks = [k(i) for i in f]
                for j in range(len(ks)):
                    a, b = ks[j], ks[(j + 1) % len(ks)]
                    if a != b:
                        uses.setdefault(frozenset((a, b)), []).append((a, b))
            if any(len(u) == 2 and u[0] == u[1] for u in uses.values()):
                bad.append((key[1], first))
    assert not bad


def test_open_cone_is_reported_open():
    k = 32
    v = [(r * math.cos(2 * math.pi * i / k), r * math.sin(2 * math.pi * i / k), z)
         for r, z in ((0.06, 0.02), (0.18, -0.03)) for i in range(k)]
    f = [(j, (j + 1) % k, k + (j + 1) % k, k + j) for j in range(k)]
    f[3] = f[3][::-1]                                                                # one face flipped
    out, is_open = mesh_ops.orient(v, f)
    assert is_open                                       # consistent winding, seeded by face 0, no flip
    assert [tuple(o) for o in out] == [tuple(x) for x in f[:3]] + [tuple(f[3][::-1])] + [tuple(x) for x in f[4:]]
