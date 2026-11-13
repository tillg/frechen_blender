import { defineConfig } from 'vite';
import { blueprintWatch } from './blueprint-watch.js';
import { serveBuild } from './serve-build.js';

export default defineConfig(({ command, isPreview }) => ({
  base: command === 'build' || isPreview ? '/frechen_blender/' : '/',   // GitHub Pages sub-path
  // addons (GLTFLoader, OrbitControls) import 'three': give them the WebGPU build the app uses
  resolve: { alias: [{ find: /^three$/, replacement: 'three/webgpu' }] },
  build: {
    target: 'es2022',                                        // top-level await in main.js
    rollupOptions: { input: ['index.html', 'ofen.html', 'desk.html', 'bad.html', 'kueche.html', 'gaeste_wc.html', 'regal.html', 'schrankbett.html', 'gaestebad.html'] },  // the house and the sub-models
  },
  plugins: [blueprintWatch(), serveBuild()],                // code/*.py saved: new .glb, reload;
                                                             // web/dist/ under /frechen_blender/
  test: { include: ['src/**/*.test.js'] },
}));
