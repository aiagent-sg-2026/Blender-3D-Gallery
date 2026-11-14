# Virtual Mall Foundation v1 — frozen scope and delivery checklist

Version: 1.2 · 2026-11-15 · Asia/Singapore

Status: **scope frozen; FND-001 through FND-003 verified within the local baseline/whitebox/module-fit boundaries; FND-004 onward remain open**. The owner explicitly authorized FND-001/002 and then FND-003 after the freeze. See the [baseline and whitebox delivery record](verification/foundation-v1/README.md). This does not approve unknown artwork rights or authorize publication.

## 1. Goal and controlling sources

A visitor can enter a single-floor mall, understand where to go, reach a store, inspect a product, update a clearly marked Demo Bag, and return to exploration. The same product information remains available through an accessible directory.

The controlling product scope is the owner's `Virtual_Mall_Master_Plan.md` v1.0, supplied from Downloads, SHA-256 `18d06eae8be046fdb17e211e5a87787f03f6afc008539a39d80f97aa8e9104c5`. This document makes its Foundation v1 requirements executable. The broader master plan continues to own later stages.

Evidence used for this freeze:

- [P0 asset inventory](gallery-p0-asset-inventory-2026-11-14.md): 31 planned model families and 33 distinct candidate assets. These are inventory counts, not a requirement to build 31 new models.
- [P0 assembly fit study](verification/p0-assembly/README.md): existing GLBs assembled in Blender and a separate Web sample. Its reports were read for this scope definition; the experiments were not rerun in this task.
- GJH v11 runtime/source snapshot at Webpage-Design-Gallery commit [`643d8048a8642a8d056a776f4eb288d095da3b34`](https://github.com/yapweijun1996/Webpage-Design-Gallery/tree/643d8048a8642a8d056a776f4eb288d095da3b34/demos/corporate/gjh/v11), inspected during the preceding read-only inventory. The matching [Pages workflow](https://github.com/yapweijun1996/Webpage-Design-Gallery/actions/runs/43610400308) reported success. This is a dated snapshot, not a statement about future deployments.
- Live inventory observations: map navigation to New Moon, keyboard entry into the shop, one product dialog and 3D preview, Demo Bag add/increase/remove, and List View. Product-dialog layouts were observed at 320×568, 390×844 and 768×1024. These were desktop-browser viewport checks, not real-phone or full touch acceptance.
- [Existing task evidence matrix](https://github.com/yapweijun1996/Webpage-Design-Gallery/blob/643d8048a8642a8d056a776f4eb288d095da3b34/docs/v11-task-evidence-matrix.md): historical test receipts retain their original revision, device and scope limitations.

## 2. Frozen product scope

| Area | Foundation v1 requirement | Acceptance boundary |
| --- | --- | --- |
| Floor and circulation | One floor, one public arrival point, one atrium and one continuous main corridor with storefronts on both sides | A connected walking route reaches the required shops and returns to the entrance; exact dimensions are recorded in the whitebox deliverable |
| New Moon concept shop | One enterable shop with four existing SKU records: New Zealand 425g, Australia 425g, South Africa 425g and Mexico 454g | Each SKU opens the matching detail, official image and reviewed demo model; no inferred price, stock or packaging claim |
| Generic shop | One enterable, unbranded Sample Store using the same storefront/shelf components, with replaceable sign and one existing original demo product | A neutral scene configuration proves reuse without New Moon logos, SKU records or official-brand links leaking into it |
| Basic public facilities | A directory/map interaction, clear store signs, existing seating and planters, and an appropriate bin placement | Fixtures support navigation and keep walking/camera paths clear; sitting is not a new Foundation release dependency |
| Visitor | One controllable visitor using an existing compatible asset | Desktop keyboard and mobile touch movement, grounded placement, animation transitions and wall collision work in the actual mall |
| Product flow | Proximity cue, detail dialog, lazy 3D loading, rotation, zoom, reset and a readable image/error fallback | Complete and cancel the journey for every required SKU; restore position, camera and focus on return |
| Demo Bag | Add, change quantity, remove and clear; retain the existing per-tab/session behavior and existing quantity limit | Explicit Demo wording; no order, reservation, payment or stock change |
| Directory | All required stores and matching product information are available without navigating the 3D space | Keyboard access and a useful no-WebGL/no-JavaScript path; a failed product preview does not remove product information |
| Help and settings | Dismissible help, a reachable menu/settings entry and a meaningful quality choice | Controls actually affect the intended setting and restore exploration cleanly; approved audio, if present, has an effective mute control. A silent build identifies that state and does not add a nonfunctional sound switch |

The minimum acceptance scene is **New Moon plus one generic shop**. Existing MILI/GOGO content does not count as the unbranded shop. Reuse an existing room shell for the neutral configuration before adding another room. Keep existing public v11 entry URLs and brand content available; the candidate layout/configuration and any release migration must be recorded before a public switch.

The current v11 atrium and three-store arrangement is a reusable baseline, not evidence that the requested corridor layout and neutral shop already meet this scope. First compare its plan with the circulation requirement; modify only demonstrated layout gaps.

Style: retain the existing jade/deep green, ivory, champagne-brass and warm-light direction for this first scene. Geometry, lighting, theme, brand and product data must remain independently replaceable.

### Deferred work

- New sitting systems, full shopping-cart integration, coffee/activity gameplay, parking connections, lifts and additional floors belong to later interaction/scene work. Preserve working existing features during changes.
- Shelf close-up/highlighting, per-can picking, character v2, wardrobe customization, crowds and new product families are separate additions.
- The generic shop is a small configuration proof. It does not introduce a multi-tenant administration platform, authentication or content-management backend.
- Real pricing, inventory, checkout, payment, orders, delivery and commercial data integrations remain stage 6 work.
- Additional light-fixture, architectural and furniture variants are created only for a demonstrated scene requirement. The broader asset backlog is not this release's scope.

## 3. Ownership and evidence states

| Owner | Responsibility |
| --- | --- |
| Blender-3D-Gallery / asset engineer | Editable sources, modular interfaces, exports, previews, measured budgets, provenance and export validation |
| Webpage-Design-Gallery GJH runtime / runtime engineer | Layout, instances, colliders, lighting, visitor/controller, camera, interaction states, UI and content configuration |
| Content owner | SKU mapping and authorized brand/image/reference inputs; unresolved packaging facts remain disclosed |
| QA / release engineer | Repeatable browser evidence, regression, release candidate identity and remote verification; physical-device tests waived by the owner |
| Product owner | Scope changes, unresolved business content and acceptance-environment decisions |

Role ownership is assigned here; individual people are not assigned. Assets in the library do not acquire Mall interaction behavior automatically. In particular, the [new interactive cart](../models/mall-basket-cart/README.md) is a candidate for later Mall integration; the v11 [cart receipt](https://github.com/yapweijun1996/Webpage-Design-Gallery/blob/643d8048a8642a8d056a776f4eb288d095da3b34/demos/corporate/gjh/v11/assets/cart-source.json) still describes the earlier static cart with a simplified pushing pose.

Use these states in delivery records:

- **Observed:** a dated source/runtime observation; limited to the recorded scenario.
- **Candidate:** potentially reusable; still requires scene-specific review.
- **Verified:** a named check passed on an identified artifact and environment.
- **Open:** work or acceptance evidence remains.
- **Deferred:** explicitly outside Foundation v1.

No historical PASS is automatically a Verified result for a new candidate.

## 4. Asset disposition and interface work

| Package | Existing candidates / evidence | Frozen disposition | Scene acceptance |
| --- | --- | --- | --- |
| Floor and ceiling | `mall-floor-tile-module`, `mall-ceiling-panel-module`; 1.2 m study grid | Reuse; confirm complete scene boundaries and cut/opening treatment | Metre scale, recorded origin/elevations, visible seams reviewed in Blender and the Mall |
| Storefront and structure | `mall-shopfront-door`, `mall-glass-partition`, `mall-structural-column` | Reuse with interfaces resolved; do not scale components arbitrarily to hide gaps | Door motion/clearance, corner treatment, long partition runs, colliders and camera clearance checked |
| Storefront upper infill | Study: storefront top 2.4 m, ceiling underside 3.0 m | Adapt or author a separate upper infill/fascia module after final scene elevations are set | Close the observed 0.60 m sample gap; keep the sign area editable; verify neighboring seams |
| Column ceiling trim | Study: 0.60 m square column inside an omitted 1.20 m ceiling cell | Adapt or author a separate trim/infill module | Close the approximately 0.30 m sample gap on each side; retain an intentional seam and inspect actual geometry |
| Frame/partition junctions and floor edges | Study only proves selected bounding-box contacts | Inspect first; add adapters/end pieces only if required | Check real frame intersections, shared posts, open-door sweep and the final floor perimeter |
| Lights and signage | Existing procedural Mall lighting, `mall-ceiling-light-module`, `mall-advertising-lightbox`, direction signs | Reuse sufficient existing fixtures; add an independent editable shop-sign/fascia interface | Lights illuminate the actual scene; decorative emission is not counted as functional lighting or wayfinding |
| Public fixtures | `mall-directory-kiosk`, `gjh-lounge-bench`, `gjh-areca-planter`, `mall-trash-bin` or `mall-waste-sorting-station` | Reuse a restrained subset | No blocked route or hidden prompt; kiosk opens the real Mall map and is labeled accurately |
| New Moon display | Existing `mall-display-shelf` and four pinned local product GLBs in v11 | Retain existing reviewed SKU mapping and disclosed demo limitations | Correct image/name/model for every SKU, readable labels and clear approach space |
| Neutral display | Existing shelf/room components plus `demo-food-tin` or another reviewed original package | Configure Sample Store; keep provenance/font notices | No real-brand/SKU/eShop content leaks; original product remains clearly a demo |
| Visitor | Existing `gjh-mall-visitor` runtime integration | Reuse v1 before considering replacement | Correct floor contact, facing, controller/animation compatibility and resource lifecycle |

The assembly study's 24 expected bounding-box relationships include measured gaps; passing those assertions is not seam acceptance. It does not prove the 1.14 m repeated-partition interface, door sweep, full layout collisions, mobile performance or GJH integration. Component counts and final dimensions are determined from the approved whitebox, not from the sample's 27 assemblies.

A concurrent local working-tree candidate under `models/mall-fit-finishes/` now contains 1.20 m and 2.10 m shopfront fascia exports and a column-ceiling collar export, alongside a [generator](../models/mall-fit-finishes/generate.py) and source files. Inspect these candidates before authoring duplicate pieces in FND-003. Their presence alone does not close the integrated fit, provenance or release gates; this scope task did not generate or independently validate them.

## 5. Executable delivery backlog

**FND-001 through FND-003 are Verified within their local baseline/whitebox/module-fit boundaries; FND-004 onward remain Open for Foundation v1 acceptance.** Dependencies refer to the IDs in this table. Each evidence record identifies the code revision, asset hashes, URL/build, browser/environment, scenario and result. Whitebox verification does not close integrated release gates.

| ID | Work / owner role | Depends on | Required output and acceptance |
| --- | --- | --- | --- |
| FND-001 | Record candidate and baseline / runtime + QA | — | Reconcile current Mall HEAD/deployment, preserve original URLs/content, record exact baseline paths and select the candidate configuration/entry. Capture the existing journey and regressions; record the browser measurement method. Verified: pinned v11 `d636ce0f` / app 1.1.30 and local candidate; [evidence](verification/foundation-v1/README.md). Physical-device tests waived by owner |
| FND-002 | Approve one-floor whitebox / runtime + asset | FND-001 | Dimensioned plan with entrance, atrium, corridor, both shop approaches, camera space, colliders and asset placements. Walk entrance → both required shops → entrance in the target engine; record gaps rather than hiding them. Verified: [dimensioned plan, editable source and walkable GLB](verification/foundation-v1/README.md), with original v11 player/Rapier modules |
| FND-003 | Resolve module interfaces / asset | FND-002 | Reviewed source and GLB for required infill/trim/sign components; evidence for elevations, junctions, open-door clearance and source editability. Regenerate and validate changed exports; preserve unaffected asset identities. Verified locally: [fitted source, GLB, shared-post runs, infill/collar surfaces, door aperture/sweep and actual controller checks](verification/foundation-v1/module-fit/README.md). Installed full-open passage is 1.734 m; 2.10 m is the rough opening |
| FND-004 | Build neutral shop configuration / runtime + content | FND-002 | Sample Store reuses the selected room, storefront and display components; change its sign/content through bounded data, not copied brand-specific logic; test both New Moon and neutral configurations |
| FND-005 | Complete Foundation dressing / runtime | FND-003, FND-004 | Lighting, direction signs, map targets, seating/planters and bin placement support the approved routes. Review entrance and every store approach at desktop and narrow widths |
| FND-006 | Verify primary input states / runtime | FND-001 | Explicit Explore, Map, Inspect, Bag and Menu behavior; one active movement input owner. Overlay/list/hidden/blur transitions clear held keys/pointers and pause movement. Close restores a safe camera, location and focus; existing Seated/Cart cannot conflict |
| FND-007 | Verify product journey / runtime + content | FND-004, FND-006 | All four New Moon SKUs and the neutral sample have correct details and 3D/image mapping. Test rotation, zoom, reset, loading failure, cancellation, repeated opens and return to exploration |
| FND-008 | Verify Demo Bag / runtime + QA | FND-007 | Add/increment/decrement/remove/clear and session behavior preserve the selected SKU; existing quantity limit enforced. Inspect/Bag/List transitions retain contents and restore input. No commerce requests or invented business data |
| FND-009 | Finish help/settings and fallback / runtime | FND-006, FND-007 | Dismissible/reopenable help, useful quality control, accurate sound state, accessible labels, keyboard/focus behavior and reduced-motion handling. No-WebGL/no-JavaScript directory and failed asset paths remain useful |
| FND-010 | Integrated acceptance / QA | FND-005, FND-008, FND-009 | Run the matrix below on the same candidate; inspect real screenshots, check resource disposal and regressions, and resolve in-scope failures. Use the owner-approved browser-only environments and disclose their limits |
| FND-011 | Release candidate record / QA + product owner | FND-010 | Review scope/evidence, remaining limitations, rights and rollback. Publish only under an explicit release instruction, then verify the remote revision, workflow and live journey |

Independent asset and runtime work can proceed after their prerequisites are satisfied. The owner waived iPhone/Android hardware tests for Foundation v1; missing physical devices are not a blocker. Browser viewport/touch emulation does not establish physical-device compatibility.

## 6. Acceptance matrix

| Gate | Scenario and passing condition | Required environment |
| --- | --- | --- |
| AC-01 · Arrival and circulation | Fresh entry → understand/dismiss help → locate/enter each required shop → return. No stuck state, route blockage, unexpected teleport or unrecoverable camera view | Desktop keyboard/mouse; browser touch emulation |
| AC-02 · Map and input ownership | Open/close map while moving; choose destination; dismiss each overlay/list and return. Character stays still while controls are paused and does not move from a stale held input after return | Keyboard, multi-pointer/cancel/blur/hidden scenarios |
| AC-03 · Product and bag | Complete view/rotate/zoom/reset/add/change/remove/clear for every required product. Close/escape and failed previews leave correct product information and bag state | Desktop + narrow/touch layouts |
| AC-04 · Reuse and content | The neutral shop uses replaceable sign/display/product content; no New Moon/MILI/GOGO assets or links appear in the neutral configuration unintentionally | Config inspection + both rendered configurations |
| AC-05 · Responsive UI | No horizontal overflow, hidden required action or HUD overlap. Product content can scroll with Close reachable; named controls have at least 44×44 CSS-pixel targets; safe-area padding is respected | 320×568, 390×844, 768×1024, 1440×900; short landscape 667×375 or 844×390 |
| AC-06 · Touch and accessibility | Movement/camera roles do not steal taps; dialogs constrain focus and restore it; keyboard operates primary UI; labels and focus are visible; list/fallback carries equivalent product information | Browser touch emulation; keyboard and a recorded screen-reader pass (hardware tests waived) |
| AC-07 · Assets and spatial fit | Selected exports validate; units/origins/facing and asset hashes match receipts; actual seams, door sweeps, collision and floor contact pass in the integrated scene | Blender source/export inspection + target-engine walkthrough |
| AC-08 · Loading and performance | Record cold entry-to-usable, product-preview latency, frame-time distribution, memory where measurable, bytes and draw calls at entrance and worst selected store view. Keep the inherited 200-draw-call limit unless a measured exception is approved. Define any additional performance thresholds against a named browser/environment and fixed protocol before final sign-off | Named desktop browser/environment; fixed scene, quality, viewport and sample protocol (hardware tests waived) |
| AC-09 · Failure and lifecycle | Missing model, unavailable WebGL/WASM, repeated product open/close and hidden tab recover to a useful state; no growing active renderers/listeners/resources or new runtime errors. Known baseline warnings are individually identified | Automated fault checks + browser inspection |
| AC-10 · Provenance and release | Selected asset/content receipts and packaging limitations are present; candidate revision matches its evidence; authorized publication passes its workflow and the live key journey | Asset/content review + remote/live evidence |

No 60 FPS, broad device support or complete accessibility claim is made from a desktop viewport screenshot. Unsupported memory telemetry is reported as unavailable rather than zero. Physical-device names and measurements are not required after the owner waiver. Additional integrated performance measurements belong to FND-010; FND-001 records the environment and protocol without inventing device thresholds.

## 7. Decision register and change control

| Decision / gap | Frozen handling | Resolution point |
| --- | --- | --- |
| Required stores | New Moon + one neutral Sample Store; existing branded rooms alone do not satisfy neutral reuse | FND-004 |
| Product scope | Four existing New Moon SKUs; one original neutral sample. Keep Demo Bag and unofficial packaging disclosures | FND-007 / content owner |
| Scene dimensions | Layout v1.0 establishes a 9.6 × 7.2 m atrium, 4.8 × 21.6 m corridor, and two opposing 7.2 × 9.6 m shops on a 1.2 m grid. These are design-study dimensions, not inferred building measurements. See the whitebox contract | FND-002 verified; FND-003 local module fit verified |
| Module interfaces and door clearance | FND-003 uses 1.14 m shared-post partition pitch, new 3.48 m run fascia, existing 2.10 m door fascia and column collar. The 2.10 × 2.40 m rough opening contains a 1.94 × 2.32 m frame aperture and 1.734 m full-open passage; retain unscaled assets and walking-only acceptance. Original whitebox remains archived | FND-003 verified locally; full dressing/performance remains FND-005 / FND-010 |
| Audio | No new soundtrack is required. Any approved audio in use must be muteable and must follow browser playback policy; a silent scene remains silent | FND-009 |
| Physical devices and performance | Owner response: “no need test by iphone or android.” Physical-device testing is waived for Foundation v1; retain desktop, narrow-layout and touch-emulation checks. No broad iOS/Android support claim follows. Decision recorded 2026-11-15 | FND-001 / FND-010 / AC-01 / AC-06 / AC-08 |
| Rights and packaging evidence | Preserve recorded owner-project reuse permissions and disclosures. Unverified package dimensions/artwork remain disclosed; new content or use requires a matching basis | Content owner, before admission/release |
| Later interactions and platform expansion | New cart integration, new seating/activity flows, additional floors, multi-company administration and transactions require separate scoped work | Master-plan stages 4–6 |

Changing the required shops, products, circulation model, business behavior or release gate requires an explicit entry in this decision register with rationale and affected acceptance IDs. Routine implementation choices remain with their owning role. Estimates are produced after the whitebox and baseline; no completion percentage or delivery date is implied here.

Definition of done: required backlog outputs exist, acceptance evidence covers the identified candidate, in-scope failures are resolved, preserved flows pass regression, and material device/content limits are disclosed. Scope freeze itself is complete when this contract is reviewable and its references are checked; it does not satisfy implementation or release gates.
