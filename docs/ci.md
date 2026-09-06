# CI integration

## GitHub Action

```yaml
name: PQC policy
on: [pull_request]

permissions:
  contents: read
  security-events: write   # to upload SARIF

jobs:
  cbomctl:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Bring a CBOM from whatever generator you use. CBOMkit-action takes no
      # `with:` inputs — it is configured by environment variables, and writes
      # the consolidated CBOM to `cbom/cbom.json`: the directory comes from
      # `CBOMKIT_OUTPUT_DIR`, which defaults to `cbom`, and the consolidated
      # file inside it is `cbom.json`. Set `CBOMKIT_OUTPUT_DIR` if you want it
      # somewhere else. Their step also exports `outputs.pattern`
      # (`<dir>/cbom*.json`), which is what to hand to upload-artifact if you
      # want the per-module CBOMs as well.
      - uses: cbomkit/cbomkit-action@main
        id: cbom
        env:
          CBOMKIT_LANGUAGES: java, python

      # v0 is a moving major tag: patch fixes arrive, breaking changes do not.
      # Pin an exact release (v0.1.4) instead if you want the tool frozen.
      - uses: lvlrSajjad/cbomctl@v0
        with:
          cbom: cbom/cbom.json
          jurisdictions: bsi-de,anssi-fr,asd-au
          config: cbomctl.yaml
          format: sarif
          output: cbomctl.sarif

      - uses: github/codeql-action/upload-sarif@v3
        if: always()
        with: { sarif_file: cbomctl.sarif }
```

The action always prints the matrix to the job log, even when the
machine-readable report goes to a file — the matrix is the part a human reads.

!!! note "How much of this workflow is checked"
    `scripts/check_commands.py` resolves **every** step on every run, ours and
    theirs. For `lvlrSajjad/cbomctl` it asserts that `@v0` is a tag this
    repository has and that each `with:` key is an input `action.yml` declares.
    For `cbomkit/cbomkit-action`, `actions/checkout` and
    `github/codeql-action/upload-sarif` it fetches their own `action.yml` at
    the ref named above and checks the same thing — and because a Docker action
    declares no inputs at all, the `env:` names are checked against
    [CBOMkit-action's README](https://github.com/cbomkit/cbomkit-action) at
    that ref. An action the checker does not know how to resolve is reported
    unchecked by name rather than passed over.

    Until 2026-09-06 this page passed `with: { output: cbom.json }` to an
    action that declares no inputs at all. That was fixed by hand, and then
    nothing could re-check it; now something does.

    **What is still not checked:** that the workflow runs. Nothing here starts
    a container or scans a repository, so `cbom/cbom.json` is read from
    CBOMkit-action's `Main.java` (`CBOMKIT_OUTPUT_DIR`, default `cbom`) and
    their README, on 2026-09-06 — transcribed, not observed. The reasoning for
    not building a scheduled job that would run it is in
    [`docs/roadmap.md`](roadmap.md#running-the-cbomkit-half-of-docscimd).

## Exit codes

| code | meaning |
|---|---|
| `0` | no mandatory rule violated |
| `1` | a mandatory rule failed, or `--fail-on-warn` and a recommendation was violated |
| `2` | usage or parse error |
| `3` | unresolved or indeterminate findings under `--strict` |

**`WARN` does not fail the build by default**, and that is deliberate. A
technical guideline that *recommends* hybrid is not a gate; treating it as one
trains people to ignore the tool. Use `--fail-on-warn` when your organisation
has decided to hold itself to recommendations.

## Choosing your gate

**Start permissive.** Run without `--strict` and read the output for a few
weeks. The unresolved section tells you how good your generator is, and that is
usually the first thing worth fixing.

**Then close the loop on unknowns.** `--strict` turns unresolved purposes and
undeclared facts into exit 3. This is the setting that forces the question back
to a human — which is where it belongs, since a CBOM cannot say what a key is
for and a config file can.

**`--require-verified-policy`** refuses to run at all against a pack containing
rules that have not been read from a primary source. If you are using the output
for anything that resembles a compliance claim, turn this on. It currently
excludes nothing — every shipped rule is verified — which is exactly when it is
cheapest to switch on and keep on.

## SARIF

The SARIF output carries **only** `cbomctl`'s risk and conflict findings, so
they sit beside your other tools' results in the GitHub Security tab rather than
duplicating them. Locations come from `evidence.occurrences`, so findings are
clickable to the file and line where the algorithm was found.

Unverified rules are marked `[UNVERIFIED RULE]` and draft-sourced rules
`[DRAFT SOURCE]` inline in the finding text, because a SARIF result detached
from its banner should still say what it is.

## Determinism

Same CBOM, same config, same pack version, same `--crqc-year` produces
byte-identical JSON. Nothing in the verdict path reaches the network, consults a
clock beyond the evaluation date, or calls a language model. Diff two runs and
any difference is a real change.
