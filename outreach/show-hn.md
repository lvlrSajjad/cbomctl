# Show HN draft

**Do not post.** For Sadjad to post from his own account, after the repository
is public and `pip install cbomctl` works.

---

## Title

`Show HN: Cbomctl – run one CBOM against several national post-quantum policies`

Alternatives, if that reads flat:

- `Show HN: Cbomctl – where national post-quantum rules contradict each other`
- `Show HN: Cbomctl – a policy engine for Cryptographic Bills of Materials`

HN lowercases after the first word in tool names; `Cbomctl` is what their
title-caser produces, so writing it that way avoids an edit.

---

## First comment (186 words)

I got interested in this after noticing that BSI, ANSSI and the EU roadmap all
recommend hybrid post-quantum key exchange, Australia's ASD recommends against
it, and the NSA doesn't permit it on national security systems outside named
exceptions. If you ship into more than one of those, that's not four
checkboxes — for one construction it's unsatisfiable.

cbomctl reads a CycloneDX CBOM you already have and evaluates it against seven
policies at once, reporting a per-asset matrix and the collisions, with the
target that satisfies everyone or a statement that none does.

What it doesn't do: scan source code (bring a CBOM from CBOMkit or similar),
diff SBOMs (sbom-tools does that), or guess. In CBOMkit's published Keycloak
CBOM, 8 of 22 algorithm components don't say what the key is for, and those come
back unresolved rather than scored.

Every rule cites the document, section or page, and the date I read it. Where a
source is a draft it says draft; where it's ambiguous I recorded the ambiguity
instead of picking.

Feedback I'd most like: whether the `binding` classifications are right, and
whether the NSA hybrid reading is defensible — details in docs/policy-sources.md.

---

## Notes on the framing

**No marketing language.** No "revolutionary", no "the first tool that", no
adjectives about the problem. HN's tolerance for this in a Show HN is near zero
and the audience will find the prior art in about ninety seconds.

**Lead with the concrete disagreement, not the tool.** The hook is that four
authorities give incompatible advice on one construction. That is interesting on
its own; the tool is what you did about it.

**State the limits before anyone asks.** Naming CBOMkit and sbom-tools as things
you don't compete with buys more credibility than a feature list, and it is
true.

**The unresolved statistic is the strongest single line.** "8 of 22 components
don't say what the key is for" is specific, checkable, and signals that the tool
refuses to fabricate. It also pre-empts the obvious "how do you know what
anything is for" question.

**The feedback ask is real, not a formality.** The NSA hybrid reading is a
genuine judgement call — the FAQ answers the question twice with different force
and one answer is scoped to a period that arguably ended. Asking about it invites
the exact expertise that reads Show HN.

## Before posting

- [ ] Repository public, `pip install cbomctl` works from PyPI
- [ ] Docs site live, so `docs/policy-sources.md` resolves
- [ ] Article 2 published — it is the piece that survives scrutiny best and is
      the natural follow-on link
- [ ] Be available for the first few hours; unanswered Show HN threads die
- [ ] Expect and welcome: "isn't this what open-quantum-secure does?" The honest
      answer is in the README's Related tools section — they run multiple
      frameworks too, they emit one report per framework rather than computing
      the collision, and they scan rather than read someone else's CBOM
