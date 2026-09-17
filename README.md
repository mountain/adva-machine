# Adva-machine

This repository brings together Adva's specification entry points, Rust
and Python toolchains, and bounded tools written in Adva. It continues the full
history of `mountain/adva` at `bbfaf3a`. The original GitHub repository is intended
to evolve toward knowledge; the eventual organization of `adva-library` remains
open.

The [iota frame profile](spec/framework/iota-frame-v1.md) jointly carries the
minimal iota process, complex structure and exponential readings. Its finite
checks retain metric, observer, clock and process residuals across three charts.

English is the primary documentation language for international collaboration.
Other language versions provide supporting translations or summaries; see the
[documentation policy](docs/DEVELOPMENT.md#documentation-language).

Start with the [toolchain commands](toolchain/README.md),
[specification index](spec/README.md), [Rust entry](adva-rust/README.md),
[Python entry](adva-python/README.md) and
[repository direction](docs/TOOLCHAIN_DIRECTION.md). Existing source paths,
versioned semantic boundaries and historical evidence are preserved during this
integration. It is published at
[`mountain/adva-machine`](https://github.com/mountain/adva-machine).
The knowledge repository is introducing a
[fixed-version consumer route](https://github.com/mountain/adva/blob/main/docs/KNOWLEDGE_MACHINE_BOUNDARY.md)
that preserves input, execution and historical evidence dependencies.

The [formal framework vocabulary v2](spec/framework/transport-communication-v2.md)
distinguishes `transport` under a shared representation contract from
`communicate`, which seeks a common interpretation across heterogeneous
interfaces. General native communication remains open.
The [first bounded Rust exchange profile](spec/framework/documentary-exchange-v1.md)
provides `adva communicate send`, `receive` and `acknowledge` for an independently
reviewed documentary library entry, retaining its source home and obligations.
The [compact structure exchange routine](exchange_routine/README.md) adds a
short discussion card, visible revision differences and one command to run
the existing bounded Rust exchange with its evidence retained.
Its documentary capability is transport in the refined vocabulary; the existing
command names, contracts and receipts retain their versions.
The [free process definition](spec/framework/free-process-v0.md) and
[finite calibration](experiments/triadic_free/README.md) connect initial
anchoring, pressure, adjustment and balance while keeping native free and
heterogeneous interpretation open.
The [two triadic readings](spec/framework/triadic-context-v0.md) retain both
participant A / participant B / their shared object and the library's
Surface / Knowledge / Substrate organization. Their correspondence must be
stated for the task; agreement remains answerable to object-related evidence.
The [conditional theory of free](spec/framework/triadic-free-theory-v0.md)
gives finite interpretation, balance and continuation criteria with proofs,
counterexamples and exact calibration evidence.

```sh
.venv/bin/python adva-machine doctor
.venv/bin/python adva-machine capabilities
.venv/bin/python adva-machine conform --output target/machine-conformance
```

The following inherited research introduction remains context for the machine
and its original knowledge-oriented repository.

**How can a finite observer construct, check, and extend arithmetic knowledge?**

[中文入口](README.zh-CN.md) · [Run an example](#run-an-example) ·
[Bring a stalled problem](#bring-a-stalled-problem) · [Development](docs/DEVELOPMENT.md)

Adva investigates this question through typed programs, explicit construction
histories, bounded experiments, and reusable witnesses. The practical aim is to
make a difficult problem easier to continue: establish what a particular
observation tells us, preserve what it leaves undecided, and find the next
construction or observation that could make a difference.

The implementation includes a Rust Lisp engine, a separately versioned bounded
data language, a library of recorded constructions, and a substantial research
record. **Pre-alpha research software.** [Unknown v0.3](Unknown-LICENSE-v0.3.md)
dedicates the first-party work to the public domain, with a voluntary philosophical
statement. See [LICENSE](LICENSE) and [licensing scope](LICENSING.md).

## Start with one observation

Suppose two explanations of a program are `f(x) = 2x` and `g(x) = x²`.

| Observation | `f(x)` | `g(x)` | What it establishes |
|---|---:|---:|---|
| Evaluate at `x = 2` | 4 | 4 | Both explanations fit this observation. |
| Evaluate at `x = 3` | 6 | 9 | This observation distinguishes them. |

Repeating the first observation does not resolve the ambiguity. A different
observation does. Even agreement on many inputs would need a justification
before becoming a claim about all inputs. Adva's
[interpretation experiment](docs/research/0166-interpretation-obligation.md)
records this distinction with explicit questions, interpretations, and checks.

Finite observation can also support a proof. For example, two polynomials over
the rationals, each of degree at most two, are identical if they agree at three
distinct rational points: their difference has degree at most two and cannot
have three distinct roots unless it is zero. The **degree bound and the root
argument** make those observations sufficient. Three arbitrary tests do not.
The [finite-example research](docs/research/0183-zhang-finite-example-verification.md)
develops this kind of boundary between examples and proof.

Adva asks how to retain that whole relationship: the original question, the
construction, the observer, the assumptions, the witness, and the unresolved
remainder. A result can then be reused with its conditions attached.

## What “finite observer” means here

An observer has a particular interface, a language of questions, and finite
resources. It can distinguish some constructions and leave others unresolved.
The research goal is to make these limits operational, including the possibility
of changing the observer or extending its language.

Four distinctions guide the work:

- **An observation is not the whole construction.** Equal output values do not
  identify two programs, their sources, or their histories. The native core
  records explicit copying and distinct occurrences.
- **An arithmetic check needs an interpretation.** In a declared field,
  equality can be tested by `A - B = 0`, or by `A / B = 1` when `B ≠ 0`.
  The domain and the correspondence to the original problem still need to be
  justified. The proposed
  [arithmetic-universality and arithmetic-truth vocabulary](docs/research/0123-arithmetic-universality-and-hypothesized-truth.md)
  remains a research hypothesis.
- **A finite success has a scope.** A complete finite check, together with an
  applicable theorem, may justify a larger conclusion. Running out of search
  time alone leaves the question `Unknown`.
- **A useful next step changes what can be established.** A new witness,
  counterexample, justified interpretation, or reusable construction can do
  this. Another run or another participant does not establish learning by itself.

The larger programme connects program geometry, arithmetic, learning, and
language formation. Its [philosophical questions](docs/philosophy/README.md),
[ontology](ontology/README.md), and [research agenda](docs/RESEARCH_ENGINEERING_AGENDA.md)
explain that ambition. They are also part of the project; the runtime is one
place where those ideas must meet concrete checks.

## What you can inspect today

| Layer | Existing work | Boundary |
|---|---|---|
| Native program core | Typed finite Lisp programs; explicit sources, occurrences and history; checked diagrams, graft traces and process slices; evaluation and forward differentiation | Finite, binder-free, linear PSC0 scope. Numerical evaluation uses floating point; structural certificates are not numerical error bounds. |
| Research data language | An arithmetic interpreter written in Adva instructions, executed by Rust; exact checked `i64` arithmetic, bounded control, suspension and replay | A separate research profile. Overflow rejects. This example interprets arithmetic trees, not its own full instruction language. |
| Research library and experiments | Reusable witnesses, observer comparisons, closure and transport checks, retained failures and counterexamples | Each result has its own assumptions, checker, budget and residual. External checks do not confer native semantic authority. |
| Open programme | Observer-conditioned specialization, richer language formation, arithmetic universality and geometric representations | Construction targets and hypotheses, with dependencies in the agenda. |

The [claim registry](docs/claims.toml) records scoped claims and their evidence;
the [semantic scope](docs/SEMANTIC_SCOPE.md) defines the native boundary. Rust is
the authority for native semantic identities and judgments. Python supplies
adapters and external research tools. Decoding JSON alone never authorizes a
semantic object.

## Run an example

Clone with the library submodule:

```sh
git clone --recurse-submodules https://github.com/mountain/adva-machine.git
cd adva-machine
```

### An interpreter that retains its execution

With a Rust toolchain installed, run these commands from the repository root
in a POSIX shell:

```sh
cargo build --locked -p adva-witness --bin adva
adva_run_dir="$(mktemp -d)"
target/debug/adva data-run programs/bounded-interpreter/interpreter.adva \
  --input programs/bounded-interpreter/input.json \
  --fuel 2048 --quantum 2048 --output "$adva_run_dir/result.adva"
```

The supplied input is `2 + (3 * 4)`. The expected status is `Returned`, with
integer result `14` after `134` instruction steps. Open the output to inspect
the program, input, execution trace, final state and fuel accounting. Outputs
must use fresh paths.

Then try the [suspend-and-resume example](programs/bounded-interpreter/README.md):
stop after 17 steps, recheck the prefix, and continue without resetting the
original lifetime fuel. Replay work is recorded separately. The
[research report](docs/research/bounded-native-data-interpreter.md) explains
what the retained calibration establishes and what remains open.

The newer [compilation calibration](docs/research/futamura-projections-in-adva-terms.md)
also compares interpretation with emitted three-instruction constant programs for
129 fully static arithmetic trees. Its recorded machine-step cost is higher for
one use and lower after two uses, including compilation. This is a finite reuse
result, with host-side program loading; it does not establish a general
specializer or a wall-clock speedup.

### A compiler that compiles itself

The [structured self compiler](experiments/bounded_self_compiler/README.md)
compiles its own Adva source through two native generations with equal target
bytes, independent block checks and execution controls. It uses the separately
bounded `adva data-run-v1` research profile. The
[report](docs/research/bounded-self-compiler-and-futamura.md) connects this bootstrap
to the existing static and dynamic first-projection calibrations and states the
remaining interpreter, `mix` and self-application contracts. This establishes
self compilation for the declared subset.

The subsequent [bounded mix experiment](experiments/bounded_mix/README.md)
implements input binding in ordinary Adva instructions and checks actual emitted
code across the three projection equations. Its separate `data-run-v2` research
profile preserves v1 and raises only instruction and node-arity capacities.
This conservative baseline retains interpreter execution; a general optimizing
specializer, interpreter elimination and unrestricted projection claims remain
open. See the [results and limits](docs/research/bounded-mix-and-three-projections.md).

### A collaboration record, without building Rust

With Python 3.11 or later:

```sh
python3 experiments/bounded_observation_exchange/check_exchange_chain.py
```

Expected result: `DisclosedByteChainChecked`, covering five recorded exchanges
and four controls that reject an old reply as an answer to a new question.
The checker compares disclosed fields and their byte bindings. It explicitly
leaves source authenticity unverified and semantic acceptance withheld. This
is a small, runnable example of retaining a question across handoffs; it does
not establish the truth of the participants' statements. See the
[exchange experiment](experiments/bounded_observation_exchange/README.md).

## Bring a stalled problem

You can start with one failed attempt, without learning the whole mathematical
framework. Keep the original problem and bring:

1. The result you need and the observations that would count as success.
2. A small reproducible attempt, with its inputs, assumptions and resource limit.
3. What passed, what failed, and the exact part that is still unresolved.
4. One proposed next step: a different observation, a counterexample, a stronger
   invariant, or a construction someone else could check.

For a coding challenge, this might mean finding a test that separates two
plausible implementations, or exposing a mismatch between the written task and
its tests. Human and AI attempts can both contribute. The useful comparison is
what becomes checkable, reusable, or less costly under stated conditions.

The [tooling work plan](docs/TOOLING_WORKFLOW.md) turns this into a proposed
working session using existing tools. A unified problem-workbench interface is
not implemented yet.

If you get stuck, come back with the attempt and the remaining question. If
this approach helps you make progress, consider starring the project so you
can find it again and follow its development.

## Find your next reading

| You want to… | Start here |
|---|---|
| Understand the idea in Chinese | [中文入口](README.zh-CN.md) |
| See how finite examples can become a proof | [Finite-example verification](docs/research/0183-zhang-finite-example-verification.md) |
| Distinguish nontermination evidence from timeout | [Finite cycle certificates](docs/research/keraia-cycle-certificates-and-halting-mass-bounds.md) |
| Write or extend native programs | [Development guide](docs/DEVELOPMENT.md), then [AGENTS.md](AGENTS.md) |
| Understand the programme's larger questions | [Philosophy](docs/philosophy/README.md) and [research agenda](docs/RESEARCH_ENGINEERING_AGENDA.md) |
| Explore the library | [Library](adva-library/README.md) and [mathematical growth obligation](adva-library/math/README.md) |
| Trace results, corrections and remaining questions | [Research index](docs/research/README.md), [claims](docs/claims.toml), and each note's later corrections |

Historical runs retain their original profiles. In particular, some stored
library epochs need their pinned historical receiver; see the
[replay guidance](docs/DEVELOPMENT.md#replaying-historical-library-epochs).
The [AI attribution policy](docs/AI_ATTRIBUTION.md) records contributions and
checks separately from account ownership.
