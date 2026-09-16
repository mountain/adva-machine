#!/usr/bin/env python3
"""Reject identified withdrawn bytes, including renamed and archived copies.

This is a bounded publication check, not a universal copyright clearance.
Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import subprocess
import tarfile
import zipfile
from pathlib import Path

MAX_EXPANDED = 2 * 1024**3
MAX_NESTED = 128 * 1024**2
MAX_DEPTH = 4
MAX_MEMBERS = 50000


class Refused(Exception):
    pass


class Scanner:
    def __init__(self, records):
        self.digests = {r['sha256'] for r in records}
        self.objects = {r['git_blob'] for r in records}
        self.expanded = 0
        self.members = 0
        self.issues = []

    def stream(self, name, source, size, depth=0):
        self.members += 1
        if self.members > MAX_MEMBERS or depth > MAX_DEPTH:
            raise Refused('archive/member depth budget exhausted')
        h = hashlib.sha256()
        chunks = []
        total = 0
        prefix = b''
        while chunk := source.read(1024 * 1024):
            if not prefix:
                prefix = chunk[:512]
            total += len(chunk)
            self.expanded += len(chunk)
            if self.expanded > MAX_EXPANDED:
                raise Refused('expanded-byte budget exhausted')
            h.update(chunk)
            if total <= MAX_NESTED:
                chunks.append(chunk)
            else:
                chunks.clear()
        if h.hexdigest() in self.digests:
            self.issues.append(name)
        is_zip = prefix.startswith((b'PK\x03\x04', b'PK\x05\x06'))
        is_gzip = prefix.startswith(b'\x1f\x8b')
        is_tar = len(prefix) >= 262 and prefix[257:262] == b'ustar'
        if is_zip or is_gzip or is_tar:
            if total > MAX_NESTED:
                raise Refused('nested archive exceeds byte budget: ' + name)
            data = b''.join(chunks)
            if is_zip:
                with zipfile.ZipFile(io.BytesIO(data)) as z:
                    for entry in z.infolist():
                        if not entry.is_dir():
                            with z.open(entry) as member:
                                self.stream(name+'!'+entry.filename, member, entry.file_size, depth+1)
            elif is_tar or name.lower().endswith(('.tar.gz', '.tgz')):
                with tarfile.open(fileobj=io.BytesIO(data), mode='r|*') as t:
                    for entry in t:
                        if entry.isfile():
                            with t.extractfile(entry) as member:
                                self.stream(name+'!'+entry.name, member, entry.size, depth+1)
            else:
                with gzip.GzipFile(fileobj=io.BytesIO(data)) as member:
                    self.stream(name+'!gzip', member, -1, depth+1)


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--history', action='store_true', help='also inspect every locally reachable Git object identity')
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = json.loads((root/'governance/withdrawals/known-withdrawn-content.json').read_text())
    scanner = Scanner(manifest['records'])
    seen = set()
    try:
        for raw in git(root, 'ls-files', '--stage', '-z').split(b'\0'):
            if not raw:
                continue
            meta, raw_path = raw.split(b'\t', 1)
            mode, oid, stage = meta.split()
            if stage != b'0':
                raise Refused('unmerged index')
            if mode == b'160000':
                continue  # Each separately versioned repository needs its own check.
            if oid in seen:
                continue
            seen.add(oid)
            path = raw_path.decode('utf-8', 'surrogateescape')
            if oid.decode() in scanner.objects:
                scanner.issues.append(path)
                continue
            data = git(root, 'cat-file', 'blob', oid.decode())
            scanner.stream(path, io.BytesIO(data), len(data))
        if args.history:
            for line in git(root, 'rev-list', '--objects', '--all').decode().splitlines():
                oid, _, path = line.partition(' ')
                if oid in scanner.objects:
                    scanner.issues.append('history:'+oid+' '+path)
        report = {'scope': 'identified withdrawn content only', 'unique_blobs': len(seen),
                  'scanned_members': scanner.members, 'expanded_bytes': scanner.expanded,
                  'history_checked': args.history, 'withdrawn_copies': scanner.issues}
        print(json.dumps(report, indent=2))
        return 1 if scanner.issues else 0
    except (Refused, OSError, ValueError, tarfile.TarError, zipfile.BadZipFile) as exc:
        print(json.dumps({'status': 'Incomplete', 'reason': str(exc), 'withdrawn_copies': scanner.issues}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
