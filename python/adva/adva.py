"""Outer CLI for bounded Adva research and external verifier orchestration.

Invoke this file directly; importing the package still requires its PyO3 kernel.
This adapter checks the protocol, never primality, arithmetic, or native free.
The executable is a trusted local backend, not an untrusted-program sandbox.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import sys
import tempfile
import time

INPUT_LIMIT, OUTPUT_LIMIT = 16_384, 262_144
REQUEST_KEYS = {"schema", "version", "primes", "n", "q", "k", "fuel"}
RESULT_KEYS = {"schema", "version", "request", "status", "reason", "fuel_spent",
               "fuel_remaining", "input_divisor_checks", "q_divisor_checks",
               "native_universe", "native_free", "allowed_action"}
EXIT_CODES = {"FiniteExtensionVerified": 0, "Blocked": 2, "Unknown": 3}


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _constant(_):
    raise ValueError("non-finite JSON constant")


def _decode(raw):
    return json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                      parse_constant=_constant)


def _read(path, limit):
    with open(path, "rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise ValueError("file exceeds declared byte limit")
    return raw


def _request(raw):
    obj = _decode(raw)
    if not isinstance(obj, dict) or set(obj) != REQUEST_KEYS:
        raise ValueError("request keys do not match research profile")
    if obj["schema"] != "adva.prime-extension.request.research" or type(obj["version"]) is not int or obj["version"] != 0:
        raise ValueError("unsupported request schema/version")
    if not isinstance(obj["primes"], list) or any(type(p) is not int for p in obj["primes"]):
        raise ValueError("primes must be an integer array")
    if any(type(obj[k]) is not int for k in ("n", "q", "k", "fuel")):
        raise ValueError("n, q, k, fuel must be integers")
    if len(obj["primes"]) > 6 or any(not 0 <= value < 2**64 for value in obj["primes"] + [obj["n"], obj["q"], obj["k"]]):
        raise ValueError("transport accepts at most six primes and unsigned 64-bit values")
    if not 0 <= obj["fuel"] <= 1024:
        raise ValueError("transport fuel must be between 0 and 1024")
    return obj


def _result(raw, request, returncode):
    obj = _decode(raw)
    if not isinstance(obj, dict) or set(obj) != RESULT_KEYS:
        raise ValueError("native result keys do not match research profile")
    if obj["schema"] != "adva.prime-extension.result.research" or type(obj["version"]) is not int or obj["version"] != 0:
        raise ValueError("unsupported result schema/version")
    # Revalidate the echo to reject bool/int equality and malformed envelopes.
    echo = _request(json.dumps(obj["request"], allow_nan=False).encode())
    if echo != request:
        raise ValueError("native result does not bind the submitted request")
    if not isinstance(obj["status"], str) or EXIT_CODES.get(obj["status"]) != returncode:
        raise ValueError("native status and exit code disagree")
    if not isinstance(obj["reason"], str):
        raise ValueError("native reason must be a string")
    used, left = obj["fuel_spent"], obj["fuel_remaining"]
    if type(used) is not int or type(left) is not int or min(used, left) < 0 or used + left != request["fuel"]:
        raise ValueError("native fuel ledger does not match the request")
    for key, width in (("input_divisor_checks", 3), ("q_divisor_checks", 2)):
        rows = obj[key]
        if not isinstance(rows, list) or len(rows) > used or any(not isinstance(row, list) or len(row) != width or any(type(v) is not int for v in row) for row in rows):
            raise ValueError("malformed native divisor-check record")
    action = "retain-finite-prime-certificate" if obj["status"] == "FiniteExtensionVerified" else None
    if obj["native_universe"] != "NotImplemented" or obj["native_free"] != "NotGranted" or obj["allowed_action"] != action:
        raise ValueError("native result exceeds declared capabilities")
    return obj


def _limits():
    # RLIMIT_AS is Linux-only. Installing it where the platform has no
    # address-space limit fails the whole child launch, so the declared
    # address-space bound is installed where it exists; CPU, file-size and core
    # limits are installed everywhere.
    if sys.platform == "linux":
        resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (OUTPUT_LIMIT,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (3, 3))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def _blob(raw, prefix=None):
    kept = raw if prefix is None else raw[:prefix]
    return {"sha256": hashlib.sha256(raw).hexdigest(), "byte_length": len(raw),
            "base64": base64.b64encode(kept).decode("ascii"),
            "truncated": len(kept) != len(raw)}


def prime_check(request_path, native=None):
    """Make at most one bounded native call and retain its protocol judgment."""
    started = time.perf_counter_ns()
    report = {"schema": "adva.python-prime-check.research", "version": 0,
              "execution": "NotRun", "status": "InputError", "reason": "",
              "request_sha256": None, "native_result": None, "native_artifact": None,
              "diagnostics": {}, "native_universe": "NotImplemented",
              "native_free": "NotGranted", "allowed_action": None,
              "cost": {"subprocess_invocations": 0, "subprocess_wall_ns": 0}}
    try:
        raw = _read(request_path, INPUT_LIMIT)
        report["request_sha256"] = hashlib.sha256(raw).hexdigest()
        request = _request(raw)
        backend = shutil.which(native or "adva-prime-verify")
        if backend is None:
            report.update(status="BackendUnavailable", reason="Rust prime checker is unavailable")
            return report
        if not sys.platform.startswith("linux"):
            report.update(status="BackendUnavailable", reason="This bounded adapter requires Linux resource limits")
            return report
        with tempfile.TemporaryDirectory(prefix="adva-prime-check-") as work:
            root = Path(work)
            snapshot, result = root / "request.json", root / "result.json"
            snapshot.write_bytes(raw)
            with (root / "stdout").open("wb") as stdout, (root / "stderr").open("wb") as stderr:
                report["status"] = "ExecutionError"
                call_started = time.perf_counter_ns()
                process = subprocess.Popen([backend, str(snapshot), "--output", str(result)],
                                           stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                           start_new_session=True, preexec_fn=_limits)
                report["cost"]["subprocess_invocations"] = 1
                timed_out = False
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    timed_out = True
                finally:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    process.wait()
                    report["cost"]["subprocess_wall_ns"] = time.perf_counter_ns() - call_started
            report["diagnostics"] = {key: _blob(_read(root / key, OUTPUT_LIMIT), 8192) for key in ("stdout", "stderr")}
            report["native_exit_code"] = process.returncode
            if timed_out:
                report.update(execution="Unknown", status="Unknown", reason="Native wall-time limit reached")
                return report
            if process.returncode not in (0, 2, 3) or not result.is_file():
                report.update(execution="Failed", status="ExecutionError", reason="Native execution did not produce a bounded result")
                return report
            report.update(execution="Failed", status="ProtocolError")
            native_raw = _read(result, OUTPUT_LIMIT)
            report["native_artifact"] = _blob(native_raw)
            checked = _result(native_raw, request, process.returncode)
            report.update(execution="Completed", status=checked["status"], reason=checked["reason"],
                          native_result=checked, allowed_action=checked["allowed_action"])
    except (OSError, ValueError, RecursionError, subprocess.SubprocessError) as error:
        report["reason"] = str(error)
        if report["cost"]["subprocess_invocations"]:
            report["execution"] = "Failed"
    finally:
        report["cost"].update(total_wall_ns=time.perf_counter_ns() - started,
                              python_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                              native_peak_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss if report["cost"]["subprocess_invocations"] else None,
                              memory_scope="Linux process peaks, not simultaneous combined memory; child peak includes pre-exec and any earlier children when the Python API is reused",
                              checkpoint_cost="Final report serialization/write is outside total_wall_ns; measure with the supervising run")
    return report


def _save_new(path, report):
    raw = (json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    if len(raw) > OUTPUT_LIMIT:
        raise ValueError("wrapper report exceeds checkpoint limit")
    fd, temporary = tempfile.mkstemp(prefix=".adva-prime-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)  # Atomic fresh-name installation; never replace.
    finally:
        os.unlink(temporary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    operator = commands.add_parser("operator-check", help="bounded external rational-affine receipt check; no native admission")
    operator.add_argument("--question", required=True, type=Path, help="independently selected local question")
    operator.add_argument("--receipt", required=True, type=Path, help="incoming receipt file")
    operator.add_argument("--output", required=True, type=Path, help="fresh report; inputs remain read-only")
    prime = commands.add_parser("prime-check", help="bounded Rust prime-check transport")
    prime.add_argument("request", type=Path)
    prime.add_argument("--native", help="trusted Rust adva-prime-verify executable")
    prime.add_argument("--output", required=True, type=Path)
    search = commands.add_parser("verifier-search", help="Research 0152 finite three-verifier calibration and search")
    search.add_argument("--native", required=True, help="built Rust verifier_search example")
    search.add_argument("--lean", default="lean")
    search.add_argument("--metamath", required=True)
    search.add_argument("--database", required=True, type=Path)
    search.add_argument("--library", type=Path, default=Path("adva-library/stability"))
    search.add_argument("--output", required=True, type=Path, help="fresh evidence directory")
    campaign = commands.add_parser("search-campaign", help="Research 0153 policy comparison and 100 frozen-policy rounds")
    campaign.add_argument("--native", required=True, help="built Rust search_campaign example")
    campaign.add_argument("--lean", default="lean")
    campaign.add_argument("--metamath", required=True)
    campaign.add_argument("--database", required=True, type=Path)
    campaign.add_argument("--library", type=Path, default=Path("adva-library/stability"))
    campaign.add_argument("--output", required=True, type=Path, help="fresh evidence directory")
    catalog = commands.add_parser(
        "math-check", help="check math catalog metadata and references; no proof admission"
    )
    catalog.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[2],
        help="repository checkout containing adva-library/math",
    )
    catalog.add_argument(
        "--output", type=Path, help="optional fresh report path; otherwise stdout only"
    )
    catalog.add_argument(
        "--key-words", action="store_true",
        help="also check the fixed registered v1 key-word mapping; not title meaning",
    )
    quine = commands.add_parser("quine-relay", help="bounded Python/Rust/PSC0 source-byte relay")
    quine.add_argument("--external-library", required=True, type=Path)
    quine.add_argument("--output", required=True, type=Path, help="fresh local evidence directory")
    quine.add_argument(
        "--previous", type=Path,
        help="one explicit correction, debiting the prior report's budget",
    )
    advance = commands.add_parser(
        "advance", help="one explicitly selected bounded research step; no native learning or free"
    )
    advance.add_argument(
        "--profile", choices=["byte-observer-v0", "symbol-surface-load-v0"],
        default="byte-observer-v0", help="frozen research profile (default: historical byte observer)",
    )
    advance.add_argument("--output", required=True, type=Path, help="fresh evidence directory")
    lineage_update = commands.add_parser(
        "lineage-update",
        help="Research 0156 Phase 0: build a checkpoint and a fresh chained anchor",
    )
    lineage_update.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[2],
        help="root containing lineage/<package>/records",
    )
    lineage_update.add_argument("--package", required=True,
                                choices=["arithmetic", "geometry", "logic"])
    lineage_update.add_argument("--global-seq", required=True, type=int)
    lineage_update.add_argument("--anchor-out", required=True, type=Path,
                                help="fresh anchor path; existing files are refused")
    tamper = commands.add_parser(
        "tamper-check",
        help="Research 0156 Phase 0: replay lineage records and compare with anchor",
    )
    tamper.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    tamper.add_argument("--anchor", required=True, type=Path)
    tamper.add_argument("--prev-anchor", type=Path,
                        help="optional previous anchor for chain verification")
    tamper.add_argument("--output", type=Path, help="optional fresh report path")
    verify = commands.add_parser(
        "verify",
        help="Research 0156 Phases 0-1: verify one credential object "
             "(inclusion/signature/disclosure)",
    )
    verify.add_argument("--kind", required=True,
                        choices=["inclusion", "signature", "disclosure"])
    verify.add_argument("--input", required=True, type=Path)
    verify.add_argument("--anchor", type=Path, help="required for inclusion checks")
    verify.add_argument("--output", type=Path, help="optional fresh report path")
    key_issue = commands.add_parser(
        "key-issue",
        help="Research 0156 Phase 0: issue an anchor-signing public key record",
    )
    key_issue.add_argument("--purpose", required=True,
                           help="declared purpose domain; undeclared purposes are Blocked")
    key_issue.add_argument("--home", required=True)
    key_issue.add_argument("--policy-version", required=True)
    key_issue.add_argument("--output", required=True, type=Path,
                           help="fresh record path (public part only)")
    key_issue.add_argument("--private-out", type=Path,
                           help="optional fresh private-seed path (0600, operator custody)")
    args = parser.parse_args()
    try:
        if args.command == "operator-check":
            if args.output.exists() or args.output.is_symlink():
                raise FileExistsError("output must be a fresh path")
            if __package__:
                from . import operator_receipt
            else:
                import operator_receipt
            report = operator_receipt.run(args.question, args.receipt)
            _save_new(args.output, report)
            print(json.dumps({"status": report["status"], "execution": report["execution"],
                              "output": str(args.output), "native_admission": "NotGranted"}))
            return operator_receipt.exit_code(report["status"])
        if args.command == "advance":
            if args.profile == "symbol-surface-load-v0" and __package__:
                from .advance_surface import run as run_advance
            elif args.profile == "symbol-surface-load-v0":
                from advance_surface import run as run_advance
            elif __package__:
                from .advance import run as run_advance
            else:
                from advance import run as run_advance
            report = run_advance(args)
            print(json.dumps({
                "status": report["status"], "phase": report["phase"],
                "output": str(args.output), "finding": report.get("finding"),
            }))
            return {"VariationObserved": 0, "Unknown": 3}.get(report["status"], 2)
        if args.command == "quine-relay":
            if __package__:
                from .quine_relay import run as run_quine
            else:
                from quine_relay import run as run_quine
            report = run_quine(args)
            print(json.dumps({
                "status": report["status"], "phase": report["phase"],
                "output": str(args.output),
            }))
            return {"ClosedFiniteByteRelay": 0, "Unknown": 3, "Rejected": 2}[report["status"]]
        if args.command == "math-check":
            if args.output is not None and (args.output.exists() or args.output.is_symlink()):
                raise FileExistsError("output must be a fresh path")
            if __package__:
                from .math_catalog import check_catalog
            else:
                from math_catalog import check_catalog
            report = check_catalog(args.root, key_words=args.key_words)
            if args.output is not None:
                _save_new(args.output, report)
            print(json.dumps(report, sort_keys=True, allow_nan=False))
            return {"CatalogConsistent": 0, "Unknown": 3}.get(report["status"], 2)
        if args.command in {"lineage-update", "tamper-check", "verify", "key-issue"}:
            if __package__:
                from . import lineage
            else:
                import lineage
        if args.command == "lineage-update":
            report = lineage.lineage_update(args.root, args.package, args.global_seq,
                                            args.anchor_out)
            print(json.dumps(report, sort_keys=True, allow_nan=False))
            return lineage.exit_code(report["status"])
        if args.command == "tamper-check":
            if args.output is not None and (args.output.exists() or args.output.is_symlink()):
                raise FileExistsError("output must be a fresh path")
            report = lineage.tamper_check(args.root, args.anchor,
                                          prev_anchor_path=args.prev_anchor)
            if args.output is not None:
                _save_new(args.output, report)
            print(json.dumps(report, sort_keys=True, allow_nan=False))
            return lineage.exit_code(report["status"])
        if args.command == "verify":
            if args.output is not None and (args.output.exists() or args.output.is_symlink()):
                raise FileExistsError("output must be a fresh path")
            report = lineage.verify(args.kind, args.input, anchor_path=args.anchor)
            if args.output is not None:
                _save_new(args.output, report)
            print(json.dumps(report, sort_keys=True, allow_nan=False))
            return lineage.exit_code(report["status"])
        if args.command == "key-issue":
            if args.output.exists() or args.output.is_symlink():
                raise FileExistsError("output must be a fresh path")
            report = lineage.key_issue(purpose=args.purpose, home=args.home,
                                       policy_version=args.policy_version,
                                       private_out=args.private_out)
            if report["record"] is not None:
                args.output.write_bytes(lineage.canonical_bytes(report["record"]))
            print(json.dumps(report, sort_keys=True, allow_nan=False))
            return lineage.exit_code(report["status"])
        if args.output.exists() or args.output.is_symlink():
            raise FileExistsError("output must be a fresh path")
        if args.command == "search-campaign":
            if __package__:
                from .search_campaign import run
            else:
                from search_campaign import run
            report = run(args)
            print(json.dumps({"status": report["status"], "completed_rounds": report["completed_rounds"], "output": str(args.output)}))
            return 0 if report["status"] == "Completed" else 3 if report["status"] == "Unknown" else 2
        if args.command == "verifier-search":
            if __package__:
                from .verifier_search import run
            else:
                from verifier_search import run
            report = run(args)
            print(json.dumps({"status": report["status"], "output": str(args.output)}))
            return 0 if report["status"] == "Completed" else 3 if report["status"] == "Unknown" else 2
        report = prime_check(args.request, args.native)
        _save_new(args.output, report)
        print(json.dumps({"status": report["status"], "execution": report["execution"]}))
        return EXIT_CODES.get(report["status"], 2)
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
