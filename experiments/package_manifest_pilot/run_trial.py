#!/usr/bin/env python3
"""Fixed aggregate trial supervisor; original work under Unknown v0.3."""
import importlib.metadata
import json
from pathlib import Path
import platform
import resource
import subprocess
import sys
import tempfile
import time


def main():
    started = time.monotonic()
    deadline = started + 10
    commands = [[sys.executable, '-m', 'unittest', '-v'],
                [sys.executable, 'check_manifest.py', 'library-only.example.json'],
                [sys.executable, 'check_manifest.py', 'library-only.example.json']]
    records = []
    status = 'Passed'
    for command in commands:
        with tempfile.TemporaryFile() as output:
            try:
                process = subprocess.run(command, cwd=Path(__file__).parent,
                                         stdout=output, stderr=subprocess.STDOUT,
                                         timeout=max(0.001, deadline-time.monotonic()),
                                         check=False)
                size = output.tell()
                output.seek(0)
                records.append({'command':command[1:], 'exit_code':process.returncode,
                                'output_bytes':size, 'output':output.read(131073).decode('utf-8', 'replace')})
                if process.returncode != 0 or size > 131072:
                    status = 'Failed'
                    break
            except subprocess.TimeoutExpired:
                status = 'Unknown'
                size = output.tell()
                output.seek(0)
                records.append({'command':command[1:], 'exit_code':None, 'output_bytes':size,
                                'output':output.read(131073).decode('utf-8', 'replace'),
                                'truncated':size>131073,
                                'reason':'Aggregate 10-second deadline exhausted'})
                break
    elapsed = time.monotonic()-started
    if elapsed > 10:
        status = 'Unknown'
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    report = {'status':status, 'profile':'documentary-trial-only', 'python':platform.python_version(),
              'jsonschema':importlib.metadata.version('jsonschema'),
              'elapsed_seconds':elapsed, 'children_user_seconds':usage.ru_utime,
              'children_system_seconds':usage.ru_stime, 'children_maxrss_platform_units':usage.ru_maxrss,
              'platform':platform.platform(), 'runs':records,
              'limits':'10 seconds cooperative between fixed subprocesses and enforced per remaining subprocess time; output-size checks post-write; no physical memory ceiling. Supervisor startup/final report write excluded from measured interval; no speedup claim.'}
    sys.stdout.write(json.dumps(report, indent=2)+'\n')
    return 0 if status == 'Passed' else 1


if __name__ == '__main__':
    sys.exit(main())
