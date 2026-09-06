# Why purpose is hard

Everything in the risk model depends on one question — *what is this key
for?* — and real CBOMs frequently do not answer it.

## What real generator output looks like

From CBOMkit's published Keycloak CBOM: 56 components, 22 of asset type
`algorithm`.

| observation | count | consequence |
|---|---|---|
| `cryptoFunctions` absent entirely | 6 / 22 | it cannot be the only signal |
| `cryptoFunctions: [keygen]` and nothing else | 12 occurrences | `keygen` is **purpose-neutral** — generating a key says nothing about what the key does |
| `primitive: other` | 4 | includes `AES` and `HMACSHA2` |
| `primitive: pke` on EC keys | 5 | `EC-secp256r1/384r1/521r1`, which in Keycloak are ECDSA and ECDH |

Two consequences invalidate the obvious implementation.

**Trusting `primitive` produces confident wrong answers.** Mapping
`pke → encryption` reports five Keycloak EC keys as harvest-now-decrypt-later
exposures that they are not.

**`cryptoFunctions` is mostly `keygen`**, the most common value in the sample
and the least informative one.

None of this is a defect in CBOMkit. Static analysis of a call site genuinely
cannot always tell you what a key is for. The right response is to say so.

## The resolution ladder

The first signal that *decides* wins; the others are kept and reported.

1. **`cryptoFunctions`, purpose-bearing values only.** `encrypt`/`decrypt`,
   `sign`/`verify`, `encapsulate`/`decapsulate`, `digest`, `tag`, `keyderive`.
   `keygen`, `other` and `unknown` are neutral — they neither decide nor block
   a lower signal from deciding.
2. **`primitive`.** Clean for `key-agree`, `kem`, `signature`, `hash`, `mac`,
   `kdf`, `drbg` and the cipher families. **`pke` resolves to `ambiguous`**, not
   `encryption`.
3. **`oid`**, for identity always — but for purpose *only* when the OID names a
   use rather than an algorithm.
4. **`name`**, last resort, mainly to recover parameters baked into strings
   like `AES128-CBC-PKCS5` or `EC-secp521r1`.

### The OID trap

| OID | | resolves purpose? |
|---|---|---|
| `1.3.132.1.12` | ECDH | ✅ key agreement |
| `1.2.840.113549.1.1.10` | RSASSA-PSS | ✅ signature |
| `1.2.840.10045.2.1` | id-ecPublicKey | ❌ identity only — EC keys sign *and* agree |
| `1.2.840.113549.1.1.1` | rsaEncryption | ❌ identity only |

`rsaEncryption` is the trap. Despite the name, it tags every RSA key in
existence, signing keys included. Reading purpose out of it is exactly the guess
this tool refuses to make.

### The plausibility guard

A higher-precedence signal can still be wrong in a way the ladder alone cannot
catch. CBOMkit tags `AES` with `cryptoFunctions: ["decapsulate"]`. Taken at face
value that resolves a block cipher to key agreement — confidently, with
harvest-now-decrypt-later weighting attached.

A symmetric cipher cannot perform key agreement. So when a signal claims
something an algorithm family cannot do, the result is `ambiguous` with the
disagreement recorded, not a wrong answer delivered with certainty. Families
that genuinely are dual-use — RSA, bare EC — are unconstrained.

### Deliberately excluded

CBOMkit records the originating API call in
`evidence.occurrences[].additionalContext` — Keycloak's `ECDH` entry carries
`javax.crypto.KeyAgreement#getInstance(...)`, which is a *better* purpose signal
than anything in `cryptoProperties`. It is still inference from a call site, and
a normalizer that silently promotes a guess to a verdict is the thing this tool
exists to replace. It is captured as corroboration, shown in reports, and never
allowed to decide.

## Three ways to not answer

| | trigger | exit |
|---|---|---|
| `unscored` | purpose is `unknown` or `ambiguous` | 3 under `--strict` |
| `indeterminate` | a rule needs a fact you did not declare | 3 under `--strict` |
| `not-applicable` | the pack demonstrably does not bind you | never |

Defaulting unknown to *low* hides exposure behind a green build. Defaulting to
*high* trains people to ignore the output. The honest answer sends the user
where the answer actually lives:

<!-- cbomctl: verdict tests/fixtures/purpose-ambiguous.json -j bsi-de,anssi-fr,asd-au,cnsa-2.0 | head -8 -->
```
ASSET     PURPOSE    bsi-de    anssi-fr  asd-au    cnsa-2.0
─────────────────────────────────────────────────────────────
RSA-2048  ambiguous  INDET     INDET     INDET     INDET
          └ unresolved: purpose-ambiguous (primitive:pke)
          └ as key transport → critical · as signature → medium
          └ Declare the purpose in cbomctl.yaml, or regenerate the CBOM with a generator that records
            cryptoFunctions.
          └ src/payments/keys.go:41
```

The gap between those two readings is the entire severity scale. That is why
guessing would be indefensible, and why more than a third of a real Keycloak
CBOM lands in this section rather than in a verdict.
