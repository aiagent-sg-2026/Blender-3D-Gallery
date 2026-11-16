# GJH Chibi Visitor: design reference

Status: three Unity-built variants now exist as a comparison set in `models/gjh-chibi-visitor/`; exact fidelity to the owner's private character sheet remains unverified.

Source: the owner's "GJH Chibi Visitor, New Design, Modular" character sheet. The sheet image is a private reference and is not embedded here; add it as `docs/assets/gjh-chibi-visitor-sheet.png` only if the owner approves redistribution.

## Character

Original rounded chibi robot mascot for the GJH mall concept, about two heads tall. Decorative concept, not an official GJH spokesperson.

- Palette: white `#F4F2FA`, near-black `#2A2838`, bright purple `#8B5CF6`, light lavender `#D9CCF7`.
- Head: large rounded white helmet; two tall, pointed ear-fins swept slightly back; black glossy face screen with glowing purple happy-arc eyes; round ring headphones with a glowing purple ring on each side.
- Body: soft white hoodie with a purple hood roll and a purple "GJH" mark on the chest; short sleeves with purple panel stripes; black shorts with purple hem; white legs with purple square patches; black rounded mitts and shoes.
- Views on the sheet: front, side, back.

## Modular system (mix and match)

| Module | Variants |
| --- | --- |
| Head (face expression) | happy `^ ^`, sleep `- -`, excited `> <`, heart |
| Ears / antennas | headphone ear-cups, ball antennas, wing fins |
| Outfit (body) | white hoodie, black jacket, plain top |
| Accessories | backpack, belt bag, ID badge |

Example combinations on the sheet: goggles, cap, scarf, cat ears.

## Runtime contract (target)

- glTF 2.0 GLB, native metres, +Y up, front +Z, feet at Y=0, about 1.0 m tall.
- Root node `GJHChibiVisitor` with separate child nodes per module: Head, Face, Expression variants, Ears, Headphones, Outfit, Legs, Hands, Feet.
- Default export shows the happy expression and the white hoodie only.
- No external textures. Emissive purple must survive export.
- Budget: under 15,000 triangles and under 2 MiB (same ceiling as `gjh-mall-visitor`).

## Authoring

Built in Unity (6000.0.85f2) with a deterministic editor script and exported with glTFast; the Unity project lives outside this repository. Reproduction steps, measured triangles and bytes belong in the model folder README once the asset is admitted. Authoring tool differs from the Blender-based collections; this gallery is tool-neutral (see `AGENTS.md`).

## Draft catalog entry

See `models/gjh-chibi-visitor/catalog-entry.draft.json`. It is intentionally not merged into `models/catalog.json` until the GLB, thumbnail and metadata exist and pass `npm run validate:assets`.
