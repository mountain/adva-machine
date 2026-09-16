# ADR 0049: A compact structure card and reusable exchange supervisor

Status: implemented bounded routine, 2026-09-16. Authored by ChatGPT (OpenAI),
contributed under Unknown v0.3 through Mingli Yuan's authorized account proxy;
account use is not his review or endorsement.

The first documentary exchange required a hand-authored supervisor around four
native calls. The following discussion of concept formation and mathematical
organization also needed a concise way to retain objects, relations, evidence
status and open questions across participants. The user asked for a reusable
routine to exchange structures quickly.

Add [the compact exchange routine](../../exchange_routine/README.md): an original
documentary structure-card format with read-only inspection/comparison, and one
command supervising the existing Rust send/receive/replay/acknowledge sequence.
The actual transfer retains its independently selected executable, receiving
contract, publication record and context. A structure card can be a bound
documentary payload once its source entry and receiving contract exist.

The human-facing convention asks for a brief restatement, explicit differences
and one bounded continuation. A response is not inferred for an absent
participant. Shape checking, understanding a proposal, accepting documentary
use and proving a claim retain different scopes. Removed questions and
preservation requirements are visible in comparisons; no obligation is
automatically discharged.

Use a separate `adva-exchange` checkout entry and `exchange_routine/` package.
The current `toolchain/*.py` sources are bound by retained conformance evidence;
this addition does not rewrite that historical producer set. The new supervisor
reuses its existing bounded process controller. Rust's communication checker
source and Cargo.lock stay unchanged, so the first exchange contract retains
its exact checker binding. No new Lisp operation, native identity or general
communication profile is introduced.

The supervisor publishes no branch and makes no rights decision. It preserves
partial artifacts outside repositories and delegates every payload/receipt/
acknowledgment write to Rust. It stops on refusal, missing capabilities or
resource exhaustion. A later explicit recheck has a new audit directory and
resource account, retaining the earlier receiver disposition.

Validation exercises a complete structure-card transfer through the real Rust
binary, explicit rechecking without repeated acceptance, pending publication,
wrong receiver/executable/request pins, changed source bytes, unavailable
checker, interrupted native recording and a supervisor interruption after
native acceptance. The latter intentionally leaves a real receiver receipt
while sender observation stays unknown. These cases establish finite workflow
behavior, not semantic correctness of prose or arbitrary crash consistency.

## Executed checks

All 21 routine tests and 36 existing toolchain/retained-evidence tests passed.
The tests build or explicitly select a real Rust executable; native integration
is not silently skipped when a binary is missing. The knowledge organization
example passed shape checking with eight objects and eight relations.

A separate invocation of `adva-exchange run` rechecked the original
`party-naming-layer-2026-09-16-v1` exchange using its unchanged contract
`d56b733921712b3ed0482acd6652d0efbfe0f0358daf69d0bd8099c9003ad5d9` (BLAKE3).
The four calls reported `Sent`, `AlreadyAccepted`, `AlreadyAccepted` and
`Acknowledged`, with 321,720 aggregate native read bytes and zero new acceptance
effects. The receipt remained
`5942c356e587f6d41df268d20f9da2d8ea5d7ee3cb054512ca8bf3d57bb5374a` (BLAKE3).
Knowledge and library working trees remained clean. The local audit's exact
result SHA-256 is `f918c62431ca99aefc9cfbea9580f37ed7cb0e409a9e7c1ebb701e172bbb89f2`;
its recorded eight producer source hashes matched this implementation. The
transport envelope and full local audit remain outside repository directories.
This explicitly budgeted recheck did not replay mathematical proofs or create
a new catalog home.
