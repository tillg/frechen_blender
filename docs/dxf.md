# The DXF format

A primer: how a DXF file is built, what it can hold, how its parts refer to each other and how it
can include other files. Section 8 records why the house is not described in DXF.

## 1. Encoding: group code / value pairs

A DXF file is a flat sequence of pairs, each on two lines: a **group code** (integer) and a
**value**. The code gives the value its meaning: `0` starts a new item, `8` is the layer, `10/20/30`
are x/y/z, `5` is the item's handle, `62` a colour.

```
  0          ← start of an item
MESH         ← its type
  5          ← handle (unique id, hex)
2A7
330          ← owner handle (the block record it belongs to)
1F
  8          ← layer
FL_Putz
 10          ← vertex x / y / z
14.73
 20
6.528
 30
0.0
```

Two encodings exist: ASCII (readable, diffable) and binary (smaller, same structure). Versions:
R12 = `AC1009` (simplest, no handles needed), R2000 = `AC1015`, … R2018 = `AC1032` (newest).

## 2. Sections

```
HEADER   variables: $ACADVER, $INSUNITS (6 = metres), $EXTMIN/MAX, custom properties …
CLASSES  declares the newer item types used (MESH, MATERIAL, …)
TABLES   named resources: LAYER, LTYPE, STYLE, DIMSTYLE, VPORT, VIEW, UCS,
         APPID (registered XDATA owners), BLOCK_RECORD
BLOCKS   block definitions: BLOCK … items … ENDBLK
ENTITIES the drawing itself (model space and the active paper space)
OBJECTS  non-graphical data: DICTIONARY, XRECORD, GROUP, LAYOUT, MATERIAL, IMAGEDEF …
```

## 3. What can be represented (entities)

| Kind | Entities |
|---|---|
| 2D lines and curves | `LINE`, `ARC`, `CIRCLE`, `ELLIPSE`, `LWPOLYLINE` (2D, bulges = arcs), `POLYLINE`, `SPLINE`, `XLINE`/`RAY` |
| Areas | `HATCH` (fill patterns, e.g. wall hatching in a Grundriss), `SOLID` (filled triangle/quad), `REGION` |
| Annotation | `TEXT`, `MTEXT`, `DIMENSION` (linear, aligned, angular, radial …), `LEADER`, `MULTILEADER`, `TOLERANCE` |
| 3D surfaces | `3DFACE` (3–4 corners), `POLYLINE` as polyface or grid mesh (faces ≤ 4 corners), **`MESH`** (n-gon faces, edges, creases, subdivision level; see section 9) |
| 3D solids | `3DSOLID`, `BODY`, `SURFACE`: an opaque ACIS/ShapeManager blob, readable only by a CAD kernel |
| Placement | `INSERT` (places a block), `ATTRIB`/`ATTDEF` (text fields on a block reference, e.g. a door number) |
| Points, lights | `POINT`, `LIGHT` |
| External pictures | `IMAGE` (raster file), `PDFUNDERLAY` / `DWFUNDERLAY` / `DGNUNDERLAY` |
| Layout | `VIEWPORT` (paper-space windows into model space) |

Common properties of every entity: layer (`8`), colour (`62` index colour or `420` true colour),
linetype (`6`), line weight (`370`), transparency (`440`), material (`347`, handle of a `MATERIAL`).
Each can be "ByLayer" or "ByBlock" (inherited from the layer or from the block reference).

2D entities live in an Object Coordinate System given by an extrusion vector (`210/220/230`), so a
circle can lie in a tilted plane. 3D entities (`MESH`, `3DFACE`, `POINT`) use world coordinates.

## 4. How items refer to each other

**By name.** An entity names its layer, linetype, text style, dimension style and (an `INSERT`) its
block as strings; the named item must exist in TABLES or BLOCKS.

**By handle.** Every item (R2000+) has a unique hex handle (`5`); pointers use these handles:

