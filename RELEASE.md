# Release checklist

Nothing here is automated end-to-end on purpose. Publishing is irreversible and
the packs make compliance-adjacent claims under your name.

## One-time setup (yours, not mine)

1. ~~**Create the GitHub repository**~~ — done: <https://github.com/lvlrSajjad/cbomctl>
2. **PyPI trusted publishing.** On PyPI, add a *pending publisher* for project
   `cbomctl`: owner `lvlrSajjad`, repository `cbomctl`, workflow
   `release.yml`, environment `pypi`. No API token is stored anywhere.
3. **GitHub environment** named `pypi` (Settings → Environments). Optionally
   require your own approval on it, which gives a manual gate before upload.
4. **GitHub Pages** — Settings → Pages → Source: GitHub Actions.

## Pre-flight

```bash
./scripts/check.sh
```

Runs everything CI runs, with honest exit codes. Written after a
`mkdocs build --strict 2>/dev/null && echo ok` reported a green docs build that
CI then failed — stderr was discarded and the exit code checked belonged to
`grep`. Do not hand-roll the check.

Confirm the identity one more time, since this is the irreversible step:

```bash
git config user.name && git config user.email && \
  GH_CONFIG_DIR=~/.config/gh-personal gh auth status
```

Expect `Sadjad Asadi <lvlr.xaus@gmail.com>` and account `lvlrSajjad`.

## Publish

The repository is already public and `main` is pushed. Releasing is the tag:

```bash
./scripts/check.sh                     # must be green
git tag -a v0.1.0 -m "v0.1.0 — all seven policy packs verified from primary sources"
git push origin v0.1.0
```

The tag triggers `release.yml`, which refuses to publish unless the suite
passes, the tag matches `pyproject.toml`, every rule cites an allowlisted
primary source, and the wheel contains all seven packs.

## Then, in order

1. **Watch the Actions run.** If `pypi` has a required reviewer, approve it.
2. **Check `pip install cbomctl` from a clean venv** before telling anyone.
3. **Verify the docs site** at `lvlrSajjad.github.io/cbomctl`.
4. **Publish article 2** (`RSA-2048 and RSA-3072 have different futures`). It
   makes no claim about the tool being novel and establishes the sourcing
   discipline. Best first impression.
5. **Article 1** — publish whenever; it is independent of the Show HN, which
   links the repository rather than the article.
6. **Show HN** — Tue–Thu, 09:00–11:00 America/New_York, which is 15:00–17:00
   CEST. Not a weekend: Sunday is the weakest day there and it is one shot. Be
   free for ~3 hours after posting.
7. **Article 3** a week later.
8. **Upstream drafts** — the [sbom-tools issue](upstream/issue-draft.md) once
   the repo is public so the context line resolves; the
   [CycloneDX Tool Center PR](outreach/cyclonedx-tool-center-pr.md) once
   `pip install` works.
9. **CfP** — [PKI Consortium](outreach/pki-consortium-cfp.md), check the
   deadline first.

## Do not

- Publish any article before the repository is public. Every demo block invokes
  `cbomctl` and readers will go looking for it.
- Remove the unverified-policy banner, the `status` field, or
  `--require-verified-policy` to make output look cleaner. They are what keeps
  the next rule honest, and they are the reason this is defensible.
- Let a pack go more than ~180 days past `last_verified`. The ASD ISM is
  revised roughly monthly and will drift first. CI reports staleness weekly.

## After release

Open issues for the roadmap items so contributors have somewhere to land: UK
NCSC pack, IR 8547 Tables 6–7, EU roadmap Part 2 and the 2026 FAQ, protocol
asset evaluation, and a cdxgen fixture if anyone has one.
