# Bounded local checked-cache reuse

This independent Rust research package calls the unchanged native witness and
compiler APIs. Its own workspace/lock preserves the root Cargo/crates freeze.
See the [v0.1 profile](../../docs/kpb/checked-roundtrip-reuse-v0.1.md) and
[retained execution/correction record](../../docs/kpb/checked-roundtrip-reuse-results.md).

From the repository root:

```sh
cargo test --locked --manifest-path experiments/checked_roundtrip_reuse/Cargo.toml
cargo run --locked --manifest-path experiments/checked_roundtrip_reuse/Cargo.toml
```

The binary accepts no external arguments or serialized checked handles. Its
JSON is bounded observation evidence, not a portable native authority token.
Project-original under Unknown v0.3; authored by dot (OpenAI) through Mingli
Yuan's authorized account proxy, which does not imply technical endorsement.
