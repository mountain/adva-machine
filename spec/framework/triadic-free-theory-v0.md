# Common interpretation, pressure and finite free: a conditional theory

Version 0, 2026-09-16. Status: **mathematical research specification**.
Direction: Mingli Yuan. Original formulation and proofs: ChatGPT (OpenAI),
contributed under Unknown v0.3 through Mingli Yuan's authorized account proxy;
account use is not his review or a correctness guarantee.

The problem is to connect the two [triadic readings](triadic-context-v0.md),
explain when a common interpretation exists, and determine when anchored
adjustment can justify a finite continuation. The propositions below answer
those questions for explicitly defined models. They do not assume a universal
translation of human meaning or a complete physical model of the open world.
The corresponding [finite checks](../../experiments/triadic_interpretation/README.md)
are calibration evidence; the proofs state the conditions beyond those cases.

## 1. How both triples can describe the same inquiry

The participant reading identifies relations `A--B`, `A--W`, and `B--W`, where
`W` is the shared object. The architectural reading identifies Surface,
Knowledge and Substrate duties. These are different classifications of one
process, not two enumerations whose matching positions establish an identity.

A concrete correspondence can label each recorded event with both:

```text
interaction role: one or more of A--B, A--W, B--W
realization duties: one or more of Surface, Knowledge, Substrate
```

For example, an observation can concern `A--W`, be acquired on a substrate,
be retained as evidence in knowledge, and be presented at a surface. A message
about that observation concerns `A--B`; it retains the observation's origin.
One event can involve several duties. Consequently a relation between these
classifications is sufficient; a bijection between their three labels is not
required. The particular labels still need a checked correspondence to the
actual records before they can authorize native use.

The historical naming layer is one documentary role assignment. It does not
prove that `W` is its knowledge record, that A must be a human, or that B must
be a machine. The proposed event classification permits both triples without
silently imposing any of those identities. It also leaves room for participants
to revise their concepts through further interactions with W.

## 2. A finite common interpretation and its obstruction

Fix an initial contract containing a nonempty finite question scope `Q`, a
finite family `K` of candidate interpretations, observation methods, guards,
comparison predicates and required evidence coverage. Candidates may use
partial or relational translations. Each candidate must declare its domain,
lost distinctions and residual, rather than silently equating representations.

For side `i` in `{A,B,W}`, let `H_i` contain exactly the candidates satisfying
that side's declared comparison for every required observation in Q. Here
`H_W` is computed from the applicable object-related observations and checks;
it is not a statement signed by the world. These predicates and their data are
assumptions of this finite model, open to later challenge. Required missing
evidence leaves the corresponding set **unknown**, not empty or universal.

**Proposition 1 (finite existence).** With complete coverage and terminating
comparison checks, a common interpretation in this declared family exists
exactly when `H = H_A intersect H_B intersect H_W` is nonempty. It can be
decided by checking at most `3*|K|` side predicates after their evidence has been
obtained; each predicate's internal work and recording costs must also be paid.

**Proof.** A member of H supplies a candidate and all three required predicate
witnesses. Conversely, any candidate with those witnesses belongs to each set
and hence H. Enumeration checks every candidate and retains either those
witnesses or a failed predicate for each excluded candidate. With missing
coverage it cannot claim this decision. The result concerns K and Q, not every
possible interpretation or every future observation.

This is a constructive finite acceptance criterion once the predicates have
been supplied. It does not solve how to discover the right predicates or
translate arbitrary prose into them.

**Obstruction 1: pairwise compatibility is insufficient.** On candidates
`{0,1,2}`, take `H_A={0,1}`, `H_B={1,2}`, `H_W={0,2}`. Every pair intersects,
but the triple intersection is empty. Three successful pairwise comparisons
therefore cannot replace the common witness. A/B agreement alone is weaker
still: `H_A=H_B={0}`, `H_W={1}` has unanimous participant agreement and no
admissible common interpretation. Relabeling the candidates bijectively
preserves these intersections and cannot remove either obstruction.

