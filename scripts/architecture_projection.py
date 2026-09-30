#!/usr/bin/env python3
"""Bounded, disposable G1 projection over the existing KPB-14 source adapter.

No imports, transport, receipts, registry writes, semantic checks or adoption.
Authored by dot (OpenAI), project-original under Unknown v0.3; prepared through
Mingli Yuan account proxy, not his review or endorsement.
"""
import argparse
import hashlib
import json
import re
import subprocess
import time
import tomllib
from collections import deque
from pathlib import Path

from kpb_inventory import AUTHORITY, Repository, build, metadata_issues

SCHEMA = 'adva.repository-architecture-projection.v0.1'
RULES = 'documentary-source-binding-and-impact-v0.1'
OBSERVER = 'adva-machine/architecture_projection.py'
REPOSITORIES = ('mountain/adva', 'mountain/adva-machine', 'mountain/adva-library')
LIMITS = dict(source_bytes=16 * 1024 * 1024, file_bytes=8 * 1024 * 1024,
              git_calls=4096, nodes=4096, edges=8192, traversal_steps=1000000,
              depth=1024, report_bytes=32 * 1024 * 1024, wall_seconds=120)
CAPABILITIES = dict(documentary_projection=True, structural_matching=False,
                    semantic_verification=False, native_admission=False,
                    transport_execution=False, registration_service=False,
                    remote_federation=False, executable_loader=False,
                    cut_checker=False, consumer_adoption=False)
DEPENDENCY_KINDS = {'declared-dependency', 'declared-file-dependency',
                    'implementation-dependency'}
STATE_VALUES = dict(
    provenance={'Declared', 'Traced', 'Unavailable', 'Conflict'},
    binding={'Unbound', 'Matched', 'Mismatch', 'Unknown'},
    delivery={'NotObserved', 'Sent', 'Arrived', 'Unknown'},
    documentary_acceptance={'NotAccepted', 'AcceptedDocumentary', 'AlreadyAccepted', 'Rejected', 'Unknown'},
    reply_observation={'NotObserved', 'Acknowledged', 'Unknown'},
    interpretation={'NotRun', 'ScopedInterpretationChecked', 'Refused', 'Unknown'},
    native_admission={'NotGranted', 'GrantedForProfile', 'Unknown'},
    registration={'Proposed', 'Listed', 'Withdrawn', 'Conflict', 'Unknown'},
    adoption={'NotAdopted', 'Locked', 'Migrated', 'Retired'})


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


class Incomplete(Exception):
    def __init__(self, reason, position=None):
        super().__init__(reason)
        self.reason, self.position = reason, position


class Budget:
    """Deterministic operation limits plus a separately disclosed safety deadline."""
    def __init__(self, limits=None):
        self.limits = dict(LIMITS, **(limits or {}))
        if any(type(v) is not int or v <= 0 for v in self.limits.values()):
            raise ValueError('budgets must be positive integers')
        if set(self.limits) != set(LIMITS):
            raise ValueError('unknown budget dimension')
        self.spent = {k: 0 for k in self.limits}
        self.spent['wall_seconds'] = None
        self.started = time.monotonic()

    def check_time(self, position=None):
        if time.monotonic() - self.started > self.limits['wall_seconds']:
            raise Incomplete('wall-clock safety deadline; output may be partial/non-repeatable', position)

    def charge(self, key, amount=1, position=None):
        self.check_time(position)
        if self.spent[key] + amount > self.limits[key]:
            raise Incomplete(key + ' budget exhausted', position)
        self.spent[key] += amount

    def depth(self, value, position):
        self.check_time(position)
        self.spent['depth'] = max(self.spent['depth'], value)
        if value > self.limits['depth']:
            raise Incomplete('depth budget exhausted', position)

    def record(self):
        return dict(limits=self.limits, spent=self.spent.copy(),
                    wall_clock='cooperative overall deadline; individual Git calls use a timeout; not a hostile-input sandbox',
                    wall_seconds_observed='not included in deterministic payload; measure process externally',
                    file_bytes='maximum unique file size, not cumulative',
                    depth='maximum graph path/DFS depth observed',
                    report_bytes='encoded output size checked before emission',
                    memory='no separately enforced process memory limit',
                    nodes_edges='counts emitted projection records/edges; registry parsing precedes projection under the source byte cap, without a separate AST/parser-memory limit',
                    setup='generator binding reads two local source files and uses two Git calls before this source/traversal account; not an executed source checker',
                    continuation='no retry or automatic budget reset; rerun needs an explicit new invocation')


