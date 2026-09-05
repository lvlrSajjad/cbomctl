# Session state — Phase 2 built; policy verification underway

`~/Coding/ME/pqc-audit` · branch `main` · **11 commits, nothing pushed** · `cbomctl`

## What works
`pip install -e .` then:
```
cbomctl verdict tests/fixtures/conflict-hybrid.json -c cbomctl.yaml.example
cbomctl prioritize|plan|normalize <cbom>
cbomctl policies list|show <id>
```
260 tests pass. Wheel builds with packs inside; verified in a clean venv.
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

## Policy verification — 6 of 7 packs verified, packs at 1.0.0
Extracted primary texts are in `.research/` (`bsi.txt`, `anssi.txt`,
`eo14412.clean.txt`, `ir8547.txt`, `eu_117507.txt`).

| pack | state |
|---|---|
| `bsi-de` 6/6 | TR-02102-1 v2026-01 §2.1, §5.3.4 |
| `anssi-fr` 5/5 | 2023 follow-up §1.1, §1.2, §2, §3.2, §4 |
| `asd-au` 6/6 | ISM Guidelines for Cryptography, page dated 2026-09-03 |
| `eu-roadmap` 6/6 | Coordinated Implementation Roadmap Part 1 v1.1 |
| `us-eo14412` 3/3 | 91 FR 38483 §4(b), §5(c) |
| `nist-ir8547` 4/4 | IR 8547 **ipd** Tables 2 and 4 — verified as a draft |
| `cnsa-2.0` 0/7 | **BLOCKED** — nsa.gov and media.defense.gov return 403 |

## THE ONE REMAINING BLOCKER — needs you and a browser
Open the CNSA 2.0 FAQ (reported U/OO/194427-22, PP-24-4014, v2.1, Dec 2024) at
`media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSA_CNSA_2.0_FAQ_.PDF`.
Seven rules are already *structured* for the reading; each `open_question` names
the sentence to find. Record the page number per rule. Priority:

1. **The hybrid sentence.** If NSA says hybrids should not be used on NSS
   mission systems except for named interop exceptions, the stance is
   `not_permitted_except_interop`, not `silent` — and then **no single
   construction satisfies all jurisdictions**, which the conflict output states
   instead of naming a compromise. Currently encoded as that hypothesis,
   unverified, so the difference is visible.
2. **Parameter sets** — ML-KEM-1024 / ML-DSA-87 required or merely preferred,
   and at all classification levels? BSI and ANSSI accept 768/65 (verified).
3. **SLH-DSA** — excluded or approved? BSI and ANSSI both exempt hash-based
   signatures from hybrid, so exclusion is a second contradiction.
4. Category deadlines against the FAQ's own table; the "all NSS by 2031" claim.

Then flip the five to seven rules, and nothing else blocks release.

## What the verification changed
- **`eu-roadmap` `hybrid: silent` was wrong** — the roadmap recommends hybrids.
  Our own assumption, caught by reading. All three European sources now
  verified as recommending hybrid.
- **BSI and ANSSI both exempt hash-based signatures** (SLH-DSA, LMS, XMSS) from
  the hybrid recommendation, independently, for the same stated reason. A
  widely-cited secondary summary says the opposite about BSI.
- **ASD is not disputing the facts.** It grants the European premise verbatim
  and prices complexity and overhead higher, adding that post-CRQC the
  classical half contributes nothing. Same axis, opposite conclusion.
- **IR 8547's 2030 deprecation only reaches 112-bit strength.** "RSA deprecated
  in 2030" is true for RSA-2048 and false for RSA-3072.
- **EO 14412 splits key establishment (2030) from signatures (2031)** in
  consecutive clauses of one sentence — the cleanest primary-source support for
  the urgency asymmetry anywhere in these packs.

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
