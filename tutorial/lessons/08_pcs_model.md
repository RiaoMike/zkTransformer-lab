# 8 · 把叶子求值认证接上，再进入模型

论文：§6.1、附录 D、H–J。
原库：[polycommit](../../upstream/src/crypto/polycommit/)、[Dag](../../upstream/src/dag/mod.rs)、[nanoGPT](../../upstream/src/dag/nanogpt.rs)。

## 第一步：只验证一个 opening

先读 `MLPolyCommit` 的接口，不必立刻推导配对公式：

```text
setup → key
commit(poly,key) → commitment
open(commitment,poly,key,point) → opening
verify_and_extract(commitment,opening,vk,point) → (ok,value)
应用层还需检查 value 等于上游归约要求的值
```

跟着 [04_pcs.rs](../project/examples/04_pcs.rs) 自己写一遍：

- 表取 `1..8`，变量数是 3，点为 `[2,3,4]`，预期值是 25。
- 使用真实 `KZH3Commit::setup`；这里 3 指变量数，而不是表长。
- commit、open、verify_and_extract，检查 `(ok && value==25)`。
- 把应用要求的值改成 26，应用检查必须失败。

```bash
cargo +nightly-2025-07-01 run --manifest-path tutorial/project/Cargo.toml --example 04_pcs -- upstream/config.yaml
python3 tutorial/tools/source.py pcs_trait
python3 tutorial/tools/source.py pcs
```

本地教学 setup 便于理解 API；真实部署另需确定 SRS 的来源和信任模型。
不要用 `fake_setup` 来判断协议正确性，它供基准用途，不生成正常的密码学设置。

## 第二步：两节点 DAG 的完整 API 流程

[05_dag_pcs.rs](../project/examples/05_dag_pcs.rs) 对第六节的 `Z=XW;Y=Z+C` 使用真实 DAG 与 KZH-3：

```text
DagBuilder 构图
  → compile
  → run 生成 witness
  → 收集变量数、准备各尺寸 SRS
  → commit
  → prove：节点 Sumcheck + 叶子 opening
  → 清除 witness 数据
  → verify
```

第一版采用 `sf=0` 的整数，且 `einsum(...,false)`，只保留 MatMul 与 Add。
先完成这个路径，再加量化、range 和 exp；这样每增加一种子协议都能单独追踪。

```bash
cargo +nightly-2025-07-01 run --manifest-path tutorial/project/Cargo.toml --example 05_dag_pcs -- upstream/config.yaml
```

本次已实测得到 `tiny DAG verified: true`，见 [验证记录](../reference/VALIDATION.md)。这是本例的验收条件。
运行时记录每个 node/edge 的 claims，和第六节表格逐项核对。
示例在 prover 侧断言输出数组符合本例预期；应用部署仍需把公共输入、期望输出和模型身份明确绑定到验证实例，
不能只接受某个未指定输出的自洽证明。

## 第三步：三个有价值的负向实验

在自己的示例副本中，每次只改一项，保存结果：

1. 在证明后改一个节点 claim 的 eval，使用新的 verifier transcript 重跑。
2. 改一个输入 claim 的 point，保持 eval 和原 opening 不变。
3. 给同一条边增加第二个下游消费者，确认它是否触发 Reducer，并追踪合并后的点。

若出现意外接受，先区分“实验没触及验证使用的数据”与“验证链缺少绑定”。
原库 `node_proofs` 与 `edge_proofs` 是两组对象；不要只改了其中不被检查的一份，然后就宣布密码学被攻破。
课程参考示例不声称完成原库安全审计。

## 第四步：把小图扩成 attention

先画简化的 `Q=XWq,K=XWk,V=XWv,S=QK^T,A=softmax(S),O=AV`。
对每个节点填表：

| 运算 | shape | 输入/输出 sf | 归约出的点 | 最后谁认证 |
|---|---|---|---|---|
| Query projection | 自己填 | 自己填 | 自己填 | 自己填 |
| RoPE / reshape | 自己填 | 自己填 | 自己填 | 自己填 |
| QK 转置乘法 | 自己填 | 自己填 | 自己填 | 自己填 |
| Softmax | 自己填 | 自己填 | 自己填 | 自己填 |
| AV | 自己填 | 自己填 | 自己填 | 自己填 |

附录 I 的 Query projection + RoPE 是较小的论文例子；先理解这一段再看完整 Transformer。

然后按照以下顺序读原库：

1. `src/bin/nanogpt.rs`：读参数、构图、run/commit/prove/verify 调用位置。
2. `src/dag/nanogpt.rs`：圈出 attention、MLP 和归一化的构图函数。
3. `src/dag/builder.rs`：把一个高级算子展开成基本节点。
4. `src/basicblock/`：挑一个节点，按本课程方法重新推导证明等式。
5. `src/bin/oneshot_gpt2.rs` 和 `src/dag/oneshot.rs`：再看 embedding、LM head、argmax 与生成 token 的连接。

源码导航：`python3 tutorial/tools/source.py model`。
如要运行上游 nanoGPT 性能入口，按上游 README 的工具链执行：

```bash
cd upstream
SEQ_LEN=1 cargo +nightly-2025-07-01 run --release --bin nanogpt -- config.yaml
```

这是原模型实验阶段的命令，尚未作为本课程验证项运行；内存需求、SRS 与构建成本都高于两节点例子。
这里显式传入配置文件，满足原库 `CONFIG_FILE` 从第一个程序参数读取路径的方式。

## 第五步：研究论文时要分清的三个结论

- **计算语义**：证明的是选定量化、近似、截断规则下的计算；与浮点模型精度需另外评估。
- **认证和零知识**：附录 D.5–D.6 讨论 hiding PCS 和 masked Sumcheck；
  当前所读路径的确定性承诺和普通轮消息不能仅凭项目名称就称为完整零知识实现。
- **性能口径**：上游性能入口使用随机权重和真实架构 shape；真实权重的量化/PPL 脚本在 `ppl_repro/`。
  Sumcheck 的轮消息大小也不等于含 PCS opening 的总证明大小。

## 本节交付

- 原库 PCS 示例和两节点 DAG 的实际运行日志，或准确的首个构建错误。
- 一张从 attention 输出到叶子 opening 的声明追踪表。
- 用自己的话说明：这条实现路径保证了什么、近似了什么、还需要验证什么。

完成后读其他 zkML 论文，也沿着“计算语义 → 代数关系 → 归约 → 认证 → 实验口径”这条线拆解。
