# ADR 0050: Anchor the free process and distinguish transport from communication

Date: 2026-09-16. Status: framework distinction adopted; free process is an
operational research specification with a bounded external calibration.
Direction: Mingli Yuan. Original specification, implementation, review and
measurements: ChatGPT (OpenAI), contributed under Unknown v0.3 through Mingli
Yuan's authorized account proxy; account use is not his review, endorsement or
correctness guarantee.

## Problem and resulting boundary

The earlier free acceptance candidate names a terminal obligation gate without
completing the process that reaches it. Mingli identifies the common starting
anchor, three-sided internal pressure and approach to balance as the unfinished
`free`. He also clarifies that the current homogeneous file/directory crossing
is `transport`; heterogeneous interfaces require `communicate` to seek a common
interpretation. A transported document or an intact certificate binding cannot
by itself establish that interpretation or free acceptance.

Adopt [framework vocabulary v2](../../spec/framework/transport-communication-v2.md)
for new designs. Its registry binds the successor and the unchanged v1 registry.
Retain v1 command names and receipts, including `adva communicate` and
`CompletedDocumentaryExchange`, with their original documentary scope.
There is no new `adva transport` CLI alias. The current documentary receiving
route implements transport in this refined vocabulary.

Specify [free process v0](../../spec/framework/free-process-v0.md) with a common
initial contract, declared correspondences, pressure and allowed adjustments,
retained residuals, a finite resource account, scoped balance and separate
acceptance/release conditions. Where sides are heterogeneous, initial semantic
correspondences can remain proposals: a common inquiry is not an assumed
solution to its interpretation problem.

The historical basis remains visible: 0037 supplies the marked three-chart
carrier; 0048 separates directional energy and hidden residuals; 0072 separates
projected and lifted closure; 0139/0143/0157 retain free's open boundary; 0166
distinguishes binding from a falsifiable interpretation check. Research
0192/0193 retain the exact `33/100` side shares and separate `1/100` joining
reserve proposal, with model-dependent cost and optimality limits. Failed joins
do not advance the committed checkpoint, but their spent resources are retained.
The earlier records are read as scoped historical evidence, not rerun here.

## Executed finite calibration

The [experiment](../../experiments/triadic_free/README.md) uses an original
integer A2 fixture with `p=2`, `q=-2..4`, three supplied chart correspondences
and strictly descending unit moves in `q`. A separate parity-cube feature
provides a retained energy residual. The independent replay logic uses explicit
coordinate formulas and a complete finite energy table; it shares the Python
runtime and integers with the producer.

One designated invocation ran after source/specification pins were fixed:

```sh
python3 experiments/triadic_free/calibration.py \
  --contract experiments/triadic_free/contract-v0.json \
  --expect-contract 9d18afea949412235d02ced974211791c760c40050643474c45a985152482da9 \
  --output /tmp/adva-triadic-free-20260916-v0-run01.json
```

The [retained report](../../experiments/triadic_free/evidence/run-01.json) is
22,388 bytes, SHA-256
`449282a82b7c746a6bcd64a7d748177e4dddf0fae19e953623d449a3f0243f7c`.
It includes the full contract, 14 checked source/reference inputs, ten case
traces, independent replay dispositions and resource observations. The raw
contract file SHA-256 above differs intentionally from the canonical JSON
contract binding embedded in frames:
`af87ae8116ca2e41de464e1b0a3ee6bc8433985477a5244af6b51cd82ed73f17`.

| Measured condition | Result |
| --- | --- |
| Relaxation from `(2,0)` or `(2,2)` | One update to `(2,1)`, energy 4 to 3, allowed pressure zero |
| Already balanced, including a declared nonblocking residual | FiniteBalanceWitness; residual remains in the record |
| Hidden energy `(4,4,4)` above its allowance, despite coarse energy zero | BlockedByResidual |
| Missing residual, missing third reading, or required human acceptance absent | Unknown with the corresponding reason |
| Closed chart cycle without update allowance; one update with further motion needed | Unknown; actual reached states retained |

All ten expected outcomes matched: four finite balance witnesses, one blocked
case and five `Unknown` cases. These are outcomes of the fixture, not ten
successful native free executions. Constrained balance retains energy 3 and
reaction pressure 3 along the fixed `p` direction. A closed chart cycle alone
does not establish balance.

The invocation used 42 counted work units, 7.854 ms wall time and 7.626 ms CPU
time before final encoding/write. Linux peak RSS was 136,808 KiB; the process
used Python 3.14.4. It made zero native calls and zero automatic retries. The
10-second wall, 5-second CPU, 256 MiB address-space and 512 KiB output limits
also cover final output; reported elapsed times exclude that last write.
Authoring, tests and publication review are separate engineering costs. This
measurement supplies no native performance comparison or real join-cost model.

## Verification and publication

All **111 targeted tests passed** in 6.19 seconds, including 31 new profile
controls. The regression set covers the new profile plus the earlier tricusp, directional
energy and unit-tangent controls, the surface-contract succession, toolchain
source/evidence continuity and the existing exchange routine. The new controls
refuse rehashed wrong anchors, fabricated charts/pressure, deleted residuals,
skipped history, false native authority and external effects. Interrupted or
refused replay retains a candidate without issuing a witness. The retained
report is also replayed against the committed contract and source pins.

The [structure card](../../exchange_routine/examples/free-process.json) passes
the existing v1 shape checker with nine objects, eight relations and four open
questions. Shape checking does not verify its philosophical or mathematical
claims. The card preserves the user's terminology, the experimental boundary
and the missing interpretation/cost evidence.

ChatGPT reviewed the exact original code, prose, synthetic fixtures and report
before publication. The report was first written outside all repositories;
its bytes contain this original contract, elementary computed integer cases,
source digests and host measurements. Historical texts are referenced and hashed,
not embedded. No third-party expression or external dataset was incorporated.
This explicit Unknown contribution and actual author/proxy attribution serve
as the routine first-party origin record. Retaining this reviewed engineering
evidence does not claim a knowledge/library content migration or an executed
Adva transport. Source retirement is not an effect of this change.

## Remaining work

Native free remains `NotImplemented`. This calibration assumes its chart
relations; it does not discover a shared interpretation between heterogeneous
participants, implement the three-share/reserve policy, establish the intended
three-computation identification, or authorize release effects. Its balance
result remains an external finite arithmetic witness.

The next communication boundary needs two concrete heterogeneous readings and
one scoped falsifiable relation, with actual local observations, retained
counterexamples and measured checking costs. The next native free boundary
additionally needs a Rust-checked task, its real three-side correspondences,
protected obligations, balance evidence and a versioned release checker. The
earlier source paths, native semantics, library pin, evidence and consumer
contracts remain unchanged and must stay replayable.
