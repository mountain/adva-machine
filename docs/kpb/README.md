# KPB-14 inventory and documentary package pilot

This is **documentary tooling**, implementing gates 1 and 2 of
[KPB v0.1](../../spec/framework/kernel-package-boundary-v0.1.md).
It is not native package authority, an executable loader, a cut checker,
an admission decision, or a replacement registry. No payload, registry,
consumer lock, guard, frozen evidence or checking predicate is changed.

## Reproduce the bounded current view

Python 3.11+ and Git are required; no extra dependencies. Run from the
machine checkout, with the other two checkouts as siblings:

```sh
python scripts/kpb_inventory.py \
  --repository mountain/adva=../adva@3287c61ab7d16253605b3d0cca818f5a698e258b \
  --repository mountain/adva-machine=.@acfc9806fe18a36d0f7194dcc196a380b2834adf \
  --repository mountain/adva-library=../adva-library@19cede9c4532b7abd85f200daf7a9611a84563f0 \
  > /tmp/kpb-view.json
python scripts/test_kpb_inventory.py
```

The supplied `documentary-view-2026-09-29.json` is a **disposable generated
review snapshot**, never an input registry. Regenerate it from its recorded
commits; do not edit it or use it to override a source. The three repositories
retain every maintenance home and authority. `HEAD` may be requested for a
fresh independent view; it is resolved once to a full commit before reading.
Caller-supplied repository names are declared bindings, not authenticated
ownership. Git reads committed objects, not dirty working-tree files. It never
checks out, executes or imports source modules. A file is limited to 8 MiB,
unique reads to 256 MiB per repository, each Git call to 20 seconds; no aggregate
time/memory or native execution enforcement is claimed.

## Existing sources and mapping

| Owning repository | Existing source | Documentary projection |
| --- | --- | --- |
| adva | `docs/claims.toml` | Assumptions, scoped claim exports, declared evidence, explicit claim dependency IDs |
| adva | `python/adva/math_catalog.py` | Literal policy/limit declarations via AST; no checker execution |
| adva | `crates/adva-lisp/src/operation.rs` | The single OperationSpec table; separate versions, boundaries and lineage declarations |
| adva-machine | `spec/catalog.json` | Referenced specification/source units and byte-integrity comparisons |
| adva-machine | framework vocabulary v1/v2 | Separate versioned word declarations; existing implementation gaps retained |
| adva-library | `math/manifest.json`, `index.json` | Existing catalog entries, their homes, scoped evidence state, reuse requirements and material references |

The three inventory/pilot units have machine source homes:

| Unit | Source/checking home | Mapping basis and retained premises |
| --- | --- | --- |
| Witness rules | `crates/adva-witness/src/witness.rs` | Research 0107: each child formed, exact endpoint/polynomial transport, fresh occurrences, concrete nonzero guards |
| Learning method | `crates/adva-witness/src/free_roundtrip.rs` | Research 0136: supplied recipe/input domain, six finite stages, replayed history, retained guards; free remains Proposed |
| Library consumer | `crates/adva-witness/src/library_checkpoint.rs` | ADR 0038: full ancestry of at most four epochs, fixed checker/dependencies, fresh guarded reuse |

These are explicitly authored documentary mappings, not inferred exports or
installed package descriptions. Each record fixes repository, path, full
commit, selector, source digest, revision when supplied, premises, exports,
checker/profile, dependency edges, authority and unresolved fields. An absent
field is `null` with a disclosed gap, never a silently discharged premise.
Trusted component classes include checking code, decoder, arithmetic, build
dependencies and platform; `Cargo.lock` is a source reference, not a newly
performed trusted-base audit. Section 5's interface/effects, resource enforcement,
evidence receiving, custody and lifecycle gaps remain explicit.

## Dependency and impact graph

The snapshot's `dependency_impact_dot` contains a Graphviz graph including all
units. Arrows run **dependency → consumer**. `potential_impact_review` supplies
its transitive reverse-dependency review set; a review marker does not mean a
dependent claim is false. Missing exact dependency bindings remain separate
records and contribute no speculative edge. Documentary references, equal
names, matching hashes and interface-shape candidates create no dependency or
equivalence edge. Existing consumer gitlinks are recorded separately: reading
current library main does not upgrade either historical consumer.

```sh
python -c 'import json; print(json.load(open("/tmp/kpb-view.json"))["dependency_impact_dot"], end="")' > /tmp/kpb-impact.dot
```

`refactor_candidates` groups repeated metadata interface shapes for human
inspection of adapter or presentation reuse. It makes no semantic-equivalence,
efficiency or admission claim. No automatic rewriting or refactor is performed.

## Executed results and residuals

