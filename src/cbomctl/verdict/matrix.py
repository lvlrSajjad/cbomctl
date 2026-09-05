"""Build the asset × jurisdiction matrix. The product."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from cbomctl.config import Config
from cbomctl.models import Cell, CryptoAsset, Risk, Unscored, Verdict
from cbomctl.policy.engine import evaluate
from cbomctl.policy.schema import Pack
from cbomctl.scoring import mosca


class Row(BaseModel):
    bom_ref: str
    display: str
    purpose: str
    purpose_signal: str
    construction: str
    quantum_status: str
    cells: dict[str, Cell]
    risk: Risk | None = None
    unscored: Unscored | None = None
    locations: list[str] = Field(default_factory=list)
    conflict_ids: list[str] = Field(default_factory=list)

    @property
    def worst(self) -> Verdict:
        return max((c.verdict for c in self.cells.values()),
                   key=lambda v: v.rank, default=Verdict.PASS)

    @property
    def governing_deadline(self) -> date | None:
        ds = [c.governing_deadline for c in self.cells.values() if c.governing_deadline]
        return min(ds) if ds else None


class Matrix(BaseModel):
    schema_version: str = "1.0"
    evaluated_at: date
    jurisdictions: list[str]
    assumptions: dict[str, object]
    unverified_packs: list[str] = Field(default_factory=list)
    strict: bool = False
    rows: list[Row] = Field(default_factory=list)

    @property
    def has_unverified(self) -> bool:
        return bool(self.unverified_packs)

    @property
    def draft_rules(self) -> list[str]:
        """Rules whose source is a draft. A verified reading of a draft is
        still a draft: the dates are proposed and may move."""
        seen: dict[str, None] = {}
        for row in self.rows:
            for jid, cell in row.cells.items():
                for ref in cell.rules:
                    if ref.is_draft:
                        seen[f"{jid}/{ref.rule_id}"] = None
        return sorted(seen)

    @property
    def exit_code(self) -> int:
        worst = [r.worst for r in self.rows]
        if Verdict.FAIL in worst:
            return 1
        if self.strict and (Verdict.INDETERMINATE in worst):
            return 3
        return 0


def build(
    assets: list[CryptoAsset],
    packs: list[Pack],
    config: Config,
    *,
    crqc_year: int = mosca.DEFAULT_CRQC_YEAR,
    migration_years: float | None = None,
    include_acquisition_gate: bool = False,
    strict: bool = False,
    today: date | None = None,
) -> Matrix:
    now = today or date.today()
    migration = migration_years if migration_years is not None else config.defaults.migration_years

    rows: list[Row] = []
    for asset in assets:
        if asset.asset_type not in ("algorithm", "protocol"):
            continue

        lifetime, source, _ = config.for_asset(asset)
        scored = mosca.score(
            asset, lifetime_years=lifetime, lifetime_source=source,
            migration_years=migration, crqc_year=crqc_year, today=now,
        )
        cells = {
            p.id: evaluate(
                p, asset,
                system_category=config.system_category,
                include_acquisition_gate=include_acquisition_gate,
                strict=strict,
            )
            for p in packs
        }
        rows.append(Row(
            bom_ref=asset.bom_ref,
            display=asset.display,
            purpose=asset.purpose.value,
            purpose_signal=asset.purpose_signal.value,
            construction=asset.construction.value,
            quantum_status=asset.quantum_status.value,
            cells=cells,
            risk=scored if isinstance(scored, Risk) else None,
            unscored=scored if isinstance(scored, Unscored) else None,
            locations=[f"{l.file}:{l.line}" if l.line else (l.file or "")
                       for l in asset.locations if l.file][:5],
        ))

    # Worst verdict first, then earliest binding deadline, then bom_ref so the
    # output is stable across runs.
    rows.sort(key=lambda r: (
        -r.worst.rank,
        -(r.risk.exposure_years if r.risk else 0),
        r.governing_deadline or date(9999, 12, 31),
        r.bom_ref,
    ))

    return Matrix(
        evaluated_at=now,
        jurisdictions=[p.id for p in packs],
        assumptions={
            "crqc_year": crqc_year,
            "migration_years": migration,
            "default_data_lifetime_years": config.defaults.data_lifetime_years,
            "system_category": config.system_category,
            "crqc_note": ("A planning assumption matching the NSM-10 / EU "
                          "horizon, not a prediction."),
        },
        unverified_packs=[p.id for p in packs if not p.is_verified],
        strict=strict,
        rows=rows,
    )
