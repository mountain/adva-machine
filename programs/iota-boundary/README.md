# Run the boundary-aware iota successor

The separate adva-iota repository now produces an ordinary data-machine-v2
request for this machine. Rust executes the supplied interpreter instructions
and receives the resulting trace through the existing run command. Iota is the
object language; the engine remains rust.

An [eight-file iota package has now been received locally](../../knowledge/exchanges/iota-process-machine-2026-09-17-v1/README.md)
through the existing Rust documentary transport. It contains the original
interpreter program, three probes and the finite process/cut comparison, with
a separate post-arrival execution record. The same packet is also received by
adva under its own contract. This route does not require access to the private
development repository for the compact checks.

The external interpreter has 344 instructions and 42 registers. Its source
grammar contains only iota, binary application, and three declared apertures.
Entry and exit policies explicitly associate those apertures with construction
{}, space [], and time (). K and S are internal expansion rules and can be
derived from pure-iota source. A submitted primitive K/S is refused, including
inside a subsequently discarded branch.

The interpreter normalizes by leftmost outermost reduction, retaining every
redex, replacement and tree position. Copy and discard remain visible in these
records. Positions are object-language coordinates; they are not native PSC0
SourceId or OccurrenceId. The policies are flat role assignments, not a parser
for nested boundary syntax.

## Reproduce

The independent checkout is published at
[mountain/adva-iota](https://github.com/mountain/adva-iota), a private repository
requiring collaborator access. [dependency.json](dependency.json) retains the
checked revision and file digests; its null publication remote records the
state before the repository was created. It is a documentary pin, not an
automatic dependency installer or transport certificate. The standard runner
binds and checks the actual supplied request and native executable profile;
it does not read this optional manifest.

From the pinned adva-iota checkout:

    python3 -m boundary_v1 emit --case duplicate --output /tmp/iota-request.json

From adva-machine, using its Python environment and built release Rust binary:

    python adva-machine run /tmp/iota-request.json --engine rust --output /tmp/iota-run

Use fresh output paths. The emitted request explicitly supplies instruction
fuel and invocation quantum. Zero quantum suspends before an instruction;
it never means unlimited execution.

The duplicate fixture applies the pure-iota encoding of S to apertures a,b,c.
Its normal form is (a c) (b c); it takes 12 object contractions and 4,838 native
instructions. The full event sequence and both policies agree with the separate
recursive Python oracle. Native replay verifies the same execution. K applied
to a,b returns a while its redex record retains b.

## Checks and remaining scope

The pinned external campaign has 26 cases and 126 campaign assertions.
Eleven normal forms, two object-fuel stops, one native-fuel stop, and twelve
invalid inputs are distinguished. Twenty-five emitted execution traces pass
Rust replay; the Boolean integer is refused before execution. An additional
native receiving check refuses a result whose history was erased.

The initial attempt incorrectly selected zero quantum. Its zero-step suspension
and implementation-failure report remain archived alongside the successful
correction under a separate continuation contract. The frozen Java audit remains
unchanged, including its failures; its baseline and 13 tooling tests pass.

The external Wick experiment first declares a three-dimensional carrier and
observes output-aperture multiplicities as v, then chooses H = vv^T/(v^Tv),
or zero for v=0. Exact rational projector and finite-series checks support that
specified observation. It retains the program and history as a residual and
does not establish a physical Hamiltonian intrinsic to iota, quantum cloning,
unitary erasure, or thermal equilibrium. No matrix observation creates a native
diagram certificate.

The knowledge mainline was first advanced from 80daf14 to
1bdadfc2a1263aac0139aeef9be69ed756e9c186 (38 commits); machine main remained
6646582. Its new reversible-memory, clock-history and failure-kind work informs
this separation of retained process, observation and physical interpretation.
Knowledge consumers and their machine/library pins are unchanged.

This integration documents an executed existing input route. It adds no stable
operation, engine, schema reinterpretation, vendored Java source, or claim that a
formal content exchange occurred. The interpreter and complete campaign evidence
remain in adva-iota at the pinned revision.

Code and report authorship: Codex (OpenAI), original contribution under Unknown
v0.3 through Mingli Yuan's authorized account proxy. This is not Mingli's
authorship, technical review or correctness guarantee.
