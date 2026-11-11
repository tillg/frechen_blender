// The production build (web/dist/), served by the dev server on 5377 under the GitHub Pages sub-path.
// No test hook here (production), so it checks requests and pixels.
import { test, expect } from '@playwright/test';
import { choose } from '../e2e/menu.js';
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
  await expect(page.getByRole('button', { name: 'Darstellung', exact: true })).toBeVisible({ timeout: 60_000 });   // after the 16 MB GLB
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

test('Ofen page is part of the build', async ({ page }) => {
  const failed = [], errors = [];
  let glb = 0;
  page.on('response', (r) => {
    if (r.status() >= 400) failed.push(`${r.status()} ${r.url()}`);
    if (r.url().endsWith('/frechen_blender/ofen.glb') && r.ok()) glb++;
  });
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto(BASE);
  await choose(page, 'Modell', 'Ofen');          // the house links to it
  await page.waitForURL(/\/frechen_blender\/ofen\.html$/);
  await expect(page.locator('.dim', { hasText: 'Tür 65' })).toBeVisible({ timeout: 30_000 });
  expect(failed).toEqual([]);
  expect(errors).toEqual([]);
  expect(glb).toBe(1);
  await choose(page, 'Modell', 'Ganzes Haus');         // and back
  await page.waitForURL(/\/frechen_blender\/(\?m=haus)?$/);
});

test('desk page is part of the build, with its screen textures', async ({ page }) => {
  const failed = [], errors = [];
  let glb = 0, tex = 0;
  page.on('response', (r) => {
    if (r.status() >= 400) failed.push(`${r.status()} ${r.url()}`);
    if (r.url().endsWith('/frechen_blender/desk.glb') && r.ok()) glb++;
    if (/\/frechen_blender\/textures\/screen_\w+\.jpg$/.test(r.url()) && r.ok() && r.frame().url().endsWith('/desk.html')) tex++;   // the house loads them too
  });
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto(BASE);
  await choose(page, 'Modell', 'Schreibtisch');
  await page.waitForURL(/\/frechen_blender\/desk\.html$/);
  await expect(page.locator('.dim', { hasText: 'Tisch 194.8' })).toBeVisible({ timeout: 30_000 });
  await expect.poll(() => tex).toBe(2);
  expect(failed).toEqual([]);
  expect(errors).toEqual([]);
  expect(glb).toBe(1);
  await choose(page, 'Modell', 'Ganzes Haus');
  await page.waitForURL(/\/frechen_blender\/(\?m=haus)?$/);
});

test('bad page is part of the build', async ({ page }) => {
  const failed = [], errors = [];
  let glb = 0;
  page.on('response', (r) => {
    if (r.status() >= 400) failed.push(`${r.status()} ${r.url()}`);
    if (r.url().endsWith('/frechen_blender/bad.glb') && r.ok()) glb++;
  });
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto(BASE);
  await choose(page, 'Modell', 'Bad Oma & Opa');
  await page.waitForURL(/\/frechen_blender\/bad\.html$/);
  await expect(page.locator('.dim', { hasText: 'Waschtrog 100' })).toBeVisible({ timeout: 30_000 });
  expect(failed).toEqual([]);
  expect(errors).toEqual([]);
  expect(glb).toBe(1);
  await choose(page, 'Modell', 'Ganzes Haus');
  await page.waitForURL(/\/frechen_blender\/(\?m=haus)?$/);
});

test('kueche page is part of the build', async ({ page }) => {
  const failed = [], errors = [];
  let glb = 0;
  page.on('response', (r) => {
    if (r.status() >= 400) failed.push(`${r.status()} ${r.url()}`);
    if (r.url().endsWith('/frechen_blender/kueche.glb') && r.ok()) glb++;
  });
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto(BASE);
  await choose(page, 'Modell', 'Küche');
  await page.waitForURL(/\/frechen_blender\/kueche\.html$/);
  await expect(page.locator('.dim', { hasText: 'Herd 80' })).toBeVisible({ timeout: 30_000 });
  expect(failed).toEqual([]);
  expect(errors).toEqual([]);
  expect(glb).toBe(1);
  await choose(page, 'Modell', 'Ganzes Haus');
  await page.waitForURL(/\/frechen_blender\/(\?m=haus)?$/);
});

test('gaeste_wc page is part of the build', async ({ page }) => {
  const failed = [], errors = [];
  let glb = 0;
  page.on('response', (r) => {
    if (r.status() >= 400) failed.push(`${r.status()} ${r.url()}`);
    if (r.url().endsWith('/frechen_blender/gaeste_wc.glb') && r.ok()) glb++;
  });
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto(BASE);
  await choose(page, 'Modell', 'Gäste-WC');
  await page.waitForURL(/\/frechen_blender\/gaeste_wc\.html$/);
  await expect(page.locator('.dim', { hasText: 'HWB 40' })).toBeVisible({ timeout: 30_000 });
  expect(failed).toEqual([]);
  expect(errors).toEqual([]);
  expect(glb).toBe(1);
  await choose(page, 'Modell', 'Ganzes Haus');
  await page.waitForURL(/\/frechen_blender\/(\?m=haus)?$/);
});
