#!/usr/bin/env python3
"""Finite documentary lint only. No fetching, execution, native IDs or admission.
Original work by dot (OpenAI), contributed under Unknown v0.3.
"""
import json
from pathlib import Path
import sys
import time

from jsonschema import Draft202012Validator

MAX_BYTES = 65536
MAX_DEPTH = 32
PROFILE = 'adva.library-carrier.draft.v0'
SCHEMA_PATH = Path(__file__).with_name('manifest.schema.json')


class Refusal(Exception):
    pass


class Exhausted(Exception):
    pass


def strict_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise Refusal('Duplicate field: ' + key)
        out[key] = value
    return out


def reject_constant(value):
    raise Refusal('Non-JSON constant: ' + value)


def bounded_read(path, account):
    with open(path, 'rb') as handle:
        data = handle.read(MAX_BYTES + 1)
    account['bytes_read'] += len(data)
    if len(data) > MAX_BYTES:
        raise Exhausted('Input byte budget exhausted')
    return data


def parse(data, account):
    account['parse_calls'] += 1
    value = json.loads(data, object_pairs_hook=strict_object,
                       parse_constant=reject_constant)
    stack = [(value, 1)]
    while stack:
        item, depth = stack.pop()
        account['visited_values'] += 1
        if depth > MAX_DEPTH:
            raise Refusal('JSON depth limit exceeded')
        if isinstance(item, dict):
            stack.extend((v, depth + 1) for v in item.values())
        elif isinstance(item, list):
            stack.extend((v, depth + 1) for v in item)
    return value


def lint(path, requested='describe', deadline_seconds=2.0):
    start = time.monotonic()
    account = dict(bytes_read=0, parse_calls=0, visited_values=0,
                   relation_checks=0, trail_step_checks=0, reference_checks=0,
                   origin_hops=0, schema_validation_calls=0)
    result = dict(status='Unknown', semantic_verification='NotRun',
                  native_admission='NotGranted', account=account,
                  residuals=['Offline metadata only; references not fetched or authenticated.',
                             'No rights admission, semantic identity, import, execution or proof judgment.',
                             'Logical bounds and cooperative time checks; no physical-memory ceiling.'])
    try:
        if requested != 'describe':
            raise Refusal('Unsupported capability request: ' + requested)
        schema = parse(bounded_read(SCHEMA_PATH, account), account)
        data = parse(bounded_read(path, account), account)
        account['schema_validation_calls'] += 1
        Draft202012Validator.check_schema(schema)
        account['schema_validation_calls'] += 1
        error = next(Draft202012Validator(schema).iter_errors(data), None)
        if error is not None:
            raise Refusal('Schema mismatch at ' + '/'.join(map(str, error.absolute_path)))
        kinds = [c['kind'] for c in data['capabilities']]
        if len(set(kinds)) != len(kinds):
            raise Refusal('Duplicate capability kind')
        if kinds != ['library'] or data['capabilities'][0]['profile'] != PROFILE:
            result['reason'] = 'No supported documentary receiver for these declared profiles'
            return result
        if any(x['required'] for x in data['extensions']):
            result['reason'] = 'Required extension interpretation unavailable'
            return result
        namespaces = [x['namespace'] for x in data['extensions']]
        if len(set(namespaces)) != len(namespaces):
            raise Refusal('Duplicate extension namespace')
        nodes = {x['id']: x for x in data['content']}
        if len(nodes) != len(data['content']):
            raise Refusal('Duplicate documentary content ID')
        for relation in data['relations']:
            account['relation_checks'] += 1
            if relation['from'] not in nodes or relation['to'] not in nodes:
                raise Refusal('Dangling relation endpoint')
            if relation['kind'] in ('computation-dependency', 'proof-premise'):
                raise Refusal('Library-only receiver cannot authorize dependency relations')
            if relation['kind'] == 'annotates' and nodes[relation['from']]['kind'] != 'annotation':
                raise Refusal('Annotation relation must originate at an annotation')
        trails = {t['id']: t for t in data['trails']}
        if len(trails) != len(data['trails']):
            raise Refusal('Duplicate trail ID')
        for trail in data['trails']:
            for step in trail['steps']:
                account['trail_step_checks'] += 1
                if step not in nodes:
                    raise Refusal('Dangling trail step')
            origin = trail.get('origin')
            if origin:
                if origin['trail'] not in trails or origin['step'] >= len(trails[origin['trail']]['steps']):
                    raise Refusal('Dangling trail origin')
                seen = {trail['id']}
                cursor = trail
                while 'origin' in cursor:
                    account['origin_hops'] += 1
                    parent = cursor['origin']['trail']
                    if parent in seen:
                        raise Refusal('Cyclic trail derivation origin')
                    seen.add(parent)
                    if parent not in trails:
                        raise Refusal('Dangling trail origin')
                    cursor = trails[parent]
        for ref in [*data['provenance']['sources'],
                    *(c['source_contract'] for c in data['capabilities']),
                    *(r for n in data['content'] for r in n['sources'])]:
            account['reference_checks'] += 1
            if ref['path'].startswith('/') or any(p in ('', '.', '..') for p in ref['path'].split('/')) or '\\' in ref['path']:
                raise Refusal('Unsafe repository-relative reference path')
        result.update(status='MetadataConsistent', reason='Finite library-carrier shape and local links checked',
                      ignored_optional_extensions=namespaces,
                      documentary_content_count=len(nodes), trail_count=len(trails))
    except Exhausted as error:
        result['reason'] = str(error)
    except FileNotFoundError:
        result['reason'] = 'Required local bytes unavailable'
    except (Refusal, ValueError, UnicodeError, RecursionError) as error:
        result.update(status='Rejected', reason=str(error)[:256])
    except OSError as error:
        result.update(reason='Input unavailable: ' + type(error).__name__)
    finally:
        account['elapsed_seconds'] = time.monotonic() - start
        if account['elapsed_seconds'] > deadline_seconds:
            result.update(status='Unknown', reason='Cooperative time budget exhausted')
    return result


def encode_report(result):
    # Report encoding is charged separately, including negative outcomes.
    result['account']['report_encodes'] = 2
    result['account']['report_bytes_before_size_field'] = 0
    first = json.dumps(result, sort_keys=True, allow_nan=False).encode()
    result['account']['report_bytes_before_size_field'] = len(first)
    output = json.dumps(result, sort_keys=True, allow_nan=False).encode() + b'\n'
    if len(output) > 8192:
        raise Refusal('Report byte limit exceeded; no successful report')
    return output


if __name__ == '__main__':
    if len(sys.argv) not in (2, 3):
        sys.exit('Usage: check_manifest.py FILE [describe|compute|verify]')
    report = lint(sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else 'describe')
    sys.stdout.buffer.write(encode_report(report))
    sys.exit({'MetadataConsistent': 0, 'Rejected': 2, 'Unknown': 3}[report['status']])
