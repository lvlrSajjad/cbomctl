---
title: Everyone agrees on the risk. They disagree on the price.
description: >-
  BSI, ANSSI and the EU roadmap recommend hybrid post-quantum key exchange.
  ASD recommends against it. The NSA does not permit it on national security
  systems. They are not disagreeing about cryptography.
date: 2026-09-06
---


# Everyone agrees on the risk. They disagree on the price.

!!! info "Published 2026-09-06"
    Every regulatory claim here was read from the primary document on that
    date, and each is cited in
    [the policy sources](../policy-sources.md). Guidance moves — the ASD ISM
    is revised roughly monthly — so check the sources before acting on any of
    it.

Germany's BSI recommends that post-quantum key establishment be deployed
alongside a classical algorithm. So does France's ANSSI. So does the EU's
coordinated roadmap. Australia's ASD recommends against it. The NSA says do not
use one on national security systems at all, outside named exceptions.

The obvious story is that the authorities disagree about whether hybrid
cryptography is safe. That story is wrong, and the real one is more useful.

## They are all making the same argument

Here is ANSSI, explaining why it wants a classical algorithm kept alongside the
post-quantum one:

> "even if the post-quantum algorithms have gained a lot of attention, they are
> still not mature enough to solely ensure the security. For example, several
> post-quantum schemes have suffered from classical attacks in the past years"

The citation attached to that sentence is Beullens, *Breaking Rainbow takes a
weekend on a laptop*. Rainbow and SIKE both fell to **classical** cryptanalysis
during the NIST competition — no quantum computer involved. The concern is not
that ML-KEM will be broken by a quantum computer. It is that it might be broken
by a mathematician.

BSI reaches the same place, and states the design requirement precisely:
hybridisation "should be implemented in such a way that the hybrid signature
scheme is secure as long as at least one of the schemes is secure."

Now here is ASD, the agency that recommends *against* hybrids:

> "Generally, such schemes have the advantage of the security offered by the
> traditional cryptographic algorithm if the post-quantum cryptographic
> algorithm is vulnerable to an implementation flaw or new attack."

That is ANSSI's argument, in Australia's own words, in the paragraph where it
declines to follow it. ASD is not disputing the benefit. It is pricing it:

> "This advantage comes at the cost of increased complexity, making maintenance,
> analysis and secure implementation more difficult, as well as having greater
> computational and bandwidth overheads."

And the NSA, in its CNSA 2.0 FAQ, makes the cost side explicit as an empirical
claim:

> "Because more security products fail due to implementation or configuration
> errors than failures in their underlying cryptographic algorithms, spending
> limited resources to add cryptographic complexity can at times weaken security
> rather than improve it."

So the disagreement is not about cryptography. It is a bet on which failure mode
is more likely: a new lattice scheme falling to cryptanalysis, or an engineer
misconfiguring a construction with twice the moving parts. Both are real. The
evidence for the first is Rainbow and SIKE. The evidence for the second is every
CVE ever filed against a TLS stack.

Reasonable people land differently on that, and they have.

## Which makes it your problem

None of this would matter if you shipped into one jurisdiction. The trouble is
that the requirements are not merely different — they are, in one specific
configuration, mutually unsatisfiable.

<!-- cbomctl: verdict tests/fixtures/conflict-hybrid.json -c cbomctl.yaml.example -j bsi-de,anssi-fr,eu-roadmap,asd-au,cnsa-2.0 | head -12 -->
```
ASSET           PURPOSE        bsi-de      anssi-fr    eu-roadmap  asd-au      cnsa-2.0
───────────────────────────────────────────────────────────────────────────────────────────
ECDH            key-agreement  WARN        WARN        WARN        WARN        FAIL          ⚠ c1,c2
                └ bsi-de · disallowed 2031-12-31
                └ anssi-fr · complete 2030-12-31
                └ eu-roadmap · transition_start 2026-12-31 · complete 2035-12-31
                └ asd-au · disallowed 2030-12-31 · complete 2030-12-31
                └ cnsa-2.0 · disallowed 2030-12-31 · exclusive_use 2031-12-31
                └ critical · exposure 19.0y · harvest-now-decrypt-later
                └ src/payments/legacy.go:12
X25519MLKEM768  key-agreement  PASS        PASS        PASS        WARN        FAIL          ⚠ c3,c4
                └ asd-au · deprecated 2030-12-31
```

