> **Published 2026-09-06**
>
> This describes **NIST IR 8547 ipd** — the initial public draft of November
> 2024 — as it stood on the date above. Its dates are proposed. If a final
> IR 8547 has published since you are reading this, check it: the numbers
> below may have moved, and the article's central caveat may no longer apply.

If you have read anything about post-quantum migration in the last year, you
have read that RSA is deprecated in 2030. It is one of those facts that has
been repeated into the shape of a rule.

It is half true, and the half that is false is the half people plan around.

Here is the actual table, from NIST IR 8547, *Transition to Post-Quantum
Cryptography Standards*:

| algorithm | parameters | transition |
|---|---|---|
| RSA, ECDSA | 112 bits of security strength | Deprecated after 2030<br>Disallowed after 2035 |
| RSA, ECDSA, EdDSA | ≥ 128 bits of security strength | Disallowed after 2035 |

Read the second row again. At 128 bits and above there is **no 2030 row at
all**. RSA-3072 is not deprecated in 2030. Neither is P-256. The 2030 date
applies to 112-bit strength — RSA-2048, P-224, 2048-bit finite-field
Diffie-Hellman — and to nothing else.

The key-establishment table (Table 4, covering finite-field DH/MQV, elliptic
curve DH/MQV and RSA) has exactly the same shape. Same split, same dates.

So an inventory that reports "47 uses of RSA, all deprecated in 2030" is
reporting something the document does not say. Some of those uses are on a
2030 clock and some are on a 2035 clock, and which is which depends on a field
most tooling does not look at.

## Deprecated is not disallowed

The second thing worth getting right is what the two words mean, because they
are not synonyms and NIST defines both:

> **deprecated** — "The algorithm and key length may be used, but the user must
> accept some security risk."
>
> **disallowed** — "The algorithm or key length is no longer allowed for
> applying cryptographic protection."

*Deprecated* is a risk acceptance. You may continue, with your eyes open and
presumably a note in a register somewhere. *Disallowed* is a stop.

Collapsing them into "banned by 2030" produces two failures at once. It makes
2030 look like a wall when for most algorithms it is a signpost, and it makes
2035 — the date that actually stops things — disappear from the conversation.
I have seen migration plans built entirely around 2030 that had no 2035
milestone in them at all.

If you are budgeting, the practical shape is: 2030 is when your 112-bit
material becomes a documented risk acceptance, and 2035 is when everything
quantum-vulnerable stops being usable for new protection, at any strength.

## The part almost nobody mentions

NIST IR 8547 is an **initial public draft**. Not a final publication. The cover
says so, the running header on every page says so, and the comment period closed
in January 2025.

Every date in it is proposed. The 2030s and 2035s that have propagated across
vendor roadmaps, conference slides and procurement documents are draft dates
from a draft document that, at the time of writing, has not been finalised.

That is not a reason to ignore them — they are the best available signal about
where NIST is going, and planning against them is entirely sensible. It is a
reason to say "draft" out loud when you cite them, and to not build a
contractual commitment on top of a number that can still move.

## Why tooling gets this wrong

The distinction between the rows is *security strength*, which is not a field
in a CBOM. It has to be derived: RSA-2048 gives roughly 112 bits, RSA-3072
roughly 128, P-224 112, P-256 128.

Most compliance tooling models a regulation as a list of banned algorithm names
with a date attached. That model cannot express this table — it has one slot for
"RSA" and one date, so it picks one, usually the earlier, because erring strict
feels safe.

Erring strict is not safe. A team that believes RSA-3072 dies in 2030 builds a
migration schedule five years tighter than it needs, competing for budget
against work that actually is on a 2030 clock. Crying wolf has a cost, and it is
paid by the findings that were real.

The same flattening recurs across this whole space, always in the same
direction — toward something simpler, stricter and wrong. "BSI mandates hybrid":
BSI *recommends* it, in a technical guideline. "The US mandates PQC by 2030":
Executive Order 14412 covers federal High Value Assets and high impact systems,
explicitly excluding National Security Systems, with key establishment at 2030
and signatures at **2031**.

## Try it

`cbomctl` is a CLI that reads a CycloneDX CBOM and evaluates it against
national post-quantum policies. The IR 8547 pack models the two states
separately, scoped by security strength, and prints "draft" wherever it cites
them.

```bash
pip install cbomctl
cbomctl verdict your-cbom.json --jurisdictions nist-ir8547
```

Assets that differ only in strength come out differently. This block is
generated from a fixture in the repository by a script and diff-checked in CI,
so it cannot drift from what the tool actually does:

