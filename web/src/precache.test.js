import { describe, expect, it } from 'vitest';
import { buildWorker, contentHash, precacheList, workerSource } from './precache.js';

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

  it('the version changes with the worker body (a fix of the worker alone gets a new store)', () => {
    const files = [['index.html', enc('<html>')]];
    const version = (src) => src.match(/const VERSION = "(\w+)";/)[1];
    expect(version(buildWorker(files, '/* v1 */'))).not.toBe(version(buildWorker(files, '/* v2 */')));
    expect(buildWorker(files, '/* v1 */')).toContain('const FILES = ["index.html"];');
  });

  it('the worker source carries version and list in front of the body', () => {
    const src = workerSource('abc123', ['index.html'], '/* body */');
    expect(src).toContain('const VERSION = "abc123";');
    expect(src).toContain('const FILES = ["index.html"];');
    expect(src.trimEnd().endsWith('/* body */')).toBe(true);
  });
});
