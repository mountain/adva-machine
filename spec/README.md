# Adva specification index

This index is the local machine repository's entry to Adva's existing contracts.
It references their canonical files and fixed bytes; it does not copy or
reinterpret them. `catalog.json` distinguishes stable PSC0/IR from separately
versioned, bounded data-machine research profiles.

`../docs/SEMANTIC_SCOPE.md`, `../docs/PROGRAM_PROCESS_CORE.md`, the relevant ADRs
and `../docs/claims.toml` retain their declared authority and limits. Rust remains
the current admission and native certificate authority. A matching file digest
records integrity, not semantic correctness.

The common toolchain request/report boundary is described in
[`../toolchain/README.md`](../toolchain/README.md). Its wrapper schema is neither
a replacement for `adva.ir` version 1 nor a new stable Adva language.

## Formal framework vocabulary

[Transport and communication v2](framework/transport-communication-v2.md) is
the current terminology for new designs: `transport` preserves presentations
under an already shared contract; `communicate` seeks a common interpretation
across heterogeneous interfaces. The [v2 registry](framework/vocabulary-v2.json)
pins this successor and its unchanged predecessor. Its distinction is adopted;
it introduces no native opcode, command alias or general interpretation engine.

[Triadic context v0](framework/triadic-context-v0.md) clarifies the sides of
that inquiry: participant A / participant B / shared nature or object, together
with Surface / Knowledge / Substrate. Both readings are retained; their
task-specific correspondence and observation obligations remain explicit.
Read it alongside the pinned vocabulary and free specification below.
The [conditional theory](framework/triadic-free-theory-v0.md) supplies proofs
for finite common interpretation, anchored quadratic balance and finite
adjustment, and counterexamples separating them from consensus or stationarity.
Its [exact finite checks](../experiments/triadic_interpretation/README.md) keep
model assumptions and actual participant/world observations distinct.

[Communication v1](framework/communication-v1.md) formally defines
`communicate`, `send`, `receive`, `acknowledge` and `accept`. Their definition
is adopted; the general native exchange operation is not yet implemented.
[ADR 0047](../docs/adr/0047-formal-communication-vocabulary.md) records that
decision and its implementation gate.

[The framework registry](framework/vocabulary-v1.json) pins the normative
document and its historical sources. It is a vocabulary index, not a parser,
operation registry or conformance result. `catalog.json` continues to pin the
existing native contracts and research profiles independently.

[Documentary library entry exchange v1](framework/documentary-exchange-v1.md)
now supplies a bounded Rust `adva communicate` CLI receiving route. It binds
one reviewed original entry, retains its home and obligations, and records
documentary acceptance and an observed acknowledgment. General communication
and native mathematical admission remain open. [ADR 0048](../docs/adr/0048-bounded-documentary-communication.md)
records the operational boundary; the earlier vocabulary registry remains a
frozen record of adoption, not the current implementation inventory.
Under v2, the existing documentary profile's implemented capability is transport;
its v1 command names, contracts and results keep their versions.

[Free process v0](framework/free-process-v0.md) specifies a research process
from initial anchoring through pressure-guided adjustment to scoped balance
and acceptance. Its [finite external calibration](../experiments/triadic_free/README.md)
tests supplied chart correspondences, retained residuals and bounded replay.
Native free, interpretation search and the three-share/reserve policy remain
open. [ADR 0050](../docs/adr/0050-triadic-free-process-calibration.md) records
the definition, vocabulary refinement and measured boundary.

## Finite iota interpretation frame

The [iota frame v1 profile](framework/iota-frame-v1.md) binds iota processes,
complex structure and exponential observations in a checked finite research
frame. Its received witnesses preserve domain boundaries, metric, observer,
clock and residuals; no stable keyword or native frame type is added.

## Carrier matrix profile

The [carrier matrix v0 profile](framework/carrier-matrix-v0.md) reads one
checked cut as a carrier: a table is realized as an operator on the grade-1
exterior carrier, composition is the matrix product, and the summation over the
middle index is the cut's own pairing rather than a new operation. Its checker
derives the incidence pairing from the declared enabled edges instead of reading
it, and its controls separate the carrier, the composition order and the
cochain. It registers no native keyword, operation, value type or IR version,
and its received run record is a local record rather than a communication
receipt until the documentary route is executed.
