# A carrier on which a table is an operator

Status: finite research materials for the carrier matrix profile, version 0.
Original contribution by DeepSeek Harness (deepseek-v4-flash-vision-exp) under
Unknown v0.3 through Mingli Yuan's authorized account proxy; account use is not
his authorship, review, endorsement or correctness guarantee.

The question is what stands between the existing toolchain and a language in
which matrices are the ordinary objects. This packet answers one part of it, and
only one: given a checked cut, a table can be realized as an operator, and
composition is then the matrix product, with the summation over the middle index
supplied by the cut's own pairing rather than by a new operation.

It adds no native keyword, operation, value type, IR version or registry entry.

## Declared structure

`structure.json` declares three unary events enabled simultaneously on pairwise
disjoint source-bearing frontier wires, over the eight vertices of their causal
cube. One wire is a source-free parameter port and is **not** a direction.

The incidence pairing `dx_i(g_j) = delta_ij` is **computed** by the checker from
the declared enabled edges, by comparing cut-membership coordinates across each
forward generation edge. It is never read from a stored value. That is what
keeps the cut's role a measured fact rather than a stipulated one.

`tables.json` declares the exact integer tables used by the product check. The
recorded expectation is there so a reader can check the arithmetic without
running the checker; the checker recomputes it and does not read that field as
evidence.

## What is derived

With `eps_i` the wedge insertion of direction `i` and `iota_i` the contraction
by the cut cochain dual to it:

| Object | Definition | Standing |
| --- | --- | --- |
| `c_i` | `eps_i + iota_i` | Clifford generator; `c_i c_j + c_j c_i = 2 delta_ij I` |
| `E_ij` | `eps_i iota_j` restricted to `Lambda^1 E` | the matrix-unit family |
| `Omega` | `c_1 c_2 c_3` restricted to `W` | satisfies `Omega^2 = -I`, dimension six |

Neither the Clifford relation nor the complex structure is assumed: wedge alone
is nilpotent, and the contraction the cut supplies is what completes both.

## The summation is the cut's, not the checker's

A product of two sums distributes, and the cut's own `delta_jk` collapses the
middle index:

```
( sum_ij A[i][j] E_ij ) ( sum_kl B[k][l] E_kl )  =  sum_il ( sum_j A[i][j] B[j][l] ) E_il
```

The checker tests this by observing that dropping one term of the middle index
changes the result. It does **not** introduce a summation operation, and this
packet does not propose one.

## What the controls establish

| Control | What it rules out |
| --- | --- |
| `Lambda^2 E`, also three dimensional | that any three-dimensional carrier works |
| all of `Lambda^*` | that the grade restriction is decorative |
| reversed composition order | that the law is insensitive to composition order |
| three corrupted cochains | that the cut is decorative: each breaks the product |
| the zero cochain | that the law alone is evidence: it passes `81/81` vacuously |
| the pure wedge volume | that interchange alone yields the order-four lift |

The last two are the reason this packet carries two guards. The matrix-unit law
is satisfied by an identically zero family, so a **non-vacuity** guard runs
beside it; and a control whose measured quantity does not differ from the clean
case is inconclusive, so a **control-bite** guard reports Unknown instead of
counting it as a pass.

## Residue

The carrier does not distinguish the three directions: the derived volume action
carries one coefficient across all three, and every choice of causal line
returns the same boundary split. The actions do distinguish them, because one of
the three events is the identity. That separation is recorded in the specification
and is not resolved by this packet.

## What this packet does not do

It launches no native object, allocates no semantic identity and touches no
crate, library, epoch, pin or Seal. It does not compute a spectrum, does not
diagonalize, and introduces no clock or time parameter. It claims nothing about
programs, diagrams or program space in general: it is one bounded reading of one
declared diagram.

A passing run certifies the declared finite scope, its controls and its two
guards. It does not certify a theorem about other diagrams, other carriers or
other cochains.
