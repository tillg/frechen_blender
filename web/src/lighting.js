// Day and dusk: sun from Blender's angle (setup_scene), hemisphere light, sky background, and
// at dusk a low warm sun, deep-blue sky and warm point lights at ROOM_LIGHTS (floor + ROOM_LIGHT_H).
import * as THREE from 'three/webgpu';
import { color, mix, uniform } from 'three/tsl';
import { PAPER } from './materials.js';

const yup = (x, y, z) => new THREE.Vector3(x, z, -y);
const DAY_DIR = yup(0.439, -0.627, 0.643);            // Blender sun rotation (50°, 0, 35°)
const h = Math.hypot(0.439, 0.627), E = (8 * Math.PI) / 180;
const DUSK_DIR = yup((0.439 / h) * Math.cos(E), (-0.627 / h) * Math.cos(E), Math.sin(E));
const SKY = [0.62, 0.76, 0.92], DUSK_SKY = [0.015, 0.03, 0.10];   // linear, SKY = Blender world

export function createLighting(scene, extras, target, uDetail = uniform(1)) {
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
  const roomLights = extras.room_lights.map(([x, y, z]) => {
    const l = new THREE.PointLight(0xffb070, 0, 8, 2);
    l.position.copy(yup(x, y, z + extras.ROOM_LIGHT_H));
    return l;
  });
  scene.add(sun, sun.target, hemi, ...roomLights);
  scene.backgroundNode = mix(mix(color(PAPER), color(...SKY), uDetail), color(...DUSK_SKY), uDusk);

  const warm = new THREE.Color(1.0, 0.62, 0.38), white = new THREE.Color(1, 1, 1);
  function setDusk(v) {
    uDusk.value = v;
    sun.position.copy(DAY_DIR).lerp(DUSK_DIR, v).normalize().multiplyScalar(40).add(target);
    sun.intensity = 2.2 + (0.7 - 2.2) * v;
    sun.color.copy(white).lerp(warm, v);
    hemi.intensity = 1.4 + (0.25 - 1.4) * v;
    for (const l of roomLights) l.intensity = 9 * v;
  }
  setDusk(0);
  return { sun, hemi, roomLights, setDusk, uDusk };
}
