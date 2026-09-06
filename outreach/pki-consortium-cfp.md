# CfP — PKI Consortium PQC Conference, Amsterdam

> ## ❌ NOT SUBMITTING — decided 2026-09-06
>
> Speakers must attend in person and self-fund travel; remote presentation is
> explicitly not permitted. Travel to the Netherlands is not possible for
> Sadjad in this window, so the proposal is not viable regardless of its
> merits.
>
> **The abstract below is kept**, not because this event might change its
> terms, but because it is the tightest 324-word statement of the project's
> three findings that exists. It is reusable for any remote-friendly venue, and
> it is a good skeleton for a talk, a README rewrite, or a conference that
> streams speakers.

**Verified 2026-09-06 against the live submission form at <https://pkic.org/call>.**

## Two things to decide before submitting

**Speakers must attend in person.** The form's terms, verbatim:

> "I confirm that I will attend the conference in person and acknowledge that
> **remote presentations are not permitted**."

The *event* is hybrid — plenary and technical tracks are livestreamed and
recorded for attendees — but that does not extend to speakers. And:

> "I acknowledge that I am responsible for all expenses related to travel,
> accommodation, and personal subsistence."

So: Amsterdam, 1–3 December 2026, self-funded, in person or not at all.

**The CFP is still open.** The May announcement said "submissions are open
through June 30, 2026", but that date has passed and the form is live with no
closure notice, the event page still links "Submit your proposal →", and the
agenda notes that "session titles and confirmed speakers are updated
progressively as the program is finalized". So it is effectively rolling, and:

> "Early submissions have a significantly higher chance of selection." … "When
> two proposals are substantially similar, prioritization will go to the one
> submitted first."

Translation: you can submit today, and today is better than next week.

## The constraint that shaped this abstract

> "No commercial or promotional talks. Product demos, hidden marketing
> messages, and self-promotional statements are not allowed."
> "Experience-led content. Prioritize real implementation experience over
> theory-only content."

The earlier draft opened with "This talk presents a deterministic, fully cited
policy engine…", which is a product pitch however open-source the product is.
Rewritten below to lead with the findings and treat the tool as the method —
which is also the honest shape, since the findings came from reading the
documents, not from writing the code.

- **Proposed title:** *Everyone agrees on the risk. They disagree on the price:
  what reading seven national PQC policies actually turned up*
- **Format:** presentation, or lightning talk if they prefer
- **Length:** ~330 words

---

## Abstract

I set out to encode seven national post-quantum policies into machine-readable
rules — BSI, ANSSI, ASD, CNSA 2.0, EO 14412, NIST IR 8547 and the EU roadmap —
and read all seven primary documents to do it. Most of what I thought I knew
going in came from secondary summaries, and a useful amount of it was wrong.

Three findings worth an audience.

**The authorities are not disagreeing about cryptography.** The received story
is that Europe favours hybrid key establishment and the anglophone agencies do
not. But ASD's ISM grants the European premise in the same paragraph where it
declines to follow it — hybrids do hedge against an implementation flaw or a
new attack — and then prices complexity and overhead higher. The NSA states the
cost side as an empirical claim: more products fail from implementation and
configuration errors than from failures in the underlying algorithms. It is a
bet on which failure mode is likelier, and Rainbow and SIKE are evidence for
one side while every TLS CVE is evidence for the other.

**"Deprecated" is not "disallowed", and the dates are not what people quote.**
NIST IR 8547 scopes its 2030 deprecation to 112 bits of security strength, not
to an algorithm — so RSA-2048 is deprecated after 2030 and RSA-3072 is not.
Also, it remains an initial public draft.

**Guidance is mostly not mandate, and tooling flattens that.** BSI TR-02102-1
recommends. ANSSI's "mandatory hybridation" binds only inside its security-visa
process. The EU roadmap is a Recommendation. Reporting any of those as a
failing control misinforms the person acting on it.

I will show what the documents say, where two of them cannot both be satisfied
by one configuration, and where the encoding required a judgement call I had to
write down rather than resolve. The engine and the cited rule sets are open
source and separable; the talk is about what the sources say, not about the
tool.
