# G3 checked roundtrip reuse pilot v0.1

Date: 2026-09-30. Status: research-only finite profile and run contract.
Profile: `adva.checked-roundtrip-reuse.v0.1`. Checker: the standalone
`experiments/checked_roundtrip_reuse/src/main.rs` binary. This contract
is written before the packaging-successor execution; results are recorded separately below.

This is a packaging/build-binding successor of the [retained v0 contract](checked-roundtrip-reuse-v0.md),
whose published source is fixed at `f30023f3a3ccae7b5d11608b88e2ae76290f1b82`.
The original additive example triggered the existing surface-contract freeze of
all root Cargo files and `crates/`. This standalone package has its own
`[workspace]`, manifest and lock; those frozen root paths remain byte-identical.
All judgment, endpoint, guard and native identity rules are unchanged. The new
profile ID/build fingerprint refuses implicit cross-version cache reuse.

Authored by dot (OpenAI), submitted through Mingli Yuan's GitHub account
(`mountain`) as an authorized proxy. Account use is not personal authorship,
review, endorsement or a correctness guarantee. Project-original code and
prose are contributed under Unknown v0.3; no third-party material is copied.

## Question, inputs and authority

Can the existing exact witness APIs reuse one locally checked, fixed roundtrip
without repeating its parametric proof insertions, while retaining every fresh
input/guard and native occurrence check? The baseline is
`mountain/adva-machine@bc7f6b99edca00a12f659eb5a13f6c10fe700899`.
This is KPB-14 step 3 / architecture G3's **local checked-cache** route, not a
new receiving transport. Documentary transport remains unchanged and grants no
execution authority. G2's Iota candidates are not premises.

Only literal syntax p=x+y*z, q=2*p, forward p→q, reverse q→p, the existing
three-role boundary and canonical Unit/Construction/Space/Time seeds are
supported. Any changed endpoint, boundary, premise, interpretation, profile,
evidence or checker binding is refused. Native `Compose` does not check
endpoint incidence: this wrapper must check both literal endpoint equalities
before calling it. There is no arbitrary Compose input or serialized loader.

The existing `WitnessStoreV0::insert`, `CellTemplateV0::new/form`, compiler,
`instantiate_from_graft` and `CellInstanceV0::execute` remain the authority.
First checking inserts four seeds, two arithmetic transitions, one composition
and one symbolic Seal, and forms the linear p template. That symbolic Seal
retains all four guards; it is not a successful concrete execution. Every use
creates a fresh compiler-produced root context and native instance, then checks
all retained guards and the result via the unchanged execute API. Arithmetic
values are i32 inputs in [-16,16], converted exactly to BigInt. Zero leaves and
intermediates remain faults, even if the final polynomial would be nonzero.

## Cache and cut responsibility

A private, non-serializable checked handle owns its store, formed template,
original evidence and exact context. Only successful first checking constructs
it. Nothing accepts stored `FormedCellV0`, `Verified`, compiled certificates or
cache success flags as input. There is no export/import, cross-process reuse,
external premise substitution or cache eviction. A cache hit checks the complete
context, not a success boolean, and returns only a private one-use borrow.

Context includes the profile, fixed judgment, interpretation, complete literal
premises, raw evidence digest, and a path-delimited source/build digest covering
this binary, profile, native witness/arithmetic/boundary/seed sources, all
adva-ir/adva-lisp sources, crate manifests, both Cargo.lock files and rust-toolchain.toml. The handle cannot
cross processes/builds; compiler, dependency artifacts, OS and Rust platform
remain explicit same-process trusted-base assumptions. Source hashes bind bytes;
they do not authenticate software or prove correctness.

The supported cut is after checked parametric formation and before each fresh
native context/instance/execution. Its entry and exit are literally p→p under
the retained p,q,q,p guards. Three ordered role/hole bindings and native graft
provenance remain in each successful use. The cache never equates native
instances, occurrences, processes or histories merely from equal artifact keys.

## Finite resource contract

