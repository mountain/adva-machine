# A native Iota substrate, checked against an external frozen witness

Status: **research-local executable crate**, 2026-09-20. It is not part of
Adva's stable semantic API. It adds no `ValueType`, no `OperationSpec`, no
registry entry, no IR version, no `Seal` and no stable semantic type; native
admission is `NotGranted`.

DeepSeek Harness (deepseek-v4-flash-vision-exp) authored this crate and its
checks under Unknown v0.3 through Mingli Yuan's authorized account proxy;
account use is not his authorship, review, endorsement or correctness
guarantee. The transported materials are the `murphy` publication unit
(`mountain/adva`, admitted 2026-09-19), authored by ChatGPT (OpenAI) from
Mingli Yuan's direction. Nobody vouches for the result; the executed check and
the retained residual are the authority.

## The question

The machine has no Iota evaluator: `spec/framework/iota-frame-v1.md` binds a
minimal iota *process* as a research profile whose executable part is Python,
and the received carrier-matrix profile is Python as well. The `murphy`
publication unit already retains, for one named program and its coordinate
family, a counted reduction witness produced by an independent implementation.

So the narrow question is:

> Can the machine parse and reduce pure Iota source in its own Rust source,
> under declared bounds, and reproduce the externally frozen contraction
> count, rule histogram, node peak and normal-form digest **byte for byte**,
> without adding a dependency or moving the pinned `Cargo.lock`?

A `yes` is a capability statement about this machine, not a claim that Iota is
an Adva subset. A `no` would be a located boundary, also worth keeping.

## What is declared, and where it comes from

The external witness declares (see `contract.json`):

| Element | Declared reading |
| --- | --- |
| source | `i` is the Iota combinator, `*AB` is application; anything else is refused |
| Iota rule | `j a -> a S K` |
| other rules | `I a -> a`, `K a b -> a`, `S x y z -> x z (y z)` |
| order | leftmost-outermost on combinator trees |
| counting | one contraction per applied combinator, named by that combinator |
| size | `nodes(t)` counts one per application and one per leaf |
| digest | SHA-256 over the canonical JSON encoding `["a",f,x]`, `["c",name]`, `["v",name]`, `["l",name,body]` |
| coordinate families | the program applied to the declared four-slot product `Z(p,q,r,s) = lambda k. k p q r s`, through bracket abstraction without eta |

The digest is what makes this a check rather than a resemblance: the encoding
is a function of the term alone, so agreement on the digest means the two
implementations agree on the whole normal form, and agreement on the retained
step trace means they agree after every contraction.

`--origin` supplies the origin's step trace separately from the transported
package, so what crossed the documentary boundary and what was supplied
independently stay distinguishable.

## Run

The crate is deliberately its own workspace root: the machine's `Cargo.lock`
is a pinned input of `spec/catalog.json` and `bootstrap/inputs.sha256`, and two
received documentary exchange contracts bind its BLAKE3. Adding a workspace
member would move that lock, so this experiment does not.

```sh
cd experiments/iota-substrate
cargo test --offline
cargo build --release --offline

# from the machine repository root: the contract paths are repository-relative
experiments/iota-substrate/target/release/adva-iota-substrate \
  --contract experiments/iota-substrate/contract.json \
  --output /tmp/iota-substrate-run-01 \
  --origin /path/to/adva/experiments/murphy
```

Every output directory must be new. The run reads only: the transported
materials listed in `contract.json`, the reception receipt it binds, and the
independently supplied origin trace (`evidence/PP-trace.json`, which is 252 KiB
and therefore was never part of a transport package limited to 64 KiB per
file). It writes one `result.json`.

## What the first executed round established

Five families, 5,348 contractions, against `mountain/adva`'s frozen
`evidence/result.json`:

| Family | Kind | Contractions | Peak nodes | Verdict |
| --- | --- | ---: | ---: | --- |
| `P` (`murphy.iota`) | iota | 893 | 833 | recorded, no frozen counted oracle exists for `P` alone |
| `PP` | iota | 1,808 | 7,627 | matched frozen oracle (`j` 822, `S` 549, `K` 437, digest `8d0434eb…`) |
| `C` | coordinate | 919 | 9,395 | matched frozen oracle (with `I` 1, digest `dc74b1b6…`) |
| `J` | coordinate | 831 | 7,889 | matched frozen oracle (digest `d40812c3…`) |
| `N` | coordinate | 897 | 8,545 | matched frozen oracle (digest `66c6cc71…`) |

The papered-in check behind those four rows is the step trace: all **1,808**
retained rows matched on path, rule, node count and per-step digest.

