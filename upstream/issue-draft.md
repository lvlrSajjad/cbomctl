# DRAFT — GitHub issue for `sbom-tool/sbom-tools`

**POSTED AND CLOSED.** Filed as
[sbom-tool/sbom-tools#362](https://github.com/sbom-tool/sbom-tools/issues/362)
and answered in full by the maintainer; they documented the outcome in their
#364 and closed it. Kept as the record of what was asked. The answer is
summarised in `src/cbomctl/loader/sbom_tools.py` and in the CHANGELOG entry
that supersedes our earlier "shape inferred from their structs" disclosure.

The one follow-up it invited — normalized JSON from their CLI — is drafted
separately in [`normalized-json-from-cli.md`](normalized-json-from-cli.md),
**unposted**.

**Repo:** <https://github.com/sbom-tool/sbom-tools>
**Suggested title:** `Is the normalized JSON payload a stable contract for downstream consumers?`
**Suggested labels:** `question`, or whatever they use for docs

> Superseded the earlier draft, which proposed BSI/ANSSI/ASD PQC profiles.
> That ask was dropped: it committed us to authoring Rust rule tables against
> regulations we had not yet verified, and it asked them to carry compliance
> assertions sourced from our reading. This version asks for one small thing we
> actually need.

---

## Body

*Context: I'm building a small tool that consumes CBOMs and evaluates them
against national PQC policies, and `sbom-tools` output is one of the input
forms I'd like to support.*

I'd like to read `sbom-tools view <cbom> -o json` as an input format, but I
can't tell from the docs whether that payload is intended as a stable contract
or as an internal representation that happens to be serializable. From the
source, `Component` derives `Serialize` and carries `crypto_properties` with no
serde renames, so fields arrive snake_cased — but that's an implementation
detail I'd be depending on, not a documented guarantee. Concretely: are the
`cryptoProperties`-derived fields (`asset_type`, `algorithm_properties`,
`primitive`, `crypto_functions`, `parameter_set_identifier`, `elliptic_curve`,
`oid`) guaranteed present in normalized output for CBOM inputs, and is the
payload shape versioned separately from the crate version?

One specific behaviour I'd want to depend on either way, and would be happy to
document rather than change: `src/parsers/cyclonedx.rs` maps both an absent
`primitive` and an explicit `primitive: "unknown"` to `CryptoPrimitive::Unknown`.
That's the right call for an allowlist checker, and it doesn't change any
verdict for me either — but it does mean a downstream consumer can't tell a
generator that *omitted* the field from one that *said it didn't know*, which is
a distinction worth surfacing to a user when a finding is unresolvable. If the
JSON is a supported contract, a note in the docs would be enough; if it isn't
one, I'd rather know that now and parse raw CycloneDX instead of coupling to a
shape that may move. Either answer is genuinely useful — no feature request
attached.
