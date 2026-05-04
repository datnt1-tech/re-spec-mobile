"""mcp_server.py — MCP server exposing the per-project spec graph.

Any Claude Code session whose CWD is inside a project with `.spec-profile.yml`
gets 8 tools (auto-rebuilds graph if stale before answering):

    spec_show(anchor)                node detail + in/out edges
    spec_list(kind, feature?)        list nodes of a type
    spec_feature(name)               summary of a feature
    spec_reuses(key?)                component reuse groups
    spec_path(src, dst, depth?)      BFS shortest nav path
    spec_acceptance(feature)         acceptance criteria of a feature
    spec_search(query, limit?)       substring match on anchor+label
    spec_stats()                     graph totals

Protocol: JSON-RPC 2.0 over stdio (MCP spec 2024-11-05). Stdlib only — no
`pip install mcp` needed.
"""
from __future__ import annotations

import json
import sys
from typing import Any

from re_spec_mobile import spec_query
from re_spec_mobile.profile_loader import Profile, load_profile

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "spec-graph"
SERVER_VERSION = "1.0.0"

_graph_cache: dict[str, Any] = {"nodes": None, "edges": None, "loaded_mtime": 0.0}
_profile: Profile | None = None


def _resolve_profile() -> Profile:
    """Cache the profile across MCP requests; load_profile honors $SPEC_PROFILE."""
    global _profile
    if _profile is None:
        _profile = load_profile()
    return _profile


def _latest_spec_mtime(p: Profile) -> float:
    latest = 0.0
    if not p.spec_root.exists():
        return latest
    skip_parts = {p.graph_root.name, p.contracts_root.name, "viz"}
    for path in p.spec_root.rglob("*.md"):
        if any(part in skip_parts for part in path.parts):
            continue
        latest = max(latest, path.stat().st_mtime)
    return latest


def _graph_mtime(p: Profile) -> float:
    nodes_file = p.graph_root / "nodes.json"
    if not nodes_file.exists():
        return 0.0
    return nodes_file.stat().st_mtime


def _rebuild_graph(p: Profile) -> None:
    """Rebuild graph in-process (no subprocess needed when packaged)."""
    from re_spec_mobile import build_graph
    paths = build_graph.discover_specs(p)
    docs = [fm for path in paths if (fm := build_graph.load_frontmatter(path, p.project_root))]
    graph = build_graph.Graph()
    build_graph.build(graph, docs)
    graph.validate_refs()
    build_graph.emit(graph, p)


def _ensure_fresh_graph() -> None:
    p = _resolve_profile()
    if _graph_mtime(p) < _latest_spec_mtime(p):
        _rebuild_graph(p)
    if _graph_cache["loaded_mtime"] < _graph_mtime(p):
        nodes, edges, _ = spec_query.load_graph(p)
        _graph_cache["nodes"] = nodes
        _graph_cache["edges"] = edges
        _graph_cache["loaded_mtime"] = _graph_mtime(p)


def _tool_show(args: dict) -> dict:
    _ensure_fresh_graph()
    return spec_query.cmd_show(_graph_cache["nodes"], _graph_cache["edges"], args["anchor"])


def _tool_list(args: dict) -> list:
    _ensure_fresh_graph()
    return spec_query.cmd_list(
        _graph_cache["nodes"], args["kind"], args.get("feature"), args.get("limit", 500),
    )


def _tool_feature(args: dict) -> dict:
    _ensure_fresh_graph()
    return spec_query.cmd_feature(_graph_cache["nodes"], _graph_cache["edges"], args["name"])


def _tool_reuses(args: dict) -> dict:
    _ensure_fresh_graph()
    return spec_query.cmd_reuses(_graph_cache["nodes"], _graph_cache["edges"], args.get("key"))


def _tool_path(args: dict) -> dict:
    _ensure_fresh_graph()
    path = spec_query.cmd_path(
        _graph_cache["edges"], args["src"], args["dst"], args.get("depth", 8),
    )
    if path is None:
        return {"path": None, "reason": f"no path within depth {args.get('depth', 8)}"}
    return {"path": path, "length": len(path) - 1}


def _tool_acceptance(args: dict) -> list:
    _ensure_fresh_graph()
    return spec_query.cmd_acceptance(_graph_cache["nodes"], args["feature"])


