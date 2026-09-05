# cbomctl

**One CBOM. Every jurisdiction's verdict. And where they contradict.**

Germany and France recommend hybrid post-quantum key exchange. Australia
recommends against it. The NSA wants ML-KEM-1024, not the -768 the others
accept. If you ship into more than one of those markets, those are not
independent checkboxes — and no tool will show you the collision.

`cbomctl` takes a CBOM from any generator, runs it against several national PQC
policies at once, and reports the matrix and the conflicts.

> ⚠️ **Pre-release. No policy rule is verified.** Every rule ships as
> `status: needs_verification` — assembled from secondary reporting, not yet
> read from primary sources. See [docs/policy-sources.md](docs/policy-sources.md).
> Not compliance advice.

<!-- badges: PyPI, CI, license -->

## What it looks like

```bash
$ cbomctl verdict app-cbom.json --jurisdictions bsi-de,anssi-fr,asd-au,cnsa-2.0

ASSET                          bsi-de    anssi-fr  asd-au    cnsa-2.0
X25519MLKEM768 (key-agree)     PASS      PASS      WARN      FAIL
ECDH secp256r1 (key-agree)     FAIL      FAIL      FAIL      FAIL
RSA-2048 (ambiguous)           INDET     INDET     INDET     INDET

CONFLICTS (1)
c1  X25519MLKEM768 — no single construction satisfies all four.
    bsi-de, anssi-fr  hybrid recommended        (guideline_recommendation)
    asd-au            hybrid not recommended    (guideline_recommendation)
    cnsa-2.0          requires ML-KEM-1024      (agency_requirement, NSS only)
    Closest satisfies-all: hybrid X25519 + ML-KEM-1024 — clears bsi-de,
    anssi-fr and cnsa-2.0, at a documented cost under asd-au.
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

`bsi-de` · `anssi-fr` · `asd-au` · `cnsa-2.0` · `us-eo14412` · `eu-roadmap`

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
