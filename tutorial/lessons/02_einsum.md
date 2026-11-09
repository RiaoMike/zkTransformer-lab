# 2 · 把论文定理 3.1 写成一个微型编译器

论文：§2.1、§3，重点是定理 3.1，而不是先记住复杂度结论。
原库：[einsum.rs](../../upstream/src/basicblock/einsum.rs)。

## 第一步：先做普通张量计算

从 `ij,jk->ik` 开始。它表示 `Z[i,k]=sum_j X[i,j]*Y[j,k]`。
用列优先表 `X=[1,2,3,4]`、`Y=[5,6,7,8]`，手写两个矩阵再乘：

```text
X = [[1,3], [2,4]]
Y = [[5,7], [6,8]]
Z = [[23,31], [34,46]]
列优先 Z = [23,34,31,46]
```

不要把 `[1,2,3,4]` 默认为逐行排列。原库 `Witness::get` 使用第一个维度变化最快的下标，
`Witness::ndarray` 和 `Einsum::run` 通过反转轴处理这种布局。

## 第二步：分类指标

在 `exercises.py` 完成 `classify`。先解析 `->` 两边，再统计每个字母出现在哪些输入中。

| 类别 | `bij,bjk->bik` | 原库字段 | 协议动作 |
|---|---|---|---|
| 输出指标，只在一个输入中出现 | `i,k` | `free_once` | 直接代入输出挑战 |
| 输出指标，在多个输入中出现 | `b` | `free_multi` | 保留布尔求和并乘 `eq` |
| 不在输出中的指标 | `j` | `summation` | 保留求和 |

```bash
python3 tutorial/check_exercises.py 2
python3 tutorial/tools/source.py classify
```

此时验收会先检查分类，再提示后面的两个编译练习尚未完成；继续本节即可。

原库分类函数名字带 `from_shapes`，但实际只接收表达式。字母占多少比特由后续 `char_to_range` 根据 shape 决定。
例如维度 8 的 `j` 占 3 个比特，不是一轮挑战。

## 第三步：把输出挑战代进去

对批量矩阵乘法，先在纸上推到这一行：

$$\widetilde Z(r_b,r_i,r_k)=\sum_{b,j}\operatorname{eq}(r_b,b)
\widetilde X(b,r_i,j)\widetilde Y(b,j,r_k).$$

`i,k` 各只出现一次，所以直接代入后仍保持对输出挑战的多线性。
`b` 出现两次，必须留在布尔求和内部，再用 `eq(rb,b)` 插值。

检验定理时问两件事：右侧对输出挑战是否多线性？当输出挑战是布尔点时，是否等于原张量计算？
这两项合起来才允许使用上一节的唯一性结论。

## 第四步：实际生成 Sumcheck 的输入表

先运行一次完整参考程序，观察每个表达式的求和变量：

```bash
python3 tutorial/labs.py 3
```

然后继续填写 `exercises.py` 的 `einsum_toy` 和 `compile_toy`。前者用普通下标计算输出张量，
后者只支持每个字母维度为 2，按以下步骤重写 `labs.py` 中的 `compile_toy`：

1. 调用自己的分类器，按 `free_multi + summation` 决定活动变量顺序。
2. 枚举活动变量的布尔点；按最低位约定转换下标。
3. 将 `free_once` 的输出挑战和活动坐标放到同一个字母字典里。
4. 按每个输入的字母顺序组点，再用 `mle` 得到一个值。
5. 最后加一张 `eq` 表；没有共享输出指标时，它是一张全 1 表。

先实现本节开头的矩阵乘法。在输出挑战 `(ri,rk)=(2,3)` 时，应得到：

```text
活动变量：j
X(ri,j) 的表：[3,5]
Y(j,rk) 的表：[11,12]
eq 表：[1,1]
布尔求和：3*11+5*12 = 93
输出 MLE：mle([23,34,31,46],[2,3]) = 93
```

再用 `bij,bjk->bik`、输入表 `1..8` 和 `11..18`、输出挑战 `[2,3,4]` 验证，活动变量为 `[b,j]`，声明值为 54。
这是第三节统一使用的例子。

重新运行 `python3 tutorial/check_exercises.py 2`，核对 7 类表达式的计算与编译结果。

## 第五步：逐段映射原库

```bash
python3 tutorial/tools/source.py einsum
```

阅读顺序：`einsum_helper` → 排列 → `fix_variables` → 构造/广播 `eq_poly` → `LinearSumcheckProver` → 生成输入 `Claim`。
在笔记里记录：`degree_one_challenges` 对应哪些输出挑战，`high_degree_challenge` 对应什么，最终点如何逆排列。

这里要区分数学定理与当前实现范围：教学编译器通过显式枚举完成缺失坐标广播；
原库 `LinearSumcheckProver::prove` 要求各输入表等长，`Einsum::prove` 这条路径没有通用广播步骤。
不要用 `ij,jk,kl->il` 的教学例子通过来断言原库也支持该表达式。

## 本节交付

- 分类器通过验收；自己的编译器生成 `[3,5]`、`[11,12]`、`[1,1]`。
- 解释 `b` 为什么不能像 `i` 一样直接固定。
- 写出原库输入表和原承诺点之间的排列关系。

下一节：[把一个求和恒等式变成消息](03_sumcheck.md)。
