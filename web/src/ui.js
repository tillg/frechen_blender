// German UI of the house page: the title and the toolbar (toolbar.js) with the house entries
// (Ganzes Haus / Erdgeschoss / 1. Stock = cutaway all / eg / noroof), the five stages as
// Darstellung (on Ganzes Haus also the plan sheets, plans.js), the Standpunkte and Routen, the sun
// toggle and Reset. body.dataset.stage / .cutaway reflect the state (for tests).
import { PLANS } from './plans.js';
import { STAGES, stageAt } from './stages.js';
import { createToolbar, HOUSE } from './toolbar.js';

const LABELS = { sketch: 'Skizze', massing: 'Massenmodell', detail: 'Detailmodell', built: 'Gebaut', furnished: 'Eingerichtet' };

function el(tag, attrs = {}, text = '') {
  const e = Object.assign(document.createElement(tag), attrs);
  if (text) e.textContent = text;
  return e;
}

const STAGE_ITEMS = STAGES.map((s, i) => ({ value: i, label: LABELS[s] }));
// the Darstellung of an entry: the stages, on Ganzes Haus then the plan sheets
const levelItems = (key) => (key === 'haus'
  ? [...STAGE_ITEMS, { group: 'Pläne' }, ...PLANS.map(([k, label]) => ({ value: `plan:${k}`, label }))]
  : STAGE_ITEMS);

// api: { model (entry key), spots (drop-down items), getProgress(), setProgress(p), getPlan(),
// setPlan(key | null), setCutaway(c), onModel(key), onSpot(value), onReset(), isDusk(), toggleSun() }
export function createUI(api) {
  const title = el('div', { className: 'fl-title' });
  title.append(el('h1', {}, 'Frechenlehen'), el('p', {}, 'Vom Strich zum Haus'));
  document.body.append(title);

  const tb = createToolbar({
    model: api.model,
    levels: levelItems(api.model),
    spots: api.spots,
    onModel: (key) => { api.onModel(key); setModel(key); refresh(); },
    onLevel: (v) => {                                     // a stage, or a plan sheet ('plan:eg')
      if (typeof v === 'string') api.setPlan(v.slice(5));
      else { api.setPlan(null); api.setProgress(v); }
      refresh();
    },
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
    tb.level.setItems(levelItems(key));
  }

  function refresh() {
    const s = stageAt(api.getProgress());
    document.body.dataset.stage = s;
    const plan = api.getPlan();
    tb.level.set(plan ? `plan:${plan}` : STAGES.indexOf(s));
    tb.spot.disabled = !!plan;                            // a sheet has no Standpunkt
    tb.refresh();
  }

  setModel(api.model);
  refresh();
  return { refresh, setModel, spot: tb.spot };
}
