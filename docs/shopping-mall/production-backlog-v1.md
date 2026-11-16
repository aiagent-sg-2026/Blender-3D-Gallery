# Blender-3D-Gallery — Shopping Mall 3D Models Production Backlog

> Version: 1.0 | Date: 2026-11-15 | Status: PLANNED (not built or tested) | Scope: 400 independent assets

## Production contract

- **Units:** metres; dimensions are preliminary bounding-box targets (W×D×H), not verified engineering dimensions. Adapt per site and accessibility requirements.
- **Source:** one editable `.blend` and one exported `.glb` per asset, with `asset.json`, preview PNG, license/attribution, and QA report.
- **Naming:** `MALL-{CATEGORY}-{NNN}`; no duplicates. Asset IDs stay stable across revisions.
- **Transforms:** Z-up authoring; apply scale/rotation before export; glTF viewer validates orientation, origin, and real-world size.
- **Materials:** PBR metallic-roughness; 512–1024 px default, higher only with justification; no copyrighted branding without permission.
- **LOD:** L0 close / L1 mid / L2 distant; simplify topology and textures, maintain silhouette; LOD meshes are separate exported assets or application-managed variants, not assumed to be a native glTF extension.
- **Performance targets (provisional):** small props L0 ≤ 3k triangles, medium fixtures ≤ 12k, large structures ≤ 25k; batch/instance repeated modules; tune with actual mobile FPS tests.
- **Interaction:** Static, Inspect, Use, Open, Sit, Navigate; interaction logic and collision proxies are authored in scene/app metadata, not assumed to run from GLB alone.
- **QA:** automated mesh/export checks plus Blender viewport and Three.js browser render review; no PASS until evidence exists.
- **Safety:** emergency systems, escalators, elevators, and accessible paths are visual demo assets, not construction or code-compliance specifications.

## QA codes

| Code | Acceptance criteria |
|---|---|
| Q-BASE | Valid mesh; no unintended loose/nonmanifold geometry; normals outward; UVs present where textured; no missing images; correct origin/scale; export/import GLB; visible in viewer; triangle and texture budget checked |
| Q-UV | Q-BASE + readable sign/graphic at target distance; no mirrored text; placeholder or properly licensed artwork |
| Q-INT | Q-BASE + stable named interaction anchor, collision proxy, action metadata, keyboard/touch trigger and cancellation tested in app |
| Q-ANIM | Q-BASE + animation clips have correct duration/loop, no clipping or unexpected transforms; imported animation playback tested |

## Model registry

### STR — Building Structure (32)

| ID | Model | Size W×D×H (m) | Material | LOD | Interaction | Priority | Blender method | GLB QA |
|---|---|---|---|---|---|---|---|---|
| MALL-STR-001 | Straight floor module | 2.0×2.0×0.1 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Extrude+Array | Q-BASE |
| MALL-STR-002 | Corner floor module | 2.0×2.0×0.1 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Extrude+Array | Q-BASE |
| MALL-STR-003 | T-junction floor module | 2.0×2.0×0.1 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Extrude+Array | Q-BASE |
| MALL-STR-004 | Cross-junction floor module | 2.0×2.0×0.1 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Extrude+Array | Q-BASE |
| MALL-STR-005 | Atrium floor ring | 2.0×2.0×0.1 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Extrude+Array | Q-BASE |
| MALL-STR-006 | Raised platform | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-STR-007 | Structural square column | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-STR-008 | Structural round column | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-STR-009 | Column cladding | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-STR-010 | Straight wall module | 2.0×0.15×2.8 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-STR-011 | Corner wall module | 2.0×0.15×2.8 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-STR-012 | Glass curtain wall | 2.0×0.15×2.8 | PBR metal/glass | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-STR-013 | Solid partition | 2.0×0.15×2.8 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-STR-014 | Half-height partition | 2.0×0.15×2.8 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-STR-015 | Glass railing straight | 2.0×0.15×2.8 | PBR metal/glass | L0/L1/L2 | Static | P0 | Extrude+Array | Q-BASE |
| MALL-STR-016 | Glass railing corner | 2.0×0.15×2.8 | PBR metal/glass | L0/L1/L2 | Static | P0 | Extrude+Array | Q-BASE |
| MALL-STR-017 | Metal balustrade | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-STR-018 | Ceiling grid module | 2.0×0.15×2.8 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-STR-019 | Suspended ceiling panel | 2.0×0.15×2.8 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-STR-020 | Ceiling bulkhead | 2.0×0.15×2.8 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-STR-021 | Ceiling cove | 2.0×0.15×2.8 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-STR-022 | Roof skylight | 0.8×0.12×0.6 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-STR-023 | Atrium balcony edge | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-STR-024 | Doorway opening | 3.0×0.25×3.0 | PBR concrete/metal | L0/L1/L2 | Open | P1 | Primitives+Bevel | Q-BASE |
| MALL-STR-025 | Double swing door | 3.0×0.25×3.0 | PBR concrete/metal | L0/L1/L2 | Open | P1 | Primitives+Bevel | Q-BASE |
| MALL-STR-026 | Sliding glass door | 3.0×0.25×3.0 | PBR metal/glass | L0/L1/L2 | Open | P1 | Primitives+Bevel | Q-BASE |
| MALL-STR-027 | Fire-rated door | 3.0×0.25×3.0 | PBR concrete/metal | L0/L1/L2 | Open | P1 | Primitives+Bevel | Q-BASE |
| MALL-STR-028 | Service corridor door | 3.0×0.25×3.0 | PBR concrete/metal | L0/L1/L2 | Open | P1 | Primitives+Bevel | Q-BASE |
| MALL-STR-029 | Loading bay door | 3.0×0.25×3.0 | PBR concrete/metal | L0/L1/L2 | Open | P1 | Primitives+Bevel | Q-BASE |
| MALL-STR-030 | Stair landing | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Extrude+Array | Q-BASE |
| MALL-STR-031 | Ramp module | 5.0×1.5×3.2 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-STR-032 | Threshold strip | 2.0×0.15×2.8 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |

### INT — Interior Architecture (32)

