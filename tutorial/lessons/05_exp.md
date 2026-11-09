# 5 · 有限域不能直接证明浮点 exp

论文：§2.3、§4、§5.3。
原库：[scale.rs](../../upstream/src/basicblock/scale.rs)、[exp.rs](../../upstream/src/basicblock/exp.rs)、[builder.rs](../../upstream/src/dag/builder.rs)。

## 第一步：分开两种算术

前几课的 101 是教学域。Q15 的 `32768` 是整数定点数的 1.0，不能把它模 101 后继续讨论数值精度。
这一节在普通有符号整数上运行，原库再把这些整数编码进大素域。

若 `q≈2**s*x`，两个尺度为 `s` 的整数相乘后，尺度变为 `2s`，需要重缩放。
域等式本身不区分正负或大小，范围证明负责把域元素限制到希望的整数语义。

## 第二步：按原库规则写重缩放

先只实现 ScaleDown。在 `exercises.py` 写：

$$D=2^{s_{in}-s_{out}},\qquad y=\left\lfloor\frac{x+D/2}{D}\right\rfloor,
\qquad a=x-yD+D/2,\quad0\le a<D.$$

整数实现中 `D/2` 使用 `D//2`；当 `D=1` 时为 0。
返回 `(y,a)`。注意 Python 的 `//` 对负数向下取整，而 `int(x/D)` 向零截断。

请先手算 `x=-3,D=2`：`y=-1,a=0`。这里半整数舍入到较大的整数，
与 Rust 浮点 `round()` 的半数远离零规则不同。

原库 `ScaleDown::run` 正是先加半个 D，再算术右移，并把 `a` 编成选择矩阵。
范围检查加上等式，才能排除 prover 任意选择 `y` 的情况。

## 第三步：把 exp 分为小幂表和小余量

设 `C=round(2**15*ln(2))=22713`。对非正整数 `q`：

$$q=-kC+r,\qquad 0\le k\le15,\qquad |r|\lesssim C/2.$$

在 `exercises.py` 写 `decompose(q)`。本课只处理小整数的合法范围；
将 `-q/C` 四舍五入到最近整数作为 k，计算 `r=q+kC`。越界应抛 `ValueError`。
因为比值非负，可以用整数公式实现最近整数，不必调用 Python 的 ties-to-even `round`。

```text
q=-32768 → k=1, r=-10055
q=-100000 → k=4, r=-9148
```

然后在笔记里写出近似：

$$e^{q/2^{15}}\approx2^{-k}\left(1+u+u^2/2+u^3/6\right),\qquad u=r/2^{15}.$$

```bash
python3 tutorial/check_exercises.py 5
python3 tutorial/labs.py 6
```

`labs.py` 的浮点结果只说明分解与 Taylor 误差，不是原库逐节点定点运算的精确模拟。

## 第四步：逐节点读 StructuredExp

```bash
python3 tutorial/tools/source.py scale
python3 tutorial/tools/source.py exp
python3 tutorial/tools/source.py exp_builder
```

沿 `DagBuilder::exp` 写一张自己的尺度表：

| 中间量 | 代码来源 | 尺度 |
|---|---|---|
| 截断后的输入 | `clamp_lower` | 全局 `SF_LOG` |
| 分解余量 | `ExpHelper`，然后 `scale` | 转为 15 |
| `2**(15-k)` | `TwoPow` | 15 |
| `1/6,1/2,1` | 整数 `5461,16384,32768` | 15 |
| Taylor 乘法结果 | `einsum(..., true)` | 经重缩放回 15 |
| 幂表乘 Taylor | `einsum(..., false)` | 30 |
| 最终输出 | `scale(...,30,SF_LOG)` | 全局 `SF_LOG` |

读完要能找到每个 `true/false` 如何决定是否插入重缩放节点。
上游 `config.yaml` 的 `SF_LOG=10`，不应把全局尺度默认为 15。

## 第五步：从 verifier 角度重看约束

在纸上列出：分解等式、k 的范围、r 的区间、输入非正的来源、截断规则、各次重缩放余数范围。
源码 `run` 算出来的 k、r 是诚实 witness；要另行确认 verifier 强制了哪些约束。
例如只约束 `0<=k<=15` 并不能保证 r 足够小。

本课程的静态源码观察在[补充阅读的安全边界部分](../reference/theory.md#pcs安全边界与研究问题) 保留，
是后续负向实验的起点，不是一次完成的安全审计。

## 本节交付

- 分解与有符号重缩放通过验收。
- 给出“整数计算完全正确，但近似实数函数仍有误差”的例子。
- 在 `DagBuilder::exp` 给每条边写下 scale，并区分 witness 计算与验证约束。

下一节：[Claim 如何沿 DAG 传播](06_claims.md)。
