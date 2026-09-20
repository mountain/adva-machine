"""Supervise one finite certificate run, with no retries or source mutations."""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: run.py NEW_OUTPUT_DIRECTORY")
    output = Path(sys.argv[1]).resolve()
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    contract = json.loads((HERE / "contract.json").read_text())
    budget = contract["budget"]
    report = {"schema": "adva.external.pascal-commutator-execution.v0", "status": "Unknown", "children": [], "retries": 0,
              "file_sha256": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in ("contract.json", "generate.py", "check.py", "run.py")}}
    try:
        import resource
        # RLIMIT_AS is Linux-only: where the platform cannot install it, the
        # declared limits are unavailable and this run refuses by name.
        if os.name != "posix" or sys.platform != "linux" or not hasattr(resource, "RLIMIT_AS"):
            raise RuntimeError("required process limits unavailable")
        def limits():
            resource.setrlimit(resource.RLIMIT_CPU, (budget["cpu_seconds_per_child"],) * 2)
            resource.setrlimit(resource.RLIMIT_AS, (budget["address_space_bytes_per_child"],) * 2)
            resource.setrlimit(resource.RLIMIT_FSIZE, (budget["output_bytes_per_child"],) * 2)
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        jobs = [("certificate.json", ["generate.py"]),
                ("check.json", ["check.py", str(output / "certificate.json")]),
                ("controls.json", ["check.py", str(output / "certificate.json"), "--controls"])]
        for name, arguments in jobs:
            remaining = budget["wall_seconds_total"] - (time.monotonic() - started)
            if remaining <= 0:
                raise TimeoutError("total wall budget")
            before = time.monotonic()
            with (output / name).open("xb") as stdout, (output / (name + ".stderr")).open("xb") as stderr:
                process = subprocess.Popen([sys.executable, str(HERE / arguments[0]), *arguments[1:]],
                                           stdout=stdout, stderr=stderr, preexec_fn=limits, start_new_session=True)
                try:
                    code = process.wait(timeout=min(remaining, budget["wall_seconds_per_child"]))
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                    raise TimeoutError("child wall budget: " + name)
            report["children"].append({"output": name, "exit_code": code, "wall_seconds": time.monotonic() - before})
            if code:
                raise RuntimeError("child failed: " + name)
        report["status"] = "VerifiedExternalConditionalCertificate"
        report["child_cpu_seconds"] = resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime + resource.getrusage(resource.RUSAGE_CHILDREN).ru_stime
        report["child_peak_rss_platform_units"] = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        report["platform"] = sys.platform
        report["output_sha256"] = {name: hashlib.sha256((output / name).read_bytes()).hexdigest() for name, _ in jobs}
    except Exception as error:
        report["reason"] = str(error)
    report["wall_seconds_through_checking"] = time.monotonic() - started
    report["python"] = sys.version.split()[0]
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    total = sum(p.stat().st_size for p in output.iterdir() if p.is_file()) + len(encoded.encode())
    if total > budget["total_retained_bytes"]:
        report["status"], report["reason"] = "Unknown", "retained-output bound"
    (output / "execution.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": report["status"], "children": len(report["children"]), "reason": report.get("reason"), "retained_bytes": total}))
    return 0 if report["status"] == "VerifiedExternalConditionalCertificate" else 1


if __name__ == "__main__":
    raise SystemExit(main())
