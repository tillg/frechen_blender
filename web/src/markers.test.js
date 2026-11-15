import { describe, expect, it } from 'vitest';
import { markerVisible } from './markers.js';

const S = { touring: false, hires: false, plan: null, cut: 'all', camInside: true, W_OUT: 14.885, D_OUT: 12.887, Z_OG: 2.7 };
const STUBE = [11.6, 3.4, 1.6], HAUS = [6.0, 7.4, 4.3], AUSSEN = [6.0, -1.5, 1.6];

describe('markerVisible', () => {
  it('inside: same storey and near', () => {
    expect(markerVisible(STUBE, [10, 2, 1.6], S)).toBe(true);
    expect(markerVisible(STUBE, [1, 11, 1.6], S)).toBe(false);          // far (Bad, 12 m)
    expect(markerVisible(STUBE, [10, 3, 4.3], S)).toBe(false);          // from the 1. Stock
    expect(markerVisible(HAUS, [6, 6, 4.3], S)).toBe(true);
    expect(markerVisible(AUSSEN, [6, 1, 1.6], S)).toBe(false);          // Außen not from inside
  });
  it('outside: Außen when near, rooms only from above into the open storey', () => {
    const out = { ...S, camInside: false };
    expect(markerVisible(AUSSEN, [6, -8, 1.6], out)).toBe(true);
    expect(markerVisible(AUSSEN, [33, -24, 13], out)).toBe(false);      // the overview: too far
    expect(markerVisible(STUBE, [24, -10, 17], out)).toBe(false);       // roof on
    expect(markerVisible(STUBE, [24, -10, 17], { ...out, cut: 'eg' })).toBe(true);
    expect(markerVisible(HAUS, [24, -10, 17], { ...out, cut: 'eg' })).toBe(false);   // OG cut away
    expect(markerVisible(HAUS, [24, -10, 17], { ...out, cut: 'noroof' })).toBe(true);
    expect(markerVisible(STUBE, [24, -10, 17], { ...out, cut: 'noroof' })).toBe(false);
  });
  it('never in a route, the film capture or on a plan sheet', () => {
    for (const k of [{ touring: true }, { hires: true }, { plan: 'eg' }])
      expect(markerVisible(STUBE, [10, 2, 1.6], { ...S, ...k })).toBe(false);
  });
});