| ID | Model | Size W×D×H (m) | Material | LOD | Interaction | Priority | Blender method | GLB QA |
|---|---|---|---|---|---|---|---|---|
| MALL-INT-001 | Porcelain floor tile | 2.0×2.0×0.1 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Extrude+Array | Q-BASE |
| MALL-INT-002 | Terrazzo floor tile | 2.0×2.0×0.1 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Extrude+Array | Q-BASE |
| MALL-INT-003 | Marble floor tile | 2.0×2.0×0.1 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Extrude+Array | Q-BASE |
| MALL-INT-004 | Wood-look floor tile | 2.0×2.0×0.1 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Extrude+Array | Q-BASE |
| MALL-INT-005 | Carpet tile | 2.0×2.0×0.1 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Extrude+Array | Q-BASE |
| MALL-INT-006 | Anti-slip floor tile | 2.0×2.0×0.1 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Extrude+Array | Q-BASE |
| MALL-INT-007 | Feature wall panel | 2.0×0.15×2.8 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-INT-008 | Wood slat wall | 2.0×0.15×2.8 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-INT-009 | Stone veneer wall | 2.0×0.15×2.8 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-INT-010 | Acoustic wall panel | 2.0×0.15×2.8 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-INT-011 | Mirrored wall panel | 2.0×0.15×2.8 | PBR metal/glass | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-INT-012 | Decorative metal screen | 0.8×0.12×0.6 | PBR metal/glass | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-INT-013 | Glass divider | 1.0×0.8×1.5 | PBR metal/glass | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-INT-014 | Privacy film glass | 1.0×0.8×1.5 | PBR metal/glass | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-INT-015 | Ceiling baffle | 2.0×0.15×2.8 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-INT-016 | Ceiling acoustic raft | 2.0×0.15×2.8 | PBR concrete/metal | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-INT-017 | Ceiling grille | 2.0×0.15×2.8 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-INT-018 | Ceiling service hatch | 2.0×0.15×2.8 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-INT-019 | Cove trim | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-INT-020 | Skirting board | 2.0×0.15×2.8 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-INT-021 | Wall corner guard | 2.0×0.15×2.8 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-INT-022 | Decorative arch | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-INT-023 | Interior portal | 3.0×0.25×3.0 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-INT-024 | Recessed niche | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-INT-025 | Feature staircase cladding | 5.0×1.5×3.2 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Extrude+Array | Q-BASE |
| MALL-INT-026 | Atrium fascia | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-INT-027 | Shopfront soffit | 3.0×0.25×3.0 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-INT-028 | Column light recess | 0.8×0.12×0.6 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-INT-029 | Floor inlay strip | 2.0×2.0×0.1 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Extrude+Array | Q-BASE |
| MALL-INT-030 | Floor transition profile | 2.0×2.0×0.1 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Extrude+Array | Q-BASE |
| MALL-INT-031 | Window sill | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-INT-032 | Interior handrail | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Curve+Bevel | Q-BASE |

### STO — Storefronts (32)

| ID | Model | Size W×D×H (m) | Material | LOD | Interaction | Priority | Blender method | GLB QA |
|---|---|---|---|---|---|---|---|---|
| MALL-STO-001 | Basic shopfront frame | 3.0×0.25×3.0 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-STO-002 | Wide shopfront frame | 3.0×0.25×3.0 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-STO-003 | Corner shopfront frame | 3.0×0.25×3.0 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-STO-004 | Luxury boutique entrance | 3.0×0.25×3.0 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-STO-005 | Convenience store entrance | 3.0×0.25×3.0 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-STO-006 | Electronics store entrance | 3.0×0.25×3.0 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-STO-007 | Fashion store entrance | 3.0×0.25×3.0 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-STO-008 | Beauty store entrance | 3.0×0.25×3.0 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-STO-009 | Jewelry store entrance | 3.0×0.25×3.0 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-STO-010 | Bookstore entrance | 3.0×0.25×3.0 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-STO-011 | Toy store entrance | 3.0×0.25×3.0 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-STO-012 | Pharmacy entrance | 3.0×0.25×3.0 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-STO-013 | Supermarket entrance | 3.0×0.25×3.0 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-STO-014 | Bakery entrance | 3.0×0.25×3.0 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-STO-015 | Cafe entrance | 3.0×0.25×3.0 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-STO-016 | Restaurant entrance | 3.0×0.25×3.0 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-STO-017 | Kiosk booth shell | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-STO-018 | Pop-up store shell | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-STO-019 | Glass shop door | 3.0×0.25×3.0 | PBR metal/glass | L0/L1/L2 | Open | P1 | Primitives+Bevel | Q-BASE |
| MALL-STO-020 | Automatic sliding entrance | 3.0×0.25×3.0 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-STO-021 | Shop roller shutter | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Open | P1 | Primitives+Bevel | Q-BASE |
| MALL-STO-022 | Shop sign fascia | 0.8×0.12×0.6 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-STO-023 | Illuminated logo panel | 2.0×0.15×2.8 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-STO-024 | Window display bay | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-STO-025 | Store display plinth | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-STO-026 | Window display light rail | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Curve+Bevel | Q-BASE |
| MALL-STO-027 | Entrance security pedestal | 3.0×0.25×3.0 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-STO-028 | Door handle set | 3.0×0.25×3.0 | PBR painted/metal | L0/L1/L2 | Open | P1 | Primitives+Bevel | Q-BASE |
| MALL-STO-029 | Shopfront mullion | 3.0×0.25×3.0 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-STO-030 | Shopfront transom | 3.0×0.25×3.0 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-STO-031 | Shopfront canopy | 3.0×0.25×3.0 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-STO-032 | Store wall branding panel | 2.0×0.15×2.8 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |

### RET — Retail Fixtures (37)

| ID | Model | Size W×D×H (m) | Material | LOD | Interaction | Priority | Blender method | GLB QA |
|---|---|---|---|---|---|---|---|---|
| MALL-RET-001 | Wall display shelf | 2.0×0.15×2.8 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Extrude+Array | Q-BASE |
| MALL-RET-002 | Island gondola shelf | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Extrude+Array | Q-BASE |
| MALL-RET-003 | Endcap shelf | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Extrude+Array | Q-BASE |
| MALL-RET-004 | Glass display cabinet | 1.8×0.7×1.2 | PBR metal/glass | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-RET-005 | Lockable showcase | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-RET-006 | Product pedestal | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-RET-007 | Tiered product riser | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-RET-008 | Pegboard wall | 2.0×0.15×2.8 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-RET-009 | Peg hook set | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-RET-010 | Slatwall panel | 2.0×0.15×2.8 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-RET-011 | Slatwall shelf | 2.0×0.15×2.8 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Extrude+Array | Q-BASE |
| MALL-RET-012 | Clothing rack straight | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Extrude+Array | Q-BASE |
| MALL-RET-013 | Clothing rack circular | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Extrude+Array | Q-BASE |
| MALL-RET-014 | Mannequin torso | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-RET-015 | Full-body mannequin | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-RET-016 | Shoe display wall | 2.0×0.15×2.8 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-RET-017 | Handbag display stand | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-RET-018 | Jewelry tray | 0.3×0.3×0.15 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-RET-019 | Watch display stand | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-RET-020 | Cosmetics tester bar | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-RET-021 | Perfume display stand | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-RET-022 | Electronics demo table | 1.2×0.8×0.75 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-RET-023 | Phone security stand | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-RET-024 | TV display wall | 2.0×0.15×2.8 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-RET-025 | Refrigerated display case | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-RET-026 | Open chiller cabinet | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-RET-027 | Freezer chest | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-RET-028 | Beverage refrigerator | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-RET-029 | Checkout counter | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-RET-030 | POS terminal | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-RET-031 | Barcode scanner | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-RET-032 | Receipt printer | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-RET-033 | Shopping basket | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-RET-034 | Shopping cart | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-RET-035 | Price label holder | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-RET-036 | Shelf talker | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Extrude+Array | Q-BASE |
| MALL-RET-037 | Queue rail | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Curve+Bevel | Q-BASE |

