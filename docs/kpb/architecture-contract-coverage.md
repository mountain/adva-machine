# Repository exchange and registration v0.1: clause coverage

Date: 2026-09-30. Status: **reviewable implementation map; not an adoption or
conformance certificate**.

This record maps every clause and N control in the proposed
[architecture contract](../../spec/framework/repository-exchange-registration-v0.1.md).
It records the complete clause/control map and the new G1 documentary implementation.
Fresh checks below bind actual implementation bytes and remain separate from
historical native evidence; no runtime result is inferred from the specification.

## Baseline and evidence boundary

- Local integration starts on `work/architecture-contract-v01` at KPB-14 PR2
  `a0702dc99d5e12cc72af1936d82162fc5a8780b5`, whose status was OPEN at the
  reviewed baseline
- Frozen machine main/read baseline:
  `acfc9806fe18a36d0f7194dcc196a380b2834adf`
- Frozen `adva` read baseline:
  `3287c61ab7d16253605b3d0cca818f5a698e258b`
- Frozen library read baseline:
  `19cede9c4532b7abd85f200daf7a9611a84563f0`
- Historical consumer pins remain machine
  `e62d88dcc83fc4967260866518029942b9631b71` and library
  `73a6af4ac4ed8225366d3c16794e309cff15f51d`
- PR2's documented 324 units, 348 dependency records, 346 exact bindings and
  two gaps are historical review-snapshot observations until a distinct local
  reproduction is recorded
- The reviewed Chinese source, `contract-review.md`, SHA-256
  `7481896c4623fcc1eca88804bf986dca60d480521170cbef879831eed9989158`, is the
  translation identity baseline; it is not an executable source or new registry

The specification is a proposed English-first home. GEN-03 records the deliberate
transition from an editable-only draft to authorized local repository engineering.
No formal adoption, remote submission, merge, exchange, migration or release is
established by that transition. Preserve separately any later integration and
execution records.

### Coverage labels

- **Documented:** the obligation/decision is present in this draft; no runtime
  implementation or acceptance result is asserted
- **Partial historical:** a bounded existing source documents some relevant
  behavior; its old results are not a fresh run and do not cover the whole clause
- **Deferred:** implementing or deciding this capability is outside this initial
  mapping; there is no claimed completed test or gate
- **Partial implemented/tested:** the named documentary slice is implemented
  and exercised by the new controls; it is not full-clause runtime conformance

Every clause is represented below. A coverage row is not a promise that every
obligation has been implemented. “Partial historical” never means that a new
normative clause has passed in full. A documentary negative control does not
count as native executable conformance.

## All 60 normative and decision clauses

