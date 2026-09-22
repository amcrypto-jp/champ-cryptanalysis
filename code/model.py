"""Independent, small CHAMP model (Python standard library).

Matrices use row-major tuples. Digests use the C/KAT little-endian convention.
This is research code, not an implementation intended for production use.
"""

A = (-2, 1, 4, -3)
B = (-5, 2, -6, 2)
ALT = (6, 4, -2, -1)
I = (1, 0, 0, 1)
PRIMES = {512: (1 << 128) - 15449, 1024: (1 << 256) - 36113}


def mul(x, y, p=None):
    a, b, c, d = x
    e, f, g, h = y
    z = (a * e + b * g, a * f + b * h,
         c * e + d * g, c * f + d * h)
    return z if p is None else tuple(v % p for v in z)


def det(x, p):
    a, b, c, d = x
    return (a * d - b * c) % p


def inv(x, p):
    a, b, c, d = x
    r = pow(det(x, p), -1, p)
    return tuple(v * r % p for v in (d, -b, -c, a))


def power(x, n, p):
    out = I
    while n:
        if n & 1:
            out = mul(out, x, p)
        x = mul(x, x, p)
        n >>= 1
    return out


def product(bits, p=None, generators=(A, B)):
    out = I
    for bit in bits:
        out = mul(out, generators[int(bit)], p)
    return out


def encode(x, p, byteorder="little"):
    size = (p.bit_length() + 7) // 8
    return b"".join((pow(v, -1, p) if v else 0).to_bytes(size, byteorder)
                    for v in (x[0], x[2], x[1], x[3]))


def decode(digest, p, byteorder="little"):
    size = (p.bit_length() + 7) // 8
    if len(digest) != 4 * size:
        raise ValueError("Wrong digest length")
    v = [int.from_bytes(digest[j:j + size], byteorder)
         for j in range(0, len(digest), size)]
    if any(x >= p for x in v):
        raise ValueError("Noncanonical field encoding")
    w = [pow(x, -1, p) if x else 0 for x in v]
    return (w[0], w[2], w[1], w[3])


def pack(bits):
    return int(bits.ljust((len(bits) + 7) // 8 * 8, "0") or "0", 2).to_bytes(
        (len(bits) + 7) // 8, "big")


def unpack(data, n):
    return "".join(f"{byte:08b}" for byte in data)[:n]


def hash_bits(bits, p):
    return encode(product(bits, p), p)


def enumerate_products(n, generators, p, initial=I):
    """Yield all n-symbol products; reuse prefixes, without storing a tree."""
    stack = [(0, initial, 0)]
    while stack:
        depth, state, word = stack.pop()
        if depth == n:
            yield word, state
        else:
            for bit in (1, 0):
                stack.append((depth + 1, mul(state, generators[bit], p),
                              2 * word + bit))


def mitm(target, n, p):
    """Find an n-bit preimage, including when integer entries wrap modulo p.

    Time and storage are exponential in n/2. This does NOT promise a distinct
    second preimage. The suffix is enumerated backwards using inverse factors.
    """
    left, right = n // 2, n - n // 2
    table = {matrix: word for word, matrix in enumerate_products(left, (A, B), p)}
    inverses = (inv(A, p), inv(B, p))
    for reversed_word, needed in enumerate_products(right, inverses, p, target):
        if needed in table:
            return f"{table[needed]:0{left}b}" + f"{reversed_word:0{right}b}"[::-1]
    return None
