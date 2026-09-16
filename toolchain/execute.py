"""One request, explicit engine, fresh artifacts, and native trace receiving."""
from pathlib import Path
import sys

from .boundary import REPORT, BoundaryError, catalog, check_request, digest, native_profile, observe, strict_json


def run(request, engine, binary, account, label="run"):
    common = {"schema": REPORT, "engine": engine, "profile": request.get("profile") if isinstance(request, dict) else None,
              "request_sha256": None, "verification": {"status": "NotRun"}}
    path = account.save(label + "/request.json", request)
    common["request_sha256"] = digest(path.read_bytes())
    if engine not in ("rust", "python"):
        return {**common, "outcome": {"kind": "Unsupported", "reason": "unknown engine"}}
    try:
        profile = check_request(request)
        catalog()
    except BoundaryError as error:
        return {**common, "outcome": {"kind": "Refused", "stage": "transport", "reason": str(error)}}
    version = profile["version"]
    if engine == "python" and version == 2:
        return {**common, "outcome": {"kind": "Unsupported", "reason": "Python reference model does not implement v2 capacity"}}
    binary = Path(binary).resolve()
    common["binary_sha256"] = digest(binary.read_bytes())
    program = account.save(label + "/program.adva", request["program"])
    data = account.save(label + "/input.json", request["input"])
    base = [str(binary), profile["command"], str(program), "--input", str(data)]
    expected_profile = native_profile(version)

    def native(name, fuel, quantum, check=None):
        output = account.root / label / (name + ".adva")
        command = base + ["--fuel", str(fuel), "--quantum", str(quantum), "--output", str(output)]
        if check is not None:
            command += ["--check", str(check)]
        code, _, stderr = account.child(label + "/" + name, command, native=True)
        if code not in (0, 2):
            raise RuntimeError(f"unexpected native exit {code}")
        if not output.exists():
            if code == 0:
                raise RuntimeError("native process returned no artifact")
            return None, stderr.decode(errors="replace").splitlines()[0]
        result = strict_json(output.read_bytes())
        if result["profile"] != expected_profile:
            raise BoundaryError("executable and pinned native source profiles differ")
        return result, output

    fuel, quantum = request["fuel"], request["quantum"]
    admission, admission_path = native("admission", 0, 0)
    if admission is None:
        return {**common, "outcome": {"kind": "Refused", "stage": "native-admission", "reason": admission_path}}
    if engine == "rust":
        result, artifact = native("execution", fuel, quantum)
    else:
        output = account.root / label / "execution.adva"
        code, _, _ = account.child(label + "/python", [
            sys.executable, "-B", "-m", "toolchain.python_worker", str(admission_path),
            "--fuel", str(fuel), "--quantum", str(quantum), "--output", str(output),
        ])
        if code != 0 or not output.exists():
            raise RuntimeError("Python execution failed; stderr retained")
        result, artifact = strict_json(output.read_bytes()), output
    if result is None:
        raise RuntimeError(f"admitted execution produced no report: {artifact}")
    received, receipt_path = native("reception", fuel, 0, check=artifact)
    if received is None:
        raise BoundaryError(f"native trace receiving failed: {receipt_path}")
    if received["state"] != result["state"] or received["verified_steps"] != result["state"]["spent"]:
        raise BoundaryError("native receiving disagrees with emitted execution")
    return {
        **common, "outcome": observe(result), "native_status": result["status"],
        "native_profile": expected_profile,
        "execution": {"artifact": str(artifact.relative_to(account.root)),
                      "sha256": digest(artifact.read_bytes()), "steps": result["state"]["spent"]},
        "verification": {"status": "NativeReplayPassed", "verified_steps": received["verified_steps"],
                         "artifact": str(receipt_path.relative_to(account.root))},
        "authority": "Rust admission and native replay; Python report is an external adapter",
    }
