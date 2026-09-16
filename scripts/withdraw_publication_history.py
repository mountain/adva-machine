#!/usr/bin/env python3
"""Remove enumerated withdrawn blobs while preserving original commit metadata.

Prepared by ChatGPT (OpenAI), at Mingli Yuan's explicit cleanup direction.
Default is a local rehearsal. Publication uses atomic, per-ref leases and never
deletes refs, pushes PR refs, changes credentials, or bypasses branch protection.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def run(*args, cwd=None, data=None, env=None):
    return subprocess.check_output([str(x) for x in args], cwd=cwd, input=data, env=env)


def git(root, *args, **kw):
    return run('git', '-C', root, *args, **kw)


def refs(root):
    return dict(line.split(' ', 1)[::-1] for line in
                git(root, 'for-each-ref', '--format=%(objectname) %(refname)').decode().splitlines())


def tree(root, commit):
    entries = {}
    for row in git(root, 'ls-tree', '-rz', commit).split(b'\0'):
        if row:
            meta, path = row.split(b'\t', 1)
            mode, kind, oid = meta.split()
            entries[path] = (mode, kind, oid)
    return entries


def identity(root, commit):
    raw = git(root, 'cat-file', 'commit', commit)
    headers, message = raw.split(b'\n\n', 1)
    fields = [x for x in headers.splitlines() if x.startswith((b'author ', b'committer ', b'encoding '))]
    parents = [x[7:].decode() for x in headers.splitlines() if x.startswith(b'parent ')]
    return fields, message, parents, b'gpgsig ' in headers


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', required=True)
    ap.add_argument('--repository', required=True, choices=['adva', 'adva-library', 'adva-machine'])
    ap.add_argument('--manifest', type=Path, required=True)
    ap.add_argument('--filter-tool', type=Path, required=True)
    ap.add_argument('--guard', type=Path, required=True)
    ap.add_argument('--workspace', type=Path, required=True)
    ap.add_argument('--library-map', type=Path)
    ap.add_argument('--expected-main')
    ap.add_argument('--publish', action='store_true')
    args = ap.parse_args()
    if args.publish and (args.source != 'https://github.com/mountain/'+args.repository+'.git' or not args.expected_main):
        raise ValueError('publication requires the exact authorized repository and event main SHA')
    args.workspace.mkdir(parents=True, exist_ok=False)
    workspace = args.workspace.resolve()
    original, clean = workspace/'original.git', workspace/'clean.git'
    run('git', 'clone', '--mirror', args.source, original)
    before = refs(original)
    if args.expected_main and before.get('refs/heads/main') != args.expected_main:
        raise ValueError('main advanced after the reviewed event; refusing stale cleanup')
    run('git', 'clone', '--mirror', '--no-hardlinks', original, clean)
    manifest = json.loads(args.manifest.read_text())
    denied = {r['git_blob'] for r in manifest['records']}
    strip = workspace/'withdrawn-objects.txt'
    strip.write_text('\n'.join(sorted(denied))+'\n')
    library = json.loads(args.library_map.read_text())['commit_map'] if args.library_map else {}
    callback = ('mapping = '+repr({a.encode(): b.encode() for a, b in library.items()})+'\n'
                'for change in commit.file_changes:\n'
                '    if change.mode == b"160000" and change.blob_id in mapping:\n'
                '        change.blob_id = mapping[change.blob_id]\n')
    run(sys.executable, args.filter_tool.resolve(), '--force', '--strip-blobs-with-ids', strip,
        '--preserve-commit-hashes', '--preserve-commit-encoding',
        '--prune-empty', 'never', '--prune-degenerate', 'never',
        '--replace-refs', 'delete-no-add', '--commit-callback', callback, cwd=clean)
    mapping = dict(line.split() for line in (clean/'filter-repo/commit-map').read_text().splitlines()[1:])
    changed = {a: b for a, b in mapping.items() if a != b}
    if any(b == '0'*40 for b in mapping.values()):
        raise ValueError('a historical commit was pruned')
    signed = []
    for old, new in changed.items():
        old_fields, old_message, old_parents, signature = identity(original, old)
        new_fields, new_message, new_parents, _ = identity(clean, new)
        if (old_fields, old_message, [mapping.get(p, p) for p in old_parents]) != (new_fields, new_message, new_parents):
            raise ValueError('commit identity/message/topology differs: '+old)
        expected = {p: (mode, kind, library.get(oid.decode(), oid.decode()).encode() if mode == b'160000' else oid)
                    for p, (mode, kind, oid) in tree(original, old).items()
                    if not (kind == b'blob' and oid.decode() in denied)}
        if expected != tree(clean, new):
            raise ValueError('unexpected content or mode change: '+old)
        if signature:
            signed.append(old)
    after = refs(clean)
    writable = {r: {'before': before[r], 'after': after[r]} for r in before
                if r.startswith(('refs/heads/', 'refs/tags/')) and before[r] != after.get(r)}
    if any(v['after'] is None for v in writable.values()):
        raise ValueError('ref deletion is not permitted')
    reachable = {line.split(b' ', 1)[0].decode() for line in git(clean, 'rev-list', '--objects', '--all').splitlines()}
    if denied & reachable:
        raise ValueError('withdrawn objects remain reachable')
    report = {
        'schema': 'adva.publication-history-correction.v0',
        'repository': 'mountain/'+args.repository,
        'scope': 'enumerated withdrawn blob identities and mapped library gitlinks',
        'commit_map': changed,
        'writable_refs': writable,
        'unwritable_refs_requiring_external_followup': {r: before[r] for r in before if r.startswith('refs/pull/') and before[r] != after.get(r)},
        'preserved': ['author identity/date', 'committer identity/date', 'commit messages', 'parent topology', 'all other file bytes and modes'],
        'removed_commit_signatures': signed,
        'known_withdrawn_objects_reachable_after_filter': 0,
        'manifest_sha256': hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
        'limits': 'Does not erase GitHub PR refs, caches, forks or existing clones. A mapped historical dependency lock remains a historical record, not a current acquisition instruction.',
    }
    report_bytes = (json.dumps(report, indent=2, ensure_ascii=False)+'\n').encode()
    (workspace/'history-map.json').write_bytes(report_bytes)
    index = workspace/'journal.index'
    env = {**os.environ, 'GIT_INDEX_FILE': str(index),
           'GIT_AUTHOR_NAME': 'ChatGPT (OpenAI)', 'GIT_AUTHOR_EMAIL': 'agent@openai.invalid',
           'GIT_COMMITTER_NAME': 'Mingli Yuan', 'GIT_COMMITTER_EMAIL': 'mingli.yuan@gmail.com'}
    main_sha = after['refs/heads/main']
    git(clean, 'read-tree', main_sha, env=env)
    oid = git(clean, 'hash-object', '-w', '--stdin', data=report_bytes).strip().decode()
    git(clean, 'update-index', '--add', '--cacheinfo', '100644', oid,
        'governance/withdrawals/history-map-2026-09-16.json', env=env)
    new_tree = git(clean, 'write-tree', env=env).strip().decode()
    message = (b'Record verified publication-history correction\n\n'
               b'Original author/committer identities, dates, messages and topology were verified. '
               b'Only identified withdrawn bytes and mapped library gitlinks were changed. '
               b'External PR refs, caches and clones are outside this result.\n\n'
               b'Agent-Authored-By: ChatGPT (OpenAI)\n'
               b'Agent-Committed-Through: Mingli Yuan <mingli.yuan@gmail.com> - account and credentials only; not endorsement, not review, not a correctness claim\n')
    journal = git(clean, 'commit-tree', new_tree, '-p', main_sha, env=env, data=message).strip().decode()
    git(clean, 'update-ref', 'refs/heads/main', journal, main_sha)
    writable['refs/heads/main'] = {'before': before['refs/heads/main'], 'after': journal}
    checkout = workspace/'verified-checkout'
    git(clean, 'worktree', 'add', '--detach', checkout, journal)
    run(sys.executable, args.guard.resolve(), '--root', checkout, '--history')
    (workspace/'publication-refs.json').write_text(json.dumps(writable, indent=2)+'\n')
    if args.publish:
        remote_now = dict(line.split('\t', 1)[::-1] for line in run('git', 'ls-remote', '--refs', args.source).decode().splitlines())
        writable_before = {r: s for r, s in before.items() if r.startswith(('refs/heads/', 'refs/tags/'))}
        writable_now = {r: s for r, s in remote_now.items() if r.startswith(('refs/heads/', 'refs/tags/'))}
        if writable_now != writable_before:
            raise ValueError('remote branches/tags changed during verification; refusing stale cleanup')
        command = ['git', '-C', str(clean), 'push', '--atomic']
        command += ['--force-with-lease='+r+':'+v['before'] for r, v in sorted(writable.items())]
        command += [args.source]
        command += [v['after']+':'+r for r, v in sorted(writable.items())]
        run(*command)
        remote_after = dict(line.split('\t', 1)[::-1] for line in run('git', 'ls-remote', '--refs', args.source).decode().splitlines())
        if any(remote_after.get(r) != v['after'] for r, v in writable.items()):
            raise ValueError('remote verification failed')
    print(json.dumps({'published': args.publish, 'changed_commits': len(changed),
                      'changed_writable_refs': len(writable), 'main': journal,
                      'verified_metadata_and_trees': len(changed)}, indent=2))


if __name__ == '__main__':
    main()
