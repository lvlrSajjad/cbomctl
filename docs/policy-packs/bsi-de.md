# BSI — Germany

`bsi-de` · pack version 1.0.0 · ✅ **Verified**

## Who this binds

BSI TR-02102-1 is a Technical Guideline. Its operative verb throughout is "recommends" — it is not a statute, and this pack therefore produces WARN, not FAIL. Verified against the English edition, Version 2026-01, dated January 23 2026.

## Notes

VERIFIED 2026-09-06 against the primary PDF (bsi.bund.de, TG02102/BSI-TR-02102-1.pdf, Version 2026-01). Section numbers and quoted sentences are in docs/policy-sources.md.

## Rules

### ✅ `bsi-classical-key-agreement-sunset`

Sole use of classical key agreement is recommended only until the end of 2031. §2.1: "The sole use of classic key agreement mechanisms is only recommended until the end of 2031."

**Binding:** `guideline_recommendation` · **Verdict:** `WARN` · **Hybrid:** `recommended` · **Rationale:** `harvest_now_decrypt_later` · **Deadline:** 2031-12-31 (disallowed)

> §2.1 names the mechanism explicitly: "encrypted data can already be stored for later decryption ('Store Now, Decrypt Later')".

**Migration target:** `ML-KEM-768` · as `hybrid`

**Source:** [BSI TR-02102-1, Cryptographic Mechanisms: Recommendations and Key Lengths, §2.1](https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Publications/TechGuidelines/TG02102/BSI-TR-02102-1.pdf) — 2026-01 (January 23, 2026)
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `bsi-high-protection-2030`

Applications with very high protection requirements should complete the transition by the end of 2030. §2.1: "For applications with very high protection requirements, the transition to quantum-safe mechanisms should already take place by the end of 2030."

**Binding:** `guideline_recommendation` · **Verdict:** `WARN` · **Hybrid:** `recommended` · **Rationale:** `harvest_now_decrypt_later` · **Deadline:** 2030-12-31 (complete)

**Source:** [BSI TR-02102-1 §2.1](https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Publications/TechGuidelines/TG02102/BSI-TR-02102-1.pdf) — 2026-01 (January 23, 2026)
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `bsi-hybrid-key-agreement`

Quantum-safe key agreement mechanisms should be used in hybrid form. §2.1: "The quantum-safe mechanisms recommended in Section 2.4 should be used in 'hybrid' form, i.e., in a suitable combination with a classical method."

**Binding:** `guideline_recommendation` · **Verdict:** `WARN` · **Hybrid:** `recommended` · **Rationale:** `algorithm_maturity`

**Migration target:** `ML-KEM-768` · as `hybrid`

**Source:** [BSI TR-02102-1 §2.1, §2.2 (Key Derivation and Hybridisation)](https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Publications/TechGuidelines/TG02102/BSI-TR-02102-1.pdf) — 2026-01 (January 23, 2026)
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `bsi-classical-signatures-2035`

Classical signature mechanisms are recommended only until the end of 2035, following the EU roadmap. §2.1: "the use of classic signature mechanisms is therefore only recommended until the end of 2035."

**Binding:** `guideline_recommendation` · **Verdict:** `WARN` · **Rationale:** `policy_alignment` · **Deadline:** 2035-12-31 (disallowed)

> §2.1 states the urgency asymmetry directly: "In contrast to key agreement, classic signatures are still trustworthy as long as no cryptographically relevant quantum computer exists." The later horizon (2035 vs 2030/2031) follows from that, and follows the EU roadmap.

**Migration target:** `ML-DSA-65`

**Source:** [BSI TR-02102-1 §2.1](https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Publications/TechGuidelines/TG02102/BSI-TR-02102-1.pdf) — 2026-01 (January 23, 2026)
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `bsi-hybrid-signatures`

Quantum-safe signature schemes are recommended only in combination with a classical signature scheme. §5.3.4: "This Technical Guideline recommends the use of a quantum-safe signature scheme only in combination with a classic signature scheme."

**Binding:** `guideline_recommendation` · **Verdict:** `WARN` · **Hybrid:** `recommended` · **Rationale:** `algorithm_maturity`

> Not a harvest argument — §2.1 says classic signatures stay trustworthy until a CRQC exists. §5.3.4 asks that hybridisation "be implemented in such a way that the hybrid signature scheme is secure as long as at least one of the schemes is secure", i.e. it hedges against the new scheme being wrong.

**Migration target:** `ML-DSA-65` · as `hybrid`

**Source:** [BSI TR-02102-1 §5.3.4, Quantum-Safe Signature Schemes](https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Publications/TechGuidelines/TG02102/BSI-TR-02102-1.pdf) — 2026-01 (January 23, 2026)
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `bsi-hash-based-standalone-permitted`

Hash-based signature schemes may be used standalone, not in hybrid form. §5.3.4: "hash-based signatures can, provided that the implementation security of stateful and stateless hash-based mechanisms is carefully considered, in principle also be used alone (i.e. not in hybrid form)."

**Binding:** `guideline_recommendation` · **Verdict:** `INFO` · **Hybrid:** `silent` · **Rationale:** `algorithm_maturity`

> §5.3.4: "The security of hash-based signature schemes is only based on complexity-theoretical assumptions about cryptographic hash functions." Recorded as an explicit permission so a hash-based signature does not inherit the hybrid recommendation from bsi-hybrid-signatures.

**Source:** [BSI TR-02102-1 §5.3.4](https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Publications/TechGuidelines/TG02102/BSI-TR-02102-1.pdf) — 2026-01 (January 23, 2026)
**Verified:** 2026-09-06 by Sadjad Asadi

---

Sourcing, open questions and the verification log for this pack are in [Policy sources](../policy-sources.md).
