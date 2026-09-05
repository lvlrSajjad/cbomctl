# Policy sources, corrections, and open questions

**No rule in any pack is verified. Every claim below still needs a primary
source read.**

Everything here was assembled from secondary reporting — vendor blogs, law-firm
summaries, consultancy explainers — which is frequently wrong about exactly the
details that matter: whether a date binds a requirement or a recommendation,
which population it binds, and whether the edition being quoted is current.

Accordingly every rule ships `status: needs_verification`. `cbomctl` prints a
banner; `--require-verified-policy` refuses to run. That is the honest default:
better a tool that admits its rules are unconfirmed than one that renders a
confident verdict from a blog post.

## Corrections already applied

An independent review found the earlier drafts overstating guidance as law.
These are fixed in the packs and in every document; they are recorded because
each would have produced a materially misleading verdict.

| # | was | now |
|---|---|---|
| 1 | "BSI **mandates** hybrid" | TR-02102-1 is a technical guideline that **recommends** it → `binding: guideline_recommendation`, `hybrid: recommended`. The word *mandatory* is removed everywhere. |
| 2 | "ANSSI **requires** hybrid" | **Strongly recommends**, and separately requires it for certain ANSSI certifications → two rules, different `binding`. |
| 3 | NIST IR 8547 dates quoted as settled | Still an **initial public draft** (Nov 2024). Dates are *proposed*; `is_draft: true`, and any output citing them prints "draft". |
| 4 | "deprecated" used as a synonym for failure | **Deprecated ≠ disallowed.** Two distinct `deadline_state` values, modelled separately. |
| 5 | (absent) | **EO 14412** added — and it is *not* a blanket federal PQC mandate. |
| 6 | (absent) | `binding` field added to the pack schema, precisely because of 1–3. |

## 1. `us-eo14412` — United States, Executive Order 14412

**Primary sources**
- EO 14412, *"Securing the Nation Against Advanced Cryptographic Attacks"*,
  June 22 2026 —
  <https://www.whitehouse.gov/presidential-actions/2026/06/securing-the-nation-against-advanced-cryptographic-attacks/>
- Federal Register publication, June 25 2026 — **91 FR 38483**.

**What the pack asserts** — `binding: executive_order`

| # | claim | status |
|---|---|---|
| U1 | Scope is federal **High Value Assets and high-impact systems**, **excluding National Security Systems** — *not* blanket federal PQC migration | `needs_verification` |
| U2 | **Key establishment** by **2030-12-31** | `needs_verification` |
| U3 | **Digital signatures** by **2031-12-31** — a separate, later deadline | `needs_verification` |
| U4 | Contractor compliance via a **FAR rule** targeting **2030-12-31** | `needs_verification` |
| U5 | CISA to publish **CBOM minimum-elements guidance within 270 days** (≈ 2027-03-19) | `needs_verification` |
| U6 | Each agency designates a PQC migration lead within 30 days (≈ 2026-07-22) | `needs_verification` |

**Open questions**

1. **U1 is the correction that matters most.** Secondary coverage routinely
   renders this as "the US mandates PQC by 2030". It does not. Confirm the HVA /
   high-impact scoping language and the NSS exclusion verbatim — if we get this
   wrong we will fail assets the order never reached.
2. **U2 vs U3 is the only place a major jurisdiction explicitly splits key
   establishment from signatures with different dates**, which is direct
   evidence for our scoring asymmetry (DESIGN §7). Worth quoting exactly.
3. U4 — a *proposed* FAR rule is not yet a contractual obligation. Confirm
   status; until the rule is final this should be `warn`, not `fail`.
4. U5 matters to us specifically: CISA CBOM minimum elements may define the
   input format we consume. Track it.
5. Confirm 91 FR 38483 and whether the FR text differs from the White House
   posting.

## 2. `cnsa-2.0` — United States, NSA

**Primary sources**
- NSA CNSA 2.0 FAQ (current revision) —
  <https://media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSA_CNSA_2.0_FAQ_.PDF>
  (verify the live URL; NSA rehosts)
