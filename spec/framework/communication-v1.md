# Communication: formal framework vocabulary, version 1

Status: **adopted framework specification**, 2026-09-16. English is primary.
Direction and adoption requested by Mingli Yuan. Authored by ChatGPT (OpenAI),
submitted through his authorized account proxy; account use is not technical
review or a correctness guarantee.

## Definition and scope

**`communicate` is an exchange across declared participant interfaces, governed
by a receiving contract, that carries a presentation with its provenance,
dependencies, evidence and residuals, and records what the receiver observed
and which continuation, if any, that observation permits.**

The participants may be machines, knowledge stores, programs or human-facing
interfaces. A repository can host an interface; a directory name alone does
not define one. The exchange may carry a question, proposal, construction,
proof presentation, counterexample, refusal or `Unknown` result. The meaning
of communication is not restricted to transmitting a successful answer.

This is the formal meaning of a framework word. Its general native operation,
wire encoding and executable conformance profile remain **unimplemented**.
The registry in [vocabulary-v1.json](vocabulary-v1.json) records that distinction.
The word is no longer merely proposed terminology; that adoption does not
assert that the runtime already executes it.

This specification governs future cross-interface exchange and repository or
library migration. It does not retrospectively certify existing transfers.
Historical records retain their original schemas, scope and receiving rules.

## Vocabulary

| Word | Formal role | Evidence needed for the event |
| --- | --- | --- |
| `communicate` | Conduct and account for the scoped exchange | Contract, bound presentation, participant-local events, receiver outcome and continuation boundary |
| `send` | Attempt dispatch of a particular presentation to a declared interface | Sender-local attempt, exact presentation/version, intended recipient and cost; receipt is not inferred |
| `receive` | Record the arrival of a presentation at a particular interface | Receiver-local arrival, observed bytes or declared representation, source claim and context; invalid input may still be recorded as received |
| `acknowledge` | Return a reference to a particular reception and its recorded outcome | Exact reception reference and responder scope; the sender records acknowledgment only when it actually observes the reply |
| `accept` | Admit a specified use or continuation under the receiver's contract | Explicit purpose, satisfied required checks, retained residuals and a receiver decision bound to this presentation and context |

`contract`, `verify`, `history`, `result` and `evidence` keep their existing
roles. In particular, `verify` performs the declared check; `accept` records
what that check and the contract permit. Acceptance of a document for catalog
registration does not establish the truth of its prose. Mathematical admission
requires the applicable proof checker and its actual certificate scope.
Human acceptance, where a contract requires it, must be evidenced separately;
an agent's receipt does not stand for a person's agreement.

`communicate` organizes exchange between interfaces. It is not added as a
fourth value of the existing `compute` / `verify` / `learn` mechanism enum, a
Lisp `OperationSpec`, a data-machine opcode or a new `adva.ir` version. A future
implementation must choose and version its actual operational boundary.

## Required contract and retained information

A concrete exchange MUST declare the following before it can authorize use.
Here MUST and MUST NOT express requirements of this framework specification;
they do not claim that an implementation already enforces them.

An initiated exchange binds its contract and finite limits before dispatch or
checking. An unsolicited arrival is handled under an already declared bounded
receiving policy; a later contract cannot retroactively authorize prior effects.

| Component | Required information |
| --- | --- |
| Purpose | Task or offer reference, version, requested use, and the receiving question; an unsolicited offer must be marked as such |
| Interfaces | Sender and receiver roles, supported representation/profile, receiver context and method of resolving endpoint claims |
| Presentation | Exact artifact/version, format, scope, assumptions and origin; a transformed representation also needs its declared correspondence |
| Dependencies | Versioned material, evidence and checker references, their roles, required availability, and how the receiver resolves them |
| Method | Receiving contract/version, checker/version, acceptance conditions, allowed effects and explicit treatment of unavailable checks |
| Events | Exchange, attempt and event coordinates; parent-event references; participant-local observations and their provenance |
| Resources | Finite limits for transfer, checking, replay and recording; spent resources, deadline and any explicitly allowed retry budget |
| Return | Receiver judgment, applicable certificates, unresolved obligations, and the continuation permitted or still blocked |

Message and event coordinates are scoped protocol references. Byte digests
check integrity relative to a chosen reference. Neither is a native `SourceId`,
`OccurrenceId`, semantic identity, proof or authenticated human identity.
Two equal payloads can belong to distinct exchanges; one payload's digest
cannot merge their histories or their permissions.

