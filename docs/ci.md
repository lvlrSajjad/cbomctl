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
      # `with:` inputs — it is configured by environment variables and writes
      # the consolidated CBOM to `cbom.json` in the workspace. Read their
      # README before copying this; it is the half of this file we cannot run.
      - uses: cbomkit/cbomkit-action@main
        id: cbom
        env:
          CBOMKIT_LANGUAGES: java, python

      # v0 is a moving major tag: patch fixes arrive, breaking changes do not.
      # Pin an exact release (v0.1.4) instead if you want the tool frozen.
      - uses: lvlrSajjad/cbomctl@v0
        with:
          cbom: cbom.json
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
    `scripts/check_commands.py` resolves the `cbomctl` step on every run: it
    asserts that `@v0` is a tag that exists and that every `with:` key is an
    input `action.yml` actually declares. It cannot execute a GitHub workflow,
    so the CBOMkit step is transcribed from
    [their README](https://github.com/cbomkit/cbomkit-action) and read against
    their `action.yml` — not run. Until 2026-09-06 this page passed
    `with: { output: cbom.json }` to an action that declares no inputs at all.

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
for anything that resembles a compliance claim, turn this on; it currently
excludes `cnsa-2.0`.

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
