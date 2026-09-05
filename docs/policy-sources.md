# Policy sources, corrections, and open questions

**Verified: `bsi-de`, `us-eo14412`, `nist-ir8547` (as a draft), and `anssi-fr`
(5 of 6 rules). Not verified: `asd-au`, `eu-roadmap`, and `cnsa-2.0` — the last
because NSA's servers refuse automated access, which needs a human with a
browser rather than more effort.**

Everything here was assembled from secondary reporting — vendor blogs, law-firm
summaries, consultancy explainers — which is frequently wrong about exactly the
details that matter: whether a date binds a requirement or a recommendation,
which population it binds, and whether the edition being quoted is current.

Accordingly every *unverified* rule ships `status: needs_verification`. `cbomctl` prints a
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

## 1. `us-eo14412` — United States, Executive Order 14412 ✅ VERIFIED

**Verified 2026-09-06 by Sadjad Asadi against the Federal Register text:**
EO 14412, *"Securing the Nation Against Advanced Cryptographic Attacks"*,
signed June 22 2026, published June 25 2026 — **91 FR 38483**, FR doc
2026-12909 —
<https://www.federalregister.gov/documents/full_text/text/2026/06/25/2026-12909.txt>

| # | claim | status | where |
|---|---|---|---|
| U1 | Scope is federal **HVAs and high impact systems, excluding National Security Systems** — not blanket federal PQC | ✅ verified | §4(b)(i) |
| U2 | **Key establishment by 2030-12-31** | ✅ verified | §4(b)(ii) |
| U3 | **Digital signatures by 2031-12-31** | ✅ verified | §4(b)(iii) |
| U4 | FAR Council to publish a **proposed** rule requiring covered contractors to comply by 2030-12-31 | ✅ verified | §5(c) |
| U5 | CISA CBOM minimum-elements guidance within **270 days** (≈ 2027-03-19) | ✅ verified | §5(d) |
| U6 | Agency PQC migration lead within **30 days** (by 2026-07-22) | ✅ verified | §4(a) |
| U7 | The order **never uses the word "hybrid"** — 0 occurrences | ✅ verified | whole text |

### The operative sentence

§4(b), one sentence, doing all the work:

> "…issue guidance requiring each agency to: (i) review their inventory of HVAs
> and high impact systems, **excluding National Security Systems**; (ii)
> transition all HVAs and high impact systems to use PQC for **key
> establishment by December 31, 2030**; (iii) transition all HVAs and high
> impact systems to use PQC for **digital signatures by December 31, 2031**"

This is the cleanest primary-source evidence for the urgency asymmetry anywhere
in these packs: **one order, one population, consecutive clauses, and signatures
get an extra year.** The order gives no reason for the gap, so the pack records
`rationale: unstated` — the inference is ours, not the document's.

§1 names the mechanism for key establishment: *"adversaries collecting United
States information now, and decrypting it later once large-scale quantum
computers are operational."*

### Two corrections to how this is usually reported

**It is not a blanket federal mandate.** Secondary coverage routinely renders
this as "the US mandates PQC by 2030". The scope is HVAs and high impact
systems, and NSS are explicitly excluded (they fall under CNSA 2.0 instead).
Running this pack against a commercial system now returns **N/A**, not PASS —
"passes" would read as "you comply" when the truth is "this does not reach you".

**The FAR rule is only proposed.** §5(c) directs the FAR Council to *publish a
proposed rule* within 180 days. A proposed rule is not a contractual
obligation, so that rule is `warn` despite the `executive_order` binding.
Revisit when the final rule publishes.

### Worth watching

§5(d): CISA must, by roughly **2027-03-19**, publish minimum elements for a
cryptographic bill of materials, and those elements *"shall enable the
automated assessment of the cryptographic assets utilized by a hardware or
software element."* That may define the input format this tool consumes. It is
recorded in the pack's notes rather than as a rule — a rule with no selector
would fire on every asset and mask real findings.

## 2. `cnsa-2.0` — United States, NSA ❌ BLOCKED — needs a human

**Verification attempted 2026-09-06 and failed. Not for lack of trying, and not
because the source is unclear — because it cannot be fetched.**

