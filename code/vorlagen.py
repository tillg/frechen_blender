"""Vorlagen (issue #31): the reference pictures in input/, sorted by where they belong in the house.

Pure Python, no bpy. BEREICHE is the one list: per Bereich (area) its key, title, the PLAN_ROOMS room
it lies in, the anchor of its marker in the house viewer (x, y, z in house coordinates; None: no
marker) and its pictures (source under input/, copy file name, German caption); a picture that repeats
a shown one is listed in DOPPELT instead. export_gltf.py writes
the anchored Bereiche to scene.extras.vorlagen (web/src/markers.js); `python3 code/vorlagen.py
<out.json>` writes the manifest for the photo pages (web/vorlagen.html, npm run blueprint).
`python3 code/vorlagen.py --copy` (once, macOS sips) puts the downsized copies (longest side
<= MAX_PX, JPEG) into web/public/vorlagen/<key>/; they are committed.
"""
import json, re, subprocess, sys
from pathlib import Path

import house_core

ROOT = Path(__file__).resolve().parent.parent
MAX_PX = 1600                                   # longest side of a copy


def foto(src, caption, file=None):
    """A picture: `src` under input/, its copy's file name (default: the source's name, ASCII,
    .jpg) and caption."""
    stem = Path(src).stem.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        stem = stem.replace(a, b)
    return {"src": src, "file": file or re.sub(r"[^a-z0-9_-]+", "_", stem).strip("_") + ".jpg", "caption": caption}


