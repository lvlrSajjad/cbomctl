"""Mosca's inequality: if X + Y > Z, you are already late.

X — how long the data must stay confidential (from the human)
Y — how long migration takes (assumption, default 3 years)
Z — years until a cryptanalytically relevant quantum computer (assumption,
    default 2035 to match the NSM-10 / EU planning horizon; a policy date, not
    a forecast, and stamped into every output that uses it)

The asymmetry this encodes is the point. Key agreement and encryption are
harvestable: an adversary recording ciphertext today reads it the day a CRQC
exists, so the exposure window is already open. Signatures are not — forging
one requires the quantum computer to exist at the moment of forgery — unless
the signed artifact stays trusted for years (firmware, code signing, root CAs),
which is why signatures are scored against verification lifetime instead.

This module answers *when must I move*. It deliberately says nothing about
*what to move to*: that is the assurance axis, it is driven by the maturity of
the target scheme rather than by timing, and it lives in the policy packs.
"""

from __future__ import annotations

from datetime import date

from cbomctl.models import CryptoAsset, Purpose, QuantumStatus, Risk, Unscored

DEFAULT_CRQC_YEAR = 2035
DEFAULT_MIGRATION_YEARS = 3.0


def _band(exposure: float, purpose: Purpose, status: QuantumStatus) -> str:
    if status is QuantumStatus.PQ_SECURE:
        return "none"
    if status is QuantumStatus.WEAKENED_BY_GROVER:
        # Grover is quadratic. SHA-256 keeps ~128-bit quantum security and is
        # not a migration target; AES-128 is weakened, not broken. Reporting
        # these as quantum-critical is inflation.
        return "low"
    if not purpose.is_harvestable:
        # Not harvestable: a positive Mosca gap still matters, but it is a
        # deadline problem rather than a retroactive-exposure one.
        return "medium" if exposure > 0 else "low"
    if exposure > 10:
        return "critical"
    if exposure > 0:
        return "high"
    return "medium"


def score(
    asset: CryptoAsset,
    *,
    lifetime_years: float,
    lifetime_source: str,
    migration_years: float = DEFAULT_MIGRATION_YEARS,
    crqc_year: int = DEFAULT_CRQC_YEAR,
    today: date | None = None,
) -> Risk | Unscored:
    """Score one asset, or explain precisely why it cannot be scored."""
    if not asset.purpose.is_resolved:
        return _unscored(asset)

    now = today or date.today()
    z = float(crqc_year - now.year)
    x = float(lifetime_years)
    y = float(migration_years)
    exposure = (x + y) - z

    if asset.purpose.is_harvestable:
        rationale = "harvest-now-decrypt-later"
    elif asset.purpose is Purpose.SIGNATURE:
        rationale = ("signature — not harvestable; scored against how long it "
                     "stays trusted, not how long data stays secret")
    else:
        rationale = f"{asset.purpose.value} — no harvest exposure"

    return Risk(
        band=_band(exposure, asset.purpose, asset.quantum_status),
        exposure_years=round(exposure, 1),
        x_years=x, y_years=y, z_years=z,
        rationale=rationale,
        x_source=lifetime_source,
    )


def _unscored(asset: CryptoAsset) -> Unscored:
    if asset.purpose is Purpose.AMBIGUOUS:
        reason = "purpose-ambiguous"
        missing = ["cryptoFunctions"]
        resolve = ("Declare the purpose in cbomctl.yaml, or regenerate the CBOM "
                   "with a generator that records cryptoFunctions.")
        # The span between the two readings is the entire severity scale, which
        # is why picking one would be indefensible.
        span = {"as_key_transport": "critical", "as_signature": "medium"}
    else:
        reason = "purpose-unknown"
        missing = [f for f in ("primitive", "cryptoFunctions", "oid")
                   if f != "oid" or not asset.oid]
        resolve = ("The CBOM records no purpose signal for this asset. Declare "
                   "it in cbomctl.yaml, or use a generator that emits "
                   "algorithmProperties.")
        span = {}
    return Unscored(
        bom_ref=asset.bom_ref,
        display=asset.display,
        reason=reason,
        signal=(f"primitive:pke" if asset.purpose is Purpose.AMBIGUOUS
                and asset.purpose_signal.value == "primitive" else asset.purpose_signal.value),
        missing=missing,
        would_resolve=resolve,
        range_if_guessed=span,
    )