class AuditedRepository(Repository):
    """Committed Git bytes only. Bounded reads, no source execution or fallback."""
    def __init__(self, name, root, revision, budget):
        self.budget = budget
        try:
            super().__init__(name, root, revision)
        except subprocess.CalledProcessError as exc:
            raise Incomplete('exact source revision unavailable',
                             dict(repository=name, requested_revision=revision)) from exc

    def git(self, *args):
        self.budget.charge('git_calls', position=dict(repository=self.name, operation=args[0]))
        remaining = max(.001, self.budget.limits['wall_seconds'] - (time.monotonic() - self.budget.started))
        try:
            return subprocess.check_output(['git', '--no-replace-objects', '-C', str(self.root), *args],
                                           timeout=min(20, remaining), stderr=subprocess.PIPE).decode('utf-8')
        except subprocess.TimeoutExpired as exc:
            raise Incomplete('Git read timeout', dict(repository=self.name, operation=args[0])) from exc

    def read(self, path):
        if not isinstance(path, str) or not path or path.startswith('/') or '..' in Path(path).parts or ':' in path:
            raise ValueError('unsafe repository path')
        if path in self.cache:
            return self.cache[path]
        position = dict(repository=self.name, commit=self.commit, path=path)
        try:
            if self.git('cat-file', '-t', self.commit + ':' + path).strip() != 'blob':
                raise ValueError('source is not a blob: ' + path)
            size = int(self.git('cat-file', '-s', self.commit + ':' + path))
            if size > self.budget.limits['file_bytes']:
                raise Incomplete('file_bytes budget exhausted', position)
            self.budget.spent['file_bytes'] = max(size, self.budget.spent['file_bytes'])
            self.budget.charge('source_bytes', size, position)
            text = self.git('show', self.commit + ':' + path)
        except subprocess.CalledProcessError as exc:
            raise Incomplete('exact source unavailable; no latest or cross-repository fallback', position) from exc
        if len(text.encode()) != size:
            raise ValueError('Git source byte count changed during immutable read')
        self.total_bytes += size
        self.cache[path] = text
        return text


def source_manifest(repos):
    return [dict(repo.ref(path), source_sha256=digest(raw.encode()), bytes=len(raw.encode()),
                 repository_binding='caller-declared', identity_verification='NotPerformed')
            for _, repo in sorted(repos.items()) for path, raw in sorted(repo.cache.items())]


def source_coordinate(unit):
    return {k: unit[k] for k in ('documentary_id', 'repository', 'full_commit', 'path', 'selector', 'source_sha256')}


def status_vector(source, binding, attempt, residuals):
    """Only byte observation advances here. Other phases have not been run."""
    values = dict(provenance='Conflict' if binding == 'Mismatch' else 'Traced' if binding == 'Matched' else 'Unavailable',
                  binding=binding, delivery='NotObserved', documentary_acceptance='NotAccepted',
                  reply_observation='NotObserved', interpretation='NotRun', native_admission='NotGranted',
                  registration='Proposed', adoption='NotAdopted')
    return {name: dict(value=value, observer=OBSERVER, input_pins=[source], attempt=attempt,
                       allowed_uses=['documentary-reference'] if binding == 'Matched' else [],
                       residuals=list(residuals)) for name, value in values.items()}


def validate_statuses(states):
    """This producer cannot accept imported success flags, receipts or site claims."""
    if set(states) != set(STATE_VALUES):
        raise ValueError('status vector dimensions incomplete or unknown')
    allowed = dict(provenance={'Traced', 'Conflict', 'Unavailable'}, binding={'Matched', 'Mismatch', 'Unknown'},
                   delivery={'NotObserved'}, documentary_acceptance={'NotAccepted'},
                   reply_observation={'NotObserved'}, interpretation={'NotRun'},
                   native_admission={'NotGranted'}, registration={'Proposed'}, adoption={'NotAdopted'})
    for name, row in states.items():
        if row.get('value') not in allowed[name]:
            raise ValueError('unsupported status promotion: ' + name)
        if any(k not in row for k in ('observer', 'input_pins', 'attempt', 'allowed_uses', 'residuals')):
            raise ValueError('incomplete status observation: ' + name)


