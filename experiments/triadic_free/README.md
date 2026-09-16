# An anchored finite calibration of free

Status: external research implementation, version 0, 2026-09-16. English is
primary. Original implementation, cases and prose by ChatGPT (OpenAI),
contributed under Unknown v0.3 through Mingli Yuan's authorized account proxy;
account use is not his review or endorsement.

[Free process v0](../../spec/framework/free-process-v0.md) records the user's
identification of the anchored three-sided pressure/balance process with the
unfinished `free`. This experiment supplies an executable finite instance of
its anchoring, permitted motion, balance and residual checks. Native free and
the intended three-computation identification remain unimplemented/open.
Following [Transport and communication v2](../../spec/framework/transport-communication-v2.md),
this fixed-chart model supplies no heterogeneous interpretation search. Its
single account also does not implement the `33/100` side allocations and
separate joining reserve discussed in Research 0192 and 0193.

## One fixed task

Use one global integer charge `(p,q)` with `p=2` fixed and `q=-2..4`. Derive
three chart readings `C=(p,q)`, `S=(-q,p-q)`, `T=(q-p,-p)`. All use the A2
quadratic `E=p*p-p*q+q*q`. Permitted motion changes `q` by one and strictly
decreases energy. The pressure along the transported permitted direction is
`2*q-p`, the same in all three charts.

The path `(2,0) -> (2,1)` lowers energy from 4 to 3. At its endpoint the allowed
pressure is zero; pressure along the fixed `p` direction is still 3. The
separate checker enumerates `E(2,q)=(q-1)^2+3` across the complete declared
domain, witnessing the unique minimum. Three-chart cycle closure is possible
at every state, so it cannot substitute for this test.

A separate parity feature on the eight-vertex cube carries directional energy
`(4*a*a,4*a*a,4*a*a)`. Its coarse average has zero directional energy. Retain
the amplitude and all residual energy; a per-case allowance, pinned before
execution, decides whether it blocks this particular model witness. A zero
coarse reading cannot silently clear it. Period energy and cube energy belong
to different declared measurements and are never added as an uncalibrated total.

## Producer and replay

`model.py` proposes a complete candidate trace using matrix evaluation and
cube-edge sums. The checker uses explicit chart-coordinate formulas, the
finite energy table and the parity energy formula. It checks every frame's
anchor, ordered parent, charge, observations, residual and allowed transition.
The candidate acquires a replay witness only after this separate check; its
intermediate frames are synthetic proposals, not accepted external effects.

Both traversals share Python integers and the host. These are three derived
views of one arithmetic fixture, not three independently executing machines or
actual participant messages. No `send`, `receive`, human acceptance, native
proof identity, Rust `Seal`, source movement, deletion or release effect is
simulated as if it happened. `FiniteBalanceWitness` is an external finite
result, not native `FreeAccepted`.

The [contract](contract-v0.json) contains ten predeclared cases:

| Case | Expected outcome |
| --- | --- |
| Anchored relaxation from `q=0` | FiniteBalanceWitness |
| Opposite start `q=2` | FiniteBalanceWitness |
| Already at `q=1` | FiniteBalanceWitness, zero updates |
| Retained nonblocking cube energy | FiniteBalanceWitness with residual retained |
| Hidden energy above its allowance | BlockedByResidual |
| Missing residual measurement | Unknown |
| Missing third chart observation | Unknown |
| Required but unavailable human acceptance | Unknown |
| Chart cycle closes but no update budget remains | Unknown |
| One descending update, then budget exhaustion | Unknown with reached state retained |

Unit tests additionally alter anchors, charts, pressure, energy, history,
residuals, numeric types, native-authority claims and effects. Rehashing a
forged trace does not make its relationships valid. Exhausted or refused
replay retains the candidate without issuing a witness.

## Reproduce one bounded invocation

Use Python 3.11+ on Linux; the runner needs only the standard library. Inspect
the contract and independently select its expected SHA-256. A locally computed
digest binds chosen bytes and does not authenticate their origin.

```sh
python3 experiments/triadic_free/calibration.py \
  --contract experiments/triadic_free/contract-v0.json \
  --expect-contract EXPECTED_CONTRACT_SHA256 \
  --output /tmp/adva-triadic-free-run-01.json
```

Choose a fresh output path with an existing parent, outside repository
directories. The runner checks all historical/specification and producer
source pins before computation. It refuses overwrite. The report embeds the
contract, checked input inventory, all reached states, separate replay
outcomes and costs. Exit codes are 0 for the complete expected calibration,
2 for a refusal/mismatch, and 3 for an unresolved invocation. A complete
calibration can contain expected blocked/Unknown cases.

Each invocation has 10 wall seconds (8 cooperative), 5 CPU seconds, 256 MiB
address space, 4,096 work units, a 32 KiB contract, at most 16 reference/source
files of 256 KiB each, and a 512 KiB output. Work units count case admission,
proposed snapshots, neighbor evaluations and replayed snapshots, not every
integer instruction. CPU/wall limits also cover source checks and final output.
At most 12 cases and 8 updates per case are accepted. There are no native
calls, retries or automatic continuation. Hard CPU termination or failed
checkpoint I/O may prevent a complete report; a partial/missing report is not
successful replay. Process exit or exhaustion does not mean free acceptance.

The report's timings stop before final encoding/write; the hard limits cover
that remaining work. They exclude research, code authoring, tests and later
publication review. Linux peak RSS is process memory; output bytes are not RAM.

Public retention requires review of the exact generated report. All inputs
and output in this calibration are original engineering artifacts; publishing
its reviewed evidence is not a claim of a knowledge/library content exchange.
The old library, consumers and experimental evidence keep their original pins.

## Discuss the same structure

The [free structure card](../../exchange_routine/examples/free-process.json)
uses the already supported card format:

```sh
python adva-exchange show-structure exchange_routine/examples/free-process.json
```

It distinguishes the user's definition, the finite model and the missing
native integration. Its shape check grants no mathematical or receiving
acceptance. A real exchange of this card would still need the existing
reviewed-entry receiving contract.

See [ADR 0050](../../docs/adr/0050-triadic-free-process-calibration.md) for the
executed result, evidence binding and remaining integration gate.
