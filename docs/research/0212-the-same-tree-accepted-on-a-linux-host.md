# Research 0212: the same tree accepted on a Linux host, and the whole suite on Linux

Date: 2026-09-20. Status: executed cross-host verification of
[Research 0210](0210-the-address-space-limit-is-linux-only.md) and
[0211](0211-an-acceptance-record-names-its-host.md). No `claims.toml` entry, no
admission, no limit or budget change. Direction: Mingli Yuan. Authored by
DeepSeek Harness (deepseek-v4-flash-vision-exp) through his authorized account
proxy; account use is not his authorship, review, endorsement or correctness
guarantee.

## The question this closes

0210 corrected the child limits so that `RLIMIT_AS` is installed only where the
platform has an address-space limit, and reported that twelve tests could not
run on the macOS host. The open question was whether the declared limit set
still holds on Linux — that the guard had not quietly weakened it there — and
whether the whole suite passes on Linux. Both were inference; this note makes
them measurements.

## The Linux host

A Lima instance (`vz` driver, Debian 13, aarch64, 4 CPU, 4 GiB) ran a copy of
this repository at revision `ced70b3`, with Rust 1.98.1, Python 3.13.5 and the
same pinned `adva-library` revision. No source was changed for the run.

| Probe | macOS (this host) | Linux (the instance) |
| --- | --- | --- |
| `setrlimit(RLIMIT_AS, 1 GiB)` | refused (in the shell too) | accepted |
| child launched under that limit | **fails in `preexec_fn`** | **launched, exit 0** |
| `adva-machine conform` | `Passed`, 16 of 16, `address_space_limit_installed: false` | `Passed`, 16 of 16, **`address_space_limit_installed: true`** |

The Linux acceptance is retained as `toolchain/evidence/local-08/`, whose host
block reads `{"platform": "linux", "machine": "aarch64", "release":
"6.12.90+deb13.1-cloud-arm64", "python": "3.13.5"}`. So the declared
per-child bound of `1073741824` bytes **is installed on Linux**, exactly as the
contract declares, and the platform guard leaves that path untouched.

## The suite, on both hosts

| Host | Result |
| --- | --- |
| macOS 26.6.2, arm64, Python 3.14.6 | 2,886 passed, **12 failed**, 5 skipped (4m 00s) |
| Debian 13, aarch64, Python 3.13.5 | **2,895 passed, 0 failed**, 5 skipped (4m 09s) |

The twelve macOS failures are the host-limit sites 0210 recorded
(`test_phase_runner.py`, `test_triadic_free.py`,
`test_pascal_commutator_certificate.py`); all of them pass on Linux, and no
Linux-only failure appeared.

The first Linux run also failed `test_latest_acceptance_names_the_host_it_ran_on`
— because the only retained acceptance carrying a host block was the macOS one.
That is the 0211 check doing its job: a record produced on one host is not
silently read as another's. It was corrected the right way round, by retaining
the Linux acceptance (`local-08`) and making the check read **this host's**
newest record, skipping with a named gap when none exists, rather than by
weakening the assertion.

## What this does not establish

- **Not host equivalence.** Two hosts accept the same 16 cases and now name
  themselves; no claim is made that their records are interchangeable or that
  their limit sets are the same.
- **Not a CI claim.** This is one executed Linux instance, not the project's
  workflow, which runs on `ubuntu-latest`.
- **No admission, no budget change.** The contract's declared limits, budgets
  and the pinned library are untouched.

## Reproduction

```sh
# on a macOS host with limactl, keeping all VM state in the workspace
export LIMA_HOME=$PWD/.lima-adva
limactl start --name=adva --cpus=4 --memory=4 --disk=15 --tty=false template:debian
limactl shell adva -- bash -lc 'cd ~/adva-machine && .venv-linux/bin/python adva-machine conform \
  --output toolchain/evidence/local-08 && .venv-linux/bin/python -m pytest -q tests/python'
```
