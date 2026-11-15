# Blender knowledge verification

Edition 1.1.0, reviewed 2026-11-15, Asia/Singapore. This directory contains reproducible native checks and the receipts for the explicitly requested `blender` knowledge-base update.

## Native calibration

Run from the repository with its Node dependencies installed and Blender available:

```sh
node docs/blender/verification/check-probe.mjs
```

Set `BLENDER_BIN` when the executable is elsewhere. The checker uses a separate background Blender process and temporary files. It does not reset the connected interactive scene. [PASS results](probe-results.json) cover context polling, mesh sharing, axes, unit-scale behavior, UV vertex splitting, scalar material transfer, one Action/slot clip and CLI failure propagation. Four emitted GLBs had zero validator errors/warnings; one retained an informational unused-UV message.

[The retained FAIL receipt](animation-time-assumption.json) records the original incorrect animation timing assumption. [Calibration](../calibration.md) explains the correction and the precise coverage. [Read-only API inspection](native-api.json) is presence evidence, not an extension operation test.

## KB synchronization

```sh
node docs/blender/verification/prepare-kb.mjs
```

This only prepares [kb-plan.json](kb-plan.json); it does not send remote writes. Summaries come from the owning chapter markers. The dated extension catalog and calibration note supply two longer chunked documents. Review current KB identity, item IDs, visibility and fresh metadata before using the plan. Do not replay a confirmed document ingestion as a new write.

[kb-sync.json](kb-sync.json) records ten existing item updates, two new document parents and six created chunks. The observed KB count was 18. All 12 canonical records were read back with exact content, source attribution, category and `user` visibility checks. Existing item titles and IDs were preserved. Metadata object comparison ignores JSON key ordering.

The read API resolves a chunk UUID to its complete parent. Consequently, parent content and chunk totals were verified, while individual child bodies were not independently exposed. Do not describe those reads as 18 independent body checks.

## Retrieval grounding and limits

[retrieval-qa.json](retrieval-qa.json) retains eight supported questions, one deliberately unsupported certificate question, automatic verdicts, full-source grounding checks and feedback receipts. The supported queries include Chinese questions about unit scaling and validator scope. All eight retrieved the expected source containing the relevant facts. The animation time midpoint of 0.6 seconds is a calculation from documented 0.1 and 1.1 second endpoints.

Initial compact answers marked their content incomplete and optional reranking reported busy/timeouts. Three representative queries were repeated with full output and optional reranking disabled; those calls had no degraded components. No confidence threshold was lowered. Exact full source reads, rather than embedding scores, supplied the evidence checks.

Automatic decisions remained `verify`. The unsupported question retrieved a topical extension document with `no_answer=false`, although it contained no requested certificate or issuing authority. This proves neither a certificate nor a reliable explicit no-answer classifier. The safe operational rule is to inspect the cited source and withhold unsupported claims. The KB content update is verified; fully automatic answer acceptance is not.

No extension installation, character deformation test, textured browser rendering, physical-device run, FPS benchmark, Skill registration, commit or push is claimed by this directory.