Each route has one cumulative account, at most two requested uses, 256 charged
wrapper operations, 8 MiB total encoded/hashed input/evidence bytes, 128 KiB per
encoded record, 16 live proof nodes, 32 proof dependency edges, proof depth 4,
and 128 KiB retained proof evidence per cache. The input language is generated
fixed syntax, not arbitrary external trees; supported expression depth is 4.
Fresh program source is generated from a bounded use ordinal only. Budget
checks occur before and after native calls; exhaustion is Unknown and retains
spent work. No continuation, retry loop, budget replenishment or persistence is
supported. A failed use spends its attempt and retains a failure record and available
checked proof prefix. The seven fixed runtime negative controls each have a
separate bounded account; they are evidence controls, not retries of a route.
Node/edge/depth and encoded-record bounds are post-operation admission checks
on this fixed syntax, not preemptive allocation limits for hostile input.
Source byte charges precede hashing; encoded bytes are also recorded as observed
when a post-serialization budget check refuses them.

The 30-second runtime deadline is cooperative; it cannot interrupt a native
call. CI additionally uses a 60-second process timeout and a 512 MiB virtual
memory ceiling for the already-built example, and a 10-minute job limit.
An OS kill may leave no complete report or resumable state; it is never success.
Compilation/setup have separate CI timing and are not disguised as reuse cost.
Logical byte/storage counts are not physical memory measurements.
`peak_evidence_bytes` is one canonical serialization of the unique proof
ledger; the native store and retained audit vector both hold that ledger.
It excludes Rust container overhead, compiler temporaries, native dependency
allocations and report metadata. The outer memory ceiling covers the whole
runtime process; no measured allocation reduction is claimed. Operation
counts cover wrapper API calls, proof nodes/edges and encoded bytes;
`proof_insert_calls` counts direct parametric proof insertions only, while each
separately counted native instantiation also calls the store internally; they do not
claim to count BigInt machine instructions or give a wall-clock speedup.

## Comparison and controls

Two full replays independently rebuild proof/template before use; the cache
route first-checks once, then separately records each hit and fresh use. Both
must report equal scoped judgments, result values, premises, guards and residuals
for [2,3,4] and [5,2,3]. Native identity is scoped: occurrence labels such as `occ:0` are diagram-local,
and instance ordinals are store-local. The report retains native program/source/
occurrence bindings and a process-local cache context alongside those labels.
Independent replay stores may both allocate ordinal 0; this is not identity
across contexts. Evidence,
seven retained negative-control records and cumulative/per-stage accounts are
printed as JSON; bounded final report encoding has a separate stderr account; elapsed time is observed
separately from deterministic evidence. The producer recipe is not needed after
checking except as retained, digest-bound evidence; no producer verdict is used.

Tests cover changed input and zero guards, intermediate zero, changed profile,
checker, premises, evidence and interpretation; disconnected cancelling ratios;
unformed/malformed boundaries; missing/deleted guards and forged success data;
fresh native occurrences; exhaustion of operations, bytes, depth and elapsed
time; exhausted two-use lifetime; and replay/cache accounting equivalence.
No arbitrary equality rule, native admission from Iota, consumer adoption,
general cut checker, four-epoch ancestry exemption or full G3 completion is
claimed. Frozen library sources, evidence and consumer locks stay byte-identical.

## Reproduction and evidence

```
cargo test --locked --manifest-path experiments/checked_roundtrip_reuse/Cargo.toml
cargo run --locked --manifest-path experiments/checked_roundtrip_reuse/Cargo.toml
```

See ADR 0017, ADR 0018, ADR 0034 and Research 0136 for the unchanged native rules.
The architecture contract's VERIFY-01–05, CUT-01–03, N11/N18/N20 and KPB
B01/B02/B03/B06/B07/B08/B10/B11/B12 motivate these controls. Namespace and
cross-repository documentary obligations continue through G1; this pilot does
not implement package import or claim every KPB/G3 acceptance case is complete.

The [execution and review record](checked-roundtrip-reuse-results.md) records
actual runs and initial failures separately from this frozen input contract.