### FUR — Furniture (32)

| ID | Model | Size W×D×H (m) | Material | LOD | Interaction | Priority | Blender method | GLB QA |
|---|---|---|---|---|---|---|---|---|
| MALL-FUR-001 | Mall bench straight | 1.2×0.65×0.85 | PBR wood/fabric | L0/L1/L2 | Sit | P0 | Primitives+Bevel | Q-BASE |
| MALL-FUR-002 | Mall bench curved | 1.2×0.65×0.85 | PBR wood/fabric | L0/L1/L2 | Sit | P0 | Primitives+Bevel | Q-BASE |
| MALL-FUR-003 | Mall lounge sofa | 1.2×0.65×0.85 | PBR wood/fabric | L0/L1/L2 | Sit | P0 | Primitives+Bevel | Q-BASE |
| MALL-FUR-004 | Single lounge chair | 1.2×0.65×0.85 | PBR wood/fabric | L0/L1/L2 | Sit | P0 | Primitives+Bevel | Q-BASE |
| MALL-FUR-005 | Ottoman stool | 1.2×0.65×0.85 | PBR wood/fabric | L0/L1/L2 | Sit | P0 | Primitives+Bevel | Q-BASE |
| MALL-FUR-006 | Round dining table | 1.2×0.8×0.75 | PBR wood/fabric | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-FUR-007 | Square dining table | 1.2×0.8×0.75 | PBR wood/fabric | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-FUR-008 | Rectangular dining table | 1.2×0.8×0.75 | PBR wood/fabric | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-FUR-009 | Dining chair | 1.2×0.65×0.85 | PBR wood/fabric | L0/L1/L2 | Sit | P0 | Primitives+Bevel | Q-BASE |
| MALL-FUR-010 | Bar stool | 1.2×0.65×0.85 | PBR wood/fabric | L0/L1/L2 | Sit | P0 | Primitives+Bevel | Q-BASE |
| MALL-FUR-011 | High-top table | 1.2×0.8×0.75 | PBR wood/fabric | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-FUR-012 | Cafe booth seating | 1.2×0.65×0.85 | PBR wood/fabric | L0/L1/L2 | Sit | P0 | Primitives+Bevel | Q-BASE |
| MALL-FUR-013 | Food court bench | 1.2×0.65×0.85 | PBR wood/fabric | L0/L1/L2 | Sit | P0 | Primitives+Bevel | Q-BASE |
| MALL-FUR-014 | Children seat | 1.2×0.65×0.85 | PBR wood/fabric | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-FUR-015 | Accessible table | 1.2×0.8×0.75 | PBR wood/fabric | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-FUR-016 | Reception desk | 1.8×0.7×1.2 | PBR wood/fabric | L0/L1/L2 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-FUR-017 | Information desk | 1.8×0.7×1.2 | PBR wood/fabric | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-FUR-018 | Coffee table | 1.2×0.8×0.75 | PBR wood/fabric | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-FUR-019 | Side table | 1.2×0.8×0.75 | PBR wood/fabric | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-FUR-020 | Console table | 1.2×0.8×0.75 | PBR wood/fabric | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-FUR-021 | Waiting area chair | 1.2×0.65×0.85 | PBR wood/fabric | L0/L1/L2 | Sit | P1 | Primitives+Bevel | Q-BASE |
| MALL-FUR-022 | Modular seating block | 1.2×0.65×0.85 | PBR wood/fabric | L0/L1/L2 | Sit | P1 | Primitives+Bevel | Q-BASE |
| MALL-FUR-023 | Planter bench | 1.2×0.65×0.85 | PBR wood/fabric | L0/L1/L2 | Sit | P1 | Primitives+Bevel | Q-BASE |
| MALL-FUR-024 | Wooden stool | 1.2×0.65×0.85 | PBR wood/fabric | L0/L1/L2 | Sit | P1 | Primitives+Bevel | Q-BASE |
| MALL-FUR-025 | Metal stool | 1.2×0.65×0.85 | PBR wood/fabric | L0/L1/L2 | Sit | P1 | Primitives+Bevel | Q-BASE |
| MALL-FUR-026 | Stackable chair | 1.2×0.65×0.85 | PBR wood/fabric | L0/L1/L2 | Sit | P1 | Primitives+Bevel | Q-BASE |
| MALL-FUR-027 | Foldable table | 1.2×0.8×0.75 | PBR wood/fabric | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-FUR-028 | Outdoor bench | 3.0×0.25×3.0 | PBR wood/fabric | L0/L1/L2 | Sit | P1 | Primitives+Bevel | Q-BASE |
| MALL-FUR-029 | Outdoor table | 3.0×0.25×3.0 | PBR wood/fabric | L0/L1/L2 | Open | P1 | Primitives+Bevel | Q-BASE |
| MALL-FUR-030 | Outdoor chair | 3.0×0.25×3.0 | PBR wood/fabric | L0/L1/L2 | Sit | P1 | Primitives+Bevel | Q-BASE |
| MALL-FUR-031 | Baby feeding chair | 1.2×0.65×0.85 | PBR wood/fabric | L0/L1/L2 | Sit | P1 | Primitives+Bevel | Q-BASE |
| MALL-FUR-032 | Wheelchair resting bay marker | 1.2×0.65×0.85 | PBR wood/fabric | L0/L1/L2 | Sit | P1 | Primitives+Bevel | Q-BASE |

### LGT — Lighting (25)

