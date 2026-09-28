# Kernel and package boundary contract v0.1

Date: 2026-09-28. Canonical home: `mountain/adva-machine`.

Status: **project engineering and documentation contract for future changes**.
The requirements below govern design and review; they do not assert that a
general package loader, independently checkable cut certificate, or compressed
verification system is implemented. Existing executable profiles keep their
own contracts. This document introduces no opcode, native type, admission,
mathematical theorem, or dependency upgrade.

Research direction: Mingli Yuan. Drafting and source review: ChatGPT (OpenAI),
submitted through Mingli Yuan's GitHub account as an authorized proxy. Account
use is not his technical review, endorsement, or a correctness guarantee.
This is project-original documentation contributed under Unknown v0.3.
The [Chinese companion](kernel-package-boundary-v0.1.zh-CN.md) is a supporting
explanation; this English document is primary. Clause identifiers are local
to this contract and its version, not native semantic identities.

## 1. Purpose and governing boundary

**A finite observer must be able to state what it checked, under which rules,
what it still assumes, and what resources further checking requires.**

Knowledge and verification histories may grow beyond any one observer's
storage or time budget. Partitioning must therefore preserve obligations at
the boundary without requiring every consumer to retain the entire history.
Small trusted code, bounded memory, bounded verification time, and broad
expressive power are separate objectives; none supplies the others for free.

**KPB-01 — Local responsibility.** Each invocation must fix its kernel/profile,
inputs, interpretation, accepted premises and finite resource account before
execution. It must expose unresolved premises and residuals in its result.
No observer is required or claimed to decide every arithmetic question within
a fixed budget. Splitting a proof can reduce memory without reducing total
first-verification work.

**KPB-02 — Existing obligations survive.** This contract adds prospective
coordination rules. It does not rewrite frozen research, source/occurrence
identity, runtime guards, publication policy, the Pascal-rooted growth
obligation, historical receiving contracts, or dependency locks. A conflict
requires an explicit successor decision; this document cannot silently waive
the earlier obligation. An unsatisfied new requirement is a disclosed gap,
not a reason to relabel historical evidence as if the requirement had run.

## 2. Responsibilities, not a premature universal vocabulary

Here *kernel* means the rules and implementation relied on to admit a judgment
in a specified profile. The trusted computing base also includes the relevant
parser/decoder, arithmetic implementation, configuration, and execution platform;
calling the rule set small does not remove those dependencies. The current
native authority remains the applicable Rust checking boundary.

| Responsibility | Must remain explicit | May grow outside the checking kernel |
| --- | --- | --- |
| Arithmetic witness checking | Formation, transport, well-formedness, guards, composition and permitted conclusions | Producers of expressions, candidate transformations and witness material |
| Process and learning protocol | Valid state transitions, retained obligations, input/output binding and resource accounting | Search order, candidate generation, exploration and domain-specific methods |
| Vocabulary and presentation | Versioned expansion/interpretation and applicable observation interface | Names, aliases, cultural conventions and derived notation |
| Domain packages | Required premises, exports, effects, evidence and receiving scope | Mathematical constructions, empirical observations and research programmes |

**KPB-03 — Meaning is scoped.** A name is an entry point into a representation
and interpretation contract, not a completed universal concept. A local ID,
filename or digest must not allocate native identity. Renaming, splitting,
specialization, conditional equivalence and unification must be recorded as
different changes. A correspondence must say what it preserves, forgets, or
leaves unresolved. Competing interpretations may coexist. Equivalence requires
its own applicable evidence; adoption or popularity cannot establish it.

The basic learning vocabulary is deliberately not declared complete here.
Existing research interfaces use `compute/verify/learn` as mechanism labels
and `subject/method/object` to `history/result/evidence` as process positions
[S2]. Whether any additional word is primitive must be decided by its required
checking responsibility, not by frequency of use or a proposed name.