BEREICHE = [
    {"key": "stube", "title": "Stube", "room": ("Stube", "EG"), "at": (11.6, 3.4, 1.6), "fotos": [
        foto("2026-09-24 input/ofen_stuben.jpg", "Kachelofen mit Ofenbank – das Vorbild für den Ofen der Stube"),
        foto("2026-11-04 input/IMG_6409.jpeg", "Skizze: der Ofen von oben, 120 × 120 cm, die Feuertür über Eck"),
        foto("2026-11-04 input/IMG_6410.jpeg", "Skizze: Ofen und Wand mit Maßen"),
        foto("2026-11-04 input/Pasted 04-11-2026 at 07.49.12.png", "Entwurf der Stube: das Ofenbett über dem Ofen, mit Regal und Lampe",
             "stube_entwurf.jpg"),
        foto("2026-11-03 input/bank-schlicht.png", "Schlichte Bank mit Kissen – die Ofenbank"),
        foto("2026-11-05 input/sofa.tiff", "Dreisitzer in Leinen – das Sofa"),
        foto("2026-11-05 input/sessel-klein.jpg", "Kleiner Sessel – die zwei Sessel der Sitzecke"),
        foto("2026-11-05 input/tischchen.jpeg", "Rundes Tischchen zwischen den Sesseln"),
        foto("2026-09-24 input/shape_door_into_stuben.jpeg", "Tiefe Rundbogennische – der Durchgang vom Flur in die Stube"),
    ]},
    {"key": "kueche", "title": "Küche & Essen", "room": ("Küche", "EG"), "at": (6.6, 3.0, 1.6), "fotos": [
        foto("2026-11-10 input/kueche_mallnitz.png", "Küche in Mallnitz – weiße Rahmenfronten, schwarze Arbeitsplatte"),
        foto("2026-11-05 input/wamsler.jpeg", "Wamsler-Holzherd"),
        foto("2026-11-09 input/speis_kueche_v6.png", "Abgestimmte Zeichnung Speis & Küche (v6)"),
        foto("2026-11-05 input/tisch-briol.png", "Wirtshaustisch im Briol – der Esstisch"),
        foto("2026-09-24 input/table_shape.png", "Tische mit Bockgestell – die Form des Esstischs"),
        foto("2026-11-05 input/stuhl.png", "Brettstuhl mit Herz – die Stühle am Esstisch"),
    ]},
    {"key": "garderobe", "title": "Garderobe & Gäste-WC", "room": ("Garderobe", "EG"), "at": (1.85, 6.4, 1.6), "fotos": [
        foto("2026-11-10 input/garderobe mallnitz.jpeg", "Garderobe in Mallnitz – Bank, Hakenleiste, Hutablage"),
        foto("2026-11-10 input/toilette mallnitz.jpeg", "Toilette in Mallnitz – grüne Fliesen und Spiegel, bei uns werden die Fliesen blau"),
        foto("2026-09-24 input/back_door_of_the_house.jpg", "Die Hintertür"),
    ]},
    {"key": "windfang", "title": "Haupteingang & Windfang", "room": ("Neuer Windfang", "EG"), "at": (13.5, 7.5, 1.6), "fotos": [
        foto("2026-09-24 input/entrance_door_from_outside.png", "Haustür mit Rundbogen, von außen"),
        foto("2026-09-24 input/main_door_seen_from_inside.jpeg", "Der Eingang von innen"),
        foto("2026-09-24 input/door_windfang.jpg", "Verglaste Doppeltür des Windfangs"),
    ]},
    {"key": "bibliothek", "title": "Bibliothek & Büro", "room": ("Bibliothek", "EG"), "at": (12.9, 10.4, 1.6), "fotos": [
        foto("2026-11-11 input/regal_tegernsee.jpeg", "Regalwand vom Tegernsee – der Schrank im Büro"),
        foto("2026-11-12 input/schreibtischgestell.jpg", "Gusseisernes Kurbelgestell – der Schreibtisch"),
        foto("2026-11-13 input/bürostuhl.png", "Bürostuhl"),
        foto("2026-11-06 input/screen_a12.png", "Bildschirm A12 – das Bild auf dem Monitor"),
        foto("2026-11-06 input/screen_pilcrow.png", "Bildschirm Pilcrow – das Bild auf dem zweiten Monitor"),
    ]},
    {"key": "bad", "title": "Bad Oma & Opa", "room": ("Bad Großeltern", "EG"), "at": (1.7, 10.6, 1.6), "fotos": [
        foto("2026-11-12 input/waschbecken_doppelt.jpg", "Doppelwaschbecken"),
        foto("2026-11-08 input/grosseltern_v4.png", "Abgestimmte Zeichnung EG Großeltern (v4)"),
        foto("2026-11-08 input/plan_grosseltern_bad.jpeg", "Handskizze des Bads"),
    ]},
    {"key": "gaestebad", "title": "Gästebad", "room": ("Bad", "OG"), "at": (1.7, 7.3, house_core.Z_OG + 1.6), "fotos": [
        foto("2026-11-15 input/badewanne.webp", "Freistehende Badewanne auf Löwenfüßen – die Wanne des Gästebads, Kopfende zur Dusche"),
    ]},
    {"key": "aussen", "title": "Außen & Garten", "room": None, "at": (6.0, -1.5, 1.6), "fotos": [
        foto("2026-09-24 input/farben_beispiel_haus.png", "Farbbeispiel: weißes Haus mit farbigen Läden"),
        foto("2026-09-24 input/farben_ral.png", "RAL-Karten: 9010 Fassade, 5014 Läden, 5008 Tür"),
        foto("2026-09-24 input/window_from_outside.jpeg", "Lärchenfenster mit Sprossen in weißer Laibung"),
        foto("2026-09-24 input/window_from_outside.png", "Kleines Fenster mit dunklen Holzläden", "window_from_outside_laeden.jpg"),
        foto("2026-09-24 input/balcony_structure.png", "Balkon aus Lärche mit gedrechselten Stäben"),
        foto("2026-09-24 input/outside_wall_structure_back_of_the_house.png", "Lärchenschalung an der Rückseite (West)"),
        foto("2026-09-24 input/glass_door_to_terrasse.png", "Verglaste Lärchentür zur Terrasse"),
        foto("2026-09-24 input/terrasse_and_outside_lamps.jpeg", "Terrasse: Granitplatten, Kiesstreifen, Außenlampe"),
        foto("2026-09-24 input/outdoor_lamp.jpeg", "Außenlampe mit Schwanenhals"),
        foto("2026-09-24 input/bushes_around_the_house.png", "Sträucher ums Haus"),
        foto("2026-09-24 input/grass_in_front_of_house.png", "Hohe Wiese vor dem Haus"),
    ]},
    {"key": "haus", "title": "Ganzes Haus", "room": ("Flur", "OG"), "at": (6.0, 7.4, house_core.Z_OG + 1.6), "fotos": [
        foto("2026-11-13 input/wandlampe.png", "Wandlampe aus Messing mit Opalglas – in allen Zimmern"),
        foto("2026-11-12 input/waschbecken_einzeln.jpeg", "Das Standard-Waschbecken (einzeln) – WCs und Bäder"),
        foto("2026-11-12 input/waschbecken_staender.png", "Sein Ständer aus Chrom"),
        foto("2026-11-05 input/waschbecken-briol.jpeg", "Waschbecken im Briol"),
        foto("2026-11-03 input/werkstattofen.jpeg", "Werkstattofen – Bibliothek, Oma & Opa, 1. Stock"),
        foto("2026-09-24 input/inside_floor_rooms.jpg", "Eichendielen – der Boden der Zimmer"),
        foto("2026-09-24 input/stone_floor_corridor.jpg", "Kalksteinplatten – Flure, WCs und Bäder"),
        foto("2026-09-24 input/door_inside_1st_floor.jpg", "Zimmertür aus Kiefer mit Füllungen"),
        foto("2026-09-24 input/stairs_indoor.png", "Holztreppe mit gedrechselten Stäben"),
    ]},
    {"key": "plaene", "title": "Pläne", "room": None, "at": None, "fotos": [
        foto("2026-11-03 input/grundriss_eg.png", "Grundriss Erdgeschoss, neuer Entwurf (3. 11. 2026)", "grundriss_eg.jpg"),
        foto("2026-11-03 input/grundriss_og.png", "Grundriss 1. Stock, neuer Entwurf (3. 11. 2026)", "grundriss_og.jpg"),
        foto("2026-09-23 input/grundriss_eg.png", "Grundriss Erdgeschoss, Bestand (23. 9. 2026)", "grundriss_eg_bestand.jpg"),
        foto("2026-09-23 input/grundriss_og.png", "Grundriss 1. Stock, Bestand (23. 9. 2026)", "grundriss_og_bestand.jpg"),
    ]},
]

