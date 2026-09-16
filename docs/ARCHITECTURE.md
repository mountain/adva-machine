# Architecture

The local `adva-machine` continuation adds a specification index under `spec/`,
Rust/Python entry points, and the [common toolchain boundary](../toolchain/README.md).
The [repository direction](TOOLCHAIN_DIRECTION.md) distinguishes these interfaces
from future target-language backends and keeps library organization open. The
existing implementation layout and semantic authority described below remain
in force.

The bounded research data machine in
[its ADR](adr/bounded-data-machine-research.md) adds a separate typed register/tree
execution carrier owned by Rust. The `adva data-run` entry validates program,
input and budget; continuation replays the complete checkpoint against those
independently supplied inputs. `programs/bounded-interpreter/interpreter.adva`
contains the arithmetic object-language interpreter. No host evaluator callback
or Python execution dependency implements its tag dispatch. The new carrier has
no PSC0 source/occurrence allocation or diagram certificate; a correspondence
with the stable sharing/graft carrier remains open.

Research 0152 uses `python/adva/adva.py` as the outer CLI, with a bounded
`verifier_search` supervisor. Its new Rust example owns arithmetic syntax,
rewrite positions, residuals and witness checks; Python copies Rust-produced
Lean/Metamath proof text and records external verification. Batched external
acceptance admits only scoped research evidence. The stable semantic boundary
and prior immutable library checkpoints are unchanged; see ADR 0040.

Research 0153 adds a separate `adva.py search-campaign` supervisor and Rust
example for policy comparison and a bounded frozen-policy continuation. It
imports the 0152 external log checks unchanged and enforces byte-identical
Rust arithmetic/proof-export blocks before running. Visit memory is over
research arithmetic syntax only. Per-direction pilot selection controls
proposals, not verifier rules, native identities or library admission; see
ADR 0041 and the explicit 100-round contract.

## Dependency direction

The separate math topic catalog (ADR 0042) is a Python documentary adapter.
`adva.py math-check` validates metadata, one-home topic membership, references
and byte pins, never Rust semantics or proof truth. Its fixed growth obligation
requires Pascal-rooted, same-home proposed geometry ancestry and retains Open
discharge. Cross-topic references are not imports or derivation parents; the
checkpoint is documentary seal, not native Seal. Actual program and proof
checks still enter through their original authority boundaries. Research 0154
records existing arithmetic, external Pascal and finite logic task mechanisms;
it does not add a unified task-loop executor or native feedback.

```text
adva-ir  <-  adva-lisp  <-  adva-python  <-  Python adapters
   ^              ^
   |              |
   |         semantic kernel
   |
adva-witness (research V0)
```

`adva-ir` contains immutable, serializable ontology. `adva-lisp` owns parsing,
module linking, type checking, explicit sharing, lowering, evaluation,
differentiation, observations, and certificate construction. `adva-python`
exposes opaque checked objects through PyO3. Pure Python modules adapt those
objects to external libraries.

No arrow points back from Python into semantic construction. External-library
results are numerical realizations or candidate data, never new Rust
judgments.

## Crates

### `adva-ir`

- language-independent module and term IR;
- typed frontiers and qualified names;
- `SharedProgramDiagram`;
- compiler-emitted nested graft-trace companion types;
- causal-cut, single-event, and exact program-slice result types;
- bounded triadic cut-observation and observer-transition companion types;
- explicit source, occurrence, path, and history data;
- distinct directed rewrite, equation, and coherence types;
- versioned JSON envelopes and certificate types.

### `adva-lisp`

- S-expression reader without host evaluation;
- `module`, `import`, `export`, `def`, `fn`, and `call`;
- module graph validation and cycle rejection;
- linear use checking and explicit structural operations;
- typed lowering from `ProgramTerm` to `SharedProgramDiagram`;
- deterministic nested graft traces retained beside compiler-produced diagrams;
- finite boundary substitution through checked module calls;
- certified causal-cut and enabled-event analysis over checked diagrams;
- exact same-diagram program-slice analysis between nested causal pasts;
- certificate-bearing exact composition of adjacent program-slice views;
- certificate-bearing three-domain opposite-pair readings and exact adjacent
  observer-transition composition;
- builtin operation registry shared by evaluation and differentiation;
- deterministic source and occurrence allocation.

