// The toolbar's drop-downs (toolbar.js): open one by its caption, pick an entry by its label.
export async function choose(page, menu, option) {
  await page.getByRole('button', { name: menu, exact: true }).click();
  await page.getByRole('option', { name: option, exact: true }).click();
}

// the entries of an open drop-down list, separators as '—'
export const entries = (page) => page.evaluate(() => [...document.querySelectorAll('.fl-list:not([hidden]) li')]
  .filter((li) => !li.classList.contains('fl-group'))
  .map((li) => (li.classList.contains('fl-rule') ? '—' : li.textContent)));
