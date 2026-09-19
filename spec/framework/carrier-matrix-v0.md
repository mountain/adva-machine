# Carrier matrix profile, version 0

Status: **finite research profile**, 2026-09-19. This profile specifies a
carrier, a matrix-unit family and a table-to-operator correspondence derived
from checked cut data. It registers **no** native keyword, operation, value
type, IR version or stable semantic type. English is primary.

Mingli Yuan requested a matrix-mechanics language and asked what stands between
the existing toolchain and one. DeepSeek Harness (deepseek-v4-flash-vision-exp)
authored this original profile and its checks under Unknown v0.3 through his
authorized account proxy; account use is not his authorship, review, endorsement
or correctness guarantee. The account owner does not vouch for the content.

## Meaning and dependency

A *carrier* is a finite-dimensional module over a declared set of cut
directions. The directions are read from one checked diagram: they are the
simultaneously enabled unary events on pairwise disjoint source-bearing
frontier wires. A source-free parameter port is not a direction.

The profile reuses the cut vocabulary already exercised by the
[causal-cut chirality cube](../../docs/research/0010-causal-cut-chirality-cube.md)
and the
[rational covariance calibration](../../docs/research/frame-covariance-rational-calibration.md).
It adds no library, epoch, pin or Seal change, and it upgrades no consumer lock.

| Component | Role | Retained distinction |
| --- | --- | --- |
| directions `1..n` | Declared index set, read from one checked diagram | An index, not an operation; not inferred from numeric values |
| `dx_i(g_j) = delta_ij` | Cut pairing between membership cochains and forward generation edges | Computed from causally enabled edges, never stipulated |
| `eps_i` | Wedge insertion of direction `i` | Construction-facing; raises exterior grade |
| `iota_i` | Contraction by the cut cochain dual to direction `i` | Boundary-facing; lowers exterior grade |
| `c_i = eps_i + iota_i` | Clifford generator | A combined action, not a third primitive |
| `Lambda^1 E` | The grade-1 carrier, dimension `n` | Not the whole exterior algebra, and not `Lambda^2 E` |
| `E_ij` | Matrix-unit family on `Lambda^1 E` | An index pair, not a direction and not an event |
| table `A` | An `n x n` array of scalars | An index structure, not an operator until realized |

## Finite laws

All laws below were re-measured on 2026-09-19 over exact integer arithmetic for
`n = 3`, on the checked three-branch fixture, and cross-checked by two
independent implementations (a Rust crate with no dependencies and a Python
probe). The executable materials are to be received under
`knowledge/received/carrier-matrix-<date>-v1/`.

### The Clifford relation is derived, not assumed

Wedge insertion alone is insufficient: the pure exterior volume is nilpotent, so
interchange cannot by itself produce an order-four orientation lift. Adding the
contraction supplied by the cut completes it:

```
c_i c_j + c_j c_i  =  2 delta_ij I
```

### The matrix-unit law

With `E_ij = eps_i iota_j` restricted to the grade-1 carrier,

```
E_ij E_kl  =  delta_jk E_il
```

holds for all `81` index quadruples at `n = 3`. In the grade-1 basis each
`E_ij` is literally the standard matrix unit `e_ij`.

### The carrier is a full matrix algebra

```
sum_i E_ii  =  I          (identity)
E_ij (E_kl E_mn) = (E_ij E_kl) E_mn   (associativity; all 729 triples checked)
E_ij (E_kl + E_mn) = E_ij E_kl + E_ij E_mn   (distributivity)
```

The nine matrix units span the full `3 x 3` matrix algebra `M_3`. No algebraic
structure is missing at this level.

### A table is realized as an operator, and composition is the product

A table `A` is realized as `sum_ij A[i][j] E_ij`, and

```
realize(A) . realize(B)  =  realize(A B)
```

was checked exactly on a concrete `3 x 3` pair. The realized operator equals the
table, so the correspondence is the identity on this carrier.

### The middle-index summation needs no operation

```
sum_i eps_i iota_i  =  deg          (grade operator)
sum_i iota_i eps_i  =  n - deg
sum_i (iota_i eps_i + eps_i iota_i)  =  n I
```

The summation over the middle index of a product is the cut's own `delta_jk`
collapsing when the two sums distribute. It is not a separate primitive, and
nothing has to be added to obtain it.

### The complex structure is derived

With `Omega = c_1 c_2 c_3` restricted to `W = Lambda^1 E + Lambda^2 E`,

```
Omega^2 = -I            (dimension 6, characteristic polynomial (lambda^2+1)^3)
```

It leaves `W` invariant and needs no new primitive.

### Carrier symmetry and action degeneracy are different facts

