# EU Coordinated Implementation Roadmap

`eu-roadmap` · pack version 1.0.0 · ✅ **Verified**

## Who this binds

A coordinated Member State planning roadmap, not a Regulation. Its language is "it is recommended"; a Commission Recommendation is non-binding on operators under TFEU Art. 288. Every rule here caps at WARN. If NIS2 or DORA pull these dates into binding obligations for in-scope entities, that warrants a separate pack rather than a change here.

## Notes

VERIFIED 2026-09-06 against the primary PDF, "A Coordinated Implementation Roadmap for the Transition to Post-Quantum Cryptography", Part 1, Version 1.1, dated 11.06.2025. A companion FAQ (NIS CG, 15.04.2026) also exists and is not yet mined. Risk tiers (high / medium / low) are not derivable from a CBOM and must be declared as system_category.

## Rules

### ✅ `eu-high-risk-2030`

§"Recommended Timeline": "high-risk use cases should be transitioned to PQC as soon as possible, no later than the end of 2030." Elaborated later: "For high-risk use cases, quantum-vulnerable public-key mechanisms shall not be used stand-alone after the end of 2030."

**Binding:** `guideline_recommendation` · **Verdict:** `WARN` · **Hybrid:** `recommended` · **Rationale:** `harvest_now_decrypt_later` · **Deadline:** 2030-12-31 (complete)

**Migration target:** `ML-KEM-768` · `ML-DSA-65` · as `hybrid`

**Source:** [A Coordinated Implementation Roadmap for the Transition to Post-Quantum Cryptography, Part 1 §Recommended Timeline](https://digital-strategy.ec.europa.eu/en/library/coordinated-implementation-roadmap-transition-post-quantum-cryptography) — Part 1, Version 1.1, 11.06.2025
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `eu-medium-risk-2035`

"For high-risk use cases, quantum-vulnerable public-key mechanisms shall not be used stand-alone after the end of 2030, analogously after the end of 2035 for medium-risk use cases."

**Binding:** `guideline_recommendation` · **Verdict:** `WARN` · **Hybrid:** `recommended` · **Rationale:** `unstated` · **Deadline:** 2035-12-31 (complete)

**Source:** [EU Coordinated Implementation Roadmap Part 1, §Hybrid solutions](https://digital-strategy.ec.europa.eu/en/library/coordinated-implementation-roadmap-transition-post-quantum-cryptography) — Part 1, Version 1.1, 11.06.2025
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `eu-hybrid-recommended`

"…it is recommended to use standardised and tested hybrid solutions, whenever feasible and suitable. In particular, whenever a quantum-vulnerable public-key cryptographic mechanism, such as RSA or any discrete logarithm based mechanism, is currently used, replacing it by a standardized hybrid combination which includes PQC should be considered."

**Binding:** `guideline_recommendation` · **Verdict:** `WARN` · **Hybrid:** `recommended` · **Rationale:** `unstated`

> The roadmap gives no explicit reason for preferring hybrids, unlike BSI and ANSSI which both cite scheme immaturity. Recorded as `unstated` rather than assumed to match them.

**Migration target:** as `hybrid`

**Source:** [EU Coordinated Implementation Roadmap Part 1, §Hybrid solutions](https://digital-strategy.ec.europa.eu/en/library/coordinated-implementation-roadmap-transition-post-quantum-cryptography) — Part 1, Version 1.1, 11.06.2025
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `eu-transition-start-2026`

"it is recommended that all Member States initiate a national PQC transition strategy following First Steps by the end of 2026 and coordinate their efforts at the EU level."

**Binding:** `guideline_recommendation` · **Verdict:** `INFO` · **Rationale:** `unstated` · **Deadline:** 2026-12-31 (transition_start)

**Source:** [EU Coordinated Implementation Roadmap Part 1, §Executive Summary](https://digital-strategy.ec.europa.eu/en/library/coordinated-implementation-roadmap-transition-post-quantum-cryptography) — Part 1, Version 1.1, 11.06.2025
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `eu-remainder-2035`

"By 2035, the transition should be completed for as many systems as practically feasible."

**Binding:** `guideline_recommendation` · **Verdict:** `WARN` · **Rationale:** `unstated` · **Deadline:** 2035-12-31 (complete)

> "as many systems as practically feasible" is not a hard deadline. WARN, never FAIL.

**Source:** [EU Coordinated Implementation Roadmap Part 1, §Executive Summary](https://digital-strategy.ec.europa.eu/en/library/coordinated-implementation-roadmap-transition-post-quantum-cryptography) — Part 1, Version 1.1, 11.06.2025
**Verified:** 2026-09-06 by Sadjad Asadi

### ✅ `eu-firmware-upgrade-signatures`

"products entering the market with an expected lifetime beyond 2030 should be upgradable to PQC and … the upgrade mechanism for software and firmware upgrades should incorporate post-quantum signature schemes for integrity and authenticity."

**Binding:** `guideline_recommendation` · **Verdict:** `WARN` · **Rationale:** `unstated` · **Deadline:** 2030-12-31 (complete)

> Primary-source support for the long-lived-verification carve-out in our scoring: firmware signing is the case where a signature's trust horizon, not the data's confidentiality horizon, drives urgency.

**Migration target:** `ML-DSA-65`

**Source:** [EU Coordinated Implementation Roadmap Part 1, §Recommended Timeline](https://digital-strategy.ec.europa.eu/en/library/coordinated-implementation-roadmap-transition-post-quantum-cryptography) — Part 1, Version 1.1, 11.06.2025
**Verified:** 2026-09-06 by Sadjad Asadi

---

Sourcing, open questions and the verification log for this pack are in [Policy sources](../policy-sources.md).
