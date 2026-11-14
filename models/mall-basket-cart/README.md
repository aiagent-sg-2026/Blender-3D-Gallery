# Interactive Shopping Cart — MALL-008

Reference-inspired, independently editable wire cart built from the supplied image and written specification. The wire basket, frame, orange plastic trim, rubber wheels and sample package are original procedural geometry; no external mesh or texture is embedded. `MALL-008` is the identifier supplied for this request, not a claim about the separate 500-model backlog numbering.

## Files and measurements

- `sources/interactive-shopping-cart.blend`: editable Blender 5.1.2 source, with separately named casters, wheel pivots, basket wires and item.
- `exports/interactive-shopping-cart.glb`: self-contained glTF 2.0, 177,624 bytes, 5,564 triangles and 89 mesh primitives; SHA-256 `1171d17f6ea58d175bb2091e14b3913ec68ca3b78dfd5b6833d854f00036ce24`. It is below the requested 2 MB even without geometry compression.
- Closed bounds in glTF axes (width, height, length): approximately 0.600 × 1.004 × 1.044 m. Wheel bottoms are approximately 1 mm above the floor origin.
- Seven GLB animation clips: four wheel rolls, two front-wheel steering clips and one item-placement clip. The editable source and GLB are independently usable; character and obstacle are not embedded in this cart GLB.
- `previews/hero.webp` is the 18,466-byte gallery thumbnail. PNGs are Blender-rendered views of the actual model.

## Gallery interaction

The gallery's cart-only demonstration loads the existing Mall Shopper separately. Grab uses the shopper's rigid joints to position both hands at the handle. Push rolls all wheels and moves the cart; steering turns the front casters and changes its direction. Stop decelerates, Release lets go, and Add/Remove animates one sample package. A fixed box demonstrates collision stopping; Reset restores the scene. This is a bounded interactive example, not a general-purpose collision or character-physics system, and it does not implement arbitrary drag-and-drop or inventory.

## Reproduce and verify

From the repository root, with Blender 5.1.2, Node 24 and `cwebp` installed:

```sh
blender --background --threads 4 --python-exit-code 1 --python models/mall-basket-cart/generate.py
cwebp -quiet -q 80 models/mall-basket-cart/previews/hero.png -o models/mall-basket-cart/previews/hero.webp
node --test tests/interactive-shopping-cart.test.mjs
npm run build
node scripts/test-shopping-cart-browser.mjs
CART_BROWSER=webkit node scripts/test-shopping-cart-browser.mjs
```

The focused GLB test checks the 15,000-triangle and 2 MB budgets, dimensions, floor datum, glTF validation, named pivots, and actual wheel and steering motion in each clip. Desktop Chromium and Playwright WebKit ran the demo at 1440, 768 and 390 px; all states and collision were exercised, with collision explicitly checked at 1440 px. Chromium screenshots were inspected. WebKit reported the same four existing native-select CSP warnings on both the old shopping-cart viewer and this demo. Physical Android Chrome, iOS Safari and performance on mobile hardware have not been tested. Build and browser checks do not establish publication.

Artwork redistribution terms remain unspecified. The gallery download control is disabled; interactive viewing still serves the GLB. The image was supplied as a visual reference; no image pixels are embedded in the asset.
