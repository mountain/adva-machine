# Documentary package-manifest trial

Read the [proposal](../../spec/framework/package-capabilities-v0.1-proposal.md).
This is a library-only, offline metadata lint, not a package loader, registry,
Adva execution/verification interface or native receiver. A separate executable
reference tool resolves exact local Git blobs without semantic admission.
Original code and synthetic fixture by dot (OpenAI), under Unknown v0.3.

The schema admits nonempty capability declarations, but this receiver supports
only `library` with `adva.library-carrier.draft.v0`. `source_contract` identifies
the predecessor obligations, not an implemented definition of this draft profile.
The draft profile is defined by this README, the proposal, schema and checker
bytes together. Actual adoption must pin these bytes through an existing lock
and receiving contract. Nothing here creates a published version coordinate.

Prerequisites: Python 3.11+ and separately installed `jsonschema` 4.x. No network,
installation or third-party source is bundled. The dependency is documentary
validation software, not native Adva authority. Tested dependency versions are
recorded in the local execution report; there is no new repository lockfile.

From this directory:

```sh
python3 -m unittest -v
python3 check_manifest.py library-only.example.json
python3 check_manifest.py library-only.example.json verify  # exit 2, Rejected
```

The sole success exit is 0 / MetadataConsistent; rejected material/request exits
2, unavailable/unsupported receiver or exhausted byte/time budget exits 3 /
Unknown. Schema shape/cardinality/depth violations are malformed trial material,
not budget exhaustion. All outcomes withhold native admission and semantic
verification. An abrupt termination or no complete report is never success.

A production receiver would need independently selected schema/checker bytes,
source availability/integrity checks, authenticated custody as required by its
profile, an actual KPB-06 interface/effects contract and complete enforcement.
No compatibility is inferred from matching names or version numbering.

Run the complete local trial within one bounded supervisor on Unix:

```sh
python3 run_trial.py
```

This includes dependency/import setup, test fixture loading, positive and negative
controls, repeat reading/checking and report encoding/writing. Each invocation
retains its own logical account. The supervisor observes aggregate child elapsed/CPU and platform RSS, but does
not enforce memory. Its own startup and final report write are outside the measured
interval; fixed-child output-size checks are post-write. No performance comparison is claimed.
The two-second per-invocation deadline is cooperative; the outer timeout is the
aggregate bound and must be checked independently of any inner success report.

The implementation does not preserve an editable output manifest; it leaves input
bytes unchanged. Optional extension payloads remain opaque. A front end may use
trail names/order/annotations, but UI behavior, multi-view synchronization,
sharing, search and user learning history are not implemented here.

## Minimum executable reference links

Given a local checkout and an independently chosen consumer pin, write one
reference JSON containing repository, full commit and path (optional sha256),
then run:

```sh
python3 lookup_reference.py reference.json --repository mountain/adva-machine \
  --commit a0b710a2517f06f2fe03cc463e855548adf418ac --checkout /path/to/adva-machine
```

The tool supports local immutable Git blobs only, performs no network fetch,
and returns coordinates/digest rather than content. ReferenceBytesLocated is
exit 0 but still NotRun/NotGranted; missing bytes or budget exhaustion are
Unknown/exit 3; unsupported or incompatible references are Rejected/exit 2
with distinct reason codes. The repository label is caller-declared, not
source authentication. Never use a manifest-supplied pin as though independently
selected. This tooling is only a machine-side pilot, not deployed library API.

The Git receiver requires support for `--no-lazy-fetch`; unsupported versions
return Unknown with UnsupportedToolchain instead of retrying without the guard.
It also sets `GIT_NO_LAZY_FETCH=1`, disables protocols and disables replace objects.
This was exercised on Git 2.52.0. Git's documented no-lazy-fetch behavior is
specified in its [command reference](https://git-scm.com/docs/git/2.45.0.html).
Local Git metadata/stderr capture assumes trusted bounded command output;
this is not a hostile-checkout or preemptive pipe-memory sandbox.
