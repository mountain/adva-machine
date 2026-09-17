"""Check a frame carrying iota, complex structure and exponential readings.

Codex (OpenAI), original contribution under Unknown v0.3. Finite external
judgments only. Historical native probes are referenced, not reexecuted here.
"""
import argparse
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import resource
import signal
import sys
import time
import traceback

import algebra as m

FILES = ('contract.json', 'frame.md', 'frames.json', 'processes.json',
         'algebra.py', 'check.py', 'dependencies.json', 'structure.json')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def pin(root):
    return sha(json.dumps([[n, sha((root/n).read_bytes())] for n in FILES],
                          separators=(',', ':')).encode())


class Budget:
    def __init__(self, limits):
        self.start = time.monotonic()
        self.work = self.assertions = 0
        self.limits = limits

    def tick(self, n=1):
        self.work += n
        if self.work > self.limits['counted_work_per_check']:
            raise TimeoutError('counted work exhausted')
        if time.monotonic()-self.start > self.limits['wall_seconds_per_check']:
            raise TimeoutError('wall time exhausted')

    def require(self, condition, reason):
        self.tick()
        self.assertions += 1
        if not condition:
            raise ValueError(reason)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate(frame, family, budget):
    need = budget.require
    cuts, h, j = m.base(family)
    n = len(h)
    need(n <= budget.limits['matrix_dimension'], 'matrix capacity')
    need(frame['process_sha256'] == sha(canonical(family)), 'process binding')
    need(frame['cut_basis'] == cuts, 'cut basis changed')
    need(frame['entry_roles'] == family['entry_roles']
         and frame['exit_roles'] == family['exit_roles'], 'boundary policy changed')
    need(frame['source_combinators'] == ['iota'], 'source generator changed')
    need(frame['exponential'] == {'coefficient_rule':'A^k/k!', 'order':12,
                                 'parameter_bound':'1', 'tail_bound':'3/13!'},
         'exponential rule changed')
    need(sum(h[k][k] for k in range(n//2)) == -Q(family['partition_linear']),
         'bound process trace differs')
    need(frame['operator_parameter'] == 'dimensionless; distinct from event clock',
         'operator parameter identified with event clock')
    need(frame['history_sha256'] == sha(canonical(family['events'])), 'history binding')
    need(frame['residual'] == ['directed events', 'copy/discard history',
                              'domain policies', 'full ancestry remains external'],
         'process residual erased')
    t, inverse = (m.decode(frame[key], n) for key in ('T', 'inverse'))
    need(m.mul(t, inverse) == m.eye(n) and m.mul(inverse, t) == m.eye(n),
         'chart not invertible')
    h1, j1, g1, o1 = (m.decode(frame[key], n) for key in ('H', 'J', 'G', 'O'))
    need(h1 == m.conjugate(t, h, inverse), 'H correspondence')
    need(j1 == m.conjugate(t, j, inverse), 'J correspondence')
    need(g1 == m.mul(m.transpose(inverse), inverse), 'metric not transported')
    need(o1 == inverse, 'observer not transported')
    need(m.mul(j1, j1) == m.scale(m.eye(n), -1), 'J squared is not minus I')
    need(m.mul(m.mul(m.transpose(j1), g1), j1) == g1, 'complex metric compatibility')
    need(m.mul(m.transpose(h1), g1) == m.mul(g1, h1), 'H metric adjoint')
    need(m.mul(j1, h1) == m.mul(h1, j1), 'H not complex linear')
    a = m.scale(m.mul(j1, h1), -1)
    need(m.add(m.mul(m.transpose(a), g1), m.mul(g1, a)) == m.zero(n),
         'real time generator not metric skew')
    clock = frame['clock']
    alpha, beta = Q(clock['scale']), Q(clock['offset'])
    need(alpha > 0, 'clock calibration reverses orientation')
    ts = list(map(Q, family['clocks']['layers']))
    transported = list(map(Q, clock['times']))
    need(transported == [alpha*x+beta for x in ts], 'clock correspondence')
    for u in range(len(ts)):
        for v in range(len(ts)):
            need((ts[u] == ts[v]) == (transported[u] == transported[v]),
                 'simultaneity groups changed')
    ledger = frame['resource']
    need(ledger['account'] == 'iota-frame-v1-shared-model-account'
         and ledger['grant'] == 3 and ledger['spent'] == frame['chart_index']
         and ledger['remaining'] == 3-ledger['spent'], 'fuel account reset')
    return h, j, t, inverse, h1, j1, g1, o1


def admission(process_checked, frame_checked, coefficient_checked):
    if None in (process_checked, frame_checked, coefficient_checked):
        return {'status':'Unknown', 'advance':False}
    passed = all((process_checked, frame_checked, coefficient_checked))
    return {'status':'FrameCovarianceChecked' if passed else 'Counterexample',
            'advance':passed}


def series_checks(frame, family, budget, order):
    need = budget.require
    h, j, t, inverse, h1, j1, g1, o1 = validate(frame, family, budget)
    n = len(h)
    a = m.scale(m.mul(j1, h1), -1)
    u = m.coefficients(a, order)
    heat = m.coefficients(m.scale(h1, -1), order)
    source_u = m.coefficients(m.scale(m.mul(j, h), -1), order)
    source_heat = m.coefficients(m.scale(h, -1), order)
    h_powers = m.coefficients(h, order)
    minus_j_power = m.eye(n)
    j_power = m.eye(n)
    for k in range(order+1):
        # An independent coefficient reading: Gaussian phases times H^k/k!.
        need(source_u[k] == m.mul(j_power, h_powers[k]), 'Gaussian phase coefficient')
        need(u[k] == m.conjugate(t, source_u[k], inverse), 'exp covariance')
        need(heat[k] == m.conjugate(t, source_heat[k], inverse), 'heat covariance')
        need(m.mul(o1, m.mul(u[k], t)) == source_u[k], 'observed exp changed')
        need(m.mul(o1, m.mul(heat[k], t)) == source_heat[k], 'observed heat changed')
        need(m.mul(minus_j_power, u[k]) == heat[k], 'Wick coefficient sign')
        norm_coefficient = m.zero(n)
        for r in range(k+1):
            norm_coefficient = m.add(norm_coefficient,
                m.mul(m.mul(m.transpose(u[r]), g1), u[k-r]))
            need(m.mul(heat[r], heat[k-r]) == m.scale(heat[k], math.comb(k, r)),
                 'two parameter heat semigroup coefficient')
        need(norm_coefficient == (g1 if k == 0 else m.zero(n)),
             'metric unitarity coefficient')
        minus_j_power = m.mul(minus_j_power, m.scale(j1, -1))
        j_power = m.mul(j_power, m.scale(j, -1))
    # The similarity transports the norm through G, not the Euclidean metric.
    need(max(sum(abs(x) for x in row) for row in h) <= 1, 'source norm bound')
    vector = [[Q(0) for _ in range(n)] for _ in range(n)]
    vector[0][0] = vector[n//2][0] = Q(1)
    encoded = m.mul(t, vector)
    need(m.mul(o1, encoded) == vector, 'coordinate observation')
    need(m.mul(m.mul(m.transpose(encoded), g1), encoded)
         == m.mul(m.transpose(vector), vector), 'coordinate norm')
    return {'frame':frame['id'], 'dimension':n, 'order':order,
            'U_coefficients':[m.encode(x) for x in u],
            'heat_coefficients':[m.encode(x) for x in heat],
            'tail_bound_in_transported_metric':str(Q(3, math.factorial(order+1))),
            'tail_parameter_domain':'absolute value <= 1',
            'actual_series_values_evaluated':False}


def controls(frames, families, budget):
    rows = []
    original = next(f for f in frames if f['id'] == 'independent-iota/scaled')
    family = families['independent-iota']
    def rejected(name, mutate):
        changed = deepcopy(original)
        mutate(changed)
        try:
            validate(changed, family, budget)
        except ValueError as error:
            rows.append({'name':name, 'status':'Counterexample', 'reason':str(error)})
        else:
            raise AssertionError('accepted altered frame: '+name)
    n = len(original['J'])
    rejected('untransported-metric', lambda f:f.update(G=m.encode(m.eye(n))))
    rejected('untransported-observer', lambda f:f.update(O=m.encode(m.eye(n))))
    rejected('imaginary-unit-is-identity', lambda f:f.update(J=m.encode(m.eye(n))))
    rejected('wrong-operator', lambda f:f.update(H=m.encode(m.zero(n))))
    rejected('missing-cut', lambda f:f['cut_basis'].pop())
    rejected('changed-domain-policy', lambda f:f.update(exit_roles=list(reversed(f['exit_roles']))))
    rejected('erased-history', lambda f:f.update(history_sha256='0'*64))
    rejected('new-source-primitive-e', lambda f:f.update(source_combinators=['iota','e']))
    rejected('wrong-exponential-coefficients', lambda f:f['exponential'].update(coefficient_rule='A^k'))
    rejected('clock-is-operator-parameter', lambda f:f.update(operator_parameter='event clock'))
    rejected('clock-group-split', lambda f:f['clock']['times'].__setitem__(1, '99'))
    rejected('frame-change-refills-fuel', lambda f:f['resource'].update(spent=0, remaining=3))
    rejected('singular-chart', lambda f:f.update(T=m.encode(m.zero(n))))
    h, j, *_ = validate(original, family, budget)
    a = m.scale(m.mul(j, h), -1)
    wrong = m.mul(j, a)  # t=+i tau has +H as its linear coefficient.
    budget.require(wrong != m.scale(h, -1), 'wrong Wick control failed')
    rows.append({'name':'wrong-Wick-sign', 'status':'Counterexample',
                 'first_coefficient_residual':m.encode(m.add(wrong, h))})
    h2 = m.base(families['changed-roles'])[1]
    budget.require(h == h2 and family['exit_roles'] != families['changed-roles']['exit_roles'],
                   'role residual control failed')
    rows.append({'name':'operator-forgets-role-policy', 'status':'ResidualRequired',
                 'same_operator':True, 'different_frame':True})
    chain = m.base(families['nested-iota'])[1]
    budget.require(len(chain) == len(h) and chain != h, 'equal dimension erases process')
    rows.append({'name':'equal-dimension-different-process', 'status':'Counterexample'})
    # A frame without required evidence cannot authorize a checkpoint.
    missing = admission(None, True, True)
    budget.require(missing == {'status':'Unknown', 'advance':False}, 'missing evidence advanced')
    rows.append({'name':'missing-process-evidence', **missing})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--materials', type=Path, required=True)
    parser.add_argument('--iota-materials', type=Path, required=True)
    parser.add_argument('--expect-package', required=True)
    parser.add_argument('--stage', choices=['source-preflight', 'knowledge-after-reception',
                                           'machine-after-reception'], required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    start, cpu = time.monotonic(), time.process_time()
    contract = json.loads((args.materials/'contract.json').read_text())
    limits = contract['limits']
    resource.setrlimit(resource.RLIMIT_CPU, (limits['cpu_seconds_per_check'],)*2)
    resource.setrlimit(resource.RLIMIT_AS, (limits['address_space_bytes'],)*2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (limits['artifact_bytes'],)*2)
    def stop(*_):
        raise TimeoutError('wall alarm')
    signal.signal(signal.SIGALRM, stop)
    signal.alarm(limits['wall_seconds_per_check'])
    budget = Budget(limits)
    m.ACCOUNT = budget
    result = {'schema':'adva.iota-frame-result.v1', 'stage':args.stage,
              'contract_sha256':sha((args.materials/'contract.json').read_bytes()),
              'package_sha256':args.expect_package, 'native_admission':'NotGranted',
              'new_native_object_executions':0, 'checkpoint_advance':False}
    try:
        need = budget.require
        need(Path(__file__).resolve() == (args.materials/'check.py').resolve(), 'checker path')
        need(Path(m.__file__).resolve() == (args.materials/'algebra.py').resolve(), 'algebra path')
        need(all((args.materials/n).stat().st_size <= 65536 for n in FILES), 'material size')
        need(pin(args.materials) == args.expect_package, 'package pin')
        dependencies = json.loads((args.materials/'dependencies.json').read_text())
        for name, digest in dependencies['previous_materials'].items():
            need(sha((args.iota_materials/name).read_bytes()) == digest, 'previous dependency '+name)
        old = load_module(args.iota_materials/'check.py', 'bound_iota_checker')
        need(old.package_pin(args.iota_materials) == dependencies['previous_package_sha256'],
             'previous package binding')
        old_families = json.loads((args.iota_materials/'interpretations.json').read_text())['families']
        summaries = [old.check_family(f, budget) for f in old_families]
        selected = json.loads((args.materials/'processes.json').read_text())
        families = {f['name']:f for f in selected}
        need(list(families) == contract['families'], 'family coverage')
        for family in selected:
            need(family == next(f for f in old_families if f['name'] == family['name']),
                 'source projection differs')
        frames = json.loads((args.materials/'frames.json').read_text())
        need([f['id'] for f in frames] == [name+'/'+chart for name in contract['families']
                for chart in contract['charts']], 'frame coverage')
        witnesses = [series_checks(f, families[f['family']], budget, contract['series_order'])
                     for f in frames]
        negatives = controls(frames, families, budget)
        body = {'frames':frames, 'witnesses':witnesses, 'controls':negatives,
                'process_checks':summaries}
        raw = (json.dumps(body, separators=(',', ':'))+'\n').encode()
        need(len(raw) < limits['artifact_bytes']-65536, 'artifact reserve')
        (args.output/'witness.json').write_bytes(raw)
        need(json.loads((args.output/'witness.json').read_bytes()) == body, 'checkpoint replay')
        accepted = admission(True, True, True)
        need(accepted['advance'], 'join did not advance')
        result.update(status=accepted['status'], checkpoint_advance=accepted['advance'],
                      witness_sha256=sha(raw), frame_count=len(frames),
                      process_families=len(summaries), controls=len(negatives),
                      series_order=contract['series_order'])
    except (FileNotFoundError, TimeoutError) as error:
        result.update(status='Unknown', reason=str(error))
    except Exception as error:
        result.update(status='Failed', reason=str(error), traceback=traceback.format_exc())
    result.update(assertions=budget.assertions, counted_work=budget.work,
                  wall_seconds=time.monotonic()-start, cpu_seconds=time.process_time()-cpu,
                  peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    (args.output/'result.json').write_text(json.dumps(result, indent=2)+'\n')
    signal.alarm(0)
    print(json.dumps(result))
    return 0 if result['status'] == 'FrameCovarianceChecked' else 1


if __name__ == '__main__':
    sys.exit(main())