### `adva-witness`

- a Rust-owned research V0 registry for the corrected six initial words;
- exact signed formation ledgers and arbitrary-precision integer-polynomial
  normalization for bounded add/multiply witnesses;
- a triadic adapter from one certified `CompilationArtifact` graft frame to
  three derived source/occurrence/path bindings, with retained certificate and
  frame-path provenance;
- finite acyclic proof artifacts with content-addressed cache keys;
- linear three-hole templates whose instances bind existing `SourceId` and
  `OccurrenceId` values without allocating or identifying them;
- explicit formed and executed type states, with non-unit transport and every
  concrete intermediate zero rejected;
- a bounded neutral-carrier mechanism grammar whose input, process, and output
  labels remain distinct, with separate open-frontier rules for computation,
  verification, and learning proposals;
- a research-only neutral `.adva` document graph and filesystem boundary with
  canonical carrier, transition-frame, and entry-point tables; mechanisms
  label frames rather than carriers, while shared carrier references express
  explicit output-to-input reuse across frames.

The bounded native `adva run` adapter also depends on `adva-lisp` for parsing,
compilation, checked diagrams and evaluation; it introduces no evaluator or
operation registry of its own. Its separate research program envelope is
described in ADR 0035. The witness artifact schema is
`adva.witness.research` version zero, not an extension of `adva.ir` version 1.
Artifact hashes are cache coordinates and never semantic identities.

### `adva-python`

- PyO3 classes wrapping linked modules and checked diagrams;
- JSON and certificate access;
- read-only Rust-derived graft-trace, program-slice, and exact-composite
  snapshots;
- read-only derivation and exact composition of Rust-owned version-zero
  triadic observer transitions;
- typed scalar evaluation and gradients.

### `python/adva`

- ergonomic typed facade;
- frozen inspection views over Rust-owned graft and slice artifacts;
- a strict, bounded research runner that packages exact triadic interfaces,
  complete slices, and chosen checked schedules without semantic allocation;
- a layered multi-hole through adapter that proposes finite fibre-product
  relations from exact call-frame holes and same-diagram ancestry while
  retaining the complete `ProgramSlice` residual;
- single-diagram triangular and typed-connector calibrations that compare
  finite relations over unchanged Rust incidence coordinates while refusing
  semantic closure, sibling identification, and forgetting authority;
- a bounded distributivity characteristic atlas that reads one Rust core as a
  triadic boundary, three opposite-pair relations, one grafted multi-hole
  carrier, one exact rational polynomial feature, and one retained residual;
- a typed-aperture research companion that reads existing finite through
  relations as filling fibres, selects close witnesses without erasing
  alternatives, and reopens the same presentation with trace retained;
- SymPy conversion;
- NumPy ufunc-style callables;
- SciPy objective/Jacobian adapters.

## Module mechanism

A module has an explicit name, imports, exports, and function definitions.
Imports name a module and exported symbols; there is no wildcard import in the
initial core. A function parameter list and result frontier are its type
boundary. Calls are resolved and type checked before lowering.

Lowering inlines the called body only as a finite representation technique. A
`HistoryEvent::Call` remains in the diagram, so inlining does not make module
history definitionally invisible. Recursive calls and cyclic module imports
are rejected until guarded recursion obtains its own semantics.

The inputs of a function are its ordered open holes. A call lowers each
argument as a program under the caller's linear resource scope, checks the
resulting frontier against those holes, and only then grafts the finite callee
body. This is PSC0's bounded substitution mechanism. It is not host-language
value application or a local binder calculus.

A compiler-produced `CompilationArtifact` also carries a checked `GraftTrace`
companion. Its deterministic frames retain parent/child nesting, exact
argument and callee-body node regions, ordered hole bindings, boundary wires,
and links to flat call-history events. Syntax argument regions remain distinct
from flattened hole bindings because an argument can produce zero or multiple
wires. Stored or externally imported diagrams do not acquire this compiler
provenance retroactively. A frame boundary is a sub-boundary of the whole DAG,
not automatically a whole causal cut.

## Native process and cut analysis

The operation dependency DAG has a causal reading and a cut reading.
`analyze_causal_cut` accepts a set of completed operation nodes, verifies that
it is downward closed, and returns the exact `WireRef` values crossing from
that past to its future. `advance_causal_cut` verifies one enabled event and
returns the frontier wires it consumes and produces.

