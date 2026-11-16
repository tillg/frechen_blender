"""code/vorlagen.py: every reference picture of input/ sorted into one Bereich of the house, its
downsized copy under web/public/vorlagen/, and the marker anchors of the house viewer (issue #31)."""
import itertools, json, struct, subprocess, sys, tempfile, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "code"))
import house_core  # noqa: E402
import vorlagen  # noqa: E402

RASTER = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".heic", ".webp", ".gif", ".avif"}
BP = house_core.build()
nfc = lambda s: unicodedata.normalize("NFC", s)   # macOS file names come decomposed (ü)


def by_key():
    return {b["key"]: b for b in vorlagen.BEREICHE}


def test_every_input_image_is_assigned_once():
    files = sorted(nfc(str(p.relative_to(ROOT / "input"))) for p in (ROOT / "input").rglob("*")
                   if p.suffix.lower() in RASTER)
    srcs = [nfc(f["src"]) for b in vorlagen.BEREICHE for f in b["fotos"]]
    doppelt = {nfc(a): nfc(b) for a, b in vorlagen.DOPPELT.items()}
    assert len(files) == 57
    assert sorted(srcs + list(doppelt)) == files      # each one exactly once (shown or a duplicate), none missing or extra
    assert set(doppelt.values()) <= set(srcs) and not set(doppelt) & set(srcs)   # a duplicate's photo is shown once
    keys = [b["key"] for b in vorlagen.BEREICHE]
    assert len(set(keys)) == len(keys)
    names = [(b["key"], f["file"]) for b in vorlagen.BEREICHE for f in b["fotos"]]
    assert len(set(names)) == len(names)              # window_from_outside .jpeg / .png: two copies
    for b in vorlagen.BEREICHE:
        assert b["title"] and b["fotos"]
        for f in b["fotos"]:
            assert f["caption"] and f["file"].endswith(".jpg") and f["file"].isascii() and " " not in f["file"]


def test_issue_examples():
    """The examples of issue #31: Garderobe + Toilette Mallnitz on one page (the Gäste-WC corner by
    the back hall's Windfang door), the Ofen in the Stube, the standard basins and lamps for the
    whole house."""
    b = by_key()
    src = lambda k: {Path(f["src"]).name for f in b[k]["fotos"]}
    assert {"garderobe mallnitz.jpeg", "toilette mallnitz.jpeg"} <= src("garderobe")
    assert "ofen_stuben.jpg" in src("stube")
    assert {"waschbecken_einzeln.jpeg", "waschbecken_staender.png", "wandlampe.png"} <= src("haus")
    assert src("gaestebad") == {"badewanne.webp"} and b["gaestebad"]["room"] == ("Bad", "OG")   # #32: the tub


def part_boxes(names):
    """(lo, hi) of every Part of the objects whose name passes `names`."""
    out = []
    for key, parts in BP.parts.items():
        if not names(key[1]):
            continue
        g = BP.geo[key]
        for first, n in parts:
            pts = [g["v"][i] for f in g["f"][first:first + n] for i in f]
            out.append((tuple(min(p[k] for p in pts) for k in range(3)), tuple(max(p[k] for p in pts) for k in range(3))))
    return out


def crosses(a, b, box):
    """Does the segment a-b pass through the box (slab method)?"""
    t0, t1 = 0.0, 1.0
    for k in range(3):
        d = b[k] - a[k]
        if abs(d) < 1e-12:
            if not box[0][k] < a[k] < box[1][k]:
                return False
            continue
        u, v = sorted(((box[0][k] - a[k]) / d, (box[1][k] - a[k]) / d))
        t0, t1 = max(t0, u), min(t1, v)
        if t0 >= t1:
            return False
    return True


def test_anchors_in_free_air_in_their_room():
    """Each marker stands in the air (inside no Part, 15 cm clear), between floor and ceiling of
    its storey, inside the house in the room the plan names (no wall between it and the room's
    label anchor of PLAN_ROOMS); the Außen marker outside the house; Pläne has none."""
    boxes = part_boxes(lambda n: True)
    walls = part_boxes(lambda n: n.endswith(house_core.PLAN["wall_suffix"]))
    rooms = {}                                        # a name can stand twice in a storey (the OG's two "Bad")
    for n, s, x, y in house_core.PLAN_ROOMS:
        rooms.setdefault((n, s), []).append((x, y))
    m = 0.15
    for b in vorlagen.BEREICHE:
        at = b["at"]
        if b["key"] == "plaene":
            assert at is None and b["room"] is None
            continue
        assert at is not None, b["key"]
        x, y, z = at
        for lo, hi in boxes:
            assert not all(lo[k] - m < at[k] < hi[k] + m for k in range(3)), (b["key"], lo, hi)
        inside = 0 < x < house_core.W_OUT and 0 < y < house_core.D_OUT
        if b["key"] == "aussen":
            assert not inside and 1.0 < z < 2.5
            continue
        assert inside, b["key"]
        name, storey = b["room"]
        z0 = 0.0 if storey == "EG" else house_core.Z_OG
        assert z0 + 1.0 < z < z0 + 2.2, b["key"]
        assert any(not any(crosses(at, (rx, ry, z), w) for w in walls) for rx, ry in rooms[(name, storey)]), b["key"]