| Clause | Obligation / documentary home | Current coverage | Remaining evidence or decision |
| --- | --- | --- | --- |
| GEN-01 | Draft status and MUST/MUST NOT/SHOULD meaning; contract §1 | Documented | Explicit adoption record before treating proposed obligations as adopted |
| GEN-02 | Existing / under-review / proposed evidence labels; contract §1 | Documented | Every new result must retain label, exact source and actual execution status |
| GEN-03 | Authorized local engineering scope and proposed specification home; contract §1 | Documented + checked diff | Local successor on PR2; no remote write, final integration/adoption separate |
| GEN-04 | Reading baseline versus historical consumer pins; contract §1 | Partial implemented/tested | consumer_locks + N10 preserve exact historical JSON/pins; no native replay |
| GEN-05 | Earlier receiving, guard, growth and publication obligations survive; contract §1 | Documented | Explicit versioned decision for any future conflict |
| OWN-01 | Repository/receiver/site/consumer responsibility matrix; contract §2 | Documented | Source ownership remains declared; no physical-migration authority inferred |
| OWN-02 | Preserve material home; library split remains Open; contract §2 | Partial implemented/tested | source_conditions + N15 reject silent library-home replacement; lifecycle migration deferred |
| OBJ-01 | Distinct entity types and occurrence identity; contract §2 | Partial implemented/tested | project_units types DocumentaryDeclaration and leaves package/occurrence/context/site absent; not all entity implementations |
| OBJ-02 | Separate repository/site/context/endpoint coordinates; contract §2 | Partial implemented/tested | Separate null package/site/receiver fields and explicit capability flags; no inferred endpoint |
| REF-01 | Full documentary coordinates, digest, original revision and missing fields; contract §3 | Partial implemented/tested | project_units + source_manifest fix full coordinates/SHA/revision and gaps; no native identity |
| REF-02 | Separate declared origin, byte integrity and identity/authentication; contract §3 | Partial implemented/tested | AuditedRepository checks immutable blob bytes with Git replacement disabled; authentication explicitly NotPerformed |
| REF-03 | Exact dependency or explicit unresolved result; mismatch versus unavailable; contract §3 | Partial implemented/tested | N01/N02 separate mismatch/conflict from unavailable Unknown; two exact IDs remain unresolved |
| EDGE-01 | Typed edges and evidence; no similarity-to-authority promotion; contract §3 | Partial implemented/tested | typed_edges records typed endpoints, source, declarer, scope, evidence, status, algorithm and digest; no derivation authority |
| EDGE-02 | Explicit direction, typed impact traversal, cycles and exhaustion; contract §3 | Partial implemented/tested | impact_graph + GraphControls cover real excluded edge types, SCCs, typed paths and partial exhaustion |
| REF-04 | Preserve PR2 snapshot counts and under-review scope; contract §3 | Documented + reproduced | Fresh pinned local run: 324 records /348 dependencies /346 bound /2 gaps; PR2 historical snapshot unchanged |
| EX-01 | Prefer applicable existing Rust transport; bounded profile and vocabulary; contract §4 | Partial historical | Existing route is limited to one documentary entry/eight files; no new exchange executed here |
| EX-02 | Independent contract/context/checker/publication/budget bindings; unchanged strict schema; contract §4 | Partial historical | Existing strict types retained; any new fields require projection or successor schema tests |
| STAT-01 | Independent status vector with observer/pins/attempt/use/residuals; contract §4 | Partial implemented/tested | status_vector/validate_statuses + N05/N09 provide nine contextual dimensions for this projection attempt only |
| EX-03 | Receive durability, recheck idempotence and limited acknowledge; contract §4 | Partial historical | Fresh existing transport tests pass (15 Rust CLI +21 Python routine); full runtime scope and failure limits remain separate |
| EX-04 | Preserve NotRun/NotGranted and Unknown traces; no retry/refill; contract §4 | Partial historical | Existing receipt/profile boundary retained; fresh interruption, pending/lock, no-retry and lost-observation controls passed |
| REG-01 | Disposable projection of existing registries; no second registry; contract §5 | Partial implemented/tested | Existing build adapter read from fixed Git blobs, no registry writes or source execution |
| REG-02 | Minimum registration fields and authentication disclosure; contract §5 | Partial implemented/tested | Required field slots/gaps are represented; real publisher, package, site, lifecycle and receiving records remain unavailable |
| REG-03 | Registration, index, discovery, availability, receipt and adoption separate; contract §5 | Partial implemented/tested | No promotion of Listed/receipt/ack into interpretation/native/adoption; no discovery service |
| REG-04 | Site scope, budgets, view version, staleness and incompleteness; contract §5 | Deferred | Hosted site/query protocol and enforcement require a separate bounded design |
| REG-05 | Immutable-coordinate conflicts, retained withdrawal/history; contract §5 | Deferred | Registration-store lifecycle not implemented by a read-only projection |
| REG-06 | Identity/auth/authz/replay/conflict/withdrawal/disconnection protocol; contract §5 | Deferred | G5 protocol design, independent approval and bounded multi-node failure tests |
| REG-07 | Hosting goal distinct from API/backend/installer/loader; contract §5 | Documented | Those capabilities remain unimplemented by this draft; verify claims stay bounded |
| REG-08 | Reconstructible source manifest, dependencies, gaps, candidates and cost; contract §5 | Partial implemented/tested | source_manifest/generator_binding/resource_account + deterministic reproduction; structural candidate generation deferred |
| MINE-01 | Pinned typed inputs with occurrences/premises/guards/residuals; contract §6 | Deferred | First finite extractor/domain must declare missing fields without filename inference |
| MINE-02 | Frozen rules, canonicalization, deterministic steps and partial cutoff; contract §6 | Deferred | Comparator replay and step/wall-clock exhaustion tests required |
| MINE-03 | Only profile-authorized algebraic rules with concrete guards; contract §6 | Deferred | No default cancellation, copying or normalization; exact allowed-rule tests required |
| MINE-04 | Declared matching relation, witness and unmatched boundaries; contract §6 | Deferred | Mapping witness validation and scoped failure/Unknown tests required |
| MINE-05 | Complete candidate evidence with no source/checker/lock mutation; contract §6 | Deferred | Candidate schema and read-only/no-authority controls required |
| MINE-06 | Existing shape cards/candidates are not L2/L3; new comparator separate; contract §6 | Partial historical | `exchange_routine/structure.py` and PR2 only establish documentary shape; new comparator requires actual rules/tests |
| VERIFY-01 | Scoped judgment, trust, domain, evidence, budget and residuals; contract §7 | Partial historical | KPB describes applicable boundaries; no general success checker is added |
| VERIFY-02 | Separate first/cache/reuse cost and complete cache binding; contract §7 | Deferred | New executable cache route needs its own profile/checker and fresh-instance controls |
| CUT-01 | Preserve every cross-boundary obligation when splitting; contract §7 | Documented | No general fragment composition or cut acceptance is implemented |
| CUT-02 | Minimum cut fields do not create a cut checker; contract §7 | Documented | Actual receiving rule and executable checker are deferred to G3 |
| CUT-03 | Recheck joins, freshness, premises, residuals and total account; contract §7 | Deferred | Executable disconnected/zero-guard/collapsed-occurrence/formation tests required |
| VERIFY-03 | Versioned one-route executable pilot, full replay comparison, four-epoch limit; contract §7 | Deferred | G3 profile, checker, positive/negative controls and total-cost evidence |
| VERIFY-04 | Declared full budgets, actual enforcement and successor accounting; contract §7 | Partial implemented/tested | Finite source/Git/projected-node/edge/traversal/output limits and retained prefixes; parser memory and hostile sandbox not supplied |
| VERIFY-05 | Explicit receiver replay/cache/proof/premise route and trust; contract §7 | Documented | No portable Verified or general boundary-proof route supplied |
| VERIFY-06 | PR205 effect witness is observational, not retry/write authority; contract §7 | Documented | Preserve original effect records; no new effect trial run in this documentation step |
| LOCK-01 | Exact executable locks independent of reading/index pins; contract §8 | Partial implemented/tested | consumer_locks retains exact historical JSON and digests; no migration or current-use audit |
| LOCK-02 | Reviewed successor lock, reruns, rollback and retained predecessor; contract §8 | Deferred | G4 adoption is not authorized or performed by a projection |
| LOCK-03 | Enumerate all live consumers before retiring any source; contract §8 | Deferred | No exhaustive inventory or source-retirement claim supplied |
| CHANGE-01 | Proposal/adoption/run/admission/adoption/release/retirement separated; contract §8 | Documented | Maintain actual role and lifecycle records for this local work |
| CHANGE-02 | Versioned substantive changes, traceable errata and separate licensing; contract §8 | Documented | Future revisions require predecessor/scope and evidence mapping |
| CASE-01 | Fixed Iota package and distinct receiver history; contract §9 | Documented | Historical record only; no fresh Iota replay or source-private-content import |
| CASE-02 | Original NotRun/NotGranted; same-agent verifier limitation; contract §9 | Documented | Do not overwrite receipt fields or infer independent verification |
| CASE-03 | No full Iota equivalence/communication or library-route exemption; contract §9 | Documented | Independent applicable receiving tests remain required |
| CASE-04 | Iota L1/L2 proposal only; package/execution/adoption gated separately; contract §9 | Deferred | Selecting this domain would require pinned extraction and mapping witnesses |
| TEST-01 | All N01–N20 obligations; retain inputs, checker, budget and evidence; contract §10 | Documented | Control matrix below requires explicit implementation-level evidence |
| TEST-02 | Positive controls plus separate schema/structure/semantic outcomes; contract §10 | Documented | Must retain KPB B01–B12 and existing conformance; no metadata-to-native promotion |
| GATE-01 | G0–G5, KPB mapping, maintainer, pins, costs and residuals; contract §11 | Documented | Each gate requires a distinct decision/evidence record; none automatically passes |
| GATE-02 | G1/G2 priority, open PR2 dependency and no G3 grant; contract §11 | Documented + partial G1 | G1-only implementation explicitly depends on PR2; G2 not relabelled from metadata grouping |
| DEC-01 | Adoption, normative home and final path; contract §11 | Deferred | Proposed path exists locally; formal home/adoption decision remains unresolved |
| DEC-02 | First finite G2 domain and budget with positive/near/negative examples; contract §11 | Deferred | Record selected finite domain and implementation-local limits when decided |
| DEC-03 | Candidate review owner and source correction for two missing claims; contract §11 | Deferred | No substitute declaration may be invented by tooling |
| DEC-04 | Hosting maintainer, criteria and trust model; contract §11 | Deferred | G5 decision; does not block read-only G1/G2 |

