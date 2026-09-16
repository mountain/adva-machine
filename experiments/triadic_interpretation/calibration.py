"""Finite checks of common interpretation and free's conditional theory.

Original work by ChatGPT (OpenAI), contributed under Unknown v0.3 through
Mingli Yuan's authorized account proxy; not his review or endorsement.
Invoke with python -m experiments.triadic_interpretation.calibration.
"""
import argparse
from fractions import Fraction as F
import hashlib
import itertools
import json
import os
from pathlib import Path
import resource
import signal
import sys
import time

from experiments.triadic_free.calibration import check_output, enforce_limits, read, strict_json
from experiments.triadic_free.model import Account, Exhausted, Refused, encode, require


ROOT = Path(__file__).resolve().parents[2]
LIMITS = {"wall_seconds": 10, "cooperative_seconds": 8, "cpu_seconds": 5,
          "address_space_bytes": 268435456, "max_work": 20000,
          "max_report_bytes": 524288, "max_contract_bytes": 32768,
          "max_source_bytes": 262144, "max_sources": 8,
          "automatic_retries": 0, "native_calls": 0}
FAMILY = {"candidate_count": 3, "graph_vertices": 3, "graph_edge_candidates": [[1, 0], [2, 0], [2, 1]],
          "object_weights": [1, 2], "coupling_weights": [0, 1, 2], "prior_weights": [0, 1],
          "displacements": [-1, 0, 1], "coordinate_rounds": 4,
          "max_prefix_length": 5, "max_integer_budget": 1000}
SOURCES = ["experiments/triadic_interpretation/calibration.py",
           "experiments/triadic_free/calibration.py", "experiments/triadic_free/model.py",
           "spec/framework/triadic-free-theory-v0.md", "spec/framework/triadic-context-v0.md"]


def common(a, b, w):
    if any(x is None for x in (a, b, w)):
        return "Unknown", None
    result = sorted(set(a) & set(b) & set(w))
    return ("FiniteCommonInterpretation" if result else "EmptyDeclaredFamily"), result


def paths(graph, start, accepted):
    if start in accepted or not graph[start]:
        return [[start]]
    return [[start] + tail for next_state in graph[start]
            for tail in paths(graph, next_state, accepted)]


def reachable_sinks(graph, start, accepted):
    pending, reached, sinks = [start], set(), set()
    while pending:
        v = pending.pop()
        if v in reached:
            continue
        reached.add(v)
        if v in accepted or not graph[v]:
            sinks.add(v)
        else:
            pending.extend(graph[v])
    return sorted(sinks)


def worst_work(graph, start, accepted):
    # One declared edge costs 2 units, terminal replay/recording costs 3.
    costs = {}
    for v in range(3):
        costs[v] = 3 if v in accepted or not graph[v] else max(2 + costs[u] for u in graph[v])
    return costs[start]


def energy(a, b, alpha, beta, gamma, la, lb, a0=-1, b0=2, w=0):
    return alpha*(a-w)**2 + beta*(b-w)**2 + gamma*(a-b)**2 + la*(a-a0)**2 + lb*(b-b0)**2


def equilibrium(alpha, beta, gamma, la, lb, a0=-1, b0=2, w=0):
    da, db = alpha + gamma + la, beta + gamma + lb
    ra, rb = alpha*w + la*a0, beta*w + lb*b0
    delta = da*db - gamma*gamma
    require(alpha > 0 and beta > 0 and min(gamma, la, lb) >= 0, "unsupported quadratic")
    return F(db*ra + gamma*rb, delta), F(gamma*ra + da*rb, delta)


