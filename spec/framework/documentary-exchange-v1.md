# Documentary library entry exchange, version 1

Status: bounded Rust CLI profile, 2026-09-16. Implements one local receiving
route under [Communication v1](communication-v1.md). General communication,
network transport, native proof admission and source retirement remain open.
English is primary. Authored by ChatGPT (OpenAI), contributed under Unknown
v0.3 through Mingli Yuan's authorized account proxy, without his endorsement
or technical review.

## Operational boundary

`adva communicate` supplies `send`, `receive` and `acknowledge`. Its receiving
path performs the profile's integrity checks and `accept` decision. These are
compiled Rust CLI operations; they do not introduce a stable Lisp builtin,
IR instruction, native `SourceId`, proof checker or `Seal`.

This profile accepts exactly one library entry with home `logic`, status
`proposed-document`, explicit null `checker` and `geometry_lineage`, and empty
`evidence`. It retains the complete catalog entry, including assumptions,
reuse requirements and open obligations. Permitted use is solely
`documentary-reference`; the original catalog remains the entry's home.
References inside the entry and its files remain source-relative documentary
references at the pinned origin revision. The receiver does not fetch or
execute them, and does not claim they resolve in its new directory.

The local operator chooses the receiving store and independently supplies its
receiver name, context and expected contract digest. A matching string is not
endpoint authentication. The operator must establish the checkout revision
and build provenance; source coordinates are retained claims. The trusted
build is fixed in each run record; the contract additionally binds BLAKE3 of
the exact compiled checker source and Cargo.lock. A different installed checker
returns `Unknown` and cannot substitute its own behavior.

## Contract and encoding

The executable schemas are the strict `Contract`, `Member`, `Checker`, `Origin`
and `Envelope` types in
[`communication_cli.rs`](../../crates/adva-witness/src/bin/support/communication_cli.rs).
Unknown fields in those types and duplicate JSON keys at any depth are refused.
Floating-point values are outside the input profile. JSON byte pins are BLAKE3
of exact bytes. The catalog entry pin uses compact, UTF-8 JSON with sorted
object keys, retaining array order; its original prose is not normalized.

The contract schema is `adva.communication.contract.v1`, with these fields:

| Field | Required meaning |
| --- | --- |
| `profile` | `documentary-library-entry-v1` |
| `exchange_id`, `entry_key` | Scoped ASCII identifiers, at most 96 characters |
| `sender`, `receiver`, `context` | Declared local interfaces and receiving context |
| `purpose`, `home` | `documentary-reference`, `logic` |
| `origin` | GitHub repository, full revision, source catalog path and BLAKE3 |
| `entry_blake3` | Pin of the entire selected catalog entry |
| `publication_record_blake3` | Pin of the independently completed review record |
| `checker` | `implementation_blake3` and `cargo_lock_blake3` of compiled inputs |
| `files` | Ordered `source`, `destination`, `bytes`, `blake3`, `sha256` per member |
| `read_budget` | Total bytes read per explicit invocation, at most 8 MiB |
| `dependency_policy` | `retain-references-no-execution` |

Every source material in the catalog entry must occur in the contract in the
same order, with its catalog SHA-256. Source paths are relative to the library
root; destinations start `materials/`. Canonical relative paths use ASCII
letters, digits, `.`, `_`, `-` and `/`, with no empty, `.` or `..` components,
at most 200 characters and eight components. Duplicate sources, duplicate or
overlapping destinations and symbolic links are refused.

The publication record must have schema `adva.publication-admission.v1`, status
`admitted`, basis `project-original`, an identified reviewer, complete required
provenance, reviewed components/outputs and no unresolved eligibility questions.
Its ordered file list binds exact destination paths under
`knowledge/received/<exchange_id>/`, sizes, SHA-256 and BLAKE3. This profile
does not yet support CC0 or other public-domain intake bases.

Rights review is an independent workflow obligation under
[PUBLICATION_BOUNDARY.md](../../PUBLICATION_BOUNDARY.md). The code checks a
bound review record's required facts and payload coverage; it does not determine
rights or authenticate the reviewer. SHA-256 is computed and checked against
the original catalog during review. Rust checks its consistent retention and
checks actual transported bytes using size and BLAKE3; it does not recompute
SHA-256. No hash or `admitted` string grants rights on its own.

## Commands and local events

All commands require `--contract`, independently obtained `--expect-contract`
and an explicit `--attempt` coordinate. Attempt names label local observations;
they are not native identities and their global uniqueness is not claimed.

