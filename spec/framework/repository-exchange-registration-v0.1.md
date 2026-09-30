# Three-repository collaboration, exchange and registration architecture contract v0.1

Date: 2026-09-30. Status: **reviewable local engineering draft**.
This is a technical architecture contract, not a legal agreement. English is
primary. Proposed specification home:
`mountain/adva-machine/spec/framework/repository-exchange-registration-v0.1.md`.
Formal adoption remains an explicit project decision.

Research direction: Mingli Yuan. English drafting and local repository
integration: dot (OpenAI), prepared for submission through Mingli Yuan's GitHub
account (`mountain`) as an authorized account proxy. The original local validation snapshot
preceded submission, publication and merge; later Git/PR records must establish
those actions separately. Account use is not Mingli's
technical review, endorsement, personal authorship or a correctness guarantee.
This is project-original documentation contributed under
[Unknown v0.3](../../Unknown-LICENSE-v0.3.md). No third-party text, figure,
dataset or software is incorporated.

## 1. Purpose and scope

This contract defines how `adva`, `adva-machine` and `adva-library` retain their
separate responsibilities, share material through bounded, reviewable exchanges,
and incrementally derive structural indexes and refactoring candidates from
existing registration sources. It gates near-term deterministic structural
comparison separately from future PyPI-like hosting and distributed
registration. Across every boundary, provenance, premises, guards, occurrences,
residuals and consumer version constraints remain traceable. Registration,
delivery, acceptance, interpretation, native admission and actual adoption are
not one undifferentiated success.

**GEN-01.** This is a v0.1 draft for review. `MUST` denotes an obligation proposed
to become mandatory upon adoption; `MUST NOT` denotes a prohibition; `SHOULD`
denotes a recommendation whose departure requires a recorded reason. Except
for facts explicitly labelled **existing**, the normative clauses below propose
obligations. They do not claim those obligations are already implemented,
merged or deployed.

**GEN-02.** This document uses three evidence labels: **existing** means code,
a specification or a historical record readable at a fixed commit;
**under review** means a proposal branch not yet merged at the recorded review
baseline; **proposed** means a required capability whose implementation has not
been established. Reading a historical success MUST NOT be reported as a fresh
successful execution. A source-code location MUST NOT automatically be treated
as maintenance ownership or semantic authority. [S1–S10]

**GEN-03.** This repository edition is an authorized **local engineering draft**
of the reviewed architecture text, integrated at the proposed specification home
with a navigation link and clause-coverage record. Its preparation starts from
the KPB-14 PR2 review snapshot below, rather than the frozen machine main
baseline. This is a documented change from the earlier editable-only delivery
scope, which made no repository edits. Any accompanying implementation and its
checks MUST be reported separately in the coverage record; adding this document
does not establish full implementation, formal adoption, merge or publication.
This drafting step does not publish a site, create an API, change consumer
locks, migrate material, execute an exchange or introduce an executable loader.
`adva-machine` remains the proposed maintenance repository; the final adoption
record, maintenance-path decision and actual reviewers remain to be recorded.

### Frozen reading and integration baseline

| Role | Fixed coordinate |
| --- | --- |
| `adva` reading view | `3287c61ab7d16253605b3d0cca818f5a698e258b` |
| `adva-machine` reading view / frozen main baseline | `acfc9806fe18a36d0f7194dcc196a380b2834adf` |
| `adva-library` reading view | `19cede9c4532b7abd85f200daf7a9611a84563f0` |
| KPB-14 PR2 review snapshot / local integration parent | `a0702dc99d5e12cc72af1936d82162fc5a8780b5` |

The local integration line is `work/architecture-contract-v01`, based on the
PR2 snapshot. PR2 is an explicit documentary-tooling dependency and was OPEN
at the reviewed baseline. Depending on its branch does not report it as merged
or replace any frozen source pin. A later integration must record the actual
PR2 disposition separately. [S9]

**GEN-04.** A “current view” means only the fixed commits inspected above. Older
consumers remain pinned to machine
`e62d88dcc83fc4967260866518029942b9631b71` and library
`73a6af4ac4ed8225366d3c16794e309cff15f51d`; this contract MUST NOT replace them
with current main. [S7–S8]

**GEN-05.** This draft supplements, and does not waive, existing receiving,
provenance, guard, Pascal-growth, publication and consumer-lock obligations.
Conflicts MUST remain visible until an explicit versioned successor decision;
no new clause may silently weaken an earlier contract.

## 2. Responsibility and object boundaries

**OWN-01.** The three repositories MUST divide work by maintained interfaces and
uses, and MUST NOT mechanically migrate content by file extension or inherited
directory. Physical storage creates no second normative authority. Historical
code may remain, but every current specification, material entry and checking
predicate MUST have a declared maintenance source. [S1–S2]