def jpeg_size(path):
    """(width, height) from the first SOF marker of a JPEG."""
    data = Path(path).read_bytes()
    assert data[:2] == b"\xff\xd8", path
    i = 2
    while i < len(data):
        marker, length = data[i + 1], struct.unpack(">H", data[i + 2:i + 4])[0]
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            return w, h
        i += 2 + length
    raise AssertionError(f"no SOF in {path}")


def test_every_copy_exists_and_is_small():
    for b in vorlagen.BEREICHE:
        for f in b["fotos"]:
            p = ROOT / "web" / "public" / "vorlagen" / b["key"] / f["file"]
            assert p.is_file(), p
            assert max(jpeg_size(p)) <= vorlagen.MAX_PX, p
            assert p.stat().st_size < 1_000_000, p
    on_disk = {str(p.relative_to(ROOT / "web" / "public" / "vorlagen"))
               for p in (ROOT / "web" / "public" / "vorlagen").rglob("*.jpg")}
    assert on_disk == {f"{b['key']}/{f['file']}" for b in vorlagen.BEREICHE for f in b["fotos"]}   # no stale copy


def average_hashes(paths, n=16):
    """Per picture the n x n grayscale average hash (bits: brighter than the mean) in its four 90° turns; the
    pictures are scaled with sips (macOS, as vorlagen.copy()) to n x n BMPs, which are read here."""
    with tempfile.TemporaryDirectory() as d:
        tmp = [Path(d) / f"{i}.jpg" for i in range(len(paths))]
        for a, b in zip(paths, tmp):
            b.write_bytes(a.read_bytes())
        subprocess.run(["sips", "-z", str(n), str(n), "-s", "format", "bmp", *map(str, tmp), "--out", d],
                       check=True, capture_output=True)
        out = []
        for t in tmp:
            data = t.with_suffix(".bmp").read_bytes()
            off, (w, h), bpp = struct.unpack("<I", data[10:14])[0], struct.unpack("<ii", data[18:26]), data[28] // 8
            row = (w * bpp + 3) & ~3
            g = [[0.114 * data[off + y * row + x * bpp] + 0.587 * data[off + y * row + x * bpp + 1]
                  + 0.299 * data[off + y * row + x * bpp + 2] for x in range(w)] for y in range(abs(h))]
            g = g[::-1] if h > 0 else g                                     # BMP rows run bottom-up
            turns = []
            for _ in range(4):
                mean = sum(map(sum, g)) / (w * abs(h))
                turns.append([v > mean for r in g for v in r])
                g = [list(r) for r in zip(*g[::-1])]
            out.append(turns)
        return out


def test_no_photo_shown_twice():
    """Bug (user, Fotos & Vorlagen): „die Toilette aus Mallnitz ist doppelt auf der Seite“ – toilette mallnitz.jpeg and
    bad_mallnitz.jpeg are the same photo at two sizes. No two shown copies are near-identical: their 16 x 16 average
    hashes (any 90° turn) differ in more than 16 of 256 bits (the two duplicates found: 3 and 10; the closest
    different pictures: 23). Duplicates stay in input/, listed in vorlagen.DOPPELT."""
    shown = [ROOT / "web" / "public" / "vorlagen" / b["key"] / f["file"] for b in vorlagen.BEREICHE for f in b["fotos"]]
    hashes = average_hashes(shown)
    for i, j in itertools.combinations(range(len(shown)), 2):
        d = min(sum(x != y for x, y in zip(hashes[i][0], t)) for t in hashes[j])
        assert d > 16, (shown[i].name, shown[j].name, d)


def test_json_manifest(tmp_path):
    out = tmp_path / "vorlagen.json"
    subprocess.run([sys.executable, str(ROOT / "code" / "vorlagen.py"), str(out)], check=True)
    js = json.loads(out.read_text())
    assert [b["key"] for b in js["bereiche"]] == [b["key"] for b in vorlagen.BEREICHE]
    g = next(b for b in js["bereiche"] if b["key"] == "garderobe")
    assert g["title"] and g["fotos"][0]["file"].endswith(".jpg") and g["fotos"][0]["caption"]
    assert g["fotos"][0]["src"].startswith("2026-")
