# Package capabilities and library carrier: v0.1 proposal

Date: 2026-10-10. Status: **local proposal, not adopted and not a native profile**.
Canonical proposed home: `mountain/adva-machine`. Authored by dot (OpenAI),
project-original work contributed under Unknown v0.3. Prepared for submission
through Mingli Yuan's GitHub account as an authorized proxy; account use is not
his authorship, technical review, endorsement or a correctness guarantee.

## 1. Predecessor and exact scope

Predecessor: [KPB v0.1](kernel-package-boundary-v0.1.md), read at machine
`a0b710a2517f06f2fe03cc463e855548adf418ac`. This is an additive proposal,
not an in-place revision of that contract. KPB-14 names the four gates in
section 11; it is not the name of the entire contract.

This proposal refines KPB-06's package description, KPB-13's repository
responsibilities and KPB-14's next documentary pilot. It preserves KPB-01–14,
A/M scope, guards, fresh identities, receiving rules, budget obligations,
frozen evidence, four-epoch ancestry and all consumer pins. It changes no
operation registry, Rust identity/judgment, native admission, cache or loader.
A later incompatible rule needs a separately reviewed profile successor.

The immediate question is whether a package can expose a useful library-only
interface and an executable reference-linking tool without pretending to perform
Adva computation, verification, or own the user's interaction history. Library
content remains primary; its minimum practical interface includes bounded
reference lookup/validation, not passive storage alone. The attached code checks
bounded documentary instances and locates exact local Git blobs.

## 2. Responsibilities and capabilities are different axes

Repository ownership remains:

- `adva-machine`: canonical contracts, native checking implementations and
  conformance. Only an applicable selected native boundary admits native judgments.
- `adva`: questions, interpretations, experiments, methods, claims and evidence;
  its consumers choose fixed machine/library revisions.
- `adva-library`: canonical material homes, identity/version references, content,
  typed relationships, provenance and an extensible documentary carrier.

Package capability is a separate nonempty subset of `{compute, verify, library}`.
A package may implement one, two or all three. Its maintenance home, source
language or storage location does not automatically grant any capability.
Outsourced implementations do not transfer the owning repository's obligations.

A declared capability supplies a versioned profile and explicit interface
binding. A compute interface must bind input/output domains, guards, effects,
implementation and execution budget. A verify interface must bind judgment,
premises, evidence format, receiver/checker/build and trust boundary. A library
interface binds identity/revision, materials, relationship vocabulary, origin,
extensions, retrieval limits and availability. Executable/evidence descriptions
must map every KPB-06 field, including lifecycle and receiving gaps. This does
not require a new registry: descriptions may project existing catalog,
OperationSpec, claims, lock and profile sources without copying their authority.

Typed optional interfaces are discoverable declarations, not callable objects
or automatically trusted verdicts. A package may produce candidate evidence;
only an independently selected applicable receiver can accept it. Trusting an
external verifier's result as a premise enlarges the declared trust boundary.
A library-only package must remain usable without a compute or verify service.

## 3. Minimal library carrier and the scoped fixture

The minimal proposed core is deliberately documentary:

1. Identity and version: maintenance home, namespace/name/revision, exact
   repository/path/full-commit references where source bytes are claimed.
2. Content and relationships: bounded materials and annotations, explicit local
   IDs, separately typed edges. These IDs never allocate native identities.
3. Origin and extensions: contributor/publication basis, source coordinates,
   required/optional versioned extension namespaces and retained residuals.

The schema at `experiments/package_manifest_pilot/manifest.schema.json` is a
**trial wire description**, not a stable package format. The profile label
`adva.library-carrier.draft.v0` names only this proposal's finite documentary lint.
The fixture capability's `source_contract` reference points to the pinned KPB-06
boundary being mapped, not to an existing implementation of this new profile.
Its local schema/checker and this proposal supply the trial interface; a
published adoption must additionally pin their exact committed bytes. No draft
file is falsely claimed to exist at the predecessor commit.

The trial keeps four original inline materials and two named trails over those
same objects. A trail is a named ordered list of material/annotation IDs. It may
revisit an object; it does not clone the material. A branch/continuation records
its source trail and step while keeping its own explicit sequence. A branch
origin is provenance, not a required shared prefix or a proof premise. Trail
origins must be acyclic; associative material graphs may cycle. An annotation
edge must originate in an annotation object and have a present target.

Sharing means transferring a version-bound trail description through an
appropriate authorized transport route. This prototype performs no transfer,
sharing permission change or synchronization. Continuation is not proof-fuel
continuation. Deleted/unavailable external targets are retained as unresolved
references by a future resolver, never silently replaced by matching names.
The offline prototype rejects dangling *local* targets and reports that all
external source availability is unchecked.

