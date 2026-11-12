"""code/show.py: a view URL that frames named objects of the Blueprint (the Show)."""
import math, sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "code"))
import house_core, show  # noqa: E402

FOV, ASPECT = 28.0, 16 / 9


@pytest.fixture(scope="module")
def bp():
    return house_core.build()


def corners(box):
    (x0, y0, z0), (x1, y1, z1) = box
    return [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]


def in_frame(cam, at, p, fov=FOV, aspect=ASPECT):
    """p inside the view frustum of a camera at cam looking at at (z up): written here, not in show.py."""
    sub = lambda a, b: [a[i] - b[i] for i in range(3)]
    dot = lambda a, b: sum(a[i] * b[i] for i in range(3))
    cross = lambda a, b: [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
    unit = lambda a: [c / math.sqrt(dot(a, a)) for c in a]
    f = unit(sub(at, cam))
    r = unit(cross(f, [0, 0, 1]))
    u = cross(r, f)
    d = sub(p, cam)
    depth = dot(d, f)
    ty = math.tan(math.radians(fov / 2))
    return depth > 0 and abs(dot(d, u) / depth) <= ty and abs(dot(d, r) / depth) <= ty * aspect


def test_front_door_is_seen_from_the_east(bp):
    box = show.bbox(bp, ["EG_Haustuer"])
    cam, at, p, cut = show.view(bp, box)
    assert cam[0] > house_core.W_OUT
    assert cut == "all" and p == 4
    assert all(in_frame(cam, at, c) for c in corners(box))


def test_inside_object_cuts_the_storeys_above(bp):
    box = show.bbox(bp, ["EG_Tisch"])
    cam, at, p, cut = show.view(bp, box)
    assert cut == "eg"
    assert cam[2] > box[1][2]
    assert all(in_frame(cam, at, c) for c in corners(box))
    assert show.view(bp, show.bbox(bp, ["OG_Moebel"]))[3] == "noroof"


def test_from_overrides_the_side(bp):
    box = show.bbox(bp, ["EG_Haustuer"])
    cam, at, _, _ = show.view(bp, box, side="w")
    assert cam[0] < at[0] and abs(cam[1] - at[1]) < 1e-6
    cam, at, _, _ = show.view(bp, box, side="n")
    assert cam[1] > at[1] and abs(cam[0] - at[0]) < 1e-6
    assert all(in_frame(cam, at, c) for c in corners(box))


def test_url_matches_the_viewer_format():
    # keys and order as main.js / submodel.js write them, numbers as +n.toFixed(3)
    assert (show.url("house", (1, 2.5, -0.0001), (0.12345, 0, 3), 4, "eg")
            == "http://localhost:5377/?cam=1,2.5,0&at=0.123,0,3&p=4&cut=eg")
    assert (show.url("ofen", (1.5, -2, 1), (0, 0, 0.75))
            == "http://localhost:5377/ofen.html?cam=1.5,-2,1&at=0,0,0.75&look=full")
    assert show.num(0.0625) == "0.063" and show.num(-0.0625) == "-0.063"   # ties: half away from 0


LSOF = """COMMAND   PID     USER   FD   TYPE DEVICE SIZE/OFF      NODE NAME
node    22417 tgartner  cwd    DIR   1,15      640 564230222 {}
"""


def test_server_owner_is_checked():
    repo = "/Users/u/git/frechen_blender2"
    assert show.server_is_ours(LSOF.format(repo + "/web"), repo)
    assert not show.server_is_ours(LSOF.format("/Users/u/git/frechen_blender/web"), repo)
    assert not show.server_is_ours("", repo)
    assert show.server_cwd(LSOF.format("/Users/u/git/frechen_blender/web")) == "/Users/u/git/frechen_blender/web"


def test_stage_only_on_the_house_page():
    with pytest.raises(SystemExit) as e:
        show.main(["--page", "bad", "--p", "2", "--print"])
    assert e.value.code == 2


def test_kueche_page(capsys):
    """The Küche sub-model page (kueche.html) is a --page like the other sub-models."""
    assert show.main(["Kueche_Herd", "--page", "kueche", "--print"]) == 0
    link = capsys.readouterr().out.strip()
    assert link.startswith("http://localhost:5377/kueche.html?cam=") and link.endswith("&look=full")
    cam, at = (tuple(map(float, q.split("=")[1].split(","))) for q in link.split("?")[1].split("&")[:2])
    assert cam[1] < at[1] and cam[0] == at[0]      # from the open south, not through the east wall (SE)


def test_gaeste_wc_page(capsys):
    """The Gäste-WC sub-model page (gaeste_wc.html) is a --page, seen from the Flur (north) like the
    drawing's section, not through the south wall (SE)."""
    assert show.main(["GaesteWC_Garderobe", "--page", "gaeste_wc", "--print"]) == 0
    link = capsys.readouterr().out.strip()
    assert link.startswith("http://localhost:5377/gaeste_wc.html?cam=") and link.endswith("&look=full")
    cam, at = (tuple(map(float, q.split("=")[1].split(","))) for q in link.split("?")[1].split("&")[:2])
    assert cam[1] > at[1] and cam[0] == at[0]


def test_regal_page(capsys):
    """The "Schrank im Büro" sub-model page (regal.html) is a --page, seen from the room (west), facing
    the window, not through the east wall (SE)."""
    assert show.main(["Regal_Moebel", "--page", "regal", "--print"]) == 0
    link = capsys.readouterr().out.strip()
    assert link.startswith("http://localhost:5377/regal.html?cam=") and link.endswith("&look=full")
    cam, at = (tuple(map(float, q.split("=")[1].split(","))) for q in link.split("?")[1].split("&")[:2])
    assert cam[0] < at[0] and cam[1] == at[1]


def test_variant_objects_are_shown_in_their_entry(bp):
    """Objects of the EG variant Alternativ (#5) are hidden in Erdgeschoss: the Show uses its entry
    Erdgeschoss - Alternativ (cut eg_alt) for them; default objects keep cut eg."""
    names = ["EG_Alt_Schrank", "EG_Alt_Pendeltuer_S"]
    assert show.view(bp, show.bbox(bp, names), names=names)[3] == "eg_alt"
    assert show.view(bp, show.bbox(bp, ["EG_Speis_C"]), names=["EG_Speis_C"])[3] == "eg"
    assert show.view(bp, show.bbox(bp, ["EG_Alt"]), names=["EG_Alt"])[3] == "eg_alt"           # prefixes
    assert show.view(bp, show.bbox(bp, ["EG_Speis"]), names=["EG_Speis"])[3] == "eg"            # both layouts
