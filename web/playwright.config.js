import { defineConfig } from '@playwright/test';

const APP = 5377;   // the one dev server (CLAUDE.md): / the viewer, /frechen_blender/ the build

export default defineConfig({
  outputDir: 'test-results',
  timeout: 120_000,
  workers: 1,
  // @eye tests only make pictures for a human: run them on request (npx playwright test --grep @eye;
  // a config grepInvert would also drop them then, so it is left out when @eye is asked for)
  grepInvert: process.argv.some((a) => a.includes('@eye')) ? undefined : /@eye/,
  use: {
    viewport: { width: 1280, height: 720 },
    // real GPU (Metal via ANGLE) instead of SwiftShader; WebGPU is still off in headless
    // Chromium, so the viewer runs on its WebGL2 fallback here
    launchOptions: { args: ['--use-angle=metal', '--enable-gpu'] },
  },
  projects: [
    { name: 'dev', testDir: 'e2e', use: { baseURL: `http://localhost:${APP}/` } },
    { name: 'build', testDir: 'e2e-preview', testMatch: /build\.setup\.js/ },
    // the production build, under /frechen_blender/ as GitHub Pages serves it
    { name: 'preview', testDir: 'e2e-preview', testMatch: /\.spec\.js/, dependencies: ['build'], use: { baseURL: `http://localhost:${APP}/` } },
  ],
  // no server of its own: use the one on 5377, start it there only if none is running
  webServer: { command: 'npm run dev', url: `http://localhost:${APP}/`, reuseExistingServer: true, timeout: 120_000 },
});