- The Sept 2022 CSA and any revision after NIST finalised FIPS 203/204/205.

**What the pack asserts** — `binding: agency_requirement`, **NSS only**

| # | claim | status |
|---|---|---|
| C1 | Applies to **National Security Systems** — not federal IT generally, not the private sector | `needs_verification` |
| C2 | **2027-01-01** acquisition gate for new NSS acquisitions | `needs_verification` |
| C3 | Software/firmware signing and networking equipment: exclusive use by **2030** | `needs_verification` |
| C4 | Browsers, servers, cloud, and operating systems: exclusive use by **2033** | `needs_verification` |
| C5 | "All NSS by **2031** unless excepted" milestone | `needs_verification` |
| C6 | Algorithms: **ML-KEM-1024, ML-DSA-87, AES-256, SHA-384/512, LMS/XMSS** | `needs_verification` |
| C7 | Hybrid **not required**; NSA has stated pure CNSA 2.0 suffices → `hybrid: silent` | `needs_verification` |

**Open questions**

1. **C6's ML-KEM-1024 is a conflict driver.** BSI and ANSSI reportedly accept
   ML-KEM-768; CNSA 2.0 reportedly requires -1024. That is a `parameter`
   conflict distinct from the hybrid one, and it is the second contradiction the
   matrix should surface. Verify the level requirement precisely.
2. **C7 phrasing.** *Not required* and *discouraged* are different pack
   semantics. `silent` is the current encoding; if NSA actively discourages
   hybrids, change it to `not_recommended` — that changes the conflict story.
3. **C5** — how does the 2031 "all NSS unless excepted" milestone interact with
   the 2030/2033 category dates? Possibly a conflation in secondary sources.
4. **C1 scoping.** Run against commercial SaaS, the honest output is "these
   rules do not apply to you". The pack carries an `applicability` banner.
5. **Category list.** `system_category` config enum must match the FAQ's own
   category names. (Design decision already settled: undeclared ⇒ `INDET`; the
   2027 gate is its own flag.)

## 3. `bsi-de` — Germany, BSI

**Primary source**
BSI TR-02102-1, *"Cryptographic Mechanisms: Recommendations and Key Lengths"*,
**version 2026-01 (published 2026-01-23)** —
<https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Publications/TechGuidelines/TG02102/BSI-TR-02102-1.html>

English and German editions are published; the German is normative.

**What the pack asserts** — `binding: guideline_recommendation`,
`hybrid: recommended`

| # | claim | status |
|---|---|---|
| B1 | It **recommends** hybrid key establishment during the transition. **Not a mandate** — TR-02102-1 is a technical guideline, not a statute | `needs_verification` |
| B2 | Sole use of classical key agreement recommended only until **2031-12-31** | `needs_verification` |
| B3 | **Very high protection requirements**: complete by **2030-12-31** | `needs_verification` |
| B4 | Classical **signatures** follow the EU **2035** horizon | `needs_verification` |

**Open questions**

1. **B1 was previously wrong in our drafts** ("mandatory") and is now corrected
   to *recommends*. Verify the verb in the German text. The pack's verdict for a
   non-hybrid deployment is `WARN`, not `FAIL`, and that follows from `binding` —
   if it turns out to bind BSI-approved or government-facing systems more
   strongly, add a second rule with `binding: agency_requirement` scoped to that
   population rather than changing B1.
2. **B2 vs B3** — two deadlines by protection level, or has one superseded the
   other? 2030 and 2031 appearing together smells like a conflation of the
   2025-01 and 2026-01 editions.
3. **Scope** — does TR-02102-1 carry the migration timeline at all, or does it
   live in a separate BSI publication? Do not attribute a deadline to the wrong
   guideline.
4. **B4** — confirm BSI adopts the EU roadmap's date rather than setting its
   own, and cite the roadmap as a second source (see §6 Q3).

## 4. `anssi-fr` — France, ANSSI

**Primary sources**
- ANSSI, *"ANSSI views on the Post-Quantum Cryptography transition"* — 2022
  position paper and 2023 follow-up —
  <https://cyber.gouv.fr/publications/anssi-views-post-quantum-cryptography-transition>
