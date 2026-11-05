// Dev server only: when a core file (code/*.py) is saved, regenerate the .glb files
// (npm run blueprint) and reload the page. The viewer keeps its view in the URL, so the reload
// shows the changed model from the same spot. A failed export is logged and does not reload.
import { spawn } from 'node:child_process';
import { resolve, sep } from 'node:path';

export function blueprintWatch() {
  return {
    name: 'blueprint-watch',
    apply: 'serve',
    configureServer(server) {
      if (process.env.VITEST) return;                            // unit tests: no watching
      const code = resolve(server.config.root, '../code') + sep;
      const log = server.config.logger;
      let timer = 0, running = false, again = false;
      function run() {
        if (running) { again = true; return; }                  // one export at a time
        running = true;
        log.info('core changed: npm run blueprint', { timestamp: true });
        const p = spawn('npm', ['run', 'blueprint'], { cwd: server.config.root, stdio: ['ignore', 'ignore', 'pipe'] });
        let err = '';
        p.stderr.on('data', (d) => { err += d; });
        p.on('close', (status) => {
          running = false;
          if (again) { again = false; run(); return; }           // saved again meanwhile: export again first
          if (status === 0) server.ws.send({ type: 'full-reload', path: '*' });
          else log.error(`blueprint failed (exit ${status}), page not reloaded:\n${err}`, { timestamp: true });
        });
      }
      const onFile = (file) => {
        if (!file.startsWith(code) || !file.endsWith('.py')) return;
        clearTimeout(timer);
        timer = setTimeout(run, 300);                            // several saves in a row: one export
      };
      server.watcher.add(code);
      server.watcher.on('change', onFile).on('add', onFile);
    },
  };
}
