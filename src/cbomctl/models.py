"""Core value types.

The distinctions this module draws are the ones the tool exists to preserve:
`UNKNOWN` versus `AMBIGUOUS` purpose, `WARN` versus `FAIL` by binding force,
and urgency versus assurance as separate axes. Collapsing any of them produces
output that looks more decisive and means less.
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field


class Purpose(StrEnum):
    KEY_AGREEMENT = "key-agreement"
    ENCRYPTION = "encryption"
    SIGNATURE = "signature"
    HASH = "hash"
    MAC = "mac"
    KDF = "kdf"
    RNG = "rng"
    #: A signal exists but cannot separate two purposes with materially
    #: different risk (``primitive: pke`` is the canonical case).
    AMBIGUOUS = "ambiguous"
    #: The generator recorded no purpose signal at all.
    UNKNOWN = "unknown"

    @property
    def is_harvestable(self) -> bool:
        """Whether recorded traffic becomes readable once a CRQC exists.

        Signatures are not harvestable: forging one requires the quantum
        computer to exist at the moment of forgery. This is the whole basis of
        the urgency asymmetry.
        """
        return self in (Purpose.KEY_AGREEMENT, Purpose.ENCRYPTION)

    @property
    def is_resolved(self) -> bool:
        return self not in (Purpose.AMBIGUOUS, Purpose.UNKNOWN)


class Construction(StrEnum):
    CLASSICAL = "classical"
    PURE_PQC = "pure-pqc"
    HYBRID = "hybrid"
    UNKNOWN = "unknown"


class QuantumStatus(StrEnum):
    BROKEN_BY_SHOR = "broken-by-shor"
    WEAKENED_BY_GROVER = "weakened-by-grover"
    PQ_SECURE = "pq-secure"
    NOT_APPLICABLE = "not-applicable"
    UNKNOWN = "unknown"


class Signal(StrEnum):
    """Which CBOM field decided the purpose. Always recorded, always reported."""

    CRYPTO_FUNCTIONS = "cryptoFunctions"
    PRIMITIVE = "primitive"
    OID = "oid"
    NAME = "name"
    CONFIG = "config"
    NONE = "none"


class Verdict(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    INFO = "INFO"
    INDETERMINATE = "INDET"
    NOT_APPLICABLE = "N/A"

    #: Worst-first, for picking a cell's verdict when several rules match.
    @property
    def rank(self) -> int:
        return {"FAIL": 5, "INDET": 4, "WARN": 3, "INFO": 2,
                "PASS": 1, "N/A": 0}[self.value]

    @classmethod
    def parse(cls, value: str) -> "Verdict":
        """Packs are authored in lowercase; accept both spellings."""
        key = str(value).strip().lower()
        return {
            "pass": cls.PASS, "fail": cls.FAIL, "warn": cls.WARN,
            "info": cls.INFO, "indeterminate": cls.INDETERMINATE,
            "indet": cls.INDETERMINATE, "n/a": cls.NOT_APPLICABLE,
            "not_applicable": cls.NOT_APPLICABLE,
        }[key]


class Binding(StrEnum):
    """Force of a rule. Decides FAIL versus WARN — severity does not."""

    STATUTE = "statute"
    EXECUTIVE_ORDER = "executive_order"
    AGENCY_REQUIREMENT = "agency_requirement"
    CERTIFICATION_REQUIREMENT = "certification_requirement"
    GUIDELINE_RECOMMENDATION = "guideline_recommendation"

    @property
    def is_mandatory(self) -> bool:
        return self in (
            Binding.STATUTE,
            Binding.EXECUTIVE_ORDER,
            Binding.AGENCY_REQUIREMENT,
        )


class HybridStance(StrEnum):
    """Stance on hybrid constructions, for the purposes a rule is scoped to.

    A three-step gradient, not a binary. `NOT_RECOMMENDED` is discouraged but
    permitted, so a satisfies-all target can still exist at a documented cost.
    `NOT_PERMITTED_EXCEPT_INTEROP` is not permitted at all outside named
    exceptions, which means no construction can satisfy it *and* a pack that
    recommends hybrids — the honest output there is that no single
    configuration works.
    """

    REQUIRED = "required"
    RECOMMENDED = "recommended"
    NOT_RECOMMENDED = "not_recommended"
    NOT_PERMITTED_EXCEPT_INTEROP = "not_permitted_except_interop"
    SILENT = "silent"

    @property
    def favours_hybrid(self) -> bool:
        return self in (HybridStance.REQUIRED, HybridStance.RECOMMENDED)

    @property
    def opposes_hybrid(self) -> bool:
        return self in (HybridStance.NOT_RECOMMENDED,
                        HybridStance.NOT_PERMITTED_EXCEPT_INTEROP)

    @property
    def permits_hybrid(self) -> bool:
        """Whether a hybrid remains an option at all, however discouraged."""
        return self is not HybridStance.NOT_PERMITTED_EXCEPT_INTEROP


class Rationale(StrEnum):
    """Why an authority takes a stance. Orthogonal to urgency.

    ``HARVEST_NOW_DECRYPT_LATER`` drives *when* to move and cannot apply to
    signatures. ``ALGORITHM_MATURITY`` drives *what* to move to and applies to
    every purpose — Rainbow and SIKE both fell to classical attacks during the
    NIST competition, and that risk does not shrink as the CRQC date nears.
    """

    HNDL = "harvest_now_decrypt_later"
    ALGORITHM_MATURITY = "algorithm_maturity"
    KEY_LENGTH = "key_length"
    POLICY_ALIGNMENT = "policy_alignment"
    UNSTATED = "unstated"


class RuleStatus(StrEnum):
    VERIFIED = "verified"
    NEEDS_VERIFICATION = "needs_verification"


class DeadlineState(StrEnum):
    """`deprecated` and `disallowed` are different states and never collapse."""

    DEPRECATED = "deprecated"
    DISALLOWED = "disallowed"
    EXCLUSIVE_USE = "exclusive_use"
    ACQUISITION_GATE = "acquisition_gate"
    TRANSITION_START = "transition_start"
    COMPLETE = "complete"


class Location(BaseModel):
    file: str | None = None
    line: int | None = None
    context: str | None = None


class PurposeConflict(BaseModel):
    """Two signals disagreed. Kept rather than discarded."""

    signal: Signal
    suggested: Purpose
    note: str


class CryptoAsset(BaseModel):
    bom_ref: str
    raw_name: str
    algorithm: str | None = None
    purpose: Purpose = Purpose.UNKNOWN
    purpose_signal: Signal = Signal.NONE
    purpose_conflicts: list[PurposeConflict] = Field(default_factory=list)
    construction: Construction = Construction.UNKNOWN
    quantum_status: QuantumStatus = QuantumStatus.UNKNOWN
    key_size: int | None = None
    #: Classical security strength in bits. NIST IR 8547 scopes its 2030
    #: deprecation to 112-bit, so RSA-2048 and RSA-3072 differ here.
    security_strength: int | None = None
    parameter_set: str | None = None
    curve: str | None = None
    oid: str | None = None
    asset_type: str = "algorithm"
    locations: list[Location] = Field(default_factory=list)
    #: Evidence that supports the purpose but is never allowed to decide it.
    corroborating: list[str] = Field(default_factory=list)
    spec_version: str | None = None

    @property
    def display(self) -> str:
        """What the generator called it.

        Deliberately not the canonical algorithm name. Canonicalisation exists
        for policy matching and it *loses* the parameter: `RSA-2048` and
        `RSA-3072` both canonicalise to `RSA`, and `ECDSA-P224` and
        `ECDSA-P256` both resolve through their shared OID to `ECDSA-SHA256`.
        Those pairs have different transition dates under NIST IR 8547, so a
        report that displays them identically hides the finding.

        The raw name is also what the reader will recognise from their own
        codebase. Fall back to the canonical name only when there is no name.
        """
        return self.raw_name or self.algorithm or "<unnamed>"


class Risk(BaseModel):
    band: str
    exposure_years: float
    x_years: float
    y_years: float
    z_years: float
    rationale: str
    x_source: str


class Unscored(BaseModel):
    bom_ref: str
    display: str
    reason: str
    signal: str | None = None
    missing: list[str] = Field(default_factory=list)
    would_resolve: str
    range_if_guessed: dict[str, str] = Field(default_factory=dict)


class RuleRef(BaseModel):
    rule_id: str
    jurisdiction: str
    binding: Binding
    status: RuleStatus
    source_url: str
    source_title: str
    is_draft: bool = False
    deadline: date | None = None
    deadline_state: DeadlineState | None = None
    hybrid: HybridStance | None = None
    rationale: Rationale | None = None
    description: str = ""


class Cell(BaseModel):
    """One asset × one jurisdiction."""

    verdict: Verdict
    rules: list[RuleRef] = Field(default_factory=list)
    note: str | None = None

    @property
    def governing_deadline(self) -> date | None:
        ds = [r.deadline for r in self.rules if r.deadline]
        return min(ds) if ds else None


class Conflict(BaseModel):
    id: str
    kind: str  # construction | parameter | deadline | scope
    bom_ref: str
    display: str
    summary: str
    jurisdictions: list[str]
    satisfies_all: str | None = None
    cost_note: str | None = None
