"""SARIF 2.1.0 — our risk and conflict findings only.

Deliberately does not restate what a generator or validator already reported.
These sit *beside* other tools' findings in the GitHub Security tab.
"""

from __future__ import annotations

import json

from cbomctl.models import Conflict, Verdict
from cbomctl.verdict.matrix import Matrix

_LEVEL = {
    Verdict.FAIL: "error",
    Verdict.WARN: "warning",
    Verdict.INDETERMINATE: "note",
    Verdict.INFO: "note",
    Verdict.PASS: "none",
    Verdict.NOT_APPLICABLE: "none",
}


def _location(loc: str) -> dict:
    path, _, line = loc.partition(":")
    region = {"startLine": int(line)} if line.isdigit() else {"startLine": 1}
    return {"physicalLocation": {
        "artifactLocation": {"uri": path},
        "region": region,
    }}


def render(matrix: Matrix, conflicts: list[Conflict]) -> str:
    rules: dict[str, dict] = {}
    results: list[dict] = []

    for row in matrix.rows:
        for jid, cell in sorted(row.cells.items()):
            if cell.verdict in (Verdict.PASS, Verdict.NOT_APPLICABLE):
                continue
            for ref in cell.rules:
                rid = f"{jid}/{ref.rule_id}"
                if rid not in rules:
                    text = ref.description.strip() or ref.rule_id
                    if ref.is_draft:
                        text = f"[DRAFT SOURCE] {text}"
                    if ref.status.value != "verified":
                        text = f"[UNVERIFIED RULE] {text}"
                    rules[rid] = {
                        "id": rid,
                        "shortDescription": {"text": f"{jid}: {ref.rule_id}"},
                        "fullDescription": {"text": text},
                        "helpUri": ref.source_url,
                        "properties": {
                            "binding": ref.binding.value,
                            "status": ref.status.value,
                            "isDraft": ref.is_draft,
                            "source": ref.source_title,
                        },
                    }
                msg = (f"{row.display} ({row.purpose}) — {cell.verdict.value} under "
                       f"{jid}. {ref.description.strip()}")
                if ref.deadline:
                    msg += f" Deadline {ref.deadline.isoformat()}."
                if ref.status.value != "verified":
                    msg += (" This rule is UNVERIFIED: assembled from secondary "
                            "reporting, not read from a primary source.")
                results.append({
                    "ruleId": rid,
                    "level": _LEVEL[cell.verdict],
                    "message": {"text": msg},
                    "locations": [_location(l) for l in row.locations] or [
                        {"physicalLocation": {
                            "artifactLocation": {"uri": "cbom.json"},
                            "region": {"startLine": 1}}}],
                    "partialFingerprints": {"cbomctl/v1": f"{row.bom_ref}/{rid}"},
                })

    conflict_rule = "cbomctl/jurisdiction-conflict"
    if conflicts:
        rules[conflict_rule] = {
            "id": conflict_rule,
            "shortDescription": {"text": "Jurisdictions disagree about this asset"},
            "fullDescription": {"text": (
                "Two or more selected jurisdictions impose requirements that "
                "cannot both be optimally satisfied for this asset.")},
            "properties": {"binding": "n/a"},
        }
    for c in conflicts:
        row = next((r for r in matrix.rows if r.bom_ref == c.bom_ref), None)
        text = f"[{c.kind}] {c.summary}"
        if c.satisfies_all:
            text += f" Satisfies all: {c.satisfies_all}."
        if c.cost_note:
            text += f" {c.cost_note}"
        if c.alternative_reading:
            text += f" CONTESTED ENCODING: {c.alternative_reading}"
        results.append({
            "ruleId": conflict_rule,
            "level": "warning",
            "message": {"text": text},
            "locations": [_location(l) for l in (row.locations if row else [])] or [
                {"physicalLocation": {
                    "artifactLocation": {"uri": "cbom.json"},
                    "region": {"startLine": 1}}}],
            "partialFingerprints": {"cbomctl/v1": f"{c.bom_ref}/{c.kind}"},
        })

    doc = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {
                "name": "cbomctl",
                "informationUri": "https://github.com/lvlrSajjad/cbomctl",
                "rules": [rules[k] for k in sorted(rules)],
            }},
            "results": results,
        }],
    }
    return json.dumps(doc, indent=2, ensure_ascii=False)
