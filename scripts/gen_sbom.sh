#!/usr/bin/env bash
# Build a CycloneDX SBOM of cbomctl itself.
#
# A supply-chain-adjacent tool that ships no bill of materials for itself is
# asking for trust it will not extend to anyone else. This closes that.
#
# An SBOM, and deliberately not a CBOM. Nothing under `src/` imports
# `hashlib`, `hmac`, `secrets`, `ssl` or `cryptography` -- cbomctl reads
# other people's crypto inventories and performs none -- so a CBOM of this
# tool would be an empty `components` array with a CycloneDX header on it,
# which looks like evidence and is not. The dependency tree is real, so that
# is what gets published.
#
# Generator: cyclonedx-py (`cyclonedx-bom` on PyPI), not syft
# ----------------------------------------------------------
#   * It is the CycloneDX project's own Python tool, so the document is native
#     CycloneDX rather than converted into it. For a tool whose *input* format
#     is CycloneDX, emitting through the reference implementation is the only
#     coherent choice -- if their writer and our reader disagree, that is a
#     bug worth finding here rather than in someone's CBOM.
#   * It reads installed distribution metadata, so extras and environment
#     markers are resolved by the installer rather than guessed by a scanner.
#   * It validates its output against the CycloneDX schema before writing it.
#
# syft is the better tool for the job it is for: one scanner across many
# ecosystems, and containers and binaries in particular. We publish a
# pure-Python wheel and an sdist. There is no image to scan, so its breadth
# buys nothing here, and on this input it would read the same `*.dist-info`
# directories through a third-party parser and hand back CycloneDX it does
# not own.
#
# Lifecycle: this is a BUILD SBOM
# -------------------------------
# Stamped as `metadata.lifecycles: [{phase: build}]` below, because a document
# that does not say which kind it is invites the reader to assume the strongest
# one. CycloneDX defines the build phase as a BOM "obtained during a build
# process where component inventory is available for use", with "the precise
# versions of resolved components" known. That is exactly this: the target is
# installed into a clean environment and the resolved closure is read back out.
#
# What that means it does *not* assert:
#
#   * Not a source SBOM. `pyproject.toml` declares ranges (`typer>=0.12`);
#     this document names the versions those ranges resolved to, once, here.
#   * Not an analyzed SBOM. Nothing inspects the wheel's bytes. Every
#     component is a distribution's own metadata, taken at its word.
#   * No component hashes, so it is not evidence of what you installed. It is
#     the closure this build resolved, on this Python, for this platform. An
#     install next month can resolve differently; `cbomctl:source-commit` is
#     stamped so two documents can be told apart when it does.
#
# Usage: scripts/gen_sbom.sh <output-file> [target]
#
# `target` defaults to `.`, the project in this checkout. `release.yml` passes
# the built wheel instead, so the released document describes the artifact
# being published rather than a second build of it. The two resolve the same
# closure -- installing the project builds that same wheel first -- so the
# asset attached at a tag is byte-identical to the artifact `ci.yml` built
# from the same commit, and that is worth being able to check.
set -euo pipefail

cd "$(dirname "$0")/.."

out="${1:?usage: scripts/gen_sbom.sh <output-file> [target]}"
target="${2:-.}"

# Pinned, because the generator's name and version are recorded in
# `metadata.tools` and its output shape is its own. Unpinned, an upgrade
# would show up as a diff in the SBOM that is not a dependency change.
GENERATOR="cyclonedx-bom==7.3.1"

# Nothing here wants pip's upgrade notice in a build log.
export PIP_DISABLE_PIP_VERSION_CHECK=1

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# Two environments, kept apart. The generator lives in `tool/` because
# anything installed next to cbomctl becomes a component of cbomctl.
python3 -m venv "$tmp/tool"
"$tmp/tool/bin/pip" install --quiet "$GENERATOR"

# `--without-pip`: the measured environment *is* the claim, and a venv with
# pip in it lists pip as a component of cbomctl, which it is not.
python3 -m venv --without-pip "$tmp/env"
"$tmp/tool/bin/pip" --python "$tmp/env/bin/python" install --quiet -- "$target"

mkdir -p "$(dirname "$out")"

# `--output-reproducible` drops `metadata.timestamp` and the random
# `serialNumber`. Two runs on the same commit then differ only if the
# dependency resolution moved, which is the only difference worth looking at;
# without it every run differs and real drift is invisible. The document's
# identity is the commit it was built from, stamped below.
"$tmp/tool/bin/cyclonedx-py" environment "$tmp/env" \
  --pyproject pyproject.toml \
  --mc-type application \
  --spec-version 1.6 \
  --output-reproducible \
  --output-format JSON \
  --output-file "$out"

# Say what the document is, inside the document, then re-validate -- with the
# generator's own validator, so the check is the one cyclonedx-py already ran
# on the bytes it wrote and not a second opinion about the schema.
"$tmp/tool/bin/python" - "$out" <<'PY'
import json, re, subprocess, sys, tomllib
from pathlib import Path

from cyclonedx.schema import SchemaVersion
from cyclonedx.validation.json import JsonStrictValidator

path = Path(sys.argv[1])
doc = json.loads(path.read_text())
meta = doc.setdefault("metadata", {})
meta["lifecycles"] = [{"phase": "build"}]

# Absent outside a checkout, which is not a reason to refuse to build one.
commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                        text=True).stdout.strip()
if commit:
    meta.setdefault("properties", []).append(
        {"name": "cbomctl:source-commit", "value": commit})
    meta["properties"].sort(key=lambda p: p["name"])


def normalized(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()      # PEP 503


# An SBOM of the wrong environment is a valid CycloneDX document that says
# nothing, and it is the one failure here that would not announce itself: the
# install cannot fail quietly, but pointing the generator at an environment
# other than the one it installed into can. So cbomctl's declared
# dependencies have to be in the document, or nothing is written.
declared = {normalized(re.split(r"[<>=!~;\[ ]", d)[0])
            for d in tomllib.loads(Path("pyproject.toml").read_text())
            ["project"]["dependencies"]}
found = {normalized(c["name"]) for c in doc.get("components", [])}
if not declared <= found:
    print(f"the SBOM is missing declared dependencies: "
          f"{sorted(declared - found)}\nthe measured environment is not the "
          f"one cbomctl was installed into", file=sys.stderr)
    raise SystemExit(1)

serialized = json.dumps(doc, indent=2, sort_keys=True) + "\n"
error = JsonStrictValidator(SchemaVersion.V1_6).validate_str(serialized)
if error is not None:
    print(f"the stamped SBOM is not valid CycloneDX 1.6:\n{error}",
          file=sys.stderr)
    raise SystemExit(1)

path.write_text(serialized)
print(f"{path}: {len(doc['components'])} components "
      f"({len(declared)} declared, the rest transitive), lifecycle build, "
      f"commit {commit[:12] or 'unknown'}")
PY
