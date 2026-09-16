"""Replay the 0150 seed with its exact receiver without weakening the live gate.

The macOS PyO3 build fix changed Cargo.lock, which is part of the library
checker fingerprint. Current builds must refuse those historical snapshots.
The example's unchanged tests can still run with their frozen dependency graph.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tomllib
from resolve_publication_revision import resolve_revision

ROOT = Path(__file__).resolve().parents[1]
REVISION = "caabb28b95bb7484680b8d0039fd5a571de421d6"
CHECKER = "34f4d38420963c49809aa09c5fd7258f0247faaac6caba89221650356e941b27"
FILES = ["crates/adva-witness/src/" + name + ".rs"
         for name in ("library_checkpoint", "arithmetic", "witness", "boundary", "seed")]
FILES.append("crates/adva-witness/examples/library_generation.rs")
SNAPSHOTS = {
    "epoch-0000.json": "27016fc510e067caa930eb4e75b0d445342d4c1bc611dcf5b2577644e96ff8bb",
    "epoch-0001.json": "eafbee5a0e8d56d326088c608ee34e3f5557c55a9f1cdb40feb7aa73342013bb",
}


def prepare(destination):
    destination.mkdir(parents=True, exist_ok=False)
    effective_revision = resolve_revision(ROOT, REVISION)
    # A changed live checker/example requires an explicit new compatibility decision.
    for name in FILES:
        frozen = subprocess.check_output(["git", "show", effective_revision + ":" + name], cwd=ROOT)
        if frozen != (ROOT / name).read_bytes():
            raise ValueError("live source differs from frozen replay: " + name)
    archive = destination / "source.tar"
    subprocess.run(["git", "archive", "--format=tar", "--output", str(archive), effective_revision,
                    "Cargo.toml", "Cargo.lock", "crates", "experiments/labs-search",
                    "docs", "programs"],
                   cwd=ROOT, check=True, timeout=30)
    source = destination / "source"
    source.mkdir()
    with tarfile.open(archive) as bundle:
        bundle.extractall(source, filter="data")
    workspace = tomllib.loads((source / "Cargo.toml").read_text())["workspace"]
    for member in workspace["members"]:
        if not (source / member / "Cargo.toml").is_file():
            raise ValueError("missing frozen workspace member: " + member)
    # Rust can embed non-Rust inputs at compile time, including the proposal
    # experiment's own research note. Keep these at the same frozen revision.
    compiled_sources = [source / FILES[-1]]
    for crate in ("adva-ir", "adva-lisp", "adva-witness"):
        compiled_sources.extend((source / "crates" / crate / "src").rglob("*.rs"))
    for rust_source in compiled_sources:
        for relative in re.findall(r'include_(?:bytes|str)!\(\s*"([^"]+)"',
                                   rust_source.read_text()):
            if not (rust_source.parent / relative).is_file():
                raise ValueError("missing frozen embedded input: " + relative)
    library = source / "adva-library/stability"
    library.mkdir(parents=True)
    for name, digest in SNAPSHOTS.items():
        original = ROOT / "adva-library/stability" / name
        data = original.read_bytes()
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError("frozen snapshot bytes changed: " + name)
        if json.loads(data)["checker_revision"] != CHECKER:
            raise ValueError("unexpected historical checker")
        shutil.copyfile(original, library / name)
    (destination / "provenance.json").write_text(json.dumps({
        "revision": REVISION, "resolved_revision": effective_revision, "checker_revision": CHECKER,
        "unchanged_live_sources": FILES, "snapshots_sha256": SNAPSHOTS,
        "scope": "Historical 0150 seed replay only; current reader remains strict.",
    }, indent=2) + "\n")
    return source


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    destination = args.output.resolve()
    source = prepare(destination)
    if not args.prepare_only:
        # Exercise the current boundary too: a stale fingerprint must stay rejected.
        report = destination / "live-rejection.json"
        current = subprocess.run([
            "cargo", "run", "--locked", "-q", "-p", "adva-witness", "--bin", "adva", "--",
            "library", "check", "--path", str(ROOT / "adva-library"), "--epoch", "1",
            "--output", str(report)], cwd=ROOT, check=False, timeout=180)
        result = json.loads(report.read_text())
        if current.returncode != 2 or result["status"] != "Rejected":
            raise ValueError("live checker unexpectedly accepted a stale snapshot")
        if "snapshot schema/checker/epoch mismatch" not in json.dumps(result):
            raise ValueError("live rejection was not the expected fingerprint boundary")
        subprocess.run(["cargo", "test", "--locked", "-p", "adva-witness",
                        "--example", "library_generation"],
                       cwd=source, check=True, timeout=180)
    print(json.dumps({"status": "Prepared" if args.prepare_only else "Passed",
                      "revision": REVISION, "output": str(destination)}))


if __name__ == "__main__":
    main()
