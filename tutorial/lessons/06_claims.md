# 6 · 证明沿着 DAG 反方向走

论文：§5、附录 H–I。
原库：[dag/mod.rs](../../upstream/src/dag/mod.rs)、[reducer.rs](../../upstream/src/basicblock/reducer.rs)。

## 第一步：认识两个核心类型

`Witness` 保存张量数据和元信息：shape、数据类型、定点尺度 sf、角色。
`Claim` 表示一句话：某条边的某个多项式在某个点的值是某个数。

```text
Claim { edge_id, sparse_id, point, eval }
语义：该 edge_id / sparse_id 对应的多项式在 point 上求值为 eval
```

不能只跟踪 eval；点、边、稀疏块编号都是声明的一部分。

## 第二步：先跟踪一个两节点图

让 `Z=XW`，然后 `Y=Z+C`，用第二节的 X、W 和全 1 的 C。
输出表为 `[24,35,32,47]`，在输出点 `(2,3)` 上的值为 94（模 101）。

正向计算：`X,W → Z → Y`。反向证明：

```text
Y(2,3)=94
  Add：归约为 Z(2,3)=93 和 C(2,3)=1
  MatMul：对 j 做 Sumcheck
    若 j 的挑战为 7：归约为 X(2,7)=17 和 W(7,3)=18
  叶子：这三个输入求值还必须由真实输入/权重认证
```

运行可打印完整记录的参考程序：

```bash
python3 tutorial/tools/trace_claims.py
```

这个演示在叶子处直接求值，没有 PCS。它让你看到每一步缺少哪种认证，
第八节再把这个位置替换成真实 commitment/open/verify。

## 第三步：自己画 Claim 表

给边编号 `X=0,W=1,C=2,Z=3,Y=4`，列出：

| 节点 | 收到的输出 claim | 产生的输入 claim | 验证关系 |
|---|---|---|---|
| Add | `(4,[2,3],94)` | `(3,[2,3],93)`、`(2,[2,3],1)` | 同一点的值相加 |
| MatMul | `(3,[2,3],93)` | `(0,[2,7],17)`、`(1,[7,3],18)` | 轮消息递推与最终乘积 |

注意最后两个输入的点不同，因为它们各自的指标顺序分别是 `(i,j)` 和 `(j,k)`。
证明反向传播不是训练反向传播，没有梯度。

## 第四步：一个张量被多个节点消费怎么办

同一张表 A 可能收到多个点上的声明 `A(rt)=vt`。这些值不能直接视为同一点的值相加。
先固定原声明，再取随机 alpha，使用：

$$\sum_t\alpha^t v_t=\sum_b E(b)\widetilde A(b),\quad
E(b)=\sum_t\alpha^t\operatorname{eq}(r_t,b).$$

右侧是两张 MLE 表的乘积求和，可再做一次 Sumcheck，归约成新的 A 求值。
在 `exercises.py` 实现 `reducer_weights`，这里 alpha=7 仅用于确定性教学。

```bash
python3 tutorial/check_exercises.py 6
python3 tutorial/tools/source.py reducer
```

对照原库：`calc_pow` 对应 alpha 的幂，`eq_partial_polys` 对应每个点的 eq 表，
`eq_poly` 对应 E，最后的 `claim_x` 对应合并后的输入声明。

## 第五步：回到 BasicBlock 和 DAG

```bash
python3 tutorial/tools/source.py witness
python3 tutorial/tools/source.py block
python3 tutorial/tools/source.py dag_prove
```

每种 BasicBlock 有三个阶段：

- `run`：由输入计算诚实 witness。
- `prove`：从输出声明生成协议消息和输入声明。
- `verify`：验证消息及节点的代数关系。

`Dag::prove` 负责挑选可以反向处理的节点、必要时插入 Reducer、调用节点 prove、归集叶子 opening。
读原库时用不同颜色标记两类对象：`node_proofs` 内的 claim 和 `edge_proofs` 中用于 opening 的 claim。
继续检查 verifier 如何强制它们的边、点和值一致；内部各自通过还不足以证明组合正确。

## 本节交付

- 独立列出两节点图所有 claim，解释各点坐标的顺序。
- Reducer 恒等式通过验收。
- 对一个 BasicBlock 填完“收到什么声明、发送什么消息、产生什么声明、最后谁认证”的四栏表。

下一节：[调用真实 Rust API](07_rust.md)。