| ID | Model | Size W×D×H (m) | Material | LOD | Interaction | Priority | Blender method | GLB QA |
|---|---|---|---|---|---|---|---|---|
| MALL-LGT-001 | Recessed downlight | 0.8×0.12×0.6 | PBR painted/metal | L0/L1 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-LGT-002 | Linear ceiling light | 2.0×0.15×2.8 | PBR painted/metal | L0/L1 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-LGT-003 | Pendant globe light | 0.8×0.12×0.6 | PBR painted/metal | L0/L1 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-LGT-004 | Pendant cylinder light | 0.8×0.12×0.6 | PBR painted/metal | L0/L1 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-LGT-005 | Track light rail | 1.8×0.7×1.2 | PBR painted/metal | L0/L1 | Static | P0 | Extrude+Array | Q-BASE |
| MALL-LGT-006 | Track spotlight | 1.8×0.7×1.2 | PBR painted/metal | L0/L1 | Static | P0 | Extrude+Array | Q-BASE |
| MALL-LGT-007 | Wall sconce | 2.0×0.15×2.8 | PBR painted/metal | L0/L1 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-LGT-008 | Cove LED strip | 2.0×0.15×2.8 | PBR painted/metal | L0/L1 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-LGT-009 | Floor uplight | 2.0×2.0×0.1 | PBR painted/metal | L0/L1 | Static | P0 | Extrude+Array | Q-BASE |
| MALL-LGT-010 | Stair tread light | 0.8×0.12×0.6 | PBR painted/metal | L0/L1 | Static | P0 | Extrude+Array | Q-BASE |
| MALL-LGT-011 | Emergency bulkhead light | 0.8×0.12×0.6 | PBR painted/metal | L0/L1 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-LGT-012 | Exit light box | 0.8×0.12×0.6 | PBR painted/metal | L0/L1 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-LGT-013 | Display cabinet LED | 1.8×0.7×1.2 | PBR metal/glass | L0/L1 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-LGT-014 | Shelf LED strip | 2.0×0.15×2.8 | PBR painted/metal | L0/L1 | Static | P0 | Extrude+Array | Q-BASE |
| MALL-LGT-015 | Storefront light bar | 0.8×0.12×0.6 | PBR painted/metal | L0/L1 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-LGT-016 | Decorative chandelier | 1.0×0.8×1.5 | PBR painted/metal | L0/L1 | Static | P0 | Primitives+Bevel | Q-BASE |
| MALL-LGT-017 | Atrium ring chandelier | 1.0×0.8×1.5 | PBR painted/metal | L0/L1 | Static | P1 | Curve+Bevel | Q-BASE |
| MALL-LGT-018 | Light column | 0.8×0.12×0.6 | PBR painted/metal | L0/L1 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-LGT-019 | Outdoor bollard light | 3.0×0.25×3.0 | PBR painted/metal | L0/L1 | Open | P1 | Primitives+Bevel | Q-BASE |
| MALL-LGT-020 | Parking ceiling light | 2.0×0.15×2.8 | PBR painted/metal | L0/L1 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-LGT-021 | Parking warning beacon | 1.0×0.8×1.5 | PBR painted/metal | L0/L1 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-LGT-022 | Backlit panel | 2.0×0.15×2.8 | PBR painted/metal | L0/L1 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-LGT-023 | Neon sign tube | 0.8×0.12×0.6 | PBR painted/metal | L0/L1 | Static | P1 | Curve+Bevel | Q-BASE |
| MALL-LGT-024 | Food stall heat lamp | 0.8×0.12×0.6 | PBR painted/metal | L0/L1 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-LGT-025 | Accent projector lamp | 0.8×0.12×0.6 | PBR painted/metal | L0/L1 | Static | P1 | Primitives+Bevel | Q-BASE |

### PUB — Public Facilities (32)

| ID | Model | Size W×D×H (m) | Material | LOD | Interaction | Priority | Blender method | GLB QA |
|---|---|---|---|---|---|---|---|---|
| MALL-PUB-001 | Information kiosk | 1.8×0.7×1.2 | PBR plastic/metal | L0/L1/L2 | Static | P0 | Primitives+Boolean | Q-BASE |
| MALL-PUB-002 | Mall directory kiosk | 1.8×0.7×1.2 | PBR plastic/metal | L0/L1/L2 | Static | P0 | Primitives+Boolean | Q-BASE |
| MALL-PUB-003 | Digital wayfinding kiosk | 1.8×0.7×1.2 | PBR plastic/metal | L0/L1/L2 | Static | P0 | Primitives+Boolean | Q-BASE |
| MALL-PUB-004 | Rubbish bin | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P0 | Primitives+Boolean | Q-BASE |
| MALL-PUB-005 | Recycling bin | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P0 | Primitives+Boolean | Q-BASE |
| MALL-PUB-006 | Waste sorting station | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P0 | Primitives+Boolean | Q-BASE |
| MALL-PUB-007 | Planter box | 1.2×1.2×2.5 | PBR plastic/metal | L0/L1/L2 | Static | P0 | Primitives+Boolean | Q-BASE |
| MALL-PUB-008 | Indoor tree pot | 3.0×0.25×3.0 | PBR plastic/metal | L0/L1/L2 | Open | P0 | Primitives+Boolean | Q-BASE |
| MALL-PUB-009 | Drinking fountain | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P0 | Primitives+Boolean | Q-BASE |
| MALL-PUB-010 | Water bottle refill station | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P0 | Primitives+Boolean | Q-BASE |
| MALL-PUB-011 | Public clock | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P0 | Primitives+Boolean | Q-BASE |
| MALL-PUB-012 | ATM machine | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P0 | Primitives+Boolean | Q-BASE |
| MALL-PUB-013 | Parcel locker | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Open | P0 | Primitives+Boolean | Q-BASE |
| MALL-PUB-014 | Phone charging locker | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Open | P0 | Primitives+Boolean | Q-BASE |
| MALL-PUB-015 | Public charging station | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P0 | Primitives+Boolean | Q-BASE |
| MALL-PUB-016 | Queue barrier | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P0 | Primitives+Boolean | Q-BASE |
| MALL-PUB-017 | Retractable belt post | 1.2×0.8×0.75 | PBR plastic/metal | L0/L1/L2 | Static | P1 | Primitives+Boolean | Q-BASE |
| MALL-PUB-018 | Stroller parking stand | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P1 | Primitives+Boolean | Q-BASE |
| MALL-PUB-019 | Wheelchair parking stand | 1.2×0.65×0.85 | PBR plastic/metal | L0/L1/L2 | Sit | P1 | Primitives+Boolean | Q-BASE |
| MALL-PUB-020 | Baby stroller | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P1 | Primitives+Boolean | Q-BASE |
| MALL-PUB-021 | Public seating island | 1.2×0.65×0.85 | PBR plastic/metal | L0/L1/L2 | Sit | P1 | Primitives+Boolean | Q-BASE |
| MALL-PUB-022 | Lost and found counter | 1.8×0.7×1.2 | PBR plastic/metal | L0/L1/L2 | Static | P1 | Primitives+Boolean | Q-BASE |
| MALL-PUB-023 | Customer service bell | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P1 | Primitives+Boolean | Q-BASE |
| MALL-PUB-024 | Restroom entrance portal | 3.0×0.25×3.0 | PBR plastic/metal | L0/L1/L2 | Static | P1 | Primitives+Boolean | Q-BASE |
| MALL-PUB-025 | Accessible restroom door | 3.0×0.25×3.0 | PBR plastic/metal | L0/L1/L2 | Open | P1 | Primitives+Boolean | Q-BASE |
| MALL-PUB-026 | Baby changing station | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P1 | Primitives+Boolean | Q-BASE |
| MALL-PUB-027 | Hand dryer | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P1 | Primitives+Boolean | Q-BASE |
| MALL-PUB-028 | Soap dispenser | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P1 | Primitives+Boolean | Q-BASE |
| MALL-PUB-029 | Paper towel dispenser | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P1 | Primitives+Boolean | Q-BASE |
| MALL-PUB-030 | Sanitary disposal bin | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P1 | Primitives+Boolean | Q-BASE |
| MALL-PUB-031 | Public mirror | 1.0×0.8×1.5 | PBR metal/glass | L0/L1/L2 | Static | P1 | Primitives+Boolean | Q-BASE |
| MALL-PUB-032 | Water dispenser | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P1 | Primitives+Boolean | Q-BASE |