## 3. Arithmetic invariants and the present kernel candidate

The six-word research witness implementation is the initial candidate to audit,
not a replacement for stable PSC0 [S1, S2]. In its declared profile:

- `A(P) = actual_boundary(P) - declared_boundary(P)`. Additive zero is formation
  success. Each child must satisfy formation before composition; opposite
  defects cannot cancel into an admitted parent.
- `M(P) = poly(after) / poly(before)` describes the profile's exact transport
  residual. Multiplicative unity is distinct from the program's output value.
  Ordered syntax, sources, occurrences, endpoints and history remain relevant.
- Symbolic closure does not discharge concrete nonzero obligations. Every
  retained guard must be checked in the actual input environment; an
  intermediate `ZeroFault` cannot be repaired by a later scalar cancellation.
- Reuse of a checked template does not merge its fresh instances or occurrence
  bindings. A cache coordinate is not a program identity.

**KPB-04 — No weakened composition.** Every package claiming this witness
profile must preserve these conditions, including endpoint correspondence.
`A=0` and `M=1` are not universal substitutes for all typing, interpretation,
observation, or proof obligations. A different arithmetic domain, guard policy,
equivalence relation, or composition rule requires a separately versioned
profile and its evidence. Exhaustion or arithmetic capacity limits are not
permission to switch to approximation or weaken equality silently.

Current witness nodes are `Seed`, `ArithmeticTransition`, `Instantiate`,
`Compose`, and `Seal` [S1]. This inventory identifies an existing implementation;
it is not a proof that these nodes form the final minimal kernel.

## 4. Learning without self-granted admission

**KPB-05 — Separate proposing from accepting.** A learning method may propose
names, hypotheses, strategies, constructions, counterexamples and kernel
changes. Its result can become usable only through the already selected
receiving/checking contract. The method must not replace its checker, alter
its acceptance predicate, erase a failed guard, reset fuel, or turn an open
obligation into a closed one within the run.

A derived word that expands into already admitted expressions may be packaged
with its expansion and checked under the existing profile. A new primitive or
a new meaning of equality/admission is a kernel/profile proposal. A bounded
learning transition may be valid while its hypothesis remains `Proposed`.
Interpretation changes must preserve the original question and explain which
observations or claims no longer transfer.

## 5. Package contract: a finite boundary with visible premises

A package is a unit with one maintenance home and a declared interface. It
may contain documentary knowledge, candidate-producing methods, executable
content, or evidence. These kinds have different admission routes. In this
contract a documentary description is not an installed package format.

**KPB-06 — Required package description.** A new executable/evidence package
proposal must supply the following fields. An existing format may supply them
through a documented mapping; no duplicate registry is required.

| Field | Required content |
| --- | --- |
| Identity and origin | Owning repository/namespace, package revision, exact payload references, authorship and publication basis |
| Required checker | Kernel/profile version, checker source and applicable build/dependency bindings; any extra trusted rules |
| Interface and interpretation | Inputs, outputs, types/domains, units, observation policy, retained guards and allowed effects/capabilities; state their enforcement boundary |
| Premises and dependencies | Each imported premise and its exact source; distinguish executable imports, proof premises, observations and documentary citations |
| Exports | Scoped conclusions or operations, relevant claim IDs, undischarged premises and what use their evidence permits; no implicit widening of domain or conclusion |
| Evidence | Proof/certificate or replay material, receiver procedure and the route actually available |
| Resource contract | Input/expansion size, time, memory, depth/fan-out and checking/continuation budgets as applicable; enforcement or an explicit enforcement gap |
| Residual and lifecycle | Open questions, failed controls, conditions for reuse, withdrawal/supersession and evidence availability/custody |

The intended interface can be written as `Gamma_P |-_{K_v} J_P`: under fixed
premises `Gamma_P`, kernel/profile `K_v` checks the stated judgment `J_P`.
This is contract notation, not a newly installed Adva proof calculus.

