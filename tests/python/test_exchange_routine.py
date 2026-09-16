"""Original fixtures under Unknown v0.3; observable effects pass through Rust.

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy;
not his review or endorsement.
"""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import blake3
import pytest

from exchange_routine import structure
from exchange_routine.run import execute
from toolchain.boundary import BoundaryError, ROOT
from toolchain.process import Account, Exhausted


def raw(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def b3(value):
    return blake3.blake3(value).hexdigest()


def card():
    return {"schema": structure.SCHEMA, "id": "original-test-structure",
            "question": "Which relation is proposed?", "origin": "Original synthetic project fixture",
            "objects": [{"id": "observation", "meaning": "A situated observation"},
                        {"id": "concept", "meaning": "A proposed reusable distinction"}],
            "relations": [{"from": "observation", "relation": "informs", "to": "concept",
                           "status": "proposed", "basis": "Synthetic example, not an empirical result"}],
            "preserve": ["Retain the source"], "open_questions": ["Is the interpretation adequate?"],
            "request": "Identify missing relations without inferring agreement."}


@pytest.fixture(scope="module")
def binary():
    supplied = os.environ.get("ADVA_EXCHANGE_BINARY")
    if supplied:
        result = Path(supplied).resolve()
    else:
        result = ROOT / "target/debug/adva"
        # Build once so CI cannot silently skip native receiving coverage.
        subprocess.run(["cargo", "build", "--locked", "-p", "adva-witness", "--bin", "adva"],
                       cwd=ROOT, check=True, capture_output=True, timeout=180)
    assert result.is_file()
    return result, sha(result.read_bytes())


def fixture(root, binary):
    source, store, acks = root / "source", root / "store", root / "acks"
    (source / "notes").mkdir(parents=True)
    store.mkdir()
    acks.mkdir()
    data = raw(card())
    (source / "notes/structure.json").write_bytes(data)
    entry = {"key": "logic-structure-test", "home": "logic", "title": "Original structure fixture",
             "domains": ["logic"], "theory": {"name": "documentary structure", "version": "1"},
             "scope": "Discussion only", "recorded_status": "proposed-document", "checker": None,
             "geometry_lineage": None, "evidence": [], "assumptions": ["Synthetic example"],
             "reuse_requires": ["Retain provenance"], "open_obligations": ["Meaning not checked"],
             "materials": [{"path": "adva-library/notes/structure.json", "sha256": sha(data)}]}
    catalog = raw({"entries": [entry]})
    (source / "catalog.json").write_bytes(catalog)
    review = {"schema": "adva.publication-admission.v1", "status": "admitted", "resource_id": "test-flow",
              "eligible_basis": "project-original", "files": [{"path": "knowledge/received/test-flow/materials/notes/structure.json",
              "bytes": len(data), "sha256": sha(data), "blake3": b3(data)}],
              "provenance": {"source_url": "https://github.com/mountain/adva-library", "source_version": "a" * 40,
              "creator_or_rights_holder": "Original project fixture contributor",
              "publication_basis_evidence_urls": ["https://github.com/mountain/adva-library"],
              "rights_holder_authority_evidence": "Original synthetic test contribution under Unknown v0.3",
              "jurisdictions_and_limitations": "Test attestation; not a legal judgment",
              "incorporated_components": [], "transformations": []},
              "review": {"reviewer": "ChatGPT (OpenAI)", "reviewed_at": "2026-09-16",
              "all_components_reviewed": True, "output_publication_reviewed": True,
              "unresolved_questions": [], "decision_reason": "Original test fixture"}}
    review_raw = raw(review)
    (root / "review.json").write_bytes(review_raw)
    contract = {"schema": "adva.communication.contract.v1", "profile": "documentary-library-entry-v1",
                "exchange_id": "test-flow", "sender": "fixture-source", "receiver": "fixture-receiver",
                "context": "discussion", "purpose": "documentary-reference", "home": "logic",
                "origin": {"repository": "https://github.com/mountain/adva-library", "revision": "a" * 40,
                           "catalog_path": "catalog.json", "catalog_blake3": b3(catalog)},
                "entry_key": entry["key"], "entry_blake3": b3(json.dumps(entry, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()),
                "publication_record_blake3": b3(review_raw), "read_budget": 8388608,
                "dependency_policy": "retain-references-no-execution",
                "checker": {"implementation_blake3": b3((ROOT / "crates/adva-witness/src/bin/support/communication_cli.rs").read_bytes()),
                            "cargo_lock_blake3": b3((ROOT / "Cargo.lock").read_bytes())},
                "files": [{"source": "notes/structure.json", "destination": "materials/notes/structure.json",
                           "bytes": len(data), "sha256": sha(data), "blake3": b3(data)}]}
    (root / "contract.json").write_bytes(raw(contract))
    request = {"schema": "adva.exchange-routine.request.v1", "binary": {"path": str(binary[0]), "sha256": binary[1]},
               "contract": {"path": "contract.json", "blake3": b3(raw(contract))},
               "publication_record": "review.json", "source": "source",
               "receiver": {"store": "store", "name": "fixture-receiver", "context": "discussion"},
               "acknowledgment": "acks/reply.json", "structure_member": "notes/structure.json"}
    path = root / "request.json"
    path.write_bytes(raw(request))
    return path, request, contract, review


def run(path):
    return execute(path, sha(path.read_bytes()), path.parent / "audit")


def test_structure_render_retains_relation_status_and_open_obligations():
    value = structure.check(raw(card()))
    shown = structure.render(value)
    assert "proposed" in shown and "not an empirical result" in shown
    assert value["preserve"][0] in shown and value["open_questions"][0] in shown
    result = structure.report(raw(value), value)
    assert result["claims_verified"] is False and result["native_admission"] == "NotGranted"


@pytest.mark.parametrize("change", [
    lambda c: c["objects"].append(deepcopy(c["objects"][0])),
    lambda c: c["relations"][0].update(to="absent"),
    lambda c: c["relations"][0].update(status="proved"),
    lambda c: c["relations"][0].update(basis=""),
    lambda c: c.update(request="\x1b[2J"),
])
def test_ambiguous_or_inflated_structure_is_refused(change):
    value = card()
    change(value)
    with pytest.raises(BoundaryError):
        structure.check(raw(value))


def test_structure_duplicate_json_keys_and_byte_limit_are_refused():
    value = raw(card())
    with pytest.raises(BoundaryError, match="duplicate"):
        structure.check(b'{"id":"shadow",' + value[1:])
    with pytest.raises(BoundaryError, match="32 KiB"):
        structure.check(b" " * 32769)


def test_comparison_does_not_discharge_removed_questions_or_requirements():
    before, after = card(), card()
    after["preserve"], after["open_questions"] = [], []
    result = structure.compare(raw(before), raw(after))
    assert result["removed_preservation_requirements"] == before["preserve"]
    assert result["removed_open_questions"] == before["open_questions"]
    assert result["obligations_discharged"] is False
    assert result["base_sha256"] == sha(raw(before)) and result["next_sha256"] == sha(raw(after))


def test_one_command_exchanges_structure_and_keeps_source_and_rust_evidence(tmp_path, binary):
    path, _, _, _ = fixture(tmp_path, binary)
    source = (tmp_path / "source/notes/structure.json").read_bytes()
    result, code = run(path)
    assert code == 0, result
    assert result["status"] == "CompletedDocumentaryExchange"
    assert result["cost"]["native_calls"] == 4
    assert result["new_acceptance_effects"] == 1
    assert result["observations"][2]["acceptance_effects"] == 0
    assert (tmp_path / "source/notes/structure.json").read_bytes() == source
    assert (tmp_path / "store/test-flow/materials/notes/structure.json").read_bytes() == source
    receipt = (tmp_path / "store/test-flow/receipt.json").read_bytes()
    ack = json.loads((tmp_path / "acks/reply.json").read_bytes())
    assert result["receipt_blake3"] == ack["receipt_blake3"] == b3(receipt)
    assert result["sender_observation"] == "Acknowledged"
    assert json.loads((tmp_path / "audit/result.json").read_bytes()) == result
    producer = json.loads((tmp_path / "audit/producer.json").read_bytes())
    for name, expected in producer["source_sha256"].items():
        assert sha((ROOT / name).read_bytes()) == expected
    with pytest.raises(FileExistsError):
        run(path)


@pytest.mark.parametrize("change", ["context", "binary", "pending-review", "unbound-card"])
def test_preflight_refusals_start_no_native_calls(tmp_path, binary, change):
    path, q, c, p = fixture(tmp_path, binary)
    if change == "context":
        q["receiver"]["context"] = "another-context"
    elif change == "binary":
        q["binary"]["sha256"] = "0" * 64
    elif change == "pending-review":
        p["status"] = "pending"
        (tmp_path / "review.json").write_bytes(raw(p))
        c["publication_record_blake3"] = b3(raw(p))
        (tmp_path / "contract.json").write_bytes(raw(c))
        q["contract"]["blake3"] = b3(raw(c))
    else:
        q["structure_member"] = "not-in-the-contract.json"
    path.write_bytes(raw(q))
    result, code = run(path)
    assert code == 2 and result["cost"]["native_calls"] == 0
    assert list((tmp_path / "store").iterdir()) == []
    assert not (tmp_path / "acks/reply.json").exists()


def test_independent_request_pin_is_required(tmp_path, binary):
    path, _, _, _ = fixture(tmp_path, binary)
    result, code = execute(path, "0" * 64, tmp_path / "audit")
    assert code == 2 and result["reason"] == "request pin mismatch"
    assert result["cost"]["native_calls"] == 0


def test_explicit_second_run_reuses_request_and_has_no_new_acceptance(tmp_path, binary):
    path, q, _, _ = fixture(tmp_path, binary)
    q["acknowledgment"] = None
    path.write_bytes(raw(q))
    first, code = run(path)
    assert code == 0, first
    second, code = execute(path, sha(path.read_bytes()), tmp_path / "second-audit")
    assert code == 0, second
    assert second["new_acceptance_effects"] == 0
    assert first["receipt_blake3"] == second["receipt_blake3"]
    assert Path(first["acknowledgment_path"]).is_file()
    assert Path(second["acknowledgment_path"]).is_file()
    assert first["acknowledgment_path"] != second["acknowledgment_path"]


def test_native_rejection_stops_after_send_and_retains_raw_observation(tmp_path, binary):
    path, q, _, _ = fixture(tmp_path, binary)
    q["structure_member"] = None
    path.write_bytes(raw(q))
    (tmp_path / "source/notes/structure.json").write_text("changed")
    result, code = run(path)
    assert code == 2 and result["status"] == "Rejected"
    assert result["cost"]["native_calls"] == 1
    assert (tmp_path / "audit/send-1.stdout.txt").is_file()
    assert list((tmp_path / "store").iterdir()) == []


def test_interrupted_receiver_does_not_reset_pending_state(tmp_path, binary):
    path, _, _, _ = fixture(tmp_path, binary)
    pending = tmp_path / "store/.test-flow.pending"
    pending.mkdir()
    (pending / "partial").write_text("retained interruption")
    result, code = run(path)
    assert code == 3 and result["status"] == "Unknown"
    assert result["cost"]["native_calls"] == 2
    assert result["sender_observation"] == "Unknown"
    assert (pending / "partial").read_text() == "retained interruption"
    assert not (tmp_path / "acks/reply.json").exists()


def test_missing_required_native_checker_keeps_unknown(tmp_path, binary):
    path, q, c, _ = fixture(tmp_path, binary)
    c["checker"]["implementation_blake3"] = "0" * 64
    (tmp_path / "contract.json").write_bytes(raw(c))
    q["contract"]["blake3"] = b3(raw(c))
    path.write_bytes(raw(q))
    result, code = run(path)
    assert code == 3 and result["status"] == "Unknown"
    assert result["cost"]["native_calls"] == 1
    assert list((tmp_path / "store").iterdir()) == []


def test_lost_supervisor_observation_preserves_native_receipt_without_ack(tmp_path, binary, monkeypatch):
    path, _, _, _ = fixture(tmp_path, binary)
    original = Account.child
    def lost_reply(account, label, command, **kwargs):
        result = original(account, label, command, **kwargs)
        if label == "receive-1":
            raise Exhausted("injected interruption after native reception")
        return result
    monkeypatch.setattr(Account, "child", lost_reply)
    result, code = run(path)
    assert code == 3 and result["cost"]["native_calls"] == 2
    assert result["receiver_observation"] == "Unknown"
    assert (tmp_path / "store/test-flow/receipt.json").is_file()
    assert (tmp_path / "audit/receive-1.stdout.txt").is_file()
    assert not (tmp_path / "acks/reply.json").exists()


def test_existing_output_and_repository_audit_location_are_refused(tmp_path, binary):
    path, _, _, _ = fixture(tmp_path, binary)
    repo = tmp_path / "fake-repository"
    (repo / ".git").mkdir(parents=True)
    with pytest.raises(BoundaryError, match="outside repository"):
        execute(path, sha(path.read_bytes()), repo / "audit")
    assert not (repo / "audit").exists()


def test_cli_works_from_another_directory_and_preserves_example_scope(tmp_path):
    example = ROOT / "exchange_routine/examples/knowledge-organization.json"
    result = subprocess.run([sys.executable, str(ROOT / "adva-exchange"), "check-structure", str(example)],
                            cwd=tmp_path, capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stdout + result.stderr
    checked = json.loads(result.stdout)
    assert checked["objects"] == 8 and checked["relations"] == 8
    assert checked["claims_verified"] is False