| Participant | Decides and maintains | Not automatically granted by that role |
| --- | --- | --- |
| `adva-machine` | Language, IR, kernel, profiles, checkers, toolchains and conformance tests | Universal truth of research conclusions; automatic admission of external material |
| `adva` | Questions, interpretations, methods, experiments, scoped conclusions and evidence | Rewriting machine acceptance rules; implicit consumer upgrades |
| `adva-library` | Current homes of materials and catalog entries; existing receiving and reuse conditions | General executable-package authority; an obligation for receivers to accept |
| Receiver | This disposition under an independently bound contract, context and budget | Acceptance on behalf of another receiver; proof of sender identity |
| Registration site | Admission, indexing and publication of registration records within its declared scope | Mathematical truth; bypassing checkers, material homes or consumer locks |
| Consumer | Intended use, version locks, migration acceptance and retirement timing | Treating catalog `latest` or registration status as an executable dependency |

**OWN-02.** The eventual physical split of `adva-library` remains Open. A material
may occur in several caches or receiving repositories. Copies MUST retain the
source home and MUST NOT declare it retired merely because delivery occurred.
A home change requires an explicit succession record and review of affected
consumers. [S1–S2]

**OBJ-01.** The following entities MUST be typed separately; their identifiers
MUST NOT substitute for one another:

- **Repository:** a source collection with a declared name and fixed commit
- **PackageSnapshot:** a bounded selection of files, declarations and dependencies
  for a declared use; neither an entire repository nor presumed executable
- **MaterialOccurrence:** an occurrence of a material in a particular origin,
  receipt, transformation or use; equal bytes do not mean the same occurrence
- **ReceiverContext:** the binding of receiving participant, store, profile,
  contract digest and use context
- **SiteSnapshot:** the registration view available from one bounded registration
  participant at a fixed time/version; not a global arbiter
- **Endpoint:** a specific protocol entry exposed by a participant; one repository
  may have multiple endpoints and one site may serve multiple repositories
- **CheckerProfile**, **EvidenceRun**, **ConsumerLock:** respectively, judgment
  rules, one finite run, and a particular consumer's adoption binding

**OBJ-02.** Repository, PackageSnapshot, ReceiverContext, SiteSnapshot and Endpoint
MUST use their own fields and coordinates. Neither “one repository, one site,”
“one site, one receiver,” nor “readable repository, available endpoint” may be
inferred. The present local-file receiving route does not establish a network
endpoint. [S3]

## 3. Provenance coordinates and typed relations

**REF-01.** Documentary objects MUST retain a `documentary_id` of the form
`repo@full_commit:path#selector`, and separately store `repository`, full
`commit`, `path`, `selector`, `source_sha256`, original `revision` when supplied
by the source, `home`, and unresolved fields. This is the KPB documentary
projection's locator format, not a new native identity. A missing original
revision MUST be recorded as missing and MUST NOT be guessed from a number,
path or `documentary_id`. [S9]

**REF-02.** A source digest establishes only integrity of the specified bytes.
The declared repository binding, obtained bytes, and identity/control
verification MUST be recorded separately. A hash, Git URL, author attribution,
registrant identity or signature MUST NOT alone replace technical correctness,
publication eligibility or receiving admission. [S3,S9]

**REF-03.** Every dependency reference MUST resolve to the exact original
declaration or to an explicit unresolved record. Without evidence, a same-name,
same-research-number or same-path object from another repository MUST NOT fill
the gap. Unavailable source and observed digest mismatch MUST be distinct: the
former is undecidable from available evidence; the latter refutes that binding.
Both block a new success claim for a use that requires that dependency.
Unresolved background references allowed by the contract may remain documentary
residuals; they are not satisfied premises.

### Relation types and inference permissions

| Edge type | What it expresses | What it does not establish |
| --- | --- | --- |
| `cites` | A documentary reference to a source | An execution dependency or valid derivation |
| `source-byte-depends-on` | Exact source bytes declared as a dependency | Discharged proof premises |
| `imports` / `executes-with` | A declared execution route uses a dependency or profile | Adoption by another consumer |
| `implements` / `checked-by` | An implementation correspondence or specified checking route | Passing conformance merely from association |
| `derives-from` | A derivation with scope, premises and evidence | Unconditional truth across profiles |
| `received-under` | An occurrence received under a contract | Semantic correctness or native executability |
| `structurally-matches` | Structural correspondence under frozen rules | Proof equivalence, substitutability or permission to import |
| `supersedes` / `adopted-by` | Declared succession or consumer adoption | Erasure of the predecessor and its evidence |

**EDGE-01.** Every edge MUST carry endpoint types, provenance coordinates,
asserting party, scope, status and basis. Derived edges additionally record
algorithm version and input digests. Structural similarity, equal bytes, equal
names and citations MUST NOT automatically become dependency, equivalence or
implementation edges. Unresolved dependencies remain gaps, not fabricated target
nodes.

