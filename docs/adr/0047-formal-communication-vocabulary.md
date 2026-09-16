# ADR 0047: Adopt communication as formal framework vocabulary

Status: **accepted for framework vocabulary version 1**. Date: 2026-09-16.
Native implementation status: **not implemented as a general primitive**.
Direction and adoption requested by Mingli Yuan. Authored by ChatGPT (OpenAI),
submitted through his authorized account proxy; account use is not technical
review or a correctness guarantee.

## Problem

The library has a checked documentary catalog, but its materials, evidence and
checkers span repository boundaries. Reorganizing filenames cannot establish
that another interface has received a construction with its assumptions and
dependencies intact. Mingli requires content to pass through Adva exchange and
receiving mechanisms rather than using operating-system file operations as
the migration itself, and asks to make the communication proposal formal
framework vocabulary.

Research 0139 supplied the four event distinctions. Research 0158 placed
`communicate` at the return interface of a bounded inquiry. The existing
symbol-surface receiver checks one historical handoff/reply relation, but
there is no general native exchange operation. A formal term needs a durable
definition without reporting an unimplemented operation as executable.

## Decision

Adopt [Communication v1](../../spec/framework/communication-v1.md) as the
normative framework specification for `communicate`, with supporting events
`send`, `receive`, `acknowledge` and `accept`. Register their meanings and
implementation boundary in
[the framework vocabulary registry](../../spec/framework/vocabulary-v1.json).

Formal adoption takes effect in this successor document. It does not rewrite
the historical research notes or claim that their earlier experiments met
the new specification. `verify` and the existing native operation registry
retain their present meanings. The neutral carrier's three mechanism labels,
stable Lisp, IR and data-machine profiles are unchanged.

Every implementing profile must bind source, receiver context, versioned
contract, dependencies, observations, residuals, resource account and permitted
continuation. Reception, acknowledgment and scoped acceptance have separate
evidence. An explicit rejection or `Unknown` is a communicable outcome.

The canonical owner is `adva-machine`. Knowledge and library consumers should
cite the exact specification revision. Adopting a documentation version does
not silently change their separately pinned executable machine or library.
The framework vocabulary registry is separate from `spec/catalog.json`, whose
existing native/profile byte pins remain unchanged.

## Consequences and next implementation gate

New migration designs must use this vocabulary and show a checked receiving
route. File storage and Git are possible backend mechanisms; neither completes
the exchange by itself. Ordinary specification and implementation editing is
not misreported as a content exchange.

The next implementation is one finite local exchange for an existing library
entry, with an explicit operational profile and controls for wrong context,
missing dependencies, repeated delivery, refusal, `Unknown` and partial failure.
The requirements in Communication v1 govern it; no runtime implementation,
library rearrangement, proof promotion or network delivery is performed by
this documentation decision.

Formal vocabulary, executable semantics and checked evidence are separately
versioned obligations. This adoption completes the first of those obligations.

## Validation of this documentation change

On 2026-09-16, the framework registry's normative-document digest, two historical
source digests and pinned library-receiver reference matched. Eleven local
document links resolved. `adva-machine doctor` reported `Ready`, retaining all
14 native/profile pins and 11 library pins. `math-check --key-words` reported
`CatalogConsistent` for 32 entries and `MatchedDeclaredKeys`.

The existing toolchain and retained-evidence regression suites passed 36 tests.
These checks cover documentation integrity and existing boundaries; they are
not conformance tests of an implemented `communicate` primitive. Native source,
schemas, historical research/evidence, library contents and executable dependency
pins were unchanged.
