"""Bounded local file reads; no recursive intake or filesystem migration."""
import hashlib
import os
from pathlib import Path
import stat

from toolchain.boundary import BoundaryError


def plain(path):
    path = Path(os.path.abspath(path))
    for component in (path, *path.parents):
        if component.is_symlink():
            raise BoundaryError("symbolic links are outside this local routine")
    return path


def read(path, limit):
    path = plain(path)
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise BoundaryError("regular file required")
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise BoundaryError(f"file exceeds {limit} bytes")
    return raw


def binary_digest(path):
    path = plain(path)
    total = 0
    digest = hashlib.sha256()
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise BoundaryError("regular binary required")
        while raw := stream.read(1024 * 1024):
            total += len(raw)
            if total > 256 * 1024**2:
                raise BoundaryError("binary exceeds 256 MiB")
            digest.update(raw)
    return digest.hexdigest(), total
