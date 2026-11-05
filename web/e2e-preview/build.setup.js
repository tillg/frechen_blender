// Before the preview tests: the production build (web/dist/), which the dev server on 5377 serves
// under /frechen_blender/ like GitHub Pages (serve-build.js).
import { test } from '@playwright/test';
import { execSync } from 'node:child_process';

test('production build', () => {
  test.setTimeout(180_000);
  execSync('npm run build', { cwd: new URL('..', import.meta.url), stdio: 'pipe' });
});
