# A murphy unit received by the machine interface

Eight files of the `murphy` publication unit (`mountain/adva`, admitted
2026-09-19) have been received by the machine interface through the bounded
[documentary exchange profile](../../../spec/framework/documentary-exchange-v1.md).
This record is the **machine** reception and its post-arrival check by the
[research-local Iota substrate](../../../experiments/iota-substrate/README.md)
under the [iota substrate profile](../../../spec/framework/iota-substrate-v0.md).

The transported materials are the named Iota value from Zot word `0001011011`,
its ordinary self-application, the three coordinate permutation programs on the
declared four-slot product, the unit's own replay contract, its upstream source
manifest and its frozen counted witness.

## Executed result

The documentary route ran end to end with the compiled Rust CLI:

| Step | Result |
| --- | --- |
| `send` | `Sent`; envelope `c81c160e39bce705b7dfae68855001345ff7cdfe7a3d9407189e4b913beeb1fe` |
| `receive` | `AcceptedDocumentary`; receipt `8a161fef76845b59d17b83347c5c7743f57543c7f56161e09633c0af3c5f2213`; one acceptance effect |
| `acknowledge` | `Acknowledged`; observed receiver status `AcceptedDocumentary`; new acceptance effects `0` |
| explicit repeated delivery | `AlreadyAccepted`; zero new acceptance effects; same receipt bytes |

Receipt fields keep the profile's separations: `native_admission` is
`NotGranted`, `semantic_verification` is `NotRun`, `accepted_use` is
`documentary-reference`, and `rights_determined_by_machine` is `false`.

The [contract](contract.json), [envelope](envelope.json),
[reviewed publication record](publication-record.json),
[sender acknowledgment](sender-acknowledgment.json) and the
[unchanged command observations](transport-result.json) are retained.

The Python exchange runner was tried first and refused **on this host** inside
its process-limit wrapper (`preexec_fn` failed under macOS). The three declared
commands were then invoked directly against the same contract and publication
record, and their unchanged JSON observations are retained verbatim in
`transport-result.json`. This is a host limitation of the runner, not a change
of the route: the same compiled Rust profile performed the transport.

The publication record is a review by an agent that did not author the
transported materials, but it is a machine review: it is not independent human
verification, and the receipt's own residual says the origin claims are pinned
rather than authenticated.

## The post-arrival check

The [substrate contract](../../../experiments/iota-substrate/contract.json)
reads the **received** bytes and binds each of them to the digest the receipt
records for its destination. The [run result](../../../experiments/iota-substrate/evidence/run-01/result.json)
reports `IotaSubstrateChecked` over five families and 5,348 contractions:

| Family | Contractions | Peak nodes | Verdict |
| --- | ---: | ---: | --- |
| `P` | 893 | 833 | recorded; the unit retains no counted oracle for `P` alone |
| `PP` | 1,808 | 7,627 | matched frozen oracle (`j` 822, `S` 549, `K` 437, digest `8d0434eb…`) |
| `C` | 919 | 9,395 | matched frozen oracle (digest `dc74b1b6…`) |
| `J` | 831 | 7,889 | matched frozen oracle (digest `d40812c3…`) |
| `N` | 897 | 8,545 | matched frozen oracle (digest `66c6cc71…`) |

An independent Rust implementation — a locally written SHA-256, the declared
leftmost-outermost reducer and bracket abstraction — reproduced the origin's
Python-computed witness, including all 1,808 retained trace rows on contraction
path, applied combinator, node count and per-step digest. Six controls passed;
the altered-digest falsifier, the alternative-order control and the
altered-source-byte control are what make the agreement non-vacuous, and the
tight-bound control confirms exhaustion is reported as `Unknown`.

## Why the run record sits here

The substrate result is retained in the exchange directory rather than inside
`knowledge/received/<exchange_id>/`. The receiving profile rechecks an explicit
repeated delivery against the exact inventory it wrote, so an extra file in the
received directory would make that recheck refuse. This exchange keeps the
received directory exactly as the route wrote it — eight materials and the
receipt — so the repeated-delivery result above stays reproducible.

## What this reception does not do

It grants no native admission, installs no operation, retires no source and
creates no new catalog home: the entry remains a proposed document whose home
is the `murphy` unit at `experiments/murphy` in `mountain/adva`. The 2×2 table
adjoint programs and their sixteen assertions, the Zot CEK stage, the text
probe and the declared end-leaf representation bridge are not part of this
package and are not replayed.
