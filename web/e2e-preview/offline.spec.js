// The production build as an offline web app (issue #56, ADR-004-CTPY): after the first visit the
// service worker has stored every file of the build; with the network off the pages still load,
// every response from the worker. The other preview specs block service workers (config).
import { test, expect } from '@playwright/test';
import { readFileSync, writeFileSync } from 'node:fs';
import { shot } from '../e2e/pixels.js';

const BASE = '/frechen_blender/';
test.use({ serviceWorkers: 'allow' });

// the live build's cache in a generated sw.js (the one key that is not a version's, issue #59)
const liveCache = (src) => src.match(/"(frechenlehen-[0-9a-f]{12})":\[/)[1];
const VERSION_ID = '2026-11-25';                                          // the first plan version (#59)

async function firstVisit(page) {
  await page.goto(BASE);
  await expect.poll(() => page.evaluate(async () => !!(await navigator.serviceWorker.getRegistration())),
    { timeout: 15_000 }).toBe(true);                                       // the build registers it
  await page.waitForFunction(() => navigator.serviceWorker.controller, null, { timeout: 90_000 });   // all stored
}

test('offline after the first visit: house, sub-model, plan sheet, Vorlagen', async ({ page, context }) => {
  test.setTimeout(240_000);
  await firstVisit(page);
  const manifest = await page.locator('link[rel="manifest"]').getAttribute('href');
  expect(manifest).toBe(`${BASE}manifest.webmanifest`);
  await expect(page.locator('link[rel="apple-touch-icon"]')).toHaveAttribute('href', `${BASE}icon-180.png`);

  await context.setOffline(true);
  const ours = [], errors = [];
  page.on('response', (r) => r.url().includes(BASE) && ours.push([r.url(), r.status(), r.fromServiceWorker()]));
  page.on('pageerror', (e) => errors.push(e.message));

  await page.goto(`${BASE}?m=haus`);
  await expect(page.getByRole('button', { name: 'Darstellung', exact: true })).toBeVisible({ timeout: 60_000 });
  await page.waitForTimeout(4000);
  const img = await shot(page, 'offline-house.png');
  let ink = 0;
  for (let i = 0; i < img.data.length; i += 16) if (img.data[i] < 110) ink++;
  expect(ink / (img.data.length / 16)).toBeGreaterThan(0.01);               // the house is drawn, offline
  const m = await page.evaluate(async (u) => (await fetch(u)).json(), manifest);
  expect([m.name, m.display, m.start_url]).toEqual(['Frechenlehen', 'standalone', './']);

  await page.goto(`${BASE}bad.html?cam=6.823,-3.89,5.935&at=1.024,1.909,1.2&look=full`);
  await expect(page.locator('.dim', { hasText: 'HWB 60' })).toBeVisible({ timeout: 30_000 });

  await page.goto(`${BASE}plans/eg.svg`);
  expect(await page.content()).toContain('Grundriss EG');

  await page.goto(`${BASE}?m=haus&v=${VERSION_ID}`);                       // a plan version (#59)
  await expect(page.getByRole('button', { name: 'Version', exact: true })).toContainText(VERSION_ID, { timeout: 60_000 });
  await page.goto(`${BASE}v/${VERSION_ID}/plans/eg.svg`);
  expect(await page.content()).toContain('Grundriss EG');

  await page.goto(`${BASE}vorlagen.html?b=garderobe`);
  await expect(page.locator('figcaption', { hasText: 'Toilette in Mallnitz' })).toBeVisible();
  const ok = await page.evaluate(async () => Promise.all([...document.querySelectorAll('img')].map((i) =>
    (i.complete ? i.naturalWidth > 0 : new Promise((r) => { i.onload = () => r(true); i.onerror = () => r(false); })))));
  expect(ok.length).toBeGreaterThan(0);
  expect(ok.every(Boolean)).toBe(true);

  expect(ours.length).toBeGreaterThan(10);
  for (const g of ['frechenlehen.glb', 'bad.glb', `v/${VERSION_ID}/frechenlehen.glb`]) expect(ours.some(([u]) => u.endsWith(`${BASE}${g}`)), g).toBe(true);
  expect(ours.filter(([, s, sw]) => s !== 200 || !sw)).toEqual([]);         // all from the worker's store
  expect(errors).toEqual([]);
});

test('the badge reports the download and Offline bereit, then goes; not on the next visit', async ({ page }) => {
  test.setTimeout(180_000);
  await page.addInitScript(() => {                                            // every text the badge shows
    window.__seen = [];
    new MutationObserver(() => {
      const t = document.querySelector('.fl-offline')?.textContent;
      if (t && window.__seen.at(-1) !== t) window.__seen.push(t);
    }).observe(document, { subtree: true, childList: true, characterData: true });
  });
  await firstVisit(page);
  const badge = page.locator('.fl-offline');
  await expect(badge).toHaveText('Offline bereit', { timeout: 30_000 });
  const seen = await page.evaluate(() => window.__seen);
  expect(seen.some((t) => /^Offline: \d+ \/ \d+$/.test(t))).toBe(true);
  expect(seen.at(-1)).toBe('Offline bereit');
  await shot(page, 'offline-badge.png');
  await expect(badge).toBeHidden({ timeout: 10_000 });
  await page.reload();
  await expect(page.getByRole('button', { name: 'Darstellung', exact: true })).toBeVisible({ timeout: 60_000 });
  await page.waitForTimeout(2000);
  expect(await page.evaluate(() => window.__seen)).toEqual([]);              // stored already: no badge
});

test('a new build replaces the stored one; offline then the new one', async ({ page, context }) => {
  test.setTimeout(180_000);
  const sw = new URL('../dist/sw.js', import.meta.url);
  const built = readFileSync(sw, 'utf8');
  const old = liveCache(built);
  try {
    await firstVisit(page);
    const keys = () => page.evaluate(async () => (await caches.keys()).filter((k) => k.startsWith('frechenlehen-') && !k.startsWith('frechenlehen-v-')));
    expect(await keys()).toEqual([old]);
    writeFileSync(sw, built.replace(`"${old}"`, '"frechenlehen-next000build"'));               // a new deploy
    await page.evaluate(async () => (await navigator.serviceWorker.getRegistration()).update());
    await expect.poll(keys, { timeout: 90_000 }).toEqual(['frechenlehen-next000build']);   // the old live store is gone
    await context.setOffline(true);
    await page.reload();
    await expect(page.getByRole('button', { name: 'Darstellung', exact: true })).toBeVisible({ timeout: 60_000 });
  } finally {
    writeFileSync(sw, built);
  }
});

test('"Update laden": the newest says so; after a new deploy it stores the new build and reloads into it', async ({ page }) => {
  test.setTimeout(240_000);
  const sw = new URL('../dist/sw.js', import.meta.url);
  const built = readFileSync(sw, 'utf8');
  const old = liveCache(built);
  const keys = () => page.evaluate(async () => (await caches.keys()).filter((k) => k.startsWith('frechenlehen-') && !k.startsWith('frechenlehen-v-')));
  const button = page.locator('.fl-update');
  try {
    await firstVisit(page);
    await expect(page.getByRole('button', { name: '↻ Update laden', exact: true })).toBeVisible();
    await expect(button).toHaveText('↻ Update laden');
    await button.click();
    await expect(button).toHaveText('Schon aktuell ✓', { timeout: 30_000 });
    await expect(button).toHaveText('↻ Update laden', { timeout: 10_000 });
    expect(await keys()).toEqual([old]);
    writeFileSync(sw, built.replace(`"${old}"`, '"frechenlehen-next000build"'));               // a new deploy
    await page.evaluate(() => { window.__before = true; });
    const reloaded = page.waitForEvent('load', { timeout: 120_000 });
    await button.click();
    await reloaded;                                                              // into the new build
    expect(await page.evaluate(() => window.__before)).toBeUndefined();
    expect(await keys()).toEqual(['frechenlehen-next000build']);
    await expect(button).toHaveText('↻ Update laden', { timeout: 30_000 });
  } finally {
    writeFileSync(sw, built);
  }
});

test('a new build stored in the background while the page is open turns the button into "Update bereit"', async ({ page }) => {
  test.setTimeout(240_000);
  const sw = new URL('../dist/sw.js', import.meta.url);
  const built = readFileSync(sw, 'utf8');
  const old = liveCache(built);
  try {
    await firstVisit(page);
    await page.reload();                                                          // now a page of the stored build
    await expect(page.locator('.fl-update')).toHaveText('↻ Update laden', { timeout: 60_000 });
    writeFileSync(sw, built.replace(`"${old}"`, '"frechenlehen-next000build"'));
    await page.evaluate(async () => (await navigator.serviceWorker.getRegistration()).update());   // the browser's own check
    await expect(page.locator('.fl-update')).toHaveText('↻ Update bereit – neu laden', { timeout: 120_000 });
    await page.evaluate(() => { window.__before = true; });
    const reloaded = page.waitForEvent('load', { timeout: 60_000 });
    await page.locator('.fl-update').click();
    await reloaded;
    expect(await page.evaluate(() => window.__before)).toBeUndefined();
    await expect(page.locator('.fl-update')).toHaveText('↻ Update laden', { timeout: 30_000 });
  } finally {
    writeFileSync(sw, built);
  }
});

test('a file that can\'t be stored stops with a message', async ({ page }) => {
  test.setTimeout(120_000);
  const sw = new URL('../dist/sw.js', import.meta.url);
  const built = readFileSync(sw, 'utf8');
  try {
    writeFileSync(sw, built.replace(`"${liveCache(built)}":[`, '"frechenlehen-failing00000":["missing.bin",'));   // a 404 in the list
    await page.goto(BASE);
    await expect(page.locator('.fl-offline')).toHaveText('Offline nicht möglich', { timeout: 60_000 });
  } finally {
    writeFileSync(sw, built);
  }
});

test('a new deploy keeps a stored plan version: its cache is neither dropped nor fetched again (#59)', async ({ page }) => {
  test.setTimeout(180_000);
  const sw = new URL('../dist/sw.js', import.meta.url);
  const built = readFileSync(sw, 'utf8');
  const vcache = built.match(new RegExp(`"(frechenlehen-v-${VERSION_ID}-[0-9a-f]{12})":\\[`))[1];
  const others = [...built.matchAll(/"(frechenlehen-v-[0-9-]+-[0-9a-f]{12})":\[/g)].map((m) => m[1]).filter((n) => n !== vcache);
  const keys = () => page.evaluate(async () => (await caches.keys()).filter((k) => k.startsWith('frechenlehen-')).sort());
  try {
    await firstVisit(page);
    expect(await keys()).toEqual([liveCache(built), vcache, ...others].sort());   // every plan version stored
    await page.evaluate(async (n) => (await caches.open(n)).put('marker', new Response('kept')), vcache);   // survives only if kept
    writeFileSync(sw, built.replace(`"${liveCache(built)}"`, '"frechenlehen-next000build"'));        // a new deploy, same version
    await page.evaluate(async () => (await navigator.serviceWorker.getRegistration()).update());
    await expect.poll(keys, { timeout: 90_000 }).toEqual(['frechenlehen-next000build', vcache, ...others].sort());
    expect(await page.evaluate(async (n) => (await (await caches.open(n)).match('marker'))?.text(), vcache)).toBe('kept');
  } finally {
    writeFileSync(sw, built);
  }
});
