# Research 0209: the quine relay's implementation correspondence, corrected

Date: 2026-09-20. Status: bounded evidence correction. No `claims.toml` entry,
no native admission, no new relay lap. Direction: Mingli Yuan. Authored by
DeepSeek Harness (deepseek-v4-flash-vision-exp) through his authorized account
proxy; account use is not his authorship, review, endorsement or correctness
guarantee.

## What was asked

Whether the Quine relay's relations can still be held, with whatever
corrections that needs.

## What the relations are

The [paired-quotation relay](0164-paired-quotation-quine-relay.md) records four
kinds of relation, and they are not equally durable:

| Relation | Kind | State on 2026-09-20 |
| --- | --- | --- |
| Retained bundle integrity: every stored payload's bytes and digests | byte correspondence inside the bundle | **holds** |
| Byte closure inside each retained lap: `p` equals its regeneration and its scale control, `q` equals its regeneration | recorded comparison | **holds** for the retained laps |
| Implementation ↔ retained copy | byte correspondence across the repository and the bundle | **broken** for the Python side, corrected here |
| A fresh lap closing with the current implementation | executable | **not re-established**, and refused by the library gate |

## The drift, measured

The bundle froze the implementations on 2026-09-09 (`c2daa17`). Three later
commits changed the Python supervisor without a retained copy:

| Historical version | SHA-256 | Bytes |
| --- | --- | --- |
| `run-01` copy | `d53153ae66da…` | 16,743 |
| `run-02` copy | `fa2c3483d3c7…` | 19,153 |
| `publication-03` copy | `9701a7f28c93…` | 22,306 |
| **repository, 2026-09-20** | **`6ad1e190975d…`** | **23,178** |

The current file matches none of them. The drift is three fixes, each one a
*refusal* made stricter or a limit made honest:

- `e33bccb` (2026-09-10) — a child CPU allowance is admitted only when a whole
  second remains; the earlier form rounded a fractional remainder up with
  `max(1, ...)`, so it could grant more CPU than the budget held.
- `524709a` (2026-09-10) — the allowance is computed in the supervisor before
  side effects and installed after `fork`, because `RUSAGE_CHILDREN` cannot
  measure the supervisor's own completed children from the child.
- `d60258a` (2026-09-09) — `RLIMIT_AS` is installed only on Linux, since the
  limit is unsupported on the host used for the later checks. That is the same
  host limitation this session met independently in the machine's own
  `toolchain/process.py` wrapper.

The Rust observer example is unchanged (`af6c706250f2…`), so its
correspondence still holds directly.

## The correction

`docs/research/0164-evidence/postcommit-check-02/` retains the current bytes —
the Python supervisor, the Rust example, the experiment contract — plus
`relation.json`, which records both historical and current digests, the drift
class with its commits, the relations that still hold, and the gate
measurements below. `docs/research/0164-evidence/manifest.json` gains those
entries; **no earlier entry is edited**, so every previously retained payload
keeps its bytes and digest.

The correction is made load-bearing rather than documentary:
`experiments/quine_relay/verify_evidence.py` now checks, in addition to the
stored bytes, that

- the repository's Python supervisor equals the copy retained in this version;
- the three historical versions stay pairwise distinct and byte-preserved, and
  the current file does not reuse any of them;
- the Rust observer example still equals its publication copy;
- the correction record and the contract agree on the library pins.

Falsifier, executed: appending one comment line to
`python/adva/quine_relay.py` makes the verifier refuse with
`python implementation differs from its retained copy`; restoring the file
returns `RetainedBytesAndComparisonsChecked`. The check bites.

## What is not re-established, and why

`closure_re_established` is reported as **false**, and the reason is measured
rather than asserted. A fresh lap needs its own calibration because the
contract pins a library that the checkout no longer holds:

| Gate | Measurement |
| --- | --- |
| `base_commit` ancestor of HEAD | true |
| protected Rust build inputs changed since `base_commit` | **0** files |
| library revision in the checkout | `73a6af4ac4ed…` |
| library revision pinned by the contract | `a705aa2290d6…` |
| library tree in the checkout | `20d3ddca02b2…` |
| library tree pinned by the contract | `b67934ad294f…` |

The library gate compares the embedded gitlink and the standalone checkout
against those pins, so it refuses before any relay work starts. Two things
follow, and both are recorded rather than repaired:

- the 2026-09-09 laps remain valid **for their own** bodies; a lap with the
  corrected bodies would be a new calibration, needing a new `base_commit`, a
  re-pinned library revision and tree, and a re-derived paired context — and its
  own finite budget;
- re-running the old contract against today's library would be a *different*
  experiment wearing the old pins, which is exactly what the gate exists to
  refuse.

Nothing here weakens the pinned-library discipline to make a run possible.

## What this does not establish

- **No relay lap was executed.** No `p`, `q` or `r` was regenerated, and no
  closure is claimed for the corrected implementation.
- **No authentication and no semantic change.** Hashes establish byte
  correspondence only; the corrected supervisor's stricter CPU admission is not
  claimed to change any recorded result, because it was never run under the
  contract's pins.
- **No new admission, operation or claim.** Nothing is promoted; the relay's
  contract, budgets and controls are unchanged.
- **Not a rewrite of history.** Every earlier version stays in place, including
  the failed `run-01` and its `Unknown` status addendum.

## Reproduction

```sh
# from the machine repository root
python3 experiments/quine_relay/verify_evidence.py
```

The output reports the retained file count, the recorded costs, the correction
version, `implementation_correspondence_checked: true` and
`closure_re_established: false`.
