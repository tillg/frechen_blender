# Frechenlehen – Blender-Modell und Web-Ansicht

![Ansicht von Südosten](docs/images/ansicht_suedost.png)
![Ansicht von Nordwesten](docs/images/ansicht_nordwest.png)

3D-Modell des Hauses, erzeugt aus den Architekten-Plänen (Grundriss EG/OG, Ansichten, M 1:100).
Ein gemeinsamer Python-Kern (`code/house_core.py`, die Öfen in `code/ofen.py`) beschreibt das Haus; daraus entstehen das
Blender-Modell und die interaktive Web-Ansicht im Browser.

## Struktur

| Pfad | Inhalt |
|---|---|
| `input/` | Eingangsdaten: die aktuellen Pläne in `2026-11-03 input/` (3 PDFs, daraus gerenderte Grundriss-Bilder `grundriss_eg/og.png`, im Modell als ausgeblendete Referenz), in `processed/` ältere Pläne, Farbvorlagen (`farben_*.png`) und Detailfotos (Dateiname = Bauteil, z. B. `entrance_door_from_outside.png`); was sich zwischen den Planständen geändert hat, steht in `LOG.md` |
| `code/` | Python: der Kern `house_core.py` (ohne Blender), die Blender-Skripte (laufen in Blender, z. B. über den Blender-MCP-Server) und der glTF-Export |
| `web/` | Web-Ansicht mit three.js (Vite); `web/public/frechenlehen.glb` wird aus dem Kern erzeugt, nicht eingecheckt |
| `tests/` | Python-Tests (`pytest`), u. a. Vergleich des Blender-Neubaus mit einem gespeicherten Fingerabdruck |
| `frechenlehen.blend` | das Modell (erzeugt; nach Änderungen neu bauen und speichern) |
| `JJJJ-MM-TT_frechen_rundgang_blender.mp4`, `…_threejs.mp4` | Film: Rundgang außen, dann EG und OG (Blender-Render bzw. Web-Ansicht) |
| `docs/images/` | Ansichten für dieses README |
| `tmp/` | Zwischenstände (Einzelbilder, Testrender, Logs) – kann gelöscht werden |

## Skripte (`code/`)

