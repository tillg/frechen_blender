// TSL materials from the MAT_DEF extras in the GLB, following make_materials() in build_house.py:
// wood/speck: noise in object space -> colour ramp 0.35..0.68 -> value (and hue) varied by _rnd;
// wood and bump: noise height -> bump. One material per FL_* covers all stages:
// colour = mix(clay, detail, uDetail), Skizze paper via emissive (uPaper). image: a picture
// (path under public/) mapped in object space, local x / size[0] and model z / size[1] from the
// object's pivot (its lower-left corner), also its emission (a screen).
import * as THREE from 'three/webgpu';
import {
  attribute, bumpMap, clamp, color, float, hue, mix, mx_fractal_noise_float, normalView, positionLocal, texture, vec2, vec3,
} from 'three/tsl';

export const PAPER = 0xf3efe6;
export const CLAY = 0xeeebe4;

export const srgbToLinear = (v) => {
  const c = v / 255;
  return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
};

const AXIS = ['x', 'z', 'y'];          // three.js local axis i holds model axis AXIS[i] (x, z, -y)

// Blender Noise Texture (Scale 5, Roughness 0.6) as a 0..1 factor around 0.5
const noise = (scale, octaves) =>
  mx_fractal_noise_float(positionLocal.mul(scale).mul(5), octaves, 2, 0.6).mul(0.3).add(0.5);

const ramp = (fac, c1, c2) => mix(color(...c1), color(...c2), clamp(fac.sub(0.35).div(0.33), 0, 1));

function detail(d, base, image) {
  const rnd = attribute('_rnd', 'float');
  if (image) return { col: texture(image, vec2(positionLocal.x.div(d.size[0]), positionLocal.y.div(d.size[1]))).rgb, height: null, usesRnd: false };
  if (!d.wood && !d.speck) return { col: color(...base.slice(0, 3)), height: null, usesRnd: false };
  const [c1, c2, p] = d.wood || d.speck;
  const scale = d.wood ? vec3(...AXIS.map((a) => (a === p ? 1.5 : 60))) : vec3(p, p, p);
  const fac = noise(scale, 6);
  let col = ramp(fac, c1, c2).mul(rnd.mul(0.5).add(0.75));
  if (d.hue) col = hue(col, rnd.sub(0.5).mul(d.hue * 2 * Math.PI));
  return { col, height: d.wood ? [fac, 0.15] : null, usesRnd: true };
}

export function makeMaterials(defs, { uPaper, uDetail, uDusk = float(1), textureBase = '/', onTexture = () => {} }) {   // uDusk: lamps marked night
  const out = {};
  for (const { name, extras: d } of defs) {
    let image = null;                              // loads in the background; onTexture once it is there
    if (d.image) {
      image = new THREE.TextureLoader().load(textureBase + d.image, onTexture);
      image.colorSpace = THREE.SRGBColorSpace;
      image.anisotropy = 8;
    }
    const base = d.paint ? [...d.paint.map(srgbToLinear), (d.rgba || [0, 0, 0, 1])[3]]
      : d.rgba || [...d[d.wood ? 'wood' : 'speck'].slice(0, 2).reduce((a, b) => a.map((x, i) => (x + b[i]) / 2)), 1];
    const m = new THREE.MeshStandardNodeMaterial();
    const { col, height, usesRnd } = detail(d, base, image);
    m.colorNode = mix(color(CLAY), col, uDetail).mul(uPaper.oneMinus());
    let emissive = color(PAPER).mul(uPaper);
    if (d.emit) emissive = emissive.add((image ? col : color(...base.slice(0, 3))).mul(d.emit).mul(uDetail).mul(d.night ? uDusk : 1));
    m.emissiveNode = emissive;
    m.roughnessNode = mix(float(0.9), float(d.rough ?? 0.8), uDetail);
    m.metalnessNode = float(d.metal ?? 0).mul(uDetail);
    const bump = d.bump ? [noise(vec3(d.bump[0], d.bump[0], d.bump[0]).div(5), 8), d.bump[1]] : height;
    if (bump) m.normalNode = mix(normalView, bumpMap(bump[0], bump[1] * 0.05), uDetail).normalize();
    if (d.alpha !== undefined) {
      m.transparent = true;
      m.opacityNode = mix(float(1), float(d.alpha), uDetail);
    }
    m.polygonOffset = true;                         // the ink lines win the depth test
    m.polygonOffsetFactor = m.polygonOffsetUnits = 1;
    m.name = name;
    m.userData = { kind: d.kind, base, emit: d.emit, night: d.night, alpha: d.alpha, usesRnd, image: d.image };
    out[name] = m;
  }
  return out;
}

// glass writes depth until the detail stage, so the Skizze keeps hiding the interior
export function updateStage(mats, w) {
  const see = w.detail + w.built >= 0.5;
  for (const m of Object.values(mats)) {
    if (m.userData.alpha === undefined || m.depthWrite === !see) continue;
    m.depthWrite = !see;
    m.needsUpdate = true;
  }
}
