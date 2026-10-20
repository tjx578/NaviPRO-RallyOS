#!/usr/bin/env python3
from pathlib import Path
import yaml, sys
repo = Path(__file__).resolve().parents[1]
p = repo / "contracts/openapi/navipro-rallyos.openapi.yaml"
spec = yaml.safe_load(p.read_text(encoding="utf-8"))
assert spec.get("openapi") == "3.1.0"
assert isinstance(spec.get("paths"), dict) and spec["paths"]
ops=[]
missing=[]
for path,item in spec["paths"].items():
    for method,op in item.items():
        if method.lower() not in {"get","post","put","patch","delete"}: continue
        oid=op.get("operationId")
        assert oid, f"missing operationId: {method} {path}"
        ops.append(oid)
        for k in ["x-navipro-mcp","x-navipro-mode","x-navipro-authority","x-navipro-side-effect"]:
            if k not in op: missing.append((oid,k))
assert len(ops)==len(set(ops)), "duplicate operationId"
assert not missing, f"missing NaviPRO metadata: {missing}"
print(f"OpenAPI OK: {len(ops)} operations, {len(spec['components']['schemas'])} schemas")
