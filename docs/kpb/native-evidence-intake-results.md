# Bounded native evidence intake: execution and review

Date: 2026-09-30. Scope: [raw-evidence receiving profile v0](native-evidence-intake-v0.md)
on machine base `89d6f87554f474020de79e59056bce49d8ceb167`.
Authored by dot (OpenAI) through Mingli Yuan's authorized GitHub account proxy.
Separate AI implementation and review are not independent human verification,
Mingli's endorsement, or a separately developed mathematical kernel. Original
code, prose and synthetic evidence are contributed under Unknown v0.3; no
external research payload or dependency source is imported or vendored.

## Observed lifecycle

The original synthetic raw proof was transported through the unchanged Rust
profile: `Sent` → `AcceptedDocumentary` → `AlreadyAccepted` → `Acknowledged`.
The third observation recorded zero new acceptance effects. The exact receipt
and acknowledgment remained `semantic_verification: NotRun` and
`native_admission: NotGranted`, with the receipt bytes unchanged before/after
the separate native-check process. The original catalog/payload stayed at its
source home. The independent receiver binding was selected before fixture
emission and was never an envelope member.

The new receiver parsed only primitive fixed-proof fields, checked the source,
profile, premises, guards and independent bindings, rebuilt eight proof nodes
and formed the same p=x+y*z → 2*p → p template through unchanged native APIs.
Two cache hits then compiled fresh contexts, instantiated and executed [2,3,4]
→ 14 and [5,2,3] → 11. Both retain all four guards and different scoped native
program/source/occurrence bindings. No transport verdict was passed as a proof
premise. `LocalCheckedAndUsed` is this separate local report's outcome, never
an edited receipt or a portable authority token.

## Measured accounts

| Separately reported stage | Operations | Charged bytes | Direct parametric inserts |
| --- | ---: | ---: | ---: |
| Primitive intake, source binding and two input reads | 66 | 483186 | 0 |
| Native expected-binding setup | 34 | 332073 | 0 |
| Native first_check | 71 | 364516 | 8 |
| First cache hit / fresh use | 5 / 12 | 2474 / 14015 | 0 / 0 |
| Second cache hit / fresh use | 5 / 12 | 2474 / 14015 | 0 / 0 |
| Native first_check plus two-use total | 105 | 397494 | 8 |

Intake read 2654 bytes, parsed two records, and separately records 476530 hashed
bytes and 1348 encoded bytes; these overlap the charged-byte count. Native
execution retains one template check, two cache checks and two each of compile,
instantiate and execute. Native instantiation internally inserts another proof
node; it is separately counted rather than called a direct parametric insertion.
Peak unique ledger is 9 nodes, 8 edges, depth 4, 11322 encoded bytes. Those are
logical records, not heap allocations or CPU instruction counts.

The integration plan performed exactly seven processes: receiver-binding,
fixture emission, four existing documentary calls, and separate native check.
One local observation used approximately 0.337 seconds wall and 0.327 seconds
CPU including children. Its 89547-byte artifact observation is before final
integration-report encoding; embedded native/transport reports overlap their
separately retained files. Nested transport observed about 0.103 seconds wall,
0.101 seconds CPU and 14529 bytes before its report. Outer times include nested
work and must not be added to nested times. Setup compilation is separate.
No speedup or physical-allocation reduction is claimed.

Two further **fresh-process** native rechecks of the received bytes, each under
60 seconds and 512 MiB address space, both returned 0 and produced identical
**23249-byte** JSON including the newline:
SHA-256 `2762a8ab7d30757b4ac755320bfc110d2aa48f7b6769828f709775a98d58c3ed`.
Their local wall observations were about 0.0106 and 0.0107 seconds; child maximum
RSS observations were 6604 and 6660 KiB, including subprocess-accounting effects,
not isolated per-stage memory. Each recheck rebuilds a new local checked object;
there is no cross-process cache import. Report encoding is a separate stderr
account (23249 bytes, 128 KiB bound), not hidden in native reuse cost.

## Exact byte bindings

- Raw synthetic evidence BLAKE3:
  `62700c3e1024572472bb94b0b1ff9d2c21cc3166f868d2138d1c11a4dee2d04b`
- Intake source/build BLAKE3:
  `fe3a090fbf206639c0b8ea3374fc5038d1ee74604c1bb7c3d25702e33bdca96b`
- Unchanged retained native v0.1 checker/build BLAKE3:
  `c85cbd06968562d3fc8bf90d41981c5d98f3ec18bae9ae42436b142e5b5ec7fd`
- Exact receipt BLAKE3 for the recorded documentary run:
  `6164040fd4e35ee5efa5c0c4355952b44c5b7cfdb9e6ac34eed60a90df72ebde`

