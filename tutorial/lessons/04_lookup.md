# 4 · 验证者为什么不用下载整张查找表

论文：§2.5 和 §4 的结构化表。
原库：[poly.rs](../../upstream/src/util/poly.rs)、[dag/mod.rs](../../upstream/src/dag/mod.rs)。

## 第一步：先用一张真的选择矩阵查表

查询索引取 `[1,3,0,2]`，表 `T=[0,1,2,3]`。
手画一个 `4×4` 的矩阵 `a`：第 `i` 行仅在所选列放 1，其余为 0。

$$v[i]=\sum_j a[i,j]T[j],\qquad
\widetilde v(r)=\sum_j\widetilde a(r,j)\widetilde T(j).$$

查表还必须强制 `a` 的元素为 0/1，且每行和为 1。
否则普通线性组合也能满足等式。试写一行 `[2,-1,0,0]`：行和也是 1，却不是合法选择。

运行 `python3 tutorial/labs.py 5`，然后自己重建该例子的选择矩阵。
列优先布局中，下标为 `i+j*4`；本练习只验证代数关系，不实现完整 Shout。

## 第二步：不用整张表也能算表 MLE

对范围表 `T[j]=j`，因为 `j=sum_h 2**h * bit_h(j)`，多线性延拓就是：

$$\widetilde T(r)=\sum_h2^h r_h.$$

在 `exercises.py` 实现 `range_mle`。算表长 8 的例子时只做 3 项求和。

对幂表 `T[j]=2**j`，先在布尔点写成每个比特的乘积：

$$2^j=\prod_h 2^{2^h b_h}.$$

每个单比特因子的 MLE 是 `1+(2**(2**h)-1)*r_h`，所以：

$$\widetilde T(r)=\prod_h\big(1+(2^{2^h}-1)r_h\big).$$

实现 `power_mle`，运行：

```bash
python3 tutorial/check_exercises.py 4
```

不要在一般域点上直接计算 `2**sum(2**h*r[h])`；那不是这张表的 MLE。

## 第三步：对照真实实现

```bash
python3 tutorial/tools/source.py selection
python3 tutorial/tools/source.py lookup
```

按这个顺序看：`SelectionPolynomial` 如何变稀疏表 → `prove_range` 如何组织证明 → `verify_range` 如何消费它。
再找 `two_pow_dense`：当前表并不是本课的正向幂表，而是 16 项的 `T[k]=2**(15-k)`。
它的闭式是：

$$\widetilde T(r)=2^{15}\prod_{h=0}^{3}\big((1-r_h)+2^{-2^h}r_h\big),$$

负幂用域乘法逆元表示。把这张 16 项表和闭式在三个非布尔点上交叉验证，作为进阶练习。

结构化省掉的是表的承诺及 opening；选择矩阵仍是要认证的 witness。
在原库看到 `TwoPow::verify` 直接返回 `true` 时，继续读 DAG 批量验证路径。
沿路径检查 sumcheck 最终挑战和最终值是否被使用，不能以轮消息递推通过来代替最终认证。

## 本节交付

- 两个闭式函数通过验收。
- 手画选择矩阵，并标出布尔性、行和、表乘积三个约束。
- 分清“表无需承诺”与“查询不需要 witness”这两个说法。

下一节：[定点数和指数分解](05_exp.md)。
