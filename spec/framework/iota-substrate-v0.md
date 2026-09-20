# Iota substrate profile, version 0

Status: **research-local executable profile**, 2026-09-20. This profile uses the
existing research-record vocabulary; it registers no native keyword, operation,
value type, IR version or stable semantic type. Its implementation is the
research crate [`experiments/iota-substrate`](../../experiments/iota-substrate/README.md),
which is deliberately its own workspace root so that the pinned `Cargo.lock`
does not move. English is primary.

DeepSeek Harness (deepseek-v4-flash-vision-exp) authored this profile, the
crate and its checks under Unknown v0.3 through Mingli Yuan's authorized account
proxy; account use is not his authorship, review, endorsement or correctness
guarantee. The transported witness is the `murphy` publication unit in
`mountain/adva` (admitted 2026-09-19), authored by ChatGPT (OpenAI) from Mingli
Yuan's direction.

## Meaning and dependency

The machine had no Iota evaluator. The
[iota interpretation frame](iota-frame-v1.md) binds a minimal iota *process* as
an interpretation profile whose executable part is Python, and the
[carrier matrix profile](carrier-matrix-v0.md) is a Python-checked
correspondence over one checked cut. Both deliberately register no native
operation.

This profile adds one bounded native substrate instead: a Rust parser and
combinator reducer for pure Iota source, checked against an externally frozen
witness rather than against its own expectations. It is a capability statement
about this machine — *the machine can now parse and reduce Iota source in its
own source, under declared bounds, and reproduce an external counting and
digest witness exactly* — and not a claim that Iota is an Adva subset.

The substrate depends on the received unit
[`murphy-iota-machine-2026-09-20-v1`](../../knowledge/received/murphy-iota-machine-2026-09-20-v1/receipt.json)
for its materials, and on the origin's retained step trace, supplied
independently and digest-pinned.

## What is declared

| Element | Declared reading | Retained distinction |
| --- | --- | --- |
| source | `i` is the Iota combinator, `*AB` is application | any other character, and any unconsumed suffix, is refused |
| Iota rule | `j a -> a S K` | `j` is the Iota combinator, **not** the carrier's contraction symbol `iota_j` |
| other rules | `I a -> a`, `K a b -> a`, `S x y z -> x z (y z)` | the three combinators are introduced by the rules, not by the source |
| order | leftmost-outermost | the declared order is load-bearing and separately controlled |
| counting | one contraction per applied combinator, named by it | the Iota/S/K counting here is not the external machine's transition count |
| size | `nodes(t)`: one per application, one per leaf | a tree measure, not a cost or a step count |
| digest | SHA-256 over the canonical encoding `["a",f,x]`, `["c",name]`, `["v",name]`, `["l",name,body]` | an encoding of a term, not a decoded string or a semantic identity |
| coordinate families | the program applied to the four-slot product `Z(p,q,r,s) = lambda k. k p q r s`, through bracket abstraction without eta | an explicit coordinate representation, not a replacement for any proposed Adva list representation |

Bounds are declared per family: a contraction limit, a node limit and a wall
limit. Exhaustion reports `Unknown`; it is never reported as divergence and
never as a proof that no normal form exists.

## Executed finite result

The reception completed through the bounded
[documentary exchange profile](documentary-exchange-v1.md): `Sent`,
`AcceptedDocumentary` and `Acknowledged`, with one acceptance effect, and an
explicit repeated delivery returning `AlreadyAccepted` with zero new acceptance
effects. The receipt records `native_admission: NotGranted` and
`semantic_verification: NotRun`.

The post-arrival substrate run then read the **received** bytes, bound to the
receipt's recorded digests, and reproduced the origin's frozen witness:

| Family | Kind | Contractions | Peak nodes | Verdict |
| --- | --- | ---: | ---: | --- |
| `P` | iota | 893 | 833 | recorded; no frozen counted oracle exists for `P` alone |
| `PP` | iota | 1,808 | 7,627 | matched frozen oracle (`j` 822, `S` 549, `K` 437, digest `8d0434eb…`) |
| `C` | coordinate | 919 | 9,395 | matched frozen oracle (digest `dc74b1b6…`) |
| `J` | coordinate | 831 | 7,889 | matched frozen oracle (digest `d40812c3…`) |
| `N` | coordinate | 897 | 8,545 | matched frozen oracle (digest `66c6cc71…`) |

