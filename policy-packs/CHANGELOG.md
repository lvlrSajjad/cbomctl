# Changelog — PQC policy packs

Semantic versioning on the pack collection. A change that can flip a verdict is
never a patch. See [README](README.md#versioning).

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
