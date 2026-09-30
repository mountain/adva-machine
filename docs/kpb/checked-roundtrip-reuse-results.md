# Checked roundtrip reuse v0: execution and review record

Date: 2026-09-30. Scope: the [research-only local profile](checked-roundtrip-reuse-v0.md),
on machine base `bc7f6b99edca00a12f659eb5a13f6c10fe700899`.
Authored by dot (OpenAI), through Mingli Yuan's GitHub account (`mountain`) as
an authorized proxy. The account is not personal authorship, review,
endorsement or a correctness guarantee. Project-original under Unknown v0.3;
no external code, prose, dataset or software is incorporated.

## Observed result

Two independent full replays and one first-check-plus-cache route both execute
[2,3,4] → 14 and [5,2,3] → 11, with equal exact summaries and four retained
nonzero guards. Cache uses retain distinct scoped native program/source/
occurrence contexts and distinct native instance ordinals. Rebuilt stores may
both allocate instance ordinal zero; those labels are not global identities.

| Actual account for two uses | Full replay | Checked cache |
| --- | ---: | ---: |
| Charged wrapper operations | 162 | 100 |
| Charged source/encoded bytes | 739400 | 388661 |
| Observed encoded bytes (overlaps charged bytes) | 97570 | 67601 |
| Direct parametric proof insertions | 16 | 8 |
| Template checks | 2 | 1 |
| Cache-context checks | 0 | 2 |
| Native compilation / instantiation / execution | 2 / 2 / 2 | 2 / 2 / 2 |
| Peak unique proof nodes / edges / depth | 9 / 8 / 4 | 9 / 8 / 4 |
| Peak one-copy encoded proof ledger | 11322 bytes | 11322 bytes |

Each instantiation also calls native store insertion internally. The table
separates those calls from direct parametric insertions and makes no claim of
constant-time validation. Setup additionally records 31 operations and 323244
charged bytes; final report encoding records 2 operations and 71706 encoded
bytes, with one output newline. The seven fixed negative controls carry their
own actual limits and spent accounts. These are separate bounded cases, not
unaccounted retries of a comparison route. Per-stage deltas and cumulative
accounts are emitted by the example.

The whole example (both routes, setup and seven negatives) ran twice under a
60-second subprocess timeout and 512 MiB address-space limit. Both returned 0
and emitted byte-identical 71707-byte JSON:
SHA-256 `535568a1dbce561c95a17a1ec4587010b0e6baed22c20c00a023b8e3dc2a63eb`.
Observed local wall times were approximately 0.066 and 0.033 seconds. Python's
child-resource maximum RSS observations were 6620 and 6624 KiB; these include
subprocess-launch accounting and are not isolated per-route measurements.
This demonstrates fewer counted wrapper calls for this fixed two-use case,
not a wall-clock speedup, total allocation reduction, or scalable proof
compression. Native call internals and build work are not wrapper instructions.

## Checked source binding

The final checker/build BLAKE3 coordinate emitted by the example is
`a1cd26b806a18dd751beecf0c3a0bc611b84d15b3ec085417c497e926ea0e3d1`.
It is a byte binding, not authentication or an executable consumer lock.

| Source | SHA-256 |
| --- | --- |
| `crates/adva-witness/examples/checked_roundtrip_reuse.rs` | `b2420d39a74a1989f756e36296520007f58d1bf7949abfd36a4c0fe2522f8971` |
| `crates/adva-witness/examples/support/checked_roundtrip.rs` | `67c632f0becf2398f071a272ac49942808d7ca22026bda97701133d7ea6f59db` |
| `docs/kpb/checked-roundtrip-reuse-v0.md` | `0f967aaef556b77ef3777c63106a60ca6b5b30e6339bc2573d772818b46233c0` |

These digests cover the reviewed source used for the observations above.
Future source changes require fresh evidence rather than relabelling this run.

## Checks actually run locally

- 17 dedicated Rust controls passed, including positive replay/cache equality,
  fresh scoped contexts, changed context components, endpoint cancellation,
  opposite/unsupported boundaries, zero/intermediate-zero, input range,
  guard deletion, deadline behavior, retained partial evidence, budget stopping,
  no producer-verdict dependency, and internal native-context replay fault
- Workspace Rust tests passed: 282 tests; dedicated example tests are separate
- `cargo fmt --all --check` and full-workspace, all-target, all-feature Clippy
  with warnings denied passed; the final example was retested after review edits
- Existing frozen-library stability example: 11 tests passed
- Unchanged frozen-library replay gate passed: current stale fingerprint was
  refused and the historical fixed receiver passed its 12 tests
- Final executable refuses any supplied argument, including forged serialized
  `Verified`/`FormedCellV0` data; there is no imported checked-handle entry point

The local Rust/Cargo toolchain was 1.98.1. No local Python suite claim is made:
the available old editable environment points to another checkout. The PR's
full remote Python 3.11/3.12/3.13 matrix and ordinary Rust CI remain required
before merge. This record does not pre-claim remote publication, merge or
post-merge execution. GitHub PR and workflow records must establish those
separate lifecycle events.

## Failures, corrections and review

The first compile rejected a nested `impl Trait` function-bound spelling; it
was replaced with an ordinary generic error parameter. The first native trial
correctly exposed an overbroad freshness comparison: raw occurrence labels are
diagram-local, so separately compiled contexts can both contain `occ:0`.
The wrapper now retains/checks native qualified program/source/occurrence
triples without changing or manufacturing native IDs.

