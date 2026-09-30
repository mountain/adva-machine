# Bounded native raw-evidence intake v0

Date: 2026-09-30. Status: research-only finite receiving experiment.
Profile: `adva.native-evidence-intake.v0`. Contract fixed before first execution.
Authored by dot (OpenAI), through Mingli Yuan's authorized GitHub account proxy;
account use is not his authorship, review, endorsement or correctness guarantee.
Project-original code, prose and synthetic fixtures under Unknown v0.3. No
external evidence, package, quotation or software implementation is incorporated.

## Question and preserved boundary

Can one documentary delivery of the same fixed p=x+y*z → q=2*p → p raw proof
be independently checked locally, and then reused twice, without turning its
transport receipt or producer verdict into native authority?

The predecessor is machine commit `89d6f87554f474020de79e59056bce49d8ceb167`,
[checked roundtrip v0.1](checked-roundtrip-reuse-v0.1.md). All its source,
contract and evidence bytes are retained unchanged. The new standalone Cargo
workspace includes the private predecessor module lexically and calls its
unchanged checking APIs. It neither exports nor serializes its checked handle.
Root Cargo files, all `crates/`, library source homes, consumer pins and the
four-epoch/full-ancestry library rule remain unchanged.

This implements only a new strictly bounded *raw input* wrapper. The existing
WitnessStoreV0 insert, CellTemplateV0 form, compiler-derived graft bindings,
fresh instantiation and execute rules remain authoritative. No semantic,
guard, equality, Compose incidence or native identity rule changes. G2/Iota
structural matches are not inputs or premises. There is no general package
loader, cut-certificate verifier, arbitrary Compose or consumer adoption.

## Minimal primitive input and independent binding

The raw proof is one strict JSON record (16 KiB maximum), using strings, integer
triples and fixed-size arrays only. It carries:

- schema/profile; exact judgment, interpretation and three explicit premises
- origin repository, full baseline revision, generator path and BLAKE3 of the
  exact generator source; explicit original synthetic publication provenance
- ordered Construction/Space/Time roles and four named canonical seeds
- two transitions with literal before/after strings and actual/declared signed
  three-role boundary triples; only p/q and the positive unit triple are supported
- one Compose with transition indices 0/1 and Unit seed index 0, followed by
  one Seal whose body is that composition; the whole history is mandatory
- the ordered nonzero guards [p,q,q,p]

Literal endpoint strings select only the two fixed native expression trees;
this is not an expression parser or arbitrary expression decoder. Exact
endpoint incidence and all guards are checked before native Compose. Every
input member is checked; unknown/duplicate fields, noninteger indices, missing
history, foreign seeds, changed guards/roles, additional authority fields or
serialized native structures are rejected. Unavailable bytes are Unknown.
Malformed/unsupported proofs are Rejected, not refutations of their claims.

A separate receiver-binding file is generated from locally compiled expected
source, proof and profile bytes before any sender fixture is received. It is
not an envelope member. The checker invocation independently supplies its exact
BLAKE3, receiver `native-evidence-receiver` and context
`fixed-roundtrip-intake-v0`. The binding retains exact origin, judgment,
interpretation, premises, raw-byte digest, predecessor native source/build
digest and a successor fingerprint. The latter includes the successor source,
manifest/lock, this profile and the retained checker binding, which covers the
unchanged native/compiler source/manifests, root lock and toolchain selector.
The checker reconstructs this expected binding from its local compiled inputs;
a received/re-pinned altered binding cannot authorize itself. Canonically
equivalent JSON with different bytes also fails the raw-byte pin.

The baseline revision is ancestry, not a claim the new fixture existed there.
Exact generator bytes are separately bound, and the subsequent PR fixes the
published source revision. Hashes are integrity coordinates, not endpoint,
software, rights or semantic authentication. Native instance/occurrence IDs
are scoped; retain program/source/occurrence/context tuples.

## Lifecycle and authority

1. The experiment prepares the independent receiver binding and source fixture,
   explicit original-publication review, documentary catalog and contract.
2. Unchanged `exchange_routine.run.execute` invokes the existing Rust
   `adva communicate` send, receive, replay and acknowledge. Its entry remains
   home=logic, checker=null, evidence=[], status=proposed-document, and grants
   documentary-reference only. This locally generated catalog is the fixture's
   source home; no catalog migration or external repository adoption occurs.
