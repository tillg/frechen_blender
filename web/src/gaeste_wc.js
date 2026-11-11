// Gäste-WC sub-model (gaeste_wc.html): the back hall's WC and Garderobe of house_core.build_gaeste_wc()
// (code/gaeste_wc.py) with the partition, the WC's north wall and door, toilet, bench and the hand
// basin on the Flur wall, drawn by submodel.js. Model origin: the old WC room's inner SW corner; WC
// and Garderobe span x 0..2.048, y 0..1.099, the Flur north of them (basin at y 1.39..1.79).
import { startSubmodel } from './submodel.js';

await startSubmodel({
  glb: 'gaeste_wc.glb',
  views: {
    iso: ['Schräg', [-1.6, 4.6, 3.4], [1.1, 0.9, 0.8]],          // from the Flur's north-west, above
    top: ['Von oben', [1.1, 1.0, 9.0], [1.1, 1.001, 0.0]],         // plan, north at the top
    flur: ['Vom Flur', [0.9, 4.4, 1.6], [1.1, 0.6, 1.0]],          // from the Flur looking south (the drawing's section)
  },
  colors: { GaesteWC_Sanitaer: 0x2b5f8e, GaesteWC_Innentueren: 0x8a5a2b, GaesteWC_Garderobe: 0x8a5a2b,
            GaesteWC_Fliesen: 0x4f7a5a, GaesteWC_Waende: 0x8a8a8a },
  walls: [[2.048, 2.4, [1.024, 0, 1.2], 0], [1.933, 2.4, [2.048, 0.9665, 1.2], Math.PI / 2]],   // south, east
  grid: [1.1, 1.2],
  sun: [[-2.0, 4.0, 5.0], [1.0, 0.9, 0.5]],
  hook: '__gaeste_wc',
});
