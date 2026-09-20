# Research 0208: accepting the renamed murphy unit — every recorded relation preserved

Date: 2026-09-20. Status: bounded local acceptance of a derived publication unit.
No `claims.toml` entry, no native admission, no reissue of the admitted unit's
digests. Direction: Mingli Yuan. Authored by DeepSeek Harness
(deepseek-v4-flash-vision-exp) through his authorized account proxy; account use
is not his authorship, review, endorsement or correctness guarantee.

## What was accepted

`murphy-iota-v0` at `mountain/adva` revision
`76c4aa8a108d3f49224d4b8b075066d6459d7949`, admitted there as
`murphy-iota-renaming-2026-09-20`: the five murphy programs with the Iota
combinator spelled `ι` instead of `i`, plus a manifest recording both digests
per program and the relations the rename must preserve. The admitted murphy
unit of 2026-09-19 is untouched, and nothing here reissues, retires or
supersedes its digests.

The acceptance run is
`experiments/iota-substrate/evidence/run-04-murphy-renamed/result.json`, under
the contract `experiments/iota-substrate/contract-murphy-renamed.json`, with the
renamed unit read at that revision through the origin root.

## Executed result: `IotaSubstrateChecked`

| Check | Observed |
| --- | --- |
| Published bytes vs this machine's derivation | **5 of 5 byte-identical** (`external_matched` 5/5, every pin re-hashed at the revision) |
| Frozen counted witnesses, renamed spelling | `PP` 1,808 contractions, `j` 822 / `S` 549 / `K` 437, peak 7,627, digest `8d0434eb…`; `C` 919 `dc74b1b6…`; `J` 831 `d40812c3…`; `N` 897 `66c6cc71…` — **4 of 4 frozen oracles matched** |
| `P` | 893 contractions recorded; the unit froze no counted oracle for `P` alone, so this row stays recorded, not matched |
| Renaming | **5 of 5 preserved**: same canonical term, same rule histogram, node peak, normal-form digest and declared test shape |
| Controls | 6 of 6, including `external-pins-hold` and `relations-agree-across-spellings` |

The same contract also runs the muprhy corpus relations for both spellings; the
retained `run-01` result reports 9 of 9 controls with the relation outcomes
below identical in the two spellings.

## The semantic relations, in both spellings

A sequence `[P1, P2]` means `P2 (P1 Z)`: applied to the declared four-slot
product from the inside out and observed at `out`. The slot order each side
produced is retained, so "holds" is a statement about the algebra, not about a
string.

| Relation | Left order | Right order | Verdict (documentary and renamed) |
| --- | --- | --- | --- |
| `C² = I` | `p q r s` | `p q r s` | holds |
| `J² = N` | `q p s r` | `q p s r` | holds |
| `C J C = N J` | `r s q p` | `r s q p` | holds |
| `N² = I` | `p q r s` | `p q r s` | holds |
| `J⁴ = I` | **Unknown** | `p q r s` | **exhausted the declared bounds** |
| `J² ≠ I` | `q p s r` | `p q r s` | differs as declared |
| `C ≠ J` | `p q s r` | `r s q p` | differs as declared |

**First finding: the rename is invisible to every relation the unit recorded.**
The two negative witnesses the original unit retained still separate, the four
directly checked laws still hold with identical slot orders, and the two
spellings agree on all fourteen relation outcomes. A change of spelling that
moved any of these would have failed the run.

**Second finding, recorded as a boundary rather than repaired.** `J⁴ = I` does
not finish on this profile's declared four-slot application: both spellings
exhaust the declared bounds, so the relation is declared `unknown` and the
exhaustion is the retained observation. It is *implied* by `J² = N` and
`N² = I`, both checked directly here, but that implication is not itself
executed and is not claimed. The unit's original check compared lambda normal
forms, a different reduction; this profile does not implement a lambda
normalizer, so the direct comparison is simply out of reach at these bounds.

## What this does not establish

- **Not a re-derivation of the murphy results.** Every frozen number is read
  from the received unit's own `result.json`; the Zot CEK stage, the 2×2 table
  adjoint programs and their sixteen assertions, the text probe and the declared
  end-leaf representation bridge are not replayed here.
- **Not an endorsement of the rename elsewhere.** The admitted unit and its
  transport receipts keep the documentary spelling; whether any other consumer
  should adopt `ι` is a separate decision with its own reissued digests.
- **No native admission.** No `ValueType`, `OperationSpec`, registry entry, IR
  version, `Seal` or `claims.toml` entry accompanies this acceptance.
- **Two machine implementations, no human review.** The relations are checked
  against the unit's own frozen evidence by this substrate; the agreement is
  between machine implementations and a machine-authored contract.

## Reproduction

```sh
# from the machine repository root; the origin is the adva checkout at 76c4aa8
experiments/iota-substrate/target/release/adva-iota-substrate \
  --contract experiments/iota-substrate/contract-murphy-renamed.json \
  --output /tmp/iota-substrate-acceptance-01 \
  --origin /path/to/adva
```

The fresh output directory receives `result.json` and the re-derived `renamed/`
copies that the external pins are compared against.