```text
adva communicate send --contract C --expect-contract H --attempt send-1 \
  --source LIBRARY --publication-record P --output ENVELOPE
adva communicate receive --contract C --expect-contract H --attempt receive-1 \
  --envelope ENVELOPE --publication-record P --store knowledge/received \
  --receiver RECEIVER --context CONTEXT
adva communicate acknowledge --contract C --expect-contract H --attempt ack-1 \
  --envelope ENVELOPE --publication-record P --receipt RECEIPT --output ACK
```

1. `send` checks the source catalog and all selected bytes against the contract,
   then writes a fresh `adva.communication.envelope.v1`: contract digest, complete
   entry and ordered byte arrays. `Sent` leaves receiver observation `Unknown`.
2. `receive` checks the independent context, records arrival, checks the envelope
   and reviewed contract, and exclusively locks the exchange in the store. It
   writes materials and `receipt.json` in a private pending directory, checks
   their exact inventory and bytes, syncs files/directories, and renames the
   completed directory into its exchange slot. `AcceptedDocumentary` permits
   only the named documentary use. Filesystem operations implement this checked
   boundary; an external copy command cannot issue its receipt.
3. The receipt binds contract, envelope, source, complete catalog entry, files,
   checker, publication record, resource limits and retained residuals. It
   explicitly reports `semantic_verification: NotRun` and
   `native_admission: NotGranted`.
4. An explicit repeated delivery rechecks the old receipt, exact file/directory
   inventory and payloads. `AlreadyAccepted` records zero new acceptance effects
   and retains the same receipt bytes. A conflicting exchange is refused.
5. `acknowledge` checks an actually supplied reply against the exact expected
   receipt and writes a fresh acknowledgment referring to its byte digest.
   It does not independently recheck the receiver's current storage. A missing
   reply produces `Unknown`; no agreement or non-delivery is inferred.

Each invocation prints a JSON observation with its action, attempt, supplied
contract pin, reached events, bytes read, elapsed time and outcome. Retain these
observations alongside the receipt: they account for dispatch, checks, repeated
delivery and reply observation separately. The deterministic receipt records
the disposition, not a fabricated global event clock or variable run costs.
Code 0 means the reported scoped action completed, 2 means `Rejected`, and 3
means `Unknown`. Failure observations assert no completed acceptance effect;
they do not assert that no partial storage effect occurred.

## Bounds, failure and permitted continuation

There are at most eight files, 64 KiB each, 256 KiB payload total, 256 KiB per
metadata file, 2 MiB per encoded envelope, 64 receiver inventory nodes and
8 MiB total read bytes per invocation. A five-second cooperative deadline is
checked between bounded steps. Recording is bounded by these fixed sizes;
there is no recursive dependency import, subprocess, network, implicit retry,
proof execution or automatic replenishment. Each explicit replay is a new
accounted invocation; an enclosing run declares its finite invocation plan.

The store is an already-created, trusted local POSIX directory. Exclusive
lock creation prevents cooperating receivers from writing the same slot at
once. Existing locks and pending records yield `Unknown` and remain intact;
the command never deletes them to restart an interrupted exchange. Completed
stores have their payload/receipt inventory checked before replay can succeed.
Failures after staging retain available partial records. Failures after a
rename may leave a completed destination with an unresolved invocation result;
a later explicitly budgeted check can observe it. A failure report must be
retained rather than replaced with a successful later run.

This is a quiescent-filesystem profile, not protection against malicious local
writers, path races, blocking I/O or arbitrary crash/power-loss behavior. The
cooperative deadline is not an OS watchdog. Interrupted-stage tests establish
the stated retained-state handling, not exhaustive crash consistency. Source
retirement, a new catalog home, execution and mathematical or human acceptance
each require a separately justified receiving/continuation contract.

## Conformance evidence

[`communication_cli.rs` tests](../../crates/adva-witness/tests/communication_cli.rs)
exercise success, context mismatch, changed source/payload/obligations, pending
rights review, unavailable checker, missing reply, repetition, conflicting
identity, altered receipt, symlinks, duplicate fields, finite budget exhaustion,
existing locks and interrupted staging. Fixtures are original project material.
See [ADR 0048](../../docs/adr/0048-bounded-documentary-communication.md) for the
implemented boundary and recorded development failure. The frozen Communication
v1 document and vocabulary registry keep their historical adoption bytes.
