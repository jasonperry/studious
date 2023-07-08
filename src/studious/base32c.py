# my own implementation of Crockford base32


def cb32encode(bs: bytes):
    """Encode byte string in (lowercase) Crockford's base32."""
    b32chars = "0123456789abcdefghjkmnpqrstvwxyz"
    if len(bs) % 5 != 0:
        raise ValueError("Can only encode multiples of 5 bytes currently")
    res = ""
    for i in range(0, len(bs), 5):
        # b0, b1, b2, b3, b4 = [ord(b) for b in bs[i:i+5]]
        b0, b1, b2, b3, b4 = bs[i:i+5]
        # parentheses are needed, the shift takes higher precedence!
        # or I could shift first...I seem to prefer &-then-shift, however.
        c0 = b32chars[b0 >> 3]
        c1 = b32chars[(b0 & 7) << 2 | b1 >> 6]
        c2 = b32chars[(b1 & 62) >> 1]
        c3 = b32chars[(b1 & 1) << 4 | b2 >> 4]
        c4 = b32chars[(b2 & 15) << 1 | (b3 & 128) >> 7]
        c5 = b32chars[(b3 & 124) >> 2]
        c6 = b32chars[(b3 & 3) << 3 | (b4 & 224) >> 5]
        c7 = b32chars[b4 & 31]
        res += c0 + c1 + c2 + c3 + c4 + c5 + c6 + c7
    return res

# 'hellothere' -> D1JPRV3FEHM6AWK5

