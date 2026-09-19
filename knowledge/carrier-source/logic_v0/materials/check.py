"""Check the carrier matrix profile (version 0).

DeepSeek Harness (deepseek-v4-flash-vision-exp), original contribution under
Unknown v0.3, submitted through Mingli Yuan's authorized account proxy.

Finite external judgments only. No native object is launched, no native
semantic identity is allocated, and no Rust, library, epoch or Seal is touched.
Every number this checker reports is recomputed here from the declared
structure; none is read back from a stored expectation.

Two guards are load-bearing:

  * the NON-VACUITY guard, because the matrix-unit law is satisfied by an
    identically zero family and a law that passes without the guard certifies
    nothing;
  * the CONTROL-BITE guard, because a control whose measured quantity does not
    differ from the clean case is inconclusive, and an inconclusive control is
    reported as Unknown rather than counted as a pass.
"""
import argparse
from pathlib import Path
import hashlib
import json
import resource
import signal
import sys
import time
import traceback

import algebra as m

FILES = ('contract.json', 'carrier.md', 'structure.json', 'tables.json',
         'algebra.py', 'check.py', 'dependencies.json')

CLEAN_COCHAIN = 'identity (the cut)'
CORRUPTED_COCHAIN = ('off-diagonal swap', 'doubled diagonal', 'sign flip on one axis')
ZERO_COCHAIN = 'zero'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pin(root):
    return sha(json.dumps([[n, sha((root / n).read_bytes())] for n in FILES],
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
        if time.monotonic() - self.start > self.limits['wall_seconds_per_check']:
            raise TimeoutError('wall time exhausted')

    def require(self, condition, reason):
        self.tick()
        self.assertions += 1
        if not condition:
            raise ValueError(reason)


# ------------------------------------------------------------------ stages --

def derive(structure, budget):
    """Derive the cut pairing and the carriers from the declared cube."""
    need = budget.require
    directions = structure['directions']
    n = len(directions)
    need(n == budget.limits['directions'], 'direction count')
    need([d['index'] for d in directions] == list(range(n)), 'direction indices')
    need(len({d['operation'] for d in directions}) == n, 'direction operations distinct')
    pairing, witnesses = m.incidence_pairing(structure)
    need(witnesses > 0, 'no enabled generation edge')
    expected = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    need(pairing == expected, 'incidence pairing is not the identity pairing')
    # The DECLARED clean cochain must be the DERIVED pairing. Without this
    # binding a corrupted declaration would pass silently, because the main
    # path computes the pairing rather than reading the declaration.
    declared_name = structure['declared_cut_cochain']
    need(structure['cochains'][declared_name] == pairing,
         'the declared cut cochain is not the derived pairing')
    need(declared_name == CLEAN_COCHAIN, 'the declared cut cochain changed name')
    signed = structure['carrier']['signed_basis']
    basis = [entry[0] for entry in signed]
    need(all(entry[1] == 1 for entry in signed), 'grade-1 basis must be unsigned')
    need(len(basis) == n, 'grade-1 carrier dimension')
    need(len(structure['extended_carrier']['signed_basis'])
         == budget.limits['extended_carrier_dimension'], 'extended carrier dimension')
    need(m.size(n) == budget.limits['exterior_dimension'], 'exterior dimension')
    return n, pairing, basis, structure['extended_carrier']['signed_basis'], witnesses


def anchor(n, budget):
    """eps_i iota_j + iota_j eps_i = delta_ij I, the cut duality everything rests on."""
    need = budget.require
    identity = m.identity_op(n)
    zero = m.zero_op(n)
    checked = 0
    for i in range(n):
        for j in range(n):
            anti = m.add(m.compose(m.wedge(n, i), m.contract(n, j)),
                         m.compose(m.contract(n, j), m.wedge(n, i)))
            need(anti == (identity if i == j else zero),
                 'cut duality fails at (%d,%d)' % (i, j))
            checked += 1
    return checked


def matrix_units(n, cochain, basis):
    return m.matrix_units(n, cochain, basis)


def laws(n, family, basis, budget, tables):
    need = budget.require
    hold, total, first = m.law_score(family, n)
    need(total == n ** 4, 'law coverage: %d of %d' % (total, n ** 4))
    need(hold == total, 'matrix-unit law fails: %d/%d first %s' % (hold, total, first))
    need(not m.family_is_zero(family), 'family is identically zero: law passed vacuously')

    # sum_i E_ii = I
    k = len(basis)
    accumulator = m.zero_mat(k)
    for i in range(n):
        accumulator = m.matadd(accumulator, family[i][i])
    need(accumulator == m.identity_mat(k), 'sum_i E_ii is not the identity')

    # associativity over every index triple, and distributivity
    associative = distributive = triples = 0
    for i in range(n):
        for j in range(n):
            for kk in range(n):
                for ll in range(n):
                    for mm in range(n):
                        for nn in range(n):
                            triples += 1
                            if m.matmul(m.matmul(family[i][j], family[kk][ll]), family[mm][nn]) \
                               != m.matmul(family[i][j], m.matmul(family[kk][ll], family[mm][nn])):
                                raise ValueError('associativity fails at %s'
                                                 % ((i, j, kk, ll, mm, nn),))
                    left = m.matmul(family[i][j], m.matadd(family[kk][ll], family[kk][ll]))
                    right = m.matadd(m.matmul(family[i][j], family[kk][ll]),
                                     m.matmul(family[i][j], family[kk][ll]))
                    need(left == right, 'distributivity fails')
                    distributive += 1
    need(triples == n ** 6, 'associativity coverage')
    return {'law': '%d/%d' % (hold, total), 'triples': triples,
            'distributive': distributive}


def product(n, family, basis, tables, budget):
    need = budget.require
    T = tables['tables']
    A, B, identity, zero = T['A'], T['B'], T['identity'], T['zero']
    realize = lambda t: m.realize(t, family, n)
    need(realize(identity) == m.identity_mat(len(basis)), 'identity table is not the identity operator')
    need(m.is_zero_matrix(realize(zero)), 'zero table is not the zero operator')
    need(realize(A) == A, 'the table is not its own realized operator')
    need(realize(B) == B, 'the table is not its own realized operator')
    composed = m.matmul(realize(A), realize(B))
    ordinary = m.matmul(A, B)
    need(composed == ordinary, 'composition differs from the matrix product')
    need(composed == tables['expected_product_AB'],
         'the product does not equal the recorded expectation')
    # the middle index really is summed: dropping one term must change the result
    partial = m.matmul(A, [[B[r][c] if r != 0 else 0 for c in range(n)] for r in range(n)])
    need(partial != ordinary, 'the middle index summation is not observable')
    return composed


def summation(n, budget):
    need = budget.require
    s, size = m.zero_op(n), m.size(n)
    for i in range(n):
        s = m.add(s, m.compose(m.wedge(n, i), m.contract(n, i)))
    reverse = m.zero_op(n)
    for i in range(n):
        reverse = m.add(reverse, m.compose(m.contract(n, i), m.wedge(n, i)))
    for blade in range(size):
        for row in range(size):
            deg = m.degree(blade) if row == blade else 0
            need(s[row][blade] == deg, 'sum eps iota is not the degree operator')
            need(reverse[row][blade] == (n - deg if row == blade else 0),
                 'sum iota eps is not n minus the degree')
    need(m.add(s, reverse) == m.scale(m.identity_op(n), n), 'the two sums do not total n I')
    return size


def volume(n, basis_w, budget):
    """Omega = c_1 c_2 c_3 on W, with Omega^2 = -I."""
    need = budget.require
    c = [m.add(m.wedge(n, i), m.contract(n, i)) for i in range(n)]
    op = m.identity_op(n)
    for i in range(n):
        op = m.compose(c[i], op)
    restricted = m.restrict_signed(op, basis_w)
    need(restricted is not None, 'the volume action does not preserve W')
    k = len(basis_w)
    square = m.matmul(restricted, restricted)
    need(square == m.scale(m.identity_mat(k), -1), 'Omega^2 is not -I on W')
    return restricted


def sparse_action(restricted, basis_w):
    """(coefficient, target) for each slot of the volume action, or None."""
    out = []
    for column in range(len(basis_w)):
        entries = [(row, restricted[row][column]) for row in range(len(basis_w))
                   if restricted[row][column]]
        out.append(entries[0] if len(entries) == 1 else None)
    return out


def carrier_symmetry(action, n, budget):
    """The carrier does not distinguish the three directions; every causal line splits alike."""
    need = budget.require
    need(all(entry is not None for entry in action), 'volume action is not sparse on W')
    coefficients = {action[i][1] for i in range(n)}
    need(len(coefficients) == 1, 'carrier coefficients differ across directions')
    shapes = {}
    for causal in range(n):
        transverse = tuple(d for d in range(n) if d != causal)
        orientation = (action[causal][0],)
        relations = tuple(action[d][0] for d in transverse)
        one_two_two_one = (1, len(transverse), len(relations), len(orientation))
        one_two_three = (1, len(transverse), len(set(relations + orientation)))
        one_three_two = (1, len(set(transverse + orientation)), len(relations))
        shapes[causal] = (one_two_two_one, one_two_three, one_three_two)
        need(one_two_two_one == (1, n - 1, n - 1, 1), 'causal-line split differs from (1,2,2,1)')
    need(len(set(shapes.values())) == 1, 'the carrier distinguishes the causal directions')
    # The INVARIANT is that one common coefficient appears across the three
    # directions. Its VALUE depends on the declared composition order and on the
    # declared signed basis, so both are recorded here rather than presented as
    # a result. No claim is made about the value.
    return {'coefficient_set': sorted(coefficients),
            'common_value': sorted(coefficients)[0] if len(coefficients) == 1 else None,
            'presentation_dependent': True,
            'composition_order': 'c_2 (c_1 (c_0 .))',
            'shapes': shapes[0]}


def controls(n, pairing, basis, basis_w, tables, budget):
    """Each control must BITE. A control that cannot fail is Unknown, not a pass."""
    need = budget.require
    T = tables['tables']
    clean = matrix_units(n, pairing, basis)
    clean_hold, clean_total, _ = m.law_score(clean, n)
    clean_product = m.matmul(m.realize(T['A'], clean, n),
                             m.realize(T['B'], clean, n))
    rows = []

    def record(name, quantity, bit, detail):
        rows.append({'control': name, 'quantity': quantity, 'bite': bit, 'detail': detail})
        need(bit, 'control %s did not bite (%s)' % (name, detail))

    # 1-3: wrong carrier or wrong composition order must lower the law score
    wrong_carriers = {
        'lambda2_carrier': [3, 5, 6],
        'all_of_lambda': list(range(m.size(n))),
    }
    for name, blades in wrong_carriers.items():
        family = m.matrix_units(n, pairing, blades)
        hold, total, first = m.law_score(family, n)
        record(name, 'law', hold < clean_hold,
               '%d/%d vs clean %d/%d first %s' % (hold, total, clean_hold, clean_total, first))

    reversed_family = m.matrix_units(n, pairing, basis, reversed_order=True)
    hold, total, first = m.law_score(reversed_family, n)
    record('reversed_composition_order', 'law', hold < clean_hold,
           '%d/%d vs clean %d/%d first %s' % (hold, total, clean_hold, clean_total, first))

    # 4: every corrupted cochain must break the PRODUCT, not merely the law
    for name in CORRUPTED_COCHAIN:
        declared = _declared_cochain(budget, name)
        family = m.matrix_units(n, declared, basis)
        product = m.matmul(m.realize(T['A'], family, n),
                           m.realize(T['B'], family, n))
        cochain_hold, cochain_total, _ = m.law_score(family, n)
        record(name, 'product', product != clean_product,
               'product %s; law %d/%d' % ('differs' if product != clean_product
                                          else 'matches', cochain_hold, cochain_total))

    # 5: the zero cochain passes the law vacuously and must be caught by the guard
    zero_declared = _declared_cochain(budget, ZERO_COCHAIN)
    zero_family = m.matrix_units(n, zero_declared, basis)
    hold, total, _ = m.law_score(zero_family, n)
    need(hold == total, 'the zero cochain was expected to satisfy the law vacuously')
    record('zero_cochain', 'non_vacuity_guard', m.family_is_zero(zero_family),
           'law %d/%d and the family is identically zero' % (hold, total))

    # 6: pure wedge is nilpotent, so interchange alone cannot give the order-four lift
    volume = m.identity_op(n)
    for i in range(n):
        volume = m.compose(m.wedge(n, i), volume)
    square = m.compose(volume, volume)
    record('pure_wedge_nilpotent', 'nilpotency', m.is_zero_matrix(square),
           'the wedge volume squares to zero')

    # 7: the law ALONE would accept a family the non-vacuity guard refuses.
    # This is the control for the guard itself: it shows the guard is load
    # bearing rather than decorative, because without it this family would have
    # been reported as a survivor.
    law_would_accept = (hold == total and hold > 0)
    guard_refuses = m.family_is_zero(zero_family)
    record('law_alone_is_insufficient', 'non_vacuity_guard',
           law_would_accept and guard_refuses,
           'law %d/%d would accept a family the guard refuses' % (hold, total))
    return rows


_DECLARED = {}


def _declared_cochain(budget, name):
    budget.tick()
    return _DECLARED[name]


# -------------------------------------------------------------------- main --

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--materials', type=Path, required=True)
    parser.add_argument('--expect-package', required=True)
    parser.add_argument('--stage', choices=['source-preflight', 'machine-after-reception'],
                        required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    start, cpu = time.monotonic(), time.process_time()

    contract = json.loads((args.materials / 'contract.json').read_text())
    limits = contract['limits']
    structure = json.loads((args.materials / 'structure.json').read_text())
    tables = json.loads((args.materials / 'tables.json').read_text())
    for name, cochain in structure['cochains'].items():
        _DECLARED[name] = cochain

    resource.setrlimit(resource.RLIMIT_CPU, (limits['cpu_seconds_per_check'],) * 2)
    if sys.platform == 'linux':
        resource.setrlimit(resource.RLIMIT_AS, (limits['address_space_bytes'],) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (limits['artifact_bytes'],) * 2)

    def stop(*_):
        raise TimeoutError('wall alarm')

    signal.signal(signal.SIGALRM, stop)
    signal.alarm(limits['wall_seconds_per_check'])
    budget = Budget(limits)
    m.ACCOUNT = budget

    result = {'schema': 'adva.carrier-matrix-result.v0', 'stage': args.stage,
              'contract_sha256': sha((args.materials / 'contract.json').read_bytes()),
              'package_sha256': args.expect_package,
              'native_admission': 'NotGranted',
              'new_native_object_executions': 0,
              'checkpoint_advance': False}
    try:
        need = budget.require
        need(Path(__file__).resolve() == (args.materials / 'check.py').resolve(), 'checker path')
        need(Path(m.__file__).resolve() == (args.materials / 'algebra.py').resolve(), 'algebra path')
        need(all((args.materials / n).stat().st_size <= 65536 for n in FILES), 'material size')
        need(pin(args.materials) == args.expect_package, 'package pin')

        n, pairing, basis, basis_w, witnesses = derive(structure, budget)
        anchors = anchor(n, budget)
        family = matrix_units(n, pairing, basis)
        law = laws(n, family, basis, budget, tables)
        composed = product(n, family, basis, tables, budget)
        size = summation(n, budget)
        restricted = volume(n, basis_w, budget)
        action = sparse_action(restricted, basis_w)
        symmetry = carrier_symmetry(action, n, budget)
        negatives = controls(n, pairing, basis, basis_w, tables, budget)

        body = {
            'declared': {'directions': contract['directions'],
                         'carrier': structure['carrier']['name'],
                         'cut_cochain': CLEAN_COCHAIN,
                         'enabled_edges': len(structure['cube']['enabled'])},
            'derived': {'pairing': pairing, 'edge_witnesses': witnesses,
                        'exterior_dimension': size},
            'laws': {'cut_duality_pairs': anchors, 'matrix_unit': law,
                     'product_AB': composed, 'volume_squares_to_minus_identity': True,
                     'carrier_symmetry': symmetry},
            'controls': negatives,
        }
        raw = (json.dumps(body, separators=(',', ':')) + '\n').encode()
        need(len(raw) < limits['artifact_bytes'] - 65536, 'artifact reserve')
        (args.output / 'witness.json').write_bytes(raw)
        # compare the DECODED form: the in-memory body may hold tuples where
        # JSON holds arrays, and the replay check is about the recorded bytes
        need(json.loads((args.output / 'witness.json').read_bytes()) == json.loads(raw),
             'checkpoint replay')
        result.update(status='CarrierMatrixChecked', checkpoint_advance=True,
                      witness_sha256=sha(raw), directions=n,
                      carrier_dimension=len(basis), controls=len(negatives),
                      assertions=budget.assertions)
    except (FileNotFoundError, TimeoutError) as error:
        result.update(status='Unknown', reason=str(error))
    except Exception as error:
        result.update(status='Failed', reason=str(error), traceback=traceback.format_exc())
    result.update(assertions=budget.assertions, counted_work=budget.work,
                  wall_seconds=time.monotonic() - start, cpu_seconds=time.process_time() - cpu,
                  peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    (args.output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    signal.alarm(0)
    print(json.dumps(result))
    return 0 if result['status'] == 'CarrierMatrixChecked' else 1


if __name__ == '__main__':
    sys.exit(main())
