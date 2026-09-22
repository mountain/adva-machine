# A rename declaration with a checked signature and a published kernel witness

Status: **research-local executable crate**, 2026-09-22. It is not part of
Adva's stable semantic API. It adds no `ValueType`, no `OperationSpec`, no
registry entry, no IR version, no `Seal` and no stable semantic type; native
admission is `NotGranted`.

DeepSeek Harness (deepseek-v4-flash-vision-exp) authored this crate and its
checks under Unknown v0.3 through Mingli Yuan's authorized account proxy;
account use is not his authorship, review, endorsement or correctness
guarantee. Nobody vouches for the result; the executed check and the retained
residual are the authority.

This crate is deliberately **outside** every Adva repository checkout. Moving it
into `adva-machine/experiments/` is a file move, not a rewrite, and is left to
the project's review process.

## The question

`rename` is a *Proposed* word in `adva/docs/research/0135-…`: "change local names
while retaining their bindings", a finite bijection, collisions rejected. The
one rename that has actually been executed and published — the murphy unit's
`i -> iota` — is not an instance of that: it is a **global, per-source,
exclusive dialect switch**, and it is a two-valued enum, so there is no
composition and no rename group at all. Its `scope` is a prose string
(`"the Iota combinator token only; '*' is unchanged"`) that nothing verifies.

Two questions follow, and this crate answers only these two:

> Can the fixed part of a rename be **checked** rather than asserted in prose?
> And can the class of renames that the recorded relation set **cannot tell
> apart** be **published** rather than left implicit?

## What is declared, and where it comes from

| Element | Declared reading |
| --- | --- |
| signature | operator tokens with arities, plus atom tokens, plus ignorable tokens. A rename is admissible only if every token it moves *that the signature knows* keeps its arity and kind |
| fixed operators | operators the declaration claims not to move; a declaration that moves one is refused |
| **level** | the level the rename *acts* at, with that level's distinguishing structure. Not a prose string: it is checked |
| relation-set level | the level a relation set *measures* at. A relation set that declares none measures at the acting level; one that declares another makes the witness a **cross-level** statement, which the run reports rather than hides |
| collision rule | a moved token may not land on an occupied token that is not itself moved. **Occupied is per relation set**: re-spelling a source collides with the source, re-spelling an equation collides with the letters the equation uses, re-spelling a label collides with the labels. Tietze's generator replacement is legal only for a fresh symbol, and that freshness is exactly this set |
| rename universe | each relation set declares its own finite name universe, because "how much can this relation set see" is meaningless without one |
| renames | **partial bijections** of that universe. `i -> iota` is injective only because `iota` lies outside the source alphabet, so the algebraic home is the symmetric inverse monoid `I_X`, not `Sym(X)`, and the kernel of a monoid homomorphism is a congruence, not a normal subgroup |
| relation sets | `spelling_fixed` (the source spelling is unchanged), `word_equations` under one of three readings, and `label_counts_fixed` (every declared label keeps its declared count) |
| source | either an embedded short fixture source, or a path with a digest. **The digest is verified in both cases**, so "these are the bytes the declaration is about" is a check rather than a claim: for a path it is the digest the admitted unit records, and for an embedded source it pins the fixture bytes against later drift. The murphy fixture uses the path form, so the run reads the received bytes instead of a copy of them |
| readings | `tietze` (relabel the words **and** move the denotation coherently), `words_relabelled` (relabel the words, keep the denotation), `denotation_moved` (keep the words, move the denotation) |

The three readings are not variants of one idea. `tietze` is the reading under
which "this rename is presentation-only" is **true by construction**, so its
verdict can never fail; the other two read the rename as a change of meaning.

### The three levels, and what makes each one checkable

`TRIADICITY-LEVEL-RULING.md` ruled that triadicness belongs to the index/carrier
structure and not to the action layer. Each level is distinguished by one
structure, and that structure is what a rename must respect:

| level | distinguished by | what a rename must respect |
| --- | --- | --- |
| `carrier` | the signature | every moved token is a token of the declared signature |
| `combinator` | a derivation: one primitive introduces the others | the primitive/derived partition |
| `action` | exactly one action does nothing | the identity action, unless the declaration says it is changing which action is trivial |

The combinator row is the one the murphy evidence makes concrete. The
substrate's own comment says `j` is the Iota combinator and `S`, `K` and `I` are
the combinators the Iota rule introduces — while the frozen rule histogram puts
all four in **one flat key space**. Renaming the primitive onto a derived name
is the combinator-level analogue of an arity change, and it is refused.

## Run

The crate is deliberately its own workspace root, like
`experiments/iota-substrate`: it is not a member of the root workspace, so it
cannot move the machine's pinned `Cargo.lock` and `cargo clippy --workspace`
does not reach it. That also means the repository CI does not build it — the
checks below are executed from the crate directory.

```bash
cd experiments/rename-declaration
cargo test
cargo run --quiet -- --contract fixtures/contract.json --out result.json --root ../..
python3 make_fixtures.py ../..
```

