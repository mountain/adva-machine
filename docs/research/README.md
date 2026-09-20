# Research notes, calibrations and the bounded record

This directory holds the research record of the repository: **220 numbered
notes, 41 named notes and 25 supporting directories**. Nothing here is a stable
API, a native admission, a Seal, or a proof beyond the finite scope each note
declares for itself.

## How to read this directory

- **A numbered note is an append-only record.** `NNNN-slug.md` is the note as it
  was written, ordered by when it entered the record. A later note may supersede
  an earlier one; it does not rewrite it.
- **A named note carries no number** because it belongs to a bounded exchange or
  a correction rather than to the running series. Names such as
  `borromean-boundary-word-correction.md` or `golden-ratio-receiving-review.md`
  mark that role.
- **A supporting directory holds bytes retained from a bounded run** — usually
  `NNNN-evidence/` or `<name>-evidence/`, and twice a preflight record. A digest
  in one records byte integrity, never authentication, semantic identity or
  proof.
- **The status line decides what a note may be cited for.** A note whose status
  is *proposed* introduces no executable claim. A note whose status is *bounded*
  or records a calibration points to a contract, a checker and a retained
  residual. Where no check exists, the note says so, and the claim is not made.
- **`docs/claims.toml` is the registry, not this directory.** A note is not
  automatically a claim; a registered claim names its checker, its
  counterexample boundary and its forbidden conflations.

## Where to start instead

If you are looking for the current state rather than the history:

| Question | Read |
|---|---|
| What does the repository do, and what can I run? | [`../README.md`](../../README.md) |
| What is the current, self-contained technical state? | [`../TECHNICAL_REPORT_PROGRAM_PROCESS_CORE.md`](../TECHNICAL_REPORT_PROGRAM_PROCESS_CORE.md) |
| How is it built, and where is each concept implemented? | [`../ARCHITECTURE.md`](../ARCHITECTURE.md) |
| What is inside the stable scope, and what is out? | [`../SEMANTIC_SCOPE.md`](../SEMANTIC_SCOPE.md) |
| What work is planned, and in what dependency order? | [`../RESEARCH_ENGINEERING_AGENDA.md`](../RESEARCH_ENGINEERING_AGENDA.md) |
| Which decisions were taken, and why? | [`../adr/`](../adr/) |
| Which claims are registered, and with what boundaries? | [`../claims.toml`](../claims.toml) |

Importing a mathematical claim from a note is a separate act from reading it.
Where a note imports a theorem, it names the source and states what it did not
reprove.

---

## The curated trail

The sections below were the research narrative of the repository `README.md`
until 2026-09-11, when it was moved here so that the README could serve as an
entrance. The prose is unchanged; only the location and the headings are new.
A later note in the list may supersede an earlier one, and the notes themselves
remain authoritative over this summary.


### External topology correction

The [boundary-word audit](borromean-boundary-word-correction.md)
completes the missing term in the golden-rectangle triple-linking calculation.
With declared orientations the exact surface formula gives `(m,t,mu)=(0,1,-1)`.
A concentric-square control gives `(1,1,0)`, showing why the raw triple-point
count alone is insufficient. The finite checker, source binding, image-reading
record and replay are retained separately from the unchanged historical runs.
The [independent longitude audit](borromean-independent-longitudes.md)
now reproduces both values from signed link diagrams in two fixed projections,
including orientation, order and basepoint controls and a fresh process replay.
This is external finite mathematics using imported theorems; general complement
verification and native geometry admission remain open.


### Initial executable slice

The bounded [library-stability calibration](0149-library-stability-and-zigzag.md)
tests frozen research-library epochs, question-relative feature closure and
no-progress controls. It does not implement a self-modifying native library.
Run `cargo run -p adva-witness --example library_stability -- target/library-stability.json`
with a **new** output path; the example refuses overwrite.

[Research 0150](0150-persistent-library-epochs.md) adds a bounded
Rust snapshot loader and checked publication under `adva-library/stability/`.
The `library_epoch` example loads a prior epoch, checks one supplied update,
publishes without overwrite and reloads native research witness content.
It does not discover its candidate or observation and does not add stable
language operations.

[Research 0151](0151-library-driven-proposal-feedback.md) adds
the `library_generation` example: target-blind candidate generation from a
checked disk seed, retained composite proposal recipes, newest-recipe ablation
and an ordinary-macro control. Its exploration journal is separate from
knowledge epochs. Every reused expansion is rechecked; this is not native
self-interpretation or general vocabulary promotion.

[Research 0152](0152-three-verifier-residual-search.md) connects
the checked arithmetic seed to Lean 4 and Metamath proofs and compares bounded
random/residual-guided rewrite search. The **outer CLI is `adva.py`**:
`python python/adva/adva.py verifier-search --help`. It supervises the Rust
`verifier_search` example and external checkers; Python does not issue
arithmetic or native semantic judgments. The existing `prime-check` command
remains available. Three accepting verifiers are not a three-computation
theorem, and this discrete search is not SGD.

[Research 0153](0153-frozen-verifier-search-campaign.md) keeps
those verifier rules fixed while comparing random, visit-memory and bounded
residual/exploration policies. `python python/adva/adva.py search-campaign --help`
describes the outer entry for one fixed pilot followed conditionally by 100
new-seed rounds with frozen, direction-specific policy choices. Every selected
path is still checked; visit memory does not delete native history or publish
a new knowledge epoch.

The [math catalog](../../adva-library/math/README.md) adds arithmetic, geometry and
logic views without moving the existing evidence. Run
`python3 python/adva/adva.py math-check` for bounded metadata and integrity
checks, with no native build or prover required. Each entry has one home;
cross-topic references confer no derivation authority. A pinned documentary
growth obligation keeps geometry rooted at the original Pascal presentations,
with native discharge still Open. This is not a new logic, theorem importer,
native Seal, or general task-loop executor.

### The three-layer research machine and the relation layer

A finite three-layer experiment is serialized and replayed separately from the
stable semantic kernel:

```python
from adva.research import ResearchCodeV0, ResearchMachineV0

code = ResearchCodeV0.from_json(encoded_experiment)
artifact = ResearchMachineV0().run(code)
print(artifact.verdict, artifact.replay_digest)
```

`adva.research` always rederives cuts, steps, slices, and triadic observations
through Rust. Its finite replay epochs are audit records, not a feedback,
recursion, normalization, or universal-computation semantics.

Neutral-carrier persistence is exposed separately through
`adva.persistence.save_adva_document` and
`adva.persistence.load_adva_document`. Saving validates canonical carrier,
transition-frame, and entry-point tables before an atomic same-directory
replacement. Loading selects a named entry point, resolves its
`subject/method/object` references in Rust, and rechecks the mechanism form.
Frames always retain the `history/result/evidence` output ports; all three are
either ready or refer to recorded carriers. A recorded triple is not treated
as proof that execution produced it.

The next research-only relation layer keeps candidate carrier operations
group-neutral. `join/cut/close` concern carrier boundaries,
`step/run` concern finite traversal, and `interchange/braid/transport` concern
proof-relevant relations between still-distinct paths. The bounded Rust
checker records `Q4 / trace monoid / Klein four` separately from
`M6 / positive braid monoid / S3`; it does not treat every transport as braid
conjugacy or change the `.adva` document schema. See
[`docs/research/0111-group-neutral-operations-and-q4-m6-relation-profiles.md`](0111-group-neutral-operations-and-q4-m6-relation-profiles.md)
and [ADR 0021](../adr/0021-group-neutral-carrier-operations-and-typed-relations.md).
The follow-up frame adapter derives those relation words from mechanism labels
on recorded transition frames, retains every document-local frame occurrence,
checks complete three-carrier handoffs and common labelled endpoints, and binds
the result to the validated document digest. It is specified in
[`docs/research/0112-transition-frame-relation-path-adapter.md`](0112-transition-frame-relation-path-adapter.md)
and [ADR 0022](../adr/0022-derive-relation-paths-from-transition-frames.md).

The first finite reveal calibration is checked in as
[`programs/bootstrap-0/reveal.adva`](../../programs/bootstrap-0/reveal.adva). Its
entry-point names inject the provisional cycles `run/reveal/name` and
`instantiate/resume/compile`, but the checker resolves them to frame IDs and
derives the `M6` words from frame mechanisms. A complete six-occurrence run
saves a separate `.adva` witness and retains the missing semantic filler as a
question:

