# CNSA 2.0 — NSA

`cnsa-2.0` · pack version 1.0.0 · ✅ **Verified**

## Who this binds

CNSA 2.0 governs US National Security Systems. The FAQ is explicit: "NSA is not using these requirements to dictate to any other entity outside of NSS what algorithms they should use, although NSA recognizes that interoperability requirements or other interests may lead to scenarios where these recommendations are used by a larger community." Federal IT generally falls under EO 14412, which excludes NSS. Run against a commercial CBOM, the honest output is that these rules do not apply to you.

## Notes

VERIFIED 2026-09-06 against the primary PDF: "The Commercial National Security Algorithm Suite 2.0 and Quantum Computing FAQ", U/OO/194427-22 | PP-24-4014 | December 2024 Ver. 2.1.
Two corrections to the pre-release stub, which had been assembled from secondary reporting. There are NO per-product-category deadlines in v2.1 — no browsers, operating systems or networking rows — and the string "2033" does not appear in the document at all. Those came from the September 2022 announcement's chart and are superseded here by the CNSSP 15 dates: 2027-01-01, 2030-12-31, 2031-12-31, with a 2035 NSM-10 backstop.

## Rules

### ✅ `cnsa2-classical-asymmetric`

Quantum-vulnerable asymmetric algorithms are not in the CNSA 2.0 suite. "CNSA 2.0 algorithms will be required for all products that employ public-standard algorithms in NSS, whether a future design or currently fielded. Any usage of Suite B or CNSA 1.0 algorithms will be required to transition to CNSA 2.0."

**Binding:** `agency_requirement` · **Verdict:** `FAIL` · **Rationale:** `unstated`

**Migration target:** `ML-KEM-1024` · `ML-DSA-87` · `AES-256` · `SHA-384` · as `pure-pqc`

