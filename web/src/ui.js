// German UI of the house page: the title and the toolbar (toolbar.js) with the house entries
// (Ganzes Haus / Erdgeschoss / 1. Stock = cutaway all / eg / noroof), the five stages as
// Darstellung, the Standpunkte and Routen, the sun toggle and Reset. body.dataset.stage / .cutaway
// reflect the state (for tests).
import { STAGES, stageAt } from './stages.js';
import { createToolbar, HOUSE } from './toolbar.js';

const LABELS = { sketch: 'Skizze', massing: 'Massenmodell', detail: 'Detailmodell', built: 'Gebaut', furnished: 'Eingerichtet' };

function el(tag, attrs = {}, text = '') {
  const e = Object.assign(document.createElement(tag), attrs);
  if (text) e.textContent = text;
  return e;
}

// api: { model (entry key), spots (drop-down items), getProgress(), setProgress(p), setCutaway(c),
// onModel(key), onSpot(value), onReset(), isDusk(), toggleSun() }
export function createUI(api) {
  const title = el('div', { className: 'fl-title' });
  title.append(el('h1', {}, 'Frechenlehen'), el('p', {}, 'Vom Strich zum Haus'));
  document.body.append(title);

  const tb = createToolbar({
    model: api.model,
    levels: STAGES.map((s, i) => ({ value: i, label: LABELS[s] })),
    spots: api.spots,
    onModel: (key) => { api.onModel(key); setModel(key); },
    onLevel: (i) => { api.setProgress(i); refresh(); },
    onSpot: api.onSpot,
    onReset: api.onReset,
    sun: { toggle: api.toggleSun, isDusk: api.isDusk, enabled: () => api.getProgress() >= 1.5 },   // light only matters from the Detailmodell on
  });

  // a house entry: its cutaway, without a reload
  function setModel(key) {
    const cut = HOUSE.find(([k]) => k === key)[2];
    api.setCutaway(cut);
    document.body.dataset.cutaway = cut;
    tb.model.set(key);
  }

  function refresh() {
    const s = stageAt(api.getProgress());
    document.body.dataset.stage = s;
    tb.level.set(STAGES.indexOf(s));
    tb.refresh();
  }

  setModel(api.model);
  refresh();
  return { refresh, setModel, spot: tb.spot };
}