`media.defense.gov` and `nsa.gov` return **HTTP 403** to every automated
request, including with browser user-agents and a referer. Opening the PDF in
the browser triggers a file download rather than rendering it. Attempted:

- `https://media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSA_CNSA_2.0_FAQ_.PDF` → 403
- `https://www.nsa.gov/Cybersecurity-Guidance/` → 403
- the same PDF via a real browser engine → download dialog, no text

**This is a ten-minute job for a human with a browser.** Open the CNSA 2.0 FAQ,
find the timeline table, and check the seven claims below. Until then every
`cnsa-2.0` rule stays `needs_verification` and the pack triggers the banner.

**What the pack currently asserts** — `binding: agency_requirement`, **NSS only**

| # | claim | status |
|---|---|---|
| C1 | Applies to **National Security Systems** only | `needs_verification` |
| C2 | **2027-01-01** acquisition gate | `needs_verification` |
| C3 | Software/firmware signing and networking: exclusive use by **2030** | `needs_verification` |
| C4 | Browsers, servers, cloud, operating systems: exclusive use by **2033** | `needs_verification` |
| C5 | "All NSS by **2031** unless excepted" | `needs_verification` |
| C6 | **ML-KEM-1024, ML-DSA-87, AES-256, SHA-384/512, LMS/XMSS** | `needs_verification` |
| C7 | Hybrid **not required** → `hybrid: silent` | `needs_verification` |

**Priority when you do read it:**

1. **C6's ML-KEM-1024.** BSI and ANSSI both accept ML-KEM-768 (verified). If
   CNSA 2.0 requires -1024, that is a `parameter` conflict independent of the
   hybrid one, and it is the second contradiction the matrix surfaces. Get the
   level requirement exactly.
2. **C7's phrasing.** *Not required* and *discouraged* are different pack
   semantics. `silent` is the current encoding; if NSA actively discourages
   hybrids, change it to `not_recommended` — that sharpens the Europe-versus-
   anglophone split considerably.
3. **C5 versus C3/C4.** A 2031 "all NSS unless excepted" milestone alongside
   2030/2033 category dates looks like it may be a conflation in secondary
   sources. Check whether all three exist.
4. **C1 scoping**, so the applicability banner is right.

## 3. `bsi-de` — Germany, BSI ✅ VERIFIED

**Verified 2026-09-06 by Sadjad Asadi against the primary PDF.**

Source: BSI TR-02102-1, *"Cryptographic Mechanisms: Recommendations and Key
Lengths"*, **Version 2026-01, dated January 23, 2026**, English edition —
<https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Publications/TechGuidelines/TG02102/BSI-TR-02102-1.pdf>

| # | claim | status | where |
|---|---|---|---|
| B1 | **Recommends**, does not mandate. Operative verb throughout is *recommends* → `guideline_recommendation` | ✅ verified | §2.1, §5.3.4 |
| B2 | Sole use of classical key agreement recommended only until **2031-12-31** | ✅ verified | §2.1 |
| B3 | Very high protection requirements: transition by **2030-12-31** | ✅ verified | §2.1 |
| B4 | Classical signatures recommended only until **2035-12-31**, following the EU roadmap | ✅ verified | §2.1 |
| B5 | Quantum-safe **key agreement** should be used in hybrid form | ✅ verified | §2.1, §2.2 |
| B6 | Quantum-safe **signatures** recommended only in combination with a classical signature | ✅ verified | §5.3.4 |
| B7 | **Hash-based signatures may be used standalone** — an explicit carve-out from B6 | ✅ verified | §5.3.4 |

### The operative sentences

**B2 / B3** — §2.1:

> "The sole use of classic key agreement mechanisms is only recommended until
> the end of 2031, see also Section 2.3. For applications with very high
> protection requirements, the transition to quantum-safe mechanisms should
> already take place by the end of 2030."

This settles the earlier open question: 2030 and 2031 are **two distinct
deadlines by protection level**, not a conflation of the 2025-01 and 2026-01
editions.

**B5** — §2.1:

> "The quantum-safe mechanisms recommended in Section 2.4 should be used in
> 'hybrid' form, i.e., in a suitable combination with a classical method."

**B6** — §5.3.4:

