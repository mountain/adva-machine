"""One bounded engineering acceptance run over a fixed shared request family."""
from .boundary import ROOT, catalog, digest, library_receipt, strict_json
from .execute import run


def receive_pair(left, right, left_raw=None, right_raw=None):
    if left["request_sha256"] != right["request_sha256"] or left["profile"] != right["profile"]:
        raise ValueError("request/profile correspondence mismatch")
    if left["outcome"] != right["outcome"]:
        raise ValueError("terminal/refusal correspondence mismatch")
    if left_raw is not None or right_raw is not None:
        if left_raw is None or right_raw is None:
            raise ValueError("one execution artifact is missing")
        for field in ("program", "input", "fuel", "status", "state", "trace", "segments"):
            if left_raw[field] != right_raw[field]:
                raise ValueError(f"same-profile {field} correspondence mismatch")
        if left["verification"]["status"] != "NativeReplayPassed" or right["verification"]["status"] != "NativeReplayPassed":
            raise ValueError("native replay receipt missing")


def conform(binary, account, library=None):
    spec = catalog()
    library = library_receipt(library)
    contract = strict_json((ROOT / "toolchain/conformance.contract.json").read_bytes())
    corpus = ROOT / contract["corpus"]["path"]
    if digest(corpus.read_bytes()) != contract["corpus"]["sha256"]:
        raise ValueError("corpus differs from finite contract")
    cases = strict_json(corpus.read_bytes())
    if len(cases) != 16:
        raise ValueError("expected the declared sixteen-case family")
    account.save("contract.json", contract)
    account.save("spec-catalog.json", spec)
    account.save("library-receipt.json", library)
    source_files = {}
    for path in sorted((ROOT / "toolchain").glob("*.py")):
        raw = path.read_bytes()
        account.save("sources/" + path.name, raw)
        source_files[str(path.relative_to(ROOT))] = digest(raw)
    account.save("source-manifest.json", source_files)
    rows = []
    for case in cases:
        name = case["name"]
        results = {}
        raw = {}
        for engine in ("rust", "python"):
            result = run(case["request"], engine, binary, account, name + "/" + engine)
            for key, value in case["expected"].items():
                if result["outcome"].get(key) != value:
                    raise ValueError(f"{name}/{engine} differs from expected {key}")
            account.save(name + "/" + engine + "/report.json", result)
            results[engine] = result
            raw[engine] = strict_json((account.root / result["execution"]["artifact"]).read_bytes()) if "execution" in result else None
        receive_pair(results["rust"], results["python"], raw["rust"], raw["python"])
        rows.append({"case": name, "profile": case["request"]["profile"],
                     "outcome": results["rust"]["outcome"],
                     "same_state_and_trace": raw["rust"] is not None,
                     "steps": {e: results[e].get("execution", {}).get("steps") for e in results}})
    return {"schema": "adva.machine.conformance.v0", "status": "Passed",
            "case_count": len(rows), "engines": ["rust", "python"], "cases": rows,
            "observer": "exact outcomes and same-profile primitive states/traces; costs separate",
            "scope": "v0/v1 finite family, not independent full-language implementations",
            "library": library}
