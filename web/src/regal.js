// "Schrank im Büro" sub-model (regal.html): the Tegernsee bookcase around the Bibliothek's east window
// of house_core.build_regal() (code/regal.py) with the pieces of its three walls (east wall with the
// window, north wall with the balcony door, Flur wall with the Büro door), drawn by submodel.js.
// Model origin: the Bibliothek's inner SE corner; the room lies west (x < 0), the bookcase stands
// along the east wall at x -0.42..0, y 0.48..3.30, the window at y 1.44..2.34.
import { startSubmodel } from './submodel.js';

await startSubmodel({
  glb: 'regal.glb',
  views: {
    iso: ['Schräg', [-4.2, -1.0, 3.0], [-0.3, 1.9, 1.0]],        // from the room's south-west, above
    front: ['Von vorn', [-4.4, 1.89, 1.5], [0, 1.89, 1.2]],        // facing the window (the drawing's view A)
    top: ['Von oben', [-0.8, 1.85, 9.5], [-0.8, 1.851, 0.0]],      // plan, north at the top
  },
  colors: { Regal_Moebel: 0x8a5a2b, Regal_Innentueren: 0x8a5a2b, Regal_Waende: 0x8a8a8a, Regal_Fenster_Tueren: 0x4f7a5a },
  walls: [],
  grid: [-0.9, 1.85],
  sun: [[-3.0, 0.5, 5.0], [-0.3, 1.9, 0.5]],
  hook: '__regal',
});
