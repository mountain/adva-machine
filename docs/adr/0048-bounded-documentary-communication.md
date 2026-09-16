# ADR 0048: Implement one bounded documentary communication profile

Status: implemented bounded CLI profile, 2026-09-16. General native communication
remains open. Authored by ChatGPT (OpenAI), contributed under Unknown v0.3 through
Mingli Yuan's authorized account proxy; account use is not review or endorsement.

## Problem and decision

The repositories' publication cleanup makes an uncontrolled file move unsuitable
for content migration. Communication v1 already requires a checked receiving
contract. Implement
[documentary-library-entry-v1](../../spec/framework/documentary-exchange-v1.md)
in the Rust `adva` CLI before receiving one original library entry into the
knowledge repository. Keep its source home and dependencies intact.

The contract binds the selected catalog entry, exact materials, independent
publication review, recipient context and compiled checker source/lock. The
Rust receiver checks these bindings before publishing its local directory and
receipt. The sender subsequently observes a particular reply. Repeated delivery
reuses the prior disposition; missing replies, unavailable checkers and partial
records keep an explicit unresolved result.

The first selected entry is `logic-party-naming-layer`. Its three naming JSON
files fit this profile; the original Pascal references remain documentary
references and their bytes are not imported. The receiving run and its actual
publication review belong with the knowledge recipient, and the observed
acknowledgment belongs with the library sender. This implementation decision
alone does not claim that exchange has happened.

## Authority and limits

Publication review and receiving acceptance are different judgments. The code
checks a completed, independently pinned review record but cannot determine
copyright status. It verifies bytes with BLAKE3, retaining the independently
reviewed SHA-256 pins. The result grants documentary reference use only; a
receipt cannot discharge the entry's open human acceptance or native identity
obligations.

Source retirement and a new catalog home are separate future effects requiring
dependency continuity. The kernel, Lisp operation registry, native specification
catalog, historical communication registry and existing consumer locks keep
their versions. This profile is versioned beside them. It neither implements
general communication nor repairs the remaining `mix`/Futamura projections.

The local filesystem is a transport/persistence backend inside the checked
receiver. The declared model is trusted, quiescent POSIX storage with cooperative
invocation bounds; hostile path races and general distributed delivery are not
claimed. Operators retain per-attempt JSON observations with resource accounts.

## Development checks and retained failure

The first compiled CLI integration run on 2026-09-16 had five passing cases and
nine failing cases. Sending to a bare output filename wrote the envelope but
returned `Unknown` because directory sync used an empty parent path. This was
a partial output, not a successful dispatch. Resolving a bare filename's parent
to the current directory corrected the implementation. The same integration
cases then passed; unavailable-checker coverage was added afterward.

The executable cases also require that source files stay unchanged, a repeated
receive creates zero new acceptance effects, pending stages and old locks are
retained, review failures cannot emit an envelope, and altered obligations or
receipts cannot acquire broader acceptance. Bounds and interruption cases are
finite observations, not proofs of correctness for arbitrary hosts.

After the correction, all 15 communication integration tests, five existing
library CLI tests and 36 toolchain/retained-evidence Python tests passed.
`cargo clippy --locked -p adva-witness --bin adva --test communication_cli -- -D warnings`
also passed. These are the checks executed for this change, rather than a claim
that the entire historical research suite was rerun.

## Missed dependent contract, and its explicit successor

The full Python CI for `df8b29a` exposed a missed dependency in this change:
`test_the_base_commit_boundary_holds_at_this_commit` failed because the active
symbol-surface contract v8 still required the earlier entire Rust directory.
The communication CLI, dispatch and integration tests changed three paths
inside that protected boundary. The Python 3.12 job retained 2,834 passing
tests, five skips and this one failure in
[run 35109036957](https://github.com/mountain/adva-machine/actions/runs/35109036957).
The same failing assertion was reproduced locally before correction.

[Contract v9](../../experiments/advance_symbol_surface/contract-v9.json) names
v8's exact digest and advances only its version/base/chain metadata to the
communication commit. v0 through v8 and all retained evidence remain unchanged.
The live entry selects v9; the existing chain test now includes v8 and v9 and
still enforces ancestry and zero differences across all Cargo/crate paths.
Input pins, library boundary, open obligations, authorization and execution
limits are unchanged. This corrects the declared engineering baseline; it
does not replay the trial or establish a new symbol-surface result.

After this correction, 170 selected Python regressions passed: the contract
chain, symbol-surface and advance boundaries, math catalog, exchange routine,
and existing machine toolchain/evidence checks. The native communication source
and Cargo lock stayed unchanged, preserving the actual exchange bindings.
