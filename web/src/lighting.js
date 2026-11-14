// Day and dusk: sun from Blender's angle (setup_scene), hemisphere light, sky background, and
// at dusk a low warm sun, deep-blue sky and warm point lights at ROOM_LIGHTS (floor + ROOM_LIGHT_H) and,
// dimmer, at the bulbs of the Wandlampen (WALL_LIGHTS; one ranking, one pool with the room lights; a
// Wandlampe of one EG layout only (extras.wall_light_variant "main" / "alt") lights only in that layout: setLayout),
// and the wall lamps outside switched on: a warm spot pointing down from the OUTSIDE_LIGHTS bulbs.
// hires (full quality, film capture): one light per site, always in the render list. Fast mode
// (default): a fixed pool of ROOM_N room / OUTSIDE_N outside lights, out of the render list by day,
// at dusk moved to the sites nearest the camera. A pool, not per-site lights switched on and off:
// three.js hashes the id of every light in the render list into each material's cache key, so a
// changing set would rebuild every material's pipeline while the camera moves.
import * as THREE from 'three/webgpu';
import { color, mix, uniform } from 'three/tsl';
import { PAPER } from './materials.js';

const yup = (x, y, z) => new THREE.Vector3(x, z, -y);
const DAY_DIR = yup(0.439, -0.627, 0.643);            // Blender sun rotation (50°, 0, 35°)
const h = Math.hypot(0.439, 0.627), E = (8 * Math.PI) / 180;
const DUSK_DIR = yup((0.439 / h) * Math.cos(E), (-0.627 / h) * Math.cos(E), Math.sin(E));
const SKY = [0.62, 0.76, 0.92], DUSK_SKY = [0.015, 0.03, 0.10];   // linear, SKY = Blender world
const ROOM_N = 6, OUTSIDE_N = 2;                     // fast mode: pool sizes
const ROOM_BASE = 9, LAMP_BASE = 2, OUTSIDE_BASE = 14;   // dusk intensity per site: fill light, Wandlampe, outside lamp
const FADE = 1.0, STOREY_W = 3;   // fade width (m) before the cut-off; height counts 3× indoors (own storey first)

export function createLighting(scene, extras, target, uDetail = uniform(1), { hires = false } = {}) {
  const uDusk = uniform(0);
  const sun = new THREE.DirectionalLight(0xffffff, 2.2);
  sun.target.position.copy(target);
  sun.castShadow = true;
  sun.shadow.mapSize.set(4096, 4096);
  Object.assign(sun.shadow.camera, { left: -22, right: 22, top: 22, bottom: -22, near: 1, far: 90 });
  sun.shadow.bias = -0.0004;
  sun.shadow.normalBias = 0.02;
  sun.shadow.radius = 3;
  const hemi = new THREE.HemisphereLight(0xffffff, 0xb8b0a0, 1.4);
  const roomSites = [
    ...extras.room_lights.map(([x, y, z]) => ({ p: yup(x, y, z + extras.ROOM_LIGHT_H), base: ROOM_BASE })),
    ...(extras.wall_lights ?? []).map(([x, y, z], i) => ({ p: yup(x, y, z), base: LAMP_BASE, variant: extras.wall_light_variant?.[i] ?? null })),
  ];
  let layout = 'main', last = null;                                // the EG layout shown; the last camera (fast mode)
  const inLayout = (s) => !s.variant || s.variant === layout;
  const outsideSites = extras.outside_lights.map(([x, y, z]) => ({ p: yup(x, y, z), base: OUTSIDE_BASE }));
  const roomLight = ({ p, base }) => {
    const l = new THREE.PointLight(0xffb070, 0, 8, 2);
    l.position.copy(p);
    l.userData.base = base;
    return l;
  };
  const outsideLight = ({ p, base }) => {
    const l = new THREE.SpotLight(0xffb070, 0, 9, 1.2, 0.7, 2);     // under the shade: down and out
    l.position.copy(p);
    l.target.position.copy(p).y -= 1;
    l.userData.base = base;
    return l;
  };
  const roomLights = (hires ? roomSites : roomSites.slice(0, ROOM_N)).map(roomLight);
  if (hires) roomLights.forEach((l, i) => { l.userData.site = roomSites[i]; });
  const outsideLights = (hires ? outsideSites : outsideSites.slice(0, OUTSIDE_N)).map(outsideLight);
  scene.add(sun, sun.target, hemi, ...roomLights, ...outsideLights, ...outsideLights.map((l) => l.target));
  scene.backgroundNode = mix(mix(color(PAPER), color(...SKY), uDetail), color(...DUSK_SKY), uDusk);

  const warm = new THREE.Color(1.0, 0.62, 0.38), white = new THREE.Color(1, 1, 1);
  function setDusk(v) {
    uDusk.value = v;
    sun.position.copy(DAY_DIR).lerp(DUSK_DIR, v).normalize().multiplyScalar(40).add(target);
    sun.intensity = 2.2 + (0.7 - 2.2) * v;
    sun.color.copy(white).lerp(warm, v);
    hemi.intensity = 1.4 + (0.25 - 1.4) * v;
    for (const l of [...roomLights, ...outsideLights]) l.intensity = l.userData.base * v * (!l.userData.site || inLayout(l.userData.site) ? 1 : 0);
    if (!hires) showPool(v > 0);
  }
  function setLayout(v) {                                          // 'main' (default) or 'alt' (Erdgeschoss - Alternativ)
    layout = v;
    setDusk(uDusk.value);
    if (last) update(...last);
  }
  function showPool(on) {
    for (const o of [...roomLights, ...outsideLights, ...outsideLights.map((l) => l.target)]) o.visible = on;
  }
  // fast mode: compile the dusk variant (pool in the render list) once at load, so the first dusk
  // (e.g. the Rundgang start) doesn't recompile every material; compile = renderer.compileAsync
  async function prewarm(compile) {
    if (hires) return;
    showPool(true);
    try {
      await compile();
    } catch (e) {
      console.warn('lights: prewarm failed, the first dusk compiles instead', e);   // the viewer runs on
    }
    showPool(uDusk.value > 0);
  }
  // fast mode, at dusk: pooled light k sits at the k-th nearest site and dims to 0 as its distance
  // reaches that of the nearest site left out (d_cut), so a light leaves the pool already dark
  function place(sites, lights, cam, w) {
    const d = sites.map(({ p }, i) => [Math.hypot(p.x - cam.x, w * (p.y - cam.y), p.z - cam.z), i]).sort((a, b) => a[0] - b[0]);
    const dCut = d[lights.length]?.[0] ?? Infinity;
    lights.forEach((l, k) => {
      const [dk, i] = d[k];
      const { p, base } = sites[i];
      l.position.copy(p);
      if (l.isSpotLight) l.target.position.copy(p).y -= 1;
      l.userData.base = base;
      l.intensity = base * uDusk.value * Math.min(Math.max((dCut - dk) / FADE, 0), 1);
    });
  }
  function update(cam, inside) {                                   // y-up camera position; inside: indoors()
    last = [cam.clone(), inside];
    if (hires || uDusk.value === 0) return;
    const w = inside ? STOREY_W : 1;
    place(roomSites.filter(inLayout), roomLights, cam, w);
    place(outsideSites, outsideLights, cam, w);
  }
  setDusk(0);
  return { sun, hemi, roomLights, outsideLights, setDusk, setLayout, update, prewarm, uDusk };
}
