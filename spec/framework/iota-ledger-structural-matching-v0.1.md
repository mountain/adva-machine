# Projected Iota ledger structural matching v0.1

Date: 2026-09-30. Status: bounded read-only engineering profile for architecture
G2. Maintenance home: `mountain/adva-machine`; this does not resolve the separate
architecture contract's formal-adoption decision. Profile identifier:
`adva.iota-ledger-structural-isomorphism.v0.1`.

Project-original by dot (OpenAI), contributed under Unknown v0.3, submitted
through Mingli Yuan's GitHub account as an authorized account proxy. Account use
is not his technical review, endorsement or a correctness guarantee.

## Question, scope and exclusions

Can the same public projected Iota event/cut ledger in two separately received
packages be compared by actual finite graph structure, with reviewable mappings
and conservative counterexamples? This is the implementation-local selection
of the public-Iota option in architecture DEC-02. It does not select an algebra,
a new semantic equivalence, a native occurrence authority, or executable reuse.

The relation is **colored directed multigraph isomorphism with exact retained
conditions**. A positive result is only `StructuralMatchCandidate` at L2 for
this projected documentary ledger. This is stricter than unlabelled topology:
matching can miss meaningful similarities because source identifiers, terms,
readings and all conditions remain anchored. `NoMatchWithinProfile` negates
only this relation for these finite inputs. `Unknown` negates nothing.

The node-kind and edge-label types below are documentary representation types,
not Rust wire types. The original ledger supplies no checked PSC0 type judgment,
complete annotated ancestry or separately typed semantic guards. These gaps
remain explicit. Python constructs no native `SourceId`, `OccurrenceId`,
`CausalCut`, proof, certificate, transport receipt or admitted program. The
historical source checker, kernel program and private archive are never run or
fetched. Registration, semantic verification, native admission and adoption do
not advance. There is no refactoring, loader, cache, network access or mutation.

## Fixed inputs and preservation

Two public received locations are read through immutable Git objects with
replacement objects, lazy fetching and optional locks disabled:

- `mountain/adva-machine@79aced81e972e8a4af96b118d8e236f7e337ffcb:knowledge/received/iota-process-machine-2026-09-17-v1/`
- `mountain/adva@3287c61ab7d16253605b3d0cca818f5a698e258b:knowledge/received/iota-process-knowledge-2026-09-17-v1/`

Each location binds `materials/interpretations.json`, `materials/contract.json`,
`materials/structure.json`, `materials/dependencies.json`, and `receipt.json` by
exact path, full commit and independently frozen SHA-256 in the adapter. The
29,903-byte ledger digest is
`8009db7b8828ae76aa01b25684b9aa974fc91c4fcb64a439946701a49fe528b1`.
The source schema is exactly `adva.iota-term-ledger.v1`. A wrong digest is rejected;
a missing blob or exhausted read budget is Unknown. No local/latest/same-name
substitution is allowed. Repository identity is caller-declared, not authenticated.

The report retains both different receipt/context records and full source
coordinates. Equal package bytes never coalesce the two receiving occurrences.
A historical receipt is an opaque supplied observation; reading it is not a
fresh receive or revalidation. `NotRun`/`NotGranted` values remain historical.
All consumer locks, frozen receipts/evidence and existing strict transport
schemas remain byte-for-byte unchanged.

The exact contract is retained as opaque premises; its protected declarations
are retained alongside `guards.status=Unavailable`. Structure-card preservation
and open questions, the complete dependencies object, source-archive digest,
schedule count, partition reading and full-process digest are retained conditions.
Different conditions block a positive candidate and are reported on both sides.
The `source_revision`, original source home and all source references survive;
they do not imply that the private source archive was available or verified.

## Representation and allowed transformations

The family selector/name is provenance, not an equality color. Every node and
edge has a local handle plus a source selector relative to the family's JSON
pointer. Append that selector to the family source pointer to locate the source.
These handles are disposable, not semantic identities.

| Node kind | Exact color / retained meaning | Directed relations |
| --- | --- | --- |
| `OrderedInterface` | Source and normal prefix terms, ordered entry/exit roles and role reading | Contains events/cuts; ordered output-slot edges |
| `LedgerEvent` | Anchored event ID, rule tag, ordered rewrite path, before/after/discard terms, named clock assignments | Dependency predecessor to event |
| `LedgerCut` | Exact term, entry/terminal flags | Event to cut for each performed-event bit |
| `LedgerTransition` | One distinct node per declared transition, including repeats | Input cut to transition, transition to output cut, event to transition |
| `ApertureOccurrence` | Exact port, occurrence, origin and ordered copy path | Ordered output slot, origin and copy-event/branch relations |
| `DeclaredSourceOrigin` | Exact supplied origin string | Origin to every distinct supplied occurrence |

Prefix terms are validated over ordered application `@` and tokens `iksabc`;
they are exact syntax labels, not normalized expressions. Tags 0, 2 and 3 are
retained source event tags, not newly authorized rewrite laws. This adapter
checks representation, references and syntax only; it does not redo Iota
reduction correctness, causal down-closure, schedule counts or physical clocks.
The complete public source checker has a different, historical finite scope.

