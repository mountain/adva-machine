"""Post-run evidence storage and bounded integrity receiving; no executions."""
import argparse
import json
from pathlib import Path
import tarfile

from .boundary import digest, encoded

MAX_FILES = 512
MAX_BYTES = 64 * 1024**2


def receive(directory):
    root = Path(directory)
    manifest = json.loads((root / "manifest.json").read_bytes())
    archive = root / "complete.tar.gz"
    if digest(archive.read_bytes()) != manifest["archive_sha256"]:
        raise ValueError("archive digest differs")
    with tarfile.open(archive, "r:gz") as stream:
        members = stream.getmembers()
        if not 0 < len(members) <= MAX_FILES or sum(m.size for m in members) > MAX_BYTES:
            raise ValueError("evidence exceeds archive bounds")
        names = [m.name for m in members]
        if len(set(names)) != len(names) or set(names) != set(manifest["files"]):
            raise ValueError("evidence member inventory differs")
        if any(not m.isfile() or Path(m.name).is_absolute() or ".." in Path(m.name).parts for m in members):
            raise ValueError("nonregular or escaping archive member")
        raw = {m.name: stream.extractfile(m).read() for m in members}
    for name, value in raw.items():
        record = manifest["files"][name]
        if len(value) != record["bytes"] or digest(value) != record["sha256"]:
            raise ValueError("evidence member digest/size differs: " + name)
        loose = root / name
        if loose.exists() and loose.read_bytes() != value:
            raise ValueError("loose evidence differs from archive: " + name)
    if sum(len(value) for value in raw.values()) != manifest["uncompressed_bytes"]:
        raise ValueError("uncompressed byte accounting differs")
    return raw


def retain(directory):
    root = Path(directory)
    report = json.loads((root / "report.json").read_bytes())
    if report.get("status") not in ("Passed", "Error", "Unknown"):
        raise ValueError("expected a completed engineering acceptance record")
    if (root / "manifest.json").exists() or (root / "complete.tar.gz").exists():
        raise FileExistsError("evidence already retained")
    paths = sorted(p for p in root.rglob("*") if p.is_file())
    if len(paths) > MAX_FILES or sum(p.stat().st_size for p in paths) > MAX_BYTES:
        raise ValueError("evidence exceeds archive bounds")
    if any(p.is_symlink() for p in paths):
        raise ValueError("evidence contains a symlink")
    files = {p.relative_to(root).as_posix(): {"sha256": digest(p.read_bytes()), "bytes": p.stat().st_size}
             for p in paths}
    archive = root / "complete.tar.gz"
    with tarfile.open(archive, "x:gz") as stream:
        for p in paths:
            stream.add(p, arcname=p.relative_to(root).as_posix(), recursive=False)
    manifest = {"schema": "adva.machine.evidence-manifest.v0",
                "archive_sha256": digest(archive.read_bytes()), "files": files,
                "uncompressed_bytes": sum(r["bytes"] for r in files.values())}
    with (root / "manifest.json").open("xb") as stream:
        stream.write(encoded(manifest) + b"\n")
    receive(root)
    keep = {"report.json", "contract.json", "spec-catalog.json", "library-receipt.json", "source-manifest.json"}
    for p in paths:
        if p.relative_to(root).as_posix() not in keep:
            p.unlink()
    for p in sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if p.is_dir() and not any(p.iterdir()):
            p.rmdir()
    return {"files": len(paths), "raw_bytes": manifest["uncompressed_bytes"], "archive_bytes": archive.stat().st_size}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    print(json.dumps(retain(args.directory)))
