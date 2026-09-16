# Symbol-surface native load: one version-bound advance

This profile answers the next minimal question in the library's
`symbol-surface/handoff.json`: can the unchanged envelope pass the existing
Rust document loader, preserving its nine open frontier annotations?

The completed first run and its interpretation are recorded in
[RESULTS.md](RESULTS.md); [reply.json](reply.json) binds the response to
the exact incoming handoff and its retained native result.

The source boundary is adva `91f57d0`, library `f0312ca`, and PR 170's eight
archived files. The exact handoff and the prior byte-observer receipt are
both pinned. [contract.json](contract.json) fixes all input hashes, eight
native load calls, eight controls, finite limits and exit conditions before
execution. The original `byte-observer-v0` profile remains unchanged.

**Contracts, and what a frozen replay would now do.** The active contract is
[contract-v8.json](contract-v8.json). Each successor names the digest of the one
it supersedes, so the chain is `contract.json` (v0) <- `contract-v1.json` <-
`contract-v2.json` <- `contract-v3.json` <- `contract-v4.json` <- `contract-v5.json` <- `contract-v6.json` <- `contract-v7.json` <- `contract-v8.json`, and a run verifies that digest rather than
trusting the file:
editing a superseded contract afterwards is a failure, not a silent
reinterpretation. v1 moved two inputs — the symbol-surface README pin, after the
unearned game label was withheld, and the base commit. v2 moves the base commit
again and nothing else, because the profile requires that nothing under
`Cargo.toml`, `Cargo.lock` and `crates` has changed since it, and the macOS
extension-module link fix changed all three. v3 moves the base commit a third
time for the same reason and no other: the merged symbol-surface native-load
gate adds a Rust integration test under `crates/adva-witness/tests/`, which is
inside the boundary the profile pins. v4 moves the Rust base to `c0d94bd` after
the separately versioned bounded data interpreter was added. Its input pins,
library boundary, controls, authorization text and execution limits are exactly
v3's; this maintenance update does not execute another advance or renew any
run's fuel. v5 moves the Rust base to the structured self-compiler integration
commit, preserving v4's inputs and all non-metadata fields. It likewise starts
no new run. v6 binds the Rust benchmark example added at `81f0e97`, preserving
every non-metadata field of v5. v7 binds the separate v2 data-machine capacity
profile and its native tests at `4701e01`, preserving every non-metadata field
of v6 and starting no new run. v8 binds the Unknown v0.2 license-file
metadata in Cargo manifests, with native source, Cargo.lock and every
non-metadata contract field unchanged. It starts no new run.
The strict Rust-diff check remains unchanged.
The run-01 evidence below keeps the
frozen version-zero contract and its original digests as the record of what that
run actually executed, so a literal replay of run-01 now fails on the README pin
**by design rather than by drift**: an input changed after that run. Use the active
contract, and read `supersedes.note` for the reasoning at each step.

The new outer profile invokes existing code: it builds the Rust/PyO3 extension
offline, copies the fresh library to its evidence directory and directly loads
that artifact. `load_adva_document_json` calls `load_adva_document_v0` in Rust.
No Rust semantic code or operation registry is modified, and no installed
Python extension is replaced. The outer Python checks byte bindings and the
returned protocol; it does not issue the load certificate.

Eight finite calls load the original, the library copy, the same original
again, three structurally invalid envelopes, an invalid entrypoint, and the
same envelope with no external payload files. The last control makes explicit
that the native loader checks the document's cache-coordinate strings without
resolving or proving the external payload. Separately, the outer SHA256 check
must reject altered payload bytes. Source files and historical statuses are
never rewritten.

Run once under the active contract, with a fresh output directory. GNU `timeout`
is present on Linux and in CI; on macOS it is not, so the same command runs under
`gtimeout` from `brew install coreutils`, or with no wrapper at all, in which case
the profile's own 180-second account is the only bound:

```sh
timeout 190s python3 python/adva/adva.py advance \
  --profile symbol-surface-load-v0 \
  --output target/advance-symbol-surface-20260910-01
```

```sh
# macOS: `timeout` is absent. Either install coreutils and use gtimeout, or drop
# the wrapper and rely on the contract's own wall_seconds: 180. Only the outer
# host guard is lost, and it is the guard whose hard termination can prevent the
# final checkpoint.
gtimeout 190s python3 python/adva/adva.py advance \
  --profile symbol-surface-load-v0 \
  --output target/advance-symbol-surface-20260910-01
```

The 180-second account includes preflight, all child processes, rebuilding,
controls, source copying, inventory and checkpoint checks. A 190-second outer
timeout provides the final host limit. Hard termination or storage failure can
prevent a completed checkpoint; partial files remain. No automatic retries or
next round are performed. Authoring, engineering tests and later integrity
checks are outside the experiment timing.

Success is `VariationObserved` with `NativeEnvelopeLoaded`, a ready frame,
conditional verification formation, nine remaining frontier annotations and
no recorded outputs. This is a new native load result, not mathematical proof,
mechanism execution, new knowledge epoch, `free`, or a Rust Seal. The frontier
coordinates index the external annotations and are not a native encoding of
the mathematical tasks listed there.

Engineering checks, separate from the actual trial:

```sh
.venv/bin/python -m pytest -q tests/python/test_advance_surface_boundary.py \
  tests/python/test_advance_boundary.py tests/python/test_persistence.py \
  tests/python/test_math_catalog.py
```

The complete 54-file run is retained under [`evidence/run-01/`](evidence/run-01/).
The executed shared library is losslessly gzip-compressed; the manifest records
both original and stored byte lengths and SHA256 hashes. All other files are
unchanged byte copies, including the original report and implementation snapshots.
Historical absolute paths remain as recorded. Verify the archive without loading
the shared library or restarting the experiment:

```sh
python3 experiments/advance_symbol_surface/verify_evidence.py
```