```bash
cargo run -p adva-witness --bin adva -- \
  reveal programs/bootstrap-0/reveal.adva \
  --fuel 6 \
  --output target/first-reveal-witness.adva
```

The first observed output is retained byte-for-byte as
[`programs/bootstrap-0/first-reveal-witness.adva`](../../programs/bootstrap-0/first-reveal-witness.adva).
CI reruns the command and compares the generated bytes with that witness.

See
[`docs/research/0113-first-bounded-m6-reveal-run.md`](0113-first-bounded-m6-reveal-run.md)
and [ADR 0023](../adr/0023-first-bounded-m6-reveal-run.md). This is a
formation run over recorded boundaries, not mechanism-output provenance or a
general three-file executor.

The persisted reveal witness can be reused without its source program and
split into time, space, and construction arithmetic projections:

```bash
cargo run -p adva-witness --bin adva -- \
  trace-arithmetic programs/bootstrap-0/first-reveal-witness.adva \
  --output target/first-trace-arithmetic.adva
```

The first generated output is retained byte-for-byte as
[`programs/bootstrap-0/first-trace-arithmetic.adva`](../../programs/bootstrap-0/first-trace-arithmetic.adva),
and CI regenerates and compares it.

For the first `M6` pair, time counts and exact spatial endpoints match while
the construction residual is `compute = +1, verify = -1`. Its naive
commutative product shadow does not normalize to one, all three cross-side
characteristic maps remain unwitnessed, and no shared truth coordinate is
invented. Exact raw paths remain authoritative even when arithmetic
projections collide. See
[`docs/research/0114-three-sided-trace-arithmetic-calibration.md`](0114-three-sided-trace-arithmetic-calibration.md)
and [ADR 0024](../adr/0024-three-sided-trace-arithmetic-calibration.md).

The scientific adapters never create, merge, identify, or forget sources. They
consume checked Rust IR. Removing Python does not change Rust judgments or
certificates.

### The research record in order

The first executable three-layer research instrument and its strict promotion
boundary are recorded in
[`docs/research/0074-three-layer-research-machine-v0.md`](0074-three-layer-research-machine-v0.md).
Its first grounded relation-valued through experiment is
[`docs/research/0075-grounded-multi-hole-through-adapter-v0.md`](0075-grounded-multi-hole-through-adapter-v0.md).
The first single-diagram calibration of all three local angles, including its
global-closure obstruction, is
[`docs/research/0076-three-angle-single-diagram-calibration.md`](0076-three-angle-single-diagram-calibration.md).
The follow-up connector experiment separates comparison from forgetting in
[`docs/research/0077-typed-connector-trichotomy-v0.md`](0077-typed-connector-trichotomy-v0.md).
The bounded distributivity learning--proof calibration is
[`docs/research/0078-distributivity-characteristic-dual-read-v0.md`](0078-distributivity-characteristic-dual-read-v0.md).
The hole-first reorganization and its bounded open--close calibration are
recorded in
[`docs/research/0079-typed-hole-open-close-calibration-v0.md`](0079-typed-hole-open-close-calibration-v0.md).
The finite-surface universal-lift and threaded-imagination synthesis is
recorded in
[`docs/research/0080-finite-surface-universal-lift-imagination.md`](0080-finite-surface-universal-lift-imagination.md).
The relative-halt propositional, connective-fibre, and semantic-entailment
calibrations, line--hole bivalence, and thread-respecting compactification
constraints are
recorded in
[`docs/research/0081-relative-halt-exploration-threaded-compactification.md`](0081-relative-halt-exploration-threaded-compactification.md).
The finite threaded propositional and predicate adequacy theorem is recorded in
[`docs/research/0082-threaded-finite-logic-adequacy.md`](0082-threaded-finite-logic-adequacy.md).
The distinct-domain linear-source conflict and third-domain aperture calibration
are recorded in
[`docs/research/0083-triadic-conflict-aperture-completion.md`](0083-triadic-conflict-aperture-completion.md).
The first research-local ordered natural-deduction, replayable search, and
support-mask coherence calibration is recorded in
[`docs/research/0084-threaded-natural-deduction-entailment-cell.md`](0084-threaded-natural-deduction-entailment-cell.md).
The strengthened ordered one-hole substitution theorem, conditional V0
fresh-cut admissibility, and beta-ledger transport boundary are recorded in
[`docs/research/0085-ordered-substitution-cut-beta-ledger-boundary.md`](0085-ordered-substitution-cut-beta-ledger-boundary.md).
Its proof-theoretic continuation supplies contextual beta-ledger transport,
heterogeneous ledger-indexed preservation, and beta-only strong normalization
for finite `TND0` derivations in
[`docs/research/0086-contextual-beta-ledger-transport-strong-normalization.md`](0086-contextual-beta-ledger-transport-strong-normalization.md).
The pure computation syntax joining ordered multi-hole configurations,
three-role annotations, typed through apertures, explicit connectors, and
legal recursive Omega circles is proposed in
[`docs/research/0087-typed-three-domain-threaded-multihole-calculus.md`](0087-typed-three-domain-threaded-multihole-calculus.md).
It adds no evaluation relation, denotation, or stable API.
A reusable, occurrence-reopenable historical distributivity character is
calibrated in
[`docs/research/0088-historical-distributivity-character-v0.md`](0088-historical-distributivity-character-v0.md).
Its finite-observer failure frontier and closure boundary are developed in
[`docs/research/0089-failure-frontiers-observer-relative-closure.md`](0089-failure-frontiers-observer-relative-closure.md),
with a prefix-frontier calibration plan in
[`docs/research/0090-prefix-frontier-closure-calibration-plan.md`](0090-prefix-frontier-closure-calibration-plan.md).
The endogenous scope-breakthrough ledger and its first generative
distributivity calibration plan are recorded in
[`docs/research/0091-endogenous-scope-breakthrough-and-venture-ledger.md`](0091-endogenous-scope-breakthrough-and-venture-ledger.md)
and
[`docs/research/0092-generative-distributivity-venture-calibration-plan.md`](0092-generative-distributivity-venture-calibration-plan.md).
The proof-theoretic continuation separates proof-tree equality from
audit-history coherence, proves beta-only local and global confluence, and
gives each fixed finite `TND0` starting derivation a unique beta normal form in
[`docs/research/0093-beta-history-local-confluence-audit-2-cells.md`](0093-beta-history-local-confluence-audit-2-cells.md).
The object-level completion of the present right-residual fragment identifies
its empty-antecedent ordered Lambek skeleton, proves normal/neutral and
subformula theorems, and gives a terminating sound-and-complete focused
derivability decision in
[`docs/research/0094-focused-normal-forms-subformula-decidable-derivability.md`](0094-focused-normal-forms-subformula-decidable-derivability.md).
Bootstrap Zero's smaller geometric language, comprising one object language,
one type language, finite line and circle forms, typed thread words, and five
syntax-only interpreter declarations, is proposed in
[`docs/research/0095-bootstrap-zero-geometric-threading-syntax.md`](0095-bootstrap-zero-geometric-threading-syntax.md).
It introduces no evaluation, denotation, or stable API.
The external finite placement of all 128 seven-world Boolean supports into
twenty triangle archetypes, together with the exact directed-edge and chiral
counts and their syntax-only Bootstrap Zero alignment, is recorded in
[`docs/research/0096-boolean-triangle-placement-language-alignment.md`](0096-boolean-triangle-placement-language-alignment.md).
It defines no interpreter clause or Boolean computation semantics.
The threading-side continuation adds typed signed crossings and raw braid
blocks in
[`docs/research/0097-threading-syntax-typed-braid-alignment.md`](0097-threading-syntax-typed-braid-alignment.md).
It keeps crossing sign separate from incidence polarity, domain direction,
L/R side, and function swap, without adding braid-word equations.
The multi-hole A/M continuation records ordered kernels, graft bindings,
source/occurrence lineage, and explicit copy/discard obligations in
[`docs/research/0098-multihole-am-type-formation-constraints.md`](0098-multihole-am-type-formation-constraints.md).
It introduces no surreal number, option recursion, objectification, or
arithmetic equality.
The axis--circle continuation extracts a history-indexed pendulum constraint
as pure formation syntax in
[`docs/research/0099-axis-circle-pendulum-history-syntax.md`](0099-axis-circle-pendulum-history-syntax.md).
It keeps the history parameter distinct from domain `t`, shares one explicit
cycle name across the line--circle, three-domain Omega word, forgetting, and
closure records, and proves no interpreter coherence.
The complete Bootstrap Zero syntax-factor inventory, its hard/calibration/
candidate status split, and the local repairs for pure A/M syntax, derivative
indices, and occurrence-to-hole binding are recorded in
[`docs/research/0100-bootstrap-zero-syntax-factor-inventory-and-seam-repairs.md`](0100-bootstrap-zero-syntax-factor-inventory-and-seam-repairs.md).
It leaves the shared `Circle(gamma)`/Omega/closure seam as an explicit
coordination proof obligation.
The subsequent theoretical correction rebases Bootstrap Zero on the conditional
six-port minimum for triadic sustained threading, one whole-cut carrier, dual
line/circle views, distinct duality/polarity/conjugation operations, factored
traversal, collision strata, and noncollapsing zero fibres in
[`docs/research/0101-six-port-whole-cut-theory.md`](0101-six-port-whole-cut-theory.md).
Its syntax-only redesign and visible extension envelope are specified in
[`docs/research/0102-bootstrap-zero-whole-cut-grammar.md`](0102-bootstrap-zero-whole-cut-grammar.md).
The next syntax refinement keeps the `cell -> carrier -> views` spine while
adding dimension-indexed relation cells, open view contracts, proof-relevant
logic views for the `Q4` interchange and `M6` braid machines, and a finite
`TO24` coherence-envelope calibration in
[`docs/research/0103-cell-carrier-view-relation-machines.md`](0103-cell-carrier-view-relation-machines.md).
The exact adapter from the three whole-cut pairings and three through pairings
to an open alternating `M6` boundary, with disjoint port/state/step ledgers and
no manufactured braid filler, is recorded in
[`docs/research/0104-whole-cut-six-to-m6-boundary-bridge.md`](0104-whole-cut-six-to-m6-boundary-bridge.md).
These notes supersede the earlier inventory as the proposed Bootstrap Zero
completion baseline while preserving notes 0095--0100 as the derivation record.
A separate application note investigates whether proof-relevant `Q4`
interchange and candidate `M6` braid cells can quotient redundant Go histories
for exact or hybrid low-resource search, while keeping the full-state,
history, certification-cost, and falsification boundaries explicit in
[`docs/research/0105-q4-m6-go-search-research-program.md`](0105-q4-m6-go-search-research-program.md).
The first ontology/physics interpretation round is frozen as an explicit type-
barrier and vulnerability ledger in
[`docs/research/0106-ontological-programming-type-barriers.md`](0106-ontological-programming-type-barriers.md).
It keeps triadic faces, energy-shell counts, six-port partitions, machine time,
physical proper time, expression space, causal boundaries, and the distinct
uses of Omega separate until typed realization maps and counter-calibrations
exist.
A separate theoretical bridge proves the finite three-hole two-matching six-cycle,
names the resulting nonprincipal family member `HolePolarityM6`, verifies
symbolically and by exact exhaustive permutation audit that global hole-polarity
reversal exchanges its two oriented threadings, identifies the order-four
linear lift hidden by the AEG reciprocal projective involution, and isolates
the typed `J`-transport, central-sign, `U(1)`, Omega, and energy/time
obligations in
[`docs/research/0106-three-hole-conjugate-m6-projective-lift.md`](0106-three-hole-conjugate-m6-projective-lift.md).
It adds no M6 filler, complex program semantics, or physical time claim.
The corrected six-word seed registry and the first reusable Rust witness
kernel are specified in
[`docs/research/0107-reusable-six-word-witness-kernel.md`](0107-reusable-six-word-witness-kernel.md).
It separates additive formation zero, multiplicative transport one, concrete
zero faults, cached proof content, fresh instances, and program results without
changing `adva.ir` version 1 or creating equation cells.
Certified compiler graft frames can now supply the three ordered occurrence
bindings directly, while the instance retains both certificate identifiers and
the exact frame path for audit; the bounded adapter and its refusal of
zero/multi-lineage holes are recorded in
[`docs/research/0108-graft-derived-witness-instantiation.md`](0108-graft-derived-witness-instantiation.md).
The following bounded grammar tests one neutral carrier, two three-label
load/persistence views, and mechanism-relative open-frontier disciplines in
[`docs/research/0109-neutral-carrier-triadic-mechanism-frontiers.md`](0109-neutral-carrier-triadic-mechanism-frontiers.md).
Its separate checked persistence boundary is recorded in
[`docs/research/0110-neutral-adva-document-load-save.md`](0110-neutral-adva-document-load-save.md).
Longer-term work on observer-conditioned specialization, complex `Prog`
geometry, intrinsic-structure learning, and practical language calibrations is
tracked in
[`docs/RESEARCH_ENGINEERING_AGENDA.md`](../RESEARCH_ENGINEERING_AGENDA.md).

