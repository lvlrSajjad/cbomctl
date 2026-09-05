# CNSA 2.0 — NSA

`cnsa-2.0` · pack version 1.0.0 · ⚠️ **Unverified**

!!! danger "Not for compliance use"
    7 of 7 rules in this pack have not been read from a primary source. `cbomctl` prints a banner when this pack is used, and `--require-verified-policy` refuses to run against it.

## Who this binds

CNSA 2.0 governs US National Security Systems. It does not govern federal IT generally — those fall under EO 14412, which explicitly excludes NSS — and it does not govern the private sector. Run against a commercial CBOM, the honest output is that these rules do not apply to you.

## Notes

⚠️ NOT VERIFIED. Verification was attempted 2026-09-06 and failed: nsa.gov and media.defense.gov return HTTP 403 to every automated request, and the FAQ PDF triggers a download rather than rendering in a browser pane. This pack is the only one in the set still built from secondary reporting.
The rules below are STRUCTURED for the reading, not asserted by it. Each open_question names the sentence to find. The document to open is the CNSA 2.0 FAQ (reported as U/OO/194427-22, PP-24-4014, Version 2.1, December 2024) at media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSA_CNSA_2.0_FAQ_.PDF — record the page number for each rule you confirm.

## Rules

### ⚠️ `cnsa2-classical-asymmetric`

Quantum-vulnerable asymmetric algorithms are not on the CNSA 2.0 allowlist.

**Binding:** `agency_requirement` · **Verdict:** `FAIL` · **Rationale:** `unstated`

**Migration target:** `ML-KEM-1024` · `ML-DSA-87` · `AES-256` · `SHA-384` · as `pure-pqc`

**Source:** [NSA CNSA 2.0 FAQ](https://media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSA_CNSA_2.0_FAQ_.PDF)

!!! question "Open question"
    Confirm the allowlist and that it is exclusive (nothing else approved).

### ⚠️ `cnsa2-parameter-set-highest-only`

CNSA 2.0 is reported to require the highest parameter sets only — ML-KEM-1024 for key establishment and ML-DSA-87 for signatures — at all classification levels.

**Binding:** `agency_requirement` · **Verdict:** `FAIL` · **Rationale:** `key_length`

> A parameter conflict with BSI and ANSSI, which both accept ML-KEM-768 and ML-DSA-65 (verified). It is independent of the hybrid disagreement: a deployment could satisfy every jurisdiction's construction preference and still fail this on strength alone.

**Migration target:** `ML-KEM-1024` · `ML-DSA-87`

**Source:** [NSA CNSA 2.0 FAQ — approved algorithms and parameter sets](https://media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSA_CNSA_2.0_FAQ_.PDF)

!!! question "Open question"
    Confirm ML-KEM-1024 and ML-DSA-87 are required rather than merely preferred, and that this holds at ALL classification levels rather than only the highest. Record the page.

### ⚠️ `cnsa2-hybrid-not-permitted`

NSA is reported to direct that hybrid or other non-standardised quantum-resistant solutions not be used on NSS mission systems, except where NSA specifically recommends them for standardisation or interoperability (IKEv2 is cited as such an exception), and to state that because it is confident in the CNSA 2.0 algorithms it does not require a hybrid solution for security purposes.

**Binding:** `agency_requirement` · **Verdict:** `FAIL` · **Hybrid:** `not_permitted_except_interop` · **Rationale:** `unstated`

> If confirmed, this is a stronger stance than ASD's "not recommended; however, it is not prohibited" (verified), and it makes the hybrid axis a three-step gradient rather than a binary: recommended (BSI, ANSSI, EU) → not recommended but permitted (ASD) → not permitted outside named exceptions (NSA). It also removes the satisfies-all target: no single construction can clear both a recommending and a forbidding jurisdiction.

**Source:** [NSA CNSA 2.0 FAQ — hybrid solutions](https://media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSA_CNSA_2.0_FAQ_.PDF)

!!! question "Open question"
    THE key sentence for this pack. Get NSA's exact words on hybrids and record the page. "Does not require" and "shall not use except…" are different stances: the first would be `silent`, the second `not_permitted_except_interop`, and the difference decides whether a satisfies-all target exists in the conflict output. Confirm the IKEv2 exception too.

### ⚠️ `cnsa2-signing-exclusive-2030`

Software and firmware signing, and networking equipment: exclusive CNSA 2.0 use by 2030.

**Binding:** `agency_requirement` · **Verdict:** `FAIL` · **Rationale:** `unstated` · **Deadline:** 2030-12-31 (exclusive_use)

**Source:** [NSA CNSA 2.0 FAQ — timeline table](https://media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSA_CNSA_2.0_FAQ_.PDF)

!!! question "Open question"
    Verify each category deadline against the FAQ's own table; do not trust transcription.

### ⚠️ `cnsa2-web-os-exclusive-2033`

Browsers, servers, cloud services and operating systems: exclusive CNSA 2.0 use by 2033.

**Binding:** `agency_requirement` · **Verdict:** `FAIL` · **Rationale:** `unstated` · **Deadline:** 2033-12-31 (exclusive_use)

**Source:** [NSA CNSA 2.0 FAQ — timeline table](https://media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSA_CNSA_2.0_FAQ_.PDF)

!!! question "Open question"
    Confirm the category names so the cbomctl.yaml enum matches the FAQ's own wording, and check whether a separate "all NSS by 2031 unless excepted" milestone exists alongside these — that may be a conflation in secondary sources.

### ⚠️ `cnsa2-acquisition-gate-2027`

From 2027-01-01 new NSS acquisitions are expected to be CNSA 2.0 compliant by default. A procurement condition, not an algorithm deadline, so it sits behind --cnsa-acquisition-gate.

**Binding:** `agency_requirement` · **Verdict:** `FAIL` · **Rationale:** `unstated` · **Deadline:** 2027-01-01 (acquisition_gate)

**Source:** [NSA CNSA 2.0 FAQ — acquisition](https://media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSA_CNSA_2.0_FAQ_.PDF)

!!! question "Open question"
    Confirm the gate's scope and wording.

### ⚠️ `cnsa2-slh-dsa-status`

SLH-DSA (FIPS 205) status under CNSA 2.0 is disputed in secondary sources — excluded outright, or approved only for specific uses such as firmware signing.

**Binding:** `agency_requirement` · **Verdict:** `INDET` · **Rationale:** `unstated`

> Worth getting right: BSI and ANSSI both *exempt* hash-based signatures from their hybrid recommendations (verified), so if NSA excludes SLH-DSA outright that is a second, independent contradiction on the same family.

**Source:** [NSA CNSA 2.0 FAQ — hash-based signatures](https://media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSA_CNSA_2.0_FAQ_.PDF)

!!! question "Open question"
    Does the FAQ approve SLH-DSA, exclude it, or approve LMS/XMSS (SP 800-208) instead? Secondary sources disagree. Until read, this rule deliberately returns INDETERMINATE rather than guessing either way.

---

Sourcing, open questions and the verification log for this pack are in [Policy sources](../policy-sources.md).
