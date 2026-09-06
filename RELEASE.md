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

<!-- unverified: reads this machine's git and gh configuration. Not executed by
     scripts/check_commands.py, because what it asserts is a property of your
     workstation, not of the repository. Run it yourself and read the output. -->
```bash
git config user.name && git config user.email && \
  GH_CONFIG_DIR=~/.config/gh-personal gh auth status
```

Expect `Sadjad Asadi <lvlr.xaus@gmail.com>` and account `lvlrSajjad`.

## Publish

The repository is already public and `main` is pushed. Releasing is the tag:

<!-- unverified: pushes a tag, which is irreversible and publishes to PyPI.
     Nothing in CI runs this, and nothing should. The version must match
     `pyproject.toml` — release.yml enforces that and will fail if it does not. -->
```bash
./scripts/check.sh                     # must be green
git tag -a v0.1.3 -m "v0.1.3 — an action.yml the Marketplace will accept"
git push origin v0.1.3
```

The tag triggers `release.yml`, which refuses to publish unless the suite
passes, the tag matches `pyproject.toml`, every rule cites an allowlisted
primary source, and the wheel contains all seven packs.

Then move the major tag, so `uses: lvlrSajjad/cbomctl@v0` — the form
[docs/ci.md](docs/ci.md) hands to readers — points at the release just cut.
`release.yml` deliberately ignores `v0` (`tags: ["v*.*.*"]`), because a moving
tag would fail its version gate by construction:

<!-- unverified: force-pushes a tag other people's workflows resolve. Not run
     in CI; the tag it moves is checked by scripts/check_commands.py, which
     fails if docs/ci.md names a ref this repository does not have. -->
```bash
git tag -f v0 v0.1.3
git push -f origin v0
```

## Then, in order

1. **Watch the Actions run.** If `pypi` has a required reviewer, approve it.
2. **Check `pip install cbomctl` from a clean venv** before telling anyone.
   `scripts/check_commands.py` only resolves the name on the index; it does
   not install, and cannot tell you the console script works. Last done
   2026-09-06 against 0.1.3: installs, `cbomctl --help` exits 0, and
   `cbomctl verdict tests/fixtures/conflict-hybrid.json` renders the matrix.
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
8. **Upstream drafts** — the sbom-tools JSON-contract question is
   [posted, answered and closed](https://github.com/sbom-tool/sbom-tools/issues/362);
   its record is [`upstream/issue-draft.md`](upstream/issue-draft.md). The
   follow-up it invited — normalized JSON from their CLI — is drafted and
   **unposted** in
   [`upstream/normalized-json-from-cli.md`](upstream/normalized-json-from-cli.md);
   read it before sending. The
   [CycloneDX Tool Center PR](outreach/cyclonedx-tool-center-pr.md) goes out
   once `pip install` works — it does; verified from a clean venv on
   2026-09-06.
9. ~~**CfP** — PKI Consortium Amsterdam~~ — **declined 2026-09-06**: speakers
   must attend in person and self-fund; travel is not possible in this window.
   The [abstract](outreach/pki-consortium-cfp.md) is kept as reusable material.

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