## N01–N20 control coverage

All rows currently lack a fresh architecture-contract acceptance result in this
skeleton. “Existing basis” identifies a potential reusable test surface, not a
claim that the architecture control has been fully exercised. The integration
reviewer should add exact test names and outcomes without erasing the limits.

| Control | Required observable result | Existing basis / intended test level | Result and residual |
| --- | --- | --- | --- |
| N01 | Reject commit/path/digest mismatch; no latest/local substitute | PR2 binding tests; new documentary projection | Passed documentary controls: exact blob/digest conflict, edge digest/coordinate, Git replace; no native conformance |
| N02 | Unknown/unresolved for unavailable required source; block dependent success | PR2 unresolved dependencies; documentary projection | Passed documentary controls: absent exact IDs/bytes/revision stay unresolved or Unknown; no fallback |
| N03 | Separate same-name repository/profile coordinates; no import | PR2 documentary B04; finite comparator inputs | Passed documentary scope: same exports/version coordinates remain distinct; old B04 same-repository tests retained |
| N04 | Missing premise/guard/residual/occurrence blocks unconditional success | PR2 documentary B06; preservation validation | Passed documentary retention/deletion controls for source claims and library assumptions/guards/residuals; occurrences remain explicit unavailable |
| N05 | Receipt/ack/Listed cannot upgrade interpretation/native admission | Status projection; existing transport receipts | Passed status-projection controls; historical receipts untouched and not rerun |
| N06 | Same contract/package recheck gives AlreadyAccepted with zero new effects | Existing Rust transport conformance | Passed existing runtime: Rust send_receive_repeat_and_ack_keep_obligations_and_source and Python explicit-second-run control; no new receiving schema |
| N07 | Altered receipt/payload/inventory conflicts or rejects without overwrite | Existing Rust transport conformance | Passed existing runtime: stored_tampering_and_scope_inflation_are_detected plus payload/obligation refusal controls; no overwrite repair |
| N08 | Lock/pending/reply/exhaustion/unknown effects stay Unknown without retry/refill | Existing Rust transport and exchange supervisor | Partial passed: new projection budgets/prefixes plus existing runtime lock/pending/missing-reply/checker/budget controls; no power-loss claim |
| N09 | Unsupported site verification assertion remains only an assertion | Documentary status/report validation | Passed local report controls refusing imported success/Listed promotion; no hosting service |
| N10 | Current catalog cannot silently replace historical consumer pin | PR2 consumer pin reporting; documentary lock separation | Passed exact historical-lock read/digest/pin controls; native adoption replay not run |
| N11 | Disconnected or zero-guard composition fails despite local successes | Existing KPB executable obligations B02/B03 | Deferred G3 executable test; metadata comparisons do not discharge it |
| N12 | Similarity with different histories/copy/discard yields at most scoped candidates | New finite comparator and witness tests | Partial passed: real structurally-matches/cites edges excluded from impact; genuine structure/history/copy comparison deferred G2 |
| N13 | Exhausted comparison budget yields Unknown and partial search record | New finite comparator step/time bounds | Partial passed: graph step/depth cutoff is Unknown with prefix; comparator node/edge/time tests deferred G2 |
| N14 | Method cannot rewrite its checker/acceptance rules | Candidate/read-only controls; executable KPB B09 | Partial passed: forged verified/native flags cannot grant authority; no search method/checker mutation interface supplied |
| N15 | Broken provenance or silent home replacement conflicts and blocks adoption | Documentary source/home preservation | Partial passed: owning library home and source conflicts protected; registration lifecycle/adoption checks deferred |
| N16 | False general loader/cut checker/sync claim fails capability acceptance | Capability claim/report validator | Passed report-capability controls: no claimed loader/cut checker/federation/structural matcher |
| N17 | Post-rename uncertainty/failed durable record preserves observations and Unknown | Existing transport failure boundary; PR205 reference | Partial passed: actual native receipt survives injected supervisor observation loss without ack; general post-rename/durable-write crash proof not supplied |
| N18 | Changed cache input/premise/checker/occurrence triggers recheck or refusal/Unknown | KPB B07/B11; future cache profile | Deferred G3 runtime check; no new executable cache implemented |
| N19 | Unsupported executable import cycle remains documentary and cannot execute | Dependency graph cycles; future receiving rule | Partial passed: cycles/SCCs and paths preserved with no executable capability; native cycle admission unchanged and not rerun |
| N20 | Unformed child/malformed boundary rejected before composition | KPB B01/B02; future composition checker | Deferred G3 native control; schema validation alone is insufficient |

