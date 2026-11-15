// Bad Nadine & Till sub-model page (elternbad.html): the OG Bad between Waschküche and Schlafzimmer of
// house_core.build_elternbad() (code/elternbad.py, issue #3) with the pieces of its four walls, drawn by
// submodel.js. Model origin: the room's inner SW corner; the room spans x 0..3.00, y 0..2.22: two showers on
// a strip along the west wall (glass at x 0.90, the 60 passage in the middle, #33), the toilet on the north
// wall, the basin on the east wall north of the door, the door at the south end of the east wall.
import { startSubmodel } from './submodel.js';

await startSubmodel({
  glb: 'elternbad.glb',
  views: {
    iso: ['Schräg', [6.4, 5.0, 5.0], [1.5, 1.1, 0.7]],              // from the Schlafzimmer's side (east), above
    top: ['Von oben', [1.5, 1.11, 9.0], [1.5, 1.111, 0.0]],         // plan, north at the top
    door: ['Von der Tür', [3.7, 0.72, 1.65], [0.0, 1.11, 1.0]],    // in the doorway (Schlafzimmer side), looking through the passage
  },
  colors: { Elternbad_Sanitaer: 0x2b5f8e, Elternbad_Spiegel: 0x2b5f8e, Elternbad_Wandlampen: 0x8a6a2b,
    Elternbad_Fliesen: 0x4f7a5a, Elternbad_Waende: 0x8a8a8a,
    Elternbad_Innentueren: 0x8a5a2b, Elternbad_Fenster_Tueren: 0x4f7a5a },
  walls: [],
  grid: [1.5, 1.11],
  sun: [[3.0, -2.0, 5.0], [1.5, 1.1, 0.5]],
  hook: '__elternbad',
});
