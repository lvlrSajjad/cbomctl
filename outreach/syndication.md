# Syndication

The canonical copy of every article is on the docs site. Syndicated copies must
set a canonical URL back to it — these cite a **draft** standard, and when NIST
IR 8547 finalises the dates may move. Only one copy can be corrected; make sure
search engines and readers land on that one.

## dev.to

**The current dev.to editor has no markdown/frontmatter mode.** Title, tags and
canonical URL are separate fields; the body box takes plain markdown. A
frontmatter block pasted into the body renders as literal text.

(An older v1 editor with frontmatter still exists behind
Settings → Customization → Editor Version. Not worth switching — the fields
work fine.)

Two generated files, so nothing is hand-converted:

```bash
python3 scripts/gen_syndication.py
cat outreach/devto/rsa-2048-and-rsa-3072.fields.md    # what to type in the fields
cat outreach/devto/rsa-2048-and-rsa-3072.body.md | pbcopy   # what goes in the body
```

### Steps

1. <https://dev.to/new>
2. **Post Title** — from the fields file.
3. **Add up to 4 tags…** — `security cryptography postquantum compliance`.
4. **Post Content** — paste `…body.md` whole. It has no frontmatter and no H1,
   because the title field supplies the heading and a second one would
   duplicate it.
5. **Advanced Post options** (button under the editor) → the field with
   placeholder `https://yoursite.com/post-title` → paste the canonical URL →
   **Done**.
6. **Save** (not Publish) → **Preview**.
7. In preview, check three things: the title appears once, the terminal code
   block keeps its column alignment, and the tables render. If a table looks
   broken, dev.to wants a blank line before it.
8. **Publish**.

### Afterwards

View source on the published dev.to page and confirm:

```html
<link rel="canonical" href="https://lvlrsajjad.github.io/cbomctl/writing/rsa-2048-and-rsa-3072/">
```

If that is missing, the canonical field did not save — reopen Advanced Post
options and check.

## LinkedIn

Post the hook, not the article. ~150 words, link at the end.

> Everyone repeating "RSA is deprecated in 2030" is half right, and the wrong
> half is the one people are planning around.
>
> NIST IR 8547 scopes that 2030 date to **112 bits of security strength**, not
> to an algorithm. RSA-2048 is deprecated after 2030. RSA-3072 is not — it is
> only disallowed after 2035, and there is no 2030 row for it at all. Same table.
> P-224 and P-256 split the same way.
>
> Two other things worth knowing: "deprecated" and "disallowed" are different
> states in NIST's own glossary — one is a risk acceptance, the other is a stop —
> and IR 8547 is still an initial public draft, so every date in it is proposed.
>
> If you are budgeting a migration, that distinction is worth five years of
> schedule on part of your estate.
>
> Full piece, with the tables and the glossary text:
> https://lvlrsajjad.github.io/cbomctl/writing/rsa-2048-and-rsa-3072/

No hashtag spam. Two at most, if any.

## Where not to post this one

- **Hacker News** — save it for the Show HN with article 1. Two submissions from
  one domain in a week reads as marketing, and Show HN is effectively one shot.
- **Medium** — paywall friction, worse canonical handling than dev.to.

## Higher-risk, higher-value: the lists

The people who care most about this article are on the **NIST pqc-forum**
Google Group and the **IETF PQUIP** list. That is where IR 8547 is actually
discussed.

Do not post the article there. Ask the question and link the article as
context:

> IR 8547 ipd Tables 2 and 4 scope the 2030 deprecation to 112-bit security
> strength, leaving ≥128-bit with only the 2035 disallowance. Is that reading
> right — RSA-3072 and P-256 have no 2030 row? Most secondary summaries I can
> find say "RSA deprecated 2030" without the qualifier.

If the reading is wrong you learn it from the people who wrote the draft, which
is worth considerably more than the traffic. If it is right, you have a citable
confirmation.

**CycloneDX Slack** is lower-risk and directly relevant, especially alongside
the Tool Center submission.
