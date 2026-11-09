"""按课验收：python3 tutorial/check_exercises.py 1。

--reference 验证参考实现；--module 可加载你自己的模块（模块名）。
测试包含独立定义式、随机交叉检查与不诚实消息，不能只靠背示例通过。
"""
import argparse
import importlib
import random
import sys
from math import prod

P = 101


def bits(i, n):
    return [(i >> j) & 1 for j in range(n)]


def eq_definition(r, b):
    return prod(x*y + (1-x)*(1-y) for x, y in zip(r, b)) % P


def eval_definition(table, r):
    return sum(v * eq_definition(r, bits(i, len(r)))
               for i, v in enumerate(table)) % P


def lesson1(m):
    assert m.fold([1, 2, 3, 4], 2) == [3, 5]
    assert m.mle([1, 2, 3, 4], [2, 3]) == 9
    assert m.mle([7], []) == 7
    assert m.eq([], []) == 1
    rng = random.Random(101)
    for n in range(1, 5):
        for _ in range(12):
            table = [rng.randrange(P) for _ in range(1 << n)]
            r = [rng.randrange(P) for _ in range(n)]
            before = table[:]
            assert m.mle(table, r) % P == eval_definition(table, r)
            assert table == before, "mle 不应改写调用者的输入"
            for i in range(1 << n):
                assert m.mle(table, bits(i, n)) == table[i]
            assert m.eq(r, bits(0, n)) == eq_definition(r, bits(0, n))
    a, b, c = [1, 2], [3, 5], [3, 10]
    correct = m.mle(c, [2])
    wrong = m.mle(a, [2]) * m.mle(b, [2]) % P
    repaired = sum(m.eq([2], [i]) * a[i] * b[i] for i in range(2)) % P
    assert (correct, wrong, repaired) == (17, 21, 17)
    print("  fold/MLE/eq；乘法反例 17/21/17；48 组随机交叉检查通过")


def lesson2(m):
    cases = {
        "bij,bjk->bik": (["i", "k"], ["b"], ["j"]),
        "ij,jk->ik": (["i", "k"], [], ["j"]),
        "i,i->i": ([], ["i"], []),
        "ij->ji": (["j", "i"], [], []),
        "ij->i": (["i"], [], ["j"]),
        "ij,jk,kl->il": (["i", "l"], [], ["j", "k"]),
        "ij,j->": ([], [], ["i", "j"]),
    }
    for equation, expected in cases.items():
        assert m.classify(equation) == expected, equation
    print("  矩阵乘法、批量乘法、逐元素乘法、转置等 7 类指标分类通过")
    cases = [
        ("ij,jk->ik", [[1, 2, 3, 4], [5, 6, 7, 8]], [2, 3], 93),
        ("bij,bjk->bik", [list(range(1, 9)), list(range(11, 19))], [2, 3, 4], 54),
        ("i,i->i", [[1, 2], [3, 5]], [2], 17),
        ("ij->i", [[1, 2, 3, 4]], [2], 8),
        ("ij->ji", [[1, 2, 3, 4]], [2, 3], 8),
        ("ij,jk,kl->il", [list(range(1, 5))]*3, [2, 3], 20),
        ("ij,j->", [[1, 2, 3, 4], [5, 6]], [], 57),
    ]
    for equation, inputs, r, expected in cases:
        output = m.einsum_toy(equation, inputs)
        assert eval_definition(output, r) == expected, equation
        active, factors = m.compile_toy(equation, inputs, r)
        _, multi, summed = m.classify(equation)
        assert active == multi + summed
        assert len(factors) == len(inputs) + 1
        assert all(len(t) == 1 << len(active) for t in factors)
        assert sum(prod(row) for row in zip(*factors)) % P == expected, equation
    assert m.einsum_toy("ij,jk->ik", [[1, 2, 3, 4], [5, 6, 7, 8]]) == [23, 34, 31, 46]
    assert m.compile_toy("ij,jk->ik", [[1, 2, 3, 4], [5, 6, 7, 8]], [2, 3]) == (
        ["j"], [[3, 5], [11, 12], [1, 1]])
    print("  7 类普通张量计算与编译恒等式交叉验算通过")


