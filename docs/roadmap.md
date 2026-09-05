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
