# Adva Python toolchain

This entry runs the existing Python research instruction model for frozen
data-machine v0/v1, with Rust admission and native replay of the resulting trace:

```sh
.venv/bin/python adva-python/run.py toolchain/examples/arithmetic.request.json \
  --output target/python-example
```

The [common contract](../toolchain/README.md) records that Rust is a dependency,
not an independent Python certificate authority. V2 is explicitly Unsupported by
this model; the wrapper never substitutes Rust execution for a requested Python
run. The existing `../python/adva` package is a separate Rust-backed PyO3 facade
and scientific integration surface. The two roles are listed separately in the
capability inventory.

Python source generation and Python-to-Adva source translation need their own
backends/frontends and declared subsets. These wrappers do not implement them.
