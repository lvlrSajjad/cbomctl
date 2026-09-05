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
    Six of seven policy packs have been read from their primary sources.
    `cnsa-2.0` has not — NSA's servers refuse automated access — and every
    output computed from it carries a visible banner. Not compliance advice.

```
ASSET           PURPOSE        bsi-de    anssi-fr  asd-au    cnsa-2.0
X25519MLKEM768  key-agreement  PASS      PASS      WARN      FAIL      ⚠ c3,c4
ECDH            key-agreement  WARN      WARN      WARN      FAIL      ⚠ c1,c2
RSA             ambiguous      INDET     INDET     INDET     INDET

CONFLICTS
  c3  [construction]  X25519MLKEM768
      anssi-fr, bsi-de recommend a hybrid construction for key-agreement;
      asd-au, cnsa-2.0 do not permit one.
      No single configuration satisfies all selected jurisdictions.
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
