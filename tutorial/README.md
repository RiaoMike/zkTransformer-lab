# 边读 zkTransformer 论文，边实现一个小证明系统

学习目标：不是记住模块名，而是亲手完成一次“计算输出 → 证明输出 → 验证证明”，再把自己的实现映射到原库。

## 每次学习怎么进行

每节按这个顺序做，建议一次只做一节，约 1–2 小时；第 7–8 节可能更久。

1. **先读指定论文片段**：先能说清它要证明的等式。
2. **在 `exercises.py` 补函数**：先独立写，卡住再看提示。
3. **运行该课验收**：包含诚实情况与篡改情况。
4. **打开对应原库函数**：逐个标出自己代码中的同一操作。
5. **回答课末问题**：运行成功与理解协议是两个验收维度。

前六节用 Python 小整数把协议过程完全打印出来；第七节起调用真实 Rust API。
Python 用来减少语言和依赖带来的干扰，原库对照贯穿每节。

## 八节课与成果

| 节 | 论文位置 | 你要写出的东西 | 原库对应 |
|---|---|---|---|
| [1. MLE 与乘法反例](lessons/01_mle.md) | §2.4.1、引理 2.2、§3 的例子 | `fold`、`mle`、`eq`，解释 17/21/17 | `DenseMLPoly` |
| [2. Einsum 编译](lessons/02_einsum.md) | §2.1、定理 3.1 | 指标分类、手算两张部分固定表 | `einsum_helper`、`Einsum::prove` |
| [3. Sumcheck 消息](lessons/03_sumcheck.md) | §2.4.2、附录 E–G | prover、插值、verifier、篡改测试 | `LinearSumcheckProver`、`SumcheckVerifier` |
| [4. 结构化 lookup](lessons/04_lookup.md) | §2.5、§4 | 两种表的闭式 MLE、one-hot 查询 | `SelectionPolynomial`、DAG lookup |
| [5. 定点数与 StructuredExp](lessons/05_exp.md) | §2.3、§4、§5.3 | 有符号重缩放、整数分解 | `ScaleDown`、`ExpHelper`、`DagBuilder::exp` |
| [6. Claim 与 DAG](lessons/06_claims.md) | §5、附录 H–I | 跟踪三条输入声明、合并多点声明 | `Claim`、`Reducer`、`Dag::prove` |
| [7. 真实 Rust API](lessons/07_rust.md) | 回看 §3、§5 | MLE、Sumcheck、单个 Einsum 的原库程序 | `tutorial/project/examples/` |
| [8. PCS 与模型](lessons/08_pcs_model.md) | §6.1、附录 D、H–J | KZH-3 opening、小 DAG 全流程、模型阅读记录 | `MLPolyCommit`、`Dag`、nanoGPT |

公式的进一步推导与实现边界见 [补充阅读](reference/theory.md)。

## 第一次开始

在项目根目录：

```bash
# 先打开 lessons/01_mle.md，再实现 exercises.py 的前三个函数
python3 tutorial/check_exercises.py 1

# 定位原库实现
python3 tutorial/tools/source.py mle
```

开始时出现“待完成”是正常的。`check_exercises.py` 不会替你填答案。
需要对照时，再打开 `solutions.py` 或执行：

```bash
python3 tutorial/check_exercises.py 1 --reference
```

第 2 节的编译器和其他小例子的参考实现集中在 `labs.py`。

## 源码和构建

`upstream/` 是提交 `55344d7c37232b4dbe8aa479e139967230d8449b` 的源码快照，
函数名和 [SOURCE_MAP.md](reference/SOURCE_MAP.md) 均以这个版本为准。通过 GitHub 连接下载了 72 个文本文件，
没有 `.git`；论文保存在工作区根目录。可运行 `python3 tutorial/tools/verify_materials.py` 校验快照和教学参考实现。

正常联网且有可写 Cargo/Rustup 缓存的环境，先按上游说明安装工具链并检查原库：

```fish
source tutorial/env.fish
rustup toolchain install nightly-2025-07-01 --profile minimal
cargo +nightly-2025-07-01 check --manifest-path tutorial/project/Cargo.toml --examples --locked
```

以上适用于 fish；Bash 请改为 `source tutorial/env.sh`。两种脚本不要交叉加载。

`env.fish` / `env.sh` 将缓存、工具链和编译产物放在项目的 `.build/`，配置 [rsproxy](https://rsproxy.cn/) 的 Rustup 镜像，
并在项目缓存尚无配置时复制 `tutorial/cargo-config.toml`，使用 crates.io sparse 镜像。
它不修改 shell 启动文件或全局 Cargo 配置。GitHub 的 Git 依赖仍访问其原始 URL，需要可用的网络连接。

上游含 Icicle Git 依赖，以及指向 `a16z/arkworks-algebra` 的补丁依赖；后者使用分支而非固定提交。
上游发布版本没有提供 `Cargo.lock`，本工作区已保留依赖下载后生成的锁文件，并将不兼容旧 nightly 的 `kstring` 固定为 2.0.2。
固定源码提交还不足以固定依赖版本，请保留这些 lockfile 和工具链版本。
不要为了让示例运行而删掉这些依赖或随意改成 crates.io 版本，那会改变你正在学习的实现。

教程示例使用 [CPU 构建入口](cpu/README.md)，直接编译同一份上游证明模块，只将未使用的 ONNX/Icicle 构建设为可选。
原始构建路径仍可通过 `cargo ... --manifest-path upstream/Cargo.toml --lib` 检查；当前版本还涉及 CMake 和 Taskflow 的本地构建。

五个 Rust 示例已通过指定 nightly 的实际编译运行，详见 [VALIDATION.md](reference/VALIDATION.md)。
可用 `python3 tutorial/tools/run_rust_examples.py` 重跑全部示例；运行日志保存在 `.build/results/`。

## 贯穿全课的四个问题

- **计算语义**：shape、内存顺序、定点尺度分别是什么？
- **证明关系**：当前证明的多项式恒等式是哪一条？
- **声明连接**：边 ID、挑战点和值如何传给下一节点？
- **认证来源**：最后的值由公开计算、上游归约还是 PCS opening 保证？

每个模块读完，写下这四项，比从第一行顺读到最后一行更容易掌握 zkML 系统。
