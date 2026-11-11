"""Show a change in the browser: a view URL on the dev server that frames named objects.

Pure Python (no bpy): the bounding box comes from the Blueprint, so the view is computed from the
same geometry the viewer draws (ADR-001-XEWL).

Outside objects (box within EDGE of the footprint W_OUT x D_OUT or beyond it) are seen from the
nearest facade, 20 degrees from above, nothing cut away; inside objects from the SE diagonal,
55 degrees from above, with the storeys above the box centre cut away (cut=eg below Z_EG_TOP,
noroof below Z_OG_TOP). Sub-model pages: from the SE diagonal, 30 degrees from above.

    .venv/bin/python code/show.py EG_Haustuer            # opens the viewer at the front door
    .venv/bin/python code/show.py EG_Tisch --from top    # from above, storeys above cut away
    .venv/bin/python code/show.py --page bad --print     # Bad sub-model, only print the URL

It refuses (exit 2) when the dev server on 5377 runs from another clone: switching is the user's call.
"""
import argparse, math, os, subprocess, sys
from decimal import ROUND_HALF_UP, Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import house_core  # noqa: E402

PORT = 5377
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = {"ofen": house_core.build_ofen, "desk": house_core.build_desk, "bad": house_core.build_bad,
         "kueche": house_core.build_kueche, "gaeste_wc": house_core.build_gaeste_wc,
         "regal": house_core.build_regal}
FOV = {"house": 28.0, "sub": 35.0}       # vertical field of view of main.js / submodel.js
MARGIN = 1.15                             # bounding sphere radius x MARGIN fills half the frame height
EDGE = 0.2                                # closer to the outer face than this: an outside object
SIDES = {"n": (0, 1), "e": (1, 0), "s": (0, -1), "w": (-1, 0), "se": (1, -1), "top": (0, -1)}
FACING = {"kueche": "s", "gaeste_wc": "n", "regal": "w"}                  # a sub-model seen from the SE unless its page opens elsewhere
UP = {"outside": 20.0, "inside": 55.0, "sub": 30.0, "top": 85.0}   # elevation, degrees


def bbox(bp, names=()):
    """Min/max corner over the vertices of the objects whose name starts with one of names (all
    objects when names is empty)."""
    vs = [v for (_, o), g in bp.geo.items() if not names or o.startswith(tuple(names)) for v in g["v"]]
    if not vs:
        raise SystemExit(f"no object matches {' '.join(names)}")
    return tuple(min(v[i] for v in vs) for i in range(3)), tuple(max(v[i] for v in vs) for i in range(3))


def view(bp, box, side=None):
    """(cam, at, p, cut) framing box; side n|e|s|w|top overrides the direction."""
    lo, hi = box
    at = tuple((lo[i] + hi[i]) / 2 for i in range(3))
    r = math.dist(lo, hi) / 2
    sub = bp.garden is None              # a sub-model page (ofen/desk/bad): no house around it
    if sub:
        kind, cut = "sub", None
        side = side or "se"
    elif (lo[0] < EDGE or lo[1] < EDGE or hi[0] > house_core.W_OUT - EDGE
          or hi[1] > house_core.D_OUT - EDGE):
        kind, cut = "outside", "all"
        if side is None:     # the facade nearest to the box centre (negative: beyond it)
            gap = {"w": at[0], "e": house_core.W_OUT - at[0], "s": at[1], "n": house_core.D_OUT - at[1]}
            side = min(gap, key=gap.get)
    else:
        kind = "inside"
        cut = "eg" if at[2] < house_core.Z_EG_TOP else "noroof" if at[2] < house_core.Z_OG_TOP else "all"
        side = side or "se"
    dx, dy = SIDES[side]
    h = math.hypot(dx, dy)
    up = math.radians(UP["top" if side == "top" else kind])
    d = r * MARGIN / math.sin(math.radians(FOV["sub" if sub else "house"] / 2))
    cam = (at[0] + d * math.cos(up) * dx / h, at[1] + d * math.cos(up) * dy / h, at[2] + d * math.sin(up))
    return cam, at, 4, cut


def num(n):
    """A number as main.js writes it (+n.toFixed(3)): 4, 2.5, -0.125; ties away from zero."""
    s = f"{Decimal(n).quantize(Decimal('0.001'), ROUND_HALF_UP):f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def url(page, cam, at, p=4, cut="all"):
    """The viewer's view URL: house ?cam=&at=&p=&cut=, sub-model <page>.html?cam=&at=&look=full."""
    xyz = lambda v: ",".join(num(c) for c in v)
    base = f"http://localhost:{PORT}/"
    if page == "house":
        return f"{base}?cam={xyz(cam)}&at={xyz(at)}&p={num(p)}&cut={cut}"
    return f"{base}{page}.html?cam={xyz(cam)}&at={xyz(at)}&look=full"


def server_cwd(lsof_text):
    """The cwd path in the output of `lsof -a -p <pid> -d cwd` (None if there is none)."""
    for line in lsof_text.splitlines():
        f = line.split(None, 8)
        if len(f) == 9 and f[3] == "cwd":
            return f[8]
    return None


def server_is_ours(lsof_text, repo=REPO):
    """True when the dev server's cwd (lsof output) is this repo's web/."""
    cwd = server_cwd(lsof_text)
    return cwd is not None and os.path.realpath(cwd) == os.path.realpath(os.path.join(repo, "web"))


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    a.add_argument("objects", nargs="*", help="object name prefixes (all objects when none)")
    a.add_argument("--at", help="frame a point x,y,z instead of objects")
    a.add_argument("--from", dest="side", choices=["n", "e", "s", "w", "top"])
    a.add_argument("--p", type=float, help="stage 0..4 (default 4, Eingerichtet)")
    a.add_argument("--page", choices=["house", *PAGES], default="house")
    a.add_argument("--print", action="store_true", help="only print the URL")
    o = a.parse_args(argv)
    sub = o.page != "house"
    if sub and o.p is not None:
        a.error("--p is for the house page only (a sub-model URL has no stage)")
    bp = PAGES[o.page]() if sub else house_core.build()
    if o.at:
        pt = tuple(float(c) for c in o.at.split(","))
        box = (tuple(c - 0.5 for c in pt), tuple(c + 0.5 for c in pt))
    else:
        box = bbox(bp, o.objects)
    cam, at, p, cut = view(bp, box, o.side or FACING.get(o.page))
    link = url(o.page, cam, at, p if o.p is None else o.p, cut)
    if not o.print:
        pid = subprocess.run(["lsof", "-tiTCP:%d" % PORT, "-sTCP:LISTEN"], capture_output=True, text=True).stdout.split()
        if not pid:
            print(f"no dev server on {PORT}: start it with  cd web && npm run dev", file=sys.stderr)
            return 2
        text = subprocess.run(["lsof", "-a", "-p", pid[0], "-d", "cwd"], capture_output=True, text=True).stdout
        if not server_is_ours(text):
            print(f"the dev server on {PORT} belongs to {server_cwd(text)}", file=sys.stderr)
            return 2
        subprocess.run(["open", link], check=True)
    print(link)
    return 0


if __name__ == "__main__":
    sys.exit(main())
