// Küche sub-model (kueche.html): the kitchen of house_core.build_kueche() (code/kueche.py) with its
// worktop rows, Wamsler cooker, hood and Besenschrank, drawn by submodel.js. Model origin: the
// kitchen's inner NW corner; the room spans x 0..3.067, y -2.82..0 (south is -y).
import { startSubmodel } from './submodel.js';

await startSubmodel({
  glb: 'kueche.glb',
  views: {
    iso: [[-1.6, -5.6, 3.8], [1.6, -1.3, 0.9]],        // from the open south-west (Essen), above
    top: [[1.53, -1.4, 8.0], [1.53, -1.399, 0.0]],     // plan, north at the top
    zeile: [[1.5, -4.6, 1.6], [1.5, 0.0, 1.0]],        // from the room onto the Spülzeile at the north wall
  },
  colors: { Kueche_Kueche: 0x8a5a2b, Kueche_Herd: 0x2b5f8e, Kueche_Haube: 0x4f7a5a, Kueche_Waende: 0x8a8a8a },
  walls: [[2.72, 2.4, [0, -1.36, 1.2], Math.PI / 2], [3.067, 2.4, [1.5335, 0, 1.2], 0],   // west, north,
          [2.82, 2.4, [3.067, -1.41, 1.2], Math.PI / 2]],                                  // east
  grid: [1.53, -1.4],
  sun: [[4.5, -5.0, 5.0], [1.5, -1.4, 0.5]],
  hook: '__kueche',
});
