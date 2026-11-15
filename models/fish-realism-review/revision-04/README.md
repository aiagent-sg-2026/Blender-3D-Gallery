# Maskray realism review 04

Scope: stingray only. The accepted revision-03 Barramundi and Betta files and all 60 production GLBs are protected by `preserved-assets.json`. No production, gallery or deployment change is authorized by this local review.

## References inspected

The photographs were visually inspected in a real browser. They serve as anatomical and material references only; no photograph is copied into a texture or distributed with the model.

- [National Museum of Nature and Science, Fishes of Andaman Sea — Neotrygon kuhlii](https://www.kahaku.go.jp/research/db/zoology/Fishes_of_Andaman_Sea/contents/dasyatidae/04.html): dorsal shape, orbital mounds, mask pigment and spiracles; photographs credited on that page to Mark Strickland and Seishi Kimura.
- [Scientific Shot of a Kuhls Stingray's eye](https://commons.wikimedia.org/wiki/File:Scientific_Shot_of_a_Kuhls_Stingray%27s_eye.jpg): U-shaped pupil, iris operculum, exposed eye within a thick skin fold. Sand on the photographed animal is environmental material, not anatomical skin grain.
- [Blue-spotted Stingray photograph 8465011759](https://commons.wikimedia.org/wiki/File:Blue-spotted_Stingray_(Neotrygon_kuhlii)_(8465011759).jpg): fine skin granularity, unequal blue spots, joined orbital tissue and spiracle, thin raised pectoral edge and a low tapered tail. This source uses a historical identification; this asset is a visual maskray study, not a verified taxonomic specimen.
- [Blevins and Lauder (2012), Rajiform locomotion](https://pubmed.ncbi.nlm.nih.gov/22693031/): three-dimensional pectoral-surface kinematics. The animated wave is an artistic approximation informed by research, not a measured biological simulation.

## Cause and revision

Previous drafts passed basic animation/file checks while still failing the user's visual review. Their tiny spherical eyes, uniform diffuse surface and three spanwise wing hinges were insufficient anatomical representations. The old normal-map helper differentiated height in pixel coordinates; at the selected amplitudes, the resulting normal was almost flat. Increasing geometric density alone could not address these issues.

This isolated revision rebuilds:

- The continuous rhomboid disc and orbital tissue, with shallow spiracle bowls.
- An exposed iris cap with original radial pigment and a U-shaped pupil/operculum texture; the iris surface follows the continuous orbital mound, eliminating the detached collar seam.
- Original pigment, pore, normal and roughness maps. Normal derivatives use the physical UV footprint to retain visible fine dermal relief without invented fish scales.
- Pectoral motion as sine and cosine components on each side, exported as paired nonnegative morph targets. Phase varies along the front-to-back axis, amplitude increases away from the trunk, and the front/rear margins taper. This replaces a broad rigid flap with a continuous traveling wave. Paired targets preserve the negative half-cycle in importers that clamp a target to its default zero minimum. The central head remains quiet and the tail has a smaller passive lag. Each quadrature is explicitly created from the unmixed Basis shape; inheriting the current pose would contaminate the independent wave components. Verification checks both the expected front/rear phase delay and the expected probe amplitude.

## Acceptance and limits

Reopen the source and exported GLB. Check actual deformation, loop closure, finite geometry, the wave's forward-to-rear phase progression, source-to-export probe agreement and the preservation manifest. Inspect both an overall view and an eye/skin close-up. File validity and moving vertices do not certify realism; owner visual acceptance remains pending. Do not replace the gallery or the accepted fish without that review.

The prevention lesson stays project-local: before another realism claim, inspect the relevant anatomy at close range, compare the same structures to photographs, and check the deformation pattern rather than accepting any nonzero motion as natural swimming. No global Skill is changed because this is a project art workflow and artistic acceptance is still pending.

## Reproduction

Run `create_stingray.py` in Blender 5.1.2 background mode, followed by `finish_stingray.py` and `verify_stingray.py`. The scripts write only inside this revision. Textures and geometry are original project work; reusable utility functions are imported from preserved revision 02.

## Verified result

The final packed source and exported GLB agree exactly at the sampled front/rear probes across the complete cycle. The rear probe peak follows the front by 26 frames (the analytic target is approximately 27 frames); the head probe stays stationary and loop endpoints match. The Khronos validator reports zero errors and zero warnings, with informational notes about unused UV/tangent attributes and the iris texture dimensions. All 70 preservation hashes match. The final review GIF contains 48 frames over four seconds. Artistic acceptance remains pending.

`render_detail.py` recreates the close-up from the final saved source. `portable_morphs.py` owns the nonnegative target conversion and independent quadrature reconstruction used by the export workflow. Temporary frame sequences and intermediate scene backups are removed after GIF validation.
