# 课程验证记录

日期：2026-11-08。上游提交：`55344d7c37232b4dbe8aa479e139967230d8449b`。

## 当前结果

**五个真实 Rust API 示例均已使用论文指定的 `nightly-2025-07-01` 编译运行通过。**
构建使用 [CPU 入口](../cpu/README.md)：直接读取上游证明模块，把 ONNX/Icicle 的未使用构建路径设为可选。
原始 `upstream/` 的 72 个来源文件仍通过 Git blob 哈希校验。

实际工具链：`rustc 1.90.0-nightly (f26e58023 2025-06-30)`。
正式验证没有使用 `RUSTC_BOOTSTRAP` 或替换 rustc；依赖全部命中用户下载的缓存。

| 示例 | 实测结果 |
|---|---|
| `01_mle` | 部分固定表 `[3,5]`；`MLE(2,3)=9` |
| `02_sumcheck` | 初始和 70 通过；改为 71 被拒绝；最终 oracle 对比通过 |
| `03_einsum` | 输出表 `[23,34,31,46]`；输入 claim 与直接求值一致；篡改输入 eval 被拒绝 |
| `04_pcs` | 真实 KZH-3 setup/commit/open/verify，认证值为 25 |
| `05_dag_pcs` | MatMul + Add 的完整 DAG，在清除 witness 数据后验证为 `true` |

实际程序输出见 [results/rust-nightly.txt](rust-nightly.txt)。
完整构建日志和带锁文件 SHA-256 的 JSON 报告位于 `.build/results/`。
日志中的 `Round ... mismatch` 和 `verified einsum failed` 来自故意篡改测试，程序的预期检查已通过。

执行命令（fish）：

```fish
source tutorial/env.fish
cargo +nightly-2025-07-01 check --manifest-path tutorial/project/Cargo.toml --examples --locked --offline
python3 tutorial/tools/run_rust_examples.py all --offline
```

`--offline` 只用于本次验证确认无需再下载；正常使用可省略，runner 默认也不启用它。
每个例子的实际 cargo 命令均传入 `-- upstream/config.yaml`，满足原库全局配置的参数读取规则。

## 教学材料检查

- 72 个上游文本文件的 Git blob SHA-1 全部匹配；保留上游许可证。
- 六课新练习的参考实现全部通过，覆盖 MLE、Einsum 编译、Sumcheck、结构化表、重缩放和 Reducer。
- 原 `labs.py all` 的六课例子、48 组随机交叉检查及负向测试通过。
- 两节点 Python Claim 追踪通过，修改叶子值或交换坐标会被直接 oracle 拒绝。
- 本地 Markdown 链接、源码定位、CPU 清单与原清单的依赖对应关系均通过检查。
- CPU 入口和五个例子的 nightly rustfmt 检查通过。
- fish 脚本已做语法检查、实际加载和指定工具链调用验证；Bash 脚本也通过语法检查。

练习区 `exercises.py` 的 TODO 留给学习者；参考实现通过不代表作业已经完成。

```bash
python3 tutorial/tools/verify_materials.py
```

## 构建过程中处理的问题

1. 使用 rsproxy 的 Rustup 与 crates.io sparse 镜像；GitHub Git 依赖仍需要原地址的网络连接。
2. 初次下载的 nightly 缺少标准库且压缩包未完成；用户补齐后，已确认 `rust-std` 等组件安装完整。
3. 上游依赖解析到了 MSRV 1.96 的 `kstring 2.0.5`，已在上游锁文件中固定为 MSRV 1.73 的 `2.0.2`。
   默认 CPU 教程不启用 ONNX，其实际依赖图不包含 kstring。
4. 上游默认 arkworks 构建仍会因无条件 Icicle 依赖而执行 CMake，并下载 Taskflow。
   该原始完整构建路径仍需 CMake 和 Taskflow；本次不将它记为构建完成。
5. 因此教程增加独立 CPU 入口：没有修改上游证明算法；具体边界在 `cpu/README.md`。
6. `ark-bn254 0.5.0-alpha.0` 补丁未匹配 `0.5.0` 的警告保留，不影响本次五个例子的通过结果。

在 nightly 修复前，曾用本机 stable 1.98 + `RUSTC_BOOTSTRAP=1` 做临时兼容性诊断；
这些诊断不作为当前通过结论的依据，现已由指定 nightly 的正式运行替代；临时诊断目录和辅助工具已清理。

## 验证范围

本次验证的是教学代数、原库小协议 API 和两节点 DAG 的诚实执行/示例负向测试。
未执行完整 Transformer 性能复现、真实模型权重/PPL 实验或安全审计。
论文性能入口和 ONNX/Icicle 后端的完整构建，仍应按上游说明另行准备环境。
