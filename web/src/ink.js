// Skizze: ink edge lines (EdgesGeometry, 30°), merged into one LineSegments per collection
// and cutaway level (so "Nur EG" can hide the OG balconies' lines).
// SMOOTH objects (pebbles, lamps) get none: they would turn into ink noise; furniture neither.
import * as THREE from 'three/webgpu';
import { cutLevel } from './blueprint.js';

export const INK = 0x2b2926;

export function inkLines(bp, opacityNode) {
  bp.root.updateMatrixWorld(true);
  const perCollection = {}, sources = [];
  for (const obj of bp.objects) {
    if (obj.userData.smooth || obj.userData.hidden || obj.userData.furniture) continue;
    sources.push(obj.name);
    obj.traverse((m) => {
      if (!m.isMesh) return;
      const edges = new THREE.EdgesGeometry(m.geometry, 30).applyMatrix4(m.matrixWorld);
      (perCollection[obj.userData.collection + ':' + cutLevel(obj)] ??= []).push(edges.attributes.position.array);
      edges.dispose();
    });
  }
  const material = new THREE.LineBasicNodeMaterial({ color: INK, transparent: true, depthWrite: false });
  material.opacityNode = opacityNode;
  const group = new THREE.Group();
  for (const [key, arrays] of Object.entries(perCollection)) {
    const [collection, level] = key.split(':');
    const pos = new Float32Array(arrays.reduce((n, a) => n + a.length, 0));
    arrays.reduce((off, a) => (pos.set(a, off), off + a.length), 0);
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const lines = new THREE.LineSegments(geo, material);
    lines.name = `Ink_${collection}_${level}`;
    lines.userData = { collection, level };
    group.add(lines);
  }
  return { group, sources };
}
