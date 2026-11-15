// The Vorlagen markers of the house viewer (issue #31): one link per Bereich of code/vorlagen.py
// that has an anchor (scene.extras.vorlagen), drawn over the canvas at its anchor; a click opens the
// Bereich's photo page in a new tab. markerVisible() says when one shows; a ray against the wall
// objects (scene.extras.vorlagen_walls) hides it behind a wall.
import * as THREE from 'three';
import { pageUrl } from './vorlagen-data.js';

export const NEAR_IN = 8, NEAR_OUT = 15;   // m: a marker shows within this distance (inside / outside)
const isIn = (at, s) => at[0] > 0 && at[0] < s.W_OUT && at[1] > 0 && at[1] < s.D_OUT;

// Is the marker at `at` (model coords, z up) shown from camera `cam`? s: { touring, hires, plan,
// cut ('all' | 'noroof' | 'eg'), camInside, W_OUT, D_OUT, Z_OG }. A room's marker: from inside on
// its storey and near, or from above when the cutaway opens that storey (Erdgeschoss / 1. Stock).
// Außen: from outside and near.
export function markerVisible(at, cam, s) {
  if (s.touring || s.hires || s.plan) return false;
  const og = at[2] >= s.Z_OG, dist = Math.hypot(at[0] - cam[0], at[1] - cam[1], at[2] - cam[2]);
  if (!isIn(at, s)) return !s.camInside && dist <= NEAR_OUT;
  if (og && s.cut === 'eg') return false;                          // the 1. Stock is cut away
  if (s.camInside) return (cam[2] >= s.Z_OG) === og && dist <= NEAR_IN;
  return (og ? s.cut === 'noroof' : s.cut === 'eg') && cam[2] > at[2];   // looking down into the open storey
}

const ICON = '<svg viewBox="0 0 16 16" width="15" height="15" aria-hidden="true"><rect x="1.5" y="2.5" width="13" height="11" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.3"/><path d="M3.5 11.5l3-3.5 2.2 2.4 1.6-1.6 2.2 2.7z" fill="currentColor"/><circle cx="11" cy="5.6" r="1.2" fill="currentColor"/></svg>';

// bp: the loaded blueprint; yup: model -> three.js coords. Returns update(camera, state) (call where
// a frame is drawn) and hide() (a plan sheet covers the 3D view).
export function createMarkers(bp, yup) {
  const ex = bp.extras;
  const walls = (ex.vorlagen_walls ?? []).map((n) => bp.byName[n]).filter(Boolean);
  const ray = new THREE.Raycaster(), v = new THREE.Vector3();
  const markers = (ex.vorlagen ?? []).map((b) => {
    const a = Object.assign(document.createElement('a'), { className: 'fl-vorlage', href: pageUrl(b.key), target: '_blank', rel: 'noopener' });
    a.innerHTML = `${ICON}<span></span>`;
    a.lastChild.textContent = `Fotos: ${b.title}`;
    a.title = `Fotos und Vorlagen: ${b.title}`;
    a.dataset.key = b.key;
    a.hidden = true;
    document.body.append(a);
    return { at: b.at, pos: yup(b.at), el: a };
  });
  function hidden(m, eye) {                                          // a visible wall between?
    const d = m.pos.clone().sub(eye), far = d.length();
    ray.set(eye, d.normalize());
    ray.far = far - 0.05;
    return ray.intersectObjects(walls.filter((w) => w.visible), true).length > 0;
  }
  function update(camera, s) {
    const eye = camera.position, cam = [eye.x, -eye.z, eye.y], st = { ...s, W_OUT: ex.W_OUT, D_OUT: ex.D_OUT, Z_OG: ex.Z_OG };
    camera.updateMatrixWorld();
    for (const m of markers) {
      v.copy(m.pos).project(camera);
      const show = markerVisible(m.at, cam, st) && v.z < 1 && Math.abs(v.x) < 1 && Math.abs(v.y) < 1
        && !hidden(m, eye);
      m.el.hidden = !show;
      if (show) m.el.style.transform = `translate(${((v.x + 1) / 2) * window.innerWidth}px, ${((1 - v.y) / 2) * window.innerHeight}px) translate(-50%, -50%)`;
    }
  }
  const hide = () => markers.forEach((m) => { m.el.hidden = true; });
  return { update, hide };
}
