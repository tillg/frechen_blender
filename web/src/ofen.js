// Ofen sub-model (ofen.html): the corner stove of house_core.build_ofen() with the core's
// dimension lines (scene extras "dims"), in three looks: see-through line drawing on a 10 cm floor
// grid, massing (clay, shadows) and rendered (the house's materials, see materials.js).
import * as THREE from 'three/webgpu';
import { uniform } from 'three/tsl';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { CSS2DObject, CSS2DRenderer } from 'three/addons/renderers/CSS2DRenderer.js';
import { loadBlueprint } from './blueprint.js';
import { INK } from './ink.js';
import { makeMaterials, updateStage } from './materials.js';
import './ui.css';

const yup = ([x, y, z]) => new THREE.Vector3(x, z, -y);        // model z-up -> three.js y-up
const COLOR = { Ofen_Koerper: INK, Ofen_Feuertuer: 0xb0412e, Ofen_Bett: 0x8a5a2b, Ofen_Bettrand: 0x8a5a2b, Ofen_Bank: 0x8a5a2b };

const renderer = new THREE.WebGPURenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
document.body.appendChild(renderer.domElement);
const labels = new CSS2DRenderer();
labels.setSize(window.innerWidth, window.innerHeight);
Object.assign(labels.domElement.style, { position: 'absolute', top: '0', pointerEvents: 'none', zIndex: '0' });  // own stacking context: labels stay below the menu
document.body.appendChild(labels.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf3efe6);
const camera = new THREE.PerspectiveCamera(35, window.innerWidth / window.innerHeight, 0.05, 100);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

const VIEWS = {
  iso: [[5.0, 4.4, 3.0], [1.4, 0.8, 0.5]],
  top: [[1.701, 1.1, 8.5], [1.7, 1.1, 0.0]],     // plan, oriented like the sketch (walls top and left)
  front: [[3.6, 3.6, 1.0], [0.95, 0.95, 0.6]],   // onto the fire door
};
const heights = [];                              // labels of vertical dimensions: hidden in the plan
function view(name) {
  const [pos, target] = VIEWS[name];
  for (const l of heights) l.visible = name !== 'top';
  camera.position.copy(yup(pos));
  controls.target.copy(yup(target));
  controls.update();
}
// light for massing and rendered: sun from the room side, hemisphere fill
const sun = new THREE.DirectionalLight(0xffffff, 2.2);
sun.position.copy(yup([4.5, 3.0, 5.0]));
sun.target.position.copy(yup([1.0, 1.0, 0.5]));
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, { left: -3, right: 3, top: 3, bottom: -3, near: 1, far: 15 });
sun.shadow.bias = -0.0004;
sun.shadow.normalBias = 0.01;
sun.shadow.radius = 3;
scene.add(sun, sun.target, new THREE.HemisphereLight(0xffffff, 0xb8b0a0, 1.4));

// floor grid 10 cm, every 50 cm darker (line drawing); floor and the two walls of the room corner
const fine = new THREE.GridHelper(4, 40, 0xd9d1c1, 0xd9d1c1);
const coarse = new THREE.GridHelper(4, 8, 0xb8ae9a, 0xb8ae9a);
coarse.position.y = 0.001;
for (const g of [fine, coarse]) { g.position.add(yup([1.5, 1.5, 0])); scene.add(g); }
const wallLine = new THREE.MeshBasicNodeMaterial({ color: 0xc8c0b0, transparent: true, opacity: 0.18, side: THREE.DoubleSide, depthWrite: false });
const wallSolid = new THREE.MeshStandardNodeMaterial({ color: 0xe6e0d4, side: THREE.DoubleSide });
const walls = [];
for (const [w, h, pos, rot] of [[3.5, 2.4, [1.75, 0, 1.2], 0], [3.5, 2.4, [0, 1.75, 1.2], Math.PI / 2]]) {
  const wall = new THREE.Mesh(new THREE.PlaneGeometry(w, h), wallLine);
  wall.position.copy(yup(pos));
  wall.rotation.y = rot;
  wall.receiveShadow = true;
  walls.push(wall);
  scene.add(wall);
}
const floor = new THREE.Mesh(new THREE.PlaneGeometry(4, 4), new THREE.MeshStandardNodeMaterial({ color: 0xece6da }));
floor.rotation.x = -Math.PI / 2;
floor.position.copy(yup([1.5, 1.5, -0.001]));
floor.receiveShadow = true;
scene.add(floor);

