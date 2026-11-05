// Dev server only: also serve the production build (web/dist/, `npm run build`) under
// /frechen_blender/, the GitHub Pages path, so one server shows the source (/) and the build.
import { readFile, stat } from 'node:fs/promises';
import { extname, join, normalize, resolve } from 'node:path';

const BASE = '/frechen_blender/';
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.glb': 'model/gltf-binary',
  '.json': 'application/json', '.png': 'image/png', '.svg': 'image/svg+xml', '.woff2': 'font/woff2' };

export function serveBuild() {
  return {
    name: 'serve-build',
    apply: 'serve',
    configureServer(server) {
      const dist = resolve(server.config.root, 'dist');
      server.middlewares.use(async (req, res, next) => {
        const path = decodeURIComponent(new URL(req.url, 'http://x').pathname);
        if (!path.startsWith(BASE)) return next();
        let file = join(dist, normalize(path.slice(BASE.length)));
        if (!file.startsWith(dist)) return next();                       // no way out of dist/
        try {
          if ((await stat(file)).isDirectory()) file = join(file, 'index.html');
          const body = await readFile(file);
          res.setHeader('Content-Type', TYPES[extname(file)] ?? 'application/octet-stream');
          res.end(body);
        } catch {
          res.statusCode = 404;
          res.end(`not in web/dist/ (npm run build): ${path}`);
        }
      });
    },
  };
}