def _tool_search(args: dict) -> list:
    _ensure_fresh_graph()
    return spec_query.cmd_search(_graph_cache["nodes"], args["query"], args.get("limit", 50))


def _tool_stats(args: dict) -> dict:
    _ensure_fresh_graph()
    return spec_query.cmd_stats(_graph_cache["nodes"], _graph_cache["edges"])


TOOLS: list[dict] = [
    {
        "name": "spec_show",
        "description": "Return a spec node's detail + outgoing/incoming edges. `anchor` format: `<feature>/<type>/<name>`.",
        "inputSchema": {"type": "object", "properties": {"anchor": {"type": "string"}}, "required": ["anchor"]},
        "_impl": _tool_show,
    },
    {
        "name": "spec_list",
        "description": "List nodes of a kind. `kind` ∈ {screen, block, component, api, data_model, criterion, invariant, question, state, feature, layer}. Optional `feature` filter.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "kind": {"type": "string"},
                "feature": {"type": "string"},
                "limit": {"type": "integer", "default": 500},
            },
            "required": ["kind"],
        },
        "_impl": _tool_list,
    },
    {
        "name": "spec_feature",
        "description": "Summary of one feature: total node count + counts by type + grouped children.",
        "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]},
        "_impl": _tool_feature,
    },
    {
        "name": "spec_reuses",
        "description": "Component reuse groups — components sharing a `reuse_key` + all `reuses_component` edges. Pass `key` to filter to one group.",
        "inputSchema": {"type": "object", "properties": {"key": {"type": "string"}}},
        "_impl": _tool_reuses,
    },
    {
        "name": "spec_path",
        "description": "BFS shortest path between two screen anchors via `navigates_to` edges.",
        "inputSchema": {
            "type": "object",
            "properties": {"src": {"type": "string"}, "dst": {"type": "string"}, "depth": {"type": "integer", "default": 8}},
            "required": ["src", "dst"],
        },
        "_impl": _tool_path,
    },
    {
        "name": "spec_acceptance",
        "description": "All acceptance criteria of a feature (nodes of type `criterion`).",
        "inputSchema": {"type": "object", "properties": {"feature": {"type": "string"}}, "required": ["feature"]},
        "_impl": _tool_acceptance,
    },
    {
        "name": "spec_search",
        "description": "Substring match on node `anchor` + `label`. Use when you don't know the exact anchor.",
        "inputSchema": {
            "type": "object",
            "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "default": 50}},
            "required": ["query"],
        },
        "_impl": _tool_search,
    },
    {
        "name": "spec_stats",
        "description": "Graph totals: node count, edge count, per-type counts.",
        "inputSchema": {"type": "object", "properties": {}},
        "_impl": _tool_stats,
    },
]

_TOOL_MAP = {t["name"]: t for t in TOOLS}


def _response(req_id: Any, result: Any = None, error: dict | None = None) -> dict:
    msg: dict = {"jsonrpc": "2.0", "id": req_id}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    return msg


def _error(code: int, message: str, data: Any = None) -> dict:
    e: dict = {"code": code, "message": message}
    if data is not None:
        e["data"] = data
    return e


def handle_request(req: dict) -> dict | None:
    method = req.get("method")
    req_id = req.get("id")
    params = req.get("params") or {}

    if method == "initialize":
        return _response(req_id, {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
        })

    if method == "notifications/initialized":
        return None

    if method == "tools/list":
        public = [{k: v for k, v in t.items() if not k.startswith("_")} for t in TOOLS]
        return _response(req_id, {"tools": public})

    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        tool = _TOOL_MAP.get(name)
        if not tool:
            return _response(req_id, error=_error(-32601, f"unknown tool: {name}"))
        try:
            result = tool["_impl"](args)
        except SystemExit as e:
            return _response(req_id, result={"content": [{"type": "text", "text": f"error: {e}"}], "isError": True})
        except Exception as e:
            return _response(req_id, result={
                "content": [{"type": "text", "text": f"tool crashed: {type(e).__name__}: {e}"}],
                "isError": True,
            })
        return _response(req_id, {
            "content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False, default=str)}],
        })

    if method in ("ping",):
        return _response(req_id, {})

    if req_id is not None:
        return _response(req_id, error=_error(-32601, f"method not found: {method}"))
    return None


def serve() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError as e:
            sys.stderr.write(f"json parse error: {e}\n")
            continue
        resp = handle_request(req)
        if resp is None:
            continue
        sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    serve()
