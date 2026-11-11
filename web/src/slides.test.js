import { describe, expect, it } from 'vitest';
import { Object3D } from 'three';
import { createSlides, DOOR_PERIOD, DOOR_SWING, BUERO_PERIOD, BUERO_SWING, PERIOD, ROLL, slidingNodes, swingingNodes } from './slides.js';

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

describe('swingingNodes (the doors by the back hall, code/gaeste_wc.py)', () => {
  it('every 3 s one door, picked at random, swings to its other state in 3 s', () => {
    expect([DOOR_PERIOD, DOOR_SWING]).toEqual([3, 3]);
    const tick = createSlides(3, () => 0.5, DOOR_PERIOD, DOOR_SWING);   // always door 1
    expect(tick(2.9)).toEqual([0, 0, 0]);
    expect(tick(4.5)).toEqual([0, 0.5, 0]);
    expect(tick(6)).toEqual([0, 1, 0]);                                 // 3 s: at its other state
    expect(tick(7.5)).toEqual([0, 0.5, 0]);                             // 6 s: the next pick swings it back
    expect(tick(9)).toEqual([0, 0, 0]);
  });

  it('turns the nodes with extras.swing about their origin (the hinge), back to as built when off', () => {
    const a = new Object3D(), b = new Object3D();
    a.name = 'a'; a.userData.swing = Math.PI / 2; a.position.set(1, 0, 2);
    const s = swingingNodes([a, b], () => 0);
    expect(s.nodes.map((n) => n.obj.name)).toEqual(['a']);
    expect(s.update(0)).toBe(false);
    expect(s.update(4.5)).toBe(true);
    expect(a.rotation.y).toBeCloseTo(Math.PI / 4);
    expect(a.position.toArray()).toEqual([1, 0, 2]);                    // turns about its origin
    expect(s.state()).toEqual({ a: { pos: 0.5, yaw: Math.PI / 4 } });
    expect(s.update(4.6, false)).toBe(true);                            // off (film / Rundgang)
    expect(a.rotation.y).toBe(0);
    expect(s.update(6)).toBe(true);
    expect(a.rotation.y).toBeCloseTo(Math.PI / 2);
  });
});

describe('the Büro door (code/regal.py) on its own clock', () => {
  it('it swings in 2 s, rests 4 s open, swings shut in 2 s, rests 4 s, apart from the back hall doors', () => {
    expect([BUERO_PERIOD, BUERO_SWING]).toEqual([6, 2]);
    const a = new Object3D(), b = new Object3D();
    a.name = 'EG_WC_Tuer'; a.userData.swing = Math.PI / 2;
    b.name = 'EG_Buerotuer'; b.userData.swing = Math.PI / 2;
    const s = swingingNodes([a, b], () => 0);
    const at = (t) => { s.update(t); return s.state().EG_Buerotuer.pos; };
    expect(at(0)).toBe(0);
    s.update(4.5);
    expect(s.state().EG_WC_Tuer.pos).toBe(0.5);                         // the back hall's clock: 3 s slot, 3 s swing
    expect(at(5.9)).toBe(0);                                            // at rest the first 6 s
    expect(at(7)).toBe(0.5);                                            // swinging, half way after 1 s
    expect(at(8)).toBe(1);                                              // there after 2 s
    expect(at(11.9)).toBe(1);                                           // rests 4 s
    expect(at(13)).toBe(0.5);                                           // and swings back
    expect(at(14)).toBe(0);
    expect(at(17.9)).toBe(0);                                           // rests 4 s again
  });
});
