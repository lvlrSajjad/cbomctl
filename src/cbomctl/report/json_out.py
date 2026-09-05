"""Deterministic JSON. Same inputs, byte-identical output."""

from __future__ import annotations

import json

from cbomctl.models import Conflict
from cbomctl.verdict.matrix import Matrix


def render(matrix: Matrix, conflicts: list[Conflict]) -> str:
    payload = {
        "schema_version": matrix.schema_version,
        "evaluated_at": matrix.evaluated_at.isoformat(),
        "jurisdictions": matrix.jurisdictions,
        "assumptions": matrix.assumptions,
        "policy_warning": (
            None if not matrix.has_unverified else {
                "level": "unverified",
                "message": ("UNVERIFIED POLICY PACK — not for compliance use. "
                            "Rules were assembled from secondary reporting and "
                            "have not been read from primary sources."),
                "packs": matrix.unverified_packs,
            }
        ),
        "matrix": [
            {
                "bom_ref": r.bom_ref,
                "display": r.display,
                "purpose": r.purpose,
                "purpose_signal": r.purpose_signal,
                "construction": r.construction,
                "quantum_status": r.quantum_status,
                "locations": r.locations,
                "governing_deadline": (r.governing_deadline.isoformat()
                                       if r.governing_deadline else None),
                "worst": r.worst.value,
                "conflict_ids": r.conflict_ids,
                "risk": (json.loads(r.risk.model_dump_json()) if r.risk else None),
                "unscored": (json.loads(r.unscored.model_dump_json())
                             if r.unscored else None),
                "cells": {
                    j: {
                        "verdict": c.verdict.value,
                        "note": c.note,
                        "rules": [
                            {
                                "rule_id": ref.rule_id,
                                "binding": ref.binding.value,
                                "status": ref.status.value,
                                "is_draft": ref.is_draft,
                                "hybrid": ref.hybrid.value if ref.hybrid else None,
                                "rationale": ref.rationale.value if ref.rationale else None,
                                "deadline": ref.deadline.isoformat() if ref.deadline else None,
                                "deadline_state": (ref.deadline_state.value
                                                   if ref.deadline_state else None),
                                "source_url": ref.source_url,
                                "source_title": ref.source_title,
                                "description": ref.description.strip(),
                            }
                            for ref in c.rules
                        ],
                    }
                    for j, c in sorted(r.cells.items())
                },
            }
            for r in matrix.rows
        ],
        "conflicts": [json.loads(c.model_dump_json()) for c in conflicts],
        "exit_code": matrix.exit_code,
    }
    return json.dumps(payload, indent=2, sort_keys=False, ensure_ascii=False)
