# 公式详解与补充阅读

按 [课程入口](../README.md) 学习时，需要更详细的公式推导和实现边界可查本文。
源码路径均相对于 `upstream/`；版本与实测范围见 [验证记录](VALIDATION.md)。

## MLE 与求值表

一段长度为 $2^n$ 的数组并不是多项式的系数。它存放多项式在布尔点的值：

$$\widetilde A(r)=\sum_{b\in\{0,1\}^n} A[b]\operatorname{eq}(r,b),\qquad
\operatorname{eq}(r,b)=\prod_{j=0}^{n-1}\big(r_jb_j+(1-r_j)(1-b_j)\big).$$

`eq` 在两个布尔向量上是相等指示函数；在一般域点上，它是多项式，不是返回真假值的比较操作。

本教程与 `DenseMLPoly::fix_variables` 采用的邻接折叠约定相同：数组下标的最低位对应第一个变量。因此 `[a00,a10,a01,a11]` 的顺序为 `(0,0),(1,0),(0,1),(1,1)`。不要把通常写矩阵的逐行顺序直接套到这个约定上。仓库 `Witness::ndarray`、`reversed_axes` 和排列函数值得一起看。

固定第一个变量为 $r_0$ 后，每对相邻值替换为：

$$a'_j=(1-r_0)a_{2j}+r_0a_{2j+1}=a_{2j}+r_0(a_{2j+1}-a_{2j}).$$

反复折叠就得到 MLE 求值。计算量是 $N/2+N/4+\cdots+1=O(N)$。

**自己敲：** 新建 `my_mle.py`，先写 `fold`，再写循环调用它的 `mle`。模数取 101；减法后也取模。不要使用浮点数。然后用定义式写另一个低效版本交叉验证。

验收：`mle([1,2,3,4],[2,3]) == 9`；在四个布尔点分别返回 1、2、3、4。读取 `labs.py` 的 `lesson1` 对照。

源码定位：`DenseMLPoly::from_evaluations`、`fix_variables`、`evaluate_lagrange_basis`。注意 `fix_variables` 返回剩余变量的多项式，而不是总是返回一个域元素；只有全部固定后才剩一个值。

## 逐元素乘法反例

给定 $A=[1,2]$、$B=[3,5]$，逐元素乘积为 $C=[3,10]$。

$$\widetilde A(t)=1+t,\quad\widetilde B(t)=3+2t,\quad\widetilde C(t)=3+7t.$$

在 $t=0,1$ 上，$\widetilde C(t)=\widetilde A(t)\widetilde B(t)$。但在 $t=2$：

$$\widetilde C(2)=17,\qquad\widetilde A(2)\widetilde B(2)=21.$$

两个多项式相差 $2t(t-1)$。它在布尔点消失，在一般域点不消失。因此“在布尔输入正确”不能直接推出“用相同表达式在随机挑战上也正确”。唯一性论证要求两边都是多线性多项式。

正确等式为：

$$\widetilde C(r)=\sum_{u\in\{0,1\}}\operatorname{eq}(r,u)\widetilde A(u)\widetilde B(u).$$

这里把乘法保留在布尔求和内部，外侧通过 `eq` 对输出进行多线性插值。这个等式与逐元素乘法的 sumcheck/zero-check 思路直接相连。

**自己敲：** 输出 `17,21,17`，分别代表输出 MLE、错误的直接乘积、修正后的求和。再把 $r$ 改成 0 和 1，观察错误写法为什么能通过只测布尔点的测试。

源码：`Einsum::prove` 构建 `eq_poly` 并把它加入 `sumcheck_input_polys`。`Einsum::verify` 最后计算 `eq_eval * product_eval`。不要把这个 `eq` 因子当成可删去的编码细节。

## EinSumcheck 编译

考虑 `bij,bjk->bik`：

$$Z[b,i,k]=\sum_j X[b,i,j]Y[b,j,k].$$

一个字母通常代表一组比特变量，例如维度为 8 的 `j` 代表 3 个布尔变量。本课教学代码让每个字母的维度都为 2，便于查看每轮计算。

