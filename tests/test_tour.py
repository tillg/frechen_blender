"""tour.py: the walkthrough route, baked to smoothed camera keys for the film and the viewer.

tests/golden/tour.json holds the keys film.py produced before the route moved to tour.py
(count, sha1 over the keys at 6 decimals, first and last key). After a deliberate route change:
    UPDATE_TOUR_GOLDEN=1 python3 -m pytest -q tests/test_tour.py
"""
import hashlib, json, math, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "code"))
import tour  # noqa: E402

KEYS = tour.build_tour()
SHA = hashlib.sha1(";".join(",".join(f"{v:.6f}" for v in k) for k in KEYS).encode()).hexdigest()
PATH = ROOT / "tests" / "golden" / "tour.json"
if os.environ.get("UPDATE_TOUR_GOLDEN"):
    PATH.write_text(json.dumps({"n": len(KEYS), "sha1_6dp": SHA, "first": list(KEYS[0]),
                                "last": list(KEYS[-1]), "fps": tour.FPS}, indent=1) + "\n")
GOLDEN = json.loads(PATH.read_text())


def test_build_tour_reproduces_the_film_keys():
    assert len(KEYS) == GOLDEN["n"] and tour.FPS == GOLDEN["fps"]
    assert list(KEYS[0]) == GOLDEN["first"] and list(KEYS[-1]) == GOLDEN["last"]
    assert SHA == GOLDEN["sha1_6dp"]


def test_keys_are_six_numbers():
    assert all(len(k) == 6 for k in KEYS)


def test_route_ends_where_it_starts():
    """Closed route: the viewer loops it without a jump (same pose at the seam; the route ends
    with a pause, so the orbit starts from rest, but no step at the seam exceeds the orbit's)."""
    a, b = KEYS[0], KEYS[-1]
    assert math.dist(a[:3], b[:3]) < 1e-6 and abs(a[4] - b[4]) < 1e-9 and abs(a[5] - b[5]) < 1e-9
    assert abs(math.remainder(b[3] - a[3], 2 * math.pi)) < 1e-9
    cruise = math.dist(KEYS[51][:3], KEYS[50][:3])                  # orbit at full speed
    seam = (math.dist(KEYS[1][:3], KEYS[0][:3]), math.dist(KEYS[-1][:3], KEYS[-2][:3]))
    assert max(seam) <= 1.05 * cruise


def test_route_looks_into_the_grosseltern_shower_and_wc():
    """Request 2026-11-08: the Rundgang steps into the Bad Großeltern (code/bad.py) and looks into
    its walk-in shower (NW corner, x 0.31-1.11, y 10.92-12.47) and into its WC (niche, west half,
    toilet at x 0.79 on the south wall), pausing at each."""
    def looking_at(k, tx, ty, tol=12):
        a = math.degrees(math.atan2(ty - k[1], tx - k[0]) - k[3])
        return abs((a + 180) % 360 - 180) < tol
    bad = [k for k in KEYS if 0.31 < k[0] < 2.358 and 9.9 < k[1] < 12.47 and k[2] < 2]
    shower = [k for k in bad if looking_at(k, 0.71, 11.7)]
    wc = [k for k in bad if looking_at(k, 0.79, 9.1)]
    assert len(shower) >= tour.PAUSE * tour.FPS and len(wc) >= tour.PAUSE * tour.FPS
    assert min(k[4] for k in wc) < -0.3                                   # looks down at the toilet


def test_route_walks_into_the_elternbad_and_back_out():
    """Issue #3 (request 2026-11-13): the door of the Bad Nadine & Till moved to the south end of its east wall
    (y 0.65 .. 1.58, wall x 8.59 .. 8.72). The Rundgang walks in through it to the back (west) wall, turns right
    (past the shower and toilet in the north) until its back is to that wall, waits, and walks straight out."""
    def looking_at(k, tx, ty, tol=12):
        a = math.degrees(math.atan2(ty - k[1], tx - k[0]) - k[3])
        return abs((a + 180) % 360 - 180) < tol
    og = [(i, k) for i, k in enumerate(KEYS) if k[2] > house_core.Z_OG]
    bad = [(i, k) for i, k in og if 5.59 < k[0] < 8.59 and 0.40 < k[1] < 2.62]
    back = [(i, k) for i, k in bad if k[0] < 6.2]                         # at the back wall
    assert back and min(k[0] for i, k in back) > 5.59 + 0.25
    i0, i1 = back[0][0], back[-1][0]
    assert looking_at(back[0][1], 5.0, back[0][1][1])                      # arrives facing the wall
    east = [k for i, k in back if looking_at(k, 9.0, k[1], 3)]
    assert len(east) >= tour.PAUSE * tour.FPS                             # back to the wall, waiting
    assert [k for i, k in back if looking_at(k, k[0], 3.0)]               # turned right: via the north
    assert not [k for i, k in back if looking_at(k, k[0], 0.0)]           # not via the basin (south)
    door = lambda k: 8.5 < k[0] < 9.0 and 0.75 < k[1] < 1.5
    assert [k for i, k in og if i < i0 and door(k) and looking_at(k, 5.0, k[1], 20)]     # in through the door
    assert [k for i, k in og if i > i1 and door(k) and looking_at(k, 10.0, k[1], 20)]    # straight out again
    assert not [k for i, k in og if 8.72 < k[0] < 9.0 and 1.7 < k[1] < 2.6]             # old door


