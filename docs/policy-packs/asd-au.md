# ASD / ACSC — Australia

`asd-au` · pack version 1.0.0 · ✅ **Verified**

## Who this binds

The ISM is ASD's guidance for Australian government entities and their suppliers. Its controls are written as statements of fact ("... is used"), and Australian government entities are expected to comply; it is not a statute. Treated as guideline_recommendation, so this pack produces WARN.

## Notes

VERIFIED 2026-09-06 against the ISM Guidelines for Cryptography as published on cyber.gov.au, page last updated 03 September 2026 (controls dated up to Sep-26). The ISM is revised roughly monthly, so this pack goes stale faster than the others -- re-verify quarterly and update source_edition.

## Rules

### ✅ `asd-classical-asymmetric-2030`

RSA, DH, ECDH and ECDSA are each withdrawn after 2030. The ISM states separately for each: "Taking into account projected technological advances in quantum computing, [RSA / DH / ECDH / ECDSA] will not be approved beyond 2030."

**Binding:** `guideline_recommendation` · **Verdict:** `WARN` · **Rationale:** `harvest_now_decrypt_later` · **Deadline:** 2030-12-31 (disallowed)

> The ISM's stated reason is Shor: "One known quantum attack (using Shor's algorithm) effectively defeats all traditional cryptography that relies upon asymmetric cryptographic algorithms such as DH, ECDH, ECDSA or RSA."

**Migration target:** `ML-KEM-1024` · `ML-DSA-87` · as `pure-pqc`

**Source:** [ASD Information Security Manual, §Guidelines for Cryptography — approved asymmetric algorithms](https://www.cyber.gov.au/business-government/asds-cyber-security-frameworks/ism/cyber-security-guidelines/guidelines-for-cryptography) — ISM as published 2026-09-03
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `asd-hybrid-not-recommended`

"The use of post-quantum traditional hybrid schemes is not recommended; however, it is not prohibited."

**Binding:** `guideline_recommendation` · **Verdict:** `WARN` · **Hybrid:** `not_recommended` · **Rationale:** `algorithm_maturity`

> ASD accepts the European premise and rejects the trade. It grants the benefit -- hybrids have "the advantage of the security offered by the traditional cryptographic algorithm if the post-quantum cryptographic algorithm is vulnerable to an implementation flaw or new attack" -- then weighs it against "increased complexity, making maintenance, analysis and secure implementation more difficult, as well as having greater computational and bandwidth overheads", and adds that "in the presence of a CRQC, the security of such schemes is reduced to that provided by the post-quantum cryptographic algorithm. As such, there is no practical value in the use of such schemes in the presence of a CRQC." So this is not a disagreement about facts; it is the same maturity argument decided the other way on cost.

**Source:** [ASD Information Security Manual, §Guidelines for Cryptography — post-quantum traditional hybrid schemes](https://www.cyber.gov.au/business-government/asds-cyber-security-frameworks/ism/cyber-security-guidelines/guidelines-for-cryptography) — ISM as published 2026-09-03
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `asd-mlkem768-2030`

"For interoperability and maintainability reasons, ML-KEM-768 will not be approved beyond 2030." ML-KEM-768 and ML-KEM-1024 are both approved now, "preferably ML-KEM-1024".

**Binding:** `guideline_recommendation` · **Verdict:** `WARN` · **Rationale:** `key_length` · **Deadline:** 2030-12-31 (deprecated)

> Stated as interoperability and maintainability, not security. Contrast BSI and ANSSI, which accept ML-KEM-768 without a sunset.

**Migration target:** `ML-KEM-1024`

**Source:** [ASD Information Security Manual, §Guidelines for Cryptography — ML-KEM](https://www.cyber.gov.au/business-government/asds-cyber-security-frameworks/ism/cyber-security-guidelines/guidelines-for-cryptography) — ISM as published 2026-09-03
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `asd-mldsa65-2030`

"For interoperability and maintainability reasons, ML-DSA-65 will not be approved beyond 2030." ML-DSA-65 and ML-DSA-87 are both approved now, "preferably ML-DSA-87".

**Binding:** `guideline_recommendation` · **Verdict:** `WARN` · **Rationale:** `key_length` · **Deadline:** 2030-12-31 (deprecated)

**Migration target:** `ML-DSA-87`

**Source:** [ASD Information Security Manual, §Guidelines for Cryptography — ML-DSA](https://www.cyber.gov.au/business-government/asds-cyber-security-frameworks/ism/cyber-security-guidelines/guidelines-for-cryptography) — ISM as published 2026-09-03
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `asd-sha256-aes128-2030`

"For interoperability and maintainability reasons, SHA-224 and SHA-256 will not be approved beyond 2030" and "AES-128 and AES-192 will not be approved beyond 2030"; likewise HMAC-SHA256.

**Binding:** `guideline_recommendation` · **Verdict:** `WARN` · **Rationale:** `key_length` · **Deadline:** 2030-12-31 (deprecated)

> Notable and stricter than any other pack here, and explicitly NOT a quantum argument: "The impact of quantum attacks on hashing algorithms and symmetric cryptographic algorithms, such as SHA-2 and AES, is unlikely to be felt for some time. However, for interoperability reasons" new equipment intended for use beyond 2030 "should support SHA-384, SHA-512 and AES-256." Our scorer still bands these low, correctly — the deadline is real but the quantum risk is not.

**Migration target:** `AES-256` · `SHA-384`

**Source:** [ASD Information Security Manual, §Guidelines for Cryptography — hashing and symmetric algorithms](https://www.cyber.gov.au/business-government/asds-cyber-security-frameworks/ism/cyber-security-guidelines/guidelines-for-cryptography) — ISM as published 2026-09-03
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `asd-pqc-support-by-2030`

"The development and procurement of new cryptographic equipment, applications and libraries ensures support for the use of ML-DSA-87, ML-KEM-1024, SHA-384, SHA-512 and AES-256 by no later than 2030."

**Binding:** `guideline_recommendation` · **Verdict:** `WARN` · **Rationale:** `harvest_now_decrypt_later` · **Deadline:** 2030-12-31 (complete)

**Migration target:** `ML-KEM-1024` · `ML-DSA-87` · `AES-256` · `SHA-384`

**Source:** [ASD Information Security Manual, §Guidelines for Cryptography — transitioning to post-quantum cryptography](https://www.cyber.gov.au/business-government/asds-cyber-security-frameworks/ism/cyber-security-guidelines/guidelines-for-cryptography) — ISM as published 2026-09-03
**Verified:** 2026-09-06 by Sadjad Asadi

---

Sourcing, open questions and the verification log for this pack are in [Policy sources](../policy-sources.md).