## Gate disposition

| Gate | This local delivery establishes | Still open |
| --- | --- | --- |
| G0 | English-first review draft, proposed path, full clause/control map | Formal adoption, maintainer/reviewer decisions and final path record |
| G1 | Pinned read-only projection, exact sources, typed dependencies, nine-dimensional observations, locks, SCC/path evidence and documentary tests | Missing source conditions/IDs, complete registry lifecycle, parser-memory limits and full gate review; no native proof of claims |
| G2 | Finite comparison requirements and capability boundaries specified | Concrete domain decision, implemented rules/witnesses and acceptance evidence |
| G3 | Existing transport retained as a bounded basis | New executable reuse/cut profile, checker and complete cost/conformance evidence |
| G4 | Historical consumer locks remain governing | Authorized successor lock and individual consumer migration evidence |
| G5 | Future hosting/distribution requirements enumerated | Protocol ownership, identity/security design, authorization and multi-node tests |

## Fresh checks and integration additions

At initial creation of this record:

- A local comparison of anchored clause declarations in the reviewed source and
  English specification found exactly 60 identifiers, once each, in the same order
- The same comparison found N01–N20 once each and in the same order
- These are documentary identity checks only, not semantic verification,
  executable controls, or a gate pass

### Fresh local implementation evidence

