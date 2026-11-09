// The sliding leaves of a sub-model (node extras.slide, the Bad's niche in code/bad.py): every
// PERIOD s one leaf, picked at random, rolls to its other end of travel in ROLL s (eased in and
// out); on its next turn it rolls back.
export const PERIOD = 4, ROLL = 2;

// n leaves, rand() in [0, 1). Returns tick(t) for rising t (seconds) -> each leaf's position:
// 0 as built, 1 at its other end.
export function createSlides(n, rand = Math.random) {
  const at = new Array(n).fill(0);
  let next = PERIOD, move = null;
  return (t) => {
    if (!move && n && t >= next) {
      while (next + PERIOD <= t) next += PERIOD;          // after a pause: this slot, no burst
      move = { i: Math.min(n - 1, Math.floor(rand() * n)), t0: next };
      next += PERIOD;
    }
    const pos = [...at];
    if (move) {
      const s = Math.min(Math.max((t - move.t0) / ROLL, 0), 1), e = s * s * (3 - 2 * s);
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
