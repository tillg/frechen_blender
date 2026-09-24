# Frechenlehen – Blender-Modell

3D-Modell des Hauses, erzeugt aus den ALLPLAN-Plänen (Grundriss EG/OG, Ansichten, M 1:100).

## Struktur

| Pfad | Inhalt |
|---|---|
| `input/` | Eingangsdaten: die 3 PDFs, daraus gerenderte Grundriss-Bilder (`grundriss_eg/og.png`, im Modell als ausgeblendete Referenz), Farbvorlagen (`farben_*.png`) |
| `code/` | Python-Skripte, laufen in Blender (z. B. über den Blender-MCP-Server) |
| `frechenlehen.blend` | das Modell |
| `frechenlehen_rundgang.mp4` | Film: Rundgang außen, dann EG und OG |
| `tmp/` | Zwischenstände (Einzelbilder, Testrender, Logs) – kann gelöscht werden |

## Skripte (`code/`)

| Skript | Macht |
|---|---|
| `build_house.py` | baut das Haus komplett neu (Collection „Haus“). **Achtung:** überschreibt Handänderungen im Modell |
| `paint.py` | Farben (RAL 9010 / 5014 / 5008) und weiße Querbretter an den Läden – nach `build_house.py` erneut ausführen |
| `windrose.py` | Windrose (eigene Collection, bleibt bei Neubau erhalten) |
| `film.py` | Kamerafahrt, Raumlichter, geöffnete Haustür; Renderausgabe nach `tmp/film/` |

Ausführen in Blender: `exec(open("/Users/tgartner/git/frechen_blender/code/<skript>.py").read())`

Koordinaten: Ursprung = äußere SW-Ecke, +X = Osten, +Y = Norden, Meter.
