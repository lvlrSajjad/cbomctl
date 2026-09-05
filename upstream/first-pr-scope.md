# What a first PR to `sbom-tool/sbom-tools` would touch

Internal note for Sadjad — not for posting. Scope estimate for the
`bsi-tr02102` profile, derived by reading `main`. I have not built the project,
so line counts are estimates from structure, not from a compile.

## The shape of the work

A compliance profile in this repo is four things: a `Standard` clap variant, a
`ComplianceLevel` variant, a checker module, and rule metadata in the registry.
`cnsa2` and `pqc` share one module (`src/quality/compliance/crypto.rs`, 1192
lines) because they share the crypto asset walk; a jurisdiction profile would
join that module rather than start a new one.

| File | Change | Est. |
|---|---|---|
| `src/quality/compliance/selector.rs` | `Standard::BsiTr02102` clap variant + aliases; `ComplianceLevel::BsiTr02102_1`; `as_str`; the string→level table (~line 215) | ~25 lines |
| `src/quality/compliance/crypto.rs` | `check_bsi_tr02102()` reusing `classify_crypto_component`, `classify_algorithm`, the protocol-asset walk, and `is_hybrid_pqc()` | ~150–250 lines |
| `src/quality/compliance/registry.rs` | `SBOM-BSITR02102-*` `RuleMeta` entries — `sarif_id`, `name`, `short_description`, `default_severity`, `refs: &[(K::…, edition)]`, `remediation`; plus a `K::` reference-kind variant and its help URI | ~80–120 lines |
| `src/quality/compliance/mod.rs` | dispatch | ~5 lines |
| `docs/STANDARDS_VERSIONS.md` | one pinned-edition row + a watch-list row (TR-02102-1 is revised roughly annually) | ~2 rows |
| `tests/fixtures/cyclonedx/` | `cbom-bsi-hybrid-compliant.cdx.json`, `cbom-bsi-pure-pqc-violation.cdx.json` | 2 files |
| `tests/cbom_tests.rs` | profile tests, following the existing `cbom-cnsa2-*` pattern | ~100 lines |
| `README.md` / `--help` | profile list, count 16 → 17 | small |

Call it **400–500 lines** plus fixtures for the first profile. `anssi` and
`asd-au` afterwards are cheaper — the plumbing is amortised, so mostly rule
tables and fixtures, maybe 150–250 lines each.

## Where it gets interesting rather than mechanical

**The hybrid verdict inversion is the whole point and the main design
question.** They currently emit `SBOM-PQC-010` `PqcHybridCombiner` at
`Warning`, described as "recommended transition practice". Under a BSI profile
the *absence* of hybrid on a quantum-vulnerable key establishment path is the
finding; the presence of hybrid satisfies the requirement. So the same
`is_hybrid_pqc() == true` fact needs to produce opposite verdicts under
different profiles.

That is straightforward if the profile owns the mapping and the detector stays
neutral — which is how it's already factored, since `is_hybrid_pqc()` lives on
the algorithm properties, not in a profile. Worth confirming with a maintainer
before writing code, because it's the one place a wrong assumption costs a
rewrite.

**Key establishment vs signature.** BSI's reported treatment differs between
the two (key agreement on one horizon, signatures on a later one), and ASD's
reported RSA/DH/ECDH/ECDSA sunset is a single date across both. Distinguishing
them needs purpose, and purpose is where the CBOM data is weakest:

- `AlgorithmProperties::crypto_functions` is parsed but not read anywhere under
  `src/quality/compliance/`.
- In real CBOMkit output, `cryptoFunctions` is absent on 6 of 22 algorithm
  components, and where present it is `keygen` 12 times — which carries no
  purpose information at all.
- `primitive: pke` is genuinely ambiguous between encryption and signature, and
  CBOMkit applies it to EC keys that are in fact ECDSA/ECDH.

So a rule that says "classical key agreement fails after date X" has to handle
"I cannot tell whether this is key agreement" as a first-class outcome. Their
`CnsaVerdict::Unknown → Warning, never a silent pass` convention is the right
precedent and I'd follow it exactly.

**Absent vs explicit-unknown is erased in normalization.**
`src/parsers/cyclonedx.rs:859` maps a missing `primitive` and an explicit
`primitive: "unknown"` both to `CryptoPrimitive::Unknown`
(`.map_or(CryptoPrimitive::Unknown, …)`). Harmless for an allowlist check.
Relevant if a jurisdiction rule ever wants to say *why* it couldn't decide —
"your generator omitted this" and "your generator said it didn't know" send the
user to different places. Not worth a PR on its own; worth knowing.

## Sequencing

1. **Verify the regulations first.** Every rule needs a primary source and a
   verification date to meet this project's bar. Do not write Rust before
   `docs/policy-sources.md` is signed off — the rule tables are downstream of
   those answers, and if BSI turns out to *recommend* rather than *require*
   hybrid, the severity mapping changes and so does the pitch.
2. **Post the issue and wait.** A maintainer may prefer different ids, may want
   the deadline-scaling mechanism (their plan P2) first, or may not want
   jurisdiction profiles at all. All three answers are cheap to receive now and
   expensive to discover in review.
3. **Then one PR, `bsi-tr02102` only.** Three profiles in one PR is a
   reviewer-hostile diff and triples the surface for a "we'd rather not" reply.

## Why to do this even though it hands away a differentiator

Upstreaming the packs is worth it, and the trade is smaller than it looks.

**The likely outcome is not "they build it themselves."** A generalist tool with
16 standards and a small maintainer group usually answers a well-scoped proposal
with "PRs welcome" — which makes us the author of those profiles, in their
changelog and in `STANDARDS_VERSIONS.md`. If they do build it themselves, the
proposer credit on a 240-star OpenSSF-badged project is worth more than the
feature was.

**The differentiator changes shape rather than disappearing.** Upstream, a
jurisdiction profile produces PASS/FAIL. In `cbomctl` the same pack is an
*input to the plan*: it selects hybrid vs pure migration targets, supplies the
deadline that orders the work, and drives the verdict-conflict section. Keep the
packs in `cbomctl` regardless. If upstream gains equivalent profiles, our story
becomes **shared input, unique use** instead of unique input — and the README
should say that from day one, so the positioning does not have to wobble later
when it happens.

**It is also the cheapest marketing available.** Every `sbom-tools` user who
sees a BSI-vs-ASD contradiction in their own output has just been shown, in
their own repository, the problem `cbomctl` exists to solve.

The line to hold: **the product is the scoring-plus-plan layer** — data lifetime,
HNDL weighting, ranked migration output. The policy packs are inputs to it. That
is the part no inventory or validation tool can produce, it is unaffected by
whatever upstream decides, and it is where the investment should go.

The failure mode to avoid is an issue that reads as marketing — hence the
one-line context note at the top of the draft rather than a confession at the
bottom. A maintainer will look at the profile anyway; learning it from the issue
is much better than learning it from our README a month later, and it signals a
downstream user who will keep caring about these profiles after they merge.