| Skript | Macht |
|---|---|
| `house_core.py` | der Kern, ohne Blender: Maße, Materialdefinitionen (`MAT_DEF`), RAL-Farben, Raumlicht-Positionen, Bauteil-Funktionen und Gartenplan (Wiesenflächen, Dichte, Grasbüschel, Strauchplätze, Windrosen-Lage). Enthält alle Details nach den Fotos: Rundbogen-Haustür, Hintertür mit Ovalfenster, Stuben-Nische mit Segmentbogen, Kassettentüren innen (geöffnet), verglaste Doppeltür zum Windfang (ebenso verglast die Tür zum hinteren Windfang), Fenster mit Lärchenrahmen und Sprossen, Westfenster im OG (Yoga, Bad) mit 75 cm Brüstung und bis unter die Decke, Terrassentüren in Lärche, Lärchenschalung der ganzen Westseite und des Ostgiebels (über den Giebelfenstern als Lattung), Schiebetür vom Bad ins WC der Großeltern, Anbau mit Elektroraum und Heizung (Holzwände mit Lärchenschalung, Flachdach), Balkone in Lärche mit Baluster-Ausschnitten, Treppe mit gedrechseltem Geländer (auch um das Treppenloch im OG, darunter frei), Kalksteinplatten im EG-Flur, sonst Eichendielen (auch im OG-Flur), großer Esstisch im Stil des Briol-Tischs (Brettplatte, gespreizte Beine auf flachem Fußrahmen) mit 14 Stühlen in Küche/Essen, Küche nach Plan (Spülzeile, Zeile an der Ostwand, Halbinsel mit Kochfeld; am Nordende der Ostzeile ein Wamsler-Holzherd nach Foto mit Feuer hinter der Scheibe und Rauchrohr in die Wand, darüber eine stählerne Abzugshaube in alter Form, Hängeschränke über Spülzeile und Ostzeile), Eck-Ofen in der NW-Ecke der Stube (aus `ofen.py`), Möbel nach Plan (in der Stube eine Sitzecke zwischen den beiden großen Fenstern: rundes Tischchen mit gedrechselter Säule und zwei kleine Bouclé-Sessel nach Foto, dazu ein Dreisitzer-Sofa in Leinen nach Foto zwischen Ofen und Sitzecke, mit Blick auf den Eckpfeiler; Betten mit Nachttischen, Schränke, in der Bibliothek Flügel (30° nach links gedreht), Schreibtisch zwischen den beiden Fenstertüren der Nordwand, deckenhohe Bücherwand aus dunklem Holz mit Büchern an der Flurwand und ein kleiner Werkstattofen an der Flurwand nach Foto; im Schlafzimmer SE (OG) eine 15 cm starke Wand am Kopfende des Bettes und ein zweiter Werkstattofen in der Ecke Bad/WC, Regale in der Speis, in der Waschküche zwei Waschmaschinen (auf einer ein Trockner) und ein 80 cm tiefer Tisch über die ganze Rückwand mit zwei Stapeln gefalteter Kleidung, an der rechten Wand ein offener Schrank mit durchgehenden Böden und je drei grob geflochtenen Weidekörben; in der Jugend zwei Stockbetten), Bäder und WCs mit Dusche, Waschbecken und Hänge-WC nach Plan, im OG-Flur rechts der Waschküchentür ein tiefes Keramikbecken auf dunkler Steinplatte mit Einhebelmischer (nach Foto), Raumnamen auf dem Boden (Stube, Küche, Bibliothek, Speis, Oma & Opa; OG: Nadine & Till, Waschküche, Saschi, Bichlach, Jugend, Yoga), Sparren/Pfetten und Untersicht, Granit-Terrasse mit Kiesstreifen und Beeten, Außenleuchten, weiße Querbretter an den Läden |
| `ofen.py` | Teil des Kerns, ohne Blender: die Öfen – Eck-Ofen der Stube nach den Skizzen in `input/ofen/` (weiß verputzt, Feuer hinter Glastür in der Schräge und hinten eine zweite Feuertür in der Flurwand, zwei Bänke, Liege darüber mit dünner cremefarbener Matratze, drei Leitersprossen am Fußende und kleiner, eingeschalteter Schwanenhals-Leuchte über dem Kopfende wie auf dem Foto; siehe Teilmodell Ofen), seine Lage in der Stube, der kleine Werkstattofen und der Wamsler-Küchenherd nach Foto. `house_core.py` ruft ihn auf, damit am Ofen getrennt vom übrigen Haus gearbeitet werden kann |
| `build_house.py` | Blender-Seite: baut aus dem Kern das Haus komplett neu (Collection „Haus“), mit Materialien, Raumnamen und ausgeblendeten Referenzplänen. **Achtung:** überschreibt Handänderungen im Modell |
| `mesh_ops.py` | Dreieckszerlegung und Ausrichtung der Flächen für den glTF-Export (das macht in Blender bmesh) |
| `export_gltf.py` | schreibt den Kern als `.glb` für die Web-Ansicht: `python3 code/export_gltf.py web/public/frechenlehen.glb` (nur Standardbibliothek); mit `--ofen` nur das Ofen-Teilmodell |
| `paint.py` | Farben aus dem Kern (Putz/Fenster RAL 9010, Läden RAL 5014; Türen bleiben Naturholz) – nach `build_house.py` erneut ausführen |
| `fire.py` | loderndes Feuer als Komponente (eigene Collection `Feuer`): Flammenzungen pro Feuerstelle, skaliert auf deren Breite und Höhe, bewegt über F-Curve-Rauschen, dazu ein flackerndes Licht; dieselben Zungen zeigt die Web-Ansicht (`fire.js`). Brennt im Eck-Ofen (vorn und hinten zum Flur), in beiden Werkstattöfen und im Küchenherd |
| `windrose.py` | Windrose (eigene Collection, bleibt bei Neubau erhalten) |
| `garden.py` | Wiese (Geometry-Nodes-Streuung, im Viewport 10 %) und grüne Laubsträucher in den Erd-Beeten nach dem Gartenplan des Kerns (eigene Collection „Garten“) – nach `build_house.py` erneut ausführen. Seit der Web-Ansicht stehen die Sträucher um wenige Zentimeter anders |
| `tour.py` | die Route des Rundgangs (ohne Blender): außen herum, durch EG und OG (langsame Drehungen und Blicke in die Räume; Drehgeschwindigkeit `TURN`, Pausendauer `PAUSE` und Kamerahöhe `EYE` = 1,60 m über dem Boden sind je eine Variable), über Treppe und Haustür zurück zum Startpunkt; daraus die Kamera pro Bild – für den Film und den Rundgang in der Web-Ansicht |
| `film.py` | Kamerafahrt nach `tour.py`, Raumlichter, geöffnete Haustür; Renderausgabe nach `tmp/film/` |

