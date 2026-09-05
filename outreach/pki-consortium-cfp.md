# CfP abstract — PKI Consortium PQC Conference

**DRAFT — do not submit until the policy packs are verified.** The talk asserts
what four authorities say; giving it on unverified sources would be indefensible
in that room.

- **Event:** PKI Consortium Post-Quantum Cryptography Conference, Amsterdam,
  December 1–3 2026
- **Verify before submitting:** CfP deadline, submission portal, format
  (talk length, slots), and whether the event is vendor-neutral by policy — the
  PKI Consortium generally is, which suits a talk with no product pitch in it.
- **Proposed title:** *Contradictory by design: what to do when Germany, France
  and Australia disagree about hybrid PQC*
- **Length:** ~300 words

---

## Abstract

Post-quantum guidance has diverged, and the divergence is not noise. Germany's
BSI recommends hybrid key establishment during the transition. France's ANSSI
strongly recommends it, and requires it for certain certifications. Australia's
ASD recommends against it — permitted, but not an end state. The NSA's CNSA 2.0
asks for ML-KEM-1024 where others accept ML-KEM-768. A vendor selling into more
than one of these markets faces requirements that cannot all be satisfied
optimally on the same key establishment path.

Most tooling models these as independent compliance checkboxes: run the profile,
get PASS or FAIL. That framing hides the interesting failure. It also tends to
report a technical guideline that *recommends* as though it were a mandate —
the distinction between a statute, an agency requirement, a certification
condition, and a recommendation is exactly what determines whether a finding
blocks a release, and it is routinely flattened.

This talk presents a deterministic, fully cited policy engine that evaluates one
CycloneDX CBOM against several national policies simultaneously and reports
where their verdicts contradict each other, why, and what target — if any —
satisfies all of them. Every rule carries its primary source, a verification
date, and an explicit classification of its binding force. Rules whose sources
are drafts say so; NIST IR 8547 remains an initial public draft, and
*deprecated* is not *disallowed*.

We will also cover what the engine refuses to do. In real CBOM output — CBOMkit's published Keycloak
inventory — more than a third of algorithm components carry no usable
indication of what a key is actually for, and the difference between key transport and signature moves a
finding across the entire severity range. Those findings are reported as
unresolved, with the range they would span if guessed. The tool and policy packs
are open source and separable — the packs are consumable without the tool.