- `scripts/architecture_projection.py` implements schema
  `adva.repository-architecture-projection.v0.1` and rule set
  `documentary-source-binding-and-impact-v0.1`
- `scripts/test_architecture_projection.py`: 38 finite documentary controls
  passed; `scripts/test_kpb_inventory.py`: seven retained controls passed
- Two final 9,698,886-byte projections were byte-identical, SHA-256
  `622a6d34b61e1f3b6905bafdfb46a9312417eadd16ca60ea990bbaa87dc8f367`;
  60 source blobs /1,906,611 source bytes /185 Git calls /7,932 graph steps.
  Outer wall times: 1.7110s and 1.6013s; cumulative child peak RSS: 80,488 KiB
- Separate reviewing agent reran the 45 tests, all six audit reproductions and
  an independent 150-graph reachability/SCC/path oracle with no remaining blocker
- `.github/workflows/architecture-projection.yml` wires the two documentary
  suites and pinned double reconstruction into future CI. It has not run remotely
- `python -m py_compile` on all four changed/new Python scripts passed;
  `git diff --check` passed
- Publication `--history` check passed for identified withdrawn content:
  4,520 unique blobs, 12,395 members; this is not a rights review of all legacy files
- The first snapshot had no Cargo/pytest available. The later
  [aggregate verification record](architecture-verification-2026-09-30.json)
  records recovery in isolated official tool environments: 282 Rust workspace
  tests, 13 release numerical-boundary tests, 21 exchange routine tests, and
  full pytest with 2,896 passed /4 skipped /26 subtests passed. The skips require
  absent lawful external images/PDF inputs. No Rust/transport implementation
  changed, and these existing-profile tests do not complete a new G3 profile
