"""Exact exterior algebra over a declared direction set.

DeepSeek Harness (deepseek-v4-flash-vision-exp), original contribution under
Unknown v0.3, submitted through Mingli Yuan's authorized account proxy.

Coordinates are external research coordinates, never native semantic IDs. All
arithmetic is exact integer arithmetic; no floating point value is computed,
compared or retained anywhere in this module.

An operator is a square integer matrix acting on the exterior basis blades of a
declared direction set. Blade `b` has direction `i` present exactly when bit `i`
of `b` is set, so the carrier has `2**n` blades for `n` directions.
"""

ACCOUNT = None


def charge(n=1):
    """Debit the shared finite account, when one is installed."""
    if ACCOUNT is not None:
        ACCOUNT.tick(n)


def size(n):
    return 1 << n


def zero_op(n):
    s = size(n)
    return [[0] * s for _ in range(s)]


def identity_op(n):
    s = size(n)
    return [[1 if i == j else 0 for j in range(s)] for i in range(s)]


def parity(mask):
    return -1 if bin(mask).count('1') % 2 else 1


def wedge(n, direction):
    """Exterior multiplication by one direction. Construction-facing; raises grade."""
    out = zero_op(n)
    bit = 1 << direction
    for blade in range(size(n)):
        if blade & bit:
            continue
        out[blade | bit][blade] = parity(blade & (bit - 1))
    return out


def contract(n, direction):
    """Contraction by the cut cochain dual to one direction. Boundary-facing."""
    out = zero_op(n)
    bit = 1 << direction
    for blade in range(size(n)):
        if not blade & bit:
            continue
        out[blade ^ bit][blade] = parity(blade & (bit - 1))
    return out


def compose(a, b):
    n = len(a)
    out = [[0] * n for _ in range(n)]
    for i in range(n):
        for k in range(n):
            x = a[i][k]
            if x:
                charge(n)
                for j in range(n):
                    out[i][j] += x * b[k][j]
    return out


