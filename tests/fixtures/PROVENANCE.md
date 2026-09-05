# Fixture provenance

Stated because a hand-built fixture that looks captured is a way to fool
yourself about what your tool handles.

| file | provenance |
|---|---|
| `cbomkit-keycloak.json` | **Real** CBOMkit output, [cbomkit/cbomkit `example/keycloak-cbom.json`](https://github.com/cbomkit/cbomkit/tree/main/example). 56 components. The messy case: 6 of 22 algorithm components carry no `cryptoFunctions`, `AES`/`HMACSHA2` are tagged `primitive: other`, and five EC keys are tagged `pke`. |
| `cbomkit-kafka.json` | **Real** CBOMkit output, same repo. 11 components. |
| `spec-conformance-1.6.json` | CycloneDX's own `valid-cryptography-full-1.6.json` conformance fixture. All four asset types. |
| `conflict-hybrid.json` | **Hand-built.** The four-way conflict case: a hybrid KEM, a classical KEM, an ambiguous RSA key, and a PQ signature. |
| `sbom-tools-view.json` | **Constructed** from `sbom-tools` Rust struct definitions (snake_case, no serde renames), *not* captured from a run of their binary. The shape is inferred and may be wrong; see `upstream/issue-draft.md`. |
