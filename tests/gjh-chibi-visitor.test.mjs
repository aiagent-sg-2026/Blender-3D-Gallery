// Contract tests for the GJH Chibi Visitor (models/gjh-chibi-visitor).
// Rebuild with: Blender --background --factory-startup --python-exit-code 1 \
//   --python models/gjh-chibi-visitor/src/build.py -- --out models/gjh-chibi-visitor --keep-going
import test from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import fs from "node:fs";
import validator from "gltf-validator";
import { loadCatalog } from "../scripts/catalog.mjs";

const dir = "models/gjh-chibi-visitor";
const glbPath = `${dir}/exports/gjh-chibi-visitor.glb`;
const bytes = fs.readFileSync(glbPath);
const gltf = JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)).toString("utf8"));
const report = JSON.parse(fs.readFileSync(`${dir}/qa/run-001/report.json`, "utf8"));

const CLIPS = ["Idle", "Walk", "Run", "Sit", "Wave", "Talk", "ShopBrowse", "PickUp", "Inspect", "Point", "Nod", "Cheer"];
const MORPHS = ["blink", "happy", "wink_L", "surprised", "thinking", "excited", "talk"];
const SOCKETS = ["SOCKET_Back", "SOCKET_Wrist_L", "SOCKET_Hand_R"];
const DEFORM = ["root", "hips", "spine", "chest", "neck", "head",
  ...["L", "R"].flatMap(s => [`shoulder.${s}`, `upper_arm.${s}`, `forearm.${s}`, `hand.${s}`,
    `thigh.${s}`, `shin.${s}`, `foot.${s}`])];

test("chibi visitor is registered once and loads through the catalog rules", () => {
  const assets = loadCatalog().collections.flatMap(c => c.assets).filter(a => a.id === "gjh-chibi-visitor");
  assert.equal(assets.length, 1);
  const [asset] = assets;
  assert.equal(asset.file, glbPath);
  assert.equal(asset.root, undefined, "skinned meshes are scene roots, so no single root is declared");
  assert.equal(asset.details.id, "gjh-chibi-visitor");
  assert.ok(asset.triangles >= 3000 && asset.triangles <= 8000, `triangles ${asset.triangles}`);
  assert.equal(asset.animations, CLIPS.length);
  assert.ok(fs.statSync(asset.thumbnail).size > 10_000);
});

test("GLB passes the glTF validator with no errors or warnings", async () => {
  const result = await validator.validateBytes(new Uint8Array(bytes), { uri: glbPath, maxIssues: 50 });
  assert.equal(result.issues.numErrors, 0);
  assert.equal(result.issues.numWarnings, 0);
});

test("every mesh is skinned to one 23-joint skin with the 20 deform bones and 3 sockets", () => {
  assert.equal(gltf.skins.length, 1);
  const joints = gltf.skins[0].joints.map(i => gltf.nodes[i].name);
  assert.deepEqual([...joints].sort(), [...DEFORM, ...SOCKETS].sort());
  const meshNodes = gltf.nodes.filter(n => n.mesh !== undefined);
  assert.equal(meshNodes.length, 8);
  assert.ok(meshNodes.every(n => n.skin === 0));
  const roots = gltf.scenes[gltf.scene ?? 0].nodes.map(i => gltf.nodes[i].name);
  for (const node of meshNodes) assert.ok(roots.includes(node.name), `${node.name} must be a scene root`);
  assert.ok(roots.includes("GJHChibiVisitorRig"));
});

test("face carries the seven expression morph targets", () => {
  const face = gltf.meshes.find(m => m.name === "Face");
  assert.deepEqual(face.extras.targetNames, MORPHS);
  assert.equal(face.primitives[0].targets.length, MORPHS.length);
});

test("twelve named clips; expression clips also animate the face weights", () => {
  assert.deepEqual(gltf.animations.map(a => a.name), CLIPS);
  const faceNode = gltf.nodes.findIndex(n => n.name === "Face");
  for (const clip of gltf.animations) {
    const paths = clip.channels.map(c => c.target.path);
    assert.ok(paths.includes("rotation"), `${clip.name} rotates bones`);
    assert.ok(clip.channels.some(c => c.target.node === faceNode && c.target.path === "weights"),
      `${clip.name} keys the face weights so switching clips resets expressions`);
  }
});

test("rest pose stands on the floor at chibi height; textures are embedded", () => {
  let minY = Infinity, maxY = -Infinity;
  for (const mesh of gltf.meshes) for (const prim of mesh.primitives) {
    const acc = gltf.accessors[prim.attributes.POSITION];
    minY = Math.min(minY, acc.min[1]);
    maxY = Math.max(maxY, acc.max[1]);
  }
  assert.ok(Math.abs(minY) <= 0.002, `feet at ${minY}`);
  assert.ok(Math.abs(maxY - 1.30) <= 0.025, `height ${maxY}`);
  assert.equal(gltf.images.length, 3);
  assert.ok(gltf.images.every(img => img.bufferView !== undefined && img.uri === undefined));
});

test("QA report matches the shipped GLB and records every gate", () => {
  const hash = createHash("sha256").update(bytes).digest("hex");
  assert.equal(report.glb.sha256, hash, "rebuild the model so the report describes this GLB");
  assert.deepEqual(report.gates.map(g => g.stage), [0, 1, 2, 3, 4, 5, 6, 7, 8]);
  for (const name of ["reference", "proportions", "body-and-clothes", "face", "props", "animation", "export"])
    assert.equal(report.gates.find(g => g.name === name).pass, true, `${name} gate`);
});

test("browser check loaded the GLB in three.js and played every clip above the floor", () => {
  const browser = JSON.parse(fs.readFileSync(`${dir}/qa/run-001/browser.json`, "utf8"));
  assert.equal(browser.glb_sha256, createHash("sha256").update(bytes).digest("hex"),
    "re-run qa/check-glb.mjs after rebuilding");
  assert.deepEqual(browser.errors, []);
  assert.equal(browser.allSkinned, true);
  assert.deepEqual(browser.morphs, MORPHS);
  assert.deepEqual(browser.sockets, SOCKETS);
  assert.deepEqual(Object.keys(browser.clips), CLIPS);
  for (const [name, clip] of Object.entries(browser.clips)) {
    assert.equal(clip.finite, true, name);
    assert.ok(clip.minY >= -0.005, `${name} dips to ${clip.minY}`);
  }
});
