# Architecture G1 projection: bounded implementation

Date: 2026-09-30. Reviewable local successor to KPB-14 PR2. This is original
engineering by dot (OpenAI), contributed under Unknown v0.3, prepared through
Mingli Yuan's account proxy. Account use is not his review or endorsement.
The initial measurements precede remote submission; actual publication and
merge are recorded separately by Git and pull-request evidence.

## Dependency and integration order

This patch starts at open PR2 head
`a0702dc99d5e12cc72af1936d82162fc5a8780b5`, not directly at machine main
`acfc9806fe18a36d0f7194dcc196a380b2834adf`. PR2 contributes the existing
registry adapters, two historical generated artifacts and their publication
records. These are not duplicated or represented as newly authored work.

Preserve PR2 before this successor in commit ancestry. For publication, review
a clearly labelled combined series that retains both PR2 commits and the G1
fixes, then merge its final checked tree atomically. This avoids exposing PR2
without the source-binding and graph corrections found in the G1 review. Recheck the final exact
commit and CI before reporting mainline integration. This patch neither closes
PR2 nor changes PR205. No fourth repository is needed: specifications and this
read-only adapter belong to `adva-machine`; owning registries, materials and
consumer locks remain in their three present homes.

The [proposed English contract](../../spec/framework/repository-exchange-registration-v0.1.md)
has all 60 clause IDs and N01–N20. The
[coverage map](architecture-contract-coverage.md) distinguishes documented,
implemented/tested documentary slices, historical runtime behavior and deferred
work. Formal adoption and full G1 acceptance remain separate from local checks.

## Reproduce

Python 3.11+ and Git; no additional packages, network access or native binary are
needed once the three immutable source checkouts are available as siblings:

```sh
python scripts/test_kpb_inventory.py
python scripts/test_architecture_projection.py
python scripts/architecture_projection.py \
  --repository mountain/adva=../adva@3287c61ab7d16253605b3d0cca818f5a698e258b \
  --repository mountain/adva-machine=.@acfc9806fe18a36d0f7194dcc196a380b2834adf \
  --repository mountain/adva-library=../adva-library@19cede9c4532b7abd85f200daf7a9611a84563f0 \
  > /tmp/adva-architecture-projection.json
```

The [retained local run summary](architecture-projection-run-2026-09-30.json)
records exact generator bytes, source manifest and measured spending. The later
[aggregate verification record](architecture-verification-2026-09-30.json)
adds full local Rust/Python checks and retains the initial environment failures.

Run the final command twice from identical generator bytes and Git base state;
`cmp` must find the reports byte-identical unless the disclosed wall-clock safety
cutoff interrupts one. Exit 0 means the projection completed within its declared
view, not that all dependencies/conditions were resolved. Exit 2 and `Unknown`
retain the stop reason and available observation prefix; malformed inputs are
`RefusedInvalidProjection`. Tiny output budgets may be unable to hold even an
Unknown report, in which case only a bounded stderr diagnostic is produced.

All sources are immutable committed Git **blobs**. Directory listings, Git replacement objects, working
files, other repositories' same-name files and `latest` fallbacks are not byte
bindings. The source manifest accounts for every successful unique source read,
including catalog/checker references and the two consumer lock JSONs. A claimed
repository name and matching digest do not authenticate control of the origin.

The generator record binds its base commit and exact source-file SHA-256 values.
When local generator changes are uncommitted, this is explicit; the base commit
alone does not reproduce those changes. A report is disposable and is never
read back as an authoritative registry.

## What is implemented

- `DocumentaryDeclaration` is a report-local documentary type. It is not a
  `PackageSnapshot`, native identity, occurrence, endpoint or receiving context.
  Unknown package/site/receiver fields remain null with residuals
- The old sources and full documentary coordinates are preserved. Source claim
  assumptions, counterexample boundaries and forbidden conflations are carried
  exactly from the owning registry. Missing guards, occurrence maps, revisions
  and homes remain explicit gaps
- Every projected dependency names typed endpoints, complete source coordinates,
  declaration origin, scope, original edge kind, evidence, algorithm version and
  input digests. An exact source-byte binding does not discharge a premise
- Only source-bound dependency edges propagate potential review. Real citation,
  structural-similarity, unknown-kind, unresolved and conflicting edges cannot
  enter the propagation relation. Each downstream witness retains the IDs of
  its ordered typed edge path; cycles and SCCs remain visible
