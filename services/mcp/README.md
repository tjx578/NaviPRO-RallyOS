# NaviPRO MCP Gateway

MCP is generated from `contracts/openapi/navipro-rallyos.openapi.yaml`.

Rules:
- Only operations with `x-navipro-mcp.enabled: true` become agent tools.
- PREP/REVIEW tools may read, calculate, compare, search, and create proposal/staging records.
- Authority mutations (`route.confirm`, location decisions), release publication, and external delivery are not agent tools.
- Driver LIVE runtime does not depend on the MCP server.

Generate the tool registry:

```bash
python tools/build_mcp_registry.py
```
