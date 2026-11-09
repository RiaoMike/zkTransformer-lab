"""参考实现。先做 exercises.py，再用本文件对照。

教学域与固定挑战仅用于理解；没有 PCS、Fiat–Shamir 或零知识。
"""
from labs import (P, bits, classify as _classify, compile_toy, einsum_toy, eq,
                  fold, interpolate, mle, prove_sumcheck, verify_sumcheck)
from math import prod


def classify(equation):
    _, _, once, multi, summed = _classify(equation)
    return once, multi, summed


def round_message(tables):
    return [sum(prod(row) for row in zip(*(fold(t, x) for t in tables))) % P
            for x in range(len(tables) + 1)]


def range_mle(r):
    return sum((1 << j) * x for j, x in enumerate(r)) % P


def power_mle(r):
    return prod(1 + (pow(2, 1 << j, P) - 1) * x
                for j, x in enumerate(r)) % P


def decompose(q):
    if q > 0:
        raise ValueError("本课要求 q <= 0")
    c = 22713
    k = (2 * (-q) + c) // (2 * c)
    if not 0 <= k <= 15:
        raise ValueError("k 超出 4 比特范围")
    return k, q + k * c


def scale_down(x, input_sf, output_sf):
    if input_sf < output_sf:
        raise ValueError("这里只实现 ScaleDown")
    d = 1 << (input_sf - output_sf)
    y = (x + d // 2) // d
    return y, x - y * d + d // 2


def reducer_weights(points, alpha):
    n = len(points[0])
    assert all(len(point) == n for point in points)
    return [sum(pow(alpha, t, P) * eq(point, bits(b, n))
                for t, point in enumerate(points)) % P
            for b in range(1 << n)]
