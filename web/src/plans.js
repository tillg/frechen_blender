// The architect's plan sheets (plans/*.svg, written by code/export_plans.py; npm run blueprint copies
// them to public/plans/) over the 3D view of the house page: the sheet fitted to the window on white
// paper, the wheel zooms at the pointer, dragging moves it; a link downloads the SVG. The sheet is
// resized in layout (not CSS-scaled), so the browser redraws the vector lines sharp at every zoom.
import './ui.css';

export const PLANS = [['eg', 'Grundriss EG'], ['og', 'Grundriss OG'], ['nord', 'Ansicht Nord'],
  ['ost', 'Ansicht Ost'], ['sued', 'Ansicht Süd'], ['west', 'Ansicht West']];

const ZOOM = [0.5, 20];                            // scale relative to the fitted sheet

export function createPlanView(base) {
  const box = Object.assign(document.createElement('div'), { className: 'fl-plan', hidden: true });
  const img = Object.assign(document.createElement('img'), { alt: '', draggable: false });
  const link = Object.assign(document.createElement('a'), { className: 'fl-plan-dl', textContent: 'SVG herunterladen' });
  box.append(img, link);
  document.body.append(box);

  let key = null, fit = 1, s = 1, x = 0, y = 0;
  const place = () => Object.assign(img.style, { width: `${img.naturalWidth * s}px`, left: `${x}px`, top: `${y}px` });
  function fitSheet() {                            // into the free area below the toolbar, above the link
    if (!img.naturalWidth) return;
    const top = 96, bottom = 64, side = 24, W = box.clientWidth - 2 * side, H = box.clientHeight - top - bottom;
    fit = s = Math.min(W / img.naturalWidth, H / img.naturalHeight);
    x = side + (W - img.naturalWidth * s) / 2;
    y = top + (H - img.naturalHeight * s) / 2;
    place();
  }
  img.onload = fitSheet;
  window.addEventListener('resize', () => key && fitSheet());

  box.addEventListener('wheel', (e) => {
    e.preventDefault();
    const n = Math.min(Math.max(s * Math.exp(-e.deltaY * 0.002), fit * ZOOM[0]), fit * ZOOM[1]);
    x = e.clientX - (e.clientX - x) * (n / s);     // the point under the pointer stays put
    y = e.clientY - (e.clientY - y) * (n / s);
    s = n;
    place();
  }, { passive: false });
  let drag = null;
  box.addEventListener('pointerdown', (e) => {
    if (e.target === link) return;
    drag = { px: e.clientX, py: e.clientY, x, y };
    box.setPointerCapture(e.pointerId);
  });
  box.addEventListener('pointermove', (e) => {
    if (!drag) return;
    x = drag.x + e.clientX - drag.px;
    y = drag.y + e.clientY - drag.py;
    place();
  });
  box.addEventListener('pointerup', () => { drag = null; });

  return {
    get key() { return key; },
    show(k) {
      const label = PLANS.find(([p]) => p === k)[1];
      key = k;
      box.hidden = false;
      const src = `${base}plans/${k}.svg`;
      if (!img.src.endsWith(src)) img.src = src; else fitSheet();
      link.href = src;
      link.download = `Frechenlehen ${label}.svg`;
    },
    hide() { key = null; box.hidden = true; },
  };
}