### FNB — Food Court & F&B (33)

| ID | Model | Size W×D×H (m) | Material | LOD | Interaction | Priority | Blender method | GLB QA |
|---|---|---|---|---|---|---|---|---|
| MALL-FNB-001 | Food stall counter | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-FNB-002 | Hawker stall counter | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-FNB-003 | Cafe service counter | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-FNB-004 | Bakery display counter | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-FNB-005 | Dessert stall counter | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-FNB-006 | Bubble tea counter | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-FNB-007 | Juice bar counter | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-FNB-008 | Coffee espresso machine | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-FNB-009 | Coffee grinder | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-FNB-010 | Beverage dispenser | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-FNB-011 | Soda fountain | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-FNB-012 | Tea urn | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-FNB-013 | Rice cooker | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-FNB-014 | Food warmer | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-FNB-015 | Display bain-marie | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-FNB-016 | Food menu board | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P0 | Primitives+Bevel | Q-BASE |
| MALL-FNB-017 | Digital order screen | 0.8×0.12×0.6 | PBR metal/glass | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-FNB-018 | Self-order kiosk | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-FNB-019 | Pickup shelf | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Extrude+Array | Q-BASE |
| MALL-FNB-020 | Tray return station | 0.3×0.3×0.15 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-FNB-021 | Dish collection trolley | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-FNB-022 | Food tray | 0.3×0.3×0.15 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-FNB-023 | Reusable plate | 0.3×0.3×0.15 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-FNB-024 | Bowl | 0.3×0.3×0.15 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-FNB-025 | Cup with lid | 0.3×0.3×0.15 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-FNB-026 | Cutlery set | 0.3×0.3×0.15 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-FNB-027 | Napkin dispenser | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-FNB-028 | Condiment station | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-FNB-029 | Tissue holder | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-FNB-030 | Water jug | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-FNB-031 | Food court table divider | 1.2×0.8×0.75 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-FNB-032 | Kitchen pass window | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |
| MALL-FNB-033 | Commercial refrigerator | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-BASE |

### SIG — Signage & Advertising (25)

| ID | Model | Size W×D×H (m) | Material | LOD | Interaction | Priority | Blender method | GLB QA |
|---|---|---|---|---|---|---|---|---|
| MALL-SIG-001 | Advertising lightbox | 0.8×0.12×0.6 | PBR metal/glass | L0/L1 | Navigate | P0 | Primitives+Bevel | Q-UV |
| MALL-SIG-002 | Digital advertising screen | 0.8×0.12×0.6 | PBR metal/glass | L0/L1 | Navigate | P0 | Primitives+Bevel | Q-UV |
| MALL-SIG-003 | Mall floor directory | 2.0×2.0×0.1 | PBR painted/metal | L0/L1 | Navigate | P0 | Extrude+Array | Q-UV |
| MALL-SIG-004 | Overhead directional sign | 0.8×0.12×0.6 | PBR painted/metal | L0/L1 | Navigate | P0 | Primitives+Bevel | Q-UV |
| MALL-SIG-005 | Wall directional sign | 2.0×0.15×2.8 | PBR painted/metal | L0/L1 | Navigate | P0 | Primitives+Bevel | Q-UV |
| MALL-SIG-006 | Restroom sign | 0.8×0.12×0.6 | PBR painted/metal | L0/L1 | Navigate | P0 | Primitives+Bevel | Q-UV |
| MALL-SIG-007 | Accessible route sign | 0.8×0.12×0.6 | PBR painted/metal | L0/L1 | Navigate | P0 | Primitives+Bevel | Q-UV |
| MALL-SIG-008 | Emergency exit sign | 0.8×0.12×0.6 | PBR painted/metal | L0/L1 | Navigate | P0 | Primitives+Bevel | Q-UV |
| MALL-SIG-009 | No smoking sign | 0.8×0.12×0.6 | PBR painted/metal | L0/L1 | Navigate | P0 | Primitives+Bevel | Q-UV |
| MALL-SIG-010 | Store promotion poster | 0.8×0.12×0.6 | PBR painted/metal | L0/L1 | Navigate | P0 | Primitives+Bevel | Q-UV |
| MALL-SIG-011 | Standing poster frame | 0.8×0.12×0.6 | PBR painted/metal | L0/L1 | Navigate | P0 | Primitives+Bevel | Q-UV |
| MALL-SIG-012 | A-frame sidewalk sign | 0.8×0.12×0.6 | PBR painted/metal | L0/L1 | Navigate | P0 | Primitives+Bevel | Q-UV |
| MALL-SIG-013 | Hanging banner | 0.8×0.12×0.6 | PBR painted/metal | L0/L1 | Navigate | P0 | Primitives+Bevel | Q-UV |
| MALL-SIG-014 | Vertical banner stand | 0.8×0.12×0.6 | PBR painted/metal | L0/L1 | Navigate | P0 | Primitives+Bevel | Q-UV |
| MALL-SIG-015 | Ceiling banner | 2.0×0.15×2.8 | PBR painted/metal | L0/L1 | Navigate | P0 | Primitives+Bevel | Q-UV |
| MALL-SIG-016 | Floor decal | 2.0×2.0×0.1 | PBR painted/metal | L0/L1 | Navigate | P0 | Extrude+Array | Q-UV |
| MALL-SIG-017 | Window vinyl graphic | 1.0×0.8×1.5 | PBR painted/metal | L0/L1 | Navigate | P1 | Primitives+Bevel | Q-UV |
| MALL-SIG-018 | Brand logo plaque | 1.0×0.8×1.5 | PBR painted/metal | L0/L1 | Navigate | P1 | Primitives+Bevel | Q-UV |
| MALL-SIG-019 | Store opening hours plaque | 1.0×0.8×1.5 | PBR painted/metal | L0/L1 | Navigate | P1 | Primitives+Bevel | Q-UV |
| MALL-SIG-020 | Price promotion tag | 1.0×0.8×1.5 | PBR painted/metal | L0/L1 | Navigate | P1 | Primitives+Bevel | Q-UV |
| MALL-SIG-021 | QR code display stand | 1.8×0.7×1.2 | PBR painted/metal | L0/L1 | Navigate | P1 | Primitives+Bevel | Q-UV |
| MALL-SIG-022 | Interactive map display | 1.8×0.7×1.2 | PBR painted/metal | L0/L1 | Navigate | P1 | Primitives+Bevel | Q-UV |
| MALL-SIG-023 | Event stage backdrop | 1.0×0.8×1.5 | PBR painted/metal | L0/L1 | Navigate | P1 | Primitives+Bevel | Q-UV |
| MALL-SIG-024 | Parking direction sign | 0.8×0.12×0.6 | PBR painted/metal | L0/L1 | Navigate | P1 | Primitives+Bevel | Q-UV |
| MALL-SIG-025 | Loading bay sign | 0.8×0.12×0.6 | PBR painted/metal | L0/L1 | Navigate | P1 | Primitives+Bevel | Q-UV |

