# Iota received by the machine object-language interface

The same eight-file iota package was received separately by adva and
adva-machine on 2026-09-17. This record is the **machine** reception and its
post-arrival interpretation check. The [received presentation](../../received/iota-process-machine-2026-09-17-v1/materials/iota.md)
includes the generator rules, explicit boundaries, an ordinary data-machine
interpreter, three probes and a compact process/cut reading. Only this iota
packet crossed the boundary; no repository merge or global dependency upgrade
was performed.

The package is public here even though its complete development repository is
private. The eight materials total 81,651 bytes. Full annotated source evidence
remains an exact, optionally consulted external reference; the local package
contains everything this compact comparison consumes apart from its explicitly
pinned machine and external Python dependency.

## Two different questions and results

| Question | Actual observation | Scope |
| --- | --- | --- |
| Did the declared presentation arrive intact? | Rust send, receive, replay, acknowledgment all completed | Documentary transport under a separately bound receiver/context |
| Do the two finite readings agree for the declared use? | ScopedInterpretationChecked; 1,490 assertions | Prefix/spine reduction, reconstructed cuts/clocks, and three actual native probes |

[transport-result.json](transport-result.json) records Sent ->
AcceptedDocumentary -> AlreadyAccepted -> Acknowledged. There was one acceptance
effect; replay added zero. The sender's actual acknowledgment is preserved
[here](sender-acknowledgment.json). The [native receipt](../../received/iota-process-machine-2026-09-17-v1/receipt.json)
still says semantic verification NotRun and native admission NotGranted.
Nothing edits that historical judgment into the later interpretation result.

[interpretation-result.json](interpretation-result.json) reconstructs all 159
cut terms and transitions in twelve finite families, checks 92 local contractions,
and counts 519 schedules by dynamic programming. It rechecks boundary policies,
three clocks per family and the first cut-Laplacian partition coefficient.
It does not replay every scheduler path or reconstruct the full annotated
ancestry: those are distinct claims of the original process_v2 campaign.

Rust separately executes the supplied pure-iota identity, K-discard and S-copy
probes, returning after 1,126 / 3,025 / 4,838 instructions, then replays all three
traces. The native execution total is 8,989 instructions, plus the
same number replayed. The three runs use nine native launches. This is an
ordinary object-language program on the existing data-machine-v2 engine, not a
new builtin, native iota identity system or full language-equivalence proof.

## What communication adds to transport

The sender starts with tagged-tree reduction records. The receiving reading
uses prefix terms, an independently written application-spine reducer, event
masks and a reconstructed cut graph. Their exact finite correspondence is
checked against actual Rust object-program observations. Transport then carries
that presentation and its limits; each receiver rechecks what it received.

The retained controls show why the judgments must remain separate:

- Equal terminal values can have different histories and cut counts.
- Concurrency is not a transitive equality of observer clock readings.
- The same source boundary-policy bytes cannot justify a different proposed
  role reading; that control changes the proposed reading while keeping the
  bound policy constant.
- Swapped iota expansion, erased discarded arguments, identified copy
  occurrences and missing cuts are refused by concrete comparisons.
- Missing correspondence, absent object observations or an exhausted join
  reserve leave Unknown and do not advance the interpretation checkpoint.

All adapters were authored by one agent. Repeating the checker in three contexts
is not independent human agreement or three independently developed verifiers.
The shared object is the finite process; Surface presents the packet and
questions, Knowledge retains the scoped results/residuals, and Substrate carries
and executes the checks. These duties are not positional identifications with
A/B/object or the {}/[]/() domain chart.

The current Rust command spelling remains `adva communicate`. Under the
[fixed v2 vocabulary](https://github.com/mountain/adva-machine/blob/efa4031cd18b315b25179d1b4967ff6bdd5060a8/spec/framework/transport-communication-v2.md),
its documentary crossing is transport. The additional finite adapter comparison
is this trial's communication work; it does not implement a general native
heterogeneous communication operation or free balance.

## Exact source, receiving boundary and resources

- Source: adva-iota `602d5239011a3a463e72ce8db98e5f0da5c84690`, `exchange_v1/catalog.json`.
- Machine: `efa4031cd18b315b25179d1b4967ff6bdd5060a8`; binary and checker pins
  are retained in the request/contract archive and received dependencies.
- Packet SHA-256: `58aad08d14563201e8adb632db0a61d23016851878f103ba002da9aebba7e772`.
- Receiving contract: [contract.json](contract.json), BLAKE3
  `e29e9b17f14379333f221935d92b3cb48e669d339937693698fca5bb1113379d`.
- Publication admission: [exact eight-file review](../../../governance/publication/records/iota-process-machine-2026-09-17-v1.json).
- Complete execution inventories: [evidence-manifest.json](evidence-manifest.json).
- Other receiver: [adva reception](https://github.com/mountain/adva/tree/main/knowledge/exchanges/iota-process-knowledge-2026-09-17-v1).

This transport used four native calls, 1,173,479
aggregate bytes read and 0.190 wall seconds.
The subsequent comparison used 3,655 counted host units,
1.231 wall seconds and
1.048 aggregate CPU seconds.
The fixed campaign allows one source preflight, two transports and two receiver
checks: 35 native launches total. All completed on their first declared attempt;
no allowance was renewed. Authoring, preparing dependencies, output review,
archiving and Git publication are outside those execution timings.

The source catalog's home is logic. The native profile retains its historical
`adva-library/` reference prefix and `knowledge/received` review namespace;
these are resolved by this explicit source root and receiving store. The global
adva-library catalog, Pascal obligation, earlier consumer lock, original Java
and old evidence are unchanged. No source retirement is permitted.

## Reproduce the scoped comparison

With the exact pinned machine executable and its external Python dependencies:

    python knowledge/received/iota-process-machine-2026-09-17-v1/materials/check.py \
      --materials knowledge/received/iota-process-machine-2026-09-17-v1/materials \
      --expect-package 58aad08d14563201e8adb632db0a61d23016851878f103ba002da9aebba7e772 \
      --machine /path/to/pinned/adva-machine \
      --stage machine-after-reception --output /fresh/external/output

The machine implements the data instructions and replay; the received package
supplies the object interpreter. A missing or different required binary/pin
refuses this historical run. A new build or broader question needs a separately
bound continuation, leaving these received bytes and results intact.

Actual transport reproduction uses the archived original request as a template,
independently selects the source checkout, receiving context and trusted binary,
and binds the resulting new request before invoking `adva-exchange run`. Use a
fresh audit outside repositories. Never substitute a host copy for the native
receiver or manufacture a second acceptance effect from an archived receipt.

Full ancestry admission into PSC0, general nested residual equivalence,
physical simultaneity and a physical Hamiltonian remain open. The real/imaginary
operator and clock are distinct declared observations of one finite process.

Original report and checking: Codex (OpenAI), under Unknown v0.3 through Mingli
Yuan's authorized account proxy; not his authorship, endorsement, technical
review or correctness guarantee.
