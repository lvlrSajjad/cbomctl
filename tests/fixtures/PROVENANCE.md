# Fixture provenance

Stated because a hand-built fixture that looks captured is a way to fool
yourself about what your tool handles.

| file | provenance |
|---|---|
| `cbomkit-keycloak.json` | **Real** CBOMkit output, [cbomkit/cbomkit `example/keycloak-cbom.json`](https://github.com/cbomkit/cbomkit/tree/main/example). 56 components. The messy case: 6 of 22 algorithm components carry no `cryptoFunctions`, `AES`/`HMACSHA2` are tagged `primitive: other`, and four EC keys are tagged `pke` (a fifth `pke` component is RSA-2048). |
| `cbomkit-kafka.json` | **Real** CBOMkit output, same repo. 11 components. |
| `spec-conformance-1.6.json` | CycloneDX's own `valid-cryptography-full-1.6.json` conformance fixture. All four asset types. |
| `conflict-hybrid.json` | **Hand-built.** The four-way conflict case: a hybrid KEM, a classical KEM, an ambiguous RSA key, and a PQ signature. |
| `rsa-strength-split.json` | **Hand-built.** RSA-2048 and RSA-3072, identical but for modulus size, to pin that IR 8547's 112-bit deprecation reaches one and not the other. |
| `schemas/tool-center-v2.tool.schema.json` | **Vendored**, unmodified: CycloneDX/tool-center [`schemas/tool.schema.json`](https://github.com/CycloneDX/tool-center/blob/main/schemas/tool.schema.json) at commit `fb39a9915635` (2025-11-13), fetched 2026-09-06. draft-07, 17,473 bytes, `$id` `https://cyclonedx.org/schema/tool-center-v2.tool.schema.json` — the copy served at that `$id` parses to the same document, minified. Pinned so `tests/test_tool_center_entry.py` validates the Tool Center submission offline; `ci.yml` diffs it against their `main` so upstream movement is a separate, named failure. It sits in `schemas/` rather than beside the CBOMs because it is not one, and because the `cbom-schema-conformance` job globs `tests/fixtures/*.json`. |
| `sbom-tools-normalized.json` | **Constructed** from `sbom-tools` Rust struct definitions (snake_case, no serde renames), *not* captured from a run of their binary. The shape is now **confirmed by the maintainer** ([issue 362](https://github.com/sbom-tool/sbom-tools/issues/362)), who stated the normalized payload arrives "snake_case, no serde renames, `Option` fields as `null`, and `crypto_properties` itself omitted when the component has none". It is the payload of `parse_path_json` / `parse_string_json`, **not** of `sbom-tools view -o json` — which is a curated projection carrying no crypto fields at all. The file was named `sbom-tools-view.json` until 2026-09-06, and that name is what put a `view -o json` pipeline into the quickstart. |
