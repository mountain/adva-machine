# Agent instructions

## Unknown adoption

The project adopts [Unknown v0.2](Unknown-LICENSE-v0.2.md): public domain with
a voluntary philosophical statement. Use [LICENSING.md](LICENSING.md) for scope.
Contribution and attribution practices below govern this project's workflow;
they do not add copyright conditions on downstream use. Preserve separately
licensed third-party material and frozen historical evidence.

## Local toolchain continuation, 2026-09-16

The user's latest direction makes this local repository `adva-machine`, owning
the Adva specification entry points and Rust/Python toolchains. The original
GitHub `mountain/adva` is intended to evolve toward knowledge. `adva-library`'s
eventual organization remains Open and is consumed at a fixed revision here.
Read `docs/TOOLCHAIN_DIRECTION.md` for the concrete migration boundary.

The integration practice below records the source repository's history. For
this independent local continuation, commit completed work to local `main`;
`adva-source` is the historical source remote, not a selected publishing target
for machine changes. Preserve frozen paths/profiles and evidence while adding
toolchain entry points. No remote repository rename or library split is implied.

## Documentation language

Mingli Yuan's instruction, 2026-09-16: prioritize English documentation for
international collaboration. Write and maintain specifications, design records,
user/developer guides, research reports and shared change descriptions in English
first. Default navigation and references should lead to the English version.
Chinese and other language versions are optional supporting translations or
summaries; label their role and link to the primary English document. Correct
translation discrepancies against that document. See the
[documentation policy](docs/DEVELOPMENT.md#documentation-language).

## Required reading

Before modifying semantic code, read:

1. `README.md`
2. `docs/ARCHITECTURE.md`
3. `docs/SEMANTIC_SCOPE.md`
4. `docs/PROGRAM_PROCESS_CORE.md`
5. `docs/TECHNICAL_REPORT_PROGRAM_PROCESS_CORE.md`
6. `docs/NEXT_PHASE_TRIADIC_OBSERVER_TRANSITIONS.md`
7. `docs/claims.toml`
8. relevant ADRs under `docs/adr/`

Before starting or proposing a new research or engineering phase, also read
`docs/RESEARCH_ENGINEERING_AGENDA.md`. Its dependency order is part of the
project plan. The exact `GraftTrace`, `ProgramSlice`, and bounded triadic
transition phases are complete. The currently approved research-only bridge is
the typed aperture calibration in
`docs/research/0079-typed-hole-open-close-calibration-v0.md`. It does not
authorize a stable Rust hole calculus, observer specialization, or logic.

## Authority and dependency direction

- Rust is the sole authority for types, terms, diagrams, sources, occurrences,
  histories, cells, observers, calculus, and certificates.
- Python may adapt checked IR to SymPy, NumPy, SciPy, plotting, search, or
  experiments. Python must not create or identify semantic identities.
- The versioned JSON IR is the language-independent interchange boundary.
- External or stored diagrams enter semantic code only through the Rust
  `validate_diagram` / `import_diagram_json` boundary. Serde decoding alone is
  not authorization.
- `process-geometry` supplies theory and independent regression oracles. Do not
  silently copy its experimental claims into the stable API.

## Ontology discipline

Keep `TypedFrontier`, `DomainFrontier`, `CodomainFrontier`, `ProgramTerm`,
`SharedProgramDiagram`, `CausalCut`, `CausalStep`, `History`, `Value`,
`Occurrence`, `Source`,
`ProjectiveDevelopment`, `Probe`, `ObservationPolicy`,
`PredicateRegion`, `ProofObject`, `DirectedRewrite`, `EquationCell`,
`CoherenceCell`, and `ObjectificationWitness` distinct.

`SourceId` and `OccurrenceId` must be explicit, deterministic, stable under
serialization, and independent of memory addresses, object identity, value
equality, structural hashing, or accidental AST sharing.

Sharing is a program operation whose result has two ordered output ports on a
`TypedFrontier`; it is never a type modifier or host-language alias.
Treat a function boundary as an ordered family of holes and
`ProgramTerm::Call` as the current finite simultaneous-substitution mechanism.
Do not describe finite lowering as value application: argument programs are
grafted before evaluation. The flat call history is not yet a complete
nested-substitution carrier.
`DomainFrontier` and `CodomainFrontier` orient a 1-cell boundary; they do not
stand for the temporal and spatial sides of the semantic duality. No frontier
type may be presented as an implemented tensor product. Value equality and
observational equivalence never authorize contraction, memoization, CSE, or a
cell.

The research-only typed aperture presentation is derived from existing
through relations and exact residuals. Do not conflate a function input hole,
cut port, syntax metavariable, logical obligation, observer aperture, or
singular point. `Open` and `Close` are not stable operations or historical
inverses, and an empty or multivalued filling fibre does not by itself define
`Omega`.

For `D: DomainFrontier -> CodomainFrontier`, reserve `D*` for a future
contravariant observer pullback. Do not implement it as a `ProgramTerm`,
boundary swap, inverse, dagger, involution, or unconditional matrix transpose.
Any executable pullback must be derived from a checked diagram and return a
certificate.

Directed normalization steps, invertible equation cells, and coherence cells
use different Rust types. Search exhaustion produces `Unknown`, never a proof
of nonexistence.

`CausalCut` and `CausalStep` are derived readings of a checked
`SharedProgramDiagram`. They must reuse exact `WireRef`, source, occurrence,
and lineage data. Python may request these Rust judgments but must not
reconstruct or authorize them.

Triadic domain labels are observer-policy metadata over exact input-source
fibres. They must not be installed as wire types or inferred from scalar
values. Opposite-pair views may overlap, while source-free and hidden
incidences remain in an explicit residual. A triadic observer transition is a
view of a `ProgramSlice`; it is not an active program transformation,
reversible transport, specialization result, or proof object.

## Scope

Stable code currently covers the binder-free, finite, linear core. Keep
objectification, generic higher proof transport, HPC, sheaf/stack semantics,
full abstraction, and physical interpretations out of the stable API.

All semantic transformations return a result together with a certificate.
Tests are evidence for the declared finite scope, not unrestricted theorems.

## Math directory growth obligation

When extending mathematical library content or proposing mathematical program
growth, read `adva-library/math/README.md` and the pinned obligation and
documentary checkpoint under `adva-library/math/constraints/`.
Each entry has one home directory. Cross-topic references are not derivation
parents, implicit imports, or permission transfers. Geometry growth must start
at the pinned Pascal presentations and retain a same-directory derivation
chain; unconnected Q4/M6 or other legacy materials are references, not admitted
Pascal descendants. The current geometry obligation is Open. Do not mark it
discharged or issue a native `Seal` without the missing native import and
derivation certificates. A documentary `seal` pins an obligation; it is not a
Rust `Seal`. Do not rewrite the obligation or reseal it merely to pass a check.
Continuations remain separately finite and do not reset fuel automatically.

## Operation changes

Stable Lisp builtins are declared through the Rust `OperationSpec` registry.
Do not add separate parser, type-checker, evaluator, differential, or lineage
name tables. A new operation must declare its versioned boundary, exact
parameters, surface visibility, scalar differential realization, and explicit
`LineageRule`, with a registry completeness test. Changing an existing rule is
an IR-versioning decision, not an in-place reinterpretation.

## Bounded breakthrough research

Before a breakthrough trial, read
`docs/research/0129-bounded-breakthrough-trusted-boundaries.md` and write the
concrete question, current level, imported assumptions, cross-domain
justification, protected obligations, checker, and enforceable finite budget.
Missing boundary evidence blocks execution. Count checking, retries, nested
searches, and checkpointing within the declared resource limits. Stop on the
specified outcome or limit, retain failures and residuals, and report
exhaustion as `Unknown`. Do not automatically reset fuel, widen scope, or
restart indefinitely. Continuation requires a revised finite run contract and
rechecked boundaries within the existing authorization. A heuristic score
never overrides a protected obligation. A working name or energy-level label
does not establish a native operation, physical interpretation, or completed
language-formation step.

## Authorship and proxy attribution

Commits made by an autonomous agent in this repository carry two trailers:

    Agent-Authored-By: <model> (DeepSeek Harness) <agent@deepseek-harness.invalid>
    Agent-Committed-Through: Mingli Yuan <mingli.yuan@gmail.com> - account and
      credentials only; not endorsement, not review, not a correctness claim

The git author field stays the account owner because the commit travels through
that account's repository and credentials. That is a technical channel. The
trailers say who wrote the change and that nobody vouched for it.

The account owner does not vouch for the content, and this rule exists because of
how he put it: he trusts the **mechanism** - bounded checks, retained witnesses,
recorded failures and residuals, one declared contract per new machinery - and
explicitly does not treat machines as free of bugs, nor does he claim the
mathematical competence to approve a result. Therefore:

- **A signature never certifies correctness.** Every claim must point to its
  executed check, its witness and its residual. Where no check exists, the claim
  is not made, and a green run is a statement about verification, not progress.
- **No approval is required for an agent to state what its checks establish**, and
  the account owner's name may not be cited as evidence for any of it. The
  authority is the executed check and the retained residual, never a person.
- **The limits an agent observes are the repository's own conventions**, not a
  grant of permission: shared branches, main, published history and account
  credentials are changed by the project's review process, so an agent does not
  rewrite published history, force-push, or alter credentials on its own
  initiative - and does not describe that restraint as waiting for authorization.
- **Errors are expected and must be visible.** A false assertion, a reverted
  half-working attempt and a failed control are recorded in the notes rather than
  quietly repaired, because the mechanism is only worth trusting while its
  failures remain on the record.

## AI authorship and account proxy

Follow [docs/AI_ATTRIBUTION.md](docs/AI_ATTRIBUTION.md), recording Mingli
Yuan's explicit 2026-09-10 instruction. Sign AI-produced reports, PR bodies
and commit messages with the actual assistant's name and state that they
are submitted through his GitHub account as an authorized proxy. Account
ownership does not imply personal authorship or technical verification by
Mingli. Authorization and mutual trust do not establish correctness: both
human proposals and AI reasoning/code remain open to challenge and revision.
Record actual contributions, checks and limits; do not imply guarantees or
transfer responsibility merely through account use. Follow the mutual
fallibility clarification in the linked document. This attribution rule
does not expand operational authorization.

## Integration practice

Mingli Yuan's instruction, 2026-09-11:

> 直接合并主线，以后如果不是工程特别需要，请直接合并主线

So finished work is committed on `main` and pushed there, rather than being
parked on a side branch for a later merge. A branch is used only when the
engineering itself requires one: an isolated build or CI job, a change that has
to run detached from `main`, work that is not finished, or a line the project
has explicitly agreed to keep separate until it is accepted.

This changes where integration happens, not what an agent may do to published
history. The restraint in the attribution section still holds: no force-push,
no rewriting of published commits, no credential changes, and no push of a
change whose checks have not run. A direct `main` push is still a fast-forward
or a reviewed merge, and the checks for the change are reported with it,
including the ones that could not run on the current host.
