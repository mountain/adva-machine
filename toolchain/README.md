# Common local toolchain interface

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy;
not his technical review or correctness guarantee.

This is an engineering interface over existing, bounded implementations. It
introduces no new Adva primitive, source/occurrence identity or stable proof rule.
The [repository direction](../docs/TOOLCHAIN_DIRECTION.md) separates the machine,
knowledge and still-open library organization.

## Build and use

From the machine repository root on a POSIX host, with Python 3.11+ and the existing Rust
toolchain:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install blake3 pytest
cargo build --locked --release -p adva-witness --bin adva
.venv/bin/python adva-machine capabilities
.venv/bin/python adva-machine doctor
.venv/bin/python adva-machine doctor --library ../adva-library
.venv/bin/python adva-machine run toolchain/examples/arithmetic.request.json \
  --engine rust --output target/machine-rust-example
.venv/bin/python adva-machine run toolchain/examples/arithmetic.request.json \
  --engine python --output target/machine-python-example
.venv/bin/python adva-machine conform --output target/machine-conformance
```

Every output directory must be new. The two `run.py` entries under
`adva-rust/` and `adva-python/` accept the same request and output arguments,
with their engine fixed. These checkout entries do not yet constitute separately
published Cargo/Python packages. Existing `cargo` and `python/adva` commands remain
available at their historical paths.

## Request and report

`adva.machine.request.v0` has exactly these fields:

| Field | Meaning |
| --- | --- |
| `schema` | `adva.machine.request.v0` |
| `profile` | `data-machine-v0`, `data-machine-v1` or Rust-only `data-machine-v2` |
| `program` | The unchanged native JSON program for that profile |
| `input` | The native tagged data input |
| `fuel` | Original lifetime native instruction budget |
| `quantum` | Maximum instructions in this invocation, without fuel renewal |

The transport rejects duplicate JSON keys, nonfinite numbers, Boolean fuel and
unknown request fields. Rust performs program typing, instruction, shape and
capacity admission. Each route first requests zero-fuel admission. The Rust route
then runs the native machine. The Python route uses the already existing external
v0/v1 instruction models in `experiments/`, in a separate bounded process. Both
routes pass their execution artifact through fresh native replay.

`adva.machine.report.v0` retains request and executable digests, profile, exact
outcome, raw execution and receiving paths, instruction counts, resource limits,
child exit codes and timing. Native execution traces keep their original format.
Python-created traces are proposals until Rust replays them. No program is
considered equivalent solely because a report has a success string or digest.

The common outcome distinguishes `Returned`, runtime `Rejected`, admission or
transport `Refused`, `Unsupported`, and resource-limited `Unknown`. An adapter
failure is `Error`, not a language rejection. Native `Suspended` and
`FuelExhausted` remain separately recorded and are both open outcomes, never
proofs of divergence. Existing native checkpoint commands remain available;
the common wrapper does not yet add a resume protocol.

The first conformance observer checks exact terminal outcomes and, because these
two engines execute the same primitive profile, identical state and trace. A
future code-generation backend will need its own explicit correspondence and
observer: equal host steps or traces are not required merely by sharing a language.
All raw state and trace data are retained even when the common terminal projection
forgets them. No native PSC0 lineage or `SourceId` is invented here.

## Fixed engineering acceptance

`conformance.contract.json` pins sixteen cases before execution. They include
exact i64 boundaries, overflow, uninitialized reads, malformed inputs, invalid
register typing/schema, finite looping, suspension, zero fuel, v0/v1 capacity
differences, dynamic field/pack operations, and the existing Adva arithmetic
interpreter as a program run by both engines. It is not an Adva implementation
of the full machine.

One invocation allows at most 100 child processes, 80 native calls, 120 wall
seconds, 110 aggregate CPU seconds, 1 GiB address space per child and 64 MiB
artifacts. Child processes have CPU/file limits and a remaining-wall timeout;
only their own process group is stopped on timeout. Partial artifacts and errors
are retained. There is no automatic retry, refuel, fallback to another engine,
scope expansion or backend code generation. These are reproducible engineering
tests, not a new open-ended research search.

Single-request defaults are 30 wall seconds, 25 aggregate CPU seconds, three
child launches and 128 MiB artifacts. Building/installing tools and later archive
checks are outside execution timing. The supervisor is for trusted local engines,
not a sandbox for a deliberately hostile executable.

## Library connection

`library.lock.json` pins the current library revision and selected interfaces.
`doctor` accepts the in-tree submodule or an explicit separate checkout only if
the revision, tracked cleanliness and pins match. The receipt establishes
documentary integrity; it does not load every entry into Rust, discharge the
geometry obligation or turn documentary references into executable packages.

The final library layout remains Open. The current usable agreement is a fixed
external dependency plus explicit artifact roles. A later standard-library or
package split requires a native import contract for the entries it executes.

## Iota object-language example

The independent boundary-aware iota successor emits requests for this existing
runner. See [the pinned integration guide](../programs/iota-boundary/README.md)
for pure-iota source, explicit three-domain policies, retained reduction history
and the Rust execution/replay boundary.