**KPB-07 — Composition retains premises.** A consumer may reuse only the exact
exported judgment whose domain, interpretation, guards and effects match its
request. Undischarged premises survive composition. Replacing a premise with a
checked upstream conclusion requires an applicable substitution/transport rule
and evidence, not merely matching names. Imports from distinct profiles do not
automatically share semantics. A translation must record coverage, preserved
observations and losses. Ordinary documentary links create no derivation edge.

An external verifier may produce candidate evidence for an existing checker.
If its verdict is trusted without that check, the verifier and its assumptions
join the declared trust boundary. Installing a plugin must not disguise this
as an ordinary derived package. Unsupported capability requests are refused.

## 6. Verification cuts, caches and retention

**KPB-08 — A cut transfers no invisible responsibility.** At each proposed cut,
record the upstream export, exact boundary, downstream use, retained premises,
evidence location and receiver's acceptance route. A cut record without a
working applicable receiving route remains a proposal. Missing history must
not silently become an axiom or a successful check.

| Receiving route | What the receiver can report | Remaining responsibility |
| --- | --- | --- |
| Local replay or proof checking | The specified material was checked under the recorded rules and budget | Declared premises, checker/platform assumptions and original observation provenance |
| Reuse of a local checked cache | A matching earlier local judgment was reused under an unchanged compatible context | Cache integrity/custody and the original judgment's assumptions |
| Independent boundary/combined proof | The supplied boundary proof was checked by an implemented applicable checker | That proof system's rules, assumptions, translation and cost; this general route is not supplied here |
| External result used as a premise | A conditional local conclusion relying on a named external result | The external assertion/checker remains an explicit premise or trust dependency |

A cache key must bind the exact judgment, premises, profile, checker/version,
applicable build dependencies, evidence and interpretation. Guards and input
bindings that depend on a fresh instance must still be checked. A portable
`Verified` flag, hash, signature or membership proof does not establish semantic
correctness. Cross-observer cache reuse needs an explicit receiving contract;
it cannot inherit another observer's local checked status by file copying.

**KPB-09 — Availability and invalidation.** Hot working memory may evict old
proof bodies after an allowed receiving route is satisfied. Eviction does not
authorize deleting frozen archives or obligations. Retain a bounded working
frontier and retrievable provenance, or disclose that revalidation is unavailable.
A reference is not a promise that its bytes will remain available forever.
Custody, integrity, semantic validity and current applicability are separate.

Changes to a required premise, interpretation, checker or dependency invalidate
unqualified current reuse until rechecking or a supported compatibility result.
Such a compatibility result must bind both old and new profiles/checkers,
the exact affected judgments and premises, and the permitted migration scope.
An already selected receiving rule must check it; a package cannot grant
compatibility to its own changed checker merely by declaring it compatible.
Retain the historical result under its original conditions. Corrections trigger
an impact review through actual dependency edges, not every bibliographic link.
Impacted results are marked for review; they are not automatically all false.

No bounded-cost verification of arbitrary growing histories is promised.
Proof compression is a separate implementation/research task; any added logical
or cryptographic assumptions must be visible in its profile.

## 7. Outcomes and finite continuation

**KPB-10 — Keep outcomes distinct.** The following are reporting distinctions,
not new CLI status strings. Each existing profile retains its own vocabulary
and must document any mapping.

| Outcome | Meaning |
| --- | --- |
| Locally checked | A particular judgment was checked; list all remaining premises and its scope |
| Conditional use | The use relies on named premises not discharged by this receiver; not an unconditional local proof |
| Rejected material/request | Malformed proof, failed guard, incompatible profile or unsupported permission; does not by itself refute the proposition |
| Checked counterexample | Applicable evidence refutes the precise scoped claim |
| Unknown / incomplete / unavailable | Budget exhausted, required evidence missing, or applicable checking unavailable; retain reason and progress |

