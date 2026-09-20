"""Local finite Quine relay supervisor; all PSC0 judgments stay in Rust."""

from __future__ import annotations

import ast
import contextlib
import functools
import hashlib
import json
import math
import os
import resource
import signal
import subprocess
import sys
import time
from pathlib import Path

PY_BODY = (
    b"import sys\n"
    b"n=lambda v:'['+','.join(map(str,v))+']'\n"
    b"sys.stdout.write('fn main(){let a:&[u8]=&'+n(a)+';let b:&[u8]=&'+"
    b"n(b)+';let c:&[u8]=&'+n(c)+';'+bytes(b).decode('ascii')+'}\\n')\n"
)
RS_BODY = (
    b'let n=|v:&[u8]|format!("[{}]",v.iter().map(|x|x.to_string()).coll'
    b'ect::<Vec<_>>().join(","));\n'
    b'let p=format!("a={}\\nb={}\\nc={}\\n{}",n(a),n(b),n(c),std::str::fro'
    b"m_utf8(a).unwrap());\n"
    b'let e=p.bytes().map(|x|{let u=i32::from(x%8)+1;format!("(add (add'
    b' (copy {})) {})",u,i32::from(x)-2*u)}).collect::<Vec<_>>().join("'
    b' ");\n'
    b'println!("(module relay (export main) (def main (fn () (outputs {'
    b'}) (frontier {}))))",vec!["Real";p.len()].join(" "),e);\n'
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def numbers(raw):
    return b"[" + b",".join(str(x).encode() for x in raw) + b"]"


def python_source(context):
    return (
        b"a="
        + numbers(PY_BODY)
        + b"\nb="
        + numbers(RS_BODY)
        + b"\nc="
        + numbers(context)
        + b"\n"
        + PY_BODY
    )


def expected_rust(context):
    return (
        b"fn main(){let a:&[u8]=&"
        + numbers(PY_BODY)
        + b";let b:&[u8]=&"
        + numbers(RS_BODY)
        + b";let c:&[u8]=&"
        + numbers(context)
        + b";"
        + RS_BODY
        + b"}\n"
    )


def inspect_python(source, context):
    """Check the complete generated source against the frozen no-source-read template."""
    tree = ast.parse(source)
    for statement, name, expected in zip(
        tree.body[:3], ("a", "b", "c"), (PY_BODY, RS_BODY, context), strict=True
    ):
        if (
            not isinstance(statement, ast.Assign)
            or len(statement.targets) != 1
            or not isinstance(statement.targets[0], ast.Name)
            or statement.targets[0].id != name
        ):
            raise ValueError("quotation data binding differs")
        if bytes(ast.literal_eval(statement.value)) != expected:
            raise ValueError("quotation data differs")
    if source != python_source(context):
        raise ValueError("Python source differs from the complete frozen emitter")


def check_context(context, contract):
    if (
        context["embedded"]["commit"] != contract["library_commit"]
        or context["standalone"]["commit"] != contract["library_commit"]
    ):
        raise ValueError("library commit differs from the frozen contract")
    if context["tree"] != contract["library_tree"]:
        raise ValueError("library tree differs from the frozen contract")
    if (
        context["embedded"]["role"] != "gitlink-dependency"
        or context["standalone"]["role"] != "named-checkout"
    ):
        raise ValueError("library roles cannot be identified")
    if context["embedded"]["path"] == context["standalone"]["path"]:
        raise ValueError("two distinct checkout contexts required")


def check_source_base(supervisor, root, contract):
    """Allow research commits while keeping the frozen Rust build inputs unchanged."""
    supervisor.call(
        "source-base-ancestor",
        ["git", "merge-base", "--is-ancestor", contract["base_commit"], "HEAD"],
        root,
    )
    supervisor.call(
        "source-base-content",
        [
            "git",
            "diff",
            "--exit-code",
            "--no-ext-diff",
            contract["base_commit"],
            "--",
            *contract["source_boundary"]["protected_paths"],
            ":(exclude)crates/adva-witness/examples/quine_relay.rs",
        ],
        root,
    )


class Exhausted(Exception):
    """No implicit continuation or resource renewal."""


class Supervisor:
    def __init__(self, output, limits):
        self.output = output
        self.limits = limits
        self.started = time.monotonic()
        self.deadline = self.started + limits["wall_seconds"]
        self.calls = []
        self.child_cpu_start = self.child_cpu()

    @staticmethod
    def child_cpu():
        usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        return usage.ru_utime + usage.ru_stime

    def check(self):
        if time.monotonic() >= self.deadline:
            raise Exhausted("whole-run wall deadline")
        if self.child_cpu() - self.child_cpu_start >= self.limits["aggregate_child_cpu_seconds"]:
            raise Exhausted("aggregate child CPU budget")

    def child_cpu_limit(self):
        """Admit only a whole-second limit contained in the remaining budget.

        RLIMIT_CPU has integer-second granularity. This sequential supervisor
        must stop before launch when no positive whole second remains; it must
        not round a fractional remainder up to one second.
        """
        remaining = self.limits["aggregate_child_cpu_seconds"] - (
            self.child_cpu() - self.child_cpu_start
        )
        cpu = math.floor(min(self.limits["child_cpu_seconds"], remaining))
        if cpu < 1:
            raise Exhausted("no whole second remains for child CPU limit")
        return cpu

    def restrictions(self, cpu):
        # This runs after fork: RUSAGE_CHILDREN here cannot measure the
        # supervisor's completed children. Install its precomputed allowance.
        if sys.platform == "linux":
            # RLIMIT_AS is Linux-only; macOS keeps CPU/FSIZE/CORE limits.
            resource.setrlimit(resource.RLIMIT_AS, (self.limits["address_space_bytes"],) * 2)
        resource.setrlimit(resource.RLIMIT_CPU, (cpu,) * 2)
        resource.setrlimit(resource.RLIMIT_FSIZE, (self.limits["max_file_bytes"],) * 2)
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

    def call(self, name, command, cwd, *, output=None, allow_failure=False):
        self.check()
        if len(self.calls) >= self.limits["max_processes"]:
            raise Exhausted("subprocess count")
        # Compute in the parent before side effects; this supervisor is serial.
        cpu = self.child_cpu_limit()
        stdout = output or self.output / (name + ".stdout")
        stderr = self.output / (name + ".stderr")
        record = {"name": name, "argv": [str(x) for x in command], "cwd": str(cwd)}
        self.calls.append(record)
        started = time.monotonic()
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", CARGO_NET_OFFLINE="true", LC_ALL="C")
        timed_out = False
        with stdout.open("xb") as out, stderr.open("xb") as err:
            child = subprocess.Popen(
                record["argv"],
                cwd=cwd,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=out,
                stderr=err,
                start_new_session=True,
                preexec_fn=functools.partial(self.restrictions, cpu),
            )
            try:
                child.wait(timeout=max(0.001, self.deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                timed_out = True
            finally:
                with contextlib.suppress(ProcessLookupError):
                    os.killpg(child.pid, signal.SIGKILL)
                child.wait()
        record.update(
            exit_code=child.returncode,
            wall_seconds=time.monotonic() - started,
            stdout_bytes=stdout.stat().st_size,
            stderr_bytes=stderr.stat().st_size,
        )
        self.check()
        if timed_out or child.returncode in (-signal.SIGXCPU, -signal.SIGXFSZ, -signal.SIGKILL):
            raise Exhausted("child time, resource or external termination")
        if child.returncode and not allow_failure:
            diagnostic = stderr.read_bytes()[-65536:]
            if (
                b"File size limit exceeded" in diagnostic
                or b"memory allocation of" in diagnostic
                or b"out of memory" in diagnostic
            ):
                raise Exhausted(f"{name}: nested resource failure; see {stderr.name}")
            raise ValueError(f"{name} failed with exit {child.returncode}; see {stderr.name}")
        return child.returncode

    def git(self, name, root, *args):
        self.call(name, ["git", "-C", root, *args], root)
        return (self.output / (name + ".stdout")).read_text().strip()

    def inventory(self):
        self.check()
        files = {}
        total = 0
        for path in sorted(self.output.rglob("*")):
            if path.is_file() and path.name != "report.json":
                size = path.stat().st_size
                if size > self.limits["max_file_bytes"]:
                    raise Exhausted("retained file size")
                total += size
                if total > self.limits["max_retained_bytes"]:
                    raise Exhausted("total retained bytes")
                files[str(path.relative_to(self.output))] = {
                    "bytes": size,
                    "sha256": digest(path.read_bytes()),
                }
                self.check()
        return files, total


def run(args):
    root = Path(__file__).resolve().parents[2]
    internal = root / "adva-library"
    external = Path(args.external_library).resolve()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    contract_path = root / "experiments/quine_relay/contract.json"
    contract_raw = contract_path.read_bytes()
    contract = json.loads(contract_raw)
    (output / "contract.json").write_bytes(contract_raw)
    limits = dict(contract["limits"])
    continuation = None
    if getattr(args, "previous", None):
        previous = Path(args.previous).resolve()
        previous_raw = previous.read_bytes()
        prior = json.loads(previous_raw)
        if (
            prior.get("continuation") != "none-automatic"
            or prior.get("contract_sha256") != digest(contract_raw)
            or prior.get("status") == "ClosedFiniteByteRelay"
        ):
            raise ValueError("not an eligible first-run correction")
        spent = prior["cost"]
        limits["wall_seconds"] -= math.ceil(spent["wall_seconds_before_report"]) + 1
        limits["aggregate_child_cpu_seconds"] -= math.ceil(spent["child_cpu_seconds"])
        limits["max_processes"] -= spent["processes"]
        retained = sum(p.stat().st_size for p in previous.parent.rglob("*") if p.is_file())
        limits["max_retained_bytes"] -= retained
        if (
            min(
                limits["wall_seconds"],
                limits["aggregate_child_cpu_seconds"],
                limits["max_processes"],
                limits["max_retained_bytes"],
            )
            <= 0
        ):
            raise Exhausted("no correction budget remains")
        continuation = {
            "previous_report": str(previous),
            "previous_sha256": digest(previous_raw),
            "correction": "Strip debug information at link time; consolidate read-only Git probes.",
            "remaining_limits": limits,
            "prior_retained_bytes": retained,
            "boundary_recheck": (
                "Both library contexts and witnesses are rechecked again; "
                "no source, library, equality or output criterion changes."
            ),
        }
        (output / "continuation-contract.json").write_bytes(canonical(continuation) + b"\n")
    supervisor = Supervisor(output, limits)
    report = {
        "schema": "adva.quine-relay-report.research.v0",
        "status": "Unknown",
        "phase": "preflight",
        "controls": {},
        "native_semantics_changed": False,
        "library_admission": "NotGranted",
        "general_duality": "Open",
        "continuation": "correction-used" if continuation else "none-automatic",
        "contract_sha256": digest(contract_raw),
    }
    constructed = 0
    try:
        implementation = output / "implementation"
        implementation.mkdir()
        for source in (
            "python/adva/quine_relay.py",
            "python/adva/adva.py",
            "crates/adva-witness/examples/quine_relay.rs",
            "Cargo.lock",
        ):
            (implementation / source.replace("/", "__")).write_bytes((root / source).read_bytes())
        base, pin = supervisor.git(
            "base-and-gitlink", root, "rev-parse", "HEAD", "HEAD:adva-library"
        ).splitlines()
        check_source_base(supervisor, root, contract)
        report["source_boundary"] = {
            "implementation_head": base,
            "kernel_base": contract["base_commit"],
            "kernel_content_unchanged": True,
        }
        inside, inside_tree = supervisor.git(
            "embedded-commit-tree", internal, "rev-parse", "HEAD", "HEAD^{tree}"
        ).splitlines()
        outside, outside_tree = supervisor.git(
            "standalone-commit-tree", external, "rev-parse", "HEAD", "HEAD^{tree}"
        ).splitlines()
        if pin != inside or inside_tree != outside_tree:
            raise ValueError("gitlink, checkout or tree mismatch")
        for name, directory in (("embedded-clean", internal), ("standalone-clean", external)):
            if supervisor.git(name, directory, "status", "--porcelain", "--untracked-files=all"):
                raise ValueError("library worktree must be clean")
        branch = supervisor.git("standalone-branch", external, "symbolic-ref", "--short", "HEAD")
        origins = [
            supervisor.git(name, directory, "remote", "get-url", "origin")
            for name, directory in (("embedded-origin", internal), ("standalone-origin", external))
        ]
        if origins[0] != origins[1]:
            raise ValueError("library remotes differ")
        pins = {}
        for name in (
            "stability/epoch-0000.json",
            "stability/epoch-0001.json",
            "math/manifest.json",
            "math/constraints/growth-obligation-v0000.json",
            "math/constraints/growth-obligation-seal-v0000.json",
        ):
            a, b = (internal / name).read_bytes(), (external / name).read_bytes()
            if a != b:
                raise ValueError("library material bytes differ: " + name)
            pins[name] = digest(a)
        context = {
            "schema": "quine-library-context-v0",
            "repository": origins[0],
            "tree": inside_tree,
            "embedded": {"role": "gitlink-dependency", "path": str(internal), "commit": pin},
            "standalone": {
                "role": "named-checkout",
                "path": str(external),
                "commit": outside,
                "branch": branch,
            },
            "entry_views": {"p": "standalone", "q": "embedded", "r": "byte-observation"},
            "pins": pins,
        }
        check_context(context, contract)
        encoded = canonical(context)
        (output / "context.json").write_bytes(encoded + b"\n")
        altered = json.loads(encoded)
        altered["standalone"]["commit"] = "0" * 40
        try:
            check_context(altered, contract)
        except ValueError:
            report["controls"]["different_library_commit_rejected"] = True
        else:
            raise ValueError("changed context accepted")
        report["phase"] = "build-and-native-library-check"
        supervisor.call(
            "build-observer",
            [
                "cargo",
                "rustc",
                "--locked",
                "--offline",
                "-j",
                "1",
                "-p",
                "adva-witness",
                "--example",
                "quine_relay",
                "--",
                "-C",
                "debuginfo=0",
                "-C",
                "strip=debuginfo",
            ],
            root,
        )
        native = root / "target/debug/examples/quine_relay"
        supervisor.call(
            "check-libraries",
            [native, "libraries", internal, external, output / "library-recheck.json"],
            root,
        )
        library = json.loads((output / "library-recheck.json").read_bytes())
        report["controls"]["zero_guard_rejected_in_both_libraries"] = all(
            x["zero_refusal"] for x in library["readings"]
        )
        report["library_fuel"] = library["fuel"]
        report["phase"] = "construct-one-paired-quotation"
        p = python_source(encoded)
        constructed = 1
        if len(p) > contract["limits"]["max_python_source_bytes"]:
            raise Exhausted("Python source bound")
        inspect_python(p, encoded)
        (output / "p.py").write_bytes(p)
        empty = output / "empty-cwd"
        empty.mkdir()
        report["phase"] = "python-to-rust"
        supervisor.call(
            "p-to-q", [sys.executable, "-I", "-S", output / "p.py"], empty, output=output / "q.rs"
        )
        q = (output / "q.rs").read_bytes()
        if q != expected_rust(encoded):
            raise ValueError("Rust source differs from frozen mutual quotation")
        supervisor.call(
            "compile-q", ["rustc", "--edition=2024", output / "q.rs", "-o", output / "q-bin"], empty
        )
        report["phase"] = "rust-to-adva"
        supervisor.call("q-to-r", [output / "q-bin"], empty, output=output / "r.adva")
        r = (output / "r.adva").read_bytes()
        if len(r) > contract["limits"]["max_lisp_source_bytes"]:
            raise Exhausted("Lisp source bound")
        report["phase"] = "checked-adva-to-python"
        supervisor.call(
            "r-to-p",
            [
                native,
                "emit",
                output / "r.adva",
                output / "p-regenerated.py",
                output / "r-native.json",
            ],
            empty,
        )
        regenerated = (output / "p-regenerated.py").read_bytes()
        if p != regenerated:
            raise ValueError("source-byte closure failed")
        inspect_python(regenerated, encoded)
        report["closure"] = {
            "p_bytes": len(p),
            "q_bytes": len(q),
            "r_bytes": len(r),
            "p_sha256": digest(p),
            "regenerated_sha256": digest(regenerated),
            "byte_equal": True,
        }
        report["phase"] = "frozen-controls"
        changed = bytes([regenerated[0] ^ 1]) + regenerated[1:]
        (output / "p-tampered.py").write_bytes(changed)
        report["controls"]["changed_byte_fails_closure"] = changed != p
        supervisor.call(
            "regenerated-p-to-q",
            [sys.executable, "-I", "-S", output / "p-regenerated.py"],
            empty,
            output=output / "q-regenerated.rs",
        )
        report["controls"]["regenerated_p_repeats_q"] = (
            output / "q-regenerated.rs"
        ).read_bytes() == q
        for name, body, reason in (
            ("fraction", "1/2", "finite integers"),
            ("unknown-print", "(print 65)", "unknown operation"),
        ):
            path = output / (name + ".adva")
            path.write_text("(module relay (export main) (def main (fn () Real " + body + ")))\n")
            result_path = output / (name + ".json")
            exit_code = supervisor.call(
                name,
                [native, "emit", path, output / (name + ".out"), result_path],
                empty,
                allow_failure=True,
            )
            refusal = json.loads(result_path.read_bytes())
            report["controls"][name + "_rejected"] = (
                exit_code != 0
                and reason in refusal.get("error", "")
                and not (output / (name + ".out")).exists()
            )
        # This control changes process construction, preserving only the declared byte observation.
        scale = r
        for value in range(1, 9):
            scale = scale.replace(f"(add (copy {value}))".encode(), f"(scale 2 {value})".encode())
        (output / "r-scale-control.adva").write_bytes(scale)
        supervisor.call(
            "scale-control",
            [
                native,
                "emit",
                output / "r-scale-control.adva",
                output / "p-scale-control.py",
                output / "scale-native.json",
            ],
            empty,
        )
        additive = json.loads((output / "r-native.json").read_bytes())
        multiplicative = json.loads((output / "scale-native.json").read_bytes())
        report["controls"]["same_bytes_distinct_diagrams"] = (
            output / "p-scale-control.py"
        ).read_bytes() == p and additive["compilation"]["result"] != multiplicative["compilation"][
            "result"
        ]
        report["native"] = {
            key: additive[key]
            for key in ("ast_terms", "compiled_nodes", "source_count", "output_bytes")
        }
        report["native"]["scale_control_nodes"] = multiplicative["compiled_nodes"]
        if len(report["controls"]) != 7 or not all(report["controls"].values()):
            raise ValueError("a frozen control failed")
        for name, expected in pins.items():
            if any(
                digest((directory / name).read_bytes()) != expected
                for directory in (internal, external)
            ):
                raise ValueError("protected library material changed")
        report["files"], report["retained_bytes_before_report"] = supervisor.inventory()
        report.update(status="ClosedFiniteByteRelay", phase="complete")
    except Exhausted as error:
        report.update(status="Unknown", error=str(error))
    except (OSError, ValueError, KeyError, SyntaxError, subprocess.SubprocessError) as error:
        report.update(status="Rejected", error=str(error))
    finally:
        report["calls"] = supervisor.calls
        report["cost"] = {
            "wall_seconds_before_report": time.monotonic() - supervisor.started,
            "child_cpu_seconds": supervisor.child_cpu() - supervisor.child_cpu_start,
            "processes": len(supervisor.calls),
            "candidate_constructions": constructed,
            "memory_scope": "2 GiB cap per child; no claim of a measured combined peak",
        }
        raw = json.dumps(report, indent=2).encode() + b"\n"
        if len(raw) > contract["limits"]["max_file_bytes"]:
            raise Exhausted("final report size")
        with (output / "report.json").open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        # A post-check includes the first checkpoint in the finite wall account.
        if time.monotonic() >= supervisor.deadline and report["status"] == "ClosedFiniteByteRelay":
            report.update(status="Unknown", error="deadline reached while checkpointing")
            with (output / "checkpoint-limit.json").open("xb") as stream:
                stream.write(canonical(report))
    return report