Learning-progress tracking, search ranking/indexing, interaction state,
authentication, media execution/rendering and UI live outside the library
core. Optional presentation metadata may coordinate several views of one
object, but synchronized display does not establish equivalence. Narrative
trail order, reactive computation dependencies and proof dependencies are
three separate relations. Changing display order cannot schedule a computation
or change its premises. The library-only receiver rejects computation-dependency
and proof-premise edges; richer profiles need their own typed semantics.

### Executable reference mechanism (machine pilot, not library deployment)

`lookup_reference.py` accepts one strict repository/commit/path coordinate and
optional SHA-256. The caller separately supplies a supported repository label,
consumer commit pin and local Git checkout. It never chooses the consumer pin
from the reference itself. The caller is responsible for the repository-label
binding; this tool makes no ownership/authenticity claim. It checks that the
reference matches that supplied repository/pin, that the full 40-hex coordinate
is a real locally available commit, and reads/hashes only that commit's exact
blob. Dirty working-tree bytes and Git replacement objects do not override it.
Git is invoked with `--no-lazy-fetch`, `GIT_NO_LAZY_FETCH=1`, and
`protocol.allow=never`; unsupported Git versions return explicit Unknown.
No current-branch lookup, same-name fallback, fetch, recursive dependency import,
external process execution of content, or network access is part of this tool.

The report distinguishes `ReferenceBytesLocated`, `Unknown/Unavailable`,
`Rejected/UnsupportedReference` or `UnsupportedRepository`,
`Rejected/IncompatibleRevision` or `IncompatibleDigest`, and
`Unknown/BudgetExhausted`. A located reference still retains NotRun/NotGranted.
These are tooling report states, not new native Adva outcomes. A Git hash/digest
binds bytes; it proves neither semantic compatibility nor publication eligibility.

The lookup has one 64 KiB reference-input budget, one 64 KiB target-blob budget,
at most three Git subprocess calls, a shared two-second deadline enforced as
remaining subprocess timeout, and the same bounded reporting routine. The
committed object size is checked before reading its payload; commit-addressed
bytes cannot become a different dirty file between those calls. Paths must be
relative and exclude traversal, backslashes and control characters. The local
Git executable/configuration, quiescent object store and OS remain trusted;
there is no hostile-checkout sandbox or physical-memory bound. Git metadata
and stderr capture are not preemptively bounded; controlled Git output is a
trusted-command assumption, not a pipe-memory isolation guarantee. Git setup,
lookup and hash counts/spending survive failures. Reports contain coordinates
and digest, never the referenced content itself.

Tests create original temporary Git fixtures and cover exact resolution, dirty
worktree isolation, matching/mismatched digest, missing path/commit, incompatible
consumer pin, unsupported repository/URL/moving revision/path, byte/time exhaustion
and forged success fields. Fixture production/commits and every receiver/control
are inside the same ten-second aggregate supervisor as the manifest tests.
This is executable tooling delivered in `adva-machine` for a library-facing
interface; **no change or deployment in `adva-library` has occurred**.

## 4. Compatibility, extension and failure rules

- Unknown top-level fields, duplicate JSON keys/IDs/capability kinds, malformed
  references and unsupported authority flags are Rejected by this strict trial.
- Unknown schema versions are Rejected as outside the selected schema.
  Unknown declared capability profiles yield Unknown for documentary inspection;
  actual compute/verify requests are refused as Rejected.
- Missing required local bytes or unknown required extension semantics yield
  Unknown, with no success result or native authority. An optional unknown
  extension is preserved in the input, ignored and named in the report. Even
  a `Verified` value inside such opaque metadata has no authority.
- Core compatibility is not inferred from version spelling. Changing a required
  extension, profile or interpretation needs a new receiver decision and
  evidence. No package can declare its own changed checker compatible.
- Package revision is a descriptive local label, not a digest/authentication
  claim. Publication/adoption must bind exact manifest/payload bytes and source
  commit through the existing consumer contract. This offline lint does not
  resolve, authenticate or trust any external bytes.
- MetadataConsistent means only shape and finite local links were checked.
  Every report retains `semantic_verification=NotRun` and
  `native_admission=NotGranted`. It changes no transport receipt or old result.
  Rejected is not a refutation; Unknown is not negative evidence.

## 5. Finite trial contract and accounting

The trial uses pre-existing separately installed Python/jsonschema, with its
version recorded in results; no software or dependency source is vendored.
It is documentary tooling and supplies no replacement for native Rust authority.
It reads at most 65,537 bytes per attempted local file, reports Unknown when the 65,536-byte resource budget is exhausted,
allows at most depth 32 after parsing, 32 content items, 64 relationships,
8 trails of 32 steps, 8 extensions and 16 residual strings. The local schema
is subject to the same read/depth bound. No remote fetch or recursive package
resolution occurs. Manifest lint reads at most two files per invocation; the
separate reference tool has the explicit budget stated above.

