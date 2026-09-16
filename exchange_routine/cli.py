"""One local entry; structures are read-only, execution delegates to Rust."""
import argparse
import json
import sys
from pathlib import Path

from toolchain.boundary import BoundaryError

from . import structure


def main(argv=None):
    parser = argparse.ArgumentParser(prog="adva-exchange")
    sub = parser.add_subparsers(dest="command", required=True)
    for action in ("check-structure", "show-structure"):
        command = sub.add_parser(action, help="read a bounded documentary structure card")
        command.add_argument("card", type=Path)
    compare = sub.add_parser("compare-structures", help="show a bounded documentary difference and removed obligations")
    compare.add_argument("base", type=Path)
    compare.add_argument("next", type=Path)
    run = sub.add_parser("run", help="perform one prebound four-call Rust exchange")
    run.add_argument("request", type=Path)
    run.add_argument("--expect-request", required=True, help="independently selected request SHA-256")
    run.add_argument("--output", type=Path, required=True, help="fresh audit directory outside repositories")
    args = parser.parse_args(argv)
    try:
        if args.command == "run":
            from .run import execute
            result, code = execute(args.request, args.expect_request, args.output)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return code
        if args.command == "compare-structures":
            left, _ = structure.load(args.base)
            right, _ = structure.load(args.next)
            print(json.dumps(structure.compare(left, right), ensure_ascii=False, indent=2))
            return 0
        raw, card = structure.load(args.card)
        if args.command == "show-structure":
            print(structure.render(card))
        else:
            print(json.dumps(structure.report(raw, card), ensure_ascii=False, indent=2))
        return 0
    except (BoundaryError, ValueError, OSError, RecursionError) as error:
        print(json.dumps({"status": "Refused", "reason": str(error),
                          "native_admission": "NotGranted"}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
