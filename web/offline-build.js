// Build only (issue #56, ADR-004-CTPY): after `vite build`, write web/dist/sw.js, the service worker
// that keeps every file of the build for offline use: the list of dist's files and their content
// hash (src/precache.js) in front of the worker body src/sw.js.
import { readdir, readFile, writeFile } from 'node:fs/promises';
import { join, relative, resolve, sep } from 'node:path';
import { buildWorker } from './src/precache.js';

async function walk(dir) {
  const out = [];
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const p = join(dir, e.name);
    out.push(...(e.isDirectory() ? await walk(p) : [p]));
  }
  return out;
}

export function offlineBuild() {
  let root, outDir;
  return {
    name: 'offline-build',
    apply: 'build',
    configResolved(config) { root = config.root; outDir = resolve(config.root, config.build.outDir); },
    async closeBundle() {
      const paths = (await walk(outDir)).map((f) => relative(outDir, f).split(sep).join('/')).filter((p) => p !== 'sw.js');
      const entries = await Promise.all(paths.map(async (p) => [p, await readFile(join(outDir, p))]));
      const body = await readFile(join(root, 'src/sw.js'), 'utf8');
      await writeFile(join(outDir, 'sw.js'), buildWorker(entries, body));
    },
  };
}