Read/parse/shape/link checks and their failures share one invocation account;
bytes read, parse calls, visited values, schema-validation calls, reference checks,
origin-chain hops, relationship checks and trail steps
are retained. Repeat lint is a fresh charged invocation, never cache admission.
Report encoding has a separate two-encoding account and an 8 KiB output cap.
Time checking is cooperative at invocation completion (two seconds), not a
preemptive guarantee; report encoding/write and interpreter/dependency startup
are outside that cooperative interval and must be measured by the outer run.
The example suite includes all producer fixture loading, both example replays,
controls, schema validation, reporting, imports and report writing in one outer
bounded process. Use `run_trial.py` with its ten-second aggregate subprocess timeout; observe
child CPU, elapsed and platform RSS separately. Supervisor startup and final
report write are outside its measured interval; child output-size limits are
post-write checks on this fixed test set. No continuation, automatic retry or budget reset.
A timeout/kill/missing report is Unknown, never a pass or resumable state.

Input depth/cardinality checks are post-parse admission checks, not preemptive
allocation limits. JSON parser/schema library/platform, quiescent regular local
files and trusted local schema are assumptions. No physical memory ceiling,
secure sandbox, hostile filesystem protection, network service, source
availability or native resource enforcement is supplied. Counts do not measure
CPU instructions or claim speedup. A real producer/receiver/replay service must
supply separately bounded implementation and aggregate costs before adoption.

## 6. Incremental gates, retaining actual prior work

Keep the original G1–G4 ordering and evidence. Do not restart them or mark them
universally complete because a new library pilot passes.

| Gate | Existing evidence context | Next package-specific obligation |
|---|---|---|
| G1 inventory | Existing finite source projections; two exact claim-binding gaps remain | Map capability descriptions onto existing owning sources; retain all missing fields |
| G2 documentary pilot | Existing documentary descriptions and separately bounded structure comparison | Run this library-only shape/relationship pilot and independently inspect its authority limits |
| G3 executable boundary | Checked-roundtrip local-cache route and a separate synthetic raw native-evidence intake | Select at most one additional capability route; write its receiver/trust/budget contract before execution; no automatic authority from this pilot |
| G4 one consumer | A selected adva consumer has separately migrated its machine lock; synthetic intake was not that adoption | Only after appropriate prior gates, choose one real library consumer and create a successor lock/new evidence; do not update all consumers |

The two unresolved claim IDs are `adva.bounded-experiment.leak-wall.v0` and
`adva.exact.structural-forward-differential.v1`; no alias or replacement is
invented here. The current exact status and historical consumer pins must be
rechecked from their owning records when integration is proposed. This change
executes none of the older G1/G2/native G3/G4 checks, and makes no claim
that B01–B12 have now all passed.

Trial acceptance controls are in `test_manifest.py`: library-only success;
two paths sharing material; independent narrative order; permitted associative
cycles; forbidden branch-origin cycles; missing/duplicate IDs; dangling relation,
annotation and origin targets; changed profile/version; optional vs required
extension; forged authority; compute/verify refusal; byte/cardinality/time
bounds; missing bytes; duplicate keys/nonfinite values; and repeat accounting.
A passing run is documentary evidence only, not mathematical progress or an
implemented general package loader.

## 7. Decisions still open and the smallest next delivery

Adopt the responsibility/capability distinction and minimal library carrier as
a design direction; review this trial before selecting a real consumer. Do not
wait for a universal language to complete that limited documentary experiment.

The Adva core vocabulary's minimal completeness remains **relative to a named
profile and responsibility**. A follow-on decision must state target judgments,
what is derived versus primitive, expressiveness and excluded tasks, minimality
criterion and counterexample tests. Neither compute/verify/library labels nor
the existing six-word research kernel settles that question.

First landing can be only these additive files and their finite tests. Second
landing, separately reviewed, maps one existing real material home without
moving content and pins an actual consumer fixture. Only then consider executable
capability wiring. Reversion removes the new unadopted proposal/pilot; it cannot
rewrite historical contracts, receipts, source homes or consumer locks.

## 8. Motivation and publication scope

The trail and linked-representation requirements are original engineering
formulations prompted by the user's discussion of Bush's memex trails, Bret
Victor's media for thinking, and Observable's distinction between dependency
execution and narrative order. They are design motivations, not evidence that
Adva implements those systems or their semantics. No third-party prose, code,
figures, PDFs or payloads are incorporated.

- Bret Victor, [Media for Thinking the Unthinkable](https://worrydream.com/MediaForThinkingTheUnthinkable/)
- Observable Framework, [Reactivity](https://observablehq.github.io/framework/reactivity)
- Bush, *As We May Think*: bibliographic motivation supplied in discussion;
  no edition/translation is admitted or copied.

This contribution contains original schema, code, synthetic wording and
specification only. Publication still requires the repository's exact staged
payload review and known-withdrawal check; local tests do not grant publication
rights or claim that a full repository audit ran.
