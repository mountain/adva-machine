# Research 0211: an acceptance record now names the host it ran on

Date: 2026-09-20. Status: bounded provenance correction to the engineering
acceptance record. No `claims.toml` entry, no admission, no limit or budget
change. Direction: Mingli Yuan. Authored by DeepSeek Harness
(deepseek-v4-flash-vision-exp) through his authorized account proxy; account use
is not his authorship, review, endorsement or correctness guarantee.

## The gap

[Research 0210](0210-the-address-space-limit-is-linux-only.md) corrected the
child limits so that `RLIMIT_AS` is installed only where the platform has an
address-space limit, and made each child record and the cost limits state
`address_space_limit_installed`. That field is host-derived, but the record did
not say **which host** produced it: two acceptances — one on Linux with the
limit installed, one on macOS without it — were distinguishable by an inference
rather than by a statement, and nothing in the record named the platform,
machine, OS release or interpreter.

## The correction

`toolchain/conformance.py` now writes a `host` block into every acceptance
report, and `toolchain/evidence/local-07/` is the fresh acceptance carrying it:

```json
"host": {"platform": "darwin", "machine": "arm64", "release": "25.6.0", "python": "3.14.6"}
"cost": {"limits": {"address_space_per_child": 1073741824,
                    "address_space_limit_installed": false, ...}}
```

The declaration is unchanged and the record now reads as one host's statement:
this acceptance ran here, on this interpreter, and installed this limit set.

## Made load-bearing, not decorative

A new check,
`test_latest_acceptance_names_the_host_it_ran_on`, reads the newest acceptance
and requires that its `host.platform` equals the running `sys.platform`, that
machine, release and Python version are non-empty, that
`address_space_limit_installed` equals `sys.platform == "linux"`, and that the
declared per-child address-space bound is still `1073741824`. A record produced
on one host and read on another therefore fails rather than passing silently,
and a doctored platform field fails the same check.

The retained chain is: `local-01` … `local-05` (pre-correction acceptances),
`local-06` (host-portable limits, no host block), `local-07` (host block), with
`toolchain/evidence/README.md` carrying a row per invocation. Every earlier
archive keeps its bytes, and the latest one is what the acceptance tests read —
**20 tests pass**.

## What this does not establish

- **Not authentication.** The host block is provenance: it states where a run
  happened, and authenticates nothing about the machine or the run.
- **Not host equivalence.** Two hosts' acceptances are now *distinguishable*,
  not equal; the record makes no claim that a Linux run and a macOS run are
  interchangeable, and the retained pre-correction records keep their own
  meaning.
- **No limit or budget change.** `conformance.contract.json` is untouched; the
  declared address-space bound stays `1073741824`.
- **No admission.** Nothing here creates a native type, operation, registry
  entry, IR version, `Seal` or epoch.

## Reproduction

```sh
# from the machine repository root
.venv/bin/python adva-machine conform --output /tmp/conform-host
.venv/bin/python -m toolchain.archive /tmp/conform-host     # archives in place
.venv/bin/python -m pytest -q tests/python/test_machine_toolchain_evidence.py
```
