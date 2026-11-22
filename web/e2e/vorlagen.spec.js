// The Vorlagen (issue #31): the photo pages (vorlagen.html, code/vorlagen.py) and the markers in the
// house viewer that open them.
import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { choose } from './menu.js';

const MANIFEST = JSON.parse(readFileSync(new URL('../public/vorlagen.json', import.meta.url)));

// every picture on the page has loaded (no broken image)
const loaded = (page) => page.evaluate(async () => {
  const imgs = [...document.querySelectorAll('img')];
  for (const i of imgs) { i.loading = 'eager'; if (!i.complete) await new Promise((r) => { i.onload = i.onerror = r; }); }
  return imgs.map((i) => i.naturalWidth > 0);
});

function watch(page) {
  const errors = [];
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('response', (r) => r.status() >= 400 && errors.push(`${r.status()} ${r.url()}`));
  return errors;
}

test('the index lists every Bereich with its cover picture', async ({ page }) => {
  const errors = watch(page);
  await page.goto('/vorlagen.html');
  await page.waitForFunction(() => window.__vorlagen?.ready === true);
  await expect(page.locator('.grid figure')).toHaveCount(MANIFEST.bereiche.length);
  for (const b of MANIFEST.bereiche) await expect(page.locator('.grid figure strong', { hasText: b.title })).toBeVisible();
  expect((await loaded(page)).every(Boolean)).toBe(true);
  await page.locator('.grid figure', { hasText: 'Ganzes Haus' }).click();
  await expect(page).toHaveURL(/vorlagen\.html\?b=haus$/);
  await expect(page.locator('figcaption', { hasText: 'Wandlampe' })).toBeVisible();
  expect(errors).toEqual([]);
});

test('the Garderobe page shows Garderobe and Toilette Mallnitz, every picture loads', async ({ page }) => {
  const errors = watch(page);
  await page.goto('/vorlagen.html?b=garderobe');
  await expect(page.locator('h1')).toHaveText('Garderobe & Gäste-WC');
  const g = MANIFEST.bereiche.find((b) => b.key === 'garderobe');
  await expect(page.locator('.grid figure')).toHaveCount(g.fotos.length);
  await expect(page.locator('figcaption', { hasText: 'Garderobe in Mallnitz' })).toBeVisible();
  await expect(page.locator('figcaption', { hasText: 'Toilette in Mallnitz' })).toBeVisible();
  expect((await loaded(page)).every(Boolean)).toBe(true);
  await expect(page.getByRole('link', { name: 'Ganzes Haus' })).toHaveAttribute('href', 'vorlagen.html?b=haus');
  await page.screenshot({ path: '../tmp/web/vorlagen_garderobe.png' });
  expect(errors).toEqual([]);
});

// at eye height in the Stube, looking at its marker (anchor from the manifest via the viewer's extras)
async function house(page, q) {
  await page.goto(`/?${q}`);
  await page.waitForFunction(() => window.__fl?.ready === true);
  await page.waitForTimeout(300);
}

test('the Stube marker shows in the Stube and opens the Stube page with the Ofen', async ({ page, context }) => {
  await house(page, 'cam=13.2,2.4,1.6&at=11.6,3.4,1.6&p=4&cut=all');
  const m = page.locator('a.fl-vorlage[data-key="stube"]');
  await expect(m).toBeVisible();
  await expect(page.locator('a.fl-vorlage[data-key="bad"]')).toBeHidden();          // far, behind walls
  await page.screenshot({ path: '../tmp/web/vorlagen_stube_marker.png' });
  const [popup] = await Promise.all([context.waitForEvent('page'), m.click()]);
  await expect(popup).toHaveURL(/vorlagen\.html\?b=stube$/);
  await expect(popup.locator('figcaption', { hasText: 'Kachelofen' })).toBeVisible();
});

test('as a home-screen app (standalone) the marker opens the page in the same window (#56: stays offline)', async ({ page }) => {
  await page.addInitScript(() => Object.defineProperty(navigator, 'standalone', { get: () => true }));
  await house(page, 'cam=13.2,2.4,1.6&at=11.6,3.4,1.6&p=4&cut=all');
  const m = page.locator('a.fl-vorlage[data-key="stube"]');
  await expect(m).toBeVisible();
  expect(await m.getAttribute('target')).toBeNull();
  await m.click();
  await expect(page).toHaveURL(/vorlagen\.html\?b=stube$/);
});

test('a marker hides behind a wall, in the Rundgang and on a plan sheet', async ({ page }) => {
  await house(page, 'cam=13.2,2.4,1.6&at=11.6,3.4,1.6&p=4&cut=all');
  await expect(page.locator('a.fl-vorlage[data-key="stube"]')).toBeVisible();
  // from the Windfang behind the Stube's north wall, looking at the Stube anchor: hidden by the wall
  await page.evaluate(() => window.__fl.lookFrom(13.5, 7.5, 1.6));
  await page.waitForTimeout(300);
  await expect(page.locator('a.fl-vorlage[data-key="stube"]')).toBeHidden();
  await page.evaluate(() => window.__fl.lookFrom(13.2, 2.4, 1.6));
  await expect(page.locator('a.fl-vorlage[data-key="stube"]')).toBeVisible();
  await choose(page, 'Darstellung', 'Grundriss EG');
  await expect(page.locator('a.fl-vorlage:visible')).toHaveCount(0);
  await choose(page, 'Darstellung', 'Eingerichtet');
  await choose(page, 'Standpunkt', 'Um und durch das Haus');
  await page.waitForTimeout(500);
  await expect(page.locator('a.fl-vorlage:visible')).toHaveCount(0);
});

test('the house page links the photo pages', async ({ page }) => {
  await house(page, '');
  await expect(page.getByRole('link', { name: 'Fotos & Vorlagen' })).toHaveAttribute('href', 'vorlagen.html');
});

test('the Garderobe marker shows in the Garderobe corner', async ({ page }) => {
  await house(page, 'cam=2.1,7.6,1.6&at=1.5,5.6,1.2&p=4&cut=all&fov=50');
  await expect(page.locator('a.fl-vorlage[data-key="garderobe"]')).toBeVisible();
});

test('from outside at the wall, with the storey open from above, a room marker stays behind the wall', async ({ page }) => {
  // north of the house, above the anchor's height but below the cut-open EG's wall tops: Flur walls between
  await house(page, 'cam=11.6,16,2.2&at=11.6,3.4,1.6&p=4&cut=eg');
  await expect(page.locator('a.fl-vorlage[data-key="stube"]')).toBeHidden();
});
