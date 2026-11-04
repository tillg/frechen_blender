// @vitest-environment happy-dom
import { test, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import * as THREE from 'three/webgpu';
import { createLighting } from './lighting.js';

const buf = readFileSync('public/frechenlehen.glb');
const extras = JSON.parse(buf.subarray(20, 20 + buf.readUInt32LE(12)).toString()).scenes[0].extras;

test('one room light per ROOM_LIGHTS entry at floor + ROOM_LIGHT_H, converted to y-up', () => {
  const scene = new THREE.Scene();
  expect(extras.ROOM_LIGHT_H).toBe(2.1);                           // NaN would compare equal below
  const L = createLighting(scene, extras, new THREE.Vector3());
  expect(L.roomLights.length).toBe(extras.room_lights.length);
  L.roomLights.forEach((l, i) => {
    const [x, y, z] = extras.room_lights[i];
    expect(l.isPointLight).toBe(true);
    expect(l.position.toArray()).toEqual([x, z + extras.ROOM_LIGHT_H, -y]);
  });
});

test('dusk turns the room lights on and the sun down', () => {
  const L = createLighting(new THREE.Scene(), extras, new THREE.Vector3());
  L.setDusk(0);
  const sunDay = L.sun.intensity;
  expect(L.roomLights.every((l) => l.intensity === 0)).toBe(true);
  L.setDusk(1);
  expect(L.sun.intensity).toBeLessThan(sunDay);
  expect(L.sun.position.y).toBeLessThan(L.sun.position.length() * Math.sin((20 * Math.PI) / 180));  // low sun
  expect(L.roomLights.every((l) => l.intensity > 0)).toBe(true);
});

test('dusk switches the outside lamps on: a warm light at every bulb of OUTSIDE_LIGHTS', () => {
  const L = createLighting(new THREE.Scene(), extras, new THREE.Vector3());
  expect(extras.outside_lights.length).toBe(8);
  expect(L.outsideLights.length).toBe(8);
  L.outsideLights.forEach((l, i) => {
    const [x, y, z] = extras.outside_lights[i];
    expect(l.position.toArray()).toEqual([x, z, -y]);
  });
  L.setDusk(0);
  expect(L.outsideLights.every((l) => l.intensity === 0)).toBe(true);
  L.setDusk(1);
  expect(L.outsideLights.every((l) => l.intensity > 0)).toBe(true);
});
