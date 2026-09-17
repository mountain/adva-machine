"""Finite prefix-term/ledger interpretation, separate from native transport.

Original contribution by Codex (OpenAI) under Unknown v0.3.
The same checker is explicitly run at the sender and both receivers; those
runs are not independent authors, humans or general semantic certificates.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import resource
import signal
import sys
import time
import traceback

FILES = ('contract.json', 'iota.md', 'kernel-program.json', 'interpretations.json',
         'probes.json', 'dependencies.json', 'structure.json', 'check.py')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def package_pin(root):
    rows = [[name, sha((root/name).read_bytes())] for name in FILES]
    return sha(json.dumps(rows, separators=(',', ':')).encode())


def parse(text):
    pos = 0
    def read():
        nonlocal pos
        if pos >= len(text):
            raise ValueError('incomplete prefix term')
        token = text[pos]
        pos += 1
        if token == '@':
            return (read(), read())
        if token not in 'iksabc':
            raise ValueError('unknown term token')
        return token
    result = read()
    if pos != len(text):
        raise ValueError('trailing term tokens')
    return result


def show(t):
    return '@'+show(t[0])+show(t[1]) if isinstance(t, tuple) else t


def from_wire(t):
    if t['tag'] == 1:
        return (from_wire(t['fields'][0]), from_wire(t['fields'][1]))
    if t['tag'] == 4:
        return 'abc'[t['fields'][0]['value']]
    return {0:'i', 2:'k', 3:'s'}[t['tag']]


def wire(t):
    if isinstance(t, tuple):
        return {'kind':'node', 'tag':1, 'fields':[wire(t[0]), wire(t[1])]}
    if t in 'abc':
        return {'kind':'node', 'tag':4, 'fields':[{'kind':'integer', 'value':'abc'.index(t)}]}
    return {'kind':'node', 'tag':{'i':0, 'k':2, 's':3}[t], 'fields':[]}


def reduce_root(t, swapped=False):
    head, args = t, []
    while isinstance(head, tuple):
        args.append(head[1])
        head = head[0]
    args.reverse()
    if head == 'i' and len(args) == 1:
        x, = args
        return ((x, 'k' if swapped else 's'), 's' if swapped else 'k'), None
    if head == 'k' and len(args) == 2:
        return args[0], args[1]
    if head == 's' and len(args) == 3:
        x, y, z = args
        return ((x, z), (y, z)), None
    raise ValueError('not a saturated internal root redex')


def subtree(t, path):
    for step in path:
        t = t[step]
    return t


def replace(t, path, value):
    if not path:
        return value
    children = list(t)
    children[path[0]] = replace(children[path[0]], path[1:], value)
    return tuple(children)


class Budget:
    def __init__(self, limits):
        self.limits, self.work, self.assertions = limits, 0, 0
        self.start = time.monotonic()
    def tick(self):
        self.work += 1
        if self.work > self.limits['counted_work_per_check'] or time.monotonic()-self.start > self.limits['wall_seconds_per_check']:
            raise TimeoutError('interpretation account exhausted')
    def require(self, condition, reason):
        self.tick()
        self.assertions += 1
        if not condition:
            raise ValueError(reason)


def roles(policy):
    return {port:glyph for glyph, port in zip(('{}','[]','()'), policy)}


def check_family(f, budget):
    need = budget.require
    events = f['events']
    n = len(events)
    need(n <= budget.limits['events_per_family'], 'event capacity')
    need(len({e['id'] for e in events}) == n, 'event coordinates collapsed')
    source = parse(f['source'])
    need(all(c not in 'ks' for c in f['source']), 'source has primitive K/S')
    need(show(from_wire(wire(source))) == f['source'], 'prefix/tagged-tree round trip')
    deps = []
    for i, event in enumerate(events):
        need(all(type(d) is int and 0 <= d < i for d in event['deps']), 'noncausal dependency')
        deps.append(sum(1 << d for d in set(event['deps'])))
        before, after = parse(event['before']), parse(event['after'])
        got, discarded = reduce_root(before)
        need(got == after, 'local root rule differs')
        need(event['discard'] == (None if discarded is None else show(discarded)), 'discarded argument erased or changed')
        need(show(from_wire(wire(after))) == event['after'], 'replacement round trip')
    advertised = {c['mask']:parse(c['term']) for c in f['cuts']}
    need(len(advertised) == len(f['cuts']), 'duplicate cut')
    states, todo, edges, ways = {0:source}, [0], [], {0:1}
    while todo:
        mask = todo.pop(0)
        for i, event in enumerate(events):
            budget.tick()
            if mask & (1 << i) or deps[i] & mask != deps[i]:
                continue
            old = subtree(states[mask], event['path'])
            need(show(old) == event['before'], 'event observes a different term')
            new, _ = reduce_root(old)
            state = replace(states[mask], event['path'], new)
            end = mask | (1 << i)
            edges.append((mask, end, i))
            ways[end] = ways.get(end, 0)+ways[mask]
            if end in states:
                need(states[end] == state, 'two paths disagree on cut term')
            else:
                need(len(states) < budget.limits['cuts_per_family'], 'cut capacity')
                states[end] = state
                todo.append(end)
    need(states == advertised, 'incomplete or incorrect cut family')
    need(sorted(edges) == sorted(map(tuple, f['edges'])), 'transition correspondence differs')
    terminal = (1 << n)-1
    need(show(states[terminal]) == f['normal'], 'terminal term differs')
    need(ways[terminal] == f['schedules'], 'schedule count differs')
    for policy in (f['entry_roles'], f['exit_roles']):
        need(sorted(policy) == [0,1,2], 'boundary does not assign three roles')
    need(f['role_reading'] == [roles(f['exit_roles'])[i] for i in range(3)], 'same bytes with incompatible role interpretation')
    leaves = f['final_apertures']
    need(len({v['occurrence'] for v in leaves}) == len(leaves), 'copy occurrences identified')
    need(Counter(v['port'] for v in leaves) == Counter('abc'.index(c) for c in f['normal'] if c in 'abc'), 'aperture fibre multiplicity differs')
    for clock in f['clocks'].values():
        ts = [Q(v) for v in clock]
        need(len(ts) == n, 'clock coverage differs')
        need(all(ts[d] < ts[i] for i,e in enumerate(events) for d in e['deps']), 'clock reverses dependency')
        for time in set(ts):
            mask = sum(1 << i for i,t in enumerate(ts) if t < time)
            need(mask in states, 'clock threshold is not an admitted cut')
    degrees = Counter()
    for a,b,_ in edges:
        degrees[a] += 1
        degrees[b] += 1
    scale = max(1, 2*max(degrees.values(), default=0))
    trace = Q(sum(degrees.values()), scale)
    need(f['partition_linear'] == str(-trace), 'operator trace differs')
    return {'name':f['name'], 'events':n, 'cuts':len(states), 'edges':len(edges),
            'schedules_counted':ways[terminal], 'partition_linear':str(-trace)}


def join(interpretation, receiver, object_evidence, reserve):
    # Three separately paid, required predicates. No checkpoint advance on failure.
    spent = 0
    for available in (interpretation, receiver, object_evidence):
        if spent >= reserve:
            return {'status':'Unknown', 'reason':'join reserve exhausted', 'spent':spent, 'advance':False}
        spent += 1
        if available is None:
            return {'status':'Unknown', 'reason':'required correspondence or observation unavailable', 'spent':spent, 'advance':False}
        if not available:
            return {'status':'Counterexample', 'reason':'required predicate failed', 'spent':spent, 'advance':False}
    return {'status':'ScopedInterpretationChecked', 'spent':spent, 'advance':True}


def controls(families, budget):
    by_name = {f['name']:f for f in families}
    rows = []
    def refusal(name, value):
        try:
            check_family(value, budget)
        except ValueError as error:
            rows.append({'name':name, 'status':'Counterexample', 'reason':str(error)})
        else:
            raise AssertionError('control was accepted: '+name)
    first = by_name['independent-iota']['events'][0]
    wrong, _ = reduce_root(parse(first['before']), swapped=True)
    budget.require(show(wrong) != first['after'], 'swapped iota must differ')
    rows.append({'name':'swapped-iota-expansion', 'status':'Counterexample', 'before':first['before'], 'wrong':show(wrong), 'retained':first['after']})
    changed = deepcopy(by_name['changed-roles'])
    changed['role_reading'] = ['{}','[]','()']
    refusal('same-bytes-different-role-reading', changed)
    a,b = by_name['identity'],by_name['double-identity']
    budget.require(a['normal'] == b['normal'] and len(a['cuts']) != len(b['cuts']), 'endpoint-only counterexample missing')
    rows.append({'name':'equal-value-erases-process', 'status':'Counterexample', 'normal':a['normal'], 'cut_counts':[len(a['cuts']),len(b['cuts'])]})
    f = by_name['chain-and-single']
    dep = [set(e['deps']) for e in f['events']]
    def independent(a,b):
        return a != b and a not in dep[b] and b not in dep[a]
    witness = next((a,b,c) for a in range(3) for b in range(3) for c in range(3)
                   if a in dep[c] and independent(a,b) and independent(b,c))
    rows.append({'name':'concurrency-is-simultaneity', 'status':'Counterexample', 'events':list(witness)})
    for name,args in [('missing-correspondence',(None,True,True,3)),
                      ('missing-object-evidence',(True,True,None,3)),
                      ('exhausted-join-reserve',(True,True,True,2))]:
        outcome = join(*args)
        budget.require(outcome['status'] == 'Unknown' and not outcome['advance'], name)
        rows.append({'name':name, **outcome})
    changed = deepcopy(by_name['discard'])
    next(e for e in changed['events'] if e['discard'] is not None)['discard'] = None
    refusal('erased-discard', changed)
    changed = deepcopy(by_name['copy'])
    copies = [v for v in changed['final_apertures'] if v['port'] == 2]
    copies[1]['occurrence'] = copies[0]['occurrence']
    refusal('identified-copy-occurrences', changed)
    changed = deepcopy(by_name['independent-iota'])
    changed['cuts'].pop()
    refusal('incomplete-cut-family', changed)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--materials', type=Path, required=True)
    parser.add_argument('--expect-package', required=True)
    parser.add_argument('--machine', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--stage', choices=('source-preflight','knowledge-after-reception','machine-after-reception'), required=True)
    args = parser.parse_args()
    root = args.materials.resolve()
    contract = json.loads((root/'contract.json').read_text())
    limits = contract['limits']
    if package_pin(root) != args.expect_package:
        raise ValueError('independently supplied package pin differs')
    sys.path.insert(0, str(args.machine.resolve()))
    dependencies = json.loads((root/'dependencies.json').read_text())
    for name,pin in dependencies['machine_files'].items():
        if sha((args.machine/name).read_bytes()) != pin:
            raise ValueError('required machine component differs: '+name)
    binary = args.machine/'target/release/adva'
    if sha(binary.read_bytes()) != dependencies['native_binary_sha256']:
        raise ValueError('required native executable differs')
    from toolchain.process import Account, Exhausted
    from toolchain.execute import run
    account = Account(args.output, wall=limits['wall_seconds_per_check'], cpu=limits['cpu_seconds_per_check'],
                      launches=9, native_launches=9, artifacts=limits['artifacts_per_check']-1048576)
    budget = Budget(limits)
    def stop(_signum,_frame):
        raise TimeoutError('supervisor limit')
    signal.signal(signal.SIGALRM, stop)
    signal.signal(signal.SIGXCPU, stop)
    signal.alarm(limits['wall_seconds_per_check'])
    resource.setrlimit(resource.RLIMIT_CPU, (limits['cpu_seconds_per_check'],limits['cpu_seconds_per_check']+1))
    resource.setrlimit(resource.RLIMIT_AS, (limits['address_space_bytes'],limits['address_space_bytes']))
    report = {'schema':'adva.iota-interpretation-result.v1', 'stage':args.stage, 'package_sha256':args.expect_package,
              'status':'Unknown', 'native_admission':'NoPSC0Admission', 'physical_interpretation':'Open',
              'families':[], 'native':[], 'controls':[], 'checkpoint_advanced':False}
    try:
        size = 0
        for name in FILES:
            raw = (root/name).read_bytes()
            size += len(raw)
            budget.require(len(raw) <= limits['bytes_per_material'], 'material exceeds profile capacity')
        budget.require(size <= limits['total_material_bytes'], 'package exceeds profile capacity')
        account.save('package-inventory.json', {name:sha((root/name).read_bytes()) for name in FILES})
        account.save('contract.json', (root/'contract.json').read_bytes())
        families = json.loads((root/'interpretations.json').read_text())['families']
        budget.require([f['name'] for f in families] == contract['fixtures'], 'declared fixture coverage')
        report['families'] = [check_family(f,budget) for f in families]
        report['controls'] = controls(families,budget)
        budget.require([c['name'] for c in report['controls']] == contract['controls'], 'control coverage')
        probes = json.loads((root/'probes.json').read_text())
        program = json.loads((root/'kernel-program.json').read_text())
        budget.require([p['name'] for p in probes] == contract['native_probes'], 'native probe coverage')
        by_name = {f['name']:f for f in families}
        for probe in probes:
            name = probe['name']
            budget.require(show(from_wire(probe['input']['fields'][0])) == by_name[name]['source'], 'native probe source differs')
            request = {'schema':'adva.machine.request.v0', 'profile':'data-machine-v2', 'program':program,
                       'input':probe['input'], 'fuel':limits['native_fuel_per_probe'], 'quantum':limits['native_fuel_per_probe']}
            native = run(request, 'rust', binary, account, 'native-'+name)
            account.save('native-'+name+'/report.json', native)
            budget.require(native['verification']['status'] == 'NativeReplayPassed', 'native replay failed')
            budget.require(native['outcome']['kind'] == 'Returned', 'native did not return')
            result = native['outcome']['value']['fields']
            budget.require(result[0] == {'kind':'integer','value':0}, 'native object normalization incomplete')
            budget.require(show(from_wire(result[1])) == by_name[name]['normal'], 'native object observation disagrees')
            budget.require(result[2:4] == probe['input']['fields'][1:3], 'native boundary changed')
            budget.require(len(result[4]['fields']) == len(by_name[name]['events']), 'native event count changed')
            report['native'].append({'name':name, 'steps':native['execution']['steps'], 'verification':native['verification']['status']})
        conclusion = join(True, True, len(report['native']) == 3, limits['join_predicate_units'])
        report.update(status=conclusion['status'], checkpoint_advanced=conclusion['advance'], join=conclusion,
                      permitted_use='Finite iota term/ledger comparison and the three checked native probes; documentary transport has its own receipt')
    except Exception as error:
        report.update(status='Unknown' if isinstance(error,(TimeoutError,Exhausted,MemoryError)) else 'ImplementationFailure',
                      failure={'type':type(error).__name__, 'reason':str(error), 'traceback':traceback.format_exc()})
    finally:
        signal.alarm(0)
        report.update(assertions=budget.assertions, counted_work=budget.work, cost=account.cost(),
                      authorship='Codex (OpenAI), through Mingli Yuan account proxy; no independent human or second-agent review')
        with (account.root/'result.json').open('x') as stream:
            json.dump(report,stream,indent=2)
            stream.write('\n')
        print(json.dumps({k:report[k] for k in ('stage','status','assertions','counted_work','checkpoint_advanced')}))
    return 0 if report['status'] == 'ScopedInterpretationChecked' else 1


if __name__ == '__main__':
    raise SystemExit(main())
