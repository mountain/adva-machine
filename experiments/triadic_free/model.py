"""An external finite calibration of the proposed free process, not native free.

Original work by ChatGPT (OpenAI), contributed under Unknown v0.3 through
Mingli Yuan's authorized account proxy; not his review or endorsement.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import time
from dataclasses import dataclass, field


SIDES = ("C", "S", "T")
CHARTS = {"C": [[1, 0], [0, 1]], "S": [[0, -1], [1, -1]],
          "T": [[-1, 1], [-1, 0]]}
OBLIGATIONS = ["fixed-anchor", "three-chart-correspondence", "allowed-motion",
               "retained-residual", "scoped-balance", "finite-account"]
ANCHOR = {
    "name": "a2-fixed-p-two-v0", "fixed_p": 2,
    "q_domain": list(range(-2, 5)), "charts": CHARTS,
    "allowed_direction": [0, 1], "period_energy": "p*p-p*q+q*q",
    "residual_model": "parity-cube-amplitude-v0",
    "phase_convention": "symbolic-marking-no-theta-evaluation",
    "obligations": OBLIGATIONS,
}


class Refused(ValueError):
    pass


class Exhausted(RuntimeError):
    pass


def require(ok, message):
    if not ok:
        raise Refused(message)


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode()


def digest(value):
    """A documentary binding only; never an Adva semantic identity."""
    return hashlib.sha256(encode(value)).hexdigest()


def fields(value, names):
    require(type(value) is dict and set(value) == set(names.split()), "unexpected fields")


def integer(value, low, high):
    require(type(value) is int and low <= value <= high, "integer outside finite domain")


@dataclass
class Account:
    max_work: int = 4096
    wall_seconds: float = 8
    work: int = 0
    started: float = field(default_factory=time.monotonic)

    def tick(self):
        if self.work >= self.max_work or time.monotonic() - self.started >= self.wall_seconds:
            raise Exhausted("finite calibration account exhausted")
        self.work += 1


def validate_case(case):
    fields(case, "id start_q hidden_amplitude max_hidden_directional available_sides "
                 "require_human max_updates expected")
    require(type(case["id"]) is str and 0 < len(case["id"]) <= 80, "invalid case name")
    integer(case["start_q"], -2, 4)
    if case["hidden_amplitude"] is not None:
        integer(case["hidden_amplitude"], 0, 4)
    integer(case["max_hidden_directional"], 0, 64)
    integer(case["max_updates"], 0, 8)
    require(type(case["require_human"]) is bool, "human requirement must be explicit")
    require(type(case["available_sides"]) is list and
            case["available_sides"] == [s for s in SIDES if s in case["available_sides"]],
            "sides must be a unique ordered subset")
    require(case["expected"] in {"FiniteBalanceWitness", "BlockedByResidual", "Unknown"},
            "invalid expected fixture outcome")


def binding(contract, case):
    return digest({"anchor": contract["anchor"], "case": case})


def energy(p, q):
    return p * p - p * q + q * q


def hidden_energies(amplitude):
    """The actual eight-vertex parity fixture; averaging hides all variation."""
    if amplitude is None:
        return None
    values = {v: amplitude * (sum(v) % 2) for v in itertools.product((0, 1), repeat=3)}
    result = []
    for axis in range(3):
        total = 0
        for v, value in values.items():
            if v[axis] == 0:
                w = list(v)
                w[axis] = 1
                total += (value - values[tuple(w)]) ** 2
        result.append(total)
    return result


def snapshot(contract, case, q, sequence, parent):
    p = contract["anchor"]["fixed_p"]
    observations = {}
    for side, matrix in contract["anchor"]["charts"].items():
        if side not in case["available_sides"]:
            observations[side] = None
            continue
        x, y = [a * p + b * q for a, b in matrix]
        direction = [row[1] for row in matrix]
        gradient = [2 * x - y, 2 * y - x]
        observations[side] = {
            "coordinates": [x, y], "energy": energy(x, y),
            "directional_pressure": sum(a * b for a, b in zip(gradient, direction)),
        }
    frame = {
        "sequence": sequence, "parent": parent, "anchor_binding": binding(contract, case),
        "charge": [p, q], "observations": observations,
        "hidden_amplitude": case["hidden_amplitude"],
        "hidden_directional_energy": hidden_energies(case["hidden_amplitude"]),
        "coarse_hidden_directional_energy": None if case["hidden_amplitude"] is None else [0, 0, 0],
    }
    return {**frame, "sha256": digest(frame)}


def disposition(case, frame, updates):
    if any(frame["observations"][side] is None for side in SIDES):
        return "Unknown", "SideObservationUnavailable"
    hidden = frame["hidden_directional_energy"]
    if hidden is None:
        return "Unknown", "ResidualMeasurementUnavailable"
    if any(value > case["max_hidden_directional"] for value in hidden):
        return "BlockedByResidual", "ResidualOutsideDeclaredAllowance"
    if frame["observations"]["C"]["directional_pressure"] == 0:
        if case["require_human"]:
            return "Unknown", "HumanAcceptanceUnavailable"
        return "FiniteBalanceWitness", "AnchoredPressureBalanced"
    if updates >= case["max_updates"]:
        return "Unknown", "UpdateBudgetExhausted"
    return None


def run_case(contract, case, account, frames=None):
    validate_case(case)
    frames = [] if frames is None else frames
    require(not frames, "a new finite case needs an empty trace")
    q = case["start_q"]
    for sequence in range(case["max_updates"] + 1):
        account.tick()
        frame = snapshot(contract, case, q, sequence, frames[-1]["sha256"] if frames else None)
        frames.append(frame)
        outcome = disposition(case, frame, sequence)
        if outcome:
            status, reason = outcome
            break
        candidates = []
        for next_q in (q - 1, q + 1):
            account.tick()
            if next_q in contract["anchor"]["q_domain"]:
                next_energy = energy(2, next_q)
                if next_energy < energy(2, q):
                    candidates.append((next_energy, next_q))
        if not candidates:
            status, reason = "Unknown", "NoAdmissibleDescent"
            break
        _, q = min(candidates)
    return {
        "case_id": case["id"], "contract_binding": digest(contract),
        "status": status, "reason": reason, "frames": frames,
        "updates": len(frames) - 1, "native_free": "NotImplemented",
        "human_acceptance": "NotObserved", "permitted_external_effects": [],
    }


def check_case(contract, case, report, account):
    """Replay with explicit coordinates and a finite energy table.

    The checker does not call snapshot, energy, hidden_energies, disposition or
    run_case. It shares integers, JSON and the host runtime with the producer.
    This is separate replay logic, not independent three-computation.
    """
    validate_case(case)
    require(encode(contract["anchor"]) == encode(ANCHOR), "unsupported anchor/profile")
    fields(report, "case_id contract_binding status reason frames updates native_free "
                   "human_acceptance permitted_external_effects")
    require(report["case_id"] == case["id"] and report["contract_binding"] == digest(contract),
            "case/contract binding mismatch")
    require(report["native_free"] == "NotImplemented" and
            report["human_acceptance"] == "NotObserved" and
            report["permitted_external_effects"] == [], "unsupported authority claim")
    frames = report["frames"]
    require(type(frames) is list and 1 <= len(frames) <= case["max_updates"] + 1,
            "invalid trace length")
    require(type(report["updates"]) is int and report["updates"] == len(frames) - 1,
            "update account mismatch")
    # With the fixed p=2 anchor, E(q)=(q-1)^2+3. This independent table also
    # witnesses a nonzero unique minimum over every declared admissible q.
    table = {q: (q - 1) ** 2 + 3 for q in range(-2, 5)}
    amplitude = case["hidden_amplitude"]
    hidden = None if amplitude is None else [4 * amplitude * amplitude] * 3
    parent = None
    previous_q = None
    for index, frame in enumerate(frames):
        account.tick()
        fields(frame, "sequence parent anchor_binding charge observations hidden_amplitude "
                      "hidden_directional_energy coarse_hidden_directional_energy sha256")
        payload = {k: v for k, v in frame.items() if k != "sha256"}
        require(frame["sha256"] == digest(payload), "frame binding mismatch")
        require(type(frame["sequence"]) is int and frame["sequence"] == index and
                frame["parent"] == parent, "history prefix mismatch")
        require(frame["anchor_binding"] == binding(contract, case), "anchor drift")
        require(type(frame["charge"]) is list and len(frame["charge"]) == 2,
                "invalid charge")
        p, q = frame["charge"]
        integer(p, 2, 2)
        integer(q, -2, 4)
        require(index != 0 or q == case["start_q"], "initial state changed")
        if previous_q is not None:
            require(abs(q - previous_q) == 1 and table[q] < table[previous_q],
                    "unpermitted or non-descending update")
        expected_coordinates = {"C": [2, q], "S": [-q, 2 - q], "T": [q - 2, -2]}
        expected = {side: ({"coordinates": expected_coordinates[side], "energy": table[q],
                           "directional_pressure": 2 * q - 2}
                          if side in case["available_sides"] else None) for side in SIDES}
        # Canonical bytes also distinguish booleans from integer observations.
        require(encode(frame["observations"]) == encode(expected), "chart/pressure mismatch")
        require(encode(frame["hidden_amplitude"]) == encode(amplitude) and
                encode(frame["hidden_directional_energy"]) == encode(hidden) and
                encode(frame["coarse_hidden_directional_energy"]) == encode(None if hidden is None else [0, 0, 0]),
                "residual erased or changed")
        if len(case["available_sides"]) < 3:
            expected_outcome = ("Unknown", "SideObservationUnavailable")
        elif hidden is None:
            expected_outcome = ("Unknown", "ResidualMeasurementUnavailable")
        elif max(hidden) > case["max_hidden_directional"]:
            expected_outcome = ("BlockedByResidual", "ResidualOutsideDeclaredAllowance")
        elif q == 1:
            require(all(table[q] <= e for e in table.values()), "minimum witness failed")
            expected_outcome = (("Unknown", "HumanAcceptanceUnavailable") if case["require_human"]
                                else ("FiniteBalanceWitness", "AnchoredPressureBalanced"))
        elif index >= case["max_updates"]:
            expected_outcome = ("Unknown", "UpdateBudgetExhausted")
        else:
            expected_outcome = None
        if index < len(frames) - 1:
            require(expected_outcome is None, "continued after terminal outcome")
        else:
            require(expected_outcome is not None and
                    (report["status"], report["reason"]) == expected_outcome,
                    "unearned terminal outcome")
        parent, previous_q = frame["sha256"], q
    return {"status": "ReplayMatchedFiniteModel", "frames_checked": len(frames),
            "minimum_energy_if_balanced": 3 if report["status"] == "FiniteBalanceWitness" else None}
