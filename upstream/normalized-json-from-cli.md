# GitHub issue for `sbom-tool/sbom-tools` — posted

**POSTED 2026-09-06** as
[sbom-tool/sbom-tools#366](https://github.com/sbom-tool/sbom-tools/issues/366),
from the `lvlrSajjad` account, on your say-so in session. Kept as the record
of what was asked. The posted body differs from the draft below in two ways:
the "Notes for Sadjad" section was stripped, and the opening line cites #364
explicitly — it turned out to be docs-only (`README.md`,
`docs/PROJECT_BRIEF.md`), so it documented the contract without changing the
CLI surface, which is what made this request still worth filing.

**Repo:** <https://github.com/sbom-tool/sbom-tools>
**Title as posted:** `Expose the normalized JSON payload from the CLI`
**Labels:** none applied; theirs are not open to non-members.

Invited explicitly by the maintainer in
[#362](https://github.com/sbom-tool/sbom-tools/issues/362):

> If there's demand for the normalized JSON from the CLI rather than only via
> the bindings, that's a reasonable follow-up request — open a separate issue
> and we can discuss the shape.

and again when closing it: *"If a normalized-JSON output from the CLI would
help, please open a separate issue for it."*

So this is a wanted request, not an unsolicited one. It still should not be
posted without reading it first — the last one was posted from this repo, and
what came back changed what we ship.

---

## Body

Following up on #362 as invited.

**The ask:** a way to get the `NormalizedSbom` payload out of the CLI — the
same JSON that `sbom_tools_parse_sbom_path_json` and the bindings' `parse`
helpers already return.

**Why the bindings are not enough for this case.** The consumer here is a
Python tool that reads CBOMs and evaluates them against national PQC policies.
Reaching the normalized payload today means either linking the C ABI or
importing the in-tree Python binding, and the binding is not published to PyPI
— so a user who already has `sbom-tools` on their PATH still cannot pipe its
normalized output into another tool without building a native library first.
The CLI is the boundary most cross-tool composition happens at.

**Shape, in rough order of preference:**

1. A flag on the existing parse path, e.g. `sbom-tools parse <file> -o json`,
   emitting `NormalizedSbom` verbatim — no projection, no reshaping. Whatever
   the ABI returns for the same input, byte for byte.
2. Failing that, a distinct output value on `view`, e.g.
   `view <file> -o normalized`, kept clearly separate from the existing
   `-o json` projection so the two are never confused. (Speaking from
   experience: they *are* easy to confuse. Our quickstart shipped a
   `view -o json | ...` pipeline for four releases on the assumption that
   `view -o json` was the normalized payload. It carried no crypto fields at
   all, so it could never have produced a result. That was our error, but the
   naming made it an easy one to make.)

**What I am not asking for.** Not a stability guarantee. #362 was clear that
nested shape is not test-pinned, that there is no schema version separate from
the crate version, and that pre-1.0 a breaking JSON change is fair game in a
minor release with a note in the upgrade notes. That is a workable contract for
a consumer who pins your crate version, which is what we tell our users to do.
A CLI surface would not need to promise more than the ABI already does.

**Willing to send the PR** if the shape is agreed — happy to work to whichever
of the two forms above you prefer, or a third.

---

## Notes for Sadjad, not for the issue

*Not part of the posted body.*

- ~~Check first whether #364 already added this~~ — checked before posting.
  Docs only: `README.md` and `docs/PROJECT_BRIEF.md`. No CLI change.
- Our own use of this is genuinely marginal — raw CycloneDX is the primary
  path, the adapter is opt-in, and the maintainer's advice was to parse raw
  CycloneDX for exactly this job. The honest framing is "this would help
  cross-tool composition generally", not "we are blocked".
- `upstream/issue-draft.md` was the precedent for tone, and this followed it:
  one small concrete ask, sourced from their code, no compliance claims
  attached, and an explicit statement of what is *not* being asked for.
