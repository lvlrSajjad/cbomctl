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

## Reading someone else's normalized output

```bash
sbom-tools view app-cbom.cdx.json -o json | cbomctl verdict - --from sbom-tools
```

Optional and best-effort: that payload's shape is read from source, not from a
documented contract. Raw CycloneDX is the supported path.
