// German UI: title, timeline bar (play/pause, scrubber 0…3, the four stage names), cutaway
// buttons and the sun toggle. body.dataset.stage / .cutaway reflect the state (for tests).
import { STAGES, stageAt } from './stages.js';

const LABELS = { sketch: 'Skizze', massing: 'Massenmodell', detail: 'Detailmodell', built: 'Gebaut' };
const CUTS = [['all', 'Ganzes Haus'], ['noroof', 'Ohne Dach'], ['eg', 'Nur EG']];
const SECONDS_PER_STAGE = 4;

const CSS = `
.fl-title { position: fixed; top: 20px; left: 24px; color: #2b2926; pointer-events: none; padding: 8px 14px 10px;
  background: rgba(243, 239, 230, .86); border-radius: 10px; box-shadow: 0 1px 6px rgba(0,0,0,.12); }
.fl-title h1 { margin: 0; font: 400 34px/1.1 Georgia, 'Times New Roman', serif; letter-spacing: .02em; }
.fl-title p { margin: 4px 0 0; font: italic 15px Georgia, serif; opacity: .75; }
.fl-tools, .fl-bar { position: fixed; display: flex; gap: 6px; align-items: center; padding: 8px;
  background: rgba(243, 239, 230, .86); border-radius: 10px; box-shadow: 0 1px 6px rgba(0,0,0,.12);
  font: 13px system-ui, sans-serif; color: #2b2926; }
.fl-tools { top: 20px; right: 24px; }
.fl-bar { bottom: 22px; left: 50%; transform: translateX(-50%); }
.fl-bar input { width: 240px; accent-color: #2b2926; }
.fl-tools button, .fl-bar button { font: inherit; color: inherit; background: transparent; border: 1px solid transparent;
  border-radius: 6px; padding: 5px 10px; cursor: pointer; white-space: nowrap; }
.fl-tools button:hover, .fl-bar button:hover { border-color: rgba(43,41,38,.3); }
.fl-tools button[aria-pressed="true"], .fl-bar button[aria-current="true"] { background: #2b2926; color: #f3efe6; }
.fl-play { width: 34px; font-size: 15px !important; }
.fl-sep { width: 1px; height: 22px; background: rgba(43,41,38,.25); margin: 0 4px; }
`;

function el(tag, attrs = {}, text = '') {
  const e = Object.assign(document.createElement(tag), attrs);
  if (text) e.textContent = text;
  return e;
}

// api: { getProgress(), setProgress(p), setCutaway(c), isDusk(), toggleSun() }
export function createUI(api) {
  document.head.append(el('style', {}, CSS));
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
  tools.append(...cutButtons.map(([, b]) => b), el('span', { className: 'fl-sep' }), sun);

  const bar = el('div', { className: 'fl-bar' });
  const play = el('button', { type: 'button', className: 'fl-play' });
  const scrub = el('input', { type: 'range', min: 0, max: 3, step: 0.001, value: 0 });
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
    const p = Math.min(api.getProgress() + (t - last) / 1000 / SECONDS_PER_STAGE, 3);
    last = t;
    go(p);
    if (p >= 3) stop(); else requestAnimationFrame(tick);
  }
  play.onclick = () => {
    if (playing) return stop();
    if (api.getProgress() >= 3) go(0);
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
  return { refresh };
}
