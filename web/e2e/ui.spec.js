import { test, expect } from '@playwright/test';
import { choose } from './menu.js';
import { utimesSync } from 'node:fs';
import { shot } from './pixels.js';

async function open(page) {
  await page.goto('/');
  await page.waitForFunction(() => window.__fl?.ready === true);
}

const stage = (page) => page.evaluate(() => document.body.dataset.stage);
const vis = (page, name) => page.evaluate((n) => window.__fl.visible(n), name);

test('clicking "Detailmodell" selects the detail stage', async ({ page }) => {
  await open(page);
  await choose(page, 'Darstellung', 'Detailmodell');
  expect(await stage(page)).toBe('detail');
  expect(await page.evaluate(() => window.__fl.progress)).toBe(2);
});

test('"1. Stock" hides the roof collection, keeps the ground', async ({ page }) => {
  await open(page);
  await choose(page, 'Modell', '1. Stock');
  expect(await page.evaluate(() => document.body.dataset.cutaway)).toBe('noroof');
  for (const n of ['Dach', 'Dach_Sparren', 'Verschalung_West', 'Giebel']) expect(await vis(page, n)).toBe(false);
  for (const n of ['Gelaende', 'OG_Waende', 'EG_Waende']) expect(await vis(page, n)).toBe(true);
});

test('"Erdgeschoss" also hides the OG and its balconies', async ({ page }) => {
  await open(page);
  await choose(page, 'Modell', 'Erdgeschoss');
  expect(await page.evaluate(() => document.body.dataset.cutaway)).toBe('eg');
  for (const n of ['Dach', 'OG_Waende', 'OG_Decke_EG', 'OG_Laeden_Querbretter', 'Balkon_OG_Nord', 'Balkon_OG_Ost', 'Balkon_OG_Sued'])
    expect(await vis(page, n)).toBe(false);
  for (const n of ['Gelaende', 'EG_Waende', 'Balkon_EG_Nord']) expect(await vis(page, n)).toBe(true);
  // the OG workshop stove's fire goes with the OG (it floated over the EG), the EG fires stay
  expect(await page.evaluate(() => window.__fl.fires())).toEqual(['EG', 'EG', 'EG', 'EG']);
  await choose(page, 'Darstellung', 'Detailmodell');
  await page.waitForTimeout(500);
  await shot(page, 'cutaway_eg.png');                                       // for the eye
  await choose(page, 'Modell', 'Ganzes Haus');
  expect(await vis(page, 'Dach')).toBe(true);
  expect((await page.evaluate(() => window.__fl.fires())).sort()).toEqual(['EG', 'EG', 'EG', 'EG', 'OG']);
});

for (const [w, h] of [[1280, 720], [1920, 1080]])
  test(`controls don't overlap at ${w}×${h}`, async ({ page }) => {
    await page.setViewportSize({ width: w, height: h });
    await open(page);
    const boxes = await page.evaluate(() =>
      ['.fl-title', '.fl-tools'].map((s) => document.querySelector(s).getBoundingClientRect().toJSON()));
    for (let i = 0; i < boxes.length; i++)
      for (let j = i + 1; j < boxes.length; j++) {
        const a = boxes[i], b = boxes[j];
        const overlap = a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom;
        expect(overlap, `${i}/${j}`).toBe(false);
      }
    for (const b of boxes) expect(b.right <= w && b.bottom <= h && b.left >= 0 && b.top >= 0).toBe(true);
    // every control group sits on its own paper panel, so it stays readable on the dusk sky
    const bgs = await page.evaluate(() =>
      ['.fl-title', '.fl-tools'].map((s) => getComputedStyle(document.querySelector(s)).backgroundColor));
    for (const bg of bgs) expect(bg).not.toBe('rgba(0, 0, 0, 0)');
    await shot(page, `ui_${w}.png`);
  });

test('furniture shows only in Eingerichtet and follows the cutaway', async ({ page }) => {
  await open(page);
  const set = (p, c) => page.evaluate(([p, c]) => { window.__fl.setProgress(p); window.__fl.setCutaway(c); }, [p, c]);
  await set(3, 'all');
  for (const n of ['OG_Moebel', 'EG_Tisch']) expect(await vis(page, n)).toBe(false);
  await set(4, 'all');
  for (const n of ['OG_Moebel', 'EG_Tisch']) expect(await vis(page, n)).toBe(true);
  await set(4, 'eg');
  expect(await vis(page, 'OG_Moebel')).toBe(false);
  expect(await vis(page, 'EG_Moebel')).toBe(true);
  await set(4, 'all');
  expect(await vis(page, 'OG_Moebel')).toBe(true);
});

test('the built-in Ofen shows in every stage, without dimensions, and "Ofen" opens its sub-model', async ({ page }) => {
  await open(page);
  expect(await page.evaluate(() => window.__fl.lineSources)).toContain('EG_Ofen_Koerper');   // Skizze lines
  for (const p of [0, 1, 2, 3, 4]) {
    await page.evaluate((q) => window.__fl.setProgress(q), p);
    expect(await vis(page, 'EG_Ofen_Koerper')).toBe(true);
    expect(await vis(page, 'EG_Ofen_Bett')).toBe(true);
  }
  expect(await page.locator('.dim').count()).toBe(0);
  await choose(page, 'Modell', 'Ofen');
  await page.waitForURL(/\/ofen\.html$/);
  await page.waitForFunction(() => window.__ofen?.ready === true);
  await expect(page.locator('.dim', { hasText: 'Bett 190' })).toBeVisible();
  await expect(page.locator('.dim', { hasText: 'Bank 160' })).toBeVisible();
});

