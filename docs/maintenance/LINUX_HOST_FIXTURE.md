# The resident Linux host fixture

Authored by DeepSeek Harness (deepseek-v4-flash-vision-exp) under Unknown v0.3
through Mingli Yuan's authorized account proxy; account use is not his
authorship, review, endorsement or correctness guarantee. Date: 2026-09-20.

Some checks in this repository declare a per-child **address-space** limit
(`RLIMIT_AS`). That limit is Linux-only: on macOS the call is refused by the
platform — `/bin/sh -c 'ulimit -v …'` fails too — and a child launched under it
dies inside `preexec_fn` instead of running. Research
[0210](../research/0210-the-address-space-limit-is-linux-only.md) corrected the
child limits so the bound is installed only where it exists and the record
states which limits were installed; Research
[0212](../research/0212-the-same-tree-accepted-on-a-linux-host.md) executed the
same tree on a Linux host and retained its acceptance as
`toolchain/evidence/local-08`.

This document keeps that Linux host available as a **resident fixture**: a Lima
guest on this machine, so the Linux half of the checks can be re-run after any
change without leaving the host or waiting for CI.

## Where it lives

| Item | Value |
| --- | --- |
| Instance | `adva` (Lima, `vz` driver) |
| Guest | Debian 13, aarch64, 4 CPU, 4 GiB, 15 GiB disk |
| State directory | `/Users/mingli/work/public/.lima-adva` — **outside every repository**, about 4.9 GB |
| Guest working copy | `~/adva-machine` (the tree is synced there; the repository itself is never built in place by the guest) |
| Guest environment | Python 3.13.5 with `.venv-linux`, Rust 1.98.1, the pinned `adva-library` checkout |

The state directory sits beside the repositories rather than inside one, so it
is never committed and never shows up in `git status`. `LIMA_HOME` must be set
for every `limactl` call:

```sh
export LIMA_HOME=/Users/mingli/work/public/.lima-adva
```

## Operating it

```sh
export LIMA_HOME=/Users/mingli/work/public/.lima-adva

limactl list                     # status
limactl start adva --tty=false   # boot after a host restart
limactl shell adva               # a shell in the guest
limactl stop adva                # stop, keeping the disk
limactl delete adva              # remove the fixture and reclaim ~4.9 GB
```

Two host-side steps needed the sandbox widened when the fixture was created:
`colima`/`limactl` write their configuration under `~/.colima`, and Lima caches
the guest image under `~/Library/Caches/lima`. Both are outside the session
workspace. The fixture itself keeps its state in the workspace, so routine use
needs no such widening.

## Running the checks there

[`scripts/linux_host_check.sh`](../../scripts/linux_host_check.sh) syncs the
working tree into the guest, builds the native binary if it is missing, runs the
acceptance, and runs the host-dependent tests:

```sh
scripts/linux_host_check.sh              # acceptance + the three host-limit files
scripts/linux_host_check.sh --full       # the whole python suite
scripts/linux_host_check.sh --retain linux-YYYYMMDD   # also retain an acceptance
```

The sync excludes `target/`, `.venv*`, `.cargo-adva` and `.lima-adva`, so the
guest keeps its own build outputs and never writes into the host tree.

## What it is for, and what it is not

**For.** Re-running the Linux half of the checks after a change; producing a
Linux acceptance record (`--retain`), which is a different host's record and is
read as such; confirming that a correction which skips a Linux-only limit on
macOS still installs it on Linux.

**Not for.** It is not the project's CI, which runs on `ubuntu-latest`; it is
one guest on one machine, with its own toolchain versions. A record it produces
names its own host and is not interchangeable with a record from another host.
It grants no admission and changes no declared limit or budget.

## Measured state, 2026-09-20

| Check | macOS 26.6.2 arm64, Python 3.14.6 | Debian 13 aarch64, Python 3.13.5 |
| --- | --- | --- |
| `adva-machine conform` | `Passed`, 16 of 16, `address_space_limit_installed: false` | `Passed`, 16 of 16, **`address_space_limit_installed: true`** |
| `pytest tests/python` | 2,888 passed, **0 failed**, 10 skipped | **2,895 passed, 0 failed**, 5 skipped |
| of those skips | 5 host-limit checks, named with a pointer here | none for the host limits |

Since [Research 0213](../research/0213-honest-capability-probes-and-host-named-skips.md)
the launchers probe whether the Linux-only address-space limit can be
*installed*, not whether it exists as an attribute, so a host that cannot
install it refuses by name: `experiments/phase_runner/run_six.py` reports
`RequiredProcessLimitsUnavailable` and
`experiments/pascal_commutator_certificate/run.py` raises its declared
`RuntimeError("required process limits unavailable")`. The five checks that need
the limit are skipped on macOS with that reason and run here; the guest exists so
that they can be seen passing where the limit is real.

`experiments/triadic_free/calibration.py` still installs the limit
unconditionally: both a guard and a refusal there were measured and reverted,
because they change what that calibration's retained report or its four
input-validation tests mean — a decision about a host-labelled report version,
not a local guard.
