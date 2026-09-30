#!/usr/bin/env python3
"""Transport newly generated original fixture bytes, then run a separate checker.

Project-original under Unknown v0.3, authored by dot (OpenAI) through Mingli
Yuan's authorized account proxy; account use is not review or endorsement.
This is a finite local experiment, not a package loader or rights oracle.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import blake3

from exchange_routine.io import binary_digest, plain, read
from exchange_routine.run import execute as execute_transport, outside_repository
from toolchain.boundary import BoundaryError, strict_json
from toolchain.process import Account, Exhausted

BASE_REVISION = "89d6f87554f474020de79e59056bce49d8ceb167"
REPOSITORY = "https://github.com/mountain/adva-machine"
RECEIVER = "native-evidence-receiver"
CONTEXT = "fixed-roundtrip-intake-v0"
PROFILE = "adva.native-evidence-intake.v0"
EXCHANGE = "native-evidence-intake"
SOURCE_MEMBER = "evidence/raw.json"
DESTINATION_MEMBER = "materials/evidence/raw.json"
LIMITS = {"wall": 90, "cpu": 75, "launches": 3, "native_launches": 3,
          "artifacts": 16 * 1024**2}
SOURCE_BINDINGS = (
    "main.rs", "intake.rs", "native.rs", "../Cargo.toml", "../Cargo.lock",
    "../../../docs/kpb/native-evidence-intake-v0.md",
    "../../checked_roundtrip_reuse/src/checked_roundtrip.rs",
    "../../checked_roundtrip_reuse/src/main.rs",
)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def b3(raw):
    return blake3.blake3(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()


def require(condition, reason):
    if not condition:
        raise BoundaryError(reason)


def source_selection():
    """Retain exact local source coordinates for the selected receiver build."""
    root = Path(__file__).parent / "src"
    records, fingerprint = {}, blake3.blake3()
    for relative in SOURCE_BINDINGS:
        raw = read(root / relative, 262144)
        path = relative.encode()
        fingerprint.update(len(path).to_bytes(8, "little"))
        fingerprint.update(path)
        fingerprint.update(len(raw).to_bytes(8, "little"))
        fingerprint.update(raw)
        records[relative] = {"bytes": len(raw), "sha256": sha(raw), "blake3": b3(raw)}
    return records, fingerprint


def prepare_transport(account, payload, transport_binary, transport_sha, checker_sha):
    """Author metadata only for this experiment's trusted emit-fixture output.

    There is deliberately no arbitrary external payload admission CLI. The
    generator binary is a trusted, digest-bound input selected by the operator.
    The review covers the original synthetic recipe, not third-party evidence.
    """
    require(len(payload) <= 65536, "synthetic payload exceeds documentary file bound")
    require(type(strict_json(payload)) is dict, "synthetic fixture must be a JSON object")
    payload.decode("utf-8")
    source = account.root / "source"
    store = account.root / "store"
    store.mkdir()
    account.save("source/" + SOURCE_MEMBER, payload)
    entry = {
        "key": "logic-native-evidence-fixture", "home": "logic",
        "title": "Original fixed-roundtrip raw evidence fixture",
        "domains": ["logic"], "theory": {"name": "synthetic documentary evidence", "version": "0"},
        "scope": "Raw candidate evidence for separately selected local checking",
        "recorded_status": "proposed-document", "checker": None,
        "geometry_lineage": None, "evidence": [],
        "assumptions": ["Newly generated project-original synthetic fixture under Unknown v0.3",
                        "Origin revision names the base environment, not a commit containing these new bytes"],
        "reuse_requires": ["Independent local native check with the preselected receiver binding"],
        "open_obligations": ["Transport grants no native admission or proof conclusion"],
        "materials": [{"path": "adva-library/" + SOURCE_MEMBER, "sha256": sha(payload)}],
    }
    catalog = encoded({"entries": [entry]})
    account.save("source/catalog.json", catalog)
    member = {"source": SOURCE_MEMBER, "destination": DESTINATION_MEMBER,
              "bytes": len(payload), "sha256": sha(payload), "blake3": b3(payload)}
    review = {
        "schema": "adva.publication-admission.v1", "status": "admitted",
        "resource_id": EXCHANGE, "eligible_basis": "project-original",
        "files": [{"path": f"knowledge/received/{EXCHANGE}/{DESTINATION_MEMBER}",
                   "bytes": len(payload), "sha256": sha(payload), "blake3": b3(payload)}],
        "provenance": {
            "source_url": REPOSITORY, "source_version": BASE_REVISION,
            "creator_or_rights_holder": "dot (OpenAI), project-original contribution under Unknown v0.3",
            "publication_basis_evidence_urls": [REPOSITORY + "/blob/" + BASE_REVISION + "/PUBLICATION_BOUNDARY.md"],
            "rights_holder_authority_evidence":
                "Original fixed synthetic recipe authored for this project under Unknown v0.3; no external evidence supplied",
            "jurisdictions_and_limitations": "Project contribution review; not a machine determination of legal rights",
            "incorporated_components": [],
            "transformations": [{"operation": "new synthetic fixture generation",
                                 "generator_path": "experiments/native_evidence_intake/src/intake.rs",
                                 "generator_binary_sha256": checker_sha,
                                 "base_revision_scope": "Base environment only; newly generated bytes did not exist at this revision"}],
        },
        "review": {"reviewer": "dot (OpenAI)", "reviewed_at": "2026-09-30",
                   "all_components_reviewed": True, "output_publication_reviewed": True,
                   "unresolved_questions": [],
                   "decision_reason": "Original bounded fixture recipe and its synthetic output only; no third-party input or native authority token"},
    }
    review_raw = encoded(review)
    account.save("publication-record.json", review_raw)
    contract = {
        "schema": "adva.communication.contract.v1", "profile": "documentary-library-entry-v1",
        "exchange_id": EXCHANGE, "sender": "original-synthetic-evidence-source", "receiver": RECEIVER,
        "context": CONTEXT, "purpose": "documentary-reference", "home": "logic",
        "origin": {"repository": REPOSITORY, "revision": BASE_REVISION,
                   "catalog_path": "catalog.json", "catalog_blake3": b3(catalog)},
        "entry_key": entry["key"],
        "entry_blake3": b3(json.dumps(entry, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()),
        "publication_record_blake3": b3(review_raw), "read_budget": 8388608,
        "dependency_policy": "retain-references-no-execution",
        "checker": {"implementation_blake3": b3(read(ROOT / "crates/adva-witness/src/bin/support/communication_cli.rs", 262144)),
                    "cargo_lock_blake3": b3(read(ROOT / "Cargo.lock", 262144))},
        "files": [member],
    }
    contract_raw = encoded(contract)
    account.save("contract.json", contract_raw)
    request = {
        "schema": "adva.exchange-routine.request.v1",
        "binary": {"path": str(transport_binary), "sha256": transport_sha},
        "contract": {"path": "contract.json", "blake3": b3(contract_raw)},
        "publication_record": "publication-record.json", "source": str(source),
        "receiver": {"store": str(store), "name": RECEIVER, "context": CONTEXT},
        "acknowledgment": None, "structure_member": None,
    }
    request_path = account.save("request.json", encoded(request))
    return request_path, store / EXCHANGE


def child_json(account, label, command, limit):
    code, raw, _ = account.child(label, command, native=True)
    require(len(raw) <= limit, f"{label} output exceeds its declared bound")
    value = strict_json(raw)
    require(type(value) is dict, f"{label} output is not a JSON object")
    return code, raw, value


def check_native_observation(native, code, binding, payload_pin):
    """Check reported scope and bindings; Rust remains the proof authority."""
    require(native.get("schema") == "adva.native-evidence-intake.v0", "unexpected native report schema")
    require(native.get("delivery_authority_used") is False, "native report used transport authority")
    require(code in (0, 2, 3), "unexpected native checker exit code")
    expected = {0: "LocalCheckedAndUsed", 2: "Rejected", 3: "Unknown"}[code]
    require(native.get("outcome") == expected, "native report outcome and exit code differ")
    if code != 0:
        return
    require(native.get("evidence_blake3_observed") == payload_pin, "native observation binds different evidence")
    require(native.get("independently_bound_context") == binding, "native observation binds different receiver context")
    local = native.get("local_check_and_cache")
    require(type(local) is dict and local.get("outcome") == "LocalCheckedAndUsed"
            and local.get("failure") is None and native.get("failure") is None,
            "successful native report lacks independent local check")
    stages = local.get("stages")
    require(type(stages) is list and all(type(stage) is dict for stage in stages), "malformed native stage records")
    require([stage.get("phase") for stage in stages] == [
        "first_check", "cache_hit", "fresh_use", "cache_hit", "fresh_use"],
        "native stages differ from declared first-check/two-use plan")
    uses = local.get("uses")
    require(type(uses) is list and all(type(use) is dict for use in uses), "malformed native use records")
    require(len(uses) == 2 and [use.get("values") for use in uses] == [[2, 3, 4], [5, 2, 3]]
            and [use.get("value") for use in uses] == ["14", "11"]
            and all(use.get("outcome") == "ScopedExecutionChecked" for use in uses),
            "native report lacks the two declared scoped executions")
    require(uses[0].get("program") != uses[1].get("program"), "fresh native uses report the same program")


def run(transport_binary, checker_binary, output):
    output = outside_repository(output)
    account = Account(output, **LIMITS)
    report = {
        "schema": "adva.native-evidence-intake.integration.v0", "status": "Unknown",
        "stage": "preflight", "transport": None, "native_check": "NotRun",
        "automatic_retries": 0, "source_retirement": "NotPerformed",
        "transport_receipt_mutated": False,
        "residual": "Only a newly generated synthetic fixed-roundtrip fixture; no package import, authority transfer or general native loader",
    }
    code = 3
    try:
        transport_binary, checker_binary = plain(transport_binary), plain(checker_binary)
        transport_sha, transport_bytes = binary_digest(transport_binary)
        checker_sha, checker_bytes = binary_digest(checker_binary)
        source_records, source_fingerprint = source_selection()
        account.save("source-selection.json", {"relative_to": "experiments/native_evidence_intake/src",
                                               "sources": source_records,
                                               "bytes_hashed": sum(item["bytes"] for item in source_records.values()),
                                               "scope": "Local source integrity; binary/platform remains operator-selected trusted input"})
        account.save("producer.json", {
            "schema": "adva.native-evidence-intake.integration-producer.v0",
            "transport_binary_sha256": transport_sha, "checker_binary_sha256": checker_sha,
            "binary_bytes_hashed": transport_bytes + checker_bytes,
            "supervisor_sha256": sha(read(Path(__file__), 65536)),
            "base_revision": BASE_REVISION, "generator_path": "experiments/native_evidence_intake/src/intake.rs",
            "origin_scope": "Base environment only; this run generates new original fixture bytes",
            "trusted_inputs": "Operator-selected binaries and quiescent local POSIX filesystem",
        })
        account.save("plan.json", {
            "schema": "adva.native-evidence-intake.integration-plan.v0",
            "stages": ["receiver-binding", "emit-fixture", "send", "receive", "replay", "acknowledge", "independent-native-check"],
            "maximum_checker_processes": 3, "maximum_transport_processes": 4,
            "automatic_retries": 0, "supervisor_limits": LIMITS,
            "native_process_address_space_bytes": 1024**3,
            "receipt_policy": "Immutable documentary NotRun/NotGranted; later native report is separate",
        })
        report["stage"] = "receiver-binding"
        status, binding_raw, binding = child_json(account, "receiver-binding", [str(checker_binary), "receiver-binding"], 131072)
        require(status == 0, "receiver binding generation did not succeed")
        require(binding.get("schema") == "adva.fixed-roundtrip-receiver-binding.v0"
                and binding.get("profile") == PROFILE
                and binding.get("receiver") == RECEIVER and binding.get("context") == CONTEXT,
                "unexpected independently selected receiver binding")
        origin = binding.get("origin")
        require(type(origin) is dict and origin.get("repository") == REPOSITORY
                and origin.get("baseline_revision") == BASE_REVISION
                and origin.get("generator_path") == "experiments/native_evidence_intake/src/intake.rs"
                and origin.get("generator_blake3") == source_records["intake.rs"]["blake3"],
                "receiver binding differs from selected local generator source")
        native_build = binding.get("native_checker_build_blake3")
        require(type(native_build) is str and len(native_build) == 64, "missing native source/build fingerprint")
        source_fingerprint.update(native_build.encode())
        require(binding.get("intake_checker_build_blake3") == source_fingerprint.hexdigest(),
                "receiver binary differs from selected local intake sources")
        binding_path = account.save("receiver-binding.json", binding_raw)
        binding_pin = b3(binding_raw)
        account.save("receiver-selection.json", {"binding_blake3": binding_pin, "receiver": RECEIVER, "context": CONTEXT,
                                                  "scope": "Selected independently before fixture generation and transport; never an envelope member"})
        report["stage"] = "emit-fixture"
        status, payload, fixture = child_json(account, "emit-fixture", [str(checker_binary), "emit-fixture"], 65536)
        require(status == 0, "fixture generation did not succeed")
        require(fixture.get("schema") == "adva.fixed-roundtrip-raw-evidence.v0"
                and fixture.get("profile") == PROFILE and fixture.get("origin") == origin
                and binding.get("raw_evidence_blake3") == b3(payload),
                "emitted raw fixture differs from independently selected evidence binding")
        request_path, received = prepare_transport(account, payload, transport_binary, transport_sha, checker_sha)
        request_raw = read(request_path, 32768)
        report["stage"] = "documentary-transport"
        transport, transport_code = execute_transport(request_path, sha(request_raw), account.root / "audit")
        report["transport"] = transport
        account.remaining()
        if transport_code != 0:
            report.update(status=transport["status"], reason=transport.get("reason", "documentary transport did not complete"))
            code = transport_code
        else:
            require(transport["status"] == "CompletedDocumentaryExchange", "unexpected documentary result")
            require(transport["cost"]["native_calls"] == 4, "documentary plan did not perform exactly four native calls")
            receipt_path = received / "receipt.json"
            payload_path = received / DESTINATION_MEMBER
            receipt_before = read(receipt_path, 262144)
            account.save("receipt-before-native.json", receipt_before)
            report["transport_receipt_mutated"] = b3(receipt_before) != transport["receipt_blake3"]
            require(not report["transport_receipt_mutated"], "pre-native receipt differs from completed transport receipt pin")
            receipt = strict_json(receipt_before)
            require(receipt.get("semantic_verification") == "NotRun" and receipt.get("native_admission") == "NotGranted",
                    "documentary receipt scope differs")
            require(read(payload_path, 65536) == payload, "received payload differs from original fixture bytes")
            require(read(account.root / "source" / SOURCE_MEMBER, 65536) == payload, "original source changed")
            ack_path = plain(transport["acknowledgment_path"])
            ack_before = read(ack_path, 262144)
            ack = strict_json(ack_before)
            require(ack.get("semantic_verification") == "NotRun" and ack.get("native_admission") == "NotGranted"
                    and ack.get("receipt_blake3") == b3(receipt_before) == transport["receipt_blake3"]
                    and b3(ack_before) == transport["acknowledgment_blake3"], "acknowledgment scope or binding differs")
            report.update(received_evidence_path=str(payload_path), receipt_path=str(receipt_path),
                          receipt_blake3=b3(receipt_before), payload_blake3=b3(payload), receiver_binding_blake3=binding_pin,
                          acknowledgment_path=str(ack_path), acknowledgment_blake3=b3(ack_before))
            report["stage"] = "independent-native-check"
            selected_sha, selected_bytes = binary_digest(checker_binary)
            account.save("checker-before-native.json", {"sha256": selected_sha, "bytes_hashed": selected_bytes,
                                                        "matches_selected_binary": selected_sha == checker_sha})
            require(selected_sha == checker_sha, "selected native checker binary changed before independent checking")
            # This checker is never passed the receipt, acknowledgment, catalog,
            # producer verdict, serialized checked handle or transport success flag.
            report["native_check"] = {"outcome": "Unknown", "reason": "Invocation attempted; no complete native report yet"}
            try:
                native_code, native_raw, native = child_json(account, "native-check", [
                    str(checker_binary), "check", str(payload_path), str(binding_path),
                    "--expect-binding", binding_pin, "--receiver", RECEIVER, "--context", CONTEXT,
                ], 2 * 1024**2)
            finally:
                # Preserve the documentary scope even when the later checker
                # rejects, times out, exits abnormally or emits invalid JSON.
                receipt_after = read(receipt_path, 262144)
                account.save("receipt-after-native.json", receipt_after)
                report["transport_receipt_mutated"] = receipt_after != receipt_before
                require(receipt_after == receipt_before, "independent check altered documentary receipt")
                require(read(payload_path, 65536) == payload, "independent check altered received evidence")
                require(read(account.root / "source" / SOURCE_MEMBER, 65536) == payload, "independent check altered original source")
                require(read(binding_path, 131072) == binding_raw, "independent receiver binding changed")
                require(read(ack_path, 262144) == ack_before, "independent check altered documentary acknowledgment")
            account.save("native-report.json", native_raw)
            report["native_check"] = native
            check_native_observation(native, native_code, binding, b3(payload))
            report.update(status="CompletedSeparateNativeCheck" if native_code == 0 else ("Rejected" if native_code == 2 else "Unknown"),
                          stage="complete", native_report_path=str(account.root / "native-report.json"))
            code = native_code
        account.remaining()
    except Exhausted as error:
        report.update(status="Unknown", reason=str(error))
        code = 3
    except (BoundaryError, ValueError, TypeError, KeyError, RecursionError) as error:
        report.update(status="Refused", reason=str(error))
        code = 2
    except OSError as error:
        report.update(status="Unknown", reason=str(error))
        code = 3
    report["supervisor_cost"] = account.cost()
    report["aggregate_native_calls"] = account.native_calls + (report.get("transport") or {}).get("cost", {}).get("native_calls", 0)
    report["accounting_scope"] = "Outer wall/CPU/artifact account includes nested transport; three checker processes plus four transport processes, no automatic retries"
    try:
        account.save("result.json", report)
    except (Exhausted, OSError) as error:
        report.update(status="Unknown", reason=f"could not retain final integration report: {error}")
        code = 3
    return report, code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transport-binary", required=True, type=Path)
    parser.add_argument("--checker-binary", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        report, code = run(args.transport_binary, args.checker_binary, args.output)
    except (BoundaryError, ValueError, OSError) as error:
        report, code = {"schema": "adva.native-evidence-intake.integration.v0", "status": "Refused", "reason": str(error), "native_check": "NotRun"}, 2
    print(json.dumps(report, ensure_ascii=False, allow_nan=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