All analyses first revalidate the diagram and return Rust certificates.
`analyze_program_slice(P,U,V)` additionally requires nested causal pasts and
retains the exact events in `V` minus `U`, changed lower and upper boundaries,
unchanged through wires, and internal events invisible at the upper frontier.
Optional graft links are revalidated compiler provenance and may overlap; they
are not an event partition or a frame/cut bijection.  Adjacent composition
revalidates both input views, checks the literal middle cut and event union,
rebuilds the outer view in original diagram order, and requires equality with
the direct outer slice. Exact tests exhaust the full five-cut lattice of one
independent three-event diamond, including all nested triples and quadruples.
The two legal schedules retain distinct step paths while yielding the same
canonical outer slice; schedule order is therefore not stored as slice event
order.

These analyses preserve source and occurrence lineage without evaluation.
They do not assert a topology object, an observer pullback, equality of
alternative schedules, or a coherence cell.

The first bounded observer companion is
`TriadicObserverTransitionV0`. An explicit policy assigns exactly three input
positions to construction, space, and time; Rust derives the corresponding
source map from the checked initial cut. Each endpoint cut is expanded into
occurrence-level incidences. The view for one role exposes the other two source
fibres, while own-role incidences and source-free wires remain explicit. Lower
and upper incidences are related by unchanged source identity and checked
occurrence-path ancestry. Adjacent views compose only after both embedded
`ProgramSlice` values and the finite ancestry relation compose exactly.

This companion does not type internal wires as construction, space, or time.
It is an observer projection of one exact process interval, not an active
program rewrite, reversible transport, specialization result, or proof.

The Python boundary exposes these artifacts only by invoking Rust and decoding
the returned result/certificate JSON. Adjacent composition accepts three pasts
and derives both input slices inside Rust; no Python-constructed slice, frame,
or certificate is admitted as semantic input. Imported version-one diagrams
still have no graft trace.

`adva.research.ResearchMachineV0` sits above this read-only boundary. One
`InterpretationCellV0` retains the lower and upper triadic observations, the
complete canonical `ProgramSlice`, and one stepwise checked schedule. Optional
finite replay repeats the same static experiment under a literal endpoint
comparison and gives each dynamic record a nonsemantic epoch coordinate. It
does not feed an upper cut back into the program, re-enable events, or allocate
fresh `NodeId`, occurrence, wire, cut, or source identities. The decision and
promotion boundary are recorded in
[ADR 0011](adr/0011-bounded-three-layer-research-machine.md).

The theoretical dependency and promotion gates are specified in
[`PROGRAM_PROCESS_CORE.md`](PROGRAM_PROCESS_CORE.md) and
[ADR 0006](adr/0006-program-process-before-projections.md).

## Operation library

Every builtin operation has one Rust definition of:

- namespace, name, version, and surface visibility;
- exact parameter schema;
- input and output boundary rules;
- scalar realization;
- local forward differential;
- source and occurrence transport.

The first registry contains `id`, `swap`, `copy`, `discard`, constants, `add`,
`mul`, `scale`, `neg`, `sin`, `cos`, `exp`, and `log`. Structural operations
are diagram nodes, not Rust or Python aliases. `frontier` is deliberately not
an operation: it assembles an ordered typed open boundary without claiming a
tensor-product semantics.

The IR represents that boundary with an orientation-free `TypedFrontier` and
distinct `DomainFrontier` and `CodomainFrontier` orientations. For a future
observer semantics, `D*` runs contravariantly from codomain probes to domain
probes. The executable spelling will be `pullback`, not a Lisp program term;
it must be derived from checked diagram data and accompanied by a certificate.

Polynomial-like carriers and matrix-like transports are distinct compiled
presentations, not replacements for this boundary constructor. They remain
chart-, basis-, observer-, and certificate-relative construction targets; see
[ADR 0004](adr/0004-frontier-before-compiled-presentations.md).

The parser, typed lowering, evaluator, and forward differential all resolve the
same `OperationSpec`. Stored IR is checked against the registry again before
execution, so changing a serialized node boundary cannot silently select a
different realization. Differential certificates record versioned rule IDs
such as `adva.builtin:mul@1`, rather than unqualified names. Adding or changing
a builtin version is governed by
[ADR 0003](adr/0003-single-operation-registry.md).

