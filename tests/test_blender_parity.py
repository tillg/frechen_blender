"""The Blender build must match the golden snapshot (tests/golden/blender_snapshot.json).

Runs headless Blender on tests/blender/snapshot.py. Regenerate the golden on purpose with
    UPDATE_GOLDEN=1 python3 -m pytest -q tests/test_blender_parity.py
"""
import json, os, subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
BLENDER = os.environ.get("BLENDER", "/Applications/Blender.app/Contents/MacOS/Blender")
GOLDEN = ROOT / "tests" / "golden" / "blender_snapshot.json"


def snapshot(tmp_path):
    out = tmp_path / "snapshot.json"
    subprocess.run([BLENDER, "-b", "--factory-startup", "--python",
                    str(ROOT / "tests" / "blender" / "snapshot.py"), "--", str(out)],
                   check=True, capture_output=True, text=True)
    return json.loads(out.read_text())


def diff(old, new):
    keys = sorted(set(old) | set(new))
    return {k: {"golden": old.get(k), "now": new.get(k)} for k in keys if old.get(k) != new.get(k)}


@pytest.mark.slow
def test_rebuild_matches_golden_snapshot(tmp_path):
    snap = snapshot(tmp_path)
    if os.environ.get("UPDATE_GOLDEN"):
        GOLDEN.parent.mkdir(exist_ok=True)
        GOLDEN.write_text(json.dumps(snap, indent=1, sort_keys=True) + "\n")
    golden = json.loads(GOLDEN.read_text())
    d = diff(golden, snap)
    assert not d, "objects differ from golden:\n" + json.dumps(d, indent=1)[:4000]


@pytest.mark.slow
def test_saved_blend_matches_golden(tmp_path):
    """frechenlehen.blend is generated output: it must be the current build, saved."""
    out = tmp_path / "saved.json"
    subprocess.run([BLENDER, "-b", str(ROOT / "frechenlehen.blend"), "--python",
                    str(ROOT / "tests" / "blender" / "snapshot.py"), "--", str(out), "--saved"],
                   check=True, capture_output=True, text=True)
    d = diff(json.loads(GOLDEN.read_text()), json.loads(out.read_text()))
    assert not d, "saved .blend differs from golden:\n" + json.dumps(sorted(d))[:2000]