| 指标类别 | 本例 | 如何处理 |
|---|---|---|
| 只在一个输入中出现的输出指标 $F_1$ | `i,k` | 直接代入输出挑战 $r_i,r_k$ |
| 在多个输入中出现的输出指标 $F_{\ge2}$ | `b` | 保留布尔求和，并乘 `eq(rb,b)` |
| 不出现在输出中的求和指标 $S$ | `j` | 保留布尔求和 |

所以：

$$\widetilde Z(r_b,r_i,r_k)=\sum_{b,j}\operatorname{eq}(r_b,b)
\widetilde X(b,r_i,j)\widetilde Y(b,j,r_k).$$

为什么可以直接固定 `i`？因为它只出现在一个输入因子中，乘积对它的每一位仍然最多一次。`b` 同时出现在两个因子中，必须使用上一课的修复。

一般式为：

$$\widetilde Z(r)=\sum_{s,h}\operatorname{eq}(r_{F_{\ge2}},h)
\prod_t\widetilde T_t\big(\pi_t(h,s,r_{F_1})\big).$$

这里 $s,h$ 的长度是对应指标的**比特数之和**，不是字母的数量。$\pi_t$ 挑选并排列第 $t$ 个输入需要的坐标。

证明分两步：右侧对输出挑战 $r$ 多线性；在布尔 $r$ 上，`eq` 让 $h$ 求和塌缩，剩下原来的 Einsum。于是由 MLE 唯一性得到任意域点上的恒等式。

**自己敲：** 按顺序实现 `classify`、`einsum_toy`、`compile_toy`。后两者必须走不同路径：前者算布尔张量，后者部分固定输入 MLE 再生成求和表。最后比较输出 MLE 与所有乘积项之和。参考实现覆盖矩阵乘法、批量矩阵乘法、逐元素乘法、ReduceSum、Transpose 和三输入 contraction。

源码阅读顺序：

1. `classify_einsum_indices_from_shapes`：返回 `free_once/free_multi/summation`，实际参数只有表达式；函数名不意味着读取了 shape。
2. `char_to_range`：把一个指标变成若干 MLE 比特位置。
3. `einsum_helper`：算输入排列、可直接固定的挑战、高次数自由指标挑战、求和轮数。
4. `permute_evals_by_ranges`、`fix_variables`：重排后固定 $F_1$。
5. `evaluate_lagrange_basis` 与 `broadcast_evals_by_doubling`：构建并扩展 `eq` 表。
6. `LinearSumcheckProver`：对乘积关系执行 sumcheck。
7. `invert_points_by_ranges`：把协议挑战还原到输入承诺采用的变量顺序；预排列路径需要单独追踪。

**实现范围必须区分：** 论文附录 F 讨论不同变量数的操作数以及忽略额外坐标的算法。当前 `LinearSumcheckProver::prove` 明确断言所有输入表等长；上述 `Einsum::prove` 路径没有通用的缺失指标扩展步骤。不要据定理的通用性推断任意 Einsum 表达式都能在当前实现中运行。教程 `compile_toy` 显式枚举统一坐标域完成广播，便于理解，但不是论文优化的完整复刻。重复指标如 `ii->i` 也不在教学编译器支持范围。

另一个术语区别：论文称这些算子为 linear operations；矩阵乘法对两个可变输入联合而言是双线性的，逐元素乘法也不是联合线性映射。

## Sumcheck 消息

令 $g(b,j)=\operatorname{eq}(r_b,b)\widetilde X(b,r_i,j)\widetilde Y(b,j,r_k)$，初始声明为 $H$。

第一轮发送 $q_1(t)=\sum_j g(t,j)$。验证者检查 $q_1(0)+q_1(1)=H$，随后给出挑战 $\rho_b$。第二轮发送 $q_2(t)=g(\rho_b,t)$，检查 $q_2(0)+q_2(1)=q_1(\rho_b)$。最后需要检查：

$$q_2(\rho_j)=\operatorname{eq}(r_b,\rho_b)
\widetilde X(\rho_b,r_i,\rho_j)\widetilde Y(\rho_b,\rho_j,r_k).$$

**最后这一步不能省略。** 前面的递推只保证消息彼此一致，未保证它们描述真实的输入多项式。一般验证者不直接读取整个输入；两个输入 MLE 的值必须通过上游归约或 PCS opening 认证。

