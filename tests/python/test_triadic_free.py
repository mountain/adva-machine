"""Finite free-process controls; no native free or participant acceptance.

Original tests by ChatGPT (OpenAI), contributed under Unknown v0.3 through
Mingli Yuan's authorized account proxy; not his review or endorsement.
"""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from experiments.triadic_free.calibration import execute, preflight, strict_json
from experiments.triadic_free.model import Account, Refused, check_case, digest, run_case


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "experiments/triadic_free/contract-v0.json"


@pytest.fixture
def contract():
    return json.loads(CONTRACT.read_bytes())


def successful(contract):
    case = contract["cases"][0]
    return case, run_case(contract, case, Account())


def rehash(frames):
    parent = None
    for index, frame in enumerate(frames):
        frame["parent"], frame["sequence"] = parent, index
        frame["sha256"] = digest({k: v for k, v in frame.items() if k != "sha256"})
        parent = frame["sha256"]


def test_pinned_cases_execute_and_replay_with_separate_outcomes(contract):
    account = Account()
    status, reports = execute(contract, account)
    assert status == "CompletedCalibration"
    assert len(reports) == 10 and all(r["expected_matched"] for r in reports)
    statuses = [r["observed"]["status"] for r in reports]
    assert statuses.count("FiniteBalanceWitness") == 4
    assert statuses.count("BlockedByResidual") == 1
    assert statuses.count("Unknown") == 5
    assert 0 < account.work < account.max_work
    assert all(r["observed"]["permitted_external_effects"] == [] for r in reports)


def test_balance_has_nonzero_energy_and_boundary_reaction(contract):
    case, report = successful(contract)
    assert [f["charge"] for f in report["frames"]] == [[2, 0], [2, 1]]
    assert [f["observations"]["C"]["energy"] for f in report["frames"]] == [4, 3]
    final = report["frames"][-1]
    assert all(o["directional_pressure"] == 0 for o in final["observations"].values())
    p, q = final["charge"]
    assert 2 * p - q == 3  # pressure along the fixed direction need not vanish
    assert check_case(contract, case, report, Account())["minimum_energy_if_balanced"] == 3


def test_all_finite_starts_reach_the_same_anchored_minimum(contract):
    for q in range(-2, 5):
        case = dict(contract["cases"][0], start_q=q)
        report = run_case(contract, case, Account())
        check_case(contract, case, report, Account())
        assert report["status"] == "FiniteBalanceWitness"
        assert report["frames"][-1]["charge"] == [2, 1]
        assert report["updates"] == abs(q - 1)


def test_hidden_energy_blocks_while_coarse_observation_is_constant(contract):
    case = contract["cases"][4]
    report = run_case(contract, case, Account())
    frame = report["frames"][0]
    assert frame["coarse_hidden_directional_energy"] == [0, 0, 0]
    assert frame["hidden_directional_energy"] == [4, 4, 4]
    assert frame["observations"]["C"]["directional_pressure"] == 0
    assert report["status"] == "BlockedByResidual" and report["updates"] == 0
    check_case(contract, case, report, Account())


def test_nonblocking_residual_stays_in_the_witness(contract):
    case = contract["cases"][3]
    report = run_case(contract, case, Account())
    assert report["status"] == "FiniteBalanceWitness"
    assert report["frames"][-1]["hidden_directional_energy"] == [4, 4, 4]
    assert report["permitted_external_effects"] == []


@pytest.mark.parametrize("index,reason", [
    (5, "ResidualMeasurementUnavailable"), (6, "SideObservationUnavailable"),
    (7, "HumanAcceptanceUnavailable"), (8, "UpdateBudgetExhausted"),
    (9, "UpdateBudgetExhausted"),
])
def test_missing_requirements_and_exhaustion_cannot_be_promoted(contract, index, reason):
    case = contract["cases"][index]
    report = run_case(contract, case, Account())
    assert (report["status"], report["reason"]) == ("Unknown", reason)
    if index == 9:
        assert [f["charge"] for f in report["frames"]] == [[2, 4], [2, 3]]
    report["status"], report["reason"] = "FiniteBalanceWitness", "AnchoredPressureBalanced"
    with pytest.raises(Refused, match="terminal"):
        check_case(contract, case, report, Account())


@pytest.mark.parametrize("attack", [
    "anchor", "zero-state", "chart", "pressure", "energy", "residual", "extra-field",
    "reset-history", "skip-state", "boolean-coordinate", "native-authority", "effect",
])
def test_rehashed_forgeries_do_not_pass_relation_replay(contract, attack):
    case, report = successful(contract)
    frame = report["frames"][-1]
    if attack == "anchor":
        frame["anchor_binding"] = "0" * 64
    elif attack == "zero-state":
        frame["charge"] = [0, 0]
    elif attack == "chart":
        frame["observations"]["T"]["coordinates"] = [-2, -1]
    elif attack == "pressure":
        frame["observations"]["S"]["directional_pressure"] = 1
    elif attack == "energy":
        frame["observations"]["C"]["energy"] = 0
    elif attack == "residual":
        frame["hidden_amplitude"] = 1
    elif attack == "extra-field":
        frame["discharged_all_obligations"] = True
    elif attack == "reset-history":
        report["frames"] = [frame]
        report["updates"] = 0
    elif attack == "skip-state":
        frame["charge"] = [2, 3]
    elif attack == "boolean-coordinate":
        frame["charge"] = [2, True]
    elif attack == "native-authority":
        report["native_free"] = "FreeAccepted"
    elif attack == "effect":
        report["permitted_external_effects"] = ["delete-source"]
    rehash(report["frames"])
    with pytest.raises(Refused):
        check_case(contract, case, report, Account())