def source_conditions(unit, repo):
    """Preserve existing claim restrictions, never invent native conditions."""
    fields = ('assumptions', 'counterexample_boundary', 'forbidden_conflations')
    if unit['repository'] == 'mountain/adva' and unit['path'] == 'docs/claims.toml':
        if not hasattr(repo, '_source_claims'):
            repo._source_claims = tomllib.loads(repo.read('docs/claims.toml'))['claim']
        claims = repo._source_claims
        matches = [c for c in claims if c['claim_id'] == unit['selector']]
        if len(matches) != 1:
            raise ValueError('exact owning claim declaration unavailable or ambiguous')
        source = matches[0]
        if unit.get('premises') != source.get('assumptions'):
            raise ValueError('projected premise differs from original declaration')
        return {k: source.get(k) for k in fields}
    if unit['repository'] == 'mountain/adva-library' and unit['path'] == 'math/manifest.json':
        entries = json.loads(repo.read('math/manifest.json'))['entries']
        matches = [e for e in entries if e['key'] == unit['selector']]
        if len(matches) != 1 or unit.get('home') != matches[0].get('home'):
            raise ValueError('material home differs from owning declaration; no silent replacement')
        entry = matches[0]
        if unit.get('premises') != entry.get('assumptions') or unit.get('guards') != entry.get('reuse_requires'):
            raise ValueError('library premise/guard differs from owning declaration')
        if any(item not in unit.get('unresolved_fields', []) for item in entry.get('open_obligations', [])):
            raise ValueError('library residual deleted from owning declaration')
        return dict(assumptions=entry.get('assumptions'), reuse_requires=entry.get('reuse_requires'),
                    open_obligations=entry.get('open_obligations'))
    return {k: unit.get(k) for k in fields}


def project_units(view, repos, budget, attempt, output=None):
    result, seen = output if output is not None else [], set()
    for unit in sorted(view['units'], key=lambda item: item['documentary_id']):
        budget.charge('nodes', position=unit['documentary_id'])
        coord = source_coordinate(unit)
        expected_id = f"{coord['repository']}@{coord['full_commit']}:{coord['path']}#{coord['selector']}"
        if coord['documentary_id'] != expected_id or expected_id in seen:
            raise ValueError('non-exact or duplicate documentary coordinate')
        seen.add(expected_id)
        if not re.fullmatch('[0-9a-f]{64}', coord['source_sha256']):
            raise ValueError('invalid source SHA-256')
        repo = repos[coord['repository']]
        if coord['full_commit'] != repo.commit:
            raise ValueError('source commit does not match independently fixed input')
        raw = repo.read(coord['path'])
        binding = 'Matched' if digest(raw.encode()) == coord['source_sha256'] else 'Mismatch'
        if unit.get('integrity_match') is False:
            binding = 'Mismatch'
        if unit.get('verified') or unit.get('native_admission'):
            raise ValueError('untrusted semantic/native success flag')
        conditions = source_conditions(unit, repo)
        issues = metadata_issues(unit)
        residuals = sorted(set(unit['unresolved_fields'] + issues + [
            'publisher identity/control not authenticated', 'no receiver/checker execution',
            'occurrence bindings are unavailable; this is a documentary declaration',
            'not a complete inventory of live consumers']))
        if binding == 'Mismatch':
            residuals.append('source digest conflict blocks new use')
        for field, value in conditions.items():
            if value is None:
                residuals.append('source condition unavailable: ' + field)
        if unit.get('home') is None:
            residuals.append('material home not declared by this source adapter')
        states = status_vector(coord, binding, attempt, residuals)
        validate_statuses(states)
        result.append(dict(record_id=digest(canonical([SCHEMA, expected_id])), schema_version=SCHEMA,
                           entity_type='DocumentaryDeclaration', source=coord, original_revision=unit['revision'],
                           home=unit.get('home'), publisher=dict(declared_identity=None, authentication='NotPerformed'),
                           package=dict(coordinate=None, residual='inventory unit is not an installed PackageSnapshot'),
                           registration_site=dict(site_snapshot=None, state='local projection only; no registration performed'),
                           receiver_profile=None, permitted_uses=['documentary-reference'] if binding == 'Matched' else [],
                           premises=unit.get('premises'), guards=unit.get('guards'), occurrence_bindings=None,
                           source_conditions=conditions,
                           exports=unit.get('exports'), checker_profile=unit.get('checker_profile'),
                           publication_license=dict(status='Unknown', source_policy='consult owning source; not verified by projection'),
                           evidence_references=unit.get('documentary_references', []),
                           lifecycle=dict(state='Unknown', predecessor=None, successor=None, withdrawal_reason=None),
                           statuses=states, residuals=residuals))
    return result


