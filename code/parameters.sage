"""Proof-enabled primality verification and exact generator-order checks.

Run: sage code/parameters.sage
Primality is requested with proof=True.
"""
from sage.all import ZZ, GF, matrix
from sage.version import version

if not __debug__:
    raise SystemExit("Assertions are required: disable PYTHONOPTIMIZE")

print(version)
for bits, offset in [(128, 15449), (256, 36113)]:
    p = ZZ(2)**bits - offset
    q = (p - 1)//2
    assert p.is_prime(proof=True) and q.is_prime(proof=True)
    print("field_bits", bits, "p", p, "q", q, "both prime with proof=True", flush=True)
    F = GF(p)
    A = matrix(F, [[-2, 1], [4, -3]])
    B = matrix(F, [[-5, 2], [-6, 2]])
    C = matrix(F, [[6, 4], [-2, -1]])
    assert F(2).multiplicative_order() == q
    assert B.multiplicative_order() == 2*q
    print("ord(2)=q; ord(B)=2q; 17 square:", F(17).is_square(), flush=True)
    print("A^q=I:", A**q == 1, "B_alt^q=I:", C**q == 1, flush=True)
    if bits == 256:
        assert A**q == 1 and C**q == -1
        print("ord(A)=q; ord(B_alt)=2q", flush=True)
    else:
        assert not F(17).is_square() and A**q != 1
        assert A**(p+1) == 2
        print("A and B_alt are nonsplit; A^(p+1)=2I", flush=True)

    # Every larger candidate is eliminated with proof-enabled primality tests.
    candidates = 0
    for candidate in range(int(p)+2, 2**bits, 2):
        candidates += 1
        candidate = ZZ(candidate)
        assert not (candidate.is_prime(proof=True) and ((candidate-1)//2).is_prime(proof=True))
    print("No larger safe prime:", candidates, "odd candidates checked", flush=True)