**EDGE-02.** An impact graph MUST make direction explicit; this contract
recommends `dependency → consumer`. Potential-impact propagation follows only
source-bound dependency kinds and retains each hop's edge kind. Its result is
a set requiring review, and MUST NOT automatically pronounce downstream
conclusions false. Cycles and strongly connected components remain explicit;
exhausted traversal budget MUST NOT be reported as a complete closure. [S9]

**REF-04.** The fixed KPB-14 PR2 snapshot records 324 units and 348 dependencies:
346 have exact documentary bindings and two remain missing. This is an
**under-review** documentary-tooling result, not a merged registry or proof
graph. These historical figures were not newly executed by the source draft or
by translating this clause; any later reproduction must have its own record.
[S9]

## 4. Exchange and independent status dimensions

**EX-01.** A workflow within the exact existing profile MUST preferentially
reuse Rust `send`, `receive`, `acknowledge` and `exchange_routine`, and MUST NOT
represent an external copy as a checked receipt. The existing profile receives
one `logic` home, `proposed-document` entry, with at most eight files, retaining
references without execution. Work beyond that scope requires another versioned
contract and conformance; this does not mandate the same CLI forever. The
command remains `adva communicate`. V2 calls its documentary crossing
`transport`; seeking, testing and revising a common interpretation of
heterogeneous interfaces is separately `communicate`. [S3–S6,S12]

**EX-02.** Bound inputs MUST include an independently selected receiver/context,
expected contract digest, sources, file inventory, checker and build
dependencies, publication record, budget and explicit attempt plan. The existing
strict `Contract`, `Origin`, `Member`, `Checker`, `Payload` and `Envelope` types
and version constraints MUST be preserved. This contract's fields MUST NOT be
silently inserted into an old strict schema. New fields belong only in a
documentary projection or a reviewed successor schema. [S3,S11]

### Status is a vector

| Dimension | Recorded scope and example states | Evidence threshold |
| --- | --- | --- |
| Provenance | `Declared` / `Traced` / `Unavailable` / `Conflict` | Source chain and original coordinates; authentication recorded separately |
| Binding | `Unbound` / `Matched` / `Mismatch` / `Unknown` | Exact comparison of actual bytes, expected contract and receiver/context |
| Delivery | `NotObserved` / `Sent` / `Arrived` / `Unknown` | A specific local observation event |
| Documentary acceptance | `NotAccepted` / `AcceptedDocumentary` / `AlreadyAccepted` / `Rejected` / `Unknown` | The named receiver's checks and durable receipt |
| Reply observation | `NotObserved` / `Acknowledged` / `Unknown` | Checking an actually supplied receipt; not a live remote recheck |
| Interpretation | `NotRun` / `ScopedInterpretationChecked` / `Refused` / `Unknown` | A separately bound finite correspondence check |
| Native admission | `NotGranted` / `GrantedForProfile` / `Unknown` | Actual judgment by an applicable native checker |
| Registration | `Proposed` / `Listed` / `Withdrawn` / `Conflict` / `Unknown` | Site scope, criteria and version record |
| Adoption | `NotAdopted` / `Locked` / `Migrated` / `Retired` | A particular consumer's successor lock and migration evidence |

**STAT-01.** These are proposed common reporting dimensions, not modifications
to existing wire enums. Each value MUST be recorded with observer, input pins,
time/attempt, permitted use and residuals. A check not run cannot be filled as
passed; Unknown cannot be filled as failure or success. Success in one
dimension MUST NOT automatically advance another.

**EX-03.** Existing `receive` checks context, budget and integrity, then uses
lock, pending storage, file/directory synchronization and rename to complete
`AcceptedDocumentary`. An explicit repeated `receive` rechecks the existing
receipt, inventory and payload. Successful `AlreadyAccepted` MUST add zero
acceptance effects. `acknowledge` checks only the actually supplied receipt and
does not establish that current remote storage remains intact. [S3]

**EX-04.** Existing receipt values `semantic_verification=NotRun` and
`native_admission=NotGranted` MUST remain unchanged. Later interpretation checks
must be additional independent records. Lock occupancy, pending state, missing
reply, exhausted budget or a mismatched installed checker can produce `Unknown`;
traces MUST NOT be deleted, budgets silently replenished, or attempts
automatically retried. [S3,S5]

## 5. Registration, indexing and discovery

**REG-01.** The first phase MUST generate disposable projections from existing
sources. S9 actually uses `adva`'s `docs/claims.toml`,
`python/adva/math_catalog.py` and `crates/adva-lisp/src/operation.rs`;
`adva-machine`'s `spec/catalog.json` and framework vocabulary; and
`adva-library`'s `math/manifest.json` and `index.json`. Machine's forward
maintenance responsibility does not change that historical source location of
`OperationSpec`. The projection MUST NOT overwrite those sources or become a
second registry. [S2,S9]

