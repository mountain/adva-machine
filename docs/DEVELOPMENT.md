# Development and semantic boundaries

This guide retains the engineering detail behind the [project introduction](../README.md).
Read [AGENTS.md](../AGENTS.md) before changing semantic code.

## Documentation language

English is the primary maintained documentation language for international
collaboration, as requested by Mingli Yuan on 2026-09-16. Write new specifications,
ADRs, design notes, API and toolchain guides, research reports, release notes and
shared change descriptions in English first. Default documentation links should
point to the English version.

Translations and summaries in Chinese or other languages are welcome as
supporting material. Label them as translations or summaries and link to the
primary English document. If a translation falls behind, mark that clearly and
resolve discrepancies against the English version. Publishing an English update
does not require a simultaneous translation.

Historical quotations and retained evidence keep their original wording;
add an English explanation when needed for readers. This language convention
does not change versioned semantic authority or evidence requirements.

## PSC0: a first program

PSC0 is the finite, binder-free, linear program core. The separately versioned
[data-machine interpreter](../programs/bounded-interpreter/README.md) has its own
research semantics. Its control flow does not extend PSC0.

```lisp
(module arithmetic
  (export shared-double square)

  (def shared-double
    (fn ((x Real)) Real
      (add (copy (use x)))))

  (def square
    (fn ((x Real)) Real
      (mul (copy (use x))))))
```

Modules can import exported definitions:

```lisp
(module client
  (import arithmetic shared-double)
  (export quadruple)

  (def quadruple
    (fn ((x Real)) Real
      (call arithmetic/shared-double
        (call arithmetic/shared-double (use x))))))
```

Assign the two Lisp blocks above to `ARITHMETIC_SOURCE` and `CLIENT_SOURCE`
as Python strings. After installing `adva` with the scientific dependencies:

```python
from adva import link_modules

workspace = link_modules([ARITHMETIC_SOURCE, CLIENT_SOURCE])
quadruple = workspace.function("client", "quadruple")

value = quadruple.evaluate({"x": 3.0})
value, gradient, certificate = quadruple.value_and_gradient({"x": 3.0})

sympy_expression = quadruple.to_sympy()
numpy_function = quadruple.numpy_callable()
objective = quadruple.scipy_objective()
```

### Where the boundaries are

Successful JSON decoding is **not** semantic authorization. Stored diagrams
cross a separate checked boundary:

```python
from adva import load_program

restored = load_program(quadruple.ir)
assert restored.validation_certificate["linear_use"] == "checked"
assert restored.compilation_certificate is None
```

`load_program` returns only a diagram accepted by the Rust validator. Numerical
source selects `log@2` and correctly rounded `constant@2`; stored version-one
operations remain replayable. Ordinary Python evaluation requires finite
inputs and results and, when requested, a finite Jacobian, while Rust retains an
explicit raw IEEE replay. See
[ADR 0045](../docs/adr/0045-rational-rounding-and-finite-numeric-boundaries.md) for
compatibility, JSON transport, and the distinction from error bounds.

The **first stable slice is binder-free inside function bodies**. Function
parameters are typed 0-cell boundaries; module-level `def` and `call` do not
introduce local term binders. Recursive module calls and cyclic imports are
rejected.

## What is stable, and what is research-only

The scope statement is [`docs/SEMANTIC_SCOPE.md`](../docs/SEMANTIC_SCOPE.md) and the
working rules are [`AGENTS.md`](../AGENTS.md). The split below follows them.

**Stable kernel** — the binder-free, finite, linear core:

- immutable `ProgramTerm`, `TypedFrontier` with distinct `DomainFrontier` and
  `CodomainFrontier` orientations, module IR, and `SharedProgramDiagram`;
- explicit `copy`, `discard`, `swap`, `id`, ordered `frontier` construction,
  arithmetic and elementary unary operations;
- stable serializable `SourceId`, `OccurrenceId`, `OccurrencePath`, and
  `History`;
- Rust module parsing, imports, exports, linking, and typed lowering;
- compiler-emitted certified `GraftTrace` companions retaining nested call
  frames, argument regions, ordered hole bindings, and callee-body regions;
- a single versioned Rust operation registry shared by parsing, typed lowering,
  lineage transport, evaluation, and forward differentiation;
- scalar evaluation and forward differential, each with a certificate;
- JSON IR round-trips with an explicit schema version;
- semantic diagram import in Rust with graph, linear-use, occurrence, source,
  history, and boundary certificates;
