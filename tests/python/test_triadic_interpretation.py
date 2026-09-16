"""Separate checks of retained theory evidence; no native semantic authority.

Original work by ChatGPT (OpenAI), under Unknown v0.3 through Mingli Yuan's
authorized account proxy; not his review or endorsement.
"""
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys

import pytest

from experiments.triadic_free.model import Account, Exhausted
from experiments.triadic_interpretation.calibration import calculate, common

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "experiments/triadic_interpretation/contract-v0.json"
REPORT = ROOT / "experiments/triadic_interpretation/evidence/run-01.json"


@pytest.fixture
def report():
    return json.loads(REPORT.read_bytes())


def test_report_bindings_and_scope(report):
    assert hashlib.sha256(REPORT.read_bytes()).hexdigest() == "d6c29ba8d7cd5da273fe9e32f43ed946feb9b6f2cd19d923228faa56c8f4806c"
    assert hashlib.sha256(CONTRACT.read_bytes()).hexdigest() == report["contract_sha256"]
    assert json.loads(CONTRACT.read_bytes()) == report["contract"]
    assert report["status"] == "CompletedFiniteChecks" and report["complete_family_witness"] is True
    assert report["reason"] is None and report["native_free"] == "NotImplemented"
    assert report["real_participant_or_world_observations"] == 0 and report["permitted_external_effects"] == []
    assert set(report["checked_inputs"]) == set(report["contract"]["sources"])
    for path, item in report["checked_inputs"].items():
        raw = (ROOT/path).read_bytes()
        assert item == {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
        assert item["sha256"] == report["contract"]["sources"][path]


def test_intersection_coverage_and_missing_evidence(report):
    rows = report["records"]["intersections"]
    assert len(rows) == 512
    assert {(a, b, w) for a, b, w, _, _ in rows} == set(itertools.product(range(8), repeat=3))
    for a, b, w, found, status in rows:
        expected = [i for i in range(3) if all(mask // (2**i) % 2 for mask in (a, b, w))]
        assert found == expected
        assert status == ("FiniteCommonInterpretation" if expected else "EmptyDeclaredFamily")
    for missing in range(3):
        sides = [[0], [0], [0]]
        sides[missing] = None
        assert common(*sides) == ("Unknown", None)
    sets = [{0, 1}, {1, 2}, {0, 2}]
    assert all(x & y for x, y in itertools.combinations(sets, 2)) and not set.intersection(*sets)
    assert common([0], [0], [1]) == ("EmptyDeclaredFamily", [])


def test_graph_results_against_all_short_vertex_sequences(report):
    rows = report["records"]["descent_graphs"]
    assert len(rows) == 192
    assert {(r["edges"], r["accepted"], r["start"]) for r in rows} == set(itertools.product(range(8), range(8), range(3)))
    for row in rows:
        edges = {e for bit, e in enumerate([(1, 0), (2, 0), (2, 1)]) if row["edges"] & 2**bit}
        accepted = {v for v in range(3) if row["accepted"] & 2**v}
        expected = []
        for length in (1, 2, 3):
            for path in itertools.product(range(3), repeat=length):
                if path[0] != row["start"] or any(v in accepted for v in path[:-1]):
                    continue
                if any(e not in edges for e in zip(path, path[1:])):
                    continue
                if path[-1] in accepted or not any(v == path[-1] for v, _ in edges):
                    expected.append(list(path))
        assert sorted(row["paths"]) == sorted(expected)
        assert row["sinks"] == sorted({p[-1] for p in expected})
        assert row["all_paths_accept"] == all(p[-1] in accepted for p in expected)
        assert row["worst_work"] == max(2*len(p)+1 for p in expected)
        assert all(len(p)-1 <= min(2, row["start"]) for p in expected)


def test_exact_quadratic_readings_and_contraction(report):
    rows = report["records"]["quadratics"]
    assert len(rows) == 48
    assert {tuple(r["weights"]) for r in rows} == set(itertools.product([1, 2], [1, 2], [0, 1, 2], [0, 1], [0, 1]))
    for row in rows:
        alpha, beta, gamma, la, lb = row["weights"]
        a, b = F(row["a"]), F(row["b"])
        assert alpha*a + gamma*(a-b) + la*(a+1) == 0
        assert beta*b + gamma*(b-a) + lb*(b-2) == 0
        assert F(row["energy"]) == alpha*a*a + beta*b*b + gamma*(a-b)**2 + la*(a+1)**2 + lb*(b-2)**2
        rho = F(gamma*gamma, (alpha+gamma+la)*(beta+gamma+lb))
        assert F(row["rho"]) == rho and 0 <= rho < 1
        assert [F(x) for x in row["b_errors"]] == [(3-b)*rho**n for n in range(5)]
    c = report["records"]["equilibrium_controls"]
    assert c["stationary_readings"] == [1, 1] and c["object"] == 0 and c["energy"] == 4
    assert c["object_equality_requirement"] == "Blocked"


def test_prefix_and_allocation_coverage(report):
    prefixes = report["records"]["future_prefixes"]
    expected = {p for n in range(6) for p in itertools.product((0, 1), repeat=n)}
    assert len(prefixes) == 63 and {tuple(left[:-1]) for left, _ in prefixes} == expected
    for left, right in prefixes:
        assert left[:-1] == right[:-1] and left[-1] == 0 and right[-1] == 1
    allocations = report["records"]["allocations"]
    assert len(allocations) == 1001
    for expected_budget, (budget, side, reserve) in enumerate(allocations):
        assert budget == expected_budget and side == (33*budget)//100
        assert 3*side + reserve == budget and F(reserve) >= F(budget, 100)
    assert allocations[100][2] == 1 < 2 <= allocations[300][2]
    assert report["records"]["reserve_control"]["actual_key_or_certificate_execution"] == "NotPerformed"


def test_exhaustion_retains_reached_records():
    records = {}
    with pytest.raises(Exhausted):
        calculate(Account(max_work=1), records)
    assert records == {"intersections": []}


def test_cli_refuses_wrong_contract_without_output(tmp_path):
    output = tmp_path / "refused.json"
    result = subprocess.run([sys.executable, "-m", "experiments.triadic_interpretation.calibration",
        "--contract", str(CONTRACT), "--expect-contract", "0"*64, "--output", str(output)],
        cwd=ROOT, text=True, capture_output=True, timeout=15)
    assert result.returncode == 2 and not output.exists()
    assert json.loads(result.stdout)["status"] == "Refused"
