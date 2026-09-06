# Writing

Longer pieces on post-quantum migration, written while building `cbomctl` and
reading the source documents it cites.

Every code block in these is generated from a real run and diff-checked in CI,
so the prose cannot describe behaviour the tool does not have. That rule exists
because one of them nearly shipped a demo showing behaviour that did not exist
yet — the story is in the first article below.

## Published

- [**Everyone agrees on the risk. They disagree on the price.**](everyone-agrees-on-the-risk.md)
  *2026-09-06* — Germany, France and the EU recommend hybrid post-quantum key
  exchange. Australia recommends against it. The NSA does not permit it on
  national security systems. They are not disagreeing about cryptography: ASD
  grants the European premise in the paragraph where it declines to follow it.

- [**RSA-2048 and RSA-3072 have different futures**](rsa-2048-and-rsa-3072.md)
  *2026-09-06* — NIST IR 8547 scopes its 2030 deprecation to 112 bits of
  security strength, not to an algorithm. Half of "RSA is deprecated in 2030"
  is false, and it is the half people plan around.

## Coming

- **Signatures aren't urgent — but they aren't simple.** Why key exchange comes
  first, and why that does not make signatures easy.

---

*These are syndicated elsewhere with a canonical link back here. This is the
copy that gets corrected.*
