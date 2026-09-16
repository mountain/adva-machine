# Adva specification index

This index is the local machine repository's entry to Adva's existing contracts.
It references their canonical files and fixed bytes; it does not copy or
reinterpret them. `catalog.json` distinguishes stable PSC0/IR from separately
versioned, bounded data-machine research profiles.

`../docs/SEMANTIC_SCOPE.md`, `../docs/PROGRAM_PROCESS_CORE.md`, the relevant ADRs
and `../docs/claims.toml` retain their declared authority and limits. Rust remains
the current admission and native certificate authority. A matching file digest
records integrity, not semantic correctness.

The common toolchain request/report boundary is described in
[`../toolchain/README.md`](../toolchain/README.md). Its wrapper schema is neither
a replacement for `adva.ir` version 1 nor a new stable Adva language.

## Formal framework vocabulary

[Communication v1](framework/communication-v1.md) formally defines
`communicate`, `send`, `receive`, `acknowledge` and `accept`. Their definition
is adopted; the general native exchange operation is not yet implemented.
[ADR 0047](../docs/adr/0047-formal-communication-vocabulary.md) records that
decision and its implementation gate.

[The framework registry](framework/vocabulary-v1.json) pins the normative
document and its historical sources. It is a vocabulary index, not a parser,
operation registry or conformance result. `catalog.json` continues to pin the
existing native contracts and research profiles independently.

[Documentary library entry exchange v1](framework/documentary-exchange-v1.md)
now supplies a bounded Rust `adva communicate` CLI receiving route. It binds
one reviewed original entry, retains its home and obligations, and records
documentary acceptance and an observed acknowledgment. General communication
and native mathematical admission remain open. [ADR 0048](../docs/adr/0048-bounded-documentary-communication.md)
records the operational boundary; the earlier vocabulary registry remains a
frozen record of adoption, not the current implementation inventory.
