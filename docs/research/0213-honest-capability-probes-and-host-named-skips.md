# Research 0213: honest capability probes, and checks that say which host can run them

Date: 2026-09-20. Status: bounded correction to three launchers and three test
files, with measured outcomes on two hosts. No `claims.toml` entry, no
admission, no limit or budget change. Direction: Mingli Yuan. Authored by
DeepSeek Harness (deepseek-v4-flash-vision-exp) through his authorized account
proxy; account use is not his authorship, review, endorsement or correctness
guarantee.

## Why

[Research 0210](0210-the-address-space-limit-is-linux-only.md) recorded twelve
macOS failures caused by one Linux-only limit (`RLIMIT_AS`), and
[0212](0212-the-same-tree-accepted-on-a-linux-host.md) showed all of them
passing on a Linux host. That left the macOS suite red for a *known* reason, and
left three launchers probing the wrong thing: they asked whether the limit
**exists as an attribute**, which is true on macOS, instead of whether the
platform can **install** it.

Two corrections were made together, and neither one turns "cannot install the
declared limit" into a pass:

**(B) The launchers say what they actually require.** A capability probe now
tests installability, so a host that cannot install the declared limit refuses
by name instead of dying inside `preexec_fn`:

| Launcher | Before | After |
| --- | --- | --- |
| `experiments/phase_runner/run_six.py` | probe passed on the attribute; child died; the phase reported a crash-like `BackendError` | probe tests installability; the phase reports its declared `RequiredProcessLimitsUnavailable` |
| `experiments/pascal_commutator_certificate/run.py` | same defect behind `os.name != "posix"` | refuses with its declared `RuntimeError("required process limits unavailable")` |

Measured, on macOS: `run.py /tmp/pascal-refusal` reports
`{"status": "Unknown", "children": 0, "reason": "required process limits unavailable"}`.

**(A) The checks name the host that can run them.** Five tests that need the
limit — one pascal replay, three phase-runner synthetics, one triadic-free CLI
run — are reported as not runnable here, with a reason and a pointer:

```
SKIPPED [1] test_phase_runner.py:147: the declared per-child address-space limit
            is Linux-only (Research 0210); run it on the Linux guest:
            docs/maintenance/LINUX_HOST_FIXTURE.md
```

They are skipped only where the limit cannot be installed. The predicate is
`sys.platform == "linux"`, the platform where Research 0212 measured the limit
installed, so the Linux guest runs every one of them.

## The pascal record: a corrected launcher, a superseding record

`execution.json` binds the launcher digests it ran with, so changing the probe
in `run.py` changed `file_sha256["run.py"]` (`4fbcefef…` → `9b63bfc8…`). The
earlier record is **not** edited. Instead the experiment was re-run on the Linux
guest, which showed that the correction changes nothing it produces:

| Artifact | Fresh Linux run vs retained |
| --- | --- |
| `certificate.json`, `check.json`, `controls.json` | **byte-identical** |
| `execution.json` `output_sha256` | identical |
| `execution.json` `file_sha256` | only `run.py` differs |

That run is retained as
`experiments/pascal_commutator_certificate/evidence/execution-linux-01.json`,
carrying its own supersession note, and the binding test now requires that **at
least one** retained execution record binds to the current code rather than
naming a single record.

## Measured outcome

| Check | macOS 26.6.2 arm64, Python 3.14.6 | Debian 13 aarch64, Python 3.13.5 |
| --- | --- | --- |
| the three affected files, before | 12 failed | 0 failed |
| the three affected files, after | **0 failed, 5 skipped** (41 passed) | **0 failed, 0 skipped** (46 passed) |

## What was deliberately not done

`experiments/triadic_free/calibration.py` keeps its unconditional install. Two
attempts were **measured and reverted** rather than shipped:

- installing the limit only where the platform has it changed two retained-report
  comparisons, because that calibration's report carries the declared bound;
- refusing inside `enforce_limits` when the platform cannot install it changed
  four tests, because that refusal fires before the input-validation subjects
  those tests examine.

Either is a decision about **what that experiment's report means on a host
without the limit** — a new, host-labelled report version and its comparisons —
not a local guard. Its CLI test is therefore covered by (A) and it runs on the
Linux guest, and the launcher is left exactly as it was.

## What this does not establish

- **Not host equivalence.** A skipped check is not a passed check: the report
  states that this host cannot run it, and where it does run (the Linux guest)
  it is executed.
- **No weakening of the limit.** No declared bound, budget or contract changed,
  and no launcher silently drops a limit: they refuse instead.
- **No CI change.** The project's CI already runs on `ubuntu-latest`, where the
  limit exists; this work is about the macOS host's honesty and noise level.
- **No admission.** No `ValueType`, `OperationSpec`, registry entry, IR version,
  `Seal` or `claims.toml` entry is added.

## Reproduction

```sh
scripts/linux_host_check.sh --full     # the whole suite on the Linux guest
.venv/bin/python -m pytest -q tests/python   # this host, with named skips
```
