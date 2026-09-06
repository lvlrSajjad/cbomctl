# Syndication

The canonical copy of every article is on the docs site. Syndicated copies must
set a canonical URL back to it — these cite a **draft** standard, and when NIST
IR 8547 finalises the dates may move. Only one copy can be corrected; make sure
search engines and readers land on that one.

## dev.to

Paste the article body. In the dev.to editor's frontmatter:

```yaml
---
title: RSA-2048 and RSA-3072 have different futures
published: true
canonical_url: https://lvlrsajjad.github.io/cbomctl/writing/rsa-2048-and-rsa-3072/
tags: security, cryptography, postquantum, compliance
---
```

`canonical_url` is the load-bearing line. Without it dev.to outranks your own
site for your own writing, and readers land on the copy you will forget to fix.

Drop the MkDocs `!!! info` admonition — it will not render there. Replace it
with a plain blockquote:

> Published 2026-09-06. This describes NIST IR 8547 **ipd** — the initial public
> draft of November 2024 — as it stood on that date. Its dates are proposed. If
> a final IR 8547 has published since, check it.

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
