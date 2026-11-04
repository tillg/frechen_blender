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
    """Closed route: the viewer loops it without a jump (same pose, same speed at the seam)."""
    a, b = KEYS[0], KEYS[-1]
    assert math.dist(a[:3], b[:3]) < 1e-6 and abs(a[4] - b[4]) < 1e-9 and abs(a[5] - b[5]) < 1e-9
    assert abs(math.remainder(b[3] - a[3], 2 * math.pi)) < 1e-9
    step = math.dist(KEYS[1][:3], KEYS[0][:3])
    assert abs(math.dist(KEYS[-1][:3], KEYS[-2][:3]) - step) < 0.1 * step
