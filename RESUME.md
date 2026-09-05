# Session state — Phase 2 built, v0.1.0 unreleased

`~/Coding/ME/pqc-audit` · branch `main` · **11 commits, nothing pushed** · `cbomctl`

## What works
`pip install -e .` then:
```
cbomctl verdict tests/fixtures/conflict-hybrid.json -c cbomctl.yaml.example
cbomctl prioritize|plan|normalize <cbom>
cbomctl policies list|show <id>
```
124 tests pass. Wheel builds with packs inside; verified in a clean venv.
JSON output byte-identical across runs. Exit codes: 0/1/2/3.

## The two conditions on building against stubs — both enforced and tested
1. Every rule in all six packs is `status: needs_verification`; a test asserts it.
2. Unverified output is unmissable: a banner in text/markdown, a
   `policy_warning` object in JSON, `[UNVERIFIED RULE]` inline in SARIF.
   `--strict` turns unverified rules into INDETERMINATE and exits 3.
   `--require-verified-policy` refuses to run at all (exit 2).

## Design decisions now in code
- `binding` decides FAIL vs WARN, not severity. `guideline_recommendation`
  can never FAIL — enforced in `Rule.effective_verdict`, tested.
- `hybrid` scoped per purpose via `applies_to.purpose`. ANSSI recommends it for
  signatures with `rationale: algorithm_maturity`; BSI's signature stance is
  deliberately unset pending verification of TR-02102-1 2026-01.
- Urgency (Mosca × data lifetime) and assurance (target maturity) are separate.
- Three non-answers: `unscored`, `indeterminate`, `not-applicable`.
- CNSA 2027 acquisition gate off by default (`--cnsa-acquisition-gate`).

## Found while building — a real bug the design predicted
CBOMkit tags `AES` with `cryptoFunctions: [decapsulate]`. The precedence ladder
alone resolved that to key-agreement — confidently wrong, with HNDL weighting
attached. Added `PLAUSIBLE_PURPOSES`: when a signal claims something an
algorithm family cannot do, the result is AMBIGUOUS with the disagreement
recorded. Measured share of unresolved algorithm assets in the real Keycloak
CBOM: **8 of 22**. Docs corrected from "roughly a quarter" to "more than a third".

## Blocking release: policy verification
Rule tables are downstream of `docs/policy-sources.md`. Read primary sources
only, record URL + section + date, flip `status`, add a verification-log row.
Where the text is ambiguous, leave it unverified and quote the ambiguity.
Priority order: BSI TR-02102-1 2026-01 (**check the signature-hybrid language
specifically**), ANSSI F4 (hybrid-for-signatures — blocks article 3), ASD ISM
A2 (the literal "not recommended" sentence), EO 14412 U1 (HVA scope + NSS
exclusion), CNSA C6 (ML-KEM-1024), EU E4 (binding force).

## Not started
Phase 3 docs site (MkDocs). Phase 4 release. Show HN draft.
Drafts ready but unposted: `upstream/issue-draft.md`, `outreach/*`.

## Scratch
`.research/` — schemas, CBOMkit samples, sbom-tools + OQS sources. Gitignored.