## Serialization

The interchange format is JSON with schema identifier `adva.ir` and version
`1`. IDs are written as data. They are never reconstructed from memory address,
Python `id()`, Rust pointer identity, hashes, values, or incidental object
sharing. The repository also publishes a JSON Schema under `schemas/`.

Decoding and semantic import are deliberately separate. The Rust Lisp kernel
rechecks graph topology, operation boundaries, linear frontier use, occurrence
paths, source-preserving copy history, and the final codomain before returning
a `DiagramValidationArtifact`. Evaluation repeats this integrity check. Python
can load stored diagrams only through this Rust boundary; see
[ADR 0005](adr/0005-checked-diagram-import.md).

Binary encoding is intentionally deferred until profiling justifies it. A
future binary codec must preserve the same ontology and schema versioning.

## Stable versus research code

The stable slice contains finite modules, terms, diagrams, compiler-emitted
certified nested graft frames, evaluation, differentiation, explicit source
partitions, certified finite causal cuts, single-event frontier replacement,
exact program slices and adjacent composition, and lossless serialization.
It also contains the bounded version-zero triadic observer-transition
companion over exact three-source input policies.

The Python research runner is deliberately outside the stable semantic slice.
It is a bounded experiment orchestrator over stable artifacts; its verdicts
and replay digest are not Rust certificates and are never accepted by the
kernel as semantic input.

The Rust `adva-witness` companion is also outside the stable semantic slice.
It makes one bounded six-word witness and reuse proposal executable without
changing PSC0 terms, builtin operations, diagrams, or certificates. Its exact
integer-polynomial normalization is a witness observation, not a new stable
Adva scalar domain or an equation-cell constructor. Its graft adapter consumes
an existing compiler `CompilationArtifact` as a whole, derives bindings only
from an ordered three-hole frame with singleton lineage, and records rather
than replaces the compiler and graft certificate identities. Its subsequent
neutral-carrier grammar uses research-local frontier coordinates to distinguish
closed computation, explicitly open verification, and candidate learning fill
plans. Those coordinates are not stable holes, cut ports, or logical
obligations. Its separate `.adva` research document stores a canonical table
of neutral carrier cache references, a canonical table of mechanism-labelled
three-input/three-output transition frames, and named entry points. Rust
resolves every document-local carrier and frame reference and rechecks every
mechanism form before it returns the selected transition; Python supplies
paths, entry-point names, and JSON-shaped values only. A complete stored
output triple records a graph state but does not certify mechanism-output
provenance. This does not change the Lisp parser, `adva.ir` version 1, or
feedback semantics, and loading does not resolve the referenced witness
artifacts.

The same research crate contains a separate bounded relation-cell formation
checker. It keeps carrier operations (`join/cut/close`), traversal
(`step/run`), and relation witnesses (`interchange/braid/transport`) in
different layers. `RelationProfileV0` fixes the `Q4` interchange profile to a
trace-monoid lift with Klein-four Coxeter shadow and the `M6` braid profile to
a positive-braid-monoid lift with `S3` shadow. Raw paths are never identified;
open cells retain a residual reference, and filled cells authorize only their
explicit orientation. These are research formation records rather than
`adva.ir` equation cells, executable rewrites, group operations, or generic
conjugacy certificates. They are not stored in `AdvaDocumentV0`.

`FrameRelationCellV0` can derive such a relation from two explicit paths in
one already validated neutral document. Mechanism labels, not method carriers,
become the relation generators. Every step retains its `FrameIdV0`; every
adjacent pair must reuse all three recorded output carriers exactly once as
the next input triple, and the resulting permutation is retained. Both paths
must share exact labelled input and recorded-output boundaries. The artifact
is bound to the validated document digest. This is a document-local formation
adapter: `FrameIdV0` does not become `OccurrenceId`, recorded output does not
gain execution provenance, and the adapter neither searches for nor constructs
a `join`.