All **1,808** retained trace rows matched on contraction path, applied
combinator, node count and per-step digest. Six controls ran and passed: the
local SHA-256 against the FIPS 180-4 vectors, the altered-digest falsifier, the
alternative reduction order (which changes both counts and digest), bound
exhaustion reported as `Unknown`, the non-vacuity guard, and the
altered-source-byte digest check.

The executed artifacts are the
[substrate result](../../experiments/iota-substrate/evidence/run-01/result.json),
the [exchange record](../../knowledge/exchanges/murphy-iota-machine-2026-09-20-v1/README.md)
and the [receipt](../../knowledge/received/murphy-iota-machine-2026-09-20-v1/receipt.json).

## The iota-lang case corpus

A second contract, `experiments/iota-substrate/contract-iota-lang.json`, replays
the 17 recorded cases of the external iota-lang reduction contract under the
same declared rules, in a **separately declared case grammar**
(S-expressions over `i` = identity, `k`, `s`, `ι` = Iota, and opaque variables).
The two grammars' `i` tokens denote different combinators; both readings are
declared, they are never mixed, and a control asserts the collision.

All 17 recorded expectations were reproduced in 57 contractions. The run also
compares its own transcription with Research 0167's frozen replay and reports
where they differ; that transcript is never used as an expected value. The
discrimination — which iota-lang material can and cannot test this substrate —
and the two transcription findings are recorded in
[Research 0205](../../docs/research/0205-iota-lang-recorded-contract-replayed-by-the-native-substrate.md).

## What this profile does not establish

- **No native admission.** `ValueType` remains `Real | Bool`. No
  `OperationSpec`, parser surface form, registry change, IR version, schema or
  `Seal` is created, proposed or implied. The substrate is not an Adva engine.
- **No language claim.** It does not establish that Iota is an Adva subset,
  that an Adva program compiles to Iota or vice versa, or that the declared
  rewriting rules agree with any denotational semantics. A normal form here is
  a rewriting result.
- **No divergence or halting claim.** Bounds decide the run; exhaustion is
  `Unknown`.
- **No independent verification.** Two machine implementations by different
  agents agree; neither was reviewed by a person.
- **No equivalence, in either direction.** The case corpus compares a recorded
  string contract with one native reducer. It does not establish that the
  iota-lang machine agrees with this substrate, that the recorded strings are
  iota-lang's intended semantics, or that bounded rewriting is confluent.
- **Not the whole transported unit.** The 2×2 table adjoint programs and their
  sixteen assertions, the Zot CEK stage, the text probe, the retained failed
  reflection control and the declared end-leaf representation bridge are not
  replayed. The coordinate families cover the declared four-slot application,
  not arbitrary Iota syntax; the origin's `C(C(L))` result stays outside it.
- **No process or carrier claim.** The substrate does not reinterpret the
  iota frame, does not identify its reductions with frame exponentials, and
  does not touch the carrier's `Omega`, its sign convention or its requirement
  of a declared real form or grading.

## Receiving and reuse

Reuse requires the received materials at their recorded digests, the receipt
that binds them, the declared rule set, order, counting and encoding, and the
separately supplied origin trace for the step-level comparison. A changed
program changes the reduction; a changed declared rule changes the witness; a
missing binding leaves the comparison unresolved; a failed control refuses the
proposed correspondence rather than weakening it.

The substrate may be extended only as a separately scoped continuation with its
own declared contract: a new family, a wider source grammar, a different
encoding or a different order each require their own finite bounds and their
own retained residuals. Nothing in this profile promotes the substrate into the
stable semantic API, and the promotion gates of the
[research agenda](../../docs/RESEARCH_ENGINEERING_AGENDA.md) are untouched.
