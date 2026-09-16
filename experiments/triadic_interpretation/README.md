# Exact checks for the conditional theory of communication and free

Date: 2026-09-16. Status: completed external finite calibration of
[the conditional theory](../../spec/framework/triadic-free-theory-v0.md).
Original code, cases, prose and review by ChatGPT (OpenAI), contributed under
Unknown v0.3 through Mingli Yuan's authorized account proxy; account use is
not his review, endorsement or a correctness guarantee.

The user's two readings are A / B / their shared object, and Substrate /
Knowledge / Surface. The [context specification](../../spec/framework/triadic-context-v0.md)
retains both. These checks use supplied finite models. They obtain no actual
participant or natural-world observations and implement no native free.

| Family | Complete declared coverage | Check |
| --- | ---: | --- |
| Three interpretation sets on three candidates | 512 triples | Set intersection versus bitmask intersection |
| Descending graphs, acceptance sets and starts on three vertices | 192 combinations | Complete paths versus reachable sinks and backward worst cost |
| Anchored rational quadratics | 48 coefficient choices | Zero gradient, displacement energy identity and four exact contraction rounds |
| Binary observed prefixes of length 0 through 5 | 63 prefixes | Same prefix admits different next responses |
| Integer budgets 0 through 1,000 | 1,001 budgets | Exact side allowances, reserve and indivisible remainder |

The run completed **4,018 counted checks**. Explicit controls retain pairwise
compatibility without a triple witness, consensus contradicted by the object
predicate, missing evidence as Unknown, a descending search trapped before a
feasible solution, and a stationary `(1,1)` violating the required object value
zero. The contraction example has factor `1/9`; the written proof explains why
its nonzero error never becomes exactly zero in finitely many iterations.

The reserve control checks that one unit cannot fund a declared two-unit join.
It executes no key/certificate operation. Checkpoint non-advance is a required
future effect, not a fabricated observation. Graph edge costs of two and
terminal costs of three are stipulated model costs, not measured native costs.
The written proofs establish the conditional propositions; enumeration checks
finite instances and does not replace those proofs.

## Invocation and evidence

The contract and five source/specification pins were fixed before this run:

```sh
python3 -m experiments.triadic_interpretation.calibration \
  --contract experiments/triadic_interpretation/contract-v0.json \
  --expect-contract 7c303bec7460ff15eccf8b508652aeb5bdf6e54df7ceb25527ddab8ae6e295ec \
  --output /tmp/adva-triadic-interpretation-20260916-run01.json
```

Use Python 3.11+ on Linux and a fresh output outside all repositories. Only
the standard library is required. The runner reuses the previously pinned
external runner's hard OS limits, strict JSON and fresh-output checks without
editing its sources. Changed pins or finite families refuse execution. Output
is never overwritten; it is flushed and fsynced before success is printed.

The [full report](evidence/run-01.json) retains all enumerated cases, controls,
the contract, source inventory and costs: 62,461 bytes, SHA-256
`d6c29ba8d7cd5da273fe9e32f43ed946feb9b6f2cd19d923228faa56c8f4806c`.
The run used 29.122 ms wall time, 27.508 ms CPU time before final encoding/write,
and Linux peak RSS of 139,112 KiB under Python 3.14.4.
Elapsed measurements and the wall alarm start in CLI `main`, after module
imports; they do not measure interpreter startup. Process CPU limits apply to
the process's accumulated CPU usage.

Bounds are 10 wall seconds (8 cooperative), 5 CPU seconds, 256 MiB address
space, 20,000 counted checks, a 32 KiB contract, eight source slots of 256 KiB
each, and 512 KiB output. Hard time/size bounds cover final output; elapsed
measurements exclude that last write. Counted units are assertion checks, not
every Python operation. Authoring, tests and publication review are separate
costs. There are zero native calls, retries or automatic continuations.

The seven evidence/guard regressions and the 31 earlier free-profile regressions
passed together: **38 tests in 0.56 seconds**. Separate replay checks complete
case coverage, enumerates all short vertex sequences, and substitutes retained
rational values into the pressure and contraction equations. The successor
structure card passes its shape check and comparison retains every earlier
preservation requirement and open question. These checks confer no native
authority or participant acceptance.

On cooperative exhaustion or failed checking, reached rows remain in the
report and no whole-family witness is issued. Hard termination or failed I/O
may prevent a complete report; partial bytes are not a successful witness.
Exit codes: 0 complete finite checks, 2 refusal/mismatch, 3 Unknown.

## Publication and scope

The candidate report was generated outside the repositories. ChatGPT reviewed
its exact original contract, controlled numeric families, computed records,
source digests and host observations before retention. No external expression,
dataset or historical text is embedded. The explicit Unknown contribution and
actual author/proxy attribution serve as the routine first-party origin record.
Publishing this reviewed engineering evidence claims no executed Adva transport
or migration of existing library content.

The earlier A2 calibration, vocabulary, commands, library pin and receipts are
unchanged. The [successor card](../../exchange_routine/examples/free-context-v1.json)
retains both readings and earlier open obligations. Actual participants,
object observations, interpretation predicates and native release checks still
require a concrete instantiation of the conditional theory.
