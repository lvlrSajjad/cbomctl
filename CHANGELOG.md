# Changelog

Semantic versioning. Policy-pack versions move independently — see
[`policy-packs/CHANGELOG.md`](policy-packs/CHANGELOG.md).

## [Unreleased] — 0.1.0

First working version. **All seven policy packs are read from primary sources**
— every rule cites the section or page it came from, names its verifier and
pins the edition. The `UNVERIFIED POLICY PACK` banner, the `status` field and
`--require-verified-policy` remain in place for the next rule that has not been
checked, and are exercised by a synthetic test fixture.

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
- **`hybrid` is scoped per purpose and is a three-step gradient**:
  `recommended` (BSI, ANSSI, EU) → `not_recommended` but permitted (ASD) →
  `not_permitted_except_interop` (NSA). The middle step leaves a satisfies-all
  target available at a cost; the third removes it, and the conflict output says
  so rather than inventing a compromise.
- **Urgency and assurance are separate axes.** BSI and ANSSI both recommend
  hybrid *signatures* on algorithm-maturity grounds — ANSSI citing the classical
  break of Rainbow — which is a different argument from
  harvest-now-decrypt-later and reaches purposes HNDL cannot.
- **Security strength is derived**, so NIST IR 8547's 112-bit 2030 deprecation
  reaches RSA-2048 and P-224 but not RSA-3072 or P-256. Where it cannot be
  derived the finding is indeterminate rather than the stricter date.
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
- **One reading is a judgement call.** The CNSA 2.0 FAQ answers the hybrid
  question twice with different force, and the stronger answer is framed "while
  waiting for a final NIST post-quantum standard". Encoded at the stronger
  reading; the alternative and its consequence are in `docs/policy-sources.md`.
- The `sbom-tools` adapter's payload shape is inferred from their Rust struct
  definitions, not captured from a run. Its fixture is labelled constructed.
- cdxgen is unverified as a CBOM producer; a code search of their repository
  finds no `cryptoProperties` handling.
- `security_level` selectors always evaluate to INDETERMINATE — there is no
  config field for them yet.
