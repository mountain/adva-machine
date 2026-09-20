"""Check retained bytes and recorded comparisons without executing a new relay."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path


def verify(root):
    root = root.resolve()
    manifest = json.loads((root / "manifest.json").read_bytes())
    retained = {}
    for name, entry in manifest["files"].items():
        path = (root / entry["stored_path"]).resolve()
        if not path.is_relative_to(root):
            raise ValueError(f"evidence path escapes bundle: {name}")
        stored = path.read_bytes()
        if (
            len(stored) != entry["stored_bytes"]
            or hashlib.sha256(stored).hexdigest() != entry["stored_sha256"]
        ):
            raise ValueError(f"stored bytes differ: {name}")
        raw = gzip.decompress(stored) if entry["encoding"] == "gzip" else stored
        if (
            len(raw) != entry["original_bytes"]
            or hashlib.sha256(raw).hexdigest() != entry["original_sha256"]
        ):
            raise ValueError(f"original bytes differ: {name}")
        retained[name] = raw

    for run in ("run-02", "publication-03"):
        report = json.loads(retained[f"{run}/report.json"])
        if (
            report["status"] != "ClosedFiniteByteRelay"
            or len(report["controls"]) != 7
            or not all(report["controls"].values())
        ):
            raise ValueError(f"recorded controls did not all pass: {run}")
        p = retained[f"{run}/p.py"]
        if p != retained[f"{run}/p-regenerated.py"] or p != retained[f"{run}/p-scale-control.py"]:
            raise ValueError(f"retained source-byte closure differs: {run}")
        if retained[f"{run}/q.rs"] != retained[f"{run}/q-regenerated.rs"]:
            raise ValueError(f"retained second Python emission differs: {run}")
        if hashlib.sha256(p).hexdigest() != report["closure"]["p_sha256"]:
            raise ValueError(f"recorded Python digest differs: {run}")
        additive = json.loads(retained[f"{run}/r-native.json"])
        scale = json.loads(retained[f"{run}/scale-native.json"])
        if additive["compilation"]["result"] == scale["compilation"]["result"]:
            raise ValueError(f"retained diagrams are identical: {run}")

    addendum = json.loads(retained["run-01/status-addendum.json"])
    if addendum["audited_status"] != "Unknown":
        raise ValueError("resource-limited failure classification differs")
    # Costs of the failed build remain visible alongside both successful runs.
    costs = [
        json.loads(retained[f"{run}/report.json"])["cost"]
        for run in ("run-01", "run-02", "publication-03")
    ]
    correction, problems = verify_correction(root)
    if problems:
        raise ValueError("; ".join(problems))
    print(
        json.dumps(
            {
                "status": "RetainedBytesAndComparisonsChecked",
                "retained_files": len(retained),
                "recorded_relay_runs": 2,
                "recorded_supervised_calls": sum(cost["processes"] for cost in costs),
                "recorded_child_cpu_seconds": sum(cost["child_cpu_seconds"] for cost in costs),
                "evidence_corrections": [correction["version"]],
                "implementation_correspondence_checked": True,
                "closure_re_established": False,
                "scope": (
                    "Stored-byte checks, the recorded implementation correspondence and comparisons; no native "
                    "replay, no new relay lap and no authentication."
                ),
            },
            indent=2,
        )
    )


def verify_correction(evidence):
    """Check the retained corrected implementation against the repository.

    The bundle froze the implementations of 2026-09-09; two later supervisor
    fixes were committed without a retained copy, so
    `postcommit-check-02/relation.json` records the corrected bytes and the
    class of drift. This check makes that record load-bearing: the current
    implementation must equal the retained copy, the historical versions must
    stay distinct and byte-preserved, and the record's library pins must agree
    with the contract's. A relay lap is *not* re-run here.
    """
    repo = Path(__file__).resolve().parents[2]
    relation = json.loads((evidence / "postcommit-check-02/relation.json").read_bytes())
    problems = []

    python = relation["correspondence"]["python_implementation"]
    current = hashlib.sha256((repo / python["path"]).read_bytes()).hexdigest()
    if current != python["current_sha256"] or current != python["retained_here"]:
        problems.append("python implementation differs from its retained copy")

    historical = {name: entry["sha256"] for name, entry in python["historical_versions"].items()}
    if len(set(historical.values())) != len(historical):
        problems.append("historical python versions are not distinct")
    if current in historical.values():
        problems.append("current implementation reuses a historical version's bytes")
    if python["matches_any_historical_version"] != (current in historical.values()):
        problems.append("recorded historical-version membership disagrees")

    rust = relation["correspondence"]["rust_observer_example"]
    rust_current = hashlib.sha256((repo / rust["path"]).read_bytes()).hexdigest()
    if rust_current != rust["current_sha256"] or rust_current != rust["retained_here"]:
        problems.append("rust observer example differs from its retained copy")

    contract = json.loads((repo / "experiments/quine_relay/contract.json").read_bytes())
    measured = relation["not_re_established"]["measured_gate_status"]
    if (
        measured["contract_library_commit"] != contract["library_commit"]
        or measured["contract_library_tree"] != contract["library_tree"]
    ):
        problems.append("the correction record and the contract disagree on the library pins")
    return relation, problems



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--evidence",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "docs/research/0164-evidence",
    )
    verify(parser.parse_args().evidence)
