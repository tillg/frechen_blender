// Loads the Blueprint .glb written by code/export_gltf.py.
// One object per glTF node (a Group when the object has several materials); node extras
// (collection, smooth, hidden) land in userData, scene extras (lights, garden) in `extras`.
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

export function parseBlueprint(arrayBuffer) {
  return new Promise((resolve, reject) => {
    new GLTFLoader().parse(arrayBuffer, '', (gltf) => {
      const root = gltf.scene;
      const objects = [...root.children];
      const byName = Object.fromEntries(objects.map((o) => [o.name, o]));
      for (const o of objects) if (o.userData.hidden) o.visible = false;
      resolve({ root, objects, byName, extras: root.userData });
    }, reject);
  });
}

export async function loadBlueprint(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url}: ${res.status}`);
  return parseBlueprint(await res.arrayBuffer());
}

// what a cutaway hides: 'roof' (collection Dach, incl. the west cladding), 'og' (collection OG
// and the OG balconies), 'base' (everything else, never hidden)
export function cutLevel(obj) {
  const c = obj.userData.collection;
  if (c === 'Dach') return 'roof';
  if (c === 'OG' || obj.name.startsWith('Balkon_OG')) return 'og';
  return 'base';
}
