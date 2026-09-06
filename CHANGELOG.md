# Changelog

Semantic versioning. Policy-pack versions move independently — see
[`policy-packs/CHANGELOG.md`](policy-packs/CHANGELOG.md).

## [Unreleased]

### Added
- **`scripts/check_stats.py`, and it runs in `check.sh` and in CI.** Every
  number the prose states about a fixture, a policy pack, the loader or a
  vendored schema is derived from the thing it describes — 55 claims across
  40 sites as this was written, in the docs, the README, the outreach
  drafts, `PROVENANCE.md` and one module docstring in `src/`. Running it for the first time found three stale
  numbers that a hand pass a day earlier had missed.

  **Parsing the prose, not generating it** — argued at length in the file's
  docstring. These numbers live in sentences, not only in table cells: "it
  appears in 12 components; in 11 it is the only function recorded" carries the
  argument of the page, and four of the six stale claims standing that morning
  were in prose a generator cannot reach, one of them a docstring in `src/`.
  The known weakness of parsing — reword the sentence and the check silently
  stops applying — is closed by making a claim site mandatory: **a pattern that
  matches nothing fails**, with the same weight as a wrong number.

  Fixture claims are derived from the fixture JSON and cbomctl's claims through
  the loader, deliberately kept apart, so a normalizer bug cannot rewrite the
  description of the input it was meant to normalize.

- **`scripts/check_published.py`** diffs the **live** dev.to articles against
  `outreach/devto/`. `gen_syndication.py --check` pinned those files to
  `docs/writing/` and stopped at the edge of the repository; between the file
  and the copy a reader sees sits a paste into a browser, which is where 206
  characters were once mangled into Mac Roman and where a later correction can
  simply not be made. dev.to serves `body_markdown` to anonymous clients, so
  the gap is closeable: both articles are live under `lvlrsajjad`, both were
  byte-identical, and the published URLs are now recorded in `ARTICLES` so an
  unrecorded article is reported unpublished rather than passed over. Title,
  the four tags and the canonical URL are checked too — that last field is the
  one that silently does not save.

- **`tests/test_tool_center_entry.py`** validates the Tool Center submission in
  `outreach/cyclonedx-tool-center-pr.md` against their schema on every `pytest`
  run. The schema is **vendored** to `tests/fixtures/schemas/`, so the check
  works offline like the rest of the suite; `ci.yml` separately diffs the
  vendored copy against `CycloneDX/tool-center@main`, so upstream movement
  fails by naming the schema rather than our entry. It was previously validated
  once by hand against a copy in gitignored `.research/`, and the file has been
  edited since.

  The schema is at the obvious raw path,
  `raw.githubusercontent.com/CycloneDX/tool-center/main/schemas/tool.schema.json`
  — a note in this repo said that 404s, and it does not.

- The command checker now reads **prose, not just fences**. Any `` `--flag` ``
  written anywhere in the swept files must be one the CLI has, or must appear
  in `FOREIGN_FLAGS` naming the tool it belongs to. `--strict-unknown` sat in
  `docs/DESIGN.md` three times and not once inside a fence, so the 0.1.4
  checker would still have missed all three. Today's six foreign flags all
  belong to `open-quantum-secure` or are declared future work; none was fiction.
- `.github/ISSUE_TEMPLATE/` is swept too — `bug.md` hands the reporter a
  `cbomctl verdict ...` blank, now marked `illustrative` rather than looking
  like something that runs.

- **`check_commands.py` now resolves third-party actions.** Every `uses:` in a
  documented workflow is checked against that action's own `action.yml`,
  fetched at the ref the page names — not just ours. Because a Docker action
  declares no inputs at all, `env:` names are checked against the action
  repository's README at the same ref. An action the checker cannot resolve is
  reported unchecked by name.

