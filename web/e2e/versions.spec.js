// Plan versions (issue #59, ADR-005-JXWL): the drop-down Version in the title box of the house page;
// ?v=<id> shows a frozen version's house and plan sheets. The viewer must open every listed version
// (versionen.json, written by code/versionen.py build) — the compatibility check of ADR-005-JXWL.
import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { choose, entries } from './menu.js';

const LIST = JSON.parse(readFileSync(new URL('../public/versionen.json', import.meta.url)));
const label = (v) => `${v.id} ${v.name}`;

async function open(page, url) {
  const errors = [], fetched = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('response', (r) => fetched.push(new URL(r.url()).pathname));
  await page.goto(url);
  await page.waitForFunction(() => window.__fl?.ready === true, null, { timeout: 60_000 });
  return { errors, fetched };
}

test('at least one version is listed', () => {
  expect(LIST.length).toBeGreaterThan(0);
  expect(LIST.map((v) => v.id)).toContain('2026-11-25');
});

for (const v of LIST) {
  test(`version ${v.id} opens: its house and its plan sheet`, async ({ page }) => {
    const { errors, fetched } = await open(page, `/?m=haus&v=${v.id}`);
    expect(errors).toEqual([]);
    expect(fetched).toContain(`/v/${v.id}/frechenlehen.glb`);
    expect(fetched).not.toContain('/frechenlehen.glb');
    await expect(page.getByRole('button', { name: 'Version', exact: true })).toHaveText(label(v));
    await expect(page.locator('.fl-title')).toHaveClass(/fl-frozen/);
    await choose(page, 'Darstellung', 'Grundriss EG');
    const img = page.locator('.fl-plan img');
    await expect(img).toBeVisible();
    expect(await img.getAttribute('src')).toBe(`/v/${v.id}/plans/eg.svg`);
    expect(await img.evaluate((i) => i.complete && i.naturalWidth > 0)).toBe(true);
    await expect(page).toHaveURL(new RegExp(`[?&]v=${v.id}\\b`));       // the written URL keeps v
    expect(errors).toEqual([]);
  });
}

test('the drop-down lists Aktuell and the versions; choosing one keeps the view', async ({ page }) => {
  await open(page, '/?cam=30,-20,12&at=8,6,2&p=3&cut=all');
  const menu = page.getByRole('button', { name: 'Version', exact: true });
  await expect(menu).toHaveText('Aktuell');
  await expect(page.locator('.fl-title')).not.toHaveClass(/fl-frozen/);
  await menu.click();
  expect(await entries(page)).toEqual(['Aktuell', ...LIST.map(label)]);
  await page.screenshot({ path: '../tmp/web/versions-menu.png' });
  await page.keyboard.press('Escape');
  await choose(page, 'Version', label(LIST[0]));
  await page.waitForURL(new RegExp(`[?&]v=${LIST[0].id}\\b`));
  await page.waitForFunction(() => window.__fl?.ready === true, null, { timeout: 60_000 });
  expect(new URL(page.url()).searchParams.get('cam')).toBe('30,-20,12');
  await expect(page.getByRole('button', { name: 'Version', exact: true })).toHaveText(label(LIST[0]));
  await choose(page, 'Version', 'Aktuell');
  await page.waitForURL((u) => !u.searchParams.has('v'));
  await page.waitForFunction(() => window.__fl?.ready === true, null, { timeout: 60_000 });
  expect(new URL(page.url()).searchParams.get('cam')).toBe('30,-20,12');
});

test('a sub-model page has no Version drop-down', async ({ page }) => {
  await page.goto('/ofen.html');
  await page.waitForFunction(() => window.__ofen?.ready === true, null, { timeout: 60_000 });
  await expect(page.getByRole('button', { name: 'Version', exact: true })).toHaveCount(0);
});