**REG-02.** A proposed registration record MUST contain at least `record_id`,
`schema_version`, package coordinates, source pins, home, publisher's declared
identity, registering site, permitted uses, receiver/profile, dependencies and
unresolved items, publication/licensing status, checking-evidence references,
lifecycle, predecessor/successor and withdrawal reason. Unimplemented identity
verification, signatures or authentication MUST be disclosed; registration
MUST NOT imply authentication.

**REG-03.** Registration is a site's decision to accept a record within its
scope. An index is a query view generated from fixed registration sources.
Discovery is the location/protocol for finding candidates. The three MUST
remain separate: discoverability does not establish availability; availability
does not establish receipt; receipt does not establish adoption. Search rank,
download count and repetition across sites do not raise technical authority.

**REG-04.** A site MUST publish its bounded responsibility: covered namespaces,
sources and update boundary, per-read/traversal budget, supported schemas and
profiles, index time and incompleteness. Queries MUST return the view version,
evidence sources and Unknown/staleness information. They MUST NOT claim
network-wide completeness, global uniqueness or universal synchronization.

**REG-05.** New registration MUST NOT overwrite old content at an immutable
coordinate. Equal coordinates with unequal digests require a retained conflict
and block new acceptance; equal names at different commits are different
versions. Withdrawal MUST retain its reason, visible history and affected
consumer set. Historical accepted records MUST NOT be rewritten as never
having happened.

**REG-06.** Future distributed synchronization between sites MUST define node
identity, authentication and authorization, replay protection, conflict rules,
withdrawal propagation and disconnection semantics. Without those protocols,
only documentary exchange of fixed snapshots is permitted; automatic federation
or an arbitrarily reachable inter-site network MUST NOT be claimed.

**REG-07.** A PyPI-like hosting experience is a future goal, not this phase's
installation interface. This contract supplies no upload API, remote backend,
package executor, automatic dependency resolver/installer or general loader.
Even future managed registration can publish only candidates and scoped
receiving results; a site cannot select consumer versions or add kernel rules.

### Near-term deliverables

**REG-08.** Near-term outputs SHOULD be a source manifest, typed dependency view,
unresolved inventory and read-only structural-candidate report over fixed
three-repository inputs. Each derived report MUST record generator commit, rule
version, source digests, resource limits and actual expenditure. A lost report
is reconstructible; it holds neither the sole material copy nor authority above
the source registrations.

## 6. Deterministic algebraic comparison and structural matching

**MINE-01.** Reproducible symbolic and structural comparison is the implementation
priority. Inputs MUST be pinned declarations, expressions or graphs with their
occurrences, types, edge direction, premises, guards, residuals and profile.
An extractor MUST NOT fill semantics from similar filenames; unextractable
fields MUST produce explicit gaps.

**MINE-02.** Each comparison MUST freeze extraction schema, allowed equivalence
relations, rule list, normalization algorithm, stable sorting/serialization,
deterministic step budget and stopping conditions. Equal inputs, rules and
step boundaries MUST produce equal candidates and grounds; heuristic ordering
must be replayable. A separate wall-clock safety cutoff may produce different
partial results. Those MUST be labelled `Unknown`/`Partial` with the stopping
position retained, without claims of candidate-set completeness or full identity.

### Permitted comparison levels

| Level | Comparison | Strongest reportable conclusion |
| --- | --- | --- |
| L0 bytes | Exact bytes and digest recheck | `ByteIdentical`, byte equality only |
| L1 syntax | Specified syntax tree; capture-avoiding renaming of bound variables | `SameSyntaxUnderRules`, with a mapping |
| L2 typed structure | Graph matching retaining types, direction, multiplicity, edge labels and occurrences | `StructuralMatchCandidate`, with witness mapping and unmatched boundary |
| L3 finite semantic correspondence | An independently frozen checker over a given domain, premises and budget | `ScopedCorrespondenceChecked`, only for the stated scope |

**MINE-03.** Algebraic simplification may use only identity rules explicitly
allowed by the selected profile. Commutation, association, cancellation,
copying, discarding or normalization of a ratio to one MUST NOT be assumed.
Relevant types, guards, zero values and linear/occurrence semantics MUST be
checked before application. An inapplicable rule leaves the original structure;
unknown applicability is not an identity.

**MINE-04.** Structural matching MUST declare whether its relation is
isomorphism, embedding, partial matching or another scoped relation, and output
the corresponding node/edge mappings, occurrence mapping, boundary interfaces,
preserved and lost conditions, unmatched portions and counterexamples when
available. Only an asserted isomorphism requires bijections. Equal final values,
names or local degrees cannot identify the same process. Matching failure
negates only matching within these rules and scope. Exhaustion returns `Unknown`,
not “no match exists.”

**MINE-05.** A candidate record MUST give both complete input coordinates,
algorithm version, matching level, permitted transformations, evidence digest,
premise/guard differences, potentially affected consumers and suggested next
check. It can recommend a common presentation, adapter or new package only.
It MUST NOT automatically modify sources, checkers, acceptance rules, proof
edges, material homes or consumer locks.