`X25519MLKEM768` — a hybrid of X25519 and ML-KEM-768, the construction most TLS
libraries are shipping today — passes in Europe, warns in Australia, and fails
for the NSA. And the conflict section explains why, in the terms above:

<!-- cbomctl: verdict tests/fixtures/conflict-hybrid.json -c cbomctl.yaml.example -j bsi-de,anssi-fr,eu-roadmap,asd-au,cnsa-2.0 | head -34 -->
```
ASSET           PURPOSE        bsi-de      anssi-fr    eu-roadmap  asd-au      cnsa-2.0
───────────────────────────────────────────────────────────────────────────────────────────
ECDH            key-agreement  WARN        WARN        WARN        WARN        FAIL          ⚠ c1,c2
                └ bsi-de · disallowed 2031-12-31
                └ anssi-fr · complete 2030-12-31
                └ eu-roadmap · transition_start 2026-12-31 · complete 2035-12-31
                └ asd-au · disallowed 2030-12-31 · complete 2030-12-31
                └ cnsa-2.0 · disallowed 2030-12-31 · exclusive_use 2031-12-31
                └ critical · exposure 19.0y · harvest-now-decrypt-later
                └ src/payments/legacy.go:12
X25519MLKEM768  key-agreement  PASS        PASS        PASS        WARN        FAIL          ⚠ c3,c4
                └ asd-au · deprecated 2030-12-31
                └ src/payments/tls.go:88
ML-DSA-65       signature      WARN        WARN        WARN        WARN        FAIL          ⚠ c5,c6
                └ asd-au · deprecated 2030-12-31
                └ src/payments/sign.go:7
RSA-2048        ambiguous      INDET       INDET       INDET       INDET       INDET
                └ eu-roadmap · transition_start 2026-12-31
                └ unresolved: purpose-ambiguous (primitive:pke)
                └ as key transport → critical · as signature → medium
                └ Declare the purpose in cbomctl.yaml, or regenerate the CBOM with a generator that records cryptoFunctions.
                └ src/payments/keys.go:41

CONFLICTS (6)
  c1  [construction]  ECDH
      anssi-fr, bsi-de, eu-roadmap recommend a hybrid construction for key-agreement; asd-au recommend against it; cnsa-2.0 does not permit one outside named interoperability exceptions.
      cnsa-2.0 does not permit a hybrid construction outside named interoperability exceptions, while anssi-fr, bsi-de, eu-roadmap recommend one. **No single configuration satisfies all selected jurisdictions.** You will need different builds, or to drop a jurisdiction from scope. asd-au would permit a hybrid but recommends against it, so even dropping cnsa-2.0 leaves a documented cost. This is a business decision, not a technical one.
      ⚖ This conflict depends on a contested encoding. Under the alternative reading (cnsa-2.0 silent), a hybrid construction would satisfy all selected jurisdictions, at a documented cost. The argument and the evidence for the encoding used are in the `cnsa-2.0` rule's interpretation note (`cbomctl policies show cnsa-2.0`).
  c2  [deadline]  ECDH
      eu-roadmap requires this by 2026-12-31; bsi-de allows until 2031-12-31.
      satisfies all: meet the earlier date (2026-12-31)
      eu-roadmap governs in practice — the later deadline provides no relief if you are bound by both.
  c3  [construction]  X25519MLKEM768
      anssi-fr, bsi-de, eu-roadmap recommend a hybrid construction for key-agreement; asd-au recommend against it; cnsa-2.0 does not permit one outside named interoperability exceptions.
```

Two distinct collisions on one asset. The construction conflict has **no**
resolution: nothing you can build satisfies a jurisdiction that recommends
hybrids and one that does not permit them. The parameter conflict does have
one — ML-KEM-1024 clears everybody, because CNSA 2.0 requires that level "for
all classification levels" while BSI and ANSSI accept 768 without objecting to
1024. It just costs you performance nobody else asked for.