The constructive responses are to retain the obstruction, or propose a new
scope, candidate family or comparison justified by new evidence. Deleting an
object constraint to obtain agreement changes the question and requires a new
contract. Missing required evidence gives `Unknown`.

## 3. Anchors and internal pressure after a common scale is justified

A scalar energy only becomes meaningful after the compared quantities and
units have been related. To isolate that subsequent question, assume two
commensurate rational readings `a,b`, a fixed object observation `w`, soft
initial reference values `a0,b0`, and rational weights
`alpha,beta > 0`, `gamma,lambdaA,lambdaB >= 0`. Define

```text
E(a,b) = alpha*(a-w)^2 + beta*(b-w)^2 + gamma*(a-b)^2
         + lambdaA*(a-a0)^2 + lambdaB*(b-b0)^2

dA = alpha + gamma + lambdaA
dB = beta  + gamma + lambdaB
rA = alpha*w + lambdaA*a0
rB = beta*w  + lambdaB*b0
Delta = dA*dB - gamma^2
```

The pressure convention is minus the gradient of E. The fixed contract,
object scope and protected obligations remain hard constraints; the soft
references in this illustrative energy are not permission to relax them.

**Proposition 2 (unique conditional balance).** This model has exactly one
stationary point, which is its global minimum:

```text
a_star = (dB*rA + gamma*rB) / Delta
b_star = (gamma*rA + dA*rB) / Delta
```

**Proof.** Let `u=alpha+lambdaA > 0`, `v=beta+lambdaB > 0`.
Then `Delta = u*v + gamma*(u+v) > 0`. The gradient equations are the invertible
linear system `dA*a-gamma*b=rA`, `dB*b-gamma*a=rB`, giving the displayed solution.
For any displacement `(h,k)`, the energy difference from that stationary point
is `u*h^2 + v*k^2 + gamma*(h-k)^2`, strictly positive unless `h=k=0`.

With `lambdaA=lambdaB=0`, the unique minimum is `a=b=w`. Without any object
or anchor weights, `E=gamma*(a-b)^2` instead has every consensus as a minimum,
including false consensus about W. Object anchoring removes this degeneracy
only under the model's stipulated common scale and fixed observation.

**Obstruction 2: equilibrium need not license the claim.** Set all five
weights to 1, `w=0`, and `a0=b0=2`. The unique minimum is `a=b=1`, with `E=4`.
Both pressures vanish. If the task requires agreement with `w=0`, its
object-related obligation still fails. Positive energy at a constrained balance
can be legitimate, but a blocking discrepancy cannot be accepted merely
because the energy is stationary. This keeps energy minimization separate from
the acceptance predicate of free.

**Proposition 3 (convergence is not finite arrival).** Alternately minimize E
in a and then in b:

```text
a_next = (rA + gamma*b) / dA
b_next = (rB + gamma*a_next) / dB
b_next - b_star = rho*(b-b_star),   rho = gamma^2/(dA*dB) < 1
```

**Proof.** Subtract the stationary equations in the two update formulas and
substitute. Positivity of Delta gives `0 <= rho < 1`. The b error after n
full updates is `rho^n` times its initial error, so it converges to zero.
If `gamma>0` and that error is nonzero, it is nonzero at every finite n.

Thus a convergent pressure process may never meet an exact-equality stop rule
in finitely many iterations. This rational quadratic has a finite exact solver
given above. Other tasks need a justified finite method or an explicitly scoped
tolerance, with all hard obligations still checked. A tolerance cannot silently
replace a task that requires exact equality.

## 4. When a finite adjustment process actually reaches acceptance

Fix a finite set V of admissible states, start `s0`, allowed edges, and a
nonnegative integer potential Phi. The edges retain the initial contract,
history obligations and object context. Let F be the states satisfying the
task's complete acceptance conditions, including the object-related evidence,
required participant acceptance and permitted continuation. An energy minimum
is not the definition of F. Missing checks prevent membership being certified.

