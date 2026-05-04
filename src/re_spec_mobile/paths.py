"""paths.py — locate bundled data files (templates, canonical samples, shell scripts).

Uses `importlib.resources` so it works whether the package is installed via
pip (data inside site-packages or wheel) OR run from source (data in the repo).

Public functions:
    template(name)      → Path to <pkg>/_data/templates/<name>
    canonical(name)     → Path to <pkg>/_data/canonical/<name>
    shell(name)         → Path to <pkg>/_data/_shell/<name>
    data_root()         → Path to <pkg>/_data/

CLI: `re-spec-paths` prints all resolved paths (useful for debugging install).
"""
from __future__ import annotations

import argparse
from importlib import resources
from pathlib import Path


# Modern API: importlib.resources.files() returns a Traversable. For real
# filesystem files we cast to Path. If installed in a zip/wheel without
# extraction, importlib.resources.as_file gives a temporary path.
def _root() -> Path:
    return Path(str(resources.files("re_spec_mobile").joinpath("_data")))


def data_root() -> Path:
    """Directory containing bundled templates/, canonical/, _shell/."""
    return _root()


def template(name: str) -> Path:
    """e.g. template('scope.md.tmpl') → <pkg>/_data/templates/scope.md.tmpl"""
    p = _root() / "templates" / name
    if not p.exists():
        raise FileNotFoundError(f"Bundled template not found: {p}")
    return p


def canonical(name: str) -> Path:
    """e.g. canonical('SPEC_SCHEMA.md') → <pkg>/_data/canonical/SPEC_SCHEMA.md"""
    p = _root() / "canonical" / name
    if not p.exists():
        raise FileNotFoundError(f"Bundled canonical not found: {p}")
    return p


def shell(name: str) -> Path:
    """e.g. shell('setup_portal.sh') → <pkg>/_data/_shell/setup_portal.sh"""
    p = _root() / "_shell" / name
    if not p.exists():
        raise FileNotFoundError(f"Bundled shell script not found: {p}")
    return p


def list_templates() -> list[str]:
    return sorted(p.name for p in (_root() / "templates").iterdir() if p.is_file())


def list_canonical() -> list[str]:
    return sorted(p.name for p in (_root() / "canonical").iterdir() if p.is_file())


def list_shell() -> list[str]:
    return sorted(p.name for p in (_root() / "_shell").iterdir() if p.is_file())


def main() -> int:
    ap = argparse.ArgumentParser(description="Show bundled data file paths.")
    ap.add_argument("--shell", help="resolve a single shell script name (e.g. setup_portal.sh)")
    ap.add_argument("--template", help="resolve a single template name")
    ap.add_argument("--canonical", help="resolve a single canonical sample name")
    args = ap.parse_args()

    if args.shell:
        print(shell(args.shell))
        return 0
    if args.template:
        print(template(args.template))
        return 0
    if args.canonical:
        print(canonical(args.canonical))
        return 0

    print(f"data_root: {data_root()}")
    print(f"\n[templates] ({len(list_templates())})")
    for n in list_templates():
        print(f"  {n}")
    print(f"\n[canonical] ({len(list_canonical())})")
    for n in list_canonical():
        print(f"  {n}")
    print(f"\n[shell] ({len(list_shell())})")
    for n in list_shell():
        print(f"  {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
