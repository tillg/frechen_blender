// @vitest-environment happy-dom
import { test, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { createFire } from './fire.js';

const extras = (file) => {
  const buf = readFileSync(file);
  return JSON.parse(buf.subarray(20, 20 + buf.readUInt32LE(12)).toString()).scenes[0].extras;
};
const house = extras('public/frechenlehen.glb');

test('one flame group per fire bed, at its base (z-up -> y-up), outer + core per tongue', () => {
  const F = createFire(house);
  expect(F.group.children.length).toBe(house.fires.length);
  expect(house.fires.length).toBe(5);                       // Ofen front + back, two workshop stoves, Küche Herd
  F.group.children.forEach((g, i) => {
    const [x, y, z] = house.fires[i].base;
    expect(g.position.toArray().map((v) => +v.toFixed(6))).toEqual([x, z, -y].map((v) => +v.toFixed(6)));
    expect(g.children.length).toBe(2 * house.fires[i].tongues.length);
    expect(g.userData.collection).toBe(house.fires[i].collection);   // the cutaway hides it with its storey
  });
});

test('the flames really move: tick changes height, width and sway, within bounds', () => {
  const F = createFire(house);
  const t0 = house.fires[0].tongues[0];
  const flame = F.group.children[0].children[0];
  F.tick(0);
  const a = [flame.scale.x, flame.scale.y, flame.rotation.z];
  F.tick(0.37);
  const b = [flame.scale.x, flame.scale.y, flame.rotation.z];
  expect(a).not.toEqual(b);
  for (let t = 0; t < 5; t += 0.05) {
    F.tick(t);
    expect(flame.scale.y).toBeGreaterThan(0.6 * t0.h);
    expect(flame.scale.y).toBeLessThan(1.4 * t0.h);
  }
});

test("the Ofen sub-model has its two fires (front and back door)", () => {
  expect(createFire(extras("public/ofen.glb")).group.children.length).toBe(2);
});
