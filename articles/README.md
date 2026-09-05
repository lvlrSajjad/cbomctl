# Article plan (Phase 3 inputs)

Revised after the competitive review. Voice: practitioner, direct, no hype.
900–1400 words. Each ends with a runnable demo.

**Blocking dependency:** articles 1 and 3 make regulatory claims. Neither can be
published until [`docs/policy-sources.md`](../docs/policy-sources.md) is
verified — especially ANSSI **F4**, which may require conceding a point in
article 3.

## 1. "One CBOM, three verdicts: why Germany, France and Australia disagree about hybrid PQC" *(lead)*

The launch piece. BSI and ANSSI recommend hybrid key establishment; ASD
recommends against it; CNSA 2.0 wants ML-KEM-1024 where others accept -768. Show
the contradiction on one real CBOM, then show the satisfies-all target and its
cost.

Demo: `cbomctl verdict … --jurisdictions bsi-de,anssi-fr,asd-au,cnsa-2.0`.

**Two things this article must not do.** It must not say any of these
authorities *mandate* hybrid — BSI and ANSSI recommend, and getting that wrong
is the error the review caught in our own drafts, which is itself worth a
paragraph. And it must not claim nobody else evaluates multiple jurisdictions:
[`open-quantum-secure`](https://github.com/jimbo111/open-quantum-secure) ships
seven frameworks and documents the divergence in its README. The honest claim is
narrower — conflict as a computed artifact, over a CBOM you did not generate.
Link them generously; anyone who checks will find them anyway, and being the
person who pointed at the prior art is a better position than being the person
who didn't.

## 2. "Deprecated is not disallowed: reading NIST IR 8547 correctly"

The most commonly misstated point in PQC compliance. IR 8547 is still an
**initial public draft**; its 2030/2035 dates are *proposed*; and *deprecated*
(discouraged, still permitted) and *disallowed* (not permitted) are different
states that vendor marketing routinely collapses into "banned by 2030".

No conflict framing, no product pitch until the last paragraph. This is the
piece most likely to be linked by people who care about being right, and its
credibility depends on not selling anything.

Demo: two assets, one deprecated and one disallowed, rendering differently.

## 3. "Signatures aren't urgent — but they aren't simple"

Retitled from "Your CBOM is not a plan", and it is a better article for it. The
nuance here is exactly what practitioners get wrong in both directions.

**Part one — the urgency argument.** Key establishment is time-critical because
of harvest-now-decrypt-later: an adversary recording ciphertext today reads it
the day a CRQC exists, so the exposure window is already open. Signatures cannot
be harvested. Forging one requires the quantum computer to exist at the moment
of forgery, so a TLS handshake signature verified in 2026 and discarded carries
essentially no retroactive risk. Signatures can wait — **unless the signed thing
is long-lived**: firmware, code signing, document signing, root CAs, where the
artifact stays trusted for years or decades after issuance.

**Part two — the assurance argument, which cuts the other way.** ANSSI
recommends hybrid constructions for signatures too, and the reason is not
timing. ML-DSA and SLH-DSA are young. During the NIST competition **Rainbow** was
broken by classical cryptanalysis, and **SIKE** was broken outright by a
classical attack after reaching the fourth round. Keeping a classical signature
alongside the post-quantum one hedges against the new scheme turning out to be
wrong — a risk that has nothing to do with quantum computers and does not
diminish as the CRQC date approaches.

**The point of the article:** these are orthogonal. Urgency answers *when must I
move*; assurance answers *what must I move to*. A signature can be low urgency
and still need a hybrid target. Most readers will have collapsed them into one
axis, and most tools do too.

Demo: `cbomctl verdict` showing a signature asset ranked low urgency while
`anssi-fr` still requires a hybrid target, with the `rationale` field naming
`algorithm_maturity` as the reason.

**Verify before publishing:** ANSSI F4 (the signature-hybrid stance and its
stated reasoning), and BSI's 2026-01 signature-hybrid language, which may or may
not mirror its key-agreement position.

## Dropped

- **"Gate your CI on quantum risk in 20 minutes"** — CI gating is well covered
  by `sbom-tools` and `open-quantum-secure`. Writing a tutorial for a commodity
  feature invites the comparison we lose.
- **"sbom-tools says FAIL. Now what?"** — written for the previous positioning,
  where we were the layer above one specific tool. We are not.

## Outreach

- Show HN draft — Phase 3, not yet written
- [PKI Consortium CfP abstract](../outreach/pki-consortium-cfp.md)
- [CycloneDX Tool Center PR](../outreach/cyclonedx-tool-center-pr.md)

LinkedIn and dev.to variants of article 1 once it is verified and published.
