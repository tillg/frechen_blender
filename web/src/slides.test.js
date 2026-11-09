import { describe, expect, it } from 'vitest';
import { Object3D } from 'three';
import { createSlides, PERIOD, ROLL, slidingNodes } from './slides.js';

describe('createSlides (the Bad sub-model\'s sliding leaves)', () => {
  it('every 4 s one leaf, picked at random, rolls to its other end in 2 s, and back on its next turn', () => {
    expect([PERIOD, ROLL]).toEqual([4, 2]);
    const picks = [0.7, 0.2, 0.9];                       // leaf 1, leaf 0, leaf 1
    const tick = createSlides(2, () => picks.shift());
    for (const t of [0, 2, 3.99]) expect(tick(t)).toEqual([0, 0]);   // nothing before the first 4 s
    const early = tick(4.5)[1];
    expect(early).toBeGreaterThan(0);
    expect(early).toBeLessThan(0.25);                    // eased in: slower than linear at the start
    expect(tick(5)).toEqual([0, 0.5]);
    expect(tick(6)).toEqual([0, 1]);                      // 2 s: at the other end
    expect(tick(7.9)).toEqual([0, 1]);                    // and stays there
    expect(tick(9)).toEqual([0.5, 1]);                    // 8 s: the next pick
    expect(tick(10)).toEqual([1, 1]);
    expect(tick(13)).toEqual([1, 0.5]);                   // 12 s: leaf 1 rolls back
    expect(tick(14)).toEqual([1, 0]);
  });

  it('slidingNodes moves the nodes with extras.slide by their travel, back to as built when off', () => {
    const a = new Object3D(), b = new Object3D();
    a.name = 'a'; a.userData.slide = [-1, 0, 0]; a.position.set(2, 0, 0);
    const s = slidingNodes([a, b], () => 0);
    expect(s.nodes.map((n) => n.obj.name)).toEqual(['a']);
    expect(s.update(0)).toBe(false);                      // nothing moved
    expect(s.update(5)).toBe(true);
    expect(a.position.x).toBeCloseTo(1.5);
    expect(s.state()).toEqual({ a: { pos: 0.5, dx: -0.5 } });
    expect(s.update(5, false)).toBe(true);                // off (house: not Eingerichtet, Rundgang)
    expect(a.position.x).toBe(2);
    expect(s.update(5.5, false)).toBe(false);
    expect(s.update(6)).toBe(true);                       // the clock ran on
    expect(a.position.x).toBe(1);
  });

  it('after a long pause (hidden tab) the next roll starts on the 4 s grid, not in a burst', () => {
    const tick = createSlides(2, () => 0);
    expect(tick(0)).toEqual([0, 0]);
    expect(tick(41)).toEqual([0.5, 0]);                   // the roll of the 40 s slot, half way
    expect(tick(42)).toEqual([1, 0]);
    expect(tick(43)).toEqual([1, 0]);
  });
});
