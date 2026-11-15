"""The Blender backend is dormant (issue #35): nothing runs it, but its scripts must still compile,
so Blender can be switched back on cheaply. Syntax only; bpy is not imported."""
from pathlib import Path

import pytest

CODE = Path(__file__).resolve().parent.parent / "code"
SCRIPTS = ("build_house", "fire", "paint", "windrose", "garden", "film")   # the rebuild order


@pytest.mark.parametrize("name", SCRIPTS)
def test_blender_script_compiles(name):
    path = CODE / f"{name}.py"
    compile(path.read_text(), str(path), "exec")