The original v0.1 retained snapshot contains 300 units (adva 237, machine 28, library 35),
348 dependency records and 41 unresolved dependency bindings. All projected
machine catalog and library index digest comparisons match. These checks are
byte/metadata checks, not re-executions of the underlying claims or checkers.
Historical library manifest references often retain monorepo paths without
repository/commit bindings. They remain unresolved; this tool never resolves
an absent cross-repository reference by a same-number/name local fallback.
The inventory covers the listed registries and selected pilot only, not every
material home or hidden dependency in the repositories. An unresolved field
does not retroactively invalidate historical evidence.

Five unittest checks passed: documentary B04 separates same exports across
packages/repositories and OperationSpec versions; documentary B06 exposes
missing/deleted premises and guards and rejects forged success metadata;
impact propagation excludes citations/similarity; repeated projections retain
unique full coordinates; dirty working-tree content cannot alter a view.
These are **metadata negative controls**, not executable B04/B06 conformance
or proof that source runtime guards were checked. An initial parser trial
refused the symbolic `BUILTIN_VERSION`; the adapter now reads that declaration
from the same registry rather than installing a second version table.

Next work is qualified source binding review for unresolved dependencies.
Gate 3 requires its own profile/receiving contract and evidence; this pilot
does not start it or authorize a general registry.

## Dependency binding successor (2026-09-29)

The v0.2 tool binds 39 of the original 41 unresolved dependency records.
All 39 are **explicit repository-relative paths in adva's claims registry**.
The adapter checks the exact path in that owning repository at its selected
immutable commit, records its digest and creates a separate documentary
source node. It never finds a target by filename similarity, research number,
another repository's same path, or a guessed alias. This is a source-byte
dependency, not a derivation edge or a discharged proof premise. Unreferenced
prose links still do not generate impact edges.

There are 24 newly referenced source files, giving a current view of 324 units
and the same 348 dependency records. 346 now have exact documentary bindings;
the following two exact claim IDs remain unavailable in the owning registry:

| Consumer | Absent dependency | Audited boundary |
| --- | --- | --- |
| `adva.bounded-experiment.borromean-cut-linkage.v0` | `adva.bounded-experiment.leak-wall.v0` | The distinct registered ID `adva.bounded-experiment.dual-facility-leak-wall.v0` is not an established alias. Research 0186 names that distinct ID; a later reading correction further prevents unqualified semantic substitution. |
| `adva.bounded-verified.symbolic-probe-matrix-shadow.v0` | `adva.exact.structural-forward-differential.v1` | Research 0143 and the triadic-period-bridge correction explicitly record this pre-existing absent entry. No replacement claim declaration was located. |

These observations were checked in `mountain/adva` at
`3287c61ab7d16253605b3d0cca818f5a698e258b`, using `docs/claims.toml`,
`docs/research/0186-dual-facility-leak-wall.md`,
`docs/research/leak-wall-reading-correction-lines-and-rings.md`,
`docs/research/0143-distinction-knowledge-and-free-boundary.md`, and
`docs/research/triadic-period-bridge-correction.md`.
An exact-declaration `git log --all -S` search of the fetched local history
for each missing ID returned no declaration-changing commit. This is not a
claim of exhaustive coverage of remote/unfetched branches or private history.
Closing these two gaps requires an explicit correction or versioned source
declaration by the owning registry, with scope evidence; this tool invents none.

`dependency-bindings-2026-09-29.json` is a compact derived review report: the
39 repaired records, two remaining gaps, a DOT graph restricted to repaired
bindings, and downstream potential-impact review sets computed using the
**full** current dependency graph. It is not an input registry. Reproduce it
by adding `--report-only` to the pinned command above. Omitting that option
generates the full v0.2 view/graph; it need not be committed as another copy.
The old v0.1 snapshot and its publication record are unchanged. To reproduce
that exact old projection, use the tool from machine PR commit
`07117ccae785b65b60233374b993b2ef233d1df8`, with the same three source pins.

Seven tests passed for this successor, retaining B04/B06 and adding exact
local-path/digest/impact bindings plus refusal of a real same-path file in a
different repository. Test sources are pinned; unrelated main growth does not
silently change these fixtures. The broader library manifest monorepo-path,
checker/build/guard, custody and receiving gaps remain outside these 41
declared claim dependencies. No registry, payload, evidence or consumer lock
is changed. No executable loader or admission is added.

Authored and checked by ChatGPT (OpenAI), contributed under Unknown v0.3,
submitted through Mingli Yuan's GitHub account as an authorized proxy.
No third-party implementation or source payload is incorporated. Source
metadata is a derived documentary projection of project-owned registries;
account use is not Mingli's technical review, endorsement or a correctness
guarantee.