test('the stoves burn from the Detailmodell on, and the flames move', async ({ page }) => {
  await open(page);
  expect(await page.evaluate(() => window.__fl.fire())).toBe(false);          // Skizze: no fire
  await choose(page, 'Darstellung', 'Detailmodell');
  const a = await page.evaluate(() => window.__fl.fire());
  await page.waitForTimeout(300);
  const b = await page.evaluate(() => window.__fl.fire());
  expect(a).toBeGreaterThan(0);
  expect(b).not.toBe(a);
});

test('URL ?cam=&at=&p= sets the viewpoint (model coords) and the stage', async ({ page }) => {
  await page.goto('/?cam=11.7,3.13,1.6&at=10.01,4.895,0.9&p=2');
  await page.waitForFunction(() => window.__fl?.ready === true);
  expect(await stage(page)).toBe('detail');
  const c = await page.evaluate(() => window.__fl.project(10.01, 4.895, 0.9));   // the target sits mid-screen
  const vp = page.viewportSize();
  expect(Math.abs(c.x - vp.width / 2)).toBeLessThan(2);
  expect(Math.abs(c.y - vp.height / 2)).toBeLessThan(2);
  expect(await page.evaluate(() => window.__fl.cameraAt())).toEqual([11.7, 3.13, 1.6]);
});

test('URL ?fov= sets the vertical field of view (default 28°), kept in the URL across a reload', async ({ page }) => {
  await open(page);
  expect(await page.evaluate(() => window.__fl.fov)).toBe(28);
  expect(new URL(page.url()).searchParams.has('fov')).toBe(false);
  await page.goto('/?cam=8.5,5.97,4.3&at=6.19,4.65,3.75&p=4&fov=60');
  await page.waitForFunction(() => window.__fl?.ready === true);
  expect(await page.evaluate(() => window.__fl.fov)).toBe(60);
  await page.evaluate(() => window.__fl.lookFrom(8.4, 5.9, 4.3));         // a view change rewrites the URL
  await expect.poll(() => new URL(page.url()).searchParams.get('cam')).toBe('8.4,5.9,4.3');
  expect(new URL(page.url()).searchParams.get('fov')).toBe('60');
  await page.reload();
  await page.waitForFunction(() => window.__fl?.ready === true);
  expect(await page.evaluate(() => window.__fl.fov)).toBe(60);
});

test('the URL follows the view (camera, target, stage, cutaway); a reload restores it', async ({ page }) => {
  await open(page);
  await choose(page, 'Modell', '1. Stock');                          // opens at its own standard Standpunkt
  await page.evaluate(() => window.__fl.lookFrom(-22, 34, 13));
  await choose(page, 'Darstellung', 'Eingerichtet');
  await expect.poll(() => new URL(page.url()).searchParams.get('p')).toBe('4');
  expect(new URL(page.url()).searchParams.get('cut')).toBe('noroof');
  const q = new URL(page.url()).searchParams;
  expect(q.get('cam').split(',').map(Number)).toEqual([-22, 34, 13]);
  expect(q.get('p')).toBe('4');
  expect(q.get('at')).toBeTruthy();
  const before = await page.evaluate(() => window.__fl.cameraAt());
  await page.reload();
  await page.waitForFunction(() => window.__fl?.ready === true);
  const after = await page.evaluate(() => window.__fl.cameraAt());
  after.forEach((v, i) => expect(Math.abs(v - before[i])).toBeLessThan(0.01));
  expect(await stage(page)).toBe('furnished');
  expect(await page.evaluate(() => document.body.dataset.cutaway)).toBe('noroof');
  expect(await vis(page, 'Dach')).toBe(false);
});

test('saving a core file (code/*.py) re-exports the blueprint and reloads the page at the same view', async ({ page }) => {
  test.setTimeout(120_000);
  await page.goto('/?cam=-22,34,13&at=7.4,6.4,3.2&p=4&cut=noroof');
  await page.waitForFunction(() => window.__fl?.ready === true);
  await page.evaluate(() => { window.__beforeSave = true; });
  const reloaded = page.waitForEvent('load', { timeout: 60_000 });
  const now = new Date();
  utimesSync(new URL('../../code/tour.py', import.meta.url), now, now);   // "saved", content unchanged
  await reloaded;
  await page.waitForFunction(() => window.__fl?.ready === true);
  expect(await page.evaluate(() => window.__beforeSave)).toBeUndefined();
  const cam = await page.evaluate(() => window.__fl.cameraAt());
  [-22, 34, 13].forEach((v, i) => expect(Math.abs(cam[i] - v)).toBeLessThan(0.01));
  expect(await stage(page)).toBe('furnished');
  expect(await page.evaluate(() => document.body.dataset.cutaway)).toBe('noroof');
});