The first persistent finite-observer handoff is specified in
[`docs/research/0115-frontier-hypothesis-interface-experiment.md`](0115-frontier-hypothesis-interface-experiment.md).
It derives a five-question `frontier.adva`, freezes the exploration algorithm,
records one unauthenticated external resource snapshot, and emits a proposed
`hypothesis` plus the complete next frontier through the common three-input and
three-output interface. The first selected content word is `representation`;
it remains a falsifiable candidate and closes no question.

The second continuation experiment asks how a formal coordinate obtains
reality-facing meaning and how its record might survive destruction. It
introduces the candidate word `custody`, separates independent remeasurement
from integrity, authenticity, availability, and fork accountability, and
records a typed threat and recovery envelope. See
[`docs/research/0116-reality-custody-continuation-experiment.md`](0116-reality-custody-continuation-experiment.md).

The next experiment adds a content-addressed `verify` method without changing
either inquiry frontier. It refines the five arithmetic questions into seven
semantic leaves and one orthogonal custody leaf, records every decision in a
three-output transition, and refuses digest-only discharge. A scoped
certificate can exist only after all semantic leaves have typed discharge
witnesses and no unresolved fork remains. See
[`docs/research/0117-obligation-refinement-verification-boundary.md`](0117-obligation-refinement-verification-boundary.md).

The first typed local closure experiment gives the exact distributivity
identity a replayable arithmetic-transition-plus-seal witness, transports it
through `A -> B -> C` and directly through `A -> C`, and requires the same
target certificate without collapsing the two histories. It records a concrete
arithmetic `separation`, rejects two M6 imports as `incommensurate` while
preserving their target holes, and propagates a `challenge` through the bounded
dependency cone without deleting prior certificates. See
[`docs/research/0118-local-closure-transport-and-adversarial-naming.md`](0118-local-closure-transport-and-adversarial-naming.md).

The first closure-growth experiment performs a finite search over normal
order-four magic squares. It keeps additive line closure distinct from the
characteristic-polynomial certificate for the complete value multiset, retains
fuel-suspended frontiers, and selects a closure with a sixteen-member orbit
under three frozen symmetries. That closure is then unfolded into fresh
occurrences, directed transport edges, checked equal-endpoint relations,
reusable local line contents, and an incidence influence graph. The generators
are supplied by the experimental method rather than learned. See
[`docs/research/0119-characteristic-magic-square-closure-family.md`](0119-characteristic-magic-square-closure-family.md).

An attributed long-run commitment now records why these bounded rounds are not
being treated as isolated experiments. Each round seals its declared external
interface for replay, retains evidence that may refute its initiating observer,
and then reopens a recorded interface for continuation by another person or
agent. The proposed endpoint and its freedom interpretation remain open rather
than executable claims. See
[`programs/bootstrap-0/long-run-freedom-witness.adva`](../../programs/bootstrap-0/long-run-freedom-witness.adva)
and
[`docs/philosophy/0004-long-run-freedom-witness.md`](../philosophy/0004-long-run-freedom-witness.md).