**MINE-06.** Existing structure cards check documentary shape such as `objects`,
`relations`, `preserve`, `open_questions` and `request`; they are not mathematical
graph importers. KPB `refactor_candidates` groups metadata interface shapes and
makes no actual structural-equivalence judgment. A new comparator MUST reuse
the preservation obligations and binding facilities, but supply a separately
verifiable version and finite tests; old results MUST NOT simply be renamed
L2 or L3. [S6,S9]

## 7. Bounded verification and responsibility at cuts

**VERIFY-01.** Every successful judgment MUST identify its object, permitted use,
premises, checker/profile and build dependencies, explicit inputs and applicable
domain, evidence, finite checking budget, resource account and residuals.
A finite procedure may check a quantified proposition, but success MUST NOT
expand beyond the checked judgment's domain, premises or use. Producers, search
methods and registration sites cannot change the acceptance predicate themselves.
[S2]

**VERIFY-02.** First verification, cache-hit checking and reuse verification MUST
be charged and recorded separately. Cache keys MUST bind judgment, premises,
profile, checker/build dependencies, evidence and interpretation. Obligations
on fresh inputs, guards or occurrences remain. Caching a success boolean alone
does not authorize reuse.

**CUT-01.** Splitting a large package into subpackages or a large proof/process
into fragments MUST retain all cross-boundary obligations. Each cut MUST declare
entry/exit interfaces, exact dependencies, premises, guards, occurrence
correspondence, spent resources, remaining obligations and composition conditions
still to check. Partitioning reorganizes checking; it does not eliminate its
responsibility.

**CUT-02.** A proposed cut record minimally has `cut_id`, parent judgment/input
pins, subgraph pins, boundary map, trusted rules, premise/guard bindings,
occurrence map, cost spent/reserved, residuals, checker/profile and continuation
policy. Missing fields prohibit a claim of closure or completion. This field
list does not establish a general cut-certificate checker.

**CUT-03.** Composing checked fragments MUST recheck boundary agreement,
instance freshness, premise compatibility, transmission of residual obligations
and the total budget account. Local successes cannot conceal disconnected
composition, cancelling but disconnected factors, concrete zero guards,
collapsed copy instances or lost history.

**VERIFY-03.** The first executable reuse pilot MUST supply an independently
versioned profile, checker and positive/negative examples, and compare full
replay with the supported cut/cache route for judgments, residuals and total
cost. This contract MUST NOT relax the existing research loader's maximum
four-epoch ancestry. A general loader and general cut checker remain unavailable.
[S2]

**VERIFY-04.** Budgets MUST be declared before execution and cover at least bytes,
nodes/edges, depth, invocation count, time and evidence storage. Record which
limits are cooperative and which are enforced by the execution environment;
a cooperative deadline MUST NOT be described as an adversarial-input sandbox.
On stopping, preserve expenditure and available partial evidence. An explicit
continuation MUST have a successor binding and MUST NOT reset the old account.

**VERIFY-05.** A receiver may use its own replay/check, an applicable compatible
local cache, an implemented applicable boundary-proof checker, or an external
result explicitly retained as a named premise. Each route MUST state trust and
residuals. Complete cut fields, a copied `Verified`, hashes or signatures cannot
transfer another observer's checked status. Missing history MUST NOT silently
become an axiom.

**VERIFY-06.** PR205's finite effect witness may inform research on retained
effect observations. It MUST NOT be interpreted as retry permission, authority
to mutate state or native admission. When completion is unknown, observations
are limited to an authorized, budgeted checking plan. Any write or new attempt
requires an independent explicit basis. [S10]

## 8. Consumer locks and change governance

**LOCK-01.** Consumers MUST pin actually used source commits, material digests,
machine and library versions, checker/profile, inputs and applicable evidence.
Documentary reading pins and executable consumer pins MUST remain separate.
Reading a latest registry or index MUST NOT update locks, download/execute new
dependencies or replace historical evidence. [S1,S7–S8]

**LOCK-02.** An upgrade MUST create a reviewed successor lock identifying its
predecessor, rationale, affected scope, receiving contract, rerun scope,
positive/negative examples and rollback/retention route. Retain predecessor
locks and historical bundles. A digest mismatch is a failed gate; weakening
fingerprints, changing old witnesses or falling back to an inherited local
implementation MUST NOT “repair” it.

**LOCK-03.** Before retiring old code, a path or material, enumerate live
consumers individually. Each MUST have an accepted replacement route and
replayable evidence. One consumer's successful migration does not authorize
another's. Without exhaustive dependency coverage, mark the inventory incomplete
and do not declare the old path safe to delete.

**CHANGE-01.** Proposal, merge, documentary adoption, execution verification,
native admission, consumer adoption, public release and source retirement MUST
be recorded separately. Account-proxy submission, attribution, review and merge
do not replace technical checks. This document presumes neither anyone's
technical endorsement nor any new legal commitment.

