# cbomctl

**One CBOM. Every jurisdiction's verdict. And where they contradict.**

Germany, France and the EU recommend hybrid post-quantum key exchange.
Australia recommends against it. The NSA wants the highest parameter sets and,
on current reading, does not permit hybrids on mission systems at all. If you
ship into more than one of those markets, those are not independent
checkboxes — and no tool will show you the collision.

`cbomctl` takes a CBOM from any generator, runs it against several national PQC
policies at once, and reports the matrix and the conflicts.

!!! warning "Pre-release"
    All seven policy packs have been read from their primary sources, and every
    rule cites the section or page it came from. Still not compliance advice —
    read the sources before acting on a verdict.

<!-- cbomctl: verdict tests/fixtures/conflict-hybrid.json -j bsi-de,anssi-fr,asd-au,cnsa-2.0 | head -30 -->
```
ASSET           PURPOSE        bsi-de    anssi-fr  asd-au    cnsa-2.0
───────────────────────────────────────────────────────────────────────
ECDH            key-agreement  WARN      WARN      WARN      FAIL        ⚠ c1
                └ bsi-de · disallowed 2031-12-31
                └ anssi-fr · complete 2030-12-31
                └ asd-au · disallowed 2030-12-31 · complete 2030-12-31
                └ cnsa-2.0 · disallowed 2030-12-31 · exclusive_use 2031-12-31
                └ src/payments/legacy.go:12
X25519MLKEM768  key-agreement  PASS      PASS      WARN      FAIL        ⚠ c2,c3
                └ asd-au · deprecated 2030-12-31
                └ src/payments/tls.go:88
ML-DSA-65       signature      WARN      WARN      WARN      FAIL        ⚠ c4,c5
                └ asd-au · deprecated 2030-12-31
                └ src/payments/sign.go:7
RSA-2048        ambiguous      INDET     INDET     INDET     INDET
                └ unresolved: purpose-ambiguous (primitive:pke)
                └ as key transport → critical · as signature → medium
                └ Declare the purpose in cbomctl.yaml, or regenerate the CBOM with a generator that records
                  cryptoFunctions.
                └ src/payments/keys.go:41

CONFLICTS (5)
  c1  [construction]  ECDH
      anssi-fr, bsi-de recommend a hybrid construction for key-agreement; asd-au recommend
      against it; cnsa-2.0 does not permit one outside named interoperability exceptions.
      cnsa-2.0 does not permit a hybrid construction outside named interoperability exceptions,
      while anssi-fr, bsi-de recommend one. **No single configuration satisfies all selected
      jurisdictions.** You will need different builds, or to drop a jurisdiction from scope.
      asd-au would permit a hybrid but recommends against it, so even dropping cnsa-2.0 leaves a
      documented cost. This is a business decision, not a technical one.
```

## Three things it does that inventory tools cannot

**It knows what the data is worth.** A CBOM says you use ECDH. It cannot say
that this particular ECDH protects payment records with a 25-year retention
requirement — that comes from you, in `cbomctl.yaml`, and it is what decides
whether a finding is urgent or routine.

**It knows that guidance is not law.** Every rule carries a `binding` value,
from `statute` down to `guideline_recommendation`, and that — not severity —
decides `FAIL` versus `WARN`. A guideline that *recommends* cannot fail your
build. See [Policy packs](policy-packs/index.md).

**It refuses to guess.** In CBOMkit's published Keycloak CBOM, 8 of 22
algorithm components carry no usable indication of what the key is for. Those
are reported unresolved, with the range they would span if guessed — for an
ambiguous RSA key that range is the entire severity scale. See
[Why purpose is hard](purpose.md).

## Start here

- [Quickstart](quickstart.md) — install, first verdict, `cbomctl.yaml`
- [Urgency and assurance](concepts.md) — why key exchange and signatures need
  different answers to different questions
- [Policy packs](policy-packs/index.md) — what each authority actually says
- [CI integration](ci.md) — the GitHub Action and exit codes
