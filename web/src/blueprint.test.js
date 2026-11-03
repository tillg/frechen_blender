// @vitest-environment happy-dom
import { test, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { parseBlueprint } from './blueprint.js';

const buf = readFileSync('public/frechenlehen.glb');           // vitest runs in web/
const ab = buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength);
const json = JSON.parse(buf.subarray(20, 20 + buf.readUInt32LE(12)).toString());
const bp = await parseBlueprint(ab);

test('one object per GLB node, with its collection', () => {
  expect(bp.objects.length).toBe(json.nodes.length);
  expect(bp.byName.EG_Waende.userData.collection).toBe('EG');
  expect(bp.byName.Kiesel.userData.smooth).toBe(true);
});

test('GLTFLoader exposes _RND as _rnd', () => {
  const meshes = [];
  bp.byName.EG_Waende.traverse((o) => o.isMesh && meshes.push(o));
  expect(meshes.length).toBeGreaterThan(0);
  for (const m of meshes) expect(Object.keys(m.geometry.attributes)).toContain('_rnd');
});

test('scene extras and the hidden grass clump', () => {
  expect(bp.extras.garden.shrubs.length).toBeGreaterThan(0);
  expect(bp.extras.room_lights.length).toBe(23);
  expect(bp.byName.GA_Grasbuschel.visible).toBe(false);
});
