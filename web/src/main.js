import * as THREE from 'three/webgpu';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { uniform } from 'three/tsl';
import { cutLevel, loadBlueprint } from './blueprint.js';
import { createFire } from './fire.js';
import { buildGarden, indoors } from './garden.js';
import { inkLines } from './ink.js';
import { createPlanView, PLANS } from './plans.js';
import { createLighting } from './lighting.js';
import { makeMaterials, updateStage } from './materials.js';
import { weights, stageAt } from './stages.js';
import { slidingNodes, swingingNodes } from './slides.js';
import { createTour, drawDue, LOOK } from './tour.js';
import { createUI } from './ui.js';
import { cleanView, hasView, initialQuery, read, remove, safeStorage, storageKey, write } from './viewstate.js';

const yup = ([x, y, z]) => new THREE.Vector3(x, z, -y);        // model z-up -> three.js y-up
// ?hires=on: full quality for the film capture, no speed shortcut that changes the picture
const hires = new URLSearchParams(location.search).get('hires') === 'on';

const renderer = new THREE.WebGPURenderer({ antialias: true });
renderer.setPixelRatio(hires ? window.devicePixelRatio : Math.min(window.devicePixelRatio, 1.5));   // Retina: 44 % fewer pixels, barely softer
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;      // soft via shadow.radius
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();

const FOV = 28;                                    // default vertical field of view; ?fov= overrides it
const camera = new THREE.PerspectiveCamera(FOV, window.innerWidth / window.innerHeight, 0.1, 500);
const controls = new OrbitControls(camera, renderer.domElement);
const ORBIT = { maxPolarAngle: Math.PI / 2 - 0.02, enableZoom: true, enablePan: true };
controls.enableDamping = true;
Object.assign(controls, ORBIT);

// stage blend: uPaper 1 = Skizze surfaces in flat paper (hidden-line), uDetail 0 = clay,
// 1 = real materials; uInk = opacity of the ink lines (fade out across Massenmodell)
const uPaper = uniform(1), uDetail = uniform(0), uInk = uniform(1);

const bp = await loadBlueprint(import.meta.env.BASE_URL + 'frechenlehen.glb');
// the Standpunkte of code/tour.py; the first, "Von Südosten" (the README view, setup_scene in
// build_house.py), is the opening view, and the sun is aimed at its target
const SPOTS = bp.extras.spots;
camera.position.copy(yup(SPOTS[0].cam));
controls.target.copy(yup(SPOTS[0].at));
controls.update();
const defs = {};
const isHouse = (o) => o.isMesh && o.material.userData.kind;       // not the grass clump
bp.root.traverse((o) => isHouse(o) && (defs[o.material.name] = { name: o.material.name, extras: o.material.userData }));
const lights = createLighting(scene, bp.extras, controls.target.clone(), uDetail, { hires });   // sun fixed on the house
const mats = makeMaterials(Object.values(defs), { uPaper, uDetail, uDusk: lights.uDusk,
  textureBase: import.meta.env.BASE_URL, onTexture: () => { dirty = true; } });   // screen images (desk)
const surfaces = [];
bp.root.traverse((o) => {
  if (!isHouse(o)) return;
  o.material = mats[o.material.name];
  o.castShadow = !o.material.transparent;
  o.receiveShadow = true;
  surfaces.push(o);
});
const ink = inkLines(bp, uInk);
const garden = buildGarden(bp, { uPaper, uDetail, uInk });
const fire = createFire(bp.extras);                       // the stoves' fires (code/fire.py)
// the Bad's sliding leaves roll in Eingerichtet, outside the Rundgang (it sees them as built); their
// travel boxes count as in view like the fires
const slides = slidingNodes(bp.objects);
const slideBoxes = slides.nodes.map((n) => new THREE.Box3().setFromObject(n.obj)
  .union(new THREE.Box3().setFromObject(n.obj).translate(n.by)));
// the doors by the back hall (code/gaeste_wc.py) swing open and shut the same way; their boxes cover
// both states plus the arc between
const swings = swingingNodes(bp.objects);
const swingBoxes = swings.nodes.map((n) => {
  const b = new THREE.Box3().setFromObject(n.obj);
  n.obj.quaternion.multiplyQuaternions(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), n.by), n.home);
  n.obj.updateMatrixWorld(true);
  b.union(new THREE.Box3().setFromObject(n.obj)).expandByScalar(0.3);
  n.obj.quaternion.copy(n.home);
  n.obj.updateMatrixWorld(true);
  return b;
});
scene.add(bp.root, ink.group, garden.group, fire.group);