Ausführen in Blender: `exec(open("/Users/tgartner/git/frechen_blender/code/<skript>.py").read())`
Reihenfolge beim Neubau: `build_house` → `fire` → `paint` → `windrose` → `garden` → `film`.

Koordinaten: Ursprung = äußere SW-Ecke, +X = Osten, +Y = Norden, Meter.

## Web-Ansicht (three.js)

Das Haus im Browser, frei drehbar, in fünf Stufen „Vom Strich zum Haus“: **Skizze** (Tuschelinien
auf Papier), **Massenmodell** (weißes Modell mit Schatten), **Detailmodell** (echte Materialien,
Tag), **Gebaut** (Abend, warmes Licht in den Räumen, Außenleuchten an) und **Eingerichtet** (wie Gebaut, mit Möbeln nach Plan). Unten Abspielen, Zeitleiste und die
Stufen; oben rechts „Ganzes Haus / Ohne Dach / Nur EG“, Tag/Abend und „Ofen“ (springt ins
Teilmodell Ofen). Für Desktop-Browser.

**Rundgang** (oben rechts): dieselbe Kamerafahrt wie im Film, live im Browser mit 0,75-facher
Geschwindigkeit (Stufe Eingerichtet, ganzes Haus, Haustür offen; die Schnitt-Knöpfe sind solange
aus). Die Route endet, wo sie beginnt; mit „Endlos“ läuft sie ohne Sprung immer wieder. Unten
Abspielen/Anhalten, Zeitleiste, „Endlos“ und „Beenden“ (zurück zur vorigen Kameraposition);
angehalten kann man sich mit der Maus umschauen.

Teilmodell **Ofen** (`ofen.html`): der Eck-Ofen der Stube nach den Skizzen in `input/ofen/` mit
Feuertür (Feuer hinter Glas), unten hohl auf vier Beinen mit Bögen auf allen drei Seiten, zwei
Bänken (lange Bank 1,60 m) und Liege darüber (1,90 m; Rand nur an den freien Kanten: einzelne
senkrechte 5-cm-Bretter mit 10 cm Luft an Wand, Ecken und Fußende; darauf eine dünne cremefarbene
Matratze), mit Maßen (angenommene Maße kursiv).
Ansichten schräg, von oben und auf die Feuertür; Darstellung als Drahtmodell (10-cm-Raster),
Masse oder gerendert; „← Haus“ führt zurück. Schlichte Bankbeine (Vierkant mit Querriegel, nach bank-schlicht.png), Oberkante des Ofens gerundet. Derselbe Ofen steht im Haus (ohne Maße) in allen Stufen.

- Online: <https://tillg.github.io/frechen_blender/> (wird bei jedem Push auf `main` neu gebaut)
- Lokal: `cd web && npm install && npm run dev` – erzeugt zuerst das `.glb` aus dem Kern; danach Haus unter `http://localhost:5377/`, Ofen unter `http://localhost:5377/ofen.html`, der Produktions-Build (`npm run build`, wie auf GitHub Pages) unter `http://localhost:5377/frechen_blender/` (immer nur ein Server, fester Port 5377; auch die Tests laufen gegen ihn). Wird eine Datei in `code/` gespeichert, erzeugt der Server das `.glb` neu und lädt die Seite nach – an derselben Stelle, denn die Ansicht steht in der URL (Haus: Kamera, Blickpunkt, Stufe, Schnitt, optional `fov=` als vertikales Sichtfeld in Grad, Standard 28; Ofen: Kamera, Blickpunkt, Darstellung). So lässt sich eine Ansicht auch als Link weitergeben.
  (braucht `python3`) und öffnet dann die Seite.

Jede Änderung am Haus geschieht einmal im Kern (`code/house_core.py`, Öfen in `code/ofen.py`) und erscheint in Blender und im
Browser.

## Tests

- Python (ohne Blender, der Paritätstest startet Blender selbst im Hintergrund):
  `python3 -m pytest -q`
- Web: `cd web && npm test && npx playwright test` (Screenshots nach `tmp/web/`)
