// The service worker of the production build (issue #56, ADR-004-CTPY); offline-build.js puts
// CACHES in front: {cache name: [files, relative URLs]}, the live build in one cache and each plan
// version (v/<id>/…, issue #59) in one of its own (src/precache.js).
// Install: fetch every file not yet stored into its cache (a version kept from an earlier deploy costs
// nothing); activate: drop this app's caches not in CACHES; fetch: answer from the cache of the URL's
// group, ignoring the query (the view lives in the URL), the rest from the network.
/* global CACHES */
const PREFIX = 'frechenlehen-';            // the origin is shared with other repos' pages: only ours
const SCOPE = new URL('./', self.location).href;
const NAMES = Object.keys(CACHES);
const LIVE = NAMES.find((n) => !n.startsWith(`${PREFIX}v-`));
const TOTAL = Object.values(CACHES).reduce((n, files) => n + files.length, 0);

async function tell(msg) {
  for (const c of await self.clients.matchAll({ includeUncontrolled: true, type: 'window' })) c.postMessage(msg);
}

self.addEventListener('install', (e) => {
  e.waitUntil((async () => {
    let done = 0, failed = false;
    const queue = [];
    for (const name of NAMES) {
      const cache = await caches.open(name);
      for (const f of CACHES[name]) queue.push([cache, f]);
    }
    async function next() {
      for (let job = queue.shift(); job !== undefined && !failed; job = queue.shift()) {
        const [cache, f] = job;
        if (!(await cache.match(f))) {                     // an interrupted install resumes, a kept version is skipped
          const r = await fetch(f, { cache: 'reload' });
          if (!r.ok) throw new Error(`${r.status} ${f}`);
          await cache.put(f, r);
        }
        if (!failed) tell({ type: 'offline-progress', done: ++done, total: TOTAL });
      }
    }
    try {
      await Promise.all([next(), next(), next(), next()]);
    } catch (err) {                                          // a 404, the quota: say so, install fails
      failed = true;
      tell({ type: 'offline-failed', error: String(err) });
      throw err;
    }
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) if (k.startsWith(PREFIX) && !NAMES.includes(k)) await caches.delete(k);
    await self.clients.claim();
    tell({ type: 'offline-ready', total: TOTAL });
  })());
});

// the cache a URL of the scope lives in: its version's (v/<id>/…), else the live build's
function cacheOf(href) {
  const id = href.slice(SCOPE.length).match(/^v\/([^/]+)\//)?.[1];
  return id ? NAMES.find((n) => n.startsWith(`${PREFIX}v-${id}-`)) : LIVE;
}

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET' || req.headers.has('range') || !req.url.startsWith(SCOPE)) return;
  const url = new URL(req.url);
  url.search = ''; url.hash = '';
  if (url.pathname.endsWith('/')) url.pathname += 'index.html';
  const name = cacheOf(url.href);
  if (!name) return;                                          // a version this build doesn't have
  e.respondWith((async () => {
    const hit = await (await caches.open(name)).match(url.href);
    return hit ?? fetch(req);
  })());
});