```
330  soft owner      entity → its block record; dictionary entry → dictionary
340  hard pointer    e.g. HATCH → boundary, MLEADER → style
350  soft owner      dictionary → its entries
360  hard owner      e.g. extension dictionary → XRECORD
{ACAD_REACTORS … }      back-pointers: "who depends on me"
{ACAD_XDICTIONARY … }   the entity's own extension dictionary
```

The ownership tree:

```
root DICTIONARY (OBJECTS)
 ├─ ACAD_LAYOUT ─ LAYOUT "Model" ─▶ BLOCK_RECORD *Model_Space ─▶ entities
 ├─ ACAD_MATERIAL ─ MATERIAL …
 ├─ ACAD_GROUP ─ GROUP (named selection set of entity handles)
 └─ own entries ─ XRECORD (arbitrary data)
BLOCK_RECORD table ─ one per block (incl. *Model_Space, *Paper_Space)
```

Model space is itself a special block (`*Model_Space`); every entity is owned by a block record.

**No real hierarchy:** layers are flat (`EG|Wände` is only a naming convention). Blocks are the only
true nesting (blocks can `INSERT` other blocks, any depth). `GROUP` objects are named selections
without a transform.

## 5. Blocks: reuse inside one file

```
BLOCKS:   BLOCK "Fenster_120"  base point (0,0,0)
            MESH …  MESH …  ATTDEF "Nr"
          ENDBLK
ENTITIES: INSERT "Fenster_120"  at (3.2, 0, 0.9)  rotation 90°  scale 1,1,1
          INSERT "Fenster_120"  at (7.8, 0, 0.9)  …
          MINSERT …  (rectangular array of the same block)
```

- Each `INSERT` carries a transform: insertion point, x/y/z scale, rotation about its extrusion,
  extrusion vector.
- Nested inserts multiply the transforms. Changing the definition changes every insert.
- Items inside a block on layer `0` or with "ByBlock" properties take the layer/colour of each
  `INSERT`: one window block can sit on layer `EG` here and `OG` there.

## 6. Including other files

1. **XREF (external reference).** A block definition flagged *external* (block flag 4; flag 8 =
   *overlay* instead of *attach*) with a file path (group code `1`) and no contents of its own. The
   CAD tool loads the other file's model space into it on open. An `INSERT` of that block places the
   other file with a transform, like any block. The xref's layers appear as `ofen|FL_Putz`.
   *Attach* passes nested xrefs on, *overlay* doesn't. Paths may be absolute or relative.
   AutoCAD, BricsCAD & co. resolve xrefs; simple viewers often show nothing. In Python, `ezdxf`
   (≥ 1.1) has `ezdxf.xref` to attach, load and embed; nothing is resolved automatically, a reader
   has to resolve them itself.
2. **Copying blocks** between files (import the block definition): a one-time copy, no live link.
3. **Underlays / images:** a PDF, DWF, DGN or raster file placed as visual reference only, no
   geometry. A PDF underlay of the architect's plan under layer `EG` would be an alignment aid.

## 7. Own data

| Mechanism | Holds | Notes |
|---|---|---|
| **XDATA** | Typed values on one entity under a registered APPID (`1000` string, `1040` real, `1010` point, `1070` int, `1002 {` `}` nesting) | ≤ 16 KB per entity; CAD tools keep it on copy. Would fit `rnd`, pivot, turn, smooth. |
| **Extension dictionary + XRECORD** | Any amount of tagged data per entity | Bigger, structured. |
| **XRECORD in the root dictionary** | File-wide data | E.g. a garden layout, if it ever moved into the DXF. |
| **Header custom properties** | Key/value strings | Shown in the CAD tool's drawing properties. Would fit plan constants (`Z_OG`, …). |
| **`MATERIAL` objects** | Render materials, linkable from layers/entities | Only roughly like `MAT_DEF` (no procedural wood). |

## 8. What this means for this project

**Decision (2026-11-09): the Python core stays the source** (ADR-001-XEWL). Making 3D DXF files
the source was considered and dropped: the core describes the house parametrically (moving a
window is one opening tuple; wall cut, frame, shutters, cross boards and cladding follow), while a
mesh DXF holds only the result (the same move would be 10+ separate `MESH` edits with matching
`rnd` values). CAD tools edit meshes poorly, and an architect works in 2D or BIM, not in a mesh
DXF. For viewing and exchange, a DXF **exported** from the core gives the same benefit.