let progress = 0, cut = 'all', sun = null;               // sun: null = follow the stage, else forced dusk 0/1
// drawn on demand: a frame only when something changed (dirty), a fire in view flickers, or the tour runs
let dirty = true;
function setProgress(p) {
  progress = Math.min(Math.max(p, 0), 4);
  sun = null;
  const w0 = weights(progress);
  const w = { ...w0, built: w0.built + w0.furnished };   // Eingerichtet looks like Gebaut
  uPaper.value = w.sketch;
  uDetail.value = w.detail + w.built;
  updateStage(mats, w);
  garden.update(w);
  fire.group.visible = w.detail + w.built > 0.5;          // burning from the Detailmodell on
  lights.setDusk(w.built);
  uInk.value = w.sketch + w.massing;
  ink.group.visible = uInk.value > 0.001;
  applyVisibility();
  dirty = true;
  saveView();
}
// cutaway: hide whole collections ('roof' = Dach incl. west cladding, 'og' = OG + OG balconies)
const HIDE = { all: [], noroof: ['roof'], eg: ['roof', 'og'] };
// furniture only in Eingerichtet
function applyVisibility() {
  const furnished = stageAt(progress) === 'furnished';
  for (const o of bp.objects) {
    if (!o.userData.hidden) o.visible = !HIDE[cut].includes(cutLevel(o)) && (!o.userData.furniture || furnished);
  }
  for (const g of fire.group.children) g.visible = !HIDE[cut].includes(cutLevel(g));   // the OG stove's fire goes with the OG
}
function setCutaway(c) {
  cut = c;
  applyVisibility();
  for (const l of ink.group.children) l.visible = !HIDE[c].includes(l.userData.level);
  dirty = true;
  saveView();
}

// ?cam=x,y,z&at=x,y,z&p=0…4&cut=all|noroof|eg: start at a viewpoint (model coordinates, z up),
// stage and cutaway. The URL follows the view, so a reload (e.g. after a core change) or a shared
// link opens the same view. Each house entry (Ganzes Haus / Erdgeschoss / 1. Stock) also keeps its
// view in the browser (viewstate.js): a URL without a view opens the last entry at its saved view.
const ENTRY = { all: 'haus', eg: 'eg', noroof: 'og' }, HOUSE_ENTRIES = Object.values(ENTRY);
const storage = safeStorage(), key = (m) => storageKey('index', m), LAST = key('last');
const url = new URLSearchParams(location.search);
const urlPlan = PLANS.some(([k]) => k === url.get('plan')) ? url.get('plan') : null;   // ?plan=eg: a sheet of Ganzes Haus
let model = (urlPlan && 'haus') ?? [url.get('m'), ENTRY[url.get('cut')], read(storage, LAST)].find((m) => HOUSE_ENTRIES.includes(m)) ?? 'haus';
url.delete('m');                                                    // ?m=: from a sub-model page
const query = new URLSearchParams(initialQuery(url.size ? `?${url}`.replaceAll('%2C', ',') : '', storage, key(model)));
const zup = (v) => [v.x, -v.z, v.y].map((n) => +n.toFixed(3)).join(',');
const cutOf = (m) => Object.keys(ENTRY).find((c) => ENTRY[c] === m);
const standard = (m) => SPOTS.find((s) => s.entries.includes(m));      // the entry's first Standpunkt
let saveTimer = 0;
function saveView() {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => {
    const view = `?cam=${zup(camera.position)}&at=${zup(controls.target)}&p=${+progress.toFixed(3)}&cut=${cut}`
      + (viewFov !== FOV ? `&fov=${viewFov}` : '');
    // the entry's default (Reset) is kept as no saved view and a bare URL
    const std = standard(model), home = view === `?cam=${std.cam}&at=${std.at}&p=0&cut=${cutOf(model)}`;
    const extra = [plan && `plan=${plan}`, hires && 'hires=on'].filter(Boolean);
    const q = (home ? '' : view) + (extra.length ? (home ? '?' : '&') + extra.join('&') : '');
    if (tour.state !== 'off') return;                               // a route is not saved, not even in the URL
    if (q !== location.search) history.replaceState(history.state, '', q || location.pathname);
    if (home) remove(storage, key(model)); else write(storage, key(model), view);
    write(storage, LAST, model);
  }, 300);
}