def add(a, b):
    charge(len(a) ** 2)
    return [[x + y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def subtract(a, b):
    charge(len(a) ** 2)
    return [[x - y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def scale(a, k):
    charge(len(a) ** 2)
    return [[k * x for x in row] for row in a]


def contract_by(n, cochain):
    """Contract by a declared cochain `c = sum_t cochain[t] * dx_t`.

    The cut's own cochain is the identity matrix. Every other declared cochain
    is a control: it must break a downstream law, which is what makes the cut's
    role testable rather than decorative.
    """
    out = zero_op(n)
    for t, coefficient in enumerate(cochain):
        if coefficient:
            out = add(out, scale(contract(n, t), coefficient))
    return out


def restrict(op, basis):
    """Restrict an operator to a declared blade basis.

    Returns None when the operator does not preserve that basis. `None` is a
    result, not an error: it records that the declared carrier is the wrong one.
    """
    index = {blade: position for position, blade in enumerate(basis)}
    k = len(basis)
    out = [[0] * k for _ in range(k)]
    for column, blade in enumerate(basis):
        for row in range(len(op)):
            value = op[row][blade]
            if not value:
                continue
            if row not in index:
                return None
            out[index[row]][column] = value
    return out


def restrict_signed(op, signed_basis):
    """Restrict an operator to a SIGNED blade basis `v_j = sign_j * e_blade_j`.

    With `w = sum_j a_j v_j`, the new matrix is
    `M'_ij = (sign_j / sign_i) * op[blade_i][blade_j]`.

    The sign convention is a declared presentation. It changes the recorded
    coefficient VALUES of an action; it does not change whether those values
    agree across directions, which is the property this profile claims.
    """
    blades = [entry[0] for entry in signed_basis]
    signs = [entry[1] for entry in signed_basis]
    index = {blade: position for position, blade in enumerate(blades)}
    k = len(blades)
    out = [[0] * k for _ in range(k)]
    for column, blade_j in enumerate(blades):
        for row in range(len(op)):
            value = op[row][blade_j]
            if not value:
                continue
            if row not in index:
                return None
            i = index[row]
            out[i][column] = signs[column] * value // signs[i]
    return out


def matrix_units(n, cochain, basis, reversed_order=False):
    """`E_ij = eps_i` composed with contraction by `cochain[j]`, restricted.

    `reversed_order=True` builds `iota_j eps_i` instead. That is the declared
    control for the composition order, and it must fail the law.
    """
    out = []
    for i in range(n):
        row = []
        for j in range(n):
            contraction = contract_by(n, cochain[j])
            op = (compose(contraction, wedge(n, i)) if reversed_order
                  else compose(wedge(n, i), contraction))
            row.append(restrict(op, basis))
        out.append(row)
    return out


def matmul(a, b):
    k = len(a)
    charge(k ** 3)
    return [[sum(a[i][t] * b[t][j] for t in range(k)) for j in range(k)]
            for i in range(k)]


def matadd(a, b):
    return [[x + y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def matsub(a, b):
    return [[x - y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def zero_mat(k):
    return [[0] * k for _ in range(k)]


def identity_mat(k):
    return [[1 if i == j else 0 for j in range(k)] for i in range(k)]


def law_score(family, n):
    """The matrix-unit law over every index quadruple.

    Returns (hold, total, first_counterexample). Quadruples whose cells do not
    exist on the declared carrier are skipped and are not counted as holds.
    """
    hold = total = 0
    first = None
    for i in range(n):
        for j in range(n):
            for k in range(n):
                for l in range(n):
                    if family[i][j] is None or family[k][l] is None:
                        continue
                    total += 1
                    target = family[i][l] if j == k else zero_mat(len(family[i][j]))
                    if target is not None and matmul(family[i][j], family[k][l]) == target:
                        hold += 1
                    elif first is None:
                        first = '(i,j,k,l)=(%d,%d,%d,%d)' % (i, j, k, l)
    return hold, total, first


def realize(table, family, n):
    """A table becomes `sum_ij table[i][j] E_ij` on the declared carrier."""
    k = len(family[0][0])
    out = zero_mat(k)
    for i in range(n):
        for j in range(n):
            if not table[i][j]:
                continue
            charge(k ** 2)
            for r in range(k):
                for c in range(k):
                    out[r][c] += table[i][j] * family[i][j][r][c]
    return out


def family_is_zero(family):
    """True when every existing cell is the zero operator.

    This is the non-vacuity guard. The matrix-unit law alone is satisfied by an
    identically zero family, so a law that passes without this guard certifies
    nothing.
    """
    for row in family:
        for cell in row:
            if cell is None:
                continue
            if any(x for r in cell for x in r):
                return False
    return True


def is_zero_matrix(a):
    return all(x == 0 for row in a for x in row)


def incidence_pairing(structure):
    """Derive `dx_i(g_j)` from the declared causal cube.

    `x_i(mask)` is the cut-membership coordinate: one exactly when direction `i`
    has crossed the cut into the completed past. `g_j` is the forward generation
    edge that carries direction `j` across the cut. The pairing is therefore
    COMPUTED here from the declared enabled edges, never stipulated, which is
    what keeps the cut's role a measured fact rather than an input.
    """
    n = len(structure['directions'])
    enabled = {(e['mask'], e['direction']) for e in structure['cube']['enabled']}
    pairing = []
    witnesses = 0
    for i in range(n):
        row = []
        for j in range(n):
            differences = set()
            for mask in structure['cube']['vertices']:
                if (mask, j) not in enabled:
                    continue
                after = mask | (1 << j)
                difference = ((after >> i) & 1) - ((mask >> i) & 1)
                differences.add(difference)
                witnesses += 1
            if len(differences) != 1:
                raise ValueError('incidence pairing is not single-valued')
            row.append(differences.pop())
        pairing.append(row)
    charge(witnesses)
    return pairing, witnesses


def degree(blade):
    return bin(blade).count('1')