3. Delivery observations, acknowledgment and exact receipt bytes are retained.
   The receipt remains semantic_verification=NotRun and native_admission=NotGranted.
4. In a distinct process invocation the new checker reads the received raw
   payload and independently supplied binding. It never accepts a receipt,
   `Verified`, `FormedCellV0`, producer success flag or native serialized summary.
5. Native first_check rebuilds the eight fixed proof nodes and forms the template.
   A private process-local checked object survives only this receiver invocation.
   Two cache uses each recheck native and immutable receiver custody bindings,
   compile fresh contexts, instantiate and execute with all original guards.
   Inputs are [2,3,4] and [5,2,3], producing scoped values 14 and 11.
6. Reports live outside the receiver's stored exchange inventory. Before/after
   receipt bytes, source payload and receiver binding must remain identical.
   Delivery, local first-check, cache-hit and fresh-use costs remain distinct.

Participant A is the synthetic raw-evidence producer, B the local receiver, and
the shared object the fixed guarded roundtrip. Surface is the primitive JSON
and reports, knowledge is the explicitly scoped proof/premises, and substrate
is the unchanged native checker/OS. These are task assignments, not positional
identity of the triadic readings. Producer/receiver agreement does not replace
the native guarded execution evidence. No world observation is fabricated.

## Finite resource and failure contract

No retry, continuation, hidden fuel reset, dependency fetching or networking is
part of this runtime. The fixed supervisor plan has four documentary calls and
three checker subprocesses (binding, fixture, received check). Existing transport
per-call bounds and the supervisor's cumulative limits remain unchanged. Setup,
subprocess elapsed/resource observations and report encoding are separately
reported, not presented as native cache cost. Compilation is separate setup.

Intake has 128 charged operations, 8 MiB cumulative bytes, 16 KiB per input,
strict fixed arrays and a 30-second cooperative deadline. Bounded reads stop
at 16 KiB+1 before parsing. Source hashing and the retained fingerprint's work
are charged, parsing charges input bytes, and post-call checks retain attempted
work. Reports are at most 128 KiB. Native setup/first-check/cache use keeps the
predecessor's separate limits: 256 operations, 8 MiB encoded/source bytes, two
uses, 16 nodes, 32 edges, depth 4 and 128 KiB unique proof ledger; native calls
remain cooperatively checked, with available proof prefixes retained on failure.

The wrapper's input language excludes arbitrary trees before native admission;
its proof storage bounds remain post-operation checks on fixed syntax. Logical
byte/work counts are not actual heap or CPU-instruction measurements. The
quiescent regular-file assumption is explicit; this is not protection against
malicious local writers, path races or blocking filesystem calls. The integration supervisor separately enforces 90 seconds wall time, 75 seconds
CPU including children and 16 MiB retained artifacts; unchanged child execution
installs a 1 GiB address-space limit on Linux. CI adds a standalone native
recheck with a 60-second process timeout, 512 MiB virtual-memory ceiling and
bounded job runtime. Native calls cannot be cooperatively interrupted. An OS kill may
leave partial observations without a complete/resumable report and is never
acceptance. All failures and prior native prefixes remain separately visible.

## Required controls and stopping condition

Controls cover malformed/duplicate/unknown JSON, serialized authority, omitted
history, arbitrary Compose indices, disconnected cancelling endpoints, opposite
boundaries, missing/changed guards, same label in a changed profile, altered
source/build/premise/interpretation/receiver/context pins, noncanonical byte
changes, missing files, exhaustion, fresh/intermediate zero, partial native
proof retention and distinct scoped instances. Existing predecessor tests run
unchanged inside the successor as regression controls. End-to-end tests retain
all four documentary observations and prove the original receipt bytes do not
change when local native checking succeeds or fails.

Stop after this finite receiving experiment and its independent review/CI.
A real consumer, external package, new semantic language, general cut checking,
security/remote-hosting policy or a successor consumer lock is a separate next
decision. This result does not mark all G3 or KPB-14 complete.

Reproduce with the package README. Execution evidence and any corrections are
recorded in a separate results document, never by editing predecessor evidence.
