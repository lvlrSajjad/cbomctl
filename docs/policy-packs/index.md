# Policy packs

Each pack is a rule set describing what one authority says about post-quantum cryptography: which algorithms, which constructions, by when, and **with what force**.

The packs are a [standalone versioned artifact](https://github.com/lvlrSajjad/cbomctl/tree/main/policy-packs) with their own schema and changelog. Nothing in them depends on `cbomctl` — if you want to build something else on them, take them.

| pack | id | jurisdiction | verified rules | |
|---|---|---|---|---|
| [ANSSI — France](anssi-fr.md) | `anssi-fr` | FR | 5/5 | ✅ |
| [ASD / ACSC — Australia](asd-au.md) | `asd-au` | AU | 6/6 | ✅ |
| [BSI — Germany](bsi-de.md) | `bsi-de` | DE | 6/6 | ✅ |
| [CNSA 2.0 — NSA](cnsa-2.0.md) | `cnsa-2.0` | US-NSS | 0/7 | ⚠️ |
| [EU Coordinated Implementation Roadmap](eu-roadmap.md) | `eu-roadmap` | EU | 6/6 | ✅ |
| [NIST IR 8547 (draft) — United States](nist-ir8547.md) | `nist-ir8547` | US | 4/4 | ✅ |
| [Executive Order 14412 — United States](us-eo14412.md) | `us-eo14412` | US | 3/3 | ✅ |

## Why `binding` matters

Most post-quantum guidance is **not a mandate**, and reporting a technical guideline as a legal requirement is the most common error in this space. BSI TR-02102-1 *recommends*. ANSSI's "mandatory hybridation" applies only inside its security-visa process. The EU roadmap is a Recommendation, non-binding on operators under TFEU Art. 288.

So every rule carries a `binding` value, and it — not severity — decides `FAIL` versus `WARN`. A `guideline_recommendation` cannot produce `FAIL`, and that is enforced in code rather than left to authoring discipline.

## The hybrid gradient

`hybrid` is scoped **per purpose**, because authorities differ between key establishment and signatures. It is also not a binary:

| stance | meaning | consequence |
|---|---|---|
| `recommended` | encouraged | BSI, ANSSI, EU roadmap |
| `not_recommended` | discouraged, still permitted | ASD — a satisfies-all target still exists, at a cost |
| `not_permitted_except_interop` | not permitted outside named exceptions | NSA (pending verification) — **no** single construction satisfies everyone |

That middle step is what makes compromise possible and the third is what removes it. A tool reporting only PASS/FAIL cannot express the difference.