每轮对当前变量的次数至多等于含该变量的因子数。本例 `b` 轮最多三次；`j` 轮最多二次。仓库使用统一上界，为三个因子都发送四个求值点 `q(0),q(1),q(2),q(3)`。这些是**求值表示**，不是四个系数。

`compute_round_message` 在每个插值点先分别线性插值各因子，再相乘、求和。收到挑战后，`bind_variable_to_challenge` 折叠每个因子的数组。固定因子数时，总工作量按几何级数相加为线性；不能理解为任意张量表达式都只需输入总长度的线性时间。

**自己敲：** 先写拉格朗日插值，再写 `prove_sumcheck`、`verify_sumcheck`。练习使用固定挑战 `[7,11]`，方便逐行核对；这不是密码学实现，不能作为 Fiat–Shamir 的替代。

本例初始声明为 54，两轮消息应是 `[98,57,88,25]`、`[26,32,55,95]`，全部在模 101 下。修改初始声明、第一轮一个值、最终 oracle 值，验证者都应拒绝。

源码对应：`SumcheckVerifier::verify` 检查轮数、每轮消息长度、端点和，并返回最终 `running_sum` 与挑战；外层 `Einsum::verify` 负责最后的乘积关系。`Transcript` 使用 Merlin，先吸收消息再取挑战。生产协议还要绑定公共实例、承诺和各子协议上下文，不能只把固定挑战改成随机数就称为安全实现。

声音性估算应从实际轮数和每轮次数开始：$\sum_i d_i/|\mathbb F|$，再计入初始随机点检查、PCS 与协议组合误差。论文引理 3.2 的记号需要核对变量域的含义，不能机械地用“最大单个输入的变量数”代替任意表达式的总求和轮数。

## Structured lookup

查询数组为 $v[i]$，表为 $T[j]$。引入选择矩阵 $a[i,j]$，每行恰有一个 1，且 $v[i]=\sum_j a[i,j]T[j]$。于是：

$$\widetilde v(r)=\sum_j\widetilde a(r,j)\widetilde T(j).$$

还必须验证选择矩阵的布尔性与每行和为 1；否则一般线性组合也能满足右式，并不意味着“查询到了表里的一个元素”。布尔性可以归约为带随机 `eq` 权重的 $a(a-1)$ 零和检查，行和约束也要绑定到同一张选择矩阵。

结构化范围表 $T[j]=j$ 的 MLE 为：

$$\widetilde T(z)=\sum_{h=0}^{n-1}2^h z_h.$$

对幂表 $T[j]=2^j$：

$$\widetilde T(z)=\prod_{h=0}^{n-1}\big(1+(2^{2^h}-1)z_h\big).$$

验证者只需 $O(n)$ 次操作即可求表 MLE，无需表承诺或表 opening。但**选择矩阵仍属于需认证的 witness**，并没有因此取消所有 lookup 辅助承诺。

尤其注意：$2^{\sum_h2^hz_h}$ 在任意域点上不是这里定义的 MLE。可以在布尔点用指数拆分推导乘积式，再由多线性插值延拓；不能把实数指数直接用于有限域挑战。论文 §4 中相邻写出的指数形式与乘积形式应在这个意义下理解。

**自己敲：** 对 8 项范围表和幂表，比较枚举 MLE 与闭式求值；再构造选择索引 `[1,3,0,2]`，验证 one-hot 查询恒等式。`lesson5` 验证这些代数关系，不实现完整 Shout 证明。

源码：`SelectionPolynomial::to_sparse`、`Dag::prove_range/verify_range`、`Dag::prove_two_pow/verify_two_pow`。`TwoPow::verify` 本身返回 `true`，因为设计上交给 DAG 批量验证；要读完整调用链，不能只看单个接口。

## 指数分解与量化

真实输入用整数 $q=\operatorname{round}(2^s x)$ 表示。对非正输入，选择小整数 $k$ 与余量 $r$：

$$q\approx-k(2^s\ln2)+r,\qquad
u=r/2^s,\qquad e^x\approx2^{-k}\left(1+\nu+\frac{\nu^2}{2}+\frac{\nu^3}{6}\right).$$

分解让 $\nu$ 接近 0，因此低次 Taylor 多项式较准确。剩下的 $2^{-k}$ 转成小的幂表查询。定点表示下实际查询 $2^{15-k}$。