### VRT — Vertical Transport (20)

| ID | Model | Size W×D×H (m) | Material | LOD | Interaction | Priority | Blender method | GLB QA |
|---|---|---|---|---|---|---|---|---|
| MALL-VRT-001 | Escalator up | 5.0×1.5×3.2 | PBR plastic/metal | L0/L1/L2 | Navigate | P0 | Primitives+Bevel | Q-ANIM |
| MALL-VRT-002 | Escalator down | 5.0×1.5×3.2 | PBR plastic/metal | L0/L1/L2 | Navigate | P0 | Primitives+Bevel | Q-ANIM |
| MALL-VRT-003 | Escalator landing comb plate | 5.0×1.5×3.2 | PBR plastic/metal | L0/L1/L2 | Navigate | P0 | Primitives+Bevel | Q-ANIM |
| MALL-VRT-004 | Escalator handrail | 5.0×1.5×3.2 | PBR plastic/metal | L0/L1/L2 | Navigate | P0 | Curve+Bevel | Q-ANIM |
| MALL-VRT-005 | Escalator side glass | 5.0×1.5×3.2 | PBR metal/glass | L0/L1/L2 | Navigate | P0 | Primitives+Bevel | Q-ANIM |
| MALL-VRT-006 | Elevator door single | 3.0×0.25×3.0 | PBR plastic/metal | L0/L1/L2 | Open | P0 | Primitives+Bevel | Q-BASE |
| MALL-VRT-007 | Elevator door double | 3.0×0.25×3.0 | PBR plastic/metal | L0/L1/L2 | Open | P0 | Primitives+Bevel | Q-BASE |
| MALL-VRT-008 | Elevator call panel | 2.0×0.15×2.8 | PBR plastic/metal | L0/L1/L2 | Navigate | P0 | Primitives+Bevel | Q-BASE |
| MALL-VRT-009 | Elevator cabin | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Navigate | P0 | Primitives+Bevel | Q-ANIM |
| MALL-VRT-010 | Elevator floor indicator | 2.0×2.0×0.1 | PBR plastic/metal | L0/L1/L2 | Navigate | P0 | Extrude+Array | Q-BASE |
| MALL-VRT-011 | Elevator control panel | 2.0×0.15×2.8 | PBR plastic/metal | L0/L1/L2 | Navigate | P0 | Primitives+Bevel | Q-BASE |
| MALL-VRT-012 | Staircase straight | 5.0×1.5×3.2 | PBR plastic/metal | L0/L1/L2 | Navigate | P0 | Extrude+Array | Q-BASE |
| MALL-VRT-013 | Staircase U-turn | 5.0×1.5×3.2 | PBR plastic/metal | L0/L1/L2 | Navigate | P0 | Extrude+Array | Q-BASE |
| MALL-VRT-014 | Staircase handrail | 5.0×1.5×3.2 | PBR plastic/metal | L0/L1/L2 | Navigate | P0 | Extrude+Array | Q-BASE |
| MALL-VRT-015 | Accessible ramp | 5.0×1.5×3.2 | PBR plastic/metal | L0/L1/L2 | Navigate | P0 | Primitives+Bevel | Q-BASE |
| MALL-VRT-016 | Ramp handrail | 5.0×1.5×3.2 | PBR plastic/metal | L0/L1/L2 | Navigate | P0 | Curve+Bevel | Q-BASE |
| MALL-VRT-017 | Moving walkway | 5.0×1.5×3.2 | PBR plastic/metal | L0/L1/L2 | Navigate | P1 | Primitives+Bevel | Q-ANIM |
| MALL-VRT-018 | Moving walkway landing | 5.0×1.5×3.2 | PBR plastic/metal | L0/L1/L2 | Navigate | P1 | Primitives+Bevel | Q-ANIM |
| MALL-VRT-019 | Service lift entrance | 3.0×0.25×3.0 | PBR plastic/metal | L0/L1/L2 | Navigate | P1 | Primitives+Bevel | Q-BASE |
| MALL-VRT-020 | Lift lobby portal | 3.0×0.25×3.0 | PBR plastic/metal | L0/L1/L2 | Navigate | P1 | Primitives+Bevel | Q-BASE |

### DEC — Decorations (20)

| ID | Model | Size W×D×H (m) | Material | LOD | Interaction | Priority | Blender method | GLB QA |
|---|---|---|---|---|---|---|---|---|
| MALL-DEC-001 | Indoor tree | 3.0×0.25×3.0 | PBR painted/metal | L0/L1/L2 | Open | P1 | Primitives+Bevel | Q-BASE |
| MALL-DEC-002 | Potted palm | 1.2×1.2×2.5 | PBR painted/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-DEC-003 | Potted fern | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-DEC-004 | Hanging planter | 1.2×1.2×2.5 | PBR painted/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-DEC-005 | Vertical green wall | 2.0×0.15×2.8 | PBR painted/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-DEC-006 | Flower arrangement | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-DEC-007 | Decorative vase | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-DEC-008 | Sculpture pedestal | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-DEC-009 | Abstract sculpture | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-DEC-010 | Wall art frame | 2.0×0.15×2.8 | PBR painted/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-DEC-011 | Digital art frame | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-DEC-012 | Water feature basin | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-DEC-013 | Decorative fountain | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Static | P2 | Primitives+Bevel | Q-BASE |
| MALL-DEC-014 | Atrium hanging mobile | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Static | P2 | Primitives+Bevel | Q-BASE |
| MALL-DEC-015 | Seasonal decor arch | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Static | P2 | Primitives+Bevel | Q-BASE |
| MALL-DEC-016 | Festival lantern | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Static | P2 | Primitives+Bevel | Q-BASE |
| MALL-DEC-017 | Christmas tree | 1.2×1.2×2.5 | PBR painted/metal | L0/L1/L2 | Static | P2 | Primitives+Bevel | Q-BASE |
| MALL-DEC-018 | Deepavali decoration stand | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Static | P2 | Primitives+Bevel | Q-BASE |
| MALL-DEC-019 | Hari Raya ketupat display | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Static | P2 | Primitives+Bevel | Q-BASE |
| MALL-DEC-020 | Chinese New Year ornament | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Static | P2 | Primitives+Bevel | Q-BASE |

