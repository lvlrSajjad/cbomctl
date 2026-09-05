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

Post-quantum guidance has diverged internationally, and the usual framing —
that the authorities disagree — is wrong in an interesting way. Germany's BSI
and France's ANSSI recommend hybrid key establishment, and both extend it to
signatures on the grounds that ML-DSA and SLH-DSA are young; ANSSI cites the
classical break of Rainbow directly. Australia's ASD recommends against
hybrids — while explicitly granting the same premise, that a classical
algorithm alongside a post-quantum one hedges against an implementation flaw or
a new attack. ASD simply prices complexity and overhead higher, and adds that
once a CRQC exists the classical half contributes nothing. Same risk model,
different weights, opposite conclusions.

That distinction matters to anyone shipping into more than one market, and most
tooling erases it. PASS/FAIL cannot express "discouraged but permitted" — the
wording that decides whether any single configuration satisfies every
jurisdiction. Tools also routinely report guidance as mandate. BSI TR-02102-1 is
a technical guideline; ANSSI's "mandatory hybridation" applies only inside its
security-visa process; NIST IR 8547 is an initial public draft whose 2030 dates
are proposed and reach only 112-bit security strength.

This talk presents a deterministic, fully cited policy engine that evaluates one
CycloneDX CBOM against several national policies at once and reports where their
requirements collide, why, and what target satisfies all of them — or that none
does. Every rule carries its primary source, the section read, a verification
date, and its binding force. Six of seven jurisdictions were verified by reading
the source documents; the seventh is marked unverified because its publisher
blocks automated access, and the tool says so in every output.

We will also cover what the engine refuses to do. In real CBOM output, more than
a third of algorithm components carry no usable indication of what a key is
for, and the gap between "key transport" and "signature" spans the entire
severity range. Those are reported unresolved, with the range they would span if
guessed. Tool and policy packs are open source and separable.
