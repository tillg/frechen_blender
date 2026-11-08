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