// an inside Standpunkt (eye level inside the house) looks around in place, as in a paused route: the
// orbit target sits LOOK ahead, no zoom or pan; so does a URL or saved view whose target is that
// close (one saved from looking around). Every other view orbits its target.
const { W_OUT, D_OUT, Z_OG } = bp.extras;
const eyeLevel = ([x, y, z]) => x > 0 && x < W_OUT && y > 0 && y < D_OUT && (z < Z_OG - 0.3 || (z > Z_OG && z < Z_OG + 2));
let viewFov = FOV, spot = null;                                     // spot: the Standpunkt's name, null = Eigene Ansicht
function place(cam, at, fov, inside) {
  controls.enableDamping = false; controls.update(); controls.enableDamping = true;   // spend the momentum first
  camera.position.copy(yup(cam));
  Object.assign(controls, inside ? { maxPolarAngle: Math.PI, enableZoom: false, enablePan: false } : ORBIT);
  controls.target.copy(inside ? yup(at).sub(camera.position).setLength(LOOK).add(camera.position) : yup(at));
  controls.update();
  viewFov = camera.fov = fov;
  camera.updateProjectionMatrix();
  dirty = true;
}
// the camera stands at Standpunkt s and looks its way
function at(s) {
  const d = yup(s.at).sub(yup(s.cam)).normalize();
  return camera.position.distanceTo(yup(s.cam)) < 0.01 && camera.getWorldDirection(new THREE.Vector3()).dot(d) > 0.9999;
}
function applyView(q) {                                             // camera and stage of a query
  const v = (k) => q.get(k)?.split(',').map(Number), std = standard(model);
  if (v('cam')) place(v('cam'), v('at') ?? std.at, Number(q.get('fov') ?? FOV), !!v('at') && Math.hypot(...v('cam').map((c, i) => c - v('at')[i])) < 2 * LOOK);
  else place(std.cam, std.at, std.fov, false);
  spot = SPOTS.find((s) => s.entries.includes(model) && at(s))?.name ?? null;
  if (q.has('p')) setProgress(Number(q.get('p')));
}
applyView(query);
controls.addEventListener('change', () => {
  dirty = true;
  const routing = tour.state !== 'off' || String(ui.spot.value).startsWith('route:');   // also while a route starts
  if (!routing && spot && !at(SPOTS.find((s) => s.name === spot))) { spot = null; showSpot(); }
  saveView();
});
if (!query.has('p')) setProgress(0);

const isDusk = () => lights.uDusk.value >= 0.5;
// the Standpunkt drop-down of an entry: its spots by group, then (Ganzes Haus) the routes
const ROUTES = [{ name: 'Um und durch das Haus', ...bp.extras.tour },
  ...bp.extras.routes.map((r) => ({ fps: bp.extras.tour.fps, ...r }))];
function spotItems(m) {
  const items = [];
  let group;
  for (const s of SPOTS.filter((x) => x.entries.includes(m))) {
    if (s.group !== group) items.push({ group: (group = s.group) });
    items.push({ value: `spot:${s.name}`, label: s.name });
  }
  if (m === 'haus') items.push({ group: 'Routen' }, ...ROUTES.map((r, i) => ({ value: `route:${i}`, label: r.name })));
  return [...items, { value: 'custom', label: 'Eigene Ansicht', hidden: true }];
}
const showSpot = () => ui.spot.set(spot ? `spot:${spot}` : 'custom');
function goSpot(name) {
  tour.leave();
  const s = SPOTS.find((x) => x.name === name);
  place(s.cam, s.at, s.fov, eyeLevel(s.cam));
  spot = name;
  showSpot();
  saveView();
}
// a plan sheet of Ganzes Haus over the 3D view (plans.js), or null: back to the 3D view
const planView = createPlanView(import.meta.env.BASE_URL);
let plan = null;
function setPlan(k) {
  plan = k;
  if (k) planView.show(k); else planView.hide();
  dirty = true;
  saveView();
}
// another house entry: its saved view, else its standard Standpunkt (the stage stays)
function switchModel(m) {
  tour.leave();
  setPlan(null);
  model = m;
  ui.spot.setItems(spotItems(m));
  const saved = cleanView(read(storage, key(m)));
  if (hasView(saved)) { applyView(new URLSearchParams(saved)); ui.refresh(); showSpot(); }
  else goSpot(standard(m).name);
}
const ui = createUI({
  model,
  spots: spotItems(model),
  getProgress: () => progress,
  setProgress,
  getPlan: () => plan,
  setPlan,
  setCutaway,
  onModel: switchModel,
  onSpot: (v) => (v.startsWith('route:') ? tour.enter(Number(v.slice(6))) : goSpot(v.slice(5))),
  onReset: () => { setPlan(null); setProgress(0); ui.refresh(); goSpot(standard(model).name); },
  isDusk,
  toggleSun: () => { sun = isDusk() ? 0 : 1; lights.setDusk(sun); dirty = true; },
});
showSpot();
if (urlPlan) { setPlan(urlPlan); ui.refresh(); }
// Rundgang (a route's camera keys): furnished, whole house, entrance door open; at its end the
// Darstellung it started from comes back, unless it was changed during the route
let routeFrom = 4;
const tour = createTour({
  camera, controls, routes: ROUTES, door: bp.byName.EG_Haustuer,
  onStart: (i) => {
    setPlan(null);
    routeFrom = progress;
    setProgress(4);
    if (model !== 'haus') { model = 'haus'; ui.spot.setItems(spotItems('haus')); ui.setModel('haus'); }
    ui.refresh();
    ui.spot.set(`route:${i}`);
  },
  onEnd: () => {
    if (progress === 4 && routeFrom !== 4) { setProgress(routeFrom); ui.refresh(); }
    showSpot();
  },
});