# ---------------------------------------------------------------- routes and Standpunkte (viewer)
import house_core  # noqa: E402

ENTRIES = {"haus", "eg", "og"}
ROUTES_PATH = ROOT / "tests" / "golden" / "routes.json"


def inside(p):
    return 0 < p[0] < house_core.W_OUT and 0 < p[1] < house_core.D_OUT


def test_the_first_route_is_the_films():
    assert tour.ROUTES[0] == ("Um und durch das Haus", tour.ROUTE)
    assert tour.build_tour(tour.ROUTE) == KEYS


def test_every_route_is_closed():
    """Every route ends at its start pose, so the viewer's Endlos loops it without a jump."""
    assert len(tour.ROUTES) >= 2 and len({n for n, _ in tour.ROUTES}) == len(tour.ROUTES)
    for name, route in tour.ROUTES:
        k = tour.build_tour(route)
        a, b = k[0], k[-1]
        assert math.dist(a[:3], b[:3]) < 1e-6, name
        assert abs(math.remainder(b[3] - a[3], 2 * math.pi)) < 1e-9 and abs(a[4] - b[4]) < 1e-9, name


def test_stube_kueche_walks_through_both_rooms_in_the_eg():
    k = tour.build_tour(dict(tour.ROUTES)["Durch die Stube & Küche"])
    assert all(inside(f) and abs(f[2] - tour.EYE) < 1e-9 for f in k)        # indoors, EG eye height
    rooms = {n: (x, y) for n, _, x, y, _ in house_core.ROOM_NAMES}
    for room in ("Stube", "Küche"):
        assert min(math.dist(f[:2], rooms[room]) for f in k) < 1.5, room


def test_extra_routes_match_their_golden():
    got = {}
    for name, route in tour.ROUTES[1:]:
        k = tour.build_tour(route)
        got[name] = {"n": len(k), "sha1_6dp": hashlib.sha1(";".join(",".join(f"{v:.6f}" for v in f) for f in k).encode()).hexdigest()}
    if os.environ.get("UPDATE_TOUR_GOLDEN"):
        ROUTES_PATH.write_text(json.dumps(got, indent=1, ensure_ascii=False) + "\n")
    assert got == json.loads(ROUTES_PATH.read_text())


def test_spots_have_unique_names_and_valid_entries():
    names = [s[0] for s in tour.SPOTS]
    assert len(names) == len(set(names))
    for name, group, entries, cam, at, fov in tour.SPOTS:
        assert entries and set(entries) <= ENTRIES, name
        assert len(cam) == 3 and len(at) == 3 and 10 <= fov <= 90 and math.dist(cam, at) > 0.3, name
        assert group, name
    for e in ENTRIES:
        assert any(e in s[2] for s in tour.SPOTS), e


def test_the_standard_spots():
    """The first spot listed for an entry is its standard; the house's is the old opening view."""
    first = {e: next(s for s in tour.SPOTS if e in s[2]) for e in ENTRIES}
    assert first["haus"][0] == "Von Südosten"
    assert first["haus"][3:] == ((33, -24, 13), (7.4, 6.4, 3.2), 28)
    assert first["eg"][0] == first["og"][0] == "Von oben"


def test_every_room_has_an_inside_spot_at_eye_height():
    """A room's spot is the first one named after it ("Bibliothek" or "Bibliothek - …")."""
    for room, floor, *_ in house_core.ROOM_NAMES:
        name, group, entries, cam, at, fov = next(s for s in tour.SPOTS if s[0].split(" - ")[0] == room)
        z = tour.EYE if floor == "EG" else tour.OG
        assert inside(cam) and abs(cam[2] - z) < 1e-9, room
        assert set(entries) == {"haus", floor.lower()}, room
        assert group == {"EG": "Erdgeschoss", "OG": "1. Stock"}[floor], room