def lesson3(m):
    import labs
    _, tables = labs.compile_toy("bij,bjk->bik",
                                [list(range(1, 9)), list(range(11, 19))],
                                [2, 3, 4])
    r = [7, 11]
    assert m.round_message(tables) == [98, 57, 88, 25]
    proof = m.prove_sumcheck(tables, r)
    assert proof == [[98, 57, 88, 25], [26, 32, 55, 95]]
    oracle = lambda point: prod(eval_definition(t, point) for t in tables) % P
    assert m.verify_sumcheck(54, proof, r, 3, oracle)
    assert not m.verify_sumcheck(55, proof, r, 3, oracle)
    assert not m.verify_sumcheck(54, proof, r, 3, lambda p: oracle(p)+1)
    assert not m.verify_sumcheck(54, proof[:-1], r, 3, oracle)
    assert not m.verify_sumcheck(54, [proof[0][:-1], proof[1]], r, 3, oracle)
    corrupt = [msg[:] for msg in proof]
    corrupt[0][0] = (corrupt[0][0] + 1) % P
    assert not m.verify_sumcheck(54, corrupt, r, 3, oracle)
    # 插值以已知系数生成求值，避免只在插值节点上测。
    for x in [0, 1, 2, 7, 100]:
        assert m.interpolate([3, 10, 27], x) == (3+2*x+5*x*x) % P
    # 初始和错误也能编造出内部自洽的消息；最终 oracle 必须拒绝。
    forged = [[27, 27, 27, 27], [64, 64, 64, 64]]
    assert not m.verify_sumcheck(54, forged, r, 3, oracle)
    rng = random.Random(303)
    for n in range(1, 5):
        for count in [1, 2, 3]:
            ts = [[rng.randrange(P) for _ in range(1 << n)] for _ in range(count)]
            challenges = [rng.randrange(P) for _ in range(n)]
            h = sum(prod(row) for row in zip(*ts)) % P
            messages = m.prove_sumcheck(ts, challenges)
            final = lambda point: prod(eval_definition(t, point) for t in ts) % P
            assert m.verify_sumcheck(h, messages, challenges, count, final)
    print("  两轮消息、插值、随机乘积检查与 6 类拒绝条件通过")


def lesson4(m):
    rng = random.Random(404)
    for n in range(0, 6):
        for _ in range(8):
            r = [rng.randrange(P) for _ in range(n)]
            assert m.range_mle(r) == eval_definition(list(range(1 << n)), r)
            assert m.power_mle(r) == eval_definition([pow(2, j, P) for j in range(1 << n)], r)
    print("  range/power 闭式与枚举 MLE 的 48 组交叉检查通过")


def lesson5(m):
    assert m.decompose(0) == (0, 0)
    assert m.decompose(-32768) == (1, -10055)
    assert m.decompose(-100000) == (4, -9148)
    for q in range(-340695, 1, 997):
        k, remainder = m.decompose(q)
        assert q == -22713*k + remainder
        assert 0 <= k <= 15 and abs(2*remainder) <= 22713
    for bad in [1, -1000000]:
        try:
            m.decompose(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("超出教学输入范围时应抛 ValueError")
    for shift in range(0, 6):
        d = 1 << shift
        for x in range(-150, 151):
            y, aux = m.scale_down(x, 15+shift, 15)
            assert 0 <= aux < d
            assert x + d//2 == y*d + aux
    assert m.scale_down(-3, 16, 15) == (-1, 0)
    print("  Q15 分解与有符号整数重缩放、余数范围通过")


def lesson6(m):
    points = [[2, 3], [4, 5]]
    a = [1, 2, 3, 4]
    alpha = 7
    weights = m.reducer_weights(points, alpha)
    assert len(weights) == 4
    h = sum(pow(alpha, t, P) * eval_definition(a, point)
            for t, point in enumerate(points)) % P
    assert h == sum(x*y for x, y in zip(weights, a)) % P
    # 不同挑战点上的值不能直接当成某个自然“相加后的点”的求值。
    assert h != eval_definition(a, [6, 8])
    rng = random.Random(606)
    for n in range(1, 5):
        for count in range(1, 5):
            table = [rng.randrange(P) for _ in range(1 << n)]
            ps = [[rng.randrange(P) for _ in range(n)] for _ in range(count)]
            alpha = rng.randrange(1, P)
            w = m.reducer_weights(ps, alpha)
            assert sum(x*y for x, y in zip(w, table)) % P == sum(
                pow(alpha, t, P) * eval_definition(table, p) for t, p in enumerate(ps)) % P
    print("  多点 claim 合并恒等式及 16 组随机检查通过")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lesson", choices=["all", "1", "2", "3", "4", "5", "6"])
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--reference", action="store_true")
    group.add_argument("--module", default="exercises")
    args = parser.parse_args()
    m = importlib.import_module("solutions" if args.reference else args.module)
    lessons = [lesson1, lesson2, lesson3, lesson4, lesson5, lesson6]
    try:
        for i, lesson in enumerate(lessons, 1):
            if args.lesson in ("all", str(i)):
                print(f"第 {i} 课 · {m.__name__}")
                lesson(m)
    except NotImplementedError as e:
        print(f"待完成：{e}\n继续编辑 tutorial/exercises.py，再运行同一命令。")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
