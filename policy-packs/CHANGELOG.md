# Changelog — PQC policy packs

Semantic versioning on the pack collection. A change that can flip a verdict is
never a patch. See [README](README.md#versioning).

## [Unreleased]

### bsi-de 0.2.0 — VERIFIED

First pack verified against its primary source: BSI TR-02102-1 **Version
2026-01 (January 23, 2026)**, English edition, read directly from the PDF.

- `bsi-classical-key-agreement-sunset` — 2031-12-31 confirmed (§2.1).
- `bsi-high-protection-2030` — 2030-12-31 confirmed and **distinct** from the
  2031 date. The earlier suspicion that these were one date conflated across
  editions was wrong; §2.1 states both.
- `bsi-hybrid-key-agreement` — added. §2.1 recommends hybrid form for
  quantum-safe key agreement.
- `bsi-classical-signatures-2035` — 2035-12-31 confirmed (§2.1).
- `bsi-hybrid-signatures` — **added.** §5.3.4 recommends a quantum-safe
  signature scheme "only in combination with a classic signature scheme". The
  field previously left `null` rather than assumed is now filled from the text.
- `bsi-hash-based-standalone-permitted` — **added carve-out.** §5.3.4 permits
  hash-based schemes (SLH-DSA, LMS, XMSS) to be used alone. A widely-cited
  secondary summary claims BSI wants hybrid for all PQC including hash-based;
  the primary text says otherwise.
- Binding confirmed as `guideline_recommendation` throughout — TR-02102-1
  *recommends*. No rule in this pack can produce FAIL.

Schema addition: `applies_to.exclude_algorithm`, needed to express the §5.3.4
carve-out.

## [Unreleased] — 0.1.0

Initial six packs. **Nothing in this release is verified**; every rule ships
`status: needs_verification`.

### Added
- `bsi-de`, `anssi-fr`, `asd-au`, `cnsa-2.0`, `us-eo14412`, `eu-roadmap`
- Pack schema with `binding` and `hybrid` as first-class fields
- Primary-source allowlist enforced on `source_url`

### Corrections applied before first release

These were wrong in the pre-release drafts and are recorded because each would
have produced a materially misleading verdict:

- **BSI does not "mandate" hybrid.** TR-02102-1 is a technical guideline that
  *recommends* it → `binding: guideline_recommendation`, `hybrid: recommended`.
  The word "mandatory" is removed from every document in this repository.
- **ANSSI does not "require" hybrid unqualified.** It *strongly recommends* it,
  and separately requires it for certain ANSSI certifications — modelled as two
  rules with different `binding` values.
- **NIST IR 8547 is still an initial public draft** (Nov 2024). Its 2030/2035
  dates are *proposed*, and any output citing them prints "draft".
- **"Deprecated" and "disallowed" are different states** and are modelled
  separately, not collapsed into one failure.
- **EO 14412 is not a blanket federal PQC mandate.** It covers High Value
  Assets and high-impact systems, excluding National Security Systems, with
  key establishment and digital signatures on *separate* deadlines.
