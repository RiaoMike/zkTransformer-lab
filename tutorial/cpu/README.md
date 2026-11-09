# 教程的 CPU 构建入口

这个清单使用 BN254 + arkworks，编译 `upstream/src/` 的原始 Rust 模块。
它没有另写一套证明算法。`tutorial/project/` 的五个示例通过这里调用原库 API。

增加此入口的原因：上游清单无条件依赖 Icicle，即使默认使用 arkworks，也会构建其 C++ 库；
当前拉取的 Icicle 还在 CMake 配置阶段下载 Taskflow。ONNX 导入器又无条件引入 `icicle_core`。
这些构建路径并非前八节代数和 API 练习所需。

与原库构建入口的区别只有：

1. `Cargo.toml` 将 Icicle 和 `tract-onnx` 设为可选依赖，默认仍为 `bn254,arkworks`。
2. `build.rs` 读取原始 `upstream/src/lib.rs`，为模块补充指向上游文件的绝对路径，并给 ONNX 模块加 feature 条件。
3. 全局配置、定点尺度常量以及 `basicblock`、`crypto`、`dag`、`util` 模块都来自原始文件。
4. 没有加入原库的旧测试、性能入口或 ONNX 导入流程；这些仍在 `upstream/`。

`upstream/` 的 72 个来源文件保持原始哈希。生成的 Rust 入口位于 Cargo 的 `OUT_DIR`，可检查其差异。
这套入口适合学习协议和小图；它不等于完整论文性能环境。

```fish
source tutorial/env.fish
cargo +nightly-2025-07-01 check --manifest-path tutorial/project/Cargo.toml --examples --locked
cargo +nightly-2025-07-01 run --manifest-path tutorial/project/Cargo.toml --example 01_mle --locked -- upstream/config.yaml
```

保留教程和上游的 `Cargo.lock`，避免重新解析到不兼容旧 nightly 的依赖。
本次将 `kstring` 固定在 2.0.2（注册表声明 MSRV 1.73）；它由上游 ONNX 依赖链引入。
默认 CPU 教程不构建该依赖链。
