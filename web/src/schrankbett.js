// Schrankbett sub-model page (schrankbett.html): the Yoga room's wall bed of house_core.build_schrankbett()
// (code/schrankbett.py, issue #7) with the pieces of its two walls (west wall with the window, south
// wall with the Yoga door), drawn by submodel.js. Model origin: the room's inner SW corner; the room
// lies north-east (x > 0, y > 0), the Schrankwand along the south wall at x 0..2.79, y 0..0.45, the bed
// folded down to y 2.21. The bed folds up and down on the lift clock (slides.js liftingNodes).
import { startSubmodel } from './submodel.js';

await startSubmodel({
  glb: 'schrankbett.glb',
  views: {
    iso: ['Schräg', [5.4, 5.6, 3.3], [1.4, 0.9, 0.9]],             // from the room's north-east, above
    front: ['Von vorn', [1.39, 4.6, 1.3], [1.39, 0.0, 1.1]],       // facing the Schrankwand
    top: ['Von oben', [1.6, 1.4, 8.5], [1.6, 1.401, 0.0]],         // plan, north at the top
  },
  colors: { Schrankbett_Moebel: 0x8a5a2b, Schrankbett_Klappbett: 0x8a5a2b, Schrankbett_Innentueren: 0x8a5a2b,
    Schrankbett_Waende: 0x8a8a8a, Schrankbett_Fenster_Tueren: 0x4f7a5a },
  walls: [],
  grid: [1.6, 1.4],
  sun: [[3.0, 5.0, 5.0], [1.4, 0.5, 0.5]],
  hook: '__schrankbett',
});