- Rust-certified completed causal cuts and single-event frontier replacement,
  derived without evaluating or rebuilding checked wire lineage;
- exact certified `ProgramSlice` intervals retaining changed boundaries,
  unchanged through wires, internal events, occurrences, and history;
- exact adjacent-slice composition with identity, event-conservation, and
  associativity certificates over one unchanged diagram;
- a PyO3 extension and typed Python facade;
- optional SymPy, NumPy, and SciPy adapters.

**Research-only companions** — checked, bounded, and not stable API. Each names its own finite scope and its refusals:

- bounded `TriadicObserverTransitionV0` companions that classify three input
  source fibres, derive three opposite-pair cut readings, retain source-free
  residuals, and compose occurrence ancestry exactly across adjacent slices;
- a bounded Python research machine that packages exact triadic interfaces,
  complete `ProgramSlice` carriers, and Rust-checked schedule traces without
  claiming stable feedback or allocating semantic identities;
- a research-only multi-hole through adapter that derives one typed
  relation-valued angle form from exact graft bindings and occurrence ancestry,
  with layered failure gates and the complete slice retained as residual;
- a one-compilation triangular research calibration that derives all three
  local opposite-domain angle relations while refusing undeclared
  same-source sibling connectors and global circular closure;
- a typed connector trichotomy that separates exact occurrence identity,
  provenance-preserving direct-sibling comparison, and an unauthorized
  many-to-one source quotient;
- a bounded distributivity characteristic machine that gives learning and
  proof readouts over one exact rational polynomial feature while retaining
  two distinct checked process residuals;
- a research-only typed-aperture calibration that reads existing through
  relations as finite filling fibres, refuses implicit multivalued closure,
  and retains close/reopen history and the complete process residual;
- a Rust research V0 six-word witness companion with signed formation
  ledgers, exact integer-polynomial transport, finite proof DAGs, and reusable
  linear three-hole templates whose fresh instances bind existing semantic
  occurrences explicitly;
- a bounded neutral-carrier mechanism grammar that keeps
  `subject/method/object`, `compute/verify/learn`, and
  `history/result/evidence` distinct, rejects open compute subjects and
  objects, accounts for conditional verification, and retains partial learning
  fill proposals without changing the stable IR;
- a research-only neutral `.adva` document graph with canonical carrier and
  frame tables: mechanisms live on three-input/three-output transition edges,
  named entry points select checked frames, and later frames reuse earlier
  recorded carriers through explicit document-local references;
- a first bounded `reveal.adva` program whose observer-local names cover the
  six directed time/space/construction pairs while its checked `M6` relation
  remains explicitly open, together with the exact witness emitted by its
  first six-fuel run;

Several of these carry a parallel external check that is not native authority.
Three accepting verifiers are **not** a three-computation theorem, and a
registered external calibration is not native admission.

## Read before changing the engine

1. [Architecture](ARCHITECTURE.md) and [semantic scope](SEMANTIC_SCOPE.md).
2. [Program/process core](PROGRAM_PROCESS_CORE.md) and its
   [technical report](TECHNICAL_REPORT_PROGRAM_PROCESS_CORE.md).
3. The completed [program-slice](NEXT_PHASE_PROGRAM_SLICES.md) and
   [triadic-transition](NEXT_PHASE_TRIADIC_OBSERVER_TRANSITIONS.md) phases.
4. [Registered claims](claims.toml) and relevant [ADRs](adr/).
5. The [research and engineering agenda](RESEARCH_ENGINEERING_AGENDA.md)
   before proposing a new phase.

For a bounded research run, use the contract in
[Research 0129](research/0129-bounded-breakthrough-trusted-boundaries.md).
Before mathematical library growth, read the
[library obligation](../adva-library/math/README.md).

## Build and checks

From a recursive checkout, with Rust and Python 3.11 or later available:

```sh
cargo build --locked -p adva-witness --bin adva
cargo fmt --check
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo test --workspace

python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[test]'
pytest

python -S python/adva/adva.py math-check --key-words
```

The final command checks documentary catalog structure; it does not discharge
its open mathematical obligations. See the [CI workflow](../.github/workflows/ci.yml)
for the maintained build matrix and retained-witness checks. Report platform
failures against a clean checkout instead of inheriting old failure counts.

### Rebuild determinism of release binaries (measured, and narrower than expected)

A release binary is **deterministic while the build configuration is held
fixed**, and the configuration includes the **toolchain directory**, not merely
the compiler version. Measurements taken 2026-09-21 on `aarch64-apple-darwin`,
each run recompiling `adva-witness` from scratch with
`cargo clean -p adva-witness --release` and then
`cargo build --release --bin adva` (about 24 s of real compilation per run,
which is the evidence that the run really compiled):

