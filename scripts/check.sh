#!/usr/bin/env bash
# Everything CI checks, locally, with honest exit codes.
#
# Written after a `mkdocs build --strict 2>/dev/null && echo ok` reported a
# green docs build that CI then failed: stderr was discarded and the exit code
# checked belonged to grep, not mkdocs. A verification you cannot fail is not
# a verification.
set -uo pipefail

cd "$(dirname "$0")/.."
fail=0
step() {
  printf '\n\033[1m== %s ==\033[0m\n' "$1"; shift
  if "$@"; then printf '   \033[32mok\033[0m\n'; else printf '   \033[31mFAILED\033[0m\n'; fail=1; fi
}

step "tests"                python3 -m pytest tests/ -q
step "pack docs current"    python3 scripts/gen_pack_docs.py --check
step "article blocks current" python3 scripts/gen_article_blocks.py --check
step "docs build (strict)"  python3 -m mkdocs build --strict -d /tmp/cbomctl-site
step "wheel builds"         python3 -m build --wheel -o /tmp/cbomctl-dist .
step "packs ship in wheel"  python3 -c "
import glob, sys, zipfile
whl = sorted(glob.glob('/tmp/cbomctl-dist/*.whl'))[-1]
n = len([x for x in zipfile.ZipFile(whl).namelist() if x.startswith('cbomctl/packs/')])
print(f'   {n} packs in {whl.split(\"/\")[-1]}')
sys.exit(0 if n == 7 else 1)"

printf '\n'
if [ "$fail" -eq 0 ]; then printf '\033[32mall checks passed\033[0m\n'; else printf '\033[31mone or more checks failed\033[0m\n'; fi
exit "$fail"
