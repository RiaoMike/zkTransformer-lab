# 固定版本源码定位表

上游提交 `55344d7c37232b4dbe8aa479e139967230d8449b`；本地路径均在 `upstream/`。
行号由 `python3 tutorial/tools/source.py --write-map` 从当前快照生成。

| 定位命令参数 | 目的 | 本地文件与行号 | 固定版本链接 |
|---|---|---|---|
| `mle` | 变量折叠与部分固定 | [src/util/poly.rs:842](../../upstream/src/util/poly.rs#L842) | [source](https://github.com/uiuc-kang-lab/zkTransformer/blob/55344d7c37232b4dbe8aa479e139967230d8449b/src/util/poly.rs#L842) |
| `eq` | eq(r,b) 的求值表 | [src/util/poly.rs:573](../../upstream/src/util/poly.rs#L573) | [source](https://github.com/uiuc-kang-lab/zkTransformer/blob/55344d7c37232b4dbe8aa479e139967230d8449b/src/util/poly.rs#L573) |
| `classify` | 定理 3.1 的指标分类 | [src/basicblock/einsum.rs:379](../../upstream/src/basicblock/einsum.rs#L379) | [source](https://github.com/uiuc-kang-lab/zkTransformer/blob/55344d7c37232b4dbe8aa479e139967230d8449b/src/basicblock/einsum.rs#L379) |
| `helper` | 排列、输出挑战分组与求和轮数 | [src/basicblock/einsum.rs:321](../../upstream/src/basicblock/einsum.rs#L321) | [source](https://github.com/uiuc-kang-lab/zkTransformer/blob/55344d7c37232b4dbe8aa479e139967230d8449b/src/basicblock/einsum.rs#L321) |
| `einsum` | 部分固定、Sumcheck 与输入 Claim | [src/basicblock/einsum.rs:468](../../upstream/src/basicblock/einsum.rs#L468) | [source](https://github.com/uiuc-kang-lab/zkTransformer/blob/55344d7c37232b4dbe8aa479e139967230d8449b/src/basicblock/einsum.rs#L468) |
| `sumcheck` | 轮消息及挑战折叠 | [src/crypto/sumcheck/linear_prover.rs:13](../../upstream/src/crypto/sumcheck/linear_prover.rs#L13) | [source](https://github.com/uiuc-kang-lab/zkTransformer/blob/55344d7c37232b4dbe8aa479e139967230d8449b/src/crypto/sumcheck/linear_prover.rs#L13) |
| `verifier` | 轮数、次数、端点和、插值 | [src/crypto/sumcheck/verifier.rs:27](../../upstream/src/crypto/sumcheck/verifier.rs#L27) | [source](https://github.com/uiuc-kang-lab/zkTransformer/blob/55344d7c37232b4dbe8aa479e139967230d8449b/src/crypto/sumcheck/verifier.rs#L27) |
| `transcript` | 消息吸收与 Fiat–Shamir 挑战 | [src/util/transcript.rs:6](../../upstream/src/util/transcript.rs#L6) | [source](https://github.com/uiuc-kang-lab/zkTransformer/blob/55344d7c37232b4dbe8aa479e139967230d8449b/src/util/transcript.rs#L6) |
| `selection` | one-hot 选择矩阵 | [src/util/poly.rs:1017](../../upstream/src/util/poly.rs#L1017) | [source](https://github.com/uiuc-kang-lab/zkTransformer/blob/55344d7c37232b4dbe8aa479e139967230d8449b/src/util/poly.rs#L1017) |
| `lookup` | 批量范围查询验证 | [src/dag/mod.rs:1168](../../upstream/src/dag/mod.rs#L1168) | [source](https://github.com/uiuc-kang-lab/zkTransformer/blob/55344d7c37232b4dbe8aa479e139967230d8449b/src/dag/mod.rs#L1168) |
| `scale` | 整数舍入与余数范围 | [src/basicblock/scale.rs:17](../../upstream/src/basicblock/scale.rs#L17) | [source](https://github.com/uiuc-kang-lab/zkTransformer/blob/55344d7c37232b4dbe8aa479e139967230d8449b/src/basicblock/scale.rs#L17) |
| `exp` | 指数分解 witness | [src/basicblock/exp.rs:24](../../upstream/src/basicblock/exp.rs#L24) | [source](https://github.com/uiuc-kang-lab/zkTransformer/blob/55344d7c37232b4dbe8aa479e139967230d8449b/src/basicblock/exp.rs#L24) |
| `exp_builder` | StructuredExp 的完整构图 | [src/dag/builder.rs:332](../../upstream/src/dag/builder.rs#L332) | [source](https://github.com/uiuc-kang-lab/zkTransformer/blob/55344d7c37232b4dbe8aa479e139967230d8449b/src/dag/builder.rs#L332) |
| `witness` | shape、scale 与张量布局 | [src/dag/mod.rs:64](../../upstream/src/dag/mod.rs#L64) | [source](https://github.com/uiuc-kang-lab/zkTransformer/blob/55344d7c37232b4dbe8aa479e139967230d8449b/src/dag/mod.rs#L64) |
| `claim` | 边、点、值声明 | [src/dag/mod.rs:327](../../upstream/src/dag/mod.rs#L327) | [source](https://github.com/uiuc-kang-lab/zkTransformer/blob/55344d7c37232b4dbe8aa479e139967230d8449b/src/dag/mod.rs#L327) |
| `block` | run/prove/verify 三阶段接口 | [src/basicblock/mod.rs:31](../../upstream/src/basicblock/mod.rs#L31) | [source](https://github.com/uiuc-kang-lab/zkTransformer/blob/55344d7c37232b4dbe8aa479e139967230d8449b/src/basicblock/mod.rs#L31) |
| `reducer` | 多点声明合并 | [src/basicblock/reducer.rs:18](../../upstream/src/basicblock/reducer.rs#L18) | [source](https://github.com/uiuc-kang-lab/zkTransformer/blob/55344d7c37232b4dbe8aa479e139967230d8449b/src/basicblock/reducer.rs#L18) |
| `dag_prove` | DAG 反向归约与 opening | [src/dag/mod.rs:674](../../upstream/src/dag/mod.rs#L674) | [source](https://github.com/uiuc-kang-lab/zkTransformer/blob/55344d7c37232b4dbe8aa479e139967230d8449b/src/dag/mod.rs#L674) |
| `dag_verify` | 节点验证与叶子 opening 认证 | [src/dag/mod.rs:967](../../upstream/src/dag/mod.rs#L967) | [source](https://github.com/uiuc-kang-lab/zkTransformer/blob/55344d7c37232b4dbe8aa479e139967230d8449b/src/dag/mod.rs#L967) |
| `pcs_trait` | 承诺接口 | [src/crypto/polycommit/mod.rs:415](../../upstream/src/crypto/polycommit/mod.rs#L415) | [source](https://github.com/uiuc-kang-lab/zkTransformer/blob/55344d7c37232b4dbe8aa479e139967230d8449b/src/crypto/polycommit/mod.rs#L415) |
| `pcs` | KZH-3 commit/open/verify_and_extract | [src/crypto/polycommit/kzh3.rs:1014](../../upstream/src/crypto/polycommit/kzh3.rs#L1014) | [source](https://github.com/uiuc-kang-lab/zkTransformer/blob/55344d7c37232b4dbe8aa479e139967230d8449b/src/crypto/polycommit/kzh3.rs#L1014) |
| `model` | nanoGPT attention 构图入口 | [src/dag/nanogpt.rs:91](../../upstream/src/dag/nanogpt.rs#L91) | [source](https://github.com/uiuc-kang-lab/zkTransformer/blob/55344d7c37232b4dbe8aa479e139967230d8449b/src/dag/nanogpt.rs#L91) |

例如 `python3 tutorial/tools/source.py einsum` 会打印带行号的源码片段。
用 `rg -n 'fn prove|fn verify|pub fn' upstream/src/...` 可继续追踪其他函数。
