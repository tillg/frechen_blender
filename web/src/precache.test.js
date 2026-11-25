import { describe, expect, it } from 'vitest';
import { buildWorker, cacheGroups, contentHash, precacheList, workerSource } from './precache.js';

const enc = (s) => new TextEncoder().encode(s);

describe('precache (issue #56)', () => {
  it('lists every file but the worker, sorted, as relative URLs', () => {
    expect(precacheList(['sw.js', 'index.html', 'assets/main-1a.js', 'bad.glb', 'vorlagen/stube/a b.jpg']))
      .toEqual(['assets/main-1a.js', 'bad.glb', 'index.html', 'vorlagen/stube/a%20b.jpg']);
  });

  it('encodes a path as the browser requests it', () => {
    expect(precacheList(['v/a,b;c@d+e.jpg', 'v/ä#1?.jpg', 'v/a[1].jpg']))
      .toEqual(['v/%C3%A4%231%3F.jpg', 'v/a,b;c@d+e.jpg', 'v/a[1].jpg']);
  });

  it('the hash changes when one file\'s content changes, not with the order', () => {
    const a = [['index.html', enc('<html>')], ['bad.glb', enc('glTF1')]];
    const b = [['index.html', enc('<html>')], ['bad.glb', enc('glTF2')]];
    expect(contentHash(a)).toMatch(/^[0-9a-f]{12}$/);
    expect(contentHash(a)).toBe(contentHash([...a].reverse()));
    expect(contentHash(a)).not.toBe(contentHash(b));
  });

  it('the live cache changes with the worker body (a fix of the worker alone gets a new store)', () => {
    const files = [['index.html', enc('<html>')]];
    const names = (body) => Object.keys(cacheGroups(files, body));
    expect(names('/* v1 */')).toHaveLength(1);
    expect(names('/* v1 */')[0]).toMatch(/^frechenlehen-[0-9a-f]{12}$/);
    expect(names('/* v1 */')).not.toEqual(names('/* v2 */'));
    expect(buildWorker(files, '/* v1 */')).toContain(`const CACHES = {"${names('/* v1 */')[0]}":["index.html"]};`);
  });

  it('the worker source carries the caches in front of the body', () => {
    const src = workerSource({ 'frechenlehen-abc123': ['index.html'] }, '/* body */');
    expect(src).toContain('const CACHES = {"frechenlehen-abc123":["index.html"]};');
    expect(src.trimEnd().endsWith('/* body */')).toBe(true);
  });
});

describe('a cache per plan version (issue #59)', () => {
  const version = [['v/2026-11-25/frechenlehen.glb', enc('glTF-a')], ['v/2026-11-25/plans/eg.svg', enc('<svg/>')]];
  const groups = (live, body = '/* w */') => cacheGroups([...live, ...version, ['sw.js', enc('x')]], body);

  it('puts a version\'s files in a cache of their own, the rest in the live cache', () => {
    const g = groups([['index.html', enc('<html>')]]);
    const [live, v] = Object.keys(g);
    expect(v).toMatch(/^frechenlehen-v-2026-11-25-[0-9a-f]{12}$/);
    expect(g[v]).toEqual(['v/2026-11-25/frechenlehen.glb', 'v/2026-11-25/plans/eg.svg']);
    expect(g[live]).toEqual(['index.html']);
  });

  it('a version\'s cache keeps its name when only the live build or the worker changes', () => {
    const vname = (g) => Object.keys(g).find((n) => n.startsWith('frechenlehen-v-'));
    const a = groups([['index.html', enc('<html>')]]), b = groups([['index.html', enc('<html2>')]], '/* w2 */');
    expect(vname(a)).toBe(vname(b));
    expect(Object.keys(a)[0]).not.toBe(Object.keys(b)[0]);
  });
});