**Source:** [NSA CNSA 2.0 and Quantum Computing FAQ, §CNSA 2.0 (p. 2)](https://media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSA_CNSA_2.0_FAQ_.PDF) — U/OO/194427-22 | PP-24-4014 | December 2024 Ver. 2.1
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `cnsa2-parameter-set-highest-only`

The CNSA 2.0 table requires the highest parameter sets only: "ML-KEM-1024 for all classification levels", "ML-DSA-87 for all classification levels", "Use 256-bit keys for all classification levels" (AES), and "Use SHA-384 or SHA-512 for all classification levels".

**Binding:** `agency_requirement` · **Verdict:** `FAIL` · **Rationale:** `key_length`

> A parameter conflict with BSI and ANSSI, which both accept ML-KEM-768 and ML-DSA-65 (both verified). It is independent of the hybrid disagreement: a deployment could satisfy every jurisdiction's construction preference and still fail this on strength alone. "for all classification levels" means there is no lower tier where 768 becomes acceptable.

**Migration target:** `ML-KEM-1024` · `ML-DSA-87`

**Source:** [NSA CNSA 2.0 FAQ, Table: Commercial National Security Algorithm Suite 2.0 (p. 2)](https://media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSA_CNSA_2.0_FAQ_.PDF) — U/OO/194427-22 | PP-24-4014 | December 2024 Ver. 2.1
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `cnsa2-hybrid-not-permitted`

"Do not use a hybrid or other non-standardized QR solution on NSS mission systems except for those exceptions NSA specifically recommends to meet standardization or interoperability requirements. … Except as noted above, hybrid solutions will not be integrated into eventual deployable solutions."

**Binding:** `agency_requirement` · **Verdict:** `FAIL` · **Hybrid:** `not_permitted_except_interop` · **Rationale:** `unstated`

> READ THE SCOPE CAVEAT. The FAQ gives two answers on hybrids and they are not identical in force. The position answer says only: "NSA has confidence in CNSA 2.0 algorithms and will not require NSS developers to use hybrid certified products for security purposes. However, product availability and interoperability requirements may lead to adopting hybrid solutions." The imperative quoted in this rule's description comes from a question framed "while waiting for a final NIST post-quantum standard" — a period that arguably ended when FIPS 203/204/205 were finalised in August 2024, four months before this edition published. Its closing sentence, however, is unconditional and forward-looking.
> Encoded at the stronger reading because "Do not use" is imperative and "will not be integrated into eventual deployable solutions" is not time-scoped. NSA's reasoning is cost, not doubt about hybrids' benefit: "spending limited resources to add cryptographic complexity can at times weaken security rather than improve it."

**Source:** [NSA CNSA 2.0 FAQ, §Hybrids (pp. 19–20)](https://media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSA_CNSA_2.0_FAQ_.PDF) — U/OO/194427-22 | PP-24-4014 | December 2024 Ver. 2.1
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `cnsa2-hybrid-ikev2-exception`

IKEv2 is the named exception. "Due to difficulties introduced when unencrypted IKEv2 messages exceed a certain byte size… NSA's profile of this solution will continue the use of CNSA 1.0 key establishment algorithms, but fortified by key establishment using ML-KEM-1024."

**Binding:** `agency_requirement` · **Verdict:** `INFO` · **Hybrid:** `required` · **Rationale:** `unstated`

> The one place NSA affirmatively wants a hybrid, and it is a size constraint rather than a security judgement. Encoded so an IKEv2 hybrid does not inherit the general prohibition.

**Migration target:** `ML-KEM-1024` · as `hybrid`

**Source:** [NSA CNSA 2.0 FAQ, §Hybrids (p. 20)](https://media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSA_CNSA_2.0_FAQ_.PDF) — U/OO/194427-22 | PP-24-4014 | December 2024 Ver. 2.1
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `cnsa2-acquisition-gate-2027`

"CNSSP 15 states that by January 1, 2027, all new acquisitions for NSS will be required to be CNSA 2.0 compliant unless otherwise noted."

**Binding:** `agency_requirement` · **Verdict:** `FAIL` · **Rationale:** `unstated` · **Deadline:** 2027-01-01 (acquisition_gate)

**Source:** [NSA CNSA 2.0 FAQ, §Timeframe (p. 6)](https://media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSA_CNSA_2.0_FAQ_.PDF) — U/OO/194427-22 | PP-24-4014 | December 2024 Ver. 2.1
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `cnsa2-phase-out-2030`

"By December 31, 2030, all equipment and services that cannot support CNSA 2.0 must be phased out unless otherwise noted."

**Binding:** `agency_requirement` · **Verdict:** `FAIL` · **Rationale:** `unstated` · **Deadline:** 2030-12-31 (disallowed)

**Migration target:** `ML-KEM-1024` · `ML-DSA-87`

**Source:** [NSA CNSA 2.0 FAQ, §Timeframe (p. 6)](https://media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSA_CNSA_2.0_FAQ_.PDF) — U/OO/194427-22 | PP-24-4014 | December 2024 Ver. 2.1
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `cnsa2-mandated-2031`

"by December 31, 2031, CNSA 2.0 algorithms are mandated for use unless otherwise noted." NSA separately intends all NSS to be quantum-resistant by 2035, per NSM-10.

**Binding:** `agency_requirement` · **Verdict:** `FAIL` · **Rationale:** `unstated` · **Deadline:** 2031-12-31 (exclusive_use)

**Source:** [NSA CNSA 2.0 FAQ, §Timeframe (p. 6)](https://media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSA_CNSA_2.0_FAQ_.PDF) — U/OO/194427-22 | PP-24-4014 | December 2024 Ver. 2.1
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `cnsa2-slh-dsa-not-approved`

"Q: Can I use SLH-DSA (aka SPHINCS+) to sign software? A: While SLH-DSA is hash-based, it is not part of CNSA and is not approved for any use in NSS."

**Binding:** `agency_requirement` · **Verdict:** `FAIL` · **Rationale:** `unstated`

> A second, independent contradiction on the same algorithm family. BSI §5.3.4 and ANSSI §2/§4 both explicitly permit hash-based signatures standalone, exempting them from their hybrid recommendations. NSA does not approve SLH-DSA for any use in NSS at all. Same algorithm, three positions: exempt-and-approved (BSI, ANSSI), and not approved (NSA).

**Migration target:** `ML-DSA-87`

**Source:** [NSA CNSA 2.0 FAQ, §Quantum alternatives (p. 8)](https://media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSA_CNSA_2.0_FAQ_.PDF) — U/OO/194427-22 | PP-24-4014 | December 2024 Ver. 2.1
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `cnsa2-hash-based-firmware-signing-only`

LMS and XMSS are approved, but only "for digitally signing firmware and software". "From NIST SP 800-208, NSA has only approved LMS and XMSS for use in NSS. The multi-tree algorithms HSS and XMSSMT are not allowed." NSA's preferred parameter set is LMS with SHA-256/192.

**Binding:** `agency_requirement` · **Verdict:** `FAIL` · **Rationale:** `unstated`

> ANSSI names XMSS, LMS and SPHINCS+ together as acceptable hash-based options; NSA splits that family three ways — LMS and XMSS approved for firmware/software signing only, HSS and XMSSMT not allowed, SLH-DSA not approved at all.

**Migration target:** `LMS-SHA-256/192`

**Source:** [NSA CNSA 2.0 FAQ, Table 'Algorithms Allowed in Specific Applications' (p. 3) and §Quantum alternatives (p. 8)](https://media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSA_CNSA_2.0_FAQ_.PDF) — U/OO/194427-22 | PP-24-4014 | December 2024 Ver. 2.1
**Verified:** 2026-09-06 by Sadjad Asadi

---

Sourcing, open questions and the verification log for this pack are in [Policy sources](../policy-sources.md).