- Any 2026 ANSSI communication on certification (see F1).

**What the pack asserts** — `hybrid: recommended`, with a second rule at
`binding: certification_requirement`

| # | claim | status |
|---|---|---|
| F1 | From **2027**, ANSSI will not certify security products lacking quantum-resistant cryptography → `binding: certification_requirement` | `needs_verification` |
| F2 | Full compliance with PQC standards expected by **2030** | `needs_verification` |
| F3 | **Strongly recommends** hybrid for products protecting information beyond 2030, or deployed without updates past 2030. **Not "required" unqualified** | `needs_verification` |
| F4 | The hybrid recommendation **extends to signatures**, because PQ signature schemes are less battle-tested than PQ key establishment | `needs_verification` |
| F5 | Three-phase transition; phase 3 not before the early 2030s | `needs_verification` |
| F6 | ML-KEM and ML-DSA accepted post FIPS 203/204; explicit preference for **FrodoKEM** at highest assurance | `needs_verification` |

**Open questions**

1. **F4 cuts against our own thesis and is the most important item on this
   page.** Every other jurisdiction puts signatures on a later, looser horizon —
   which is the premise of DESIGN §7 and of the "key exchange is urgent,
   signatures aren't" article. ANSSI reportedly wants hybrid signatures *because
   PQ signatures are immature*, which is a maturity argument, not a
   harvest-now-decrypt-later one, and it points the other way. If confirmed, the
   article needs a paragraph conceding that harvest risk and migration urgency
   come apart here, and `anssi-fr` needs a `hybrid` stance that applies to
   signatures as well as key establishment.
2. **F1's scope.** "Will not certify" binds products seeking ANSSI certification
   (CSPN, Critères Communs) — a far narrower population than French industry.
   The `applicability` banner must say so.
3. **F3 vs BSI's B1.** If both merely recommend, they are not interchangeable
   with a mandate in the conflict narrative, and the launch article cannot say
   "France requires".
4. **F6 FrodoKEM.** If ANSSI genuinely prefers FrodoKEM at high assurance, the
   pack's `migration_target` is jurisdiction-specific and not simply ML-KEM.
   Confirm the assurance threshold.
5. Confirm which paper is current — the 2026 certification news suggests
   movement the published papers may not reflect.

## 5. `asd-au` — Australia, ASD / ACSC

**Primary sources**
- ASD *Information Security Manual*, Guidelines for Cryptography (current
  monthly release) — <https://www.cyber.gov.au/resources-business-and-government/essential-cybersecurity/ism>
- ACSC, *Planning for post-quantum cryptography* —
  <https://www.cyber.gov.au/business-government/secure-design/quantum/planning-for-post-quantum-cryptography>

The ISM is revised roughly monthly, so a rule citing it must record the
**release month**. This pack goes stale faster than the others.

**What the pack asserts** — `hybrid: not_recommended`

| # | claim | status |
|---|---|---|
| A1 | Cease traditional asymmetric cryptography (RSA, DH, ECDH, ECDSA) by **end of 2030** | `needs_verification` |
| A2 | Hybrid schemes **"not recommended"** — discouraged, **not prohibited** | `needs_verification` |
| A3 | **ML-KEM-1024** and **ML-DSA-87**; ML-KEM-768 acceptable only until **2030** | `needs_verification` |
| A4 | Staged: plan by end 2026, commenced by end 2028, complete by end 2030 | `needs_verification` |

The review confirmed this pack as designed. Still unverified against the ISM
itself.

**Open questions**

1. **A2 is half the flagship conflict.** Get the literal sentence. "Not
   recommended but not prohibited" is what makes the verdict `WARN` rather than
   `FAIL`, and a satisfies-all target possible at a documented cost.
2. **A1** — exact ISM control number and whether the algorithm list is
   exhaustive (Ed25519? X25519? finite-field DH separately?).
3. **A3's ML-KEM-768 sunset** interacts with CNSA's -1024 requirement and BSI's
   reported -768 acceptance. Three positions on one parameter.
