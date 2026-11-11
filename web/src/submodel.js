// A sub-model page (ofen.html, desk.html): one Blueprint .glb of the core with its dimension lines
// (scene extras "dims"), in three looks: see-through line drawing on a 10 cm floor grid, massing
// (clay, shadows) and rendered (the house's materials, see materials.js). The page passes what
// differs: the .glb, the views, line colours, the room walls behind it and the test hook's name.
import * as THREE from 'three/webgpu';
import { uniform } from 'three/tsl';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { CSS2DObject, CSS2DRenderer } from 'three/addons/renderers/CSS2DRenderer.js';
import { loadBlueprint } from './blueprint.js';
import { createFire } from './fire.js';
import { INK } from './ink.js';
import { makeMaterials, roomEnvironment, setReflections, updateStage } from './materials.js';
import { slidingNodes, swingingNodes } from './slides.js';
import { createToolbar } from './toolbar.js';
import { initialQuery, remove, safeStorage, storageKey, write } from './viewstate.js';

const yup = ([x, y, z]) => new THREE.Vector3(x, z, -y);        // model z-up -> three.js y-up

// cfg: glb (file under public/), views {name: [label, cam, target]} (model coords; the first is
// the default Standpunkt), colors {object: line colour}, walls [[w, h, centre, rotation about the vertical]],
// grid [x, y] (centre of the 4 x 4 m floor), sun [position, target], hook (window.<hook>).
// Objects with extras.slide (the Bad's sliding leaves) roll there and back, those with extras.swing
// (the doors by the back hall) swing open and shut about their hinge (slides.js).
const LOOKS = [['wire', 'Drahtmodell'], ['mass', 'Masse'], ['full', 'Gerendert']];   // Darstellung, lowest first