The first bounded CLI calibration consumes
`programs/bootstrap-0/reveal.adva`. `M6NamingPlanV0` covers all six directed
off-diagonal pairs between time, space, and construction with two opposite
three-edge cycles. Names remain entry-point selectors and are resolved to
authoritative frame coordinates. `RevealWitnessV0` records the source digest,
fuel ledger, observed and remaining names, both derived frame paths, and typed
questions. Observing all six frames completes the finite run but leaves the
relation semantically open; insufficient fuel emits a suspended witness. The
separate reveal-witness schema uses the common `.adva` suffix but does not
extend `AdvaDocumentV0` or `adva.ir`. The first six-fuel output is retained at
`programs/bootstrap-0/first-reveal-witness.adva`; CI derives it again and
requires byte equality.

The trace-arithmetic adapter consumes that persisted witness rather than the
source document. It retains both exact frame paths and derives independent
time-count, spatial-boundary, and construction-mechanism projections. Typed
`left - right` residuals cannot cancel across domains. A commutative
mechanism-weight quotient is diagnostic only and retains its nonidentity as an
open holonomy question. The three opposite-side characteristic maps and the
shared truth fiber remain explicitly unwitnessed. Projection equality, BLAKE3
coordinates, and M6 formation are not promoted to semantic equality or truth.
The first derived artifact is retained at
`programs/bootstrap-0/first-trace-arithmetic.adva` and reproduced byte-for-byte
by CI.

The bounded inquiry adapter turns that calibration into a resumable
`InquiryFrontierV0`. The frontier embeds the original calibration and carries
its five exact open obligation coordinates. A `learn` edge then reads three
independent `.adva` files through the fixed `subject/method/object` slots: the
frontier, a frozen `ExplorationContractV0`, and a recorded external
`ResourceSnapshotV0`. It writes `history/result/evidence`, where the result is
only a proposed `HypothesisV0` and the evidence contains the complete next
frontier. Candidate content identity excludes its local name, while the
resource receipt preserves both the name and recorded entropy. Algorithm
drift, resource replay, question renaming, and post-hoc resource edits are
rejected. The adapter closes no arithmetic obligation and authenticates no
external claim; it supplies continuation integrity rather than liveness or
truth.

Reality-facing inquiry candidates may optionally retain a
`RealityBoundaryV0`. It keeps protocol-bound independent remeasurement
separate from the `CustodyPlanV0` used to declare damage assumptions. Integrity,
authenticity, availability, fork accountability, and semantic reproducibility
are distinct protected properties; deletion, mutation, equivocation, key
compromise, and correlated capture are distinct threats. Rust checks nonempty
coordinates and protocols, unique ledgers, and locally consistent positive
thresholds. It does not contact an instrument, verify a signature, operate a
replica set, execute a recovery drill, or infer truth from receipts.

`VerificationFrontierV0` is an additive state layer over an embedded,
byte-unchanged `InquiryFrontierV0`. A `verify` edge again reads
`subject/method/object`: an inquiry or verification frontier, a frozen
`VerificationContractV0`, and a `VerificationPacketV0`. It writes a decision
history, a scoped result, and residual-frontier evidence. Obligations may be
open, refined into typed children, discharged by a future typed predicate, or
reopened by counterevidence. Version zero deliberately has no discharge
predicate: a request containing only witness and scope digests is recorded as
rejected. Refinement can therefore increase the number of open leaves without
pretending that knowledge regressed. Semantic closure excludes the orthogonal
custody ledger and additionally requires an empty unresolved-fork ledger.

`MagicSquareFrontierV0` is the first bounded search state admitted through the
same `learn` interface. Its method performs deterministic row-major search with
recorded node fuel. A completed order-four square is checked in two independent
ways: ten incidence-sensitive additive line equations and one order-insensitive
characteristic-polynomial equation for the value multiset. The selected closure
is then unfolded under three method-supplied automorphisms into a finite
`MagicSquareClosureFamilyV0`. Members, generator edges, coherence relations,
local line-content reuse, and shared-cell influences remain distinct records.
This is a research-local closure ecology, not a stable solver or a generic
closure operator.

The grounded multi-hole through adapter is subject to the same boundary.  Its
middle object is an explicitly declared quotient of upper incidences by exact
upper cut-wire index.  Passing its Python validation layers does not promote a
specialization, forgetting permission, active normalization, through-relation
composition law, or universal machine.  A stable successor would require a
Rust-owned result and certificate type.