**CHANGE-02.** Substantive changes MUST have a new version and predecessor/scope
mapping. Errata MUST identify affected clauses, original revision and evidence
impact; historical runs MUST NOT silently be said to have used later
corrections. Existing publication and licensing rules remain applicable.
Licensing compliance, software-dependency licenses and semantic acceptance MUST
NOT be collapsed into one status.

### Current blockers and ownership

| Unresolved item | Responsible source | Permitted next step |
| --- | --- | --- |
| Exact declaration of `adva.bounded-experiment.leak-wall.v0` not located | `adva` original claims registry | Check/correct the original reference or add an evidenced versioned declaration; do not assume identity with `dual-facility-leak-wall` |
| Exact declaration of `adva.exact.structural-forward-differential.v1` not located | `adva` original claims registry | Record absence or revise the source; do not substitute a similar research number |
| Historical library monorepo paths and broader dependency/custody obligations | Each original home and consumer | Add pinned origin mappings individually without changing old evidence |
| Remote identity, node conflict and discovery protocols | Protocol maintainer still to be designated | Design a bounded pilot; do not claim an existing network federation |

The two absent exact dependencies are observations of the PR2 snapshot, not
proof of absence across all remote, private or unfetched history. [S9]

## 9. Iota end-to-end comparison

**CASE-01.** This case uses historical records of the same package in distinct
receiving contexts to show why statuses cannot be collapsed. Its source is
`adva-iota@602d5239011a3a463e72ce8db98e5f0da5c84690:exchange_v1/catalog.json`.
The package has eight files, 81,651 bytes, and SHA-256
`58aad08d14563201e8adb632db0a61d23016851878f103ba002da9aebba7e772`.
The complete source development repository is not public; only public received
material and records are referenced here. [S4]

| Step | Existing record | Additional proposed obligation |
| --- | --- | --- |
| 1. Selection and binding | Same eight-file package separately sent to `adva` and machine, with distinct contracts/contexts | Index one PackageSnapshot separately from two ReceiverContexts, retaining each occurrence |
| 2. Transport | Rust send, receive, replay and ack; knowledge-side sequence `Sent → AcceptedDocumentary → AlreadyAccepted → Acknowledged` | Show independent status dimensions, not a single “published successfully” |
| 3. Idempotence observation | One effect on first acceptance, zero additional effects on replay | Candidates/registration cannot create a second acceptance or forge a receipt |
| 4. Finite interpretation | Knowledge-side `ScopedInterpretationChecked`, 1,490 assertions; 159 cuts reconstructed, 92 local contractions, 519 schedules computed | Expose only that finite scope; do not extend it to all paths or a full ancestral proof |
| 5. Native observation | Identity, discard and copy probes actually executed and replayed; 8,989 instructions plus an equal replay count | Identify object-language programs and the fixed machine; add no native Iota identity rule |
| 6. Post-receipt registration | Existing exchange and received records | Derive read-only registration projections/structural candidates while retaining source home, old locks and original receipts |
| 7. Consumer adoption | No whole-repository merge or global dependency upgrade occurred | A new reuse route needs a separate successor lock and its specified gate |

**CASE-02.** Receipts remain `semantic_verification=NotRun` and
`native_admission=NotGranted`. Later finite interpretation MUST NOT rewrite these
historical values. All adapters were authored by the same agent; repeated
execution across contexts does not constitute independent human consensus or
independently developed verifiers. [S4]

**CASE-03.** This case does not establish full Iota-language equivalence or a
general heterogeneous communication implementation. Unknown, a missing
correspondence or exhausted reserve in a fixed comparison MUST NOT advance the
interpretation checkpoint. The existing `library → adva` documentary route has
different sources, contracts and uses; Iota success cannot exempt it from its
own checks. [S1,S4]

**CASE-04.** Proposed structural mining can extract L1/L2 correspondences from the
two pinned received records, compare occurrences, cuts, discard/copy and boundary
conditions, and output candidates. A possible shared presentation or adapter
produces only a change proposal. Forming a common package, execution and adoption
by each consumer still require the individual checks in sections 7–8.

## 10. Required counterexamples and acceptance controls

**TEST-01.** The following are acceptance cases a future implementation MUST
supply, not tests this specification claims to have run. Each MUST retain inputs,
pinned checker/profile, budget, observations and output evidence. Rejection is
of a specific contract; unavailability or exhaustion retains Unknown rather
than becoming success or proof of impossibility.