That distinction matters more than it looks. "Discouraged but not prohibited" —
ASD's actual wording — leaves a compromise available at a documented cost. "Do
not use except for those exceptions NSA specifically recommends" does not. A
tool that reports PASS/FAIL cannot tell you which situation you are in.

## The gradient, not the tribe

It is tempting to frame this as Europe versus the anglophone agencies. The
tidier reading is a three-step gradient:

| stance | who | what it means for you |
|---|---|---|
| recommended | BSI, ANSSI, EU roadmap | ship hybrid |
| not recommended, not prohibited | ASD | hybrid is allowed, at a documented cost |
| not permitted outside named exceptions | NSA (NSS only) | no compromise exists |

And the second contradiction has nothing to do with hybrids at all. BSI and
ANSSI both **exempt hash-based signatures** — SLH-DSA, XMSS, LMS — from their
hybrid recommendations, because their security rests only on hash-function
assumptions and there is no young lattice assumption to hedge. The NSA's answer
on the same family: "While SLH-DSA is hash-based, it is not part of CNSA and is
not approved for any use in NSS." Approved-standalone in two jurisdictions, not
approved at all in a third.

## What I did about it

`cbomctl` reads a CycloneDX CBOM — from CBOMkit, from a vendor, from a
procurement process — and evaluates it against several national policies at
once, reporting the matrix and the collisions.

```bash
pip install cbomctl
cbomctl verdict your-cbom.json -j bsi-de,anssi-fr,asd-au,cnsa-2.0
```

Every rule carries the document, the section or page, the date it was read, and
a `binding` classification. That last field is load-bearing: most PQC guidance
is not a mandate, and a technical guideline that *recommends* cannot produce a
`FAIL`. BSI TR-02102-1 recommends. ANSSI's "mandatory hybridation" applies only
inside its security-visa process. The EU roadmap is a Recommendation, non-binding
on operators under TFEU Art. 288. Flattening those into "mandates" is the most
common error in this space, and I made it myself in an early draft — which is
why the field exists.

All seven packs are read from primary sources. Where a source is a draft, the
tool prints "draft". And where reading it required a judgement, the tool shows
the judgement rather than hiding it behind a verdict.

That last one earns its place here. NSA's FAQ answers the hybrid question
twice, and the answers differ in force: one says only "will not require", the
other says "Do not use … except for those exceptions NSA specifically
recommends" — but sits under a question framed "while waiting for a final NIST
post-quantum standard", a premise that arguably ended when FIPS 203/204/205
were finalised in August 2024.

I encoded the stronger reading, because Ver. 2.1 is dated four months *after*
that finalisation and was demonstrably revised in the interval — it notes that
"NSA clarified the CNSA 2.0 language when the FIPS documents were published"
and discusses a FIPS 204 variant — and NSA kept the imperative through that
revision. But the encoding is a judgement, and it is the judgement that decides
whether the tool tells you a compromise exists. So the conflict says both:

```
⚖ This conflict depends on a contested encoding. Under the alternative reading
  (cnsa-2.0 silent), a hybrid construction would satisfy all selected
  jurisdictions, at a documented cost.
```

If you disagree with me, you can see exactly which sentence you would argue
with. That seems more useful than a confident answer.

It refuses to guess, too. In CBOMkit's published Keycloak CBOM, 8 of 22
algorithm components carry no usable indication of what the key is for, and for
an ambiguous RSA key the answer spans the entire severity range. Those come back
unresolved, with the range they would have spanned.

The [policy packs](https://github.com/lvlrSajjad/cbomctl/tree/main/policy-packs)
are a separately versioned artifact with their own schema and changelog. If you
want to build something else on them, take them — that is what the citations
are for.

---

*Prior art, because you will find it anyway:
[open-quantum-secure](https://github.com/jimbo111/open-quantum-secure) is a
scanner with seven compliance frameworks that documents cross-framework
divergence in its own README — running multiple jurisdictions is not a gap in
the market. What it emits is one report per framework; `cbomctl` computes the
collision, and reads a CBOM you did not generate.
[sbom-tools](https://github.com/sbom-tool/sbom-tools) does CBOM diffing and
validation better than I will.*