The triangular and connector calibrations remain one layer further out.  Their
incidence relations and SourceId projections are candidate readings of one
unchanged checked carrier.  Symmetric sibling comparison is not inverse
execution, and a nonempty source-level cycle is not permission to identify
occurrences.  Neither artifact is accepted back by Rust.

Objectification witnesses, higher cells beyond their data boundaries,
projective observers, generic proof transport, and compiler optimizations that
consume objectification certificates remain research targets. They must not be
simulated with booleans or Python callbacks.


The additive `TraceProjectionWitnessPairV0` consumes a checked trace-arithmetic
calibration. It reuses the existing research path validator to certify the
temporal count rule and checks a finite obstruction to full construction
recovery from equal time and space inputs. The complete source calibration,
raw paths, method coordinate, and open questions remain present. A Cargo
example emits the independent research schema; it does not extend the CLI or
install a discharge predicate. See Research 0124 and ADR 0033.


## Guarded native learn roundtrip research method

Research 0136 and ADR 0034 add a version-zero method dispatch in the existing
`adva-witness` Rust executable. It replays a supplied six-stage arithmetic
round trip, checks literal reverse endpoints and retained nonzero obligations,
and packages a local `learn` record. It does not extend `adva.ir`, allocate
semantic identities, or synthesize a method. The native run and its limits are
tracked in `docs/research/0136-native-learn-guarded-roundtrip.md`.

## Frozen library stability research calibration

Research 0149 and ADR 0037 add only the `library_stability` Cargo example.
It consumes supplied, bounded `ExactExprV0` catalogues and observations and
retains question-bound feature/exclusion certificates. Its shared study fuel,
immutable requests and full-content replay are research protocol machinery,
not changes to `ProgramTerm`, diagrams, the operation registry or live library
storage. Existing Q4/M6 formation and braid regression oracles remain separate.

Research 0150 and ADR 0038 subsequently add the Rust `library_checkpoint`
module, with public functions re-exported from `adva-witness`. Its explicit
epoch files retain parent bindings, ordered candidate and observation prefixes,
complete diagnostic certificates and native ArithmeticTransition/Seal nodes.
`load_library_v0` rederives the bounded ancestry into `CheckedLibraryV0`;
`publish_library_v0` rechecks and publishes a complete file without clobbering.
The `library_epoch` example performs one supplied continuation through disk
reload. No existing diagram import, stable API meaning or documentary index
is reinterpreted by this separate research schema.

Research 0151 and ADR 0039 add the example-local `library_generation` proposal
mechanism. It reads a checked 0150 seed, enumerates arithmetic proposal syntax
without task access, checks expanded pairs against explicit calibration, and
stores composite recipes in a separate exploration journal. Continuation
drops the in-memory book and regenerates all prior stages from disk before
reusing their recipes. Unknown/Open records are diagnostic, not knowledge
admission. This journal does not change the old epoch loader or its checker
fingerprint. Newest-recipe ablation and ordinary macro expansion calibrate
bounded feedback without claiming native program or language formation.

## Structured compiler bootstrap research boundary

`data_machine_v1` supplies a separately versioned finite target for the
[structured self compiler](research/bounded-self-compiler-and-futamura.md).
Generic Rust instructions execute Adva source traversal, block-size calculation
and target construction. Python supplies an external seed, representation codec
and independent structural receiver; Rust admits and executes the resulting
typed targets. The original `data_machine` v0 module remains frozen. Neither
version allocates native diagram identities or extends stable PSC0. The compiler
has a separate research correspondence receipt, not a native `GraftTrace`.

The [bounded input-binding mix](research/bounded-mix-and-three-projections.md)
uses the same generic instruction grammar to construct a static literal prefix,
bind input and relocate the unchanged source body. Its own implementation is
ordinary structured Adva source compiled by the received self compiler. No Rust
instruction or host callback performs specialization. External Python receives
the complete syntactic correspondence; Rust admits, executes and replays targets.

`data_machine_v2` is a separate capacity successor: version/profile markers and
the instruction-count and node/field-arity limits change from 2,048 to 4,096.
All 23 operations and other resource bounds retain v1 semantics. The unchanged
v0/v1 sources retain their historical profiles and evidence. V2 cannot receive a
v1 checkpoint. The [ADR](adr/bounded-mix-self-application.md) records the actual
v1 capacity obstruction and the revised finite contract. This research boundary
does not add a stable transformation certificate or native diagram identities.
