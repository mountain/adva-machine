# Local toolchain acceptance

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy;
not his technical review or correctness guarantee. Date: 2026-09-16.

Four finite engineering regression invocations used the same fixed family in
`conformance.contract.json`, each in a fresh output directory. All sixteen cases
passed for the native Rust VM and the existing external Python reference VM in
each invocation. Each used 80 child invocations, including 68 native calls, and
478 replayed native instruction steps. No invocation retried or renewed fuel.

| Record | Integration change being checked | Status | Wall seconds | Aggregate CPU seconds |
| --- | --- | --- | --- | --- |
| `local-01` | Initial common interface | Passed | 4.963 | 4.288 |
| `local-02` | Versioned reports for malformed transport input | Passed | 6.542 | 5.749 |
| `local-03` | Bounded regular-file reads and output path confinement | Passed | 4.763 | 3.966 |
| `local-04` | Unknown v0.2 library adoption and licensing pins | Passed | 4.933 | 4.132 |

These figures include process startup, storage and native receiving; they are
not a benchmark of relative execution performance. Producer snapshots preserve
each revision rather than attributing earlier runs to later adapter bytes.

`local-04` uses library revision `f652709` and checks ten interface/license files.
The preceding three runs retain their original `9928b11` revision and seven pins.
The old lock is preserved under `toolchain/library-locks/`, with its digest named
by the new lock. Historical receipts are received against their own lock rather
than relabelled as observations of the current dependency. The adapter sources,
native transition profiles, corpus and execution budget did not change. The run
used the existing release executable, whose native source profile still matches.

After this licensing integration, 172 targeted regressions passed across the
common toolchain/evidence, public Python API, finite mix/self-compiler, symbol
contract chain, research index and mathematical catalog. Package metadata checks
also received the independent Unknown text and custom Python license identifier.

The outcome family contains five returns, four runtime rejections, four native
admission refusals and three resource-limited Unknown outcomes, each checked on
both engines. The latter are expected finite observations, not solved looping
or termination questions. The existing 51-instruction Adva arithmetic interpreter
returns 14 in the same 134 primitive steps on both implementations.

Every request, native input/program, stdout/stderr, execution trace, reception,
common report and run cost is retained in each directory's `complete.tar.gz`,
together with source snapshots and the contract/catalog used at execution.
The report, contract, catalog, library receipt and source manifest also remain
loose for inspection. `manifest.json` records every member's digest and size and
the archive digest. The archiver verified all bytes before removing the duplicate
loose files. Each archive is about 65 KiB, containing roughly 300 KiB of originals.
The manifest is documentary integrity, not a new native certificate. The
regression receiver reconstructs common observations from raw artifacts, checks
full state/trace correspondence and native receiving receipts, and rejects
mutated archives and changed histories even when return values match.

Engineering authoring caught a mutable fixture alias that could have changed
other cases when preparing the wrong-schema control. Requests were changed to
own independent copies before this acceptance run. The initial thirteen
transport/selection checks passed before the native family was launched.
After transport hardening, all seventeen transport/selection checks passed.
The existing public Python interface installed from this repository, and 52
related regressions passed across the public API, finite mix, self-compiler,
retained mix evidence, strict symbol contract chain and research index.
The first archive-regression check reported 27 passes and three failures: its
new test looked for `admission.stderr` instead of the retained
`admission.stderr.txt`. The receiver test path was corrected; no producer or
native artifact changed and no native acceptance invocation was repeated for
that correction.
The corrected transport and archive regression suite passed all 30 checks.
Both language-specific entries also ran successfully from outside the checkout:
the arithmetic request returned 14 and Rust freshly verified 134 steps in each
case. The local release binary was built with the locked Cargo dependency set.
CI is configured to run the common acceptance on Python 3.12; this new local
repository has no selected publication destination, so remote CI for this change
has not run.

The v2 Python route is explicitly Unsupported, with zero fallback launches.
The PyO3 facade remains Rust-backed. Neither this record nor directory names
establish three independent full-language machines, target-language source
generation, new library admission, useful optimizing mix or general equivalence.