A separate reviewer identified two accounting defects: native error returns
skipped a post-call deadline check, and attempted calls were counted before a
preflight budget check. Both were fixed with tests. Review also required
scoped identity and native artifact coordinates in successful records, actual
limits in negative records, separate report encoding, and retained artifact
prefixes when checking stops mid-proof. A new mid-proof depth control records
Unknown with its seven already-checked artifacts. Retaining richer failure
records initially triggered Clippy's large-error warning; the spent account
is now boxed, preserving its JSON contents without disabling the lint.

All these failures are development observations, not withdrawn prior success
claims. Implementation and review are AI work; neither is independent human
verification or a separately developed mathematical checker. The unchanged
native witness/compiler APIs remain the stated trusted boundary.

## Residuals and next decision

There is no serialized cache import, cross-observer trust transfer, arbitrary
Compose, general cut-certificate checker, proof-body eviction, ancestry skip,
new equality/guard rule, native Iota authority, remote hosting or consumer
adoption. Proof/storage numbers count logical records rather than Rust heap
allocation. Cooperative limits cannot interrupt a native call, and a hard
process kill may leave no complete/resumable report. No continuation or hidden
budget reset is provided. The four-epoch library rule and its full parent replay
remain unchanged. A next actual consumer adoption requires selection of that
consumer, a successor lock and its own migration checks; this example chooses
none. This is one bounded G3 checked-cache route, not completion of all G3.

## Packaging successor after the remote integration failure

The v0 record above is retained as the exact historical observation on PR5 head
`f30023f3a3ccae7b5d11608b88e2ae76290f1b82`; its original source paths remain
readable at that commit. The dedicated native pilot, ordinary Rust CI and all
six auxiliary workflows passed there. The Python 3.11/3.12/3.13 matrix each
reported **1 failed, 2894 passed, 5 skipped**. The sole failing assertion was
`test_advance_surface_contract_chain::test_the_base_commit_boundary_holds_at_this_commit`:
the active surface contract freezes **all** of root `Cargo.toml`, `Cargo.lock`
and `crates/`, including additive examples. The earlier source-level freeze
check was therefore insufficient to establish the wider integration boundary.

The correction leaves that assertion, its historical base, all surface
contracts and every frozen root Cargo/crates byte unchanged. The experiment
moves to `experiments/checked_roundtrip_reuse/` with its own `[workspace]`,
manifest and lock. Its 26 registry dependencies match the root lock's exact
versions, sources and checksums; no dependency source is vendored. Only module/
include paths and the explicit v0.1 packaging/profile identifier change in the
Rust code. Native judgments, literal route, guards and tests are unchanged.
The new [v0.1 contract](checked-roundtrip-reuse-v0.1.md) binds both manifests/
locks and the toolchain selector, and refuses implicit reuse of a v0 handle.

Fresh local evidence for v0.1:

- 17 isolated package tests, isolated all-target Clippy with warnings denied,
  formatting, and all 7 current-checkout surface-contract-chain checks passed
- Two whole-run executions under the same 60-second/512 MiB outer limits emitted
  byte-identical **71733-byte** JSON, SHA-256
  `c33bed16b94f7a395e0514b4c838611c9150634637c1610c754bd1e4f59f6e56`
- Full replay: **168** wrapper operations, **757062** charged bytes, **16** direct
  parametric insertions; cache: **103**, **397494**, **8**, respectively
- Both retain 2 compilations/instantiations/executions and the same 9-node,
  8-edge, depth-4, 11322-byte unique proof ledger
- Setup: 34 operations / 332073 charged bytes; final encoding: 2 operations /
  71732 encoded bytes plus newline; the extra source-bind operations are counted
- Whole-run local times were about 0.034 and 0.033 seconds; child maximum-RSS
  observations were 6632 and 6636 KiB, with the same measurement caveats above
- Checker/build digest:
  `c85cbd06968562d3fc8bf90d41981c5d98f3ec18bae9ae42436b142e5b5ec7fd`

| Relocated input | SHA-256 |
| --- | --- |
| `experiments/checked_roundtrip_reuse/src/main.rs` | `3da955d37c395974d23f443d65d2ad3fb987249a551f14157f49daba20bfb7de` |
| `experiments/checked_roundtrip_reuse/src/checked_roundtrip.rs` | `56d8c0e4b793b531d6f34299f3b56120fe26692e20fed71b673d0c0e2c1f9e1f` |
| `experiments/checked_roundtrip_reuse/Cargo.toml` | `f835594bb6eed81556352417411a34604c4e08fe3141c6854b9a0d955c8182e6` |
| `experiments/checked_roundtrip_reuse/Cargo.lock` | `10114c2baf2277f1b1faa14408cbff36f11258c285b22010b12359ba3dfae4cb` |
| `docs/kpb/checked-roundtrip-reuse-v0.1.md` | `b4046d83a3a768b68ade570664c5decf3da61da9b10e2793b8b6b2cf7c4c7a23` |

The dedicated workflow now explicitly formats, lints, tests, builds and runs the
isolated package; root `--workspace` checks no longer imply coverage of this
separate package. Full remote CI must run again on the successor head before
merge. The five Python skips are the four missing lawful golden-ratio inputs
and the optional absent ed25519 backend, not new pilot exemptions.
