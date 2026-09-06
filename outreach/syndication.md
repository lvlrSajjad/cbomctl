# Syndication

**Always pin the locale when copying.** A bare `pbcopy` through a shell with no
`LANG` set produced 206 mangled characters in the first dev.to paste — every
em-dash and every box-drawing character in the demo block, decoded as Mac Roman.

```bash
LC_ALL=en_US.UTF-8 pbcopy < <file>
```


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

Ready to paste, plain text, no markdown — LinkedIn renders `**bold**` and
`[links](url)` literally:

```bash
LC_ALL=en_US.UTF-8 pbcopy < outreach/linkedin/rsa-2048-and-rsa-3072.txt
```

Pin the locale. A bare copy through a shell with no `LANG` set is how the
dev.to paste arrived with every em-dash and box-drawing character mangled into
Mac Roman.

195 words, two hashtags, link at the end pointing at **your site** rather than
dev.to — the canonical copy is the one to send people to.

### Two choices worth making deliberately

**The link.** LinkedIn has historically down-ranked posts with external links,
and the standard workaround is to put the URL in the first comment instead.
That is real but overstated, and it costs the reader a click plus a hunt. For a
technical audience posting occasionally, in-post is fine. If you would rather
test it: drop the last two lines before posting, then add
`Full piece: <url>` as the first comment within a minute.

**The fold.** LinkedIn truncates after roughly two lines behind "…see more", so
the first two carry the whole post:

> Everyone repeating "RSA is deprecated in 2030" is half right. The wrong half
> is the one people are budgeting around.

Do not add a greeting, a "🚨" or an "I'm excited to share" line above it. That
is the fold, and spending it on throat-clearing wastes the post.

### Not a carousel, not a newsletter

Plain text post. The article is 1,500 words and lives on your site; LinkedIn's
job here is the hook and the link.

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
