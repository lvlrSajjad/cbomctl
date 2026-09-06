#!/usr/bin/env python3
"""Generate one documentation page per policy pack, from the packs themselves.

Hand-written pack pages drift from the YAML the moment a rule changes, and a
drifted citation is worse than no page. These are generated and CI fails if
they are stale.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cbomctl.models import RuleStatus  # noqa: E402
from cbomctl.policy.schema import available, load_pack  # noqa: E402

OUT = ROOT / "docs" / "policy-packs"

BADGE = {True: "✅ **Verified**", False: "⚠️ **Unverified**"}


def rule_block(rule) -> list[str]:
    verified = rule.status is RuleStatus.VERIFIED
    mark = "✅" if verified else "⚠️"
    out = [f"### {mark} `{rule.id}`", ""]
    out.append(rule.description.strip())
    out.append("")

    facts = [f"**Binding:** `{rule.binding.value}`",
             f"**Verdict:** `{rule.effective_verdict.value}`"]
    if rule.hybrid:
        facts.append(f"**Hybrid:** `{rule.hybrid.value}`")
    if rule.interpretation.value == "contested":
        facts.append("**Interpretation:** ⚖ `contested`")
    if rule.rationale:
        facts.append(f"**Rationale:** `{rule.rationale.value}`")
    if rule.deadline:
        state = f" ({rule.deadline_state.value})" if rule.deadline_state else ""
        facts.append(f"**Deadline:** {rule.deadline.isoformat()}{state}")
    out.append(" · ".join(facts))
    out.append("")

    if rule.rationale_note:
        out += ["> " + line for line in rule.rationale_note.strip().split("\n")]
        out.append("")

    if rule.migration_target:
        mt = rule.migration_target
        parts = [f"`{v}`" for v in (mt.kem, mt.signature, mt.symmetric, mt.hash) if v]
        if mt.construction:
            parts.append(f"as `{mt.construction.value}`")
        if parts:
            out += [f"**Migration target:** {' · '.join(parts)}", ""]

    src = f"[{rule.source_title}]({rule.source_url})"
    if rule.source_edition:
        src += f" — {rule.source_edition}"
    out.append(f"**Source:** {src}")
    if verified:
        out.append(f"**Verified:** {rule.last_verified.isoformat()}"
                   + (f" by {rule.verified_by}" if rule.verified_by else ""))
    if rule.is_draft:
        out.append("")
        out.append("!!! warning \"Draft source\"")
        out.append("    This rule cites a document that is still a draft. Its "
                   "dates are proposed and may move.")
    if rule.interpretation.value == "contested":
        alt = rule.alt_reading.value if rule.alt_reading else "unspecified"
        out.append("")
        out.append(f"!!! warning \"Contested encoding — alternative reading: `{alt}`\"")
        out.append("    The quote above is exact; encoding it this way is a "
                   "judgement, and it changes what the conflict output says.")
        for para in (rule.interpretation_note or "").strip().split("\n\n"):
            out.append("")
            for line in para.strip().split("\n"):
                out.append(f"    {line.strip()}")
    if rule.open_question:
        out.append("")
        out.append("!!! question \"Open question\"")
        for line in rule.open_question.strip().split("\n"):
            out.append(f"    {line.strip()}")
    out.append("")
    return out


def page(pack) -> str:
    verified = pack.is_verified
    out = [f"# {pack.name}", ""]
    out.append(f"`{pack.id}` · pack version {pack.pack_version} · "
               f"{BADGE[verified]}")
    out.append("")

    if not verified:
        n = len(pack.unverified_rules)
        out += ["!!! danger \"Not for compliance use\"",
                f"    {n} of {len(pack.rules)} rules in this pack have not been "
                f"read from a primary source. `cbomctl` prints a banner when "
                f"this pack is used, and `--require-verified-policy` refuses to "
                f"run against it.", ""]

    out += ["## Who this binds", "", pack.applicability.strip(), ""]
    if pack.notes:
        out += ["## Notes", "", pack.notes.strip(), ""]
    out += ["## Rules", ""]
    for rule in pack.rules:
        out += rule_block(rule)
    out += ["---", "",
            "Sourcing, open questions and the verification log for this pack are "
            "in [Policy sources](../policy-sources.md).", ""]
    return "\n".join(out)


def index() -> str:
    rows = []
    for pid in available():
        p = load_pack(pid)
        n_ok = len(p.rules) - len(p.unverified_rules)
        rows.append(f"| [{p.name}]({p.id}.md) | `{p.id}` | {p.jurisdiction} | "
                    f"{n_ok}/{len(p.rules)} | {'✅' if p.is_verified else '⚠️'} |")
    return "\n".join([
        "# Policy packs", "",
        "Each pack is a rule set describing what one authority says about "
        "post-quantum cryptography: which algorithms, which constructions, by "
        "when, and **with what force**.", "",
        "The packs are a [standalone versioned artifact](https://github.com/"
        "lvlrSajjad/cbomctl/tree/main/policy-packs) with their own schema and "
        "changelog. Nothing in them depends on `cbomctl` — if you want to build "
        "something else on them, take them.", "",
        "| pack | id | jurisdiction | verified rules | |",
        "|---|---|---|---|---|", *rows, "",
        "## Why `binding` matters", "",
        "Most post-quantum guidance is **not a mandate**, and reporting a "
        "technical guideline as a legal requirement is the most common error in "
        "this space. BSI TR-02102-1 *recommends*. ANSSI's \"mandatory "
        "hybridation\" applies only inside its security-visa process. The EU "
        "roadmap is a Recommendation, non-binding on operators under TFEU "
        "Art. 288.", "",
        "So every rule carries a `binding` value, and it — not severity — "
        "decides `FAIL` versus `WARN`. A `guideline_recommendation` cannot "
        "produce `FAIL`, and that is enforced in code rather than left to "
        "authoring discipline.", "",
        "## The hybrid gradient", "",
        "`hybrid` is scoped **per purpose**, because authorities differ between "
        "key establishment and signatures. It is also not a binary:", "",
        "| stance | meaning | consequence |",
        "|---|---|---|",
        "| `recommended` | encouraged | BSI, ANSSI, EU roadmap |",
        "| `not_recommended` | discouraged, still permitted | ASD — a "
        "satisfies-all target still exists, at a cost |",
        "| `not_permitted_except_interop` | not permitted outside named "
        "exceptions | NSA — **no** single construction satisfies "
        "everyone |", "",
        "That middle step is what makes compromise possible and the third is "
        "what removes it. A tool reporting only PASS/FAIL cannot express the "
        "difference.", "",
    ])


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    written = {}
    for pid in available():
        written[OUT / f"{pid}.md"] = page(load_pack(pid))
    written[OUT / "index.md"] = index()

    check = "--check" in sys.argv
    stale = []
    for path, content in written.items():
        if check:
            if not path.is_file() or path.read_text() != content:
                stale.append(path.name)
        else:
            path.write_text(content)
    if check and stale:
        print("stale pack docs (run scripts/gen_pack_docs.py):", ", ".join(stale))
        return 1
    print(f"{'checked' if check else 'wrote'} {len(written)} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
