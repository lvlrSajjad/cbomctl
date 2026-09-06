# Roadmap

## Keeping it true

**Re-verification cadence.** All seven packs are verified as of 2026-09-06. The
ASD ISM is revised roughly monthly and will go stale first; NIST IR 8547 is a
draft that may finalise and move its dates. A scheduled CI job reports rules
older than 180 days.

**One reading worth revisiting.** The CNSA 2.0 FAQ answers the hybrid question
twice with different force, and the stronger answer is framed "while waiting for
a final NIST post-quantum standard" — a premise that arguably ended when FIPS
203/204/205 finalised. We encoded the stronger reading and
[wrote down why](policy-sources.md). If a later revision drops that framing, the
stance may need to change from `not_permitted_except_interop` to `silent`, and
that would restore a satisfies-all target to the conflict output.

## Wanted

**More jurisdictions.** UK NCSC is the obvious gap — it appears in
`open-quantum-secure`'s framework list and nowhere in ours. Canada's CCCS,
Japan's CRYPTREC and Singapore's CSA are also unrepresented. Each new pack is a
commitment to keep it verified; see [CONTRIBUTING](https://github.com/lvlrSajjad/cbomctl/blob/main/CONTRIBUTING.md).

**More of the documents we have already read.** NIST IR 8547 Tables 6 and 7
(block ciphers, hash functions) are not yet encoded. The EU roadmap's Part 2 and
its April 2026 FAQ are unread. BSI §2.4's acceptance of FrodoKEM and Classic
McEliece — jurisdiction-specific algorithm approval — is not modelled.

**Generator coverage.** CBOMkit output is verified against real files. cdxgen is
listed as **untested**: a code search of its repository finds no
`cryptoProperties` handling. If you have run it and produced a CBOM, a fixture
would settle it.

**Protocol assets.** `cryptoProperties.protocolProperties` — TLS versions,
cipher suites, IKEv2 transforms — is parsed but not yet evaluated against
policy. Cipher-suite-level verdicts are a natural next step and would make the
IKEv2 exception in CNSA 2.0 expressible.

## Explicitly not planned

**CBOM generation.** Crowded and solved. Use
[CBOMkit](https://github.com/cbomkit/cbomkit) or
[open-quantum-secure](https://github.com/jimbo111/open-quantum-secure).

**SBOM diffing and validation.**
[sbom-tools](https://github.com/sbom-tool/sbom-tools) does it well.

**Guessing purpose from call sites.** `evidence.occurrences` context is captured
and shown, never allowed to decide. A future `--infer-from-evidence` could opt
in, but the default must not — a tool that silently upgrades a guess to a
verdict is the thing this one exists to replace.

**Anything that makes an unverified rule look verified.** The banner mechanism,
the `status` field and `--require-verified-policy` are load-bearing. Cleaner
output is not a reason to weaken them.

### Running the CBOMkit half of `docs/ci.md`

**Considered on 2026-09-06 and not built.** The idea was a scheduled CI job
that materialises the workflow snippet on [the CI page](ci.md) into a real
workflow file and executes it against a small fixture repository, so the
CBOMkit step is exercised rather than transcribed. Three reasons it is not
worth its weight:

**It would not run the documented snippet.** A workflow cannot execute a
workflow file it has just written; you would have to commit the generated file
to a branch and dispatch it, or inline its steps into the scheduled job. Inlined
steps are a transcription of the page — which is the gap being closed, reopened
one layer down. Committing the file means the thing that runs is an artifact
that has to be kept byte-identical to the page, which is another check, on top
of the one that was supposed to replace a check.

**It would mostly test somebody else's tool.** `cbomkit/cbomkit-action@main` is
an unpinned ref that pulls `ghcr.io/cbomkit/cbomkit-action:edge` and runs a Java
scanner over source. A red run would usually mean their edge image moved, which
tells us nothing about whether our page is right, and a scheduled job whose
failures are usually not ours is a job people learn to ignore.

**The claim the page actually makes is checkable without running anything.** It
claims their action takes no `with:` inputs and reads the environment variables
named. Both are facts in files — their `action.yml` and their README — and
`scripts/check_commands.py` now fetches both at the ref the page names and
checks them on every run, for their action as well as ours. That is the check
that would have caught the 0.1.4 bug (`with: { output: cbom.json }` passed to an
action declaring no inputs), and it caught a second one when it was written: the
consolidated CBOM lands at `cbom/cbom.json`, not `cbom.json`.

What remains unchecked is narrow and stated on the page: that the workflow runs
end to end, and that the output path read from their `Main.java` is the path the
container produces. If someone runs it, a note saying so is worth more than the
job.
