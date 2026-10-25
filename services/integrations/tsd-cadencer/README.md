# tsd-cadencer — planned service boundary

Status: NOT_IMPLEMENTED. Navigator Web/PWA uses a versioned delivery envelope through this service/bridge; the Android counterpart remains in `android/integrations/tsd-cadencer`. Transport discovery and offline connectivity must be demonstrated, not inferred from browser capabilities.

Require idempotency, exact revision/hash binding, authorized sender and actual receiver ACK. QUEUED or SENT never means ACKED. No change to an active LIVE package.

Cadencer remains an independent application/repository; this gateway does not host or fork it. Authentication, schema negotiation, durable outbox retries and exact ACK replay remain unimplemented.
