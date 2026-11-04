"""code/fire.py: the flickering-fire component. Its layout part is pure Python (no bpy), so the
glTF export and the viewer draw the same tongues as Blender."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "code"))
import fire  # noqa: E402


def test_importable_without_blender():
    assert "bpy" not in sys.modules and fire.bpy is None


def test_tongues_fill_the_bed_and_scale_with_it():
    t = fire.tongues(0.48, 0.45)
    assert len(t) == 8                                                    # one per ~6 cm
    assert all(-0.24 <= x["u"] - x["w"] / 2 and x["u"] + x["w"] / 2 <= 0.24 for x in t)
    assert all(0 < x["h"] <= 0.45 for x in t) and max(x["h"] for x in t) > 0.35
    mid = min(t, key=lambda x: abs(x["u"]))
    edge = max(t, key=lambda x: abs(x["u"]))
    assert mid["h"] > edge["h"]                                           # tallest in the middle
    small = fire.tongues(0.14, 0.24)
    assert len(small) == 2 and max(x["h"] for x in small) <= 0.24       # a small stove: fewer, lower
    big = fire.tongues(0.96, 0.90)
    assert len(big) == 16 and max(x["h"] for x in big) > 0.7


def test_tongues_are_deterministic_and_out_of_phase():
    a, b = fire.tongues(0.48, 0.45), fire.tongues(0.48, 0.45)
    assert a == b
    assert len({round(x["phase"], 3) for x in a}) == len(a)              # each flickers on its own
    assert all(0.5 < x["speed"] < 2 for x in a)
