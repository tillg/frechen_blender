// The drop-down that switches between the house and its sub-models (house toolbar and every sub-model page).
// Relative URLs: they work under the Pages base (/frechen_blender/) too.
const PAGES = [['Haus', './'], ['Ofen', 'ofen.html'], ['Schreibtisch', 'desk.html'], ['Bad Oma & Opa', 'bad.html'], ['Küche', 'kueche.html']];

export function navSelect() {
  const here = location.pathname.split('/').pop() || './';
  const sel = document.createElement('select');
  sel.setAttribute('aria-label', 'Teilmodell');
  for (const [label, href] of PAGES) {
    const o = document.createElement('option');
    o.value = href;
    o.textContent = label;
    o.selected = href === here || (href === './' && here === 'index.html');
    sel.append(o);
  }
  sel.onchange = () => { location.href = sel.value; };
  return sel;
}
