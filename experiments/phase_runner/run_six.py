#!/usr/bin/env python3
"""Bounded host orchestration only; no implementation of learn, run, free, or Seal."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

try:
    import resource
except ImportError:
    resource = None


SCHEMA = "adva.phase-runner.contract.v0"
TOKENS = ("backend", "subject", "method", "resource", "transition", "frontier")
CAPS = {"call_timeout_seconds": 30, "phase_timeout_seconds": 180,
        "output_bytes_per_file": 131072, "child_virtual_memory_kib": 262144}


def load_json(path, cap=131072):
    with path.open("rb") as stream:
        data = stream.read(cap + 1)
    if len(data) > cap:
        raise ValueError(f"file exceeds {cap} bytes: {path.name}")
    return json.loads(data)


def digest(path, cap):
    with path.open("rb") as stream:
        data = stream.read(cap + 1)
    return {"path": str(path), "bytes_observed": len(data),
            "sha256": hashlib.sha256(data).hexdigest() if len(data) <= cap else None,
            "oversized": len(data) > cap}


def backend_binding(path, cap=64 * 1024 * 1024):
    result = {"path": str(path) if path is not None else None, "sha256": None,
              "bytes": None, "hash_read_limit_bytes": cap}
    if path is None or not path.is_absolute():
        return dict(result, reason="BackendUnavailable")
    hasher, observed = hashlib.sha256(), 0
    try:
        with path.open("rb") as stream:
            while True:
                block = stream.read(min(65536, cap + 1 - observed))
                if not block:
                    return dict(result, sha256=hasher.hexdigest(), bytes=observed,
                                reason="CompleteFileHash")
                observed += len(block)
                if observed > cap:
                    return dict(result, bytes_observed=observed, reason="BackendExceedsHashLimit")
                hasher.update(block)
    except OSError as error:
        return dict(result, reason=f"BackendHashUnavailable: {error}")


def save(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write("\n")


def empty_phase(name, reason):
    return {"phase": name, "requested_slots": 6, "actual_launches": 0,
            "status": "NotRun", "reason": reason,
            "meaning": "Completed means protocol completion, not a mathematical or learning claim",
            "steps": [{"slot": i, "status": "NotRun", "reason": reason}
                      for i in range(1, 7)]}


def _check_template(template, requires, forbids):
    if not isinstance(template, list) or not template or template[0] != "{backend}":
        raise ValueError("command_template must start with {backend}")
    if not all(isinstance(arg, str) for arg in template):
        raise ValueError("command arguments must be strings")
    for arg in template:
        arg.format_map({key: key for key in TOKENS})
    for token in requires:
        if not any("{" + token + "}" in arg for arg in template):
            raise ValueError(f"command_template omits {token}")
    for token in forbids:
        if any("{" + token + "}" in arg for arg in template):
            raise ValueError(f"command_template must not use {token}")


def check_contract(contract):
    if contract.get("schema") != SCHEMA or contract.get("version") != 0:
        raise ValueError("unsupported contract schema/version")
    phases = contract.get("phases", [])
    if not isinstance(phases, list) or [p.get("name") for p in phases] != ["learn", "run", "free"]:
        raise ValueError("exactly learn, run, free phases are required in that order")
    limits = contract.get("limits", {})
    for key, cap in CAPS.items():
        value = limits.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 < value <= cap:
            raise ValueError(f"invalid limit {key}")
    for key in ("output_bytes_per_file", "child_virtual_memory_kib"):
        if not isinstance(limits[key], int):
            raise ValueError(f"{key} must be an integer")
    for phase in phases:
        if phase.get("requested_slots") != 6:
            raise ValueError("each phase must have six requested slots")
        kind = phase.get("kind")
        template = phase.get("command_template")
        if template is None:
            if kind is not None:
                raise ValueError("a null command_template phase must not declare a kind")
            continue  # An unformed adapter may deliberately have null inputs and schemas.
        if kind == "learn-roundtrip":
            for key in ("initial_subject", "method", "resource", "expected_transition_schema",
                        "expected_frontier_schema"):
                if not isinstance(phase.get(key), str) or not phase[key]:
                    raise ValueError(f"missing phase field {key}")
            _check_template(template, requires=TOKENS, forbids=())
        elif kind == "run-transport":
            if not isinstance(phase.get("initial_subject"), str) or not phase["initial_subject"]:
                raise ValueError("missing phase field initial_subject")
            for key in ("method", "resource", "expected_transition_schema",
                        "expected_frontier_schema"):
                if phase.get(key) is not None:
                    raise ValueError(f"run-transport must leave {key} null")
            _check_template(template, requires=("backend", "subject", "transition"),
                            forbids=("method", "resource", "frontier"))
        else:
            raise ValueError(f"unknown phase kind {kind!r}")


def input_path(base, name):
    candidate = Path(name)
    if candidate.is_absolute():
        raise ValueError("input paths must be relative to the contract directory")
    resolved = (base / candidate).resolve()
    if not resolved.is_relative_to(base):
        raise ValueError("input path escapes the contract directory")
    return resolved


# RLIMIT_AS is a Linux-only limit. Its presence as an attribute does not mean
# the platform can install it: where it cannot, the call fails inside
# preexec_fn and takes the whole child launch with it, so the phase reports the
# declared "required process limits unavailable" instead of a crash.
ADDRESS_SPACE_LIMIT_INSTALLABLE = (
    os.name == "posix" and sys.platform == "linux" and hasattr(resource, "RLIMIT_AS")
)


def child_limits(limits):
    if ADDRESS_SPACE_LIMIT_INSTALLABLE:
        resource.setrlimit(resource.RLIMIT_AS,
                           (limits["child_virtual_memory_kib"] * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (limits["output_bytes_per_file"],) * 2)


def read_stderr(path, cap):
    with path.open("rb") as stream:
        data = stream.read(cap + 1)
    return data[:cap].decode("utf-8", errors="replace"), len(data) >= cap


def stop_process_group(process):
    try:
        os.killpg(process.pid, signal.SIGKILL)
        outcome = "SignalSent"
    except ProcessLookupError:
        outcome = "AlreadyExited"
    process.wait()
    return outcome


def run_transport_phase(phase, base, report_dir, backend, limits):
    """One bounded native `run` per slot; output bytes recorded, not interpreted."""
    result = empty_phase(phase["name"], "NotYetRun")
    if backend is None or not backend.is_absolute() or not backend.is_file() or not os.access(backend, os.X_OK):
        return empty_phase(phase["name"], "BackendUnavailable")
    # File output bounds and process-group cleanup are mandatory for execution.
    supported = ADDRESS_SPACE_LIMIT_INSTALLABLE
    if not supported:
        return empty_phase(phase["name"], "RequiredProcessLimitsUnavailable")
    cap = limits["output_bytes_per_file"]
    phase_started = time.monotonic_ns()
    deadline = time.monotonic() + limits["phase_timeout_seconds"]
    try:
        subject = input_path(base, phase["initial_subject"])
        load_json(subject, cap)
    except (OSError, ValueError, TypeError) as error:
        return empty_phase(phase["name"], f"InvalidInput: {error}")
    result.update({"input_bindings": {"subject": digest(subject, cap)}, "limits": limits,
                   "memory_limit_applied": True, "peak_memory_bytes": None,
                   "peak_memory_note": "Not measured; virtual-memory limit is not peak memory"})
    terminal = None
    for index, row in enumerate(result["steps"], 1):
        if terminal:
            row["reason"] = "EarlierStepStoppedPhase"
            continue
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            terminal = ("Unknown", "PhaseBudgetExhausted")
            row["reason"] = terminal[1]
            continue
        prefix = report_dir / f"{phase['name']}-{index:02d}"
        transition = prefix.with_suffix(".transition.adva")
        stdout, stderr = prefix.with_suffix(".stdout.txt"), prefix.with_suffix(".stderr.txt")
        values = {"backend": str(backend), "subject": str(subject), "transition": str(transition)}
        command = [arg.format_map(values) for arg in phase["command_template"]]
        row.update({"command": command, "return_code": None, "output_bindings": {},
                    "partial_save": False,
                    "timeout_seconds": min(limits["call_timeout_seconds"], remaining)})
        started = time.monotonic_ns()
        process = None
        try:
            # Refuse drift of the immutable subject input between calls.
            if digest(subject, cap) != result["input_bindings"]["subject"]:
                raise ValueError("subject changed within phase")
            with stdout.open("xb") as out, stderr.open("xb") as err:
                process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                           shell=False, start_new_session=True,
                                           preexec_fn=lambda: child_limits(limits), cwd=base)
                result["actual_launches"] += 1
                try:
                    row["return_code"] = process.wait(timeout=row["timeout_seconds"])
                except subprocess.TimeoutExpired:
                    stop_process_group(process)
                    row["return_code"] = process.returncode
                    terminal = ("Unknown", "CallTimedOut")
            row["stderr"], row["stderr_truncation_possible"] = read_stderr(stderr, cap)
            row["stream_bindings"] = {"stdout": digest(stdout, cap), "stderr": digest(stderr, cap)}
            row["stdout_truncation_possible"] = row["stream_bindings"]["stdout"]["bytes_observed"] >= cap
            if terminal is None and row["return_code"] != 0:
                terminal = ("BackendError", "NonzeroBackendExit")
            if transition.exists():
                row["output_bindings"]["transition"] = digest(transition, cap)
            if terminal is None:
                row.update({"status": "Completed",
                            "reason": "NativeRunCompleted; output recorded as bytes, not interpreted"})
        except (OSError, ValueError, TypeError, KeyError, AttributeError, subprocess.SubprocessError) as error:
            terminal = ("BackendError", f"ProtocolFailure: {error}")
        finally:
            if process is not None:
                try:
                    # A completed leader may leave same-group descendants alive.
                    row["process_group_cleanup"] = stop_process_group(process)
                except OSError as error:
                    row["preceding_outcome"] = terminal or (row["status"], row["reason"])
                    row["process_group_cleanup"] = f"Failed: {error}"
                    terminal = ("BackendError", f"ProcessGroupCleanupFailed: {error}")
            row["elapsed_ns"] = time.monotonic_ns() - started
        if terminal:
            row.update({"status": terminal[0], "reason": terminal[1]})
    result.update({"status": terminal[0] if terminal else "Completed",
                   "reason": terminal[1] if terminal else "SixNativeRunsCompleted",
                   "elapsed_ns": time.monotonic_ns() - phase_started,
                   "final_subject": str(subject), "automatic_retries": 0})
    return result


def run_phase(phase, base, report_dir, backend, limits):
    if phase.get("kind") == "run-transport":
        return run_transport_phase(phase, base, report_dir, backend, limits)
    result = empty_phase(phase["name"], "NotYetRun")
    if phase["command_template"] is None:
        return empty_phase(phase["name"], "AdapterUnavailable")
    if backend is None or not backend.is_absolute() or not backend.is_file() or not os.access(backend, os.X_OK):
        return empty_phase(phase["name"], "BackendUnavailable")
    # File output bounds and process-group cleanup are mandatory for execution.
    supported = os.name == "posix" and resource is not None and hasattr(resource, "RLIMIT_AS")
    if not supported:
        return empty_phase(phase["name"], "RequiredProcessLimitsUnavailable")
    cap = limits["output_bytes_per_file"]
    phase_started = time.monotonic_ns()
    deadline = time.monotonic() + limits["phase_timeout_seconds"]
    try:
        subject, method, material = [input_path(base, phase[key]) for key in
                                     ("initial_subject", "method", "resource")]
        bindings = {"method": digest(method, cap), "resource": digest(material, cap)}
        for path in (subject, method, material):
            load_json(path, cap)
    except (OSError, ValueError, TypeError) as error:
        return empty_phase(phase["name"], f"InvalidInput: {error}")
    result.update({"input_bindings": bindings, "limits": limits,
                   "memory_limit_applied": True, "peak_memory_bytes": None,
                   "peak_memory_note": "Not measured; virtual-memory limit is not peak memory"})
    terminal = None
    for index, row in enumerate(result["steps"], 1):
        if terminal:
            row["reason"] = "EarlierStepStoppedPhase"
            continue
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            terminal = ("Unknown", "PhaseBudgetExhausted")
            row["reason"] = terminal[1]
            continue
        prefix = report_dir / f"{phase['name']}-{index:02d}"
        transition = prefix.with_suffix(".transition.adva")
        frontier = prefix.with_suffix(".frontier.adva")
        stdout, stderr = prefix.with_suffix(".stdout.txt"), prefix.with_suffix(".stderr.txt")
        values = dict(zip(TOKENS, map(str, (backend, subject, method, material, transition, frontier))))
        command = [arg.format_map(values) for arg in phase["command_template"]]
        row.update({"command": command, "return_code": None, "output_bindings": {},
                    "partial_save": False,
                    "timeout_seconds": min(limits["call_timeout_seconds"], remaining)})
        started = time.monotonic_ns()
        process = None
        try:
            row["input_bindings"] = {"subject": digest(subject, cap), **bindings}
            subject_value = load_json(subject, cap)
            # Refuse drift of immutable method/resource inputs between calls.
            if digest(method, cap) != bindings["method"] or digest(material, cap) != bindings["resource"]:
                raise ValueError("method or resource changed within phase")
            with stdout.open("xb") as out, stderr.open("xb") as err:
                process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                           shell=False, start_new_session=True,
                                           preexec_fn=lambda: child_limits(limits), cwd=base)
                result["actual_launches"] += 1
                try:
                    row["return_code"] = process.wait(timeout=row["timeout_seconds"])
                except subprocess.TimeoutExpired:
                    stop_process_group(process)
                    row["return_code"] = process.returncode
                    terminal = ("Unknown", "CallTimedOut")
            row["stderr"], row["stderr_truncation_possible"] = read_stderr(stderr, cap)
            row["stream_bindings"] = {"stdout": digest(stdout, cap), "stderr": digest(stderr, cap)}
            row["stdout_truncation_possible"] = row["stream_bindings"]["stdout"]["bytes_observed"] >= cap
            if terminal is None and row["return_code"] != 0:
                terminal = ("BackendError", "NonzeroBackendExit")
            for role, path in (("transition", transition), ("frontier", frontier)):
                if path.exists():
                    row["output_bindings"][role] = digest(path, cap)
            row["partial_save"] = len(row["output_bindings"]) == 1
            if terminal is None:
                value, next_value = load_json(transition, cap), load_json(frontier, cap)
                if value.get("schema") != phase["expected_transition_schema"] or next_value.get("schema") != phase["expected_frontier_schema"]:
                    raise ValueError("output schema mismatch")
                if any(type(item.get("version")) is not int or item["version"] != 0
                       for item in (value, next_value)):
                    raise ValueError("output versions must be exact integer zero")
                if value.get("input") != subject_value or value.get("output") != next_value:
                    raise ValueError("transition does not bind exact input and next frontier")
                history = next_value.get("history", [])
                guard = history[-1].get("guard", {}) if history else {}
                if guard.get("state") == "failed":
                    terminal = ("Rejected", "RetainedGuardFailure")
                    row["guard"] = guard
                else:
                    row.update({"status": "Completed", "reason": "ProtocolOutputChecked"})
                    subject = frontier
        except (OSError, ValueError, TypeError, KeyError, AttributeError, subprocess.SubprocessError) as error:
            terminal = ("BackendError", f"ProtocolFailure: {error}")
        finally:
            if process is not None:
                try:
                    # A completed leader may leave same-group descendants alive.
                    row["process_group_cleanup"] = stop_process_group(process)
                except OSError as error:
                    row["preceding_outcome"] = terminal or (row["status"], row["reason"])
                    row["process_group_cleanup"] = f"Failed: {error}"
                    terminal = ("BackendError", f"ProcessGroupCleanupFailed: {error}")
            row["elapsed_ns"] = time.monotonic_ns() - started
        if terminal:
            row.update({"status": terminal[0], "reason": terminal[1]})
    result.update({"status": terminal[0] if terminal else "Completed",
                   "reason": terminal[1] if terminal else "SixProtocolStepsCompleted",
                   "elapsed_ns": time.monotonic_ns() - phase_started,
                   "final_frontier": str(subject), "automatic_retries": 0})
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--report-dir", type=Path, required=True)
    parser.add_argument("--backend", type=Path)
    args = parser.parse_args(argv)
    try:
        args.report_dir.mkdir(parents=True, exist_ok=False)
    except OSError as error:
        print(f"report directory unavailable: {error}", file=sys.stderr)
        return 2
    reports = []
    started = time.monotonic_ns()
    binary_binding = backend_binding(args.backend)
    error = None
    try:
        contract = load_json(args.contract)
        check_contract(contract)
        base = args.contract.resolve().parent
        for phase in contract["phases"]:
            previous = reports[-1] if reports else None
            if previous is not None and previous["status"] != "Completed":
                reason = f"{previous['phase'].capitalize()}PhaseNotCompleted"
                report = empty_phase(phase["name"], reason)
                report["adapter_available"] = phase["command_template"] is not None
                report["blockers"] = [reason] + ([] if report["adapter_available"] else ["AdapterUnavailable"])
            else:
                report = run_phase(phase, base, args.report_dir.resolve(), args.backend, contract["limits"])
            reports.append(report)
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as caught:
        error = str(caught)
        reports = [empty_phase(name, f"InvalidContract: {error}") for name in ("learn", "run", "free")]
    status = "Completed" if all(p["status"] == "Completed" for p in reports) else "Incomplete"
    summary = {"schema": "adva.phase-runner.report.v0", "version": 0,
               "status": status, "contract": str(args.contract.resolve()),
               "backend_binding": binary_binding,
               "phases": reports, "actual_launches": sum(p["actual_launches"] for p in reports),
               "elapsed_ns": time.monotonic_ns() - started,
               "native_semantics_implemented_here": False, "error": error}
    if args.contract.is_file():
        summary["contract_binding"] = digest(args.contract, 131072)
    try:
        for report in reports:
            name = "run-phase" if report["phase"] == "run" else report["phase"]
            save(args.report_dir / f"{name}-report.json", report)
        save(args.report_dir / "run-report.json", summary)
    except OSError as caught:
        print(f"report save failed: {caught}", file=sys.stderr)
        return 2
    print(json.dumps({"status": status, "actual_launches": summary["actual_launches"],
                      "report": str((args.report_dir / "run-report.json").resolve())}))
    return 0 if error is None and not any(p["status"] == "BackendError" for p in reports) else 1


if __name__ == "__main__":
    sys.exit(main())
