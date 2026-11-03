"""Colour scheme (RAL): sets the base colour of the plain materials from PAINT in house_core.py.
Only edits materials (the white shutter cross boards are part of the house core).
Run inside Blender: exec(open(".../code/paint.py").read())  – re-running is safe.

  Fassade      RAL 9010 Reinweiß     Fenster  RAL 9010 Reinweiß
  Fensterläden RAL 5014 Taubenblau (weiße Querbretter), Ofenkacheln ebenso
  Türen bleiben Naturholz (Materialien aus build_house.py)
"""
import bpy, importlib, sys

sys.path.insert(0, "/Users/tgartner/git/frechen_blender/code")
import house_core; importlib.reload(house_core)        # pick up core edits in a long session
from house_core import PAINT


def lin(rgb):
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(v / 255) for v in rgb) + (1.0,)


def set_color(mat_name, rgb):
    m = bpy.data.materials[mat_name]
    col = lin(rgb)
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = col
    m.diffuse_color = col


def main():
    for name, rgb in PAINT.items():
        set_color("FL_" + name, rgb)


main()
