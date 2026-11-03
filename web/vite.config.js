import { defineConfig } from 'vite';

export default defineConfig(({ command, isPreview }) => ({
  base: command === 'build' || isPreview ? '/frechen_blender/' : '/',   // GitHub Pages sub-path
  // addons (GLTFLoader, OrbitControls) import 'three': give them the WebGPU build the app uses
  resolve: { alias: [{ find: /^three$/, replacement: 'three/webgpu' }] },
  build: { target: 'es2022' },                               // top-level await in main.js
  test: { include: ['src/**/*.test.js'] },
}));