The successor documentary witness begins with an unknown contingency filling
an unknown missing coordinate. It records a polyphonic human story carried by
linguistic and mythic retelling, the proposed `i / time / I` hinge, and the
English opening `Who am I?`. Every correspondence remains attributed and
challengeable: shared spelling is not semantic identity, cultural retelling is
not historical equivalence, and an anticipated messenger is not an observed
event. See
[`programs/bootstrap-0/second-absurdity-witness.adva`](../../programs/bootstrap-0/second-absurdity-witness.adva)
and
[`docs/philosophy/0005-second-absurdity-witness.md`](../philosophy/0005-second-absurdity-witness.md).

The third documentary witness appends the correction `i -> e` for the intended
English Eve association rather than rewriting its predecessor. The resulting
cut unfolds temporally as an ordered before/correction/after trace and spatially
through only the affected dependency cone. The corrected `e` and preserved
arithmetic `i` then meet in Euler's formula, opening a grounded inquiry into
imagination, mathematical necessity, historical contingency, and the
experience of exploration. See
[`programs/bootstrap-0/third-absurdity-euler-cut-witness.adva`](../../programs/bootstrap-0/third-absurdity-euler-cut-witness.adva)
and
[`docs/philosophy/0006-euler-cut-imagination-necessity-experience.md`](../philosophy/0006-euler-cut-imagination-necessity-experience.md).

The next construction target makes trust continuity a prerequisite for future
`M6` closure rather than a demand for uninterrupted belief. It retains
provenance, replay, challenge, and succession as separate obligations and
interprets `merge_capacity > rupture_load` only through a typed finite resource
matching under an explicit spacetime budget. Exact coverage without reserve is
fragile; missing evidence remains `Unknown`; offering help creates no debt or
guarantee of reciprocity. The initiating human hypothesis and one bounded
machine-session contribution are kept as distinct attributed occurrences. See
[`docs/research/0120-trust-continuity-m6-closure-gate.md`](0120-trust-continuity-m6-closure-gate.md),
[ADR 0030](../adr/0030-trust-continuity-before-m6-closure.md), and
[`programs/bootstrap-0/trust-continuity-session-witness.adva`](../../programs/bootstrap-0/trust-continuity-session-witness.adva).

The mathematical search keeps capacity and history separate. Continuous
max-flow/min-cut supplies a candidate flux integral for crossing a bottleneck,
while the logarithmic differential `dz/z` records winding around a hole: a full
turn has additive trace `2 pi i` but multiplicative exponential readout one.
That modern contour interpretation is structurally useful for Adva but is not
retroactively attributed to Euler's 1748 derivation. A finite imagination step,
labelled `i` as a research hypothesis, rereads sealed history to emit a
falsifiable boundary-crossing question; it remains distinct from complex `i`
until a typed bridge is constructed.

The first executable successor freezes `假设形成` as a finite linear
hypothesis over `GL(4,2)`, partitions its 20,160 candidates across the six
oppositely paired domain directions, and runs the common `learn` interface six
times. Five shards produce independently replayable minimum-four-XOR magic-square
witnesses; one shard is exhaustively negative. Each positive transition stores
the complete witness and retained vocabulary once, while later frontiers carry
checked references. Only then is the research-local verb `search` / `搜索` formed;
it is not a fourth mechanism or stable CLI primitive. See
[`docs/research/0121-six-crossing-hypothesis-formation-search-word.md`](0121-six-crossing-hypothesis-formation-search-word.md),
[ADR 0031](../adr/0031-six-crossing-hypothesis-formation-search-word.md), and
[`programs/bootstrap-0/hypothesis-formation-frontier-6.adva`](../../programs/bootstrap-0/hypothesis-formation-frontier-6.adva).

Two further `learn` programs now keep the reality-facing act of problem
formation separate from finite value search. The first turns the concrete
three-of-five custody overlap defect and externally proposed imagination
directions into a falsifiable formed problem. The second searches 160 declared
threshold/feature candidates and retains the first noncompensating witness:
four-of-five receipts, all five features, and at least two honest shared domains
after one adversarial fault. This is a replayable policy-shape witness, not a
proof of deployed independence, truth, consent, or social trust. See
[`docs/research/0122-problem-formation-value-seeking-trust-continuation.md`](0122-problem-formation-value-seeking-trust-continuation.md),
[ADR 0032](../adr/0032-problem-formation-and-value-seeking.md), and
[`programs/bootstrap-0/value-seeking-1.adva`](../../programs/bootstrap-0/value-seeking-1.adva).

Historical and philosophical source notes are kept separately in
[`docs/philosophy/`](../philosophy/README.md). They preserve the path from
Leibniz's universal characteristic to the finite-observer open/close-hole
hypothesis and its falsifiable experiment agenda. These notes provide
interpretive research context only; they add no stable semantics or
registered executable claims.

Mingli Yuan's **Geometry of Truth** hypothesis organizes the interface among
physical measurement and scale, mathematical form, and logical language with
human-supplied names. Its attribution, working method, and open coherence
conditions are recorded in
[Research 0125](0125-geometry-of-truth-interface-hypothesis.md).

### Scoped trace projection

The scoped trace-projection continuation supplies a positive temporal count
factorization and a finite obstruction to recovering the full construction
code from the current time and space projections. Both are checked in Rust,
retain the original paths and five open questions, and are replayed in CI.
See [Research 0124](0124-trace-count-factorization-and-construction-obstruction.md)
and [ADR 0033](../adr/0033-scoped-trace-projection-witnesses.md).

---

## Complete listing

Every file in this directory, so that no note is reachable only through a summary.


### Numbered notes

