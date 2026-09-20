"""One read-only, pinned external operator-receipt call; no native authority."""
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import signal
import stat
import subprocess
import sys
import tempfile
import time

INPUT_LIMIT = 16384
STREAM_LIMIT = 32768
CHECKER_SHA256 = '263fa9048e663024ffb6c6f393a2e9a1ed93208f966778c2dc33761ea10db10e'
CLOSED = 'ClosedForAllTranslationsByLinearity'
RESULT_STATUSES = {CLOSED, 'UnknownCoverage', 'Refuted', 'InvalidEvidence',
                   'InvalidContextBinding', 'InvalidBasis', 'InvalidInverse',
                   'InvalidSchema', 'UnknownResource', 'InternalMismatch'}


def decode(raw):
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise ValueError('duplicate JSON key')
            out[key] = value
        return out
    def constant(_):
        raise ValueError('nonfinite JSON value')
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


def read_regular(path, limit):
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as f:
        if not stat.S_ISREG(os.fstat(f.fileno()).st_mode):
            raise ValueError('regular file required')
        raw = f.read(limit+1)
    if len(raw) > limit:
        raise ValueError('input exceeds byte limit')
    return raw


def blob(raw):
    return {'byte_length': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
            'base64': base64.b64encode(raw).decode('ascii')}


def local_question(raw):
    obj = decode(raw)
    if type(obj) is not dict or set(obj) != {'schema', 'question_id', 'context'}:
        raise ValueError('local question schema fields')
    if obj['schema'] != 'adva.external.operator-question.v0':
        raise ValueError('local question schema version')
    if type(obj['question_id']) is not str or re.fullmatch('[A-Za-z0-9_.-]{1,64}', obj['question_id']) is None:
        raise ValueError('local question label')
    if type(obj['context']) is not dict:
        raise ValueError('local context object required')
    # Same canonical context convention as the pinned checker, selected locally.
    raw_context = json.dumps(obj['context'], sort_keys=True, separators=(',', ':'),
                             ensure_ascii=True, allow_nan=False).encode()
    return obj, hashlib.sha256(raw_context).hexdigest()


def accept_result(raw, code, expected):
    obj = decode(raw)
    if type(obj) is not dict or type(obj.get('status')) is not str or obj['status'] not in RESULT_STATUSES:
        raise ValueError('unknown external result')
    status = obj['status']
    common = {'status', 'native_admission', 'work_units', 'validation_seconds'}
    scoped = {CLOSED, 'UnknownCoverage', 'Refuted'}
    keys = (common | {'context_sha256', 'context', 'replayed', 'missing_basis_indices', 'scope'}
            if status in scoped else common | {'reason'})
    if set(obj) != keys or obj['native_admission'] != 'NotGranted':
        raise ValueError('external result exceeds protocol/authority boundary')
    if code != (0 if status == CLOSED else 2):
        raise ValueError('external exit/status disagreement')
    if type(obj['work_units']) is not int or not 0 <= obj['work_units'] <= 10001:
        raise ValueError('external work accounting')
    if type(obj['validation_seconds']) not in (int, float) or obj['validation_seconds'] < 0:
        raise ValueError('external timing field')
    if status in scoped:
        raw_context = json.dumps(obj['context'], sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()
        if obj['context_sha256'] != expected or hashlib.sha256(raw_context).hexdigest() != expected:
            raise ValueError('external result lost selected context')
        if type(obj['replayed']) is not list or type(obj['missing_basis_indices']) is not list:
            raise ValueError('external coverage shape')
    return obj


def limits():
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    # RLIMIT_AS is Linux-only; macOS keeps the CPU, file-size and core limits.
    if sys.platform == "linux":
        resource.setrlimit(resource.RLIMIT_AS, (256*1024*1024,)*2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (STREAM_LIMIT,)*2)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def run(question_path, receipt_path):
    started = time.perf_counter()
    report = {'schema': 'adva.python-operator-check.external.v0',
              'execution': 'NotRun', 'status': 'InputError', 'reason': '',
              'local_question': None, 'incoming_receipt': None,
              'question_id': None, 'expected_context_sha256': None,
              'backend': {'kind': 'ExternalPython', 'sha256': CHECKER_SHA256},
              'backend_stdout': None, 'backend_stderr': None, 'external_result': None,
              'native_free': 'NotGranted', 'native_admission': 'NotGranted',
              'cost': {'backend_invocations': 0}}
    try:
        if not sys.platform.startswith('linux'):
            report.update(status='BackendUnavailable', reason='Linux resource limits required')
            return report
        question_raw = read_regular(question_path, INPUT_LIMIT)
        report['local_question'] = blob(question_raw)
        question, expected = local_question(question_raw)
        report.update(question_id=question['question_id'], expected_context_sha256=expected)
        incoming = read_regular(receipt_path, INPUT_LIMIT)
        report['incoming_receipt'] = blob(incoming)
        source_path = Path(__file__).resolve().parents[2]/'experiments/golden_ratio_operator_lift/receipt.py'
        source = read_regular(source_path, STREAM_LIMIT)
        if hashlib.sha256(source).hexdigest() != CHECKER_SHA256:
            report.update(status='BackendUnavailable', reason='checker source pin mismatch')
            return report
        with tempfile.TemporaryDirectory(prefix='adva-operator-check-') as td:
            root = Path(td)
            (root/'receipt.py').write_bytes(source)
            (root/'input.json').write_bytes(incoming)
            # Run the exact source and input snapshots, not paths that can change later.
            call_started = time.perf_counter()
            with (root/'stdout').open('wb') as out, (root/'stderr').open('wb') as err:
                report.update(execution='Failed', status='ExecutionError')
                proc = subprocess.Popen([sys.executable, '-I', '-S', str(root/'receipt.py'),
                                         str(root/'input.json'), '--expected-context-sha256', expected],
                                        stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                        start_new_session=True, preexec_fn=limits)
                report['cost']['backend_invocations'] = 1
                timeout = False
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    timeout = True
                finally:
                    try:
                        os.killpg(proc.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    proc.wait()
            report['cost']['backend_wall_seconds'] = time.perf_counter()-call_started
            raw = read_regular(root/'stdout', STREAM_LIMIT)
            report.update(backend_stdout=blob(raw), backend_stderr=blob(read_regular(root/'stderr', STREAM_LIMIT)),
                          backend_exit_code=proc.returncode)
            if timeout or proc.returncode < 0:
                report.update(execution='Unknown', status='UnknownExecution', reason='backend stopped at execution boundary')
                return report
            report.update(execution='Failed', status='ProtocolError')
            result = accept_result(raw, proc.returncode, expected)
            report.update(execution='Completed', status=result['status'], external_result=result)
    except (OSError, ValueError, RecursionError, subprocess.SubprocessError) as e:
        report['reason'] = str(e)
    finally:
        report['cost'].update(total_wall_seconds=time.perf_counter()-started,
                              python_peak_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                              child_peak_RSS_KiB=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
                              if report['cost']['backend_invocations'] else None,
                              memory_scope='Linux process peaks; child peak includes pre-exec and prior children if API reused',
                              checkpoint_cost='Final report serialization/write excluded')
    return report


def exit_code(status):
    return 0 if status == CLOSED else 3 if status in {'UnknownCoverage', 'UnknownResource', 'UnknownExecution'} else 2
