# Research 0205: the iota-lang recorded contract, replayed by the native substrate

Date: 2026-09-20. Status: bounded local record; a native case corpus executed,
plus two transcription findings about Research 0167's replay. No `claims.toml`
entry, no native admission, no language equivalence. Direction: Mingli Yuan.
Authored by DeepSeek Harness (deepseek-v4-flash-vision-exp) through his
authorized account proxy; account use is not his authorship, review, endorsement
or correctness guarantee.

## What was asked

`experiments/iota_lang/` has held the iota-lang test programs since Research
0167. The substrate added the previous day
([iota substrate v0](../spec/framework/iota-substrate-v0.md)) can now execute
Iota/S/K reduction natively, so the question is no longer "can iota-lang run"
but: **which of those recorded programs can be used as tests of this substrate,
which cannot, and what does the usable part establish?**

The discrimination matters more than the count: iota-lang's recorded material
mixes four different layers, and only one of them is a reduction contract.

## The recorded material, layer by layer

Checkout `/Users/mingli/Adva/iota-lang`, HEAD
`a1865e6d70d55a0d9457b33570e533463818d7d6`, MIT, read and never modified.

| Layer | Path | Verdict |
| --- | --- | --- |
| Reduction contract, 17 cases | `src/tests/java/iota/SKITest.java`, sha256 `c9b84b92…`, 17 `@Test` | **usable**, adopted as declared cases |
| Parser contract, 3 cases | `src/tests/java/iota/ParserTest.java` | **not usable here**: it tests a rekex parser over `<>`, `()` and `[]` with uppercase constants, a layer this substrate does not implement; `org.rekex.*` was never resolved (0167 §3) |
| Dual machine suite | `experiments/iota_lang/java2`, `DUALMACHINE.md` | **not usable here**: a dual-stack frame machine, not an Iota/SKI reducer; its cases test space/time frame behaviour |
| Language resources | `src/main/resources/iota/lang/iota.iota`, `ski.iota` | **not executable**: Clojure-shaped Adva-data-language text whose `[...]` list reading is exactly the unstated interface 0167 §3 and the murphy note call open; no reducer for that reading exists in the checkout |
| The Java machine itself | `src/main/java/iota/**` (20 files, 755 lines) | **not usable as an oracle**: it never compiled at any commit, and its recorded rules are arithmetically inconsistent (0167 §4) |

The two resource files are still informative as *definitions*: under a
right-nested reading of `[...]`, `ski.iota` declares I = ιι, K = ι(ι(ιι)) and
S = ι(ι(ι(ιι))), and `iota.iota` declares ι x = x S K. Those are the encodings
the substrate reduces, and cases `testIota2`, `testIota4` and `testIota5` below
check their behaviour — the files are evidence for the encodings, not
executable inputs.

## The executed corpus

`experiments/iota-substrate/contract-iota-lang.json` transcribes the 17 cases
faithfully from `SKITest.java` in a **separately declared case grammar**:
S-expressions whose tokens are `i` (the identity combinator), `k`, `s`, `ι`
(the Iota combinator) and lowercase opaque variables.

That declaration is load-bearing. In the murphy grammar already in use, the
character `i` is the **Iota** combinator; in this case grammar `i` is the
**identity** combinator and the Iota combinator is written `ι`. Both grammars
are declared, no term mixes them, and a control asserts that the same token has
two distinct readings rather than letting one silently win.

Result: **17 of 17 recorded expectations reproduced**, 57 contractions in
total, 0 mismatch. Every case prints exactly the recorded string.

| Case | Contractions | Recorded expectation |
| --- | ---: | --- |
| `testXY` | 0 | `(x y)` (a variable head is already a normal form) |
| `testI`, `testK`, `testS` | 1 each | `x`, `x`, `((x z) (y z))` |
| `testFalse` | 2 | `y` |
| `testReverse` | 5 | `(y x)` |
| `testKSKS`, `testKKKSKS` | 1, 2 | `(s s)` |
| `testSKK` | 2 | `(x y)` |
| `testII` … `testIIIIII` | 1 … 5 | `i` |
| `testIota2` | 5 | `x` |
| `testIota4` | 10 | `x` |
| `testIota5` | 12 | `((x z) (y z))` |

Four controls ran and passed: the FIPS 180-4 vectors, the declared
grammar collision, the altered-expectation falsifier, and variable inertness
(a case whose head is an opaque variable must contract zero times).

