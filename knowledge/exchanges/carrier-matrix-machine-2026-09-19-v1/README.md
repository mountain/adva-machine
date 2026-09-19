# A carrier received by the machine interface

Seven original files implementing the
[carrier matrix v0 profile](../../../spec/framework/carrier-matrix-v0.md) have
been received by the machine interface through the bounded
[documentary exchange profile](../../../spec/framework/documentary-exchange-v1.md).
This record is the **machine** reception and its post-arrival check.

## Executed result

The documentary route ran end to end with the compiled Rust CLI:

| Step | Result |
| --- | --- |
| `send` | `Sent`; envelope `a77efeb04ace1bd03914bd93e57702dae1cd3918bba9a4686a4354b5124b8185` |
| `receive` | `AcceptedDocumentary`; receipt `cf3ee36d1051c6a856f6245c1ac41b2045c933263ffe7c6b3589044d96c30a01` |
| `acknowledge` | `Acknowledged`; observed receiver status `AcceptedDocumentary` |

Receipt fields keep the profile's separations: `native_admission` is
`NotGranted`, `semantic_verification` is `NotRun`, `accepted_use` is
`documentary-reference`, and `rights_determined_by_machine` is `false`.

The [receipt](receipt.json) and the [sender acknowledgment](sender-acknowledgment.json)
are retained. The publication record is a **self-review** by the same agent that
authored and checked the materials; it is not independent verification, and the
receipt's own residual says so.

## The post-arrival check

The [run record](../../received/carrier-matrix-machine-2026-09-19-v1/run-record.json)
reports `CarrierMatrixChecked` over the **received** bytes: 266 assertions, nine
controls, 159,835 counted work units. The received materials are byte-identical
to the source materials, the package digest is the same on both sides
(`c5020b7b...`), and re-running the checker from the received directory returns
the same witness digest.

Two guards are load bearing and are the reason this profile carries them:

* the **non-vacuity** guard, because the matrix-unit law holds `81/81` for an
  identically zero family, so the law alone certifies nothing;
* the **control-bite** guard, because a control whose measured quantity does not
  differ from the clean case is inconclusive and is reported as `Unknown`.

Both were exercised adversarially before the exchange: seven corruptions were
refused with the right reasons after their package pins were recomputed, and a
decoy change to unread prose was still accepted.

## What this exchange does and does not establish

It establishes that one reviewed original entry crossed the interface, that the
receiving route's integrity and contract checks passed, and that the received
bytes still pass the profile's own checker.

It does **not** establish native admission, semantic verification, independent
review, or that the origin resolves: the origin revision is a **local** commit of
this repository and is not pushed. The receiver neither fetches it nor claims it
resolves. No library, epoch, pin, geometry obligation or Seal status changed.
