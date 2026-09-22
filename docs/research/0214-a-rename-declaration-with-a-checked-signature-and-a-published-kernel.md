# Research 0214: a rename declaration with a checked signature and a published kernel

Date: 2026-09-22. Status: research-local executable contract with a retained
result and residual; eleven declarations and nineteen controls, all holding.
No `claims.toml` entry, no admission, no `Seal`, no `OperationSpec`, no registry
entry and no IR version. Direction: Mingli Yuan. Authored by DeepSeek Harness
(deepseek-v4-flash-vision-exp) through his authorized account proxy; account use
is not his authorship, review, endorsement or correctness guarantee.

## Why

`rename` is a *Proposed* word in
[`adva` Research 0135](https://github.com/mountain/adva/blob/main/docs/research/0135-reunderstanding-resource-frames-and-fuel.md):
"change local names **while retaining their bindings**", a finite role/name
bijection, collisions rejected. The one rename this project has actually
executed and published — the `murphy` unit's `i -> iota` — is not an instance of
that definition. It is a **global, per-source, exclusive dialect switch**
(`IotaSpelling::{Documentary, Renamed}` in `experiments/iota-substrate`), and
`Renamed` *refuses* the old token rather than rebinding it. Its `scope` is a
prose string, `"the Iota combinator token only; '*' is unchanged"`, that nothing
verifies. Because it is a two-valued enum, two renames cannot be composed, so no
rename group exists to be non-commutative.

Two questions follow, and this note answers only these two:

> Can the fixed part of a rename be **checked** rather than asserted in prose?
> And can the class of renames that the recorded relation set **cannot tell
> apart** be **published** rather than left implicit?

## What was declared

The crate is [`experiments/rename-declaration/`](../../experiments/rename-declaration/README.md):
its own workspace root, like `experiments/iota-substrate`, so it cannot move the
machine's pinned `Cargo.lock` and `cargo clippy --workspace` does not reach it.
That also means **the repository CI does not build it**; the checks below were
executed from the crate directory and are recorded in its `result.json`.

| Element | Declared reading |
| --- | --- |
| signature | operator tokens with arities, atom tokens, ignorable tokens. A rename is admissible only if every token it moves *that the signature knows* keeps its arity and kind |
| fixed operators | operators the declaration claims not to move |
| level | the level the rename **acts** at, with that level's distinguishing structure |
| relation-set level | the level a relation set **measures** at; a differing one makes the witness a **cross-level** statement, reported rather than hidden |
| collision rule | a moved token may not land on an occupied token that is not itself moved; **occupied is per relation set**, so re-spelling a source collides with the source and re-spelling an equation collides with the letters the equation uses |
| renames | **partial bijections** of a declared name universe, so the enumerated set is the symmetric inverse monoid `I_X`, not `Sym(X)` |
| source | a path plus a digest, or an embedded short source plus a digest. **The digest is verified either way** |

The last row is why the murphy fixture does not embed the murphy bytes. It names
`knowledge/received/murphy-iota-machine-2026-09-20-v1/materials/murphy.iota` and
pins it with `sha256 da47f5cf…`, which is the `original_sha256` that
[`murphy-iota-v0/renaming.json`](https://github.com/mountain/adva/blob/main/murphy-iota-v0/renaming.json)
records for the admitted program `P`. The run therefore *reads* the received
bytes and proves it did, instead of asserting that a copy is faithful. SHA-256
is implemented in the crate so that it adds no dependency, and is checked
against the FIPS vectors including the million-`a` case.

## What was found

The murphy unit's five frozen coordinate laws present **D8** — the declared
algebra is the full closure of the two coordinate generators, and its
element-order profile comes out `{1: 1, 2: 5, 4: 2}`, which separates all five
groups of order 8. The same rename, judged against those same five laws, has a
different kernel under each reading:

| relation set | level | universe | `I_X` | admissible | visible | **kernel** | total? | kernel abelian? |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `spelling-fixed` | carrier → carrier | 6 | 13327 | 642 | 214 | **428** | no | **no** |
| `tietze` | carrier → **combinator** | 4 | 209 | 65 | 0 | **65** | **yes** | **no** |
| `words-relabelled` | carrier → **combinator** | 4 | 209 | 65 | 49 | **16** | no | yes |
| `denotation-moved` | carrier → **combinator** | 4 | 209 | 65 | 49 | **16** | no | yes |

### The `tietze` row is the finding

Under the reading where a rename relabels the equations **and** moves the
denotation coherently — which is the reading under which "this rename is
presentation-only" is true *by construction* — **visible = 0 and the kernel is
every admissible rename**, and that kernel is non-abelian. A verdict that cannot
fail certifies nothing, and here the blind class has a measured size and a
measured structure rather than being an unquantified worry. This is the
first-principles reason the machine's `relations-agree-across-spellings` control
cannot by itself license a rename, and why `renaming-is-not-vacuous` had to be
added beside it.

The other two readings are the opposite: their kernel is exactly the 16 renames
that move nothing at all. So a relation set's discriminating power is a property
of **how it is read**, not of which relation set it is, and the kernel witness is
what makes the difference visible.

### The level column is a second finding

`TRIADICITY-LEVEL-RULING.md` in the workspace ruled that triadicness belongs to
the index/carrier structure and not to the action layer. Each level is
distinguished by one structure, and that structure is what a rename must
respect:

| level | distinguished by | what a rename must respect |
| --- | --- | --- |
| `carrier` | the signature | every moved token is a token of the declared signature |
| `combinator` | a derivation: one primitive introduces the others | the primitive/derived partition |
| `action` | exactly one action does nothing | the identity action, unless the declaration says it is changing which action is trivial |

The combinator row is concrete here. `experiments/iota-substrate/src/lib.rs`
says `'j'` is the Iota combinator and `'S'`, `'K'` and `'I'` are the combinators
the Iota rule introduces — while the frozen rule histogram puts all four in
**one flat key space**. Moving the primitive onto a derived name is refused as
`PartitionNotPreserved`, the combinator-level analogue of an arity change. At
the action level, moving the action that does nothing is refused unless declared.

And the check immediately found a level confusion in **this crate's own
declaration of the published unit**: the murphy rename *acts* on the carrier
while its five coordinate laws are statements about *combinator* names
(`C`, `J`, `N`, `I`). All three law readings are therefore reported as
`CROSS carrier->combinator`, which is what the ruling says should be reported
rather than passed over.

### The other measured refusals

| Case | Verdict |
| --- | --- |
| renaming the operator token (`* -> i`) | **`KindChanged`** — a tokenwise substitution accepts it silently |
| a declaration contradicting its own fixed-operator set | refused |
| a target that is an incumbent source token and is not moved | refused as a collision |
| a declared no-op | refused |
| a three-cycle over the alphabet (`i -> j -> iota -> i`) | **expressible and accepted**; a single `{from, to}` cannot express it |
| a universe beyond the declared bound | **`Unknown`** with a stated reason, never a truncated count |
| a combinator 3-cycle over the derived names | accepted — the level admits it |
| the same rename plus the **frozen rule counts** as a relation set | **refused** — the counts separate `S`, `K`, `I`, so a level-legal rename is still not automatically presentation-only |

The last two rows are the point of keeping the level check and the relation-set
check separate: one level admitting a rename says nothing about whether the
recorded relations can see it.

## What is not claimed

- **Not an admission.** No `ValueType`, `OperationSpec`, registry entry, IR
  version, `Seal` or stable semantic type is created; native admission remains
  `NotGranted`. Nothing here decides whether `rename` should become a native
  operation or how it would be versioned.
- **The murphy counted witnesses, digests and traces are not re-derived.**
  Reproducing those needs this machine's Iota substrate
  (`experiments/iota-substrate`) and is out of scope. The relation sets here are
  the coordinate laws and the source spelling, not the full frozen evidence.
- **That the seven iota terms realize the five laws is not re-checked.** That was
  executed at `run-04-murphy-renamed`; this crate evaluates the laws in one
  declared realization and claims nothing about the terms.
- **Every kernel witness is relative.** It is a statement about one declared
  finite universe and one declared relation set, and says nothing about any
  relation set not declared.
- **The level check is not a level calculus.** It enforces one distinguishing
  structure per level; it does not derive the level of an arbitrary name and does
  not decide whether a cross-level measurement is legitimate — it reports that
  one occurred.
- **Not run by CI.** The crate is a separate workspace root, so the repository
  workflows neither build nor test it. The checks are executed from the crate
  directory and retained in `result.json`.
- **The exact kernel orders are reported, not pinned as controls.** The controls
  assert invariants that hold by construction — `kernel + visible = admissible`,
  and every rename that moves nothing is in the kernel — so a failing control
  means the checker is wrong rather than that a prediction was optimistic. The
  control machinery itself has unit tests that feed it wrong expectations and
  require it to fail.
- **Nothing here shows** that the murphy naming is the intended spelling of any
  other consumer.

## Retained errors

Kept because the mechanism is only worth trusting while its failures stay on the
record.

1. The first version of the admissibility probe asked "which relabellings still
   satisfy the law strings literally" and read 1 admissible out of 24. That was
   the wrong question: a rename acts on the **strings** too, and holding the
   strings fixed while permuting the denotations answers something else. The
   corrected reading is 24 of 24, and the mistake is what produced the Tietze
   finding above.
2. Three controls were written from expectation and all three failed. The
   failures exposed two real defects: the declared algebra listed only the four
   named generators, so its order profile `{1: 1, 2: 2, 4: 1}` was not a group
   invariant at all while a comment claimed it was; and word-equation collisions
   must be judged against the equation's own letters rather than the source's.
   The second defect is where the per-relation-set collision rule comes from.
3. `violation_contains` originally searched only signature violations, so the new
   level violations were invisible to every control — a missing channel in the
   control machinery itself, found by a failing fixture.
4. One fixture declared a five-name universe with a bound of four and so reported
   `Unknown` where a verdict was expected. An off-by-one, caught by a control.
5. The first `level` admissibility helper mixed two semantics in one `&&`/`||`
   expression and was rewritten as two named functions.
6. A patch script asserted four occurrences where there were three; the assertion
   stopped the script before it wrote, so the fixtures were **not** regenerated
   while the run appeared to have been. The assertion is what caught it.
