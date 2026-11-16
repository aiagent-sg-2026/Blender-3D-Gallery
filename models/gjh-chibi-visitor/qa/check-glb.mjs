// Loads the exported GLB in a real browser with three.js, plays every clip and
// checks skinned bounds, morph targets and sockets; saves screenshots.
//
//   node models/gjh-chibi-visitor/qa/check-glb.mjs
//
// Writes models/gjh-chibi-visitor/qa/run-001/browser.json and browser-*.png.
import { createHash } from "node:crypto";
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { chromium } from "playwright";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../../..");
const out = path.join(root, "models/gjh-chibi-visitor/qa/run-001");
const types = { ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".glb": "model/gltf-binary" };

const page = `<!doctype html><html><head><meta charset="utf-8">
<style>html,body{margin:0;background:#ecedf8}canvas{display:block}</style>
<script type="importmap">{"imports":{"three":"/node_modules/three/build/three.module.js",
"three/addons/":"/node_modules/three/examples/jsm/"}}</script></head><body>
<script type="module">
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setSize(480, 640);
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xecedf8);
scene.add(new THREE.HemisphereLight(0xffffff, 0x8890a0, 2.2));
const sun = new THREE.DirectionalLight(0xffffff, 2.0); sun.position.set(-1.5, 3, 3); scene.add(sun);
const camera = new THREE.PerspectiveCamera(30, 480 / 640, 0.05, 50);
camera.position.set(1.1, 1.05, 3.2); camera.lookAt(0, 0.64, 0);
window.check = async () => {
  const gltf = await new GLTFLoader().loadAsync("/models/gjh-chibi-visitor/exports/gjh-chibi-visitor.glb");
  const model = gltf.scene; scene.add(model);
  const skinned = []; model.traverse(o => { if (o.isSkinnedMesh) skinned.push(o); });
  const meshes = []; model.traverse(o => { if (o.isMesh) meshes.push(o); });
  const face = meshes.find(m => m.morphTargetDictionary);
  const bounds = () => {
    const box = new THREE.Box3();
    for (const m of skinned) { m.computeBoundingBox(); box.union(m.boundingBox.clone().applyMatrix4(m.matrixWorld)); }
    return box;
  };
  model.updateMatrixWorld(true);
  const rest = bounds();
  const mixer = new THREE.AnimationMixer(model);
  const clips = {};
  for (const clip of gltf.animations) {
    mixer.stopAllAction();
    const action = mixer.clipAction(clip); action.reset().play();
    let minY = Infinity, maxY = -Infinity, finite = true, faceMax = 0;
    for (let i = 0; i <= 20; i++) {
      mixer.setTime(clip.duration * i / 20);
      model.updateMatrixWorld(true);
      const b = bounds();
      if (![b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z].every(Number.isFinite)) finite = false;
      minY = Math.min(minY, b.min.y); maxY = Math.max(maxY, b.max.y);
      if (face) faceMax = Math.max(faceMax, ...face.morphTargetInfluences);
    }
    clips[clip.name] = { duration: +clip.duration.toFixed(3), tracks: clip.tracks.length, minY: +minY.toFixed(4),
                         maxY: +maxY.toFixed(4), finite, faceMax: +faceMax.toFixed(3) };
    action.stop();
  }
  const sockets = ["SOCKET_Back", "SOCKET_Wrist_L", "SOCKET_Hand_R"].filter(n => model.getObjectByName(n));
  return {
    meshes: meshes.length, skinned: skinned.length, allSkinned: meshes.every(m => m.isSkinnedMesh),
    morphs: face ? Object.keys(face.morphTargetDictionary) : [],
    rest: { min: rest.min.toArray().map(v => +v.toFixed(4)), max: rest.max.toArray().map(v => +v.toFixed(4)) },
    clips, sockets,
    textures: meshes.filter(m => m.material.map).map(m => m.material.name),
  };
};
window.shot = async (clipName, fraction) => {
  const gltf = await new GLTFLoader().loadAsync("/models/gjh-chibi-visitor/exports/gjh-chibi-visitor.glb");
  scene.children.filter(c => c.isGroup).forEach(c => scene.remove(c));
  scene.add(gltf.scene);
  if (clipName) {
    const clip = gltf.animations.find(c => c.name === clipName);
    const mixer = new THREE.AnimationMixer(gltf.scene);
    mixer.clipAction(clip).play();
    mixer.setTime(clip.duration * fraction);
  }
  gltf.scene.updateMatrixWorld(true);
  renderer.render(scene, camera);
  return true;
};
window.ready = true;
</script></body></html>`;

const server = http.createServer((req, res) => {
  const url = decodeURIComponent(req.url.split("?")[0]);
  if (url === "/check.html") { res.writeHead(200, { "content-type": "text/html" }); res.end(page); return; }
  const file = path.join(root, url);
  if (!file.startsWith(root) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { "content-type": types[path.extname(file)] ?? "application/octet-stream" });
  fs.createReadStream(file).pipe(res);
});
await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
const port = server.address().port;
const browser = await chromium.launch({ args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
try {
  const tab = await browser.newPage({ viewport: { width: 480, height: 640 } });
  const errors = [];
  tab.on("pageerror", e => errors.push(String(e)));
  tab.on("console", m => { if (m.type() === "error") errors.push(m.text()); });
  await tab.goto(`http://127.0.0.1:${port}/check.html`);
  await tab.waitForFunction(() => window.ready === true);
  const result = await tab.evaluate(() => window.check());
  result.errors = errors;
  // Ties this evidence to the exact GLB it checked.
  result.glb_sha256 = createHash("sha256")
    .update(fs.readFileSync(path.join(root, "models/gjh-chibi-visitor/exports/gjh-chibi-visitor.glb"))).digest("hex");
  for (const [clip, f] of [[null, 0], ["Wave", 0.35], ["Walk", 0.25], ["Cheer", 0.3], ["Sit", 0.97]]) {
    await tab.evaluate(([c, t]) => window.shot(c, t), [clip, f]);
    await tab.locator("canvas").screenshot({ path: path.join(out, `browser-${clip ?? "rest"}.png`) });
  }
  fs.writeFileSync(path.join(out, "browser.json"), JSON.stringify(result, null, 2));
  console.log(JSON.stringify(result, null, 1));
} finally {
  await browser.close();
  server.close();
}
