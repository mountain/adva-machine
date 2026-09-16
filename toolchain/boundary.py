"""Transport and integrity boundaries; no native semantic identities."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

import blake3

ROOT = Path(__file__).resolve().parents[1]
REQUEST = "adva.machine.request.v0"
REPORT = "adva.machine.report.v0"
PROFILES = {
    f"data-machine-v{version}": {
        "version": version,
        "command": "data-run" if version == 0 else f"data-run-v{version}",
        "source": "crates/adva-witness/src/data_machine" + ("" if version == 0 else f"_v{version}") + ".rs",
        "fuel": 2048 if version == 0 else 200000,
    }
    for version in range(3)
}


class BoundaryError(ValueError):
    pass


def read_request(path, limit=2 * 1024**2):
    # O_NONBLOCK also lets the regular-file check refuse a FIFO before a read
    # can wait indefinitely. This toolchain supervisor currently targets POSIX.
    descriptor = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise BoundaryError("request must be a regular file")
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise BoundaryError("request exceeds the 2 MiB transport limit")
    return raw


def encoded(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise BoundaryError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def constant(value):
        raise BoundaryError(f"nonfinite JSON value: {value}")

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


def check_request(request):
    if type(request) is not dict or set(request) != {
        "schema", "profile", "program", "input", "fuel", "quantum"
    }:
        raise BoundaryError("request requires exactly schema/profile/program/input/fuel/quantum")
    if request["schema"] != REQUEST:
        raise BoundaryError("unsupported request schema")
    if type(request["profile"]) is not str or request["profile"] not in PROFILES:
        raise BoundaryError("unsupported machine profile")
    profile = PROFILES[request["profile"]]
    for key in ("fuel", "quantum"):
        if type(request[key]) is not int or not 0 <= request[key] <= profile["fuel"]:
            raise BoundaryError(f"{key} must be an integer within the selected profile bound")
    # Types, instructions, data constructors and capacity remain Rust judgments.
    if type(request["program"]) is not dict or type(request["input"]) is not dict:
        raise BoundaryError("program and input must be JSON objects")
    return profile


def native_profile(version):
    profile = PROFILES[f"data-machine-v{version}"]
    h = blake3.blake3(f"adva.data-machine.transition.v{version}\0".encode())
    h.update((ROOT / profile["source"]).read_bytes())
    h.update((ROOT / "Cargo.lock").read_bytes())
    return h.hexdigest()


def check_pins(pins, root=ROOT):
    for relative, expected in pins.items():
        path = root / relative
        if not path.is_file() or digest(path.read_bytes()) != expected:
            raise BoundaryError(f"pinned file differs: {relative}")


def catalog():
    record = strict_json((ROOT / "spec/catalog.json").read_bytes())
    check_pins(record["files"])
    return record


def library_receipt(path=None):
    lock = strict_json((ROOT / "toolchain/library.lock.json").read_bytes())
    root = Path(path).resolve() if path else ROOT / "adva-library"
    def git(*args):
        return subprocess.check_output(
            ["git", "-C", str(root), *args], text=True, stderr=subprocess.PIPE, timeout=5
        ).strip()
    if git("rev-parse", "--show-toplevel") != str(root.resolve()):
        raise BoundaryError("library must be its own initialized checkout")
    if git("rev-parse", "HEAD") != lock["revision"]:
        raise BoundaryError("library revision differs from lock")
    if git("status", "--porcelain", "--untracked-files=no"):
        raise BoundaryError("library has tracked changes")
    check_pins(lock["files"], root)
    return {
        "status": "MatchedPinnedDependency", "path": str(root), "revision": lock["revision"],
        "checked_files": len(lock["files"]), "authority": "documentary-integrity-only",
        "organization": "Open", "native_admission": "NotGranted",
    }


def observe(run):
    phase = run["state"]["phase"]
    if run["status"] in ("Suspended", "FuelExhausted"):
        return {"kind": "Unknown", "reason": run["status"]}
    if phase["kind"] == "returned":
        return {"kind": "Returned", "value": phase["value"]}
    if phase["kind"] == "rejected":
        return {"kind": "Rejected", "stage": "execution", "reason": phase["reason"]}
    raise BoundaryError("unexpected native outcome")
