# NaviPRO Field Survey — Android client contract scaffold

**Status: DESIGN/SCAFFOLD ONLY. Not an APK; Gradle build is not present.**

StreetComplete-inspired ergonomics, implemented clean-room within NaviPRO Kotlin/Compose architecture. No GPL code is copied. Map UI should reuse NaviPRO offline map stack, not import StreetComplete source directly without a full GPL compatibility assessment.

## Screen composition

- **PREP Map:** confirmed-route reference overlay (read only), open quest markers, thematic road overlays, downloaded survey area.
- **Task card:** one specific question about one OSM element, with `osm_element_id`, `osm_version` and rationale.
- **Field observation:** only from human surveyor; GPS accuracy/time, optional photo hash, optional note, explicit answer. GPS and photo permissions optional; manual capture can't be forged as sensor observation.
- **Local outbox:** `PENDING_SYNC`, `STAGED_REVIEW`, `CONFLICT`, `HOLD`. Does not depend on internet while capturing.
- **Sync:** authenticated NaviPRO *staging* API only. Not OpenStreetMap changeset upload.
- **Review UI:** navigator sees source/tag version, evidence/uncertainties; verification and route confirmation are separate human workflows.

## Boundary

Do not allow the survey screen in LIVE navigation mode. Surveyors must stop in a safe publicly accessible place to record data, never interact with survey forms while driving. Do not request entry to private or restricted locations.

## Shared contract

`contracts/jsonschema/field-survey-observation.schema.json` · `contracts/openapi/navipro-rallyos.openapi.yaml` · `governance/streetcomplete-field-survey-policy.yaml`.

## Build path

Create Kotlin Multiplatform-independent Android module `apps/field-survey-android`, use Compose, local encrypted SQLite/Room outbox (the current Python SQLite prototype is for domain testing only), and DI abstractions for map provider, GNSS capture, evidence attachment store, staging transport. Validate role auth, version conflict, idempotency, privacy and complete offline mode before releasing.