Form a directed graph D by keeping only strictly decreasing edges, and by
making states in F terminal. Assume all required checks and outgoing edges in
the declared scope are decidable and available.

**Proposition 4 (finite adjustment criterion).** Every maximal D-path from s0
ends in F if and only if every D-sink reachable from s0 belongs to F. Every
such path has at most `min(|V|-1, Phi(s0))` edges.

**Proof.** Strict decrease prevents repeated states and decreases the integer
potential by at least one per edge, proving both bounds. Every maximal path
therefore ends at a reachable sink. If all those sinks are in F, all paths
succeed. Conversely, a reachable sink outside F supplies a finite admissible
path ending without acceptance. That path is the counterexample.

The condition is stronger than the existence of one successful path and
weaker than requiring every state in V to be acceptable. It characterizes
arbitrary choices among the declared descending edges. A specified policy may
use its smaller reachable graph and requires its own check.

**Obstruction 3: a feasible solution may be inaccessible to descent.** Let
the allowed route be `x -> y -> z`, with potentials `1,2,0` and `F={z}`.
The accepting state exists and is reachable in the original graph, but strict
descent stops at x. An allowed barrier-crossing policy or revised potential
needs a separately justified contract; stationarity at x does not make x free.

For one declared additive work unit, let `c(v,u)` bound the work of deciding,
performing and recording an edge, and let `t(v)` bound terminal checking,
replay and durable recording. All must be actual upper bounds for the chosen
profile. The worst remaining work in this acyclic graph is computed backwards:

```text
R(v) = t(v)                         if v is terminal
R(v) = max(c(v,u) + R(u))           otherwise, over its outgoing edges
```

Induction on remaining path length proves that R is the largest path cost
under these declared costs. A budget at least `R(s0)`, plus any separately
bounded preflight cost, suffices for every path only when the graph and cost
assumptions hold. Smaller budgets may still allow a particular path but cannot
guarantee all of them. CPU time, memory and durable I/O require their own bounds;
they do not acquire a common additive unit by naming a reserve.

The `33/100` side shares and `1/100` joining reserve are an initial allocation
proposal. They must meet the profile's side and terminal cost bounds. A failed
join retains the prior committed head and all spent costs. Nothing in the
ratio proves that the required checking can be paid for.

## 5. Why the open world stays open

**Proposition 5 (finite observations cannot certify an unrestricted future).**
Suppose the admitted world family allows two response streams with the same
observed finite prefix but different next responses. A decision using only
that prefix cannot soundly certify one next response for every admitted world.

**Proof.** The input record to the decision is identical in both worlds, so
the decision is identical. Any definite next-response claim contradicted by
one of the two extensions is unsound for that world. A conditional prediction
requires an additional assumption excluding the counterextension; an unresolved
answer remains sound. The same argument applies after any finite prefix when
the admitted family allows arbitrary next extensions.

This is an information limitation under the stated family, not a proof that
all prediction is impossible. Laws, models and further observations can justify
narrower predictions, with their assumptions and tests retained. The restriction
fits the [freedom horizon](../../docs/philosophy/0004-long-run-freedom-witness.md):
the initial observer and interpretation stay open to counterevidence.

## 6. What is settled and what must be instantiated

Within this theory, both triadic readings can coexist through a task-relative
relation; complete finite comparison decides common interpretation in the
declared family; the quadratic model has the proved balance and convergence
conditions; and the finite descent criterion plus cost bounds decides when
every permitted adjustment path can support the requested continuation.
Pairwise agreement, consensus, zero pressure and a fixed reserve percentage
each have explicit counterexamples as substitutes for those conditions.

The remaining practical instantiation is to supply actual participants, object
observations, translation predicates, admissible transitions, acceptance checks
and measured cost bounds. This is not obtained from three labels or the model
proofs. Native communication and free remain unimplemented. No conclusion here
certifies a final interpretation of an unrestricted open universe.
