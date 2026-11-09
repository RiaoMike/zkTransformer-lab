# 3 · 自己实现 prover 和 verifier

论文：§2.4.2、附录 E–G。
原库：[linear_prover.rs](../../upstream/src/crypto/sumcheck/linear_prover.rs)、[verifier.rs](../../upstream/src/crypto/sumcheck/verifier.rs)。

## 从什么声明开始

沿用上一节的批量矩阵乘法，把编译结果记作三张表 `A,B,E`。
我们要证明 `H=sum_{b,j} A(b,j)*B(b,j)*E(b,j)=54`，所有算术模 101。

第一轮发送 `q1(t)=sum_j A(t,j)*B(t,j)*E(t,j)`。
验证者检查 `q1(0)+q1(1)=H` 后，给出挑战 `rho_b`。
第二轮发送 `q2(t)=A(rho_b,t)*B(rho_b,t)*E(rho_b,t)`。

三张 MLE 表相乘，每个变量次数最多为 3，所以用四个求值 `q(0)..q(3)` 表示轮消息。
这些数不是系数。后续轮中某些变量的真实次数可能更小，统一上界仍然合法。

## 第一步：生成单轮消息

在 `exercises.py` 实现 `round_message(tables)`。
对每个 `t=0..l`，分别 `fold` 各因子，再对同一位置的值求乘积，最后求和。

不能先把输入表逐项相乘，再对乘积表 `fold`；那会把高次多项式错误地当成 MLE。
用第一节的 17/21 反例解释为什么。

## 第二步：实现插值

实现 `interpolate(values,x)`，公式为：

$$q(x)=\sum_{j=0}^{d}q(j)\prod_{k\ne j}\frac{x-k}{j-k}.$$

每个分母都在模 101 下求逆：`pow(denominator,-1,101)`。
例如 `values=[3,10,27]` 对应 `q(t)=3+2t+5t²`，请在 `x=7` 而不只是插值节点处核对。

## 第三步：按挑战更新表

实现 `prove_sumcheck(tables,challenges)`：复制输入表，每轮生成消息，然后用本轮挑战折叠所有表。
本练习使用固定挑战 `[7,11]`，让每次运行都能核对同一份记录。

```text
H = 54
第 1 轮：[98,57,88,25]    (98+57) mod 101 = 54
挑战 7 后：q1(7) = 58
第 2 轮：[26,32,55,95]    (26+32) mod 101 = 58
挑战 11 后：q2(11) = 17
```

请自己用插值函数计算最后一个值，验收器会交叉核对全部消息。

## 第四步：实现验证器

`verify_sumcheck` 按顺序检查：轮数、每轮消息长度、端点和、插值更新，最后比较 `oracle(challenges)`。
教学程序中的 oracle 直接读取小输入表；真实协议会把这些值归约到上游声明或用 PCS 认证。

```bash
python3 tutorial/check_exercises.py 3
```

验收里有一组特别的伪造消息：第一轮四个值全为 27，第二轮全为 64。
端点和递推在模 101 下完全自洽，但它没有描述真实输入。必须靠最终 oracle 检查拒绝。
这说明“消息彼此一致”不能替代“消息绑定真实多项式”。

## 第五步：理解原库如何生成挑战

```bash
python3 tutorial/tools/source.py sumcheck
python3 tutorial/tools/source.py verifier
python3 tutorial/tools/source.py transcript
```

对照以下操作：

| 你写的代码 | 原库 |
|---|---|
| `round_message` | `compute_round_message`、`compute_g_value` |
| 按挑战折叠输入表 | `receive_challenge`、`bind_variable_to_challenge` |
| 端点和与插值 | `SumcheckVerifier::verify` |
| 固定的 `[7,11]` | Merlin transcript 吸收消息后派生挑战 |
| 最终 `oracle` 比较 | 外层 `Einsum::verify` 的 `eq_eval * product_eval` |

`SumcheckVerifier::verify` 返回最终值和挑战，并不独自完成最后的乘积认证。
不要把返回 `Some` 当成一个完整节点关系已经验证完毕。

固定挑战只是教学记录；给它换成普通随机数也不会自动得到完整非交互式协议。
原库示例还需要保证 prover/verifier 的 transcript 标签、实例参数和消息顺序一致。

## 本节交付

- 四个函数通过验收；能手工跟踪两轮 running sum。
- 篡改初始值、某条消息、最终 oracle 时都被拒绝。
- 能指出原库“递推检查”和“最终关系检查”分别在哪里。

下一节：[结构化查表](04_lookup.md)。