const bp = await loadBlueprint(import.meta.env.BASE_URL + 'ofen.glb');
bp.root.updateMatrixWorld(true);
const surface = new THREE.MeshBasicNodeMaterial({ color: 0xffffff, transparent: true, opacity: 0.35, depthWrite: false });
const uDetail = uniform(0);
const defs = {}, meshes = [], lines = new THREE.Group();
bp.root.traverse((m) => m.isMesh && (defs[m.material.name] = { name: m.material.name, extras: m.material.userData }));
const mats = makeMaterials(Object.values(defs), { uPaper: uniform(0), uDetail });
let edges = 0;
for (const obj of bp.objects) {
  const lineMat = new THREE.LineBasicNodeMaterial({ color: COLOR[obj.name] ?? INK });
  obj.traverse((m) => {
    if (!m.isMesh) return;
    m.userData.mat = mats[m.material.name];
    m.castShadow = !m.userData.mat.transparent;
    m.receiveShadow = true;
    meshes.push(m);
    const geo = new THREE.EdgesGeometry(m.geometry, 1).applyMatrix4(m.matrixWorld);
    edges += geo.attributes.position.count / 2;
    lines.add(new THREE.LineSegments(geo, lineMat));
  });
}
scene.add(bp.root, lines);

// looks: 'wire' see-through lines on the grid, 'mass' clay with shadows, 'full' real materials
let look = 'wire';
function setLook(name) {
  look = name;
  const wire = name === 'wire';
  for (const m of meshes) m.material = wire ? surface : m.userData.mat;
  uDetail.value = name === 'full' ? 1 : 0;
  updateStage(mats, { detail: uDetail.value, built: 0 });
  lines.visible = fine.visible = coarse.visible = wire;
  floor.visible = !wire;
  for (const w of walls) w.material = wire ? wallLine : wallSolid;
  for (const b of document.querySelectorAll('[data-look]')) b.setAttribute('aria-pressed', String(b.dataset.look === name));
}

// dimension lines from the core, with end ticks and a label at the middle
const dimMat = new THREE.LineBasicNodeMaterial({ color: 0x5a6f86 });
const dimPos = [];
for (const [p0, p1, text] of bp.extras.dims) {
  const a = yup(p0), b = yup(p1);
  const tick = (a.y === b.y ? new THREE.Vector3(0, 0.04, 0) : new THREE.Vector3(0.03, 0, 0.03));
  for (const [u, v] of [[a, b], [a.clone().sub(tick), a.clone().add(tick)], [b.clone().sub(tick), b.clone().add(tick)]]) dimPos.push(...u, ...v);
  const div = document.createElement('div');
  div.className = 'dim' + (text.includes('angenommen') ? ' assumed' : '');
  div.textContent = text;
  const label = new CSS2DObject(div);
  label.position.copy(a.clone().add(b).multiplyScalar(0.5));
  scene.add(label);
  if (a.y !== b.y) heights.push(label);
}
const dimGeo = new THREE.BufferGeometry();
dimGeo.setAttribute('position', new THREE.Float32BufferAttribute(dimPos, 3));
scene.add(new THREE.LineSegments(dimGeo, dimMat));

view('iso');
setLook('wire');
for (const b of document.querySelectorAll('[data-view]')) b.onclick = () => view(b.dataset.view);
for (const b of document.querySelectorAll('[data-look]')) b.onclick = () => setLook(b.dataset.look);
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  labels.setSize(window.innerWidth, window.innerHeight);
});
renderer.setAnimationLoop(() => {
  controls.update();
  renderer.render(scene, camera);
  labels.render(scene, camera);
});
if (import.meta.env.DEV) window.__ofen = { ready: true, view, setLook, look: () => look, edges, dims: bp.extras.dims.length };