源码的关键细节：

| 位置 | 实际操作 | 阅读时要核对 |
|---|---|---|
| `ExpHelper::run` | 将 $2^s\ln2$ 舍入为整数，再计算 `k` 与 `r` | 证明关系应使用同一整数常量 |
| `K_BITS=4` | 选择矩阵的表索引是 0 到 15 | 上游需保障非正输入及有效范围 |
| `DagBuilder::exp` | 先 `clamp_lower`，再建立分解节点 | 截断会改变数值语义 |
| `TwoPow::run` | 输出 `1 << (15-k)` | 表是反向幂表，不是直接 `2^k` |
| Taylor 构图 | 使用 5461、16384、32768 | 对应 Q15 的约 $1/6,1/2,1$ |
| 最终 `scale` | 从尺度 30 转回全局尺度 | 乘法、重缩放与舍入需要一起证明 |

反向幂表也有闭式：$\widetilde T(z)=2^{15}\prod_h((1-z_h)+2^{-2^h}z_h)$，其中负幂使用域乘法逆元；这与布尔索引表一致。

仓库的 Taylor 求值顺序是 $r^2$、$r/6+1/2$、两者相乘，再加 $r$ 与 1，最后乘幂表输出。每个乘法节点可能插入重缩放，因此把浮点表达式计算一次再舍入不等于逐个执行这些整数节点。

**自己敲：** `lesson6` 显示整数分解、浮点近似与真实指数的差异。它故意只是数值说明，不声称逐位模拟仓库的所有舍入，也不代表论文所报误差分布。练习中 `q=-32768` 的近似与目标相差约 5.72 个 Q15 单位，可据此体会平均误差与单点误差不同。

需要证明的约束至少包括：分解等式、$k$ 的合法范围、$r$ 的目标区间、输入符号/截断规则、乘法重缩放的余数范围。只证明 $k$ 在 0 到 15，不能推出 $r$ 很小，也不能推出 Taylor 近似准确。

**源码待核对点：** `verify_range` 的 ExpHelper 分支检查从输入/余量计算出的 $k$ 与 lookup 一致；本次检查的路径中没有看到独立限制 $r$ 到半个 ln2 区间的对应检查。应继续审计整张 DAG 与约束生成，不能把 `run` 中诚实计算出来的余量范围自动当成验证者已强制执行的范围。

## Attention 与声明图

先只考虑 $Q=XW_Q$、$K=XW_K$、$V=XW_V$，再计算 $S=QK^\top$、$A=\operatorname{softmax}(S)$、$O=AV$。论文附录 I 的 Query projection + RoPE 是更小的阅读入口。

| 正向计算 | 反向证明要做什么 |
|---|---|
| `einsum("bsi,ij->bsj", ...)` | 输出挑战固定 `b,s,j` 中的适当坐标，对 contraction 指标做 sumcheck |
| `reshape` 分 heads | 根据底层布局重新解释或排列挑战坐标 |
| RoPE 的邻位交换 | 使用结构化排列矩阵求值 |
| 与 cos/sin 逐元素乘法 | `eq` 加权乘积 sumcheck |
| 两支相加 | 同一点的求值相加，不需要乘法 sumcheck |
| 某张量被多支消费 | 合并多个求值声明，再继续向上游归约 |

完整执行路径从 `src/bin/nanogpt.rs` 或 `oneshot_gpt2.rs` 追到 `DagBuilder`，再到 `Dag::run → commit → prove → verify`。`run` 产生 witness；`prove` 沿依赖关系反向归约；`verify` 重建挑战并校验消息。它不是神经网络反向传播，不计算梯度。

`Claim` 的语义是 `(edge_id,sparse_id,point,eval)`，即某条边对应的某个多项式在某点等于某值。每次读一个 `prove`，都写下它收到什么 claim、产生什么 claim。每次读 `verify`，检查它是否验证了**边、坐标和值的连接**。

合并多个声明的一种标准等式是：

$$\sum_t\alpha_t v_t=\sum_b\left(\sum_t\alpha_t\operatorname{eq}(r_t,b)\right)\widetilde A(b).$$

