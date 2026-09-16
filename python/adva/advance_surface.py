"""Version-bound symbol-surface handoff: existing Rust loading, no execution."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

if __package__:
    from .advance import ROOT, read_bounded, require_pin, save
    from .math_catalog import check_catalog
    from .quine_relay import Exhausted, Supervisor, digest
else:
    from advance import ROOT, read_bounded, require_pin, save
    from math_catalog import check_catalog
    from quine_relay import Exhausted, Supervisor, digest

# The active contract is the newest successor. Each successor names the digest
# of the contract it supersedes, and the run verifies that digest, so editing a
# superseded contract afterwards is a failure rather than a silent
# reinterpretation. The chain is v0 <- v1 <- v2 <- v3 <- v4 <- v5 <- v6 <- v7 <- v8.
CONTRACT = ROOT / "experiments/advance_symbol_surface/contract-v8.json"
# The cargo cdylib artifact is `lib_native` with the platform dynamic-library
# extension. The profile was written for Linux, where that is `.so`; on macOS it
# is `.dylib`, and the hard-coded name made the run stop after a successful build
# with "No such file or directory: target/debug/lib_native.so".
CDYLIB_EXTENSION = {"darwin": ".dylib", "win32": ".dll"}.get(sys.platform, ".so")
NATIVE_BINARY = ROOT / ("target/debug/lib_native" + CDYLIB_EXTENSION)
SOURCE = ROOT / "experiments/symbol_surface"
LIBRARY = ROOT / "adva-library"
FILES = (
    "README.md",
    "construct_records.py",
    "inspect_representation.py",
    "inspection.json",
    "presentation.json",
    "contract.json",
    "obligations.json",
    "symbol-surface.adva",
)


def check_payload_bindings(raw):
    """Check documentary byte references; this does not admit the Rust envelope."""
    document = json.loads(raw["symbol-surface.adva"])
    payloads = ("presentation.json", "contract.json", "obligations.json")
    for carrier, name in zip(document["carriers"], payloads, strict=True):
        if carrier["carrier"]["structure"] != "sha256:" + digest(raw[name]):
            raise ValueError(f"payload binding mismatch: {name}")
    obligations = json.loads(raw["obligations.json"])["items"]
    if (
        len(obligations) != 9
        or len({item["id"] for item in obligations}) != 9
        or any(item["status"] != "Open" for item in obligations)
    ):
        raise ValueError("nine unchanged Open annotations required")
    sites = [item["document_frontier_coordinate"] for item in obligations]
    if sites != document["carriers"][0]["carrier"]["frontier"]["sites"]:
        raise ValueError("annotation/frontier binding mismatch")
    return document, sites


def check_loaded(loaded, sites):
    """Protocol checks on fresh Rust output; never import stored JSON as authority."""
    certificate = loaded["certificate"]
    for field in (
        "schema_and_version",
        "canonical_tables",
        "resolved_references",
        "mechanism_forms",
    ):
        if certificate.get(field) != "checked":
            raise ValueError(f"missing Rust load check: {field}")
    if (
        certificate.get("schema") != "adva.neutral-carrier-graph.research"
        or type(certificate.get("version")) is not int
        or certificate["version"] != 0
        or certificate.get("entrypoint") != "inspect"
        or certificate.get("frame") != 0
    ):
        raise ValueError("Rust certificate does not bind the selected envelope")
    transition = loaded["transition"]
    if transition["state"] != "ready" or transition["recorded_output"] is not None:
        raise ValueError("load must preserve absent outputs")
    form, admission = transition["form"], transition["admission"]
    if (
        form["mechanism"] != "verify"
        or form["discharges"] != []
        or form["declared_subject"]["sites"] != sites
        or form["input"]["subject"]["frontier"]["sites"] != sites
        or admission["mechanism"] != "verify"
        or admission["status"] != "conditional"
        or admission["remaining_subject"]["sites"] != sites
    ):
        raise ValueError("load changed the nine-site conditional boundary")


def worker(output):
    # Import the newly built extension directly, without the checkout's old installed wheel.
    native_path = output / "_native.abi3.so"
    spec = importlib.util.spec_from_file_location("_native", native_path)
    native = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(native)
    raw = {name: read_bounded(output / "source" / name, 65_536) for name in FILES}
    document, sites = check_payload_bindings(raw)
    calls = []
    controls = {}
    cases = output / "cases"
    cases.mkdir()

    def load(name, path, entrypoint="inspect", error_fragment=None):
        started = time.monotonic()
        record = {"name": name, "path": str(path), "entrypoint": entrypoint}
        calls.append(record)
        try:
            transition, certificate = native.load_adva_document_json(str(path), entrypoint)
        except ValueError as error:
            record.update(status="Rejected", error=str(error))
            save(cases / (name + ".json"), record)
            if error_fragment is None or error_fragment not in str(error):
                raise ValueError(f"unexpected Rust refusal in {name}: {error}") from error
            controls[name] = True
            return None
        finally:
            record["wall_seconds"] = time.monotonic() - started
        if error_fragment is not None:
            raise ValueError(f"Rust accepted the negative control: {name}")
        result = {"transition": json.loads(transition), "certificate": json.loads(certificate)}
        check_loaded(result, sites)
        record["status"] = "NativeEnvelopeLoaded"
        save(cases / (name + ".json"), result)
        return result

    original = load("original", output / "source/symbol-surface.adva")
    archived = load("library-copy", output / "library-source/symbol-surface.adva")
    repeated = load("unchanged-control", output / "source/symbol-surface.adva")
    controls["two_copies_same_load"] = original == archived
    controls["unchanged_is_evidence_stutter"] = original == repeated

    bad = copy.deepcopy(document)
    bad["frames"][0]["input"]["subject"] = 99
    save(cases / "unknown-reference.adva", bad)
    load("unknown-reference", cases / "unknown-reference.adva", error_fragment="unknown carrier")

    bad = copy.deepcopy(document)
    bad["frames"][0]["mechanism"]["declared_subject"]["sites"].pop()
    save(cases / "undeclared-site.adva", bad)
    load("undeclared-site", cases / "undeclared-site.adva", error_fragment="undeclared")

    bad = copy.deepcopy(document)
    bad["frames"][0]["output"]["history"] = 0
    save(cases / "partial-output.adva", bad)
    load("partial-output", cases / "partial-output.adva", error_fragment="partially")

    load(
        "unknown-entrypoint",
        output / "source/symbol-surface.adva",
        entrypoint="missing",
        error_fragment="unknown Adva entry point",
    )

    # Deliberately omit every external payload in this directory. The existing
    # Rust loader checks cache-coordinate strings, not their referenced payloads.
    no_payload = output / "without-payloads"
    no_payload.mkdir()
    (no_payload / "symbol-surface.adva").write_bytes(raw["symbol-surface.adva"])
    isolated = load("payload-resolution-boundary", no_payload / "symbol-surface.adva")
    controls["payload_resolution_is_not_claimed"] = isolated == original

    changed = dict(raw, **{"presentation.json": raw["presentation.json"] + b" "})
    try:
        check_payload_bindings(changed)
    except ValueError:
        controls["external_payload_tamper_refused"] = True
    else:
        raise ValueError("changed payload was accepted by the outer byte gate")
    if len(controls) != 8 or not all(controls.values()):
        raise ValueError("a frozen native-load control failed")
    save(
        output / "native-load.json",
        {
            "status": "NativeEnvelopeLoadChecked",
            "baseline": original,
            "native_load_invocations": len(calls),
            "calls": calls,
            "controls": controls,
            "remaining_annotation_ids": [
                item["id"] for item in json.loads(raw["obligations.json"])["items"]
            ],
            "arithmetic_evaluations": 0,
            "proof_replays": 0,
            "game_moves": 0,
            "payload_resolution": "NotImplementedByLoader",
        },
    )


def run(args):
    output = Path(args.output).resolve()
    output.mkdir(parents=False, exist_ok=False)
    raw_contract = read_bounded(CONTRACT, 262_144)
    contract = json.loads(raw_contract)
    if contract.get("version", 0) < 1 or "supersedes" not in contract:
        raise ValueError("the active contract must be a versioned successor")
    superseded = ROOT / contract["supersedes"]["path"]
    if contract["supersedes"]["sha256"] != hashlib.sha256(
        read_bounded(superseded, 262_144)
    ).hexdigest():
        raise ValueError(
            contract["supersedes"]["path"]
            + " changed after this contract recorded its digest"
        )
    supervisor = Supervisor(output, contract["limits"])
    report = {
        "schema": "adva.advance-symbol-surface.result.research",
        "version": 0,
        "profile": "symbol-surface-load-v0",
        "status": "Rejected",
        "phase": "preflight",
        "new_knowledge_epoch": False,
        "native_free": "NotGranted",
        "mathematical_proof_admission": "not-granted",
        "contract": {
            "path": "experiments/advance_symbol_surface/contract-v4.json",
            "version": contract["version"],
            "supersedes": contract["supersedes"]["path"],
            "supersedes_sha256": contract["supersedes"]["sha256"],
        },
    }
    try:
        (output / "contract.json").write_bytes(raw_contract)
        for relative, expected in contract["pins"].items():
            require_pin(read_bounded(ROOT / relative), expected)
        report["source_head"] = supervisor.git("source-head", ROOT, "rev-parse", "HEAD")
        supervisor.call(
            "base-ancestor",
            ["git", "merge-base", "--is-ancestor", contract["base_commit"], "HEAD"],
            ROOT,
        )
        supervisor.call(
            "rust-source-boundary",
            [
                "git",
                "diff",
                "--exit-code",
                "--no-ext-diff",
                contract["base_commit"],
                "--",
                "Cargo.toml",
                "Cargo.lock",
                "crates",
                ".cargo",
                "rust-toolchain",
                "rust-toolchain.toml",
                "build.rs",
            ],
            ROOT,
        )
        if (
            supervisor.git("library-head", LIBRARY, "rev-parse", "HEAD")
            != contract["library_commit"]
        ):
            raise ValueError("library differs from this finite contract")
        predecessor = read_bounded(ROOT / contract["predecessor"])
        (output / "predecessor-handoff.json").write_bytes(predecessor)
        prior = read_bounded(ROOT / contract["prior_advance"])
        (output / "prior-advance.json").write_bytes(prior)
        report["predecessor_sha256"] = digest(predecessor)
        report["prior_advance_sha256"] = digest(prior)
        source, library_source = output / "source", output / "library-source"
        source.mkdir()
        library_source.mkdir()
        for name in FILES:
            original = read_bounded(SOURCE / name, 65_536)
            archived = read_bounded(LIBRARY / "symbol-surface/source" / name, 65_536)
            if original != archived:
                raise ValueError(f"source/library archived bytes differ: {name}")
            (source / name).write_bytes(original)
            (library_source / name).write_bytes(archived)
        check_payload_bindings({name: read_bounded(source / name, 65_536) for name in FILES})
        catalog = check_catalog(ROOT, key_words=True)
        save(output / "catalog.json", catalog)
        if catalog["status"] != "CatalogConsistent":
            raise ValueError("catalog/key-word preflight failed")
        supervisor.call(
            "documentary-swap", [sys.executable, LIBRARY / "symbol-surface/swap.py"], LIBRARY
        )
        for name in (
            "adva.py",
            "advance_surface.py",
            "advance.py",
            "math_catalog.py",
            "quine_relay.py",
        ):
            (output / ("implementation-" + name)).write_bytes(
                read_bounded(ROOT / "python/adva" / name)
            )
        report["phase"] = "build-existing-rust-loader"
        print("advance: source binding passed; building the existing Rust/PyO3 loader", flush=True)
        supervisor.call(
            "build-native",
            [
                "cargo",
                "rustc",
                "--locked",
                "--offline",
                "-j",
                "1",
                "-p",
                "adva-python",
                "--lib",
                "--",
                "-C",
                "debuginfo=0",
                "-C",
                "strip=debuginfo",
            ],
            ROOT,
        )
        binary = NATIVE_BINARY
        binary_raw = read_bounded(binary, contract["limits"]["max_file_bytes"])
        (output / "_native.abi3.so").write_bytes(binary_raw)
        report["native_binary_sha256"] = digest(binary_raw)
        report["phase"] = "read-only-native-load"
        print("advance: running the native load and fixed boundary controls", flush=True)
        code = supervisor.call(
            "native-load",
            [sys.executable, Path(__file__).resolve(), "--worker", output],
            ROOT,
            allow_failure=True,
        )
        if code == 3:
            raise Exhausted("native-load worker resource limit")
        if code:
            raise ValueError("native-load worker failed; see native-load.stderr and retained cases")
        native = json.loads(read_bounded(output / "native-load.json"))
        if native["status"] != "NativeEnvelopeLoadChecked":
            raise ValueError("native load did not pass")
        report["controls"] = native["controls"]
        report["finding"] = {
            "native_load_before": "NotRun",
            "native_load_after": "NativeEnvelopeLoaded",
            "frame_state": native["baseline"]["transition"]["state"],
            "verification_formation": native["baseline"]["transition"]["admission"]["status"],
            "open_annotations_before": 9,
            "open_annotations_after": len(native["remaining_annotation_ids"]),
            "native_load_invocations": native["native_load_invocations"],
            "recorded_outputs": 0,
            "mathematical_discharges": 0,
            "payload_resolution": native["payload_resolution"],
        }
        for relative, expected in contract["pins"].items():
            require_pin(read_bounded(ROOT / relative), expected)
        report["delta"] = {
            "kind": "result",
            "description": "The exact handed-off envelope now "
            "has a fresh Rust load certificate with nine remaining frontier annotations.",
            "scope": "document and mechanism formation only",
        }
        report.update(status="VariationObserved", phase="complete")
    except (Exhausted, MemoryError, TimeoutError) as error:
        report.update(status="Unknown", error=str(error))
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        report.update(status="Rejected", error=str(error))
    finally:
        try:
            report["files"], report["retained_bytes_before_report"] = supervisor.inventory()
        except Exhausted as error:
            report.update(status="Unknown", error=str(error))
        report["calls"] = supervisor.calls
        report["cost"] = {
            "wall_seconds_before_report": time.monotonic() - supervisor.started,
            "child_cpu_seconds": supervisor.child_cpu() - supervisor.child_cpu_start,
            "subprocess_invocations": len(supervisor.calls),
            "scope": "Preflight, build, load, controls, inventory; authoring and "
            "engineering tests are outside this experiment account.",
        }
        save(output / "report.json", report)
        if time.monotonic() >= supervisor.deadline:
            report.update(status="Unknown", error="checkpoint crossed the run deadline")
            save(output / "checkpoint-limit.json", report)
    return report


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] != "--worker":
        raise SystemExit(
            "Use adva.py advance --profile symbol-surface-load-v0 --output NEW-DIRECTORY"
        )
    try:
        worker(Path(sys.argv[2]))
    except (MemoryError, RecursionError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(3) from error
