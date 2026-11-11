// The saved view per model entry (no three.js): the same query string the page writes to its URL,
// kept in localStorage under frechenlehen:<page>:<entry>. A URL that carries a view wins (shared
// links, show.py, the reload after a core change); otherwise the stored view applies, plus the URL's
// other keys (hires=on). Storage may be missing or throw (private window): then nothing is stored.
const VIEW_KEYS = ['cam', 'at', 'p', 'cut', 'look', 'fov'];

export const storageKey = (page, entry) => `frechenlehen:${page}:${entry}`;

// the page's localStorage, or null where reading it throws
export function safeStorage() {
  try { return window.localStorage; } catch { return null; }
}

export function read(storage, key) {
  try { return storage?.getItem(key) ?? null; } catch { return null; }
}

export function write(storage, key, value) {
  try { storage?.setItem(key, value); } catch { /* full or blocked: the view just isn't kept */ }
}

export function remove(storage, key) {
  try { storage?.removeItem(key); } catch { /* blocked */ }
}

export function hasView(search) {
  const q = new URLSearchParams(search);
  return VIEW_KEYS.some((k) => q.has(k));
}

// a malformed view key (a hand-edited link, an old stored value) is dropped, so it never turns into
// a NaN camera that is then saved: cam/at 3 finite numbers, p finite, fov finite in 10…90
const nums = (v) => v.split(',').map((s) => (s.trim() === '' ? NaN : Number(s)));
const VALID = {
  cam: (v) => nums(v).length === 3 && nums(v).every(Number.isFinite),
  at: (v) => nums(v).length === 3 && nums(v).every(Number.isFinite),
  p: (v) => v !== '' && Number.isFinite(Number(v)),
  fov: (v) => v !== '' && Number(v) >= 10 && Number(v) <= 90,
};
// raw pairs, not URLSearchParams.toString(): that would escape the commas of cam=x,y,z
const pairs = (search) => (search ?? '').replace(/^\?/, '').split('&').filter(Boolean);
const ok = (kv) => {
  const [k, v = ''] = kv.split('=');
  if (!VALID[k]) return true;
  try { return VALID[k](decodeURIComponent(v)); } catch { return false; }   // a broken %-escape
};
export const cleanView = (search) => {
  const kept = pairs(search).filter(ok);
  return kept.length ? `?${kept.join('&')}` : '';
};

// the query the page starts from: the URL's view, else the stored one with the URL's other keys
export function initialQuery(search, storage, key) {
  const url = cleanView(search);
  if (hasView(url)) return url;
  const stored = cleanView(read(storage, key));
  if (!hasView(stored)) return url;
  const view = pairs(stored).filter((kv) => VIEW_KEYS.includes(kv.split('=')[0]));
  return `?${[...view, ...pairs(url)].join('&')}`;
}
