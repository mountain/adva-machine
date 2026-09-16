"""Finite local child execution and retained artifacts, outside semantic code."""
from __future__ import annotations

import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import time

from .boundary import encoded


class Exhausted(RuntimeError):
    pass


class Account:
    def __init__(self, root, *, wall=30, cpu=25, launches=3, native_launches=3, artifacts=128 * 1024**2):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=False)
        self.started = time.monotonic()
        self.cpu_start = self.cpu_used()
        self.wall, self.cpu, self.launches, self.artifacts = wall, cpu, launches, artifacts
        self.calls = []
        self.native_calls = 0
        self.native_limit = native_launches

    @staticmethod
    def cpu_used():
        return sum(r.ru_utime + r.ru_stime for r in (
            resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
        ))

    def size(self):
        return sum(p.stat().st_size for p in self.root.rglob("*") if p.is_file())

    def remaining(self):
        wall = self.wall - (time.monotonic() - self.started)
        cpu = self.cpu - (self.cpu_used() - self.cpu_start)
        if wall <= 0 or cpu <= 0 or self.size() >= self.artifacts:
            raise Exhausted("declared wall/CPU/artifact account exhausted")
        return wall, cpu

    def save(self, relative, value):
        raw = value if isinstance(value, bytes) else encoded(value) + b"\n"
        if self.size() + len(raw) > self.artifacts:
            raise Exhausted("artifact account exhausted")
        path = self.root / relative
        if not path.resolve().is_relative_to(self.root):
            raise ValueError("artifact path leaves its declared output directory")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(raw)
        return path

    def child(self, label, command, *, native=False):
        if len(self.calls) >= self.launches:
            raise Exhausted("child launch account exhausted")
        if native and self.native_calls >= self.native_limit:
            raise Exhausted("native launch account exhausted")
        wall, cpu = self.remaining()
        # Each child writes at most stdout, stderr and one result file. Reserve
        # a fourth share for the supervisor's final report and accounting.
        file_limit = min(64 * 1024**2, (self.artifacts - self.size()) // 4)
        if file_limit < 1024:
            raise Exhausted("insufficient artifact reserve")
        out = self.root / (label + ".stdout.txt")
        err = self.root / (label + ".stderr.txt")
        if not out.resolve().is_relative_to(self.root) or not err.resolve().is_relative_to(self.root):
            raise ValueError("child artifact path leaves its declared output directory")
        out.parent.mkdir(parents=True, exist_ok=True)
        def limits():
            cap = max(1, math.ceil(cpu))
            resource.setrlimit(resource.RLIMIT_CPU, (cap, cap))
            resource.setrlimit(resource.RLIMIT_AS, (1024**3, 1024**3))
            resource.setrlimit(resource.RLIMIT_FSIZE, (file_limit, file_limit))
        start = time.monotonic()
        record = {"label": label, "native": native, "status": "Started"}
        self.calls.append(record)
        self.native_calls += int(native)
        try:
            with out.open("xb") as stdout, err.open("xb") as stderr:
                with subprocess.Popen(
                    command, cwd=Path(__file__).resolve().parents[1], stdout=stdout, stderr=stderr,
                    start_new_session=True, preexec_fn=limits,
                ) as process:
                    try:
                        code = process.wait(timeout=wall)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
                        raise Exhausted("child wall account exhausted") from None
            record.update(status="Exited", exit_code=code)
            self.remaining()
            if code < 0:
                raise Exhausted(f"child stopped by signal {-code}; resource outcome Unknown")
            return code, out.read_bytes(), err.read_bytes()
        finally:
            record["wall_seconds"] = time.monotonic() - start

    def cost(self):
        return {
            "wall_seconds": time.monotonic() - self.started,
            "cpu_seconds_including_children": self.cpu_used() - self.cpu_start,
            "artifact_bytes_before_report": self.size(), "native_calls": self.native_calls,
            "child_calls": self.calls,
            "limits": {"wall_seconds": self.wall, "cpu_seconds": self.cpu,
                       "child_launches": self.launches, "native_launches": self.native_limit,
                       "artifact_bytes": self.artifacts,
                       "address_space_per_child": 1024**3},
        }
