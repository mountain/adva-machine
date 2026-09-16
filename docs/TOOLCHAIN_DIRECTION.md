# Adva-machine: toolchain direction

Direction supplied by Mingli Yuan, 2026-09-16. Design and implementation by
ChatGPT (OpenAI), through his authorized account proxy; account use does not
imply his technical review or guarantee correctness.

This is the primary English direction document for international collaboration.
A [supporting Chinese summary](TOOLCHAIN_DIRECTION.zh-CN.md) is available.
New design decisions are maintained here first, following the
[documentation policy](DEVELOPMENT.md#documentation-language).

## Repository responsibilities

The user's explicit current direction takes precedence over the provisional
three-repository table quoted in that request:

| Repository | Direction | First local boundary |
| --- | --- | --- |
| `adva-machine` | Adva specifications, Rust/Python toolchains, Adva-written tools, future frontends and backends, conformance | An independent local continuation of `mountain/adva` at `bbfaf3a`; existing history and paths retained |
| GitHub `mountain/adva` | Evolve toward knowledge, research and reusable evidence | Historical source and future consumer of versioned toolchain interfaces; no remote reorganization performed by this step |
| `adva-library` | Its eventual split and ownership remain undecided | A pinned external dependency, retaining documentary catalogs, checked research snapshots and their distinct authority |

The local checkout is `/home/ubuntu/adva-machine`. The existing local `adva`,
its worktrees, and the independent local `adva-library` remain available.
`adva-source` records the historical GitHub source. The user subsequently selected
`git@github.com:mountain/adva-machine.git` as `origin`; `main` is now published
there and tracks `origin/main`. Completed, checked machine work is integrated
there. The original repository remains independently versioned.

## Knowledge consumers and dependency continuity

The user requires the dependency chain to remain intact. The knowledge repository
is introducing a [pinned consumer route](https://github.com/mountain/adva/blob/main/docs/KNOWLEDGE_MACHINE_BOUNDARY.md)
over an immutable machine commit and library revision. It builds the external
machine, compares one library fixture with retained native history/certificates,
and checks returned, rejected and suspended arithmetic interpreter executions
through native replay. See that repository for the consumer lock and evidence.

This is a first migration gate, not permission to remove either inherited tree.
Every later caller/package migration must retain its program format, input pins,
versioned receiver, source/history relationships and resource accounting. Old
evidence keeps its original machine and checker binding. A fixed library test
input does not create a runtime dependency on live knowledge research, and
documentary references do not become implicit executable imports.

## A usable boundary before moving source directories

The `spec/` index identifies the existing normative documents, IR schema and
separate research profiles by version and digest. `adva-rust/` and
`adva-python/` provide toolchain entry points over the existing implementation.
The actual Cargo workspace, Python package and frozen experiment paths remain
where their consumers and retained evidence expect them. These entry directories
are a migration boundary, not duplicate implementations.

The first common request contains a versioned machine profile, an unchanged
native program, input, lifetime instruction fuel and invocation quantum. Rust
admits every executable program. Rust and the existing Python research step
implementation execute the same request independently; a fresh Rust replay
receives the Python trace before the common report can say it is verified.
The common observer retains exact terminal data, rejection stage/reason,
exhaustion/suspension, state and trace. Wall time, step counts and checking costs
are recorded separately. No new stable semantic identity or certificate is
created by the Python envelope.

This first adapter supports the shared v0/v1 data-machine profiles. V2 is
available through Rust; the older Python v1 receiver is not silently relabelled
as v2. The structured compiler and input-binding `mix` remain bounded Adva
programs executed by their declared host. The arithmetic interpreter is a
program in this suite, not a third independent full-language VM.

The existing `python/adva` public facade is Rust-backed through PyO3. It remains
separate from the Python research step implementation. Three implementation
surfaces do not imply three independent authoritative machines, equal coverage,
or three unrelated specifications.

## Relationship to frontends, backends and mix

| Relation | Meaning | Present scope |
| --- | --- | --- |
| Rust/Python implements Adva | Execute admitted Adva code | Rust native machines; Rust-backed Python facade; external Python research step models |
| Adva to Rust/Python source | Emit a target-language program with a runtime contract | Future backend work; a wrapper calling the current VM does not establish it |
| Rust/Python source to Adva | Accept a declared source-language subset and translate/interpret it | Future frontend work; bindings are not such a frontend |
| Adva-written interpreter/compiler/mix | Programs that process programs under a declared profile | Existing finite arithmetic interpreter, structured bootstrap and input-binding projections |

For an interpreter for language L written in Adva, specialization produces an
Adva representation of L's program; a separate target backend is still needed
to emit Rust or Python source. Self-application can produce the corresponding
compiler and compiler generator when its language and specialization conditions
hold. See [Williams and Perugini](https://arxiv.org/pdf/1611.09906). The current
binding-only experiment retains static computation and interpreter execution;
general optimizing `mix` remains open.

## Keeping library choices reversible

The lock records a library revision and selected interface files. Both the
in-tree submodule and an explicitly supplied sibling checkout must satisfy that
same boundary. A path or catalog entry does not grant execution authority.
The geometry growth obligation remains Open; its documentary seal is not a
native `Seal`.

Use experience to decide among: one library with separate catalogs; a small
executable standard library plus a knowledge library; or independently versioned
packages with explicit dependencies. Before splitting, measure actual import
dependencies and identify which entries have a native execution/admission
contract. This step moves no library entry, changes no obligation and assumes
no package registry.

## Subsequent integration gates

The [formal communication vocabulary](../spec/framework/communication-v1.md)
governs content exchange across these boundaries. A receiving contract and
recorded outcome are prerequisites for treating a library or knowledge move
as complete. Its general native operation remains an implementation task;
host file operations cannot substitute for it. The existing native/profile
catalog and frozen evidence retain their original versions.

1. Common requests, reports and finite conformance for existing implementations.
2. A small explicit executable-library import contract, distinct from documentary
   citation and checked snapshot loading.
3. One target-language code-generation backend over a declared subset, checking
   results, refusals and the required provenance observer.
4. Frontends and useful optimizing specialization, with binding-time analysis,
   static evaluation, dynamic residualization and self-application checked under
   separately finite contracts.
5. Physical source moves only after their relative paths, build/package metadata,
   source fingerprints and historical replay obligations are received.

This ordering is an engineering choice for this migration, not a new language
theorem or a claim that the missing capabilities have already been supplied.
