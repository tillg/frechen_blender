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

// the query the page starts from: the URL's view, else the stored one with the URL's other keys
export function initialQuery(search, storage, key) {
  if (hasView(search)) return search;
  const stored = read(storage, key);
  if (!stored) return search;
  // raw pairs, not URLSearchParams.toString(): that would escape the commas of cam=x,y,z
  const view = stored.replace(/^\?/, '').split('&').filter((kv) => VIEW_KEYS.includes(kv.split('=')[0]));
  const own = search.replace(/^\?/, '').split('&').filter(Boolean);
  return `?${[...view, ...own].join('&')}`;
}