### PKG — Parking & Outdoor (25)

| ID | Model | Size W×D×H (m) | Material | LOD | Interaction | Priority | Blender method | GLB QA |
|---|---|---|---|---|---|---|---|---|
| MALL-PKG-001 | Parking bay marking | 2.0×0.15×2.8 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-PKG-002 | Accessible parking bay | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-PKG-003 | EV charging bay | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-PKG-004 | EV charger pedestal | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-PKG-005 | Parking wheel stopper | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-PKG-006 | Parking bollard | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-PKG-007 | Parking barrier arm | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-ANIM |
| MALL-PKG-008 | Ticket payment kiosk | 1.8×0.7×1.2 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-PKG-009 | Parking ticket dispenser | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-PKG-010 | Parking entry gantry | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-PKG-011 | Parking exit gantry | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-PKG-012 | Parking directional arrow | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P1 | Primitives+Bevel | Q-BASE |
| MALL-PKG-013 | Parking column marker | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P2 | Primitives+Bevel | Q-BASE |
| MALL-PKG-014 | Parking convex mirror | 1.0×0.8×1.5 | PBR metal/glass | L0/L1/L2 | Static | P2 | Primitives+Bevel | Q-BASE |
| MALL-PKG-015 | Speed bump | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P2 | Primitives+Bevel | Q-BASE |
| MALL-PKG-016 | Pedestrian crossing | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P2 | Primitives+Bevel | Q-BASE |
| MALL-PKG-017 | Outdoor pavement tile | 2.0×2.0×0.1 | PBR concrete/metal | L0/L1/L2 | Open | P2 | Extrude+Array | Q-BASE |
| MALL-PKG-018 | Outdoor curb | 3.0×0.25×3.0 | PBR concrete/metal | L0/L1/L2 | Open | P2 | Primitives+Bevel | Q-BASE |
| MALL-PKG-019 | Street planter | 1.2×1.2×2.5 | PBR concrete/metal | L0/L1/L2 | Static | P2 | Primitives+Bevel | Q-BASE |
| MALL-PKG-020 | Outdoor trash bin | 3.0×0.25×3.0 | PBR concrete/metal | L0/L1/L2 | Open | P2 | Primitives+Bevel | Q-BASE |
| MALL-PKG-021 | Bus stop shelter | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P2 | Primitives+Bevel | Q-BASE |
| MALL-PKG-022 | Taxi pickup sign | 0.8×0.12×0.6 | PBR concrete/metal | L0/L1/L2 | Static | P2 | Primitives+Bevel | Q-BASE |
| MALL-PKG-023 | Drop-off canopy | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P2 | Primitives+Bevel | Q-BASE |
| MALL-PKG-024 | Loading dock bumper | 1.0×0.8×1.5 | PBR concrete/metal | L0/L1/L2 | Static | P2 | Primitives+Bevel | Q-BASE |
| MALL-PKG-025 | Bicycle parking rack | 1.8×0.7×1.2 | PBR concrete/metal | L0/L1/L2 | Static | P2 | Extrude+Array | Q-BASE |

### ACT — Interactive Objects (25)

| ID | Model | Size W×D×H (m) | Material | LOD | Interaction | Priority | Blender method | GLB QA |
|---|---|---|---|---|---|---|---|---|
| MALL-ACT-001 | Inspectable product stand | 1.2×0.8×0.75 | PBR plastic/metal | L0/L1/L2 | Inspect+Use | P1 | Primitives+Boolean | Q-INT |
| MALL-ACT-002 | Pickup product proxy | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Inspect+Use | P1 | Primitives+Boolean | Q-INT |
| MALL-ACT-003 | Interactive checkout terminal | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Inspect+Use | P1 | Primitives+Boolean | Q-INT |
| MALL-ACT-004 | Interactive door handle | 3.0×0.25×3.0 | PBR plastic/metal | L0/L1/L2 | Inspect+Use | P1 | Primitives+Boolean | Q-INT |
| MALL-ACT-005 | Interactive seating anchor | 1.2×0.65×0.85 | PBR plastic/metal | L0/L1/L2 | Inspect+Use | P1 | Primitives+Boolean | Q-INT |
| MALL-ACT-006 | Interactive elevator button | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Inspect+Use | P1 | Primitives+Boolean | Q-INT |
| MALL-ACT-007 | Interactive escalator trigger | 5.0×1.5×3.2 | PBR plastic/metal | L0/L1/L2 | Inspect+Use | P1 | Primitives+Boolean | Q-INT |
| MALL-ACT-008 | Interactive kiosk touchscreen | 1.8×0.7×1.2 | PBR metal/glass | L0/L1/L2 | Inspect+Use | P1 | Primitives+Boolean | Q-INT |
| MALL-ACT-009 | Interactive vending machine | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Inspect+Use | P1 | Primitives+Boolean | Q-INT |
| MALL-ACT-010 | Interactive ATM screen | 0.8×0.12×0.6 | PBR metal/glass | L0/L1/L2 | Inspect+Use | P1 | Primitives+Boolean | Q-INT |
| MALL-ACT-011 | Interactive shopping basket | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Inspect+Use | P1 | Primitives+Boolean | Q-INT |
| MALL-ACT-012 | Interactive shopping cart | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Inspect+Use | P1 | Primitives+Boolean | Q-INT |
| MALL-ACT-013 | Interactive fitting mirror | 1.0×0.8×1.5 | PBR metal/glass | L0/L1/L2 | Inspect+Use | P1 | Primitives+Boolean | Q-INT |
| MALL-ACT-014 | Interactive photo booth | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Inspect+Use | P1 | Primitives+Boolean | Q-INT |
| MALL-ACT-015 | Interactive prize machine | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Inspect+Use | P1 | Primitives+Boolean | Q-INT |
| MALL-ACT-016 | Interactive locker door | 3.0×0.25×3.0 | PBR plastic/metal | L0/L1/L2 | Inspect+Use | P1 | Primitives+Boolean | Q-INT |
| MALL-ACT-017 | Interactive parcel collection point | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Inspect+Use | P1 | Primitives+Boolean | Q-INT |
| MALL-ACT-018 | Interactive QR sign | 0.8×0.12×0.6 | PBR plastic/metal | L0/L1/L2 | Inspect+Use | P1 | Primitives+Boolean | Q-INT |
| MALL-ACT-019 | Interactive digital menu | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Inspect+Use | P1 | Primitives+Boolean | Q-INT |
| MALL-ACT-020 | Interactive information counter | 1.8×0.7×1.2 | PBR plastic/metal | L0/L1/L2 | Inspect+Use | P1 | Primitives+Boolean | Q-INT |
| MALL-ACT-021 | Interactive store bell | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Inspect+Use | P1 | Primitives+Boolean | Q-INT |
| MALL-ACT-022 | Interactive ticket dispenser | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Inspect+Use | P1 | Primitives+Boolean | Q-INT |
| MALL-ACT-023 | Interactive water dispenser | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Inspect+Use | P1 | Primitives+Boolean | Q-INT |
| MALL-ACT-024 | Interactive light switch | 0.8×0.12×0.6 | PBR plastic/metal | L0/L1/L2 | Inspect+Use | P1 | Primitives+Boolean | Q-INT |
| MALL-ACT-025 | Interactive exhibition pedestal | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Inspect+Use | P1 | Primitives+Boolean | Q-INT |

