"""CLI. Subcommands only — no logic lives here."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Annotated

import typer

from cbomctl.config import Config
from cbomctl.loader import CbomParseError, read_assets
from cbomctl.models import Interpretation, RuleStatus
from cbomctl.policy.schema import available, load_pack, load_packs
from cbomctl.report import json_out, markdown, matrix_text, sarif
from cbomctl.scoring import mosca
from cbomctl.verdict.conflicts import detect
from cbomctl.verdict.matrix import build

app = typer.Typer(
    add_completion=False,
    help=("Evaluate a CycloneDX CBOM against several national post-quantum "
          "policies at once and report where their verdicts contradict."),
    no_args_is_help=True,
)

DEFAULT_JURISDICTIONS = "bsi-de,anssi-fr,asd-au,cnsa-2.0"


def _fail(msg: str) -> None:
    typer.secho(f"error: {msg}", fg=typer.colors.RED, err=True)
    raise typer.Exit(2)


@app.command()
def verdict(
    cbom: Annotated[str, typer.Argument(help="CBOM JSON path, or - for stdin.")],
    jurisdictions: Annotated[str, typer.Option("--jurisdictions", "-j")] = DEFAULT_JURISDICTIONS,
    config: Annotated[Path | None, typer.Option("--config", "-c")] = None,
    fmt: Annotated[str, typer.Option("--format", "-f", help="matrix|json|md|sarif")] = "matrix",
    source_format: Annotated[str, typer.Option("--from", help="auto|cyclonedx|sbom-tools")] = "auto",
    crqc_year: Annotated[int, typer.Option("--crqc-year")] = mosca.DEFAULT_CRQC_YEAR,
    migration_years: Annotated[float | None, typer.Option("--migration-years")] = None,
    strict: Annotated[bool, typer.Option("--strict", help=(
        "Unverified rules return INDETERMINATE rather than asserting a verdict, "
        "and indeterminate findings exit 3."))] = False,
    require_verified: Annotated[bool, typer.Option("--require-verified-policy", help=(
        "Refuse to run against any pack containing an unverified rule."))] = False,
    fail_on_warn: Annotated[bool, typer.Option("--fail-on-warn")] = False,
    cnsa_acquisition_gate: Annotated[bool, typer.Option("--cnsa-acquisition-gate", help=(
        "Include the CNSA 2.0 January 2027 acquisition gate. It is a "
        "procurement condition on new NSS acquisitions, not an algorithm "
        "deadline, so it is off by default."))] = False,
) -> None:
    """Per-asset × jurisdiction verdicts, plus the conflicts between them."""
    try:
        assets, detected = read_assets(cbom, source_format)
    except CbomParseError as exc:
        _fail(str(exc))
    if not assets:
        _fail("no cryptographic assets found — is this a CBOM?")

    try:
        packs = load_packs(jurisdictions.split(","))
    except FileNotFoundError as exc:
        _fail(str(exc))

    if require_verified:
        offenders = {p.id: [r.id for r in p.unverified_rules]
                     for p in packs if not p.is_verified}
        if offenders:
            detail = "; ".join(f"{k} ({len(v)} rules)" for k, v in offenders.items())
            _fail(f"--require-verified-policy given, but these packs contain "
                  f"unverified rules: {detail}. See docs/policy-sources.md.")

    try:
        cfg = Config.load(config)
    except FileNotFoundError as exc:
        _fail(str(exc))

    matrix = build(
        assets, packs, cfg,
        crqc_year=crqc_year, migration_years=migration_years,
        include_acquisition_gate=cnsa_acquisition_gate, strict=strict,
    )
    conflicts = detect(matrix, packs)

    renderer = {"matrix": matrix_text, "json": json_out,
                "md": markdown, "markdown": markdown, "sarif": sarif}.get(fmt)
    if renderer is None:
        _fail(f"unknown format {fmt!r}; use matrix, json, md or sarif")
    typer.echo(renderer.render(matrix, conflicts))

    code = matrix.exit_code
    if fail_on_warn and code == 0:
        from cbomctl.models import Verdict
        if any(r.worst is Verdict.WARN for r in matrix.rows):
            code = 1
    raise typer.Exit(code)


@app.command()
def prioritize(
    cbom: Annotated[str, typer.Argument(help="CBOM JSON path, or - for stdin.")],
    config: Annotated[Path | None, typer.Option("--config", "-c")] = None,
    source_format: Annotated[str, typer.Option("--from")] = "auto",
    crqc_year: Annotated[int, typer.Option("--crqc-year")] = mosca.DEFAULT_CRQC_YEAR,
    migration_years: Annotated[float | None, typer.Option("--migration-years")] = None,
) -> None:
    """Rank findings by Mosca's inequality. Answers *when must I move*."""
    try:
        assets, _ = read_assets(cbom, source_format)
        cfg = Config.load(config)
    except (CbomParseError, FileNotFoundError) as exc:
        _fail(str(exc))

    matrix = build(assets, [], cfg, crqc_year=crqc_year, migration_years=migration_years)
    scored = [r for r in matrix.rows if r.risk]
    scored.sort(key=lambda r: -r.risk.exposure_years)

    for i, r in enumerate(scored, 1):
        typer.echo(f"{i:>3}. {r.risk.band.upper():<9} {r.display:<20} {r.purpose:<15} "
                   f"exposure {r.risk.exposure_years:>5}y  ({r.risk.rationale})")
        if r.locations:
            typer.echo(f"     {r.locations[0]}")

    unresolved = [r for r in matrix.rows if r.unscored]
    if unresolved:
        typer.echo(f"\nUNRESOLVED ({len(unresolved)}) — not scored, because the "
                   f"CBOM does not say what they are for:")
        for r in unresolved:
            span = " · ".join(f"{k.replace('_', ' ')} → {v}"
                              for k, v in r.unscored.range_if_guessed.items())
            typer.echo(f"  {r.display:<20} {r.unscored.reason}"
                       + (f"  [{span}]" if span else ""))
            typer.echo(f"     {r.unscored.would_resolve}")

    a = matrix.assumptions
    typer.echo(f"\nAssumptions: CRQC {a['crqc_year']} ({a['crqc_note']}) · "
               f"migration {a['migration_years']}y")