- Nine status dimensions carry an observer, pins, attempt, uses and residuals.
  These observations describe this projection invocation, not the complete
  lifetime of the source. Receipt/ack/Listed claims cannot promote interpretation
  or native admission; they remain `NotRun` and `NotGranted`
- Consumer lock JSONs retain their exact bytes/values and hashes. The historical
  machine `e62d88d...` and library `73a6af4...` pins are not upgraded by reading
  newer main snapshots
- Declared Git/read/output/graph limits, deterministic spending and stop positions
  are reported. No automatic retry, restart, source write, transport or loader
  exists in this command

The legacy `kpb_inventory.py` entry also receives the minimal blob, integrity
and edge-filter repairs. Its original graph is still an unbudgeted documentary
helper; use `architecture_projection.py` for bounded SCC/path/status reporting.
The old frozen generated reports and their rights records remain byte-unchanged.

## Resource and trust boundary

Defaults: 16 MiB total unique source bytes, 8 MiB per blob, 4,096 Git calls,
4,096 projected nodes, 8,192 projected edges, 1,000,000 graph steps, depth 1,024,
32 MiB encoded report and a 120-second cooperative wall deadline. Each Git call
has a timeout capped at 20 seconds. CLI `--max-*` options select the finite budget
before an invocation; continuation does not reset a previous account.

Node/edge limits apply to projected records after the legacy registry parsers
run. Source bytes bound those parser inputs; no separate AST-count, parser-memory
or hostile-process containment limit is implemented. A cooperative deadline is
not a sandbox. Generator setup uses two local source-file reads and two Git calls
outside the source/traversal account, recorded separately in its binding.
Wall time and process memory are host measurements kept outside the deterministic
payload; they must not be reported as zero or confused with graph steps.

No source checker is executed. Existing guards are not evaluated, claims are
not proven, publication eligibility is not established by this projection,
and absence from the selected registries is not absence from every possible
private/unfetched history. `CompleteWithinDeclaredView` does not mean closed
premises or complete live-consumer inventory.

## Preserved source gaps

Both exact claim IDs remain unresolved; no adapter alias or new source claim is
invented:

1. `adva.bounded-experiment.leak-wall.v0`: introduced as a missing dependency
   in adva commit `511d179dec71ce6b188c36c91f3e47c1a31549a5`. The existing
   test repeats the string, which does not establish a declaration. The actual
   Borromean consumer uses the golden-ratio calibration/evidence; the distinct
   dual-facility flow experiment is not an evidenced substitute. Its
   [reading correction][leak-correction] further prohibits an unqualified alias
2. `adva.exact.structural-forward-differential.v1`: absent when the consumer
   arrived at `d1642a48793174363e03107584c905c5563ed0bc`.
   [Research 0143][structural-audit] retains the gap. Current Python code calls
   `evaluate_with_finite_differential`, while the historical wrapper used
   `evaluate_with_differential`; neither the method string nor a certificate
   format establishes the missing exact claim

An exact-declaration `git log --all -S` audit of fetched, non-shallow adva history
found no declaration for either ID. Future corrections belong in adva's owning
registry, with explicit source evidence, retained predecessor references and
scope. This patch changes no adva claim, test or evidence file.

## Deferred capabilities and next coherent step

G2 is **not implemented**. Boolean interface grouping is not structural matching.
A candidate next domain is the pinned Iota compact cut/term ledger, whose twelve
finite families expose event/cut/occurrence data. Before implementation, freeze
its extraction schema, comparison relation, preserved boundary/occurrence fields,
allowed transformations, deterministic budget, positive/near-match/adversarial
controls and the known absence of full annotated ancestry. No L2/L3 result is
claimed by this patch.

G3 requires its own one-route executable reuse/cut profile and B01–B12. Existing
Rust send/receive/replay/ack and strict v1 schemas are unchanged. The four-epoch
research loader bound is untouched. G4 needs a reviewed successor consumer lock.
G5 needs separate protocol ownership and authenticated remote/discovery/conflict/
withdrawal design. These are not supplied by a documentation index or read-only
G1 report. A new repository is unnecessary now; consider one for a separately
approved hosting service only after its ownership and protocol boundary exist.

[leak-correction]: https://github.com/mountain/adva/blob/3287c61ab7d16253605b3d0cca818f5a698e258b/docs/research/leak-wall-reading-correction-lines-and-rings.md
[structural-audit]: https://github.com/mountain/adva/blob/3287c61ab7d16253605b3d0cca818f5a698e258b/docs/research/0143-distinction-knowledge-and-free-boundary.md
