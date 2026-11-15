// @vitest-environment happy-dom
import { test, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import * as THREE from 'three/webgpu';
import { createLighting } from './lighting.js';

const buf = readFileSync('public/frechenlehen.glb');
const extras = JSON.parse(buf.subarray(20, 20 + buf.readUInt32LE(12)).toString()).scenes[0].extras;

const hires = { hires: true };                                     // full quality: one light per site, as before the pool

test('hires: one room light per ROOM_LIGHTS entry at floor + ROOM_LIGHT_H and per Wandlampe light (WALL_LIGHTS), y-up', () => {
  const scene = new THREE.Scene();
  expect(extras.ROOM_LIGHT_H).toBe(2.1);                           // NaN would compare equal below
  const L = createLighting(scene, extras, new THREE.Vector3(), undefined, hires);
  const n = extras.room_lights.length;
  expect(extras.wall_lights.length).toBe(65);                         // OG 31 (#33, #32), EG 33 (#22, #34: 32 + the Ofen bed's), the hood's spots
  expect(L.roomLights.length).toBe(n + extras.wall_lights.length);
  L.roomLights.forEach((l, i) => {
    const [x, y, z] = i < n ? extras.room_lights[i] : extras.wall_lights[i - n];
    expect(l.isPointLight).toBe(true);
    expect(l.position.toArray()).toEqual(i < n ? [x, z + extras.ROOM_LIGHT_H, -y] : [x, z, -y]);
  });
  L.setDusk(1);                                                    // a Wandlampe is dimmer than a fill light
  expect(L.roomLights.map((l) => l.intensity)).toEqual(L.roomLights.map((_, i) => (i < n ? 9 : 2)));
});

test('one EG layout (#34): no layout tags, no setLayout; the Essen lamps on the back of B join the pool (fast)', () => {
  expect(extras.wall_light_variant).toBeUndefined();
  const F = createLighting(new THREE.Scene(), extras, new THREE.Vector3());
  expect(F.setLayout).toBeUndefined();
  F.setDusk(1);
  F.update(new THREE.Vector3(3.6, 1.6, -2.6), true);                 // in the Essen
  const pool = F.roomLights.map((l) => [l.position.x, -l.position.z]);
  for (const x of [3.9035, 4.7245]) expect(pool.some(([px, py]) => Math.abs(px - x) < 0.002 && Math.abs(py - 3.215) < 0.002)).toBe(true);
});

test('hires: dusk turns the room lights on and the sun down; they stay in the render list by day', () => {
  const L = createLighting(new THREE.Scene(), extras, new THREE.Vector3(), undefined, hires);
  L.setDusk(0);
  const sunDay = L.sun.intensity;
  expect(L.roomLights.every((l) => l.intensity === 0 && l.visible)).toBe(true);
  L.setDusk(1);
  expect(L.sun.intensity).toBeLessThan(sunDay);
  expect(L.sun.position.y).toBeLessThan(L.sun.position.length() * Math.sin((20 * Math.PI) / 180));  // low sun
  expect(L.roomLights.every((l) => l.intensity > 0 && l.visible)).toBe(true);
});

test('hires: dusk switches the outside lamps on: a warm light at every bulb of OUTSIDE_LIGHTS', () => {
  const L = createLighting(new THREE.Scene(), extras, new THREE.Vector3(), undefined, hires);
  expect(extras.outside_lights.length).toBe(8);
  expect(L.outsideLights.length).toBe(8);
  L.outsideLights.forEach((l, i) => {
    const [x, y, z] = extras.outside_lights[i];
    expect(l.position.toArray()).toEqual([x, z, -y]);
  });
  L.setDusk(0);
  expect(L.outsideLights.every((l) => l.intensity === 0 && l.visible)).toBe(true);
  L.setDusk(1);
  expect(L.outsideLights.every((l) => l.intensity > 0 && l.visible)).toBe(true);
});

test('fast mode: a fixed pool of ROOM_N room and OUTSIDE_N outside lights', () => {
  const L = createLighting(new THREE.Scene(), extras, new THREE.Vector3());
  expect(L.roomLights.length).toBe(6);
  expect(L.outsideLights.length).toBe(2);
  expect(L.roomLights.every((l) => l.isPointLight)).toBe(true);
  expect(L.outsideLights.every((l) => l.isSpotLight)).toBe(true);
});

test('fast mode: by day the pool is out of the render list, at dusk in it', () => {
  const L = createLighting(new THREE.Scene(), extras, new THREE.Vector3());
  const pool = [...L.roomLights, ...L.outsideLights, ...L.outsideLights.map((l) => l.target)];
  L.setDusk(0);
  const sunDay = L.sun.intensity;
  expect(pool.every((o) => o.visible === false)).toBe(true);
  L.setDusk(1);
  expect(pool.every((o) => o.visible === true)).toBe(true);
  expect(L.sun.intensity).toBeLessThan(sunDay);
});

// model z-up coordinates of a y-up position
const zup = (p) => [p.x, -p.z, p.y].map((v) => +v.toFixed(3));
// site i: ROOM_LIGHTS first (floor + ROOM_LIGHT_H), then WALL_LIGHTS (absolute), as lighting.js ranks them
const roomSite = (i) => {
  const n = extras.room_lights.length;
  if (i >= n) return extras.wall_lights[i - n].map((v) => +v.toFixed(3));
  const [x, y, z] = extras.room_lights[i];
  return [x, y, +(z + extras.ROOM_LIGHT_H).toFixed(3)];
};
const outSite = (i) => extras.outside_lights[i].map((v) => +v.toFixed(3));
const sorted = (a) => a.map((p) => p.join(',')).sort();

test('update() moves the pool to the sites nearest the camera, storey-aware indoors', () => {
  const L = createLighting(new THREE.Scene(), extras, new THREE.Vector3());
  L.setDusk(1);
  const rooms = [...L.roomLights], outs = [...L.outsideLights];
  L.update(new THREE.Vector3(33, 13, 24), false);                     // default camera, outside
  expect(sorted(L.roomLights.map((l) => zup(l.position)))).toEqual(sorted([34, 21, 22, 65, 63, 33].map(roomSite)));   // 33, 34: Stube (#22); 65, 63: Elternbad (#33: window, mirror)
  expect(sorted(L.outsideLights.map((l) => zup(l.position)))).toEqual(sorted([2, 3].map(outSite)));
  for (const l of L.outsideLights) expect(l.target.position.toArray()).toEqual(l.position.clone().setY(l.position.y - 1).toArray());
  L.update(new THREE.Vector3(11.7, 1.6, -3.2), true);                 // Stube: all EG, its Wandlampen (#22)
  L.roomLights.forEach((l, i) => expect(l).toBe(rooms[i]));
  L.outsideLights.forEach((l, i) => expect(l).toBe(outs[i]));
  expect(sorted(L.roomLights.map((l) => zup(l.position)))).toEqual(sorted([35, 33, 34, 1, 31, 37].map(roomSite)));   // 1: the Ofen bed's, 31: Windfang (the hood's spots, 2, moved over the Halbinsel, #26)
  L.update(new THREE.Vector3(11.1, 4.3, -6.3), true);                 // OG Galerie: all OG, Wandlampen only
  expect(sorted(L.roomLights.map((l) => zup(l.position)))).toEqual(sorted([23, 12, 13, 7, 24, 11].map(roomSite)));
  L.update(new THREE.Vector3(7.1, 4.3, -4.4), true);                  // Waschküche: its five lamps and the WC's
  expect(sorted(L.roomLights.map((l) => zup(l.position)))).toEqual(sorted([27, 26, 29, 28, 25, 24].map(roomSite)));
  expect(L.roomLights.every((l) => l.userData.base === 2)).toBe(true);
});

test('a pooled light fades to 0 at the cut-off (FADE 1.0 m)', () => {
  const L = createLighting(new THREE.Scene(), extras, new THREE.Vector3());
  L.setDusk(0.5);
  const cam = new THREE.Vector3(33, 13, 24);
  L.update(cam, false);
  const at = (i) => L.roomLights.find((l) => zup(l.position).join() === roomSite(i).join());
  const d = (i) => at(i).position.distanceTo(cam);
  const [x, y, z] = extras.wall_lights[64 - extras.room_lights.length];   // exact: its distance is the cut-off
  const dCut = new THREE.Vector3(x, z, -y).distanceTo(cam);           // the 7th nearest site: first one left out
  expect(at(34).intensity).toBeCloseTo(2 * 0.5, 5);                   // the nearest, a Wandlampe (Stube, #22), full
  expect(at(21).intensity).toBeCloseTo(2 * 0.5, 5);                   // an OG Wandlampe, full
  expect(at(33).intensity).toBeCloseTo(2 * 0.5 * (dCut - d(33)), 5);  // the 6th, a Wandlampe (Stube), nearly out
  expect(at(33).intensity).toBeLessThan(2 * 0.5 * 0.3);
});

test('prewarm() compiles with the pool in the render list, then restores day/dusk', async () => {
  const L = createLighting(new THREE.Scene(), extras, new THREE.Vector3());
  L.setDusk(0);
  let during = null;
  await L.prewarm(async () => { during = L.roomLights.every((l) => l.visible) && L.outsideLights.every((l) => l.visible && l.target.visible); });
  expect(during).toBe(true);
  expect([...L.roomLights, ...L.outsideLights].every((l) => !l.visible)).toBe(true);
  const H = createLighting(new THREE.Scene(), extras, new THREE.Vector3(), undefined, hires);
  let called = false;
  await H.prewarm(async () => { called = true; });                     // hires: nothing to prewarm
  expect(called).toBe(false);
});

test('a failing prewarm restores the pool and resolves', async () => {
  const L = createLighting(new THREE.Scene(), extras, new THREE.Vector3());
  L.setDusk(0);
  await expect(L.prewarm(async () => { throw new Error('device lost'); })).resolves.toBeUndefined();
  expect([...L.roomLights, ...L.outsideLights].every((l) => !l.visible)).toBe(true);
});

