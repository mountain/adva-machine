"""Local machine toolchain entry; implementation capabilities remain explicit."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from .boundary import REPORT, ROOT, BoundaryError, catalog, library_receipt, read_request, strict_json
from .conformance import conform
from .execute import run
from .process import Account, Exhausted


def main(argv=None):
    parser = argparse.ArgumentParser(prog="adva-machine")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("capabilities", help="show formats, implementation dependencies and unimplemented directions")
    doctor = sub.add_parser("doctor", help="check pinned specification and library interfaces")
    doctor.add_argument("--library", type=Path)
    doctor.add_argument("--binary", type=Path, default=ROOT / "target/release/adva")
    execute = sub.add_parser("run", help="execute one versioned request and retain native receiving")
    execute.add_argument("request", type=Path)
    execute.add_argument("--engine", choices=("rust", "python"), required=True)
    execute.add_argument("--binary", type=Path, default=ROOT / "target/release/adva")
    execute.add_argument("--output", type=Path, required=True)
    check = sub.add_parser("conform", help="run the fixed sixteen-case engineering acceptance contract once")
    check.add_argument("--binary", type=Path, default=ROOT / "target/release/adva")
    check.add_argument("--library", type=Path)
    check.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "capabilities":
        print(json.dumps(strict_json((ROOT / "toolchain/capabilities.json").read_bytes()), indent=2))
        return 0
    if args.command == "doctor":
        try:
            spec = catalog()
            library = library_receipt(args.library)
            binary = args.binary.resolve()
            report = {"status": "Ready" if binary.is_file() else "NeedsBuild",
                      "specification": spec["schema"], "pinned_files": len(spec["files"]),
                      "library": library, "binary": str(binary),
                      "binary_profile": "checked during native execution, not inferred from path"}
        except (BoundaryError, OSError, ValueError, subprocess.SubprocessError) as error:
            report = {"status": "Refused", "reason": str(error)}
        print(json.dumps(report, indent=2))
        return 0 if report["status"] == "Ready" else 2
    try:
        if args.command == "conform":
            limits = strict_json((ROOT / "toolchain/conformance.contract.json").read_bytes())["limits"]
            account = Account(args.output, **limits)
        else:
            account = Account(args.output)
    except FileExistsError:
        parser.exit(2, "output already exists; choose a new directory\n")
    result = None
    stage = "setup"
    try:
        if args.command == "conform":
            result = conform(args.binary, account, args.library)
        else:
            stage = "request"
            raw = read_request(args.request)
            account.save("request-original.json", raw)
            request = strict_json(raw)
            stage = "execution"
            result = run(request, args.engine, args.binary, account)
    except Exhausted as error:
        result = {"schema": REPORT, "status": "Unknown", "reason": str(error)}
    except (BoundaryError, json.JSONDecodeError) as error:
        if stage == "request":
            result = {"schema": REPORT, "engine": args.engine,
                      "outcome": {"kind": "Refused", "stage": "transport", "reason": str(error)},
                      "verification": {"status": "NotRun"}}
        else:
            result = {"schema": REPORT, "status": "Error", "reason": str(error), "exception": type(error).__name__}
    except Exception as error:
        result = {"schema": REPORT, "status": "Error", "reason": str(error), "exception": type(error).__name__}
    result["cost"] = account.cost()
    account.save("report.json", result)
    print(json.dumps(result, indent=2))
    if "outcome" in result:
        return 0 if result["outcome"]["kind"] in ("Returned", "Unknown") else 2
    return 0 if result.get("status") == "Passed" else 2


if __name__ == "__main__":
    sys.exit(main())
