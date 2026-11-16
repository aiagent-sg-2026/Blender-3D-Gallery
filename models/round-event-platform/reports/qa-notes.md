# QA notes

- Initial asset validation rejected Blender's default double-sided material export.
  Set backface culling on the three original opaque materials and rebuilt. Final
  GLB passes the same unchanged gate with zero Khronos errors and warnings.
- Initial repository test run: 727/728 passed; the Pomelo STEM test requires its
  collection to remain last. Inserted the new platform immediately before that
  collection, preserving all pre-existing catalog content and tests. The initial
  failure is retained in npm-test-initial.log.gz; final results are in npm-test.log.gz.
- Initial low orthographic previews exposed a finite studio-floor horizon.
  Front/side now use the clean world backdrop. Hero/3q retain the studio floor.
  Studio geometry, lights and cameras are excluded from the delivered GLB.
- System Python had no Pillow; thumbnail conversion uses the pre-existing
  /tmp/pomelo-pillow package with Python 3.14. No dependency manifest changes.
- Independent full generation and native saved-source replay both reproduce GLB
  SHA-256 3576a8fe97009cb32abfc97a5c8538cf9d7964c1840ac4bdd670763cddd858e7.
- Existing build chunk-size advisory is outside this asset-only change.