> "This Technical Guideline recommends the use of a quantum-safe signature
> scheme only in combination with a classic signature scheme. Hybridisation
> should be implemented in such a way that the hybrid signature scheme is
> secure as long as at least one of the schemes is secure."

**B7, the carve-out** — §5.3.4:

> "The security of hash-based signature schemes is only based on
> complexity-theoretical assumptions about cryptographic hash functions.
> Therefore, hash-based signatures can, provided that the implementation
> security of stateful and stateless hash-based mechanisms is carefully
> considered, in principle also be used alone (i.e. not in hybrid form)."

### A secondary source we can now show to be wrong

A widely-circulated PQShield/ECCG-derived summary states that BSI recommends
classical algorithms in conjunction with **all** PQC algorithms, *including
hash-based ones*. The primary text says the opposite for that specific family:
SLH-DSA, LMS and XMSS may be used alone. The pack encodes this as
`applies_to.exclude_algorithm` on `bsi-hybrid-signatures`, plus an explicit
permission rule.

This is the clearest available argument for the primary-source rule. A pack
built from that summary would have warned on every standalone SLH-DSA signature
in Germany, incorrectly, and no one would have caught it.

### What BSI confirms about the two axes

Both are stated in the guideline itself, which is the best possible evidence for
modelling them separately:

**Urgency** — §2.1 names the mechanism and the asymmetry:

> "…encrypted data can already be stored for later decryption ('Store Now,
> Decrypt Later')."
> "In contrast to key agreement, classic signatures are still trustworthy as
> long as no cryptographically relevant quantum computer exists."

