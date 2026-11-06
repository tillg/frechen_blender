import * as THREE from 'three/webgpu';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { uniform } from 'three/tsl';
import { cutLevel, loadBlueprint } from './blueprint.js';
import { createFire } from './fire.js';
import { buildGarden, indoors } from './garden.js';
import { inkLines } from './ink.js';
import { createLighting } from './lighting.js';
import { makeMaterials, updateStage } from './materials.js';
import { weights, stageAt } from './stages.js';
import { createTour, drawDue } from './tour.js';
import { createUI } from './ui.js';

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

// camera from the south-east, as the README view (setup_scene in build_house.py)
const FOV = 28;                                    // default vertical field of view; ?fov= overrides it
const camera = new THREE.PerspectiveCamera(FOV, window.innerWidth / window.innerHeight, 0.1, 500);
camera.position.copy(yup([33, -24, 13]));
const controls = new OrbitControls(camera, renderer.domElement);
controls.target.copy(yup([7.4, 6.4, 3.2]));
controls.enableDamping = true;
controls.maxPolarAngle = Math.PI / 2 - 0.02;
controls.update();

// stage blend: uPaper 1 = Skizze surfaces in flat paper (hidden-line), uDetail 0 = clay,
// 1 = real materials; uInk = opacity of the ink lines (fade out across Massenmodell)
const uPaper = uniform(1), uDetail = uniform(0), uInk = uniform(1);

const bp = await loadBlueprint(import.meta.env.BASE_URL + 'frechenlehen.glb');
const defs = {};
const isHouse = (o) => o.isMesh && o.material.userData.kind;       // not the grass clump
bp.root.traverse((o) => isHouse(o) && (defs[o.material.name] = { name: o.material.name, extras: o.material.userData }));
const lights = createLighting(scene, bp.extras, controls.target.clone(), uDetail, { hires });   // sun fixed on the house
const mats = makeMaterials(Object.values(defs), { uPaper, uDetail, uDusk: lights.uDusk });
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
// link opens the same view.
const query = new URLSearchParams(location.search), xyz = (k) => query.get(k)?.split(',').map(Number);
const zup = (v) => [v.x, -v.z, v.y].map((n) => +n.toFixed(3)).join(',');
let saveTimer = 0;
function saveView() {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => {
    const q = `?cam=${zup(camera.position)}&at=${zup(controls.target)}&p=${+progress.toFixed(3)}&cut=${cut}`
      + (viewFov !== FOV ? `&fov=${viewFov}` : '') + (hires ? '&hires=on' : '');
    if (q !== location.search) history.replaceState(history.state, '', q);
  }, 300);
}
const viewFov = Number(query.get('fov') ?? FOV);                   // vertical, degrees
camera.fov = viewFov;
camera.updateProjectionMatrix();
if (xyz('cam')) camera.position.copy(yup(xyz('cam')));
if (xyz('at')) controls.target.copy(yup(xyz('at')));
controls.update();
controls.addEventListener('change', () => { dirty = true; saveView(); });
setProgress(Number(query.get('p') ?? 0));

const isDusk = () => lights.uDusk.value >= 0.5;
const ui = createUI({
  getProgress: () => progress,
  setProgress,
  setCutaway,
  isDusk,
  toggleSun: () => { sun = isDusk() ? 0 : 1; lights.setDusk(sun); dirty = true; },
});
if (Object.hasOwn(HIDE, query.get('cut') ?? '')) ui.setCut(query.get('cut'));
// Rundgang (the film's camera path): furnished, whole house, entrance door open
const tour = createTour({
  camera, controls, tour: bp.extras.tour, door: bp.byName.EG_Haustuer,
  tools: document.querySelector('.fl-tools'),
  onStart: () => { setProgress(4); ui.setCut('all'); ui.refresh(); },
});

// a fire counts as in view when its box (tongues at full height) meets the camera frustum
const fireBoxes = fire.group.children.map((g) => new THREE.Box3().setFromObject(g));
const frustum = new THREE.Frustum(), viewProj = new THREE.Matrix4();
function fireInView() {
  if (!fire.group.visible) return false;
  camera.updateMatrixWorld();
  frustum.setFromProjectionMatrix(viewProj.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse), camera.coordinateSystem);
  return fireBoxes.some((b) => frustum.intersectsBox(b));
}

window.addEventListener('resize', () => {                             // before the awaits: no resize lost while compiling
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  tour.resize();
  renderer.setSize(window.innerWidth, window.innerHeight);
  dirty = true;
});

await renderer.init();
await lights.prewarm(() => renderer.compileAsync(scene, camera));   // fast mode: no stall at the first dusk
let draws = 0, lastDraw = -Infinity;
renderer.setAnimationLoop((now) => {
  const touring = tour.state !== 'off';
  if (!tour.update(now)) controls.update();
  const p = camera.position, inside = indoors(bp.extras, [p.x, -p.z, p.y]);
  if (garden.setIndoors(!hires && inside)) dirty = true;            // hires (film capture) keeps the grass
  // tour and fire: ≤ 30 fps, less GPU load; otherwise only after a change
  if (touring || (!dirty && fireInView())) { if (!drawDue(now, lastDraw)) return; }
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
      const v = yup(p).project(camera);
      return { x: ((v.x + 1) / 2) * window.innerWidth, y: ((1 - v.y) / 2) * window.innerHeight };
    },
  };
  // ready once two frames have been drawn with the blueprint
  renderer.render(scene, camera);
  requestAnimationFrame(() => requestAnimationFrame(() => { window.__fl.ready = true; }));
}
