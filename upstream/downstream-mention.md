# Comment on `sbom-tool/sbom-tools#366` — posted

**Ready once**POSTED 2026-09-29** as
[a comment on #366](https://github.com/sbom-tool/sbom-tools/issues/366#issuecomment-5881611637),
from the `lvlrSajjad` account, by Claude on Sadjad's explicit one-off say-so in
session, after #374 and after CI and the docs deploy for `85c782e` passed.
Differences from the draft below: `#NNN` became #374, "documents the pipeline"
links the quickstart section, paragraphs were unwrapped, and the notes were
stripped. **Awaiting the maintainer's answer on the listing PR — do not open it
before a yes.**

 comment on the closed
[#366](https://github.com/sbom-tool/sbom-tools/issues/366), not a new issue.
Discussions are disabled on their repo, and #366 is where the maintainer
(`matrosov`) built the feature this follows up on — the thread already has the
context, and a comment asks nothing of their triage.

## The blocker, and what running it found

`convert --to normalized` merged in
[#367](https://github.com/sbom-tool/sbom-tools/pull/367) (`a393479`,
2026-09-07); it is on their `main` and in no release (latest v0.2.0,
2026-08-01). On 2026-09-29 sbom-tools was built from `main` and the pipeline
run for the first time. It failed on every input: cbomctl's adapter had been
written against a fixture constructed from their structs, and the real payload
nests each component as `{canonical_id, component}`. Fixed in the same change
as this file; the fixture is now captured from their binary, and verdicts
through the adapter equal verdicts from raw CycloneDX. Running it also turned
up their 1.6 `curve` bug.

None of that belongs in the comment — our bug is ours, and theirs has its own
issue.

## Draft

> Following up now that #367 is in — thank you for building it rather than
> leaving it as a request. I built `main` and ran it end to end against our
> fixtures: verdicts through `convert --to normalized` match reading the
> CycloneDX directly. (It also turned up a 1.6 `curve` gap, filed as #NNN.)
>
> cbomctl now documents the pipeline:
>
> ```sh
> sbom-tools convert --to normalized my.cbom.json -O normalized.json
> cbomctl verdict normalized.json --from sbom-tools
> ```
>
> Your advice in #362 still stands and is what the docs say: raw CycloneDX is
> cbomctl's primary input, and `--from sbom-tools` is for people who already
> have sbom-tools in their pipeline.
>
> One small ask, and an easy no: would you take a one-line PR adding cbomctl
> as an example consumer under *JSON output contract*, next to the `jq`
> example? It would show a reader what the normalized document is for
> downstream. The pointer already runs the other way — cbomctl's README sends
> anyone who wants diff or validation to sbom-tools. If a consumers mention
> isn't something you want in the README, that's completely fine.

## Notes for Sadjad — strip before posting

- Replace `#NNN` with the number the curve issue gets, or cut that sentence if
  you don't file it.
- The pipeline is the one in `docs/quickstart.md`, and the second line runs in
  CI against the captured output. Check the quickstart is live on the docs site
  before posting.
- Offering the PR, rather than asking them to write the line, is deliberate:
  it costs them a review instead of a task. Don't open the PR before they say
  yes — an unsolicited "add my tool" PR reads as exactly that.
- The README quote ("If you want diff and validation, use `sbom-tools`") is
  current as of 2026-09-29, `README.md` line ~106.