| ID | Injected condition | Required observation |
| --- | --- | --- |
| N01 | Commit/path and digest disagree | Reject that binding; no `latest` or same-name local substitute |
| N02 | Required source unavailable or dependency missing | Unknown/unresolved; block a new success that depends on it |
| N03 | Same-name cross-repository objects or exports under different profiles | Preserve distinct coordinates; no automatic identification or import |
| N04 | Premise, guard, residual or occurrence removed | Refuse unconditional success; retain gap and affected scope |
| N05 | Receipt/ack/Listed impersonates semantic or native admission | No dimension promotion; original records remain NotRun/NotGranted |
| N06 | Exact same package replayed under the same contract | AlreadyAccepted after successful recheck; zero new acceptance effects |
| N07 | Receipt, payload or inventory altered in an existing slot | Conflict or rejection; no overwrite to recover apparent success |
| N08 | Lock/pending, missing reply, exhausted budget or unknown effect | Unknown; no trace deletion, silent budget refill or automatic retry |
| N09 | Site claims verification without applicable checker evidence | Registration assertion may be retained; it cannot establish verification success |
| N10 | Current catalog entry differs from a consumer's historical pin | Consumer retains its historical lock; upgrade requires a successor gate |
| N11 | Fragments individually pass but composition is disconnected or has a zero guard | Composition fails/is refused; local success cannot close the cut |
| N12 | Bytes/structure look similar but histories or copy/discard differ | At most a candidate at the applicable level; no theorem/equivalence edge |
| N13 | Node, edge or time budget exhausted during comparison | Unknown plus partial search record; no complete no-match report |
| N14 | Method tries to rewrite its checker or acceptance rules | Block self-granted admission; rule changes require separate versioned review |
| N15 | New registration silently replaces source home or breaks provenance | Explicit conflict; block new adoption and retain original home/history |
| N16 | General loader/cut checker/network-wide sync falsely claimed | Capability-claim acceptance fails; return to the actual finite boundary |
| N17 | Result unknown after rename, or required durable-record writing fails | Retain observations and Unknown; neither fabricate completion nor assert zero effects |
| N18 | Input, premise, checker or occurrence changed after a cache hit | Recheck applicability/fresh guards and instances; otherwise reject or Unknown |
| N19 | Cyclic executable import unsupported by its profile | Preserve documentary cycle without execution; graph reachability grants no import |
| N20 | Unformed child or malformed boundary enters composition | Reject before composition; valid fragments cannot vouch for a malformed child |

**TEST-02.** This matrix supplements rather than replaces existing profile
conformance and KPB B01–B12. Tests MUST also retain valid controls: success with
exact pinned sources, complete conditions, applicable receiver and budget; and
distinct outcomes for schema/type checking, structural matching and finite
semantic correspondence. Testing rejection alone is insufficient. Documentary
metadata negatives MUST NOT masquerade as native executable conformance. [S2,S9]

## 11. Staged gates and review decisions

**GATE-01.** G0–G5 are this draft's route identifiers; they do not renumber
KPB-14. Its steps 1/2 correspond to G1 documentary work, step 3 to G3, and step 4
to G4. G2 structural comparison and G5 hosting are added tracks; G2 is not a
mandatory prerequisite for all existing bounded executable research. Every gate
MUST have a maintainer, fixed inputs, reproduction steps, artifact digests,
failure boundary and residuals. Passing establishes only its stated conclusion
and does not automatically open other capabilities.

| Gate | Scope and exit conditions | Explicitly excluded |
| --- | --- | --- |
| G0 contract review | Decide maintenance home, entity/status vocabulary, responsibility matrix and unresolved issues; retain version | Repository-edit authorization or certification of technical conclusions |
| G1 pinned registration projection | Reuse existing registries; reconstruct exact bindings, gaps and impact graph; satisfy N01–N05, N09–N10, N15 | New independent registry or automatic dependency import |
| G2 deterministic comparison | One finite expression/graph domain; frozen rules, mapping witnesses, guard/occurrence controls; satisfy N03–N04, N12–N14 | Automatic refactoring or universal semantic equivalence |
| G3 receiving and one executable route | Reuse transport; new profile/checker for selected reuse/cut; positive/negative cases, total cost and budget evidence | General loader or ancestry-limit exemptions |
| G4 one-consumer adoption | Successor lock and positive/negative cases pass; old evidence replayable; migration impact visible | Other consumer upgrades or automatic source retirement |
| G5 hosting/distributed pilot | Separately approve identity/authorization, remote backend, discovery, conflict/withdrawal protocols; bounded multi-node failure tests | Network-wide consistency or arbitrary all-to-all reachability guarantees |

**GATE-02.** G1–G2 are the near-term priority and may proceed in parallel through
explicit interfaces. KPB-14 PR2 is a candidate starting point for G1, but its
OPEN review-baseline status and known gaps MUST remain visible. It does not
complete all of G1 or authorize G3. G2 MUST add actual structural rules and
witnesses; reusing the name `refactor_candidates` does not create that capability.

### Decisions still requiring explicit resolution

**DEC-01.** Decide whether to adopt this responsibility boundary and status
vector, and establish `adva-machine` as normative maintenance home. The file
path above is the local proposal; a final path decision and adoption record
remain required.

**DEC-02.** Select the first finite G2 domain and budget. The proposed starting
choices are occurrence/cut structure from the public Iota package or an existing
witness interface, not all algebraic and proof domains at once. The choice MUST
retain independently reviewable positive, near-match and negative examples.