The carrier treats the three directions symmetrically: the derived volume action
carries **one common coefficient** across all three directions, and the
causal-line split returns `(1,2,2,1)` for **every** choice of which direction is
time.

The **invariant** is that the coefficient is common. Its **value** is not an
invariant: it depends on the declared composition order of the volume word and
on the declared signed basis of the carrier. The checker records both
conventions with its measurement and makes no claim about the value.

The actions do not: of the three enabled events, `neg` and `scale 2` change the
value and `id` is the identity for every tested input.

> A causal line may be chosen from any **direction**, but not from a direction
> whose **action** is the identity; that direction advances nothing.

Triadicity therefore belongs to the index structure and not to the operations.
The `81/81` law above is not in tension with an inert third event: they are
statements about different layers.

### Scale

A `k x k` family requires at least `k` independent cut directions, because
`Lambda^1 E` has dimension `n`. Larger tables require a diagram with more
independent directions; nothing here claims a bound beyond that.

## Controls

Each control was executed and is retained with its witness. A control that
passes under a corrupted input would make the corresponding claim vacuous.

| Control | Measured |
| --- | --- |
| `Lambda^2 E`, also 3-dimensional | law holds only `45/81` |
| All of `Lambda^*` rather than grade 1 | law holds only `45/81` |
| Reversed composition `iota_j eps_i` on `Lambda^1 E` | law holds only `27/81` |
| Off-diagonal cochain substitution | matrix product **fails**; law `45/81` |
| Doubled-diagonal cochain | matrix product **fails**; law `54/81` |
| Sign-flipped cochain | matrix product **fails**; law `72/81` |
| Zero cochain | law passes `81/81` **vacuously**; product **fails** |
| Interchange alone (pure wedge) | volume is nilpotent; no order-four lift |

The zero-cochain row is the reason a non-vacuity guard is mandatory rather than
optional: the matrix-unit law alone can be satisfied by an identically zero
family. The falsifier that has teeth is the product comparison, not the law.

## Contraction authorization

`E_ij E_kl = delta_jk E_il` identifies the middle indices `j` and `k`. Under the
existing discipline, value equality and observational equivalence never
authorize contraction, memoization, CSE, or a cell, and this profile does not
weaken that rule. The authorization here is different in kind and is stated
explicitly:

> The identification of `j` and `k` is authorized **only** by the checked
> identity `E_ij E_kl = delta_jk E_il` holding over the declared finite index
> set of this profile. It is **not** authorized by equality of realized values,
> by observational equivalence under any policy, by structural hashing, or by
> any host-language aliasing. No contraction outside a checked matrix-unit
> identity is licensed by this profile.

## What this profile does not establish

- **No native admission.** `ValueType` remains `Real | Bool`. No `OperationSpec`
  entry, parser surface form, registry change, IR version change or Seal is
  created, proposed or implied.
- **No linear or matrix ontology for programs in general.** The
  [research agenda](../../docs/RESEARCH_ENGINEERING_AGENDA.md) states that its
  notation "must not force general programs into a linear or matrix ontology",
  and that the useful intrinsic structure of a fragment may instead be an SCC
  decomposition, a minimal automaton, a recurrence, a minimal polynomial, a
  reachable/observable quotient, a block normal form or a finite boundary
  response. This profile is one bounded reading of one declared diagram among
  those possibilities. It does not claim that programs, diagrams or program
  space are matrices, and it licenses no promotion of this reading to a general
  presentation.
- **No spectrum, no diagonalization, no dynamics.** No eigenvalue, resolvent,
  process exponential, clock or time parameter is added. The known no-go that
  a spectrum does not determine a program is untouched.
- **No physical reading.** Nothing here identifies a direction with a state, an
  operator with an observable, or `Omega` with a physical imaginary unit. The
  repository's standing separation of structural analogy, typed semantic map and
  physical realization theorem is unchanged.
- **No general duality.** The table-to-operator correspondence is a finite
  calibration; it is not `D*`, not an observer pullback and not an equation cell.
- **No claim beyond the checked scope.** Every number above is bounded to
  `n = 3`, to the declared finite index set and to the executed controls. A
  passing control set is evidence for the declared scope, not a theorem.

## Receiving and reuse

Reuse requires the exact diagram, profile version, direction set, carrier and
control set. A changed diagram changes the directions and therefore the carrier;
a missing binding leaves the correspondence unresolved; a failed control refuses
the proposed correspondence rather than weakening it.

This specification is a document. It does not execute, does not certify and does
not promote anything. Its companion checker and evidence are to be received
separately under `knowledge/received/`, following the pattern already used for
the iota interpretation frame, which likewise registers no native keyword,
operation or stable semantic type.
