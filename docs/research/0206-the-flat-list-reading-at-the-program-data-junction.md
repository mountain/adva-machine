# Research 0206: the flat-list reading at the program/data junction

Date: 2026-09-20. Status: bounded local record; one declared reading decided on
four declared forms. No `claims.toml` entry, no native admission, no language
equivalence. Direction: Mingli Yuan. Authored by DeepSeek Harness
(deepseek-v4-flash-vision-exp) through his authorized account proxy; account use
is not his authorship, review, endorsement or correctness guarantee.

## What was asked

The murphy publication unit names the next object as "a representation that
carries application, endpoint order, pairing and observation from the
right-expanded program/left-expanded data interface", and its Chinese companion
asks for a representation map at that junction that transports application,
keeps the interface order, and keeps pairing consistent under a change of basis.
The iota-lang resources are the only concrete left-expanded data in reach:

```clojure
;; ski.iota
(defn I [x] ([Iota Iota] x))
(defn K [x y] ([Iota Iota Iota Iota] x y))
(defn S [x y z] ([Iota Iota Iota Iota Iota] x y z))
;; iota.iota
(defn Iota [x] (x [Iota Iota Iota Iota Iota] [Iota Iota Iota Iota]))
```

These files are definitions, not executable programs: no reducer for the `[...]`
reading exists in that checkout (Research 0205). So the bounded question is:

> Which nesting reading of a flat list `[t1 … tn]` makes those declarations
> true, and from how many elements is the reading even decided?

## The declared junction

Two readings are declared, on one notation:

| Reading | `[t1 t2 t3]` becomes |
| --- | --- |
| left-nested | `((t1 t2) t3)` |
| right-nested | `(t1 (t2 t3))` |

Parentheses stay ordinary left-associated application, so a form can mix a data
list with a program application and the junction is explicit at every bracket.
The rules, reduction order, counting and bounds are the ones already declared
for the murphy corpus: `j a -> a S K`, `I a -> a`, `K a b -> a`,
`S x y z -> x z (y z)`, leftmost-outermost.

## Executed result

`experiments/iota-substrate/contract-list-reading.json`, seven declared cases,
54 contractions, three controls passed:

| Case | Reading | Form | Expected | Observed | Verdict |
| --- | --- | --- | --- | --- | --- |
| `R-I` | right-nested | `([ι ι] x)` | `x` | `x` | holds |
| `R-K` | right-nested | `(([ι ι ι ι] x) y)` | `x` | `x` | holds |
| `R-S` | right-nested | `((([ι ι ι ι ι] x) y) z)` | `((x z) (y z))` | `((x z) (y z))` | holds |
| `R-iota-rule` | right-nested | `(ι x)` | `((x s) k)` | `((x s) k)` | holds |
| `L-I` | left-nested | `([ι ι] x)` | `x` | `x` | holds |
| `L-K` | left-nested | `(([ι ι ι ι] x) y)` | `x` | `(x y)` | fails as declared |
| `L-S` | left-nested | `((([ι ι ι ι ι] x) y) z)` | `((x z) (y z))` | `((((x s) k) y) z)` | fails as declared |

**First finding: the right-nested reading is the one that transports
application.** Under it, `ski.iota`'s three lists reproduce the identity, K and
S behaviours on their declared arities, and `iota.iota`'s rule reaches `x S K`
in one contraction. The left-nested reading reproduces none of the K and S
declarations.

**Second finding: the reading is not decided below three elements.** A
two-element list is `(t1 t2)` under both readings, so `L-I` holds as well as
`R-I`: the identity declaration is compatible with either reading and cannot
discriminate. The two controls measure exactly this — the readings coincide at
two elements, first differ at three, and differ at three, four and five.

So the declarations themselves are what pin the reading: they are only true
together, and only under right-nesting. That is the finite content of the
"pairing" half of the junction question at this size: the head is the first
element in both readings, and what a reading fixes is where the tail is paired.

## What this does not establish

- **Not the representation map.** This decides one reading of one bracket
  notation on four forms. It does not define a decoder, an encoder, an observer,
  or a correspondence between the bracket notation and the Adva data language,
  and it does not transport observation.
- **No general program conjugation and no left/right program duality.** That a
  list reading is decided here says nothing about conjugating a program, about
  `C(C(L))`, or about the end-leaf interface the murphy note keeps open.
- **No equivalence claim about iota-lang.** The two resource files are read as
  declarations at pinned digests; nothing here says they are that repository's
  intended semantics, and no iota-lang source is copied, vendored or relicensed.
- **One observation is deliberately not read further.** The left-nested
  four-element list applied to two opaque variables returns `(x y)`, the same
  string Research 0167's reconnected machine produced for `S K x y`. The
  coincidence is recorded because it is visible in both transcripts; no
  mechanism is claimed to connect them, and no defect is inferred on either
  side from it.
- **No native admission.** The reading corpus is research-local; no
  `ValueType`, `OperationSpec`, registry entry, IR version, `Seal` or
  `claims.toml` entry accompanies this note.

## Reproduction

```sh
# from the machine repository root
experiments/iota-substrate/target/release/adva-iota-substrate \
  --contract experiments/iota-substrate/contract-list-reading.json \
  --output /tmp/iota-substrate-list-reading-01
```

The output directory must not exist. The run reads the contract, whose forms
and pins are declared inside it; it writes one `result.json`. The retained
executed result is
[`experiments/iota-substrate/evidence/run-03-list-reading/result.json`](../../experiments/iota-substrate/evidence/run-03-list-reading/result.json).
