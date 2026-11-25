"""Plan versions (issue #59, ADR-005-JXWL): code/versionen.py freezes committed source snapshots and
builds each into its house .glb (with the snapshot's own exporter) and plan sheets."""
import json, re, subprocess, sys, tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "code"))
import versionen  # noqa: E402

SHEETS = {"eg", "og", "nord", "ost", "sued", "west"}


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout


@pytest.fixture
def repo(tmp_path):
    """A throw-away git repo with a committed code/ and plans/."""
    r = tmp_path / "repo"
    (r / "code").mkdir(parents=True)
    (r / "plans").mkdir()
    (r / "code" / "export_gltf.py").write_text("print('x')\n")
    (r / "plans" / "eg.svg").write_text("<svg/>\n")
    (r / "README.md").write_text("not in the snapshot\n")
    git(r, "init", "-q")
    git(r, "add", ".")
    git(r, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init")
    return r


def test_freeze_writes_snapshot_and_entry(repo):
    snap = versionen.freeze(repo, "Mit Ideen", "2026-11-07")
    assert snap == repo / "versionen" / "2026-11-07.tar.gz"
    with tarfile.open(snap) as t:
        names = set(t.getnames())
    assert {"code/export_gltf.py", "plans/eg.svg"} <= names
    assert "README.md" not in names
    assert versionen.load(repo) == [{"id": "2026-11-07", "name": "Mit Ideen"}]
    versionen.freeze(repo, "Früher", "2026-11-01")
    assert [v["id"] for v in versionen.load(repo)] == ["2026-11-01", "2026-11-07"]   # sorted by id


def test_freeze_refuses_existing_id_bad_id_and_dirty_sources(repo):
    versionen.freeze(repo, "A", "2026-11-07")
    with pytest.raises(ValueError, match="exists"):
        versionen.freeze(repo, "B", "2026-11-07")
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        versionen.freeze(repo, "B", "7.11.2026")
    with pytest.raises(ValueError, match="name"):
        versionen.freeze(repo, "  ", "2026-11-08")
    (repo / "code" / "export_gltf.py").write_text("print('changed')\n")
    with pytest.raises(ValueError, match="uncommitted"):
        versionen.freeze(repo, "B", "2026-11-08")
    assert [v["id"] for v in versionen.load(repo)] == ["2026-11-07"]


def test_listed_versions_are_well_formed():
    listed = versionen.load(ROOT)
    assert listed, "no version frozen yet"
    ids = [v["id"] for v in listed]
    assert len(set(ids)) == len(ids)
    assert ids == sorted(ids)
    for v in listed:
        assert set(v) == {"id", "name"}
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", v["id"]) and v["name"].strip()
        with tarfile.open(ROOT / "versionen" / f"{v['id']}.tar.gz") as t:
            names = set(t.getnames())
        assert "code/export_gltf.py" in names and "code/house_core.py" in names, v["id"]
        assert {f"plans/{s}.svg" for s in SHEETS} <= names, v["id"]
    assert {"id": "2026-11-25", "name": "Nach Vincent & Silvia-Ideen"} in listed


@pytest.mark.slow                                                       # one export (~5 s) per listed version
def test_build_writes_glb_plans_and_list(tmp_path):
    public, cache = tmp_path / "public", tmp_path / "cache"
    (public / "v" / "stale").mkdir(parents=True)                       # a version no longer listed
    listed = versionen.load(ROOT)
    assert versionen.build(ROOT, public, cache) == len(listed)          # one export per version
    for v in listed:
        d = public / "v" / v["id"]
        assert (d / "frechenlehen.glb").read_bytes()[:4] == b"glTF"
        assert {p.stem for p in (d / "plans").glob("*.svg")} == SHEETS
    assert not (public / "v" / "stale").exists()
    assert json.loads((public / "versionen.json").read_text()) == list(reversed(listed))   # newest first
    glb = public / "v" / listed[0]["id"] / "frechenlehen.glb"
    before = glb.stat().st_ino
    assert versionen.build(ROOT, public, cache) == 0                    # second run: all from the cache
    assert glb.stat().st_ino == before                                  # and an unchanged version is not copied again


def test_build_refuses_an_id_that_is_no_date(repo, tmp_path):
    (repo / "versionen").mkdir()
    (repo / "versionen" / "versionen.json").write_text('[{"id": "../escape", "name": "x"}]')
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        versionen.build(repo, tmp_path / "public", tmp_path / "cache")
    assert not (tmp_path / "public").exists()