```
⚠ DRAFT SOURCE — these rules cite a document that is still a draft; their dates are proposed and may move:
    nist-ir8547/nist-112bit-key-establishment-deprecated-2030
    nist-ir8547/nist-112bit-signatures-deprecated-2030
    nist-ir8547/nist-key-establishment-disallowed-2035
    nist-ir8547/nist-signatures-disallowed-2035

ASSET       PURPOSE        nist-ir8547
────────────────────────────────────────
ECDSA-P224  signature      WARN
            └ nist-ir8547 · deprecated 2030-12-31 · disallowed 2035-12-31
RSA-2048    key-agreement  WARN
            └ nist-ir8547 · deprecated 2030-12-31 · disallowed 2035-12-31
ECDSA-P256  signature      WARN
            └ nist-ir8547 · disallowed 2035-12-31
RSA-3072    key-agreement  WARN
            └ nist-ir8547 · disallowed 2035-12-31
```

Note `ECDSA-P224` and `ECDSA-P256`. Because IR 8547 scopes by *strength* rather
than by algorithm name, P-256 escapes the 2030 deprecation exactly as RSA-3072
does. The rule is not "RSA is fine and ECDSA is not", or the reverse — it is
112 bits versus 128, whatever the algorithm.

If the strength cannot be derived — no key size, no curve, no
`classicalSecurityLevel` in the CBOM — the finding is reported as indeterminate
rather than falling back to the stricter rule. Erring strict would put RSA-3072
on a 2030 clock it is not on.

## How the demo caught the tool lying

Worth admitting, since this article is about people repeating claims they have
not checked.

I wrote the paragraphs above first, then wrote the demo block by hand to
illustrate them, then — almost as an afterthought — actually ran the command.
Both RSA keys came out identical.

The bug was that the rule selector for security strength was inert. It always
reported "not declared", because nothing computed strength from a CBOM in the
first place. Every strength-scoped rule silently never fired. The prose was
describing behaviour the tool did not have, and I would have shipped it.

The fix derives strength from modulus size, elliptic curve, or the CBOM's own
`classicalSecurityLevel` field — which is the one in bits;
`nistQuantumSecurityLevel` is a category from 1 to 5 and reading it by mistake
would score ML-KEM-768 as three-bit security. There is now a test for that
specific confusion, tests pinning that RSA-2048 and P-224 get the 2030
deprecation while RSA-3072 and P-256 do not, and a fixture holding all four.

Two smaller things fell out. The report was displaying both RSA sizes as `RSA`
and both ECDSA curves as `ECDSA-SHA256`, because canonicalising an algorithm for
policy matching throws the parameter away — so the distinction existed in the
verdict and was invisible in the output. And every code block in this article is
now generated by a script and diff-checked in CI, the same way the tool's policy
documentation is, because a block typed by hand is a claim nobody verified.

That failure — confident prose about behaviour that does not exist — is
precisely the one this tool is built to catch in compliance reporting. It is
worth saying out loud that it happened here first.

## Try it yourself

You can read the rule and its citation without installing anything:

```bash
cbomctl policies show nist-ir8547
```

Every rule carries the section it was read from, the edition, a verification
date, and whether the source is a draft. The packs are a
[separate versioned artifact](https://github.com/lvlrSajjad/cbomctl/tree/main/policy-packs)
with their own schema, so you can consume them without the tool if you would
rather build your own.

All seven packs are read from primary sources — every rule names the section or
page it came from. Where a source is a draft, as IR 8547 is, the tool says
draft. Where a source is ambiguous, the ambiguity is recorded rather than
resolved quietly. The banner and `--require-verified-policy` remain in place for
the next rule that has not been checked yet, because rules assembled from blog
posts are roughly how "RSA is deprecated in 2030" got started.

---

*NIST IR 8547 ipd is a US federal work in the public domain.
[Read it directly](https://nvlpubs.nist.gov/nistpubs/ir/2024/NIST.IR.8547.ipd.pdf) —
Tables 2 and 4 are on pages 13 and 14, and the glossary definitions are in
Appendix A. Check whether a final version has published since; if it has, this
article's caveat is out of date and the dates may have moved.*

---

*Originally published at [https://lvlrsajjad.github.io/cbomctl/writing/rsa-2048-and-rsa-3072/](https://lvlrsajjad.github.io/cbomctl/writing/rsa-2048-and-rsa-3072/), which is the copy that gets corrected — this article describes a draft standard whose dates may move.*
