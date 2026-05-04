"""re-spec-mobile — reverse-engineer mobile apps into 3-layer markdown specs.

Public API:
    from re_spec_mobile import (
        Profile, load_profile,           # profile_loader
        Scope, load_scope,                # scope_loader
        NavGraph, load as load_nav_graph, screen_hash,  # nav_graph
        paths,                            # access bundled data files
    )

Console entry points (after `pip install`):
    re-spec-init             — bootstrap a new project
    re-spec-profile          — show/validate .spec-profile.yml
    re-spec-scope            — show/check scope contract
    re-spec-capture          — capture one screen
    re-spec-coverage-check   — list uncovered clickables
    re-spec-coverage-report  — generate Gate 2 audit
    re-spec-render-nav       — Mermaid nav graph
    re-spec-observations     — boilerplate observations.md
    re-spec-build-graph      — rebuild spec graph
    re-spec-validate         — validate spec frontmatter
    re-spec-query            — query spec graph
    re-spec-mcp-server       — JSON-RPC MCP server
    re-spec-paths            — show bundled data file paths
"""

__version__ = "1.0.0"

from re_spec_mobile.profile_loader import Profile, load_profile, parse_profile, find_profile  # noqa: F401
from re_spec_mobile.scope_loader import Scope, Cluster, ScopeQuestion, load_scope, parse_scope  # noqa: F401
from re_spec_mobile.nav_graph import NavGraph, load as load_nav_graph, screen_hash  # noqa: F401
from re_spec_mobile import paths  # noqa: F401

__all__ = [
    "__version__",
    "Profile",
    "load_profile",
    "parse_profile",
    "find_profile",
    "Scope",
    "Cluster",
    "ScopeQuestion",
    "load_scope",
    "parse_scope",
    "NavGraph",
    "load_nav_graph",
    "screen_hash",
    "paths",
]
