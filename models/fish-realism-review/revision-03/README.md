# Accepted Barramundi and Betta — revision 03

The owner retained these two versions on 2026-11-15. See [the release acceptance record](../acceptance.json). The stingray's accepted model is [revision 04](../revision-04/README.md).

- [Barramundi source and animated GLB](barramundi/): Microsoft / Khronos, CC0 1.0. Original textured geometry is retained; this project adds an 11-bone swim rig, distal-fin weighting and a three-second loop.
- [Betta source and animated GLB](betta/): BlueMesh, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), [original model](https://sketchfab.com/3d-models/betta-splendens-f4eeb7f50ad24873842bd954ad27d23b). The 53-bone `Take 01` clip is retained. Material response, framing and source placeholders are adjusted.

The original free GLBs, source credits and mirror revision are preserved under `../external-candidates/`. No purchase or protected viewer extraction was used. GIFs are actual Blender renders. Per-asset `verification.json` files record evaluated vertex motion and loop endpoint differences. The Betta has a small inherited endpoint discrepancy; it is not mathematically exact.

`create_review.py` imports the original assets and creates isolated review scenes. Run `finalize.py` once for each freshly generated scene to add the bass rig, adjust materials, export and render. Blender 5.1.2 is the reproduction environment. Scripts write only into this revision. Gallery assets and production deployment are not changed by these scripts.