Parsing, dependency resolution, decompression, normalization, proof checking,
replay and required record writing must be accounted for. Setup excluded from
a run must be measured/reported separately. A declared but unenforced limit
must not be reported as enforced. Cyclic dependencies require a dedicated
well-founded/recursive rule; otherwise refuse that import cycle.

Continuation must bind the same question, inputs, profile, checked prefix,
remaining obligations and spent resources. Renewed allowance is an explicit
new finite contract, not a hidden restart. A mutable checkpoint or remote
receipt is not enough to resume a trusted judgment. Global anti-fork resource
accounting and crash recovery require their own mechanisms; local fuel does
not establish them.

An executable profile must distinguish exhaustion modes that can produce a
valid continuation record from termination modes that leave no resumable state.
Abrupt termination or missing output is never acceptance; recovery must
re-establish the last trusted boundary before continuing.

## 8. Namespaces and research sequences

**KPB-11 — Qualify every cross-repository reference.** A research number is
local to its repository's sequence. Human discussion must name the repository;
document links must identify the repository and full path; evidence dependencies
must also fix an immutable commit (and payload digest when their format requires
one). A moving branch may be a clearly labelled navigation link only.

The collision is concrete:

| Repository | Local 0207 |
| --- | --- |
| `mountain/adva` | [constructive-starvation-and-budget-matched-control][S8] |
| `mountain/adva-machine` | [renaming-the-iota-combinator-spelling-on-the-accepted-package][S9] |

Never resolve an absent cross-repository reference to a local file with the
same number. Shared filenames do not prove equal bytes, equal current meaning,
or mutual admission. Keep historical numbers; record forks and successors with
qualified versioned references. New work must have one canonical maintenance
home. Another repository holds a reference or an explicitly independent fork,
not an unlabelled second authority.

Mingli reports that this rule is already recorded in a document called R0.
The exact R0 path/revision was not located in the accessible sources during
this drafting. Its contents are not claimed as reviewed. The rule here is
grounded in his explicit 2026-09-28 instruction and the two fixed files above;
linking the exact R0 remains a documentary follow-up, not a reason to guess one.

## 9. Change and release management

**KPB-12 — Classify changes before adoption.**

| Change | Required treatment |
| --- | --- |
| Alias, translation or expanded derived notation | Version the presentation/expansion and preserve interpretation scope |
| Search policy, candidate generator or domain package | Version the method/package; retain the unchanged receiver and compare within a finite contract |
| New primitive, judgment form or admission rule, guard/equality change, trusted verifier, or changed certificate interpretation | Kernel/profile successor with explicit rules, trusted-base impact and conformance evidence |
| Cross-profile correspondence | Explicit translation contract with accepted/refused examples and coverage residual |
| Correction or supersession | Preserve original bytes/evidence, name the changed scope and affected dependents |

Rules are versioned by meaning, not merely by the implementation's language or
filename. A fixed profile cannot silently acquire a new checker because a newer
binary is installed. Changing an existing stable operation follows the current
`OperationSpec`/IR-versioning discipline [S7]. An extension may coexist with
older profiles; it does not globally upgrade their results.

A kernel or cross-package interface change record must state: the problem;
affected objects/profiles; exact proposed rules; alternatives and objections;
preserved and lost properties; dependency impact; positive/negative checks;
actual results and cost; unresolved questions; and migration/reversion route.
The proposer and reviewing agent/person record their actual roles. Agreement,
merge, attribution and signatures do not replace checking evidence. Approval of
a design and evidence supporting its mathematical claims are separate statuses.

Ordinary edits need no new research number. Use existing ADR/decision and claim
mechanisms, with the correct owning repository, rather than a parallel ledger.
Record concept splits and proposed unifications without forcing one global name.

## 10. Three-repository operation

**KPB-13 — One home, pinned consumers.**

