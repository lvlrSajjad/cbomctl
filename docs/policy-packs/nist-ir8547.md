# NIST IR 8547 (draft) — United States

`nist-ir8547` · pack version 1.0.0 · ✅ **Verified**

## Who this binds

NIST IR 8547 is an INITIAL PUBLIC DRAFT (November 2024). Its dates are proposed, not settled, and every output citing this pack prints "draft". It describes the transition for US federal civilian cryptography; it is guidance, not a mandate, and produces WARN at most.

## Notes

VERIFIED 2026-09-06 against the primary PDF, nvlpubs.nist.gov NIST.IR.8547.ipd.pdf. Verified as a DRAFT: the reading is confirmed, the status of the document is not. Deprecated and disallowed are modelled as separate states using NIST's own glossary definitions.

## Rules

### ✅ `nist-112bit-signatures-deprecated-2030`

Table 2: ECDSA and RSA signatures at 112 bits of security strength are "Deprecated after 2030". Glossary: deprecated means "The algorithm and key length may be used, but the user must accept some security risk."

**Binding:** `guideline_recommendation` · **Verdict:** `WARN` · **Rationale:** `unstated` · **Deadline:** 2030-12-31 (deprecated)

**Migration target:** `ML-DSA-65`

**Source:** [NIST IR 8547 ipd, Transition to Post-Quantum Cryptography Standards, §4.1.1 Table 2](https://nvlpubs.nist.gov/nistpubs/ir/2024/NIST.IR.8547.ipd.pdf) — Initial Public Draft, November 2024
**Verified:** 2026-09-06 by Sadjad Asadi

!!! warning "Draft source"
    This rule cites a document that is still a draft. Its dates are proposed and may move.

### ✅ `nist-signatures-disallowed-2035`

Table 2: quantum-vulnerable signatures (ECDSA, EdDSA, RSA) are "Disallowed after 2035" at every security strength. Glossary: disallowed means "The algorithm or key length is no longer allowed for applying cryptographic protection."

**Binding:** `guideline_recommendation` · **Verdict:** `WARN` · **Rationale:** `unstated` · **Deadline:** 2035-12-31 (disallowed)

**Migration target:** `ML-DSA-65`

**Source:** [NIST IR 8547 ipd §4.1.1 Table 2](https://nvlpubs.nist.gov/nistpubs/ir/2024/NIST.IR.8547.ipd.pdf) — Initial Public Draft, November 2024
**Verified:** 2026-09-06 by Sadjad Asadi

!!! warning "Draft source"
    This rule cites a document that is still a draft. Its dates are proposed and may move.

### ✅ `nist-112bit-key-establishment-deprecated-2030`

Table 4: finite-field DH/MQV, EC DH/MQV and RSA key establishment at 112 bits of security strength are "Deprecated after 2030".

**Binding:** `guideline_recommendation` · **Verdict:** `WARN` · **Rationale:** `harvest_now_decrypt_later` · **Deadline:** 2030-12-31 (deprecated)

**Migration target:** `ML-KEM-768`

**Source:** [NIST IR 8547 ipd §4.1.2 Table 4](https://nvlpubs.nist.gov/nistpubs/ir/2024/NIST.IR.8547.ipd.pdf) — Initial Public Draft, November 2024
**Verified:** 2026-09-06 by Sadjad Asadi

!!! warning "Draft source"
    This rule cites a document that is still a draft. Its dates are proposed and may move.

### ✅ `nist-key-establishment-disallowed-2035`

Table 4: quantum-vulnerable key establishment is "Disallowed after 2035" at every security strength.

**Binding:** `guideline_recommendation` · **Verdict:** `WARN` · **Rationale:** `harvest_now_decrypt_later` · **Deadline:** 2035-12-31 (disallowed)

**Migration target:** `ML-KEM-768`

**Source:** [NIST IR 8547 ipd §4.1.2 Table 4](https://nvlpubs.nist.gov/nistpubs/ir/2024/NIST.IR.8547.ipd.pdf) — Initial Public Draft, November 2024
**Verified:** 2026-09-06 by Sadjad Asadi

!!! warning "Draft source"
    This rule cites a document that is still a draft. Its dates are proposed and may move.

---

Sourcing, open questions and the verification log for this pack are in [Policy sources](../policy-sources.md).