```
configuration                                          sha256 of target/release/adva
RUSTUP_HOME=~/.rustup, toolchain `stable`   run 1      f2c914def8f3b36a577f68541be822d3a403c762e64aa165678fe8949855f83e
RUSTUP_HOME=~/.rustup, toolchain `stable`   run 2      f2c914def8f3b36a577f68541be822d3a403c762e64aa165678fe8949855f83e
RUSTUP_HOME=~/.rustup, toolchain `stable`   run 3      f2c914def8f3b36a577f68541be822d3a403c762e64aa165678fe8949855f83e
RUSTUP_HOME=~/.rustup, toolchain `1.96.1`    run 1      9b6fa650f4346b38f33ae2d6fee3c5dd3d33085f4b26b44c9167c9b7992f9425
RUSTUP_HOME=~/.rustup, toolchain `1.96.1`    run 2      9b6fa650f4346b38f33ae2d6fee3c5dd3d33085f4b26b44c9167c9b7992f9425
RUSTUP_HOME=<workspace copy of rustup>, run 1          5ca66b8d9d19233a37d50bd74fee6360d42d1cc0a16f52676b1f33b71aa4bab2
RUSTUP_HOME=<workspace copy of rustup>, run 2          5ca66b8d9d19233a37d50bd74fee6360d42d1cc0a16f52676b1f33b71aa4bab2
```

What this establishes, with the residuals left visible:

1. **Within a fixed configuration the build is deterministic.** Three
   consecutive runs in the `stable` configuration agreed exactly, and two runs
   agreed exactly in each of the other two configurations.
2. **The toolchain directory is part of the configuration.** Two `rustc`
   executables with **identical sha256**
   (`d10051fa870c54067bd21047e9709084141ffff65695537eb2c0c5d2477467d4`) produced
   different binaries when the toolchain lived in a different directory: 47 bytes
   apart between two of the configurations above.
3. **Pinning `channel` to an exact version was tried and reverted.** It moved the
   sysroot path away from the one the existing binaries were built with, so it
   changed the bytes it was meant to stabilise. `rust-toolchain.toml` stays at
   `stable`; the pinning experiment is recorded here rather than repeated.
4. **Not every observed difference is explained.** One binary built earlier in
   this same workspace differed from the `stable` rebuilds by 511 KB while all
   configurations produce files of the same size (6430624 bytes), and 47 bytes is
   the only difference for which a cause was identified. The mechanism behind the
   larger spread is **not** established. Treat cross-configuration byte-identity
   as **unestablished**, in either direction.
5. Only `adva-witness` was recompiled throughout. Nothing here says what a full
   workspace rebuild from an empty `target/` produces; `cargo clean` in full was
   not run, because it would discard crate downloads and risk unrelated work on a
   volume that is 96% full.

**How to check whether a rebuild really happened**: deleting only
`target/release/<bin>` is **not** sufficient — cargo re-links it from
`target/release/deps/` and finishes in about 0.01 s without compiling anything,
so any byte comparison afterwards is vacuous. Use
`cargo clean -p <package> --release`, and treat the wall time as the evidence.

Consequence for archiving: deleting `target/` loses no source and no capability,
and a rebuild is functionally equivalent. Byte-identity is achievable when the
configuration is reproduced, including the toolchain directory, but it is not
guaranteed in general — so where a specific artifact identity matters, keep the
artifact or record its digest rather than assuming a rebuild will reproduce it.

## Replaying historical library epochs

A stored epoch names its checker revision, which includes `Cargo.lock`.
The current lockfile differs from the receiver used for the Research 0150
epochs. A live receiver rejecting an old epoch is an expected boundary check.
Do not change its pin merely to get an accepted result.

The [frozen library CI procedure](maintenance/CI_LIBRARY_REPLAY.md) builds the
historical receiver separately, checks its archived examples, and checks the
live receiver's refusal. It requires repository history. See
[`scripts/check_frozen_library_ci.py`](../scripts/check_frozen_library_ci.py).
The [bootstrap runtime](BOOTSTRAP_RUNTIME_V0.md) is also a pinned release
profile, not a promise that every current checkout accepts every saved witness.

## Attribution

Follow [AI attribution](AI_ATTRIBUTION.md). Authorship, account use and
verification are recorded separately; neither a person's name nor a passing
check guarantees an unrestricted result.