| Repository | Responsibility under this contract |
| --- | --- |
| `adva-machine` | Canonical kernel/package interface specifications, checking implementations and conformance; this contract's maintenance home |
| `adva` | Research questions, interpretations, task-specific methods, experiments, scoped claims and retained evidence; consume fixed machine/library versions |
| `adva-library` | Current catalog/material homes and their existing receiving/reuse conditions; no general executable package authority is inferred |

This table does not decide the still-open physical split of `adva-library`.
Do not move inherited code, payloads, logs or evidence merely to fit the table.
Retirement of a duplicate implementation needs a checked replacement for each
consumer and a retained replay route. Documentary adoption of this contract
does not advance executable locks, submodule pins or historical source hashes.

Actual cross-repository content migration follows the existing transport/
communication and receiving contracts [S4, S5]. Writing specification files
or synchronizing Git is engineering work, not an executed Adva exchange.
Keep publication eligibility and software dependency licensing separate from
semantic acceptance. Existing publication rules govern all new payloads.

## 11. Adoption and implementation gates

The baseline below is source inspection at `adva-machine@3043be35ff1186d502d091baa8bb96581449595c`,
`adva@fec283277f3175be2a6ff69897d896526fc54fc9`, and
`adva-library@dbb73e393a67f071744490eec29d18b3c20fe6f3`.
It does not claim a fresh execution of those experiments.

| Capability | Baseline | Next obligation |
| --- | --- | --- |
| Scoped A/M witnesses, guards, fresh instances | Existing bounded Rust research implementation [S1] | Inventory its exact trusted rules and costs; preserve separation from PSC0 |
| Method-driven native learn | Existing bounded methods; the six-stage example replays 15 prior stages [S2, S3] | Preserve question, guards and spent work at any new cut |
| Checked persistent library | Existing research loader, maximum four-epoch ancestry [S6] | Do not lift the bound or skip ancestors without a successor contract |
| Documentary transport | Existing bounded receiving route [S4] | No promotion to general executable package admission |
| General package loader and cut-certificate checker | **Not supplied by this contract** | Versioned implementation plus positive and adversarial conformance |
| Automatic namespace/dependency/impact audit | **Not supplied by this contract** | Read-only documentary tooling, with its limited authority stated |

**KPB-14 — Incremental gates.** Implement these in order, keeping each step
bounded and independently reviewable:

1. **Inventory.** Map existing witness rules, learning method contracts and one
   library consumer to section 5. Classify every trusted component and open
   field. Reuse current registries; do not migrate payloads.
2. **Documentary package pilot.** Describe those three units, resolve all
   qualified references and produce a current view of definitions, premises,
   exports and unresolved dependencies. Passing is metadata consistency only.
3. **Executable boundary pilot.** Design and implement a new profile for one
   selected reuse/cut route. Preserve the old loader and its four-epoch rule.
   Declare budgets before running; measure first-check and reuse cost separately.
4. **Consumer adoption.** Upgrade one consumer through a successor lock and new
   evidence; only then consider retirement of its duplicate path. Each other
   consumer remains pinned until its own migration completes.

The following acceptance obligations belong to the executable pilot, not to a
test suite claimed as run by this documentation change:

| ID | Required example/control | Required observation |
| --- | --- | --- |
| B01 | Valid formed components and guarded composition | Scoped success with all provenance and instance bindings |
| B02 | Opposite malformed boundaries; disconnected cancelling ratios | Rejection before a false composite success |
| B03 | Symbolic unity with a concrete intermediate zero | Guard refusal; no successful seal |
| B04 | Same export name in different packages or profiles | No implicit identification; explicit translation or refusal |
| B05 | Same research number in the two repositories | Resolve exact qualified paths; never local fallback |
| B06 | Missing premise, deleted guard, forged success flag | No unconditional admission; distinguish invalid from unavailable |
| B07 | Cache hit after changing checker/profile/premise/input | Recheck, proved applicable compatibility, or explicit refusal |
| B08 | Time/memory/dependency-depth exhaustion and continuation | Incomplete outcome, retained spending and no hidden reset |
| B09 | Method attempts to replace its acceptance rules | No self-granted authority |
| B10 | Remove the domain/search package while retaining its proof material | Applicable kernel checker can check the supported certificate without trusting the producer |
| B11 | Reuse with fresh occurrence bindings | No implicit sharing or collapse of history |
| B12 | Replay versus supported cut/cache reuse | Compare judgments, premises, residuals and total checking/storage cost |

