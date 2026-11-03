// The production build, served by `vite preview` under the GitHub Pages sub-path.
// No test hook here (production), so it checks requests and pixels.
import { test, expect } from '@playwright/test';
import { shot } from '../e2e/pixels.js';

const BASE = '/frechen_blender/';

test('page loads under /frechen_blender/ with the blueprint', async ({ page }) => {
  const outside = [], failed = [], errors = [];
  let glb = 0;
  page.on('request', (r) => {
    const u = new URL(r.url());
    if (u.hostname === 'localhost' && !u.pathname.startsWith(BASE)) outside.push(u.pathname);
  });
  page.on('response', (r) => {
    if (r.status() >= 400) failed.push(`${r.status()} ${r.url()}`);
    if (r.url().endsWith('/frechenlehen.glb') && r.ok()) glb++;
  });
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto(BASE);
  await expect(page.getByRole('button', { name: 'Detailmodell' })).toBeVisible({ timeout: 60_000 });   // after the 16 MB GLB
  await page.waitForTimeout(4000);
  expect(outside).toEqual([]);
  expect(failed).toEqual([]);
  expect(errors).toEqual([]);
  expect(glb).toBe(1);
  expect(await page.evaluate(() => typeof window.__fl)).toBe('undefined');   // no test hook in production
  const img = await shot(page, 'preview.png');
  let ink = 0;
  for (let i = 0; i < img.data.length; i += 16) if (img.data[i] < 110) ink++;
  expect(ink / (img.data.length / 16)).toBeGreaterThan(0.01);               // the Skizze is drawn
});
