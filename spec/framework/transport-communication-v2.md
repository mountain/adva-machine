# Transport and communication: framework vocabulary, version 2

Status: **adopted framework distinction**, 2026-09-16. English is primary.
Mingli Yuan distinguishes homogeneous traversal from the search for a shared
interpretation across heterogeneous interfaces. Original formulation by
ChatGPT (OpenAI), contributed under Unknown v0.3 through his authorized account
proxy; account use is not his review or endorsement.

This version refines the broad use of `communicate` in
[Communication v1](communication-v1.md). V1's contracts, event separation,
provenance, residuals and finite accounting remain required. Its exact bytes,
registry and existing receipts remain historical inputs. This successor changes
the vocabulary for new designs; it does not reinterpret an old acceptance or
register a new native operation.

## 1. The distinction is relative to an interface contract

| Term | Framework meaning | Completion evidence |
| --- | --- | --- |
| `transport` | Carry a bound presentation across interfaces that already share the relevant representation and interpretation contract, preserving the declared structure and dependencies | Actual arrival, integrity and preservation checks, receiver disposition, and the required durable records |
| `communicate` | Seek, test and revise a scoped common interpretation across interfaces whose relevant representations, observations or ways of checking do not yet coincide | Actual contributions, candidate correspondences, applicable checks on each side, retained disagreements and a scoped outcome; success is not presumed |

The current repository crossing carries disk files and directories under an
already specified documentary receiving profile. At that boundary its task is
`transport`. Path equality is unnecessary; the contract must specify how homes,
references, bytes and history resolve at the destination. Filesystem success
alone cannot establish that preservation.

Homogeneity concerns what this task needs to preserve, not only the physical
carrier. Two files can contain interpretations with different units, concepts
or observation rules. Carrying their bytes is transport; establishing how their
claims correspond can still require communication. Conversely, different
physical media can implement an already checked common representation.

`send`, `receive` and `acknowledge` name participant-local events in either
process. `verify` names a declared check. `accept` admits only a specified use
under its receiving contract. None of those names alone proves a shared meaning.
A communication attempt may use many transports and end in a counterexample,
refusal or `Unknown` without reaching an agreed interpretation.

## 2. A method for seeking a common interpretation

For a bounded task, each participating side declares its question, presentation,
observation methods, units, constraints and locally available checking evidence.
A common interpretation is a proposed relation between these readings, with
an explicit domain and an observable condition that could refute it.

One possible presentation uses a candidate comparison domain `K` and declared
relations from each side into `K`. This is a design form, not a universal
encoding theorem: the relations may be partial or many-valued, and `K` may be
unavailable. They need not be inverse functions. A third participant, a third
chart and a binding record are distinct roles; naming `K` supplies none of them.

The finite routine is:

1. Bind the starting question, each side's initial position, protected
   obligations, candidate scope, checker and resource account. Distinguish a
   proposed common anchor from correspondences already supported by evidence.
2. Obtain actual local observations. Transported statements about an observation
   retain their source and do not become independent observations by arrival.
3. Propose a correspondence and its comparison test. State what each reading
   retains, forgets, changes or cannot yet express; keep that loss as a residual.
4. Check it against the declared observations and required coverage on every
   participating side. Record matches, counterexamples, unavailable checks and
   disagreements separately. A matching digest only binds the tested proposal.
5. Return the bounded outcome. A refinement cites its predecessor and consumes
   its declared allowance. If a required comparison is still missing, retain
   `Unknown`; if observations refute it, retain the counterexample. Exhaustion
   cannot show that no common interpretation exists.
6. Admit only the continuation whose obligations have actually been discharged.
   Extending the domain or changing the interpretation requires a new checked
   boundary. Preserve the old readings and evidence of their limitations.

For example, [Research 0166](../../docs/research/0166-interpretation-obligation.md)
records correctly bound doubling and squaring interpretations that agree at 2
but differ at 3. Binding the description did not decide the behavioral question;
the finite comparison did. This is retained evidence for that scope, not a fresh
execution here or a general interpretation engine.