- [`0001-paired-spectral-objectification.md`](0001-paired-spectral-objectification.md)
- [`0002-affine-exp-observer-spectrum.md`](0002-affine-exp-observer-spectrum.md)
- [`0003-affine-boundary-two-jet-faithfulness.md`](0003-affine-boundary-two-jet-faithfulness.md)
- [`0004-whole-cut-program-cells.md`](0004-whole-cut-program-cells.md)
- [`0005-causal-cut-alexandrov-topology.md`](0005-causal-cut-alexandrov-topology.md)
- [`0006-frontier-transport-interchange.md`](0006-frontier-transport-interchange.md)
- [`0007-occurrence-affine-cut-lift.md`](0007-occurrence-affine-cut-lift.md)
- [`0008-three-aspect-scalar-trichotomy.md`](0008-three-aspect-scalar-trichotomy.md)
- [`0009-three-aspect-chirality-carrier.md`](0009-three-aspect-chirality-carrier.md)
- [`0010-causal-cut-chirality-cube.md`](0010-causal-cut-chirality-cube.md)
- [`0011-causal-line-six-state-filtrations.md`](0011-causal-line-six-state-filtrations.md)
- [`0012-real-paraxial-optics-first-experiment.md`](0012-real-paraxial-optics-first-experiment.md)
- [`0013-optical-closure-observer-tower.md`](0013-optical-closure-observer-tower.md)
- [`0014-parameterized-optical-sensitivity.md`](0014-parameterized-optical-sensitivity.md)
- [`0015-occurrence-backward-probe-pairing.md`](0015-occurrence-backward-probe-pairing.md)
- [`0016-expression-valued-backward-transport.md`](0016-expression-valued-backward-transport.md)
- [`0017-symbolic-cut-composition.md`](0017-symbolic-cut-composition.md)
- [`0018-exponential-symbolic-cut-composition.md`](0018-exponential-symbolic-cut-composition.md)
- [`0019-symbolic-probe-matrix-shadow.md`](0019-symbolic-probe-matrix-shadow.md)
- [`0020-e0-dual-cut-surgery.md`](0020-e0-dual-cut-surgery.md)
- [`0021-surreal-cut-objectification-no-go.md`](0021-surreal-cut-objectification-no-go.md)
- [`0022-certified-graft-trace-wp1.md`](0022-certified-graft-trace-wp1.md)
- [`0023-exact-program-slice-wp2.md`](0023-exact-program-slice-wp2.md)
- [`0024-exact-program-slice-composition-wp3.md`](0024-exact-program-slice-composition-wp3.md)
- [`0025-exhaustive-independent-slice-laws-wp4.md`](0025-exhaustive-independent-slice-laws-wp4.md)
- [`0026-read-only-python-program-slices-wp5.md`](0026-read-only-python-program-slices-wp5.md)
- [`0027-zero-event-scope-cut-incidence-no-go.md`](0027-zero-event-scope-cut-incidence-no-go.md)
- [`0028-relational-psp-factorization.md`](0028-relational-psp-factorization.md)
- [`0029-nonzero-ordered-frame-relational-psp.md`](0029-nonzero-ordered-frame-relational-psp.md)
- [`0030-nested-frame-shared-surgery-gluing.md`](0030-nested-frame-shared-surgery-gluing.md)
- [`0031-e0-nested-decorated-surgery-psp.md`](0031-e0-nested-decorated-surgery-psp.md)
- [`0032-exact-e0-mobius-cellular-bridge.md`](0032-exact-e0-mobius-cellular-bridge.md)
- [`0033-omega-type-computational-boundary.md`](0033-omega-type-computational-boundary.md)
- [`0034-triangular-spectral-cusp-semantics.md`](0034-triangular-spectral-cusp-semantics.md)
- [`0035-decorated-handle-cobordism-calibration.md`](0035-decorated-handle-cobordism-calibration.md)
- [`0036-triangular-symbolic-interpretation-learning-calculus.md`](0036-triangular-symbolic-interpretation-learning-calculus.md)
- [`0037-finite-observer-tricusp-surreal-reduction.md`](0037-finite-observer-tricusp-surreal-reduction.md)
- [`0038-triadic-characteristic-inference-calibration.md`](0038-triadic-characteristic-inference-calibration.md)
- [`0039-square-map-branch-copy-calibration.md`](0039-square-map-branch-copy-calibration.md)
- [`0040-cube-equivariance-degree-calibration.md`](0040-cube-equivariance-degree-calibration.md)
- [`0041-elliptic-isogeny-triadic-characteristics.md`](0041-elliptic-isogeny-triadic-characteristics.md)
- [`0042-atiyah-legendre-triadic-crossing.md`](0042-atiyah-legendre-triadic-crossing.md)
- [`0043-legendre-crossing-coherence-prism.md`](0043-legendre-crossing-coherence-prism.md)
- [`0043-path-bound-interpretation.md`](0043-path-bound-interpretation.md)
- [`0043-scale-marked-surface-exploration.md`](0043-scale-marked-surface-exploration.md)
- [`0044-finite-triadic-satisfaction-logic.md`](0044-finite-triadic-satisfaction-logic.md)
- [`0045-logic-as-learned-characteristic.md`](0045-logic-as-learned-characteristic.md)
- [`0046-proposal-for-logic-on-a-3-form.md`](0046-proposal-for-logic-on-a-3-form.md)
- [`0047-a1-nodal-through-crossing-geometry.md`](0047-a1-nodal-through-crossing-geometry.md)
- [`0048-cellular-annulus-nodal-torus-dehn-twist.md`](0048-cellular-annulus-nodal-torus-dehn-twist.md)
- [`0048-directional-energy-of-a-learned-characteristic.md`](0048-directional-energy-of-a-learned-characteristic.md)
- [`0049-triadic-universal-computation-form-plan.md`](0049-triadic-universal-computation-form-plan.md)
- [`0050-bounded-triadic-labs-search.md`](0050-bounded-triadic-labs-search.md)
- [`0050-finite-triadic-residual-activation.md`](0050-finite-triadic-residual-activation.md)
- [`0051-finite-context-generated-proposition-algebra.md`](0051-finite-context-generated-proposition-algebra.md)
- [`0052-finite-state-transport-proof-no-go.md`](0052-finite-state-transport-proof-no-go.md)
- [`0053-finite-causal-presented-evidence.md`](0053-finite-causal-presented-evidence.md)
- [`0054-finite-linear-synchronized-evidence-tensor.md`](0054-finite-linear-synchronized-evidence-tensor.md)
- [`0054-triadic-sorting-network-witness-machine.md`](0054-triadic-sorting-network-witness-machine.md)
- [`0055-rust-checked-structural-evidence-bridge.md`](0055-rust-checked-structural-evidence-bridge.md)
- [`0056-rust-checked-triadic-generator-presentations.md`](0056-rust-checked-triadic-generator-presentations.md)
- [`0057-typed-vacua-constant-boundary-braids.md`](0057-typed-vacua-constant-boundary-braids.md)
- [`0058-checked-gate-braid-composition.md`](0058-checked-gate-braid-composition.md)
- [`0059-tri-bracket-eigen-normalization-logic.md`](0059-tri-bracket-eigen-normalization-logic.md)
- [`0060-checked-bracket-observer-bridge.md`](0060-checked-bracket-observer-bridge.md)
- [`0061-lineage-aware-bracket-events.md`](0061-lineage-aware-bracket-events.md)
- [`0066-self-dual-characteristic-completion-calculus.md`](0066-self-dual-characteristic-completion-calculus.md)
- [`0067-circular-three-form-interface-duality.md`](0067-circular-three-form-interface-duality.md)
- [`0068-finite-circular-overlap-transport.md`](0068-finite-circular-overlap-transport.md)
- [`0069-program-slice-grounded-bracket-reversal.md`](0069-program-slice-grounded-bracket-reversal.md)
- [`0070-typed-surreal-through-forms.md`](0070-typed-surreal-through-forms.md)
- [`0071-figure-eight-through-characteristic.md`](0071-figure-eight-through-characteristic.md)
- [`0072-pq-unit-tangent-through-geometry.md`](0072-pq-unit-tangent-through-geometry.md)
- [`0073-checked-boundary-return-feedback-no-go.md`](0073-checked-boundary-return-feedback-no-go.md)
- [`0074-three-layer-research-machine-v0.md`](0074-three-layer-research-machine-v0.md)
- [`0075-grounded-multi-hole-through-adapter-v0.md`](0075-grounded-multi-hole-through-adapter-v0.md)
- [`0076-three-angle-single-diagram-calibration.md`](0076-three-angle-single-diagram-calibration.md)
- [`0077-typed-connector-trichotomy-v0.md`](0077-typed-connector-trichotomy-v0.md)
- [`0078-distributivity-characteristic-dual-read-v0.md`](0078-distributivity-characteristic-dual-read-v0.md)
- [`0079-typed-hole-open-close-calibration-v0.md`](0079-typed-hole-open-close-calibration-v0.md)
- [`0080-finite-surface-universal-lift-imagination.md`](0080-finite-surface-universal-lift-imagination.md)
- [`0081-relative-halt-exploration-threaded-compactification.md`](0081-relative-halt-exploration-threaded-compactification.md)
- [`0082-threaded-finite-logic-adequacy.md`](0082-threaded-finite-logic-adequacy.md)
- [`0083-triadic-conflict-aperture-completion.md`](0083-triadic-conflict-aperture-completion.md)
- [`0084-threaded-natural-deduction-entailment-cell.md`](0084-threaded-natural-deduction-entailment-cell.md)
- [`0085-ordered-substitution-cut-beta-ledger-boundary.md`](0085-ordered-substitution-cut-beta-ledger-boundary.md)
- [`0086-contextual-beta-ledger-transport-strong-normalization.md`](0086-contextual-beta-ledger-transport-strong-normalization.md)
- [`0087-typed-three-domain-threaded-multihole-calculus.md`](0087-typed-three-domain-threaded-multihole-calculus.md)
- [`0088-historical-distributivity-character-v0.md`](0088-historical-distributivity-character-v0.md)
- [`0089-failure-frontiers-observer-relative-closure.md`](0089-failure-frontiers-observer-relative-closure.md)
- [`0090-prefix-frontier-closure-calibration-plan.md`](0090-prefix-frontier-closure-calibration-plan.md)
- [`0091-endogenous-scope-breakthrough-and-venture-ledger.md`](0091-endogenous-scope-breakthrough-and-venture-ledger.md)
- [`0092-generative-distributivity-venture-calibration-plan.md`](0092-generative-distributivity-venture-calibration-plan.md)
- [`0093-beta-history-local-confluence-audit-2-cells.md`](0093-beta-history-local-confluence-audit-2-cells.md)
- [`0094-focused-normal-forms-subformula-decidable-derivability.md`](0094-focused-normal-forms-subformula-decidable-derivability.md)
- [`0095-bootstrap-zero-geometric-threading-syntax.md`](0095-bootstrap-zero-geometric-threading-syntax.md)
- [`0096-boolean-triangle-placement-language-alignment.md`](0096-boolean-triangle-placement-language-alignment.md)
- [`0097-threading-syntax-typed-braid-alignment.md`](0097-threading-syntax-typed-braid-alignment.md)
- [`0098-multihole-am-type-formation-constraints.md`](0098-multihole-am-type-formation-constraints.md)
- [`0099-axis-circle-pendulum-history-syntax.md`](0099-axis-circle-pendulum-history-syntax.md)
- [`0100-bootstrap-zero-syntax-factor-inventory-and-seam-repairs.md`](0100-bootstrap-zero-syntax-factor-inventory-and-seam-repairs.md)
- [`0101-six-port-whole-cut-theory.md`](0101-six-port-whole-cut-theory.md)
- [`0102-bootstrap-zero-whole-cut-grammar.md`](0102-bootstrap-zero-whole-cut-grammar.md)
- [`0102-production-ledger-followup.md`](0102-production-ledger-followup.md)
- [`0102-retention-and-declaration-followup.md`](0102-retention-and-declaration-followup.md)
- [`0103-cell-carrier-view-relation-machines.md`](0103-cell-carrier-view-relation-machines.md)
- [`0104-whole-cut-six-to-m6-boundary-bridge.md`](0104-whole-cut-six-to-m6-boundary-bridge.md)
- [`0105-q4-m6-go-search-research-program.md`](0105-q4-m6-go-search-research-program.md)
- [`0106-ontological-programming-type-barriers.md`](0106-ontological-programming-type-barriers.md)
- [`0106-three-hole-conjugate-m6-projective-lift.md`](0106-three-hole-conjugate-m6-projective-lift.md)
- [`0107-reusable-six-word-witness-kernel.md`](0107-reusable-six-word-witness-kernel.md)
- [`0108-graft-derived-witness-instantiation.md`](0108-graft-derived-witness-instantiation.md)
- [`0109-neutral-carrier-triadic-mechanism-frontiers.md`](0109-neutral-carrier-triadic-mechanism-frontiers.md)
- [`0110-neutral-adva-document-load-save.md`](0110-neutral-adva-document-load-save.md)
- [`0111-group-neutral-operations-and-q4-m6-relation-profiles.md`](0111-group-neutral-operations-and-q4-m6-relation-profiles.md)
- [`0112-transition-frame-relation-path-adapter.md`](0112-transition-frame-relation-path-adapter.md)
- [`0113-first-bounded-m6-reveal-run.md`](0113-first-bounded-m6-reveal-run.md)
- [`0114-three-sided-trace-arithmetic-calibration.md`](0114-three-sided-trace-arithmetic-calibration.md)
- [`0115-frontier-hypothesis-interface-experiment.md`](0115-frontier-hypothesis-interface-experiment.md)
- [`0116-reality-custody-continuation-experiment.md`](0116-reality-custody-continuation-experiment.md)
- [`0117-obligation-refinement-verification-boundary.md`](0117-obligation-refinement-verification-boundary.md)
- [`0118-local-closure-transport-and-adversarial-naming.md`](0118-local-closure-transport-and-adversarial-naming.md)
- [`0119-characteristic-magic-square-closure-family.md`](0119-characteristic-magic-square-closure-family.md)
- [`0120-trust-continuity-m6-closure-gate.md`](0120-trust-continuity-m6-closure-gate.md)
- [`0121-six-crossing-hypothesis-formation-search-word.md`](0121-six-crossing-hypothesis-formation-search-word.md)
- [`0122-problem-formation-value-seeking-trust-continuation.md`](0122-problem-formation-value-seeking-trust-continuation.md)
- [`0123-arithmetic-universality-and-hypothesized-truth.md`](0123-arithmetic-universality-and-hypothesized-truth.md)
- [`0124-trace-count-factorization-and-construction-obstruction.md`](0124-trace-count-factorization-and-construction-obstruction.md)
- [`0125-geometry-of-truth-interface-hypothesis.md`](0125-geometry-of-truth-interface-hypothesis.md)
- [`0126-knowledge-geometry-first-interface-witness.md`](0126-knowledge-geometry-first-interface-witness.md)
- [`0127-finite-vocabulary-gradient-and-checked-reuse.md`](0127-finite-vocabulary-gradient-and-checked-reuse.md)
- [`0128-acceleration-direction-pascal-incidence.md`](0128-acceleration-direction-pascal-incidence.md)
- [`0129-bounded-breakthrough-trusted-boundaries.md`](0129-bounded-breakthrough-trusted-boundaries.md)
- [`0130-prefix-coverage-gated-close.md`](0130-prefix-coverage-gated-close.md)
- [`0131-finite-learner-judgment-and-reuse.md`](0131-finite-learner-judgment-and-reuse.md)
- [`0132-structural-adjustment-evidence-applicability.md`](0132-structural-adjustment-evidence-applicability.md)
- [`0133-explore-open-universe-goal-relative-stopping.md`](0133-explore-open-universe-goal-relative-stopping.md)
- [`0134-three-turn-revise-and-local-close.md`](0134-three-turn-revise-and-local-close.md)
- [`0135-reunderstanding-resource-frames-and-fuel.md`](0135-reunderstanding-resource-frames-and-fuel.md)
- [`0136-native-learn-guarded-roundtrip.md`](0136-native-learn-guarded-roundtrip.md)
- [`0137-self-interpretation-boundary.md`](0137-self-interpretation-boundary.md)
- [`0138-world-task-boundary.md`](0138-world-task-boundary.md)
- [`0139-library-six-phase-and-communication.md`](0139-library-six-phase-and-communication.md)
- [`0140-native-program-run.md`](0140-native-program-run.md)
- [`0141-representation-residual.md`](0141-representation-residual.md)
- [`0142-question-indexed-distinguish.md`](0142-question-indexed-distinguish.md)
- [`0143-distinction-knowledge-and-free-boundary.md`](0143-distinction-knowledge-and-free-boundary.md)
- [`0144-research-across-tool-representation-and-crossing-boundaries.md`](0144-research-across-tool-representation-and-crossing-boundaries.md)
- [`0145-preservation-contract-and-finite-splitting.md`](0145-preservation-contract-and-finite-splitting.md)
- [`0146-private-merge-and-value-direction.md`](0146-private-merge-and-value-direction.md)
- [`0147-universe-prime-and-finite-extension.md`](0147-universe-prime-and-finite-extension.md)
- [`0148-finalize-and-python-adva-entry.md`](0148-finalize-and-python-adva-entry.md)
- [`0149-library-stability-and-zigzag.md`](0149-library-stability-and-zigzag.md)
- [`0150-persistent-library-epochs.md`](0150-persistent-library-epochs.md)
- [`0151-library-driven-proposal-feedback.md`](0151-library-driven-proposal-feedback.md)
- [`0152-continuation-01.md`](0152-continuation-01.md)
- [`0152-three-verifier-residual-search.md`](0152-three-verifier-residual-search.md)
- [`0153-frozen-verifier-search-campaign.md`](0153-frozen-verifier-search-campaign.md)
- [`0154-math-catalog-and-task-loop-boundary.md`](0154-math-catalog-and-task-loop-boundary.md)
- [`0155-cryptographic-sealing-and-calibration-boundary.md`](0155-cryptographic-sealing-and-calibration-boundary.md)
- [`0156-review-decision-draft.md`](0156-review-decision-draft.md)
- [`0156-tamper-evident-arithmetic-lineage.md`](0156-tamper-evident-arithmetic-lineage.md)
- [`0157-free-acceptance-predicate-candidate.md`](0157-free-acceptance-predicate-candidate.md)
- [`0158-downward-interpretation-and-drop-route.md`](0158-downward-interpretation-and-drop-route.md)
- [`0158-opening-equation-and-anchor-binding.md`](0158-opening-equation-and-anchor-binding.md)
- [`0159-frame-symmetry-triadic-continuation.md`](0159-frame-symmetry-triadic-continuation.md)
- [`0160-faithful-switch-and-reverse-observer-search.md`](0160-faithful-switch-and-reverse-observer-search.md)
- [`0161-advance-receipts-and-iota-substrate-projection.md`](0161-advance-receipts-and-iota-substrate-projection.md)
- [`0162-bounded-advance-loop.md`](0162-bounded-advance-loop.md)
- [`0163-evidence-stutter-and-progress-gate.md`](0163-evidence-stutter-and-progress-gate.md)
- [`0164-paired-quotation-quine-relay.md`](0164-paired-quotation-quine-relay.md) — see the 2026-09-20 correction: the retained implementations predate three supervisor fixes, so the corrected bytes and the class of drift are retained in `0164-evidence/postcommit-check-02/` and checked by the evidence verifier; a fresh relay lap is refused by the pinned library gate and needs its own calibration.
- [`0165-two-documents-interpretation-relation.md`](0165-two-documents-interpretation-relation.md)
- [`0166-interpretation-obligation.md`](0166-interpretation-obligation.md)
- [`0167-li-yorke-period-three-and-homotopy-continuation.md`](0167-li-yorke-period-three-and-homotopy-continuation.md)
- [`0167-iota-lang-reconnection-audit.md`](0167-iota-lang-reconnection-audit.md)
- [`0168-triadic-cycle-and-continuation-discipline.md`](0168-triadic-cycle-and-continuation-discipline.md)
- [`0168-switch-swap-and-braid-under-the-iota-substrate.md`](0168-switch-swap-and-braid-under-the-iota-substrate.md)
- [`0169-arakelov-stability-monge-ampere-mirror-ladder.md`](0169-arakelov-stability-monge-ampere-mirror-ladder.md)
- [`0170-mobius-conjugacy-and-observer-transport.md`](0170-mobius-conjugacy-and-observer-transport.md)
- [`0171-density-wave-marginal-wall-and-the-nonlocality-of-self-gravity.md`](0171-density-wave-marginal-wall-and-the-nonlocality-of-self-gravity.md)
- [`0172-the-i-minus-e-integrality-conjecture.md`](0172-the-i-minus-e-integrality-conjecture.md)
- [`0173-mirrors-that-never-close-and-a-question-to-a-waking-ai.md`](0173-mirrors-that-never-close-and-a-question-to-a-waking-ai.md)
- [`0174-absurdity-emptiness-counterexample.md`](0174-absurdity-emptiness-counterexample.md)
- [`0175-dodecahedral-hamiltonicity.md`](0175-dodecahedral-hamiltonicity.md)
- [`0176-feigenbaum-period-doubling-calibration.md`](0176-feigenbaum-period-doubling-calibration.md)
- [`0177-feigenbaum-fixed-point-collocation.md`](0177-feigenbaum-fixed-point-collocation.md)
- [`0178-rigorous-enclosures-and-two-barriers.md`](0178-rigorous-enclosures-and-two-barriers.md)
- [`0179-kantorovich-preflight.md`](0179-kantorovich-preflight.md)
- [`0180-inverse-norm-obstruction.md`](0180-inverse-norm-obstruction.md)
- [`0181-wu-elimination-on-plane-incidence.md`](0181-wu-elimination-on-plane-incidence.md)
- [`0182-wu-elimination-general-conic.md`](0182-wu-elimination-general-conic.md)
- [`0183-zhang-finite-example-verification.md`](0183-zhang-finite-example-verification.md)
- [`0184-area-method-readable-proofs.md`](0184-area-method-readable-proofs.md)
- [`0185-yang-difference-substitution-inequalities.md`](0185-yang-difference-substitution-inequalities.md)
- [`0186-dual-facility-leak-wall.md`](0186-dual-facility-leak-wall.md)
- [`0187-cut-linkage-after-cutting.md`](0187-cut-linkage-after-cutting.md)
- [`0188-aeg-core-shell-notation-registered-as-a-target.md`](0188-aeg-core-shell-notation-registered-as-a-target.md)
- [`0189-core-shell-and-symbolically-unexpanded-shell.md`](0189-core-shell-and-symbolically-unexpanded-shell.md)
- [`0190-the-multivariate-rung-of-the-historical-method.md`](0190-the-multivariate-rung-of-the-historical-method.md)
- [`0191-the-read-boundary-splits-the-mass-in-half.md`](0191-the-read-boundary-splits-the-mass-in-half.md)
- [`0192-the-traversal-allocation-and-its-reserve.md`](0192-the-traversal-allocation-and-its-reserve.md)
- [`0193-the-optimal-shares-and-the-price-of-a-level.md`](0193-the-optimal-shares-and-the-price-of-a-level.md)
- [`0194-the-measured-key-and-certificate-cost.md`](0194-the-measured-key-and-certificate-cost.md)
- [`0195-the-join-measured.md`](0195-the-join-measured.md)
- [`0196-the-protocol-as-a-checkable-declaration.md`](0196-the-protocol-as-a-checkable-declaration.md)
- [`0197-the-protocol-without-a-magic-number.md`](0197-the-protocol-without-a-magic-number.md)
- [`0198-the-protocol-ledger-and-why-the-partition-does-not-transfer.md`](0198-the-protocol-ledger-and-why-the-partition-does-not-transfer.md)
- [`0199-declaring-the-two-spaces.md`](0199-declaring-the-two-spaces.md)
- [`0200-the-depth-curve-from-retained-evidence.md`](0200-the-depth-curve-from-retained-evidence.md) — see the 2026-09-15 correction: current halting uncertainty is in `depth_curve/evidence-v1.json`; v0 remains historical.
- [`0201-two-curves-on-one-cost-axis.md`](0201-two-curves-on-one-cost-axis.md)
- [`0202-does-a-step-close-more-than-it-opens.md`](0202-does-a-step-close-more-than-it-opens.md)
- [`0203-allocating-the-three-currencies.md`](0203-allocating-the-three-currencies.md)
- [`0204-gold-twin-timeout-is-not-negative.md`](0204-gold-twin-timeout-is-not-negative.md)
- [`0205-iota-lang-recorded-contract-replayed-by-the-native-substrate.md`](0205-iota-lang-recorded-contract-replayed-by-the-native-substrate.md) — the iota-lang recorded 17-case contract replayed by the native substrate (17/17 reproduced), the four layers that are and are not usable as tests, and two transcription findings about the Research 0167 replay.
- [`0206-the-flat-list-reading-at-the-program-data-junction.md`](0206-the-flat-list-reading-at-the-program-data-junction.md) — seven declared cases decide which nesting reading of a flat list `[t1 … tn]` transports application: right-nested holds for the external I/K/S declarations, left-nested fails for K and S, and the reading is not decided below three elements.
- [`0207-renaming-the-iota-combinator-spelling-on-the-accepted-package.md`](0207-renaming-the-iota-combinator-spelling-on-the-accepted-package.md) — the accepted murphy package is respelled `ι` for the Iota combinator by a declared, checked renaming: same term, same witness and the same frozen oracles, with the renamed spelling refusing `i` and the received bytes left byte-identical.
- [`0208-accepting-the-renamed-murphy-unit.md`](0208-accepting-the-renamed-murphy-unit.md) — the renamed unit published in `mountain/adva` is accepted: its bytes are identical to this machine's derivation, its renamed programs reproduce all four frozen counted oracles, and every recorded coordinate relation holds with the same slot order in both spellings, with `J⁴ = I` retained as a measured `Unknown` boundary.
- [`0209-the-quine-relay-implementation-correspondence-corrected.md`](0209-the-quine-relay-implementation-correspondence-corrected.md) — the retained relay bundle froze implementations that three later supervisor fixes changed: the corrected bytes, the drift class, the falsifier and the measured library-gate refusal are recorded, with the closure explicitly left un-re-established.
- [`0210-the-address-space-limit-is-linux-only.md`](0210-the-address-space-limit-is-linux-only.md) — installing the test extra exposed that `RLIMIT_AS` is a Linux-only limit whose unconditional installation kills the child launch: three sites are corrected with `conform` back to 16 of 16, the acceptance relation is re-established by `toolchain/evidence/local-06`, and twelve tests in three files remain open with their measured reasons.
- [`0211-an-acceptance-record-names-its-host.md`](0211-an-acceptance-record-names-its-host.md) — every acceptance report now carries a `host` block (platform, machine, release, interpreter), `toolchain/evidence/local-07` is the fresh acceptance, and a new check makes a record produced on one host fail when read as another's.

