// Pure helpers of the Vorlagen (code/vorlagen.py, issue #31): the photo page's URL per Bereich and
// the Bereich a page shows.

// the page of a Bereich (no key: the index of all); relative, so it works under the Pages base too
export const pageUrl = (key) => (key ? `vorlagen.html?b=${encodeURIComponent(key)}` : 'vorlagen.html');

// the Bereich of ?b=<key>, or null (index)
export function pickBereich(manifest, search) {
  const b = new URLSearchParams(search).get('b');
  return manifest.bereiche.find((x) => x.key === b) ?? null;
}