def typed_edges(view, records, budget, output=None):
    by_id = {r['source']['documentary_id']: r for r in records}
    edges = output if output is not None else []
    for unit in sorted(view['units'], key=lambda item: item['documentary_id']):
        consumer = by_id[unit['documentary_id']]
        for ordinal, old in enumerate(unit['dependency_edges']):
            budget.charge('edges', position=dict(consumer=unit['documentary_id'], ordinal=ordinal))
            target = by_id.get(old.get('target'))
            source_ok = consumer['statuses']['binding']['value'] == 'Matched'
            target_ok = target is not None and target['statuses']['binding']['value'] == 'Matched'
            edge_binding = old.get('status') in {'resolved-metadata', 'documentary-source-inspection'}
            edge_digest_conflict = target is not None and old.get('source_sha256', target['source']['source_sha256']) != target['source']['source_sha256']
            if target is not None and old.get('target_source') is not None:
                edge_digest_conflict |= any(old['target_source'].get(k) != target['source'][k] for k in ('repository', 'full_commit', 'path'))
            known = old['kind'] in DEPENDENCY_KINDS
            conflict = not source_ok or (target is not None and not target_ok) or edge_digest_conflict
            status = 'Conflict' if conflict else 'BoundDocumentary' if target_ok and known and edge_binding else 'Unresolved'
            edge = dict(edge_id=digest(canonical([RULES, unit['documentary_id'], ordinal, old])),
                        kind='source-byte-depends-on' if known else old['kind'], original_kind=old['kind'],
                        direction='dependency-to-consumer',
                        dependency=dict(type='DocumentaryDeclaration', coordinate=target['source']) if target else None,
                        consumer=dict(type='DocumentaryDeclaration', coordinate=consumer['source']),
                        declared_reference=old.get('declared'), declarer=consumer['source'],
                        source_coordinates=[consumer['source']] + ([target['source']] if target else []),
                        scope='declared documentary dependency; no imported judgment or executable dependency',
                        status=status, basis=old, algorithm_version=RULES,
                        input_sha256=[consumer['source']['source_sha256']] + ([target['source']['source_sha256']] if target else []),
                        propagates_review=known and status == 'BoundDocumentary',
                        residuals=['source binding does not discharge premises, guards or semantic obligations'])
            if target is None:
                edge['unresolved_reference'] = dict(declared=old.get('declared'), attempted_source=old.get('attempted_source'),
                                                    reason=old.get('reason', 'no exact target in this bounded view'))
            edges.append(edge)
    return edges


