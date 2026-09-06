# cbomctl — Design

> **Status:** shipped as 0.1.3. This document is the design as built;
> where it describes intent rather than code it says so. Regulatory claims
> are tracked in [`policy-sources.md`](policy-sources.md); **all seven packs
> are now verified from primary sources**, and the unverified-rule machinery
> stays in place for the next pack that is not.

## 1. What this is

`cbomctl` evaluates one CBOM against several national PQC policies at once and
reports **where their verdicts contradict each other**.

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

That matrix and that conflict block are the product. Everything else in this
document exists to make them correct.

`cbomctl` consumes a CBOM produced by any generator. It does not scan source
code, probe endpoints, or generate a CBOM.

## 2. Positioning, honestly

This is the third scoping pass, and each one narrowed the claim. What survives
is narrow, and stating it precisely is worth more than stating it broadly.

**Risk scoring by data lifetime is not a differentiator.** It ships in IBM
Quantum Safe Migration Orchestrator, SandboxAQ AQtive Guard, O3 Security, and in
open source in [`jimbo111/open-quantum-secure`](https://github.com/jimbo111/open-quantum-secure)
— which has `--data-lifetime-years`, `--sector` presets for HNDL shelf-life, and
explicit HNDL urgency classification. Keep the feature; stop selling on it.

**Multi-jurisdiction evaluation is not a differentiator either, and the review
that reached this repository did not catch that.** `open-quantum-secure` ships
seven frameworks — including `bsi-tr-02102`, `asd-ism` and `anssi-guide-pqc`,
the exact three we picked as the flagship contrast — accepts
`--compliance a,b,c` and `--compliance all`, and its README already documents
the divergence in the same terms we were planning to launch with, down to the
same worked example:

> *"Cross-framework divergence is common by design. …`X25519MLKEM768` PASSES
> ANSSI + BSI (it's the required hybrid) but FAILS CNSA 2.0 … and ASD ISM."*

So "nobody runs a CBOM against multiple national policies" is false, and the
launch narrative cannot claim it.

**What is actually unoccupied**, verified against that tool's README and command
surface:

1. **Conflict as a computed output, not a reading exercise.** Their
   multi-framework report is *"one per framework, concatenated with `---`
   separators"*. Divergence is real in the output but the user has to find it by
   diffing N reports by eye. Nothing emits a per-asset × jurisdiction matrix, a
   conflict object naming the disagreeing authorities and the reason, or a
   computed satisfies-all target.
2. **Evaluating somebody else's CBOM.** `open-quantum-secure` is a scanner: its
   compliance engine runs off its own scan. Its only `--cbom` flag is on
   `upload`. If your CBOM came from CBOMkit, or from a vendor, or from a
   procurement process, no tool currently evaluates it across jurisdictions.
3. **`binding` as a first-class field.** Every tool surveyed reports PASS/FAIL.
   None distinguishes a statute from a technical guideline that *recommends*.
   The review found our own drafts overstating guidelines as mandates — if we
   made that error with the documents in front of us, shipped tools are unlikely
   to be doing better.
4. **Refusing to guess purpose.** `unknown` and `ambiguous` as reported outcomes
   with the range they would span (§6.4).

Points 1 and 2 together are the product: **conflict analysis over a CBOM you did
not generate.** That is defensible and small. It is not "the only tool that
knows Germany and Australia disagree."

## 3. Inputs

**Primary and only required input: raw CycloneDX 1.6 / 1.7 CBOM JSON**, from
any generator — CBOMkit, cbomscanner, KeyLens, pqc-scanner,
open-quantum-secure, or hand-authored. No external tool is required to run
`cbomctl`.

**Optional adapter:** `--from sbom-tools` reads
[`sbom-tools`](https://github.com/sbom-tool/sbom-tools) normalized JSON. It is
behind a flag, has its own fixture, and creates no dependency —
`sbom-tools` is MIT, pre-1.0 (v0.2.0), and its Python binding is an in-tree
wrapper that is not published to PyPI (the `sbomtools` package that *is* on
PyPI is an unrelated project — do not depend on it).

Upstream [has now answered](https://github.com/sbom-tool/sbom-tools/issues/362).
The normalized shape is exactly as we read it from their structs, but it is
reachable only through the C ABI and the language bindings — **not** through
`sbom-tools view -o json`, which is a curated projection with no crypto fields
in it at all. Their snapshot tests pin only the top-level keys, there is no
schema version separate from the crate version, and a breaking JSON change is
permitted in any pre-1.0 minor release. So the adapter stays behind a flag and
a consumer of this path should pin their crate version.

**Data lifetimes** come from `cbomctl.yaml` or from CycloneDX component
`properties` (`cbomctl:data_lifetime_years`), so the annotation can live next to
the asset in the CBOM.

## 4. Data model

```python
class Purpose(StrEnum):
    KEY_AGREEMENT = "key-agreement"   # incl. KEM — HNDL-exposed
    ENCRYPTION    = "encryption"      # HNDL-exposed
    SIGNATURE     = "signature"
    HASH = "hash"; MAC = "mac"; KDF = "kdf"; RNG = "rng"
    AMBIGUOUS     = "ambiguous"       # a signal exists but cannot decide
    UNKNOWN       = "unknown"         # no signal at all

class Construction(StrEnum):
    CLASSICAL = "classical"; PURE_PQC = "pure-pqc"
    HYBRID    = "hybrid";    UNKNOWN  = "unknown"
```

`AMBIGUOUS` ≠ `UNKNOWN`, and neither means "probably fine": `UNKNOWN` is *the
generator recorded no purpose*; `AMBIGUOUS` is *a signal exists but cannot
separate two purposes with materially different risk*. RSA is the case — the
same key serves encryption (HNDL-exposed) and signature (not), and
`primitive: pke` has not said which.

`Construction` is the axis jurisdictions contradict each other on, so it is a
model field rather than a derived property.

Every asset carries `purpose_signal` (which CBOM field decided) and
`purpose_conflicts` (signals that disagreed, kept not discarded), so a matrix
cell traces back to the field that produced it.

## 5. Purpose normalization

Grounded in real CBOMs — CBOMkit's published
[Keycloak and Kafka](https://github.com/cbomkit/cbomkit/tree/main/example)
output and CycloneDX's `valid-cryptography-full-1.6.json`. From Keycloak
(22 algorithm components):

| observation | count | consequence |
|---|---|---|
| `cryptoFunctions` absent | 6 / 22 | cannot be the only signal |
| `cryptoFunctions: [keygen]` only | 12 | `keygen` is **purpose-neutral** |
| `primitive: other` | 4 | includes `AES` and `HMACSHA2` |
| `primitive: pke` on EC keys | 5 | in Keycloak these are ECDSA/ECDH, not encryption |

Mapping `pke → encryption` would report five Keycloak EC keys as HNDL exposures
they are not. This is not a CBOMkit defect — static analysis of a call site
genuinely cannot always tell what a key is for.

**Resolution ladder.** First signal that *decides* wins; the rest are kept.

1. **`cryptoFunctions`, purpose-bearing values only** — `encrypt`/`decrypt` →
   ENCRYPTION · `sign`/`verify` → SIGNATURE · `encapsulate`/`decapsulate` →
   KEY_AGREEMENT · `digest` → HASH · `tag` → MAC · `keyderive` → KDF.
   `keygen`, `other`, `unknown` are **neutral** — they neither decide nor block
   a lower signal. Two purpose-bearing functions from different purposes ⇒
   AMBIGUOUS.
2. **`primitive`** — `key-agree`/`kem` → KEY_AGREEMENT ·
   `block-cipher`/`stream-cipher`/`ae`/`key-wrap` → ENCRYPTION · `signature` →
   SIGNATURE · `hash`/`xof` → HASH · `mac` → MAC · `kdf` → KDF · `drbg` → RNG ·
   **`pke` → AMBIGUOUS** · `other`/`unknown`/absent → UNKNOWN · `combiner` →
   sets `construction = HYBRID`.
3. **`oid`** — identity always; purpose only when the OID is purpose-specific.
   `1.3.132.1.12` (ECDH) ✅ · `1.2.840.113549.1.1.10` (RSASSA-PSS) ✅ ·
   `1.3.101.112` (Ed25519) ✅ · `1.2.840.10045.2.1` (id-ecPublicKey) ❌ ·
   `1.2.840.113549.1.1.1` (rsaEncryption) ❌ — the generic RSA key OID despite
   the name, tagging signing keys too. Reading purpose from it is the guess this
   tool refuses to make.
4. **`name`**, last resort, mainly to recover parameters baked into strings
   (`AES128-CBC-PKCS5`, `EC-secp521r1`, `RSA-2048`).

**Excluded: `evidence.occurrences[].additionalContext`.** CBOMkit records the
originating call there — Keycloak's `ECDH` carries
`javax.crypto.KeyAgreement#getInstance(...)`, a *better* signal than anything in
`cryptoProperties`. It is still inference from a call site; captured as
corroboration, never decisive. `--infer-from-evidence` can opt in later.

**1.6 / 1.7.** 1.7 is a superset in the crypto subtree. Prefer `ellipticCurve`,
accept `curve`; note 1.7's `certificateExtensions` is X.509 extensions, a
different field from the deprecated `certificateExtension`, not a rename. An
unrecognised enum degrades to `UNKNOWN` rather than crashing.

## 6. Verdicts

### 6.1 The matrix

For each asset × selected jurisdiction, one cell:

| cell | meaning |
|---|---|
| `PASS` | no rule in this pack is violated |
| `FAIL` | a rule with `binding` of statute / executive_order / agency_requirement is violated |
| `WARN` | a `guideline_recommendation` or `certification_requirement` rule is violated |
| `INDET` | a rule needs a fact not supplied (purpose unresolvable, category undeclared) |
| `N/A` | the pack demonstrably does not bind this user |

**`FAIL` vs `WARN` is decided by the rule's `binding` field, not by severity.**
Violating a technical guideline that *recommends* hybrid is not the same as
violating a statute, and reporting both as FAIL is how a tool misinforms its
user. `--fail-on-warn` is available for teams that want recommendations to gate.

### 6.2 Conflicts

A conflict exists when two selected jurisdictions produce incompatible
*requirements* for the same asset — not merely different verdicts. Kinds:

- **`construction`** — one recommends or requires hybrid, another does not
  recommend it (BSI/ANSSI vs ASD).
- **`parameter`** — both accept the same algorithm at different strengths
  (ML-KEM-768 acceptable under BSI, CNSA 2.0 requires -1024).
- **`deadline`** — same requirement, dates far enough apart that the earlier
  governs.
- **`scope`** — one pack binds this asset and another does not.

Each conflict carries a **satisfies-all** field: the target that clears every
selected jurisdiction, or an explicit statement that none exists. Where a
construction is merely *discouraged* rather than prohibited, a satisfies-all
target may exist at a documented cost — and the tool says so rather than
pretending the tension is resolved. Choosing is a business decision.

### 6.3 Three ways to not answer

| bucket | trigger | exit |
|---|---|---|
| `unscored` | purpose `UNKNOWN` or `AMBIGUOUS` | 3 under `--strict` |
| `indeterminate` | rule needs an undeclared fact (e.g. CNSA category) | 3 under `--strict` |
| `not-applicable` | pack demonstrably does not bind | never |

Defaulting unknown to *low* hides exposure behind a green build; defaulting to
*high* trains people to ignore output. Unscored findings report the range they
would span if guessed — for `RSA-2048` with `primitive: pke`, *as key transport
→ critical, as signature → medium*. The gap between those is the entire severity
scale, which is why guessing is indefensible.

## 7. Prioritization (secondary)

`cbomctl prioritize` ranks findings by Mosca's inequality — **X** (data
lifetime, from the human) + **Y** (migration time, default 3y) > **Z** (years to
CRQC, default 2035, an assumption stamped into every output, overridable with
`--crqc-year`).

The asymmetry that drives ordering: **key agreement and encryption are urgent
now** — an adversary recording ciphertext today decrypts it when a CRQC exists,
so the window is already open. **Signatures are not harvest-now-decrypt-later** —
forging requires the CRQC to exist at the moment of forgery — *unless
verification is long-lived* (firmware, code signing, root CAs), where the
relevant horizon is `verification_lifetime_years`. Hashes are a Grover problem:
SHA-256 keeps ~128-bit quantum security and is not a migration target; SHA-1 is
a finding but a *classical* one, and reporting it as quantum risk is inflation.

### 7.1 Urgency and assurance are two axes, not one

`urgency` is derived from purpose × data lifetime, exactly as above. It answers
**when must I move**.

There is a second, independent question: **what must I move to**. ANSSI
reportedly recommends hybrid constructions for *signatures* as well as key
establishment — not on harvest grounds, since a signature cannot be harvested,
but because ML-DSA and SLH-DSA are young. The field watched **Rainbow** and
**SIKE** fall to classical attacks during the NIST competition, so the argument
is: keep a classical signature alongside the post-quantum one until the new
schemes have aged.

These are orthogonal, and both can be true of one asset:

| | question | driven by | applies to |
|---|---|---|---|
| **urgency** | when must I move? | HNDL exposure × data lifetime | key establishment and encryption; signatures only when verification is long-lived |
| **assurance** | what must I move to? | maturity of the target scheme | every purpose, signatures included |

So a TLS handshake signature can be correctly ranked *low urgency* — nothing
recorded today becomes forgeable later — and still require a hybrid target under
ANSSI, because the reason for hybrid there has nothing to do with timing. A tool
that models one axis will report one of those two facts and silently drop the
other.

Consequently `hybrid` is a **per-purpose** field on a policy rule, scoped by
`applies_to.purpose`, and every rule carries a `rationale`
(`harvest_now_decrypt_later` | `algorithm_maturity` | `key_length` |
`policy_alignment` | `unstated`). Jurisdictions differ by purpose: ANSSI
reportedly recommends hybrid for both; BSI clearly recommends it for key
agreement while its 2026-01 signature language **needs verification**; ASD
recommends against it for both; CNSA 2.0 is pure for both. A pack-level hybrid
stance would not be able to express that, which is why there isn't one.

Ranking feeds ordering inside `plan`; it does not affect a verdict.

## 8. Migration plan (secondary)

`cbomctl plan` emits an ordered plan from the verdicts and the ranking: what to
fix first, to which target, under whose deadline — ordered by exposure
descending, then earliest governing deadline, then `bom_ref` for stability.
`governing_deadline` is the earliest across selected jurisdictions.

Output is JSON, Markdown, or SARIF (**our findings only**, with `locations` from
`evidence.occurrences`, so they sit beside other tools' findings in the GitHub
Security tab rather than duplicating them). Exit: `0` pass · `1` policy failure ·
`2` usage/parse error · `3` unscored or indeterminate under `--strict`.

Deterministic: same inputs ⇒ byte-identical output.

## 9. Policy packs

Packs live in [`policy-packs/`](https://github.com/lvlrSajjad/cbomctl/tree/main/policy-packs) as a **standalone, semantically
versioned artifact** with its own schema and CHANGELOG, designed so another tool
can consume them without `cbomctl`. Full field reference in
[`policy-packs/README.md`](https://github.com/lvlrSajjad/cbomctl/blob/main/policy-packs/README.md); the two load-bearing
fields are `binding` (statute … guideline_recommendation) and `hybrid`
(required … silent). `source_url` must be a primary source from an allowlisted
host.

v0.1 packs: `bsi-de`, `anssi-fr`, `asd-au`, `cnsa-2.0`, `us-eo14412`,
`eu-roadmap`. **None is verified.** `--require-verified-policy` refuses to run
against an unverified rule; otherwise a banner prints. Rules citing a draft
source print "draft" in every output.

CNSA 2.0 categories are declared as `system_category` in `cbomctl.yaml`; when
absent the verdict is `INDET`, never informational. The January 2027 acquisition
gate is a separate rule behind `--cnsa-acquisition-gate`, because it is a
procurement condition on new NSS acquisitions rather than an algorithm deadline.

## 10. CLI

<!-- synopsis -->
```
cbomctl verdict <cbom|-> --jurisdictions bsi-de,anssi-fr,asd-au,cnsa-2.0,eu-roadmap,us-eo14412
                         [--format matrix|md|json|sarif] [--config cbomctl.yaml]
                         [--from cyclonedx|sbom-tools] [--strict]
                         [--require-verified-policy] [--fail-on-warn]
                         [--cnsa-acquisition-gate] [--crqc-year YYYY]
cbomctl prioritize <cbom|->      # Mosca ranking          (§7)
cbomctl plan <cbom|->            # ordered migration plan (§8)
cbomctl normalize <cbom|->       # purpose resolution, for debugging
cbomctl policies list | show <id>
```

## 11. Optional

**Not built.** `cbomctl plan --llm` would draft a prose narrative from findings
the deterministic core already produced — a separate extra
(`pip install cbomctl[llm]`, declared in `pyproject.toml`), consuming the
finished report object, unable to reach a scoring or policy path, and
watermarked. As of 0.1.3 neither the flag nor the module exists; the extra is
a placeholder. This paragraph is intent, not description.

## 12. Repository layout

<!-- illustrative: repository layout, not tool output. Pinned by
     tests/test_docs_layout.py, which asserts every module drawn here
     exists and that no module exists which is not drawn. -->
```
cbomctl/
├── src/cbomctl/
│   ├── cli.py                    # typer — subcommands only
│   ├── models.py
│   ├── loader/{cyclonedx.py,sbom_tools.py}
│   ├── normalize/{purpose.py,oids.py,identity.py}
│   ├── verdict/{matrix.py,conflicts.py}      # §6 — the product
│   ├── scoring/mosca.py
│   ├── plan.py
│   ├── policy/{schema.py,engine.py}          # loads ../policy-packs
│   ├── report/{matrix_text,markdown,sarif,json_out}.py
│   └── config.py
├── policy-packs/                 # standalone versioned artifact
│   ├── schema/pack.schema.json · CHANGELOG.md · README.md
│   └── packs/{bsi-de,anssi-fr,asd-au,cnsa-2.0,us-eo14412,eu-roadmap,nist-ir8547}.yaml
├── tests/fixtures/
├── action.yml · .github/workflows/ci.yml
├── cbomctl.yaml.example · pyproject.toml · LICENSE (Apache-2.0)
├── docs/ · articles/ · outreach/ · upstream/
```

**Fixtures**, provenance stated in each:

| fixture | provenance |
|---|---|
| `cbomkit-keycloak.json` | real CBOMkit output, 56 components — the messy case |
| `cbomkit-kafka.json` | real CBOMkit output, 11 components |
| `spec-conformance-1.6.json` | CycloneDX `valid-cryptography-full-1.6.json` |
| `purpose-ambiguous.json` | **hand-built**: the RSA-2048 component of `conflict-hybrid.json`, alone |
| `signatures.json` · `rsa-strength-split.json` | **hand-built**; see `tests/fixtures/PROVENANCE.md` |
| `conflict-hybrid.json` | **hand-built**: X25519MLKEM768, the four-way conflict case |
| `sbom-tools-normalized.json` | **constructed** from their Rust struct definitions, not captured — shape since [confirmed upstream](https://github.com/sbom-tool/sbom-tools/issues/362) |

Fixtures validate against the official schemas in CI so hand-built files cannot
drift out of spec.

**cdxgen support is unverified**: a code search of `CycloneDX/cdxgen` returns
zero matches for `cryptoProperties` and `CBOM`. Listed as untested, not claimed.

## 13. Name

`pqc-audit` is taken on PyPI (v0.4.1,
[rauleteee/pqc-scanner](https://github.com/rauleteee/pqc-scanner)). **`cbomctl`**
is free on PyPI and GitHub.
