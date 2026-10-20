# TSD Cadencer external interface — planned

Navigator Page 1 serializes timing plans with version, source hash, sub ordering, start, exact mm/ms and idempotency key; delivery states: NOT_READY / READY / SENDING / ACKED / QUEUED_OFFLINE / REJECTED. An actual external ACK is required. Driver may read TSD/odometer feed but never sends or mutates its plan. **External TSD app is not vendored or built here; adapter NOT_IMPLEMENTED.**
