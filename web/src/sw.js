// The service worker of the production build (issue #56, ADR-004-CTPY); offline-build.js puts
// VERSION (content hash of the build) and FILES (every file of web/dist, relative URLs) in front.
// Install: fetch every file into one cache; activate: drop the older caches of this app; fetch:
// answer from the cache, ignoring the query (the view lives in the URL), the rest from the network.
/* global VERSION, FILES */
const PREFIX = 'frechenlehen-';            // the origin is shared with other repos' pages: only ours
const CACHE = PREFIX + VERSION;
const SCOPE = new URL('./', self.location).href;

async function tell(msg) {
  for (const c of await self.clients.matchAll({ includeUncontrolled: true, type: 'window' })) c.postMessage(msg);
}

self.addEventListener('install', (e) => {
  e.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    let done = 0, failed = false;
    const queue = [...FILES];
    async function next() {
      for (let f = queue.shift(); f !== undefined && !failed; f = queue.shift()) {
        if (!(await cache.match(f))) {                     // an interrupted install resumes
          const r = await fetch(f, { cache: 'reload' });
          if (!r.ok) throw new Error(`${r.status} ${f}`);
          await cache.put(f, r);
        }
        if (!failed) tell({ type: 'offline-progress', done: ++done, total: FILES.length });
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
    for (const k of await caches.keys()) if (k.startsWith(PREFIX) && k !== CACHE) await caches.delete(k);
    await self.clients.claim();
    tell({ type: 'offline-ready', total: FILES.length });
  })());
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET' || req.headers.has('range') || !req.url.startsWith(SCOPE)) return;
  const url = new URL(req.url);
  url.search = ''; url.hash = '';
  if (url.pathname.endsWith('/')) url.pathname += 'index.html';
  e.respondWith((async () => {
    const hit = await (await caches.open(CACHE)).match(url.href);
    return hit ?? fetch(req);
  })());
});
