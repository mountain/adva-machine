#!/usr/bin/env python3
"""Read-only, bounded projected-Iota-ledger graph comparison, never a native judgment.

Project-original by dot (OpenAI), under Unknown v0.3, submitted through Mingli
Yuan's authorized account proxy; not his technical review or endorsement.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

PROFILE = 'adva.iota-ledger-structural-isomorphism.v0.1'
SCHEMA = 'adva.finite-structure-comparison.v0.1'
ALGORITHM = 'colored-directed-multigraph-backtracking.v0.1'
LIMITS = dict(input_bytes=1048576, file_bytes=131072, git_calls=64,
              nodes=8192, edges=32768, steps=2000000, depth=256,
              comparisons=32, report_bytes=16777216, wall_seconds=120)
PIN = '79aced81e972e8a4af96b118d8e236f7e337ffcb'
KNOWLEDGE_PIN = '3287c61ab7d16253605b3d0cca818f5a698e258b'
BASE = 'knowledge/received/iota-process-{}-2026-09-17-v1/materials/'
FILES = ('interpretations.json', 'contract.json', 'structure.json', 'dependencies.json')
AUTHORITY = dict(structural_matching='projected ledger only', semantic_verification='NotRun',
                 native_admission='NotGranted', automatic_refactoring=False,
                 transport_execution=False, executable_loader=False, consumer_adoption=False)
RESIDUALS = [
    'Typed semantic guards are not supplied by the source; no guard is discharged.',
    'Native source/occurrence identities and CausalCut validation are not supplied.',
    'Full annotated constructor and interval ancestry remains in the private source archive; it is not fetched.',
    'Source control/authentication and dependent source claims are not verified.',
    'Matching a projected ledger neither proves equivalence nor authorizes reuse or adoption.',
]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class Incomplete(Exception):
    def __init__(self, reason, position):
        super().__init__(reason)
        self.reason, self.position = reason, position


class Budget:
    def __init__(self, limits=None):
        self.limits = dict(LIMITS, **(limits or {}))
        if set(self.limits) != set(LIMITS) or any(type(v) is not int or v < 1 for v in self.limits.values()):
            raise ValueError('limits must be known positive integer dimensions')
        self.spent = dict.fromkeys(self.limits, 0)
        self.spent['wall_seconds'] = None
        self.started = time.monotonic()

    def tick(self, dimension='steps', amount=1, position=None):
        if time.monotonic() - self.started > self.limits['wall_seconds']:
            raise Incomplete('wall-clock safety cutoff; nondeterministic prefix', position)
        if self.spent[dimension] + amount > self.limits[dimension]:
            raise Incomplete(dimension + ' exhausted', position)
        self.spent[dimension] += amount

    def depth(self, n, position):
        self.tick(position=position)
        if n > self.limits['depth']:
            raise Incomplete('depth exhausted', position)
        self.spent['depth'] = max(self.spent['depth'], n)

    def record(self):
        return dict(limits=self.limits, spent=self.spent.copy(),
                    enforcement='cooperative counted limits and wall safety cutoff; Git calls have timeouts; not a hostile-input sandbox',
                    accounting='input bytes before JSON parsing; nodes/edges cumulative extraction; steps include extraction/search/witness checking; file_bytes/depth are maxima',
                    memory='JSON decode and canonical serialization allocate within byte caps, without a separate process-memory limit',
                    continuation='no retry, cache, hidden refill or automatic continuation',
                    wall_observation='excluded from deterministic payload; measure externally')


def exact_keys(value, keys, label):
    if type(value) is not dict or set(value) != set(keys):
        raise ValueError(label + ': missing or unsupported fields')


def integer(value, low, high, label):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(label + ': invalid integer')


def text(value, label):
    label = str(label)
    if type(value) is not str or not value:
        raise ValueError(label + ': nonempty string required')


def term(value, budget, label):
    """Validate only ordered prefix syntax; no reduction, identity or type judgment."""
    label = str(label)
    text(value, label)
    pending = [0]
    for i, token in enumerate(value):
        budget.tick(position=[label, i])
        if not pending:
            raise ValueError(label + ': trailing syntax')
        depth = pending.pop()
        budget.depth(depth, [label, i])
        if token == '@':
            pending.extend((depth + 1, depth + 1))
        elif token not in 'iksabc':
            raise ValueError(label + ': unsupported prefix token')
    if pending:
        raise ValueError(label + ': incomplete syntax')


def decode(raw, budget, label):
    # Byte cap precedes parsing. Reject duplicate keys, floats and nonfinite numbers.
    budget.tick('input_bytes', len(raw), label)
    if len(raw) > budget.limits['file_bytes']:
        raise Incomplete('file_bytes exhausted', label)
    budget.spent['file_bytes'] = max(budget.spent['file_bytes'], len(raw))
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    def refuse(value):
        raise ValueError('noninteger JSON numeric value: ' + value)
    try:
        value = json.loads(raw, object_pairs_hook=pairs, parse_float=refuse, parse_constant=refuse)
    except RecursionError as exc:
        raise Incomplete('JSON parser depth unavailable', label) from exc
    stack = [(value, 0)]
    while stack:
        item, depth = stack.pop()
        budget.depth(depth, label)
        if isinstance(item, dict):
            stack.extend((v, depth + 1) for v in item.values())
        elif isinstance(item, list):
            stack.extend((v, depth + 1) for v in item)
    return value


def git(root, args, budget):
    budget.tick('git_calls', position=args)
    remaining = budget.limits['wall_seconds'] - (time.monotonic() - budget.started)
    try:
        return subprocess.check_output(['git', '--no-replace-objects', '-C', str(root), *args],
                                       timeout=max(.001, min(20, remaining)), stderr=subprocess.PIPE,
                                       env=dict(os.environ, GIT_NO_LAZY_FETCH='1', GIT_OPTIONAL_LOCKS='0'))
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise Incomplete('exact Git source unavailable; no fallback', args) from exc


def read_source(root, repository, commit, path, expected, budget, observed_sources=None):
    if not re.fullmatch('[0-9a-f]{40}', commit):
        raise ValueError('full immutable commit required')
    if path.startswith('/') or '..' in Path(path).parts or ':' in path:
        raise ValueError('unsafe source path')
    if git(root, ['cat-file', '-t', commit + ':' + path], budget).strip() != b'blob':
        raise ValueError('source is not a Git blob')
    size = int(git(root, ['cat-file', '-s', commit + ':' + path], budget))
    if size > budget.limits['file_bytes'] or size + budget.spent['input_bytes'] > budget.limits['input_bytes']:
        raise Incomplete('source byte budget exhausted before read/parse', [repository, commit, path])
    raw = git(root, ['show', commit + ':' + path], budget)
    if len(raw) != size or sha(raw) != expected:
        raise ValueError('source byte binding mismatch')
    source = dict(repository=repository, commit=commit, path=path, source_sha256=sha(raw),
                  bytes=size, identity_verification='NotPerformed', repository_binding='caller-declared')
    # Byte observation is already valid even if JSON decoding later exhausts.
    if observed_sources is not None:
        observed_sources.append(source)
    value = decode(raw, budget, path)
    return value, source


# Exact public received bytes, not a latest lookup, executable source or secret input.
DIGESTS = dict(zip(FILES, (
    '8009db7b8828ae76aa01b25684b9aa974fc91c4fcb64a439946701a49fe528b1',
    'c2656bf793d4175054cfc1822618233fe0bbb65a6f276578e77ba9749186bef6',
    'fa0df8a1610d5d5e5c3d8eef85624a78f7b33b9d4cd7e1a757a418e5d8bf6071',
    '3a33c2a17145629f07d70533184358708f80a88687713e10e03d270d96448ea3')))


RECEIPT_DIGESTS = dict(machine='14d4d4d374b45dee1e00222875e52aa4fe48eb5c400aee1ab5801f42290de6f9',
                       knowledge='171672842756cf0584091ad0f204fbf0fd560d8208ff4e4b2e617293611e7caa')


def load_package(root, repository, commit, receiver, budget, observed_sources=None):
    values, sources = {}, []
    for filename in FILES:
        value, source = read_source(root, repository, commit, BASE.format(receiver) + filename,
                                    DIGESTS[filename], budget, observed_sources)
        values[filename] = value
        sources.append(source)
    ledger = values['interpretations.json']
    exact_keys(ledger, ('schema', 'source_archive_sha256', 'families'), 'ledger')
    if ledger['schema'] != 'adva.iota-term-ledger.v1' or type(ledger['families']) is not list:
        raise ValueError('unsupported ledger schema')
    if any(type(f) is not dict for f in ledger['families']):
        raise ValueError('family must be an object')
    names = [f.get('name') for f in ledger['families']]
    if any(type(n) is not str for n in names) or len(set(names)) != len(names):
        raise ValueError('invalid or duplicate family selectors')
    conditions = dict(profile=PROFILE, source_schema=ledger['schema'],
                      source_archive_sha256=ledger['source_archive_sha256'],
                      premises=values['contract.json'],
                      guards=dict(status='Unavailable', protected=values['contract.json']['protected']),
                      preservation=values['structure.json']['preserve'],
                      residuals=values['structure.json']['open_questions'],
                      dependencies=values['dependencies.json'])
    receipt_path = BASE.format(receiver).removesuffix('materials/') + 'receipt.json'
    receipt, receipt_source = read_source(root, repository, commit, receipt_path,
                                          RECEIPT_DIGESTS[receiver], budget, observed_sources)
    sources.append(receipt_source)
    context = dict(source=receipt_source, original_receipt=receipt,
                   observation='Historical supplied receipt only; not a fresh receive or revalidation')
    return dict(families=ledger['families'], conditions=conditions, sources=sources, receiver_context=context)


def extract(f, package, budget):
    """No imported source code runs. IDs here are documentary graph handles only."""
    exact_keys(f, ('name', 'source', 'normal', 'entry_roles', 'exit_roles', 'role_reading',
                  'events', 'cuts', 'edges', 'final_apertures', 'clocks', 'schedules',
                  'partition_linear', 'full_process_sha256'), 'family')
    text(f['name'], 'family name')
    for key in ('events', 'cuts', 'edges', 'final_apertures', 'entry_roles', 'exit_roles', 'role_reading'):
        if type(f[key]) is not list:
            raise ValueError(key + ': list required')
    for key in ('entry_roles', 'exit_roles'):
        if len(f[key]) != 3 or any(type(x) is not int for x in f[key]) or sorted(f[key]) != [0, 1, 2]:
            raise ValueError('invalid ordered boundary roles')
    if len(f['role_reading']) != 3 or any(x not in ('{}', '[]', '()') for x in f['role_reading']):
        raise ValueError('invalid role reading')
    if type(f['clocks']) is not dict or any(type(v) is not list or len(v) != len(f['events'])
                                          for v in f['clocks'].values()):
        raise ValueError('invalid clock coverage')
    integer(f['schedules'], 0, 2**63 - 1, 'schedule count')
    text(f['partition_linear'], 'partition reading')
    if not re.fullmatch('[0-9a-f]{64}', f['full_process_sha256']):
        raise ValueError('full-process digest required')
    if len(f['events']) > 24 or len(f['cuts']) > 128:
        raise ValueError('source family exceeds frozen finite representation capacity')
    nodes, edges = {}, []
    def node(identifier, kind, labels, selector):
        budget.tick('nodes', position=selector)
        if identifier in nodes:
            raise ValueError('duplicate graph handle')
        nodes[identifier] = dict(kind=kind, labels=labels, selector=selector)
        return identifier
    def edge(a, b, label, selector):
        budget.tick('edges', position=selector)
        edges.append(dict(id='edge:' + str(len(edges)), source=a, target=b,
                          label=label, selector=selector))
    for key in ('source', 'normal'):
        term(f[key], budget, key)
    node('boundary', 'OrderedInterface', {k: f[k] for k in ('source', 'normal', 'entry_roles', 'exit_roles', 'role_reading')}, '')
    event_ids = {}
    for i, event in enumerate(f['events']):
        exact_keys(event, ('id', 'rule', 'deps', 'before', 'after', 'path', 'discard'), 'event')
        text(event['id'], 'event source identifier')
        if event['id'] in event_ids:
            raise ValueError('duplicate event source identifier')
        if event['rule'] not in (0, 2, 3) or type(event['rule']) is not int:
            raise ValueError('unsupported event rule tag')
        if type(event['path']) is not list or any(type(x) is not int or x not in (0, 1) for x in event['path']):
            raise ValueError('invalid ordered term path')
        budget.depth(len(event['path']), ['events', i, 'path'])
        if type(event['deps']) is not list:
            raise ValueError('event dependencies must be a list')
        for dep in event['deps']:
            integer(dep, 0, len(f['events']) - 1, 'dependency index')
        for key in ('before', 'after'):
            term(event[key], budget, ['events', i, key])
        if event['discard'] is not None:
            term(event['discard'], budget, ['events', i, 'discard'])
        labels = {k: event[k] for k in ('id', 'rule', 'before', 'after', 'path', 'discard')}
        labels['clocks'] = {k: v[i] for k, v in f['clocks'].items()}
        event_ids[event['id']] = node('event:' + str(i), 'LedgerEvent', labels, '/events/' + str(i))
    for i, event in enumerate(f['events']):
        edge('boundary', 'event:' + str(i), 'contains-event', '/events/' + str(i))
        for j, dep in enumerate(event['deps']):
            edge('event:' + str(dep), 'event:' + str(i), 'depends-before', f'/events/{i}/deps/{j}')
    cuts = {}
    for i, cut in enumerate(f['cuts']):
        exact_keys(cut, ('mask', 'term'), 'cut')
        integer(cut['mask'], 0, (1 << len(f['events'])) - 1, 'cut mask')
        if cut['mask'] in cuts:
            raise ValueError('duplicate cut mask')
        term(cut['term'], budget, ['cuts', i, 'term'])
        identifier = node('cut:' + str(i), 'LedgerCut', dict(term=cut['term'],
                          entry=cut['mask'] == 0, terminal=cut['mask'] == (1 << len(f['events'])) - 1), '/cuts/' + str(i))
        cuts[cut['mask']] = identifier
        edge('boundary', identifier, 'contains-cut', '/cuts/' + str(i))
        for j in range(len(f['events'])):
            budget.tick(position=['cut-membership', i, j])
            if cut['mask'] & (1 << j):
                edge('event:' + str(j), identifier, 'performed-at-cut', f'/cuts/{i}/mask')
    if 0 not in cuts or (1 << len(f['events'])) - 1 not in cuts:
        raise ValueError('missing entry or terminal cut')
    for i, transition in enumerate(f['edges']):
        if type(transition) is not list or len(transition) != 3:
            raise ValueError('invalid transition triple')
        a, b, e = transition
        for mask in (a, b):
            integer(mask, 0, (1 << len(f['events'])) - 1, 'transition cut mask')
            if mask not in cuts:
                raise ValueError('transition cut unavailable')
        integer(e, 0, len(f['events']) - 1, 'transition event')
        identifier = node('transition:' + str(i), 'LedgerTransition', {}, '/edges/' + str(i))
        for start, end, label in ((cuts[a], identifier, 'transition-input'),
                                  (identifier, cuts[b], 'transition-output'),
                                  ('event:' + str(e), identifier, 'transition-event')):
            edge(start, end, label, '/edges/' + str(i))
    origins = {}
    occurrences = set()
    for i, aperture in enumerate(f['final_apertures']):
        exact_keys(aperture, ('port', 'occurrence', 'origin', 'copy_path'), 'aperture')
        integer(aperture['port'], 0, 2, 'aperture port')
        for key in ('occurrence', 'origin'):
            text(aperture[key], key)
        if aperture['occurrence'] in occurrences:
            raise ValueError('collapsed occurrence identifier')
        occurrences.add(aperture['occurrence'])
        if type(aperture['copy_path']) is not list:
            raise ValueError('invalid copy lineage')
        identifier = node('occurrence:' + str(i), 'ApertureOccurrence', aperture, '/final_apertures/' + str(i))
        edge('boundary', identifier, 'ordered-output:' + str(i), '/final_apertures/' + str(i))
        if aperture['origin'] not in origins:
            origins[aperture['origin']] = node('origin:' + str(len(origins)), 'DeclaredSourceOrigin',
                                             dict(origin=aperture['origin']), f'/final_apertures/{i}/origin')
        edge(origins[aperture['origin']], identifier, 'source-of-occurrence', f'/final_apertures/{i}/origin')
        for j, copy in enumerate(aperture['copy_path']):
            if type(copy) is not list or len(copy) != 2 or type(copy[0]) is not str or copy[0] not in event_ids:
                raise ValueError('copy event reference unavailable')
            integer(copy[1], 0, 1, 'copy branch')
            edge(event_ids[copy[0]], identifier, f'copy-lineage:{j}:branch:{copy[1]}', f'/final_apertures/{i}/copy_path/{j}')
    source = dict(package['sources'][0], selector='/families/' + str(package['families'].index(f)),
                  family_name=f['name'], receiver_context=package['receiver_context'],
                  home=package['conditions']['dependencies']['source_repository'], original_revision=package['conditions']['premises']['source_revision'])
    source['documentary_id'] = f"{source['repository']}@{source['commit']}:{source['path']}#{source['selector']}"
    return dict(profile=PROFILE, nodes=nodes, edges=edges, source=source,
                conditions=dict(package['conditions'], readings={k: f[k] for k in ('schedules', 'partition_linear', 'full_process_sha256')}),
                residuals=RESIDUALS.copy())


def graph_index(graph, budget):
    exact_keys(graph, ('profile', 'nodes', 'edges', 'source', 'conditions', 'residuals'), 'graph')
    if graph['profile'] != PROFILE or type(graph['nodes']) is not dict or type(graph['edges']) is not list:
        raise ValueError('unsupported graph/profile')
    colors, adjacency, edge_ids = {}, defaultdict(Counter), set()
    if any(type(n) is not str for n in graph['nodes']):
        raise ValueError('node handles must be strings')
    if len(graph['nodes']) > budget.limits['nodes'] or len(graph['edges']) > budget.limits['edges']:
        raise Incomplete('graph capacity exhausted', 'index')
    for identifier, node in sorted(graph['nodes'].items()):
        budget.tick(position=['index-node', identifier])
        exact_keys(node, ('kind', 'labels', 'selector'), 'node')
        text(identifier, 'node handle')
        text(node['kind'], 'node kind')
        if type(node['selector']) is not str or type(node['labels']) is not dict:
            raise ValueError('node selector/labels have wrong types')
        colors[identifier] = canonical([node['kind'], node['labels']])
    for edge in graph['edges']:
        budget.tick(position='index-edge')
        exact_keys(edge, ('id', 'source', 'target', 'label', 'selector'), 'edge')
        for key in ('id', 'source', 'target', 'label'):
            text(edge[key], 'edge ' + key)
        if type(edge['selector']) is not str:
            raise ValueError('edge selector must be a string')
        if edge['id'] in edge_ids or edge['source'] not in colors or edge['target'] not in colors:
            raise ValueError('invalid edge endpoint or duplicate edge ID')
        edge_ids.add(edge['id'])
        adjacency[(edge['source'], edge['target'])][edge['label']] += 1
    return colors, dict(adjacency)


def verify_mapping(left, right, mapping, budget):
    """Separate full-bijection/edge-multiset check; no search decisions are trusted."""
    lc, _ = graph_index(left, budget)
    rc, _ = graph_index(right, budget)
    if set(mapping) != set(lc) or len(set(mapping.values())) != len(rc) or set(mapping.values()) != set(rc):
        return False
    if canonical(left['conditions']) != canonical(right['conditions']) or canonical(left['residuals']) != canonical(right['residuals']):
        return False
    for a, b in mapping.items():
        budget.tick(position=['verify-node', a, b])
        if lc[a] != rc[b]:
            return False
    a_edges, b_edges = Counter(), Counter()
    for graph, counts, mapped in ((left, a_edges, True), (right, b_edges, False)):
        for e in graph['edges']:
            budget.tick(position=['verify-edge', e['id']])
            a, b = (mapping[e['source']], mapping[e['target']]) if mapped else (e['source'], e['target'])
            counts[(a, b, e['label'])] += 1
    return a_edges == b_edges


def verify_witness(left, right, witness, budget):
    """Check the emitted node and edge bijections, anchors and evidence bindings."""
    exact_keys(witness, ('nodes', 'edges', 'occurrences', 'sources', 'boundary',
                        'unmatched_left', 'unmatched_right', 'lost_conditions',
                        'left_graph_sha256', 'right_graph_sha256'), 'witness')
    if witness['left_graph_sha256'] != sha(canonical(left)) or witness['right_graph_sha256'] != sha(canonical(right)):
        return False
    for key in ('nodes', 'edges'):
        rows = witness[key]
        if type(rows) is not list or any(type(row) is not list or len(row) != 2 or
                                       any(type(v) is not str for v in row) for row in rows):
            return False
        if len({r[0] for r in rows}) != len(rows) or len({r[1] for r in rows}) != len(rows):
            return False
    mapping = dict(witness['nodes'])
    if not verify_mapping(left, right, mapping, budget):
        return False
    le, re = ({e['id']: e for e in g['edges']} for g in (left, right))
    em = dict(witness['edges'])
    if set(em) != set(le) or set(em.values()) != set(re):
        return False
    for a, b in em.items():
        budget.tick(position=['verify-edge-bijection', a, b])
        if (mapping[le[a]['source']], mapping[le[a]['target']], le[a]['label']) != (re[b]['source'], re[b]['target'], re[b]['label']):
            return False
    for key, kind in (('occurrences', 'ApertureOccurrence'), ('sources', 'DeclaredSourceOrigin'),
                      ('boundary', 'OrderedInterface')):
        expected = [row for row in witness['nodes'] if left['nodes'][row[0]]['kind'] == kind]
        if canonical(witness[key]) != canonical(expected):
            return False
    return all(witness[key] == [] for key in ('unmatched_left', 'unmatched_right', 'lost_conditions'))


def compare(left, right, budget):
    result = dict(left=left['source'], right=right['source'], profile=PROFILE, algorithm=ALGORITHM,
                  level='L2', relation='colored directed multigraph isomorphism',
                  permitted_transformations=['graph-local handle renaming', 'unordered record serialization permutation'],
                  status='Unknown', complete=False, witness=None, partial_mapping=[], differences=[],
                  authority=AUTHORITY.copy(), residuals=left['residuals'],
                  conditions=dict(left=left['conditions'], right=right['conditions']),
                  input_graph_sha256=dict(left=sha(canonical(left)), right=sha(canonical(right))),
                  resource_start=budget.spent.copy(),
                  potentially_affected_consumers=dict(status='Unknown', reason='No exhaustive consumer-use inventory in this profile'),
                  suggested_next_check='Review mapped source coordinates and conditions; executable reuse requires a separately versioned G3 receiving/checking profile')
    mapping = {}
    def finish():
        result['resource_end'] = budget.spent.copy()
        retained = set(mapping) if result['status'] in ('Unknown', 'StructuralMatchCandidate') else set()
        result['unmatched_left'] = sorted(set(left['nodes']) - retained)
        result['unmatched_right'] = sorted(set(right['nodes']) - {mapping[n] for n in retained})
        return result
    try:
        budget.tick('comparisons', position=[left['source'], right['source']])
        lc, la = graph_index(left, budget)
        rc, ra = graph_index(right, budget)
        for key in ('conditions', 'residuals'):
            if canonical(left[key]) != canonical(right[key]):
                result['differences'].append(dict(kind=key + '-differ', left=left[key], right=right[key]))
        if Counter(lc.values()) != Counter(rc.values()) or len(left['edges']) != len(right['edges']):
            result['differences'].append(dict(kind='typed-label-or-multiplicity-mismatch',
                left_nodes=len(lc), right_nodes=len(rc), left_edges=len(left['edges']), right_edges=len(right['edges'])))
            result.update(status='NoMatchWithinProfile', complete=True)
            return finish()
        if result['differences']:
            result.update(status='NoMatchWithinProfile', complete=True)
            return finish()
        def signatures(graph, colors):
            incident = defaultdict(list)
            for e in graph['edges']:
                budget.tick(position=['signature', e['id']])
                incident[e['source']].append(('out', e['label'], colors[e['target']].hex()))
                incident[e['target']].append(('in', e['label'], colors[e['source']].hex()))
            return {n: canonical([colors[n].hex(), sorted(incident[n])]) for n in colors}
        # One exact typed incidence refinement; signatures are full bytes, not semantic IDs.
        ls, rs = signatures(left, lc), signatures(right, rc)
        if Counter(ls.values()) != Counter(rs.values()):
            result.update(status='NoMatchWithinProfile', complete=True,
                          differences=[dict(kind='directed-typed-incidence-mismatch')])
            return finish()
        classes = defaultdict(list)
        for n in sorted(rs):
            classes[rs[n]].append(n)
        candidates = {n: classes[ls[n]] for n in ls}
        order = sorted(lc, key=lambda n: (len(candidates[n]), n))
        offsets, used, depth = [0] * len(order), set(), 0
        while 0 <= depth < len(order):
            budget.depth(depth + 1, ['search-depth', depth])
            a = order[depth]
            if offsets[depth] == len(candidates[a]):
                offsets[depth] = 0
                depth -= 1
                if depth >= 0:
                    used.remove(mapping.pop(order[depth]))
                continue
            b = candidates[a][offsets[depth]]
            offsets[depth] += 1
            budget.tick(position=['try', depth, a, b])
            if b in used:
                continue
            compatible = la.get((a, a), {}) == ra.get((b, b), {})
            for x, y in mapping.items():
                budget.tick(position=['adjacency', a, b, x, y])
                if la.get((a, x), {}) != ra.get((b, y), {}) or la.get((x, a), {}) != ra.get((y, b), {}):
                    compatible = False
                    break
            if compatible:
                mapping[a] = b
                used.add(b)
                depth += 1
        if depth < 0:
            result.update(status='NoMatchWithinProfile', complete=True,
                          differences=[dict(kind='finite-search-exhausted-all-bijections')])
            return finish()
        if not verify_mapping(left, right, mapping, budget):
            raise ValueError('internal witness verification failed')
        targets = defaultdict(list)
        for edge in right['edges']:
            budget.tick(position=['edge-map-index', edge['id']])
            targets[(edge['source'], edge['target'], edge['label'])].append(edge['id'])
        for values in targets.values():
            values.sort(reverse=True)
        edge_map = []
        for edge in sorted(left['edges'], key=lambda e: e['id']):
            budget.tick(position=['edge-map', edge['id']])
            key = (mapping[edge['source']], mapping[edge['target']], edge['label'])
            edge_map.append([edge['id'], targets[key].pop()])
        rows = [[a, mapping[a]] for a in sorted(mapping)]
        witness = dict(nodes=rows, edges=edge_map,
                       occurrences=[row for row in rows if left['nodes'][row[0]]['kind'] == 'ApertureOccurrence'],
                       sources=[row for row in rows if left['nodes'][row[0]]['kind'] == 'DeclaredSourceOrigin'],
                       boundary=[row for row in rows if left['nodes'][row[0]]['kind'] == 'OrderedInterface'],
                       unmatched_left=[], unmatched_right=[], lost_conditions=[],
                       left_graph_sha256=sha(canonical(left)), right_graph_sha256=sha(canonical(right)))
        if not verify_witness(left, right, witness, budget):
            raise ValueError('emitted witness verification failed')
        result.update(status='StructuralMatchCandidate', complete=True, witness=witness,
                      evidence_sha256=sha(canonical(witness)))
    except Incomplete as exc:
        result.update(status='Unknown', complete=False, stopping_position=exc.position,
                      reason=exc.reason, partial_mapping=sorted(map(list, mapping.items())))
    return finish()


def run(machine_root, knowledge_root, limits=None):
    budget = Budget(limits)
    result = dict(schema=SCHEMA, profile=PROFILE, algorithm=ALGORITHM, status='Unknown',
                  complete=False, sources=[], graphs=[], comparisons=[], authority=AUTHORITY.copy(), residuals=RESIDUALS.copy())
    try:
        machine = load_package(machine_root, 'mountain/adva-machine', PIN, 'machine', budget, result['sources'])
        knowledge = load_package(knowledge_root, 'mountain/adva', KNOWLEDGE_PIN, 'knowledge', budget, result['sources'])
        graphs = []
        for package in (machine, knowledge):
            current = {}
            for family in package['families']:
                graph = extract(family, package, budget)
                current[family['name']] = graph
                result['graphs'].append(graph)
            graphs.append(current)
        if set(graphs[0]) != set(graphs[1]):
            raise ValueError('pinned receiver family selector sets differ')
        pairs = [(name, name) for name in sorted(graphs[0])]
        pairs += [('identity', 'double-identity'), ('independent-iota', 'changed-roles'), ('copy', 'copy-pending')]
        for a, b in pairs:
            comparison = compare(graphs[0][a], graphs[1][b], budget)
            result['comparisons'].append(comparison)
            if comparison['status'] == 'Unknown':
                raise Incomplete(comparison['reason'], comparison['stopping_position'])
        result.update(status='CompleteWithinDeclaredView', complete=True)
    except Incomplete as exc:
        result.update(reason=exc.reason, stopping_position=exc.position)
    except (ValueError, KeyError, TypeError, UnicodeError) as exc:
        result.update(status='RejectedInput', reason=str(exc))
    result['budget'] = budget.record()
    return result


def encode_report(report, budget_limit):
    # Output size is a maximum, not an extra search allowance. Include the newline.
    def encoded(value):
        previous = -1
        while previous != value['budget']['spent']['report_bytes']:
            previous = value['budget']['spent']['report_bytes']
            raw = canonical(value) + b'\n'
            value['budget']['spent']['report_bytes'] = len(raw)
        return canonical(value) + b'\n'
    raw = encoded(report)
    if len(raw) > budget_limit:
        envelope = dict(schema=SCHEMA, profile=PROFILE, status='Unknown', complete=False,
                      reason='report_bytes exhausted', omitted_payload_sha256=sha(raw),
                      sources=report['sources'], budget=report['budget'], authority=AUTHORITY.copy(),
                      stopping_position=dict(encoded_bytes=len(raw)))
        report.clear()
        report.update(envelope)
        raw = encoded(report)
        if len(raw) > budget_limit:
            raise ValueError('report budget too small for Unknown envelope; no report emitted')
    return raw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--machine-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--knowledge-root', type=Path, required=True)
    args = parser.parse_args()
    report = run(args.machine_root, args.knowledge_root)
    # Bind actual local generator bytes separately from pinned input commits.
    report['generator'] = dict(path='scripts/finite_structure_match.py', source_sha256=sha(Path(__file__).read_bytes()),
        head_commit=subprocess.check_output(['git', '--no-replace-objects', '-C', str(Path(__file__).resolve().parents[1]), 'rev-parse', 'HEAD'], env=dict(os.environ, GIT_NO_LAZY_FETCH='1', GIT_OPTIONAL_LOCKS='0')).decode().strip(),
        commit_binding='HEAD records checkout ancestry; actual generator bytes bound separately, including uncommitted edits',
        setup='one Git call and local generator read, separately from input/search account')
    print(encode_report(report, LIMITS['report_bytes']).decode(), end='')
    return 0 if report['complete'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