def calculate(account, records):
    def check(condition, name):
        account.tick()
        require(condition, name)

    subsets = [[i for i in range(3) if mask & (1 << i)] for mask in range(8)]
    records["intersections"] = []
    for ia, ib, iw in itertools.product(range(8), repeat=3):
        status, result = common(subsets[ia], subsets[ib], subsets[iw])
        expected = [i for i in range(3) if (ia & ib & iw) & (1 << i)]
        check(result == expected, "set/bitmask intersection mismatch")
        check(status == ("FiniteCommonInterpretation" if expected else "EmptyDeclaredFamily"), "existence status mismatch")
        records["intersections"].append([ia, ib, iw, result, status])
    pairwise = [[0, 1], [1, 2], [0, 2]]
    check(all(set(x) & set(y) for x, y in itertools.combinations(pairwise, 2)), "pairwise control")
    check(common(*pairwise) == ("EmptyDeclaredFamily", []), "pairwise promoted to triple")
    check(common([0], [0], [1]) == ("EmptyDeclaredFamily", []), "consensus overrides object")
    check(common([0], [0], None) == ("Unknown", None), "missing object promoted")
    check(common([0], None, [0]) == ("Unknown", None), "missing participant promoted")
    records["interpretation_controls"] = {"pairwise_sets": pairwise, "pairwise_common": [],
        "participant_consensus": [0], "object_allows": [1], "consensus_common": [],
        "missing_object": "Unknown", "missing_participant": "Unknown"}

    records["descent_graphs"] = []
    for mask in range(8):
        graph = {v: [] for v in range(3)}
        for bit, (v, u) in enumerate(FAMILY["graph_edge_candidates"]):
            if mask & (1 << bit):
                graph[v].append(u)
        for accepted_mask in range(8):
            accepted = subsets[accepted_mask]
            for start in range(3):
                trajectories = paths(graph, start, accepted)
                sinks = reachable_sinks(graph, start, accepted)
                all_accept = all(p[-1] in accepted for p in trajectories)
                check(all_accept == all(v in accepted for v in sinks), "sink theorem mismatch")
                check(sorted({p[-1] for p in trajectories}) == sinks, "path coverage mismatch")
                check(all(len(p)-1 <= min(2, start) for p in trajectories), "rank bound mismatch")
                cost = worst_work(graph, start, accepted)
                check(cost == max(2*(len(p)-1)+3 for p in trajectories), "backward cost mismatch")
                check(all(2*(len(p)-1)+3 <= cost for p in trajectories), "sufficient cost failed")
                check(any(2*(len(p)-1)+3 > cost-1 for p in trajectories), "worst path missing")
                records["descent_graphs"].append({"edges": mask, "accepted": accepted_mask,
                    "start": start, "paths": trajectories, "sinks": sinks,
                    "all_paths_accept": all_accept, "worst_work": cost})
    route, potential = [[0, 1], [1, 2]], [1, 2, 0]
    descent = [e for e in route if potential[e[1]] < potential[e[0]]]
    check(descent == [[1, 2]], "barrier counterexample missing")
    records["descent_barrier"] = {"allowed_edges": route, "potential": potential,
        "accepted": [2], "start": 0, "descending_edges": descent, "start_is_unacceptable_sink": True}

    records["quadratics"] = []
    for alpha, beta, gamma, la, lb in itertools.product([1, 2], [1, 2], [0, 1, 2], [0, 1], [0, 1]):
        a, b = equilibrium(alpha, beta, gamma, la, lb)
        da, db, ra, rb = alpha+gamma+la, beta+gamma+lb, -la, 2*lb
        check(alpha*a + gamma*(a-b) + la*(a+1) == 0, "A pressure nonzero")
        check(beta*b + gamma*(b-a) + lb*(b-2) == 0, "B pressure nonzero")
        base = energy(a, b, alpha, beta, gamma, la, lb)
        for h, k in itertools.product([-1, 0, 1], repeat=2):
            diff = energy(a+h, b+k, alpha, beta, gamma, la, lb) - base
            expected = (alpha+la)*h*h + (beta+lb)*k*k + gamma*(h-k)**2
            check(diff == expected and (diff > 0 if (h, k) != (0, 0) else diff == 0), "minimum identity failed")
        rho = F(gamma*gamma, da*db)
        check(0 <= rho < 1, "contraction coefficient outside bound")
        current = F(3)
        errors = [str(current-b)]
        for _ in range(4):
            next_a = (ra + gamma*current) / da
            next_b = (rb + gamma*next_a) / db
            check(next_b-b == rho*(current-b), "contraction identity failed")
            current = next_b
            errors.append(str(current-b))
        records["quadratics"].append({"weights": [alpha, beta, gamma, la, lb],
            "a": str(a), "b": str(b), "energy": str(base), "rho": str(rho), "b_errors": errors})
    a, b = equilibrium(1, 1, 1, 1, 1, a0=2, b0=2)
    check((a, b) == (1, 1) and energy(a, b, 1, 1, 1, 1, 1, a0=2, b0=2) == 4, "blocked equilibrium missing")
    check(a != 0 and b != 0, "equilibrium falsely equals object")
    check(all((a-b)**2 == 0 for a, b in [(-1, -1), (0, 0), (1, 1)]), "unanchored degeneracy missing")
    records["equilibrium_controls"] = {"object": 0, "soft_references": [2, 2],
        "stationary_readings": [1, 1], "energy": 4, "object_equality_requirement": "Blocked",
        "no_object_no_prior_consensuses": [[-1, -1], [0, 0], [1, 1]],
        "contraction_nonfinite_example": {"rho": "1/9", "initial_error": "1", "finite_n_error": "1/9^n"}}

    records["future_prefixes"] = []
    for length in range(6):
        for prefix in itertools.product([0, 1], repeat=length):
            left, right = list(prefix) + [0], list(prefix) + [1]
            check(left[:-1] == right[:-1] and left[-1] != right[-1], "indistinguishable prefix missing")
            records["future_prefixes"].append([left, right])

    records["allocations"] = []
    for budget in range(1001):
        side = 33*budget//100
        reserve = budget-3*side
        check(3*side+reserve == budget and 100*reserve >= budget, "reserve allocation failed")
        records["allocations"].append([budget, side, reserve])
    check(records["allocations"][100][2] < 2 <= records["allocations"][300][2], "reserve insufficiency control")
    records["reserve_control"] = {"declared_join_work": 2, "budget_100_reserve": 1,
        "budget_100_join": "UnknownInsufficientReserve", "required_failed_join_effect": "retain-previous-committed-head",
        "budget_300_reserve": 3, "budget_300_can_fund_declared_join": True,
        "actual_key_or_certificate_execution": "NotPerformed"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--expect-contract", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    started, cpu = time.monotonic(), time.process_time()
    try:
        enforce_limits()  # Same hard OS limits as the pinned earlier runner.
        target = check_output(args.output)
        raw = read(args.contract, LIMITS["max_contract_bytes"])
        require(hashlib.sha256(raw).hexdigest() == args.expect_contract, "contract pin mismatch")
        contract = strict_json(raw)
        require(contract["schema"] == "adva.triadic-interpretation.contract.v0", "unsupported schema")
        require(encode(contract["limits"]) == encode(LIMITS) and
                encode(contract["family"]) == encode(FAMILY), "changed finite contract")
        require(set(contract["sources"]) == set(SOURCES), "source inventory mismatch")
        checked = {}
        for path in SOURCES:
            payload = read(ROOT/path, LIMITS["max_source_bytes"])
            sha = hashlib.sha256(payload).hexdigest()
            require(sha == contract["sources"][path], "source pin mismatch: " + path)
            checked[path] = {"sha256": sha, "bytes": len(payload)}
        account = Account(max_work=LIMITS["max_work"], started=started)
        records, status, reason = {}, "CompletedFiniteChecks", None
        try:
            calculate(account, records)
        except (Exhausted, Refused) as error:
            status = "Unknown" if isinstance(error, Exhausted) else "CalibrationMismatch"
            reason = str(error)
        result = {"schema": "adva.triadic-interpretation.report.v0", "status": status, "reason": reason,
            "contract": contract, "contract_sha256": args.expect_contract, "checked_inputs": checked,
            "records": records, "complete_family_witness": status == "CompletedFiniteChecks",
            "authority": "external-exact-finite-calibration", "native_free": "NotImplemented",
            "real_participant_or_world_observations": 0, "permitted_external_effects": [],
            "costs": {"check_work_units": account.work, "wall_seconds_before_final_write": time.monotonic()-started,
                "cpu_seconds_before_final_write": time.process_time()-cpu,
                "peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                "native_calls": 0, "automatic_retries": 0}, "python_version": sys.version}
        output = encode(result)
        require(len(output) <= LIMITS["max_report_bytes"] , "report exceeds bound")
        with target.open("xb") as stream:
            stream.write(output)
            stream.flush()
            os.fsync(stream.fileno())
        print(json.dumps({"status": status, "report": str(target), "bytes": len(output),
            "sha256": hashlib.sha256(output).hexdigest(), "work_units": account.work}))
        return 0 if status == "CompletedFiniteChecks" else 3 if status == "Unknown" else 2
    except (Refused, ValueError, TypeError, KeyError, RecursionError) as error:
        print(json.dumps({"status": "Refused", "reason": str(error)}))
        return 2
    except (Exhausted, OSError, MemoryError) as error:
        print(json.dumps({"status": "Unknown", "reason": str(error)}))
        return 3
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    raise SystemExit(main())