**DEC-03.** Assign responsibility for reviewing structural candidates and
correcting provenance, and decide how to address `adva`'s two absent exact
dependencies. Until then, retain the gaps without manufacturing substitute
declarations.

**DEC-04.** The future hosting protocol maintainer, registration criteria and
trust model remain undecided. This does not block read-only G1/G2, nor may an
implicit “trusted site” premise bypass it.

Version record: v0.1 is the present review draft. Existing source records are
the evidence baseline. After adoption, every substantive change requires a
successor version under CHANGE-02.

## 12. Fixed sources and review boundary

The references below fix full commits for reviewing clauses and existing
capabilities. S1–S8 and S11 refer to the frozen reading baseline or historical
records referenced there; S9 is the PR2 review snapshot; S10 is the finite
effect-witness source snapshot; S12 is the existing v2 vocabulary boundary.
Drafting and source inspection do not execute the repositories' tests or replay
historical runs. New local implementation results, if any, belong in the
[clause coverage record](../../docs/kpb/architecture-contract-coverage.md) with
an explicit distinction from these historical observations.

- [S1: `adva` three-repository maintenance and consumer continuity](https://github.com/mountain/adva/blob/3287c61ab7d16253605b3d0cca818f5a698e258b/docs/KNOWLEDGE_MACHINE_BOUNDARY.md)
- [S2: machine kernel/package boundary v0.1](https://github.com/mountain/adva-machine/blob/acfc9806fe18a36d0f7194dcc196a380b2834adf/spec/framework/kernel-package-boundary-v0.1.md)
- [S3: documentary exchange v1 strict types, receiving steps and resource boundary](https://github.com/mountain/adva-machine/blob/acfc9806fe18a36d0f7194dcc196a380b2834adf/spec/framework/documentary-exchange-v1.md)
- [S4: historical Iota knowledge-side receipt and finite interpretation](https://github.com/mountain/adva/blob/3287c61ab7d16253605b3d0cca818f5a698e258b/knowledge/exchanges/iota-process-knowledge-2026-09-17-v1/README.md)
- [S5: exchange routine finite four-step supervision plan](https://github.com/mountain/adva-machine/blob/acfc9806fe18a36d0f7194dcc196a380b2834adf/exchange_routine/run.py)
- [S6: structure-card shape checks and difference reports](https://github.com/mountain/adva-machine/blob/acfc9806fe18a36d0f7194dcc196a380b2834adf/exchange_routine/structure.py)
- [S7: `adva` machine/library consumer lock](https://github.com/mountain/adva/blob/3287c61ab7d16253605b3d0cca818f5a698e258b/dependencies/adva-machine.lock.json)
- [S8: machine's retained library lock](https://github.com/mountain/adva-machine/blob/acfc9806fe18a36d0f7194dcc196a380b2834adf/toolchain/library.lock.json)
- [S9: KPB-14 PR2 documentary projection and two unresolved dependencies](https://github.com/mountain/adva-machine/blob/a0702dc99d5e12cc72af1936d82162fc5a8780b5/docs/kpb/README.md)
- [S10: PR205 finite pending-effect-witness receiver](https://github.com/mountain/adva/blob/28d39804308cbe5d96b1c1fe24c7dcd3c99cbc2a/experiments/pending_effect_witness/receiver.py)
- [S11: Rust documentary exchange implementation types and receiving logic](https://github.com/mountain/adva-machine/blob/acfc9806fe18a36d0f7194dcc196a380b2834adf/crates/adva-witness/src/bin/support/communication_cli.rs)
- [S12: transport/communicate v2 vocabulary boundary](https://github.com/mountain/adva-machine/blob/acfc9806fe18a36d0f7194dcc196a380b2834adf/spec/framework/transport-communication-v2.md)

A full commit fixes a source version; source-content SHA-256 remains a required
field of future reconstructible reports and is not replaced by link text.
Maintenance responsibility, historical execution pins and consumer locks do
not substitute for one another. On adoption, proposed fields, types, gates and
controls must be mapped to actual implementations and tests; unmapped items
remain unimplemented.

### Translation and local-integration provenance

The reviewed project-original Chinese source is `contract-review.md`, dated
2026-09-30, with SHA-256
`7481896c4623fcc1eca88804bf986dca60d480521170cbef879831eed9989158`.
This English-first repository edition preserves its 60 clause identifiers,
N01–N20 controls, G0–G5 gates, frozen source coordinates and open decisions.
The source is not copied into this repository as a second specification home.

The deliberate delivery-scope adjustment is GEN-03: the earlier draft's
“no repository modification” statement now records the separately authorized
local integration. Related front matter, PR2 dependency disclosure, DEC-01 path
clarification and this traceability record distinguish a proposed path from
formal adoption. They do not grant remote publication, advance locks or promote
historical results. No adoption, release or executed exchange is inferred from
this translation or its local presence.
