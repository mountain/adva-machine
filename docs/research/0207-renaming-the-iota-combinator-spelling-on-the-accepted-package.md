# Research 0207: renaming the Iota combinator's spelling on the accepted package

Date: 2026-09-20. Status: bounded local record; one declared renaming executed
and checked. No `claims.toml` entry, no native admission, no new reception.
Direction: Mingli Yuan. Authored by DeepSeek Harness
(deepseek-v4-flash-vision-exp) through his authorized account proxy; account use
is not his authorship, review, endorsement or correctness guarantee.

## What was asked

On the accepted-package side, spell the Iota combinator `ι` instead of `i`,
because `i` means something else in mathematics.

The objection is not stylistic, and this repository already carries three
different meanings for that one letter:

| Where | `i` means |
| --- | --- |
| Mathematics | the imaginary unit |
| [Iota interpretation frame](../spec/framework/iota-frame-v1.md) | the complex structure `J`, "a representation structure, not a source combinator or native scalar" |
| iota-lang case corpus ([Research 0205](0205-iota-lang-recorded-contract-replayed-by-the-native-substrate.md)) | the **identity** combinator, with the Iota combinator written `ι` |
| murphy documentary source | the **Iota** combinator |

A source spelling that flips meaning between two grammars in the same substrate
is exactly the conflation this project's discipline forbids, so the rename is
also a de-collision.

## What was done

The received bytes are **not** rewritten. The receipt pins all eight received
materials by SHA-256 and BLAKE3, and the repeated-delivery recheck compares the
received directory against that exact inventory, so a rewrite would destroy the
record it is meant to serve.

Instead the renaming is **declared and checked**, and materialized as a derived
copy:

```json
"renaming": {"from": "i", "to": "ι", "output": "renamed", ...},
"renamings": [{"label": "PP", "program": "materials/PP.iota", "kind": "iota", ...}, ...]
```

For each of the five received programs the run parses both spellings, reduces
both under the same declared rules and bounds, and requires:

- the same canonical term digest for the two spellings;
- the same rule histogram, node peak and normal-form digest;
- the same declared test shape (a coordinate program is checked on its
  four-slot application, not bare);
- where the unit froze an oracle, the same frozen contractions, rule
  histogram, node peak and digest.

The renamed copies are written to `renamed/` under the run output and retained
as evidence.

## Executed result

`experiments/iota-substrate/evidence/run-01/`, `IotaSubstrateChecked`, eight
controls passing:

| Program | Characters | Bytes | Witness (contractions) | Frozen oracle | Verdict |
| --- | --- | --- | --- | --- | --- |
| `P` | 823 → 823 | 824 → 1236 | 893 | none retained for `P` alone | preserved |
| `PP` | 1647 → 1647 | 1648 → 2472 | 1,808 | matched (`8d0434eb…`) | preserved |
| `C` | 743 → 743 | 744 → 1116 | 919 | matched (`dc74b1b6…`) | preserved |
| `J` | 671 → 671 | 672 → 1008 | 831 | matched (`d40812c3…`) | preserved |
| `N` | 725 → 725 | 726 → 1089 | 897 | matched (`66c6cc71…`) | preserved |

Two controls carry the renaming:

- `renaming-refuses-legacy-token` — under the renamed spelling a source
  containing `i` is **refused**, while the documentary spelling still reads
  `i` as the Iota combinator. A rename that left both spellings silently
  accepted everywhere would not have separated anything.
- `renaming-is-not-vacuous` — for every program the character count is
  unchanged, the byte count differs, and the file digest differs. The rename is
  a real substitution, not a copy.

Character counts are unchanged because `ι` is one Unicode scalar value where
`i` is one too; byte counts change because `ι` is two bytes in UTF-8. Both
numbers are retained rather than one being called "the size".

## What this does not establish

- **Not a second reception.** The renamed copy has no receipt, no catalog entry
  and no receiving record of its own. It is an artifact of this run, derived
  from the received bytes, and the documentary spelling remains the one the
  receipt pins.
- **Not a change to the origin.** Nothing in `mountain/adva` is renamed, and the
  murphy publication unit still spells its programs `i`. Renaming the published
  unit would be a separate, deliberate change in that repository, with its own
  publication record and its own broken digests to reissue.
- **Not a claim about the iota-lang resources.** `iota.iota` and `ski.iota`
  already write `Iota`/`Iota`-like tokens in the Adva data language; this note
  says nothing about their spelling, and Research 0206's reading decision is
  untouched.
- **Not an admission.** No `ValueType`, `OperationSpec`, registry entry, IR
  version, `Seal` or `claims.toml` entry accompanies the rename; the substrate's
  `native_admission` stays `NotGranted`.
- **The refused spelling is refused only in the renamed grammar.** Under the
  documentary spelling `i` still denotes the Iota combinator, because the
  received bytes must keep parsing exactly as they were received.

## Reproduction

```sh
# from the machine repository root
experiments/iota-substrate/target/release/adva-iota-substrate \
  --contract experiments/iota-substrate/contract.json \
  --output /tmp/iota-substrate-renamed-01 \
  --origin /path/to/adva/experiments/murphy
```

The fresh output directory receives `result.json` and `renamed/`, the `ι`
spelling of the five programs.