Each final-aperture entry remains a distinct occurrence. Repeated ports are
valid: the copy fixture has ports `[0,2,1,2]`. Duplicate occurrence identifiers
are rejected. Copy-path references must resolve to a declared event; origin
strings are anchored, and equal origins do not merge occurrences. Every edge
has direction, label and multiplicity; duplicates cannot be discarded as sets.

Only generated graph-local handle renaming and unordered record serialization
permutation are allowed. Reordering the source event array must consistently
remap all dependency indices, cut-mask bits, transition-event indices and clock
assignments. Cut/transition/dependency record order is not a color. Role arrays,
rewrite paths, final-aperture sequence and copy-path sequence are ordered and
must not be permuted. Source/event/occurrence/origin strings are **not** renamed.
There is no commutation, association, cancellation, copying, discarding,
term reduction, history erasure, proof equivalence or new algebraic identity rule.
Unsupported schemas/fields, malformed references and collapsed occurrences are
rejected rather than guessed. Changing rules requires a successor profile.

## Algorithm, witness and outcomes

Algorithm `colored-directed-multigraph-backtracking.v0.1`:

1. Validate the exact input schema, term syntax, finite capacities and references
2. Build the typed graph and directed edge multiset, charging extraction
3. Compare exact conditions, typed-color counts and edge multiplicity; mismatch
   provides a finite negative invariant, not a semantic counterexample
4. Refine each node once by its exact typed, directed, multiplicity-preserving
   neighbor-color list. Full canonical bytes are compared, not hash identities
5. Order source nodes by candidate-class size then lexicographic local handle;
   enumerate target handles lexicographically, with explicit iterative backtracking
6. Check self-loops and both directions against every already mapped node
7. Before reporting success, separately verify the complete bijection, all exact
   colors/conditions and the complete mapped edge multiset; construct the edge
   bijection by matching each endpoint/label occurrence
8. Independently check the emitted witness, including edge bijection, occurrence/
   source/boundary subsets, graph digests and empty unmatched/lost-condition claims

The report includes both complete input coordinates, graph digests, node/edge,
occurrence, source and boundary mappings, unmatched portions, retained/lost
conditions, full conditions on both sides, spent resources, rule version and
evidence digest. A successful isomorphism has empty unmatched/lost lists; the
input residuals remain, including absent full ancestry and guards. All candidate
output graphs are retained so a reviewer can reconstruct the mapped selectors.
Potentially affected consumers remain Unknown because this profile performs no
exhaustive consumer-use inventory. The proposed next check is human/engineering
review followed, if selected, by a separately versioned G3 receiving/checker route.

Results distinguish malformed `RejectedInput`, observed finite
`NoMatchWithinProfile`, `StructuralMatchCandidate` and incomplete `Unknown`.
A successful representation check alone does not produce a candidate. A search
cutoff preserves its partial mapping and exact stopping position; it never
becomes a complete NoMatch. No automatic retry or continuation resets its account.

## Declared finite account

Defaults are fixed before invocation: 1 MiB total source bytes, 128 KiB/file,
64 Git calls, 8,192 extracted nodes, 32,768 extracted edges, 2,000,000 counted
steps, depth 256, 32 comparisons, 16 MiB output and 120 seconds cooperative wall
safety limit. Source families additionally have at most 24 events and 128 cuts.
One pilot invokes 15 comparisons: 12 same-family pairs plus three near matches.

Input byte limits are checked against Git object size before reading/parsing.
JSON duplicate keys, floats and nonfinite numbers are refused. JSON is decoded
under its byte cap, then its nesting is checked; Python parser recursion failure
is Unknown. Prefix syntax depth is checked while parsing; search-stack depth is also bounded. Counts include graph
extraction, search candidates/adjacency checks, independent witness checking and
edge mapping. Nodes/edges count cumulative extracted objects, depth/file size
are maxima, and report bytes count the emitted envelope including its newline.
The local generator read and one HEAD ancestry lookup are disclosed separately.

These are cooperative limits, with individual Git-call timeouts. Canonical
encoding, hashing, sorting and JSON parser allocation occur within the finite
byte/node/edge capacities; their individual CPU instructions are not a claimed
instruction count. There is no process-memory sandbox or adversarial scheduler.
A separate wall cutoff can yield a non-repeatable Unknown prefix and is explicitly
labelled. Normal report payloads exclude elapsed wall time for byte-repeatability.

If an encoded report exceeds its storage limit, only a bounded Unknown envelope
with source pins, account and omitted-payload digest is emitted. If even that
envelope cannot fit, no JSON report is emitted and the invocation fails. These
limits do not bypass a protected obligation or justify silently extending scope.

## Compatibility and next gate

The profile is an additive script with no stable Rust/Python semantic API change.
It does not rename the G1 metadata-shape clusters. G1 results and historical
architecture snapshots remain predecessor evidence. The current implementation
establishes a finite G2 slice, not all architectural adoption/conformance.

G3 needs a separately chosen executable reuse/cut route with applicable native
checker, formed-boundary/guard/freshness controls, total first-check/reuse cost,
retained failures and unchanged four-epoch ancestry rule. A structural candidate
cannot supply missing native identities, authorize private source acquisition,
or select/upgrade a consumer. G4 needs its own successor lock; G5 needs explicit
identity, security, hosting and ownership decisions.
