# cbomctl

**One CBOM. Every jurisdiction's verdict. And where they contradict.**

Germany and France recommend hybrid post-quantum key exchange. Australia
recommends against it. The NSA wants ML-KEM-1024, not the -768 the others
accept. If you ship into more than one of those markets, those are not
independent checkboxes — and no tool will show you the collision.

`cbomctl` takes a CBOM from any generator, runs it against several national PQC
policies at once, and reports the matrix and the conflicts.

> ⚠️ **Pre-release.** All seven policy packs are read from their primary
> sources — every rule cites the section or page it came from. The machinery for
> unverified rules stays in place for the next pack that has not been checked:
> any verdict derived from one carries a visible banner naming the packs
> involved. Read the sources yourself before acting on a verdict — they are
> listed in [docs/policy-sources.md](docs/policy-sources.md). Not compliance
> advice.

[![PyPI](https://img.shields.io/pypi/v/cbomctl)](https://pypi.org/project/cbomctl/)
[![CI](https://github.com/lvlrSajjad/cbomctl/actions/workflows/ci.yml/badge.svg)](https://github.com/lvlrSajjad/cbomctl/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

## What it looks like

```bash
cbomctl verdict app-cbom.json --jurisdictions bsi-de,anssi-fr,asd-au,cnsa-2.0
```

<!-- cbomctl: verdict tests/fixtures/conflict-hybrid.json -j bsi-de,anssi-fr,asd-au,cnsa-2.0 | head -34 -->
```
ASSET           PURPOSE        bsi-de    anssi-fr  asd-au    cnsa-2.0
───────────────────────────────────────────────────────────────────────
ECDH            key-agreement  WARN      WARN      WARN      FAIL        ⚠ c1
                └ bsi-de · disallowed 2031-12-31
                └ anssi-fr · complete 2030-12-31
                └ asd-au · disallowed 2030-12-31 · complete 2030-12-31
                └ cnsa-2.0 · disallowed 2030-12-31 · exclusive_use 2031-12-31
                └ src/payments/legacy.go:12
X25519MLKEM768  key-agreement  PASS      PASS      WARN      FAIL        ⚠ c2,c3
                └ asd-au · deprecated 2030-12-31
                └ src/payments/tls.go:88
ML-DSA-65       signature      WARN      WARN      WARN      FAIL        ⚠ c4,c5
                └ asd-au · deprecated 2030-12-31
                └ src/payments/sign.go:7
RSA-2048        ambiguous      INDET     INDET     INDET     INDET
                └ unresolved: purpose-ambiguous (primitive:pke)
                └ as key transport → critical · as signature → medium
                └ Declare the purpose in cbomctl.yaml, or regenerate the CBOM with a generator that records
                  cryptoFunctions.
                └ src/payments/keys.go:41

CONFLICTS (5)
  c1  [construction]  ECDH
      anssi-fr, bsi-de recommend a hybrid construction for key-agreement; asd-au recommend
      against it; cnsa-2.0 does not permit one outside named interoperability exceptions.
      cnsa-2.0 does not permit a hybrid construction outside named interoperability exceptions,
      while anssi-fr, bsi-de recommend one. **No single configuration satisfies all selected
      jurisdictions.** You will need different builds, or to drop a jurisdiction from scope.
      asd-au would permit a hybrid but recommends against it, so even dropping cnsa-2.0 leaves a
      documented cost. This is a business decision, not a technical one.
      ⚖ This conflict depends on a contested encoding. Under the alternative reading (cnsa-2.0
      silent), a hybrid construction would satisfy all selected jurisdictions, at a documented
      cost. The argument and the evidence for the encoding used are in the `cnsa-2.0` rule's
      interpretation note (`cbomctl policies show cnsa-2.0`).
```

`WARN` rather than `FAIL` for ASD is deliberate: the ISM *recommends against*
hybrids, it does not prohibit them. Reporting a guideline as a mandate is the
most common error in this space, so every rule carries a `binding` field —
`statute`, `executive_order`, `agency_requirement`, `certification_requirement`,
or `guideline_recommendation` — and the verdict follows from it.

`INDET` is the tool declining to guess. That CBOM records `primitive: pke` for
the RSA key, which cannot distinguish key transport from signature — and the
answer moves the finding between critical and medium. Rather than pick, it says
what is missing and what would resolve it.

## Related tools

Most of what a PQC readiness tool does, other people already do — several of
them well. Use them.

| tool | what it does |
|---|---|
| [CBOMkit](https://github.com/cbomkit/cbomkit), [cbomscanner](https://cyclonedx.org/capabilities/cbom/), KeyLens, [pqc-scanner](https://github.com/rauleteee/pqc-scanner) | generate CBOMs from source |
| [open-quantum-secure](https://github.com/jimbo111/open-quantum-secure) | scans source + live TLS/SSH, generates CBOM, quantum readiness score, `--data-lifetime-years` HNDL weighting, and **seven compliance frameworks** including BSI, ASD ISM and ANSSI |
| [sbom-tools](https://github.com/sbom-tool/sbom-tools) | CycloneDX/SPDX ingestion, semantic CBOM diff, quality scoring, CNSA 2.0 and NIST IR 8547 validation, SARIF/OSCAL |
| IBM Quantum Safe Migration Orchestrator, SandboxAQ AQtive Guard, O3 Security | commercial discovery, risk prioritization and migration planning |

**`cbomctl` overlaps all of them, and only two things are actually its own:**

1. **Conflict as a computed output.** `open-quantum-secure` runs multiple
   frameworks at once and its README documents cross-framework divergence
   directly — this is not a gap in the market, and anyone claiming otherwise
   has not read it. What it emits is one report per framework, concatenated;
   you find the disagreement by comparing them yourself. `cbomctl` emits the
   matrix, a conflict object naming the disagreeing authorities and the reason,
   and a computed satisfies-all target where one exists.
2. **Evaluating a CBOM you did not generate.** The tools above evaluate their
   own scan. If your CBOM came from a vendor, a procurement process, or a
   different generator, `cbomctl` will read it.

If you want a scanner, use `open-quantum-secure`. If you want diff and
validation, use `sbom-tools`. If you have a CBOM and need to know which
jurisdiction's answer to believe, that is this tool.

## What it does not do

- **It does not scan source code or probe endpoints.** Bring a CBOM.
- **It does not guess.** In CBOMkit's published Keycloak CBOM, 8 of 22
  algorithm components carry no usable purpose signal — more than a third.
  Those are reported as unresolved, with the range they would span if guessed.
- **It does not give compliance advice.** It reports what a rule set says, with
  the primary source and verification date attached. Every rule today is
  unverified.
- **It does not treat guidance as law.** See `binding`, above.
- **It does not know when a CRQC arrives.** 2035 is a planning assumption
  matching the NIST/NSM-10 horizon, not a prediction. `--crqc-year` changes it;
  whatever you choose is stamped into the output.
- **It does not diff SBOMs, verify signatures, or scan binaries.**

## Also included

`cbomctl prioritize` ranks findings by Mosca's inequality using data lifetimes
you supply, weighting harvest-now-decrypt-later exposure highest.
`cbomctl plan` emits an ordered migration plan. Both are useful; neither is
novel — see Related tools.

## Policy packs

The rule sets live in [`policy-packs/`](policy-packs/) as a standalone,
semantically versioned artifact with its own schema and changelog, so another
tool can consume them without `cbomctl`. Every rule carries a primary-source
URL, a `last_verified` date, a `binding` classification, and a `hybrid` stance.

| pack | state |
|---|---|
| pack | state |
|---|---|
| pack | state |
|---|---|
| `bsi-de` | ✅ TR-02102-1 v2026-01 §2.1, §5.3.4 |
| `anssi-fr` | ✅ 5/6 — ANSSI 2023 follow-up §1.1, §1.2, §2, §3.2, §4 |
| `asd-au` | ✅ ISM Guidelines for Cryptography, 2026-09-03 |
| `eu-roadmap` | ✅ Coordinated Implementation Roadmap Part 1 v1.1 |
| `us-eo14412` | ✅ 91 FR 38483 §4(b), §5(c) |
| `nist-ir8547` | ✅ **as a draft** — IR 8547 ipd Tables 2 and 4 |
| `cnsa-2.0` | ✅ CNSA 2.0 FAQ v2.1 (Dec 2024), pp. 2, 6, 8, 19–20 |

## Install

```bash
pip install cbomctl
```

Optional: `pip install cbomctl[llm]` adds a prose migration narrative that
cannot affect any verdict.

## Documentation

[Design](docs/DESIGN.md) · [Policy sources and open questions](docs/policy-sources.md) ·
[Policy packs](policy-packs/README.md)

## License

Apache-2.0