The contract defines a finite dependency boundary. Every dependency required
for the requested use MUST resolve to the declared version and pass its
applicable check. References retained only for documentary context may remain
unresolved when the contract explicitly permits that limited use. A receipt
must make that distinction visible. Importing a record never imports its
checker authority merely because the record names a checker.

## Observations and acceptance

An exchange is recorded through causally related local events, not one global
success flag. The receiver's observation and the sender's knowledge can differ:
the receiver may have accepted a presentation while its reply is still absent
at the sender. Clock order alone is not a causal proof.

Reception precedes an acknowledgment or acceptance that cites it. Checking can
precede or follow an acknowledgment of reception. Acknowledging a refusal or
an unresolved outcome is meaningful, and acceptance does not require inventing
a previously unobserved acknowledgment. The protocol profile must specify any
stronger ordering it needs.

For one presentation `p`, receiver context `r`, contract `c` and requested use
`u`, the framework requires:

```text
accept(p, r, c, u) requires
    a bound receiver observation of p
    + an applicable, versioned c in r
    + all checks and dependencies required by c for u
    + the retained evidence, residuals and resource account
    + c's permission for precisely u
```

This is a specification obligation, not executable syntax or a new inference
rule in the native kernel. An implementation must supply the concrete
predicates and demonstrate that its acceptance path enforces them.

Reports MUST separate at least: arrival, integrity/representation checks,
semantic checks, acceptance for the named use, and observation of any reply.
`NotRun`, `Rejected`, `Unknown` and a scoped successful check must retain their
different reasons. Exhausted resources, missing replies and unavailable
required checks do not prove a mathematical negation or imply consent.
An exchange can finish with a refusal while all mathematical obligations stay
open. Successfully communicating an `Unknown` result does not solve its task.

Acceptance is relative to the named context, contract and use. A changed
theory, checker, destination or purpose requires a new receiving judgment.
An old receipt may be cited as history but MUST NOT be silently broadened.
A correction or reopening records its predecessor and reason; it does not
erase an earlier event.

## Continuity, repetition and composition

1. **Preserve the source.** Retain origin, version, assumptions, evidence and
   unresolved obligations. Receiving or recataloguing does not rewrite their
   earlier meaning. Explicitly record any representation change and its check.
2. **Retain distinct judgments.** Transport integrity, receiving-contract
   checks, native import, mathematical verification and human acceptance keep
   their own scopes. A receipt is not automatically a Rust `Seal`.
3. **Account for repeated delivery.** Within the contract's declared identity
   and retention scope, replay of the same logical exchange must refer to its
   prior disposition without duplicating an acceptance effect or resource
   grant. Rechecking costs are still counted. Conflicting payloads under one
   exchange identity must be refused. Global exactly-once delivery is not
   assumed; crash recovery and concurrency need their own protocol guarantees.
4. **Check each receiving boundary.** If A communicates with B and B with C,
   C must receive under C's own contract. B's acceptance is evidence to inspect,
   not a transferable permission. A changed presentation records a derivation
   or correspondence; an unchanged relay retains its original source.
5. **Make continuation explicit.** Neither a reply nor a new directory entry
   renews fuel, executes received code or schedules another exchange. Any such
   action needs its own declared allowance and required native checks.
6. **Retain partial outcomes.** If recording, reply delivery or another stage
   fails, preserve the observations that actually occurred. Do not claim a
   durable receipt or completed migration when its required record is absent.

These are obligations for an implementation, including its resource and
recovery model. They are not distributed-system guarantees obtained by naming
the five events.

## Repository and library migration

The intended migration is an exchange of declared content between interfaces.
The receiving contract binds the existing catalog key, owning topic, material
and evidence versions, checker requirements, and intended destination use.
The receiver produces a new record referring back to that source. A change of
owning topic is a separate catalog revision with its own justification;
cross-topic references remain references rather than derivation parents.

Operating-system storage and Git can implement a transport or persistence
backend. Direct copying, moving, renaming, or Git synchronization MUST NOT be
treated as completing the Adva exchange or granting a new catalog home. A
host script named `communicate` is insufficient unless its receiving contract
and effect boundary are implemented and checked. Until the required operation
exists, retain the current content and references and record the missing
capability instead of bypassing it with file rearrangement.

