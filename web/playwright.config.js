import { defineConfig } from '@playwright/test';

const DEV = 5199, PREVIEW = 4199;

export default defineConfig({
  outputDir: 'test-results',
  timeout: 120_000,
  workers: 1,
  use: {
    viewport: { width: 1280, height: 720 },
    // real GPU (Metal via ANGLE) instead of SwiftShader; WebGPU is still off in headless
    // Chromium, so the viewer runs on its WebGL2 fallback here
    launchOptions: { args: ['--use-angle=metal', '--enable-gpu'] },
  },
  projects: [
    { name: 'dev', testDir: 'e2e', use: { baseURL: `http://localhost:${DEV}/` } },
    { name: 'preview', testDir: 'e2e-preview', use: { baseURL: `http://localhost:${PREVIEW}/` } },
  ],
  webServer: [
    { command: `npx vite --port ${DEV} --strictPort`, url: `http://localhost:${DEV}/`, reuseExistingServer: false },
    // the production build, as GitHub Pages serves it
    { command: `npm run build && npx vite preview --port ${PREVIEW} --strictPort`, port: PREVIEW, reuseExistingServer: false, timeout: 120_000 },
  ],
});