A successful pilot may establish one receiving route. It must not be reported
as unrestricted package composition, universal arithmetic truth, complete
learning vocabulary, constant-time validation, or completion of the programme.

## 12. Sources and revision record

All source references below are repository-qualified and commit-pinned. They
are documentary references, not new executable imports.

- [S1: adva-machine / Research 0107, six-word witness kernel][S1].
- [S2: adva-machine / semantic scope and research interfaces][S2].
- [S3: adva-machine / Research 0136, guarded learn roundtrip][S3].
- [S4: adva-machine / transport and communication v2][S4].
- [S5: adva / knowledge-machine dependency boundary][S5].
- [S6: adva-machine / ADR 0038, persistent research epochs][S6].
- [S7: adva-machine / ADR 0003, single operation registry][S7].
- [S8: adva / Research 0207][S8].
- [S9: adva-machine / Research 0207][S9].
- [S10: adva-library / math catalog and growth obligations][S10].

The user directions of 2026-09-28 supply the finite-observer, naming,
kernel/package and qualified-reference requirements. Original wording and
engineering formulation are by ChatGPT. No third-party text, figure, dataset
or software is incorporated by this contract.

| Version | Change | Implementation effect |
| --- | --- | --- |
| 0.1, 2026-09-28 | Initial boundary contract, qualified references and finite adoption gates | Documentation and review rules only |

Future substantive revisions must have a distinct version and an explicit
predecessor/scope mapping. Preserve this version's meaning and published source
references. Errata must identify the affected clause and retained original
revision; do not silently claim old readers or evidence used the correction.

[S1]: https://github.com/mountain/adva-machine/blob/3043be35ff1186d502d091baa8bb96581449595c/docs/research/0107-reusable-six-word-witness-kernel.md
[S2]: https://github.com/mountain/adva-machine/blob/3043be35ff1186d502d091baa8bb96581449595c/docs/SEMANTIC_SCOPE.md
[S3]: https://github.com/mountain/adva-machine/blob/3043be35ff1186d502d091baa8bb96581449595c/docs/research/0136-native-learn-guarded-roundtrip.md
[S4]: https://github.com/mountain/adva-machine/blob/3043be35ff1186d502d091baa8bb96581449595c/spec/framework/transport-communication-v2.md
[S5]: https://github.com/mountain/adva/blob/fec283277f3175be2a6ff69897d896526fc54fc9/docs/KNOWLEDGE_MACHINE_BOUNDARY.md
[S6]: https://github.com/mountain/adva-machine/blob/3043be35ff1186d502d091baa8bb96581449595c/docs/adr/0038-checked-persistent-research-library-epochs.md
[S7]: https://github.com/mountain/adva-machine/blob/3043be35ff1186d502d091baa8bb96581449595c/docs/adr/0003-single-operation-registry.md
[S8]: https://github.com/mountain/adva/blob/fec283277f3175be2a6ff69897d896526fc54fc9/docs/research/0207-constructive-starvation-and-budget-matched-control.md
[S9]: https://github.com/mountain/adva-machine/blob/3043be35ff1186d502d091baa8bb96581449595c/docs/research/0207-renaming-the-iota-combinator-spelling-on-the-accepted-package.md
[S10]: https://github.com/mountain/adva-library/blob/dbb73e393a67f071744490eec29d18b3c20fe6f3/math/README.md