Ordinary source-code and specification authoring remains engineering work.
Writing this specification does not count as a `communicate` execution or as
the transfer of an existing knowledge object. This distinction allows the
mechanism to be implemented without pretending it already exists.

For a library migration, source retirement is a separate effect after checked
reception and dependency continuity. No successful transfer grants implicit
deletion rights. Frozen evidence remains tied to its original paths/revisions
or to an explicitly checked resolution route. The current Pascal-rooted
geometry obligation remains `Open`, with native `Seal` `NotIssued`.

## Worked boundary cases

These are specification examples, **not executed conformance results**.

| Situation | Required reading |
| --- | --- |
| Files arrive with matching byte pins, but a required proof checker is absent | Reception/integrity can be recorded; proof admission remains unavailable and the requested proof-dependent use is not accepted |
| A proposal is accepted for documentary cataloging with its obligations intact | That scoped catalog use is accepted; its mathematical claims retain their original status |
| An acknowledged message has a false or unsupported claim | Acknowledgment remains valid as a reception event; the claimed conclusion is not thereby accepted |
| The sender has no reply at the deadline | Sender-side disposition is `Unknown`; do not invent receiver refusal, consent or non-delivery |
| A received counterexample invalidates a prior assumption | Record the checked counterexample and a scoped reopening with the earlier record retained |
| The same logical exchange arrives again | Resolve against the prior disposition within the declared retention scope; do not repeat its acceptance effects or replenish fuel |
| The same bytes are offered for a different theory or use | Require a new receiver judgment; byte equality does not transfer the earlier permission |
| B forwards A's result to C | Preserve A's origin and B's forwarding event; C applies its own receiving contract |
| A required record cannot be durably saved | Record or surface the partial failure; completion must not be asserted |
| A directory move loses a dependency or its checked resolution route | The migration is incomplete, regardless of filesystem success |

## Existing evidence and implementation requirements

The following existing components inform this specification:

- [Research 0139](../../docs/research/0139-library-six-phase-and-communication.md#minimal-communication-proposal)
  distinguishes send, receive, acknowledge and accept.
- [Research 0158's working vocabulary](../../docs/research/0158-evidence/downward-interpretation-v0/downward-interpretation-v0.md#7-proposed-operational-placement-of-the-working-words)
  places `communicate` at an interface capable of checking a scoped return.
- [ADR 0020](../../docs/adr/0020-research-neutral-adva-document-persistence.md)
  supplies checked graph persistence with an explicit limitation on what loading
  establishes. It does not implement this exchange.
- The [library's native-load acknowledgment](../../adva-library/symbol-surface/receipts/native-load-v0/README.md)
  checks a fixed reply against its handoff, retains nine open obligations and
  refuses several forms of scope inflation. It is an external documentary
  receiver, not a general native communication primitive.

A first executable profile must define actual input/output schemas, local
state transitions, checker binding, permitted effects and finite limits. Its
conformance cases must include accepted documentary use, a refusal, an
unavailable required check, repeated delivery, context mismatch, lost reply and
interrupted recording. Native identities and mathematical judgments still pass
through the appropriate Rust admission/checking boundary. A broader transport,
concurrency or hostile-input claim requires its own evidence.

The first profile should address one existing library entry and one local
receiving interface. It must preserve that entry's home, sources and residuals
before a larger migration is attempted. Designing that profile is the next
implementation task; this adoption does not claim it has run.

## Related work and limits of the comparison

[DeYoung, Caires, Pfenning and Toninho, CSL 2012](https://doi.org/10.4230/LIPIcs.CSL.2012.228)
relate linear-logic cut reduction to asynchronous session communication under
a specific process typing. That motivates making interface rules explicit;
Adva has not obtained their metatheorems merely by adopting this vocabulary.

[W3C PROV-DM, 30 April 2013](https://www.w3.org/TR/2013/REC-prov-dm-20130430/#term-Communication)
models communication through an entity generated by one activity and used by
another, and distinguishes derivation. It provides a useful comparison for
origin and event records. No PROV encoding, conformance or semantic identity
mapping is specified here. The Adva receiving and acceptance obligations above
are this framework's explicit design choices.

Finite participants can exchange constructions and unresolved questions while
exploration remains open. The scope of a receipt is the declared observation,
not a closure of the universe or an author's authority over arithmetic truth.
