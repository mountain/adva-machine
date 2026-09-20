"""Receive retained engineering evidence without trusting its summary alone."""
from copy import deepcopy
import json
import sys
from pathlib import Path
import shutil

import pytest

from toolchain.archive import receive
from toolchain.boundary import ROOT, digest, native_profile, observe
from toolchain.conformance import receive_pair


EVIDENCE = ROOT / "toolchain/evidence"


@pytest.fixture(scope="module", params=("local-01", "local-02", "local-03", "local-04", "local-05"))
def retained(request):
    return receive(EVIDENCE / request.param)


def test_retained_contract_and_producer_snapshots_are_bound(retained):
    contract = json.loads(retained["contract.json"])
    assert contract["automatic_retries"] == 0
    assert contract["attempts_per_invocation"] == 1
    assert digest((ROOT / contract["corpus"]["path"]).read_bytes()) == contract["corpus"]["sha256"]
    for path, expected in json.loads(retained["source-manifest.json"]).items():
        assert digest(retained["sources/" + Path(path).name]) == expected
    library = json.loads(retained["library-receipt.json"])
    assert library["status"] == "MatchedPinnedDependency"
    lock = json.loads((ROOT / "toolchain/library.lock.json").read_bytes())
    # Historical receipts stay bound to their original lock when licensing-only
    # library successors are adopted; never rewrite the retained run bytes.
    while lock["revision"] != library["revision"]:
        previous = lock["previous_lock"]
        raw = (ROOT / previous["path"]).read_bytes()
        assert digest(raw) == previous["sha256"]
        lock = json.loads(raw)
    assert library["checked_files"] == len(lock["files"])
    assert library["native_admission"] == "NotGranted"


def test_retained_acceptance_stayed_within_its_contract(retained):
    report = json.loads(retained["report.json"])
    assert report["status"] == "Passed" and report["case_count"] == 16
    cost = report["cost"]
    limits = cost["limits"]
    assert len(cost["child_calls"]) == 80 <= limits["child_launches"]
    assert cost["native_calls"] == sum(c["native"] for c in cost["child_calls"]) == 68
    assert cost["native_calls"] <= limits["native_launches"]
    assert all(c["status"] == "Exited" and c["exit_code"] in (0, 2) for c in cost["child_calls"])
    assert cost["wall_seconds"] < limits["wall_seconds"]
    assert cost["cpu_seconds_including_children"] < limits["cpu_seconds"]
    assert sum(map(len, retained.values())) < limits["artifact_bytes"]


def test_raw_requests_executions_and_native_receipts_agree(retained):
    corpus = json.loads((ROOT / "toolchain/corpus.json").read_bytes())
    summary = json.loads(retained["report.json"])
    total_steps = receipts = 0
    for case, row in zip(corpus, summary["cases"], strict=True):
        assert row["case"] == case["name"]
        reports, executions = {}, {}
        for engine in ("rust", "python"):
            prefix = case["name"] + "/" + engine + "/"
            request_bytes = retained[prefix + "request.json"]
            assert json.loads(request_bytes) == case["request"]
            report = reports[engine] = json.loads(retained[prefix + "report.json"])
            assert report["engine"] == engine
            assert report["request_sha256"] == digest(request_bytes)
            assert report["outcome"] == row["outcome"]
            for key, expected in case["expected"].items():
                assert report["outcome"][key] == expected
            executions[engine] = None
            if report["outcome"]["kind"] == "Refused":
                assert report["verification"]["status"] == "NotRun"
                assert "execution" not in report
                assert retained[prefix + "admission.stderr.txt"].decode().splitlines()[0] == report["outcome"]["reason"]
                continue
            execution_bytes = retained[report["execution"]["artifact"]]
            assert digest(execution_bytes) == report["execution"]["sha256"]
            execution = executions[engine] = json.loads(execution_bytes)
            receipt = json.loads(retained[report["verification"]["artifact"]])
            admission = json.loads(retained[prefix + "admission.adva"])
            assert admission["fuel"] == admission["state"]["spent"] == 0
            assert admission["status"] == "FuelExhausted"
            for key in ("program", "input", "fuel"):
                assert execution[key] == case["request"][key]
            assert observe(execution) == report["outcome"]
            assert execution["status"] == report["native_status"]
            assert execution["profile"] == receipt["profile"] == native_profile(int(case["request"]["profile"][-1]))
            assert receipt["state"] == execution["state"]
            steps = receipt["verified_steps"]
            assert steps == execution["state"]["spent"] == len(execution["trace"])
            assert steps == report["verification"]["verified_steps"] == row["steps"][engine]
            total_steps += steps
            receipts += 1
        receive_pair(reports["rust"], reports["python"], executions["rust"], executions["python"])
    assert receipts == 24 and total_steps == 478


def test_latest_acceptance_for_this_host_names_it():
    """A retained acceptance is one host's statement, so read this host's own.

    Records carry a host block from `local-07` on. A record produced elsewhere is
    not this host's acceptance: when no retained record was produced here, the
    gap is reported rather than passed or silently accepted.
    """
    newest = None
    for directory, report in retained_acceptances():
        host = report.get("host")
        if host and host.get("platform") == sys.platform:
            newest = (directory, report)
    if newest is None:
        pytest.skip(f"no retained acceptance carries a host block for {sys.platform}")
    _, report = newest
    host = report["host"]
    assert host["platform"] == sys.platform
    assert host["machine"] and host["release"] and host["python"]
    limits = report["cost"]["limits"]
    assert limits["address_space_limit_installed"] == (sys.platform == "linux")
    assert limits["address_space_per_child"] == 1073741824


def retained_acceptances():
    """Every archived acceptance, oldest first, with its recorded host block."""
    found = []
    for directory in sorted(EVIDENCE.iterdir()):
        report_path = directory / "report.json"
        if report_path.is_file():
            found.append((directory, json.loads(report_path.read_bytes())))
    return found


def test_latest_acceptance_contains_current_adapter_sources():
    directory, _ = retained_acceptances()[-1]
    retained = receive(directory)
    manifest = json.loads(retained["source-manifest.json"])
    assert set(manifest) == {str(p.relative_to(ROOT)) for p in (ROOT / "toolchain").glob("*.py")}
    for path, expected in manifest.items():
        assert digest((ROOT / path).read_bytes()) == expected


@pytest.mark.parametrize("field", ("trace", "state"))
def test_equal_return_value_does_not_hide_changed_history(field):
    retained = receive(EVIDENCE / "local-03")
    prefix = "exact-integer/"
    left = json.loads(retained[prefix + "rust/report.json"])
    right = json.loads(retained[prefix + "python/report.json"])
    left_raw = json.loads(retained[left["execution"]["artifact"]])
    right_raw = deepcopy(json.loads(retained[right["execution"]["artifact"]]))
    if field == "trace":
        right_raw["trace"][0]["state_digest"] = "0" * 64
    else:
        right_raw["state"]["pc"] += 1
    assert observe(left_raw) == observe(right_raw)
    with pytest.raises(ValueError, match=field + " correspondence"):
        receive_pair(left, right, left_raw, right_raw)


def test_mutated_archive_is_refused_before_receiving_reports(tmp_path):
    for name in ("manifest.json", "complete.tar.gz"):
        shutil.copyfile(EVIDENCE / "local-03" / name, tmp_path / name)
    archive = tmp_path / "complete.tar.gz"
    content = bytearray(archive.read_bytes())
    content[-1] ^= 1
    archive.write_bytes(content)
    with pytest.raises(ValueError, match="archive digest"):
        receive(tmp_path)
