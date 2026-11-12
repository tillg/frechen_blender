// Desk sub-model (desk.html): the Büro desk of house_core.build_desk() (code/desk.py), cherry top
// on the crank frame (it cranks up and down: slides.js liftingNodes), with its monitors, MacBook,
// keyboard and trackpad, in front of the Bibliothek's north wall, drawn by submodel.js. Model
// origin: the desk's SW corner; the wall is at y = 1.002.
import { startSubmodel } from './submodel.js';

await startSubmodel({
  glb: 'desk.glb',
  views: {
    iso: ['Schräg', [-0.9, -2.6, 2.3], [1.0, 0.5, 0.8]],
    top: ['Von oben', [0.95, 0.3, 5.5], [0.95, 0.301, 0.0]],      // plan, wall at the top
    front: ['Auf die Bildschirme', [1.0, -1.25, 1.3], [1.0, 0.7, 0.95]],       // onto the monitors, from behind the chair
  },
  colors: { Desk_Bildschirm_L: 0x2b5f8e, Desk_Bildschirm_R: 0x2b5f8e, Desk_Geraete: 0x5a5a60 },
  walls: [[3.0, 2.4, [0.95, 1.002, 1.2], 0]],
  grid: [0.95, 0.5],
  sun: [[-1.5, -3.0, 4.0], [1.0, 0.5, 0.7]],
  hook: '__desk',
});
