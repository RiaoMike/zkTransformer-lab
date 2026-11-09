# 7 · 把自己写过的算法接回真实 Rust 库

这节的参考程序通过 [CPU 构建入口](../cpu/README.md) 加载 `upstream/` 原始证明模块，没有复制原库的证明算法。
示例都在 [project/examples](../project/examples/)。本次执行状态见 [VALIDATION.md](../reference/VALIDATION.md)。

## 先准备工具链与依赖

上游 README 指定 `nightly-2025-07-01`。下面命令均从工作区根目录运行：

```fish
source tutorial/env.fish
rustup toolchain install nightly-2025-07-01 --profile minimal
cargo +nightly-2025-07-01 check --manifest-path tutorial/project/Cargo.toml --examples --locked
```

这是正常联网构建，会下载 Git 和 crates.io 依赖；不需要手动先下载所有 crate。
以上适用于 fish；Bash 请使用 `source tutorial/env.sh`。
环境脚本使用 rsproxy 加速 Rustup 和 crates.io 下载；GitHub Git 依赖仍需可用的 GitHub 连接。

后面的 `cargo run` 命令均传入 `-- upstream/config.yaml`。原库的 `CONFIG_FILE` 从程序的第一个参数读取配置，
某些 Sumcheck 插值/缓存路径也会间接访问它；因此只运行一个小协议也要显式传配置。
若本机缓存目录不可写，可为该命令指定一个可写的 `CARGO_HOME`；不必改上游源码。

`tutorial/project/Cargo.toml` 中重复了上游的 `[patch.crates-io]`，因为 path 依赖的 patch 不会自动成为根包的 patch。
其 `zk_torch_2` 依赖指向 `tutorial/cpu`：证明和 DAG 源码保持上游原文，只将 ONNX 导入器和 Icicle 本地库设为可选，避免引入本节不使用的构建路径。
共享字段类型通过原库导出的 `ArkBn254` 和 `PairingTrait` 取得，避免混用两份不同来源的 arkworks 类型。

如果出现 `Patch ark-bn254 v0.5.0-alpha.0 was not used`，这是当前补丁版本没有匹配 `0.5.0` 依赖的警告。
保留本工作区锁文件即可继续本教程；不要为了消除警告而整体更新依赖。

如果构建失败，记录**第一条错误**，先区分下载错误、工具链错误、上游源码错误、自己的接口错误。
不要直接运行全部旧测试：当前 `tests/` 中一些导入仍叫 `zktransformer`，而真实包名是 `zk_torch_2`。

## 练习 A：MLE

先不复制整份参考程序。创建 `tutorial/project/examples/my_mle.rs`：

1. 引入 `DenseMLPoly`、`MLPoly` 和教程 crate 的 `f,F`。
2. 用 `DenseMLPoly::from_evaluations` 建 `[1,2,3,4]`。
3. 调 `fix_variables(&[f(2)])`，打印 `n` 和 `evaluations`。
4. 对剩余变量求值，断言等于 `f(9)`。
5. 加入第一节的乘法反例。

参考入口：[01_mle.rs](../project/examples/01_mle.rs)。

```bash
cargo +nightly-2025-07-01 run --manifest-path tutorial/project/Cargo.toml --example 01_mle -- upstream/config.yaml
```

本节的域是 BN254 标量域，不能用 Python 模 101 的随机挑战结果作为 Rust 数值期望。
这些不发生模约减的小整数例子仍应一致。

## 练习 B：Sumcheck

参考入口：[02_sumcheck.rs](../project/examples/02_sumcheck.rs)。先自己写出：

```rust
let mut pt = Transcript::<F>::new(b"tutorial-sumcheck");
let mut prover = LinearSumcheckProver::new(2, 2, &mut pt);
let proof = prover.prove(&polys, &mut pt);
```

两张表分别为 `[1,2,3,4]` 和 `[5,6,7,8]`，初始和是 70。
prover/verifier 必须各用一个新 transcript，标签相同。
调用 verifier 后，自己补“返回最终值等于输入 MLE 乘积”的检查。

```bash
cargo +nightly-2025-07-01 run --manifest-path tutorial/project/Cargo.toml --example 02_sumcheck -- upstream/config.yaml
```

把 70 改成 71，验证应拒绝。然后把最后的 oracle 对比删除，再解释此时程序少验证了什么。

## 练习 C：一个真实 Einsum BasicBlock

参考入口：[03_einsum.rs](../project/examples/03_einsum.rs)。自己按四步搭建：

1. 用 `Witness::new` 创建两张 `2×2`、`sf=0` 的整数表。
2. `Einsum { equation: "ij,jk->ik".into() }.run(...)` 算输出，检查布局。
3. 手动设置输出 `Claim(edge=2, point=[2,3], eval=93)`，调用 `prove`。
4. 打印两个输入 Claim，直接求值交叉检查，再调用 `verify`。

```bash
cargo +nightly-2025-07-01 run --manifest-path tutorial/project/Cargo.toml --example 03_einsum -- upstream/config.yaml
```

这里的 `witnesses`、`edge_ids` 顺序是“输入在前、输出在后”；verify 的 claims 也将输出 claim 放最后。
不要只看 eval，要记录每个输入点中哪个坐标来自输出点、哪个来自 Sumcheck。

进阶：改成 `bij,bjk->bik`，shape 全部为 2、输入值用第二节的数据；
亲自观察新增的批次变量挑战和 eq 因子。不要预期 BN254 下的初始声明仍为模 101 的 54，
应先通过输出 MLE 计算真实域中的初始声明。

## 本节交付

- 自己写的三个 Rust 程序与参考示例分别运行，保存实际输出。
- 从运行输出指出 `run`、`prove`、`verify` 的边界。
- 解释目前为什么仍需要直接读取输入表，以及下一节 PCS 会替换哪一行。

下一节：[PCS 与整个模型](08_pcs_model.md)。
