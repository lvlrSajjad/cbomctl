# Session state — Phase 2 built; policy verification underway

`~/Coding/ME/pqc-audit` · branch `main` · **11 commits, nothing pushed** · `cbomctl`

## What works
`pip install -e .` then:
```
cbomctl verdict tests/fixtures/conflict-hybrid.json -c cbomctl.yaml.example
cbomctl prioritize|plan|normalize <cbom>
cbomctl policies list|show <id>
```
135 tests pass. Wheel builds with packs inside; verified in a clean venv.
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

## Policy verification — 2 of 6 packs done
Primary PDFs are in `.research/` (`bsi.txt`, `anssi.txt`) if you want to re-read.

**✅ `bsi-de` 6/6** — TR-02102-1 v2026-01 (Jan 23 2026). Recommends, never
mandates. 2030 and 2031 are two real distinct dates (the "conflated editions"
suspicion was wrong). Signatures 2035. §5.3.4 recommends hybrid signatures —
the field left `null` rather than assumed is now filled from the text. Carve-out
found: hash-based schemes may be used standalone, contradicting a widely-cited
secondary summary.

**✅ `anssi-fr` 5/6** — 2023 follow-up (Dec 21 2023). Same hash-based carve-out,
independently. Split into two rules: `certification_requirement` ("mandatory",
"shall", inside the visa process) vs `guideline_recommendation` (everywhere
else). **F4 resolved**: §1.1 gives the maturity reason itself and cites the
Rainbow break, so `algorithm_maturity` is ANSSI's reasoning, not our inference.
The 2027 certification date is **not in the document** — press-only, still
unverified.

**Remaining, in order:** EO 14412 on federalregister.gov (the split 2030/2031
dates), CNSA 2.0 FAQ (media.defense.gov — C6 ML-KEM-1024), NIST IR 8547 draft
status, ASD ISM A2 (the literal "not recommended" sentence), EU roadmap E4
(binding force).

## Article 3 is now stronger, and sourced
Both BSI and ANSSI recommend hybrid signatures on maturity grounds, both citing
that PQ schemes are young; ANSSI cites Rainbow directly. NSA requires neither;
ASD recommends against. So the hybrid split is Europe vs the anglophone
agencies **on both purposes**, not an ANSSI quirk — and both European
authorities still put signatures on a later horizon (2035) than key
establishment (2030/2031). Urgency and assurance are both documented in the
same guidelines, which is the best possible evidence for modelling them apart.

## Not started
Phase 3 docs site (MkDocs). Phase 4 release. Show HN draft.
Drafts ready but unposted: `upstream/issue-draft.md`, `outreach/*`.

## Scratch
`.research/` — schemas, CBOMkit samples, sbom-tools + OQS sources. Gitignored.
