"""Small explicit compatibility family; these are test data, not language laws."""
from copy import deepcopy
import json

from .boundary import REQUEST, ROOT


def integer(value):
    return {"kind": "integer", "value": value}


def node(tag, fields):
    return {"kind": "node", "tag": tag, "fields": fields}


def program(code, kinds=("data",), version=0):
    return {"schema": f"adva.data-machine.program.research.v{version}", "name": "toolchain-fixture",
            "registers": [{"name": f"r{i}", "kind": kind} for i, kind in enumerate(kinds)], "code": code}


def request(q, data=None, fuel=256, quantum=None):
    version = int(q["schema"].rsplit("v", 1)[1])
    return {"schema": REQUEST, "profile": f"data-machine-v{version}", "program": deepcopy(q),
            "input": integer(0) if data is None else deepcopy(data), "fuel": fuel,
            "quantum": fuel if quantum is None else quantum}


def cases():
    result = []
    def add(name, req, expected):
        result.append({"name": name, "request": req, "expected": expected})
    def returned(value):
        return {"kind": "Returned", "value": value}
    def rejected(reason):
        return {"kind": "Rejected", "stage": "execution", "reason": reason}
    literal = program([
        {"op": "constant", "dst": 1, "value": 9007199254740993},
        {"op": "box_integer", "src": 1, "dst": 0}, {"op": "return", "src": 0},
    ], ("data", "integer"))
    identity = program([{"op": "input", "dst": 0}, {"op": "return", "src": 0}])
    add("exact-integer", request(literal), returned(integer(9007199254740993)))
    overflow = program([
        {"op": "constant", "dst": 1, "value": 2**63 - 1},
        {"op": "constant", "dst": 2, "value": 1},
        {"op": "add", "left": 1, "right": 2, "dst": 1},
        {"op": "box_integer", "src": 1, "dst": 0}, {"op": "return", "src": 0},
    ], ("data", "integer", "integer"))
    add("overflow", request(overflow), rejected("integer overflow"))
    add("uninitialized", request(program([{"op": "return", "src": 0}])), rejected("uninitialized register"))
    add("finite-loop", request(program([{"op": "jump", "target": 0}]), fuel=7), {"kind": "Unknown", "reason": "FuelExhausted"})
    add("suspension", request(literal, quantum=1), {"kind": "Unknown", "reason": "Suspended"})
    add("zero-fuel", request(literal, fuel=0), {"kind": "Unknown", "reason": "FuelExhausted"})
    wrong_type = deepcopy(identity)
    wrong_type["registers"][0]["kind"] = "integer"
    refusal = {"kind": "Refused", "stage": "native-admission"}
    add("wrong-register-type", request(wrong_type), refusal)
    add("boolean-is-not-integer", request(identity, integer(True)), refusal)
    interpreter = json.loads((ROOT / "programs/bounded-interpreter/interpreter.adva").read_bytes())
    sample = json.loads((ROOT / "programs/bounded-interpreter/input.json").read_bytes())
    add("adva-arithmetic-interpreter", request(interpreter, sample, fuel=2048), returned(integer(14)))
    syntax = node(1, [node(0, [integer(2**63 - 1)]), node(0, [integer(1)])])
    add("adva-interpreter-overflow", request(interpreter, syntax, fuel=2048), rejected("integer overflow"))
    dynamic = program([
        {"op": "input", "dst": 0}, {"op": "length", "src": 0, "dst": 1},
        {"op": "box_integer", "src": 1, "dst": 3}, {"op": "clear", "stack": 2},
        {"op": "push", "stack": 2, "src": 3}, {"op": "constant", "dst": 1, "value": 1},
        {"op": "field_dynamic", "src": 0, "index": 1, "dst": 3},
        {"op": "push", "stack": 2, "src": 3}, {"op": "pack", "stack": 2, "tag": 77, "dst": 3},
        {"op": "stack_length", "stack": 2, "dst": 1}, {"op": "return", "src": 3},
    ], ("data", "integer", "stack", "data"), version=1)
    data = node(7, [integer(3), integer(9)])
    add("dynamic-fields-and-pack", request(dynamic, data), returned(node(77, [integer(2), integer(9)])))
    negative = deepcopy(dynamic)
    negative["code"][5]["value"] = -1
    add("negative-field-index", request(negative, data), rejected("negative field index"))
    wide = node(0, [integer(0)] * 9)
    v1_identity = deepcopy(identity)
    v1_identity["schema"] = "adva.data-machine.program.research.v1"
    add("v1-wide-node", request(v1_identity, wide), returned(wide))
    add("v0-wide-node-refusal", request(identity, wide), refusal)
    bad_schema = request(identity)
    bad_schema["program"]["schema"] = "unknown.program"
    add("wrong-program-schema", bad_schema, refusal)
    add("minimum-integer", request(v1_identity, integer(-(2**63))), returned(integer(-(2**63))))
    return result
