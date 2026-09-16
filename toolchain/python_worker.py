"""Execute an already Rust-admitted request with an existing external step model."""
import argparse
from importlib import import_module
import json
from pathlib import Path

import blake3

from .boundary import encoded


def execute(admission, fuel, quantum):
    version = int(admission["schema"].rsplit("v", 1)[1])
    if version not in (0, 1):
        raise ValueError("Python step model only supports frozen v0/v1")
    name = "bounded_native_interpreter" if version == 0 else "bounded_self_compiler"
    reference = import_module(f"experiments.{name}.reference")
    program, data = admission["program"], admission["input"]
    state = reference.initial(program)
    trace = []
    budget = reference.Budget(maximum=fuel)
    for _ in range(min(fuel, quantum)):
        if state["phase"]["kind"] != "running":
            break
        pc = state["pc"]
        state = reference.transition(program, data, state, budget)
        trace.append({"pc": pc, "next_pc": state["pc"],
                      "state_digest": blake3.blake3(reference.encoded(state)).hexdigest()})
    return {
        "schema": admission["schema"], "profile": admission["profile"],
        "program": program, "input": data, "fuel": fuel, "state": state,
        "status": reference.status(state, fuel), "trace": trace,
        "segments": [{"start": 0, "end": state["spent"], "replayed": 0}],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("admission", type=Path)
    parser.add_argument("--fuel", type=int, required=True)
    parser.add_argument("--quantum", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = execute(json.loads(args.admission.read_bytes()), args.fuel, args.quantum)
    with args.output.open("xb") as stream:
        stream.write(encoded(report) + b"\n")


if __name__ == "__main__":
    main()
