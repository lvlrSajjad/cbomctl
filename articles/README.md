# Article plan

Restructured after six primary sources were read. Voice: practitioner, direct,
no hype. 900–1400 words. Each ends with a runnable demo.

**One discipline carried from the packs into the prose: where you infer, say you
infer.** EO 14412 puts key establishment at 2030 and signatures at 2031 in
consecutive clauses and gives no reason. The pack records `rationale: unstated`.
The articles do the same — "the order does not say why, but the obvious reading
is…" rather than asserting the reasoning as the source's own.

**All seven packs are verified** and `pip install cbomctl` works, so nothing is
blocked.

**Where these go.** The docs site is the canonical home — a URL we control and
can correct, which matters because these cite a draft standard whose dates may
move. Everything else syndicates back to it:

| where | what |
|---|---|
| [the docs site](https://lvlrsajjad.github.io/cbomctl/writing/) | full text, canonical |
| dev.to | full text with `canonical_url` set to the docs site |
| LinkedIn | ~150 words plus the link, not the full text |

Not Hacker News for articles 2 and 3 — HN gets one shot, and that is the Show HN
with article 1. Not Medium.

**Order:** article 2 is published. Article 1 next, with the Show HN the same day
and the article live first so the comment can link it. Article 3 a week later.

---

## 1. "Everyone agrees on the risk. They disagree on the price." *(lead)* — ✅ [drafted](01-everyone-agrees-on-the-risk.md)

The old title was "One CBOM, three verdicts: why Germany, France and Australia
disagree about hybrid PQC". Reading the sources killed that framing, because
**they do not disagree about the facts**. ASD grants the European premise word
for word:

> "Generally, such schemes have the advantage of the security offered by the
> traditional cryptographic algorithm if the post-quantum cryptographic
> algorithm is vulnerable to an implementation flaw or new attack."
> — ASD ISM, Guidelines for Cryptography

That is BSI's and ANSSI's argument, stated by the agency that recommends
against hybrids. ASD then prices complexity, maintenance burden and overhead
higher, and adds a point the Europeans do not address: post-CRQC, the classical
half of a hybrid contributes nothing.

**Structure the article as the argument itself** — premise, weights, conclusion
— once per jurisdiction:

| | premise | weights | conclusion |
|---|---|---|---|
| BSI, ANSSI | PQ schemes are young; Rainbow and SIKE fell to *classical* attacks | scheme risk > complexity cost | hybrid recommended, for signatures too |
| EU roadmap | same | same | hybrid recommended; no reason stated |
| ASD | **same premise, quoted above** | complexity + overhead + no post-CRQC value > scheme risk | not recommended, not prohibited |
| NSA | confidence in the CNSA 2.0 algorithms | — | *pending verification* |

Then the tool's conflict section is the natural illustration rather than the
point: a reader who has followed the argument already knows why
`X25519MLKEM768` clears BSI and warns under ASD.

**The gradient is the payoff.** It is not Europe versus the anglophone
agencies, and it is not binary: recommended → not recommended but permitted →
(pending) not permitted outside named exceptions. The middle step is what makes
a satisfies-all target possible; the third removes it. That is a real
engineering consequence of a wording difference, and it is the best argument for
reading the primary text.

Demo: `cbomctl verdict … --jurisdictions bsi-de,anssi-fr,asd-au,cnsa-2.0`.

**Must not say:** that any of these authorities *mandates* hybrid — BSI and
ANSSI recommend, and ANSSI's "mandatory" applies only inside its security-visa
process. Nor that nobody else evaluates multiple jurisdictions:
[open-quantum-secure](https://github.com/jimbo111/open-quantum-secure) ships
seven frameworks and documents the divergence in its README. Link it.

## 2. "RSA-2048 and RSA-3072 have different futures" — ✅ **published**

Lives at [`docs/writing/rsa-2048-and-rsa-3072.md`](../docs/writing/rsa-2048-and-rsa-3072.md)
and is served at
<https://lvlrsajjad.github.io/cbomctl/writing/rsa-2048-and-rsa-3072/>.

That URL is canonical. Syndicated copies point back to it, because the article
describes a **draft** standard and will need correcting when IR 8547 finalises —
this is the copy that gets corrected.

Retitled from "Deprecated is not disallowed", and led with the concrete hook.
NIST IR 8547's Tables 2 and 4 split by security strength:

| strength | transition |
|---|---|
| 112 bits (RSA-2048) | **Deprecated** after 2030, **disallowed** after 2035 |
| ≥128 bits (RSA-3072) | Disallowed after 2035 — **no 2030 deprecation at all** |

Almost every summary drops the qualifier and writes "RSA is deprecated in
2030", which is true of one and false of the other. Then the two states, in
NIST's own glossary words: deprecated is *"may be used, but the user must
accept some security risk"*; disallowed is *"no longer allowed for applying
cryptographic protection."*

And the frame around all of it: **IR 8547 is still an initial public draft.**
Every date in it is proposed.

No conflict framing, no product pitch until the last paragraph. This is the
piece most likely to be linked by people who care about being right, and its
credibility depends on not selling anything.

Demo: two RSA assets at different strengths rendering differently, with the
draft notice visible.

## 3. "Signatures aren't urgent — but they aren't simple" — ✅ [drafted](03-signatures-arent-simple.md)

**Part one, urgency.** Key establishment is time-critical because of
harvest-now-decrypt-later. Signatures cannot be harvested: forging one needs the
quantum computer to exist at the moment of forgery. Both halves are now
primary-sourced:

> "encrypted data can already be stored for later decryption ('Store Now,
> Decrypt Later')" … "In contrast to key agreement, classic signatures are
> still trustworthy as long as no cryptographically relevant quantum computer
> exists." — BSI TR-02102-1 §2.1

And the deadlines follow: EO 14412 puts key establishment at 2030 and
signatures at 2031; BSI puts key agreement at 2030/2031 and signatures at 2035.

**Part two, assurance, which cuts the other way.** ANSSI says why:

> "even if the post-quantum algorithms have gained a lot of attention, they are
> still not mature enough to solely ensure the security. For example, several
> post-quantum schemes have suffered from classical attacks in the past years"

with a citation to Beullens, *Breaking Rainbow takes a weekend on a laptop*.
BSI §5.3.4 reaches the same place. So a signature can be **low urgency and
still need a hybrid target**, because the reason for hybrid has nothing to do
with timing.

**Part three, the exception that proves both authorities are reasoning rather
than rule-making.** BSI and ANSSI *both* exempt hash-based signatures — SLH-DSA,
XMSS, LMS — from the hybrid recommendation, independently, for the same stated
reason: their security rests only on hash-function assumptions, so there is no
young lattice assumption to hedge against. Applying the maturity argument
consistently rather than as a blanket rule is what makes it credible.

Worth noting plainly: a widely-circulated secondary summary states BSI wants
hybrid for *all* PQC including hash-based. The primary text says the opposite.
That is the article's own argument for reading sources.

Demo: `cbomctl verdict` on an ML-DSA asset (low urgency, hybrid target under
BSI/ANSSI) beside an SLH-DSA asset (low urgency, no hybrid target), with the
`rationale` field naming `algorithm_maturity`.

## Dropped

- **"Gate your CI on quantum risk in 20 minutes"** — commodity feature, well
  covered by `sbom-tools` and `open-quantum-secure`. Writing a tutorial for it
  invites the comparison we lose.
- **"sbom-tools says FAIL. Now what?"** — written for a positioning we no
  longer hold.
- **"Your CBOM is not a plan"** — folded into article 3's opening. As a
  standalone it restated the premise without the sourced payoff.

## Outreach

- [PKI Consortium CfP abstract](../outreach/pki-consortium-cfp.md) — needs
  updating: it still describes the conflict as jurisdictions disagreeing,
  rather than as the same risk model priced differently.
- [CycloneDX Tool Center PR](../outreach/cyclonedx-tool-center-pr.md)
- Show HN draft — not yet written.

LinkedIn and dev.to variants of article 1 once it is published.