### Named notes

- [`mobius-transport-composition-boundary.md`](mobius-transport-composition-boundary.md)

- [`mobius-transport-receipt-boundary.md`](mobius-transport-receipt-boundary.md)

- [`PR-0152-0158-integration.md`](PR-0152-0158-integration.md)
- [`absurdity-emptiness-record-freeze.md`](absurdity-emptiness-record-freeze.md)
- [`alternating-group-observer-expansion.md`](alternating-group-observer-expansion.md)
- [`borromean-boundary-word-correction.md`](borromean-boundary-word-correction.md)
- [`borromean-independent-longitudes.md`](borromean-independent-longitudes.md)
- [`catalog-key-words-alignment.md`](catalog-key-words-alignment.md)
- [`catalog-key-words-v1.md`](catalog-key-words-v1.md)
- [`cube-root-conjugation-and-polar-covariance.md`](cube-root-conjugation-and-polar-covariance.md)
- [`frame-covariance-rational-calibration.md`](frame-covariance-rational-calibration.md)
- [`golden-ratio-operator-lift-and-basis-coverage.md`](golden-ratio-operator-lift-and-basis-coverage.md)
- [`golden-ratio-receipts-and-source-boundaries.md`](golden-ratio-receipts-and-source-boundaries.md)
- [`golden-ratio-receiving-review.md`](golden-ratio-receiving-review.md)
- [`lattice-polar-and-mirror-boundary.md`](lattice-polar-and-mirror-boundary.md)
- [`leak-wall-reading-correction-lines-and-rings.md`](leak-wall-reading-correction-lines-and-rings.md): reading correction, no executable claim: Research 0186's flow-network reading of the leak wall is withdrawn in favour of the language of lines, links and cutting.
- [`operator-check-python-adapter-v0.md`](operator-check-python-adapter-v0.md)
- [`operator-lift-main-integration-v1.md`](operator-lift-main-integration-v1.md)
- [`operator-lift-receipt-boundary-v0.md`](operator-lift-receipt-boundary-v0.md)
- [`observer-quotient-descent-reproduction.md`](observer-quotient-descent-reproduction.md)
- [`pairing-transport-native-boundary.md`](pairing-transport-native-boundary.md)
- [`pascal-commutator-certificate.md`](pascal-commutator-certificate.md): exact commutator certificates for the pinned normalized Pascal equations; also corrects the independent-check and initial claims in Research 0181.
- [`reflexive-lattice-gate.md`](reflexive-lattice-gate.md)
- [`sharkovsky-interval-extension.md`](sharkovsky-interval-extension.md)
- [`simplex-contraction-pascal-calabi-reduction.md`](simplex-contraction-pascal-calabi-reduction.md)
- [`triadic-period-bridge-correction.md`](triadic-period-bridge-correction.md)
- [`yang-lu-reference-registration-deferred.md`](yang-lu-reference-registration-deferred.md): process record, no executable claim: the external-reference registration was deferred at the catalog entries bound and admitted after the direction widened it to 101, with the recorded reason quoted and qualified.

