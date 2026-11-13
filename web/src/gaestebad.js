// Gästebad sub-model page (gaestebad.html): the OG Bad at the end of the Flur of house_core.build_gaestebad()
// (code/gaestebad.py, issue #18) with the pieces of its four walls, drawn by submodel.js. Model origin:
// the room's inner SW corner; the room spans x 0..2.26, y 0..3.11: along the south wall the WC niche
// (x 0..1.01) and the shower (x 1.11..2.26, to y 1.39), the basin in the middle of the north wall.
import { startSubmodel } from './submodel.js';

await startSubmodel({
  glb: 'gaestebad.glb',
  views: {
    iso: ['Schräg', [4.6, 4.9, 4.2], [1.1, 1.5, 0.8]],             // from the Flur's side (north-east), above
    top: ['Von oben', [1.13, 1.55, 9.0], [1.13, 1.551, 0.0]],      // plan, north at the top
    door: ['Von der Tür', [2.1, 2.95, 1.6], [1.1, 0.5, 0.9]],      // inside the Flur door, looking at niche and shower
  },
  colors: { Gaestebad_Sanitaer: 0x2b5f8e, Gaestebad_Fliesen: 0x4f7a5a, Gaestebad_Waende: 0x8a8a8a,
    Gaestebad_Innentueren: 0x8a5a2b, Gaestebad_Fenster_Tueren: 0x4f7a5a },
  walls: [],
  grid: [1.13, 1.55],
  sun: [[3.0, 4.0, 5.0], [1.1, 1.5, 0.5]],
  hook: '__gaestebad',
});