export async function startSubmodel(cfg) {
  const first = Object.keys(cfg.views)[0], page = location.pathname.split('/').pop().replace('.html', '');
  const tb = createToolbar({
    model: page,
    levels: LOOKS.map(([value, label]) => ({ value, label })),
    spots: [{ group: 'Standpunkte' }, ...Object.entries(cfg.views).map(([value, [label]]) => ({ value, label })),
      { value: 'custom', label: 'Eigene Ansicht', hidden: true }],
    onLevel: (name) => setLook(name),
    onSpot: (name) => view(name),
    onReset: () => { setLook('wire'); view(first); },
  });
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

  const heights = [];                              // labels of vertical dimensions: hidden in the plan
  let spot = first;                                 // the view shown; null = Eigene Ansicht (moved by the user)
  function view(name) {
    const [, pos, target] = cfg.views[name];
    for (const l of heights) l.visible = name !== 'top';
    controls.enableDamping = false; controls.update(); controls.enableDamping = true;   // spend the momentum first
    camera.position.copy(yup(pos));
    controls.target.copy(yup(target));
    controls.update();
    spot = name;                                     // after the updates: their change events see the old view
    tb.spot.set(name);
  }
  const matching = () => Object.keys(cfg.views).find((k) => {     // the view the camera is at, if any
    const [, pos, target] = cfg.views[k];
    return camera.position.distanceTo(yup(pos)) < 0.01 && controls.target.distanceTo(yup(target)) < 0.01;
  }) ?? null;
  // light for massing and rendered: sun from the room side, hemisphere fill
  const sun = new THREE.DirectionalLight(0xffffff, 2.2);
  sun.position.copy(yup(cfg.sun[0]));
  sun.target.position.copy(yup(cfg.sun[1]));
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -3, right: 3, top: 3, bottom: -3, near: 1, far: 15 });
  sun.shadow.bias = -0.0004;
  sun.shadow.normalBias = 0.01;
  sun.shadow.radius = 3;
  scene.add(sun, sun.target, new THREE.HemisphereLight(0xffffff, 0xb8b0a0, 1.4));

  // floor grid 10 cm, every 50 cm darker (line drawing); floor and the room walls behind the model
  const fine = new THREE.GridHelper(4, 40, 0xd9d1c1, 0xd9d1c1);
  const coarse = new THREE.GridHelper(4, 8, 0xb8ae9a, 0xb8ae9a);
  coarse.position.y = 0.001;
  for (const g of [fine, coarse]) { g.position.add(yup([...cfg.grid, 0])); scene.add(g); }
  const wallLine = new THREE.MeshBasicNodeMaterial({ color: 0xc8c0b0, transparent: true, opacity: 0.18, side: THREE.DoubleSide, depthWrite: false });
  const wallSolid = new THREE.MeshStandardNodeMaterial({ color: 0xe6e0d4, side: THREE.DoubleSide });
  const walls = [];
  for (const [w, h, pos, rot] of cfg.walls) {
    const wall = new THREE.Mesh(new THREE.PlaneGeometry(w, h), wallLine);
    wall.position.copy(yup(pos));
    wall.rotation.y = rot;
    wall.receiveShadow = true;
    walls.push(wall);
    scene.add(wall);
  }
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(4, 4), new THREE.MeshStandardNodeMaterial({ color: 0xece6da }));
  floor.rotation.x = -Math.PI / 2;
  floor.position.copy(yup([...cfg.grid, -0.001]));
  floor.receiveShadow = true;
  scene.add(floor);

  const bp = await loadBlueprint(import.meta.env.BASE_URL + cfg.glb);
  bp.root.updateMatrixWorld(true);
  const surface = new THREE.MeshBasicNodeMaterial({ color: 0xffffff, transparent: true, opacity: 0.35, depthWrite: false });
  const uDetail = uniform(0);
  const defs = {}, meshes = [], lines = new THREE.Group();
  let textures = 0;
  bp.root.traverse((m) => m.isMesh && (defs[m.material.name] = { name: m.material.name, extras: m.material.userData }));
  const mats = makeMaterials(Object.values(defs), { uPaper: uniform(0), uDetail,
    textureBase: import.meta.env.BASE_URL, onTexture: () => textures++ });
  let edges = 0;
  const slides = slidingNodes(bp.objects);                  // the sliding leaves, each with its edge lines
  const sliders = slides.nodes.map((n) => ({ ...n, lines: new THREE.Group() }));
  for (const s of sliders) lines.add(s.lines);
  const swings = swingingNodes(bp.objects);                 // the swinging doors: edge lines turn about the hinge
  const swingers = swings.nodes.map((n) => {
    const at = n.obj.getWorldPosition(new THREE.Vector3()), group = new THREE.Group(), inner = new THREE.Group();
    group.position.copy(at);
    inner.position.copy(at).negate();
    group.add(inner);
    lines.add(group);
    return { ...n, lines: group, inner };
  });
  for (const obj of bp.objects) {
    const lineMat = new THREE.LineBasicNodeMaterial({ color: cfg.colors[obj.name] ?? INK });
    const into = sliders.find((s) => s.obj === obj)?.lines ?? swingers.find((s) => s.obj === obj)?.inner ?? lines;
    obj.traverse((m) => {
      if (!m.isMesh) return;
      m.userData.mat = mats[m.material.name];
      m.castShadow = !m.userData.mat.transparent;
      m.receiveShadow = true;
      meshes.push(m);
      const geo = new THREE.EdgesGeometry(m.geometry, 1).applyMatrix4(m.matrixWorld);
      edges += geo.attributes.position.count / 2;
      into.add(new THREE.LineSegments(geo, lineMat));
    });
  }
  const fire = createFire(bp.extras);                       // a stove's fire behind the glass (code/fire.py)
  scene.add(bp.root, lines, fire.group);

  // looks: 'wire' see-through lines on the grid, 'mass' clay with shadows, 'full' real materials
  let look = 'wire';
  function setLook(name) {
    look = name;
    const wire = name === 'wire';
    for (const m of meshes) m.material = wire ? surface : m.userData.mat;
    uDetail.value = name === 'full' ? 1 : 0;
    updateStage(mats, { detail: uDetail.value, built: 0 });
    lines.visible = fine.visible = coarse.visible = wire;
    fire.group.visible = name === 'full';
    floor.visible = !wire;
    for (const w of walls) w.material = wire ? wallLine : wallSolid;
    tb.level.set(name);
    saveView();
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

  // ?cam=x,y,z&at=x,y,z&look=wire|mass|full: the URL follows the view, so a reload (e.g. after a
  // core change) or a shared link opens the same view. The page also keeps its view in the browser
  // (viewstate.js): opened without a view in the URL, it shows the saved one.
  const storage = safeStorage(), key = storageKey(page, page);
  const query = new URLSearchParams(initialQuery(location.search, storage, key)), xyz = (k) => query.get(k)?.split(',').map(Number);
  const zup = (v) => [v.x, -v.z, v.y].map((n) => +n.toFixed(3)).join(',');
  const [, homeCam, homeAt] = cfg.views[first];
  let saveTimer = 0;
  function saveView() {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(() => {
      const q = `?cam=${zup(camera.position)}&at=${zup(controls.target)}&look=${look}`;
      const home = q === `?cam=${homeCam}&at=${homeAt}&look=wire`;   // the default (Reset): nothing saved, bare URL
      if ((home ? '' : q) !== location.search) history.replaceState(history.state, '', home ? location.pathname : q);
      if (home) remove(storage, key); else write(storage, key, q);
    }, 300);
  }
  view(first);
  setLook(LOOKS.some(([k]) => k === query.get('look')) ? query.get('look') : 'wire');
  if (xyz('cam')) camera.position.copy(yup(xyz('cam')));
  if (xyz('at')) controls.target.copy(yup(xyz('at')));
  controls.update();
  if (xyz('cam')) {                                  // a saved or linked view: name it if it is one
    spot = matching();
    tb.spot.set(spot ?? 'custom');
    for (const l of heights) l.visible = spot !== 'top';
  }
  controls.addEventListener('change', () => {
    if (spot && matching() !== spot) { spot = null; tb.spot.set('custom'); }
    saveView();
  });
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
    labels.setSize(window.innerWidth, window.innerHeight);
  });
  await renderer.init();
  setReflections(mats, roomEnvironment(renderer));                 // metals reflect a neutral room, not black
  let t0;
  renderer.setAnimationLoop((now) => {
    controls.update();
    fire.tick(now / 1000);
    const t = now / 1000 - (t0 ??= now / 1000);
    if (slides.update(t)) for (const s of sliders) s.lines.position.subVectors(s.obj.position, s.home);
    if (swings.update(t)) for (const s of swingers) s.lines.quaternion.copy(s.home).invert().premultiply(s.obj.quaternion);
    renderer.render(scene, camera);
    labels.render(scene, camera);
  });
  if (import.meta.env.DEV) window[cfg.hook] = { ready: true, view, setLook, look: () => look, edges, dims: bp.extras.dims.length,
    textures: () => textures,                                                  // image textures loaded
    slides: slides.state,
    doors: swings.state,                                                       // the swinging doors
    get camera() { const p = camera.position; return [p.x, -p.z, p.y]; },        // model z-up coords
    fire: () => fire.group.visible && fire.group.children[0].children[0].scale.y };   // a flame's height (0: off)
}