@app.command()
def plan(
    cbom: Annotated[str, typer.Argument(help="CBOM JSON path, or - for stdin.")],
    jurisdictions: Annotated[str, typer.Option("--jurisdictions", "-j")] = DEFAULT_JURISDICTIONS,
    config: Annotated[Path | None, typer.Option("--config", "-c")] = None,
    source_format: Annotated[str, typer.Option("--from")] = "auto",
    crqc_year: Annotated[int, typer.Option("--crqc-year")] = mosca.DEFAULT_CRQC_YEAR,
    strict: Annotated[bool, typer.Option("--strict")] = False,
) -> None:
    """Ordered migration plan: what to fix first, to what, by whose deadline."""
    try:
        assets, _ = read_assets(cbom, source_format)
        packs = load_packs(jurisdictions.split(","))
        cfg = Config.load(config)
    except (CbomParseError, FileNotFoundError) as exc:
        _fail(str(exc))

    from cbomctl import plan as plan_mod

    matrix = build(assets, packs, cfg, crqc_year=crqc_year, strict=strict)
    conflicts = detect(matrix, packs)
    typer.echo(plan_mod.render(matrix, conflicts, packs))
    raise typer.Exit(matrix.exit_code)


@app.command()
def normalize(
    cbom: Annotated[str, typer.Argument(help="CBOM JSON path, or - for stdin.")],
    source_format: Annotated[str, typer.Option("--from")] = "auto",
) -> None:
    """Show purpose resolution and which CBOM field decided it."""
    try:
        assets, detected = read_assets(cbom, source_format)
    except CbomParseError as exc:
        _fail(str(exc))
    typer.echo(f"# read as {detected}, {len(assets)} assets\n")
    typer.echo(f"{'ASSET':<22}{'PURPOSE':<15}{'VIA':<18}{'CONSTRUCTION':<12}QUANTUM")
    for a in assets:
        typer.echo(f"{a.display:<22}{a.purpose.value:<15}{a.purpose_signal.value:<18}"
                   f"{a.construction.value:<12}{a.quantum_status.value}")
        for c in a.purpose_conflicts:
            typer.echo(f"  ! {c.note}")
        for ctx in a.corroborating[:1]:
            typer.echo(f"  ~ corroborating (never decides): {ctx}")


policies = typer.Typer(help="Inspect policy packs.", no_args_is_help=True)
app.add_typer(policies, name="policies")


@policies.command("list")
def policies_list() -> None:
    """List packs and their verification state."""
    for pid in available():
        p = load_pack(pid)
        unverified = len(p.unverified_rules)
        state = "VERIFIED" if not unverified else f"{unverified}/{len(p.rules)} UNVERIFIED"
        typer.echo(f"{p.id:<14} {state:<18} {p.name}")
    typer.echo("\nNo pack is verified. Rules were assembled from secondary "
               "reporting; see docs/policy-sources.md.")


@policies.command("show")
def policies_show(pack_id: str) -> None:
    """Show a pack's rules, sources and open questions."""
    try:
        p = load_pack(pack_id)
    except FileNotFoundError as exc:
        _fail(str(exc))
    typer.echo(f"{p.name}  ({p.id} v{p.pack_version})")
    typer.echo(f"authority: {p.authority}\n")
    typer.echo(f"applicability: {p.applicability.strip()}\n")
    for r in p.rules:
        mark = "✓" if r.status is RuleStatus.VERIFIED else "✗"
        typer.echo(f"  {mark} {r.id}")
        typer.echo(f"      {r.description.strip()}")
        typer.echo(f"      binding={r.binding.value} verdict={r.effective_verdict.value}"
                   + (f" hybrid={r.hybrid.value}" if r.hybrid else "")
                   + (f" rationale={r.rationale.value}" if r.rationale else "")
                   + (f" deadline={r.deadline}" if r.deadline else ""))
        typer.echo(f"      source: {r.source_title} — {r.source_url}")
        if r.interpretation.value == "contested":
            alt = r.alt_reading.value if r.alt_reading else "unspecified"
            typer.secho(f"      ⚖ CONTESTED ENCODING — alternative reading: {alt}",
                        fg=typer.colors.YELLOW)
            for line in (r.interpretation_note or "").strip().split("\n"):
                if line.strip():
                    typer.echo(f"        {line.strip()}")
        if r.open_question:
            typer.echo(f"      OPEN: {r.open_question.strip()}")
        typer.echo("")


def main() -> None:  # pragma: no cover
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
