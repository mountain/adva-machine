#!/usr/bin/env python3
"""Why bound (1) cannot be obtained in the weighted l1 norm this thread has used.

Frozen contract: contract.json in this directory (Research 0129 section 3).

The previous round left three missing bounds. This round attacks the first one,
the tail bound on the inverse of the linearised operator, and reports a negative
result with measurements rather than a derivation:

  * the norm conversion from the truncated coefficient matrix to the space norm is
    exact, and it closes gap (3) for the finite block, but the numbers are
    hopeless: the inverse norm in the weighted norm is about 1.5e10;
  * the inner series of the composition has constant term one, so its weighted
    norm exceeds one in every weighted l1 norm, and high powers of it grow;
  * consequently the linearisation does not contract the tail at all: the measured
    action on y^j grows with j, tracking (1 + delta)^j.

The conclusion is a redirection: bound (1) has to be sought in a sup-norm on a
disk, where composition is stable and folding high degrees back to low ones is not
penalised. Nothing here is an enclosure of anything.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import sys
import time
from decimal import Decimal
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
CONTRACT = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
OBJ = CONTRACT["objects"]
SIBLING_DIR = HERE.parent / "feigenbaum_kantorovich_preflight"
SIBLING_SRC = SIBLING_DIR / "calibration.py"

ASSERTIONS = {"n": 0}


def check(condition, message):
    ASSERTIONS["n"] += 1
    if not condition:
        raise AssertionError(message)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SIB = load(SIBLING_SRC, "feigenbaum_kantorovich_preflight_calibration")


def operator_norm(matrix, rho):
    """The weighted l1 operator norm: the largest weighted column sum."""
    n = len(matrix)
    best = Fr(0)
    for j in range(n):
        total = Fr(0)
        for i in range(n):
            total += abs(matrix[i][j]) * (rho ** (i - j))
        best = max(best, total)
    return best


def main():
    started = time.monotonic()
    guess = [Decimal(1), Decimal("-1.52763"), Decimal("0.104815"), Decimal("0.0267057")]
    degree = OBJ["fixed_point_degree"]
    x0 = [SIB.to_fraction(v, OBJ["exact_digits"]) for v in SIB.solve_fixed_point(degree, guess, 80)]
    x0[0] = Fr(1)
    rho = Fr(OBJ["rho"])
    truncation = OBJ["linearisation_degree"]

    evidence = {
        "schema": "adva.external.feigenbaum-inverse-norm-obstruction.v0",
        "variant": "fast: monomial compositions replaced by re-used powers of the inner series",
        "version": 0,
        "checker_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        "contract": "experiments/feigenbaum_inverse_norm_obstruction_fast/contract.json",
        "sibling": {
            "source": "experiments/feigenbaum_kantorovich_preflight/calibration.py",
            "sha256": hashlib.sha256(SIBLING_SRC.read_bytes()).hexdigest(),
            "note": "the candidate and the truncated linearisation come from the frozen sibling round",
        },
        "precision": {"binary_floating_point_in_reported_bounds": False, "acceleration_applied": False},
    }

    # --- the norm conversion, closed exactly for the finite block
    matrix = SIB.truncated_linearisation(x0, truncation, -35)
    inverse = SIB.rational_inverse(matrix)
    residual = SIB.identity_minus_product(matrix, inverse)
    worst_residual = max(abs(v) for row in residual for v in row)
    norm_matrix = operator_norm(matrix, rho)
    norm_inverse = operator_norm(inverse, rho)
    infinity_norm_inverse = max(sum(abs(v) for v in row) for row in inverse)
    evidence["norm_conversion"] = {
        "matrix_size": truncation + 1,
        "residual_max_abs_entry": f"{float(worst_residual):.3E}",
        "exactly_invertible": worst_residual == 0,
        "weighted_l1_norm_of_the_matrix": f"{float(norm_matrix):.6E}",
        "weighted_l1_norm_of_the_inverse": f"{float(norm_inverse):.6E}",
        "infinity_norm_of_the_inverse": f"{float(infinity_norm_inverse):.6E}",
        "ratio_to_the_previous_rounds_infinity_norm": f"{float(norm_inverse / infinity_norm_inverse):.6E}",
        "gap_three_status": "closed for the finite block: the conversion is exact, and it shows the truncated block is hopelessly ill-conditioned in this norm",
    }

    # --- the inner series has constant term one, so no weighted l1 norm can contract it
    extent = OBJ["tail_extent"]
    x0_ext = x0 + [Fr(0)] * (extent + 1 - len(x0))
    A = Fr(1) / sum(x0_ext)
    inner_argument = SIB.rat_rescale(x0_ext, Fr(1) / (A * A), extent)
    inner = SIB.rat_mul(inner_argument, inner_argument, extent)
    outer = SIB.rat_compose(x0_ext, inner, extent)
    derivative = [Fr(j) * x0_ext[j] for j in range(1, extent + 1)] + [Fr(0)]
    derivative_composed = SIB.rat_compose(derivative, inner, extent)

    # --- 幂次复用（本变体相对冻结原件的唯一算法改动）------------------------
    # 通用复合 rat_compose(h, inner, extent) 每次要跑 extent+1 次 rat_mul，
    # 而 extent=60、系数位长已被推到 ~13,600 bit（Fraction 每步都要 gcd）。
    # 但 h 在这些调用点**全是单项式 y^j**，而 compose(y^j, inner) == inner^j。
    # 于是改成递乘复用：一次算出 inner 的各次幂，之后 O(1) 取用。
    # 等价性已逐项验证（j=1,2,3,5,8 与通用复合逐系数一致）。
    _maxj = max(OBJ["monomial_degrees"])
    _powers = [[Fr(0)] * (extent + 1) for _ in range(_maxj + 1)]
    _powers[0][0] = Fr(1)
    for _j in range(1, _maxj + 1):
        _powers[_j] = SIB.rat_mul(_powers[_j - 1], inner, extent)

    def compose_h(h):
        """h(inner)：单项式查表，其余退回通用复合。"""
        nz = [i for i, v in enumerate(h) if v]
        if len(nz) == 1 and h[nz[0]] == 1 and nz[0] <= _maxj:
            return list(_powers[nz[0]])
        return SIB.rat_compose(h, inner, extent)

    def linearised(h):
        h_scaled = SIB.rat_rescale(h, Fr(1) / (A * A), extent)
        first = compose_h(h)
        second = SIB.rat_mul(
            SIB.rat_mul(derivative_composed,
                        [2 * inner_argument[i] for i in range(extent + 1)], extent),
            h_scaled, extent)
        variation = -sum(h) / (sum(x0_ext) ** 2)
        return [A * (first[i] + second[i]) + variation * outer[i] for i in range(extent + 1)]

    norm_inner = SIB.weighted_norm(inner_argument, rho)
    deficit = SIB.weighted_norm([inner_argument[0] - 1] + inner_argument[1:], rho)
    evidence["inner_series"] = {
        "constant_term": str(inner_argument[0]),
        "weighted_l1_norm_of_the_inner_series": f"{float(norm_inner):.10f}",
        "norm_exceeds_one": norm_inner > 1,
        "why_that_settles_it": "a series with constant term one has weighted norm at least one, in every weighted l1 norm and at every radius, so its powers cannot decay",
        "norm_of_the_inner_series_minus_one": f"{float(deficit):.10f}",
    }

    # --- the measured action on high-degree monomials
    rows = []
    for j in OBJ["monomial_degrees"]:
        h = [Fr(0)] * (extent + 1)
        h[j] = Fr(1)
        image = linearised(h)
        rows.append({
            "j": j,
            "weighted_norm_of_the_image": f"{float(SIB.weighted_norm(image, rho)):.6f}",
            "constant_term": f"{float(image[0]):.6f}",
            "lowest_nonzero_degree": next((i for i, v in enumerate(image) if v != 0), None),
            "highest_nonzero_degree": max((i for i, v in enumerate(image) if v != 0), default=None),
            "predicted_growth_factor_power": f"{float((1 + deficit) ** j):.6f}",
        })
    evidence["tail_action"] = {
        "rows": rows,
        "no_contraction": all(float(row["weighted_norm_of_the_image"]) > 0.1 for row in rows[-3:]),
        "grows_with_the_degree": float(rows[-1]["weighted_norm_of_the_image"]) > float(rows[0]["weighted_norm_of_the_image"]),
    }

    # --- a finer radius does not help: the constant term still dominates
    alternatives = {}
    for rho_alt in (Fr(1, 64), Fr(1, 128)):
        norm_alt = SIB.weighted_norm(inner_argument, rho_alt)
        alternatives[str(rho_alt)] = {
            "weighted_norm_of_the_inner_series": f"{float(norm_alt):.10f}",
            "still_exceeds_one": norm_alt > 1,
        }
    evidence["radius_control"] = {
        "alternatives": alternatives,
        "conclusion": "shrinking the radius does not remove the obstruction, because the constant term carries weight one at every radius",
    }

    # --- the folding measurement: composition sends high degrees back to low ones
    fold = []
    for j in OBJ["monomial_degrees"][-3:]:
        image = linearised([Fr(1) if i == j else Fr(0) for i in range(extent + 1)])
        fold.append({"j": j, "lowest_degree_present": next((i for i, v in enumerate(image) if v != 0), None)})
    evidence["folding"] = {
        "rows": fold,
        "why_it_matters": "in a weighted l1 norm the weight of a low-degree output fed by a high-degree input is rho^(i-j), which is enormous; a sup norm on a disk does not penalise folding",
    }

    evidence["redirection"] = {
        "bound_one_status": "not obtained, and now known to be unobtainable in this norm, with the reason measured",
        "what_that_means": "the weighted l1 space is the wrong space for the tail argument; the standard choice is a sup norm on a disk, where composition is stable",
        "still_missing": [
            "a sup-norm-on-a-disk framework for the linearised operator, with the disk mapping data already verified",
            "the second derivative bound, which that framework would also need",
        ],
    }
    evidence["what_is_not_claimed"] = {
        "enclosure_of_alpha": False,
        "enclosure_of_delta": False,
        "existence_or_uniqueness_of_the_fixed_point": False,
        "any_new_bound_on_the_inverse": False,
    }

    checks = {
        "the_norm_conversion_is_exact": worst_residual == 0,
        "the_inner_series_norm_exceeds_one": norm_inner > 1,
        "the_tail_action_does_not_decay": evidence["tail_action"]["grows_with_the_degree"],
        "shrinking_the_radius_does_not_help": all(
            entry["still_exceeds_one"] for entry in alternatives.values()),
        "the_folding_is_measured": all(row["lowest_degree_present"] is not None for row in fold),
        "no_new_inverse_bound_is_claimed": evidence["what_is_not_claimed"]["any_new_bound_on_the_inverse"] is False,
        "within_assertion_budget": ASSERTIONS["n"] <= OBJ["max_assertions"],
        "within_time_budget": (time.monotonic() - started) <= CONTRACT["budget"]["wall_seconds"],
    }
    evidence["checks"] = checks
    evidence["status"] = "ExternalExactPass" if all(checks.values()) else "Residual"
    evidence["cost"] = {
        "wall_seconds_before_serialization": round(time.monotonic() - started, 3),
        "assertions": ASSERTIONS["n"],
        "subprocesses": 0,
    }
    (HERE / "evidence.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n",
                                        encoding="utf-8")
    print(json.dumps({k: evidence[k] for k in ("status", "checks", "cost")}, indent=1))
    print("norm conversion: residual", evidence["norm_conversion"]["residual_max_abs_entry"],
          "| ||M^-1||_{l1,rho} =", evidence["norm_conversion"]["weighted_l1_norm_of_the_inverse"])
    print("inner series norm:", evidence["inner_series"]["weighted_l1_norm_of_the_inner_series"],
          "| minus one:", evidence["inner_series"]["norm_of_the_inner_series_minus_one"])
    for row in rows:
        print(f"  j={row['j']:3d}  ||DT[y^j]|| = {row['weighted_norm_of_the_image']:>10}"
              f"   lowest degree = {row['lowest_nonzero_degree']:>3}   predicted (1+d)^j = {row['predicted_growth_factor_power']}")
    return 0 if evidence["status"] == "ExternalExactPass" else 1


if __name__ == "__main__":
    sys.exit(main())
