"""Exact finite matrix presentation; Codex (OpenAI), Unknown v0.3.

Coordinates are external research coordinates, never native semantic IDs.
"""
from fractions import Fraction as Q

ACCOUNT = None


def charge(n=1):
    if ACCOUNT is not None:
        ACCOUNT.tick(n)


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def zero(n):
    return [[Q(0) for _ in range(n)] for _ in range(n)]


def transpose(a):
    return list(map(list, zip(*a)))


def scale(a, q):
    charge(len(a) ** 2)
    return [[q * x for x in row] for row in a]


def add(a, b):
    charge(len(a) ** 2)
    return [[x + y for x, y in zip(r, s)] for r, s in zip(a, b)]


def mul(a, b):
    n = len(a)
    c = zero(n)
    for i, row in enumerate(a):
        for k, x in enumerate(row):
            if x:
                charge(n)
                for j, y in enumerate(b[k]):
                    c[i][j] += x * y
    return c


def encode(a):
    return [[str(x) for x in row] for row in a]


def decode(a, n):
    if (not isinstance(a, list) or len(a) != n
            or any(not isinstance(r, list) or len(r) != n for r in a)):
        raise ValueError('matrix dimension')
    if any(not isinstance(x, str) or len(x) > 160 for r in a for x in r):
        raise ValueError('bounded rational strings required')
    result = [[Q(x) for x in r] for r in a]
    if encode(result) != a:
        raise ValueError('noncanonical rational matrix')
    return result


def conjugate(t, a, inverse):
    return mul(mul(t, a), inverse)


def base(family):
    """One declared observation: undirected cut Laplacian / (2 max degree)."""
    cuts = sorted(c['mask'] for c in family['cuts'])
    n = len(cuts)
    index = {mask: i for i, mask in enumerate(cuts)}
    lap = zero(n)
    for left, right, _ in family['edges']:
        a, b = index[left], index[right]
        lap[a][a] += 1
        lap[b][b] += 1
        lap[a][b] -= 1
        lap[b][a] -= 1
    h = scale(lap, Q(1, max(1, 2 * max(lap[i][i] for i in range(n)))))
    lifted, j = zero(2*n), zero(2*n)
    for a in range(n):
        j[a][a+n], j[a+n][a] = Q(-1), Q(1)
        for b in range(n):
            lifted[a][b] = lifted[a+n][b+n] = h[a][b]
    return cuts, lifted, j


def chart(n, name):
    t, inverse = eye(n), eye(n)
    if name == 'scaled':
        for k in range(n):
            t[k][k], inverse[k][k] = Q(k+1), Q(1, k+1)
    elif name == 'mixed':
        # Mix one real coordinate with its imaginary companion, not just cuts.
        t[0][n//2], inverse[0][n//2] = Q(1), Q(-1)
    elif name != 'identity':
        raise ValueError('unknown declared chart')
    return t, inverse


def coefficients(a, order):
    result = [eye(len(a))]
    for k in range(1, order+1):
        result.append(scale(mul(a, result[-1]), Q(1, k)))
    return result
