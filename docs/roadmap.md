# Roadmap

## Before 1.0

**Verify `cnsa-2.0`.** The only pack still built from secondary reporting.
NSA's servers return HTTP 403 to automated requests, so it needs a human with a
browser. Its seven rules are already structured for the reading, and each
`open_question` names the sentence to find. The hybrid sentence matters most:
if NSA does not permit hybrids on mission systems outside named interoperability
exceptions, then paired with BSI or ANSSI **no single construction satisfies
every jurisdiction** — and that changes the output, not just a label.

**Re-verification cadence.** The ASD ISM is revised roughly monthly and will go
stale fastest. A scheduled CI job reports rules older than 180 days.

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