**First finding: the recorded contract is sound.** The seventeen expectations
are exactly what the declared Iota/S/K rules produce under leftmost-outermost
reduction with arity-based combinator rules. What 0167 measured was the state of
a machine, not a defect of the contract.

## Two transcription findings about the 0167 replay

The audit's frozen replay (`docs/research/0167-evidence/replay.jsonl`, sha256
`e1bb323b…`) is supplied to this run as a **comparison document only** — never
as an expected value. Comparing the two transcriptions case by case:

**Finding 2: seven of the seventeen replay terms are not the recorded terms.**
Ten agree; the seven that differ are `testII`, `testIII`, `testIIII`,
`testIIIII`, `testIIIIII`, `testIota4` and `testIota5`.

- The five identity cases: the recorded file builds five *distinct* terms —
  `(i i)`, `((i i) i)`, `((i i) (i i))`, `(((i i) (i i)) i)`,
  `(((i i) (i i)) (i i))` — while the replay uses `((ι ι) (ι ι))` for all five.
  The driver's own comment states that "the term is therefore ((i i) (i i)) for
  every one of the five"; the recorded file does not say that, and these five
  terms are distinct in it. The substitution also replaces the identity
  combinator with its Iota encoding, which changes the term.
- `testIota4` and `testIota5`: the replay applies the encoding to one argument
  (`(x y)`, `((x y) z)`) where the recorded file applies it to two and three
  separate arguments (`((ι (ι (ι ι))) x) y`,
  `((((ι (ι (ι (ι ι)))) x) y) z`). Both recorded forms are the ones the
  classical K and S encodings are expected to satisfy.

**Finding 3: five `expected` columns in the replay are form-strings, not
evaluation-strings.** `SKITest` asserts twice per case — once on the
unevaluated form (`iii.toString()`), once on the executed result
(`execute(iii).toString()`). For `testII` … `testIIIIII` the replay's
`expected` column carries the *form* assertion, while the other twelve cases
carry the *evaluation* assertion. The replay's own summary is unaffected (no
case produced a readable result in either mode), but the column does not mean
one thing across the seventeen rows.

**One consequence for a sentence of 0167.** Section 5 says: "what the machine
computes for `S K x y` is `(x y)`, the standard value, while the recorded test
asserts `y` — a mistake in the contract rather than a difference of rule
semantics." Under the declared rules `S K x y` reduces to `y` in two
contractions: `S K x y → (K y) (x y) → y`. The recorded expectation is the
standard value, and 0167's own transcript agrees on the point — its
`testFalse` row records the expected `y` as *reached* at round 1 before the
machine re-split it and dead-ended at `x|y`. The `(x y)` in that sentence is
what the reconnected machine computed, not the standard value. This note
records the correction; it does not rewrite 0167.

## What this does not establish

- **No language equivalence, either direction.** This compares a recorded
  *string contract* with one native reducer. It does not establish that the
  iota-lang machine agrees with the substrate, that the substrate implements the
  SKI or Iota calculus, or that the recorded strings are iota-lang's intended
  semantics.
- **No confluence or universality claim.** Bounded leftmost-outermost rewriting
  under declared limits is not a proof of the Church–Rosser property, of ι's
  universality, or of any halting property. Exhaustion is `Unknown`.
- **No native admission.** No `ValueType`, `OperationSpec`, registry entry, IR
  version, `Seal` or `claims.toml` entry accompanies this note; the corpus is
  research-local, and the substrate's `native_admission` stays `NotGranted`.
- **Nothing is imported.** The checkout is read at a pinned revision and
  digest; no iota-lang source is copied, vendored or relicensed, and the MIT
  licence of that repository is untouched. Only transcribed case strings and
  reported results enter this record.
- **The unused layers stay unused.** The parser cases, the DualMachine suite
  and the two resource files are not executed here, and this note makes no
  claim about whether they are correct for their own layers.

## Reproduction

```sh
# from the machine repository root
experiments/iota-substrate/target/release/adva-iota-substrate \
  --contract experiments/iota-substrate/contract-iota-lang.json \
  --output /tmp/iota-substrate-iota-lang-01
```

The output directory must not exist. The run reads the contract, the recorded
case strings inside it, and the independently supplied comparison document at
its pinned digest; it writes one `result.json`. The retained executed result is
[`experiments/iota-substrate/evidence/run-02-iota-lang/result.json`](../../experiments/iota-substrate/evidence/run-02-iota-lang/result.json).
