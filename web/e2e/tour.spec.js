import { test, expect } from '@playwright/test';
import { shot } from './pixels.js';

async function open(page) {
  await page.goto('/');
  await page.waitForFunction(() => window.__fl?.ready === true);
}

const tourState = (page) => page.evaluate(() => document.body.dataset.tour);
const cam = (page) => page.evaluate(() => window.__fl.camera);          // model coords
const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);

test('Rundgang starts at the first key in stage Eingerichtet, whole house', async ({ page }) => {
  await open(page);
  await page.getByRole('button', { name: 'Nur EG' }).click();
  await page.getByRole('button', { name: 'Rundgang', exact: true }).click();
  expect(await tourState(page)).toBe('playing');
  expect(await page.evaluate(() => document.body.dataset.stage)).toBe('furnished');
  expect(await page.evaluate(() => document.body.dataset.cutaway)).toBe('all');
  await expect(page.getByRole('button', { name: 'Beenden' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Detailmodell' })).toBeHidden();   // timeline bar hidden
  await page.evaluate(() => window.__fl.tour.seek(0));
  expect(await tourState(page)).toBe('paused');
  expect(dist(await cam(page), await page.evaluate(() => window.__fl.tourKey(0)))).toBeLessThan(1e-3);
});

test('playing advances the camera along the route', async ({ page }) => {
  await open(page);
  await page.getByRole('button', { name: 'Rundgang', exact: true }).click();
  const c0 = await cam(page);
  await page.waitForTimeout(1500);
  expect(await page.evaluate(() => window.__fl.tour.time)).toBeGreaterThan(0.8);
  expect(dist(await cam(page), c0)).toBeGreaterThan(1);                 // orbit: ~4 m/s
  await page.getByRole('button', { name: 'Rundgang anhalten' }).click();
  expect(await tourState(page)).toBe('paused');
  const t = await page.evaluate(() => window.__fl.tour.time);
  await page.waitForTimeout(500);
  expect(await page.evaluate(() => window.__fl.tour.time)).toBe(t);
});

test('Beenden restores the previous view', async ({ page }) => {
  await open(page);
  const before = await cam(page);
  await page.getByRole('button', { name: 'Rundgang', exact: true }).click();
  await page.evaluate(() => window.__fl.tour.seek(60));
  await page.getByRole('button', { name: 'Beenden' }).click();
  expect(await tourState(page)).toBe('off');
  await page.waitForTimeout(300);
  expect(dist(await cam(page), before)).toBeLessThan(1e-3);
  await expect(page.getByRole('button', { name: 'Detailmodell' })).toBeVisible();
});

test('stills along the Rundgang (for the eye)', { tag: '@eye' }, async ({ page }) => {
  await open(page);
  await page.getByRole('button', { name: 'Rundgang', exact: true }).click();
  for (const s of [10, 30, 40, 55, 75, 95, 115, 135]) {
    await page.evaluate((x) => window.__fl.tour.seek(x), s);
    await page.waitForTimeout(400);
    const img = await shot(page, `tour_${String(s).padStart(3, '0')}s.png`);
    let lit = 0;
    for (let i = 0; i < img.data.length; i += 64) if (img.data[i] + img.data[i + 1] + img.data[i + 2] > 90) lit++;
    expect(lit / (img.data.length / 64), `${s} s`).toBeGreaterThan(0.3);   // not a black frame
  }
});

test('paused, dragging looks around in place', async ({ page }) => {
  await open(page);
  await page.getByRole('button', { name: 'Rundgang', exact: true }).click();
  await page.evaluate(() => window.__fl.tour.seek(40));
  const c0 = await cam(page);
  const v0 = await page.evaluate(() => window.__fl.view);
  await page.mouse.move(640, 360);
  await page.mouse.down();
  await page.mouse.move(400, 330, { steps: 10 });
  await page.mouse.up();
  await page.waitForTimeout(800);
  expect(dist(await cam(page), c0)).toBeLessThan(0.15);                // stays where it stopped
  const v1 = await page.evaluate(() => window.__fl.view);
  expect(v0[0] * v1[0] + v0[1] * v1[1] + v0[2] * v1[2]).toBeLessThan(0.99);   // but the view turned (> 8°)
  expect(await tourState(page)).toBe('paused');
});

const tourTime = (page) => page.evaluate(() => window.__fl.tour.time);

test('plays at 0.75× the film speed', async ({ page }) => {
  await open(page);
  await page.getByRole('button', { name: 'Rundgang', exact: true }).click();
  const [t0, r0] = await page.evaluate(() => [window.__fl.tour.time, performance.now()]);
  await page.waitForTimeout(3000);
  const [t1, r1] = await page.evaluate(() => [window.__fl.tour.time, performance.now()]);
  expect((t1 - t0) / ((r1 - r0) / 1000)).toBeGreaterThan(0.65);
  expect((t1 - t0) / ((r1 - r0) / 1000)).toBeLessThan(0.8);
});

test('without Endlos it stops at the end, with Endlos it starts over', async ({ page }) => {
  await open(page);
  await page.getByRole('button', { name: 'Rundgang', exact: true }).click();
  const T = await page.evaluate(() => window.__fl.tour.duration);
  await page.evaluate((x) => window.__fl.tour.seek(x), T - 0.3);
  await page.getByRole('button', { name: 'Rundgang abspielen' }).click();
  await page.waitForTimeout(1500);
  expect(await tourState(page)).toBe('paused');
  expect(await tourTime(page)).toBe(T);
  await page.getByRole('button', { name: 'Endlos' }).click();
  await expect(page.getByRole('button', { name: 'Endlos' })).toHaveAttribute('aria-pressed', 'true');
  await expect(page.getByRole('button', { name: 'Endlos' })).toHaveCSS('background-color', 'rgb(43, 41, 38)');   // dark like the active buttons
  await page.evaluate((x) => window.__fl.tour.seek(x), T - 0.3);
  await page.getByRole('button', { name: 'Rundgang abspielen' }).click();
  await page.waitForTimeout(1500);
  expect(await tourState(page)).toBe('playing');
  expect(await tourTime(page)).toBeLessThan(1.5);
  await page.getByRole('button', { name: 'Rundgang anhalten' }).click();
  const t = await tourTime(page);
  expect(dist(await cam(page), await page.evaluate((i) => window.__fl.tourKey(i), Math.round(t * 25)))).toBeLessThan(0.3);
});

test('cutaway buttons are off during the tour; resize while paused refits the lens', async ({ page }) => {
  await open(page);
  await page.getByRole('button', { name: 'Rundgang', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Nur EG' })).toBeDisabled();
  await page.evaluate(() => window.__fl.tour.seek(60));                  // inside: 16 mm
  const wide = await page.evaluate(() => window.__fl.fov);
  await page.setViewportSize({ width: 720, height: 1280 });
  await page.waitForTimeout(300);
  expect(wide).toBeCloseTo(64.65, 1);
  expect(await page.evaluate(() => window.__fl.fov)).toBeCloseTo(96.73, 1);   // portrait: 36 mm tall
  await page.getByRole('button', { name: 'Beenden' }).click();
  await expect(page.getByRole('button', { name: 'Nur EG' })).toBeEnabled();
});

test('the tour draws at most ~30 frames per second (the film has 25)', async ({ page }) => {
  await open(page);
  await page.getByRole('button', { name: 'Rundgang', exact: true }).click();
  const [d0, r0] = await page.evaluate(() => [window.__fl.draws, performance.now()]);
  await page.waitForTimeout(2000);
  const [d1, r1] = await page.evaluate(() => [window.__fl.draws, performance.now()]);
  expect((d1 - d0) / ((r1 - r0) / 1000)).toBeLessThan(32);
  expect((d1 - d0) / ((r1 - r0) / 1000)).toBeGreaterThan(15);
});