If such an export is ever built, these findings apply:

- **Mapping:** only robust, widely supported parts: `MESH` per Part (no vertex merging), block +
  one `INSERT` per object, layers per collection and per material, XDATA (`rnd`, object flags),
  `POINT`s for light sites and fire beds, `DIMENSION`s, header properties for plan constants. No
  ACIS.
- **Floats** round-trip exactly with `ezdxf` 1.4.5 (`MESH` vertices come back as `np.float64`,
  equal after `float()`; XDATA `1040`, `POINT` and header values exact, incl. `-0.0`), so a `.glb`
  rebuilt from the DXF could be byte-identical.
- **Size and speed:** the house as 9,989 `MESH` is ~18 MB of ASCII DXF; `ezdxf.readfile` takes
  ~1.6 s.
- **Ofen and desk** inside the house could be XREFs to their own files (insertion point and
  rotation instead of copies); the transform changes the house's floats, so byte identity is lost.
- Repeated parts (windows, shutters, chairs) could become one block with many inserts: smaller
  files, same caveat.

## 9. What a MESH is

A **mesh** is the way 3D software stores a surface: not as a mathematical description of a shape
("a cylinder of radius 0.2 m"), but as a list of **corner points (vertices)** and a list of flat
**faces** that connect them. Every face is a polygon: it names, in order, which vertices form its
outline.

A box of 1 × 1 × 1 m as a mesh:

```
vertices (8):                         faces (6), each a list of vertex numbers:
 0 (0,0,0)   4 (0,0,1)                 bottom  0 3 2 1        front  0 1 5 4
 1 (1,0,0)   5 (1,0,1)                 top     4 5 6 7        right  1 2 6 5
 2 (1,1,0)   6 (1,1,1)                 back    2 3 7 6        left   3 0 4 7
 3 (0,1,0)   7 (0,1,1)

        7 ─────── 6
       /|        /|
      4 ─────── 5 |
      | 3 ──────|─2
      |/        |/
      0 ─────── 1
```

Properties:

- **Only flat faces.** A round shape (the Ofen's rounded corner, a lamp shade) is approximated by
  many narrow faces; the finer, the rounder. Smooth shading (`SMOOTH`) only *looks* round.
- **Faces share vertices** by number: moving vertex 6 moves the corner of top, back and right face.
- **The order of a face's vertices** gives its direction (which side is "outside"): counter-clockwise
  seen from outside, by convention. Our core doesn't keep it consistent; `mesh_ops.orient()` (and
  Blender) fix it.
- **A face can have any number of corners** (an *n-gon*), also concave ones (an L-shaped slab). For
  drawing, the GPU splits every face into triangles (`mesh_ops.triangulate()`).
- **A mesh is just a surface.** It knows nothing about being a "wall" or "solid"; it is *closed*
  (watertight) if every edge belongs to exactly two faces, like the box. Each of our Parts is a
  closed mesh.

The DXF `MESH` entity stores exactly this: a vertex list (group code `10/20/30` per vertex), a face
list (`93` = total count, then per face its corner count and vertex numbers as `90` values), and
optionally edges, creases and a subdivision level (from AutoCAD's smooth-mesh modelling; we don't
use them). Unlike the older `3DFACE` (≤ 4 corners), a `MESH` face can have any number of corners, so
our Parts (up to 360 corners per face) fit without being cut into triangles.

**Mesh vs. solid.** A CAD *solid* (`3DSOLID`) is the other way to store 3D: an exact, mathematical
boundary description (planes, cylinders, NURBS) from a modelling kernel (ACIS), on which a CAD
tool can do Boolean operations ("subtract the window opening from the wall"). It is exact and
editable as a construction, but opaque in DXF without that kernel. A mesh is simple, universal,
what every renderer (three.js, Blender) draws — and what our core already produces.
