# Power-handle native touch fling regression

Baseline de3f6fc5, unchanged test-game-responsive.mjs selected1440x900 failed locally twice (plain and diagnostic trace), matching CI pause events without click. Diagnostic copy adds CDP tracing/observations only, not different inputs, assertions or timeout.

Chromium trace: a native GestureFlingStart at power-handle drag end, followed by3FilterTapSuppression events at Pause. Candidate only adds scoped non-passive cancelable touchstart cancellation on power-handle, with existing AbortSignal. No synthetic clicks, pause handler changes, global cancellation or test weakening.

Candidate: build PASS, original selected1440case PASS; same diagnostic journey PASS with0fling and0suppression; moving-phase Pause nativeclick restored. Trace excerpt retains Chromium names/timestamps; full traces remain /tmp/fitting-game-1440-trace and /tmp/fitting-game-candidate/trace. Capture-observer defaultPrevented may be recorded before target listeners and is not used as final cancellation evidence.

Existing5touch cancellation tests PASS: cancel charge/canvas, pinch/orbit, keyboard/native button once, noncanvas page scroll, canvas listener disposal. Four existing experience cases selected through existing B3G_PULL_CASE PASS: lost capture, duplicate up, second pointer and keyboard charge. Added power-specific scope/lifecycle test PASS: actual native handle tap never shoots, document-bubble observation shows handle cancellation and ordinary button not canceled, label descendant scope, noncancelable events and3unmount/remount abort cleanup.

Desktop Chromium emulation only; no physical-device claim. No remote push or deployment. Original responsive, experience and touch-cancellation tests unchanged.
