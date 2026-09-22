# Three-Hole Conjugate M6 and the Projective J-Lift

Status: theoretical bridge candidate following
[AEG Paper 0](https://github.com/mountain/aeg-paper/blob/main/paper-0/aeg-paper-0.tex),
[AEG Paper II](https://github.com/mountain/aeg-paper/blob/main/paper-2/aeg-paper-2.tex),
[note 0101](0101-six-port-whole-cut-theory.md),
[note 0103](0103-cell-carrier-view-relation-machines.md), and
[note 0104](0104-whole-cut-six-to-m6-boundary-bridge.md).

This note records a proposal initiated by Mingli Yuan:

> The three residual holes appear to lack one common line. A line threaded
> through those holes should produce a conjugate M6, and the conjugate
> direction may be the same imaginary unit already latent in the projective
> left/right expansion of AEG.

The note separates two exact finite statements from the proposed bridge that
joins them. It changes no stable Adva language, evaluator, semantic API,
physical interpretation, or claim about Teichmüller space.

---

## 0. Result and status boundary

There are three layers.

### Exact finite layer

Three binary holes have six distinct boundary germs. Their hole pairing,
together with any disjoint complete pairing whose union is connected, forms an
alternating six-cycle. The two cyclic orders through three labeled holes give
two oppositely oriented M6 boundary presentations.

### Exact projective layer

The AEG reciprocal switch

\[
z\longmapsto-\frac1z
\]

is represented on real homogeneous coordinates by

\[
J=
\begin{pmatrix}
0&-1\\
1&0
\end{pmatrix}.
\]

It satisfies

\[
J^2=-I
\]

before projectivization, while

\[
[J]^2=[I]
\]

in the projective quotient. Thus the projective involution is the shadow of an
order-four linear lift, and that lift is the real two-dimensional
representation of multiplication by \(i\).

### Proposed bridge

The two three-hole M6 presentations may carry one typed transport
\(\mathcal J\) whose square is a retained central sign upstairs and the
identity in a projective view:

\[
\mathcal J^2=\epsilon,
\qquad
\rho(\epsilon)=-I,
\qquad
\pi(\epsilon)=1.
\]

This bridge is not supplied by the six-cycle theorem alone. It requires a
typed adapter that preserves port, state, step, orientation, source, and
occurrence ledgers. Its compatibility with Q4, M6, and TO24 remains open.

---

## 1. Three holes as six boundary germs

Let the labeled holes be

\[
h_1,\qquad h_2,\qquad h_3.
\]

Binary cutting exposes two distinct boundary germs per hole:

\[
P_h=
\{
h_1^+,h_1^-,
h_2^+,h_2^-,
h_3^+,h_3^-
\}.
\]

The signs record a local coorientation only. They are not Boolean truth,
energy sign, braid crossing sign, left/right syntax, or complex conjugation.

The hole pairing is the fixed-point-free involution

\[
\kappa_h=
\{
(h_1^+,h_1^-),
(h_2^+,h_2^-),
(h_3^+,h_3^-)
\}.
\tag{HolePairing}
\]

A line that visits all three holes once must also account for all six exposed
germs. The positive cyclic threading is

\[
\tau_+=
\{
(h_1^+,h_2^-),
(h_2^+,h_3^-),
(h_3^+,h_1^-)
\},
\tag{PositiveThread}
\]

and the negative cyclic threading is

\[
\tau_-=
\{
(h_1^+,h_3^-),
(h_3^+,h_2^-),
(h_2^+,h_1^-)
\}.
\tag{NegativeThread}
\]

Each is a complete fixed-point-free involution on the same six-germ ledger,
and neither shares an edge with \(\kappa_h\).

A single drawn curve may represent either pairing only when its occurrence
ledger records all three segments and their cyclic incidence. Visual
connectedness is not a substitute for that record.

---

## 2. Three-hole alternating-cycle theorem

### Theorem

Let \(P\) be a six-element set and let \(\kappa,\tau:P\to P\) be
fixed-point-free involutions. Assume:

1. both involutions are total on the same set;
2. their unordered edge sets are disjoint; and
3. the graph \(G=(P,E_\kappa\cup E_\tau)\) is connected.

Then \(G\) is an alternating six-cycle.

### Proof

Every vertex belongs to exactly one \(\kappa\)-edge and exactly one
\(\tau\)-edge. Hence every vertex of \(G\) has degree two. A finite connected
two-regular graph is a cycle. Because \(G\) has six vertices, it is \(C_6\).
At each vertex the two incident edges come from different involutions, so the
edge labels alternate. Therefore, after choosing a root and orientation, the
two length-three paths between opposite vertices read

\[
\kappa\tau\kappa
\qquad\text{and}\qquad
\tau\kappa\tau.
\]

They present the open relation boundary

\[
M_6^\partial[
\kappa\tau\kappa
\Rightarrow
\tau\kappa\tau].
\qquad\square
\]

Applying the theorem to \((\kappa_h,\tau_+)\) and
\((\kappa_h,\tau_-)\) yields two M6 boundary presentations

\[
M_{6,+}^\partial,
\qquad
M_{6,-}^\partial.
\]

The transposition \(h_2\leftrightarrow h_3\) exchanges the two cyclic
threadings. If the hole labels carry the declared cyclic order
\(h_1\to h_2\to h_3\to h_1\), this exchange reverses its orientation.

### What the theorem does not prove

It does not provide:

- an M6 filler;
- a braid equation;
- a complex vector space;
- a canonical map between the two M6 presentations;
- a phase, Hamiltonian, or time parameter;
- a Teichmüller-space identification; or
- a physical interpretation of the holes.

The theorem proves only the finite incidence statement.

### Exact hole-polarity conjugacy

The displayed fixture has a further exact symmetry. Define the simultaneous
hole-polarity reversal

\[
\rho_h
:=
(h_1^+\,h_1^-)
(h_2^+\,h_2^-)
(h_3^+\,h_3^-)
=
\kappa_h.
\tag{HolePolarityReversal}
\]

Relabeling every endpoint of the positive threading by \(\rho_h\) gives

\[
\begin{aligned}
(h_1^+,h_2^-)&\longmapsto(h_1^-,h_2^+)
                         =(h_2^+,h_1^-),\\
(h_2^+,h_3^-)&\longmapsto(h_2^-,h_3^+)
                         =(h_3^+,h_2^-),\\
(h_3^+,h_1^-)&\longmapsto(h_3^-,h_1^+)
                         =(h_1^+,h_3^-).
\end{aligned}
\]

These are exactly the three edges of \(\tau_-\). Hence

\[
\boxed{
\rho_h\kappa_h\rho_h^{-1}=\kappa_h,
\qquad
\rho_h\tau_+\rho_h^{-1}=\tau_-,
\qquad
\rho_h^2=1.
}
\tag{HolePolarityConjugacy}
\]

If hole identities are fixed, no reversal of only one or two holes has this
property. Indeed, write \(f_i\in\{0,1\}\) for whether hole \(h_i\) is reversed.
For every edge of \(\tau_+\) to remain a plus--minus edge after transport,
adjacent holes must satisfy \(f_i=f_{i+1}\). Connectedness of the three-hole
cycle forces \(f_1=f_2=f_3\). Reversing none leaves \(\tau_+\) unchanged, so
reversing all three is the unique label-preserving solution.

If hole labels may be transported, exchanging any two complete labeled holes
also reverses the cyclic threading. With a distinguished root \(h_1\), the
label-only reflection is \(h_2\leftrightarrow h_3\). Such relabelings are not
occurrence-preserving identities; a typed adapter must account for them.

An independent exhaustive audit over all \(6!=720\) port permutations finds:

| exact filter | number of permutations |
|---|---:|
| preserves \(\kappa_h\) | 48 |
| also sends \(\tau_+\) to \(\tau_-\) | 6 |
| also squares to the identity on the port ledger | 4 |

The four involutive solutions are the global reversal \(\rho_h\) and the three
transpositions of complete hole labels. The executable audit is
tests/python/test_three_hole_polarity_m6.py.

The verification methods are deliberately separated:

| check | verification kind | proof status |
|---|---|---|
| displayed edge transport and \(\rho_h^2=1\) | exact symbolic finite calculation | proof |
| classification of all port transports | exact exhaustive discrete calculation | machine-checked proof for the six-port fixture |
| \(J^2=-I\) | exact integer-matrix calculation | proof |
| six nonzero rational round trips under \(z\mapsto-1/z\) | exact-arithmetic sample check | supplementary, not a proof |
| floating-point experiment | not used | none |

### M6-family name

Use \(M_6^\partial\) for the abstract alternating six-state boundary type and
\(\mathfrak M_6\) for the family of relation machines presenting that type.
The braid machine remains the principal representative:

\[
\mathcal M_6^{\mathrm{br}}\in\mathfrak M_6.
\]

Name the present nonprincipal member the **Three-Hole Polarity M6 Machine**:

\[
\boxed{
\mathcal M_6^{\mathrm{hp}}\in\mathfrak M_6,
}
\qquad
\mathrm{hp}=\mathrm{hole\mbox{-}polarity}.
\tag{HolePolarityM6}
\]

Its two oriented open presentations are

\[
\left(\mathcal M_6^{\mathrm{hp}}\right)_\pm^\partial
=
(P_h,\kappa_h,\tau_\pm),
\]

and their exact port transport is

\[
\rho_h:
\left(\mathcal M_6^{\mathrm{hp}}\right)_+^\partial
\longrightarrow
\left(\mathcal M_6^{\mathrm{hp}}\right)_-^\partial.
\]

In code and prose use HolePolarityM6 for the member and reserve unqualified M6
for the established boundary/family context. Do not call this member JM6,
ConjugateM6, or ReciprocalM6: those names would promote the unproved typed
projective bridge or conflate distinct conjugations. If the typed lift is later
constructed, attach it as extra structure

\[
\left(\mathcal M_6^{\mathrm{hp}},\mathcal J_h,\epsilon\right),
\qquad
V_{\mathrm{port}}(\mathcal J_h)=\rho_h,
\qquad
\mathcal J_h^2=\epsilon,
\]

without changing the family-member name.

The equality \(V_{\mathrm{port}}(\mathcal J_h)=\rho_h\) remains a typing and
naturality obligation. The exact permutation calculation does not by itself
identify local coorientation with left/right syntax or with the linear complex
structure \(J\).

---

## 3. Relation to the existing WholeCut6 bridge

Note 0104 starts with six authoritative ports, one cut pairing
\(\kappa\), and one through pairing \(\tau\). Under the same totality,
disjointness, and connectedness conditions it obtains an open M6 boundary.

The present construction has the same abstract matching theorem but a
different proposed source:

| construction | first matching | second matching | retained meaning |
|---|---|---|---|
| WholeCut6 bridge | three atomic cut pairings | three sustained through pairings | checked six-port carrier |
| three-hole bridge | three exposed hole-side pairings | one three-hole line recorded as three segments | residual-hole presentation |

No identification between these rows is authorized by their isomorphic
six-cycles. A future adapter must specify whether each hole germ reuses an
existing WholeCut6 port occurrence, presents a view-local state, or introduces
a genuinely new typed boundary. It must not infer occurrence identity from a
shared drawing.

---

## 4. The AEG left/right projective switch

AEG Paper 0 distinguishes two expression expansions.

- The nondegenerate left-expanded one-hole language lies in the affine
  stabilizer of infinity.
- The right-expanded language includes reciprocal behavior and reaches a
  larger projective Möbius carrier.

They are not merely two spellings of one operator. The common projective
carrier nevertheless contains the reciprocal switch

\[
j(z)=-\frac1z.
\tag{ReciprocalSwitch}
\]

On homogeneous real coordinates \([x:y]\), let

\[
J(x,y)=(-y,x).
\]

Then

\[
[x:y]\longmapsto[-y:x]
\]

has affine coordinate

\[
\frac{-y}{x}=-\frac1{x/y}.
\]

Thus \(J\) is a linear lift of the AEG reciprocal switch. Direct calculation
gives

\[
J^2(x,y)=(-x,-y),
\]

hence

\[
J^2=-I.
\tag{LinearSquare}
\]

The scalar \(-I\) acts trivially on projective points, so

\[
[J]^2=[I].
\tag{ProjectiveSquare}
\]

Equivalently, in the central double cover

\[
\{\pm I\}
\longrightarrow
SL_2(\mathbb R)
\longrightarrow
PSL_2(\mathbb R),
\]

the lift \(J\) has order four while its projective image has order two.

Identifying \(\mathbb R^2\) with \(\mathbb C\) by

\[
(x,y)\longleftrightarrow x+iy
\]

makes \(J\) multiplication by \(i\):

\[
J(x+iy)=i(x+iy).
\]

The imaginary direction is therefore already latent in the linear lift of the
projective left/right switch. It is not introduced by naming the projective
involution alone; it appears only when the central sign erased by
projectivization is retained.

---

## 5. Five operations called conjugation

The word conjugation currently risks collapsing five different operations.

### 5.1 Cycle reversal

The combinatorial reversal

\[
R_{\mathrm{cyc}}:
M_{6,+}^\partial
\longleftrightarrow
M_{6,-}^\partial
\]

changes the declared cyclic orientation. It squares to the identity.

### 5.2 Path inverse

A history word may be reversed and each invertible step replaced by its
inverse. This is stronger than reading the same incidence cycle backward and
is unavailable for a noninvertible step.

### 5.3 Möbius conjugation

For a projective operator \(g\),

\[
g\longmapsto JgJ^{-1}
\]

changes the projective frame. It is ordinary group conjugation.

### 5.4 Complex conjugation and complex structure

On \(\mathbb C\), complex conjugation is the real-linear reflection

\[
C(x+iy)=x-iy,
\qquad
C^2=I.
\]

Multiplication by \(i\) is the real-linear complex structure \(J\), with

\[
J^2=-I.
\]

They satisfy

\[
CJC^{-1}=-J=J^{-1}.
\tag{ConjugateComplexStructure}
\]

Thus \(i\) is not complex conjugation. Rather, complex conjugation reverses
the \(i\)-direction. A precise formulation of the motivating intuition is:

> the conjugate M6 pair should be exchanged by a reflection \(C\), while the
> transverse transport joining their real presentations should be governed
> by one complex structure \(J\).

This distinction is mandatory.

### 5.5 Boundary identification reversal

A fifth operation is needed by the motivating sentence and is none of 5.1--5.4.
When two oriented surfaces with boundary are glued along boundary components,
the identification must reverse orientation for the result to be orientable.
Two three-holed spheres glued along all three boundary circles therefore yield
one closed orientable surface of genus two: each three-holed sphere has Euler
characteristic \(-1\), so the union has \(-2\), and \(2-2g=-2\) gives \(g=2\).
Cutting that surface back along the three curves of its pants decomposition
returns the two three-holed spheres, whose boundary circles number six in
total, two per cut curve.

Record the operation as

\[
\gamma:
\partial P_+\;\longrightarrow\;\partial P_-,
\qquad
\gamma \text{ orientation-reversing},
\tag{BoundaryGluing}
\]

where \(P_\pm\) are the two three-holed carriers. It is an operation **between
two carriers**, not a permutation of one six-germ ledger. That is what
separates it from \(\rho_h=\kappa_h\) of Section 2, which acts on the single
ledger \(P_h\) of one carrier, and from the cycle reversal 5.1, which acts on
one declared cyclic order.

Whether the gluing reversal \(\gamma\) is \(\rho_h\), or
\(V_{\mathrm{port}}(\mathcal J_h)\), or a third transport that no current
definition supplies, is a typing obligation. A shared six-cycle, a shared
count of six, or a shared drawing decides none of it; this is the same
prohibition that Section 3 applies between the WholeCut6 bridge and the
three-hole bridge.

The theorem of Section 2 supplies neither carrier nor gluing: it is a
statement about two matchings on one six-element set. Recording this
distinction here therefore constructs no gluing, admits no carrier, and adds
no filler. The label \(\gamma\) is a name for the obligation, not an
implemented operation.

---

## 6. Candidate typed J-lift of the M6 pair

Let

\[
\mathcal M_\pm
=
(P_\pm,S_\pm,E_\pm,D_{\kappa,\pm},D_{\tau,\pm},R_\pm)
\]

denote two fully typed M6 boundary carriers. A candidate J-lift is not merely
a bijection of six anonymous vertices. It consists of:

1. a total transport of port presentations;
2. a total transport of view-local state names;
3. a total transport of step occurrences and their origins;
4. preservation or explicitly declared reversal of coorientation;
5. preservation of source, occurrence, type, and multiplicity payloads;
6. transport of both length-three histories; and
7. a retained central residual \(\epsilon\).

Write

\[
\mathcal J:\mathcal M_+\longrightarrow\mathcal M_-.
\]

The proposed square is

\[
\mathcal J^2
=
\epsilon:
\mathcal M_+\longrightarrow\mathcal M_+,
\tag{JSquare}
\]

where the projective view forgets the central residual,

\[
V_{\mathrm{proj}}(\epsilon)=1,
\]

but a linear or phase-sensitive view reads

\[
V_{\mathrm{lin}}(\epsilon)=-I.
\]

This is the precise location where the same finite return can be identity in
one view and nontrivial in a finer history-bearing view.

The construction is presently a proof obligation. Neither the three-hole
matching theorem nor the AEG matrix calculation supplies the typed adapter
between their carriers.

---

## 7. From the central sign to a phase fibre

The exact projective lift supplies the discrete central distinction

\[
\{I,-I\}.
\]

Once a real complex structure \(J\) and a continuous parameter
\(\theta\) are admitted, it generates the circle action

\[
e^{\theta J}
=
\cos\theta\,I+\sin\theta\,J.
\tag{CircleAction}
\]

This is a mathematical \(SO(2)\cong U(1)\) action on the chosen real
two-plane. It is not yet program evolution. For that interpretation one still
needs:

- a declared complex or real-with-\(J\) state carrier;
- a norm, pairing, or other observable structure;
- a connection or transport rule;
- a continuous history parameter distinct from the domain role \(t\); and
- an infinitesimal generator.

Thus the current implication is only

\[
\text{projective involution with retained order-four lift}
\Longrightarrow
\text{candidate complex line and phase fibre}.
\]

It does not yet imply physical time.

---

## 8. Omega as a candidate inaccessible phase boundary

For a declared universal prefix-free machine \(U\), let

\[
\Omega_{\ell,b}
=
\sum_{\substack{|p|\leq\ell\\
U(p)\text{ halts within budget }b}}
2^{-|p|}.
\]

Each term is a computable rational and

\[
\Omega_{\ell,b}\nearrow\Omega_U,
\]

but there is no computable convergence modulus for a universal machine.

Given the chosen \(J\)-plane, a candidate finite phase is

\[
\omega_{\ell,b}
=
\exp(2\pi J\Omega_{\ell,b}).
\tag{FiniteOmegaPhase}
\]

Externally this converges to

\[
\omega_{\Omega}
=
\exp(2\pi J\Omega_U).
\]

The construction has three strict qualifications.

1. \(\Omega_U\) depends on the prefix-free machine and its code.
2. The exponential map does not make the limit internally computable.
3. No current rule identifies this phase with the filler of an M6 boundary.

The appropriate conjecture is instead a projective defect relation

\[
U_{\kappa\tau\kappa}
=
\omega_\Omega\,
U_{\tau\kappa\tau},
\tag{OmegaM6Candidate}
\]

or its finite approximants. This would close the endpoint only projectively
while retaining a phase defect. It requires a genuine \(U(1)\)-valued
two-cocycle on the relation complex, not an arbitrary phase label.

---

## 9. Energy and the seven relative halt worlds

The seven nonempty triadic relative halt worlds form the finite set

\[
H_7=
\mathcal P(\{K,X,t\})\setminus\{\varnothing\}.
\]

A complex amplitude carrier would be

\[
\mathcal H_7=\ell^2(H_7;\mathbb C).
\]

Suppose, as a separate declared hypothesis, that the seven worlds are
partitioned into two energy classes with projectors \(P_0,P_1\). Then

\[
P_0+P_1=I,
\qquad
H=E_0P_0+E_1P_1
\]

is the minimal two-level Hamiltonian. For a complex-linear realization, require
that (H) commute with the real complex structure (J); a unitary reading
would additionally require the appropriate self-adjointness and inner-product
data. Its candidate evolution is

\[
U(\zeta)
=
\exp\left(-\frac{JH\zeta}{\hbar}\right),
\tag{TwoLevelEvolution}
\]

where \(\zeta\) is a history parameter and not yet physical time.

Only the relative phase

\[
\exp\left(
-\frac{J(E_1-E_0)\zeta}{\hbar}
\right)
\]

can serve as a clock. If every admitted state is diagonal in the two energy
classes and there is no observable cross-level coherence, the phase is
invisible and no time coordinate has been obtained.

The present repository has not fixed the exact two-class partition or proved
its invariance under Q4/M6 transport. Both are prerequisites.

---

## 10. Relationship to the three residual fibres

Let the three residual fibres over the triadic roles be

\[
F_K,\qquad F_X,\qquad F_t.
\]

A cyclic connection has the form

\[
F_K
\xrightarrow{U_{KX}}
F_X
\xrightarrow{U_{Xt}}
F_t
\xrightarrow{U_{tK}}
F_K.
\]

Its monodromy is

\[
W=
U_{tK}U_{Xt}U_{KX}.
\]

The three-hole line supplies a candidate finite incidence carrier for this
cyclic connection. The J-lift supplies a candidate transverse phase
direction. A Hamiltonian interpretation would require

\[
WP_a
=
\exp\left(-\frac{JE_aT}{\hbar}\right)P_a,
\qquad a\in\{0,1\}.
\]

On this reading, the three fibres do not become three time dimensions. Their
cyclic transport produces one phase circle, and the universal cover of that
circle may provide one unwrapped history coordinate:

\[
\mathbb R\longrightarrow S^1.
\]

Calling that coordinate physical time requires further dynamical and
observational theorems.

---

## 11. Coherence obligations

The proposed bridge must pass the following independent checks.

### J0: six-germ formation

Every hole supplies two distinct typed germs and every germ occurs exactly
once in each matching.

### J1: connected matching

The hole and line pairings are disjoint and their union is connected. Failure
produces smaller even cycles or disconnected components rather than M6.

### J2: carrier adapter

The map from residual-hole germs to WholeCut6 ports or view-local states is
typed and retains complete source and occurrence data.

### J3: central residual

The second application of \(\mathcal J\) returns a named central residual
rather than silently identifying \(-I\) with \(I\) in every view.

### J4: Q4 naturality

Transport by \(\mathcal J\) preserves Q4 interchange boundaries or records an
explicit defect.

### J5: M6 naturality

Transport by \(\mathcal J\) maps both M6 boundary histories and does not
manufacture a filler.

### J6: TO24 cocycle closure

Any assigned M6 phase must satisfy the three-dimensional coherence equations
around the proposed TO24 envelope. A facewise phase assignment that fails
this check is not a global line bundle or connection.

### J7: energy invariance

The proposed two energy classes are preserved by the admitted Q4/M6
transports.

### J8: observable coherence

At least one admitted comparison of the two M6 histories detects a relative
phase. If all observables factor through classical endpoint probabilities,
the imaginary direction has no operational effect.

---

## 12. Falsification boundaries

The motivating conjecture is weakened or refuted if any of the following
holds.

1. The three residual holes do not expose one common six-germ ledger.
2. Every admissible line pairing is disconnected or repeats a hole edge.
3. The two oriented M6 presentations cannot be related without erasing source
   or occurrence identity.
4. The AEG left and right expansions have no common carrier on which the
   reciprocal \(J\)-lift acts.
5. The central sign is forced to be trivial in every admissible view.
6. The candidate J-transport violates Q4 or M6 typing.
7. The M6 phase fails TO24 cocycle closure.
8. The two-level halt-world partition is not transport invariant.
9. No observable retains cross-level or cross-history phase coherence.
10. The same finite effects are completely modeled by real signs, making a
    complex structure unnecessary.

A failure at a later stage does not invalidate the exact two-matching theorem
or the exact projective matrix calculation.

---

## 13. Status ledger

| statement | status |
|---|---|
| two disjoint connected perfect matchings on six vertices form an alternating \(C_6\) | exact finite theorem |
| \((\kappa_h,\tau_\pm)\) each form an M6 boundary | exact for the displayed six-germ fixture |
| \(\rho_h=\kappa_h\) is the unique label-preserving polarity reversal with \(\rho_h\tau_+\rho_h^{-1}=\tau_-\) | exact symbolic proof and exhaustive six-port audit |
| \(\mathcal M_6^{\mathrm{hp}}\) is the Three-Hole Polarity M6 Machine | nonprincipal M6-family member name |
| \(J:z\mapsto-1/z\) has \(J^2=-I\) in the linear lift and projective square \(1\) | exact linear/projective calculation |
| the AEG reciprocal lift is multiplication by \(i\) on \(\mathbb R^2\cong\mathbb C\) | exact after the displayed identification |
| the boundary-identification reversal \(\gamma\) of Section 5.5 is a fifth operation, distinct from \(\rho_h\) and from the cycle reversal | distinction recorded; no carrier, gluing or typed transport constructed |
| the two three-hole M6 carriers admit one typed \(\mathcal J\) with a retained central sign | construction target |
| the central sign extends to a program-relevant \(U(1)\) phase fibre | conjectural |
| the M6 defect is \(\exp(2\pi J\Omega_U)\) | conjectural and machine-dependent |
| the seven halt worlds carry a transport-invariant two-level Hamiltonian | separate hypothesis |
| the phase circle lifts to physical time | deferred physical interpretation |
| Q4/M6 jointly form a Teichmüller space | not established |

---

## 14. Narrow next theorem programme

The next theoretical work should remain finite.

1. Define a typed six-germ residual-hole fixture without adding stable syntax.
2. Exhibit the two explicit matchings and mechanically audit their alternating
   cycles.
3. Define a ledger-preserving candidate \(\mathcal J\) between the two
   carriers.
4. Compute \(\mathcal J^2\) and determine whether a central residual survives.
5. Check all Q4 faces and both M6 histories under \(\mathcal J\).
6. Formulate the TO24 phase product and test whether a nontrivial cocycle is
   possible.
7. Only then compare the resulting cocycle with finite
   \(\Omega_{\ell,b}\) phases and the two-level halt-world split.

No evaluator, floating-point numerical experiment, stable API, or physical
postulate is needed for the first five steps. The finite fixture now has an
exact executable permutation audit; its rational samples are supplementary.

---

## Conservative conclusion

The two exact observations fit together unusually tightly:

\[
\boxed{
\begin{aligned}
\text{three binary holes}
&+
\text{one complete connected threading}
\\
&\Longrightarrow
M_6^\partial,
\\[1mm]
z\mapsto-\frac1z
&\xleftarrow{\text{projectivize}}
J,\qquad J^2=-I.
\end{aligned}
}
\]

Their conjunction suggests, but does not yet prove, that the missing
three-hole line is a conjugate M6 direction governed by the same complex
structure already hidden in AEG's projective left/right switch.

The conceptual compression is:

\[
\boxed{
\text{projective involution}
=
\text{complex quarter-turn with its central sign forgotten}.
}
\]

If a typed J-lift exists and survives Q4/M6/TO24 coherence, the imaginary unit
is not an imported scalar decoration. It is the retained orientation of a
projective return in the history-bearing program carrier. Phase, energy, and
an unwrapped time coordinate then become legitimate next questions rather
than assumptions.