4. **Applicability** — Australian government entities and suppliers, or general
   guidance? Determines the banner and arguably the `binding` value.
5. Record the ISM release month; open a recurring re-verification issue.

## 6. `eu-roadmap` — European Union, NIS Cooperation Group

**Primary sources**
- NIS Cooperation Group, *"A Coordinated Implementation Roadmap for the
  Transition to Post-Quantum Cryptography"* (**June 23 2025**) —
  <https://digital-strategy.ec.europa.eu/en/library/coordinated-implementation-roadmap-transition-post-quantum-cryptography>
- Commission Recommendation (EU) 2024/1101, 11 April 2024 —
  <https://eur-lex.europa.eu/eli/reco/2024/1101/oj>

**What the pack asserts** — `binding: guideline_recommendation`

| # | claim | status |
|---|---|---|
| E1 | National strategies and pilots by **end 2026** | `needs_verification` |
| E2 | **High-risk use cases** by **end 2030** | `needs_verification` |
| E3 | Medium/low risk "as far as feasible" by **2035** | `needs_verification` |
| E4 | A **Recommendation**, not a Regulation — not directly binding on operators | `needs_verification` |

The review confirmed this pack as designed.

**Open questions**

1. **E4 decides whether this pack can ever emit `FAIL`.** A Commission
   Recommendation is non-binding by definition (TFEU Art. 288). If that holds,
   every rule caps at `WARN`. Check separately whether **NIS2 or DORA** pull any
   of these dates into binding obligations for in-scope entities — that would
   justify a second pack, not a change to this one.
2. **E2's "high-risk use cases" is not CBOM-derivable**, exactly like the CNSA
   category problem. Same resolution: declared in config, `INDET` when absent.
   Confirm the roadmap's own sector list so the config enum matches.
3. **Double-citation risk.** Both `bsi-de` (B4) and `anssi-fr` reportedly follow
   "the European roadmap" for signature timing. If BSI's 2035 date simply *is*
   E3, cite the roadmap from both packs rather than duplicating a date that
   could silently drift apart in our YAML.

## 7. Cross-cutting

**NIST IR 8547 — draft, and two distinct states.** Still an *initial public
draft* (Nov 2024). Its 2030 **deprecated** / 2035 **disallowed** dates for RSA,
ECDSA, ECDH, DSA and FFDH at 112-bit and ≥128-bit security levels are
**proposed**. Encoded `binding: guideline_recommendation`, `is_draft: true`, and
any output citing them prints "draft". *Deprecated* and *disallowed* are
modelled as separate `deadline_state` values — an algorithm may be deprecated
(discouraged, still permitted) years before it is disallowed, and collapsing
them into one failure is the most commonly misstated point in this space.

**NIST SP 800-227 (final, September 2025)** is the citation for hybrid and
multi-algorithm KEM constructions. Cite it wherever a pack's
`migration_target.construction` is `hybrid`.

**HQC** was selected in March 2025 but **is not yet a final FIPS**. It must not
appear as a migration target in any pack until it is. BSI reportedly approves
FrodoKEM and Classic McEliece alongside the NIST set — jurisdiction-specific
algorithm acceptance is real and the packs must not assume the NIST list is
universal.

**The CRQC year (Z).** Default 2035, matching the NSM-10 / EU horizon. A policy
planning date, not a forecast; stated wherever used and stamped into output.
Confirm you are comfortable shipping that default.

**Staleness.** Packs warn past 180 days since `last_verified`. A scheduled CI
job opens an issue. Regulatory dates move, and silently serving stale rules is
worse than serving none.

**Sign-off.** These packs make compliance-adjacent assertions under your name.
`CONTRIBUTING.md` should require a primary-source citation, a `binding`
classification, and a named verifier for any new or changed rule, with a
dedicated PR template. Contributors adding packs clear the same bar.

## Verification log

A rule may only lose `needs_verification` with a row here.

| rule | verified by | date | primary source + section | outcome |
|---|---|---|---|---|
| | | | | |