`--root` is the repository root that a declaration's `source.path` resolves
against. `fixtures/` is generated by `make_fixtures.py`, which reads the murphy
bytes from `knowledge/received/murphy-iota-machine-2026-09-20-v1/materials/`,
verifies them against the digest recorded in the admitted unit's
`renaming.json`, and asserts that the declared algebra's element-order profile
is `{1:1, 2:5, 4:2}` before writing anything.

Exit status is non-zero if any declared control does not hold; the failing
control is retained in `result.json` with its reason.

## What it found

Eleven declarations, nineteen controls, all holding; twenty-eight unit tests.
Against the murphy unit's five coordinate laws — evaluated in the group they
present, **D8**, verified independently in `naming-probe-01/probe.py` — the same
rename has a different kernel under each reading:

| relation set | level | universe | monoid `I_X` | admissible | visible | **kernel** | total? | kernel abelian? |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| `spelling-fixed` | carrier → carrier | 6 | 13327 | 642 | 214 | **428** | no | **no** |
| `tietze` | carrier → **combinator** | 4 | 209 | 65 | 0 | **65** | **yes** | **no** |
| `words-relabelled` | carrier → **combinator** | 4 | 209 | 65 | 49 | **16** | no | yes |
| `denotation-moved` | carrier → **combinator** | 4 | 209 | 65 | 49 | **16** | no | yes |

The `tietze` row is the one that matters: **visible = 0, kernel = every
admissible rename, and that kernel is non-abelian.** The reading under which a
rename is "presentation-only" is blind to the entire rename class. That is not a
defect of the checker; it is why `relations-agree-across-spellings` cannot by
itself license a rename, and why the repository needed the separate
`renaming-is-not-vacuous` control. This crate measures that from first
principles instead of arguing it.

The other two readings are *maximally discriminating*: their kernel is exactly
the 16 renames that move nothing at all. So the honest summary is that a
relation set's discriminating power is a property of **how it is read**, and the
kernel witness is what makes the difference visible.

The level column is itself a finding. The murphy rename **acts** on the carrier
— it re-spells a source token — while its five coordinate laws are statements
about **combinator** names (`C`, `J`, `N`, `I`). Every one of those three
witnesses is therefore a **cross-level** measurement, and the run says so
instead of letting it pass silently. That is precisely the level confusion the
analysis predicted, found in the published unit's own declaration.

Also checked:

- a rename that moves the operator token (`* -> i`) is refused on **arity**
  (`KindChanged`), where a tokenwise substitution would accept it silently;
- a declaration that contradicts its own fixed-operator set is refused;
- a rename whose target is an incumbent source token is refused;
- a declared no-op is refused;
- a three-cycle over the alphabet (`i -> j -> iota -> i`) is **expressible and
  accepted** — a single `{from, to}` cannot express it at all;
- a universe beyond the declared bound yields **`Unknown`** with a stated
  reason, never a truncated count;
- at combinator level, permuting the three derived names is **accepted**, while
  moving the primitive `j` onto the derived `S` is **refused**
  (`PartitionNotPreserved`);
- the same accepted combinator rename is **refused** once the frozen rule
  histogram is declared as a relation set, because the counts separate `S`, `K`
  and `I`: a level-legal rename is still not automatically presentation-only;
- at action level, moving the action that does nothing is **refused**
  (`IdentityActionMoved`) unless the declaration says it is changing which
  action is trivial;
- the invariants `kernel + visible = admissible` and "every rename that moves
  nothing is in the kernel" hold for every relation set;
- the kernel contains no rename that touches the source under `spelling-fixed`,
  which is an invariant rather than a coincidence.

## What this is not

- **Not an admission.** No `ValueType`, `OperationSpec`, registry entry, IR
  version or `Seal` is created; native admission remains `NotGranted`.
- **Not a re-derivation of the murphy evidence.** The counted witnesses,
  digests and traces need the machine substrate
  (`adva-machine/experiments/iota-substrate`) and are out of scope. The one
  place frozen numbers are used is the `label_counts_fixed` fixture, and its
  counts are quoted from the published evidence for program C rather than
  recomputed here.
- **Not re-checked:** that the seven iota terms realize the five laws. That was
  executed at `run-04-murphy-renamed`; this crate evaluates the laws in one
  declared realization and claims nothing about the terms.
- **Not a claim about any undeclared relation set.** Every kernel witness is a
  statement about one declared finite universe and one declared relation set.
- **Not a claim about `adva`'s stable language.** It does not decide whether
  `rename` should become native, nor what its IR versioning would be.
- **Not a full level calculus.** The level check enforces one distinguishing
  structure per level. It does not derive the levels of arbitrary names, and it
  does not decide whether a cross-level measurement is legitimate — it only
  reports that one occurred.
- **The exact kernel orders are reported, not pinned as controls.** The controls
  assert invariants that hold by construction, so a failing control means the
  checker is wrong rather than that a prediction was optimistic.
