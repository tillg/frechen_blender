// @vitest-environment happy-dom
import { test, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { scatterGrass, density, indoors, RADIUS, SHARE } from './garden.js';

const buf = readFileSync('public/frechenlehen.glb');
const extras = JSON.parse(buf.subarray(20, 20 + buf.readUInt32LE(12)).toString()).scenes[0].extras;
const garden = extras.garden;
const clumps = scatterGrass(garden, 7);
const inRect = (x, y, [x0, x1, y0, y1]) => x0 <= x && x <= x1 && y0 <= y && y <= y1;

test('no clump inside a no-grass rectangle', () => {
  for (const c of clumps) for (const r of garden.no_grass) expect(inRect(c.x, c.y, r)).toBe(false);
});

test('the windrose rectangles are ignored: grass grows on the star', () => {
  expect(clumps.some((c) => inRect(c.x, c.y, garden.windrose[0]))).toBe(true);
});

test('no clump beyond 30 m from the house', () => {
  const [hx, hy] = garden.HOUSE_C;
  for (const c of clumps) expect(Math.hypot(c.x - hx, c.y - hy)).toBeLessThanOrEqual(RADIUS);
});

test('clump count is within ±10 % of the 25 % density integral', () => {
  // integrate density on a 10 cm grid over the ground disc, outside the no-grass rectangles
  const [gx0, gx1, gy0, gy1] = garden.ground, [hx, hy] = garden.HOUSE_C, h = 0.1;
  let want = 0;
  for (let x = gx0 + h / 2; x < gx1; x += h)
    for (let y = gy0 + h / 2; y < gy1; y += h)
      if (Math.hypot(x - hx, y - hy) <= RADIUS && !garden.no_grass.some((r) => inRect(x, y, r)))
        want += density(garden, x, y) * garden.DENSITY * SHARE * h * h;
  expect(Math.abs(clumps.length - want) / want).toBeLessThan(0.1);
});

test('same seed gives the same scatter, another seed another one', () => {
  expect(scatterGrass(garden, 7)).toEqual(clumps);
  expect(scatterGrass(garden, 8)).not.toEqual(clumps);
});

test('indoors: inside the main house footprint, below the ridge', () => {
  expect(indoors(extras, [7.25, 0.6, 1.6])).toBe(true);                  // Küche
  expect(indoors(extras, [7.1, 4.4, 4.3])).toBe(true);                   // Waschküche (OG)
  expect(indoors(extras, [33, -24, 13])).toBe(false);                    // the README view
  expect(indoors(extras, [7, 6, extras.RIDGE_Z + 1])).toBe(false);       // above the roof
});
