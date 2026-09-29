# Quickstart

## Install

```bash
pip install cbomctl
```

## You need a CBOM

`cbomctl` does not scan source code. Generate a CycloneDX 1.6 or 1.7 CBOM with
any generator — [CBOMkit](https://github.com/cbomkit/cbomkit),
[open-quantum-secure](https://github.com/jimbo111/open-quantum-secure),
cbomscanner, or a vendor's — or use one you were handed in a procurement
process. That last case is the one nothing else covers.

## First verdict

```bash
cbomctl verdict app-cbom.json --jurisdictions bsi-de,anssi-fr,asd-au
```

You get a row per cryptographic asset, a column per jurisdiction, and a
conflicts section listing every asset where the jurisdictions cannot all be
satisfied the same way.

Cells mean:

| | |
|---|---|
| `PASS` | no rule in that pack is violated |
| `FAIL` | a **mandatory** rule is violated — statute, executive order, or agency requirement |
| `WARN` | a recommendation or certification condition is violated |
| `INDET` | a rule needs a fact you have not supplied, or the purpose could not be resolved |
| `N/A` | that pack demonstrably does not reach this asset |

## Tell it what your data is worth

This is the input no CBOM contains, and without it there is nothing to rank by.

```yaml title="cbomctl.yaml"
version: 1

defaults:
  data_lifetime_years: 5
  migration_years: 3

# CNSA 2.0 and the EU roadmap set different deadlines per category, and a CBOM
# contains algorithms rather than product categories. Undeclared means
# INDETERMINATE — never a silent pass.
system_category: web-cloud

assets:
  - match: { location: "src/payments/**" }
    data_lifetime_years: 25          # cardholder data + regulatory retention

  - match: { location: "firmware/**" }
    verification_lifetime_years: 15  # signatures: how long it stays trusted,
                                     # not how long data stays secret
```

```bash
cbomctl verdict app-cbom.json -j bsi-de,asd-au --config cbomctl.yaml
```

Annotations can also travel in the CBOM itself, as CycloneDX component
properties named `cbomctl:data_lifetime_years`, so the fact lives next to the
asset.

## Other commands

```bash
cbomctl prioritize app-cbom.json -c cbomctl.yaml   # Mosca ranking
cbomctl plan app-cbom.json -j bsi-de,asd-au        # ordered migration plan
cbomctl normalize app-cbom.json                    # what decided each purpose
cbomctl policies list                              # packs and verification state
cbomctl policies show bsi-de                       # rules, sources, open questions
```

`cbomctl normalize` is the one to reach for when a verdict surprises you: it
shows which CBOM field resolved each asset's purpose, and every signal that
disagreed.

## Flags worth knowing

| flag | effect |
|---|---|
| `--strict` | unverified rules return `INDET` instead of asserting a verdict; indeterminate findings exit 3 |
| `--require-verified-policy` | refuse to run at all against a pack containing unverified rules |
| `--fail-on-warn` | treat recommendations as build failures |
| `--crqc-year 2035` | the quantum-computer assumption; stamped into every output |
| `--cnsa-acquisition-gate` | include CNSA 2.0's January 2027 procurement gate (off by default — it is a procurement condition, not an algorithm deadline) |
| `--format json\|md\|sarif` | machine-readable output |

## Reading `sbom-tools` normalized output

`cbomctl` can read the normalized JSON that
[`sbom-tools`](https://github.com/sbom-tool/sbom-tools) produces:

```bash
sbom-tools convert --to normalized app-cbom.cdx.json -O normalized.json  # unverified: sbom-tools is not installed in CI, and this subcommand is on their main but in no release yet
cbomctl verdict normalized.json --from sbom-tools
```

**`convert --to normalized` is not in a release yet.** It was
[added at our request](https://github.com/sbom-tool/sbom-tools/issues/366) and
merged to their `main` on 2026-09-07; v0.2.0, their latest release, predates
it. Until the next one, build from `main`. The pipeline was run end to end with
a build of `main` on 2026-09-29, and the second line above runs on every CI
push against the captured output of that run.

**`sbom-tools view -o json` is not the same thing.** It is a curated
projection — `name`, `version`, `ecosystem`, `licenses`, `supplier`,
vulnerability counts and EOL fields — with nothing derived from
`cryptoProperties`. Piping it here finds zero cryptographic assets.

**What the detour costs.** For every CBOM in this repository's fixtures the
verdicts and conflicts come out the same as reading the CycloneDX directly,
but three things are lost on the way through: source locations (their parser
does not keep `evidence.occurrences`), the difference between an absent and an
explicit-`unknown` `primitive`, and CycloneDX 1.6's `curve` field. None of the
three changed a verdict on our fixtures. The details are in
`src/cbomctl/loader/sbom_tools.py`.

**Raw CycloneDX remains the supported path** — and it is what the `sbom-tools`
maintainer recommends for this job as well. Their normalized payload is pinned
by snapshot tests only at the top level; everything under `components` may
change in any pre-1.0 minor release, announced in their CHANGELOG's upgrade
notes. Pin their version if you depend on it. That is why this adapter is
behind a flag.