// a fire counts as in view when its box (tongues at full height) meets the camera frustum
const fireBoxes = fire.group.children.map((g) => new THREE.Box3().setFromObject(g));
const frustum = new THREE.Frustum(), viewProj = new THREE.Matrix4();
function inView(boxes) {
  camera.updateMatrixWorld();
  frustum.setFromProjectionMatrix(viewProj.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse), camera.coordinateSystem);
  return boxes.some((b) => frustum.intersectsBox(b));
}
const fireInView = () => fire.group.visible && inView(fireBoxes.filter((b, i) => fire.group.children[i].visible));

window.addEventListener('resize', () => {                             // before the awaits: no resize lost while compiling
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  tour.resize();
  renderer.setSize(window.innerWidth, window.innerHeight);
  dirty = true;
});

await renderer.init();
await lights.prewarm(() => renderer.compileAsync(scene, camera));   // fast mode: no stall at the first dusk
let draws = 0, lastDraw = -Infinity, t0;
renderer.setAnimationLoop((now) => {
  if (plan) return;                                                 // a plan sheet covers the 3D view
  const touring = tour.state !== 'off';
  if (!tour.update(now)) controls.update();
  const p = camera.position, inside = indoors(bp.extras, [p.x, -p.z, p.y]);
  if (garden.setIndoors(!hires && inside)) dirty = true;            // hires (film capture) keeps the grass
  const t = now / 1000 - (t0 ??= now / 1000), moving = stageAt(progress) === 'furnished' && !touring;
  const rolling = slides.update(t, moving), swinging = swings.update(t, moving);
  // tour, fire, rolling leaves and swinging doors: ≤ 30 fps, less GPU load; otherwise only after a change
  if (touring || (!dirty && (fireInView() || (rolling && inView(slideBoxes)) || (swinging && inView(swingBoxes))))) {
    if (!drawDue(now, lastDraw)) return;
  }
  else if (!dirty) return;
  dirty = touring;                                                  // the first frame after the tour draws too
  lastDraw = now;
  fire.tick(now / 1000);
  lights.update(p, inside);                                         // fast mode, dusk: the pool to the nearest sites
  renderer.render(scene, camera);
  draws++;
});

if (import.meta.env.MODE !== 'production') {
  window.__fl = {
    ready: false,
    objectCount: bp.objects.length,
    lineSources: ink.sources,
    get progress() { return progress; },
    get linesVisible() { return ink.group.visible; },
    get garden() { return garden.state; },
    hires,
    get pixelRatio() { return renderer.getPixelRatio(); },
    get lights() {                                                  // visible room / outside lights, model coords
      const at = (ls) => ls.filter((l) => l.visible).map((l) => [l.position.x, -l.position.z, l.position.y].map((v) => +v.toFixed(3)));
      return { room: at(lights.roomLights), outside: at(lights.outsideLights) };
    },
    cameraAt: () => [camera.position.x, -camera.position.z, camera.position.y].map((v) => +v.toFixed(3)),
    fire: () => fire.group.visible && fire.group.children[0].children[0].scale.y,   // a flame's height (0: off)
    fires: () => fire.group.children.filter((g) => g.visible).map((g) => g.userData.collection),   // shown fires' collections
    slides: slides.state,                                                       // the Bad's sliding leaves
    doors: swings.state,                                                        // the doors by the back hall
    setProgress,
    setCutaway,
    visible: (name) => bp.byName[name].visible,
    setSurfaces: (on) => { surfaces.forEach((m) => { m.visible = on; }); dirty = true; },
    lookFrom: (...p) => { camera.position.copy(yup(p)); controls.update(); dirty = true; },   // model z-up coords
    get camera() { const p = camera.position; return [p.x, -p.z, p.y]; },        // model z-up coords
    get fov() { return camera.fov; },
    get draws() { return draws; },
    get view() { return camera.getWorldDirection(new THREE.Vector3()).toArray(); },  // y-up
    tour,
    tourKey: (i) => bp.extras.tour.frames[i].slice(0, 3),
    project: (...p) => {                                                        // model -> CSS px
      camera.updateMatrixWorld();                                               // also before the next frame is drawn
      const v = yup(p).project(camera);
      return { x: ((v.x + 1) / 2) * window.innerWidth, y: ((1 - v.y) / 2) * window.innerHeight };
    },
  };
  // ready once two frames have been drawn with the blueprint
  renderer.render(scene, camera);
  requestAnimationFrame(() => requestAnimationFrame(() => { window.__fl.ready = true; }));
}
