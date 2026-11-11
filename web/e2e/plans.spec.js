// The architect's plan sheets (plans/*.svg) in the viewer: Darstellung › Pläne on Ganzes Haus.
import { test, expect } from '@playwright/test';
import { choose, entries } from './menu.js';

const SHEETS = ['Grundriss EG', 'Grundriss OG', 'Ansicht Nord', 'Ansicht Ost', 'Ansicht Süd', 'Ansicht West'];

async function open(page, url = '/') {
  await page.goto(url);
  await page.waitForFunction(() => window.__fl?.ready === true);
}

const sheet = (page) => page.locator('.fl-plan img');

test('Darstellung on Ganzes Haus lists the six plan sheets after the stages, not on Erdgeschoss', async ({ page }) => {
  await open(page, '/?m=haus');
  await page.getByRole('button', { name: 'Darstellung', exact: true }).click();
  expect((await entries(page)).slice(5)).toEqual(SHEETS);
  await expect(page.locator('.fl-list:not([hidden]) .fl-group', { hasText: 'Pläne' })).toHaveCount(1);
  await page.keyboard.press('Escape');
  await choose(page, 'Modell', 'Erdgeschoss');
  await page.getByRole('button', { name: 'Darstellung', exact: true }).click();
  expect(await entries(page)).toEqual(['Skizze', 'Massenmodell', 'Detailmodell', 'Gebaut', 'Eingerichtet']);
});

test('a plan sheet replaces the 3D view; a stage brings the 3D view back', async ({ page }) => {
  await open(page, '/?m=haus');
  await choose(page, 'Darstellung', 'Grundriss EG');
  await expect(sheet(page)).toBeVisible();
  expect(await sheet(page).evaluate((i) => i.complete && i.naturalWidth > 0)).toBe(true);
  expect(await sheet(page).getAttribute('src')).toMatch(/plans\/eg\.svg$/);
  await expect(page.getByRole('button', { name: 'Darstellung', exact: true })).toHaveText('Grundriss EG');
  await expect(page.getByRole('button', { name: 'Standpunkt', exact: true })).toBeDisabled();
  const link = page.getByRole('link', { name: 'SVG herunterladen' });
  expect(await link.getAttribute('href')).toMatch(/plans\/eg\.svg$/);
  expect(await link.getAttribute('download')).toBe('Frechenlehen Grundriss EG.svg');
  await expect(page).toHaveURL(/[?&]plan=eg\b/);
  await page.screenshot({ path: '../tmp/web/plans-eg.png' });

  await choose(page, 'Darstellung', 'Gebaut');
  await expect(page.locator('.fl-plan')).toBeHidden();
  await expect(page.getByRole('button', { name: 'Standpunkt', exact: true })).toBeEnabled();
  expect(await page.evaluate(() => document.body.dataset.stage)).toBe('built');
  await expect(page).not.toHaveURL(/plan=/);
});

test('a URL with ?plan= opens that sheet; Reset returns to the 3D view', async ({ page }) => {
  await open(page, '/?plan=og');
  await expect(sheet(page)).toBeVisible();
  expect(await sheet(page).getAttribute('src')).toMatch(/plans\/og\.svg$/);
  await expect(page.getByRole('button', { name: 'Modell', exact: true })).toHaveText('Ganzes Haus');
  await page.getByRole('button', { name: '↺ Reset' }).click();
  await expect(page.locator('.fl-plan')).toBeHidden();
  await expect(page).not.toHaveURL(/plan=/);
});

test('the wheel zooms the sheet in at the pointer, dragging moves it', async ({ page }) => {
  await open(page, '/?plan=eg');
  await expect(sheet(page)).toBeVisible();
  const before = await sheet(page).boundingBox();
  await page.mouse.move(640, 360);
  await page.mouse.wheel(0, -600);
  await expect.poll(async () => (await sheet(page).boundingBox()).width).toBeGreaterThan(before.width * 1.5);
  const zoomed = await sheet(page).boundingBox();
  await page.mouse.down();
  await page.mouse.move(540, 300, { steps: 5 });
  await page.mouse.up();
  const moved = await sheet(page).boundingBox();
  expect(moved.x).toBeCloseTo(zoomed.x - 100, 0);
  expect(moved.y).toBeCloseTo(zoomed.y - 60, 0);
});
