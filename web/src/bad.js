// Bad Großeltern sub-model (bad.html): the grandparents' bathroom of house_core.build_bad()
// (code/bad.py) with its shower, low wall, Waschbecken and the WC / Schrank niche, drawn by
// submodel.js. Model origin: the room's inner SW corner; the room is 2.048 x 3.817 m, open to the
// bedroom in the east.
import { startSubmodel } from './submodel.js';

await startSubmodel({
  glb: 'bad.glb',
  views: {
    iso: ['Schräg', [6.6, -1.4, 4.4], [1.0, 1.9, 0.8]],         // from the bedroom side, above
    top: ['Von oben', [1.024, 1.9, 10.5], [1.024, 1.901, 0.0]],   // plan, north at the top
    niche: ['In die Nische', [4.0, 3.0, 1.7], [1.0, 0.8, 0.9]],        // from the bedroom onto the sliding doors
  },
  colors: { Bad_Sanitaer: 0x2b5f8e, Bad_Innentueren: 0x8a5a2b, Bad_Schrank: 0x8a5a2b, Bad_Fliesen: 0x4f7a5a },
  walls: [[3.817, 2.4, [0, 1.9085, 1.2], Math.PI / 2], [2.048, 2.4, [1.024, 0, 1.2], 0],   // west, south,
          [2.048, 2.4, [1.024, 3.817, 1.2], 0]],                                        // north
  grid: [1.024, 1.9],
  sun: [[4.5, 1.2, 5.0], [1.0, 1.9, 0.5]],
  hook: '__bad',
});
