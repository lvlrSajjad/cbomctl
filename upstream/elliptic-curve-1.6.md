# Issue for `sbom-tool/sbom-tools` — posted

**POSTED 2026-09-29** as
[sbom-tool/sbom-tools#374](https://github.com/sbom-tool/sbom-tools/issues/374),
from the `lvlrSajjad` account, by Claude on Sadjad's explicit one-off say-so in
session. Kept as the record of what was asked. The posted body differs from
the text below in three ways: paragraphs were unwrapped to one line each (as
#366 was), a first line names the build it was reproduced on, and the notes
section was stripped.

**Repo:** <https://github.com/sbom-tool/sbom-tools>
**Title:** `CycloneDX 1.6 algorithmProperties.curve is dropped; only 1.7's ellipticCurve is read`

Found on 2026-09-29 while running `convert --to normalized` end to end for the
first time (see `downstream-mention.md`). Everything below was reproduced with
their `main` at `a393479`, built `--no-default-features --features cli`.

---

`CdxAlgorithmProperties` in `src/parsers/cyclonedx.rs` deserializes
`elliptic_curve` under `rename_all = "camelCase"`, so it only matches
`ellipticCurve`, the CycloneDX 1.7 name. In 1.6, `curve` is the only curve
field in `algorithmProperties`; 1.7 keeps it as deprecated. For any 1.6 CBOM,
`elliptic_curve` comes out `null`.

**Real-world input.** CBOMkit's
[`example/keycloak-cbom.json`](https://github.com/cbomkit/cbomkit/tree/main/example)
is 1.6 and has four components with `curve` — `EC-secp521r1`, `EC-secp384r1`,
`EC-secp256r1` and `Ed25519` (`Edwards25519`). `convert --to normalized` gives
`elliptic_curve: null` for all four.

**Effect on `validate`.** The same key-agreement asset, with nothing but a curve
to classify it by:

```json
"cryptoProperties": {"assetType": "algorithm",
  "algorithmProperties": {"primitive": "key-agree", "curve": "secp256r1"}}
```

- as 1.6 with `curve` → `SBOM-CNSA2-ALG-UNKNOWN`, **Warning**: "'key-exchange'
  cannot be classified (no recognizable algorithm family, OID, or name)"
- as 1.7 with `"ellipticCurve": "secg/secp256r1"` → `SBOM-CNSA2-ALG-006`,
  **Error**: "'key-exchange' (EC-secg/secp256r1) is quantum-vulnerable, must
  migrate to CNSA 2.0 approved algorithm"

So `classify`'s curve signal (`src/model/crypto.rs`, the `elliptic_curve`
step) never fires on 1.6 input, and a quantum-vulnerable asset drops from
error to warning. On the Keycloak CBOM the names happen to carry the curve, so
the classification survives there; it is assets whose name, family and OID
don't carry it that change.

**On a fix.** `#[serde(alias = "curve")]` looks like the one-liner, but a 1.7
document carrying both the deprecated `curve` and `ellipticCurve` would then
fail with a duplicate-field error. A separate `curve: Option<String>` merged as
`elliptic_curve.or(curve)` where `algo.elliptic_curve` is set would keep 1.7
precedence. Happy to open a PR with that and a 1.6 fixture if it's useful.

---

## Notes for Sadjad — strip before posting

- Post this **before** the #366 comment in `downstream-mention.md`, or at least
  not in the same message: a bug report with a reproduction is a contribution;
  the listing ask is a favour. Leading with the first makes the second easy.
- The duplicate-field claim is standard serde derive behaviour, not something
  run against their code. If they ask, it's reasoning, not a test.
- "Happy to open a PR" is a real offer — the change is ~5 lines plus a fixture
  — only make it if you'd do it.
