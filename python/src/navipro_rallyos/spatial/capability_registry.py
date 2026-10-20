from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import yaml


@dataclass(frozen=True)
class SpatialCapability:
    id: str
    group: str
    capability: str
    priority: str
    parity_target: str
    allowed_modes: tuple[str, ...]
    navipro_target: str
    authority_class: str
    implementation_status: str
    notes: str = ""


class CapabilityRegistry:
    """Read-only view over the versioned spatial capability registry.

    The registry is an engineering contract, not evidence that a capability has
    passed runtime or device acceptance tests.
    """

    def __init__(self, registry_path: Path | None = None) -> None:
        if registry_path is None:
            repo = Path(__file__).resolve().parents[4]
            registry_path = repo / "contracts" / "spatial" / "kepler-capability-registry.yaml"
        self.registry_path = Path(registry_path)
        payload = yaml.safe_load(self.registry_path.read_text(encoding="utf-8"))
        self.registry_id = payload["registry_id"]
        self.version = payload["version"]
        self.status = payload["status"]
        self._caps = tuple(
            SpatialCapability(
                id=item["id"],
                group=item["group"],
                capability=item["capability"],
                priority=item["priority"],
                parity_target=item["parity_target"],
                allowed_modes=tuple(item["allowed_modes"]),
                navipro_target=item["navipro_target"],
                authority_class=item["authority_class"],
                implementation_status=item["implementation_status"],
                notes=item.get("notes", ""),
            )
            for item in payload["capabilities"]
        )

    def list(self, *, mode: str | None = None, priority: str | None = None) -> tuple[SpatialCapability, ...]:
        caps: Iterable[SpatialCapability] = self._caps
        if mode is not None:
            caps = (cap for cap in caps if mode in cap.allowed_modes)
        if priority is not None:
            caps = (cap for cap in caps if cap.priority == priority)
        return tuple(caps)

    def get(self, capability_id: str) -> SpatialCapability:
        for cap in self._caps:
            if cap.id == capability_id:
                return cap
        raise KeyError(capability_id)

    def live_exposure(self) -> tuple[SpatialCapability, ...]:
        return self.list(mode="LIVE")
