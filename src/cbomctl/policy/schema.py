"""Policy pack models.

Two fields carry most of the weight. `binding` decides FAIL versus WARN —
severity does not — because most PQC guidance is not a mandate and reporting a
technical guideline as a legal requirement misinforms the user. `hybrid` is
scoped per purpose via `applies_to.purpose`, because authorities take different
positions on key establishment and on signatures.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, field_validator

from cbomctl.models import (
    Binding, Construction, DeadlineState, HybridStance, Purpose,
    QuantumStatus, Rationale, RuleStatus, Verdict,
)

#: `source_url` must point at a primary source. Secondary reporting belongs in
#: docs/policy-sources.md for traceability, never in a rule.
ALLOWED_SOURCE_HOSTS = (
    "nsa.gov", "csrc.nist.gov", "nist.gov", "whitehouse.gov",
    "federalregister.gov", "bsi.bund.de", "cyber.gouv.fr", "ssi.gouv.fr",
    "cyber.gov.au", "digital-strategy.ec.europa.eu", "eur-lex.europa.eu",
    "media.defense.gov",
)


class AppliesTo(BaseModel):
    purpose: list[Purpose] = Field(default_factory=list)
    quantum_status: list[QuantumStatus] = Field(default_factory=list)
    construction: list[Construction] = Field(default_factory=list)
    algorithm: list[str] = Field(default_factory=list)
    system_category: list[str] = Field(default_factory=list)
    security_level: list[str] = Field(default_factory=list)


class MigrationTarget(BaseModel):
    kem: str | None = None
    signature: str | None = None
    symmetric: str | None = None
    hash: str | None = None
    construction: Construction | None = None
    note: str | None = None


class Rule(BaseModel):
    id: str
    description: str
    binding: Binding
    status: RuleStatus
    source_url: str
    source_title: str
    source_edition: str | None = None
    is_draft: bool = False
    last_verified: date
    verified_by: str | None = None
    deadline: date | None = None
    deadline_state: DeadlineState | None = None
    applies_to: AppliesTo = Field(default_factory=AppliesTo)
    hybrid: HybridStance | None = None
    rationale: Rationale | None = None
    rationale_note: str | None = None
    migration_target: MigrationTarget | None = None
    verdict: Verdict = Verdict.FAIL
    open_question: str | None = None

    @field_validator("verdict", mode="before")
    @classmethod
    def _parse_verdict(cls, v: object) -> object:
        return Verdict.parse(str(v)) if isinstance(v, str) else v

    @field_validator("source_url")
    @classmethod
    def _primary_source_only(cls, v: str) -> str:
        if not any(h in v for h in ALLOWED_SOURCE_HOSTS):
            raise ValueError(
                f"source_url must be a primary source; {v!r} is not on the "
                f"allowlist ({', '.join(ALLOWED_SOURCE_HOSTS)})"
            )
        return v

    @property
    def effective_verdict(self) -> Verdict:
        """A recommendation cannot produce FAIL, whatever the YAML says."""
        if self.verdict is Verdict.FAIL and not self.binding.is_mandatory:
            return Verdict.WARN
        return self.verdict


class Pack(BaseModel):
    id: str
    name: str
    authority: str
    jurisdiction: str
    pack_version: str
    applicability: str
    notes: str | None = None
    rules: list[Rule]

    @property
    def is_verified(self) -> bool:
        return all(r.status is RuleStatus.VERIFIED for r in self.rules)

    @property
    def unverified_rules(self) -> list[Rule]:
        return [r for r in self.rules if r.status is not RuleStatus.VERIFIED]

    @classmethod
    def from_file(cls, path: str | Path) -> "Pack":
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        return cls.model_validate(data)


def pack_dir() -> Path:
    """Packs ship inside the wheel; fall back to the repo layout in a checkout.

    The packaged directory only wins if it actually holds packs — an empty
    directory left by a partial build must not shadow the source of truth.
    """
    packaged = Path(__file__).resolve().parent.parent / "packs"
    if packaged.is_dir() and any(packaged.glob("*.yaml")):
        return packaged
    return Path(__file__).resolve().parents[3] / "policy-packs" / "packs"


def load_pack(pack_id: str) -> Pack:
    path = pack_dir() / f"{pack_id}.yaml"
    if not path.is_file():
        available = ", ".join(sorted(p.stem for p in pack_dir().glob("*.yaml")))
        raise FileNotFoundError(f"unknown policy pack {pack_id!r}; available: {available}")
    return Pack.from_file(path)


def load_packs(ids: list[str]) -> list[Pack]:
    return [load_pack(i.strip()) for i in ids if i.strip()]


def available() -> list[str]:
    return sorted(p.stem for p in pack_dir().glob("*.yaml"))
