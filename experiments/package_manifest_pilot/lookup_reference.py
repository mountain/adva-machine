#!/usr/bin/env python3
"""Offline pinned Git-blob lookup. Never fetches, imports, executes or admits.
Original work by dot (OpenAI), under Unknown v0.3.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

from check_manifest import Exhausted, Refusal, bounded_read, encode_report, parse


class UnsupportedToolchain(Exception):
    pass


def lookup(reference, repository_name, bound_commit, checkout, seconds=2.0):
    start = time.monotonic()
    account = {'bytes_read':0, 'parse_calls':0, 'visited_values':0,
               'git_calls':0, 'payload_bytes':0, 'hash_calls':0}
    result = {'status':'Unknown', 'reason_code':'Unavailable', 'account':account,
              'semantic_verification':'NotRun', 'native_admission':'NotGranted',
              'residuals':['Repository label is a caller binding, not authenticated ownership.',
                           'Exact Git bytes and optional digest do not establish truth, rights or compatibility.',
                           'No network, external dependency traversal or native identity allocation.']}
    def git(*args):
        remaining = seconds-(time.monotonic()-start)
        if remaining <= 0:
            raise Exhausted('Reference lookup time budget exhausted')
        account['git_calls'] += 1
        environment = dict(os.environ, GIT_NO_LAZY_FETCH='1', GIT_TERMINAL_PROMPT='0')
        response = subprocess.run(['git','--no-lazy-fetch','--no-replace-objects',
                                   '-c','protocol.allow=never','-C',str(checkout),*args],
                                  env=environment, capture_output=True, timeout=remaining, check=False)
        if response.returncode and b'unknown option' in response.stderr:
            raise UnsupportedToolchain('Git does not support required no-lazy-fetch option')
        return response
    try:
        data = parse(bounded_read(reference, account), account)
        if not isinstance(data, dict) or set(data)-{'repository','commit','path','sha256'} or not {'repository','commit','path'} <= set(data):
            raise Refusal('Unsupported reference shape')
        if any(not isinstance(v, str) for v in data.values()):
            raise Refusal('Reference fields must be strings')
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', data['repository']):
            raise Refusal('Unsupported repository coordinate')
        if not re.fullmatch(r'[0-9a-f]{40}', data['commit']):
            raise Refusal('Unsupported revision: a full immutable commit is required')
        path = data['path']
        if not path or len(path)>512 or path.startswith('/') or '\\' in path or any(p in ('','.','..') for p in path.split('/')) or any(ord(c)<32 for c in path):
            raise Refusal('Unsupported repository-relative path')
        if 'sha256' in data and not re.fullmatch(r'[0-9a-f]{64}',data['sha256']):
            raise Refusal('Unsupported digest encoding')
        if data['repository'] != repository_name:
            result.update(status='Rejected', reason_code='UnsupportedRepository', reason='No supplied local binding for this repository')
            return result
        if data['commit'] != bound_commit:
            result.update(status='Rejected', reason_code='IncompatibleRevision', reason='Reference differs from independently supplied consumer pin')
            return result
        commit = git('cat-file','-t',data['commit'])
        if commit.returncode != 0:
            result['reason'] = 'Pinned commit is unavailable locally'
            return result
        if commit.stdout.strip() != b'commit':
            raise Refusal('Coordinate is not a Git commit')
        coordinate = data['commit']+':'+path
        size = git('cat-file','-s',coordinate)
        if size.returncode != 0:
            result['reason'] = 'Exact path is unavailable at the pinned commit'
            return result
        if int(size.stdout) > 65536:
            raise Exhausted('Referenced blob byte budget exhausted')
        payload = git('cat-file','blob',coordinate)
        if payload.returncode != 0:
            raise Refusal('Reference must identify a regular Git blob, not a tree')
        account['payload_bytes'] = len(payload.stdout)
        if len(payload.stdout)>65536:
            raise Exhausted('Referenced blob byte budget exhausted')
        account['hash_calls'] += 1
        digest = hashlib.sha256(payload.stdout).hexdigest()
        if 'sha256' in data and digest != data['sha256']:
            result.update(status='Rejected', reason_code='IncompatibleDigest', reason='Pinned blob differs from requested digest')
            return result
        result.update(status='ReferenceBytesLocated', reason_code='Located',
                      reason='Exact local Git blob read and hashed; no semantic admission',
                      reference=data, sha256=digest, bytes=len(payload.stdout))
    except UnsupportedToolchain as error:
        result.update(reason_code='UnsupportedToolchain', reason=str(error))
    except (Exhausted, subprocess.TimeoutExpired) as error:
        result.update(reason_code='BudgetExhausted', reason=str(error)[:256])
    except (Refusal, ValueError, UnicodeError, RecursionError) as error:
        result.update(status='Rejected', reason_code='UnsupportedReference', reason=str(error)[:256])
    except OSError as error:
        result.update(reason='Local input, Git executable or checkout unavailable: '+type(error).__name__)
    finally:
        account['elapsed_seconds'] = time.monotonic()-start
        if account['elapsed_seconds'] > seconds:
            result.update(status='Unknown', reason_code='BudgetExhausted', reason='Reference lookup time budget exhausted')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reference')
    parser.add_argument('--repository', required=True)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--checkout', required=True, type=Path)
    args = parser.parse_args()
    result = lookup(args.reference, args.repository, args.commit, args.checkout)
    print(encode_report(result).decode(), end='')
    raise SystemExit(0 if result['status']=='ReferenceBytesLocated' else 2 if result['status']=='Rejected' else 3)
