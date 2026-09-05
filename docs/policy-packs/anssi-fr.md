# ANSSI — France

`anssi-fr` · pack version 1.0.0 · ✅ **Verified**

## Who this binds

Two different obligations, deliberately kept as separate rules. ANSSI's general position is guidance and produces WARN. Its security-visa evaluation requirement is a certification condition and binds only products seeking a French security visa (CSPN, Critères Communs) — a far narrower population than French industry.

## Notes

Rules verified 2026-09-06 against "ANSSI views on the Post-Quantum Cryptography transition (2023 follow up)", December 21 2023, read from the primary PDF. The 2027 certification deadline reported in 2026 press coverage is NOT in this document and remains unverified.

## Rules

### ✅ `anssi-hybridation-necessary`

Hybridation is emphasised as necessary wherever post-quantum mitigation is needed, short and medium term. §1.1: "ANSSI still strongly emphasizes the necessity of hybridation wherever post-quantum mitigation is needed both in the short and medium term."

**Binding:** `guideline_recommendation` · **Verdict:** `WARN` · **Hybrid:** `recommended` · **Rationale:** `algorithm_maturity`

> Stated in the document: "even if the post-quantum algorithms have gained a lot of attention, they are still not mature enough to solely ensure the security. For example, several post-quantum schemes have suffered from classical attacks in the past years" — citing Beullens, "Breaking Rainbow takes a weekend on a laptop". Not a harvest argument.

**Migration target:** `ML-KEM-768` · as `hybrid`

**Source:** [ANSSI views on the Post-Quantum Cryptography transition (2023 follow up), §1.1](https://cyber.gouv.fr/publications/anssi-views-post-quantum-cryptography-transition) — 2023 follow-up, December 21 2023
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `anssi-hybridation-signatures`

The hybridation requirement covers signatures. §4: "any product that includes post-quantum mitigation shall implement hybridation except if the quantum mitigation only relies on hash-based signatures".

**Binding:** `guideline_recommendation` · **Verdict:** `WARN` · **Hybrid:** `recommended` · **Rationale:** `algorithm_maturity`

**Migration target:** `ML-DSA-65` · as `hybrid`

**Source:** [ANSSI views on the Post-Quantum Cryptography transition (2023 follow up), §3.2, §4](https://cyber.gouv.fr/publications/anssi-views-post-quantum-cryptography-transition) — 2023 follow-up, December 21 2023
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `anssi-hash-based-hybridation-optional`

Hybridation is optional for hash-based signatures. §2 on XMSS/LMS: "Hybridation (see Section 3 for more information) is optional for this signature." §4 repeats the exception for XMSS, LMS and SPHINCS+.

**Binding:** `guideline_recommendation` · **Verdict:** `INFO` · **Hybrid:** `silent` · **Rationale:** `algorithm_maturity`

> Same carve-out as BSI TR-02102-1 §5.3.4, for the same reason: hash-based security "is very minimalist … based on the security of hash functions".

**Source:** [ANSSI views on the Post-Quantum Cryptography transition (2023 follow up), §2, §4](https://cyber.gouv.fr/publications/anssi-views-post-quantum-cryptography-transition) — 2023 follow-up, December 21 2023
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `anssi-visa-hybridation-mandatory`

For a French security visa, phase-2 evaluation requires hybridation of post-quantum algorithms. §4: evaluation "comprise[s] an analysis of all cryptographic algorithms including the post-quantum algorithms with mandatory hybridation"; end products "shall implement hybridation" except where mitigation relies only on hash-based signatures.

**Binding:** `certification_requirement` · **Verdict:** `WARN` · **Hybrid:** `required` · **Rationale:** `algorithm_maturity`

> "mandatory" and "shall" are the document's own words, but they apply inside the security-visa process. Outside it, anssi-hybridation-necessary governs and is a recommendation. Modelled separately for that reason.

**Migration target:** as `hybrid`

**Source:** [ANSSI views on the Post-Quantum Cryptography transition (2023 follow up), §4](https://cyber.gouv.fr/publications/anssi-views-post-quantum-cryptography-transition) — 2023 follow-up, December 21 2023
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `anssi-longlived-protection-2030`

§1.2: "The use of hybrid post-quantum mitigation is recommended especially for security products aimed at offering a long-lasting protection of information (until after 2030) or that will potentially be used after 2030 without updates."

**Binding:** `guideline_recommendation` · **Verdict:** `WARN` · **Hybrid:** `recommended` · **Rationale:** `harvest_now_decrypt_later` · **Deadline:** 2030-12-31 (complete)

**Source:** [ANSSI views on the Post-Quantum Cryptography transition (2023 follow up), §1.2](https://cyber.gouv.fr/publications/anssi-views-post-quantum-cryptography-transition) — 2023 follow-up, December 21 2023
**Verified:** 2026-09-06 by Sadjad Asadi

---

Sourcing, open questions and the verification log for this pack are in [Policy sources](../policy-sources.md).
