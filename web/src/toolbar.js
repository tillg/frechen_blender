// The one toolbar of every page (house and sub-models), top right: three drop-downs, Modell /
// Darstellung / Standpunkt, then the sun toggle (house only; an empty slot of its width elsewhere,
// so the drop-downs sit at the same place on every page) and Reset. The drop-downs are our own (button +
// listbox) so they always open below the box; a native macOS <select> opens over the chosen entry,
// i.e. upwards when that entry is far down the list.
// Relative URLs: they work under the Pages base (/frechen_blender/) too.
import './ui.css';

// the model entries: the house entries switch the cutaway in place, the sub-models are pages, listed by storey
export const HOUSE = [['haus', 'Ganzes Haus', 'all'], ['eg', 'Erdgeschoss', 'eg'], ['eg_alt', 'Erdgeschoss - Alternativ', 'eg_alt'], ['og', '1. Stock', 'noroof']];
export const PAGES = [['ofen', 'Ofen', 'ofen.html', 'eg'], ['desk', 'Schreibtisch', 'desk.html', 'eg'], ['bad', 'Bad Oma & Opa', 'bad.html', 'eg'],
  ['kueche', 'Küche', 'kueche.html', 'eg'], ['gaeste_wc', 'Gäste-WC', 'gaeste_wc.html', 'eg'],
  ['regal', 'Schrank im Büro', 'regal.html', 'eg'], ['schrankbett', 'Schrankbett', 'schrankbett.html', 'og'],
  ['gaestebad', 'Gästebad', 'gaestebad.html', 'og'], ['elternbad', 'Bad Nadine & Till', 'elternbad.html', 'og']];
const STOREYS = [['eg', 'Erdgeschoss'], ['og', '1. Stock']];

function el(tag, attrs = {}, text = '') {
  const e = Object.assign(document.createElement(tag), attrs);
  if (text) e.textContent = text;
  return e;
}

const open = new Set();                                   // the open lists' close functions
document.addEventListener('pointerdown', (e) => {
  if (!e.target.closest?.('.fl-field')) for (const close of open) close();
});

// items: [{value, label}] plus {group: label} headings and {rule: true} separators.
// onChoose(value) runs when the user picks an entry other than the current one.
export function dropdown(name, onChoose) {
  const field = el('div', { className: 'fl-field' });
  const btn = el('button', { type: 'button', className: 'fl-dd' });
  btn.setAttribute('aria-label', name);
  btn.setAttribute('aria-haspopup', 'listbox');
  btn.setAttribute('aria-expanded', 'false');
  const list = el('ul', { className: 'fl-list', hidden: true });
  list.setAttribute('role', 'listbox');
  list.setAttribute('aria-label', name);
  field.append(el('span', {}, name), btn, list);

  let items = [], value = null, options = [], active = -1;
  function label() {
    btn.textContent = items.find((i) => 'value' in i && i.value === value)?.label ?? '';
  }
  function build() {
    list.replaceChildren();
    options = [];
    for (const it of items) {
      if (it.rule) { list.append(el('li', { className: 'fl-rule', role: 'presentation' })); continue; }
      if (it.group) { list.append(el('li', { className: 'fl-group', role: 'presentation' }, it.group)); continue; }
      if (it.hidden && it.value !== value) continue;
      const li = el('li', {}, it.label);
      li.setAttribute('role', 'option');
      li.setAttribute('aria-selected', String(it.value === value));
      li.onmouseenter = () => mark(options.indexOf(li));
      li.onclick = () => choose(it.value);
      li.dataset.value = it.value;
      options.push(li);
      list.append(li);
    }
  }
  function mark(i) {
    options.forEach((li, j) => li.classList.toggle('fl-active', j === i));
    active = i;
    options[i]?.scrollIntoView({ block: 'nearest' });
  }
  function show() {
    for (const c of open) c();
    build();
    list.hidden = false;
    btn.setAttribute('aria-expanded', 'true');
    open.add(close);
    mark(options.findIndex((li) => li.dataset.value === String(value)));
  }
  function close() {
    list.hidden = true;
    btn.setAttribute('aria-expanded', 'false');
    open.delete(close);
  }
  function choose(v) {
    close();
    btn.focus();
    if (v !== value) onChoose(v);
  }
  btn.onclick = () => (list.hidden ? show() : close());
  btn.onkeydown = (e) => {
    const k = e.key;
    if (list.hidden) {
      if (['ArrowDown', 'Enter', ' '].includes(k)) { e.preventDefault(); show(); }
      return;
    }
    if (!['Escape', 'ArrowDown', 'ArrowUp', 'Enter', ' '].includes(k)) return;
    e.preventDefault();
    if (k === 'Escape') close();
    else if (k === 'ArrowDown') mark(Math.min(active + 1, options.length - 1));
    else if (k === 'ArrowUp') mark(Math.max(active - 1, 0));
    else if (options[active]) choose(items.find((i) => String(i.value) === options[active].dataset.value).value);
  };
  return {
    field,
    setItems(next) { items = next; label(); },
    set(v) { value = v; label(); },
    get value() { return value; },
    set disabled(d) { btn.disabled = d; },
  };
}

// cfg: { model (current entry key), levels [{value, label}], spots (items), onModel(key) (house
// entries, house page only), onLevel(value), onSpot(value), onReset(), sun (house: {toggle(),
// isDusk(), enabled()}) }. Returns the three drop-downs and refresh() for the sun button.
export function createToolbar(cfg) {
  const onHouse = !!cfg.onModel;
  const model = dropdown('Modell', (key) => {
    const house = HOUSE.find(([k]) => k === key), page = PAGES.find(([k]) => k === key);
    if (house && onHouse) { model.set(key); cfg.onModel(key); }
    else location.href = house ? `./?m=${key}` : page[2];
  });
  model.setItems([...HOUSE.map(([value, label]) => ({ value, label })), { rule: true },
    ...STOREYS.flatMap(([s, group]) => [{ group }, ...PAGES.filter((p) => p[3] === s).map(([value, label]) => ({ value, label }))])]);
  model.set(cfg.model);
  const level = dropdown('Darstellung', (v) => { level.set(v); cfg.onLevel(v); });
  level.setItems(cfg.levels);
  const spot = dropdown('Standpunkt', (v) => cfg.onSpot(v));
  spot.setItems(cfg.spots);

  // the sun toggle; on the sub-model pages an empty slot of the same width
  const sun = el(cfg.sun ? 'button' : 'span', cfg.sun ? { type: 'button', className: 'fl-sun' } : { className: 'fl-sun' });
  if (cfg.sun) sun.onclick = () => { cfg.sun.toggle(); refresh(); };
  const reset = el('button', { type: 'button', className: 'fl-reset' }, '↺ Reset');
  reset.title = 'Niedrigste Darstellung, Standard-Standpunkt';
  reset.onclick = () => cfg.onReset();

  const tools = el('div', { className: 'fl-tools' });
  tools.append(model.field, level.field, spot.field, el('span', { className: 'fl-sep' }), sun, reset);
  document.body.append(tools);

  function refresh() {
    if (!cfg.sun) return;
    const dusk = cfg.sun.isDusk();
    sun.textContent = dusk ? '☾ Abend' : '☀ Tag';
    sun.setAttribute('aria-label', dusk ? 'Abend – zu Tag wechseln' : 'Tag – zu Abend wechseln');
    sun.disabled = !cfg.sun.enabled();
  }
  refresh();
  return { tools, model, level, spot, refresh };
}
