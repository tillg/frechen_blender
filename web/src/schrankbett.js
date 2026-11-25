// Schrankbett sub-model page (schrankbett.html): the Yoga room's wall bed of house_core.build_schrankbett()
// (code/schrankbett.py, issue #7) with the pieces of its two walls (west wall, plain since 2026-11-25; north
// wall), drawn by submodel.js. Model origin: the room's inner NW corner (since 2026-11-25 the bed stands on
// the north wall, in the corner with the west wall); the room lies south-east (x > 0, y < 0), the case at
// x 0..1.50, y -0.45..0, the bed folded down to y -2.21. The bed folds up and down on the lift clock
// (slides.js liftingNodes).
import { startSubmodel } from './submodel.js';

await startSubmodel({
  glb: 'schrankbett.glb',
  views: {
    iso: ['Schräg', [4.4, -4.8, 3.3], [0.75, -1.0, 0.9]],          // from the room's south-east, above
    front: ['Von vorn', [0.75, -4.6, 1.3], [0.75, 0.0, 1.1]],       // facing the wall bed
    top: ['Von oben', [1.0, -1.3, 8.5], [1.0, -1.299, 0.0]],        // plan, north at the top
  },
  colors: { Schrankbett_Moebel: 0x8a5a2b, Schrankbett_Klappbett: 0x8a5a2b, Schrankbett_Innentueren: 0x8a5a2b,
    Schrankbett_Waende: 0x8a8a8a },
  walls: [],
  grid: [1.0, -1.3],
  sun: [[3.0, -5.0, 5.0], [0.8, -1.0, 0.5]],
  hook: '__schrankbett',
});