# pictures of input/ that are the same photo as a shown one (another size or crop): not shown; duplicate -> kept
DOPPELT = {
    "2026-11-08 input/bad_mallnitz.jpeg": "2026-11-10 input/toilette mallnitz.jpeg",                 # 768 x 1024
    "2026-11-03 input/ofenbett-1200x800.jpg": "2026-11-04 input/Pasted 04-11-2026 at 07.49.12.png",  # 1200 x 800
}


def manifest():
    """The manifest of the photo pages (JSON-able)."""
    return {"bereiche": [{"key": b["key"], "title": b["title"], "fotos": b["fotos"]} for b in BEREICHE]}


def copy(out=ROOT / "web" / "public" / "vorlagen"):
    """Downsized JPEG copies of every picture (macOS sips): longest side <= MAX_PX."""
    for b in BEREICHE:
        (out / b["key"]).mkdir(parents=True, exist_ok=True)
        for f in b["fotos"]:
            src, dst = ROOT / "input" / f["src"], out / b["key"] / f["file"]
            size = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(src)],
                                  check=True, capture_output=True, text=True).stdout
            px = max(int(n) for n in re.findall(r"pixel\w+: (\d+)", size))
            subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "80",
                            *(["-Z", str(MAX_PX)] if px > MAX_PX else []), str(src), "--out", str(dst)],
                           check=True, capture_output=True)


if __name__ == "__main__":
    if sys.argv[1] == "--copy":
        copy()
    else:
        Path(sys.argv[1]).parent.mkdir(parents=True, exist_ok=True)
        Path(sys.argv[1]).write_text(json.dumps(manifest(), ensure_ascii=False, indent=1))