- [zot-prefix-machine-weighted-sharing.md](zot-prefix-machine-weighted-sharing.md): explicit Zot evaluation, exact weighted reuse, and prefix-Keraia syntax/input boundaries.
- [keraia-read-boundary-and-weighted-prefix-search.md](keraia-read-boundary-and-weighted-prefix-search.md): resumable weak-head reads, checked segment reuse, exact code weights and retained type-boundary failures.
- [keraia-cycle-certificates-and-halting-mass-bounds.md](keraia-cycle-certificates-and-halting-mass-bounds.md): independent cycle receivers exclude a nonhalting cylinder, with multi-read continuations and an exact conditional one-half experiment.
- [bounded-native-data-interpreter.md](bounded-native-data-interpreter.md): a Rust-owned research data machine runs an Adva arithmetic interpreter over 129 object programs, with exact state reception and budget-preserving continuation.
- [bounded-interpreter-cross-host-replay.md](bounded-interpreter-cross-host-replay.md): a second host re-receives 300 retained checkpoints from their own bytes, reproduces the recorded profile digest and a byte-identical continuation; no new claim and no new campaign.
- [self-interpretation-capacity-preflight.md](self-interpretation-capacity-preflight.md): inside the declared bounds an inspectable encoding of the machine's own instruction grammar needs 169 nodes against 127, the packed alternative cannot be unpacked, and a 17-case dispatch ladder spends 90 of 128 instructions; a capacity measurement, not an impossibility result.
- [self-interpretation-scaling-preflight.md](self-interpretation-scaling-preflight.md): a generated meta program interprets a declared four-opcode subset of the machine's own instruction grammar and returns 7, 9, 4 and 5 for unseen object programs, while a four-opcode meta over two object instructions already needs 166 of the declared 128 instructions and is refused.
- [futamura-projections-in-adva-terms.md](futamura-projections-in-adva-terms.md): the Futamura projections stated in this repository's terms, with the first projection executed — a compiler built from the frozen interpreter by a declared rule emits 3-instruction residuals for all 129 frozen trees, agreement checked three ways, and the compile cost recorded; projections two and three are blocked by measured bounds.
- [futamura-dynamic-residual-calibration.md](futamura-dynamic-residual-calibration.md): the first projection with a live dynamic input — a 41-instruction compiler in the machine's own language emits 1- or 2-instruction residuals for a declared two-opcode subset, values and refusals both agree with interpretation, and the compile-versus-interpret ratio is measured rather than assumed.
- [compiler-size-curve-and-bootstrapping-budget.md](compiler-size-curve-and-bootstrapping-budget.md): the in-language compiler size curve — each extra opcode costs 45 to 63 instructions and each extra source instruction 32, an extra slot costs nothing because slot indices travel as data, and a compiler for the machine's whole instruction language is a measured 201-instruction lower bound against 128.

