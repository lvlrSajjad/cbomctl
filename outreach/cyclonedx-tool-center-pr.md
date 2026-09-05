# PR draft — CycloneDX Tool Center listing

**DRAFT — do not open until cbomctl is public and installable.** The Tool
Center lists things people can use; submitting a repository that doesn't exist
yet would be listing vapour.

**Repo:** <https://github.com/CycloneDX/tool-center>
**Process** (read from their README): open a PR adding a file under `tools/`.
Contributions must be relevant to SBOM/xBOM generation, analysis or consumption;
metadata must be accurate and current. They offer
[MetaConfigurator](https://www.metaconfigurator.org?schema=https://raw.githubusercontent.com/CycloneDX/tool-center/refs/heads/main/schemas/tool.schema.json)
as an alternative to hand-editing — the hand-written file below validates
against `schemas/tool.schema.json` (specVersion 2.0), so either route works.

**Branch:** `add-cbomctl` · **File:** `tools/cbomctl.json`

Enum values below are taken from their schema, not guessed. `capabilities: CBOM`
and `analysis: POLICY_EVALUATION` are the ones that matter — `POLICY_EVALUATION`
is precisely what this tool does, and it is a less crowded slot than
`SECURITY_VULNERABILITIES`.

## File contents

```json
{
  "$schema": "https://cyclonedx.org/schema/tool-center-v2.tool.schema.json",
  "specVersion": "2.0",
  "tool": {
    "name": "cbomctl",
    "publisher": "Sadjad Asadi",
    "description": "Evaluates a CycloneDX CBOM against multiple national post-quantum cryptography policies at once (BSI, ANSSI, ASD, CNSA 2.0, EO 14412, EU roadmap) and reports where their verdicts contradict each other. Every rule carries a primary source, a verification date, and an explicit classification of its binding force.",
    "repository_url": "https://github.com/lvlrSajjad/cbomctl",
    "website_url": "https://github.com/lvlrSajjad/cbomctl",
    "capabilities": ["CBOM"],
    "availability": ["OPEN_SOURCE", "OSI_APPROVED"],
    "functions": ["ANALYSIS"],
    "analysis": ["POLICY_EVALUATION"],
    "transform": [],
    "packaging": ["COMMAND_LINE_UTILITY", "GITHUB_ACTION"],
    "library": ["PYTHON"],
    "platform": ["LINUX", "MAC", "WINDOWS"],
    "lifecycle": ["POST-BUILD", "OPERATIONS"],
    "supportedStandards": ["CYCLONEDX"],
    "cycloneDxVersion": ["CYCLONEDX_V1.7", "CYCLONEDX_V1.6"],
    "supportedLanguages": []
  }
}
```

`supportedLanguages` is deliberately empty: it means source languages a tool
analyses, and this one reads CBOMs rather than code. `lifecycle` is
`POST-BUILD` / `OPERATIONS` because it consumes an existing CBOM rather than
producing one during a build.

## PR title

`Add cbomctl (CBOM policy evaluation)`

## PR description

Adds `cbomctl`, an open-source (Apache-2.0) CLI that consumes a CycloneDX 1.6 /
1.7 CBOM and evaluates it against several national post-quantum cryptography
policies simultaneously, reporting a per-asset × jurisdiction verdict matrix
plus the conflicts between them.

The gap it fills: national PQC guidance has diverged in ways that matter for
anyone shipping into more than one market. BSI and ANSSI recommend hybrid key
establishment; ASD's ISM recommends against it; CNSA 2.0 asks for ML-KEM-1024
where others accept ML-KEM-768. Tools generally evaluate one framework at a time
and report PASS/FAIL, which hides the contradiction. `cbomctl` computes it and
names a satisfies-all target where one exists.

Two things I'd flag rather than have a reviewer discover:

- **It consumes CBOMs, it does not generate them.** It complements the
  generators already in the Tool Center rather than competing with them.
  `capabilities: ["CBOM"]` and `analysis: ["POLICY_EVALUATION"]` are chosen to
  reflect that; happy to change either if the maintainers read the taxonomy
  differently.
- **The policy rules are versioned separately from the tool** and are
  consumable without it, with a primary-source URL, a verification date and a
  binding classification (statute / executive order / agency requirement /
  certification requirement / guideline recommendation) on every rule. The
  binding field exists because most PQC guidance is *not* a mandate, and
  reporting a technical guideline as a legal requirement is a common failure
  mode.

The JSON validates against `schemas/tool.schema.json` (specVersion 2.0). Happy
to adjust any field.
