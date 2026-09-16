"""Run one pinned finite free-process calibration; write a fresh external report.

Original work by ChatGPT (OpenAI), contributed under Unknown v0.3 through
Mingli Yuan's authorized account proxy; not his review or endorsement.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import sys
import time

if __package__:
    from .model import ANCHOR, Account, Exhausted, Refused, check_case, encode, fields
    from .model import require, run_case, validate_case
else:
    from model import ANCHOR, Account, Exhausted, Refused, check_case, encode, fields
    from model import require, run_case, validate_case


ROOT = Path(__file__).resolve().parents[2]
LIMITS = {"wall_seconds": 10, "cooperative_seconds": 8, "cpu_seconds": 5,
          "address_space_bytes": 268435456, "max_work": 4096,
          "max_report_bytes": 524288, "max_contract_bytes": 32768,
          "max_reference_bytes": 262144, "max_reference_files": 16,
          "max_cases": 12, "max_updates_per_case": 8,
          "automatic_retries": 0, "native_calls": 0}
PRODUCERS = ["experiments/triadic_free/model.py", "experiments/triadic_free/calibration.py"]


def strict_json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate JSON field")
            result[key] = value
        return result

    def no_constant(value):
        raise Refused("nonfinite JSON constant")

    return json.loads(raw, object_pairs_hook=unique, parse_constant=no_constant)


def read(path, limit):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    require(len(raw) <= limit, "input byte bound exceeded")
    return raw


def validate_contract(contract):
    fields(contract, "schema profile authored_by contribution base_revision question level "
                     "assumptions cross_domain_boundary protected_obligations anchor limits "
                     "cases references producer_sources")
    require(contract["schema"] == "adva.free-process.calibration-contract.v0" and
            contract["profile"] == "finite-a2-free-v0", "unsupported profile")
    require(encode(contract["anchor"]) == encode(ANCHOR), "anchor/profile changed")
    require(encode(contract["limits"]) == encode(LIMITS), "unsupported resource contract")
    for key in ("authored_by", "contribution", "base_revision", "question", "level",
                "cross_domain_boundary"):
        require(type(contract[key]) is str and 0 < len(contract[key]) <= 4096, "missing contract text")
    for key in ("assumptions", "protected_obligations"):
        require(type(contract[key]) is list and 1 <= len(contract[key]) <= 16 and
                all(type(x) is str and 0 < len(x) <= 4096 for x in contract[key]),
                "missing scoped obligations")
    require(type(contract["cases"]) is list and 1 <= len(contract["cases"]) <= LIMITS["max_cases"],
            "case bound exceeded")
    ids = set()
    for case in contract["cases"]:
        validate_case(case)
        require(case["id"] not in ids, "duplicate case")
        ids.add(case["id"])
    require(type(contract["producer_sources"]) is dict and
            set(contract["producer_sources"]) == set(PRODUCERS), "missing producer pins")
    require(type(contract["references"]) is dict and
            1 <= len(contract["references"]) <= LIMITS["max_reference_files"] - len(PRODUCERS),
            "reference inventory outside bound")
    require(not set(contract["references"]) & set(PRODUCERS), "overlapping source roles")


def preflight(path, expected_sha256):
    raw = read(path, LIMITS["max_contract_bytes"])
    require(hashlib.sha256(raw).hexdigest() == expected_sha256, "independent contract pin mismatch")
    contract = strict_json(raw)
    validate_contract(contract)
    checked = {}
    for relative, expected in (contract["references"] | contract["producer_sources"]).items():
        item = Path(relative)
        require(not item.is_absolute() and ".." not in item.parts, "unsafe reference path")
        target = (ROOT / item).resolve()
        require(target.is_relative_to(ROOT), "reference leaves repository")
        payload = read(target, LIMITS["max_reference_bytes"])
        require(hashlib.sha256(payload).hexdigest() == expected, f"source pin mismatch: {relative}")
        checked[relative] = {"sha256": expected, "bytes": len(payload)}
    return raw, contract, checked


def check_output(path):
    target = path.expanduser().resolve()
    require(not target.exists() and not path.is_symlink(), "output already exists")
    require(target.parent.is_dir(), "output parent must already exist")
    for parent in (target.parent, *target.parent.parents):
        require(not (parent / ".git").exists() and
                not ((parent / "HEAD").is_file() and (parent / "objects").is_dir()),
                "candidate report must remain outside repository directories")
    return target


def execute(contract, account):
    validate_contract(contract)
    reports = []
    for case in contract["cases"]:
        partial_frames = []
        observed = None
        try:
            account.tick()
            observed = run_case(contract, case, account, partial_frames)
            replay = check_case(contract, case, observed, account)
            matched = observed["status"] == case["expected"]
            reports.append({"case": case, "observed": observed, "replay": replay,
                            "expected_matched": matched})
            if not matched:
                return "CalibrationMismatch", reports
        except Exhausted:
            # Completed prior cases remain inspectable. No witness is issued
            # for a case whose generation or replay did not finish.
            reports.append({"case": case, "status": "Unknown", "reason": "SupervisorBudget",
                            "partial_frames": partial_frames, "candidate_report": observed,
                            "partial_case_witness": "NotIssued"})
            return "Unknown", reports
        except Refused as error:
            reports.append({"case": case, "status": "Rejected", "reason": str(error),
                            "partial_frames": partial_frames, "candidate_report": observed,
                            "partial_case_witness": "NotIssued"})
            return "CalibrationMismatch", reports
    return "CompletedCalibration", reports


def enforce_limits():
    resource.setrlimit(resource.RLIMIT_CPU, (LIMITS["cpu_seconds"], LIMITS["cpu_seconds"]))
    resource.setrlimit(resource.RLIMIT_AS, (LIMITS["address_space_bytes"],) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (LIMITS["max_report_bytes"],) * 2)

    def deadline(_signum, _frame):
        raise Exhausted("wall deadline reached")

    signal.signal(signal.SIGALRM, deadline)
    signal.alarm(LIMITS["wall_seconds"])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--expect-contract", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    started_wall, started_cpu = time.monotonic(), time.process_time()
    try:
        enforce_limits()
        target = check_output(args.output)
        raw, contract, checked = preflight(args.contract, args.expect_contract)
        account = Account(started=started_wall)
        status, reports = execute(contract, account)
        result = {
            "schema": "adva.free-process.calibration-report.v0", "status": status,
            "contract_sha256": hashlib.sha256(raw).hexdigest(),
            "contract": contract, "checked_inputs": checked, "cases": reports,
            "authority": "external-finite-arithmetic-calibration",
            "native_free": "NotImplemented", "real_communication_events": 0,
            "human_acceptance": "NotObserved", "permitted_external_effects": [],
            "costs": {"work_units": account.work,
                      "wall_seconds_before_final_write": time.monotonic() - started_wall,
                      "cpu_seconds_before_final_write": time.process_time() - started_cpu,
                      "peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                      "native_calls": 0, "automatic_retries": 0},
            "python_version": sys.version,
        }
        encoded = encode(result)
        require(len(encoded) <= LIMITS["max_report_bytes"], "report exceeds byte budget")
        # Exclusive creation preserves any previous report. A failed final write
        # may leave a partial file; no successful completion is then printed.
        with target.open("xb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        print(json.dumps({"status": status, "report": str(target), "cases": len(reports),
                          "sha256": hashlib.sha256(encoded).hexdigest()}))
        return 0 if status == "CompletedCalibration" else 3 if status == "Unknown" else 2
    except (Refused, ValueError, TypeError, RecursionError) as error:
        print(json.dumps({"status": "Refused", "reason": str(error)}))
        return 2
    except (Exhausted, OSError, MemoryError) as error:
        print(json.dumps({"status": "Unknown", "reason": str(error)}))
        return 3
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    raise SystemExit(main())
