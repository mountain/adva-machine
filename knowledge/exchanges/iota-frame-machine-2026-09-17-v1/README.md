# A common frame received by the machine interface

The same eight-file iota frame package has been received by adva and
adva-machine. This record is the **machine** reception and its actual
post-arrival check. The [frame specification](../../received/iota-frame-machine-2026-09-17-v1/materials/frame.md)
binds iota source/process, explicit domain boundaries, cut basis, complex
structure J, exponential rule, metric, observer, clock and residuals.
Iota remains the sole source combinator; e and i are interpretation structure.

## Executed result

The [frame result](frame-result.json) is `FrameCovarianceChecked`:
**4,062 assertions**, twelve frames over four selected processes, exact rational
coefficients through degree twelve, and seventeen controls. All twelve previous
term/ledger families were freshly checked. This run used
2,028,019 counted host units, 6.750 s wall,
6.616 s CPU and 96504 KiB peak RSS.
The retained mathematical witness matches the source and other receiver exactly.
All three runs used the same author/checker, not independent verification.

The frames use identity, nonorthogonal scaling and a shear mixing a real and
imaginary coordinate. They check J squared = -I, operator/metric compatibility,
conjugated exponential coefficients, observer covariance, Wick coefficients,
metric unitarity coefficients and the bivariate heat semigroup coefficients.
The degree-12 tail bound is 3/13! for absolute parameter <=1 in the transported
metric. Truncated polynomials are not asserted to be exactly unitary.

The negative controls reject omitted metric or observer, false J, changed H,
missing cuts, changed domain/history, extra source e, changed factorial law,
clock/parameter conflation, split simultaneity, fuel refill and singular chart.
The wrong Wick sign has a nonzero first-coefficient residual. The unchanged
operator under changed domain policy requires retaining the process residual;
equal cut dimensions can have different operators. Missing evidence stays Unknown.

This gives frame a concrete interpretation role: it carries the correspondence
among the generator, complex structure and exponential reading, including what
the operator forgets. It does not make them the same kind of object.

## Transport and interpretation remain separately recorded

[Transport](transport-result.json) completed Sent -> AcceptedDocumentary ->
AlreadyAccepted -> Acknowledged. Actual acceptance effects were one, then zero
on replay. The [native receipt](../../received/iota-frame-machine-2026-09-17-v1/receipt.json) still records
semantic verification `NotRun` and native admission `NotGranted`.
The [sender acknowledgment](sender-acknowledgment.json) records the actual reply.
The four native calls took 0.174 s wall and read
1,067,183 aggregate bytes. There were no new native
object executions: previous identity/discard/copy runs are historical evidence.

The package is 76,118 bytes, SHA-256
`3a05875e0134684978c81ef3bdb2d6a2a4455403fa5d9901856df6e28f1337a7`. Source revision:
`1a7041d8b714c695a7a9a8ea23f78fb70c7e151a`. The [contract](contract.json),
[delivery plan](delivery-plan.json), and [archive inventory](evidence-manifest.json)
retain all pins, exact outputs and costs. Original content admission is recorded
[here](../../../governance/publication/records/iota-frame-machine-2026-09-17-v1.json);
receiver output review is [separate](../../../governance/publication/records/iota-frame-machine-2026-09-17-v1-outputs.json).

The existing pointwise exp builtin, native GraftFrame and research
TransitionFrameV0 keep their meanings. This research frame adds no native
complex scalar, general Frame type, PSC0 identity mapping or process exponential.
Full ancestry, nested boundary calculus and physical semantics remain open.
No global dependency lock, catalog or frozen evidence was changed.

## Reproduce

Use Python 3.11+ standard library, the exact current and previous material
packets, and a fresh output directory:

    python knowledge/received/iota-frame-machine-2026-09-17-v1/materials/check.py \
      --materials knowledge/received/iota-frame-machine-2026-09-17-v1/materials \
      --iota-materials knowledge/received/iota-process-machine-2026-09-17-v1/materials \
      --expect-package 3a05875e0134684978c81ef3bdb2d6a2a4455403fa5d9901856df6e28f1337a7 \
      --stage machine-after-reception --output /fresh/external/frame-check

The archives contain the complete executed witnesses, request, native outputs
and counters. Transport reproduction separately binds the trusted binary,
receiver context, exact reviewed payload and original request in a fresh audit.
The checker alone does not perform a transport or grant native acceptance.

Original report and checking: Codex (OpenAI), contributed under Unknown v0.3
through Mingli Yuan's authorized account proxy; not his authorship, review,
endorsement or correctness guarantee.
