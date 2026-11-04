import { test, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { drawDue, duration, fovFor, poseAt, step } from './tour.js';

const KEYS = [[0, 0, 1, 0, 0, 16], [1, 2, 1, 1, 0.2, 24], [3, 2, 4, 2, 0, 24]];

test('poseAt interpolates between the keys at the given fps', () => {
  const p = poseAt(KEYS, 2, 0.25);                                  // frame 0.5
  expect(p.pos).toEqual([0.5, 1, 1]);
  expect(p.yaw).toBeCloseTo(0.5);
  expect(p.pitch).toBeCloseTo(0.1);
  expect(p.lens).toBe(20);
  expect(poseAt(KEYS, 2, 0.5).pos).toEqual([1, 2, 1]);             // exactly on key 1
});

test('poseAt clamps to the first and last key', () => {
  expect(poseAt(KEYS, 2, -1).pos).toEqual([0, 0, 1]);
  expect(poseAt(KEYS, 2, 99).pos).toEqual([3, 2, 4]);
  expect(duration(KEYS, 2)).toBe(1);
});

test('fovFor: 36 mm sensor fitted to the wider side, three.js fov is vertical', () => {
  const deg = (r) => (r * 180) / Math.PI;
  expect(fovFor(16, 16 / 9)).toBeCloseTo(64.65, 2);                                  // 97.4° wide
  expect(fovFor(16, 9 / 16)).toBeCloseTo(96.73, 2);                                  // portrait: 36 mm tall
  expect(fovFor(24, 1)).toBeCloseTo(deg(2 * Math.atan(18 / 24)), 6);
  expect(fovFor(24, 0.5)).toBeCloseTo(deg(2 * Math.atan(18 / 24)), 6);                 // portrait: height fitted
});

test('the blueprint carries the route of tour.py', () => {
  const buf = readFileSync('public/frechenlehen.glb');
  const t = JSON.parse(buf.subarray(20, 20 + buf.readUInt32LE(12)).toString()).scenes[0].extras.tour;
  expect(t.fps).toBe(25);
  expect(t.frames.length).toBeGreaterThan(1000);
  expect(t.frames.every((k) => k.length === 6)).toBe(true);
});

test('step: clamps dt, stops at the end or wraps when looping', () => {
  expect(step(1, 0.5, 10, false)).toBeCloseTo(1.1);                 // dt clamped to 0.1 s (background tab)
  expect(step(1, -0.2, 10, false)).toBe(1);                          // never backwards
  expect(step(9.95, 0.1, 10, false)).toBe(10);
  expect(step(9.95, 0.1, 10, true)).toBeCloseTo(0.05);
});

test('drawDue: at most 30 draws per second during the tour', () => {
  expect(drawDue(1000, 1000 - 40)).toBe(true);                        // 40 ms since the last draw
  expect(drawDue(1000, 1000 - 16)).toBe(false);                       // a 60 Hz frame later: skip
  expect(drawDue(1000, 1000 - 32)).toBe(true);                        // ~30 Hz, allowing rAF jitter
});