def test_bibliothek_stands_in_the_corner_behind_the_desk():
    """Request 2026-11-10: in the corner behind the desk (desk.DESK_AT, against the north wall),
    looking across the whole room (south); issue #9: named "Bibliothek - Ecke hinten rechts"."""
    import desk
    _, _, _, cam, at, _ = next(s for s in tour.SPOTS if s[0] == "Bibliothek - Ecke hinten rechts")
    dx, dy = desk.DESK_AT[0] + desk.DESK_W / 2, desk.DESK_AT[1] + desk.DESK_D / 2   # desk centre
    assert math.dist(cam[:2], (dx, dy)) < 3.0 and cam[1] > dy - 0.5       # by the desk, at the north wall
    assert at[1] < cam[1] - 1.0                                           # looking south into the room


def test_klavierspieler_sits_on_the_piano_bench_looking_over_the_keys():
    """Issue #9: the pianist's view, listed right after the Bibliothek's corner: seated eye above
    the bench, looking along the keyboard's normal over the piano into the room."""
    names = [s[0] for s in tour.SPOTS]
    assert names.index("Bibliothek - Klavierspieler") == names.index("Bibliothek - Ecke hinten rechts") + 1
    _, group, entries, cam, at, fov = next(s for s in tour.SPOTS if s[0] == "Bibliothek - Klavierspieler")
    assert group == "Erdgeschoss" and set(entries) == {"haus", "eg"} and fov == tour.SEE
    house_core.build()
    g = house_core.GEO[("EG", "EG_Moebel")]
    lack = {i for f, m in zip(g["f"], g["m"]) if m == "Klavierlack" for i in f}
    top = lambda z: [g["v"][i] for i in lack if abs(g["v"][i][2] - z) < 1e-6]
    bench, keys = top(0.50), top(0.70)                                   # bench top, key bed top
    centre = lambda vs: (sum(v[0] for v in vs) / len(vs), sum(v[1] for v in vs) / len(vs))
    (bx, by), (kx, ky) = centre(bench), centre(keys)
    b0, (s, l, _) = bench[0], sorted(bench[1:], key=lambda v: math.dist(v[:2], bench[0][:2]))
    for e in (s, l):                                                      # above the bench, in its own axes
        ex, ey = e[0] - b0[0], e[1] - b0[1]
        assert abs((cam[0] - bx) * ex + (cam[1] - by) * ey) < (ex * ex + ey * ey) / 2
    assert 1.1 < cam[2] < 1.35                                            # seated eye height
    k0 = keys[0]
    k1 = sorted(keys[1:], key=lambda v: math.dist(v[:2], k0[:2]))[1]     # short edge, long edge, diagonal
    ex, ey = k1[0] - k0[0], k1[1] - k0[1]                                 # along the key bed
    nx, ny = -ey, ex                                                      # its normal, away from the bench
    if nx * (kx - bx) + ny * (ky - by) < 0:
        nx, ny = -nx, -ny
    dx, dy = at[0] - cam[0], at[1] - cam[1]
    cos = (dx * nx + dy * ny) / math.hypot(dx, dy) / math.hypot(nx, ny)
    assert cos > math.cos(math.radians(5))                                # straight over the keys
    assert at[2] < cam[2]                                                 # looking a little down


def test_routes_and_spots_clear_the_wandlampen():
    """Issues #19, #22: the Wandlampen reach 21 cm from the walls at head height; every camera key of every
    route and every Standpunkt keeps the film's clearance of 0.25 m from each lamp (OG and EG, both layouts)."""
    bp = house_core.build()
    lamps = []                                                            # [(lo, hi)] per lamp: its parts lie
    parts = [(g["v"], g["f"][first:first + n]) for key, g in bp.geo.items() if "Wandlampen" in key[1]   # within 20 cm,
             for first, n in bp.parts[key]]                                                        # lamps 35+ cm apart
    for V, F in parts:
        vs = [V[i] for f in F for i in f]
        lo, hi = [min(p[k] for p in vs) for k in range(3)], [max(p[k] for p in vs) for k in range(3)]
        c = [(a + b) / 2 for a, b in zip(lo, hi)]
        j = next((j for j, (l, h) in enumerate(lamps) if math.dist(c, [(a + b) / 2 for a, b in zip(l, h)]) < 0.2), None)
        if j is None:
            lamps.append((lo, hi))
        else:
            l, h = lamps[j]
            lamps[j] = ([min(a, b) for a, b in zip(l, lo)], [max(a, b) for a, b in zip(h, hi)])
    assert len(lamps) == 35 + 35                                          # OG; EG incl. both layouts and the Ofen bed
    gap = lambda p: min(math.dist(p, [min(max(p[k], lo[k]), hi[k]) for k in range(3)]) for lo, hi in lamps)
    for name, route in tour.ROUTES:
        for f in tour.build_tour(route):
            assert gap(f[:3]) >= 0.25, (name, f[:3])
    for s in tour.SPOTS:
        assert gap(s[3]) >= 0.25, s[0]
