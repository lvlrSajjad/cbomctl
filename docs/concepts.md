# Urgency and assurance

Two questions, often collapsed into one, that have different answers and
different drivers:

| | question | driven by | reaches |
|---|---|---|---|
| **urgency** | when must I move? | harvest exposure × data lifetime | key establishment and encryption; signatures only when verification is long-lived |
| **assurance** | what must I move *to*? | maturity of the target scheme | every purpose, signatures included |

An asset can be low urgency and still need a specific target. Conflating the
two is why "signatures aren't urgent" gets misread as "signatures are simple".

## Urgency: key exchange is already exposed

An adversary who records ciphertext today decrypts it the day a
cryptanalytically relevant quantum computer exists. The exposure window opened
in the past. BSI names the mechanism directly:

> "encrypted data can already be stored for later decryption ('Store Now,
> Decrypt Later')"
> — [BSI TR-02102-1 §2.1](policy-packs/bsi-de.md)

Signatures do not work that way. Forging one requires the quantum computer to
exist *at the moment of forgery*; nothing recorded today becomes forgeable
retroactively. Again, BSI states it:

> "In contrast to key agreement, classic signatures are still trustworthy as
> long as no cryptographically relevant quantum computer exists."

The deadlines follow. EO 14412 puts key establishment at 2030 and signatures at
2031 in consecutive clauses of one sentence. BSI puts key agreement at
2030/2031 and signatures at 2035.

**The exception that matters:** a signature whose *verification* is long-lived —
firmware, code signing, document signing, root CAs — is trusted for years after
issuance. There the relevant horizon is not how long the data stays secret but
how long the signature stays trusted, which is why `cbomctl.yaml` carries
`verification_lifetime_years` separately. The EU roadmap makes the same point:

> "the upgrade mechanism for software and firmware upgrades should incorporate
> post-quantum signature schemes for integrity and authenticity"

### Mosca's inequality

Urgency is scored as **X + Y > Z**:

- **X** — how long the data must stay confidential. From you. No CBOM contains it.
- **Y** — how long migration takes. Default 3 years.
- **Z** — years until a CRQC. Default 2035.

Z is a planning assumption matching the NSM-10 and EU horizons, **not a
prediction**. It is stamped into every output, so a verdict can never be read
without the assumption behind it. Change it with `--crqc-year`.

### Strength, not algorithm name

NIST IR 8547 scopes its 2030 deprecation to **112 bits of security strength**,
not to an algorithm. RSA-2048 and P-224 are deprecated after 2030; RSA-3072 and
P-256 are not — they are only disallowed after 2035. Same table, same document,
different rows.

`cbomctl` derives strength from modulus size, elliptic curve, or the CBOM's
`classicalSecurityLevel` field. When it cannot be derived, the finding is
**indeterminate rather than the stricter date**, and that choice is deliberate:

> False urgency competes for budget with real urgency. A team that believes
> RSA-3072 dies in 2030 builds a migration schedule five years tighter than it
> needs, against work that genuinely is on a 2030 clock. Crying wolf has a cost,
> and it is paid by the findings that were real.

Grover is not Shor. SHA-256 retains roughly 128 bits of quantum security and is
not a migration target; AES-128 is weakened, not broken. `cbomctl` bands those
`low` no matter how long the data lives. SHA-1 is a real finding but a
*classical* one, and reporting it as quantum risk would be inflation.

## Assurance: the young-scheme problem

The second axis has nothing to do with timing. ANSSI states it plainly:

> "even if the post-quantum algorithms have gained a lot of attention, they are
> still not mature enough to solely ensure the security. For example, several
> post-quantum schemes have suffered from classical attacks in the past years"
> — [ANSSI, 2023 follow-up §1.1](policy-packs/anssi-fr.md)

The citation attached to that sentence is Beullens, *Breaking Rainbow takes a
weekend on a laptop*. Rainbow and SIKE both fell to **classical** cryptanalysis
during the NIST competition. That risk does not shrink as the CRQC date
approaches — it is a bet on the mathematics, not on the hardware.

Hence hybrid constructions: keep a classical algorithm alongside the
post-quantum one so the combination survives either being wrong. BSI puts it as
a design requirement:

> "Hybridisation should be implemented in such a way that the hybrid signature
> scheme is secure as long as at least one of the schemes is secure."

### The carve-out that shows it is reasoning, not a rule

BSI and ANSSI both **exempt hash-based signatures** — SLH-DSA, XMSS, LMS — from
the hybrid recommendation. Independently, and for the same stated reason: their
security rests only on hash-function assumptions, so there is no young lattice
assumption to hedge against.

> "hash-based signatures can … in principle also be used alone (i.e. not in
> hybrid form)" — BSI §5.3.4

That is the maturity argument applied consistently rather than as a blanket
rule, and it is why `cbomctl` models `rationale` explicitly. A tool that only
knew "BSI wants hybrid" would warn on standalone SLH-DSA, incorrectly.

## Everyone agrees on the risk. They disagree on the price.

The most misreported thing about international PQC guidance is that the
authorities disagree about the facts. They do not. Australia's ASD grants the
European premise word for word:

> "Generally, such schemes have the advantage of the security offered by the
> traditional cryptographic algorithm if the post-quantum cryptographic
> algorithm is vulnerable to an implementation flaw or new attack."
> — [ASD ISM](policy-packs/asd-au.md)

That is BSI's and ANSSI's argument, stated by the agency that recommends
against hybrids. ASD then weighs it against complexity, maintenance burden and
overhead, and adds a point the Europeans do not address: once a CRQC exists,
the classical half of a hybrid contributes nothing.

Same premise, different weights, opposite conclusions. That is a business
judgement, not a technical dispute — which is why `cbomctl` reports the
collision and names the trade rather than picking a side.
