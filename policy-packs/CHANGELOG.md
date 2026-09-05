# Changelog — PQC policy packs

Semantic versioning on the pack collection. A change that can flip a verdict is
never a patch. See [README](README.md#versioning).

## [1.0.0] — unreleased

First release. Six of seven packs are read from primary sources and carry a
section citation, a pinned edition, a named verifier and a verification date.

Pre-release history is collapsed into this entry: nothing was ever published, so
the corrections below are recorded as findings rather than as breaking changes.

### Packs

| pack | rules | source |
|---|---|---|
| `bsi-de` | 6 ✅ | TR-02102-1 v2026-01 (2026-01-23) §2.1, §5.3.4 |
| `anssi-fr` | 5 ✅ | ANSSI views on the PQC transition, 2023 follow-up (2023-12-21) |
| `asd-au` | 6 ✅ | ASD ISM, Guidelines for Cryptography, page dated 2026-09-03 |
| `eu-roadmap` | 6 ✅ | Coordinated Implementation Roadmap Part 1 v1.1 (2025-06-11) |
| `us-eo14412` | 3 ✅ | EO 14412, 91 FR 38483 §4(b), §5(c) |
| `nist-ir8547` | 4 ✅ | NIST IR 8547 **ipd** Tables 2 and 4 — verified *as a draft* |
| `cnsa-2.0` | 7 ❌ | **unverified** — nsa.gov returns HTTP 403 to automated requests |

### Corrected during pre-release verification

Each of these was wrong in a draft and would have produced a misleading verdict.
They are listed because the corrections are the argument for reading primary
sources at all.

- **BSI does not mandate hybrid.** TR-02102-1 *recommends*; it is a Technical
  Guideline, not a statute. Every BSI rule is `guideline_recommendation` and
  cannot produce FAIL.
- **BSI's signature stance was left `null` rather than assumed, then filled from
  the text.** §5.3.4 recommends a quantum-safe signature scheme "only in
  combination with a classic signature scheme."
- **BSI and ANSSI both exempt hash-based signatures** (SLH-DSA, LMS, XMSS) from
  their hybrid recommendations, independently, for the same stated reason. A
  widely-circulated secondary summary says the opposite about BSI.
- **`eu-roadmap` was shipped as `hybrid: silent`; the roadmap recommends
  hybrids.** Silence was our assumption and it was wrong.
- **ANSSI's obligation is two obligations.** "Mandatory hybridation" and "shall
  implement" apply inside the security-visa process; outside it the position
  paper recommends. Modelled as `certification_requirement` and
  `guideline_recommendation` separately, because merging them would tell an
  uncertified French vendor it had failed a mandate that does not reach it.
- **`anssi-certification-2027` was removed, not left unverified.** Its date came
  only from press coverage. In a pack whose value is citation discipline, a
  press-sourced rule is a liability.
- **EO 14412 is not a blanket federal mandate.** HVAs and high impact systems,
  "excluding National Security Systems", with key establishment at 2030 and
  signatures at 2031.
- **NIST IR 8547's 2030 deprecation reaches only 112-bit strength.** ≥128-bit is
  disallowed after 2035 with no 2030 deprecation. "RSA is deprecated in 2030" is
  true for RSA-2048 and false for RSA-3072.
- **`eo14412-cisa-cbom-guidance` was removed.** It had an empty selector, so it
  fired on every asset and masked real findings. The provision lives in the
  pack notes.

### Schema

- `binding` — five values, from `statute` to `guideline_recommendation`. Decides
  FAIL versus WARN; severity does not.
- `hybrid` — a **three-step gradient**, scoped per purpose via
  `applies_to.purpose`: `recommended` (BSI, ANSSI, EU) → `not_recommended` but
  permitted (ASD) → `not_permitted_except_interop` (NSA, pending verification).
  The third value forecloses a satisfies-all target, and the conflict output
  says so rather than inventing a compromise.
- `rationale` — `harvest_now_decrypt_later` versus `algorithm_maturity` and
  others. The two are orthogonal: one drives *when* to move, the other *what to
  move to*.
- `applies_to.parameter_set` — jurisdictions disagree on required strength
  independently of construction (CNSA's reported ML-KEM-1024 against BSI's and
  ANSSI's accepted 768).
- `applies_to.exclude_algorithm` — for real carve-outs, such as the hash-based
  signature exemption in BSI §5.3.4 and ANSSI §4.
- `deadline_state` — `deprecated` and `disallowed` are distinct states and never
  collapse.
- `is_draft` — a verified reading of a draft is still a draft, and every
  reporter says so.

### Known gap

`cnsa-2.0` could not be verified: `nsa.gov` and `media.defense.gov` return HTTP
403 to automated requests, and the FAQ PDF will not render in a browser pane.
Its seven rules are *structured* for the reading rather than asserted by it, and
each `open_question` names the sentence to find. See
[`../docs/policy-sources.md`](../docs/policy-sources.md) §2.
