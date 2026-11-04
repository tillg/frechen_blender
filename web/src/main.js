import * as THREE from 'three/webgpu';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { uniform } from 'three/tsl';
import { cutLevel, loadBlueprint } from './blueprint.js';
import { buildGarden } from './garden.js';
import { inkLines } from './ink.js';
import { createLighting } from './lighting.js';
import { makeMaterials, updateStage } from './materials.js';
import { weights, stageAt } from './stages.js';
import { createTour, drawDue } from './tour.js';
import { createUI } from './ui.js';

const yup = ([x, y, z]) => new THREE.Vector3(x, z, -y);        // model z-up -> three.js y-up

const renderer = new THREE.WebGPURenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;      // soft via shadow.radius
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();

// camera from the south-east, as the README view (setup_scene in build_house.py)
const camera = new THREE.PerspectiveCamera(28, window.innerWidth / window.innerHeight, 0.1, 500);
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
const lights = createLighting(scene, bp.extras, controls.target.clone(), uDetail);   // sun fixed on the house
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
scene.add(bp.root, ink.group, garden.group);

let progress = 0, cut = 'all', sun = null;               // sun: null = follow the stage, else forced dusk 0/1
function setProgress(p) {
  progress = Math.min(Math.max(p, 0), 4);
  sun = null;
  const w0 = weights(progress);
  const w = { ...w0, built: w0.built + w0.furnished };   // Eingerichtet looks like Gebaut
  uPaper.value = w.sketch;
  uDetail.value = w.detail + w.built;
  updateStage(mats, w);
  garden.update(w);
  lights.setDusk(w.built);
  uInk.value = w.sketch + w.massing;
  ink.group.visible = uInk.value > 0.001;
  applyVisibility();
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
}

setProgress(0);

const isDusk = () => lights.uDusk.value >= 0.5;
const ui = createUI({
  getProgress: () => progress,
  setProgress,
  setCutaway,
  isDusk,
  toggleSun: () => { sun = isDusk() ? 0 : 1; lights.setDusk(sun); },
});
// Rundgang (the film's camera path): furnished, whole house, entrance door open
const tour = createTour({
  camera, controls, tour: bp.extras.tour, door: bp.byName.EG_Haustuer,
  tools: document.querySelector('.fl-tools'),
  onStart: () => { setProgress(4); ui.setCut('all'); ui.refresh(); },
});

await renderer.init();
let draws = 0, lastDraw = -Infinity;
renderer.setAnimationLoop((now) => {
  if (!tour.update(now)) controls.update();
  if (tour.state !== 'off' && !drawDue(now, lastDraw)) return;      // tour: ≤ 30 fps, less GPU load
  lastDraw = now;
  renderer.render(scene, camera);
  draws++;
});

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  tour.resize();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

if (import.meta.env.MODE !== 'production') {
  window.__fl = {
    ready: false,
    objectCount: bp.objects.length,
    lineSources: ink.sources,
    get progress() { return progress; },
    get linesVisible() { return ink.group.visible; },
    get garden() { return garden.state; },
    setProgress,
    setCutaway,
    visible: (name) => bp.byName[name].visible,
    setSurfaces: (on) => surfaces.forEach((m) => { m.visible = on; }),
    lookFrom: (...p) => { camera.position.copy(yup(p)); controls.update(); },   // model z-up coords
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