| Input path | SHA-256 |
| --- | --- |
| `experiments/native_evidence_intake/src/main.rs` | `5a65569582a0a7630d6577b53b709c22e93a89b6f9122f1eb335e3a52db6c4b2` |
| `experiments/native_evidence_intake/src/intake.rs` | `f4a378f6f2fb214de988694748d5014e754f511ff040ee2e351c767213effeda` |
| `experiments/native_evidence_intake/src/native.rs` | `67c5e1ae566ab5ff605376a403e710eb028c2102ade58d4d26455aaace70be96` |
| `experiments/native_evidence_intake/Cargo.toml` | `6109139a28631ac26736807003202e907250edbb0642c10918c17737c6b1319c` |
| `experiments/native_evidence_intake/Cargo.lock` | `6ed4dd99436be40f079052259755fba1d750c5f18f9b8210afca18b02027e7c4` |
| `experiments/native_evidence_intake/run_transport.py` | `92aa594a1eaf0ba29e5780c95e9e2bc88ff2c54289e1c53b97d8663c790c3192` |
| `docs/kpb/native-evidence-intake-v0.md` | `d5873565ef00a157917f2bbebdaaeee1d185e7052a294b357572eec9282209df` |

These hashes identify tested source bytes, not authentication or proofs of
correctness. The generator source is new project-original work. Its baseline
revision is ancestry only; the new PR supplies its published source revision.
The profile/source binding is not retroactively attached to old evidence.

## Checks actually run

- 28 isolated Rust tests: the 17 retained predecessor controls plus 11 new
  primitive-input, binding, failure and budget controls
- 12 focused Python tests, including six actual transport/checker integration
  cases, with no skip in the final local run
- All 282 root Rust workspace tests; root and standalone strict Clippy and fmt
- Seven current-checkout frozen surface-contract tests
- All 26 external package versions, sources and checksums match the root lock
- Exact comparison confirms root Cargo files, the entire `crates/` tree, all
  retained checked-roundtrip source/contracts/results, and consumer pins unchanged
- Separate AI reviewer rebuilt offline, ran the same 28/12 controls, and passed
  92 direct adversarial CLI cases covering primitive leaves, independently
  re-pinned binding leaves, nested/escaped duplicates, arbitrary authority data,
  malformed shapes, exact-byte mismatch, oversized input and unavailable inputs
- Independent reviewer also reproduced the two deterministic limited rechecks
  and seven-process lifecycle, and inspected the dedicated workflow

The full remote Python 3.11/3.12/3.13 matrix, ordinary Rust CI, publication gate
and dedicated intake workflow must pass on the exact PR head before merge.
This local evidence does not pre-claim publication, remote CI, merge or post-merge
CI. GitHub's PR and workflow records establish those separate lifecycle events.

## Failures and corrections retained

The initial wrapper tried to derive Debug for a report containing the retained
private Stage type; compilation refused it. A custom wrapper Debug implementation
fixed this without editing predecessor bytes. Strict Clippy found the internal
nine-argument test helper and an unnecessary map; the helper's narrow test-only
configuration is explicitly documented and the failure propagation was improved.

Review identified that native source-binding exhaustion could lose structured
setup cost, and a failure immediately before cache hit could replace a retained
checked prefix with an empty vector. The receiver now borrows only remaining
outer fuel for nested source binding, records exact failed work, returns Unknown
instead of a setup panic, and keeps the available eight-node prefix. Explicit
regression tests exercise these paths. Review also found repeated generator
source hashing outside the intake meter; all receiver-path occurrences and
expected-fixture encoding are now charged.

A further review found that equality of before/after receipt snapshots alone
could overlook a receipt changed after transport. The supervisor now checks the
pre-native receipt against the completed transport receipt pin and the actual
acknowledgment, then retains immutable snapshots. A real mutation control changes
receipt bytes while preserving NotRun/NotGranted and correctly refuses before
native checking. Separate controls distinguish delivery failure from native
rejection after successful documentary delivery, retaining receipt/ack scope.

On this host, /tmp and /var/tmp have repository ancestor markers; the unchanged
outside-repository guard was not bypassed. Initial separately created /dev/shm
scratch did not survive to a later execution namespace, causing test setup errors.
Creating scratch and running tests in the same explicitly approved invocation
resolved that environment issue. An optional /usr/bin/time command was absent;
that incomplete measurement exited 127 and was replaced by standard Python
subprocess timeout/resource observations. Neither incomplete invocation was
reported as successful final evidence. The integration child limit was clarified
as the unchanged 1 GiB; the additional standalone recheck is separately 512 MiB.

## Residual and next decision

Only this exact synthetic fixed proof and local receiving context are supported.
The producer is not needed at check time, but the independently bound raw bytes,
source/build assumptions and complete proof history remain required. No proof
body eviction, general loader/cut checker, arbitrary Compose, guard/equality
extension, native Iota authority, security/hosting choice or external consumer
migration occurred. A selected real consumer still needs its own successor lock
and migration evidence. This is another bounded G3 receiving route, not full G3
or the completion of KPB-14's consumer-adoption gate.
