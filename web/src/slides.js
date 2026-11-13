import { Quaternion, Vector3 } from 'three/webgpu';

// The sliding leaves of a sub-model (node extras.slide, the Bad's niche in code/bad.py): every
// PERIOD s one leaf, picked at random, rolls to its other end of travel in ROLL s (eased in and
// out); on its next turn it rolls back. The doors by the back hall (node extras.swing,
// code/gaeste_wc.py) the same way: every DOOR_PERIOD s one swings to its other state in DOOR_SWING s.
// The Büro door (code/regal.py, node name *_Buerotuer) has a clock of its own: it swings to its other
// state in BUERO_SWING s, rests there 4 s, swings back (every BUERO_PERIOD s), so one sees how it clears
// the bookcase. The Büro desk (code/desk.py, node extras.lift / extras.crank) cranks up in LIFT_ROLL s,
// rests, cranks down (every LIFT_PERIOD s), its top and devices together, the hand wheel turning.
export const PERIOD = 4, ROLL = 2, DOOR_PERIOD = 3, DOOR_SWING = 3, BUERO_PERIOD = 6, BUERO_SWING = 2;
export const LIFT_PERIOD = 7, LIFT_ROLL = 3;

// n leaves, rand() in [0, 1). Returns tick(t) for rising t (seconds) -> each leaf's position:
// 0 as built, 1 at its other end.
export function createSlides(n, rand = Math.random, period = PERIOD, roll = ROLL) {
  const at = new Array(n).fill(0);
  let next = period, move = null;
  return (t) => {
    if (!move && n && t >= next) {
      while (next + period <= t) next += period;          // after a pause: this slot, no burst
      move = { i: Math.min(n - 1, Math.floor(rand() * n)), t0: next };
      next += period;
    }
    const pos = [...at];
    if (move) {
      const s = Math.min(Math.max((t - move.t0) / roll, 0), 1), e = s * s * (3 - 2 * s);
      pos[move.i] = at[move.i] + (1 - 2 * at[move.i]) * e;
      if (s === 1) { at[move.i] = 1 - at[move.i]; move = null; }
    }
    return pos;
  };
}

// The scene nodes with extras.slide (glTF metres) and their positions as built. update(t, on)
// moves them (on false: as built, the clock runs on) and says whether any moved; state() for the
// test hooks: per node name its position 0..1 and its offset in x.
export function slidingNodes(objects, rand = Math.random) {
  const nodes = objects.filter((o) => o.userData.slide).map((obj) => ({ obj, home: obj.position.clone(),
    by: obj.position.clone().fromArray(obj.userData.slide) }));
  const tick = createSlides(nodes.length, rand);
  let pos = nodes.map(() => 0);
  return {
    nodes,
    update(t, on = true) {
      const now = tick(t), next = on ? now : nodes.map(() => 0);
      const moved = next.some((f, k) => f !== pos[k]);
      pos = next;
      nodes.forEach((n, k) => n.obj.position.copy(n.home).addScaledVector(n.by, pos[k]));
      return moved;
    },
    state: () => Object.fromEntries(nodes.map((n, k) => [n.obj.name, { pos: pos[k], dx: n.obj.position.x - n.home.x }])),
  };
}

// The nodes with extras.swing (radians about the vertical, glTF y, from as built to the other
// state; the node's origin is the hinge). update(t, on) and state() as slidingNodes.
export function swingingNodes(objects, rand = Math.random) {
  const nodes = objects.filter((o) => o.userData.swing).map((obj) => ({ obj, home: obj.quaternion.clone(),
    by: obj.userData.swing }));
  // clocks: the Büro door its own; the leaves of a layout variant (extras.variant, #5) one of their
  // own, so the leaves hidden in a layout take no slot of the others; the rest share one
  const group = nodes.map((n) => (n.obj.name.endsWith('_Buerotuer') ? 'buero' : n.obj.userData.variant ?? ''));
  const clocks = Object.fromEntries([...new Set(group)].map((g) => [g, createSlides(group.filter((x) => x === g).length,
    rand, g === 'buero' ? BUERO_PERIOD : DOOR_PERIOD, g === 'buero' ? BUERO_SWING : DOOR_SWING)]));
  const tick = (t) => {
    const now = Object.fromEntries(Object.entries(clocks).map(([g, c]) => [g, c(t)]));
    return group.map((g) => now[g].shift());
  };
  const turn = new Quaternion(), up = new Vector3(0, 1, 0);
  let pos = nodes.map(() => 0);
  return {
    nodes,
    update(t, on = true) {
      const now = tick(t), next = on ? now : nodes.map(() => 0);
      const moved = next.some((f, k) => f !== pos[k]);
      pos = next;
      nodes.forEach((n, k) => n.obj.quaternion.multiplyQuaternions(turn.setFromAxisAngle(up, n.by * pos[k]), n.home));
      return moved;
    },
    state: () => Object.fromEntries(nodes.map((n, k) => [n.obj.name, { pos: pos[k], yaw: n.by * pos[k] }])),
  };
}

// The nodes with extras.lift (glTF metres up) and extras.crank ([axis x, y, z, radians] about the
// node's origin) on one clock: all at the same fraction of the stroke. A node with extras.fold
// ([hinge x, y, z relative to its origin, axis x, y, z, radians]) also folds about that hinge, in its
// own turning frame (the Schrankbett's feet fold onto the bed's underside as it goes up, #7).
// update(t, on) and state() as slidingNodes (state: per node name its position 0..1 and its rise dy or
// turn angle).
export function liftingNodes(objects) {
  const nodes = objects.filter((o) => o.userData.lift || o.userData.crank).map((obj) => ({ obj,
    home: obj.position.clone(), turn: obj.quaternion.clone(), lift: obj.userData.lift ?? 0, crank: obj.userData.crank,
    fold: obj.userData.fold }));
  const tick = createSlides(1, () => 0, LIFT_PERIOD, LIFT_ROLL);
  const q = new Quaternion(), qf = new Quaternion(), axis = new Vector3(), h = new Vector3(), v = new Vector3();
  let pos = 0;
  return {
    nodes,
    update(t, on = true) {
      const now = tick(t)[0], next = on ? now : 0;
      const moved = next !== pos;
      pos = next;
      for (const n of nodes) {
        n.obj.position.copy(n.home).setY(n.home.y + n.lift * pos);
        if (n.crank) n.obj.quaternion.multiplyQuaternions(q.setFromAxisAngle(axis.fromArray(n.crank), n.crank[3] * pos), n.turn);
        if (n.fold) {                                     // turn about the hinge h: position += Q (h - F h), Q = Q F
          qf.setFromAxisAngle(axis.fromArray(n.fold, 3), n.fold[6] * pos);
          h.fromArray(n.fold);
          n.obj.position.add(v.copy(h).sub(h.clone().applyQuaternion(qf)).applyQuaternion(n.obj.quaternion));
          n.obj.quaternion.multiply(qf);
        }
      }
      return moved;
    },
    state: () => Object.fromEntries(nodes.map((n) => [n.obj.name,
      n.crank ? { pos, angle: n.crank[3] * pos } : { pos, dy: n.obj.position.y - n.home.y }])),
  };
}