def test_removing_hidden_residual_and_repinning_trace_is_refused(contract):
    case = contract["cases"][4]
    report = run_case(contract, case, Account())
    report["frames"][0]["hidden_amplitude"] = 0
    report["frames"][0]["hidden_directional_energy"] = [0, 0, 0]
    report["status"], report["reason"] = "FiniteBalanceWitness", "AnchoredPressureBalanced"
    rehash(report["frames"])
    with pytest.raises(Refused, match="residual"):
        check_case(contract, case, report, Account())


def test_global_budget_keeps_partial_trace_and_never_issues_witness(contract):
    # One suite tick, one initial snapshot, then exhaustion while selecting a move.
    status, reports = execute(contract, Account(max_work=2))
    assert status == "Unknown"
    assert reports[0]["partial_frames"][0]["charge"] == [2, 0]
    assert reports[0]["partial_case_witness"] == "NotIssued"


def test_replay_exhaustion_keeps_candidate_without_certifying_it(contract):
    status, reports = execute(contract, Account(max_work=5))
    assert status == "Unknown"
    assert reports[0]["candidate_report"]["status"] == "FiniteBalanceWitness"
    assert reports[0]["partial_case_witness"] == "NotIssued"


def test_failed_replay_retains_proposed_trace_and_stops(contract, monkeypatch):
    def refuse(*_args):
        raise Refused("injected replay failure")

    monkeypatch.setattr("experiments.triadic_free.calibration.check_case", refuse)
    status, reports = execute(contract, Account())
    assert status == "CalibrationMismatch" and len(reports) == 1
    assert reports[0]["candidate_report"]["frames"][-1]["charge"] == [2, 1]
    assert reports[0]["partial_case_witness"] == "NotIssued"


def test_no_silent_anchor_or_contract_replacement(contract):
    case, report = successful(contract)
    changed = copy.deepcopy(contract)
    changed["anchor"]["fixed_p"] = 0
    with pytest.raises(Refused, match="anchor"):
        check_case(changed, case, report, Account())
    changed = copy.deepcopy(contract)
    changed["cases"][0]["max_updates"] = 7
    with pytest.raises(Refused, match="binding"):
        check_case(changed, changed["cases"][0], report, Account())


def test_input_pin_and_duplicate_fields_are_checked():
    raw = CONTRACT.read_bytes()
    _, _, checked = preflight(CONTRACT, hashlib.sha256(raw).hexdigest())
    assert len(checked) >= 9
    with pytest.raises(Refused, match="pin"):
        preflight(CONTRACT, "0" * 64)
    with pytest.raises(Refused, match="duplicate"):
        strict_json(b'{"a":1,"a":2}')


def test_retained_report_replays_against_exact_contract_and_sources():
    report_path = ROOT / "experiments/triadic_free/evidence/run-01.json"
    raw = report_path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "449282a82b7c746a6bcd64a7d748177e4dddf0fae19e953623d449a3f0243f7c"
    report = strict_json(raw)
    _, contract, checked = preflight(CONTRACT, report["contract_sha256"])
    assert report["contract"] == contract and report["checked_inputs"] == checked
    assert report["status"] == "CompletedCalibration"
    assert len(report["cases"]) == len(contract["cases"]) == 10
    assert report["native_free"] == "NotImplemented"
    assert report["real_communication_events"] == 0
    assert report["human_acceptance"] == "NotObserved"
    assert report["permitted_external_effects"] == []
    account = Account()
    for case, retained in zip(contract["cases"], report["cases"]):
        assert case == retained["case"]
        assert check_case(contract, case, retained["observed"], account) == retained["replay"]
        assert retained["observed"]["status"] == case["expected"]
        assert retained["expected_matched"] is True


def test_cli_retains_report_and_refuses_overwrite(tmp_path):
    output = tmp_path / "result.json"
    command = [sys.executable, str(ROOT / "experiments/triadic_free/calibration.py"),
               "--contract", str(CONTRACT), "--expect-contract",
               hashlib.sha256(CONTRACT.read_bytes()).hexdigest(), "--output", str(output)]
    first = subprocess.run(command, capture_output=True, text=True, timeout=15, cwd=tmp_path)
    assert first.returncode == 0, first.stdout + first.stderr
    saved = output.read_bytes()
    report = json.loads(saved)
    assert report["status"] == "CompletedCalibration" and len(report["cases"]) == 10
    assert report["native_free"] == "NotImplemented" and report["real_communication_events"] == 0
    second = subprocess.run(command, capture_output=True, text=True, timeout=15)
    assert second.returncode == 2 and output.read_bytes() == saved


def test_report_cannot_be_written_inside_a_repository(tmp_path):
    (tmp_path / ".git").mkdir()
    output = tmp_path / "not-admitted.json"
    process = subprocess.run(
        [sys.executable, str(ROOT / "experiments/triadic_free/calibration.py"),
         "--contract", str(CONTRACT), "--expect-contract", hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
         "--output", str(output)], capture_output=True, text=True, timeout=15)
    assert process.returncode == 2 and not output.exists()
