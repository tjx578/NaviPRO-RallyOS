# Driver Runtime — Driver 1 Overview / Driver 2 Driving

**Status: DESIGN_ONLY; no Gradle app built.** Two modes of **one** read-only Driver application, never Navigator pages 4/5.

- Driver 1 Overview: selected sub, full confirmed course, start/finish, cue list, POIs and read-only TSD panel.
- Driver 2 Driving: course-up look-ahead, vehicle in lower third, next maneuver/cue, nearby offline OSM buildings at high zoom, deterministic off-route freeze, read-only TSD panel.

Both consume the **same signed confirmed NaviPack**. Forbidden: edit route, generative agent, route confirmation, send links/packs, remote routing in LIVE. The visual mockup's “Kirim Link Driver” button is **intentionally excluded** because it contradicts spec v3.0 §7.1/§16.4; sending belongs to Navigator Page 2.

Refer to `../../../contracts/ui/cockpit-surface-registry.yaml` and `../../features/driver-runtime/`.
