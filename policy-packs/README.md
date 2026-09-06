# PQC policy packs

Machine-readable rule sets describing what each national authority says about
post-quantum cryptography: which algorithms, which constructions, by when, and
**with what force**.

These are published as a standalone, semantically versioned artifact. `cbomctl`
is the first consumer, but nothing here depends on it — the schema, the rules
and the citations are usable by any tool that has a normalized view of
cryptographic assets. If you want to build something else on them, take them.

- Schema: [`schema/pack.schema.json`](schema/pack.schema.json)
- Packs: [`packs/`](packs/)
- Version and history: [`CHANGELOG.md`](CHANGELOG.md)
- Sourcing and verification status: [`../docs/policy-sources.md`](../docs/policy-sources.md)

## Status

> **All seven packs are verified against primary sources**, and 0 rules across
> 7 packs ship `status: needs_verification`. Every rule cites the section it
> was read from, names its verifier and pins the edition; the log is in
> [`../docs/policy-sources.md`](../docs/policy-sources.md).
>
> The unverified machinery stays in place for the next rule that is not read
> yet: a rule shipping `status: needs_verification` makes `cbomctl` print a
> banner, and `--require-verified-policy` refuses to run against it at all.
> Consumers building on these packs should surface that state the same way.

## The two fields that matter most

**`binding`** — the force of the rule. Most PQC guidance is *not* a mandate,
and conflating a technical guideline with a statute is the most common error in
this space. A tool that reports "FAIL: violates BSI" for a document whose own
language is *recommends* is misinforming its user.

| value | meaning |
|---|---|
| `statute` | binding law |
| `executive_order` | binding on its addressees by executive authority |
| `agency_requirement` | binding on a defined population (e.g. US NSS under CNSA 2.0) |
| `certification_requirement` | binding only if you seek that certification |
| `guideline_recommendation` | technical guidance; recommends, does not compel |

**`hybrid`** — the axis on which jurisdictions actually contradict each other.
**It is scoped per purpose**, via `applies_to.purpose`, because authorities take
different positions on key establishment and on signatures. Never write a hybrid
rule without scoping it.

| value | meaning |
|---|---|
| `required` | a hybrid construction is compelled |
| `recommended` | encouraged, not compelled |
| `not_recommended` | discouraged, though not prohibited |
| `silent` | the source does not address hybrids for this purpose |

**`rationale`** — *why* the authority takes that stance, and the reason this is
a second axis rather than a footnote:

| value | meaning |
|---|---|
| `harvest_now_decrypt_later` | recorded ciphertext becomes readable once a CRQC exists. Drives **urgency**. Applies to key establishment and encryption only — a signature cannot be harvested. |
| `algorithm_maturity` | the post-quantum scheme is young and may yet fall to classical cryptanalysis — as Rainbow and SIKE both did during the NIST competition. Drives **target choice**, and applies to signatures just as much as to key establishment. |
| `key_length` | a parameter-strength requirement (CNSA 2.0's ML-KEM-1024) |
| `policy_alignment` | adopts another body's timeline |
| `unstated` | the source gives no reason |

These are orthogonal. HNDL answers *when must I move*; maturity answers *what
must I move to*. Both can be true of one asset, and conflating them is why
"signatures aren't urgent" gets misread as "signatures are simple". ANSSI
reportedly recommends hybrid signatures on maturity grounds while every
jurisdiction puts signature *deadlines* later than key establishment — those two
facts are consistent, and the schema has to be able to say so.

A rule may be `hybrid: recommended` + `binding: guideline_recommendation` (BSI)
or `hybrid: recommended` + `binding: certification_requirement` (ANSSI, for
products seeking certification). Those are different obligations and the schema
keeps them separate.

## `interpretation` — when the encoding is itself a judgement

`status` says whether the text was **read**. `interpretation` says whether
reasonable readers could **encode that text differently**. They are
independent: a rule can quote its source exactly and still be contested.

| value | meaning |
|---|---|
| `settled` | the text admits one sensible encoding |
| `contested` | reasonable readers could encode it differently; `alt_reading` gives the alternative and `interpretation_note` argues the case |

There is one contested rule today: `cnsa-2.0/cnsa2-hybrid-not-permitted`. The
NSA FAQ answers the hybrid question twice with different force, and the
stronger answer sits under a question framed *"while waiting for a final NIST
post-quantum standard"* — a premise that arguably ended in August 2024.

**A judgement that changes the output must not be invisible in the output.**
When a contested rule drives a conflict, consumers are expected to report both
outcomes. `cbomctl` prints:

> ⚖ This conflict depends on a contested encoding. Under the alternative
> reading (cnsa-2.0 silent), a hybrid construction would satisfy all selected
> jurisdictions, at a documented cost.

The uncontested half of that position — NSA "will not require" hybrids — is a
separate rule, so the matrix keeps an anchor even for a reader who rejects the
stronger one.

## Rule fields

`id` · `jurisdiction` · `source_url` · `source_title` · `last_verified` ·
`status` · `binding` · `deadline` · `applies_to` (purpose / category / security level / parameter set) · `hybrid` ·
`rationale` · `interpretation` · `alt_reading` · `interpretation_note` ·
`migration_target` · `verdict` · `open_question`

`source_url` **must** be a primary source. Permitted hosts:
`nsa.gov`, `csrc.nist.gov`, `nist.gov`, `whitehouse.gov`, `federalregister.gov`,
`bsi.bund.de`, `cyber.gouv.fr`, `ssi.gouv.fr`, `cyber.gov.au`,
`digital-strategy.ec.europa.eu`, `eur-lex.europa.eu`. Secondary reporting may be
recorded in `docs/policy-sources.md` for traceability, never as `source_url`.

## Packs

| pack | authority | scope | hybrid: key est. | hybrid: signatures |
|---|---|---|---|---|
| `bsi-de` | BSI (Germany) | technical guideline | `recommended` | `recommended` |
| `anssi-fr` | ANSSI (France) | guidance + certification | `recommended` | `recommended`* |
| `asd-au` | ASD/ACSC (Australia) | ISM, Australian government | `not_recommended` | `not_recommended` |
| `cnsa-2.0` | NSA (US) | National Security Systems only | `silent` | `silent` |
| `us-eo14412` | Executive Order 14412 | US federal HVAs / high-impact, excl. NSS | `silent` | `silent` |
| `eu-roadmap` | NIS Cooperation Group | EU Member State planning horizon | `silent` | `silent` |
| `nist-ir8547` | NIST (US) | IR 8547 initial public draft — dates are *proposed* | `silent` | `silent` |

`*` ANSSI's signature stance is `rationale: algorithm_maturity`, not HNDL — see
[`../docs/policy-sources.md`](../docs/policy-sources.md) F4. BSI reaches the
same stance on signatures by the same reasoning, in a separate rule
(`bsi-hybrid-signatures`) — the two were read independently, because a pack's
key-agreement stance does not imply its signature stance.

This table collapses several purpose-scoped rules into one cell per pack, and
that collapse is a reading, not a fact the packs state — `anssi-fr` carries both
`recommended` and, inside the certification scope, `required`; `cnsa-2.0`
carries both `silent` and `not_permitted_except_interop`. It is therefore the
one table here that `scripts/check_stats.py` does not derive; see the note in
that file.

## Versioning

Semver on the pack collection.

- **patch** — typo, clarification, citation fix that changes no verdict
- **minor** — new rule, new pack, or a rule moving `needs_verification → verified`
- **major** — any change that can flip an existing verdict: a deadline moving,
  a `binding` or `hybrid` reclassification, a rule removed

A verdict-flipping change is never a patch. Downstream tools pin a pack version
and get told when it moves.
