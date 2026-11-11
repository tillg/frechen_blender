// Ofen sub-model (ofen.html): the corner stove of house_core.build_ofen() in the room corner,
// drawn by submodel.js.
import { INK } from './ink.js';
import { startSubmodel } from './submodel.js';

await startSubmodel({
  glb: 'ofen.glb',
  views: {
    iso: ['Schräg', [5.0, 4.4, 3.0], [1.4, 0.8, 0.5]],
    top: ['Von oben', [1.701, 1.1, 8.5], [1.7, 1.1, 0.0]],     // plan, oriented like the sketch (walls top and left)
    front: ['Auf die Feuertür', [3.6, 3.6, 1.0], [0.95, 0.95, 0.6]],   // onto the fire door
  },
  colors: { Ofen_Koerper: INK, Ofen_Feuertuer: 0xb0412e, Ofen_Bett: 0x8a5a2b, Ofen_Bettrand: 0x8a5a2b, Ofen_Bank: 0x8a5a2b },
  walls: [[3.5, 2.4, [1.75, 0, 1.2], 0], [3.5, 2.4, [0, 1.75, 1.2], Math.PI / 2]],   // the two walls of the corner
  grid: [1.5, 1.5],
  sun: [[4.5, 3.0, 5.0], [1.0, 1.0, 0.5]],
  hook: '__ofen',
});