def impact_graph(records, edges, budget):
    """Exact dependency-only traversal, SCCs and per-hop review witnesses."""
    nodes = sorted(r['source']['documentary_id'] for r in records)
    adjacency = {n: [] for n in nodes}
    reverse = {n: [] for n in nodes}
    for edge in edges:
        if edge['propagates_review'] and edge['kind'] == 'source-byte-depends-on':
            a, b = [edge[k]['coordinate']['documentary_id'] for k in ('dependency', 'consumer')]
            adjacency[a].append((b, edge['edge_id']))
            reverse[b].append(a)
    for values in adjacency.values():
        values.sort()
    for values in reverse.values():
        values.sort()
    result = dict(direction='dependency-to-consumer', complete=False, status='Unknown',
                  review_sets={}, review_set_completion={}, strongly_connected_components=[], cycles=[], scc_complete=False,
                  residual='potential review only; never a judgment that a downstream claim is false')
    active_origin, witnesses, active_component = None, {}, None
    try:
        # Kosaraju, explicitly iterative so a documentary cycle cannot recurse forever.
        visited, order = set(), []
        for origin in nodes:
            if origin in visited:
                continue
            visited.add(origin)
            stack = [(origin, 0)]
            while stack:
                budget.depth(len(stack), dict(phase='scc-forward', origin=origin))
                node, index = stack[-1]
                budget.charge('traversal_steps', position=dict(phase='scc-forward', node=node, index=index))
                if index == len(adjacency[node]):
                    order.append(node)
                    stack.pop()
                else:
                    stack[-1] = (node, index + 1)
                    child = adjacency[node][index][0]
                    if child not in visited:
                        visited.add(child)
                        stack.append((child, 0))
        visited = set()
        components = []
        for origin in reversed(order):
            if origin in visited:
                continue
            visited.add(origin)
            stack, component = [(origin, 1)], []
            active_component = component
            while stack:
                node, depth = stack.pop()
                budget.depth(depth, dict(phase='scc-reverse', node=node))
                budget.charge('traversal_steps', position=dict(phase='scc-reverse', node=node))
                component.append(node)
                for child in reverse[node]:
                    budget.charge('traversal_steps', position=dict(phase='scc-reverse-edge', node=node, child=child))
                    if child not in visited:
                        visited.add(child)
                        stack.append((child, depth + 1))
            components.append(sorted(component))
            result['strongly_connected_components'] = sorted(components)
            result['cycles'] = [c for c in sorted(components) if len(c) > 1 or any(n == c[0] for n, _ in adjacency[c[0]])]
            active_component = None
        result['scc_complete'] = True
        result['strongly_connected_components'] = sorted(components)
        result['cycles'] = [c for c in sorted(components) if len(c) > 1 or any(n == c[0] for n, _ in adjacency[c[0]])]
        for origin in nodes:
            active_origin = origin
            witnesses, seen = {}, {origin}
            queue = deque([(origin, [])])
            while queue:
                node, prefix = queue.popleft()
                budget.charge('traversal_steps', position=dict(phase='impact', origin=origin, node=node))
                for child, edge_id in adjacency[node]:
                    budget.charge('traversal_steps', position=dict(phase='impact-edge', origin=origin, node=node, child=child))
                    path = prefix + [edge_id]
                    budget.depth(len(path), dict(phase='impact', origin=origin, node=child))
                    witnesses.setdefault(child, path)
                    if child not in seen:
                        seen.add(child)
                        queue.append((child, path))
            result['review_sets'][origin] = [dict(consumer=n, edge_path=path) for n, path in sorted(witnesses.items())]
            result['review_set_completion'][origin] = True
            active_origin = None
        result.update(complete=True, status='CompleteWithinDeclaredView')
    except Incomplete as exc:
        result['stop'] = dict(reason=exc.reason, position=exc.position)
        if active_origin is not None:
            result['review_sets'][active_origin] = [dict(consumer=n, edge_path=path) for n, path in sorted(witnesses.items())]
            result['review_set_completion'][active_origin] = False
        if active_component is not None:
            result['partial_scc_observation'] = dict(visited=sorted(active_component),
                                                      status='incomplete reverse traversal; not an SCC certificate')
    return result


def consumer_locks(repos):
    paths = {'mountain/adva': 'dependencies/adva-machine.lock.json',
             'mountain/adva-machine': 'toolchain/library.lock.json'}
    return [dict(source=dict(repo.ref(path), source_sha256=digest(repo.read(path).encode())),
                 declaration=json.loads(repo.read(path)), observation='read-only historical lock; not replayed or upgraded')
            for name, path in sorted(paths.items()) for repo in [repos[name]]]


def generator_binding():
    root = Path(__file__).resolve().parents[1]
    commit = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    paths = ['scripts/architecture_projection.py', 'scripts/kpb_inventory.py']
    changed = subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain', '--', *paths], text=True)
    return dict(repository='mountain/adva-machine', base_commit=commit,
                uncommitted_generator_changes=bool(changed),
                source_files={p: digest((root / p).read_bytes()) for p in paths},
                rules_version=RULES, python='Python 3.11+ standard library',
                boundary='exact generator file digests bind local changes; base commit alone is insufficient when dirty')


