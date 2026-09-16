# A compact structure exchange routine

Status: implemented local routine, version 1, 2026-09-16. English is primary.
Authored by ChatGPT (OpenAI), contributed under Unknown v0.3 through Mingli
Yuan's authorized account proxy; account use is not his review or endorsement.

Use a **structure card** to share a question without repeating the entire
discussion. Use the **exchange runner** when reviewed library materials must
actually cross a receiving boundary. The card supplies documentary content;
the runner invokes the existing Rust profile and retains its observations.

## The conversational routine

A person can write these six fields in ordinary language; an assistant can
fill the explicit JSON representation. Missing information remains visible.

```text
Question: what should the recipient help decide?
Objects: the relevant things and what their names mean here.
Relations: A --named relation--> B, with proposed/reported/discussion status.
Preserve: assumptions, sources, obligations and distinctions to retain.
Open: missing evidence, disagreements and unfinished connections.
Reply requested: the bounded response or next step being requested.
```

The response routine is:

1. **Restate** the structure briefly, retaining the names and directed relations.
2. **Locate differences**: distinguish what the sender proposed, what the
   recipient inferred, and what remains ambiguous or unsupported.
3. **Return one bounded continuation**, or an explicit unresolved result.

For another round, name the previous card and describe only the changed
objects, relations, conditions or questions. Keep the earlier card, produce a
successor with the changes applied, and compare them. A deleted open question
is highlighted; its removal does not discharge the underlying obligation.
Natural-language deltas are interpreted by the participants, not automatically
applied as repository edits or proof transformations.

The shared short request can be **"exchange this structure"** (Chinese:
**"按结构例程交流"**). This invokes a discussion convention, not a registered
Lisp operation, mathematical judgment or permission to publish/move content.
No response is fabricated for an absent person or agent.

The [knowledge organization card](examples/knowledge-organization.json)
condenses the preceding discussion: interaction, experience, concepts,
mathematics, arithmetic/geometry/logic and physical realization. Its proposed
relations retain their attribution and open questions. This example does not
claim that a general theory of concept formation has been verified.

## Inspect and compare cards

Use the existing project Python environment with its `blake3` dependency:

```sh
python adva-exchange show-structure exchange_routine/examples/knowledge-organization.json
python adva-exchange check-structure exchange_routine/examples/knowledge-organization.json
python adva-exchange compare-structures previous.json successor.json
```

These commands read files and print results; they do not write or transmit
materials. `show-structure` retains every card field. `check-structure` checks
shape, unique object identifiers, relation endpoints, declared status/basis
and size limits. `compare-structures` binds both exact input digests, shows a
documentary difference and lists removed preservation requirements/questions.
It does not decide semantic equivalence or accept a proposed revision.

`adva.structure-card.v1` requires exactly `schema`, `id`, `question`, `origin`,
`objects`, `relations`, `preserve`, `open_questions` and `request`. Objects have
`id` and `meaning`. Relations have `from`, `relation`, `to`, `status` and `basis`.
Allowed relation statuses are `proposed`, `reported` and
`adopted-for-discussion`; none is a native proof certificate. A reported result
still needs its independently applicable evidence/checker before reuse.

Limits are 32 KiB per UTF-8 JSON card, 32 objects, 64 relations, 16 preservation
requirements and 16 open questions, and 2,000 characters per prose field.
Duplicate JSON fields, duplicate objects/relations, undeclared endpoints and
control characters are refused. Array order is retained. IDs are document-local
coordinates, not native `SourceId` or authenticated participant identities.

## Execute a reviewed exchange with one command

Prepare one request using [request.template.json](examples/request.template.json).
Its zero digest placeholders are deliberately unusable. Select the trusted
binary, contract, publication record and receiving context independently, then
pin the request's SHA-256. A matching digest alone supplies no review or rights.

```sh
python adva-exchange run request.json --expect-request REQUEST_SHA256 \
  --output /tmp/adva-exchange-run-01
```

Paths in the request are relative to that request file, or absolute. It fixes:

| Field | Meaning |
| --- | --- |
| `schema` | `adva.exchange-routine.request.v1` |
| `binary` | Trusted Rust `adva` executable path and SHA-256 |
| `contract` | Existing receiving contract path and BLAKE3 |
| `publication_record` | Completed review record path, also bound by the contract |
| `source` | Local source library root |
| `receiver` | Already-existing store directory, independent `name` and `context` |
| `acknowledgment` | `null` for a native acknowledgment in the new audit's `sender/` directory, or a fresh explicit sender path with an existing parent |
| `structure_member` | A contract member's source path when a structure card is being sent; `null` for another supported documentary entry |

The audit directory must be fresh and outside all repository directories. It
retains the request, contract, review record, fixed plan, native envelope, four
unchanged stdout/stderr observations, process resource accounts and final result.
Producer source digests and the Python version are retained in `producer.json`.
Transported
materials and receiver receipts are written only by the Rust commands. With
an explicit acknowledgment destination, Rust writes it there; otherwise it
writes `sender/acknowledgment.json` in the audit. The result records both paths
and their exact bindings. Publication of audit outputs requires its own review.

The runner performs exactly this bounded plan, stopping at the first failure:

```text
send-1:    Rust send
receive-1: Rust receive
replay-1:  Rust receive again, requiring zero new acceptance effects
ack-1:     Rust acknowledge the actually observed receipt
```

An already accepted exchange can be explicitly checked again with the same
request and a fresh audit directory. This is a separately accounted invocation,
with zero new acceptance effects. It is not an automatic retry. An explicit
acknowledgment path must remain fresh; using `null` avoids editing that path
between independently requested audit runs.

The existing profile accepts one original documentary `logic` entry with a
null proof checker, empty evidence and preserved obligations. To send a new
structure card, first provide its source entry, exact material pins, completed
publication review and receiving contract under that profile. A card checker
pass alone cannot register a library entry or authorize transport. A present
`structure_member` must be that actual bound payload, not an unrelated planning
attachment. Rust carries its bytes; Python only checks its documentary shape.

## Bounds, partial outcomes and trust

The supervisor has 30 wall seconds, 25 aggregate CPU seconds, at most four
native child calls and 8 MiB audit artifacts. Its existing process controller
enforces child CPU, address-space and output-file limits and kills only the
child process group on wall timeout. Requests are limited to 32 KiB, contract
and review to 256 KiB each, binary hashing to 256 MiB, and final binding reads
to the existing envelope/receipt bounds. Native calls retain their own finite
contract budgets. Build, input authoring and independent publication review
precede the run and are outside its execution measurements.

`CompletedDocumentaryExchange` requires all four Rust dispositions and matching
retained envelope, receipt and acknowledgment digests. Native `Rejected` and
`Unknown` propagate with the reached stage; supervisor validation failures
report `Refused`. CLI exits are 0 for a completed action, 2 for refusal/rejection
and 3 for an unresolved run. Raw observations and partial artifacts remain
available. The final report distinguishes the receiver observation from what
the sender has observed. A missing final report or reply never implies consent.

No pending native stage or lock is cleared, no source is retired, no checker is
replaced, no budget is renewed automatically and no branch is published by this
routine. The binary, local paths and quiescent POSIX environment are trusted
inputs; this is not a sandbox for hostile binaries or concurrent filesystem
attackers. Origin Git revisions must be checked by the operator; the runner
does not fetch repositories or authenticate endpoint claims.

The frozen native profile source, contracts and existing toolchain evidence
remain unchanged. See [ADR 0049](../docs/adr/0049-compact-structure-exchange-routine.md)
and [Communication v1](../spec/framework/communication-v1.md) for the boundary.
