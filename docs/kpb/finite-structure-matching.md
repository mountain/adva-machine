# Finite projected-ledger structure comparison

This read-only G2 pilot implements the separately versioned
[Iota ledger structural-matching profile](../../spec/framework/iota-ledger-structural-matching-v0.1.md).
It compares actual event/cut graphs, not G1 metadata-shape clusters. It grants no
semantic equivalence, native identities, transport acceptance or consumer upgrade.

## Reproduce

Python 3.11+ and Git, no third-party Python packages. The machine checkout must
contain main `79aced81e972e8a4af96b118d8e236f7e337ffcb`; the knowledge checkout
must contain `3287c61ab7d16253605b3d0cca818f5a698e258b`. Reads use these exact
objects, regardless of the working branch. They neither fetch nor execute sources.

```sh
python scripts/test_finite_structure_match.py
python scripts/finite_structure_match.py --knowledge-root ../adva > /tmp/structure-1.json
python scripts/finite_structure_match.py --knowledge-root ../adva > /tmp/structure-2.json
cmp /tmp/structure-1.json /tmp/structure-2.json
```

Expected outcomes: 12 `StructuralMatchCandidate` same-family pairs and three
`NoMatchWithinProfile` pairs: identity/double-identity, independent-iota/changed-roles,
and copy/copy-pending. Identity and double-identity have the same final term but
preserve different event histories. Positive tests additionally change every
local graph handle and reorder indexed source records with consistent remapping.
Two three-cycles versus one six-cycle defeats a degree-only false positive.
A small independent permutation oracle checks the matcher on original test graphs.

The report retains the complete projected graphs and original receipt contexts,
source JSON pointers, mappings, conditions, negative grounds and finite account.
It is a disposable query view, not a registry or evidence of native execution.
Every positive mapping receives a separate complete bijection/edge-multiset check.
New output artifacts need their own exact-byte publication review.

## Acceptance coverage and limits

- N03: separate receiving coordinates and incompatible profiles remain distinct
- N04: conditions, guards, source/occurrence labels and residuals cannot disappear
- N12: histories, directional dependencies, ordered interfaces and copy/discard survive
- N13: source, extraction, search, depth, invocation, output and wall limits retain Unknown
- N14: an input cannot replace the frozen checker/profile or self-grant Verified/admission

Schema/reference/syntax checks, structural comparison and semantic interpretation
are explicitly different outcomes. Syntax checks do not re-execute the source
reductions or prove causal validity. Missing complete ancestry and typed guards
are retained gaps, not satisfied premises. See the profile for exact representation,
allowed transformations, cooperative-budget limitations and successor gate.

## Retained failures and review

The first malformed-prefix negative exposed a diagnostic bug: a list-valued
source position was concatenated with an error string, causing `TypeError`.
The position is now stringified; the source remains rejected. This is a correction
to new code before publication, not a reinterpretation of any frozen source run.
Independent review also exposed Boolean/integer conflation in opaque conditions,
malformed edge values escaping validation, an oversized Unknown report retaining
a success process exit, and Git partial-clone lazy-fetch risk. Exact canonical
condition comparisons, strict edge fields, authoritative output status and disabled
lazy fetch/optional locks now have regression tests. Search depth and the emitted
edge/occurrence/boundary witness are checked explicitly.
Fresh test/reconstruction results and independent review are recorded separately
from the predecessor G1 verification. No old receipt or generated snapshot is edited.

Authored by dot (OpenAI), project-original under Unknown v0.3, through Mingli
Yuan's authorized account proxy; no human technical review or guarantee is implied.

## Local verification snapshot

The [retained observation](finite-structure-run-2026-09-30.json) binds exact code,
profile, inputs, result/evidence digests and limits. At this pre-publication snapshot:

- 31 finite controls passed; 45 retained G1/KPB controls passed on unchanged bytes
- Two 1,626,509-byte reconstructions were identical, SHA-256
  `26ea88dff0133d1b4c879ab47d7763ec5e47eed29a19c688ba415ecb663ba7de`
- 12 candidates and three scoped negatives; 24 graphs, 1,034 nodes and 4,784 edges
- 91,280 counted steps, depth 150, 30 source Git calls and 92,130 source bytes
- Outer measured wall time 0.345504s /0.302382s; child peak RSS 25,644 KiB
- Separate reviewer checked 59,959 exhaustive/labeled oracle pairs, 1,000 colored
  random cases and 20 deliberately forged edge bijections, with no remaining finding
- Python compilation, whitespace and known-withdrawal history checks passed

The local generator was not yet committed; exact SHA-256 binds its actual bytes,
while the recorded HEAD describes checkout ancestry. Later publication and remote
CI are separate observations. No fresh local full Rust/Python semantic run is
claimed here; the PR's full CI runs those unchanged native boundaries separately.
The optional `/usr/bin/time` wrapper was absent and ran no pilot; measurements
above used Python subprocess, monotonic time and child-resource observation.