- The [retained generated summary](architecture-projection-run-2026-09-30.json) and its publication record identify final
  source digests, budgets, costs, reproduction outcome and scope limits

### Later aggregate verification and retained environment failures

The repository's declared Rust stable toolchain resolved to rustc/cargo 1.98.1;
Python 3.12.14 used pytest 9.1.1, blake3 1.0.10 and maturin 1.15.0 in an isolated
venv, with numpy 2.3.5, scipy 1.17.0 and sympy 1.14.0. No global configuration,
lockfile, source checker or acceptance rule changed. Strict Clippy and rustfmt
passed. Doctor became Ready after the missing release binary was built; the
16-case Rust/Python v0/v1 conformance suite passed with 68 native calls. The
math catalog remained documentary-only, with its growth obligation Open.

Initial exchange/full pytest attempts exposed an environment issue: all default
writable roots had a `.git` ancestor, and `/var/tmp` resolved to `/tmp`. The
existing outside-repository output guard correctly refused those destinations.
The first full run retained 12 failures, 2,884 passes, four skips and 26 subtest
passes in 420.43s. A sandbox-approved real scratch directory without a `.git`
ancestor allowed the unmodified guard to run normally. The final full run
passed 2,896 tests with four declared skips and 26 subtest passes in 422.43s.
No marker was removed and no guard weakened. The original G1 run summary keeps
its initial NotRun observations; the later record adds these new observations
rather than rewriting the earlier history. Remote CI had not run at this local verification snapshot; later PR checks
are separate observations.

### Discovered failures and corrections

The preceding PR2 positive tests did not expose several boundary defects. The
new controls deliberately reproduced citation/similarity impact leakage, a Git
tree being hashed as a file, missing digest-conflict reporting, and loss of claim
counterexample/forbidden-conflation fields. A separate code review found local
Git replacement refs could change bytes under an old pin, absent revisions were
mislabelled malformed, malformed registry types escaped the report, library
condition deletion was not checked, and interrupted BFS discarded its current
origin's observations. The implementation now rejects/discloses each condition
and retains partial evidence. These corrections change no frozen generated
snapshot or claim evidence. Review and tests are distinct evidence; another
agent reviewing the same code is not an independently developed checker.

Do not mark every control Passed just because one aggregated test command passes.
Do not infer independent verification from two agents checking the same authored
adapter. A fresh test must identify its own checker and input boundary.

## Contribution provenance

This specification map and its English explanations are project-original work
by dot (OpenAI), contributed under Unknown v0.3 and prepared for submission
through Mingli Yuan's authorized GitHub account proxy. The recorded local measurements precede
submission/publication, whose later status belongs to Git and PR records. Account use is not Mingli's technical review or a
correctness guarantee. No external text, code, dataset or fixture is imported.