### Fixed
- **`docs/ci.md` told readers CBOMkit writes `cbom.json` to the workspace root.**
  It writes `cbom/cbom.json`: the directory comes from `CBOMKIT_OUTPUT_DIR`,
  which their `Main.java` defaults to `cbom`. The next step then passed
  `cbom: cbom.json` to our action, so the documented workflow would have failed
  at the first step that mattered. This is the second error found on that half
  of the page — the first, `with: { output: cbom.json }` against an action that
  declares no inputs, was fixed by hand in 0.1.4 and then went straight back to
  being unchecked.

- **`policy-packs/README.md` said "No pack is verified yet"**, nine months after
  all seven were verified from primary sources, in the file a downstream
  consumer of the packs reads first. Its pack table also omitted `nist-ir8547`
  entirely and marked BSI's signature-hybrid stance **unverified**, when
  `bsi-hybrid-signatures` exists, is verified and says `recommended`.

- **`docs/DESIGN.md` §9 said the same thing** — "v0.1 packs: … **None is
  verified.**", six packs listed of seven — and its §5 table still had
  `cryptoFunctions: [keygen]` only as 12, which `76ca56f` corrected everywhere
  except there. `docs/ci.md` said `--require-verified-policy` "currently
  excludes `cnsa-2.0`"; it excludes nothing. `scripts/gen_pack_docs.py` emitted
  "NSA (pending verification)" into the generated pack index.

- **`tests/fixtures/PROVENANCE.md` and the `normalize/purpose.py` docstring**
  both still said five EC keys carry `primitive: pke`. Four do; the fifth `pke`
  component is RSA-2048. Same off-by-one as `76ca56f`, in the two places that
  pass had not looked.

- **Two fixture statistics in `docs/purpose.md` were off by one**, both on the
  page whose argument is that the tool does not guess. `cryptoFunctions:
  [keygen]` and nothing else is 11 of 22 components, not 12 — `keygen` appears
  in 12, but in one of those it is not the only function. And 4 EC keys carry
  `primitive: pke`, not 5; the fifth `pke` component is RSA-2048, which is the
  canonical ambiguous case rather than an EC key. Both numbers were echoed in
  `docs/DESIGN.md` §5 and corrected there too.

  The load-bearing claims all held exactly: 56 components, 22 of asset type
  `algorithm`, 6 with no `cryptoFunctions`, 4 tagged `primitive: other`, and
  **8 of 22 unresolved — 36%, "more than a third"**, which is the line the
  README and the Show HN draft lean on.

### Changed
- The routing from a fence to its check is one function, `check_block`, called
  by both the script and its tests. It was duplicated in three places, which
  would have let the thing that proves the checker works drift from the checker.
- `RESUME.md` carries a banner saying it is a superseded v0.1.0 snapshot. Its
  counts, and two article filenames that have since moved to `docs/writing/`,
  describe that moment; nothing derives them, and now nothing reads them as
  current either.

### Decided against
- **A scheduled CI job that runs the CBOMkit half of `docs/ci.md`.** Reasoning
  in [`docs/roadmap.md`](docs/roadmap.md), short version: a workflow cannot
  execute a workflow file it just wrote, so you either inline the steps — a
  transcription of the page, which is the gap reopened one layer down — or
  commit a generated file that then needs its own check. It would mostly test
  an unpinned `:edge` Docker image, so its red runs would usually not be about
  us. And the claim the page actually makes is a fact in two of their files,
  which `check_commands.py` now fetches and checks on every run.
- **Deriving the pack-stance table in `policy-packs/README.md`.** One cell per
  pack collapses several purpose-scoped rules — `anssi-fr` carries both
  `recommended` and, inside certification scope, `required` — and picking a
  winner is a reading the packs do not state. Inventing one in a checker would
  put a second, unversioned opinion beside the pack's. The table says so, and
  `check_stats.py` leaves it alone.

## [0.1.4] — released 2026-09-06

