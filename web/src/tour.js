// Rundgang: plays the camera keys of code/tour.py (scene.extras.tour: fps, frames of
// [x, y, z, yaw, pitch, lens] in z-up model metres, lens in mm on a 36 mm sensor) – the same
// path as the Blender film. Time-based playback (0.75×, optionally endless) with pause (OrbitControls look around the paused
// pose), a scrubber and "Beenden", which restores the previous view. body.dataset.tour is
// off | playing | paused (for tests).
import * as THREE from 'three/webgpu';
import './tour.css';

const yup = ([x, y, z]) => new THREE.Vector3(x, z, -y);
export const LOOK = 0.05;                     // paused: orbit target this far ahead = look around in place
const SPEED = 0.75;                    // playback speed relative to the film

export const duration = (frames, fps) => (frames.length - 1) / fps;

// the tour draws at most 30 times a second (the film has 25): 4 ms slack for rAF jitter
export const drawDue = (now, lastDraw) => now - lastDraw >= 1000 / 30 - 4;

// next route time: dt clamped to 0…0.1 s (no jump after a background tab), stop at the end or
// wrap around (Endlos; the route ends where it starts)
export function step(t, dt, T, loop) {
  const s = t + Math.min(Math.max(dt, 0), 0.1);
  return loop ? s % T : Math.min(s, T);
}

// pose at time t (s), linear between the keys (yaw is unwrapped in the keys)
export function poseAt(frames, fps, t) {
  const f = Math.min(Math.max(t * fps, 0), frames.length - 1);
  const i = Math.min(Math.floor(f), frames.length - 2), a = f - i;
  const k = frames[i].map((v, j) => v + (frames[i + 1][j] - v) * a);
  return { pos: k.slice(0, 3), yaw: k[3], pitch: k[4], lens: k[5] };
}

// three.js vertical fov (deg) for a Blender lens: sensor fit AUTO puts 36 mm on the wider side
export function fovFor(lens, aspect) {
  const half = 18 / lens;
  return (2 * Math.atan(aspect >= 1 ? half / aspect : half) * 180) / Math.PI;
}

function el(tag, attrs = {}, text = '') {
  const e = Object.assign(document.createElement(tag), attrs);
  if (text) e.textContent = text;
  return e;
}

// opts: { camera, controls, routes [{name, fps, frames}], door (pivot object), onStart(i)
// (stage/cutaway for the tour), onEnd() (after Beenden) }. The toolbar's Routen entries call enter(i).
// update(now) drives the camera and returns true while playing (the caller then skips
// controls.update()).
export function createTour({ camera, controls, routes, door, onStart, onEnd }) {
  let fps = routes[0].fps, frames = routes[0].frames, T = duration(frames, fps), route = 0;
  let state = 'off', t = 0, last = 0, loop = false, saved = null, dir = new THREE.Vector3(1, 0, 0);

  const bar = el('div', { className: 'fl-bar fl-tour' });
  const play = el('button', { type: 'button', className: 'fl-play' });
  play.onclick = () => (state === 'playing' ? setState('paused') : resume());
  const scrub = el('input', { type: 'range', min: 0, max: T, step: 0.01, value: 0 });   // max: per route
  scrub.setAttribute('aria-label', 'Rundgang-Zeit');
  scrub.oninput = () => seek(Number(scrub.value));
  const endless = el('button', { type: 'button' }, 'Endlos');
  endless.setAttribute('aria-pressed', 'false');
  endless.onclick = () => { loop = !loop; endless.setAttribute('aria-pressed', String(loop)); };
  const exit = el('button', { type: 'button' }, 'Beenden');
  exit.onclick = () => leave();
  bar.append(play, scrub, endless, exit);
  document.body.append(bar);

  function apply() {
    const p = poseAt(frames, fps, t);
    dir.set(Math.cos(p.pitch) * Math.cos(p.yaw), Math.cos(p.pitch) * Math.sin(p.yaw), Math.sin(p.pitch));
    dir = yup(dir.toArray());
    camera.position.copy(yup(p.pos));
    camera.lookAt(camera.position.clone().add(dir));
    camera.fov = fovFor(p.lens, camera.aspect);
    camera.updateProjectionMatrix();
    scrub.value = t;
  }

  function setState(s) {
    state = s;
    document.body.dataset.tour = s;
    controls.enabled = s !== 'playing';
    if (s === 'paused') {                         // look around the paused pose
      controls.target.copy(camera.position).addScaledVector(dir, LOOK);
      controls.update();
    }
    play.textContent = s === 'playing' ? '❚❚' : '▶';
    play.setAttribute('aria-label', s === 'playing' ? 'Rundgang anhalten' : 'Rundgang abspielen');
  }

  function stopSpin() {                           // drop OrbitControls' damping momentum
    controls.enableDamping = false; controls.update(); controls.enableDamping = true;
  }

  function resume() {
    if (t >= T) t = 0;
    stopSpin();
    last = performance.now();
    setState('playing');
  }

  function seek(s) {
    t = Math.min(Math.max(s, 0), T);
    apply();
    setState('paused');
  }

  function enter(i = 0) {
    if (state !== 'off') leave();
    route = i;
    ({ fps, frames } = routes[i]);
    T = duration(frames, fps);
    scrub.max = T;
    saved = { pos: camera.position.clone(), target: controls.target.clone(), fov: camera.fov,
      maxPolar: controls.maxPolarAngle, zoom: controls.enableZoom, pan: controls.enablePan };
    stopSpin();
    Object.assign(controls, { maxPolarAngle: Math.PI, enableZoom: false, enablePan: false });
    onStart(i);
    door.rotation.y = Math.PI / 2;                  // as in film.py: 90° about model z
    t = 0;
    apply();
    resume();
  }

  function leave() {
    if (state === 'off') return;
    stopSpin();
    door.rotation.y = 0;
    Object.assign(controls, { maxPolarAngle: saved.maxPolar, enableZoom: saved.zoom, enablePan: saved.pan });
    camera.position.copy(saved.pos);
    camera.fov = saved.fov;
    camera.updateProjectionMatrix();
    controls.target.copy(saved.target);
    setState('off');
    controls.update();
    onEnd();
  }

  function update(now) {
    if (state !== 'playing') return false;
    t = step(t, ((now - last) / 1000) * SPEED, T, loop);
    last = now;
    if (t >= T) { apply(); setState('paused'); return false; }
    apply();
    return true;
  }

  function resize() {                             // fov depends on the aspect
    if (state === 'off') return;
    camera.fov = fovFor(poseAt(frames, fps, t).lens, camera.aspect);
    camera.updateProjectionMatrix();
  }

  setState('off');
  return { update, resize, enter, leave, seek, get state() { return state; }, get time() { return t; },
    get duration() { return T; }, get route() { return route; }, key: (i) => frames[i].slice(0, 3) };
}
