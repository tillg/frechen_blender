// @vitest-environment happy-dom
import { test, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { uniform } from 'three/tsl';
import { makeMaterials, setReflections, updateStage, srgbToLinear } from './materials.js';
import { weights } from './stages.js';

const buf = readFileSync('public/frechenlehen.glb');
const json = JSON.parse(buf.subarray(20, 20 + buf.readUInt32LE(12)).toString());
const u = { uPaper: uniform(0), uDetail: uniform(1) };
const mats = makeMaterials(json.materials.map((m) => ({ name: m.name, extras: m.extras })), u);

test('every material in the GLB gets a node material of its kind', () => {
  expect(Object.keys(mats).sort()).toEqual(json.materials.map((m) => m.name).sort());
  for (const m of Object.values(mats)) {
    expect(m.isNodeMaterial).toBe(true);
    expect(['plain', 'wood', 'speck']).toContain(m.userData.kind);
  }
});

test('FL_Glas is transparent and stops writing depth from Detailmodell on', () => {
  const g = mats.FL_Glas;
  expect(g.transparent).toBe(true);
  updateStage(mats, weights(0));
  expect(g.depthWrite).toBe(true);           // Skizze/Massenmodell: windows hide the interior
  updateStage(mats, weights(2));
  expect(g.depthWrite).toBe(false);
});

test('FL_Feuer is emissive', () => {
  expect(mats.FL_Feuer.userData.emit).toBe(2.0);              // flames (code/fire.py): pure emission now
  expect(mats.FL_Feuer.emissiveNode).toBeTruthy();
});

test('FL_Laden uses the RAL 5014 paint colour', () => {
  const want = [99, 125, 150].map(srgbToLinear);
  mats.FL_Laden.userData.base.slice(0, 3).forEach((v, i) => expect(v).toBeCloseTo(want[i], 6));
});

test('wood and speck materials vary by _rnd, plain ones do not', () => {
  expect(mats.FL_Laerche.userData.usesRnd).toBe(true);
  expect(mats.FL_Granit.userData.usesRnd).toBe(true);
  expect(mats.FL_Putz.userData.usesRnd).toBe(false);
});

test('the lamp filament glows only at dusk (night), the fire always', () => {
  expect(mats.FL_Gluehfaden.userData.night).toBe(true);
  expect(mats.FL_Feuer.userData.night).toBeFalsy();
});

test('the switched-on lamp filament glows by day too', () => {
  expect(mats.FL_GluehfadenAn.userData.night).toBeFalsy();
  expect(mats.FL_GluehfadenAn.userData.emit).toBeGreaterThan(0);
});

test('fully metallic materials (metal >= 0.5) get the environment to reflect, the rest not', () => {
  const env = { isTexture: true };
  const ms = makeMaterials(json.materials.map((m) => ({ name: m.name, extras: m.extras })), u);
  const metallic = setReflections(ms, env);
  expect(metallic).toContain('FL_Metall');                                  // cup pulls, rings, fittings: black before
  for (const [name, m] of Object.entries(ms)) {
    const metal = json.materials.find((j) => j.name === name).extras.metal ?? 0;
    expect(m.envMap ?? null).toBe(metal >= 0.5 ? env : null);
  }
});
