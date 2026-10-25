# device-transfer — planned service boundary

Status: NOT_IMPLEMENTED. Navigator Web/PWA uses a versioned delivery envelope through this service/bridge; the Android counterpart remains in `android/integrations/device-transfer`. Transport discovery and offline connectivity must be demonstrated, not inferred from browser capabilities.

Require idempotency, exact revision/hash binding, authorized sender and actual receiver ACK. QUEUED or SENT never means ACKED. No change to an active LIVE package.
