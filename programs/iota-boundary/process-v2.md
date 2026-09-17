# Iota process cuts and observer simultaneity

The independent adva-iota successor now retains event dependencies and checks
every boundary cut in twelve finite process families. Its standalone explorer
shows the same process through dependencies, occurrence boundaries, observer
clocks, and a declared real/imaginary-time operator. Iota remains the sole
source combinator; explicit aperture policies still supply construction {},
space [], and time () roles.

[process-v2-reference.json](process-v2-reference.json) pins the completed local
revision, specification, implementation and evidence. The checkout has no
publication remote. Open `process_v2/evidence/explorer.html` from that revision
in a browser; it works without a server or external assets. The English
`process_v2/SPEC.md` is primary; the Chinese explorer is a companion.
The earlier [v1 integration](README.md), pins and evidence remain unchanged.

## From a generator to a process and its slices

The order of construction is:

    pure-iota source + explicit boundaries
        -> retained reduction events and occurrence ancestry
        -> checked dependency order and cuts
        -> observer clocks and their simultaneous layers
        -> a declared operator on that same cut carrier

Each selected trace binds a conservative family of disjoint commuting rewrites.
The model observes complete redexes and records relocation. This imposes some
nested dependencies beyond the minimal order one might obtain from a weaker
observation. Different nested rewrite orders remain different families; equal
normal forms do not identify their events or histories.

A cut is a downward-closed completed-event set, checked by reconstructing its
term and live occurrence boundary. A separate traversal explores exact event
applicability without consulting the proposed dependency edges. The two cut
sets must agree. All admitted topological schedules, commuting diamonds and
comparable cut intervals are checked. Both traversals share the annotation
reducer; this is not an independently implemented native cut checker.

The relationship with simultaneity becomes concrete in three examples:

- Two independent iota contractions have four cuts forming a diamond. Either
  event may occur first; both orders reach the same annotated endpoint. An
  observer may give the pair equal readings or distinguish their order.
- S applied to a pending identity process creates two distinct descendants
  sharing an origin. After the copy event, the two continuations can advance
  independently. The example has 48 cuts and 252 checked schedules. Copying
  syntax therefore changes the available computational slices; it does not
  assert cloning of an arbitrary quantum state.
- K can discard pending work before any of that work is executed. Its redex
  and discarded payload remain in the residual history. Performing the work
  before discarding it would ask about a different process family. Returning
  the same value cannot establish the same dependencies or simultaneous layers.

For a<c with b independent of both, concurrency holds for (a,b) and (b,c) but
not (a,c). Concurrency is not transitive. Equality of readings under one clock
is transitive, so an observer's simultaneity must be an additional slicing
policy. Every clock here strictly respects dependencies, and every threshold
past must be one of the checked cuts. Positive affine clock calibration
preserves the existing equality groups; splitting a group is a different
policy, not just a new unit or origin for the same clock.

This develops the separation of retained history and observation suggested by
the knowledge mainline's reversible-memory and clock-history experiments at
`1bdadfc2a1263aac0139aeef9be69ed756e9c186`. It leaves those experiments and
their pinned consumers unchanged.

## Real and imaginary time on one finite carrier

Use one orthonormal basis vector per checked cut. The declared observation
forgets edge direction when forming the unit-weight graph Laplacian L=D-A,
and sets H=L/(2*d_max). Directed, labeled edges and full histories remain
available separately. The same H defines

    U(t) = exp(-i*t*H),    U(-i*tau) = exp(-tau*H).

For this positive semidefinite graph Laplacian, real-time evolution is unitary
and the imaginary-time operator is a stochastic heat kernel. The latter can
move backward on the graph and is not the directed iota evaluator. Exact
rational series checks run through order 12, with spectral-norm tail at most
3/13! for absolute parameter at most one. The explorer uses a separately
checked floating-point illustration.

The four-cut diamond and four-cut chain have partition functions beginning
`4 - 2*beta` and `4 - (3/2)*beta`, respectively. Unlike v1's rank-one
final-multiplicity projector, this observation can distinguish these process
structures even with equal carrier dimension. It still loses information:
role relabeling leaves the operator unchanged, and different processes may
have isomorphic or isospectral cut graphs.

The generator, event clock and continuous operator parameter play distinct
roles. This construction supplies a finite common object for studying their
relationship. The chosen weights, symmetrization, energy scale and Hilbert
carrier do not derive physical dynamics, a spacetime metric or physical
simultaneity from iota alone.

## Executed checks and machine authority

The external campaign passed 4,144 counted assertions: 92 events, 159 cuts,
519 schedules, 55 commuting diamonds, 1,762 intervals and 2,060 adjacent
interval compositions across twelve separately bound fixtures. Eight invalid
observations are refused; wrong Wick sign and different nested order controls
retain distinct outcomes. The first semantic campaign passed without retry.

Through the existing data-machine-v2 runner, Rust checks all 92 local
unannotated contractions in one batch and three complete pure-source normal
forms. All four requests pass native replay, using 12 launches and 16,732
execution instructions, with the same instruction count replayed. The graph,
ancestry and cut coordinates remain external research results, not native
PSC0 SourceId, OccurrenceId, CausalCut or ProgramSlice certificates.

The bounded campaign took 5.73 wall seconds, 5.48 aggregate CPU seconds and
168,611 counted host work units. A separate jsdom check passed 990 assertions
over all 159 cut controls and independent diamond evolution formulas. That
check establishes DOM behavior, not browser pixel layout. The frozen audit and
its thirteen tooling tests also pass their preservation checks. The local
iota evidence archive retains every campaign file with member digests, source
snapshots, native traces, refusal controls and timing records.

From the pinned iota checkout, with the machine Python dependencies and built
release binary available:

    python -m process_v2.run --machine /path/to/adva-machine \
      --output target/new-process-campaign

Use a fresh output directory. The fixed contract caps time, memory, artifacts,
native launches, events, cuts and schedules; exhaustion remains Unknown.
This documentary reference is not an automatic dependency installer or an
executed content exchange. No new machine operation, engine or stable semantic
profile is introduced, and the machine repository incorporates no iota source
or external UI dependency.

Authored by Codex (OpenAI), original contribution under Unknown v0.3 through
Mingli Yuan's authorized account proxy. Account use is not his authorship,
technical review, endorsement or correctness guarantee. No independent human
or second-agent review is claimed.
