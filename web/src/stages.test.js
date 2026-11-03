import { test, expect } from 'vitest';
import { STAGES, weights, stageAt } from './stages.js';

const ps = Array.from({ length: 301 }, (_, i) => i / 100);
const vec = (w) => STAGES.map((s) => w[s]);

test('weights sum to 1 and are non-negative for p in 0…3', () => {
  for (const p of ps) {
    const w = vec(weights(p));
    expect(w.reduce((a, b) => a + b, 0)).toBeCloseTo(1, 12);
    for (const x of w) expect(x).toBeGreaterThanOrEqual(0);
  }
});

test('integer p gives a pure stage', () => {
  STAGES.forEach((s, i) => expect(weights(i)[s]).toBe(1));
});

test('p = 1.5 has only massing and detail non-zero', () => {
  const w = weights(1.5);
  expect(w.massing).toBeGreaterThan(0);
  expect(w.detail).toBeGreaterThan(0);
  expect(w.sketch).toBe(0);
  expect(w.built).toBe(0);
});

test('weights are continuous', () => {
  for (let i = 1; i < ps.length; i++) {
    const a = vec(weights(ps[i - 1])), b = vec(weights(ps[i]));
    for (let k = 0; k < 4; k++) expect(Math.abs(a[k] - b[k])).toBeLessThan(0.02);
  }
});

test('stageAt rounds to the nearest stage and clamps', () => {
  expect(stageAt(0)).toBe('sketch');
  expect(stageAt(0.49)).toBe('sketch');
  expect(stageAt(0.51)).toBe('massing');
  expect(stageAt(2.6)).toBe('built');
  expect(stageAt(3.4)).toBe('built');
  expect(stageAt(-1)).toBe('sketch');
});
