# Paired quotation through a checked Adva byte frontier

This is a finite research experiment requested by Mingli Yuan.
It builds Python `p` -> Rust `q` -> ordinary adva-lisp `r` -> Python `p`.
The last arrow includes an explicit byte observation of the existing Rust
kernel's ordered numeric outputs. There is no added Lisp interpreter,
string type, `print` builtin or change to the existing `adva run` caps.

The independently developed [Quine Relay](https://github.com/mame/quine-relay)
is a reference for the source-generation cycle criterion. This implementation
uses its own two-template construction and copies none of that project's code.

## The two library contexts

`adva/adva-library` is a dependency pinned by the parent Git tree. The sibling
`adva-library` checkout has its own named branch. At this calibration's pinned
revision their commit and tree are equal. Their paths, roles, and update
interfaces remain distinct. The runner checks clean worktrees, the parent
gitlink, both commits/trees and the selected material bytes. Git origin URLs
are configuration evidence, not repository authentication or a visibility check.

The complete paired context is quoted into both programs as data. It is not
read from the filesystem by the generated programs. The names `p`, `q`, and
`r` select documentary views of that retained context, not native identities.
Changing either repository later does not change an already generated relay;
a new binding requires a new calibration rather than a claim about `latest`.

## Finite construction

Let `A` be the Python emitter body, `B` the Rust emitter body, and `C` the
canonical paired-context bytes. Let `N` encode a byte string as an ASCII
decimal array, a notation accepted by both Python and Rust.

`P(A,B,C)` consists of the bindings `a=N(A)`, `b=N(B)`, `c=N(C)`, followed
by `A`. `Q(A,B,C)` contains Rust slice bindings for those same three finite
byte strings, followed by `B`.

- `A` emits the Rust bindings and the decoded `B`, hence running `P` gives `Q`.
- `B` reconstructs the Python bindings and decoded `A`, hence it obtains `P`
  without reading `P`, `Q`, or any repository. It then emits a finite Lisp
  program whose output coordinates encode those bytes.
- Evaluating that Lisp program and observing its byte frontier recovers `P`.

There is no infinitely nested literal containing the entire next program.
Each member retains the two finite *bodies* and their data quotation. The
candidate interpretation of the user's "dual force" is this paired
quotation/expansion correspondence. A source fixed point proves only this
finite correspondence; the general Adva thread dual and `D*` remain open.
Individual members are relay programs, not three individually self-printing
programs.

## The library determines the Lisp emission recipe

Both `epoch-0001` snapshots are reloaded with `load_library_v0`, using one
shared finite fuel account. The selected word must literally concern `2*x`
and `x+x`. `reuse_library_word_v0` checks its nonzero guards at every input
`1..8`, and refuses zero in both contexts. This stays inside that function's
existing `-8..8` admission bound.

For each byte `b`, choose `u = (b mod 8)+1`, `v = b-2*u`. Rust `q` emits

```lisp
(add (add (copy u)) v)
```

with `u` and `v` replaced by numeric literals. The value is `b`. Every literal
and intermediate value in this frozen recipe is a small exact integer in
the existing f64 realization. The module has no inputs and returns an
`(outputs Real ...)` frontier. Each repeated constant is a separate program
node. Since the program is closed and built from constants, its source
partition is empty; no source identities are invented for the library labels.

The research Rust example calls the existing parser, linker, compiler and
evaluator. It admits only finite integer outputs in `0..255`, writing one byte
per coordinate in order. It neither expands templates nor knows expected `p`.
Its complete compilation/graft/history artifact and evaluation certificate
are retained separately from the emitted Python source.

A control replaces the inner `add(copy u)` by `scale 2 u`. It must emit equal
bytes and have a different diagram. This observation does not authorize an
IR rewrite, identify source histories or issue an equation cell.

## Run and inspect

From the **adva** checkout, with the sibling library already cloned and a
fresh output directory:

```sh
git submodule update --init -- adva-library
cargo fetch --locked
python3 python/adva/adva.py quine-relay \
  --external-library /home/ubuntu/adva-library \
  --output target/quine-relay-run-01
```

Dependency initialization and fetching are preparation steps. The runner's
own build is offline and counted within the finite execution budget. Use the
pinned sibling library commit `a705aa2290d6ff73f6aaf89e3717413889c6d7ee`.
The original baseline must be an ancestor of the current commit, and tracked
Rust build inputs must still match that baseline except for the research
observer example. Experiment and documentation commits can therefore be
replayed without permitting kernel changes. The gate assumes a trusted local
checkout; it is not a sandbox for untracked build configuration or toolchains.

The paired context includes checkout paths. A fresh calibration on another
machine may consequently produce different `p/q/r` bytes while satisfying
the same exact closure criterion. The retained programs contain their original
context already and do not need those original directories to execute.

The outer command builds the Rust research adapter offline, rechecks both
libraries, constructs one `p`, runs it with isolated Python settings, compiles
its emitted `q` with `rustc`, executes `q`, and evaluates its emitted `r`.
Each generated program runs in an empty working directory without stdin.
The complete frozen templates are checked before execution: neither emitted
program has filesystem, network, source-inspection or environment-reading code.
This is an audit of these fixed programs, not a sandbox for hostile code.

Inspect `p.py`, `q.rs`, `r.adva`, `p-regenerated.py`, `context.json`,
`library-recheck.json`, `r-native.json` and `report.json` in the new directory.
The seven required controls and numerical limits are in `contract.json`.
All child calls, including Git queries and compilation, share the run deadline.
The command never starts a second attempt automatically. A timeout or budget
failure preserves `Unknown`; check the report and any `checkpoint-limit.json`.

The driver writes outputs under `target/`. The experiment changes neither library,
their manifests, the Pascal pins, geometry's Open obligation nor native Seal
status. Repository publication is a separately authorized action, and closure
does not admit a knowledge epoch or promote a language feature.

## Retained implementations and the 2026-09-20 correction

The retained bundle froze the implementations of 2026-09-09. Three later
supervisor fixes — a stricter whole-second child CPU admission, the
before-fork CPU allowance computation, and the Linux-only `RLIMIT_AS`
installation — changed `python/adva/quine_relay.py` without a retained copy, so
the recorded implementation correspondence no longer held for that side.
`docs/research/0164-evidence/postcommit-check-02/` retains the corrected bytes
and the drift class, and `verify_evidence.py` now checks the correspondence as
well as the stored bytes. No earlier payload was edited, no relay lap was
re-run, and the closure is explicitly **not** re-established: the contract pins
a library revision the checkout no longer holds, so the library gate refuses
before any relay work starts. See
[Research 0209](../../docs/research/0209-the-quine-relay-implementation-correspondence-corrected.md).

## Recorded result

The 2026-09-09 local run closed the relay with a 5,772-byte Python source,
6,073-byte Rust source and 167,492-byte Lisp source. All seven controls passed.
The first build exceeded its file-size cap; one explicitly debited correction
stripped debug information and completed. The complete local outputs are in
`target/quine-relay-run-01/` and `target/quine-relay-run-02/`.

After the user requested commit and push, one separately budgeted publication
validation also passed. The executed source was checked against implementation
commit `16b96e2ac256bba4ac3058a1d9272049da544a75`, followed by a post-commit
source-boundary check. See `publication-validation.json` for the additional
finite allowance and retained prior costs.

The [retained evidence bundle](../../docs/research/0164-evidence/README.md)
contains the exact programs, contracts, failure records, costs, implementation
snapshots and full native reports. Check its stored bytes without executing a
new research trial:

```sh
python3 experiments/quine_relay/verify_evidence.py
```

[Research 0164](../../docs/research/0164-paired-quotation-quine-relay.md)
records the derivation, measured scope, failed build, and the distinction
between discarding a discovery trace and erasing a program's semantic history.