### LOC — Singapore & Malaysia Local (10)

| ID | Model | Size W×D×H (m) | Material | LOD | Interaction | Priority | Blender method | GLB QA |
|---|---|---|---|---|---|---|---|---|
| MALL-LOC-001 | Singapore hawker stall fascia | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-UV |
| MALL-LOC-002 | Singapore kopi stall counter | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-UV |
| MALL-LOC-003 | Singapore MRT-style wayfinding panel | 2.0×0.15×2.8 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-UV |
| MALL-LOC-004 | Singapore HDB void deck bench | 1.2×0.65×0.85 | PBR painted/metal | L0/L1/L2 | Sit | P1 | Primitives+Bevel | Q-UV |
| MALL-LOC-005 | Singapore mall directory bilingual | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P1 | Primitives+Bevel | Q-UV |
| MALL-LOC-006 | Malaysia kopitiam counter | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P2 | Primitives+Bevel | Q-UV |
| MALL-LOC-007 | Malaysia shoplot five-foot-way arch | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P2 | Primitives+Bevel | Q-UV |
| MALL-LOC-008 | Malaysia pasar malam stall | 1.0×0.8×1.5 | PBR painted/metal | L0/L1/L2 | Inspect | P2 | Primitives+Bevel | Q-UV |
| MALL-LOC-009 | Malaysia mamak restaurant counter | 1.8×0.7×1.2 | PBR painted/metal | L0/L1/L2 | Inspect | P2 | Primitives+Bevel | Q-UV |
| MALL-LOC-010 | Malaysia bilingual retail sign | 0.8×0.12×0.6 | PBR painted/metal | L0/L1/L2 | Inspect | P2 | Primitives+Bevel | Q-UV |

### SAF — Safety & Maintenance (20)

| ID | Model | Size W×D×H (m) | Material | LOD | Interaction | Priority | Blender method | GLB QA |
|---|---|---|---|---|---|---|---|---|
| MALL-SAF-001 | Fire extinguisher | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P1 | Primitives+Boolean | Q-BASE |
| MALL-SAF-002 | Fire hose reel cabinet | 1.8×0.7×1.2 | PBR plastic/metal | L0/L1/L2 | Static | P1 | Primitives+Boolean | Q-BASE |
| MALL-SAF-003 | Fire alarm call point | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P1 | Primitives+Boolean | Q-BASE |
| MALL-SAF-004 | Smoke detector | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P1 | Primitives+Boolean | Q-BASE |
| MALL-SAF-005 | Sprinkler head | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P1 | Primitives+Boolean | Q-BASE |
| MALL-SAF-006 | Fire exit push bar | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P1 | Primitives+Boolean | Q-BASE |
| MALL-SAF-007 | Emergency exit route marker | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P1 | Primitives+Boolean | Q-BASE |
| MALL-SAF-008 | First aid cabinet | 1.8×0.7×1.2 | PBR plastic/metal | L0/L1/L2 | Static | P1 | Primitives+Boolean | Q-BASE |
| MALL-SAF-009 | AED wall cabinet | 2.0×0.15×2.8 | PBR plastic/metal | L0/L1/L2 | Static | P1 | Primitives+Boolean | Q-BASE |
| MALL-SAF-010 | CCTV dome camera | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P1 | Primitives+Boolean | Q-BASE |
| MALL-SAF-011 | CCTV bullet camera | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P1 | Primitives+Boolean | Q-BASE |
| MALL-SAF-012 | Security patrol desk | 1.8×0.7×1.2 | PBR plastic/metal | L0/L1/L2 | Static | P1 | Primitives+Boolean | Q-BASE |
| MALL-SAF-013 | Security gate | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P2 | Primitives+Boolean | Q-BASE |
| MALL-SAF-014 | Metal detector arch | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P2 | Primitives+Boolean | Q-BASE |
| MALL-SAF-015 | Maintenance trolley | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P2 | Primitives+Boolean | Q-BASE |
| MALL-SAF-016 | Cleaning mop bucket | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P2 | Primitives+Boolean | Q-BASE |
| MALL-SAF-017 | Janitor cart | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P2 | Primitives+Boolean | Q-BASE |
| MALL-SAF-018 | Floor scrubber machine | 2.0×2.0×0.1 | PBR plastic/metal | L0/L1/L2 | Static | P2 | Extrude+Array | Q-BASE |
| MALL-SAF-019 | Electrical distribution cabinet | 1.8×0.7×1.2 | PBR plastic/metal | L0/L1/L2 | Static | P2 | Primitives+Boolean | Q-BASE |
| MALL-SAF-020 | Maintenance barricade | 1.0×0.8×1.5 | PBR plastic/metal | L0/L1/L2 | Static | P2 | Primitives+Boolean | Q-BASE |

## Delivery gates and batches

1. **Gate 0 — Design:** asset ID, dimensions, references, licensing, collision/interaction metadata approved.
2. **Gate 1 — Blender:** source saved; naming, origin, normals, UV, materials, topology and budget checked.
3. **Gate 2 — Export:** GLB exported and reimported into clean scene; transforms, textures and animations checked.
4. **Gate 3 — Runtime:** Three.js desktop and mobile smoke tests, interaction and collision checks, screenshot evidence.
5. **Gate 4 — Release:** QA evidence attached; only passing assets marked READY; failures stay BLOCKED; never claim tests ran when they did not.

**Batching:** target 50 models per PR (8 PRs), with an explicit manifest of included IDs; do not merge or deploy without required checks and permission. Start with P0 structural, shopfront, fixture and public-space assets.

## Suggested directory

```text
assets/shopping-mall/MALL-STR-001/
  source/MALL-STR-001.blend
  export/MALL-STR-001.glb
  previews/front.png
  previews/three-quarter.png
  asset.json
  qa/report.md
```

## Asset metadata example

```json
{
  "id": "MALL-STR-001",
  "name": "Straight floor module",
  "dimensions_m": [2.0, 2.0, 0.1],
  "priority": "P0",
  "status": "PLANNED",
  "interaction": "Static",
  "qa_profile": "Q-BASE",
  "qa_status": "NOT_RUN",
  "license": "TBD"
}
```
