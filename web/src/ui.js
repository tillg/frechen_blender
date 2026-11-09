// German UI: title, timeline bar (play/pause, scrubber 0…4, the five stage names), cutaway
// buttons, the sun toggle and the sub-model drop-down (nav.js). body.dataset.stage / .cutaway
// reflect the state (for tests).
import { STAGES, stageAt } from './stages.js';
import { navSelect } from './nav.js';
import './ui.css';

const LABELS = { sketch: 'Skizze', massing: 'Massenmodell', detail: 'Detailmodell', built: 'Gebaut', furnished: 'Eingerichtet' };
const CUTS = [['all', 'Ganzes Haus'], ['noroof', 'Ohne Dach'], ['eg', 'Nur EG']];
const SECONDS_PER_STAGE = 4;


function el(tag, attrs = {}, text = '') {
  const e = Object.assign(document.createElement(tag), attrs);
  if (text) e.textContent = text;
  return e;
}

// api: { getProgress(), setProgress(p), setCutaway(c), isDusk(), toggleSun() }
export function createUI(api) {
  const title = el('div', { className: 'fl-title' });
  title.append(el('h1', {}, 'Frechenlehen'), el('p', {}, 'Vom Strich zum Haus'));

  const tools = el('div', { className: 'fl-tools' });
  const cutButtons = CUTS.map(([key, label]) => {
    const b = el('button', { type: 'button' }, label);
    b.onclick = () => setCut(key);
    return [key, b];
  });
  const sun = el('button', { type: 'button', className: 'fl-sun' });
  sun.onclick = () => { api.toggleSun(); refresh(); };
  tools.append(...cutButtons.map(([, b]) => b), el('span', { className: 'fl-sep' }), sun, el('span', { className: 'fl-sep' }), navSelect());

  const bar = el('div', { className: 'fl-bar' });
  const play = el('button', { type: 'button', className: 'fl-play' });
  const scrub = el('input', { type: 'range', min: 0, max: 4, step: 0.001, value: 0 });
  scrub.setAttribute('aria-label', 'Zeitleiste');
  const stageButtons = STAGES.map((s, i) => {
    const b = el('button', { type: 'button' }, LABELS[s]);
    b.onclick = () => { stop(); go(i); };
    return b;
  });
  bar.append(play, scrub, ...stageButtons);
  document.body.append(title, tools, bar);

  let playing = false, last = 0;
  function go(p) { api.setProgress(p); refresh(); }
  function stop() { playing = false; refresh(); }
  function tick(t) {
    if (!playing) return;
    const p = Math.min(api.getProgress() + (t - last) / 1000 / SECONDS_PER_STAGE, 4);
    last = t;
    go(p);
    if (p >= 4) stop(); else requestAnimationFrame(tick);
  }
  play.onclick = () => {
    if (playing) return stop();
    if (api.getProgress() >= 4) go(0);
    playing = true; last = performance.now();
    refresh();
    requestAnimationFrame(tick);
  };
  scrub.oninput = () => { const p = Number(scrub.value); stop(); go(p); };   // read before refresh resets it

  function setCut(key) {
    api.setCutaway(key);
    document.body.dataset.cutaway = key;
    for (const [k, b] of cutButtons) b.setAttribute('aria-pressed', String(k === key));
  }

  function refresh() {
    const p = api.getProgress(), s = stageAt(p);
    document.body.dataset.stage = s;
    scrub.value = p;
    stageButtons.forEach((b, i) => b.setAttribute('aria-current', String(STAGES[i] === s)));
    play.textContent = playing ? '❚❚' : '▶';
    play.setAttribute('aria-label', playing ? 'Pause' : 'Abspielen');
    const dusk = api.isDusk();
    sun.textContent = dusk ? '☾ Abend' : '☀ Tag';
    sun.setAttribute('aria-label', dusk ? 'Abend – zu Tag wechseln' : 'Tag – zu Abend wechseln');
    sun.disabled = p < 1.5;                       // light only matters from the Detailmodell on
  }

  setCut('all');
  refresh();
  return { refresh, setCut };
}