对右侧做 sumcheck，归约为一次新的 $A$ 求值。这里随机线性组合必须在原有声明固定后抽样；它和把不同点的值直接相加当成同一点值完全不同。源码入口 `src/basicblock/reducer.rs`。

**动手任务：** 在纸上或笔记里列出上述每个节点的输入/输出 shape、scale、claim point。用 `rg -n 'pub fn|fn prove|fn verify' src/dag/mod.rs src/basicblock/reducer.rs` 定位，然后跟踪一条输入边至 opening。暂时不用构建完整 LLM。

多 token 场景还要绑定生成 token 与下一步输入 token，检查 causal mask 和输出 argmax 的范围。证明某个 token 是最大值不自动规定并列最大时的 tie-breaking，也不等于证明 temperature/top-p 采样。公开模型承诺的身份和版本也属于应用声明的一部分。

## PCS、安全边界与研究问题

KZH-3 在这里认证 MLE 求值。`kzh3_commit` 用求值表和 SRS 基点做 MSM；`kzh3_open` 生成开证明；`verify_and_extract` 从证明提取求值并检查。`Dag::verify` 将 opening 提取值与 `edge_proofs` 的 claim 值比较，这是必要步骤，但还应检查这些 claim 与上游 sumcheck 派生 claim 是否完全一致。

论文 §6.1 对长度 $N$ 的表报告 KZH-3 的线性 prover 和 $O(N^{1/3})$ opening 大小/验证开销。不要把 sumcheck 的对数轮消息大小当成整个证明大小。它基于 BN254 配对，不是后量子方案。

附录 D.5–D.6 明确讨论 hiding PCS 与 masked sumcheck 才能获得零知识。本次查看的 `kzh3_commit` 为确定性 MSM，`LinearSumcheckProver` 发送未遮蔽的轮消息；不能仅因项目名含 zk 就把这条路径称为已实现完整零知识保护。给 PCS 加 hiding 也不能自动隐藏普通 sumcheck 消息。

### 从源码看到的待核对问题

以下是静态阅读发现，并非已构造攻击或完成审计的结论：

| 位置 | 观察 | 为什么需要继续检查 |
|---|---|---|
| `LinearSumcheckProver::prove` | 所有表必须等长 | 与附录 F 不同变量数输入的通用算法存在实现范围差异 |
| `verify_two_pow` | 只检查 sumcheck 递推是否成功，未使用返回的挑战/最终值做表乘积检查 | 应确认 lookup 的最终 oracle 值如何绑定 |
| `verify_range` | table/bool 的 sumcheck 返回值仅检查 `is_none` | 完整协议需要最终多项式等式和 opening 的连接 |
| `Einsum::verify` | 验证乘积值，但未在该函数重新检查各输入 claim 的 point 是否为应派生坐标 | 需要检查外层能否强制坐标一致 |
| `Dag::verify` | opening 针对 `edge_proofs[e].claims`；另行维护节点 claims | 要验证两组声明间的边、点、值绑定，不能只验证各自内部正确 |
| ExpHelper range 分支 | 检查 $k$ 相关关系 | 不可因此假定余量区间已强制执行 |

这类问题适合后续写小的负向测试定位。本教程不修改验证逻辑、不宣称消除了这些问题。`labs.py` 特意包含最终 oracle 检查，帮助理解完整协议必须具备的环节。

### 怎么读实验数字

论文表 2 的 GPT-2 3.4 秒是 16 prompt + 16 generated 的每生成 token 摊销数据；表 3 的单 token、64 输入设置不同。论文表 7 的 50.59 秒除以 16 约为 3.16 秒，与表 2 的 3.4 秒并不完全相同；阅读时保留原口径，不强行合并。2 TB 是实验服务器内存配置，不是所有练习的最低需求。README 明确性能路径采用随机权重；真实权重的量化/PPL 实验位于 `ppl_repro/`，应分开理解。

对格 PCS 研究最有价值的切入点是：保留张量到 MLE 的归约方式，枚举最终 dense/sparse opening 的数量、维度、点分布、批处理需求，再分析你的承诺是否支持。更换底层域或承诺不仅影响单次 opening，还影响范围编码、定点溢出界、挑战分布、知识性与零知识证明；不能把配对型 PCS 接口机械替换后就认定整体性质保持。

