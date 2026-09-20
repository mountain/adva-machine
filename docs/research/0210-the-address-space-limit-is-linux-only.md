# Research 0210: the address-space limit is a Linux-only limit

Date: 2026-09-20. Status: bounded host-portability correction, with measured
outcomes and retained open sites. No `claims.toml` entry, no admission and no
budget change. Direction: Mingli Yuan. Authored by DeepSeek Harness
(deepseek-v4-flash-vision-exp) through his authorized account proxy; account use
is not his authorship, review, endorsement or correctness guarantee.

## What exposed this

Installing the test extra (`pip install '.[test]'`) made the Python suite
runnable on this host and turned a suspicion into a measurement: several
launchers install `RLIMIT_AS` unconditionally, and on a platform whose
`setrlimit` has no address-space limit the call fails **inside `preexec_fn`**,
which does not merely skip the limit — it kills the whole child launch.

Measured one limit at a time, in a bare `subprocess.Popen(["true"],
preexec_fn=...)`:

| Limit | Result on this host |
| --- | --- |
| `RLIMIT_CPU` | installed |
| `RLIMIT_AS` | **raises `SubprocessError: Exception occurred in preexec_fn`** |
| `RLIMIT_FSIZE` | installed |
| `RLIMIT_CORE` | installed |

The quine relay had already met this on 2026-09-09 and fixed it the same way
(`d60258a`, "guard RLIMIT_AS behind linux in the quine relay supervisor") — the
precedent this correction follows.

## What was corrected, and what it restored

| Site | Change | Verified outcome |
| --- | --- | --- |
| `toolchain/process.py` | install `RLIMIT_AS` only where the platform has it; record which limits were installed | **`adva-machine conform` reports `Passed`, 16 of 16 cases**, 2.347 s wall, 1.475 s CPU — it previously refused inside `preexec_fn` |
| `toolchain/process.py` (record) | each child record and the cost limits gain `address_space_limit_installed` | the run states the installed limit set instead of implying the declared address-space bound was applied |
| `python/adva/adva.py` | same guard in the CLI's child limits | `tests/python/test_exchange_routine.py`: **6 failures → 6 passes** |
| `python/adva/operator_receipt.py` | same guard | part of the same restored path |

The declared address-space bound is unchanged in `conformance.contract.json`
and in the experiment contracts: it is a declaration of what a run wants, and
the record now says whether the host installed it. Nothing was re-declared to
match the host.

## The acceptance relation is re-established, not restated

`toolchain/process.py` changed, so the retained acceptance's source manifest no
longer described the current toolchain — the relation
`test_latest_acceptance_contains_current_adapter_sources` exists to catch
exactly that, and it failed. The correction follows the repository's own
archival route rather than editing the test's expectation away:

- `toolchain/evidence/local-06/` is a fresh acceptance of the corrected tree,
  produced by `adva-machine conform` and archived with `toolchain/archive.py`;
- `toolchain/evidence/README.md` gains its row (integration change: host-portable
  child limits; 2.347 s wall, 1.475 s CPU);
- the test now reads the newest acceptance, and **19 of 19 tests pass**;
- `local-01` … `local-05` keep their bytes.

## What remains open, with its measured reason

Twelve tests in three files still fail on this host, each because a further
launcher installs the same Linux-only limit:

| File | Failing | Measured reason |
| --- | --- | --- |
| `tests/python/test_phase_runner.py` | 10 | `experiments/phase_runner/run_six.py` probes `hasattr(resource, "RLIMIT_AS")`, which is true here, then fails in `preexec_fn`; the design says the limits are *mandatory* for execution, so the honest outcome on this host is `RequiredProcessLimitsUnavailable`, and these tests encode a Linux host |
| `tests/python/test_triadic_free.py` | 1 | `experiments/triadic_free/calibration.py` installs the limit unconditionally; an attempted one-line guard was **reverted** because it changed two retained-report comparisons, so it needs its own contract-aware correction |
| `tests/python/test_pascal_commutator_certificate.py` | 1 | `experiments/pascal_commutator_certificate/run.py` has the same unconditional install behind a `hasattr` host check |

A sweep of this checkout counts **83 live files** that mention `RLIMIT_AS`
outside frozen evidence, trials and the new substrate; only a minority carry a
platform guard. Sweeping them is a separate change with its own per-experiment
checks, because several of those experiments compare retained evidence whose
recorded limits were produced on a host where the limit existed. Doing it in
one pass here would have replaced their records' meaning with the host's.

## What this does not establish

- **No budget or claim change.** No wall, CPU, artifact or launch allowance was
  raised; the address-space declaration stands.
- **No host-equivalence claim.** A macOS run and a Linux run install different
  limit sets, and the record now says so per run; no claim is made that they are
  equivalent, and the retained Linux-host evidence keeps its own meaning.
- **No native admission.** No `ValueType`, `OperationSpec`, registry entry, IR
  version, `Seal` or `claims.toml` entry accompanies this correction.

## Reproduction

```sh
# from the machine repository root
.venv/bin/python -m pip install --no-deps '.[test]'     # needs a writable CARGO_HOME
.venv/bin/python adva-machine conform --output /tmp/conform-01
.venv/bin/python -m pytest -q tests/python/test_exchange_routine.py \
    tests/python/test_machine_toolchain_evidence.py
```

With a cargo home inside the workspace, the wheel builds offline from the cached
crates; the host's default `CARGO_HOME` was not writable under the session's
file policy, which is why the first attempt failed with
`failed to open …/cpufeatures-0.3.1.crate: Operation not permitted`.
