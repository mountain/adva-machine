"""Transport, engine selection and evidence checks for the local toolchain."""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from toolchain.boundary import BoundaryError, ROOT, catalog, check_request, library_receipt, read_request, strict_json
from toolchain.conformance import receive_pair
from toolchain.execute import run
from toolchain.fixtures import cases
from toolchain.process import Account, Exhausted


def test_contract_and_corpus_are_reproducible_and_keep_refusals_separate():
    corpus = json.loads((ROOT / "toolchain/corpus.json").read_bytes())
    assert corpus == cases()
    assert len(corpus) == 16
    assert len({c["name"] for c in corpus}) == 16
    schemas = [c["request"]["program"]["schema"] for c in corpus]
    assert schemas.count("unknown.program") == 1
    assert {c["expected"]["kind"] for c in corpus} == {"Returned", "Rejected", "Refused", "Unknown"}
    assert catalog()["stable"]["adva.ir"]["version"] == 1
    assert library_receipt()["native_admission"] == "NotGranted"


@pytest.mark.parametrize("raw", ['{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}'])
def test_ambiguous_or_nonfinite_json_is_not_silently_coerced(raw):
    with pytest.raises(BoundaryError):
        strict_json(raw)


@pytest.mark.parametrize("key,value", [("fuel", True), ("quantum", -1), ("fuel", 2049), ("profile", "adva.ir")])
def test_transport_budget_and_profile_changes_are_refused(key, value):
    request = deepcopy(cases()[0]["request"])
    request[key] = value
    with pytest.raises(BoundaryError):
        check_request(request)


def test_python_v2_is_unsupported_without_fallback_or_launch(tmp_path):
    request = deepcopy(cases()[0]["request"])
    request["profile"] = "data-machine-v2"
    request["program"]["schema"] = "adva.data-machine.program.research.v2"
    account = Account(tmp_path / "unsupported")
    result = run(request, "python", tmp_path / "missing-binary", account)
    assert result["outcome"]["kind"] == "Unsupported"
    assert account.calls == []
    assert result["verification"]["status"] == "NotRun"


def test_fuel_exhaustion_cannot_be_hidden_by_equal_returned_projection():
    left = {"request_sha256": "same", "profile": "data-machine-v0", "outcome": {"kind": "Unknown", "reason": "FuelExhausted"}}
    right = deepcopy(left)
    right["outcome"]["reason"] = "Suspended"
    with pytest.raises(ValueError, match="correspondence"):
        receive_pair(left, right)


def test_process_budget_stops_before_launch_and_existing_output_is_preserved(tmp_path):
    directory = tmp_path / "account"
    account = Account(directory, launches=0)
    with pytest.raises(Exhausted, match="launch"):
        account.child("never", [sys.executable, "-c", "raise AssertionError"])
    path = account.save("saved.json", {"original": True})
    before = path.read_bytes()
    with pytest.raises(FileExistsError):
        account.save("saved.json", {"original": False})
    assert path.read_bytes() == before
    with pytest.raises(FileExistsError):
        Account(directory)
    with pytest.raises(ValueError, match="leaves"):
        account.save("../escaped.json", {})
    assert not (tmp_path / "escaped.json").exists()


def test_doctor_rejects_a_non_repository_library(tmp_path):
    result = subprocess.run(
        [sys.executable, str(ROOT / "adva-machine"), "doctor", "--library", str(tmp_path)],
        cwd=tmp_path, capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 2
    assert json.loads(result.stdout)["status"] == "Refused"


def test_language_entries_resolve_from_outside_repository(tmp_path):
    for language in ("adva-rust", "adva-python"):
        result = subprocess.run(
            [sys.executable, str(ROOT / language / "run.py"), "--help"],
            cwd=tmp_path, capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0 and "--output" in result.stdout


@pytest.mark.parametrize("content", ['{"schema":1,"schema":2}', '{"fuel":NaN}', '{broken'])
def test_cli_retains_versioned_transport_refusal_without_launch(tmp_path, content):
    request = tmp_path / "request.json"
    request.write_text(content)
    output = tmp_path / "receipt"
    result = subprocess.run(
        [sys.executable, str(ROOT / "adva-machine"), "run", str(request),
         "--engine", "python", "--output", str(output)],
        cwd=tmp_path, capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 2
    report = json.loads((output / "report.json").read_bytes())
    assert report["schema"] == "adva.machine.report.v0"
    assert report["outcome"]["kind"] == "Refused"
    assert report["outcome"]["stage"] == "transport"
    assert report["cost"]["child_calls"] == []
    assert (output / "request-original.json").read_text() == content


def test_request_reader_bounds_regular_files_and_refuses_a_fifo(tmp_path):
    path = tmp_path / "request.json"
    path.write_bytes(b"12345")
    with pytest.raises(BoundaryError, match="exceeds"):
        read_request(path, limit=4)
    pipe = tmp_path / "pipe"
    os.mkfifo(pipe)
    with pytest.raises(BoundaryError, match="regular file"):
        read_request(pipe)