def run(bindings, limits=None):
    budget = Budget(limits)
    repos, report = {}, dict(schema=SCHEMA, authority=AUTHORITY, rules_version=RULES,
                             capabilities=CAPABILITIES, generator=generator_binding(),
                             scope='existing KPB registries and three authored documentary pilots; inventory incomplete outside those inputs',
                             observation_scope='state vector describes only this projection attempt; historical transport/registration/adoption outcomes are not re-observed or overwritten',
                             status='Unknown', source_commits={}, records=[], typed_edges=[], unresolved_dependencies=[])
    try:
        if set(bindings) != set(REPOSITORIES):
            raise ValueError('exactly the three owning repositories are required')
        for name, (root, revision) in sorted(bindings.items()):
            repos[name] = AuditedRepository(name, root, revision, budget)
        report['source_commits'] = {n: r.commit for n, r in sorted(repos.items())}
        view = build(repos)
        report['consumer_locks'] = consumer_locks(repos)
        attempt = digest(canonical([SCHEMA, report['source_commits'], RULES, budget.limits, report['generator']]))
        report['attempt'] = attempt
        report['records'] = project_units(view, repos, budget, attempt, report['records'])
        report['typed_edges'] = typed_edges(view, report['records'], budget, report['typed_edges'])
        report['unresolved_dependencies'] = [e for e in report['typed_edges'] if e['status'] != 'BoundDocumentary']
        report['impact_review'] = impact_graph(report['records'], report['typed_edges'], budget)
        report['status'] = 'CompleteWithinDeclaredView' if report['impact_review']['complete'] else 'Unknown'
        report['binding_summary'] = dict(records=len(report['records']), dependencies=len(report['typed_edges']),
                                         exact_documentary_bindings=sum(e['status'] == 'BoundDocumentary' for e in report['typed_edges']),
                                         unresolved=len(report['unresolved_dependencies']))
        report['success_boundary'] = 'projection completeness is not dependency closure, semantic verification, registration, receipt, or adoption'
    except Incomplete as exc:
        report['stop'] = dict(reason=exc.reason, position=exc.position)
    except (ValueError, KeyError, UnicodeError, TypeError, SyntaxError, IndexError,
            AttributeError, subprocess.CalledProcessError) as exc:
        report['status'] = 'RefusedInvalidProjection'
        report['stop'] = dict(reason=str(exc), error_type=type(exc).__name__)
    report['source_manifest'] = source_manifest(repos)
    report['resource_account'] = budget.record()
    return report


def encode_report(report):
    """Bound bytes before stdout; never emit an oversized or falsely complete payload."""
    for _ in range(4):
        raw = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False).encode() + b'\n'
        report['resource_account']['spent']['report_bytes'] = len(raw)
    raw = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False).encode() + b'\n'
    if len(raw) > report['resource_account']['limits']['report_bytes']:
        report = {k: v for k, v in report.items() if k in ('schema', 'authority', 'rules_version', 'generator', 'capabilities', 'source_commits', 'resource_account')}
        report.update(status='Unknown', stop=dict(reason='report_bytes budget exhausted',
                                                  observed_bytes=len(raw), evidence='large derived payload omitted; no complete result emitted'))
        report['resource_account']['spent']['report_bytes'] = 0
        for _ in range(4):
            raw = json.dumps(report, sort_keys=True).encode() + b'\n'
            report['resource_account']['spent']['report_bytes'] = len(raw)
        raw = json.dumps(report, sort_keys=True).encode() + b'\n'
        if len(raw) > report['resource_account']['limits']['report_bytes']:
            raise Incomplete('report budget cannot hold even the Unknown diagnostic')
    return raw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', action='append', required=True, help='mountain/name=checkout@commit')
    for key, default in LIMITS.items():
        parser.add_argument('--max-' + key.replace('_', '-'), type=int, default=default)
    args = parser.parse_args()
    bindings = {}
    for value in args.repository:
        name, location = value.split('=', 1)
        root, revision = location.rsplit('@', 1)
        if name in bindings:
            parser.error('duplicate repository binding')
        bindings[name] = (root, revision)
    limits = {k: getattr(args, 'max_' + k) for k in LIMITS}
    try:
        report = run(bindings, limits)
        raw = encode_report(report)
    except (ValueError, Incomplete) as exc:
        parser.exit(2, str(exc) + '\n')
    import sys
    sys.stdout.buffer.write(raw)
    return 0 if json.loads(raw)['status'] == 'CompleteWithinDeclaredView' else 2


if __name__ == '__main__':
    raise SystemExit(main())
