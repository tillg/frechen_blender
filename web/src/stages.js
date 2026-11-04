// Timeline math: progress p in 0…4 → weights of the five stages (no three.js).
export const STAGES = ['sketch', 'massing', 'detail', 'built', 'furnished'];

const smooth = (t) => t * t * (3 - 2 * t);

export function weights(p) {
  const q = Math.min(Math.max(p, 0), 4);
  const i = Math.min(Math.floor(q), 3);
  const t = smooth(q - i);
  const w = Object.fromEntries(STAGES.map((s) => [s, 0]));
  w[STAGES[i]] = 1 - t;
  w[STAGES[i + 1]] += t;
  return w;
}

export function stageAt(p) {
  return STAGES[Math.min(Math.max(Math.round(p), 0), 4)];
}
