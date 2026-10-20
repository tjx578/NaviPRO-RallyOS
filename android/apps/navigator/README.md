# Navigator Workspace — Page 1, 2, 3

**Status: DESIGN_ONLY; no Gradle app built.** Shared 16:9 landscape shell, official NaviPRO brand; 1/3, 2/3, 3/3 swipe indicator. Intercept map pan/zoom/drag so these gestures never switch pages.

1. Page 1 Data Rally: intake, human-checked OCR, start time/list, governed schedules, numeric speed, external TSD delivery/ACK.
2. Page 2 Offline Map & Route Editor: selected-sub route only, locked original steps, candidate/draft review, validated human confirmation, pack/send ACK.
3. Page 3 NaviPRO Rally Agent: tools for read/search/plan/propose only; no direct Page 2 mutation or LIVE operation.

Canonical contract `../../../contracts/ui/cockpit-surface-registry.yaml`; per-page modules under `../../features/`.
