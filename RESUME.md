# Session state — Phase 1 re-revised (post-review corrections applied)

`~/Coding/ME/pqc-audit` · branch `main` · **no commits yet** · name **`cbomctl`**.

## Positioning (3rd pass, now narrow and defensible)
**Product = conflict analysis over a CBOM you did not generate.**
`cbomctl verdict` emits a per-asset × jurisdiction matrix + a Conflicts section
with a computed satisfies-all target. `prioritize` (Mosca) and `plan` are
secondary features, explicitly not differentiators.

## Corrections applied
1. Repositioned: verdict/conflict is the headline; scoring + plan demoted.
2. Input: raw CycloneDX primary and only required; `--from sbom-tools` optional,
   no dependency. All "layer above sbom-tools" framing removed.
3. `policy-packs/` is now a standalone semver artifact (schema + CHANGELOG +
   README), consumable without cbomctl. New `binding` and `hybrid` fields.
4. Regulatory: BSI *recommends* (not mandates); ANSSI *strongly recommends* +
   separate certification rule; IR 8547 is a **draft** and *deprecated ≠
   disallowed* (separate states); **EO 14412 added** (HVA/high-impact only,
   excl. NSS, key-est 2030 / signatures 2031); CNSA 2027 gate + 2030/2033 +
   2031-unless-excepted; SP 800-227 cited for hybrids; HQC excluded (not FIPS).
5. Upstream issue rewritten — no longer proposes profiles; asks whether the
   normalized JSON is a stable contract. 2 paragraphs + one-line disclosure.
6. `--llm` reduced to one sentence; plan is a subsection.
7. Articles replanned; CfP abstract (301 words) + Tool Center PR written.

## ⚠️ Finding the review missed — told the user, in DESIGN §2 and README
`jimbo111/open-quantum-secure` (Go, MIT, 3★) already ships **7 frameworks incl.
bsi-tr-02102 / asd-ism / anssi-guide-pqc**, accepts `--compliance a,b,c` and
`--compliance all`, and its README already documents cross-framework divergence
with our exact worked example (X25519MLKEM768 passes ANSSI+BSI, fails CNSA 2.0
and ASD ISM). It also has `--data-lifetime-years` and `--sector` HNDL presets.
So "nobody evaluates multiple jurisdictions" is **false** and must not be claimed.
What survives: (a) conflict as a *computed artifact* — theirs is one report per
framework concatenated with `---`; (b) evaluating a **third-party** CBOM — theirs
is a scanner, `--cbom` only exists on `upload`.

## Files
`docs/DESIGN.md` · `docs/policy-sources.md` (6 packs, 33 unverified claims) ·
`README.md` · `policy-packs/{README,CHANGELOG,schema/pack.schema.json}` ·
`upstream/{issue-draft,first-pr-scope}.md` · `articles/README.md` ·
`outreach/{pki-consortium-cfp,cyclonedx-tool-center-pr}.md`

## Verified this session
EO 14412 (91 FR 38483, whitehouse.gov) · CycloneDX tool-center schema v2.0
(entry validates clean) · sbom-tools MIT / v0.2.0 / created 2026-02 ·
`sbomtools` on PyPI is an unrelated project (Eliot Lear).

## Blocking Phase 2
Policy-pack verification. Rule tables are downstream of `docs/policy-sources.md`.
Normalizer + scorer + verdict engine can be built with stubbed packs.

## Scratch
`.research/` — CycloneDX schemas, CBOMkit samples, sbom-tools + OQS sources,
tool-center schema. Gitignored.
