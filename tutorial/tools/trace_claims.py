"""模 101 的两节点 Claim 跟踪；叶子使用直接 oracle，无 PCS。"""
from dataclasses import dataclass
from math import prod
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from labs import P, compile_toy, einsum_toy, mle, prove_sumcheck, verify_sumcheck


@dataclass(frozen=True)
class Claim:
    edge_id: int
    point: tuple
    eval: int


def run(verbose=True):
    x, w, c = [1, 2, 3, 4], [5, 6, 7, 8], [1, 1, 1, 1]
    z = einsum_toy("ij,jk->ik", [x, w])
    y = [(a+b) % P for a, b in zip(z, c)]
    assert z == [23, 34, 31, 46] and y == [24, 35, 32, 47]
    point = (2, 3)
    output = Claim(4, point, mle(y, point))
    z_claim = Claim(3, point, mle(z, point))
    c_claim = Claim(2, point, mle(c, point))
    assert output.eval == (z_claim.eval + c_claim.eval) % P == 94

    active, tables = compile_toy("ij,jk->ik", [x, w], point)
    assert active == ["j"] and tables == [[3, 5], [11, 12], [1, 1]]
    challenges = [7]
    messages = prove_sumcheck(tables, challenges)
    oracle = lambda r: prod(mle(t, r) for t in tables) % P
    assert verify_sumcheck(z_claim.eval, messages, challenges, 3, oracle)
    x_claim = Claim(0, (2, 7), mle(x, [2, 7]))
    w_claim = Claim(1, (7, 3), mle(w, [7, 3]))
    assert (x_claim.eval, w_claim.eval) == (17, 18)
    assert x_claim.eval * w_claim.eval % P == oracle(challenges)

    leaves = [x_claim, w_claim, c_claim]
    inputs = {0: x, 1: w, 2: c}

    def authenticate(claim):
        return mle(inputs[claim.edge_id], claim.point) == claim.eval

    assert all(authenticate(claim) for claim in leaves)
    assert not authenticate(Claim(0, (2, 7), 18))  # 值被修改
    assert not authenticate(Claim(0, (7, 2), 17))  # 坐标被交换
    if verbose:
        print("forward: Z=XW →", z, "; Y=Z+C →", y)
        print("output:", output)
        print("Add reduces to:", z_claim, c_claim)
        print("MatMul tables:", tables)
        print("Sumcheck messages:", messages, "; j challenge:", challenges[0])
        print("MatMul reduces to:", x_claim, w_claim)
        print("leaf direct oracle accepted all claims; changed value/point rejected")
        print("next: replace direct oracle with PCS opening (lesson 8)")
    return leaves


if __name__ == "__main__":
    run()