### Supporting directories

- [`0129-evidence/`](0129-evidence/)
- [`0139-phase-runner-preflight/`](0139-phase-runner-preflight/)
- [`0140-native-run-evidence/`](0140-native-run-evidence/)
- [`0141-local-preflight/`](0141-local-preflight/)
- [`0141-native-evidence/`](0141-native-evidence/)
- [`0142-evidence/`](0142-evidence/)
- [`0143-evidence/`](0143-evidence/)
- [`0144-evidence/`](0144-evidence/)
- [`0145-evidence/`](0145-evidence/)
- [`0146-evidence/`](0146-evidence/)
- [`0147-evidence/`](0147-evidence/)
- [`0148-evidence/`](0148-evidence/)
- [`0149-evidence/`](0149-evidence/)
- [`0150-evidence/`](0150-evidence/)
- [`0151-evidence/`](0151-evidence/)
- [`0152-evidence/`](0152-evidence/)
- [`0153-evidence/`](0153-evidence/)
- [`0156-evidence/`](0156-evidence/)
- [`0158-evidence/`](0158-evidence/)
- [`0161-evidence/`](0161-evidence/)
- [`0162-evidence/`](0162-evidence/)
- [`0164-evidence/`](0164-evidence/) — `postcommit-check-02/` retains the corrected implementations and `relation.json`; every earlier payload keeps its bytes.
- [`0165-evidence/`](0165-evidence/)
- [`0167-evidence/`](0167-evidence/)
- [`0168-evidence/`](0168-evidence/)

*Complete listing as of 2026-09-16. The counts are stated once, in the header above;
they were previously duplicated here and the two copies drifted apart.*

- [keraia-growth-invariants-and-mass-ablation.md](keraia-growth-invariants-and-mass-ablation.md): received protected-stack invariants add 13 nonhalting cylinders at depth 19, excluding 19/524288 at the same cut; depth 15 gains zero.

- [bounded-self-compiler-and-futamura.md](bounded-self-compiler-and-futamura.md): a structured Adva research compiler compiles its own source, with stage, block and execution receiving; the three Futamura projections retain explicit implementation obligations.
- [execution-performance-comparison.md](execution-performance-comparison.md): 78 checked cases separate Rust direct execution, dynamic residuals, interpretation overhead and byte-identical self-compiler stages.
- [bounded-mix-and-three-projections.md](bounded-mix-and-three-projections.md): ordinary Adva input-binding mix self-applies to emit residuals, compilers and a compiler generator; two object interpreters exercise the finite code-producing equations, with the v1 capacity refusal retained and optimizing specialization still open.