Six controls ran and passed, and each is the reason the corresponding claim is
not vacuous:

* `sha256-fips-vectors` — the locally implemented SHA-256 (no new dependency)
  reproduces the three FIPS 180-4 vectors;
* `digest-falsifier` — an altered expected digest is refused, so agreement is
  being tested rather than assumed;
* `order-alternative` — the same bounds under a leftmost-innermost order give
  different counts and a different digest, so the declared order is
  load-bearing;
* `budget-exhaustion` — a tight bound reports `Unknown` with no normal-form
  claim, never divergence;
* `non-vacuity` — every family contracts, and at least one frozen oracle is
  actually matched;
* `source-alteration` — one altered byte changes the source digest.

## The iota-lang case corpus

`contract-iota-lang.json` adds a second, separately declared corpus: the 17
recorded cases of the external iota-lang reduction contract
(`src/tests/java/iota/SKITest.java` at checkout HEAD `a1865e6…`, sha256
`c9b84b92…`), transcribed faithfully. It declares its own case grammar —
S-expressions whose tokens are `i` (the identity combinator), `k`, `s`, `ι`
(the Iota combinator) and lowercase opaque variables — because the murphy
grammar's `i` is the *Iota* combinator while the case grammar's `i` is the
*identity*. Both readings are declared, nothing mixes them, and a control
asserts the collision rather than resolving it silently.

```sh
# from the machine repository root; no --origin is needed for this corpus
experiments/iota-substrate/target/release/adva-iota-substrate \
  --contract experiments/iota-substrate/contract-iota-lang.json \
  --output /tmp/iota-substrate-iota-lang-01
```

Result: **17 of 17 recorded expectations reproduced**, 57 contractions, four
controls passed. The run also reports, separately, whether Research 0167's
frozen replay transcribed the same terms: 10 of 17 agree, and the seven that
differ are `testII` … `testIIIIII` and `testIota4`/`testIota5`. The transcript
is used only for that comparison and never as an expected value. The findings
are recorded in
[Research 0205](../../docs/research/0205-iota-lang-recorded-contract-replayed-by-the-native-substrate.md),
which also lists the iota-lang layers that are **not** usable here: the parser
contract, the DualMachine suite, the two Clojure-shaped resource definitions and
the never-compiled Java machine itself.

## The flat-list reading corpus

`contract-list-reading.json` declares one more notation — a flat list
`[t1 … tn]` — under **two declared readings**, `left-nested` and `right-nested`,
and asks which one transports application at the junction between a
right-expanded program and left-expanded data. Seven cases decide it: the
external `ski.iota` and `iota.iota` declarations hold under right-nesting
(identity, K and S on their declared arities, and `Iota x -> x S K`), the
left-nested reading fails for K and S, and a two-element list cannot decide the
reading at all because both readings agree there.

```sh
experiments/iota-substrate/target/release/adva-iota-substrate \
  --contract experiments/iota-substrate/contract-list-reading.json \
  --output /tmp/iota-substrate-list-reading-01
```

Result: 4 holding cases, 2 failing as declared, 1 two-element coincidence, 54
contractions, three controls passed. The finding is recorded in
[Research 0206](../../docs/research/0206-the-flat-list-reading-at-the-program-data-junction.md),
which also states what it is not: this is one reading of one notation, not the
representation map the murphy note names.

## What this does not establish

* **No native admission.** `ValueType` remains `Real | Bool`. No
  `OperationSpec`, parser surface form, registry change, IR version, schema or
  `Seal` is created, proposed or implied.
* **No claim that Iota is an Adva subset**, that any Adva program compiles to
  Iota, or that the reducer agrees with any denotational semantics beyond the
  declared rewriting rules. A returned normal form is a rewriting result, not
  a decoded string, a halting certificate or a language-equivalence proof.
* **No divergence claim.** Bounds are declared and enforced per family;
  exhaustion is `Unknown`.
* **Not independent verification.** The reference implementation and this one
  are two machine implementations by different agents, neither human-reviewed.
* **Not the whole publication unit.** The 2×2 table adjoint programs and their
  sixteen assertions, the Zot CEK stage, the text probe, the retained failed
  reflection control and the declared end-leaf representation bridge are not
  replayed here. `P` alone has no frozen counted oracle; its row is recorded,
  not matched.
* **The coordinate families are the declared four-slot application**, not
  arbitrary Iota syntax: the earlier text probe's `C(C(L))` result stays
  outside this scope, exactly as the origin records it.

The origin's own residuals are inherited with it: the carrier's `Omega` is
minus the frame's canonical `J`, `J` alone does not select a unique `C`, and
the carrier contraction symbol is not the Iota combinator.