**Assurance** — §5.3.4's hybridisation requirement is about the *new* scheme
possibly being wrong ("secure as long as at least one of the schemes is
secure"), not about timing. Hence 2035 for signatures against 2030/2031 for key
agreement, *and* a hybrid recommendation covering both.

### Consequence for the conflict matrix

F4 is not an ANSSI quirk. **Both** BSI and ANSSI recommend hybrid for
signatures; NSA requires neither hybrid nor permits sub-1024 ML-KEM; ASD
recommends against hybrids for both purposes. The split is Europe versus the
anglophone agencies, on both rows of a purpose × jurisdiction grid — pending
ANSSI's own primary-source confirmation (§4, F4).

### Still open

- Whether BSI's forward-looking statement — §2.1: *"In future versions,
  signature methods that are not quantum-safe will therefore only be
  recommended for hybrid use"* — should be encoded now as a scheduled change or
  left until the edition that makes it operative. Currently not encoded.
- §2.4 lists FrodoKEM, Classic McEliece, ML-KEM and HQC as recommended
  quantum-safe key agreement mechanisms. HQC is **not yet a final FIPS**, so it
  must not appear as a `migration_target`; BSI's acceptance of FrodoKEM and
  Classic McEliece is jurisdiction-specific and not yet encoded.

## 4. `anssi-fr` — France, ANSSI ✅ VERIFIED (5 of 6 rules)

**Verified 2026-09-06 by Sadjad Asadi against the primary PDF:** *"ANSSI views
on the Post-Quantum Cryptography transition (2023 follow up)"*, **December 21,
2023** —
<https://cyber.gouv.fr/publications/anssi-views-post-quantum-cryptography-transition>

| # | claim | status | where |
|---|---|---|---|
| F3 | Hybridation emphasised as **necessary** wherever PQ mitigation is needed | ✅ verified | §1.1 |
| F4 | The requirement **covers signatures** | ✅ verified | §3.2, §4 |
| F4b | **Hash-based signatures exempt** — hybridation optional for XMSS/LMS/SPHINCS+ | ✅ verified | §2, §4 |
| F7 | For a **security visa**, hybridation is *mandatory* — "shall implement" | ✅ verified | §4 |
| F2 | Hybrid recommended especially for protection lasting past **2030** | ✅ verified | §1.2 |
| F1 | 2027 certification cut-off | ❌ **not in this document** | — |

### The operative sentences

**F3** — §1.1:

> "ANSSI still strongly emphasizes the necessity of hybridation wherever
> post-quantum mitigation is needed both in the short and medium term."

**F4 / F4b** — §4, on end products:

> "any product that includes post-quantum mitigation shall implement
> hybridation except if the quantum mitigation only relies on hash-based
> signatures like XMSS, LMS or SPHINCS+ for which hybridation is optional"

**F7** — §4, on the security-visa process:

> the evaluation tasks "comprise an analysis of all cryptographic algorithms
> including the post-quantum algorithms with **mandatory hybridation**"

"Mandatory" and "shall" are ANSSI's own words, but they sit inside the
security-visa process. Outside it the position paper *recommends*. The pack
models these as two rules with different `binding` — `certification_requirement`
and `guideline_recommendation` — because they bind different populations, and a
tool that merged them would tell an uncertified French vendor it had failed a
mandate that does not reach it.

### F4 resolved: it is an assurance argument, and ANSSI says so

The question that had been open since the first draft — whether ANSSI's
signature stance is a harvest argument or a maturity one — is answered in §1.1:

> "even if the post-quantum algorithms have gained a lot of attention, they are
> still not mature enough to solely ensure the security. For example, several
> post-quantum schemes have suffered from classical attacks in the past years,
> e.g. [3, 6]."

Reference **[3] is Beullens, "Breaking Rainbow takes a weekend on a laptop"**.
So the `algorithm_maturity` rationale is not our inference — ANSSI cites the
Rainbow break as its reason. This is primary-source support for modelling
urgency and assurance as separate axes.

§1.1 also notes the alignment explicitly: *"This position is aligned with the
one of other European cybersecurity agencies like BSI in Germany."*

### Two jurisdictions, one carve-out, independently confirmed

BSI §5.3.4 and ANSSI §2/§4 both exempt hash-based signatures from the hybrid
recommendation, for the same stated reason — their security rests only on
hash-function assumptions. Encoded identically in both packs via
`applies_to.exclude_algorithm`. That two independent authorities landed on the
same exception is a good sign the reading is right.

### Still open

- **F1 — the 2027 certification deadline is not in this document.** The 2023
  follow-up describes a 3-phase visa roadmap with phase-2 visas *"expected to be
  delivered around 2024-2025"*, and says ANSSI is "speeding-up the original
  agenda". The 2027 date appears only in 2026 press coverage. The rule stays
  `needs_verification`; find the 2026 ANSSI communication or drop it.
- The **2022** position paper (referenced as [1]) has not been read. F5's
  three-phase structure and any FrodoKEM preference (F6) live there. §2 of the
  follow-up does describe FrodoKEM as "a more conservative variant of
  CRYSTALS-Kyber" but states no preference ordering, so F6 is not encoded.

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

## 7. `nist-ir8547` — United States, NIST ✅ VERIFIED (as a draft)

**Verified 2026-09-06 by Sadjad Asadi against the primary PDF:** NIST IR 8547
**ipd (Initial Public Draft), November 2024**, *Transition to Post-Quantum
Cryptography Standards* —
<https://nvlpubs.nist.gov/nistpubs/ir/2024/NIST.IR.8547.ipd.pdf>

Verified **as a draft**: the reading is confirmed; the status of the document is
not. Every rule carries `is_draft: true`, and all four reporters print a draft
notice when one is cited.

### Deprecated is not disallowed

NIST's own glossary, quoted in the rules:

> **deprecated** — "The algorithm and key length may be used, but the user must
> accept some security risk."
> **disallowed** — "The algorithm or key length is no longer allowed for
> applying cryptographic protection."

These are modelled as separate `deadline_state` values. Collapsing them into one
failure is the single most commonly misstated point in PQC compliance, and it is
the subject of article 2.

### The tables, exactly

Table 2 (signatures: ECDSA, EdDSA, RSA) and Table 4 (key establishment:
finite-field DH/MQV, EC DH/MQV, RSA) have **identical structure**:

| security strength | transition |
|---|---|
| **112 bits** | Deprecated after 2030 **and** Disallowed after 2035 |
| **≥ 128 bits** | Disallowed after 2035 — **no 2030 deprecation** |

This is the detail that almost every summary loses. "RSA is deprecated in 2030"
is true only at 112-bit strength (RSA-2048). RSA-3072 and P-256 are **not**
deprecated in 2030 under this draft — they are only disallowed after 2035. A
tool that warns on all RSA in 2030 is wrong, and a pinned test asserts our
deprecation rules carry `security_level: ["112"]`.

Note also that EdDSA appears only at ≥128 bits, so it has no 2030 row at all.

### Still open

- The draft's comment period closed 2025-01-10. **Check whether a final IR 8547
  has been published**; if so this pack rebases and `is_draft` clears.
- Tables 6 and 7 (block ciphers, hash functions) are not yet encoded — they are
  Grover-scale concerns and score `low` in this tool regardless, but the pack
  should carry them for completeness.

## 8. Cross-cutting

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
| `bsi-classical-key-agreement-sunset` | Sadjad Asadi | 2026-09-06 | TR-02102-1 v2026-01 §2.1 | confirmed, 2031-12-31 |
| `bsi-high-protection-2030` | Sadjad Asadi | 2026-09-06 | TR-02102-1 v2026-01 §2.1 | confirmed, distinct from 2031 |
| `bsi-hybrid-key-agreement` | Sadjad Asadi | 2026-09-06 | TR-02102-1 v2026-01 §2.1, §2.2 | confirmed, *recommends* |
| `bsi-classical-signatures-2035` | Sadjad Asadi | 2026-09-06 | TR-02102-1 v2026-01 §2.1 | confirmed, 2035-12-31 |
| `bsi-hybrid-signatures` | Sadjad Asadi | 2026-09-06 | TR-02102-1 v2026-01 §5.3.4 | confirmed, *recommends* |
| `bsi-hash-based-standalone-permitted` | Sadjad Asadi | 2026-09-06 | TR-02102-1 v2026-01 §5.3.4 | carve-out confirmed; contradicts a common secondary summary |
| `anssi-hybridation-necessary` | Sadjad Asadi | 2026-09-06 | ANSSI 2023 follow-up §1.1 | confirmed; rationale is maturity, citing the Rainbow break |
| `anssi-hybridation-signatures` | Sadjad Asadi | 2026-09-06 | ANSSI 2023 follow-up §3.2, §4 | confirmed, covers signatures |
| `anssi-hash-based-hybridation-optional` | Sadjad Asadi | 2026-09-06 | ANSSI 2023 follow-up §2, §4 | carve-out confirmed, matches BSI |
| `anssi-visa-hybridation-mandatory` | Sadjad Asadi | 2026-09-06 | ANSSI 2023 follow-up §4 | confirmed "mandatory"/"shall", scoped to security visas |
| `anssi-longlived-protection-2030` | Sadjad Asadi | 2026-09-06 | ANSSI 2023 follow-up §1.2 | confirmed |
| `anssi-certification-2027` | — | — | — | **not found in the 2023 follow-up**; stays unverified |
| `eo14412-key-establishment-2030` | Sadjad Asadi | 2026-09-06 | 91 FR 38483 §4(b)(ii) | confirmed |
| `eo14412-signatures-2031` | Sadjad Asadi | 2026-09-06 | 91 FR 38483 §4(b)(iii) | confirmed, one year later than key establishment |
| `eo14412-far-contractors-2030` | Sadjad Asadi | 2026-09-06 | 91 FR 38483 §5(c) | confirmed; rule is *proposed*, so WARN |
| `nist-112bit-signatures-deprecated-2030` | Sadjad Asadi | 2026-09-06 | IR 8547 ipd §4.1.1 Table 2 | confirmed; 112-bit only |
| `nist-signatures-disallowed-2035` | Sadjad Asadi | 2026-09-06 | IR 8547 ipd §4.1.1 Table 2 | confirmed, all strengths |
| `nist-112bit-key-establishment-deprecated-2030` | Sadjad Asadi | 2026-09-06 | IR 8547 ipd §4.1.2 Table 4 | confirmed; 112-bit only |
| `nist-key-establishment-disallowed-2035` | Sadjad Asadi | 2026-09-06 | IR 8547 ipd §4.1.2 Table 4 | confirmed, all strengths |
| **`cnsa-2.0` (all rules)** | — | 2026-09-06 | **blocked: nsa.gov and media.defense.gov return 403** | needs a human with a browser |