A compact structure card can carry the two readings, proposed correspondence,
preservation requirements, counterexample and reply request. The existing card
checker checks documentary shape; participants still perform the interpretation
work. The card does not manufacture agreement or human acceptance.

## 3. Three shares, a reserve, and a checked join

The discussion retained in
[0192](../../docs/research/0192-the-traversal-allocation-and-its-reserve.md) and
[0193](../../docs/research/0193-the-optimal-shares-and-the-price-of-a-level.md)
proposed three shares of `33/100` and a separate `1/100` for key/certificate
assembly and checking. These are exact resource fractions, not three estimates
of truth and an unexplained remainder. For an integer budget `B`, the recorded
allocation rule is

```text
side_allowance = floor(33 * B / 100)
reserve = B - 3 * side_allowance
```

The rule retains indivisible remainders in the reserve. Use exact integers or
rationals for allocation; a floating-point sum that rounds to one cannot
certify the account. Time, storage and checking work require their own units
and conversion rules. An allocation fraction is not probability mass, pressure
or physical energy.

The proposal is an initial allocation to test, not a universal optimum. The
retained optimal-allocation experiment uses stipulated symmetric side costs
and stipulated cumulative join costs. Its finite comparisons do not establish
that equal shares or a one-percent reserve are optimal for heterogeneous
participants. Real interpretation, key/certificate checking and recording costs
remain to be measured for a concrete receiving profile.

The reserve pays for a checked join, rather than making a join correct by its
size. A profile must state what `key` identifies or authorizes, what `cert`
attests, who checks it and what continuation that check permits. An authentic
key and intact byte chain cannot discharge an interpretation obligation on
their own. These names do not equate cryptographic signatures with native proof
certificates or mathematical truth.

On an unsuccessful join, the committed checkpoint head and admitted level do
not advance. Retain the attempted correspondence, refusal or missing evidence,
and the resources spent by both the sides and the reserve. Preserving side
allowances by reserving a separate pool does not make failure globally free.
Already observed external effects need their own recovery contract; checkpoint
non-advance is not physical reversal. A new level, renewed allowance or revised
anchor requires its own finite contract. A successful hash link does not prove
compression of the three-computation system or compute its Omega boundary.

## 4. Place in the unfinished free process

[Free process v0](free-process-v0.md) connects a common initial anchor,
three-sided pressure and permissible adjustment to a checked balance and
scoped continuation. The present distinction locates two different tasks within
it: transport carries available presentations; communication works on a missing
common interpretation. Neither completed transport nor agreement on an
interpretation alone establishes all of free's balance and release conditions.

Pressure must retain the question, measurements and admissible responses on
each side. A common scalar needs checked units and weights; disagreement cannot
be erased by averaging three numbers. The initial anchor remains challengeable.
For heterogeneous sides, the initial common contract may bind the inquiry while
the proposed semantic correspondences remain open.

The current A2 calibration has explicit, fixed chart correspondences on one
integer carrier. It tests anchored motion, balance and residual retention after
those correspondences are supplied. It does not seek an interpretation between
heterogeneous participants, exercise the three-share reserve policy, or
implement native `free`.

## 5. Compatibility and the next executable boundary

The existing command remains `adva communicate send/receive/acknowledge`, and
`adva-exchange run` retains its v1 request and result schemas. In the new
vocabulary their current documentary capability is transport. Keep the command
spelling, `CompletedDocumentaryExchange` result, contracts, binary/source pins
and receipts unchanged so historical consumers remain replayable. There is no
`adva transport` command or alias implemented by this specification.

New reports should distinguish the transport result, interpretation result,
balance result and permitted continuation. An old documentary acceptance
remains acceptance for its recorded catalog use. This clarification neither
withdraws that result nor promotes it to a new semantic judgment.

The next communication profile needs two concrete heterogeneous readings, one
bounded question and a candidate relation that each required side can test.
Include a successful finite comparison, equal bytes with incompatible meanings,
an ambiguous or missing relation, a counterexample, missing third-side evidence
when required, and exhausted checking reserve without checkpoint advance.
Derive any native identities and certificates through Rust. This specification
does not claim that this profile has been implemented.
