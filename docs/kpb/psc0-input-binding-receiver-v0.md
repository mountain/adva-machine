# PSC0 input-binding receiving pilot v0

Status: experimental machine-owned receiving library; no stable operation grant.
Authored by Codex (OpenAI), through Mingli Yuan's authorized account proxy.
Original additions under Unknown v0.3. Account use is not personal review,
endorsement or a correctness guarantee.

## Question and boundary

Make the already checked finite correspondence reusable, without reimplementing
PSC0 calibration or promoting a research claim to kernel authority. The isolated
package `experiments/psc0_input_binding_receiver` exports `receive_json`.
It does not change crates, OperationSpec, adva.ir, the root Cargo lock, the
persistent loader, existing evidence or any cross-repository consumer lock.
KPB v0.1 sections 9–11 govern this separately bounded route.

The reused native judgments are `validate_diagram` and
`analyze_program_slice_with_graft`, including native graft validation. The
correspondence checker, event/occurrence mapping, static forgetting ledger and
fixed fixture producer originate in `mountain/adva` at
`b7762854031138e3c1141b8aab326fe4e4f2f90c`, path
`experiments/native_input_binding_certificate/native_input_binding_certificate.rs`.
That implementation is project-original under Unknown v0.3. This package exposes
its fields through serde and adds an independent request envelope; the existing
ten regression tests remain. The producer is compiled only in tests. This is
engineering extraction and interface authoring, not an executed content exchange
or consumer migration. No claim of independently implemented native kernels.

## Wire contract and identity

`RequestV0` has exactly `profile` and `expected`. The expected object fixes the
complete source diagram snapshot, residual qualified root and canonical exact
static Rational. Consumers supply these bytes independently of the producer.
`ProposalV0` has exactly `profile`, `source`, `residual`, `certificate`.
The source/residual are full existing CompilationArtifact values; stored success
booleans do not authorize acceptance. Both envelopes require profile
`adva.psc0-input-binding.receive.v0`. Unknown envelope/certificate fields and
unsupported profiles are Rejected. Native nested types retain their existing
serde behavior. Rust public structures are the normative field schema.

The certificate retains source/residual snapshots, static value, bound source,
dynamic source pair, ordered event map, qualified occurrence map, forgotten
static occurrences, forgotten static Source/Copy history and introduced binding
node. Qualification uses checked root, SourceId, OccurrenceId and path. Equal
local counters or values never identify contexts. A replaced source cannot
repin the caller's snapshot. Source and residual roots must differ.

The receiver rechecks both diagrams, grafts and slices, complete event/wire and
occurrence/path coverage, exact operation versions (literal constant@2), output
order, copy/discard history and the full static forgetting ledger. Its law is
exact decorated structural correspondence after the literal-prefix cut. There
is no evaluator, numerical sampling or general specialization theorem.

Version identity is **profile plus full machine commit**. The proposal cannot
choose a checker commit. v0 has no compatibility fallback, network resolution,
producer callback, cache or receipt reuse permission. Changed rules need a new
profile; implementation updates require explicit consumer repinning and replay.

## Budget and outcomes

Each independently supplied JSON input is at most 262144 bytes before parsing.
Serde's default recursion guard remains enabled. Work must be 1..4096; normal
conformance uses 512 units. Existing finite bounds remain: at most 17 nodes,
32 occurrences, 64 history rows, two inputs/outputs and two node input wires per
diagram, call-free source and exactly one residual call. Out-of-profile sizes
and work exhaustion yield Unknown with no accepted certificate and no refuel.
Malformed JSON, altered binding, unsupported identity or missing correspondence
yield Rejected. Successful complete checking yields BoundedAccepted.
Every report has `stable_native_authority=false` and consumed structural work.

Structural work counts rows, comparisons and top-level kernel calls, not CPU
instructions or bit complexity. Parsing and build costs are separate; the byte
cap bounds serialized input, not a proven peak-memory ceiling. CI has a
15-minute job limit and 180-second test limit. No continuation token, automatic
retry, constant-time shortcut or proof compression is supplied. Every call
rechecks all supplied material; first-check and repeat-check costs therefore use
the same accounting. Resource enforcement beyond this finite library profile
requires a separately sandboxed caller.

## Conformance and adoption

Run `cargo test --manifest-path experiments/psc0_input_binding_receiver/Cargo.toml`.
CI formats the extracted file before compilation and publishes formatting diff
in its log; it checks all external resolved packages against the retained root
lock. The child lock is a seed of that resolution and may be pruned by Cargo;
no dependency version change is authorized by the pilot.

The ten retained regressions cover source substitution with identical local
IDs, copy deletion, lost static lineage, forged mappings, output/graft order,
operation version, profile limits and exhaustion. Three added wire tests cover
JSON roundtrip, forbidden authority fields, version mismatch, byte bounds,
independent static binding and ledger/identity mutations. Local Rust execution
is NotRun: this authoring host has no Cargo toolchain. Actual remote results
must be read before reporting execution success.

KPB-14 consumer adoption remains Open. A successor Adva lock must name the full
merged machine commit, this profile, exact interface bytes, independently fixed
request/source and permitted outcome (`BoundedAccepted`, no stable privilege).
It must replay the actual research witnesses through this library with fresh
positive/negative evidence and measured full/repeated check cost. Preserve the
old private checker and its historical replay until that consumer migration is
verified. Neither this PR nor merge upgrades other consumers or closes Issue 26.

Alternative: immediately install a stable Specialize operation. Rejected for
this pilot because its broader contracts and authority have not been checked.
Reversion: keep consumers pinned; remove only this isolated package. Old source,
locks, receipts and native semantics remain reproducible.
