# Fixed raw-evidence intake experiment

A separate receiver reads primitive raw proof bytes for p=x+y*z → 2*p → p,
rebuilds the unchanged native proof, then uses its private local checked handle
twice. The preceding documentary receipt remains `NotRun` / `NotGranted`.

See the [finite profile](../../docs/kpb/native-evidence-intake-v0.md) and separate
[execution record](../../docs/kpb/native-evidence-intake-results.md). This is a
standalone Cargo workspace; root Cargo files, `crates/` and the retained
checked-roundtrip v0.1 package stay unchanged. There is no native serialized
handle, general loader, arbitrary expression language or real consumer adoption.

From the repository root:

```sh
cargo fmt --manifest-path experiments/native_evidence_intake/Cargo.toml --check
cargo clippy --locked --manifest-path experiments/native_evidence_intake/Cargo.toml --all-targets -- -D warnings
cargo test --locked --manifest-path experiments/native_evidence_intake/Cargo.toml
cargo build --locked --manifest-path experiments/native_evidence_intake/Cargo.toml
cargo build --locked -p adva-witness --bin adva
python experiments/native_evidence_intake/run_transport.py \
  --transport-binary target/debug/adva \
  --checker-binary experiments/native_evidence_intake/target/debug/adva-native-evidence-intake \
  --output /absolute/fresh/outside-repository/intake-run
ADVA_EXCHANGE_BINARY="$PWD/target/debug/adva" \
ADVA_NATIVE_EVIDENCE_BINARY="$PWD/experiments/native_evidence_intake/target/debug/adva-native-evidence-intake" \
pytest -q experiments/native_evidence_intake/tests --basetemp /absolute/fresh/outside-repository/tests
```

The Python environment needs the project's existing test dependencies. The
outside-repository guard is unchanged: choose real scratch with no `.git`
ancestor. Never remove a repository marker or weaken the check to make a test
pass. Output directories must be fresh; no automatic retry/cleanup is provided.

The supervisor independently prepares and pins the receiver binding before
emitting the synthetic fixture, then performs unchanged send/receive/replay/ack
and invokes the separate checker. It retains exact stdout/stderr, all transport
observations, original source and publication record, receipt snapshots and a
separate native report outside the receiver store. Do not insert extra files
into that store; exact inventory is part of transport replay verification.

The checker commands are `receiver-binding`, `emit-fixture`, and:

```sh
adva-native-evidence-intake check RAW_JSON BINDING_JSON \
  --expect-binding BLAKE3_OF_BINDING_BYTES \
  --receiver native-evidence-receiver --context fixed-roundtrip-intake-v0
```

Only the exact independently selected synthetic proof bytes are supported.
The baseline revision records ancestry; generator/source digests identify the
new bytes. Receipt/producer success is never input to the native check. The
binding command takes no received payload or producer verdict. An altered
binding cannot authorize itself merely by supplying its new digest.

Project-original under Unknown v0.3, authored by dot (OpenAI), submitted through
Mingli Yuan's authorized account proxy; no personal endorsement is implied.
