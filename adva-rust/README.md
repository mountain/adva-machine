# Adva Rust toolchain

The implementation remains in `../crates/`, using the root Cargo workspace.
This directory is its common toolchain entry, not a second Rust implementation.

```sh
cargo build --locked --release -p adva-witness --bin adva
.venv/bin/python adva-rust/run.py toolchain/examples/arithmetic.request.json \
  --output target/rust-example
```

`run.py` uses the [common versioned request/report](../toolchain/README.md), with
native admission, execution and replay. V0/v1/v2 remain separate frozen research
profiles. Stable PSC0 compilation and native certificates still live in their
existing crates and interfaces. Adva-to-Rust source generation is a separate,
unimplemented backend direction.