The docs said things nobody had run. Four releases of `docs/quickstart.md`
carried a pipeline that could not work, and the mechanism meant to prevent
exactly that only ever checked half of what the prose claims.

### Fixed
- **`docs/quickstart.md` told readers to run a pipeline that could never have
  worked.** `sbom-tools view app-cbom.cdx.json -o json | cbomctl verdict -
  --from sbom-tools` was on the page for four releases. The maintainer's answer
  in [sbom-tool/sbom-tools#362](https://github.com/sbom-tool/sbom-tools/issues/362)
  settles it: `view -o json` is a curated projection carrying `name`,
  `version`, `ecosystem`, `licenses`, `supplier`, `dependency_kind`,
  vulnerability and EOL fields — **and nothing from `cryptoProperties`**. That
  pipeline feeds `cbomctl` a document with no crypto assets in it. Nobody had
  ever run it.

  The quickstart now shows what actually produces the normalized payload —
  their C ABI, or the `parse_path_json` helper in their bindings — and says
  plainly that the step could not be executed here and why.

- **`docs/index.md`, the docs-site landing page, carried a fabricated matrix.**
  Hand-edited, never generated, and wrong: it showed `ECDH ⚠ c1,c2` and
  `X25519MLKEM768 ⚠ c3,c4` where the tool emits `c1` and `c2,c3` for that
  input, renamed `RSA-2048` to `RSA`, dropped the rule-detail lines and
  reordered the rows. It is generated now.

- **`docs/purpose.md`** showed a paraphrase of an unresolved-purpose finding as
  though it were output. Generated now, from a new fixture
  (`tests/fixtures/purpose-ambiguous.json`) that isolates the ambiguous RSA
  component.

- **`docs/ci.md` passed an input to CBOMkit's action that the action does not
  have.** `cbomkit/cbomkit-action` declares no `with:` inputs at all — it is
  configured by environment variables and writes `cbom.json` to the workspace —
  so `with: { output: cbom.json }` was meaningless. Corrected against their
  `action.yml`, and the page now states which half of the workflow is checked
  and which is only transcribed.

- **`docs/DESIGN.md` advertised `--strict-unknown`**, a flag that has never
  existed; the flag is `--strict`. Its §1 demo block was a pre-implementation
  sketch in a format the tool never emitted, printed behind a `$` prompt as
  though captured — now generated. Its §12 module tree named four files that do
  not exist and omitted one that does. Its status line still read "no rule is
  verified yet", nine months after all seven packs were verified. §11 described
  `cbomctl plan --llm` in the present tense; it is unbuilt, and now says so.

- **`cbomctl normalize` printed `CONSTRUCTIONQUANTUM`** as a column header — the
  field width was exactly the length of the word, so no space separated it from
  the next column. Found by running a command the quickstart tells readers to
  run, which is the first time anyone had.

### Changed
- `tests/fixtures/sbom-tools-view.json` is renamed
  **`sbom-tools-normalized.json`**. The old name was the root cause of the
  quickstart bug: it holds the normalized `parse` payload, and calling it
  `view` is what made a `view -o json` pipeline look plausible to write.
- The `sbom-tools` adapter's docstring no longer says "we have asked upstream
  whether the payload is stable; until they answer this adapter may break".
  They answered. It now records what they said: nested shape under
  `crypto_properties` is **not** test-pinned (only top-level keys are, in their
  `tests/fixtures/abi/contract_required_keys.json`), there is no schema version
  separate from the crate version, and pre-1.0 a breaking JSON change is
  permitted in a minor release with a note in their CHANGELOG upgrade notes —
  so pin their crate version. The `primitive` absent-vs-`"unknown"` conflation
  is confirmed, and they intend to document rather than change it, so our note
  on it stands.

### Added
- **`scripts/check_commands.py`, and it runs in `check.sh` and in CI.** Every
  copy-pasteable command in `README.md`, `docs/`, `articles/`, `outreach/`,
  `RELEASE.md` and `CONTRIBUTING.md` is now executed, against a scratch
  directory seeded with the placeholder filenames the docs use, so the
  documented line runs verbatim. Anything that cannot be run here must carry
  `<!-- unverified: reason -->` and is reported as unverified rather than
  looking checked. Untagged fences are rejected outright: a fence declares
  itself generated, an excerpt of a named command, a synopsis, illustrative, or
  unverified.

  This is the same class of gap that `aa7e3d0` closed for the README.
  `gen_article_blocks.py` regenerates blocks that claim to be *output*; nothing
  had ever checked a block that claims to be *input*, which is why a broken
  pipeline sat in the quickstart for four releases. Flag names in usage
  synopses are checked against `--help`, quoted excerpts are checked against
  the full output of the command they name, and a workflow snippet's `with:`
  keys are checked against `action.yml`.

- `tests/test_check_commands.py` — thirteen cases asserting the checker
  *rejects* fiction, including the exact quickstart pipeline, the invented
  `--strict-unknown`, an untagged matrix, a drifted excerpt and an undeclared
  action input. A check that cannot fail is not a check.
- `tests/test_docs_layout.py` — the module tree drawn in `docs/DESIGN.md` §12
  must match `src/cbomctl` in both directions.
- `tests/fixtures/purpose-ambiguous.json` — the ambiguous RSA-2048 component of
  `conflict-hybrid.json`, alone.

### Kept
- **The `--from sbom-tools` adapter stays.** The maintainer's advice was "for
  what you're building, parse raw CycloneDX, not our JSON", and that is right
  for the primary path — which is already what `cbomctl` does. The adapter is
  opt-in behind a flag, adds no dependency, is 100 lines, and its shape is now
  confirmed rather than guessed. What it buys is a user who already runs
  `sbom-tools` in a pipeline and has a normalized document in hand. What it
  costs is a breakage in any pre-1.0 minor release of theirs, announced in
  their upgrade notes — bounded, visible, and behind a flag nobody reaches by
  accident. Dropping it would remove a real path to save a maintenance risk we
  can now see the exact shape of. If it breaks twice, drop it then.

## [0.1.3] — released 2026-09-06

No change to the Python package; `cbomctl` 0.1.3 and 0.1.2 are identical. The
release exists so a tag carries an `action.yml` that GitHub will publish.

### Fixed
- The action's `description` was 135 characters. GitHub Marketplace requires
  fewer than 125 and only says so on the release publish form, after the tag is
  cut — so the constraint is now asserted in `tests/test_action_metadata.py`,
  along with the other metadata the Marketplace requires (name, description,
  `branding.icon`, `branding.color`).

## [0.1.2] — released 2026-09-06

### Fixed
- Conflict prose in the terminal matrix was emitted as one unwrapped line — the
  longest ran to 439 characters. A terminal soft-wraps that into a block with no
  indent structure and a browser `<pre>` does not wrap it at all, so the demo
  block scrolled sideways off the published article page. Conflict summaries,
  cost notes, alternative-reading notes, per-asset detail lines and the
  assumptions footer now wrap to the terminal width, clamped to 60–100 columns.
  Longest line drops to 107. Tests assert no line exceeds 120 characters at
  either 100 or 60 columns, and that wrapping loses no words.

  Found by reading the published dev.to page rather than the local output —
  the same class of check that caught the 0.1.1 bug.

## [0.1.1] — released 2026-09-06

### Fixed
- `cbomctl policies list` printed "No pack is verified. Rules were assembled
  from secondary reporting" — a sentence written when that was true, left
  unchanged when it stopped being true, and shipped in 0.1.0 two lines below
  seven rows reading `VERIFIED`. The summary is now derived from the packs and
  additionally reports which packs cite a draft source and which carry a
  contested encoding. A test forbids hardcoding any claim about verification
  state in the CLI, and another asserts the summary matches the packs.

  Caught by installing 0.1.0 from PyPI in a clean venv and reading the output,
  which is the only check that runs under the conditions a stranger has.

## [0.1.0] — released 2026-09-06

First working version. **All seven policy packs are read from primary sources**
— every rule cites the section or page it came from, names its verifier and
pins the edition. The `UNVERIFIED POLICY PACK` banner, the `status` field and
`--require-verified-policy` remain in place for the next rule that has not been
checked, and are exercised by a synthetic test fixture.

### Added
- `cbomctl verdict` — per-asset × jurisdiction matrix plus a conflicts section
  with a computed satisfies-all target. The product.
- Conflict detection across four kinds: `construction`, `parameter`,
  `deadline`, `scope`.
- `cbomctl prioritize` — Mosca ranking from user-supplied data lifetimes.
- `cbomctl plan`, `cbomctl normalize`, `cbomctl policies list|show`.
- Purpose normalizer with an explicit precedence ladder, keeping `AMBIGUOUS`
  and `UNKNOWN` distinct and never guessing between them.
- Six policy packs as a standalone, semver-versioned artifact with their own
  JSON schema, consumable without this tool.
- Reporters: terminal matrix, JSON, Markdown, SARIF 2.1.0.
- Composite GitHub Action; CI validates fixtures against the official CycloneDX
  schemas and dog-foods the action on the conflict fixture.
- Optional `--from sbom-tools` adapter, no dependency.

### Design decisions worth knowing
- **`binding` decides FAIL versus WARN, not severity.** A
  `guideline_recommendation` cannot produce FAIL, enforced in code. Most PQC
  guidance is guidance, and reporting it as law misinforms.
- **`hybrid` is scoped per purpose and is a three-step gradient**:
  `recommended` (BSI, ANSSI, EU) → `not_recommended` but permitted (ASD) →
  `not_permitted_except_interop` (NSA). The middle step leaves a satisfies-all
  target available at a cost; the third removes it, and the conflict output says
  so rather than inventing a compromise.
- **Urgency and assurance are separate axes.** BSI and ANSSI both recommend
  hybrid *signatures* on algorithm-maturity grounds — ANSSI citing the classical
  break of Rainbow — which is a different argument from
  harvest-now-decrypt-later and reaches purposes HNDL cannot.
- **Security strength is derived**, so NIST IR 8547's 112-bit 2030 deprecation
  reaches RSA-2048 and P-224 but not RSA-3072 or P-256. Where it cannot be
  derived the finding is indeterminate rather than the stricter date.
- **Three ways to not answer**: `unscored` (purpose unresolvable),
  `indeterminate` (a rule needs an undeclared fact), `not-applicable`. None is a
  silent pass.
- **`--strict`** turns every unverified rule into INDETERMINATE, so nothing
  built on stub packs can be mistaken for a real verdict.
  **`--require-verified-policy`** refuses to run at all.
- **The CNSA 2.0 January 2027 acquisition gate is off by default**
  (`--cnsa-acquisition-gate`): it is a procurement condition on new NSS
  acquisitions, not an algorithm deadline.

### Known limits
- **One rule's encoding is a judgement call, and says so.** The CNSA 2.0 FAQ
  answers the hybrid question twice with different force. The stronger reading
  is encoded, marked `interpretation: contested` with `alt_reading: silent`,
  and any conflict it drives prints both outcomes. The uncontested half of
  NSA's position is a separate rule so the matrix keeps an anchor.
- The `sbom-tools` adapter's payload shape is inferred from their Rust struct
  definitions, not captured from a run. Its fixture is labelled constructed.
  **Superseded in 0.1.4** — upstream answered; the shape is confirmed.
- cdxgen is unverified as a CBOM producer; a code search of their repository
  finds no `cryptoProperties` handling.
- `security_level` selectors always evaluate to INDETERMINATE — there is no
  config field for them yet.
