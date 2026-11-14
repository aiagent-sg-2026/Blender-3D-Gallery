import { WebGLRenderer, PMREMGenerator } from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

// WebKit counts even explicitly lost contexts until GC. One lazily acquired
// context bounds repeated model browsing independently of GC timing.
let shared;
let studioTarget;
let owner;
let lifecycleInstalled = false;
function destroy() {
  if (!shared) return;
  const renderer = shared;
  shared = undefined;
  owner = undefined;
  studioTarget?.dispose();
  studioTarget = undefined;
  renderer.dispose();
  if (!renderer.getContext().isContextLost()) renderer.forceContextLoss();
  renderer.domElement.remove();
}
export function acquireModelViewerRenderer() {
  if (owner) throw new Error('The model viewer renderer is already in use.');
  if (shared?.getContext().isContextLost()) destroy();
  shared ??= new WebGLRenderer({ antialias: true });
  if (!lifecycleInstalled) {
    addEventListener('pagehide', event => { if (!event.persisted) destroy(); });
    lifecycleInstalled = true;
  }
  const renderer = shared;
  const token = Symbol('model-viewer');
  owner = token;
  return {
    renderer,
    getStudioEnvironment() {
      if (owner !== token) throw new Error('The model viewer lease is no longer active.');
      if (!studioTarget) {
        const room = new RoomEnvironment();
        const pmrem = new PMREMGenerator(renderer);
        try { studioTarget = pmrem.fromScene(room, 0.04); }
        finally { room.dispose(); pmrem.dispose(); }
      }
      return studioTarget.texture;
    },
    release() {
      if (owner !== token) return;
      owner = undefined;
      renderer.domElement.remove();
      if (renderer.getContext().isContextLost()) { destroy(); return; }
      // Per-model geometry/material/texture disposal belongs to the viewer.
      // Drop renderer-side references and retain only a tiny idle framebuffer.
      renderer.renderLists.dispose();
      renderer.resetState();
      renderer.setRenderTarget(null);
      renderer.setSize(1, 1, false);
      renderer.clear();
    },
  };
}
