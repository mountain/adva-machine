"""Bounded golden-ratio calibration boundary; external evidence, no admission."""

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CALIBRATION = ROOT / "experiments/golden_ratio/calibration.py"
CONTRACT = ROOT / "experiments/golden_ratio/contract.json"
CONTRACT_V1 = ROOT / "experiments/golden_ratio/contract-v1.json"
REVIEW = ROOT / "docs/research/golden-ratio-receiving-review.md"
EVIDENCE = ROOT / "experiments/golden_ratio/evidence.json"
INDEX = ROOT / "adva-library/golden-ratio/index.json"
TERMS = ROOT / "docs/terminology/golden-ratio-receipt-v0.json"
MANIFEST = ROOT / "adva-library/math/manifest.json"

SPEC = importlib.util.spec_from_file_location("golden_calibration", CALIBRATION)
calibration = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(calibration)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def invoke(root, output):
    return subprocess.run(
        [
            sys.executable,
            "-S",
            str(CALIBRATION),
            "--root",
            str(root),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


@pytest.fixture
def staged_copy(tmp_path):
    """A writable copy of everything one run reads."""
    root = tmp_path / "checkout"
    shutil.copytree(ROOT / "adva-library/golden-ratio", root / "adva-library/golden-ratio")
    (root / "experiments/golden_ratio").mkdir(parents=True)
    shutil.copyfile(CONTRACT, root / "experiments/golden_ratio/contract.json")
    shutil.copyfile(CONTRACT_V1, root / "experiments/golden_ratio/contract-v1.json")
    (root / "docs/terminology").mkdir(parents=True)
    shutil.copyfile(TERMS, root / "docs/terminology/golden-ratio-receipt-v0.json")
    (root / "docs/research").mkdir(parents=True)
    shutil.copyfile(REVIEW, root / "docs/research/golden-ratio-receiving-review.md")
    return root


def withdrawn_resources():
    """Only explicitly inventoried withdrawals may be absent from a public clone."""
    records = load(ROOT / "governance/withdrawals/known-withdrawn-content.json")["records"]
    return {"adva-library/" + r["path"]: r["sha256"] for r in records
            if r["path"].startswith("golden-ratio/")}


def require_complete_private_inputs():
    missing = [a["staged_path"] for a in load(INDEX)["artifacts"]
               if not (ROOT / a["staged_path"]).is_file()]
    known = withdrawn_resources()
    assert all(p in known for p in missing), missing
    if missing:
        pytest.skip("Full historical replay requires lawfully obtained external inputs: "
                    + ", ".join(missing))


def test_public_checkout_refuses_incomplete_historical_replay(tmp_path):
    missing = [a for a in load(INDEX)["artifacts"]
               if not (ROOT / a["staged_path"]).is_file()]
    if not missing:
        pytest.skip("Private complete-input checkout; fresh replay is tested separately")
    known = withdrawn_resources()
    assert len(missing) == 8
    assert all(known[a["staged_path"]] == a["sha256"] for a in missing)
    output = tmp_path / "withdrawn-inputs.json"
    completed = invoke(ROOT, output)
    report = load(output)
    assert completed.returncode == 2
    assert report["status"] == "Invalid"
    assert "FileNotFoundError" in report["reason"]
    assert any(a["staged_path"] in report["reason"] for a in missing)
    assert report["cost"]["child_processes"] == 0


def test_staged_index_matches_every_delivered_artifact():
    index = load(INDEX)
    assert index["schema"] == "adva.golden-ratio-resource-index.research"
    assert index["authority"]["native_admission"] == "not-granted"
    assert index["authority"]["plates_are_evidence"] is False
    assert index["authority"]["pdf_is_evidence"] is False
    assert len(index["artifacts"]) == 15
    for artifact in index["artifacts"]:
        path = ROOT / artifact["staged_path"]
        if not path.is_file():
            assert withdrawn_resources().get(artifact["staged_path"]) == artifact["sha256"]
            continue
        assert path.stat().st_size == artifact["bytes"]
        assert digest(path) == artifact["sha256"]
    excluded = {entry["name"] for entry in index["delivery"]["excluded_delivered_entries"]}
    assert excluded == {".DS_Store"}


def test_retained_evidence_records_a_passed_bounded_run():
    report = load(EVIDENCE)
    assert report["status"] == "Passed", report.get("reason")
    assert report["authority"]["native_admission"] == "not-granted"
    assert report["authority"]["plates_are_evidence"] is False
    assert report["authority"]["recorded_claims_authenticated"] is False
    cost = report["cost"]
    assert cost["checks"] <= report["budget"]["max_checks"]
    assert cost["nodes"] <= report["budget"]["max_nodes"]
    assert cost["wall_seconds_before_serialization"] <= report["budget"]["max_seconds"]
    assert cost["child_processes"] == 1
    assert cost["subprocesses_beyond_replay"] == 0
    assert len(report["refusals"]) == 8
    assert {entry["outcome"] for entry in report["refusals"]} == {"Refused"}
    assert [r["receipt_kind"] for r in report["receipts"]] == list(calibration.RECEIPT_KINDS)
    for receipt in report["receipts"]:
        assert set(receipt) == set(calibration.RECEIPT_FIELDS) | {"receipt_kind"}
    assert all(entry["holds"] for entry in report["relabeling_refusals"])
    assert report["residuals"]
    assert report["external_replay"]["status"] == "ReplayedAgreement"
    # The active contract is the successor; the frozen version is pinned by the
    # digest the successor records, and the receiving review is pinned too.
    assert report["contract"]["sha256"] == digest(CONTRACT_V1)
    assert report["contract"]["path"] == "experiments/golden_ratio/contract-v1.json"
    assert report["contract"]["supersedes_sha256"] == digest(CONTRACT)
    assert report["contract"]["review"] == "docs/research/golden-ratio-receiving-review.md"
    limits = report["limits"]
    assert set(limits["installed"]) | set(limits["refused"]) == {
        "cpu_seconds",
        "address_space_bytes",
    }
    assert not set(limits["installed"]) & set(limits["refused"])


def test_fresh_run_reproduces_the_retained_evidence(tmp_path):
    require_complete_private_inputs()
    output = tmp_path / "fresh.json"
    completed = invoke(ROOT, output)
    assert completed.returncode == 0, completed.stderr
    fresh = load(output)
    retained = load(EVIDENCE)
    for report in (fresh, retained):
        # Limit installation is a host observation. Linux can install RLIMIT_AS
        # where the retained macOS run reported a refusal; validate both records
        # rather than requiring the same operating-system outcome.
        limits = report.pop("limits")
        installed, refused = limits["installed"], limits["refused"]
        assert set(installed) | set(refused) == {"cpu_seconds", "address_space_bytes"}
        assert set(installed).isdisjoint(refused)
        for key, value in installed.items():
            assert type(value) is int and value == report["budget"][key]
        assert all(isinstance(reason, str) and reason for reason in refused.values())
        report.pop("cost")
    assert fresh == retained


def test_tampered_plate_is_refused(staged_copy, tmp_path):
    require_complete_private_inputs()
    plate = staged_copy / "adva-library/golden-ratio/plates/whirling-squares.webp"
    plate.write_bytes(plate.read_bytes() + b"\x00")
    output = tmp_path / "tampered.json"
    completed = invoke(staged_copy, output)
    assert completed.returncode == 2, completed.stdout
    report = load(output)
    assert report["status"] == "Invalid"
    assert "artifact-digest" in report["reason"] or "artifact-bytes" in report["reason"]


def test_tampered_container_member_is_refused(staged_copy, tmp_path):
    require_complete_private_inputs()
    index = staged_copy / "adva-library/golden-ratio/index.json"
    document = json.loads(index.read_text(encoding="utf-8"))
    entry = next(e for e in document["digest_records"]["container_members"] if e["name"] == "evidence.json")
    entry["sha256"] = "0" * 64
    index.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output = tmp_path / "container.json"
    completed = invoke(staged_copy, output)
    assert completed.returncode == 2, completed.stdout
    assert load(output)["status"] == "Invalid"


def test_editing_the_frozen_contract_is_detected(staged_copy, tmp_path):
    frozen = staged_copy / "experiments/golden_ratio/contract.json"
    frozen.write_bytes(frozen.read_bytes().replace(b'"version": 0', b'"version": 9'))
    output = tmp_path / "frozen.json"
    completed = invoke(staged_copy, output)
    assert completed.returncode == 2, completed.stdout
    report = load(output)
    assert report["status"] == "Invalid"
    assert "contract-supersedes-frozen" in report["reason"]


def test_declared_pdf_metadata_must_match_the_bytes(staged_copy, tmp_path):
    require_complete_private_inputs()
    index = staged_copy / "adva-library/golden-ratio/index.json"
    document = json.loads(index.read_text(encoding="utf-8"))
    artifact = next(a for a in document["artifacts"] if a["role"] == "source-object")
    artifact["delivered_structure"]["title"] = "Some other article"
    index.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output = tmp_path / "pdf.json"
    completed = invoke(staged_copy, output)
    assert completed.returncode == 2, completed.stdout
    report = load(output)
    assert "artifact-pdf-title-parsed" in report["reason"]


def test_missing_receipt_contract_is_invalid(tmp_path):
    root = tmp_path / "checkout"
    shutil.copytree(ROOT / "adva-library/golden-ratio", root / "adva-library/golden-ratio")
    (root / "experiments/golden_ratio").mkdir(parents=True)
    shutil.copyfile(CONTRACT, root / "experiments/golden_ratio/contract.json")
    output = tmp_path / "missing.json"
    completed = invoke(root, output)
    assert completed.returncode == 2, completed.stdout
    assert load(output)["status"] == "Invalid"


def test_existing_output_is_never_overwritten(tmp_path):
    output = tmp_path / "keep.json"
    output.write_text("retained", encoding="utf-8")
    completed = invoke(ROOT, output)
    assert completed.returncode == 2
    assert output.read_text(encoding="utf-8") == "retained"
    missing_parent = tmp_path / "absent" / "report.json"
    completed = invoke(ROOT, missing_parent)
    assert completed.returncode == 2
    assert not missing_parent.exists()


def test_receipt_contract_matches_the_checker():
    terms = load(TERMS)
    assert terms["status"] == "Proposed"
    assert terms["authority"]["native_admission"] == "NotGranted"
    assert tuple(terms["fields"]) == calibration.RECEIPT_FIELDS
    assert tuple(terms["kinds"]) == calibration.RECEIPT_KINDS
    assert {term["name"] for term in terms["terms"]} == set(calibration.RECEIPT_KINDS)
    assert all(term["status"] == "Proposed" for term in terms["terms"])
    assert len(terms["relabeling_prohibitions"]) == 4


def test_catalog_entries_keep_the_external_reference_boundary():
    entries = {entry["key"]: entry for entry in load(MANIFEST)["entries"]}
    arithmetic = entries["arithmetic-golden-ratio-receipt-calibration"]
    geometry = entries["geometry-golden-ratio-external-reference"]
    assert arithmetic["recorded_status"] == "external-calibration-record"
    assert arithmetic["home"] == "arithmetic"
    assert arithmetic["geometry_lineage"] is None
    assert geometry["home"] == "geometry"
    assert geometry["geometry_lineage"] == {
        "kind": "external-reference",
        "parents": [],
        "derivation_evidence": [],
        "discharge": "Open",
    }
    for entry in (arithmetic, geometry):
        assert entry["checker"] is not None
        assert entry["evidence"] and entry["open_obligations"]
        for reference in entry["materials"] + entry["evidence"] + entry["checker"]["sources"]:
            assert digest(ROOT / reference["path"]) == reference["sha256"], reference["path"]
