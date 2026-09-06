"""The module tree drawn in `docs/DESIGN.md` must be the tree on disk.

It was not. §12 showed `plan/builder.py` (the module is `plan.py`),
`normalize/aliases.py` (never written), `llm/plan.py` (unwritten, and §11
promised a `--llm` flag to go with it) and omitted `normalize/identity.py`
entirely — four errors on a published page, in a diagram nothing could
contradict.

A drawing is prose, and prose about the code drifts from the code. This is the
cheapest possible pin: extract the leaf names from the fenced tree and compare
the set against `src/cbomctl`, in both directions.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "docs" / "DESIGN.md"
PKG = ROOT / "src" / "cbomctl"


def documented_modules() -> set[str]:
    """Module paths drawn under `src/cbomctl/` in the layout fence.

    Handles the brace form the diagram uses: `loader/{cyclonedx.py,x.py}`
    expands to `loader/cyclonedx.py` and `loader/x.py`.
    """
    fence = re.search(r"```\ncbomctl/\n(.*?)```", DESIGN.read_text(), re.S)
    assert fence, "docs/DESIGN.md no longer contains a `cbomctl/` layout fence"

    modules: set[str] = set()
    inside = False
    for line in fence.group(1).split("\n"):
        stripped = line.strip("│├└─ ").rstrip()
        if stripped.startswith("src/cbomctl/"):
            inside = True
            continue
        if not inside:
            continue
        if not line.startswith("│"):        # left the src/cbomctl/ subtree
            break
        entry = stripped.split("#")[0].strip()
        if not entry:
            continue
        m = re.match(r"^(?:([\w/]+)/)?\{([^}]+)\}(\.py)?$", entry)
        if m:
            prefix, names, suffix = m.group(1), m.group(2), m.group(3) or ""
            for name in names.split(","):
                name = name.strip()
                modules.add(f"{prefix}/{name}{suffix}" if prefix else f"{name}{suffix}")
        elif entry.endswith(".py"):
            modules.add(entry)
    return modules


def actual_modules() -> set[str]:
    return {
        str(p.relative_to(PKG))
        for p in PKG.rglob("*.py")
        if p.name != "__init__.py"
    }


def test_every_documented_module_exists():
    missing = sorted(m for m in documented_modules() if not (PKG / m).exists())
    assert not missing, (
        f"docs/DESIGN.md §12 draws modules that do not exist: {missing}")


def test_every_module_is_documented():
    undrawn = sorted(actual_modules() - documented_modules())
    assert not undrawn, (
        f"modules exist that docs/DESIGN.md §12 does not draw: {undrawn}")
