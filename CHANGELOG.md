# Changelog

Semantic versioning. Policy-pack versions move independently — see
[`policy-packs/CHANGELOG.md`](policy-packs/CHANGELOG.md).

## [Unreleased] — 0.1.0

First working version. **No policy rule is verified**: every rule was assembled
from secondary reporting, and any output computed from one carries a visible
`UNVERIFIED POLICY PACK — NOT FOR COMPLIANCE USE` banner.

### Added
- `cbomctl verdict` — per-asset × jurisdiction matrix plus a conflicts section
  with a computed satisfies-all target. The product.
- Conflict detection across four kinds: `construction`, `parameter`,
  `deadline`, `scope`.
- `cbomctl prioritize` — Mosca ranking from user-supplied data lifetimes.
- `cbomctl plan`, `cbomctl normalize`, `cbomctl policies list|show`.
- Purpose normalizer with an explicit precedence ladder, keeping `AMBIGUOUS`
  and `UNKNOWN` distinct and never guessing between them.
- Six policy packs as a standalone, semver-versioned artifact with their own
  JSON schema, consumable without this tool.
- Reporters: terminal matrix, JSON, Markdown, SARIF 2.1.0.
- Composite GitHub Action; CI validates fixtures against the official CycloneDX
  schemas and dog-foods the action on the conflict fixture.
- Optional `--from sbom-tools` adapter, no dependency.

### Design decisions worth knowing
- **`binding` decides FAIL versus WARN, not severity.** A
  `guideline_recommendation` cannot produce FAIL, enforced in code. Most PQC
  guidance is guidance, and reporting it as law misinforms.
- **`hybrid` is scoped per purpose.** ANSSI reportedly recommends hybrid
  signatures on *algorithm maturity* grounds — Rainbow and SIKE both fell to
  classical attacks during the NIST competition — which is a different argument
  from harvest-now-decrypt-later and applies to purposes HNDL cannot reach.
  Urgency and assurance are separate axes.
- **Three ways to not answer**: `unscored` (purpose unresolvable),
  `indeterminate` (a rule needs an undeclared fact), `not-applicable`. None is a
  silent pass.
- **`--strict`** turns every unverified rule into INDETERMINATE, so nothing
  built on stub packs can be mistaken for a real verdict.
  **`--require-verified-policy`** refuses to run at all.
- **The CNSA 2.0 January 2027 acquisition gate is off by default**
  (`--cnsa-acquisition-gate`): it is a procurement condition on new NSS
  acquisitions, not an algorithm deadline.

### Known limits
- The `sbom-tools` adapter's payload shape is inferred from their Rust struct
  definitions, not captured from a run. Its fixture is labelled constructed.
- cdxgen is unverified as a CBOM producer; a code search of their repository
  finds no `cryptoProperties` handling.
- `security_level` selectors always evaluate to INDETERMINATE — there is no
  config field for them yet.
