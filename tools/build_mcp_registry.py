#!/usr/bin/env python3
from pathlib import Path
import argparse
import yaml, sys

parser = argparse.ArgumentParser()
parser.add_argument('--check', action='store_true', help='Fail on generated drift without writing files')
args = parser.parse_args()

repo = Path(__file__).resolve().parents[1]
spec_path = repo / "contracts/openapi/navipro-rallyos.openapi.yaml"
out_path = repo / "services/mcp/generated-tool-registry.yaml"
spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))

tools = []
blocked = []
for path, item in spec.get("paths", {}).items():
    for method, op in item.items():
        if method.lower() not in {"get","post","put","patch","delete"} or not isinstance(op, dict):
            continue
        meta = op.get("x-navipro-mcp", {})
        rec = {
            "operation_id": op.get("operationId"),
            "method": method.upper(),
            "path": path,
            "modes": op.get("x-navipro-mode", []),
            "authority": op.get("x-navipro-authority"),
            "side_effect": op.get("x-navipro-side-effect"),
        }
        if meta.get("enabled"):
            rec["tool"] = meta.get("tool")
            tools.append(rec)
        else:
            blocked.append(rec)

payload = {"generated_from": str(spec_path.relative_to(repo)), "tools": tools, "blocked_operations": blocked}
rendered = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
if args.check:
    if not out_path.is_file() or out_path.read_text(encoding='utf-8') != rendered:
        sys.exit('MCP registry drift: run python tools/build_mcp_registry.py and review the diff')
else:
    out_path.write_text(rendered, encoding="utf-8")
print(f"generated {len(tools)} MCP tools; blocked {len(blocked)} operations")
